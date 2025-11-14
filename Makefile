install:
	python -m venv .venv-backend
	.venv-backend/Scripts/python -m pip install --upgrade pip
	.venv-backend/Scripts/python -m pip install -r backend/requirements.txt
	cd frontend && npm i

test:
	cd backend && ..\\.venv-backend\\Scripts\\python -m pytest

run-backend:
	cd backend && ..\\.venv-backend\\Scripts\\python -m uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && npm run dev

run:
	powershell -NoProfile -Command "Start-Process -WindowStyle Normal -WorkingDirectory 'backend' '..\\.venv-backend\\Scripts\\python.exe' -ArgumentList @('-m','uvicorn','app.main:app','--reload','--port','8000')"
	powershell -NoProfile -Command "Start-Process -WindowStyle Normal -WorkingDirectory 'frontend' 'cmd.exe' -ArgumentList @('/c','npm','run','dev')"
