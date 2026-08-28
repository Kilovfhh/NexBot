# NexBot

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.x-5865F2?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![Gemini](https://img.shields.io/badge/Gemini-AI-8E75FF?logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-Private-red)](LICENSE_EN)
[![Status](https://img.shields.io/badge/Status-Private%20Bot-2ea44f)]()

A private Discord bot for server moderation, community tools, Gemini-powered assistance, and voice-channel enforcement.

NexBot is intended for authorized use in a controlled Discord server. It includes administrative commands, logging, and custom security tooling.

> Please review [LICENSE_EN](LICENSE_EN) or [LICENSE_ES](LICENSE_ES) before using, modifying, or distributing the project.

---

## Features

- AI-powered chat with Google Gemini
- Community utilities, including meme generation through Giphy
- Moderation commands for authorized staff
- Voice activity monitoring and auto-mute support
- Administrative logging and developer diagnostics

---

## Project Structure

```text
NexBot/
├── LICENSE_EN
├── LICENSE_ES
├── README.MD
├── bot.py
├── config.py
├── requirements.txt
├── commands/
│   ├── __init__.py
│   └── community.py
├── gemini/
│   ├── __init__.py
│   ├── ai_config.py
│   └── testing.py
├── security/
│   ├── __init__.py
│   ├── adminCommands.py
│   ├── automutevc.py
│   └── assets/
├── nexa_banners/
│   └── banners.py
├── dev/
    └── drugs_are_cool.py
```

---

## Requirements

Before starting NexBot, install:

- Python 3.10+
- discord.py
- python-dotenv
- termcolor
- colorama
- google-genai
- requests
- numpy
- discord-ext-voice-recv

---

## Installation and Setup

1. Use Python 3.10 or newer.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Create `config.py` in the project root before starting the bot.
4. Copy the following template into `config.py`:

```python
"""
Setup config.py before running this bot.
"""

# Discord bot token or webhook value used by your deployment
WEBHOOK_URL = ""

# Primary Discord server ID
guild1 = None

# Giphy API key for meme commands
GIPHY = ""

# Staff permission IDs
OWNERID = None  # Full bot permissions
ADMINID = None  # Administrative permissions
MODID = None  # Moderation permissions

# Developer mention used by developer options
DEVELOPER = "<@your_id>"

# Discord server ID for community commands
CommunityCommands = None

# Google Gemini API key
Gemini = ""

# Logging channel IDs
ALL_LOGS = None
kick = None
bans = None
mute = None
purge = None

# Administrative logging channel ID
ADMIN_LOGS = None
```

5. Replace the placeholder values with your Discord server IDs, API keys, staff IDs, and logging channel IDs. Keep tokens and API keys private.
6. Start NexBot:

```bash
python bot.py
```

> `config.py` must be configured before startup. NexBot reads its runtime settings from this file and does not use a `.env` file.

---

## Commands

The command prefix is `^`.

| Command | Description |
| --- | --- |
| `^ai <question>` | Sends a question to Gemini and posts the response. |
| `^gmeme` | Posts a random meme from Giphy. |
| `^ban @user [reason]` | Bans a user when the required permissions are present. |
| `^purge [amount]` | Deletes recent messages from the current channel. |
| `^hadmin` | Opens the administrator help panel. |
| `^devmenu` | Opens the developer diagnostics panel. |

---

## Voice Monitoring

The voice moderation module in [security/automutevc.py](security/automutevc.py) monitors voice activity and supports moderation actions in voice channels.

---

## Startup Flow

The entry point is [bot.py](bot.py). At startup, it:

1. checks dependencies
2. loads values from `config.py`
3. creates the Discord bot client
4. loads command and security modules
5. connects to Discord

---

## Notes

- This is a private project intended for a controlled Discord environment.
- Access, usage, and redistribution are governed by the project license.
- Only authorized users should be given access to the source code or deployment environment.

---

## License

This project is protected under a private proprietary license. See [LICENSE_EN](LICENSE_EN) or [LICENSE_ES](LICENSE_ES) for the complete legal terms and restrictions.

---

## Developer

Nexa (aka itzokay)

Built with Python, Discord.py, Gemini AI, and custom automation for private server operations.
