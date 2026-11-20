"""One trivial smoke test so CI has something to run.
The real test suite is the student's deliverable (see 8-automation-testing/selenium-or-playwright/)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
