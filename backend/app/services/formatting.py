import logging
from typing import Optional

from app.clients.openai_client import get_openai_client
from app.clients.mistral_client import get_mistral_client

logger = logging.getLogger(__name__)

PROVIDER = "mistral"

SYSTEM_INSTRUCTION = (
    "You are a professional notary making an observation. "
    "Rewrite and format the provided transcript into a clear, formal observation. "
    "- Keep factual, objective tone; avoid speculation.\n"
    "- Correct obvious transcription errors (names if confidently inferable; otherwise mark [inaudible] or [unintelligible]).\n"
    "- Use proper punctuation, paragraphs, and consistent tense.\n"
    "- Preserve dates, times, amounts, and legal-relevant details.\n"
    "- If content is in French, respond in French."
)

def format_transcript_openai(raw_text: str, *, model: str = "gpt-4o-mini", temperature: float = 0.2) -> str:
    if not raw_text or not raw_text.strip():
        logger.debug("Empty text provided, skipping formatting")
        return ""

    logger.info(f"Starting OpenAI formatting (model={model}, input_length={len(raw_text)} chars)")
    client = get_openai_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": raw_text},
        ],
        temperature=temperature,
    )
    content: Optional[str] = None
    if resp and resp.choices and resp.choices[0].message:
        content = resp.choices[0].message.content
    formatted = content or ""
    logger.info(f"OpenAI formatting completed. Output length: {len(formatted)} characters")
    return formatted



def format_transcript_mistral(raw_text: str, *, temperature: float = 0.2) -> str:
    if not raw_text or not raw_text.strip():
        logger.debug("Empty text provided, skipping formatting")
        return ""

    model = "mistral-medium-latest"
    logger.info(f"Starting Mistral formatting (model={model}, input_length={len(raw_text)} chars)")
    client = get_mistral_client()

    resp = client.chat.complete(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": raw_text},
        ],
        temperature=temperature,
    )
    content: Optional[str] = None
    if resp and resp.choices and resp.choices[0].message:
        content = resp.choices[0].message.content
    formatted = content or ""
    logger.info(f"Mistral formatting completed. Output length: {len(formatted)} characters")
    return formatted

def format_transcript(raw_text: str, *, temperature: float = 0.2):
    logger.debug(f"Formatting transcript with provider: {PROVIDER}")
    if PROVIDER == "mistral":
        return format_transcript_mistral(raw_text, temperature=temperature)
    elif PROVIDER == "openai":
        return format_transcript_openai(raw_text, temperature=temperature)
    else:
        logger.error(f"Unknown provider: {PROVIDER}")
        raise ValueError(f"Unknown provider: {PROVIDER}")