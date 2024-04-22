"""Warren TdBP indicators."""

import logging
import re
from datetime import date, datetime, time, timedelta
from typing import List, Optional

import numpy as np
import pandas as pd
from pydantic import Json
from ralph.backends.lrs.base import LRSStatementsQuery
from ralph.exceptions import BackendException
from warren.exceptions import LrsClientException
from warren.indicators import BaseIndicator
from warren.indicators.mixins import CacheMixin
from warren.xi.client import ExperienceIndex

from .conf import settings
from .exceptions import (
    ExperienceIndexException,
    IndicatorConsistencyException,
)
from .models import (
    Action,
    Activities,
    Grades,
    Scores,
    SlidingWindow,
    Window,
)
from .utils import dataframe_to_pydantic

logger = logging.getLogger(__name__)


class SlidingWindowIndicator(BaseIndicator, CacheMixin):
    """Compute course sliding window."""

    course_experiences: List[str] = []
    until: date = date.today()

    def __init__(  # noqa:PLR0913
        self,
        course_id: str,
        until: Optional[date] = None,
        sliding_window_min: int = settings.SLIDING_WINDOW_MIN,
        active_actions_min: int = settings.ACTIVE_ACTIONS_MIN,
        dynamic_cohort_min: int = settings.DYNAMIC_COHORT_MIN,
    ):
        """Initialize sliding window indicator."""
        if until is None:
            until = date.today()

        super().__init__(
            course_id=course_id,
            until=until,
            sliding_window_min=sliding_window_min,
            active_actions_min=active_actions_min,
            dynamic_cohort_min=dynamic_cohort_min,
        )

    async def get_course_actions(self) -> List[str]:
        """Return actions related to course read from Experience Index."""
        relations = []

        xi = ExperienceIndex(url=settings.BASE_XI_URL)
        # Get the course given its experience UUID
        experience = await xi.experience.get(object_id=self.course_id)
        if experience is None:
            raise ExperienceIndexException(
                f"Unknown course {self.course_id}. It should be indexed first!"
            )
        if not experience.relations_target:
            raise ExperienceIndexException(
                f"No content indexed for course {self.course_id}"
            )

        for source in experience.relations_target:
            content = await xi.experience.get(object_id=source.source_id)
            if content is None:
                raise ExperienceIndexException(
                    f"Cannot find content with id {source.source_id} for "
                    f"course {self.course_id}"
                )
            relations.append(content.iri)

        return relations

    def get_lrs_query(self):
        """Construct the LRS query for statements whose object is the course.

        WARNING: this method is used only for key cache computing as the LRS
        query requires to look for statements which object is related to the course.
        """
        return LRSStatementsQuery(
            activity=self.course_id,
            until=datetime.combine(self.until, time.min).isoformat(),
        )

    def _get_lrs_query_for_activity(self, activity):
        """Return LRS query for a course-related activity."""
        return LRSStatementsQuery(
            activity=activity,
            until=datetime.combine(self.until, time.min).isoformat(),
        )

    async def get_statements(self) -> pd.DataFrame:
        """Return LRS statements related to course actions."""
        raw_statements = pd.DataFrame()
        course_actions = await self.get_course_actions()
        for action_id in course_actions:
            try:
                data = [
                    value
                    async for value in self.lrs_client.read(
                        target=self.lrs_client.settings.STATEMENTS_ENDPOINT,
                        query=self._get_lrs_query_for_activity(activity=action_id),
                    )
                ]
            except BackendException as exception:
                raise LrsClientException("Failed to fetch statements") from exception

            raw_statements = pd.concat([raw_statements, pd.json_normalize(data)])

        if raw_statements.empty:
            raise IndicatorConsistencyException(
                "Sliding window will not be computed. No statements have been found."
            )

        # Find object.definition.name.<lang> columns
        matching_columns = [
            column
            for column in raw_statements.columns
            if re.match(r"^object\.definition\.name.*$", column)
        ]

        # Select the first one by renaming it
        if matching_columns:
            raw_statements.rename(
                columns={matching_columns[0]: "object.definition.name"},
                inplace=True,
            )

        raw_statements["timestamp"] = raw_statements["timestamp"].apply(
            pd.to_datetime, utc=True
        )
        raw_statements["date"] = raw_statements["timestamp"].dt.date

        # Check whether statements are distributed at least over the sliding window
        statements_window = self.until - raw_statements["date"].min()
        if statements_window.days < self.sliding_window_min:
            raise IndicatorConsistencyException(
                f"Sliding window will not be computed. "
                f"Statements are distributed on a window lower than "
                f"{self.sliding_window_min} days."
            )

        # Check if there are at least enough actions for active actions computing.
        actions = raw_statements["object.id"].nunique()
        if actions < self.active_actions_min:
            raise IndicatorConsistencyException(
                f"Sliding window will not be computed. "
                f"Statements are generated on "
                f"less than {self.active_actions_min} actions."
            )

        # Check if there are enough students to compute the dynamic cohort.
        cohort = raw_statements["actor.account.name"].nunique()
        if cohort < self.dynamic_cohort_min:
            raise IndicatorConsistencyException(
                f"Sliding window will not be computed. "
                f"Statements are generated on "
                f"less than {self.dynamic_cohort_min} students."
            )

        return raw_statements

    async def compute(self) -> SlidingWindow:
        """Return parameters of computed sliding window."""
        statements = await self.get_statements()
        min_datetime = statements["date"].min()
        since = self.until - timedelta(self.sliding_window_min)

        # Instantiate indicator
        sliding_window = SlidingWindow(
            window=Window(since=self.until, until=self.until)
        )
        active_actions = pd.DataFrame(columns=["iri", "name", "module_type"])

        while since >= min_datetime:
            # Filter on statements emitted within the sliding window
            window_statements = statements[since <= statements["date"]]

            if window_statements.empty:
                since -= timedelta(days=1)  # step back from one day
                continue

            # Count unique active students in the sliding window
            cohort = window_statements["actor.account.name"].unique()
            cohort_size = len(cohort)

            # Loop on actions
            actions = (
                window_statements.groupby(
                    [
                        "object.id",
                        "object.definition.name",
                        "context.extensions.http://lrs.learninglocker.net/define/extensions/info.event_name",
                    ]
                )["actor.account.name"]
                .nunique()
                .reset_index()
            )
            actions.rename(
                columns={
                    "object.id": "iri",
                    "object.definition.name": "name",
                    (
                        "context.extensions.http://lrs.learninglocker.net"
                        "/define/extensions/info.event_name"
                    ): "module_type",
                    "actor.account.name": "cohort",
                },
                inplace=True,
            )

            # Find active actions on the current window
            for _, action in actions.iterrows():
                # Check for action not recorded as an active action
                if action.iri in active_actions["iri"].values:
                    continue
                # Record new active action
                if (
                    0.1 * cohort_size <= action.cohort
                    and action.cohort >= self.dynamic_cohort_min
                ):
                    active_actions.loc[len(active_actions)] = action[  # type: ignore[call-overload]
                        ["iri", "name", "module_type"]
                    ]

            if len(active_actions) < self.active_actions_min:
                since -= timedelta(days=1)  # step back from one day
            else:
                return SlidingWindow(
                    window=Window(since=since, until=self.until),
                    active_actions=self._compute_activation(
                        statements, active_actions, cohort_size
                    ),
                    dynamic_cohort=cohort.tolist(),
                )

        return sliding_window

    def _compute_activation(
        self, statements, active_actions, dynamic_cohort_size: int
    ) -> List[Action]:
        """Compute activation information over the course."""
        active_actions["activation_date"] = None
        active_actions["activation_students"] = None
        active_actions["activation_rate"] = None

        for index, action in active_actions.iterrows():
            # Retrieve all statements related to the action
            action_statements = statements[statements["object.id"] == action["iri"]]
            activation_date = min(action_statements["date"])
            activation_students = (
                action_statements["actor.account.name"].unique().tolist()
            )
            activation_rate = len(activation_students) / dynamic_cohort_size
            if activation_rate > 1.0:  # noqa: PLR2004
                activation_rate = 1.0

            active_actions.loc[index, "activation_date"] = activation_date
            active_actions.at[index, "activation_students"] = activation_students
            active_actions.loc[index, "activation_rate"] = activation_rate

        return dataframe_to_pydantic(Action, active_actions)


