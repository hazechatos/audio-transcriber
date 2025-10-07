# Speech-to-text finetuned for Virginie D.

## Dev Setup

Create venv and install
```
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Set env:
```
$env:OPENAI_API_KEY="sk-..."
$env:ALLOWED_ORIGINS="http://localhost:5173"
```

```
uvicorn app.main:app --reload --port 8000
```

```
streamlit run streamlit_app.py
```

## Build/run with Docker

### Backend (FastAPI)
```
docker build -t dransard-transcriber .
docker run --rm -e OPENAI_API_KEY=sk-... -p 8000:8000 dransard-transcriber
```

### Streamlit frontend
Build the Streamlit image (uses `Dockerfile.streamlit`). The container will try to reach the backend at `http://host.docker.internal:8000` by default. Override `API_BASE_URL` if needed.
```
docker build -f Dockerfile.streamlit -t dransard-transcriber-streamlit .
docker run --rm -e API_BASE_URL=http://host.docker.internal:8000 -p 8501:8501 dransard-transcriber-streamlit
```

Open `http://localhost:8501` and set the API base URL if different.

## Todo
- finish tests: 
  - ~~transcription~~
  - ~~formatting~~
  - audio format conversion
- deploy
  - do a basic front-end (Lovable)
  - deploy back-end as a single Python API
- add security
  - add login portal
  - block requests with audio files that are too long (or monitor token usage and enforce a daily limit)
- optimize costs
  - 

## Questions for Virginie D.

- Quelles sont vos habitudes d'enregistrements ? Prenez-vous plusieurs petits enregistrements, ou un long ?
  - Objectif : clarifier la nécessité de concaténer les audios