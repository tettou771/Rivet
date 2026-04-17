import os
from anthropic import AsyncAnthropic
from prompts import SYSTEM_PROMPT

MODEL = "claude-sonnet-4-6"

# Explicit hints for common country codes. Unknown codes fall through to a
# generic phrasing and let the model infer the language itself.
COUNTRY_TO_LANGUAGE = {
    "JP": "Japanese (日本語)",
    "KR": "Korean (한국어)",
    "US": "English",
    "GB": "English",
    "AU": "English",
    "CA": "English",
    "CN": "Simplified Chinese (简体中文)",
    "TW": "Traditional Chinese (繁體中文)",
    "HK": "Traditional Chinese (繁體中文)",
    "FR": "French (Français)",
    "DE": "German (Deutsch)",
    "ES": "Spanish (Español)",
    "IT": "Italian (Italiano)",
    "PT": "Portuguese (Português)",
    "BR": "Brazilian Portuguese",
    "RU": "Russian (Русский)",
    "NL": "Dutch (Nederlands)",
    "TH": "Thai (ไทย)",
    "VN": "Vietnamese (Tiếng Việt)",
    "ID": "Indonesian (Bahasa Indonesia)",
    "TR": "Turkish (Türkçe)",
    "PL": "Polish (Polski)",
    "SE": "Swedish (Svenska)",
    "NO": "Norwegian (Norsk)",
    "FI": "Finnish (Suomi)",
    "DK": "Danish (Dansk)",
}


def country_code_to_language(code: str) -> str:
    return COUNTRY_TO_LANGUAGE.get(code, f"the primary language of the country with ISO code {code}")


_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


async def translate(target_text: str, context_messages: list[dict], country_code: str) -> str:
    """Translate `target_text` into the language of `country_code`, using
    `context_messages` (oldest first, each {"author", "content"}) as context.
    """
    language = country_code_to_language(country_code)

    context_block = "\n".join(
        f"{m['author']}: {m['content']}" for m in context_messages
    ) or "(no prior context)"

    user_content = (
        f"Target language: {language}\n\n"
        f"--- CONTEXT (do not translate) ---\n"
        f"{context_block}\n"
        f"--- END CONTEXT ---\n\n"
        f"--- TARGET MESSAGE (translate this) ---\n"
        f"{target_text}\n"
        f"--- END TARGET ---"
    )

    response = await _get_client().messages.create(
        model=MODEL,
        max_tokens=2048,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_content}],
    )

    return "".join(b.text for b in response.content if b.type == "text").strip()
