"""Warren API v1 tdbp router."""

import logging
from datetime import date
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from lti_toolbox.launch_params import LTIRole
from warren.exceptions import LrsClientException
from warren.utils import get_lti_course_id, get_lti_roles, get_lti_user_id

from .indicators import (
    CohortIndicator,
    GradesIndicator,
    ScoresIndicator,
    SlidingWindowIndicator,
)
from .models import Grades, Scores, SlidingWindow
from .utils import is_instructor

router = APIRouter(
    prefix="/tdbp",
)

logger = logging.getLogger(__name__)


@router.get("/window")
async def get_sliding_window(
    course_id: Annotated[str, Depends(get_lti_course_id)],
    roles: Annotated[List[LTIRole], Depends(get_lti_roles)],
    user_id: Annotated[str, Depends(get_lti_user_id)],
    until: Annotated[
        Optional[date],
        Query(
            description="End date until when to compute the sliding window",
        ),
    ] = None,
) -> SlidingWindow:
    """Return course sliding window indicator.

    Args:
        course_id (str): The course identifier on Moodle.
        roles (LTIRole): The roles of the user.
        user_id (str): The user identifier on Moodle.
        until (date): End date until when to compute the sliding window.

    Returns:
        Json: Computed information about the sliding window.
            - window (DateRange): Timeframe of the sliding window
            - active actions (List[Action]): list of computed active actions.
            - dynamic cohort (List[str]): list of student IDs who were active during
                the sliding window.
    """
    logger.debug("Start computing 'window' indicator")

    # Instructors have access to identifying informations for the whole cohort
    student_id = None
    # Students can only read aggregated information about the sliding window
    if not is_instructor(roles):
        student_id = user_id

    indicator = SlidingWindowIndicator(
        course_id=course_id, until=until, student_id=student_id
    )

    try:
        results = await indicator.compute()
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
    course_id: Annotated[str, Depends(get_lti_course_id)],
    roles: Annotated[List[LTIRole], Depends(get_lti_roles)],
    user_id: Annotated[str, Depends(get_lti_user_id)],
    until: Annotated[
        Optional[date],
        Query(description="End date until when to compute the sliding window"),
    ] = None,
):
    """Return course (static) cohort information.

    Args:
        course_id (str): The course identifier on Moodle.
        roles (LTIRole): The roles of the user.
        user_id (str): The user identifier on Moodle.
        until (date): End date until when to compute the sliding window.

    Returns:
        Json: Lists of completed active actions per student.

    """
    logger.debug("Start computing 'cohort' indicator")

    # Instructors can see activity of all students
    student_id = None
    # Students can only see their activity
    if not is_instructor(roles):
        student_id = user_id

    indicator = CohortIndicator(course_id=course_id, until=until, student_id=student_id)

    try:
        results = await indicator.compute()
    except (KeyError, AttributeError, LrsClientException) as exception:
        message = "An error occurred while computing course cohort"
        logger.exception("%s. Exception:", message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        ) from exception

    logger.debug("Finish computing 'cohort' indicator")
    return results


@router.get("/scores")
async def get_scores(  # noqa: PLR0913
    course_id: Annotated[str, Depends(get_lti_course_id)],
    roles: Annotated[List[LTIRole], Depends(get_lti_roles)],
    user_id: Annotated[str, Depends(get_lti_user_id)],
    until: Annotated[
        Optional[date],
        Query(
            description="End date until when to compute the sliding window",
        ),
    ] = None,
    totals: Annotated[
        bool, Query(description="Flag to activate to compute total scores")
    ] = False,
    average: Annotated[
        bool, Query(description="Flag to activate to compute average scores")
    ] = False,
) -> Scores:
    """Return student or cohort scores on active actions.

    Args:
        course_id (str): The course identifier on Moodle.
        roles (LTIRole): The roles of the user.
        user_id (str): The user identifier on Moodle.
        until (datetime): End date until when to compute the sliding window.
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

    # Instructors can see scores of all students, the totals and average
    student_id = None
    # Students can only see their scores
    if not is_instructor(roles):
        student_id = user_id

    indicator = ScoresIndicator(
        course_id=course_id,
        until=until,
        student_id=student_id,
        totals=totals,
        average=average,
    )

    try:
        results = await indicator.compute()
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
    course_id: Annotated[str, Depends(get_lti_course_id)],
    roles: Annotated[List[LTIRole], Depends(get_lti_roles)],
    user_id: Annotated[str, Depends(get_lti_user_id)],
    until: Annotated[
        Optional[date],
        Query(
            description="End date until when to compute the sliding window",
        ),
    ] = None,
    average: Annotated[
        bool, Query(description="Flag to activate to compute average grades")
    ] = False,
) -> Grades:
    """Return average mark for graded active activities.

    Args:
        course_id (str): The course identifier on Moodle.
        roles (list): The roles of the user.
        user_id (str): The user identifier on Moodle.
        until (datetime): End date until when to compute the sliding window.
        average (bool): Flag to activate average grade computing on each graded active
            activity.

    Returns:
        Json: Active activities grades per student.
            - actions (list): Active activities IRIs (used as response index).
            - scores (dict): Lists of active activities grades per student.
            - average (list): Average students' grades per active activity.
    """
    logger.debug("Start computing 'grades' indicator")

    # Instructors can see grades of all students, the totals and average
    student_id = None
    # Students can only see their grades
    if not is_instructor(roles):
        student_id = user_id

    indicator = GradesIndicator(
        course_id=course_id, until=until, student_id=student_id, average=average
    )

    try:
        results = await indicator.compute()
    except (KeyError, AttributeError, LrsClientException) as exception:
        message = "An error occurred while computing grades"
        logger.exception("%s. Exception:", message)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message
        ) from exception

    logger.debug("Finish computing 'grades' indicator")
    return results
