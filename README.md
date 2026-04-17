# Rivet

**Rivet** is a Claude-powered Discord translator bot. React to any message with
a country flag (🇯🇵 🇰🇷 🇺🇸 🇨🇳 🇹🇼 🇫🇷 🇩🇪 🇪🇸 ...) and Rivet replies with a
translation into that country's language, using the surrounding messages as
context.

Named after the rivets that hold a truss together — a small but essential
joint in the [TrussC](https://github.com/tettou771/TrussC) ecosystem.

Any Regional-Indicator flag works: the ISO country code is extracted from the
emoji and passed straight to Claude, so there's no hard-coded flag list.

## Features
- 🚩 Flag-reaction triggered translation (🇯🇵🇰🇷🇺🇸🇨🇳🇹🇼🇫🇷🇩🇪🇪🇸 and more)
- 🧵 Works in channels and inside threads — replies preserve the location
- 📜 Pulls up to 20 prior messages as context for natural, on-topic translation
- 🎨 Tuned for creative coding / C++ / shaders — technical English terms stay
  in English instead of being force-translated into katakana
- 🔁 Dedup cache so the same (message × flag) won't translate twice

## Setup

### 1. Create the Discord bot
1. https://discord.com/developers/applications → **New Application** (name it `Rivet`).
2. **Bot** tab → **Reset Token** → copy the token (this is `DISCORD_TOKEN`).
3. **Privileged Gateway Intents** → enable:
   - `MESSAGE CONTENT INTENT`
   - `SERVER MEMBERS INTENT`
4. **OAuth2 → URL Generator**:
   - Scopes: `bot`
   - Bot Permissions:
     - `View Channels`
     - `Send Messages`
     - `Send Messages in Threads`
     - `Read Message History`
     - `Embed Links`
     - `Use External Emojis`
5. Open the generated URL and invite Rivet to your server.

### 2. Get an Anthropic API key
https://console.anthropic.com/ → **API Keys** → Create Key.

### 3. Install (venv)
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env, fill in DISCORD_TOKEN and ANTHROPIC_API_KEY
```

### 4. Run
```sh
python bot.py
```

## Usage
Add a country-flag reaction to any message. Rivet replies in that language.
Works in channels and inside threads. Duplicate (message × flag) reactions are
ignored.

## Deploy on Ubuntu (systemd)
```sh
sudo useradd -r -m -d /opt/rivet rivet
sudo -u rivet git clone <this-repo-url> /opt/rivet
cd /opt/rivet
sudo -u rivet python3 -m venv .venv
sudo -u rivet .venv/bin/pip install -r requirements.txt
sudo -u rivet cp .env.example .env
sudo -u rivet vi .env   # fill in tokens

sudo cp systemd/rivet.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now rivet
```

Logs: `journalctl -u rivet -f`

## Layout
```
bot.py            # Discord client, reaction handler
translator.py     # Claude API wrapper (prompt caching enabled)
prompts.py        # System prompt (creative coding / C++ / TrussC context)
requirements.txt
.env.example
systemd/
  rivet.service   # Ubuntu deploy unit file
```
