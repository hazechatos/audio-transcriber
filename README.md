# Audio Transcription Assistant

This agent transcribes audio in multiple languages and formats the text to produce reports.

It was developed in collaboration with notary professionals who needed a convenient, self-hosted solution to transcribe on-the-go audio statements—typically recorded on a phone—and format them into clean, concise documents.

## Features

- Supports multiple audio formats: .mp3, .mp4, .mpeg, .mpga, .m4a, .wav, .webm
- Supports 99 languages; this repo defaults to French.
- Formats transcribed text into a professional document, in different tones.
- Can be self-hosted.

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
- add security
  - block requests with audio files that are too long (or monitor token usage and enforce a daily limit)
- refactor front-end:
  - change Streamlit to a clean React front-end
  - add a Makefile (or another mean)