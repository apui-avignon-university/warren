"""Warren TdBP indicator models ."""

from datetime import date
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel


class Activities(Enum):
    """Activities identifiers."""

    ASSIGNMENT_SUBMITTED = "\\mod_assign\\event\\assessable_submitted"
    ASSIGNMENT_GRADED = "\\mod_assign\\event\\submission_graded"
    FEEDBACK = "\\mod_feedback\\event\\response_submitted"
    FORUM_DISCUSSION_CREATED = "\\mod_forum\\event\\discussion_created"
    FORUM_POST_CREATED = "\\mod_forum\\event\\post_created"
    TEST = "\\mod_quiz\\event\\attempt_submitted"
    SCORM_PACKAGE_LAUNCHED = r"\mod_scorm\event\sco_launched"
    SCORM_PACKAGE_RAW_SUBMITTED = r"\mod_scorm\event\scoreraw_submitted"
    SCORM_PACKAGE_STATUS_SUBMITTED = r"\mod_scorm\event\status_submitted"


class Ressources(Enum):
    """Ressources identifiers."""

    BOOK = "\\mod_book\\event\\chapter_viewed"
    CHAT = r"\mod_chat\event\course_module_viewed"
    DATABASE = "\\mod_data\\event\\course_module_viewed"
    FOLDER = "\\mod_folder\\event\\course_module_viewed"
    FORUM = "\\mod_forum\\event\\discussion_viewed"
    GLOSSARY = "\\mod_glossary\\event\\course_module_viewed"
    IMS_CONTENT_PACKAGE = "\\mod_imscp\\event\\course_module_viewed"
    EXTERNAL_TOOL = "\\mod_lti\\event\\course_module_viewed"
    PAGE = "\\mod_page\\event\\course_module_viewed"
    URL = "\\mod_url\\event\\course_module_viewed"
    WIKI = "\\mod_wiki\\event\\course_module_viewed"


class Window(BaseModel):
    """Model for sliding window dates."""

    since: date
    until: date


class Action(BaseModel):
    """Model for a computed active action.

    Attributes:
        iri (str): action identifier.
        name (str): action name.
        module_type (str): Activities or Ressources.
        activation_date (date): day when the action has been activated.
        activation_rate (float): ratio of students who made this action compared
            to the dynamic cohort.
        activation_students (list): IDs of students who made this action during
            the sliding window.
    """

    iri: str
    name: str
    module_type: Union[Ressources, Activities]
    activation_date: date
    activation_rate: float
    activation_students: List[str]


class SlidingWindow(BaseModel):
    """Model for computed sliding window indicator."""

    window: Window
    active_actions: Optional[List[Action]]
    dynamic_cohort: Optional[List[str]]


class Scores(BaseModel):
    """Model for computed score indicator."""

    actions: List[Action]
    scores: Dict
    total: Optional[List[float]]
    average: Optional[List[float]]


class Grades(BaseModel):
    """Model for computed grade indicator."""

    actions: List[Action]
    grades: Dict
    average: Optional[List[float]]
