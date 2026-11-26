from fastapi.testclient import TestClient
from agentops.api import app

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200 and response.json()["status"] == "ok"

def test_demo_run_persists_trace():
    with TestClient(app) as client:
        response = client.post("/runs/demo", json={
            "question": "What is the refund window?",
            "expected_answer": "The refund window is 30 days."
        })
        assert response.status_code == 201
        payload = response.json()
        detail = client.get(f"/runs/{payload['id']}")
        assert detail.status_code == 200
        assert detail.json()["id"] == payload["id"]
