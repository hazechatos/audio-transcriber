install: 
	python -m venv .venv-backend
	.venv-backend/Scripts/python -m pip install --upgrade pip
	.venv-backend/Scripts/python -m pip install -r backend/requirements.txt
	python -m venv .venv-frontend
	.venv-frontend/Scripts/python -m pip install --upgrade pip
	.venv-frontend/Scripts/python -m pip install -r frontend/requirements.txt

test:
	cd backend && ..\\.venv-backend\\Scripts\\python -m pytest

run-backend:
	cd backend && ..\\.venv-backend\\Scripts\\python -m uvicorn app.main:app --reload --port 8000

run-frontend:
	cd frontend && ..\\.venv-frontend\\Scripts\\python -m streamlit run streamlit_app.py --server.port 5173

run:
	powershell -NoProfile -Command "Start-Process -WindowStyle Normal -WorkingDirectory 'backend' '..\\.venv-backend\\Scripts\\python.exe' -ArgumentList @('-m','uvicorn','app.main:app','--reload','--port','8000')"
	powershell -NoProfile -Command "Start-Process -WindowStyle Normal -WorkingDirectory 'frontend' '..\\.venv-frontend\\Scripts\\python.exe' -ArgumentList @('-m','streamlit','run','streamlit_app.py','--server.port','5173')"


