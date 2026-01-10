import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, List

logger = logging.getLogger(__name__)


SUPPORTED_AUDIO_EXTS: Tuple[str, ...] = (
    ".mp3", ".mp4", ".mpeg", ".mpga", ".m4a", ".wav", ".webm"
)


def is_supported_audio(path: Path) -> bool:
    return path.suffix.lower() in SUPPORTED_AUDIO_EXTS


def ensure_supported_or_convert_to_mp3(src: Path) -> Path:
    suffix = src.suffix.lower()
    if suffix in SUPPORTED_AUDIO_EXTS:
        logger.debug(f"Audio format {suffix} is already supported, no conversion needed")
        return src

    logger.info(f"Audio format {suffix} not supported, converting to MP3")
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found on PATH. Install ffmpeg to enable conversion.")

    tmp_dir = Path(tempfile.mkdtemp(prefix="audio_convert_"))
    dst = tmp_dir / (src.stem + ".mp3")
    logger.debug(f"Converting {src} to {dst}")

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
        logger.info(f"Audio conversion completed: {src} -> {dst}")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode(errors='ignore')
        logger.error(f"ffmpeg conversion failed: {error_msg}")
        raise RuntimeError(f"ffmpeg conversion failed: {error_msg}")

    if not dst.exists():
        logger.error("Conversion reported success but output file not found")
        raise RuntimeError("Conversion reported success but output file not found.")
    return dst




def concatenate_multi_files(sources: List[Path]) -> Path:
    """Concatenate multiple audio files into a single MP3 file.

    - If only one source is provided, returns it unchanged.
    - Converts inputs to MP3 first to ensure consistent formats, then uses ffmpeg
      concat demuxer to join them. Tries a copy-based concat first, falls back
      to re-encoding if needed.
    """
    if not sources:
        raise ValueError("No source files provided for concatenation.")

    if len(sources) == 1:
        # Nothing to concatenate
        return sources[0]

    logger.info(f"Concatenating {len(sources)} files")

    # Ensure each source is MP3 (convert when necessary)
    mp3_paths: List[Path] = []
    converted_tmp_dirs: List[Path] = []
    for src in sources:
        mp3 = ensure_supported_or_convert_to_mp3(src)
        mp3_paths.append(mp3)
        if mp3.parent.name.startswith("audio_convert_"):
            converted_tmp_dirs.append(mp3.parent)

    tmp_dir = Path(tempfile.mkdtemp(prefix="audio_concat_"))
    list_file = tmp_dir / "inputs.txt"

    # Write concat demuxer file
    with list_file.open("w", encoding="utf-8") as f:
        for p in mp3_paths:
            f.write(f"file '{p.resolve().as_posix()}'\n")

    dst = tmp_dir / "concatenated.mp3"

    # Try fast concat (copy) first
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(dst),
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info(f"Concatenation completed: {dst}")
    except subprocess.CalledProcessError:
        # Fallback to re-encoding
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-ar", "16000",
            "-ac", "1",
            "-c:a", "libmp3lame",
            "-b:a", "128k",
            str(dst),
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            logger.info(f"Concatenation (re-encode) completed: {dst}")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode(errors='ignore') if getattr(e, 'stderr', None) else ""
            logger.error(f"ffmpeg concatenation failed: {error_msg}")
            raise RuntimeError(f"ffmpeg concatenation failed: {error_msg}")

    if not dst.exists():
        logger.error("Concatenation reported success but output file not found")
        raise RuntimeError("Concatenation reported success but output file not found.")

    # Cleanup any intermediate conversion directories we created
    for d in converted_tmp_dirs:
        try:
            shutil.rmtree(d)
        except Exception:
            logger.warning(f"Failed to remove temporary dir {d}")

    return dst


def preprocess(srcs: List[Path]) -> Path:
    """Prepare uploaded files for transcription: concatenate (if needed) and
    ensure the result is a supported MP3 file.
    """
    concatenated = concatenate_multi_files(srcs)
    compatible_audio = ensure_supported_or_convert_to_mp3(concatenated)
    return compatible_audio
