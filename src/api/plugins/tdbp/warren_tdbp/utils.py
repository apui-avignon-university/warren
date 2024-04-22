"""Utils for TdbP."""

import logging

from pydantic import ValidationError

logger = logging.getLogger(__name__)


def dataframe_to_pydantic(model_class, dataframe):
    """Convert a dataframe to a list of Pydantic model instances."""
    columns = model_class.__annotations__.keys()

    model = []
    for _, row in dataframe.iterrows():
        try:
            model.append(model_class(**row[columns]))
        except ValidationError as e:
            logger.warning("Could not convert dataframe to pydantic: %s", e)
            continue
    return model
