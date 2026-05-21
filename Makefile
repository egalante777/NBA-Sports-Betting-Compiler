# NBA Sports Betting Compiler - Makefile
#
# Usage: make <command>
#
# Commands:
#   help         Show this help message
#   setup        Initial project setup
#   dev          Start development servers
#   test         Run all tests
#   backend      Start only backend server
#   frontend     Start only frontend server
#   build        Build for production
#   clean        Clean up temporary files
#   docker       Run with Docker Compose
#   api-docs     Open API documentation
#   health       Check service health
#   api-status   Check API conservation status

.PHONY: help setup dev test backend frontend build clean docker api-docs health api-status

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)NBA Sports Betting Compiler$(NC)"
	@echo "$(BLUE)=============================$(NC)"
	@echo ""
	@echo "Available commands:"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(GREEN)%-12s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  make setup    # First time setup"
	@echo "  make dev      # Start development"
	@echo "  make test     # Run tests"

setup: ## Initial project setup and dependency installation
	@echo "$(BLUE)🏀 Setting up NBA Betting Compiler...$(NC)"
	@echo "$(YELLOW)📦 Installing backend dependencies...$(NC)"
	cd backend && python3 -m venv venv
	cd backend && source venv/bin/activate && pip install --upgrade pip
	cd backend && source venv/bin/activate && pip install -r requirements.txt
	@echo "$(YELLOW)📦 Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)✅ Setup complete!$(NC)"
	@echo "$(BLUE)Next: Run 'make dev' to start development servers$(NC)"

dev: ## Start both backend and frontend development servers
	@echo "$(BLUE)🚀 Starting NBA Betting Compiler Development Environment...$(NC)"
	@./scripts/start-dev.sh

stop: ## Stop both backend and frontend development servers
	@./scripts/stop-dev.sh

backend: ## Start only the FastAPI backend server
	@echo "$(BLUE)🔧 Starting FastAPI backend server...$(NC)"
	@echo "$(YELLOW)Backend will be available at: http://localhost:8000$(NC)"
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend: ## Start only the React frontend server
	@echo "$(BLUE)⚛️  Starting React frontend server...$(NC)"
	@echo "$(YELLOW)Frontend will be available at: http://localhost:3000$(NC)"
	cd frontend && npm start

test: ## Run all tests and health checks
	@echo "$(BLUE)🧪 Running NBA Betting Compiler Tests...$(NC)"
	@./scripts/test-api.sh

test-live-backend: ## Test only backend endpoints (live)
	@echo "$(BLUE)🔍 Testing Backend API...$(NC)"
	@curl -s http://localhost:8000/health | jq . || echo "$(RED)❌ Backend not running$(NC)"
	@curl -s http://localhost:8000/api/games/today | jq '. | length' | xargs -I {} echo "$(GREEN)✅ Found {} games$(NC)"

test-live-frontend: ## Test only frontend accessibility (live)
	@echo "$(BLUE)🌐 Testing Frontend...$(NC)"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3000 || echo "$(RED)❌ Frontend not accessible$(NC)"

health: ## Check health of all services
	@echo "$(BLUE)🩺 Checking Service Health...$(NC)"
	@echo "Backend API:"
	@curl -s http://localhost:8000/health 2>/dev/null | jq -r '.status // "❌ Not running"' | sed 's/healthy/$(GREEN)✅ Healthy$(NC)/'
	@echo "Frontend:"
	@curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null | sed 's/200/$(GREEN)✅ Running$(NC)/' | sed 's/000/$(RED)❌ Not running$(NC)/'

api-status: ## Check API conservation status and credit usage
	@./scripts/api-status.sh

build: ## Build for production
	@echo "$(BLUE)🏗️  Building for production...$(NC)"
	cd frontend && npm run build
	@echo "$(GREEN)✅ Production build complete$(NC)"

clean: ## Clean up temporary files and dependencies
	@echo "$(BLUE)🧹 Cleaning up...$(NC)"
	cd backend && rm -rf venv __pycache__ .pytest_cache
	cd frontend && rm -rf node_modules build
	docker system prune -f 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

docker: ## Run with Docker Compose
	@echo "$(BLUE)🐳 Starting with Docker Compose...$(NC)"
	docker-compose up --build

docker-down: ## Stop Docker containers
	@echo "$(BLUE)🛑 Stopping Docker containers...$(NC)"
	docker-compose down

api-docs: ## Open API documentation in browser
	@echo "$(BLUE)📖 Opening API documentation...$(NC)"
	@command -v open >/dev/null 2>&1 && open http://localhost:8000/docs || echo "$(YELLOW)Visit: http://localhost:8000/docs$(NC)"

