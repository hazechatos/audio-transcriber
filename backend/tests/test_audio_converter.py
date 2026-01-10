import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.services.audio_converter import (
    SUPPORTED_AUDIO_EXTS,
    ensure_supported_or_convert_to_mp3,
    is_supported_audio,
    concatenate_multi_files,
    preprocess,
)


def test_is_supported_audio_supported_formats():
    """Test is_supported_audio returns True for supported formats."""
    for ext in SUPPORTED_AUDIO_EXTS:
        path = Path(f"test{ext}")
        assert is_supported_audio(path) is True
        # Test case insensitive
        path_upper = Path(f"test{ext.upper()}")
        assert is_supported_audio(path_upper) is True


def test_is_supported_audio_unsupported_format():
    """Test is_supported_audio returns False for unsupported formats."""
    unsupported = [".flac", ".ogg", ".aac", ".txt", ".pdf"]
    for ext in unsupported:
        path = Path(f"test{ext}")
        assert is_supported_audio(path) is False


def test_is_supported_audio_no_extension():
    """Test is_supported_audio returns False for files without extension."""
    path = Path("test")
    assert is_supported_audio(path) is False


def test_ensure_supported_or_convert_to_mp3_already_supported():
    """Test ensure_supported_or_convert_to_mp3 returns original path for supported formats."""
    for ext in SUPPORTED_AUDIO_EXTS:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
            src_path = Path(tmp_file.name)
        
        try:
            result = ensure_supported_or_convert_to_mp3(src_path)
            assert result == src_path
        finally:
            src_path.unlink(missing_ok=True)


@patch("app.services.audio_converter.shutil.which")
def test_ensure_supported_or_convert_to_mp3_ffmpeg_not_found(mock_which):
    """Test ensure_supported_or_convert_to_mp3 raises RuntimeError when ffmpeg is not found."""
    mock_which.return_value = None
    
    with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as tmp_file:
        src_path = Path(tmp_file.name)
    
    try:
        with pytest.raises(RuntimeError, match="ffmpeg not found on PATH"):
            ensure_supported_or_convert_to_mp3(src_path)
    finally:
        src_path.unlink(missing_ok=True)


@patch("app.services.audio_converter.subprocess.run")
@patch("app.services.audio_converter.shutil.which")
def test_ensure_supported_or_convert_to_mp3_conversion_success(
    mock_which, mock_subprocess_run
):
    """Test ensure_supported_or_convert_to_mp3 successfully converts unsupported format."""
    mock_which.return_value = "/usr/bin/ffmpeg"
    
    with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as tmp_file:
        src_path = Path(tmp_file.name)
        tmp_file.write(b"fake audio data")
    
    # Create a side effect that creates the output file when subprocess.run is called
    def create_output_file(*args, **kwargs):
        # Extract the output file path from the command arguments
        cmd = args[0] if args else kwargs.get("args", [])
        if len(cmd) > 0 and cmd[0] == "ffmpeg":
            # The last argument is the output file path
            output_path = Path(cmd[-1])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.touch()
        return MagicMock()
    
    mock_subprocess_run.side_effect = create_output_file
    
    try:
        result = ensure_supported_or_convert_to_mp3(src_path)
        
        # Verify the result is an MP3 file in a temp directory
        assert result.suffix == ".mp3"
        assert result.stem == src_path.stem
        assert result.exists()
        mock_subprocess_run.assert_called_once()
        assert mock_subprocess_run.call_args[0][0][0] == "ffmpeg"
        
        # Clean up the created temp directory
        if result.parent.exists():
            import shutil
            shutil.rmtree(result.parent, ignore_errors=True)
    finally:
        src_path.unlink(missing_ok=True)


