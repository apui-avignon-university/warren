"""Tests for the TdBP Warren plugin."""

from datetime import datetime

import pandas as pd
import pytest

from warren_tdbp.indicators import (
    CohortIndicator,
    GradesIndicator,
    ScoresIndicator,
    SlidingWindowIndicator,
)

from .factory import test_settings


@pytest.mark.anyio
async def test_indicators_sliding_window_valid_parameters(
    db_session, sliding_window_fake_dataset
):
    """Test '/window' endpoint with invalid course_id."""
    course_id = "https://fake-lms.com/course/tdbp_101"

    indicator = SlidingWindowIndicator(course_id=course_id)
    sliding_window = await indicator.compute()

    # Check constraint on sliding window size
    window_size = sliding_window.window.until - sliding_window.window.since
    assert window_size.days >= test_settings.SLIDING_WINDOW_MIN

    # Check constraint on dynamic cohort size
    assert len(sliding_window.dynamic_cohort) >= test_settings.DYNAMIC_COHORT_MIN

    # Check constraint on active actions
    assert len(sliding_window.active_actions) >= test_settings.ACTIVE_ACTIONS_MIN


@pytest.mark.anyio
async def test_indicators_cohort_valid_parameters(
    db_session, sliding_window_fake_dataset
):
    """Test '/cohort' endpoint with valid parameters."""
    course_id = "https://fake-lms.com/course/tdbp_101"
    date_until = datetime.now().date()

    indicator = CohortIndicator(course_id=course_id, until=date_until)
    cohort = await indicator.compute()

    assert len(cohort) >= test_settings.DYNAMIC_COHORT_MIN

    # Check only active actions in output
    sliding_window_indicator = SlidingWindowIndicator(
        course_id=course_id, until=date_until
    )
    sliding_window = await sliding_window_indicator.compute()
    active_actions_iris = [action.iri for action in sliding_window.active_actions]

    for action_iris in cohort.values():
        assert any(iri in active_actions_iris for iri in action_iris)

    # Check all active actions are returned in the whole cohort activity
    actions_iris = [action for actions in cohort.values() for action in actions]
    assert sorted((set(actions_iris))) == sorted(active_actions_iris)


@pytest.mark.anyio
async def test_indicators_scores_valid_parameters(
    db_session, sliding_window_fake_dataset
):
    """Test '/scores' endpoint with valid parameters."""
    course_id = "https://fake-lms.com/course/tdbp_101"
    date_until = datetime.now().date()

    # 1.0 Compute scores for the cohort
    indicator = ScoresIndicator(course_id=course_id, until=date_until, student_id=None)
    scores = await indicator.compute()

    actions_activation_rate = [abs(action.activation_rate) for action in scores.actions]

    for student_scores in scores.scores.values():
        # Check scores indexing is correct
        assert len(scores.actions) == len(student_scores)

        # Check scores values consistency
        assert actions_activation_rate == [abs(score) for score in student_scores]

    # Check scores for all active actions are returned
    sliding_window_indicator = SlidingWindowIndicator(
        course_id=course_id, until=date_until
    )
    sliding_window = await sliding_window_indicator.compute()

    assert len(scores.actions) == len(sliding_window.active_actions)

    # 1.1. Compute scores with average option
    indicator = ScoresIndicator(
        course_id=course_id, until=date_until, student_id=None, average=True
    )
    scores = await indicator.compute()

    # Check average computing on scores
    scores_values = pd.DataFrame.from_dict(scores.scores, orient="index")
    assert scores_values.mean().tolist() == scores.average

    # 1.2. Compute scores with totals option
    indicator = ScoresIndicator(
        course_id=course_id, until=date_until, student_id=None, totals=True
    )
    scores = await indicator.compute()

    # Check totals computing on scores
    scores_values = pd.DataFrame.from_dict(scores.scores, orient="index")
    assert scores_values.sum().tolist() == scores.total

    # 2.0. Compute scores for a student having being active within the course
    indicator = ScoresIndicator(
        course_id=course_id, until=date_until, student_id="student_2"
    )
    scores = await indicator.compute()
    actions_activation_rate = [abs(action.activation_rate) for action in scores.actions]

    # Check only one student is listed in the score
    assert len(scores.scores) == 1

    student, student_scores = next(iter(scores.scores.items()))

    assert student == "student_2"

    # Check scores indexing is correct
    assert len(scores.actions) == len(student_scores)

    # Check scores values consistency
    assert actions_activation_rate == [abs(score) for score in student_scores]

    # 2.1. Compute scores for an inactive student
    indicator = ScoresIndicator(
        course_id=course_id, until=date_until, student_id="student_9"
    )
    scores = await indicator.compute()
    actions_activation_rate = [abs(action.activation_rate) for action in scores.actions]

    # Check only one student is listed in the score
    assert len(scores.scores) == 1

    # Check student score is correctly indexed
    student, student_scores = next(iter(scores.scores.items()))
    assert student == "student_9"

    # Check scores indexing is correct
    assert len(scores.actions) == len(student_scores)

    # Check scores values consistency
    assert actions_activation_rate == [abs(score) for score in student_scores]


