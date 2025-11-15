from unittest.mock import MagicMock, patch

import pytest

from app.services.formatter import (
    format_transcript,
    format_transcript_mistral,
    format_transcript_openai,
)


@patch("app.services.formatter.get_openai_client")
def test_format_transcript_openai_success(mock_get_client):
    """Test format_transcript_openai successfully formats text."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = "Formatted text"
    
    mock_client.chat.completions.create.return_value = mock_response
    
    result = format_transcript_openai("Raw text")
    
    assert result == "Formatted text"
    mock_client.chat.completions.create.assert_called_once()
    call_args = mock_client.chat.completions.create.call_args
    assert call_args.kwargs["model"] == "gpt-4o-mini"
    assert call_args.kwargs["temperature"] == 0.2
    assert len(call_args.kwargs["messages"]) == 2


@patch("app.services.formatter.get_openai_client")
def test_format_transcript_openai_empty_text(mock_get_client):
    """Test format_transcript_openai returns empty string for empty input."""
    result = format_transcript_openai("")
    assert result == ""
    
    result = format_transcript_openai("   ")
    assert result == ""
    
    mock_get_client.assert_not_called()


@patch("app.services.formatter.get_openai_client")
def test_format_transcript_openai_custom_model_and_temperature(mock_get_client):
    """Test format_transcript_openai uses custom model and temperature."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = "Formatted"
    
    mock_client.chat.completions.create.return_value = mock_response
    
    format_transcript_openai("Text", model="gpt-4", temperature=0.5)
    
    call_args = mock_client.chat.completions.create.call_args
    assert call_args.kwargs["model"] == "gpt-4"
    assert call_args.kwargs["temperature"] == 0.5


@patch("app.services.formatter.get_openai_client")
def test_format_transcript_openai_no_content(mock_get_client):
    """Test format_transcript_openai returns empty string when response has no content."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = None
    
    mock_client.chat.completions.create.return_value = mock_response
    
    result = format_transcript_openai("Text")
    assert result == ""


@patch("app.services.formatter.get_mistral_client")
def test_format_transcript_mistral_success(mock_get_client):
    """Test format_transcript_mistral successfully formats text."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = "Formatted text"
    
    mock_client.chat.complete.return_value = mock_response
    
    result = format_transcript_mistral("Raw text")
    
    assert result == "Formatted text"
    mock_client.chat.complete.assert_called_once()
    call_args = mock_client.chat.complete.call_args
    assert call_args.kwargs["model"] == "mistral-medium-latest"
    assert call_args.kwargs["temperature"] == 0.2


@patch("app.services.formatter.get_mistral_client")
def test_format_transcript_mistral_empty_text(mock_get_client):
    """Test format_transcript_mistral returns empty string for empty input."""
    result = format_transcript_mistral("")
    assert result == ""
    
    result = format_transcript_mistral("   ")
    assert result == ""
    
    mock_get_client.assert_not_called()


@patch("app.services.formatter.get_mistral_client")
def test_format_transcript_mistral_custom_temperature(mock_get_client):
    """Test format_transcript_mistral uses custom temperature."""
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = "Formatted"
    
    mock_client.chat.complete.return_value = mock_response
    
    format_transcript_mistral("Text", temperature=0.7)
    
    call_args = mock_client.chat.complete.call_args
    assert call_args.kwargs["temperature"] == 0.7


@patch("app.services.formatter.PROVIDER", "openai")
@patch("app.services.formatter.format_transcript_openai")
def test_format_transcript_openai_provider(mock_format_openai):
    """Test format_transcript calls format_transcript_openai when provider is openai."""
    mock_format_openai.return_value = "Formatted"
    
    # Need to reload the module or patch the function directly
    from app.services import formatter
    result = formatter.format_transcript("Raw text")
    
    assert result == "Formatted"
    mock_format_openai.assert_called_once_with("Raw text", temperature=0.2)


@patch("app.services.formatter.PROVIDER", "mistral")
@patch("app.services.formatter.format_transcript_mistral")
def test_format_transcript_mistral_provider(mock_format_mistral):
    """Test format_transcript calls format_transcript_mistral when provider is mistral."""
    mock_format_mistral.return_value = "Formatted"
    
    from app.services import formatter
    result = formatter.format_transcript("Raw text")
    
    assert result == "Formatted"
    mock_format_mistral.assert_called_once_with("Raw text", temperature=0.2)


@patch("app.services.formatter.PROVIDER", "unknown")
def test_format_transcript_unknown_provider():
    """Test format_transcript raises ValueError for unknown provider."""
    from app.services import formatter
    
    with pytest.raises(ValueError, match="Unknown provider"):
        formatter.format_transcript("Raw text")


@patch("app.services.formatter.PROVIDER", "openai")
@patch("app.services.formatter.format_transcript_openai")
def test_format_transcript_custom_temperature(mock_format_openai):
    """Test format_transcript passes custom temperature to provider function."""
    mock_format_openai.return_value = "Formatted"
    
    from app.services import formatter
    formatter.format_transcript("Raw text", temperature=0.5)
    
    mock_format_openai.assert_called_once_with("Raw text", temperature=0.5)

