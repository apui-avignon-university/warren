"""Warren API v1 tdbp router."""

import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from warren.exceptions import LrsClientException

from .indicators import (
    CohortIndicator,
    GradesIndicator,
    ScoresIndicator,
    SlidingWindowIndicator,
)

router = APIRouter(
    prefix="/tdbp",
)

logger = logging.getLogger(__name__)


@router.get("/window")
async def get_sliding_window(
    course_id: str,
    until: Optional[date],
):
    """Return course sliding window indicator.

    Args:
        course_id (str): The course identifier on Moodle.
        until (date): End date until when to compute the sliding window.

    Returns:
        Json: Computed information about the sliding window.
            - window (DateRange): Timeframe of the sliding window
            - active actions (List[Action]): list of computed active actions.
            - dynamic cohort (List[str]): list of student IDs who were active during
                the sliding window.
    """
    indicator = SlidingWindowIndicator(course_id=course_id, until=until)

    logger.debug("Start computing 'window' indicator")
    try:
        results = await indicator.get_or_compute()
    except (KeyError, AttributeError, LrsClientException) as exception:
        message = "An error occurred while computing sliding window"
        logger.exception("%s. Exception:", message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        ) from exception

    logger.debug("Finish computing 'window' indicator")
    return results


@router.get("/cohort")
async def get_cohort(
    course_id: str,
    until: Optional[date],
):
    """Return course (static) cohort information.

    Args:
        course_id (str): The course identifier on Moodle.
        until (date): End date until when to compute the sliding window.

    Returns:
        Json: Lists of completed active actions per student.

    """
    logger.debug("Start computing 'cohort' indicator")
    indicator = CohortIndicator(course_id=course_id, until=until)

    try:
        results = await indicator.get_or_compute()
    except (KeyError, AttributeError, LrsClientException) as exception:
        message = "An error occurred while computing course cohort"
        logger.exception("%s. Exception:", message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        ) from exception

    logger.debug("Finish computing 'cohort' indicator")
    return results


@router.get("/scores")
async def get_scores(
    course_id: str,
    until: Optional[date],
    student_id: Optional[str] = None,
    totals: bool = False,
    average: bool = False,
):
    """Return student or cohort scores on active actions.

    Args:
        course_id (str): The course identifier on Moodle.
        until (datetime): End date until when to compute the sliding window.
        student_id (str): The student identifier on Moodle.
        totals (bool): Flag to activate cohort totals scores computing on active
            actions.
        average (bool): Flag to activate cohort average scores for computing on active
            actions.

    Returns:
        Json: Active actions scores per student.
            - actions (list): Active actions IRIs (used as response index).
            - scores (dict): Lists of active actions scores per student.
            - totals (list): Sum of students' scores per active action.
            - average (list): Average students' score per active action.
    """
    logger.debug("Start computing 'scores' indicator")
    indicator = ScoresIndicator(
        course_id=course_id,
        until=until,
        student_id=student_id,
        totals=totals,
        average=average,
    )

    try:
        results = await indicator.get_or_compute()
    except (KeyError, AttributeError, LrsClientException) as exception:
        message = "An error occurred while computing student score(s)"
        logger.exception("%s. Exception:", message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        ) from exception

    logger.debug("Finish computing 'scores' indicator")
    return results


@router.get("/grades")
async def get_grades(
    course_id: str,
    until: Optional[date],
    student_id: Optional[str] = None,
    average: bool = False,
):
    """Return average mark for graded active activities.

    Args:
        course_id (str): The course identifier on Moodle.
        until (datetime): End date until when to compute the sliding window.
        student_id (str): The student identifier on Moodle.
        average (bool): Flag to activate average grade computing on each graded active
            activity.

    Returns:
        Json: Active activities grades per student.
            - actions (list): Active activities IRIs (used as response index).
            - scores (dict): Lists of active activities grades per student.
            - average (list): Average students' grades per active activity.
    """
    logger.debug("Start computing 'grades' indicator")
    indicator = GradesIndicator(
        course_id=course_id, until=until, student_id=student_id, average=average
    )

    try:
        results = await indicator.get_or_compute()
    except (KeyError, AttributeError, LrsClientException) as exception:
        message = "An error occurred while computing grades"
        logger.exception("%s. Exception:", message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        ) from exception

    logger.debug("Finish computing 'grades' indicator")
    return results