@pytest.mark.anyio
async def test_indicators_grades_valid_parameters(
    db_session, sliding_window_fake_dataset
):
    """Test '/scores' endpoint with valid parameters."""
    course_id = "https://fake-lms.com/course/tdbp_101"
    date_until = datetime.now().date()

    # 1.0 Compute grades for the cohort
    indicator = GradesIndicator(course_id=course_id, until=date_until, student_id=None)
    grades = await indicator.compute()

    for student_grades in grades.grades.values():
        # Check scores indexing is correct
        assert len(grades.actions) == len(student_grades)

    # Check only grades for active activities are returned
    sliding_window_indicator = SlidingWindowIndicator(
        course_id=course_id, until=date_until
    )
    sliding_window = await sliding_window_indicator.compute()

    assert all(activity in sliding_window.active_actions for activity in grades.actions)

    # Check grades values
    active_activities_iris = [action.iri for action in grades.actions]
    for student_id in grades.grades.keys():
        # Retrieve student's statements related to activities grades
        grades_statements = [
            statement
            for statement in sliding_window_fake_dataset
            if (
                statement.get("object", {}).get("id", {}) in active_activities_iris
                and statement.get("actor", {}).get("account", {}).get("name", {})
                == student_id
            )
        ]

        for statement in grades_statements:
            activity_iri = statement["object"]["id"]
            activity_index = next(
                (
                    index
                    for index, item in enumerate(grades.actions)
                    if item.iri == activity_iri
                ),
                None,
            )
            assert (
                grades.grades[student_id][activity_index]
                == statement["result"]["score"]["scaled"]
            )

    # 1.1 Compute average grades for the cohort
    indicator = GradesIndicator(
        course_id=course_id, until=date_until, student_id=None, average=True
    )
    grades = await indicator.compute()

    # Check average computing on scores
    grades_values = pd.DataFrame.from_dict(grades.grades, orient="index")
    assert grades_values.mean().tolist() == grades.average

    # 2.0 Compute grades for a student
    indicator = GradesIndicator(
        course_id=course_id, until=date_until, student_id="student_1"
    )
    grades = await indicator.compute()

    # Check only one student is listed in the score
    assert len(grades.grades) == 1

    student, student_grades = next(iter(grades.grades.items()))

    assert student == "student_1"

    # Check grades indexing is correct
    assert len(grades.actions) == len(student_grades)

    # Check grades values
    active_activities_iris = [action.iri for action in grades.actions]
    # Retrieve student's statements related to activities grades
    grades_statements = [
        statement
        for statement in sliding_window_fake_dataset
        if (
            statement.get("object", {}).get("id", {}) in active_activities_iris
            and statement.get("actor", {}).get("account", {}).get("name", {})
            == "student_1"
        )
    ]

    for statement in grades_statements:
        activity_iri = statement["object"]["id"]
        activity_index = next(
            (
                index
                for index, item in enumerate(grades.actions)
                if item.iri == activity_iri
            ),
            None,
        )
        assert (
            grades.grades["student_1"][activity_index]
            == statement["result"]["score"]["scaled"]
        )