urls: ## Display all service URLs
	@echo "$(BLUE)🔗 Service URLs:$(NC)"
	@echo "  $(GREEN)Frontend:$(NC)     http://localhost:3000"
	@echo "  $(GREEN)Backend API:$(NC)  http://localhost:8000"
	@echo "  $(GREEN)API Docs:$(NC)     http://localhost:8000/docs"
	@echo "  $(GREEN)Health Check:$(NC) http://localhost:8000/health"

logs-backend: ## Show backend logs (if running in background)
	@echo "$(BLUE)📋 Backend Logs:$(NC)"
	@tail -f /private/tmp/claude-*/tasks/bsy2s28fs.output 2>/dev/null || echo "$(YELLOW)Backend not running in background$(NC)"

logs-frontend: ## Show frontend logs (if running in background)
	@echo "$(BLUE)📋 Frontend Logs:$(NC)"
	@tail -f /private/tmp/claude-*/tasks/b3yz5oyq4.output 2>/dev/null || echo "$(YELLOW)Frontend not running in background$(NC)"

install-hooks: ## Install git hooks for development
	@echo "$(BLUE)🪝 Installing git hooks...$(NC)"
	@echo "#!/bin/sh\nmake test" > .git/hooks/pre-push
	@chmod +x .git/hooks/pre-push
	@echo "$(GREEN)✅ Git hooks installed$(NC)"

# Environment-specific targets
dev-reset: clean setup ## Clean environment and reset everything
	@echo "$(GREEN)✅ Development environment reset complete$(NC)"

# Production helpers
prod-check: ## Check production readiness
	@echo "$(BLUE)🔍 Checking production readiness...$(NC)"
	@echo "$(YELLOW)Backend dependencies:$(NC)"
	cd backend && source venv/bin/activate && pip check
	@echo "$(YELLOW)Frontend build:$(NC)"
	cd frontend && npm run build --silent
	@echo "$(GREEN)✅ Production ready$(NC)"

# Database (future)
db-setup: ## Setup database (placeholder for future)
	@echo "$(YELLOW)⚠️  Database setup not implemented yet$(NC)"
	@echo "$(BLUE)Future: PostgreSQL for storing historical odds and user data$(NC)"

# Monitoring (future)
monitor: ## Start monitoring dashboard (placeholder for future)
	@echo "$(YELLOW)⚠️  Monitoring not implemented yet$(NC)"
	@echo "$(BLUE)Future: Grafana dashboard for API metrics$(NC)
# Data source management
mock-data: ## Switch to mock NBA data (for development)
	@echo "$(BLUE)🎭 Switching to MOCK NBA data...$(NC)"
	@echo "USE_REAL_DATA=false" > backend/.env
	@echo "NBA_DATA_SOURCE=mock" >> backend/.env
	@echo "$(GREEN)✅ Now using mock data - restart backend to apply$(NC)"

real-data: ## Switch to real NBA data (requires API keys)
	@echo "$(BLUE)🔴 Switching to REAL NBA data...$(NC)"
	@echo "USE_REAL_DATA=true" > backend/.env
	@echo "NBA_DATA_SOURCE=real" >> backend/.env
	@echo "$(YELLOW)⚠️  Add ODDS_API_KEY to backend/.env for betting odds$(NC)"
	@echo "$(GREEN)✅ Now using real data - restart backend to apply$(NC)"

data-status: ## Check current data source configuration
	@echo "$(BLUE)📊 Current Data Source Status:$(NC)"
	@curl -s http://localhost:8000/api/games/data-source 2>/dev/null | jq . || echo "$(RED)❌ Backend not running$(NC)"

# Testing commands
test-backend: ## Run backend tests with coverage
	@echo "$(BLUE)🧪 Running backend tests...$(NC)"
	cd backend && source venv/bin/activate && pytest -v --cov=app --cov-report=term-missing

test-frontend: ## Run frontend tests with coverage
	@echo "$(BLUE)🧪 Running frontend tests...$(NC)"
	cd frontend && npm test -- --coverage --watchAll=false

test-security: ## Run security audit
	@echo "$(BLUE)🔒 Running security audit...$(NC)"
	@./scripts/security-audit.sh

test-all: ## Run all tests (backend, frontend, security)
	@echo "$(BLUE)🧪 Running comprehensive test suite...$(NC)"
	@make test-backend
	@make test-frontend
	@make test-security
	@echo "$(GREEN)✅ All tests completed!$(NC)"

pytest: ## Run pytest directly (shorthand for backend tests)
	@echo "$(BLUE)🐍 Running pytest...$(NC)"
	cd backend && source venv/bin/activate && pytest

pytest-verbose: ## Run pytest with verbose output
	@echo "$(BLUE)🐍 Running pytest (verbose)...$(NC)"
	cd backend && source venv/bin/activate && pytest -v

pytest-coverage: ## Run pytest with coverage report
	@echo "$(BLUE)🐍 Running pytest with coverage...$(NC)"
	cd backend && source venv/bin/activate && pytest --cov=app --cov-report=html
