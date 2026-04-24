.PHONY: help install-backend install-frontend run-backend run-frontend lint lint-backend lint-frontend test test-backend clean

PYTHON ?= python3.11
BACKEND_VENV := backend/.venv
BACKEND_PY := $(BACKEND_VENV)/bin/python
BACKEND_PIP := $(BACKEND_VENV)/bin/pip

help:
	@echo "Targets:"
	@echo "  install-backend    create venv and install backend deps"
	@echo "  install-frontend   install frontend npm deps"
	@echo "  run-backend        start the FastAPI + CV loop"
	@echo "  run-frontend       start the Vite dev server"
	@echo "  lint               run backend + frontend linters"
	@echo "  test               run backend tests"
	@echo "  clean              remove build artifacts and caches"

$(BACKEND_VENV):
	$(PYTHON) -m venv $(BACKEND_VENV)
	$(BACKEND_PIP) install --upgrade pip

install-backend: $(BACKEND_VENV)
	$(BACKEND_PIP) install -e "backend[dev]"

install-frontend:
	cd frontend && npm install

run-backend: $(BACKEND_VENV)
	$(BACKEND_PY) -m uvicorn app.main:app --reload --app-dir backend --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

lint-backend: $(BACKEND_VENV)
	$(BACKEND_VENV)/bin/ruff check backend

lint-frontend:
	cd frontend && npm run lint

lint: lint-backend lint-frontend

test-backend: $(BACKEND_VENV)
	$(BACKEND_VENV)/bin/pytest backend/tests

test: test-backend

clean:
	rm -rf $(BACKEND_VENV)
	rm -rf backend/**/__pycache__ backend/.pytest_cache backend/.ruff_cache
	rm -rf frontend/node_modules frontend/dist
