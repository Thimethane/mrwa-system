#!/usr/bin/env bash

set -e

echo "📁 Creating MRWA repository structure..."

# Helper function: create file if missing
touch_if_missing() {
  if [ ! -f "$1" ]; then
    mkdir -p "$(dirname "$1")"
    touch "$1"
    echo "✅ Created $1"
  else
    echo "⏭️  Skipped $1 (already exists)"
  fi
}

# Root files
touch_if_missing README.md
touch_if_missing LICENSE
touch_if_missing CONTRIBUTING.md
touch_if_missing .gitignore
touch_if_missing .env.example
touch_if_missing requirements.txt
touch_if_missing setup.sh
touch_if_missing quickstart.sh
touch_if_missing Dockerfile
touch_if_missing docker-compose.yml
touch_if_missing alembic.ini
touch_if_missing pytest.ini
touch_if_missing Makefile
touch_if_missing main.py

# Docs
touch_if_missing docs/ARCHITECTURE.md
touch_if_missing docs/API.md
touch_if_missing docs/DEPLOYMENT.md
touch_if_missing docs/AUTH.md
touch_if_missing docs/DATABASE.md

# Core
touch_if_missing core/__init__.py
touch_if_missing core/config.py
touch_if_missing core/database.py
touch_if_missing core/redis_client.py
touch_if_missing core/models.py

# Core subfolders
touch_if_missing core/auth/__init__.py
touch_if_missing core/auth/password.py
touch_if_missing core/auth/jwt_handler.py

touch_if_missing core/orchestrator/__init__.py
touch_if_missing core/orchestrator/engine.py

touch_if_missing core/validation/__init__.py
touch_if_missing core/validation/validator.py

touch_if_missing core/correction/__init__.py
touch_if_missing core/correction/corrector.py

touch_if_missing core/gemini_integration/__init__.py
touch_if_missing core/storage/__init__.py

# Ingestion
touch_if_missing ingestion/README.md
touch_if_missing ingestion/document_parser/__init__.py
touch_if_missing ingestion/code_analyzer/__init__.py
touch_if_missing ingestion/web_scraper/__init__.py
touch_if_missing ingestion/media_processor/__init__.py

# Platforms - Web
touch_if_missing platforms/web/README.md
touch_if_missing platforms/web/package.json
touch_if_missing platforms/web/next.config.js
touch_if_missing platforms/web/tailwind.config.js
touch_if_missing platforms/web/Dockerfile

# Platforms Web src structure
touch_if_missing platforms/web/src/components/Dashboard.jsx
touch_if_missing platforms/web/src/components/AuthForm.jsx
touch_if_missing platforms/web/src/components/ExecutionView.jsx

touch_if_missing platforms/web/src/pages/index.jsx

touch_if_missing platforms/web/src/lib/api.js

touch_if_missing platforms/web/src/hooks/useAuth.js

touch_if_missing platforms/web/src/styles/globals.css

touch_if_missing platforms/web/public/favicon.ico

# Tests
touch_if_missing tests/unit/test_orchestrator.py
touch_if_missing tests/unit/test_validator.py
touch_if_missing tests/unit/test_corrector.py

touch_if_missing tests/integration/test_auth_flow.py
touch_if_missing tests/integration/test_execution_flow.py

touch_if_missing tests/e2e/test_complete_workflow.py

# Migrations
touch_if_missing migrations/env.py
touch_if_missing migrations/versions/001_initial_schema.py

# Samples
touch_if_missing samples/README.md
touch_if_missing samples/links.txt
mkdir -p samples/research_papers samples/code_repositories samples/test_data

# Scripts
touch_if_missing scripts/create_admin.py
touch_if_missing scripts/backup_db.sh
touch_if_missing scripts/cleanup_old_executions.py

# Config
touch_if_missing config/development.py
touch_if_missing config/production.py
touch_if_missing config/testing.py

# Storage
mkdir -p storage/uploads storage/artifacts

echo "🎉 MRWA repository structure created successfully!"
