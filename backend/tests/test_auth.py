import pytest
import jwt
from fastapi.testclient import TestClient
from app.core.config import get_settings
from app.models.enums import UserRole, AccountStatus


@pytest.fixture(autouse=True)
def set_testing_env(monkeypatch):
    monkeypatch.setenv("APP_ENV", "testing")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def make_test_token(
    user_id: str = "00000000-0000-0000-0000-000000000001",
    email: str = "student@test.edu",
    role: str = "STUDENT",
    account_status: str = "ACTIVE",
    institution_id: str = "11111111-1111-1111-1111-111111111111",
    full_name: str = "Test Student",
) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "aud": "authenticated",
        "user_metadata": {
            "full_name": full_name,
            "role": role,
            "account_status": account_status,
            "institution_id": institution_id,
        },
        "app_metadata": {
            "role": role,
        },
    }
    return jwt.encode(payload, "test-secret-key-mastery", algorithm="HS256")


def test_unauthenticated_access_me(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert "Authorization header" in response.json()["detail"]


def test_invalid_token_format(client: TestClient):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer not-a-valid-jwt-token"},
    )
    assert response.status_code == 401


def test_authenticated_student_me(client: TestClient):
    token = make_test_token(role="STUDENT", full_name="Alice Student")
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "student@test.edu"
    assert data["role"] == "STUDENT"
    assert data["full_name"] == "Alice Student"
    assert "assessments:attempt" in data["permissions"]


def test_student_forbidden_from_admin_endpoint(client: TestClient):
    token = make_test_token(
        role="STUDENT",
        account_status="ACTIVE",
        institution_id="11111111-1111-1111-1111-111111111111",
    )
    response = client.get(
        "/api/v1/institutions/11111111-1111-1111-1111-111111111111/members",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert "requires one of the following roles" in response.json()["detail"]


def test_pending_student_forbidden_from_active_endpoint(client: TestClient):
    token = make_test_token(
        role="STUDENT",
        account_status="PENDING",
        institution_id="11111111-1111-1111-1111-111111111111",
    )
    response = client.get(
        "/api/v1/institutions/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert "pending institutional approval" in response.json()["detail"]


def test_institution_admin_access_allowed(client: TestClient):
    inst_id = "11111111-1111-1111-1111-111111111111"
    token = make_test_token(
        user_id="00000000-0000-0000-0000-000000000099",
        email="admin@test.edu",
        role="INSTITUTION_ADMIN",
        account_status="ACTIVE",
        institution_id=inst_id,
        full_name="College Admin",
    )
    response = client.get(
        f"/api/v1/institutions/{inst_id}/members",
        headers={"Authorization": f"Bearer {token}"},
    )
    # Status code is 200 (allowed) returning empty list in test DB
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_institution_admin_cross_institution_forbidden(client: TestClient):
    admin_inst = "11111111-1111-1111-1111-111111111111"
    other_inst = "22222222-2222-2222-2222-222222222222"
    token = make_test_token(
        role="INSTITUTION_ADMIN",
        account_status="ACTIVE",
        institution_id=admin_inst,
    )
    response = client.get(
        f"/api/v1/institutions/{other_inst}/members",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert "only access membership records for your designated institution" in response.json()["detail"]


def test_super_admin_cross_institution_allowed(client: TestClient):
    target_inst = "22222222-2222-2222-2222-222222222222"
    token = make_test_token(
        role="SUPER_ADMIN",
        account_status="ACTIVE",
        institution_id="33333333-3333-3333-3333-333333333333",
        full_name="Platform Super Admin",
    )
    response = client.get(
        f"/api/v1/institutions/{target_inst}/members",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_profile_self_edit_allowed_fields(client: TestClient):
    token = make_test_token(role="STUDENT", full_name="Original Name")
    response = client.patch(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Updated Name", "phone": "+91 9876543210"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    # Role cannot be modified
    assert data["role"] == "STUDENT"


def test_profile_self_edit_disallows_role_tampering(client: TestClient):
    token = make_test_token(role="STUDENT")
    response = client.patch(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Hacker", "role": "SUPER_ADMIN"},  # 'role' is ignored
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "STUDENT"


def test_get_permissions(client: TestClient):
    token = make_test_token(role="FACULTY")
    response = client.get(
        "/api/v1/auth/permissions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "FACULTY"
    assert "syllabus:upload" in data["permissions"]
    assert "assessments:create" in data["permissions"]