@patch("app.services.audio_converter.subprocess.run")
@patch("app.services.audio_converter.shutil.which")
def test_ensure_supported_or_convert_to_mp3_conversion_failure(
    mock_which, mock_subprocess_run
):
    """Test ensure_supported_or_convert_to_mp3 raises RuntimeError when conversion fails."""
    import subprocess
    
    mock_which.return_value = "/usr/bin/ffmpeg"
    
    with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as tmp_file:
        src_path = Path(tmp_file.name)
        tmp_file.write(b"fake audio data")
    
    # Mock subprocess to raise CalledProcessError
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        1, "ffmpeg", stderr=b"Conversion error"
    )
    
    try:
        with pytest.raises(RuntimeError, match="ffmpeg conversion failed"):
            ensure_supported_or_convert_to_mp3(src_path)
    finally:
        src_path.unlink(missing_ok=True)


@patch("app.services.audio_converter.subprocess.run")
@patch("app.services.audio_converter.shutil.which")
def test_ensure_supported_or_convert_to_mp3_output_file_missing(
    mock_which, mock_subprocess_run
):
    """Test ensure_supported_or_convert_to_mp3 raises RuntimeError when output file is missing."""
    mock_which.return_value = "/usr/bin/ffmpeg"
    
    with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as tmp_file:
        src_path = Path(tmp_file.name)
        tmp_file.write(b"fake audio data")
    
    # Mock subprocess to succeed (simulating ffmpeg reports success)
    mock_subprocess_run.return_value = MagicMock()
    
    # Mock Path.exists to return False for the destination file check
    # We need to patch it on the Path class used in the module
    original_exists = Path.exists
    
    def mock_exists(self):
        # Return True for source file, False for destination MP3 file
        if self == src_path:
            return True
        # For destination files (MP3 in temp directory), return False
        if self.suffix == ".mp3" and "audio_convert_" in str(self.parent):
            return False
        return original_exists(self)
    
    try:
        # Patch Path.exists to simulate missing output file
        with patch("pathlib.Path.exists", mock_exists):
            with pytest.raises(RuntimeError, match="output file not found"):
                ensure_supported_or_convert_to_mp3(src_path)
    finally:
        src_path.unlink(missing_ok=True)


@patch("app.services.audio_converter.subprocess.run")
def test_concatenate_multi_files_multiple_files_success(mock_subprocess_run):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf1, tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf2:
        p1 = Path(tf1.name); p2 = Path(tf2.name)

    def create_output_file(*args, **kwargs):
        cmd = args[0] if args else kwargs.get("args", [])
        if len(cmd) > 0 and cmd[0] == "ffmpeg":
            output_path = Path(cmd[-1])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.touch()
        return MagicMock()

    mock_subprocess_run.side_effect = create_output_file

    try:
        result = concatenate_multi_files([p1, p2])
        assert result.suffix == ".mp3"
        assert result.exists()
        mock_subprocess_run.assert_called()
        if result.parent.exists():
            import shutil
            shutil.rmtree(result.parent, ignore_errors=True)
    finally:
        p1.unlink(missing_ok=True)
        p2.unlink(missing_ok=True)


def test_concatenate_multi_files_single_file():
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
        p = Path(tf.name)
    try:
        result = concatenate_multi_files([p])
        assert result == p
    finally:
        p.unlink(missing_ok=True)


@patch("app.services.audio_converter.ensure_supported_or_convert_to_mp3")
@patch("app.services.audio_converter.subprocess.run")
def test_preprocess_with_multiple_files(mock_subprocess_run, mock_ensure):
    # Simulate per-file conversion to mp3 by ensure_supported_or_convert_to_mp3
    def ensure_side(src):
        return Path(str(src.with_suffix(".mp3")))
    mock_ensure.side_effect = ensure_side

    def create_output_file(*args, **kwargs):
        cmd = args[0] if args else kwargs.get("args", [])
        if cmd and cmd[0] == "ffmpeg":
            output_path = Path(cmd[-1])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.touch()
        return MagicMock()

    mock_subprocess_run.side_effect = create_output_file

    with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as f1, tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as f2:
        p1 = Path(f1.name); p2 = Path(f2.name)
    try:
        result = preprocess([p1, p2])
        assert result.suffix == ".mp3"
        assert result.exists()
        mock_subprocess_run.assert_called()
    finally:
        p1.unlink(missing_ok=True); p2.unlink(missing_ok=True)
        if result.parent.exists():
            import shutil
            shutil.rmtree(result.parent, ignore_errors=True)

