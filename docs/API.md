# MRWA API Reference

Base URL: `https://api.mrwa.app` (production) or `http://localhost:8000` (development)

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

Tokens expire after 15 minutes. Use the refresh endpoint to get a new token.

## Endpoints

### Authentication

#### POST /api/v1/auth/signup
Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

**Response (201):**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2024-01-01T00:00:00Z"
  },
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer"
}
```

#### POST /api/v1/auth/login
Authenticate existing user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "access_token": "jwt_token",
  "refresh_token": "refresh_token",
  "token_type": "bearer"
}
```

#### POST /api/v1/auth/refresh
Get a new access token using refresh token.

**Request:**
```json
{
  "refresh_token": "your_refresh_token"
}
```

**Response (200):**
```json
{
  "access_token": "new_jwt_token",
  "token_type": "bearer"
}
```

#### POST /api/v1/auth/logout
Invalidate current session.

**Headers:** Authorization required

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

### Executions

#### POST /api/v1/executions
Create and start a new execution.

**Headers:** Authorization required

**Request (multipart/form-data):**
```
input_type: "pdf" | "code" | "url" | "youtube"
input_value: string (URL) or file upload
auto_correct: boolean (default: true)
max_retries: integer (default: 3)
```

**Response (201):**
```json
{
  "execution_id": "uuid",
  "status": "planned",
  "plan": [
    {
      "id": 1,
      "name": "Extract document structure",
      "description": "Parse PDF and identify sections",
      "status": "pending"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET /api/v1/executions
List user's executions with pagination.

**Headers:** Authorization required

**Query Parameters:**
- `page`: integer (default: 1)
- `limit`: integer (default: 20, max: 100)
- `status`: string filter ("completed", "running", "failed")

**Response (200):**
```json
{
  "executions": [
    {
      "id": "uuid",
      "input_type": "pdf",
      "input_value": "research_paper.pdf",
      "status": "completed",
      "created_at": "2024-01-01T00:00:00Z",
      "completed_at": "2024-01-01T00:05:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "pages": 3
}
```

#### GET /api/v1/executions/{execution_id}
Get detailed execution information.

**Headers:** Authorization required

**Response (200):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "input_type": "pdf",
  "input_value": "research_paper.pdf",
  "status": "completed",
  "plan": [...],
  "current_step": 4,
  "created_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:05:00Z",
  "metadata": {
    "total_duration": 300,
    "corrections_applied": 1
  }
}
```

#### GET /api/v1/executions/{execution_id}/logs
Stream real-time execution logs.

**Headers:** Authorization required

**Response (200 - Server-Sent Events):**
```
data: {"timestamp": "2024-01-01T00:00:00Z", "level": "info", "message": "Starting execution"}

data: {"timestamp": "2024-01-01T00:00:01Z", "level": "info", "message": "Plan generated"}

data: {"timestamp": "2024-01-01T00:00:02Z", "level": "error", "message": "Step 2 failed"}
```

#### DELETE /api/v1/executions/{execution_id}
Cancel a running execution.

**Headers:** Authorization required

**Response (200):**
```json
{
  "message": "Execution cancelled",
  "execution_id": "uuid"
}
```

### Artifacts

#### GET /api/v1/artifacts/{artifact_id}
Download generated artifact.

**Headers:** Authorization required

**Response (200):**
- Binary file download or JSON data

#### GET /api/v1/executions/{execution_id}/artifacts
List all artifacts for an execution.

**Headers:** Authorization required

**Response (200):**
```json
{
  "artifacts": [
    {
      "id": "uuid",
      "type": "summary",
      "verified": true,
      "created_at": "2024-01-01T00:05:00Z",
      "download_url": "/api/v1/artifacts/uuid"
    }
  ]
}
```

### User

#### GET /api/v1/user/profile
Get current user profile.

**Headers:** Authorization required

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2024-01-01T00:00:00Z",
  "statistics": {
    "total_executions": 42,
    "successful_executions": 38,
    "total_artifacts": 38
  }
}
```

#### PATCH /api/v1/user/profile
Update user profile.

**Headers:** Authorization required

**Request:**
```json
{
  "name": "Jane Doe",
  "email": "newemail@example.com"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "email": "newemail@example.com",
  "name": "Jane Doe",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### System

#### GET /api/v1/health
Check API health status.

**Response (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected",
  "gemini": "available"
}
```

#### GET /api/v1/stats
Get system statistics (admin only).

**Headers:** Authorization required (admin)

**Response (200):**
```json
{
  "total_users": 1234,
  "total_executions": 5678,
  "active_executions": 12,
  "success_rate": 0.92
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {}
  }
}
```

### Common Error Codes

- `400 BAD_REQUEST`: Invalid request parameters
- `401 UNAUTHORIZED`: Missing or invalid authentication
- `403 FORBIDDEN`: Insufficient permissions
- `404 NOT_FOUND`: Resource not found
- `409 CONFLICT`: Resource conflict (e.g., email already exists)
- `422 VALIDATION_ERROR`: Request validation failed
- `429 RATE_LIMIT_EXCEEDED`: Too many requests
- `500 INTERNAL_ERROR`: Server error
- `503 SERVICE_UNAVAILABLE`: Service temporarily unavailable

## Rate Limiting

- Authenticated: 1000 requests/hour per user
- Unauthenticated: 100 requests/hour per IP
- Execution creation: 20 per hour per user

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Webhooks

Configure webhooks to receive execution status updates.

**Webhook Payload:**
```json
{
  "event": "execution.completed",
  "execution_id": "uuid",
  "status": "completed",
  "timestamp": "2024-01-01T00:05:00Z"
}
```

**Events:**
- `execution.started`
- `execution.completed`
- `execution.failed`
- `execution.step_completed`
- `execution.correction_applied`
