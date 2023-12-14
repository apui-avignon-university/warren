"""Exceptions for TdbP."""


class IndicatorConsistencyException(Exception):
    """Raised when the configuration of an indicator is not viable for
    computation.
    """  # noqa: D205


class ExperienceIndexException(Exception):
    """Raised when the Experience Index client has a failure."""
