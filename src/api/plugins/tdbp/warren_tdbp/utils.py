"""Utils for TdbP."""


def dataframe_to_pydantic(model_class, dataframe):
    """Convert a dataframe to a list of Pydantic model instances."""
    columns = model_class.__annotations__.keys()

    return [model_class(**row[columns]) for _, row in dataframe.iterrows()]
