from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check() -> None:
    """
    Test the health check endpoint to ensure it returns the expected status.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}