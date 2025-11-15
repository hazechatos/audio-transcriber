# Detect OS and set Python path
ifeq ($(OS),Windows_NT)
	PYTHON := .venv-backend/Scripts/python
	PYTHON_REL := ../.venv-backend/Scripts/python
else
	PYTHON := .venv-backend/bin/python
	PYTHON_REL := ../.venv-backend/bin/python
endif

install:
	python -m venv .venv-backend
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r backend/requirements.txt
	cd frontend && npm i

test:
	cd backend && $(PYTHON_REL) -m pytest

run-backend:
	cd backend && $(PYTHON_REL) -m uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev

run:
ifeq ($(OS),Windows_NT)
	powershell -NoProfile -Command "Start-Process -WindowStyle Normal -WorkingDirectory 'backend' '..\\.venv-backend\\Scripts\\python.exe' -ArgumentList @('-m','uvicorn','app.main:app','--reload','--port','8000')"
	powershell -NoProfile -Command "Start-Process -WindowStyle Normal -WorkingDirectory 'frontend' 'cmd.exe' -ArgumentList @('/c','npm','run','dev')"
else
	cd backend && $(PYTHON_REL) -m uvicorn app.main:app --reload --port 8000 &
	cd frontend && npm run dev &
endif