class CohortIndicator(BaseIndicator, CacheMixin):
    """Compute student active actions activities."""

    until: date = date.today()

    def __init__(  # noqa:PLR0913
        self,
        course_id: str,
        until: Optional[date],
        sliding_window_min: int = settings.SLIDING_WINDOW_MIN,
        active_actions_min: int = settings.ACTIVE_ACTIONS_MIN,
        dynamic_cohort_min: int = settings.DYNAMIC_COHORT_MIN,
    ):
        """Initialize Cohort indicator."""
        super().__init__(
            course_id=course_id,
            until=until,
            sliding_window_min=sliding_window_min,
            active_actions_min=active_actions_min,
            dynamic_cohort_min=dynamic_cohort_min,
        )

    def get_lrs_query(self):
        """Construct the LRS query for statements which object is the course.

        WARNING: this method is used only for key cache computing as the LRS
        query requires to look for statements which object is related to the course.
        """
        return LRSStatementsQuery(
            activity=self.course_id,
            until=datetime.combine(self.until, time.min).isoformat(),
        )

    async def compute(self) -> Json:
        """Return list of active actions per student in the course cohort."""
        sliding_window_indicator = SlidingWindowIndicator(
            course_id=self.course_id, until=self.until
        )
        sliding_window = await sliding_window_indicator.get_or_compute()
        statements = await sliding_window_indicator.get_statements()
        active_actions = sliding_window.active_actions

        # Filter statements from active actions
        filtered_statements = statements[
            statements["object.id"].isin([action.iri for action in active_actions])
        ]

        student_active_actions = (
            filtered_statements.groupby("actor.account.name")["object.id"]
            .agg(list)
            .reset_index()
        )
        return student_active_actions.set_index("actor.account.name")[
            "object.id"
        ].to_dict()


