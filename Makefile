# ============================================================================
# Makefile - Development Commands
# ============================================================================

.PHONY: help setup start stop test clean

help:
	@echo "MRWA Development Commands"
	@echo "========================="
	@echo "make setup     - Run initial setup"
	@echo "make start     - Start all services"
	@echo "make stop      - Stop all services"
	@echo "make test      - Run test suite"
	@echo "make clean     - Clean temporary files"
	@echo "make migrate   - Run database migrations"
	@echo "make logs      - Show service logs"

setup:
	./setup.sh

start:
	./quickstart.sh

stop:
	@if [ -f .backend.pid ]; then kill `cat .backend.pid` 2>/dev/null || true; fi
	@if [ -f .frontend.pid ]; then kill `cat .frontend.pid` 2>/dev/null || true; fi
	@rm -f .backend.pid .frontend.pid
	@echo "Services stopped"

test:
	./quickstart.sh --test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache htmlcov .coverage
	rm -f .backend.pid .frontend.pid

migrate:
	@source venv/bin/activate && alembic upgrade head

logs:
	@if [ -f backend.log ] && [ -f frontend.log ]; then \
		tail -f backend.log frontend.log; \
	else \
		echo "No log files found. Are services running?"; \
	fi

