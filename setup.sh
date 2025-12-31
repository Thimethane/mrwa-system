#!/bin/bash

set -e

cat << "EOF"
╔═══════════════════════════════════════════════════════════╗
║  MRWA Setup - Marathon Research & Workflow Agent         ║
║  Autonomous AI Research System with Cross-Platform Sync  ║
╚═══════════════════════════════════════════════════════════╝
EOF

echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info()    { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error()   { echo -e "${RED}✗${NC} $1"; }

# Helper to create file if it doesn't exist
create_file_if_missing() {
    local filepath="$1"
    local content="$2"
    if [[ -f "$filepath" ]]; then
        log_warning "File '$filepath' already exists, skipping."
    else
        mkdir -p "$(dirname "$filepath")"
        echo "$content" > "$filepath"
        log_success "Created '$filepath'"
    fi
}

# ============================================================================
# Check prerequisites
# ============================================================================
echo ""
log_info "Checking prerequisites..."

check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 is not installed"
        echo "   Please install $1 and try again"
        echo "   Visit: $2"
        exit 1
    else
        log_success "$1 found ($(command -v $1))"
    fi
}

check_command python3 "https://www.python.org/downloads/"
check_command node "https://nodejs.org/"
check_command npm "https://nodejs.org/"
check_command git "https://git-scm.com/"

# Python version check
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if (( $(echo "$PYTHON_VERSION < 3.9" | bc -l) )); then
    log_error "Python 3.9+ required (found $PYTHON_VERSION)"
    exit 1
fi
log_success "Python version $PYTHON_VERSION meets requirements"

# Node version check
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    log_error "Node.js 18+ required (found v$NODE_VERSION)"
    exit 1
fi
log_success "Node.js version meets requirements"

# ============================================================================
# Create directory structure
# ============================================================================
echo ""
log_info "Creating project structure..."
mkdir -p mrwa/{docs,core/{orchestrator,validation,correction,gemini_integration,auth,database,storage},ingestion/{document_parser,code_analyzer,web_scraper,media_processor},platforms/web/{src/{components,pages,lib,hooks,styles},public},samples/{research_papers,code_repositories,test_data},tests/{unit,integration,e2e},scripts,config}
log_success "Directory structure created"

cd mrwa || exit

# ============================================================================
# Documentation Files
# ============================================================================
echo ""
log_info "Creating documentation files..."

create_file_if_missing "README.md" '...PLACEHOLDER: full README.md content here...'
create_file_if_missing "docs/ARCHITECTURE.md" '...PLACEHOLDER: full ARCHITECTURE.md content here...'
create_file_if_missing "docs/API.md" '...PLACEHOLDER: full API.md content here...'
create_file_if_missing "docs/DEPLOYMENT.md" '...PLACEHOLDER: full DEPLOYMENT.md content here...'
create_file_if_missing "docs/AUTH.md" '...PLACEHOLDER: full AUTH.md content here...'
create_file_if_missing "docs/DATABASE.md" '...PLACEHOLDER: full DATABASE.md content here...'

# ============================================================================
# Run quickstart if exists
# ============================================================================
if [[ -f "./quicksart.sh" ]]; then
    log_info "Running quickstart script..."
    chmod +x ./quicksart.sh
    ./quicksart.sh
fi

log_success "Setup completed successfully!"
