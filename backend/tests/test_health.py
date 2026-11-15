from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "MASTERY"
    assert "Beyond Marks" in data["tagline"]
    assert "version" in data


def test_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "MASTERY"
    assert "services" in data
    assert data["services"]["api"] == "operational"
    # Verify it does not falsely report external services as connected
    assert data["services"]["database"] in ["unconfigured", "connected", "disconnected"]


def test_database_health_endpoint(client: TestClient):
    response = client.get("/api/v1/health/database")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["unconfigured", "connected", "disconnected"]
    assert "configured" in data


def test_custom_exception_handler(client: TestClient):
    response = client.get("/api/v1/non-existent-route-404")
    assert response.status_code == 404
    data = response.json()
    assert data["status"] == "error"
    assert data["error_type"] == "HTTPException"
    assert data["status_code"] == 404