class ScoresIndicator(BaseIndicator, CacheMixin):
    """Compute student or cohort scores on active actions."""

    until: date = date.today()
    student_id: Optional[str] = None

    def __init__(  # noqa:PLR0913
        self,
        course_id: str,
        until: Optional[date],
        student_id: Optional[str] = None,
        totals: Optional[bool] = False,
        average: Optional[bool] = False,
        sliding_window_min: int = settings.SLIDING_WINDOW_MIN,
        active_actions_min: int = settings.ACTIVE_ACTIONS_MIN,
        dynamic_cohort_min: int = settings.DYNAMIC_COHORT_MIN,
    ):
        """Initialize Scores indicator."""
        super().__init__(
            course_id=course_id,
            student_id=student_id,
            until=until,
            totals=totals,
            average=average,
            sliding_window_min=sliding_window_min,
            active_actions_min=active_actions_min,
            dynamic_cohort_min=dynamic_cohort_min,
        )

    def get_lrs_query(self):
        """Construct the LRS query for statements which object is the course.

        WARNING: this method is used only for key cache computing as the LRS
        query requires to look for statements which object is related to the course.
        """
        return LRSStatementsQuery(
            activity=self.course_id,
            until=datetime.combine(self.until, time.min).isoformat(),
        )

    async def compute(self) -> Scores:
        """Return cohort scores for active actions."""
        sliding_window_indicator = SlidingWindowIndicator(
            course_id=self.course_id, until=self.until
        )
        sliding_window = await sliding_window_indicator.get_or_compute()

        active_actions = pd.DataFrame(
            [action.dict() for action in sliding_window.active_actions]
        )

        active_actions.set_index("iri", inplace=True)
        course_cohort_indicator = CohortIndicator(
            course_id=self.course_id, until=self.until
        )
        course_cohort = await course_cohort_indicator.get_or_compute()

        if self.student_id:
            if self.student_id not in course_cohort.keys():
                scores = {
                    self.student_id: [
                        -action.activation_rate
                        for action in sliding_window.active_actions
                    ]
                }
                return Scores(actions=sliding_window.active_actions, scores=scores)

            else:
                course_cohort = {self.student_id: course_cohort[self.student_id]}

        # Get unique activities
        unique_activities = sorted(
            {
                activity
                for activities in course_cohort.values()
                for activity in activities
            }
        )

        # Create a DataFrame with 0s and 1s
        df = pd.DataFrame(
            {
                activity: [
                    1 if activity in course_cohort[student] else 0
                    for student in course_cohort
                ]
                for activity in unique_activities
            },
            index=course_cohort.keys(),
        )

        def compute_students_score(column: pd.Series, action_id, actions: pd.DataFrame):
            """Apply a transformation on a column."""
            score = actions.loc[action_id]["activation_rate"]
            return column.apply(lambda x: float(score) if x == 1 else -float(score))

        df_scores = df.apply(
            lambda col: compute_students_score(
                column=col, action_id=col.name, actions=active_actions
            )
        )

        average_scores = None
        totals_scores = None

        if self.average and self.student_id is None:
            average_scores = df_scores.mean().tolist()

        if self.totals and self.student_id is None:
            totals_scores = df_scores.sum().tolist()

        scores = {
            key: list(values.values())
            for key, values in df_scores.to_dict(orient="index").items()
        }
        actions = sorted(
            sliding_window.active_actions,
            key=lambda x: df_scores.columns.tolist().index(x.iri),
        )

        return Scores(
            actions=actions,
            scores=scores,
            average=average_scores,
            total=totals_scores,
        )


