from typing import Optional

from app.clients.openai_client import get_openai_client


SYSTEM_INSTRUCTION = (
    "You are a professional notary making an observation. "
    "Rewrite and format the provided transcript into a clear, formal observation. "
    "- Keep factual, objective tone; avoid speculation.\n"
    "- Correct obvious transcription errors (names if confidently inferable; otherwise mark [inaudible] or [unintelligible]).\n"
    "- Use proper punctuation, paragraphs, and consistent tense.\n"
    "- Preserve dates, times, amounts, and legal-relevant details.\n"
    "- If content is in French, respond in French; otherwise respond in the source language."
)


def format_transcript(raw_text: str, *, model: str = "gpt-4o-mini", temperature: float = 0.2) -> str:
    if not raw_text or not raw_text.strip():
        return ""

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
    return content or ""


