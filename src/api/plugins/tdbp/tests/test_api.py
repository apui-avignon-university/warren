"""Tests for the TdBP Warren plugin."""

from datetime import datetime

import httpx
import pytest
from pydantic import ValidationError
from warren.utils import LTIUser, forge_lti_token

from warren_tdbp.models import Grades, Scores, SlidingWindow


@pytest.mark.anyio
async def test_api_sliding_window_with_invalid_params(
    http_client: httpx.AsyncClient, auth_headers: dict
):
    """Test `/window` endpoint with invalid query parameters returns 422 HTTP code."""
    query_params = {"until": "today"}
    response = await http_client.get(
        "/api/v1/tdbp/window",
        params=query_params,
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_api_sliding_window_with_valid_params(
    http_client: httpx.AsyncClient,
    db_session,
    sliding_window_fake_dataset,
):
    """Test `/window` endpoint with query parameters returns correct output."""
    token = forge_lti_token(course_id="https://fake-lms.com/course/tdbp_101")
    date_until = datetime.now().date()

    response = await http_client.get(
        "/api/v1/tdbp/window",
        params={"until": date_until},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    try:
        SlidingWindow.parse_obj(response.json())
    except ValidationError as err:
        pytest.fail(f"Sliding window indicator is invalid: {err}")


@pytest.mark.anyio
async def test_api_sliding_window_with_invalid_auth_headers(
    http_client: httpx.AsyncClient,
):
    """Test `/window` endpoint with an invalid `auth_headers`."""
    date_until = datetime.now().date()
    response = await http_client.get(
        "/api/v1/tdbp/window",
        params={"until": date_until},
        headers={"Authorization": "Bearer Wrong_Token"},
    )

    assert response.status_code == 401
    assert response.json().get("detail") == "Could not validate credentials"


@pytest.mark.anyio
async def test_api_cohort_with_invalid_params(
    http_client: httpx.AsyncClient, auth_headers: dict
):
    """Test `/cohort` endpoint with invalid query parameters returns 422 HTTP code."""
    query_params = {"until": "today"}
    response = await http_client.get(
        "/api/v1/tdbp/cohort",
        params=query_params,
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_api_cohort_with_valid_params(
    http_client: httpx.AsyncClient,
    db_session,
    sliding_window_fake_dataset,
):
    """Test `/window` endpoint with query parameters returns correct output."""
    token = forge_lti_token(course_id="https://fake-lms.com/course/tdbp_101")
    date_until = datetime.now().date()

    response = await http_client.get(
        "/api/v1/tdbp/cohort",
        params={"until": date_until},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    assert len(response.json()) > 1


@pytest.mark.anyio
async def test_api_cohort_with_invalid_auth_headers(
    http_client: httpx.AsyncClient,
):
    """Test `/cohort` endpoint with an invalid `auth_headers`."""
    date_until = datetime.now().date()
    response = await http_client.get(
        "/api/v1/tdbp/cohort",
        params={"until": date_until},
        headers={"Authorization": "Bearer Wrong_Token"},
    )

    assert response.status_code == 401
    assert response.json().get("detail") == "Could not validate credentials"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query_params",
    [
        {
            "until": "today",
        },  # Wrong "until" parameter data type
        {
            "totals": 2,
        },  # Wrong "totals" parameter data type
        {
            "average": 2,
        },  # Wrong "average" parameter data type
    ],
)
async def test_api_scores_with_invalid_params(
    query_params, http_client: httpx.AsyncClient, auth_headers
):
    """Test `/scores` endpoint with invalid query parameters returns 422 HTTP code."""
    response = await http_client.get(
        "/api/v1/tdbp/scores",
        params=query_params,
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_api_scores_with_valid_params_instructor(
    http_client: httpx.AsyncClient,
    db_session,
    sliding_window_fake_dataset,
):
    """Test `/scores` endpoint for an instructor returns correct output."""
    token = forge_lti_token(
        roles=("instructor",),
        course_id="https://fake-lms.com/course/tdbp_101",
    )
    date_until = datetime.now().date()

    response = await http_client.get(
        "/api/v1/tdbp/scores",
        params={"until": date_until, "average": True, "totals": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    try:
        scores = Scores.parse_obj(response.json())
    except ValidationError as err:
        pytest.fail(f"Scores indicator is invalid: {err}")

    # Instructors can see average and totals scores
    assert len(scores.scores) > 1
    assert scores.average
    assert scores.total


@pytest.mark.anyio
async def test_api_scores_with_valid_params_student(
    http_client: httpx.AsyncClient,
    db_session,
    sliding_window_fake_dataset,
):
    """Test `/scores` endpoint for a student returns correct output."""
    token = forge_lti_token(
        user=LTIUser(
            id="johndoe",
            email="johndoe@example.com",
        ),
        roles=("student",),
        course_id="https://fake-lms.com/course/tdbp_101",
    )
    date_until = datetime.now().date()

    response = await http_client.get(
        "/api/v1/tdbp/scores",
        params={"until": date_until, "average": 1, "total": 1},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    try:
        scores = Scores.parse_obj(response.json())
    except ValidationError as err:
        pytest.fail(f"Scores indicator is invalid: {err}")

    # Student can only see its scores, and cannot see total and average scores
    scores.scores.pop("johndoe")
    assert not scores.scores
    assert not scores.average
    assert not scores.total


@pytest.mark.anyio
async def test_api_scores_with_invalid_auth_headers(
    http_client: httpx.AsyncClient,
):
    """Test `/scores` endpoint with an invalid `auth_headers`."""
    date_until = datetime.now().date()
    response = await http_client.get(
        "/api/v1/tdbp/scores",
        params={"until": date_until},
        headers={"Authorization": "Bearer Wrong_Token"},
    )

    assert response.status_code == 401
    assert response.json().get("detail") == "Could not validate credentials"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "query_params",
    [
        {
            "until": "today",
        },  # Wrong "until" parameter data type
        {
            "average": 2,
        },  # Wrong "average" parameter data type
    ],
)
async def test_api_grades_with_invalid_params(
    query_params, http_client: httpx.AsyncClient, auth_headers: dict
):
    """Test `/grades` endpoint with invalid query parameters returns 422 HTTP code."""
    response = await http_client.get(
        "/api/v1/tdbp/grades",
        params=query_params,
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_api_grades_with_valid_params_instructor(
    http_client: httpx.AsyncClient,
    db_session,
    sliding_window_fake_dataset,
):
    """Test `/grades` endpoint for an instructor returns correct output."""
    token = forge_lti_token(
        roles=("instructor",),
        course_id="https://fake-lms.com/course/tdbp_101",
    )
    date_until = datetime.now().date()

    response = await http_client.get(
        "/api/v1/tdbp/grades",
        params={"until": date_until, "average": True},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    try:
        grades = Grades.parse_obj(response.json())
    except ValidationError as err:
        pytest.fail(f"Grades indicator is invalid: {err}")

    assert len(grades.grades) > 1
    assert grades.average


@pytest.mark.anyio
async def test_api_grades_with_valid_params_student(
    http_client: httpx.AsyncClient,
    db_session,
    sliding_window_fake_dataset,
):
    """Test `/grades` endpoint for a student returns correct output."""
    token = forge_lti_token(
        user=LTIUser(id="student_1", email="student_1@example.com"),
        roles=("student",),
        course_id="https://fake-lms.com/course/tdbp_101",
    )
    date_until = datetime.now().date()

    response = await http_client.get(
        "/api/v1/tdbp/grades",
        params={"until": date_until},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    try:
        grades = Grades.parse_obj(response.json())
    except ValidationError as err:
        pytest.fail(f"Grades indicator is invalid: {err}")

    # Student can only see its grades
    assert len(grades.grades) == 1


@pytest.mark.anyio
async def test_api_grades_with_invalid_auth_headers(
    http_client: httpx.AsyncClient,
):
    """Test `/grades` endpoint with an invalid `auth_headers`."""
    date_until = datetime.now().date()
    response = await http_client.get(
        "/api/v1/tdbp/grades",
        params={"until": date_until},
        headers={"Authorization": "Bearer Wrong_Token"},
    )

    assert response.status_code == 401
    assert response.json().get("detail") == "Could not validate credentials"
