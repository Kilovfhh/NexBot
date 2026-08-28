# NexBot

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Discord.py](https://img.shields.io/badge/Discord.py-2.x-5865F2?logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![Gemini](https://img.shields.io/badge/Gemini-AI-8E75FF?logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-Private-red)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Private%20Bot-2ea44f)]()

A private Discord bot for moderation, community engagement, AI interaction, and voice monitoring in a controlled server environment.

This project is intended for a specific deployment and includes custom moderation tools, Gemini-powered responses, and voice-based enforcement logic.

> Please review [LICENSE](LICENSE_EN) before using, modifying, or distributing the project.

---

## Overview

NexBot is built to support a private Discord server with a combination of:

- AI-powered chat with Google Gemini
- Community utility commands
- Administrative moderation controls
- Voice activity monitoring and enforcement
- Custom logging and operational tooling

---

## Features

- Private Discord bot setup with modular command loading
- AI command integration using Gemini
- Meme generation via Giphy
- Admin help and moderation utilities
- Developer command panel for bot diagnostics
- Voice moderation support through a dedicated auto-mute system

---

## Project Structure

```text
NexBot/
├── LICENSE
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
    └── drugs_are_cool.py #Personal Log tool
```

---

## Requirements

This project requires:

- Python 3.10+
- discord.py
- python-dotenv
- termcolor
- colorama
- google-genai
- requests
- numpy
- discord-ext-voice-recv

Install dependencies with:

```bash
pip install -r requirements.txt
```

---

## Setup

1. Create a Python environment if needed.
2. Install the dependencies from [requirements.txt](requirements.txt).
3. Open [config.py](config.py) and fill in the required values for your bot deployment.
4. Start the bot:

```bash
python bot.py
```

> This project does not use a `.env` file for runtime configuration. All configuration is managed directly in [config.py](config.py).

---

## Configuration

The bot reads all required runtime values from [config.py](config.py), including:

- Discord webhook and token-related settings
- owner/admin IDs
- Gemini API key
- logging channel IDs
- Giphy API key
- server-specific values used by the bot modules

Example values include:

```python
WEBHOOK_URL = ""
OWNERID = None
ADMINID = None
MODID = None
GIPHY = ""
Gemini = ""
ADMIN_LOGS = None
```

> Keep all secret values private and do not commit live credentials to public repositories.

---

## Commands

The current command set is organized around the implementation files in the project.

### Prefix commands

| Command | Description |
| --- | --- |
| `!ai <question>` | Sends a prompt to Gemini and returns the generated response in Discord. |
| `!gmeme` | Fetches a random meme from Giphy and posts it in the active channel. |
| `!ban @user [reason]` | Bans a user when the invoking user has the appropriate permissions. |
| `!purge [amount]` | Deletes a specified number of recent messages in the current channel. |
| `!hadmin` | Displays an admin help panel with command information and button actions. |
| `!devmenu` | Opens a small developer/debug panel with ping and uptime actions. |

### Command behavior

- `!ai` is handled by the Gemini integration in [gemini/testing.py](gemini/testing.py).
- `!gmeme` is handled by the community command cog in [commands/community.py](commands/community.py).
- Administrative actions are implemented in [security/adminCommands.py](security/adminCommands.py).

---

## Voice Monitoring

The project also contains a voice-focused moderation module in [security/automutevc.py](security/automutevc.py). This component is designed to monitor voice activity, detect excessive audio levels, and assist with moderation actions in voice channels.

---

## Startup Flow

The entry point is [bot.py](bot.py), which:

1. checks required imports and dependency state
2. loads configuration values
3. creates the bot client
4. loads extension modules from the command and security folders
5. starts the Discord bot session

---

## Notes

- This is a private project intended for a controlled Discord environment.
- Access, usage, and redistribution are governed by the project license.
- Only authorized users should be given access to the source code or deployment environment.

---

## License

This project is protected under a private proprietary license. See [LICENSE](LICENSE) for the complete legal terms and restrictions.

---

## Developer

Nexa (aka itzokay)

Built with Python, Discord.py, Gemini AI, and custom automation for private server operations.