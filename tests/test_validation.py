from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ask_rejects_short_question():
    response = client.post("/ask", json={"question": "hi"})
    assert response.status_code == 422

def test_analyze_rejects_unsupported_extension():
    response = client.post("/analyze", files={"file": ("scan.dcm", b"fake", "application/dicom")})
    assert response.status_code == 415
