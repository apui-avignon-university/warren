"""Tests for the TdBP Warren plugin."""
from datetime import date, datetime

import httpx
import pytest
from pydantic import ValidationError

from warren_tdbp.models import Grades, Scores, SlidingWindow


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query_params",
    [
        {},  # Missing parameters
        {"course_id": 1234},  # Wrong "course_id" parameter data type
        {
            "course_id": "course_id_101",
            "until": "today",
        },  # Wrong "until" parameter data type
        {"until": date.today()},  # Missing "course_id" parameter
        {"foo": "fake"},  # Unsupported parameter
    ],
)
async def test_api_sliding_window_with_invalid_params(
    query_params, http_client: httpx.AsyncClient
):
    """Test '/window' indicator with invalid query parameters returns 422 HTTP code."""
    response = await http_client.get("/api/v1/tdbp/window", params=query_params)

    assert response.status_code == 422


@pytest.mark.anyio
async def test_api_sliding_window_with_valid_params(
    http_client: httpx.AsyncClient, db_session, sliding_window_fake_dataset
):
    """Test '/window' indicator with query parameters returns correct output."""
    course_id = "https://fake-lms.com/course/tdbp_101"
    date_until = datetime.now().date()

    response = await http_client.get(
        "/api/v1/tdbp/window", params={"course_id": course_id, "until": date_until}
    )

    assert response.status_code == 200

    try:
        SlidingWindow.parse_obj(response.json())
    except ValidationError as err:
        pytest.fail(f"Sliding window indicator is invalid: {err}")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query_params",
    [
        {},  # Missing parameters
        {"course_id": 1234},  # Wrong "course_id" parameter data type
        {
            "course_id": "course_id_101",
            "until": "today",
        },  # Wrong "until" parameter data type
        {"until": date.today()},  # Missing "course_id" parameter
        {"foo": "fake"},  # Unsupported parameter
    ],
)
async def test_api_cohort_with_invalid_params(
    query_params, http_client: httpx.AsyncClient
):
    """Test '/cohort' indicator with invalid query parameters returns 422 HTTP code."""
    response = await http_client.get("/api/v1/tdbp/cohort", params=query_params)

    assert response.status_code == 422


@pytest.mark.anyio
async def test_api_cohort_with_valid_params(
    http_client: httpx.AsyncClient, db_session, sliding_window_fake_dataset
):
    """Test '/window' indicator with query parameters returns correct output."""
    course_id = "https://fake-lms.com/course/tdbp_101"
    date_until = datetime.now().date()

    response = await http_client.get(
        "/api/v1/tdbp/cohort", params={"course_id": course_id, "until": date_until}
    )

    assert response.status_code == 200

    assert len(response.json()) > 1


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query_params",
    [
        {},  # Missing parameters
        {"course_id": 1234},  # Wrong "course_id" parameter data type
        {
            "course_id": "course_id_101",
            "until": "today",
        },  # Wrong "until" parameter data type
        {
            "course_id": "course_id_101",
            "student_id": 12345,
        },  # Wrong "student_id" parameter data type
        {
            "course_id": "course_id_101",
            "totals": 1,
        },  # Wrong "totals" parameter data type
        {
            "course_id": "course_id_101",
            "average": 1,
        },  # Wrong "average" parameter data type
        {"until": date.today()},  # Missing required "course_id" parameter
        {"foo": "fake"},  # Unsupported parameter
    ],
)
async def test_api_scores_with_invalid_params(
    query_params, http_client: httpx.AsyncClient
):
    """Test '/scores' indicator with invalid query parameters returns 422 HTTP code."""
    response = await http_client.get("/api/v1/tdbp/scores", params=query_params)

    assert response.status_code == 422


@pytest.mark.anyio
async def test_api_scores_with_valid_params(
    http_client: httpx.AsyncClient, db_session, sliding_window_fake_dataset
):
    """Test '/scores' indicator with query parameters returns correct output."""
    course_id = "https://fake-lms.com/course/tdbp_101"
    date_until = datetime.now().date()

    response = await http_client.get(
        "/api/v1/tdbp/scores", params={"course_id": course_id, "until": date_until}
    )

    assert response.status_code == 200

    try:
        Scores.parse_obj(response.json())
    except ValidationError as err:
        pytest.fail(f"Scores indicator is invalid: {err}")


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query_params",
    [
        {},  # Missing parameters
        {"course_id": 1234},  # Wrong "course_id" parameter data type
        {
            "course_id": "course_id_101",
            "until": "today",
        },  # Wrong "until" parameter data type
        {
            "course_id": "course_id_101",
            "student_id": 12345,
        },  # Wrong "student_id" parameter data type
        {
            "course_id": "course_id_101",
            "average": 1,
        },  # Wrong "average" parameter data type
        {"until": date.today()},  # Missing required "course_id" parameter
        {"foo": "fake"},  # Unsupported parameter
    ],
)
async def test_api_grades_with_invalid_params(
    query_params, http_client: httpx.AsyncClient
):
    """Test '/grades' indicator with invalid query parameters returns 422 HTTP code."""
    response = await http_client.get("/api/v1/tdbp/grades", params=query_params)

    assert response.status_code == 422


@pytest.mark.anyio
async def test_api_grades_with_valid_params(
    http_client: httpx.AsyncClient, db_session, sliding_window_fake_dataset
):
    """Test '/grades' indicator with query parameters returns correct output."""
    course_id = "https://fake-lms.com/course/tdbp_101"
    date_until = datetime.now().date()

    response = await http_client.get(
        "/api/v1/tdbp/grades", params={"course_id": course_id, "until": date_until}
    )

    assert response.status_code == 200

    try:
        Grades.parse_obj(response.json())
    except ValidationError as err:
        pytest.fail(f"Grades indicator is invalid: {err}")
