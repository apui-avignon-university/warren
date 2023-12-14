"""Factory for SlidingWindow statements."""

from datetime import datetime, time, timedelta
from random import randint, sample, uniform
from typing import List
from uuid import NAMESPACE_URL, uuid3, uuid4

from pydantic import BaseSettings
from warren.xi.models import ExperienceRead, RelationRead

from ..warren_tdbp.models import Activities, Ressources


class TestSettings(BaseSettings):
    """Settings for statements factory."""

    # Sliding window configuration
    SLIDING_WINDOW_MIN: int = 15
    SLIDING_WINDOW: int = 17
    COURSE_WINDOW: int = 30

    # Active actions configuration
    ACTIVE_ACTIONS_MIN: int = 6
    ACTIVE_ACTIVITIES: int = 4
    ACTIVE_ACTIONS: int = 13
    COURSE_ACTIONS: int = 25

    # Cohort configuration
    DYNAMIC_COHORT_MIN: int = 3
    DYNAMIC_COHORT: int = 7
    COURSE_COHORT: int = 10

    # TODO: implement constraints validators


test_settings = TestSettings()


class SlidingWindowStatementsFactory:
    """Factory to generate LRS statements respecting sliding window requirements."""

    def __init__(self, course_id=None, settings: TestSettings = None):
        """Initialize factory."""
        self.course_id = course_id
        self.course_experience_id = uuid3(NAMESPACE_URL, course_id)
        self.settings = settings

    def _generate_statement(
        self, action_id, student_id, day_offset, event_name: str = None
    ):
        """Generate a statement for a specific action and actor."""
        timestamp = (
            datetime.combine(datetime.now().date(), time.min)
            + timedelta(days=-day_offset)
        ).isoformat()
        actor_name = f"student_{student_id}"
        action_id = f"https://fake-lms.com/action/{action_id}"

        if event_name in Activities:
            grade = {"score": {"scaled": uniform(0.0, 20.0)}}
            return {
                "timestamp": timestamp,
                "actor": {
                    "account": {"name": actor_name, "homePage": "https://fake-lms.com"}
                },
                "object": {
                    "id": action_id,
                    "definition": {"name": f"Action {action_id}"},
                },
                "verb": {"id": "https://xapi.com/fake-verb"},
                "context": {
                    "extensions": {
                        "http://lrs.learninglocker.net/define/extensions/info": {
                            "event_name": event_name
                        }
                    },
                },
                "result": grade,
            }

        else:
            return {
                "timestamp": timestamp,
                "actor": {
                    "account": {"name": actor_name, "homePage": "https://fake-lms.com"}
                },
                "object": {
                    "id": action_id,
                    "definition": {"name": f"Action {action_id}"},
                },
                "verb": {"id": "https://xapi.com/fake-verb"},
                "context": {
                    "extensions": {
                        "http://lrs.learninglocker.net/define/extensions/info": {
                            "event_name": event_name
                        }
                    }
                },
            }

    def _associate_event_names_to_actions(self, event_names: List, action_ids: List):
        # Shuffle the event names and action indices
        shuffled_event_names = sample(event_names, len(event_names))
        shuffled_indices = sample(action_ids, len(action_ids))

        # Create a dictionary with randomly associated values
        result = dict(zip(shuffled_indices, shuffled_event_names))

        return result

    def generate_statements(self):
        """Generate a set of statements given window, cohort and actions constraints."""
        statements = []

        active_actions_event_names = self._associate_event_names_to_actions(
            [activity.value for activity in Activities],
            list(range(1, self.settings.ACTIVE_ACTIVITIES + 1)),
        )
        active_actions_event_names.update(
            self._associate_event_names_to_actions(
                [ressource.value for ressource in Ressources],
                list(
                    range(
                        self.settings.ACTIVE_ACTIVITIES + 1,
                        self.settings.ACTIVE_ACTIONS + 1,
                    )
                ),
            )
        )

        for action_id in range(1, self.settings.ACTIVE_ACTIONS + 1):
            action_cohort_size = randint(
                self.settings.DYNAMIC_COHORT_MIN, self.settings.DYNAMIC_COHORT
            )
            action_cohort = list(range(1, action_cohort_size + 1))

            # Sub cohort of students generating statements between today
            # and settings.SLIDING_WINDOW_MIN
            sub_cohort_1 = sample(action_cohort, randint(1, action_cohort_size))
            # Sub cohort of students generating tatements in a timeframe between
            # settings.SLIDING_WINDOW_MIN and sliding_window
            sub_cohort_2 = list(set(action_cohort) - set(sub_cohort_1))

            for student_id in sub_cohort_1:
                # Generate statements in a timeframe between today and window_size_min
                statement = self._generate_statement(
                    action_id=action_id,
                    student_id=student_id,
                    day_offset=randint(0, self.settings.SLIDING_WINDOW_MIN),
                    event_name=active_actions_event_names.get(action_id),
                )
                statements.append(statement)
            for student_id in sub_cohort_2:
                # Generate statements in a timeframe between window_size_min and
                # sliding_window_size
                statement = self._generate_statement(
                    action_id=action_id,
                    student_id=student_id,
                    day_offset=randint(
                        self.settings.SLIDING_WINDOW_MIN, self.settings.SLIDING_WINDOW
                    ),
                    event_name=active_actions_event_names.get(action_id),
                )
                statements.append(statement)

        # Complete statements set with non-active actions' statements
        statements.extend(self.generate_statements_noise())

        return statements

    def generate_statements_noise(self):
        """Append noisy statements to the statements set.

        Noisy statements are defined as not related to the active actions.

        Statements are generated for actions whose index is greater
        than self.active_actions and for a number of students less than
        the minimum required for the dynamic cohort and for a duration
        less than the minimum for the floating window.
        """
        statements = []
        for idx in range(
            self.settings.ACTIVE_ACTIONS + 1, self.settings.COURSE_ACTIONS
        ):
            actors = randint(1, self.settings.DYNAMIC_COHORT_MIN)
            for actor_id in range(1, actors + 1):
                statement = self._generate_statement(
                    action_id=idx, student_id=actor_id, day_offset=0
                )
                statements.append(statement)

        return statements

    def get_course_experience(self):
        """Return XI ExperienceRead for factory course."""
        return ExperienceRead(
            id=self.course_experience_id,
            created_at=datetime(2020, 1, 1).isoformat(),
            updated_at=datetime(2020, 1, 1).isoformat(),
            iri=self.course_id,
            title={"en-US": "foo"},
            language="en-US",
            description={"en-US": "foo"},
            structure="hierarchical",
            aggregation_level=2,
            technical_datatypes={},
            relations_target=[
                RelationRead(
                    id=uuid4(),
                    created_at=datetime(2020, 1, 1).isoformat(),
                    updated_at=datetime(2020, 1, 1).isoformat(),
                    source_id=self.course_experience_id,
                    target_id=uuid3(
                        NAMESPACE_URL, f"https://fake-lms.com/action/{idx}"
                    ),
                    kind="haspart",
                ).dict()
                for idx in range(1, self.settings.ACTIVE_ACTIONS + 1)
            ],
        )

    def get_course_content_experience(self, source_id):
        """Return XI ExperienceRead for factory course content source."""
        return ExperienceRead(
            id=uuid3(NAMESPACE_URL, source_id),
            created_at=datetime(2020, 1, 1).isoformat(),
            updated_at=datetime(2020, 1, 1).isoformat(),
            iri=source_id,
            title={"en-US": "foo"},
            language="en-US",
            description={"en-US": "foo"},
            structure="atomic",
            aggregation_level=1,
            technical_datatypes={},
        )
