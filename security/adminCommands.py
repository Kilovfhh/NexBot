"""Admin Commands"""
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from config import ADMINID, DEVELOPER, OWNERID, ADMIN_LOGS
import time


# Comment this part out if you dont want it
# import logging
# Developer Debug mode
# handler = logging.FileHandler(filename="Security-admin.log", encoding="utf-8", mode="w")

# logging.basicConfig(
# level=logging.DEBUG,
# format="%(asctime)s:%(levelname)s:%(name)s: %(message)s",
# handlers=[logging.StreamHandler(), handler],
# )
# I've added a '-1' because guild.member_count includes all users and bots including your own bot


# Admin Fuctions
class AdminCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    # ban
    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        member: discord.Member,
        *,
        reason="No Reason Provided - Auto Message from NexBot" or None,
    ):
        if ADMINID not in [role.id for role in ctx.author.roles]:
            await ctx.send(
                f"ACCESS DENIED! Contact {DEVELOPER} If you experiencing any issues"
            )
            return

        elif member == ctx.author:
            await ctx.send(
                f"You are not able to ban yourself. \nAre you slow? <@{ctx.author.id}>"
            )
            return

        elif member.top_role.position >= ctx.author.top_role.position:
            await ctx.send("Cannot help with this request! Reason: Your role level")
            return

        elif member == ctx.guild.owner:
            await ctx.send(f"Lmfao Strike this dude for trying to ban the owner {DEVELOPER}")
            return

        elif member == self.bot.user:
            await ctx.send(f"Papa {DEVELOPER}.. {ctx.author} tried banning me...")
            return

        else:
            await member.ban(reason=reason)
            await ctx.send(f"{member} has been banned by {ctx.author}")
            await ctx.send(f"reason: {reason}")

    # purge
    @commands.command(name="purge")
    async def devCMD(self, ctx, ammount: int = 5):
        if ctx.author.id != OWNERID:
            await ctx.send("You do NOT have permission to use this command")
            return

        await ctx.channel.purge(limit=ammount)
        await ctx.send(f"Deleted {ammount} messages!")
        log = self.bot.get_channel(ADMIN_LOGS)
        if log:
            pFile = discord.File(r"security\assets\NexBot-Logs.gif") # Change gif if you would like // find out how to do it yourself ngl
            embed = discord.Embed(
                title="Purge command log",
                description=f"{ctx.author} used the purge command and deleted {ammount} messages",
                color=discord.Color.red(),
                timestamp=ctx.message.created_at
            )
            embed.set_image(url="attachment://NexBot-Logs.gif")

        await log.send(embed=embed, file=pFile)

    @commands.command(name="hadmin")
    async def hadmin(self, ctx):
        if ADMINID not in [role.id for role in ctx.author.roles]:
            await ctx.send("You don't have permission to use this command.")
            return

        # Pulling gif

        else:
            file = discord.File(r"security\assets\NexBot-Admin.gif")

            embed = discord.Embed(
                title='# Welcome to NexBot Admin Commands 👨‍💻',
                description='Here you can find all the admin commands for NexBot! \n'
                            "-------------------------------------------------------------\n"
                            "Please Click the button(s) below to see what type of commands you have! \n"
                            "# ⚠️WARNING⚠️\n"
                            "---------------------------------------------------------------\n"
                            "ANY TYPE OF MISUSE, ABUSE, FALSE BAN, ETC.. WILL NOT BE TOLERATED! \n"
                            "EVERY ACTION THAT IS USED IS AUTOMATICALLY LOGGED BY OUR SYSYTEM! \n"
                            "DONT ABUSE YOUR POWER! USE IT WISELY! \n"
                            "---------------------------------------------------------------\n"
                            f"If you have any question(s) or need help, feel free to reach me out on discord! {DEVELOPER} \n"
                            "---------------------------------------------------------------\n",
                color=discord.Color.blue()
            )
            embed.set_image(url="attachment://NexBot-Admin.gif")
            view = View()

            ban_button = Button(label='Ban Command 🔨',
                                style=discord.ButtonStyle.danger,
                                custom_id="ban_button")
            kick_button = Button(label='Kick Command 👢',
                                 style=discord.ButtonStyle.danger,
                                 custom_id="kick_button")
            admin_commands_button = Button(label='Other Admin Commands 🛠️',
                                           style=discord.ButtonStyle.primary,
                                           custom_id="admin_commands_button")

            async def button_callback(interaction):
                button_id = interaction.data['custom_id']

                if button_id == 'ban_button':
                    await interaction.response.send_message(
                        "Ban Command Usage: !ban @user reason \n"
                        "Example: !ban @JohnDoe Spamming in the chat",
                        ephemeral=False
                    )
                elif button_id == 'kick_button':
                    await interaction.response.send_message(
                        "Kick Command Usage: !kick @user reason \n"
                        "Example: !kick @JohnDoe Being rude to other members",
                        ephemeral=False
                    )
                elif button_id == 'admin_commands_button':
                    await interaction.response.send_message(
                        "Other Admin Commands: \n"
                        "!mute @user reason - Mute a user in the server \n"
                        "!unmute @user - Unmute a user in the server \n"
                        "!kick @user reason - Kick a user from the server \n"
                        "!ban @user reason - Ban a user from the server \n" \
                        "!timeout @user duration reason - Timeout a user for a specific duration \n",
                        ephemeral=False
                    )
            ban_button.callback = button_callback
            kick_button.callback = button_callback
            admin_commands_button.callback = button_callback
            view.add_item(ban_button)
            view.add_item(kick_button)
            view.add_item(admin_commands_button)
            await ctx.send(embed=embed, view=view, file=file)

    # Developer Command
    @commands.command(name="devmenu")
    async def developer_panel(self, ctx):

        # Ping
        ping = round(self.bot.latency * 1000)
        # UpTime
        upTime_S = int(time.time() - self.start_time)
        H = upTime_S // 3600
        M = (upTime_S % 3600 // 60)
        S = upTime_S % 60

        # Embed Message
        embed = discord.Embed(title="👩‍💻NexBot Developer Debug👩‍💻", description=f"This tool was made by {DEVELOPER}", color=discord.Color.blue())
        view = View()

        ping_checker = Button(label="Check Bot Ping",
                              style=discord.ButtonStyle.primary,
                              custom_id="pingBtn")
        upTime = Button(label="Check Bot Uptime",
                        style=discord.ButtonStyle.danger,
                        custom_id="UpTimeBtn")

        async def button_callback(interaction):
            button_id = interaction.data['custom_id']

            if button_id == "pingBtn":
                # logging.info("Button: pingBtn has been clicked!")
                await interaction.response.send_message(
                    f"Current Ping: {ping}ms", ephemeral=False
                )
            elif button_id == "UpTimeBtn":
                # logging.info("Button: UpTimeBtn has been clicked!")
                await interaction.response.send_message(
                    f"Total uptime: {H}hours - {M} Min - {S} Seconds", ephemeral=False
                )

        ping_checker.callback = button_callback
        upTime.callback = button_callback

        view.add_item(ping_checker)
        view.add_item(upTime)
        await ctx.send (embed=embed, view=view)

# Extension Setup
async def setup(bot):

    await bot.add_cog(AdminCommands(bot))
