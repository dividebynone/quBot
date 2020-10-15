from main import config, bot_starttime, bot_path
from datetime import datetime, timedelta, timezone
from discord.ext import tasks, commands
import libs.utils.admintools as admintools
from libs.qulib import ExtendedCommand, ExtendedGroup
import libs.qulib as qulib
import configparser
import discord
import asyncio
import typing
import main
import math
import time
import re
import os

# User converter used for banned user retrieval
# Usage: Use instead of discord.User where retrieval of a banned user is required.
# Note(s): Since banned users are no longer in the guild, a special method of user retrieval is required. The following class provides that method
class BannedUser(commands.UserConverter):

    async def convert(self, ctx, argument):
        banned_users = await ctx.guild.bans()
        try:
            ban_entry = discord.utils.find(lambda m: m.user.id == int(argument, base=10), banned_users)
        except ValueError:
            ban_entry = discord.utils.find(lambda m: str(m.user) == argument, banned_users)

        if ban_entry is None:
            raise commands.BadArgument("Failed to convert user input to User Object. User was not found in the guild's banned user list.")
        return ban_entry.user

# Standard time converter - Converts a string into a seconds-based time interval
# Usage: Converts string input of a time interval into seconds
class TimePeriod(commands.Converter):
    
    def __init__(self):
        self.time_units = {'m':'minutes', 'h':'hours', 'd':'days', 'w':'weeks'}

    async def convert(self, ctx, argument):
        time_in_seconds = int(timedelta(**{self.time_units.get(m.group('unit').lower(), 'minutes'): int(m.group('val')) for m in re.finditer(r'(?P<val>\d+)(\s?)(?P<unit>[mhdw]?)', argument, flags=re.I)}).total_seconds())

        if time_in_seconds == 0:
            raise commands.BadArgument("Failed to convert user input to a valid time frame.")
        return time_in_seconds

# Short time converter - Same functionality as TimePeriod but is used for small time intervals
class SmallTimePeriod(commands.Converter):
    
    def __init__(self):
        self.time_units = {'s': 'seconds', 'm':'minutes', 'h':'hours'}

    async def convert(self, ctx, argument):
        time_in_seconds = int(timedelta(**{self.time_units.get(m.group('unit').lower(), 'seconds'): int(m.group('val')) for m in re.finditer(r'(?P<val>\d+)(\s?)(?P<unit>[mhdw]?)', argument, flags=re.I)}).total_seconds())
        return time_in_seconds

