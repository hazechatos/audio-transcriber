# Audio Transcription Assistant

This agent transcribes audio in multiple languages and formats the text to produce reports.

It was developed in collaboration with notary professionals who needed a convenient, self-hosted solution to transcribe on-the-go audio statements—typically recorded on a phone—and format them into clean, concise documents.

## Features

- Supports multiple audio formats: .mp3, .mp4, .mpeg, .mpga, .m4a, .wav, .webm
- Supports 2 languages: English and French.
- Formats transcribed text into a professional document, in different tones.

## Dev Setup

Only Windows is supported for now.

- Install dependencies and set up virtual environments:
```
make install
```

- Run unit tests:
```
make test
```


- Run the backend and frontend:
```
make run
```

Two terminals open. The first one is the backend process and shows backend logs in an easily-readable format.


## Todo
- add security
  - block requests with audio files that are too long (or monitor token usage and enforce a daily limit)
- refactor front-end:
  - change Streamlit to a clean React front-end

## Upcoming features:

- self-hosted version (getting Mistral builds from Hugging Face)