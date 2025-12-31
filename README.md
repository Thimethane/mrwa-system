# 🚀 MRWA - Marathon Research & Workflow Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)

An autonomous AI research and workflow agent that plans, executes, validates, and self-corrects. Built for cross-platform session syncing and transparent operation.

## ✨ Features

- 🤖 **Autonomous Execution**: Plans and executes complex workflows without human intervention
- 🔍 **Multi-Modal Input**: Process PDFs, code, URLs, and YouTube videos
- ✅ **Self-Validation**: Validates every step output and detects failures
- 🔧 **Self-Correction**: Automatically analyzes and corrects execution errors
- 🔐 **Authentication**: Secure login/signup with JWT tokens
- 🔄 **Cross-Platform Sync**: Sessions sync across web and future mobile apps
- 📊 **Real-Time Dashboard**: Live execution monitoring and logs
- 💾 **Persistent Storage**: All executions and artifacts stored securely
- 🆓 **Free Deployment**: Runs on free tiers (Fly.io + Vercel)

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/Thimethane/mrwa-system.git
cd mrwa

# Run automated setup
./setup.sh

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Launch

```bash
# Start all services
./quickstart.sh

# Or start individually
./quickstart.sh --backend-only
./quickstart.sh --frontend-only

# Run tests
./quickstart.sh --test
```

Access the dashboard at: **http://localhost:3000**

## 📖 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Authentication System](docs/AUTH.md)
- [Database Schema](docs/DATABASE.md)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Web Dashboard                        │
│              (React + Next.js + Auth)                    │
└────────────────────┬────────────────────────────────────┘
                     │ REST API + WebSocket
┌────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Orchestrator │  │  Validation  │  │  Correction  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Gemini 3 Integration                    │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│            PostgreSQL + Redis + S3                       │
│         (User Data, Sessions, Artifacts)                 │
└─────────────────────────────────────────────────────────┘
./quickstart.sh --backend-only
./quickstart.sh --frontend-only

# Run tests
./quickstart.sh --test
```

Access the dashboard at: **http://localhost:3000**
```

## 🔐 Authentication Flow

1. User signs up/logs in via web dashboard
2. JWT token issued and stored securely
3. All API requests authenticated via Bearer token
4. Sessions synced across devices using user ID
5. Refresh tokens enable seamless re-authentication

## 📊 Execution Flow

1. **Input**: User uploads PDF/code or provides URL
2. **Planning**: Gemini 3 generates multi-step execution plan
3. **Execution**: Each step runs autonomously with state tracking
4. **Validation**: Output validated against expected criteria
5. **Correction**: Failed steps analyzed and corrected automatically
6. **Artifact**: Verified output generated and stored
7. **Sync**: Execution history synced to user account

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/e2e/ -v

# Run with coverage
pytest --cov=core --cov-report=html
```

## 📦 Deployment

### Backend (Fly.io)

```bash
cd mrwa
fly launch
fly secrets set GEMINI_API_KEY=your_key
fly secrets set JWT_SECRET=your_secret
fly deploy
```

### Frontend (Vercel)

```bash
cd platforms/web
vercel --prod
```

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

## 🛠️ Technology Stack

**Backend:**
- FastAPI (Python web framework)
- PostgreSQL (User and execution data)
- Redis (Session caching and real-time updates)
- Google Gemini 3 (AI planning and correction)

**Frontend:**
- React 18
- Next.js 14
- Tailwind CSS
- Lucide Icons

**Infrastructure:**
- Fly.io (Backend hosting)
- Vercel (Frontend hosting)
- Upstash Redis (Free tier)
- Supabase PostgreSQL (Free tier)

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini for AI capabilities
- FastAPI for the amazing web framework

## 📞 Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/Thimethane/mrwa/issues)
- Discussions: [GitHub Discussions](https://github.com/Thimethane/mrwa/discussions)

---

Built with ❤️ for autonomous AI research
