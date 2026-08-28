"""
This file handles auto mute for users who are Spamming audio or Screaming in their mics!
    - This will just auto mute them for 10min / after 10min they will be unmuted
    - if they do it again they will be warned again and muted / 3 warnings = timeout for 1 hour
    - Bot joins voice channel and monitors audio levels in real-time
    - Logs all actions to a specified channel
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
import time
import audioop
import numpy as np
import struct


class VoiceChatAutoMute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warning_tracker = defaultdict(
            list
        )  # user_id -> list of warning timestamps
        self.active_mutes = {}  # user_id -> mute_end_time
        self.mute_duration = 600  # 10 minutes in seconds
        self.timeout_duration = 3600  # 1 hour in seconds
        self.max_warnings = 3
        self.monitored_channels = {}  # guild_id -> voice_client
        self.audio_threshold = 2000  # Audio level threshold for "yelling" (adjustable)
        self.yelling_duration = 5  # Seconds of continuous yelling to trigger warning
        self.user_audio_levels = defaultdict(
            list
        )  # user_id -> list of recent audio levels
        self.user_yelling_start = {}  # user_id -> timestamp when yelling started
        self.log_channel_id = None  # Set this to your log channel ID
        self.sample_rate = 48000  # Discord's sample rate
        self.channels = 2  # Discord uses stereo
        self.sample_width = 2  # 16-bit audio
        self.audio_buffer = {}  # user_id -> bytes buffer for audio analysis

    async def cog_load(self):
        """Start background tasks when cog loads"""
        self.bot.loop.create_task(self.check_mute_expiry())
        print("✅ VoiceChatAutoMute cog loaded!")

    async def check_mute_expiry(self):
        """Background task to check for expired mutes"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            current_time = time.time()
            expired_mutes = []

            for user_id, mute_end in self.active_mutes.items():
                if current_time >= mute_end:
                    expired_mutes.append(user_id)

            for user_id in expired_mutes:
                await self.unmute_user(user_id)

            await asyncio.sleep(10)  # Check every 10 seconds

    async def unmute_user(self, user_id):
        """Unmute a user across all voice channels"""
        if user_id in self.active_mutes:
            del self.active_mutes[user_id]

        for guild in self.bot.guilds:
            member = guild.get_member(user_id)
            if member and member.voice:
                try:
                    await member.edit(mute=False)
                    await self.log_action(
                        guild, f"🔊 **Unmuted** {member.mention} (automatic unmute)"
                    )
                    print(f"Unmuted {member.name} (ID: {user_id})")
                except discord.Forbidden:
                    print(f"Missing permissions to unmute {member.name}")
                except Exception as e:
                    print(f"Error unmuting {member.name}: {e}")

    async def mute_user(self, member, reason="Spamming/Screaming in voice chat"):
        """Mute a user for the specified duration"""
        if member.voice:
            try:
                await member.edit(mute=True, reason=reason)
                self.active_mutes[member.id] = time.time() + self.mute_duration
                return True
            except discord.Forbidden:
                print(f"Missing permissions to mute {member.name}")
                return False
            except Exception as e:
                print(f"Error muting {member.name}: {e}")
                return False
        return False

    def add_warning(self, user_id):
        """Add a warning to user's record and return total warnings"""
        current_time = time.time()
        self.warning_tracker[user_id].append(current_time)

        # Clean up old warnings (older than 1 hour)
        self.warning_tracker[user_id] = [
            timestamp
            for timestamp in self.warning_tracker[user_id]
            if current_time - timestamp < 3600
        ]

        return len(self.warning_tracker[user_id])

    def get_warnings(self, user_id):
        """Get current warning count for user"""
        current_time = time.time()
        if user_id in self.warning_tracker:
            # Clean up old warnings
            self.warning_tracker[user_id] = [
                timestamp
                for timestamp in self.warning_tracker[user_id]
                if current_time - timestamp < 3600
            ]
            return len(self.warning_tracker[user_id])
        return 0

    async def timeout_user(self, member, duration=3600):
        """Timeout user for specified duration (default 1 hour)"""
        try:
            if member.voice:
                await member.edit(mute=True, reason="3 warnings - Timeout for 1 hour")
                self.active_mutes[member.id] = time.time() + duration

                # Also move to AFK channel if available
                if member.guild.afk_channel:
                    try:
                        await member.move_to(
                            member.guild.afk_channel,
                            reason="3 warnings - Timeout for 1 hour",
                        )
                    except:
                        pass

                return True
        except Exception as e:
            print(f"Error timing out {member.name}: {e}")
        return False

    async def log_action(self, guild, message):
        """Log actions to the specified log channel"""
        if not self.log_channel_id:
            print(f"[LOG] {message}")
            return

        channel = guild.get_channel(self.log_channel_id)
        if channel:
            embed = discord.Embed(
                title="📝 Voice Moderation Log",
                description=message,
                color=discord.Color.blue(),
                timestamp=datetime.utcnow(),
            )
            try:
                await channel.send(embed=embed)
            except Exception as e:
                print(f"Error sending log message: {e}")

    async def handle_voice_abuse(
        self, member, reason="Spamming/Screaming in voice chat"
    ):
        """Main handler for voice chat abuse"""
        warnings = self.add_warning(member.id)

        if warnings >= self.max_warnings:
            # Timeout for 1 hour
            await self.timeout_user(member, self.timeout_duration)
            embed = discord.Embed(
                title="🔇 Voice Chat Timeout",
                description=f"{member.mention} has been timed out for 1 hour due to repeated voice abuse!",
                color=discord.Color.red(),
            )
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Warnings", value=f"{warnings}/{self.max_warnings}")
            embed.add_field(name="Duration", value="1 hour")

            # Send warning to user and channel
            await self.send_warning_embed(member, embed)
            await self.log_action(
                member.guild, f"⛔ **Timed out** {member.mention} for 1 hour - {reason}"
            )
            return embed
        else:
            # Regular mute for 10 minutes
            await self.mute_user(member, reason)
            embed = discord.Embed(
                title="🔇 Voice Chat Auto-Mute",
                description=f"{member.mention} has been auto-muted for spam/screaming!",
                color=discord.Color.orange(),
            )
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Warning", value=f"{warnings}/{self.max_warnings}")
            embed.add_field(name="Duration", value="10 minutes")
            if warnings == self.max_warnings - 1:
                embed.add_field(
                    name="⚠️ Notice",
                    value="One more warning will result in a 1-hour timeout!",
                )

            # Send warning to user and channel
            await self.send_warning_embed(member, embed)
            await self.log_action(
                member.guild,
                f"🔇 **Muted** {member.mention} for 10 minutes - {reason} (Warning {warnings}/{self.max_warnings})",
            )
            return embed

    async def send_warning_embed(self, member, embed):
        """Send warning embed to the voice channel's text channel"""
        guild = member.guild

        # Send to system channel if available
        if guild.system_channel:
            try:
                await guild.system_channel.send(embed=embed)
            except:
                pass

        # Send to log channel
        if self.log_channel_id:
            channel = guild.get_channel(self.log_channel_id)
            if channel:
                try:
                    await channel.send(embed=embed)
                except:
                    pass

    def analyze_audio(self, audio_data, user_id):
        """Analyze audio data to detect yelling"""
        try:
            # Convert bytes to numpy array for analysis
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            if len(audio_array) == 0:
                return

            # Calculate audio levels
            rms = np.sqrt(np.mean(np.square(audio_array.astype(np.float64))))
            peak = np.max(np.abs(audio_array)) if len(audio_array) > 0 else 0

            # Store recent audio levels for this user
            self.user_audio_levels[user_id].append(
                {"rms": rms, "peak": peak, "timestamp": time.time()}
            )

            # Keep only last 10 seconds of audio data
            self.user_audio_levels[user_id] = [
                level
                for level in self.user_audio_levels[user_id]
                if time.time() - level["timestamp"] < 10
            ]

            # Check if audio level exceeds threshold (yelling)
            if rms > self.audio_threshold:
                if user_id not in self.user_yelling_start:
                    self.user_yelling_start[user_id] = time.time()
                    print(
                        f"⚠️ User {user_id} started yelling (RMS: {rms:.2f}, Peak: {peak})"
                    )
                else:
                    yelling_duration = time.time() - self.user_yelling_start[user_id]
                    if yelling_duration >= self.yelling_duration:
                        # User has been yelling for too long
                        print(
                            f"🚨 User {user_id} has been yelling for {yelling_duration:.1f} seconds!"
                        )
                        asyncio.create_task(self.trigger_yelling_warning(user_id))
                        # Reset the timer
                        del self.user_yelling_start[user_id]
            else:
                # Audio level is normal
                if user_id in self.user_yelling_start:
                    print(f"✅ User {user_id} stopped yelling")
                    del self.user_yelling_start[user_id]

        except Exception as e:
            print(f"Error analyzing audio: {e}")

    async def trigger_yelling_warning(self, user_id):
        """Trigger warning for yelling user"""
        for guild in self.bot.guilds:
            member = guild.get_member(user_id)
            if member and member.voice:
                await self.handle_voice_abuse(member, "Continuous yelling detected")
                break

    async def process_audio_packet(self, voice_client, user_id, audio_data):
        """Process incoming audio packet from a user"""
        if user_id in self.active_mutes:
            return  # Skip muted users

        # Analyze the audio
        self.analyze_audio(audio_data, user_id)

    # Command to start monitoring a voice channel
    @app_commands.command(
        name="start_monitoring",
        description="Start monitoring the voice channel you're in",
    )
    @app_commands.default_permissions(administrator=True)
    async def start_monitoring(self, interaction: discord.Interaction):
        """Start monitoring the voice channel the user is in"""
        if not interaction.user.voice:
            await interaction.response.send_message(
                "You must be in a voice channel to use this command!", ephemeral=True
            )
            return

        voice_channel = interaction.user.voice.channel

        # Check if already monitoring this guild
        if interaction.guild_id in self.monitored_channels:
            await interaction.response.send_message(
                f"Already monitoring {self.monitored_channels[interaction.guild_id].channel.mention}",
                ephemeral=True,
            )
            return

        try:
            # Join the voice channel with audio receiving enabled
            voice_client = await voice_channel.connect(reconnect=True)

            # Enable voice receiving to get audio from other users
            voice_client.listen(discord.VoiceClient.listen)

            self.monitored_channels[interaction.guild_id] = voice_client

            # Set up audio packet handler
            voice_client.on_voice_state_update = self.create_voice_state_handler(
                voice_client
            )

            embed = discord.Embed(
                title="🎤 Voice Monitoring Started",
                description=f"Started monitoring {voice_channel.mention}",
                color=discord.Color.green(),
            )
            embed.add_field(name="Audio Threshold", value=str(self.audio_threshold))
            embed.add_field(
                name="Yelling Duration", value=f"{self.yelling_duration} seconds"
            )
            embed.add_field(name="Mute Duration", value="10 minutes")
            embed.add_field(name="Max Warnings", value="3 (then 1 hour timeout)")
            embed.add_field(name="Status", value="🔴 Live monitoring active")

            await interaction.response.send_message(embed=embed)
            await self.log_action(
                interaction.guild, f"🎤 **Started monitoring** {voice_channel.mention}"
            )
            print(
                f"Started monitoring {voice_channel.name} in {interaction.guild.name}"
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to join that voice channel!", ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Error joining voice channel: {e}", ephemeral=True
            )

    def create_voice_state_handler(self, voice_client):
        """Create a handler for voice state updates"""

        async def voice_state_handler(member, before, after):
            # Check if a user started speaking
            if before.self_stream != after.self_stream:
                if after.self_stream:
                    print(f"🎙️ {member.name} started streaming")
                else:
                    print(f"🎙️ {member.name} stopped streaming")

            # Check if a user was muted/unmuted
            if before.self_mute != after.self_mute:
                if after.self_mute:
                    print(f"🔇 {member.name} muted themselves")
                else:
                    print(f"🔊 {member.name} unmuted themselves")

        return voice_state_handler

    # Command to stop monitoring
    @app_commands.command(
        name="stop_monitoring", description="Stop monitoring voice channels"
    )
    @app_commands.default_permissions(administrator=True)
    async def stop_monitoring(self, interaction: discord.Interaction):
        """Stop monitoring the voice channel in this guild"""
        if interaction.guild_id in self.monitored_channels:
            voice_client = self.monitored_channels[interaction.guild_id]
            channel_name = voice_client.channel.name

            await voice_client.disconnect()
            del self.monitored_channels[interaction.guild_id]

            embed = discord.Embed(
                title="🛑 Voice Monitoring Stopped",
                description=f"Stopped monitoring #{channel_name}",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed)
            await self.log_action(
                interaction.guild, f"🛑 **Stopped monitoring** #{channel_name}"
            )
            print(f"Stopped monitoring {channel_name}")
        else:
            await interaction.response.send_message(
                "Not currently monitoring any voice channel in this server!",
                ephemeral=True,
            )

    # Command to set log channel
    @app_commands.command(
        name="set_log_channel", description="Set the channel for voice moderation logs"
    )
    @app_commands.default_permissions(administrator=True)
    async def set_log_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ):
        """Set the log channel for voice moderation actions"""
        self.log_channel_id = channel.id
        embed = discord.Embed(
            title="📝 Log Channel Set",
            description=f"Voice moderation logs will be sent to {channel.mention}",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.log_action(
            interaction.guild, f"📝 **Log channel set** to {channel.mention}"
        )

    # Command to set audio threshold
    @app_commands.command(
        name="set_threshold",
        description="Set the audio threshold for yelling detection",
    )
    @app_commands.default_permissions(administrator=True)
    async def set_threshold(self, interaction: discord.Interaction, threshold: int):
        """Set the audio threshold for yelling detection"""
        if threshold < 100:
            await interaction.response.send_message(
                "Threshold must be at least 100!", ephemeral=True
            )
            return

        self.audio_threshold = threshold
        embed = discord.Embed(
            title="🎚️ Audio Threshold Updated",
            description=f"New threshold: {threshold}",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.log_action(
            interaction.guild, f"🎚️ **Audio threshold set** to {threshold}"
        )

    # Command to check warnings
    @app_commands.command(name="warnings", description="Check your voice chat warnings")
    async def check_warnings(self, interaction: discord.Interaction):
        warnings = self.get_warnings(interaction.user.id)
        is_muted = interaction.user.id in self.active_mutes

        embed = discord.Embed(
            title="Voice Chat Warnings",
            description=f"Warnings for {interaction.user.mention}",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Warning Count", value=f"{warnings}/{self.max_warnings}")

        if is_muted:
            mute_end = self.active_mutes[interaction.user.id]
            time_left = max(0, mute_end - time.time())
            minutes_left = int(time_left // 60)
            seconds_left = int(time_left % 60)
            embed.add_field(
                name="Current Mute",
                value=f"⏰ {minutes_left}m {seconds_left}s remaining",
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Admin command to manually trigger auto-mute (for testing)
    @app_commands.command(
        name="test_automute", description="Test the auto-mute system (Admin only)"
    )
    @app_commands.default_permissions(administrator=True)
    async def test_automute(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        """Test the auto-mute system manually"""
        if not member.voice:
            await interaction.response.send_message(
                f"{member.mention} is not in a voice channel!", ephemeral=True
            )
            return

        embed = await self.handle_voice_abuse(member, "Test trigger")
        await interaction.response.send_message(embed=embed)

    # Admin command to clear warnings
    @app_commands.command(
        name="clear_warnings", description="Clear warnings for a user (Admin only)"
    )
    @app_commands.default_permissions(administrator=True)
    async def clear_warnings(
        self, interaction: discord.Interaction, member: discord.Member
    ):
        """Clear all warnings for a user"""
        if member.id in self.warning_tracker:
            del self.warning_tracker[member.id]

        if member.id in self.active_mutes:
            await self.unmute_user(member.id)

        embed = discord.Embed(
            title="Warnings Cleared",
            description=f"All warnings and mutes cleared for {member.mention}",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.log_action(
            interaction.guild, f"✅ **Cleared warnings** for {member.mention}"
        )

    # Command to view monitoring status
    @app_commands.command(
        name="monitoring_status", description="View current monitoring status"
    )
    @app_commands.default_permissions(administrator=True)
    async def monitoring_status(self, interaction: discord.Interaction):
        """View current monitoring status"""
        embed = discord.Embed(
            title="📊 Voice Monitoring Status",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow(),
        )

        if interaction.guild_id in self.monitored_channels:
            voice_client = self.monitored_channels[interaction.guild_id]
            embed.add_field(
                name="Status",
                value=f"🟢 Active - Monitoring {voice_client.channel.mention}",
                inline=False,
            )
            embed.add_field(
                name="Users in Channel", value=str(len(voice_client.channel.members))
            )
            embed.add_field(name="Audio Threshold", value=str(self.audio_threshold))
            embed.add_field(name="Active Mutes", value=str(len(self.active_mutes)))
        else:
            embed.add_field(name="Status", value="🔴 Not monitoring", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Voice state update listener
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Monitor voice state changes"""
        # Check if bot was disconnected
        if member.id == self.bot.user.id and before.channel and not after.channel:
            # Bot was disconnected from voice
            if member.guild.id in self.monitored_channels:
                del self.monitored_channels[member.guild.id]
                await self.log_action(
                    member.guild, "🔌 **Bot disconnected** from voice channel"
                )
                print(f"Bot disconnected from voice channel in {member.guild.name}")

        # Check if a monitored user joined/left
        if member.guild.id in self.monitored_channels:
            voice_client = self.monitored_channels[member.guild.id]
            if voice_client.channel:
                # User joined the monitored channel
                if (
                    after.channel
                    and after.channel.id == voice_client.channel.id
                    and before.channel != after.channel
                ):
                    await self.log_action(
                        member.guild,
                        f"👋 {member.mention} joined the monitored channel",
                    )
                    print(f"{member.name} joined the monitored channel")
                # User left the monitored channel
                elif (
                    before.channel
                    and before.channel.id == voice_client.channel.id
                    and before.channel != after.channel
                ):
                    await self.log_action(
                        member.guild, f"👋 {member.mention} left the monitored channel"
                    )
                    print(f"{member.name} left the monitored channel")
                    # Clean up their yelling timer
                    if member.id in self.user_yelling_start:
                        del self.user_yelling_start[member.id]

    # Cleanup on cog unload
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        for guild_id, voice_client in self.monitored_channels.items():
            asyncio.create_task(voice_client.disconnect())
        self.monitored_channels.clear()
        print("VoiceChatAutoMute cog unloaded")


# Setup
async def setup(bot):
    await bot.add_cog(VoiceChatAutoMute(bot))
