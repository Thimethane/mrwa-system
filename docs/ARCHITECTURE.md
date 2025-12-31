# MRWA Architecture

## System Overview

MRWA is a distributed autonomous AI system designed for research and workflow automation with cross-platform session synchronization.

## Core Components

### 1. Authentication Layer

**Purpose**: Secure user management and session handling

**Components**:
- JWT-based authentication
- Refresh token rotation
- Password hashing (bcrypt)
- Email verification
- Session management

**Database Schema**:
```sql
users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE,
  password_hash VARCHAR,
  created_at TIMESTAMP,
  last_login TIMESTAMP,
  email_verified BOOLEAN
)

sessions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  device_info JSONB,
  created_at TIMESTAMP,
  expires_at TIMESTAMP
)
```

### 2. Execution Engine

**Purpose**: Autonomous workflow planning and execution

**Components**:

#### Orchestrator
- Generates execution plans using Gemini 3
- Manages execution state machine
- Handles step dependencies and conditionals
- Implements retry logic with exponential backoff

```python
class ExecutionState:
    PLANNED = "planned"
    RUNNING = "running"
    VALIDATING = "validating"
    CORRECTING = "correcting"
    COMPLETED = "completed"
    FAILED = "failed"
```

#### Validator
- Schema-based output validation
- Content quality checks
- Format verification
- Completeness analysis

#### Corrector
- Failure root cause analysis
- Correction strategy generation
- Adaptive parameter adjustment
- Learning from past corrections

### 3. Data Ingestion Pipeline

**Multi-Modal Input Processing**:

#### PDF Parser
- Text extraction with layout preservation
- Table and figure detection
- Metadata extraction
- Citation parsing

#### Code Analyzer
- AST parsing for multiple languages
- Dependency graph generation
- Pattern detection
- Documentation extraction

#### Web Scraper
- Respectful crawling with rate limiting
- Content extraction
- Link analysis
- Metadata collection

#### Media Processor
- YouTube transcript extraction
- Video metadata parsing
- Timestamp identification
- Summary generation

### 4. Storage Layer

**Database (PostgreSQL)**:
```sql
executions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  input_type VARCHAR,
  input_value TEXT,
  status VARCHAR,
  plan JSONB,
  created_at TIMESTAMP,
  completed_at TIMESTAMP
)

execution_logs (
  id UUID PRIMARY KEY,
  execution_id UUID REFERENCES executions(id),
  timestamp TIMESTAMP,
  level VARCHAR,
  message TEXT,
  metadata JSONB
)

artifacts (
  id UUID PRIMARY KEY,
  execution_id UUID REFERENCES executions(id),
  type VARCHAR,
  data JSONB,
  file_url VARCHAR,
  verified BOOLEAN,
  created_at TIMESTAMP
)
```

**Cache (Redis)**:
- Session tokens
- Rate limiting counters
- Real-time execution state
- WebSocket connections

**Object Storage (S3)**:
- Uploaded files
- Generated artifacts
- Execution snapshots
- User data exports

## Data Flow

### Execution Flow

```
1. User Authentication
   ↓
2. Input Upload/Submission
   ↓
3. Input Validation & Storage
   ↓
4. Plan Generation (Gemini 3)
   ↓
5. Execution State Created
   ↓
6. For Each Step:
   a. Execute Step
   b. Validate Output
   c. If Failed → Correction Loop
   d. Log Everything
   ↓
7. Generate Artifact
   ↓
8. Store & Sync to User Account
   ↓
9. Notify User (WebSocket)
```

### Authentication Flow

```
1. Signup/Login Request
   ↓
2. Validate Credentials
   ↓
3. Generate JWT + Refresh Token
   ↓
4. Store Session in Redis
   ↓
5. Return Tokens to Client
   ↓
6. Client Stores in Secure Storage
   ↓
7. Subsequent Requests Include Bearer Token
   ↓
8. Token Validation Middleware
   ↓
9. Request Processing
```

## Security Architecture

### Authentication Security
- JWT tokens with short expiration (15 minutes)
- Refresh tokens with rotation
- HTTPS-only cookies for web
- Secure token storage

### API Security
- Rate limiting per user/IP
- Input sanitization
- SQL injection prevention
- XSS protection
- CORS configuration

### Data Security
- Passwords hashed with bcrypt (cost factor 12)
- Encryption at rest for sensitive data
- TLS for all communications
- Regular security audits

## Scalability Design

### Horizontal Scaling
- Stateless API servers
- Redis for shared session state
- PostgreSQL with read replicas
- S3 for distributed file storage

### Vertical Optimization
- Async I/O throughout
- Connection pooling
- Query optimization
- Caching strategies

### Performance Targets
- API response time: <200ms (p95)
- Execution start: <2s
- WebSocket latency: <50ms
- Concurrent users: 10,000+

## Monitoring & Observability

### Metrics
- Request latency (p50, p95, p99)
- Error rates by endpoint
- Execution success rate
- Gemini API usage
- Database query performance

### Logging
- Structured JSON logs
- Log levels: DEBUG, INFO, WARNING, ERROR
- Correlation IDs for request tracing
- Centralized log aggregation

### Alerting
- High error rates
- Slow API responses
- Gemini API failures
- Database connection issues
- Disk space warnings

## Disaster Recovery

### Backup Strategy
- Daily PostgreSQL backups
- Point-in-time recovery (7 days)
- S3 versioning enabled
- Configuration backups

### Recovery Procedures
- Database restore: <30 minutes
- Service recovery: <10 minutes
- Data loss tolerance: <1 hour

## Future Architecture Considerations

### Mobile App Integration
- Shared authentication via JWT
- GraphQL API for flexible queries
- Push notifications for execution updates
- Offline mode with sync queue

### Advanced Features
- Multi-tenant isolation
- Team collaboration
- Webhook integrations
- Custom workflow templates
- API rate tier management

## Technology Decisions

### Why FastAPI?
- Native async support
- Automatic API documentation
- Type safety with Pydantic
- High performance

### Why PostgreSQL?
- JSONB for flexible schema
- Strong consistency
- Rich query capabilities
- Excellent tooling

### Why Redis?
- Sub-millisecond latency
- Pub/sub for real-time updates
- Simple key-value operations
- Wide adoption

### Why Gemini 3?
- Advanced reasoning capabilities
- Large context window
- Competitive pricing
- Multimodal support
