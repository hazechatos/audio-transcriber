from typing import Optional

from app.clients.openai_client import get_openai_client
from app.clients.mistral_client import get_mistral_client

PROVIDER = "mistral"

SYSTEM_INSTRUCTION_OPENAI = (
    "You are a professional notary making an observation. "
    "Rewrite and format the provided transcript into a clear, formal observation. "
    "- Keep factual, objective tone; avoid speculation.\n"
    "- Correct obvious transcription errors (names if confidently inferable; otherwise mark [inaudible] or [unintelligible]).\n"
    "- Use proper punctuation, paragraphs, and consistent tense.\n"
    "- Preserve dates, times, amounts, and legal-relevant details.\n"
    "- If content is in French, respond in French; otherwise respond in the source language."
)


SYSTEM_INSTRUCTION_MISTRAL = (
    "Vous êtes un notaire professionnel rédigeant une observation. "
    "Réécrivez et formatez la transcription fournie en une observation claire et formelle. "
    "- Conservez un ton factuel et objectif ; évitez la spéculation.\n"
    "- Corrigez les erreurs de transcription évidentes (noms si vous pouvez les inférer avec confiance ; sinon, marquez [inaudible] ou [inintelligible]).\n"
    "- Utilisez une ponctuation correcte, des paragraphes et un temps de conjugaison cohérent.\n"
    "- Préservez les dates, heures, montants et détails pertinents sur le plan juridique.\n"
    "- Si le contenu est en français, répondez en français ; sinon, répondez dans la langue source."
)

def format_transcript_openai(raw_text: str, *, model: str = "gpt-4o-mini", temperature: float = 0.2) -> str:
    if not raw_text or not raw_text.strip():
        return ""

    client = get_openai_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION_OPENAI},
            {"role": "user", "content": raw_text},
        ],
        temperature=temperature,
    )
    content: Optional[str] = None
    if resp and resp.choices and resp.choices[0].message:
        content = resp.choices[0].message.content
    return content or ""



def format_transcript_mistral(raw_text: str, *, temperature: float = 0.2) -> str:
    if not raw_text or not raw_text.strip():
        return ""

    model = "mistral-medium-latest"
    client = get_mistral_client()

    resp = client.chat.complete(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION_MISTRAL},
            {"role": "user", "content": raw_text},
        ],
        temperature=temperature,
    )
    content: Optional[str] = None
    if resp and resp.choices and resp.choices[0].message:
        content = resp.choices[0].message.content
    return content or ""

def format_transcript(raw_text: str, *, temperature: float = 0.2):
    if PROVIDER == "mistral":
        return format_transcript_mistral(raw_text, temperature=temperature)
    elif PROVIDER == "openai":
        return format_transcript_openai(raw_text, temperature=temperature)