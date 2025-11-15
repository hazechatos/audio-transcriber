import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from app.services.transcriber import (
    transcribe_audio_file,
    transcribe_audio_file_mistral,
    transcribe_audio_file_openai,
)


@patch("app.services.transcriber.get_openai_client")
def test_transcribe_audio_file_openai_success(mock_get_client):
    """Test transcribe_audio_file_openai successfully transcribes audio."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_result = MagicMock()
    mock_result.text = "Transcribed text"
    
    mock_client.audio.transcriptions.create.return_value = mock_result
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file.write(b"fake audio data")
        file_path = Path(tmp_file.name)
    
    try:
        result = transcribe_audio_file_openai(file_path)
        
        assert result == "Transcribed text"
        mock_client.audio.transcriptions.create.assert_called_once()
        call_args = mock_client.audio.transcriptions.create.call_args
        assert call_args.kwargs["model"] == "whisper-1"
        assert call_args.kwargs["language"] is None
        assert call_args.kwargs["temperature"] == 0.0
    finally:
        file_path.unlink(missing_ok=True)


@patch("app.services.transcriber.get_openai_client")
def test_transcribe_audio_file_openai_with_language(mock_get_client):
    """Test transcribe_audio_file_openai uses language parameter."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_result = MagicMock()
    mock_result.text = "Transcribed text"
    
    mock_client.audio.transcriptions.create.return_value = mock_result
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file.write(b"fake audio data")
        file_path = Path(tmp_file.name)
    
    try:
        transcribe_audio_file_openai(file_path, language="fr")
        
        call_args = mock_client.audio.transcriptions.create.call_args
        assert call_args.kwargs["language"] == "fr"
    finally:
        file_path.unlink(missing_ok=True)


@patch("app.services.transcriber.get_openai_client")
def test_transcribe_audio_file_openai_with_temperature(mock_get_client):
    """Test transcribe_audio_file_openai uses temperature parameter."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_result = MagicMock()
    mock_result.text = "Transcribed text"
    
    mock_client.audio.transcriptions.create.return_value = mock_result
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file.write(b"fake audio data")
        file_path = Path(tmp_file.name)
    
    try:
        transcribe_audio_file_openai(file_path, temperature=0.3)
        
        call_args = mock_client.audio.transcriptions.create.call_args
        assert call_args.kwargs["temperature"] == 0.3
    finally:
        file_path.unlink(missing_ok=True)


@patch("app.services.transcriber.get_openai_client")
def test_transcribe_audio_file_openai_no_text_attribute(mock_get_client):
    """Test transcribe_audio_file_openai returns empty string when result has no text."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_result = MagicMock()
    del mock_result.text  # Remove text attribute
    
    mock_client.audio.transcriptions.create.return_value = mock_result
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file.write(b"fake audio data")
        file_path = Path(tmp_file.name)
    
    try:
        result = transcribe_audio_file_openai(file_path)
        assert result == ""
    finally:
        file_path.unlink(missing_ok=True)


@patch("app.services.transcriber.get_mistral_client")
def test_transcribe_audio_file_mistral_success(mock_get_client):
    """Test transcribe_audio_file_mistral successfully transcribes audio."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_result = MagicMock()
    mock_result.text = "Transcribed text"
    
    mock_client.audio.transcriptions.complete.return_value = mock_result
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file.write(b"fake audio data")
        file_path = Path(tmp_file.name)
    
    try:
        result = transcribe_audio_file_mistral(file_path)
        
        assert result == "Transcribed text"
        mock_client.audio.transcriptions.complete.assert_called_once()
        call_args = mock_client.audio.transcriptions.complete.call_args
        assert call_args.kwargs["model"] == "voxtral-mini-latest"
        assert call_args.kwargs["language"] is None
        assert call_args.kwargs["temperature"] == 0.0
        assert "file" in call_args.kwargs
    finally:
        file_path.unlink(missing_ok=True)


@patch("app.services.transcriber.get_mistral_client")
def test_transcribe_audio_file_mistral_with_language(mock_get_client):
    """Test transcribe_audio_file_mistral uses language parameter."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_result = MagicMock()
    mock_result.text = "Transcribed text"
    
    mock_client.audio.transcriptions.complete.return_value = mock_result
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file.write(b"fake audio data")
        file_path = Path(tmp_file.name)
    
    try:
        transcribe_audio_file_mistral(file_path, language="en")
        
        call_args = mock_client.audio.transcriptions.complete.call_args
        assert call_args.kwargs["language"] == "en"
    finally:
        file_path.unlink(missing_ok=True)


@patch("app.services.transcriber.get_mistral_client")
def test_transcribe_audio_file_mistral_no_text_attribute(mock_get_client):
    """Test transcribe_audio_file_mistral returns empty string when result has no text."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_result = MagicMock()
    del mock_result.text  # Remove text attribute
    
    mock_client.audio.transcriptions.complete.return_value = mock_result
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file.write(b"fake audio data")
        file_path = Path(tmp_file.name)
    
    try:
        result = transcribe_audio_file_mistral(file_path)
        assert result == ""
    finally:
        file_path.unlink(missing_ok=True)


@patch("app.services.transcriber.PROVIDER", "openai")
@patch("app.services.transcriber.transcribe_audio_file_openai")
def test_transcribe_audio_file_openai_provider(mock_transcribe_openai):
    """Test transcribe_audio_file calls transcribe_audio_file_openai when provider is openai."""
    mock_transcribe_openai.return_value = "Transcribed"
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file.write(b"fake audio data")
        file_path = Path(tmp_file.name)
    
    try:
        from app.services import transcriber
        result = transcriber.transcribe_audio_file(file_path, language="fr", temperature=0.2)
        
        assert result == "Transcribed"
        mock_transcribe_openai.assert_called_once_with(
            file_path, language="fr", temperature=0.2
        )
    finally:
        file_path.unlink(missing_ok=True)


@patch("app.services.transcriber.PROVIDER", "mistral")
@patch("app.services.transcriber.transcribe_audio_file_mistral")
def test_transcribe_audio_file_mistral_provider(mock_transcribe_mistral):
    """Test transcribe_audio_file calls transcribe_audio_file_mistral when provider is mistral."""
    mock_transcribe_mistral.return_value = "Transcribed"
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file.write(b"fake audio data")
        file_path = Path(tmp_file.name)
    
    try:
        from app.services import transcriber
        result = transcriber.transcribe_audio_file(file_path, language=None, temperature=0.0)
        
        assert result == "Transcribed"
        mock_transcribe_mistral.assert_called_once_with(
            file_path, language=None, temperature=0.0
        )
    finally:
        file_path.unlink(missing_ok=True)


@patch("app.services.transcriber.PROVIDER", "unknown")
def test_transcribe_audio_file_unknown_provider():
    """Test transcribe_audio_file raises ValueError for unknown provider."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file.write(b"fake audio data")
        file_path = Path(tmp_file.name)
    
    try:
        from app.services import transcriber
        with pytest.raises(ValueError, match="Unknown provider"):
            transcriber.transcribe_audio_file(file_path, language=None, temperature=0.0)
    finally:
        file_path.unlink(missing_ok=True)

