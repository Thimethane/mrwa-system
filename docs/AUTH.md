# Authentication System

## Overview

MRWA uses JWT-based authentication with refresh tokens for secure, stateless authentication that works across web and future mobile platforms.

## Authentication Flow

### Registration

```
1. User submits email + password
2. Server validates and hashes password (bcrypt)
3. User record created in database
4. JWT access token generated (15 min expiry)
5. Refresh token generated (7 day expiry)
6. Session created in database
7. Tokens returned to client
```

### Login

```
1. User submits credentials
2. Server verifies password hash
3. New JWT + refresh token generated
4. Old session revoked, new session created
5. Tokens returned to client
```

### Token Refresh

```
1. Client sends refresh token
2. Server validates token not revoked/expired
3. New access token generated
4. New refresh token generated (rotation)
5. Old refresh token marked as revoked
6. New tokens returned
```

### Logout

```
1. Client sends access token
2. Server marks session as revoked
3. Token added to blacklist (Redis)
4. Success response returned
```

## Token Structure

### Access Token (JWT)

```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "type": "access",
  "exp": 1640995200,
  "iat": 1640994300
}
```

### Refresh Token

```
Random UUID stored in database
Linked to user session
Can be revoked at any time
```

## Security Features

### Password Requirements

- Minimum 8 characters
- Must contain: uppercase, lowercase, number
- Optional special character
- Not in common password list

### Token Security

- Access tokens: Short-lived (15 minutes)
- Refresh tokens: Longer-lived (7 days) but revocable
- Tokens signed with HS256
- Secret key minimum 32 characters
- Refresh token rotation on use

### Session Management

- Device fingerprinting
- IP address tracking
- Last activity timestamp
- Concurrent session limit (5 devices)
- Automatic cleanup of expired sessions

### Rate Limiting

- Login attempts: 5 per 15 minutes per IP
- Signup: 3 per hour per IP
- Token refresh: 20 per hour per user
- Lockout after repeated failures

## Cross-Platform Sync

### How It Works

1. User logs in on Device A
2. Session created with device info
3. User logs in on Device B
4. New session created
5. Both devices have unique tokens
6. But share same user_id
7. All executions sync via user_id

### Device Management

Users can:
- View active sessions
- See device info (browser, OS)
- Revoke individual sessions
- Logout from all devices

### Sync Architecture

```sql
-- Sessions table tracks devices
sessions (
  id, user_id, refresh_token,
  device_info, created_at
)

-- Executions tied to user, not session
executions (
  id, user_id, ...
)

-- Query: Get all user's executions
SELECT * FROM executions WHERE user_id = ?
```

## Implementation Details

### Password Hashing

```python
import bcrypt

# Hash password
hashed = bcrypt.hashpw(
    password.encode('utf-8'),
    bcrypt.gensalt(12)
)

# Verify password
bcrypt.checkpw(
    password.encode('utf-8'),
    hashed
)
```

### JWT Generation

```python
import jwt
from datetime import datetime, timedelta

def create_access_token(user_id: str, email: str):
    payload = {
        "sub": user_id,
        "email": email,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=15),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
```

### Middleware

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, JWT_SECRET)
        user_id = payload.get("sub")
        
        # Check if token blacklisted
        if await redis.exists(f"blacklist:{token.credentials}"):
            raise HTTPException(401, "Token revoked")
        
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

## API Usage Examples

### Signup

```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Use Access Token

```bash
curl http://localhost:8000/api/v1/user/profile \
  -H "Authorization: Bearer <access_token>"
```

### Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

### Logout

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer <access_token>"
```

## Frontend Integration

### Store Tokens Securely

```javascript
// Web: httpOnly cookies (best)
// Or: localStorage with XSS protection

// Store after login
localStorage.setItem('access_token', response.access_token);
localStorage.setItem('refresh_token', response.refresh_token);

// Include in requests
fetch('/api/v1/executions', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```

### Auto-Refresh

```javascript
// Intercept 401 responses
async function fetchWithAuth(url, options = {}) {
  let response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${getAccessToken()}`
    }
  });
  
  if (response.status === 401) {
    // Try to refresh
    const newToken = await refreshAccessToken();
    if (newToken) {
      // Retry request
      response = await fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${newToken}`
        }
      });
    }
  }
  
  return response;
}
```

## Security Best Practices

1. **Never expose JWT secrets**
2. **Use HTTPS in production**
3. **Implement rate limiting**
4. **Monitor for brute force attacks**
5. **Rotate secrets periodically**
6. **Log authentication events**
7. **Implement account lockout**
8. **Use secure password hashing**
9. **Validate all inputs**
10. **Keep dependencies updated**

## Troubleshooting

### Token Expired

**Solution**: Use refresh token endpoint

### Token Invalid

**Solution**: Re-login required

### Session Not Found

**Solution**: Session may have been revoked, re-login

### Rate Limited

**Solution**: Wait before retrying, check for automation