class GradesIndicator(BaseIndicator, CacheMixin):
    """Compute marks on graded activities."""

    until: date = date.today()
    student_id: Optional[str] = None

    def __init__(  # noqa:PLR0913
        self,
        course_id: str,
        until: Optional[date],
        student_id: Optional[str] = None,
        average: Optional[bool] = False,
        sliding_window_min: int = settings.SLIDING_WINDOW_MIN,
        active_actions_min: int = settings.ACTIVE_ACTIONS_MIN,
        dynamic_cohort_min: int = settings.DYNAMIC_COHORT_MIN,
    ):
        """Initialize Grades indicator."""
        super().__init__(
            course_id=course_id,
            student_id=student_id,
            until=until,
            average=average,
            sliding_window_min=sliding_window_min,
            active_actions_min=active_actions_min,
            dynamic_cohort_min=dynamic_cohort_min,
        )

    def get_lrs_query(self):
        """Construct the LRS query for statements which object is the course.

        WARNING: this method is used only for key cache computing as the LRS
        query requires to look for statements which object is related to the course.
        """
        return LRSStatementsQuery(
            activity=self.course_id,
            until=datetime.combine(self.until, time.min).isoformat(),
        )

    async def compute(self) -> Grades:
        """Compute list of marks for graded active activities either for cohort students
        or a specific student.
        """  # noqa: D205
        sliding_window_indicator = SlidingWindowIndicator(
            course_id=self.course_id, until=self.until
        )
        sliding_window = await sliding_window_indicator.get_or_compute()

        statements = await sliding_window_indicator.get_statements()

        active_actions = sliding_window.active_actions

        # Filter on active activities
        active_activities = [
            activity
            for activity in active_actions
            if activity.module_type in Activities
        ]
        filtered_statements = statements[
            statements["object.id"].isin([action.iri for action in active_activities])
        ]

        if self.student_id:
            filtered_statements = filtered_statements[
                filtered_statements["actor.account.name"] == self.student_id
            ]

        # select statements associated to a grade
        filtered_statements.dropna(subset=["result.score.scaled"])
        results = filtered_statements.pivot(
            index="actor.account.name",
            columns="object.id",
            values="result.score.scaled",
        )
        results = results.replace(np.nan, None)

        graded_active_activities = [
            activity
            for activity in active_activities
            if activity.iri in results.columns.tolist()
        ]

        activities = sorted(
            graded_active_activities,
            key=lambda x: results.columns.tolist().index(x.iri),
        )

        grades = {
            key: list(values.values())
            for key, values in results.to_dict(orient="index").items()
        }
        average = None
        if self.average:
            average = results.mean().tolist()

        return Grades(actions=activities, grades=grades, average=average)
