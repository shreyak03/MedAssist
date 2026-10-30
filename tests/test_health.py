from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint_lists_three_agents():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert len(data["agents"]) == 3

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "MedAssist AI" in response.text
