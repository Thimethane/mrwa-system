# Database Schema

## Overview

MRWA uses PostgreSQL for persistent storage with JSONB for flexible schema evolution.

## Entity Relationship Diagram

```
users (1) ──< sessions (N)
  │
  └──< executions (N) ──< execution_logs (N)
                    │
                    └──< artifacts (N)
```

## Tables

### users

Stores user account information.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

**Columns**:
- `id`: Unique user identifier
- `email`: User's email (unique, used for login)
- `password_hash`: bcrypt hashed password
- `name`: Display name
- `created_at`: Account creation timestamp
- `updated_at`: Last profile update
- `last_login`: Last successful login
- `email_verified`: Email verification status
- `metadata`: Additional user data (preferences, settings)

### sessions

Tracks active user sessions across devices.

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    refresh_token VARCHAR(500) UNIQUE NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_refresh_token ON sessions(refresh_token);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
```

**device_info JSONB structure**:
```json
{
  "device_type": "web|mobile|desktop",
  "browser": "Chrome",
  "os": "Windows",
  "platform": "web"
}
```

### executions

Stores workflow execution records.

```sql
CREATE TABLE executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    input_type VARCHAR(50) NOT NULL,
    input_value TEXT NOT NULL,
    input_file_url TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'planned',
    plan JSONB,
    current_step INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb,
    error_message TEXT
);

CREATE INDEX idx_executions_user_id ON executions(user_id);
CREATE INDEX idx_executions_status ON executions(status);
CREATE INDEX idx_executions_created_at ON executions(created_at);
CREATE INDEX idx_executions_user_status ON executions(user_id, status);
```

**Status values**:
- `planned`: Execution plan generated
- `running`: Currently executing
- `validating`: Validating step output
- `correcting`: Applying corrections
- `completed`: Successfully completed
- `failed`: Failed with unrecoverable error
- `cancelled`: User cancelled execution

**plan JSONB structure**:
```json
{
  "steps": [
    {
      "id": 1,
      "name": "Extract document structure",
      "description": "Parse PDF and identify sections",
      "status": "completed",
      "output": "...",
      "attempts": 1,
      "duration_ms": 1500
    }
  ],
  "total_steps": 4,
  "corrections_applied": 1
}
```

### execution_logs

Real-time logs for execution monitoring.

```sql
CREATE TABLE execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID REFERENCES executions(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT NOW(),
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB,
    step_id INTEGER
);

CREATE INDEX idx_execution_logs_execution_id ON execution_logs(execution_id);
CREATE INDEX idx_execution_logs_timestamp ON execution_logs(timestamp);
```

**Log levels**:
- `debug`: Detailed diagnostic information
- `info`: General informational messages
- `warning`: Warning messages
- `error`: Error messages
- `critical`: Critical failures

### artifacts

Generated output artifacts from executions.

```sql
CREATE TABLE artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID REFERENCES executions(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    name VARCHAR(255),
    data JSONB,
    file_url TEXT,
    file_size_bytes BIGINT,
    mime_type VARCHAR(100),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_artifacts_execution_id ON artifacts(execution_id);
CREATE INDEX idx_artifacts_type ON artifacts(type);
```

**Artifact types**:
- `summary`: Text summary
- `analysis`: Detailed analysis
- `documentation`: Generated documentation
- `visualization`: Charts or graphs
- `data_export`: Structured data export

## Queries

### Common Queries

```sql
-- Get user's recent executions
SELECT * FROM executions
WHERE user_id = $1
ORDER BY created_at DESC
LIMIT 20;

-- Get execution with full details
SELECT 
    e.*,
    json_agg(el ORDER BY el.timestamp) as logs,
    json_agg(a) as artifacts
FROM executions e
LEFT JOIN execution_logs el ON e.id = el.execution_id
LEFT JOIN artifacts a ON e.id = a.execution_id
WHERE e.id = $1
GROUP BY e.id;

-- Get user statistics
SELECT 
    COUNT(*) as total_executions,
    COUNT(*) FILTER (WHERE status = 'completed') as successful,
    COUNT(*) FILTER (WHERE status = 'failed') as failed,
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration_sec
FROM executions
WHERE user_id = $1;

-- Clean up expired sessions
DELETE FROM sessions
WHERE expires_at < NOW() OR revoked = TRUE;

-- Get active executions
SELECT * FROM executions
WHERE status IN ('running', 'validating', 'correcting')
AND started_at > NOW() - INTERVAL '1 hour';
```

## Migrations

### Initial Migration

```sql
-- migrations/001_initial_schema.sql

BEGIN;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create tables (see above)

-- Create functions
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMIT;
```

### Example Migration: Add Email Verification

```sql
-- migrations/002_add_email_verification.sql

BEGIN;

ALTER TABLE users
ADD COLUMN email_verified BOOLEAN DEFAULT FALSE,
ADD COLUMN verification_token VARCHAR(255),
ADD COLUMN verification_token_expires TIMESTAMP;

CREATE INDEX idx_users_verification_token
ON users(verification_token)
WHERE verification_token IS NOT NULL;

COMMIT;
```

## Backup Strategy

### Automated Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL | gzip > "$BACKUP_DIR/mrwa_$DATE.sql.gz"

# Keep only last 7 days
find $BACKUP_DIR -name "mrwa_*.sql.gz" -mtime +7 -delete
```

### Point-in-Time Recovery

Supabase provides automatic PITR with 7-day retention on free tier.

## Performance Optimization

### Index Strategy

- Index foreign keys
- Index frequently queried columns
- Composite indexes for common query patterns
- Partial indexes where appropriate

### Query Optimization

```sql
-- Use EXPLAIN ANALYZE to understand query plans
EXPLAIN ANALYZE
SELECT * FROM executions WHERE user_id = $1 AND status = 'completed';

-- Add covering index if needed
CREATE INDEX idx_executions_user_status_created
ON executions(user_id, status, created_at DESC);
```

### Connection Pooling

```python
# SQLAlchemy engine configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

## Data Retention

### Retention Policy

- Active executions: Indefinite
- Completed executions: 90 days
- Failed executions: 30 days
- Logs: 30 days
- Revoked sessions: 7 days

### Cleanup Job

```sql
-- Run daily via cron job
DELETE FROM execution_logs
WHERE timestamp < NOW() - INTERVAL '30 days';

DELETE FROM executions
WHERE completed_at < NOW() - INTERVAL '90 days'
AND status = 'completed';

DELETE FROM sessions
WHERE revoked = TRUE
AND created_at < NOW() - INTERVAL '7 days';
```

## Security

### Row Level Security

```sql
-- Enable RLS
ALTER TABLE executions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own executions
CREATE POLICY executions_user_isolation ON executions
    FOR ALL
    USING (user_id = current_setting('app.user_id')::uuid);
```

### Encryption

- Passwords: bcrypt (cost factor 12)
- Sensitive data: pgcrypto
- At rest: Supabase encryption
- In transit: TLS 1.3

## Monitoring

### Key Metrics

- Connection pool utilization
- Query performance (slow queries > 1s)
- Table sizes and growth
- Index usage
- Cache hit ratio

### Queries for Monitoring

```sql
-- Find slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;
```
