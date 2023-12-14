"""Async test fixtures."""

import json
from datetime import datetime, time
from urllib.parse import quote, quote_plus, urljoin
from uuid import NAMESPACE_URL, uuid3

import pytest
from ralph.backends.data.async_lrs import AsyncLRSDataBackend
from ralph.backends.data.lrs import LRSDataBackendSettings, LRSHeaders
from warren.conf import settings
from warren.indicators import BaseIndicator

from .factory import SlidingWindowStatementsFactory, test_settings


@pytest.fixture
def sliding_window_fake_dataset(monkeypatch, httpx_mock):
    """Mock statements for sliding window requirements."""

    # Mock LRS server base URL
    def mock_lrs_client():
        """Mock LRS client for test."""
        backend_settings = LRSDataBackendSettings(
            BASE_URL="http://fake-lrs.com",
            USERNAME=settings.LRS_AUTH_BASIC_USERNAME,
            PASSWORD=settings.LRS_AUTH_BASIC_PASSWORD,
            HEADERS=LRSHeaders(
                X_EXPERIENCE_API_VERSION="1.0.3", CONTENT_TYPE="application/json"
            ),
        )
        return AsyncLRSDataBackend(settings=backend_settings)

    monkeypatch.setattr(BaseIndicator, "lrs_client", mock_lrs_client())

    # Mock XI server base URL
    fake_xi_url = "http://fake-xi.com"
    monkeypatch.setattr("warren_tdbp.conf.settings.BASE_XI_URL", fake_xi_url)

    course_id = "https://fake-lms.com/course/tdbp_101"
    date_until = datetime.now().date()
    datetime_until = datetime.combine(date_until, time.min)
    factory = SlidingWindowStatementsFactory(
        course_id=course_id, settings=test_settings
    )
    statements = factory.generate_statements()

    # Mock XI response for course experience
    xi_endpoint_course_id = urljoin(
        fake_xi_url, f"/experiences/{factory.course_experience_id}"
    )
    xi_endpoint_course_iri = urljoin(
        fake_xi_url, f"/experiences?iri={quote_plus(course_id)}"
    )

    course_experience = json.loads(factory.get_course_experience().json())
    httpx_mock.add_response(
        url=xi_endpoint_course_id, method="GET", json=course_experience
    )
    httpx_mock.add_response(
        url=xi_endpoint_course_iri, method="GET", json=[course_experience]
    )

    # Mock XI responses and LRS response for course content experiences
    for action_id in range(1, factory.settings.ACTIVE_ACTIONS + 1):
        action_iri = f"https://fake-lms.com/action/{action_id}"
        # 1. Mock XI experience
        httpx_mock.add_response(
            url=urljoin(
                fake_xi_url, f"/experiences/{uuid3(NAMESPACE_URL, action_iri)}"
            ),
            method="GET",
            json=json.loads(
                factory.get_course_content_experience(source_id=action_iri).json()
            ),
        )
        # 2. Mock LRS response
        # Mock the LRS response for each test dataset activity..
        action_statements = [
            statement
            for statement in statements
            if statement["object"]["id"] == action_iri
        ]
        httpx_mock.add_response(
            url=f"http://fake-lrs.com/xAPI/statements?activity={quote(action_iri)}&until={datetime_until.isoformat()}&limit=500",
            method="GET",
            json={"statements": action_statements},
            status_code=200,
        )

    return statements
