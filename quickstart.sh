# ============================================================================
# quickstart.sh - One-Command Launch Script
# ============================================================================

#!/bin/bash

set -e

cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║              MRWA Quickstart Launcher                     ║
║  Starting autonomous research and workflow system...      ║
╚═══════════════════════════════════════════════════════════╝
EOF

echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if setup has been run
if [ ! -d "venv" ] || [ ! -d "platforms/web/node_modules" ]; then
    echo -e "${RED}❌ Setup not complete${NC}"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Handle flags
if [ "$1" == "--test" ]; then
    echo "🧪 Running test suite..."
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
    pytest tests/ -v --cov=core --cov-report=term-missing
    deactivate
    exit 0
fi

if [ "$1" == "--backend-only" ]; then
    echo "🚀 Starting backend only..."
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    exit 0
fi

if [ "$1" == "--frontend-only" ]; then
    echo "🚀 Starting frontend only..."
    cd platforms/web
    npm run dev
    exit 0
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check for Gemini API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  GEMINI_API_KEY not set${NC}"
    echo "Running in DEMO MODE with simulated responses"
    echo "To use real Gemini AI:"
    echo "  1. Get API key from https://makersuite.google.com/app/apikey"
    echo "  2. Add to .env file: GEMINI_API_KEY=your_key_here"
    echo ""
fi

echo "🔧 Starting MRWA services..."
echo ""

# Start backend
echo -e "${BLUE}Starting backend API...${NC}"
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
deactivate

sleep 3

# Check if backend started
if ! curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "Check backend.log for details"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"

# Start frontend
echo -e "${BLUE}Starting web dashboard...${NC}"
cd platforms/web
nohup npm run dev > ../../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

sleep 5

# Check if frontend started
if ! curl -s http://localhost:3000 > /dev/null; then
    echo -e "${YELLOW}⚠️  Frontend may still be starting...${NC}"
fi

echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ MRWA is running!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📊 Dashboard:${NC}     http://localhost:3000"
echo -e "${BLUE}📚 API Docs:${NC}      http://localhost:8000/docs"
echo -e "${BLUE}💚 Health Check:${NC}  http://localhost:8000/api/v1/health"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo -e "${YELLOW}🛑 Stop Services:${NC}"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   Or press Ctrl+C"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Save PIDs for cleanup
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# Cleanup function
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    rm -f .backend.pid .frontend.pid
    echo "Services stopped"
    exit 0
}

trap cleanup INT TERM

# Wait for processes
wait