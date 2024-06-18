"""Utils for TdbP."""

import logging
from typing import List

from pydantic import ValidationError

logger = logging.getLogger(__name__)


def dataframe_to_pydantic(model_class, dataframe):
    """Convert a dataframe to a list of Pydantic model instances."""
    columns = model_class.__annotations__.keys()
    existing_columns = [col for col in columns if col in dataframe.columns]

    model = []
    for _, row in dataframe.iterrows():
        try:
            row_dict = {col: row[col] for col in existing_columns}
            # Create an instance of the model class
            model_instance = model_class(**row_dict)
            model.append(model_instance)
        except ValidationError as e:
            logger.warning("Could not convert dataframe to pydantic: %s", e)
            continue
    return model


def is_instructor(roles: List[str]):
    """Determine if any of the provided roles match an instructor position.

    Args:
        roles (List[str]): A list of roles.

    Returns:
        bool: True if any role in the list is `instructor`, `teacher`, or
        `staff`, otherwise False.
    """
    return any(role in ["instructor", "teacher", "staff"] for role in roles)
