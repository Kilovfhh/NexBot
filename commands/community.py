"""
These are some nice community Discord commands we would love you to use!

PS: You can view available commands using its personal UI -> /communityList
"""

import discord
from discord.ext import commands
from discord import app_commands
import requests
import asyncio
import random
from config import GIPHY
print("Testing")

class CommunityCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # meme Gen from applebot
    @commands.command(name='gmeme', description="Generate a funny meme")
    async def meme_command(self, ctx):
        # Fetch a random meme from Giphy
        url = f'https://api.giphy.com/v1/gifs/random?api_key={GIPHY}&tag=meme&rating=G'
        response = requests.get(url)
        if response.status_code == 200:
            phrases = [
                "Here's a random meme for you!",
                "Enjoy this meme!",
                "This meme is just for you!",
                "HAHAHA LOOK!",
                "I hope this meme makes you laugh!"
            ]
            embed = discord.Embed(title='Random Meme',
                                  description=random.choice(phrases),
                                  color=discord.Color.red())
            embed.set_image(url=response.json()['data']['images']['original']['url'])
            await asyncio.sleep(1)  # a lil thinkin time for the the lil jit ma heart :D
            await ctx.send(embed=embed)
        else:
            await ctx.send("Sorry, I couldn't fetch a meme right now.")


# Setup
async def setup(bot):
    await bot.add_cog(CommunityCommands(bot))