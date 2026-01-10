import pytest
from rest_framework.test import APIClient
from core.models import Issue

pytestmark = pytest.mark.django_db


def test_patch_issue_success():
    client = APIClient()

    issue = Issue.objects.create(
        title="Test issue",
        description="Test desc",
        status="open",
        version=1,
    )

    response = client.patch(
        f"/issues/{issue.id}",
        {
            "title": "Updated title",
            "version": 1,
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["title"] == "Updated title"
    assert response.data["version"] == 2


def test_patch_issue_version_conflict():
    client = APIClient()

    issue = Issue.objects.create(
        title="Conflict issue",
        description="Desc",
        status="open",
        version=2,
    )

    response = client.patch(
        f"/issues/{issue.id}",
        {
            "title": "Should fail",
            "version": 1,
        },
        format="json",
    )

    assert response.status_code == 409


def test_get_issues_pagination():
    client = APIClient()

    Issue.objects.create(title="A", status="open")
    Issue.objects.create(title="B", status="open")

    response = client.get("/issues")

    assert response.status_code == 200
    assert "results" in response.data
    assert "count" in response.data


def test_get_issues_filter_by_status():
    client = APIClient()

    Issue.objects.create(title="Open issue", status="open")
    Issue.objects.create(title="Closed issue", status="closed")

    response = client.get("/issues?status=closed")

    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["status"] == "closed"

def test_latency_report_returns_200():
    client = APIClient()
    response = client.get("/reports/latency")
    assert response.status_code == 200