# Cog (Moderation) - Collection of commands and assets used for chat moderation
class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.embed_color = 0xdc143c
        self.embed_color_alt = 0x8bea3a
        self.embed_color_report = 0xf8e13f

        self.MAX_SLOWMODE = 21600
        self.LEFT = '⬅️'
        self.RIGHT = '➡️'
        self.PAGINATION_TIMEOUT = '⏹️'
        
        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = False
        self.module_dependencies = []

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)

        self.Reports = admintools.Reports()
        self.Warnings = admintools.Warnings()
        self.MuteRole = admintools.MuteRole()
        self.AutoActions = admintools.AutoWarningActions()
        self.BlacklistedUsers = admintools.BlacklistedUsers()
        self.TemporaryActions = admintools.TemporaryActions()
        
        # Setting up configuration environment (config.ini)
        self.config_section = 'Moderation'

        if self.config_section not in config.sections():
            config.add_section(self.config_section)

        if 'MaxWarnings' not in config[self.config_section]:
            config.set(self.config_section, 'MaxWarnings', '20')
        if 'MaxMessageLength' not in config[self.config_section]:
            config.set(self.config_section, 'MaxMessageLength', '1500')
        if 'PurgeMessageLimit' not in config[self.config_section]:
            config.set(self.config_section, 'PurgeMessageLimit', '1000')
        
        with open(os.path.join(bot_path, 'config.ini'), 'w', encoding="utf_8") as config_file:
            config.write(config_file)
        config_file.close()

        with open(os.path.join(bot_path, 'config.ini'), 'r', encoding="utf_8") as config_file:
            config.read_file(config_file)
            self.max_warnings = int(config.get(self.config_section, 'MaxWarnings'))
            self.max_characters = int(config.get(self.config_section, 'MaxMessageLength'))
            self.purge_limit = int(config.get(self.config_section, 'PurgeMessageLimit'))
        config_file.close()

        # Starting module-related tasks
        self.temporary_actions.start() # pylint: disable=no-member

        print(f'Module {self.__class__.__name__} loaded')

    def cog_unload(self):
        self.temporary_actions.cancel() # pylint: disable=no-member

    def predicate(self, message, l, r):
        def check(reaction, user):
            if reaction.message.id != message.id or user.id == self.bot.user.id:
                return False
            if l and reaction.emoji == self.LEFT:
                return True
            if r and reaction.emoji == self.RIGHT:
                return True
            return False
        return check

    @tasks.loop(minutes=1, reconnect=True)
    async def temporary_actions(self):
        time_on_iter = int(time.time())
        guild_dict = await self.TemporaryActions.get_expired_actions(time_on_iter)

        for guild_id in guild_dict:
            guild = self.bot.get_guild(guild_id)
            if guild:
                for user_id, action in guild_dict[guild_id]:
                    if action == int(admintools.ModerationAction.TextMute):
                        member = guild.get_member(user_id)
                        if member:
                            role = await self.get_mute_role(guild)
                            guild_roles = [x.id for x in member.roles]
                            if role.id in guild_roles:
                                await member.remove_roles(role)
                    elif action == int(admintools.ModerationAction.Ban):
                        banned_users = await guild.bans()
                        ban_entry = discord.utils.find(lambda m: m.user.id == user_id, banned_users)
                        if ban_entry is not None:
                            await guild.unban(ban_entry.user, reason="Temporary ban has expired for the following individual.")

        await self.TemporaryActions.clear_expired_actions(time_on_iter)

    # Method to get the target guild's text mute role.
    # Note(s): If the role does not exist upon retrieval, a new role is created
    async def get_mute_role(self, guild: discord.Guild):
        mute_role = await self.MuteRole.get_mute_role(guild.id)
        role = discord.utils.get(guild.roles, name='Muted')
        if not role:
            role = await guild.create_role(name="Muted", permissions=discord.Permissions(send_messages = False), reason="Created mute role to support bot moderation functionality.")
        if mute_role == None or mute_role != role.id:
            await self.update_mute_role(role, guild)
            await self.MuteRole.set_mute_role(guild.id, role.id)
        
        return role

    # Method used internally to update the mute role for the target guild
    async def update_mute_role(self, role: discord.Role, guild: discord.Guild):
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.manage_roles:
                channel_overwrite = channel.overwrites_for(role)
                channel_overwrite.send_messages = False
                channel_overwrite.add_reactions = False
                
                await channel.set_permissions(role, overwrite=channel_overwrite)

    # Method used internally to shorten the user list if it exceeds a set number of lines
    def slice_userlist(self, istring: str, lines: int, langset):
        if istring.count('\n') > lines:
            other_count = istring.count('\n') - lines
            istring = '\n'.join(istring.split('\n')[:lines]) + "\n(+ {} {})".format(other_count, langset["others_string"] if other_count > 1 else langset["other_string"])
        return istring

    # Event that handles the removal of unwanted data.
    # Note(s): The event will trigger when the bot is kicked from a guild
    @commands.Cog.listener()
    @commands.guild_only()
    async def on_guild_remove(self, guild):
        await self.BlacklistedUsers.remove_blacklist_guild(guild.id)
        await self.TemporaryActions.wipe_guild_data(guild.id)

    # Module commands

    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.command(cls=ExtendedCommand, name='purge', help=main.lang["command_purge_help"], description=main.lang["command_purge_description"], aliases=['clear', 'clean', 'prune', 'delete'], usage="10 {filter}", permissions=['Manage Messages'])
    async def purge(self, ctx, messages: int, *filters):
        if messages > 0:
            await ctx.message.delete()
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            messages = self.purge_limit if messages > self.purge_limit else messages

            def is_bot(message):
                return message.author.bot

            def is_me(message):
                return message.author.id == ctx.message.author.id

            def is_embed(message):
                return len(message.embeds) > 0
            
            def is_attachment(message):
                return len(message.attachments) > 0

            def is_target_user(message):
                return user.id == message.author.id

            def is_string(message):
                return ' '.join(filters[1:]) in message.content

            def is_regex(message):
                pattern = re.compile(' '.join(filters[1:]))
                return bool(re.search(pattern, message.content))

            check = None
            if filters:
                lowered = filters[0].lower()

                if lowered in ('bot', 'bots'):
                    check = is_bot
                elif lowered in ('me', 'author'):
                    check = is_me
                elif lowered in ('embed', 'embeds'):
                    check = is_embed
                elif lowered in ('attachment', 'file', 'image', 'uploads'):
                    check = is_attachment
                elif lowered in ('user', 'member') and len(filters) > 1:
                    try:
                        user = await commands.UserConverter().convert(ctx, ' '.join(filters[1:]))
                        check = is_target_user
                    except commands.UserNotFound:
                        embed = discord.Embed(title=lang["moderation_purge_usernotfound"], color=self.embed_color)
                        await ctx.send(embed=embed, delete_after=10)
                        return
                elif lowered in ('has', 'contains') and len(filters) > 1:
                    check = is_string
                elif lowered == 'regex' and len(filters) > 1:
                    check = is_regex
                else:
                    embed = discord.Embed(title=lang["moderation_purge_invalid_filter"], color=self.embed_color)
                    await ctx.send(embed=embed, delete_after=10)
                    return

            deleted = await ctx.channel.purge(limit=messages, check=check, bulk=True)
            embed = discord.Embed(title=lang["moderation_purge_success"].format(len(deleted)), color=self.embed_color)
            await ctx.send(embed=embed, delete_after=10)

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    @commands.command(cls=ExtendedCommand, name='kick', description=main.lang["command_kick_description"], usage="@somebody {Spamming}", permissions=['Kick Members'])
    async def kick(self, ctx, members: commands.Greedy[discord.Member], *, reason: str = None):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if members:
            output = ""
            for member in members:
                try:
                    await ctx.guild.kick(member, reason=reason)
                    output += f'{str(member)} ({member.mention})\n'
                except discord.Forbidden:
                    pass
            await ctx.message.delete()

            output = self.slice_userlist(output, 20, lang)
            if len(output.strip()) > 0:
                embed = discord.Embed(title=lang["moderation_kick_embed_title"], timestamp=datetime.utcnow(), color=self.embed_color)
                embed.add_field(name=lang["moderation_kick_embed_users"], value=output or lang["empty_string"], inline=True)
                if reason:
                    embed.add_field(name=lang["reason_string"], value=reason or lang["empty_string"], inline=False)
                embed.set_footer(text=lang["moderation_kick_embed_footer"].format(str(ctx.author)))
                await ctx.send(embed=embed)
            else:
                await ctx.send(lang["moderation_kick_empty"].format(ctx.author.mention), delete_after=10)
        else:
            await ctx.send(lang["moderation_kick_not_found"], delete_after=10)
    
    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command(cls=ExtendedCommand, name='ban', help=main.lang["command_ban_help"], description=main.lang["command_ban_description"], usage='@somebody {"2 weeks 5 days"} {Harassment}', permissions=['Ban Members'])
    async def ban(self, ctx, members: commands.Greedy[discord.Member], time_period: typing.Optional[TimePeriod] = None, *, reason: str = None):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if members:
            unix_timestamp = int(time.time() + (time_period or 0))
            timestamp = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc) + timedelta(seconds=60)
            output = ""

            for member in members:
                try:
                    if time_period and not self.TemporaryActions.is_banned(member.id, ctx.guild.id):
                        if await self.TemporaryActions.set_action(member.id, ctx.guild.id, admintools.ModerationAction.Ban, unix_timestamp):
                            await member.send(lang["moderation_ban_temp_dm"].format(ctx.guild.name, reason, timestamp.strftime('%Y/%m/%d at %H:%M UTC')))
                    else:
                        await member.send(lang["moderation_ban_dm"].format(ctx.guild.name, reason))
                    await ctx.guild.ban(member, reason=reason)
                    await self.Warnings.reset_warnings(ctx.guild.id, member.id)
                    output += f'{str(member)} ({member.mention})\n'
                except discord.Forbidden:
                    pass
            await ctx.message.delete()

            output = self.slice_userlist(output, 20, lang)
            if len(output.strip()) > 0:
                embed = discord.Embed(title=lang["moderation_ban_embed_title"], timestamp=datetime.utcnow(), color=self.embed_color)
                embed.add_field(name=lang["moderation_ban_embed_users"], value=output or lang["empty_string"], inline=True)
                if reason:
                    embed.add_field(name=lang["reason_string"], value=reason or lang["empty_string"], inline=False)
                if time_period:
                    embed.add_field(name=lang["moderation_embed_expiration"], value=timestamp.strftime('%Y/%m/%d at %H:%M UTC'), inline=False)
                embed.set_footer(text=lang["moderation_ban_embed_footer"].format(str(ctx.author)))
                await ctx.send(embed=embed)
            else:
                await ctx.send(lang["moderation_ban_empty"].format(ctx.author.mention), delete_after=10)
        else:
            await ctx.send(lang["moderation_ban_not_found"], delete_after=10)

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    @commands.command(cls=ExtendedCommand, name='unban', help=main.lang["command_unban_help"], description=main.lang["command_unban_description"], usage="User#1234 OR 116267141744820233", permissions=['Ban Members'])
    async def unban(self, ctx, users: commands.Greedy[BannedUser], *, reason: str = None):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if users:
            output = ""
            for user in users:
                try:
                    await self.TemporaryActions.clear_action(user.id, ctx.guild.id, admintools.ModerationAction.Ban)
                    await ctx.guild.unban(user, reason=reason)
                    output += f'{str(user)} ({user.mention})\n'
                except discord.Forbidden:
                    pass
            await ctx.message.delete()

            output = self.slice_userlist(output, 20, lang)
            if len(output.strip()) > 0:
                embed = discord.Embed(title=lang["moderation_unban_embed_title"], timestamp=datetime.utcnow(), color=self.embed_color_alt)
                embed.add_field(name=lang["moderation_unban_embed_users"], value=output or lang["empty_string"], inline=True)
                if reason:
                    embed.add_field(name=lang["reason_string"], value=reason or lang["empty_string"], inline=False)
                embed.set_footer(text=lang["moderation_unban_embed_footer"].format(str(ctx.author)))
                await ctx.send(embed=embed)
            else:
                await ctx.send(lang["moderation_unban_empty"].format(ctx.author.mention), delete_after=10)
        else:
            await ctx.send(lang["moderation_unban_not_found"], delete_after=10)

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.has_permissions(kick_members=True, manage_messages=True)
    @commands.guild_only()
    @commands.command(cls=ExtendedCommand, name='softban', help=main.lang["command_softban_help"], description=main.lang["command_softban_description"], usage="@somebody {Spamming}", permissions=['Kick Members', 'Manage Messages'])
    async def softban(self, ctx, members: commands.Greedy[discord.Member], *, reason: str = None):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if members:
            output = ""
            for member in members:
                try:
                    await ctx.guild.ban(member, delete_message_days=1, reason=reason)
                    await ctx.guild.unban(member, reason=reason)
                    output += f'{str(member)} ({member.mention})\n'
                except discord.Forbidden:
                    pass
            await ctx.message.delete()

            output = self.slice_userlist(output, 20, lang)
            if len(output.strip()) > 0:
                embed = discord.Embed(title=lang["moderation_softban_embed_title"], timestamp=datetime.utcnow(), color=self.embed_color)
                embed.add_field(name=lang["moderation_softban_embed_users"], value=output or lang["empty_string"], inline=True)
                if reason:
                    embed.add_field(name=lang["reason_string"], value=reason or lang["empty_string"], inline=False)
                embed.set_footer(text=lang["moderation_softban_embed_footer"].format(str(ctx.author)))
                await ctx.send(embed=embed)
            else:
                await ctx.send(lang["moderation_softban_empty"].format(ctx.author.mention), delete_after=10)
        else:
            await ctx.send(lang["moderation_softban_not_found"], delete_after=10)

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.command(cls=ExtendedCommand, name='mute', help=main.lang["command_mute_help"], description=main.lang["command_mute_description"], usage='@somebody {2 days}', permissions=['Manage Messages'])
    async def mute(self, ctx, members: commands.Greedy[discord.Member], *, time_period: typing.Optional[TimePeriod] = None):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if members:
            async with ctx.channel.typing():
                role = await self.get_mute_role(ctx.guild)
            output = ""
            unix_timestamp = int(time.time() + (time_period or 0))
            timestamp = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc) + timedelta(seconds=60)
            for member in members:
                member_roles = [x.id for x in member.roles]
                if role.id not in member_roles:
                    if time_period and not self.TemporaryActions.is_textmuted(member.id, ctx.guild.id):
                        await self.TemporaryActions.set_action(member.id, ctx.guild.id, admintools.ModerationAction.TextMute, unix_timestamp)
                        await member.send(lang["moderation_mute_temp_dm"].format(ctx.guild.name, timestamp.strftime('%Y/%m/%d at %H:%M UTC')))
                    else:
                        await member.send(lang["moderation_mute_dm"].format(ctx.guild.name))
                    await member.add_roles(role)
                    output += f'{str(member)} ({member.mention})\n'
            await ctx.message.delete()

            output = self.slice_userlist(output, 20, lang)
            if len(output.strip()) > 0:
                embed = discord.Embed(title=lang["moderation_mute_embed_title"], timestamp=datetime.utcnow(), color=self.embed_color)
                embed.add_field(name=lang["moderation_mute_embed_users"], value=output or lang["empty_string"], inline=False)
                embed.set_footer(text=lang["moderation_mute_embed_footer"].format(str(ctx.author)))
                if time_period:
                    embed.add_field(name=lang["moderation_embed_expiration"], value=timestamp.strftime('%Y/%m/%d at %H:%M UTC'), inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(lang["moderation_mute_empty"].format(ctx.author.mention), delete_after=10)
        else:
            await ctx.send(lang["moderation_mute_not_found"], delete_after=10)

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    @commands.command(cls=ExtendedCommand, name='unmute', description=main.lang["command_unmute_description"], usage='@somebody', permissions=['Manage Messages'])
    async def unmute(self, ctx, members: commands.Greedy[discord.Member]):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if members:
            async with ctx.channel.typing():
                role = await self.get_mute_role(ctx.guild)
            output = ""
            for member in members:
                member_roles = [x.id for x in member.roles]
                if role.id in member_roles:
                    await member.remove_roles(role)
                    await self.TemporaryActions.clear_action(member.id, ctx.guild.id, admintools.ModerationAction.TextMute)
                    await member.send(lang["moderation_unmute_dm"].format(ctx.guild.name))
                    output += f'{str(member)} ({member.mention})\n'
            await ctx.message.delete()

            output = self.slice_userlist(output, 20, lang)
            if len(output.strip()) > 0:
                embed = discord.Embed(title=lang["moderation_unmute_embed_title"], timestamp=datetime.utcnow(), color=self.embed_color_alt)
                embed.add_field(name=lang["moderation_unmute_embed_users"], value=output or lang["empty_string"], inline=True)
                embed.set_footer(text=lang["moderation_unmute_embed_footer"].format(str(ctx.author)))
                await ctx.send(embed=embed)
            else:
                await ctx.send(lang["moderation_unmute_empty"].format(ctx.author.mention), delete_after=10)
        else:
            await ctx.send(lang["moderation_mute_not_found"], delete_after=10)

    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    @commands.guild_only()
    @commands.group(cls=ExtendedGroup, name='slowmode', invoke_without_command=True, help=main.lang["command_slowmode_help"], description=main.lang["command_slowmode_description"], usage='15', aliases=['sm'], permissions=['Manage Messages', 'Manage Channels'])
    async def slowmode(self, ctx, *, time_period: SmallTimePeriod):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if time_period <= self.MAX_SLOWMODE:
                await ctx.channel.edit(slowmode_delay=time_period)
                if time_period == 0:
                    embed = discord.Embed(title=lang["moderation_slowmode_disabled"], color=self.embed_color)
                else:
                    hours = int(time_period/3600)
                    hour_string = lang["hours_string"] if hours != 1 else lang["hour_string"]
                    minutes = int((time_period/60)%60)
                    minutes_string = lang["minutes_string"] if minutes != 1 else lang["minute_string"]
                    seconds = int(time_period%60)
                    seconds_string = lang["seconds_string"] if seconds != 1 else lang["second_string"]
                    formatted_time_string = f"{f'{hours} {hour_string} ' if hours != 0 else ''}{f'{minutes} {minutes_string} ' if minutes != 0 else ''}{f'{seconds} {seconds_string}' if seconds != 0 else ''}"

                    embed = discord.Embed(title=lang["moderation_slowmode_enabled"].format(formatted_time_string), color=self.embed_color)
            else:
                embed = discord.Embed(title=lang["moderation_slowmode_max"].format(int(self.MAX_SLOWMODE/3600)), color=self.embed_color)
            await ctx.send(embed=embed, delete_after=10)

    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    @commands.guild_only()
    @slowmode.command(cls=ExtendedCommand, name='disable', description=main.lang["command_slowmode_disable_description"], aliases=['d', 'off'], permissions=['Manage Messages', 'Manage Channels'])
    async def slowmode_disable(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.channel.edit(slowmode_delay=0)
        embed = discord.Embed(title=lang["moderation_slowmode_disabled"], color=self.embed_color)
        await ctx.send(embed=embed, delete_after=10)

    @commands.cooldown(5, 60, commands.BucketType.user)
    @commands.has_permissions(send_messages=True)
    @commands.guild_only()
    @commands.group(name='report', invoke_without_command=True, help=main.lang["command_report_help"], description=main.lang["command_report_description"], usage='@somebody Spamming')
    async def report(self, ctx, member: discord.Member, *, reason: str):
        if not ctx.invoked_subcommand:
            if ctx.author.id != member.id:
                channel_id = await self.Reports.get_channel(ctx.guild.id)
                lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
                if channel_id:
                    await ctx.message.delete()
                    channel = self.bot.get_channel(channel_id)
                    embed = discord.Embed(title=lang["moderation_report_embed_title"], timestamp=datetime.utcnow(), color=self.embed_color_report)
                    embed.add_field(name=lang["user_string"], value=f'{str(member)} ({member.mention})', inline=True)
                    embed.add_field(name=lang["reason_string"], value=reason, inline=True)
                    embed.set_footer(text=lang["moderation_report_embed_footer"].format(ctx.author))
                    await channel.send(embed=embed)
                else:
                    await ctx.send(lang["moderation_report_not_enabled"])
            else:
                raise commands.BadArgument("Failed to report user. Message author matches one of the target users.")

    @commands.cooldown(5, 60, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @report.command(cls=ExtendedCommand, name='setchannel', help=main.lang["command_report_setchannel_help"], description=main.lang["command_report_setchannel_description"], usage='#general', permissions=['Administrator'])
    async def report_setchannel(self, ctx, channel: discord.TextChannel):
        await self.Reports.set_channel(ctx.guild.id, channel.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["moderation_report_setchannel"].format(str(channel)), color=self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(5, 60, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @report.command(cls=ExtendedCommand, name='disable', description=main.lang["command_report_disable_description"], aliases=['d', 'off'], permissions=['Administrator'])
    async def report_disable(self, ctx):
        channel_id = await self.Reports.get_channel(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if channel_id:
            await self.Reports.disable(ctx.guild.id)
            embed = discord.Embed(title=lang["moderation_report_disable_success"], color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["moderation_report_disable_disabled"], color=self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.has_permissions(kick_members=True, ban_members=True)
    @commands.guild_only()
    @commands.command(cls=ExtendedCommand, name='warn', description=main.lang["command_warn_description"], usage='@someone Spamming', permissions=['Kick Members', 'Ban Members'])
    async def warn(self, ctx, members: commands.Greedy[discord.Member], *, warning: str):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if members:
            members_ids = [x.id for x in members]
            if ctx.author.id not in members_ids:
                output = ""
                reached_limit = ""
                for member in members:
                    member_warnings = await self.Warnings.get_warning_count(ctx.guild.id, member.id)
                    if member_warnings < self.max_warnings:
                        await self.Warnings.add_warning(member.id, warning, ctx.author.id, ctx.guild.id)
                        dm_embed = discord.Embed(title=lang["moderation_warn_dm_title"], description=lang["moderation_warn_dm_warnedby"].format(str(ctx.author)), timestamp=datetime.utcnow(), color=self.embed_color)
                        dm_embed.add_field(name=lang["warning_string"], value=warning, inline=False)
                        dm_embed.set_footer(text=lang["moderation_warn_dm_footer"].format(str(ctx.guild)))
                        await member.send(embed=dm_embed)
                        
                        output += f'{str(member)} ({member.mention})\n'
                        member_warnings = member_warnings + 1

                        actions = await self.AutoActions.get_actions(ctx.guild.id)
                        if actions:
                            #Automatic Ban (Takes priority over kick if they both trigger on the same number) - Warnings are reset upon automatic ban
                            if actions[2] != None and member_warnings >= actions[2]:
                                await self.Warnings.reset_warnings(ctx.guild.id, member.id)
                                await ctx.guild.ban(member, reason=lang["moderation_autoaction_ban"])
                                return
                            #Automatic Kick
                            if actions[1] != None and member_warnings >= actions[1]:
                                await ctx.guild.kick(member, reason=lang["moderation_autoaction_kick"])
                                return
                            #Automatic Mute
                            if actions[0] != None and member_warnings >= actions[0]:
                                async with ctx.channel.typing():
                                    role = await self.get_mute_role(ctx.guild)
                                role_find = discord.utils.get(member.roles, id=role.id)
                                if not role_find:
                                    await member.add_roles(role)
                    else:
                        reached_limit += f'{str(member)} ({member.mention})\n'
                await ctx.message.delete()

                output = self.slice_userlist(output, 10, lang)
                reached_limit = self.slice_userlist(reached_limit, 10, lang)
                if len(output.strip()) > 0:
                    embed = discord.Embed(title=lang["moderation_warn_embed_title"], description=lang["moderation_warn_embed_description"], timestamp=datetime.utcnow(), color=self.embed_color)
                    embed.add_field(name=lang["moderation_warn_embed_users"], value=output or lang["empty_string"], inline=True)
                    if len(reached_limit.strip()) > 0:
                        embed.add_field(name=lang["moderation_warn_embed_reached_limit"], value=reached_limit, inline=False)
                    embed.set_footer(text=lang["moderation_warn_embed_footer"].format(str(ctx.author)))
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(lang["moderation_warn_empty"].format(ctx.author.mention), delete_after=10)
            else:
                raise commands.BadArgument("Failed to warn user. Message author matches one of the target users.")
        else:
            await ctx.send(lang["moderation_warn_not_found"], delete_after=10)
 
    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.has_permissions(kick_members=True, ban_members=True)
    @commands.guild_only()
    @commands.group(cls=ExtendedGroup, name='warnings', invoke_without_command=True, help=main.lang["command_warnings_help"], description=main.lang["command_warnings_description"], usage='@someone {2}', permissions=['Kick Members', 'Ban Members'])
    async def warnings(self, ctx, member: discord.Member, page: int = 1):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            warnings = await self.Warnings.get_warnings(ctx.guild.id, member.id)
            await ctx.message.delete()

            if len(warnings) > 0:
                last_index = math.floor(len(warnings)/5)
                if len(warnings) % 5 == 0:
                    last_index -= 1
                if page and page >= 1:
                    page = last_index if (page - 1) > last_index else (page - 1)
                else:
                    page = 0
                index = page
                
                msg = None
                action = ctx.send
                try:
                    while True:
                        embed = discord.Embed(title=lang["moderation_warnings_embed_title"].format(str(member)), color=self.embed_color)
                        for warning in warnings[(index*5):(index*5 + 5)]:
                            warned_by = self.bot.get_user(warning[1])
                            embed.add_field(name=f'{lang["warning_string"]}: **{warning[0]}**', value=lang["moderation_warnings_embed_issuedby"].format(warned_by), inline=False)

                        if last_index == 0:
                            await ctx.send(embed=embed)
                            return
                        embed.set_footer(text=f"{lang['page_string']} {index+1}/{last_index+1}")
                        res = await action(embed=embed)
                        if res is not None:
                            msg = res
                        l = index != 0
                        r = index != last_index
                        await msg.add_reaction(self.LEFT)
                        if l:
                            await msg.add_reaction(self.LEFT)
                        if r:
                            await msg.add_reaction(self.RIGHT)

                        react = (await self.bot.wait_for('reaction_add', check=self.predicate(msg, l, r), timeout=30.0))[0]
                        if react.emoji == self.LEFT:
                            index -= 1
                        elif react.emoji == self.RIGHT:
                            index += 1
                        action = msg.edit
                except asyncio.TimeoutError:
                    await msg.add_reaction(self.PAGINATION_TIMEOUT)
                    return
            else:
                await ctx.send(lang["moderation_warnings_empty"].format(ctx.author.mention, str(member)), delete_after=10)

    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.has_permissions(kick_members=True, ban_members=True)
    @commands.guild_only()
    @warnings.command(cls=ExtendedCommand, name='reset', description=main.lang["command_warnings_reset_description"], usage='@someone', aliases=['clear'], permissions=['Kick Members', 'Ban Members'])
    async def warnings_reset(self, ctx, members: commands.Greedy[discord.Member]):
        if members:
            output = ""
            for member in members:
                await self.Warnings.reset_warnings(ctx.guild.id, member.id)
                output += f'{str(member)} ({member.mention})\n'
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            await ctx.message.delete()

            output = self.slice_userlist(output, 20, lang)
            if len(output.strip()) > 0:
                embed = discord.Embed(title=lang["moderation_warnings_reset_embed_title"], description=lang["moderation_warnings_reset_embed_description"], timestamp=datetime.utcnow(), color=self.embed_color_alt)
                embed.add_field(name=lang["users_string"], value=output or lang["empty_string"], inline=True)
                embed.set_footer(text=lang["moderation_warnings_reset_embed_footer"].format(str(ctx.author)))
                await ctx.send(embed=embed)
            else:
                await ctx.send(lang["moderation_warnings_reset_empty"].format(ctx.author.mention), delete_after=10)

    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.has_permissions(kick_members=True, ban_members=True)
    @commands.guild_only()
    @warnings.command(cls=ExtendedCommand, name='delete', description=main.lang["command_warnings_delete_description"], usage='@someone 3', aliases=['remove', 'del'], permissions=['Kick Members', 'Ban Members'])
    async def warnings_delete(self, ctx, member: discord.Member, number: int):
        if number >= 1:
            index = number - 1
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            try:
                await ctx.message.delete()
                await self.Warnings.delete_warning(ctx.guild.id, member.id, index)
                embed = discord.Embed(title=lang["moderation_warnings_delete"].format(number, str(member)), color=self.embed_color_alt)
            except IndexError:
                embed = discord.Embed(title=lang["moderation_warnings_outofrange"], color=self.embed_color_alt)
            await ctx.send(embed=embed)

    @commands.cooldown(10, 60, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @warnings.group(cls=ExtendedGroup, name='auto', invoke_without_command=True, help=main.lang["command_autoaction_help"], description=main.lang["command_autoaction_description"], usage='mute/kick/ban 5', permissions=['Administrator'])
    async def warnings_autoaction(self, ctx, action: str, number: int):
        if not ctx.invoked_subcommand:
            if number > 0:
                lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
                if number <= self.max_warnings:
                    action_lowered = action.lower()
                    if action_lowered in ('mute', 'kick', 'ban'):
                        await self.AutoActions.set_value(ctx.guild.id, action, number)
                        embed = discord.Embed(title=lang["moderation_autoaction_success"].format(action_lowered, number), color=self.embed_color)
                else:
                    embed = discord.Embed(title=lang["moderation_autoaction_max"].format(self.max_warnings), color=self.embed_color)
                await ctx.send(embed=embed)

    @commands.cooldown(10, 60, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @warnings_autoaction.command(cls=ExtendedCommand, name='disable', description=main.lang["command_autoaction_disable_description"], usage='mute/kick/ban', aliases=['d', 'off'], permissions=['Administrator'])
    async def warnings_autoaction_disable(self, ctx, action: str):
        if action.lower() in ('mute', 'kick', 'ban'):
            await self.AutoActions.disable_autoaction(ctx.guild.id, action)
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            embed = discord.Embed(title=lang["moderation_autoaction_disable"].format(action.lower()), color=self.embed_color)
            await ctx.send(embed=embed)

    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.group(cls=ExtendedGroup, name='blacklist', invoke_without_command=True, description=main.lang["command_blacklist_description"], usage='@someone', permissions=['Administrator'])
    async def blacklist(self, ctx, members: commands.Greedy[discord.Member]):
        if not ctx.invoked_subcommand:
            await self.blacklist_add(ctx, members)
    
    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @blacklist.command(cls=ExtendedCommand, name='add', description=main.lang["command_blacklist_add_description"], usage='@someone', aliases=['a'], permissions=['Administrator'])
    async def blacklist_add(self, ctx, members: commands.Greedy[discord.Member]):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        member_ids = [x.id for x in members]
        if ctx.message.author.id not in member_ids:
            blacklisted_users = ""
            for member in members:
                if not self.BlacklistedUsers.is_blacklisted(member.id, ctx.guild.id):
                    await self.BlacklistedUsers.blacklist(member.id, ctx.guild.id)
                    blacklisted_users += f'{str(member)} ({member.mention})\n'
            await ctx.message.delete()


            blacklisted_users = self.slice_userlist(blacklisted_users, 20, lang)
            if len(blacklisted_users.strip()) > 0:
                embed = discord.Embed(title=lang["moderation_blacklist_embed_title"], description=lang["moderation_blacklist_embed_description"], timestamp=datetime.utcnow(), color=self.embed_color)
                embed.add_field(name=lang["users_string"], value=blacklisted_users or lang["empty_string"], inline=True)
                embed.set_footer(text=lang["moderation_blacklist_embed_footer"].format(str(ctx.author)))
                await ctx.send(embed=embed)
            else:
                await ctx.send(lang["moderation_blacklist_empty"].format(ctx.author.mention), delete_after=10)
        else:
            await ctx.send(lang["moderation_blacklist_self"].format(ctx.author.mention), delete_after=10)
        
    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @blacklist.command(cls=ExtendedCommand, name='remove', description=main.lang["command_blacklist_remove_description"], usage='@someone', aliases=['r'], permissions=['Administrator'])
    async def blacklist_remove(self, ctx, members: commands.Greedy[discord.Member]):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        member_ids = [x.id for x in members]
        if ctx.message.author.id not in member_ids:
            discharged_users = ""
            for member in members:
                if self.BlacklistedUsers.is_blacklisted(member.id, ctx.guild.id):
                    await self.BlacklistedUsers.remove_blacklist(member.id, ctx.guild.id)
                    discharged_users += f'{str(member)} ({member.mention})\n'
            await ctx.message.delete()


            discharged_users = self.slice_userlist(discharged_users, 20, lang)
            if len(discharged_users.strip()) > 0:
                embed = discord.Embed(title=lang["moderation_blacklist_remove_embed_title"], description=lang["moderation_blacklist_remove_embed_description"], timestamp=datetime.utcnow(), color=self.embed_color_alt)
                embed.add_field(name=lang["users_string"], value=discharged_users or lang["empty_string"], inline=True)
                embed.set_footer(text=lang["moderation_blacklist_remove_embed_footer"].format(str(ctx.author)))
                await ctx.send(embed=embed)
            else:
                await ctx.send(lang["moderation_blacklist_remove_empty"].format(ctx.author.mention), delete_after=10)
        else:
            await ctx.send(lang["moderation_blacklist_remove_self"].format(ctx.author.mention), delete_after=10)

def setup(bot):
    bot.add_cog(Moderation(bot))