import os
import logging
from collections import OrderedDict

import discord
from dotenv import load_dotenv

from translator import translate

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("translator-bot")

CONTEXT_LIMIT = 20
CACHE_SIZE = 512

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

client = discord.Client(intents=intents)

# Dedup cache: suppress duplicate translations when the same flag is reacted
# to the same message more than once.
_seen: "OrderedDict[tuple[int, str], bool]" = OrderedDict()


def _mark_seen(message_id: int, country_code: str) -> bool:
    key = (message_id, country_code)
    if key in _seen:
        return True
    _seen[key] = True
    if len(_seen) > CACHE_SIZE:
        _seen.popitem(last=False)
    return False


def flag_to_country_code(emoji_str: str) -> str | None:
    """Convert a Regional Indicator Symbol pair (🇯🇵) into its ISO country code (JP)."""
    if emoji_str is None or len(emoji_str) != 2:
        return None
    c1, c2 = emoji_str
    if not (0x1F1E6 <= ord(c1) <= 0x1F1FF and 0x1F1E6 <= ord(c2) <= 0x1F1FF):
        return None
    return chr(ord(c1) - 0x1F1E6 + ord("A")) + chr(ord(c2) - 0x1F1E6 + ord("A"))


@client.event
async def on_ready():
    log.info("Logged in as %s (id=%s)", client.user, client.user.id)


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == client.user.id:
        return

    country_code = flag_to_country_code(payload.emoji.name)
    if country_code is None:
        return

    if _mark_seen(payload.message_id, country_code):
        return

    try:
        channel = client.get_channel(payload.channel_id) or await client.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
    except (discord.NotFound, discord.Forbidden) as e:
        log.warning("could not fetch message: %s", e)
        return

    if not message.content.strip():
        return

    # Gather up to CONTEXT_LIMIT prior messages, oldest first, skipping bot
    # messages and empty content.
    context = []
    async for m in channel.history(limit=CONTEXT_LIMIT, before=message):
        if m.author.bot or not m.content.strip():
            continue
        context.append({"author": m.author.display_name, "content": m.content})
    context.reverse()

    try:
        async with channel.typing():
            translated = await translate(message.content, context, country_code)
    except Exception as e:
        log.exception("translation failed")
        await message.reply(f"⚠️ 翻訳に失敗: {e}", mention_author=False)
        return

    # Discord hard-caps messages at 2000 chars.
    CHUNK = 1900
    chunks = [translated[i : i + CHUNK] for i in range(0, len(translated), CHUNK)] or [""]
    reply = await message.reply(chunks[0], mention_author=False)
    for extra in chunks[1:]:
        await reply.channel.send(extra)


def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise SystemExit("DISCORD_TOKEN is not set. Copy .env.example to .env and fill it in.")
    client.run(token, log_handler=None)


if __name__ == "__main__":
    main()
