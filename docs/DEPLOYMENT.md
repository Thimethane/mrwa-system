# MRWA Deployment Guide

This guide covers deploying MRWA to production using free tier services.

## Prerequisites

- Fly.io account (free tier)
- Vercel account (free tier)
- Google AI Studio account (Gemini API)
- Supabase account (PostgreSQL)
- Upstash account (Redis)

## Architecture

```
┌─────────────┐
│   Vercel    │  ← Frontend (Next.js)
│  (Frontend) │
└──────┬──────┘
       │ HTTPS
┌──────▼──────┐
│   Fly.io    │  ← Backend (FastAPI)
│  (Backend)  │
└──────┬──────┘
       │
  ┌────┴────┐
  │         │
┌─▼─────┐ ┌─▼─────┐
│Supabase│ │Upstash│
│  (DB)  │ │(Redis)│
└────────┘ └───────┘
```

## Step 1: Environment Variables

Create a `.env.production` file:

```bash
# Application
NODE_ENV=production
APP_NAME=MRWA
APP_VERSION=1.0.0

# Security
JWT_SECRET=<generate-secure-random-string-here>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database (Supabase)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis (Upstash)
REDIS_URL=redis://default:pass@host:6379

# AI Service
GEMINI_API_KEY=<your-gemini-api-key>
GEMINI_MODEL=gemini-pro

# Storage (optional - use Supabase storage)
STORAGE_PROVIDER=supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=<your-supabase-anon-key>

# CORS
CORS_ORIGINS=https://your-frontend.vercel.app

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60

# Monitoring
SENTRY_DSN=<optional-sentry-dsn>
LOG_LEVEL=info
```

## Step 2: Deploy Database (Supabase)

### 2.1 Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Choose a name and password
4. Select region closest to your users

### 2.2 Run Database Migrations

```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link project
supabase link --project-ref <your-project-ref>

# Run migrations
cd mrwa
supabase db push
```

### 2.3 Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE
);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    refresh_token VARCHAR(500) UNIQUE NOT NULL,
    device_info JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE
);

-- Executions table
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
    metadata JSONB
);

-- Execution logs table
CREATE TABLE execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID REFERENCES executions(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT NOW(),
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB
);

-- Artifacts table
CREATE TABLE artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID REFERENCES executions(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    data JSONB,
    file_url TEXT,
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_refresh_token ON sessions(refresh_token);
CREATE INDEX idx_executions_user_id ON executions(user_id);
CREATE INDEX idx_executions_status ON executions(status);
CREATE INDEX idx_execution_logs_execution_id ON execution_logs(execution_id);
CREATE INDEX idx_artifacts_execution_id ON artifacts(execution_id);
```

## Step 3: Deploy Redis (Upstash)

1. Go to [upstash.com](https://upstash.com)
2. Create a new Redis database
3. Select region (same as your backend)
4. Copy the Redis URL
5. Add to environment variables

## Step 4: Deploy Backend (Fly.io)

### 4.1 Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
```

### 4.2 Login and Initialize

```bash
fly auth login
cd mrwa
fly launch --no-deploy
```

### 4.3 Configure fly.toml

```toml
app = "mrwa-backend"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"
  script_checks = []

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.tcp_checks]]
    grace_period = "10s"
    interval = "15s"
    restart_limit = 0
    timeout = "2s"
```

### 4.4 Set Secrets

```bash
fly secrets set JWT_SECRET=your-secret
fly secrets set DATABASE_URL=your-db-url
fly secrets set REDIS_URL=your-redis-url
fly secrets set GEMINI_API_KEY=your-api-key
```

### 4.5 Deploy

```bash
fly deploy
```

## Step 5: Deploy Frontend (Vercel)

### 5.1 Install Vercel CLI

```bash
npm i -g vercel
```

### 5.2 Configure Environment

In Vercel dashboard, add environment variables:
- `NEXT_PUBLIC_API_URL`: Your Fly.io backend URL
- `NEXT_PUBLIC_APP_NAME`: MRWA

### 5.3 Deploy

```bash
cd platforms/web
vercel --prod
```

## Step 6: Post-Deployment

### 6.1 Verify Health

```bash
curl https://your-backend.fly.dev/api/v1/health
```

### 6.2 Test Authentication

```bash
curl -X POST https://your-backend.fly.dev/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

### 6.3 Monitor Logs

```bash
# Backend logs
fly logs

# Frontend logs (in Vercel dashboard)
```

## Scaling

### Backend Scaling (Fly.io)

```bash
# Scale to 2 instances
fly scale count 2

# Scale VM size
fly scale vm shared-cpu-2x
```

### Database Scaling (Supabase)

Upgrade to paid plan for:
- More connections
- Larger storage
- Point-in-time recovery

## Monitoring

### Health Checks

Setup monitoring at:
- [UptimeRobot](https://uptimerobot.com)
- [Better Uptime](https://betteruptime.com)

Monitor endpoints:
- `https://your-backend.fly.dev/api/v1/health`
- `https://your-frontend.vercel.app`

### Error Tracking

Integrate Sentry:

```bash
pip install sentry-sdk
```

```python
import sentry_sdk
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))
```

## Backup Strategy

### Database Backups

Supabase automatically backs up daily. For manual backups:

```bash
pg_dump $DATABASE_URL > backup.sql
```

### Application Backups

- Git for code
- Fly.io volume snapshots
- Export user data regularly

## Rollback Procedure

### Backend Rollback

```bash
# List deployments
fly releases

# Rollback to previous
fly releases rollback
```

### Frontend Rollback

In Vercel dashboard:
1. Go to Deployments
2. Find previous working deployment
3. Click "Promote to Production"

## Cost Estimate (Free Tier)

| Service | Free Tier | Cost If Exceeded |
|---------|-----------|------------------|
| Fly.io | 3 shared VMs | $0.0000022/sec |
| Vercel | 100GB bandwidth | $20/month pro |
| Supabase | 500MB storage | $25/month pro |
| Upstash | 10K commands/day | $0.2/100K |
| Gemini | 60 req/min | Pay per token |

**Total Monthly (Free Tier)**: $0
**Estimated at 1K users**: ~$50-100/month

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
psql $DATABASE_URL

# Check connection pool
fly ssh console
python -c "from core.database import engine; print(engine.pool.status())"
```

### Redis Connection Issues

```bash
# Test Redis
redis-cli -u $REDIS_URL ping
```

### Gemini API Issues

Check quota:
```bash
curl https://generativelanguage.googleapis.com/v1/models \
  -H "Authorization: Bearer $GEMINI_API_KEY"
```

## Security Checklist

- [ ] All secrets in environment variables
- [ ] HTTPS enforced everywhere
- [ ] CORS configured properly
- [ ] Rate limiting enabled
- [ ] Database backups automated
- [ ] Error tracking configured
- [ ] Health checks setup
- [ ] JWT secrets strong (32+ chars)
- [ ] Database passwords strong
- [ ] API keys restricted to backend only

## Support

For deployment issues:
- Fly.io: https://community.fly.io
- Vercel: https://vercel.com/support
- Supabase: https://supabase.com/docs
