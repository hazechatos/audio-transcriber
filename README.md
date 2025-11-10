# Audio Transcription Assistant

This agent transcribes audio in multiple languages and formats the text to produce reports.

It was developed in collaboration with notary professionals who needed a convenient, self-hosted solution to transcribe on-the-go audio statements—typically recorded on a phone—and format them into clean, concise documents.

## Features

- Supports multiple audio formats: .mp3, .mp4, .mpeg, .mpga, .m4a, .wav, .webm
- Supports 99 languages; this repo defaults to French.
- Formats transcribed text into a professional document, in different tones.
- Can be self-hosted.

## Dev Setup

- Install dependencies and set up virtual environments:
```
make install
```

- Run the backend and frontend:
```
make run
```

## Todo
- add security
  - block requests with audio files that are too long (or monitor token usage and enforce a daily limit)
- refactor front-end:
  - change Streamlit to a clean React front-end