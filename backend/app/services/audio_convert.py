import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple


SUPPORTED_AUDIO_EXTS: Tuple[str, ...] = (
    ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"
)


def is_supported_audio(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_AUDIO_EXTS


def ensure_supported_or_convert_to_mp3(src: Path) -> Path:
    suffix = src.suffix.lower()
    if suffix in SUPPORTED_AUDIO_EXTS:
        return src

    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found on PATH. Install ffmpeg to enable conversion.")

    tmp_dir = Path(tempfile.mkdtemp(prefix="audio_convert_"))
    dst = tmp_dir / (src.stem + ".mp3")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(src),
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "libmp3lame",
        "-b:a", "128k",
        str(dst),
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg conversion failed: {e.stderr.decode(errors='ignore')}")

    if not dst.exists():
        raise RuntimeError("Conversion reported success but output file not found.")
    return dst


