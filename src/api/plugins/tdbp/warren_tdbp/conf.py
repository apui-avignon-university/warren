"""Warren TdBP settings."""


from warren.conf import Settings as WarrenSettings


class Settings(WarrenSettings):
    """Warren's TdBP global environment and configuration settings."""

    DEBUG: bool = False

    # Sliding window
    SLIDING_WINDOW_MIN: int = 15
    ACTIVE_ACTIONS_MIN: int = 6
    DYNAMIC_COHORT_MIN: int = 3

    # Experience Index
    BASE_XI_URL: str = "http://localhost:8100/api/v1"


settings = Settings()
