# MASTERY — API Contracts & Integration Conventions

**Version:** 2.0  
**Base URL:** `/api/v1`  
**Data Format:** JSON (`application/json`)  
**Phase:** 02/11 — Authentication & Identity Foundation  

---

## 1. Global API Design Conventions

### 1.1 Versioning
All domain routes reside strictly under `/api/v1`. Route naming uses lowercase, hyphen-separated kebab-case:
- Correct: `/api/v1/auth/me`
- Incorrect: `/api/v1/auth/getMe`

### 1.2 Authentication Header
All protected endpoints require the caller's Supabase JWT access token:
```http
Authorization: Bearer <access_token>
```
Tokens are validated via the Supabase project's JWKS endpoint (`ES256`).

---

## 2. Authentication & User Profile Endpoints (Phase 02)

### 2.1 Get Current Authenticated Profile
- **Endpoint:** `GET /api/v1/auth/me`
- **Security:** Requires valid Bearer JWT.
- **Description:** Returns the caller's authoritative profile, global role, account status, and effective RBAC permissions.
- **Response Schema:**
```json
{
  "user_id": "00000000-0000-0000-0000-000000000001",
  "email": "student@institution.edu",
  "full_name": "Rohan Sharma",
  "role": "STUDENT",
  "account_status": "ACTIVE",
  "institution_id": "11111111-1111-1111-1111-111111111111",
  "permissions": [
    "profile:self:read",
    "profile:self:update",
    "assessments:attempt",
    "mastery:self:read"
  ]
}
```

### 2.2 Refresh Authoritative Profile
- **Endpoint:** `POST /api/v1/auth/refresh-profile`
- **Security:** Requires valid Bearer JWT.
- **Description:** Forces a backend database synchronization to fetch the latest role and approval status, rejecting client-side metadata overrides.

### 2.3 Get Effective Permissions
- **Endpoint:** `GET /api/v1/auth/permissions`
- **Security:** Requires valid Bearer JWT.
- **Response Schema:**
```json
{
  "role": "FACULTY",
  "permissions": [
    "syllabus:upload",
    "syllabus:approve",
    "assessments:create",
    "risk:view_alerts"
  ]
}
```

### 2.4 Update Self-Editable Profile Fields
- **Endpoint:** `PATCH /api/v1/users/me`
- **Security:** Requires valid Bearer JWT.
- **Description:** Allows modifying ONLY self-editable personal information. Ignores any client attempts to elevate role or account status.
- **Request Schema:**
```json
{
  "full_name": "Rohan K. Sharma",
  "phone": "+91 9876543210",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

### 2.5 Get User Affiliated Institution
- **Endpoint:** `GET /api/v1/institutions/me`
- **Security:** Requires valid Bearer JWT + `ACTIVE` account status.
- **Response Schema:**
```json
{
  "id": "11111111-1111-1111-1111-111111111111",
  "name": "National Institute of Technology",
  "institution_code": "NIT-01",
  "institution_type": "Autonomous Engineering Institute",
  "city": "Mumbai",
  "state": "Maharashtra",
  "country": "India",
  "is_active": true,
  "created_at": "2026-11-15T12:00:00Z"
}
```

### 2.6 Get Institution Membership Roster
- **Endpoint:** `GET /api/v1/institutions/{institution_id}/members`
- **Security:** Requires role `INSTITUTION_ADMIN` or `SUPER_ADMIN`.
- **Description:** Returns roster of members. Institution admins are restricted strictly to their own institution.

### 2.7 Update Member Approval Status
- **Endpoint:** `PATCH /api/v1/institutions/{institution_id}/members/{user_id}`
- **Security:** Requires role `INSTITUTION_ADMIN` or `SUPER_ADMIN`.
- **Request Schema:**
```json
{
  "membership_status": "ACTIVE",
  "membership_role": "STUDENT"
}
```
