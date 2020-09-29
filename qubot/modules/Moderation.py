from libs.utils.admintools import Reports, Warnings, MuteRole, AutoWarningActions, BlacklistedUsers
from libs.utils.admintools import ModerationAction, TemporaryActions
from libs.utils.servertoggles import ServerToggles
from discord.ext import tasks, commands
from main import bot_starttime
from main import modules as loaded_modules
from datetime import datetime, timedelta
import libs.qulib as qulib
import discord
import main
import time
import re

class BannedUser(commands.UserConverter):
    async def convert(self, ctx, argument):
        banned_users = await ctx.guild.bans()
        try:
            ban_entry = discord.utils.find(lambda m: m.user.id == int(argument, base=10), banned_users)
        except ValueError:
            ban_entry = discord.utils.find(lambda m: str(m.user) == argument, banned_users)

        if ban_entry is None:
            raise commands.BadArgument("Failed to convert user input to User Object. User was not found in banned user list.")
        return ban_entry.user

class TimePeriod(commands.Converter):
    
    def __init__(self):
        self.time_units = {'m':'minutes', 'h':'hours', 'd':'days', 'w':'weeks'}

    async def convert(self, ctx, argument):
        time_in_seconds = int(timedelta(**{self.time_units.get(m.group('unit').lower(), 'minutes'): int(m.group('val')) for m in re.finditer(r'(?P<val>\d+)(\s?)(?P<unit>[mhdw]?)', argument, flags=re.I)}).total_seconds())

        if time_in_seconds == 0:
            raise commands.BadArgument("Failed to convert user input to a valid time frame.")
        return time_in_seconds

class SmallTimePeriod(commands.Converter):
    
    def __init__(self):
        self.time_units = {'s': 'seconds', 'm':'minutes', 'h':'hours'}

    async def convert(self, ctx, argument):
        time_in_seconds = int(timedelta(**{self.time_units.get(m.group('unit').lower(), 'seconds'): int(m.group('val')) for m in re.finditer(r'(?P<val>\d+)(\s?)(?P<unit>[mhdw]?)', argument, flags=re.I)}).total_seconds())
        return time_in_seconds
        
class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0xdc143c
        print(f'Module {self.__class__.__name__} loaded')

        self.max_warnings = 20
        self.max_characters = 1500
        self.purge_limit = 100

        self.max_slowmode_value = 21600

        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = False
        self.module_dependencies = []

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)

        self.Reports = Reports()
        self.Warnings = Warnings()
        self.MuteRole = MuteRole()
        self.AutoActions = AutoWarningActions()
        self.Toggles = ServerToggles()
        self.BlacklistedUsers = BlacklistedUsers()
        self.TemporaryActions = TemporaryActions()

        self.temporary_actions.start() # pylint: disable=no-member

    def cog_unload(self):
        self.temporary_actions.cancel() # pylint: disable=no-member

    @tasks.loop(minutes=1, reconnect=True)
    async def temporary_actions(self):
        time_on_iter = int(time.time())
        guild_dict = await TemporaryActions.get_expired_actions(time_on_iter)

        for guild_id in guild_dict:
            guild = self.bot.get_guild(guild_id)
            if guild:
                for user_id, action in guild_dict[guild_id]:
                    if action == int(ModerationAction.Ban):
                        banned_users = await guild.bans()
                        ban_entry = discord.utils.find(lambda m: m.user.id == user_id, banned_users)
                        if ban_entry is not None:
                            await guild.unban(ban_entry.user, reason="Temporary ban has expired for the following individual.")
                    elif action == int(ModerationAction.TextMute):
                        member = guild.get_member(user_id)
                        if member:
                            role = await Moderation.get_mute_role(guild)
                            user_rlist = [x.id for x in member.roles]
                            if role.id in user_rlist:
                                await member.remove_roles(role)

        await TemporaryActions.clear_expired_actions(time_on_iter)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(manage_messages=True)
    @commands.command(name='purge', help=main.lang["command_purge_help"], description=main.lang["command_purge_description"], usage="10", ignore_extra=True)
    @commands.guild_only()
    async def purge(self, ctx, prune_num: int, filters: str = None):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if prune_num > 0:
            await ctx.message.delete()
            prune_num = self.purge_limit if prune_num > self.purge_limit else prune_num
            if filters:
                if filters.lower() == "bot" or filters.lower() == "bots":
                    def is_bot(message):
                        return message.author.bot

                    deleted = await ctx.channel.purge(limit=prune_num, check=is_bot, bulk=True)
                    embed = discord.Embed(title=lang["administration_purge_delmsg"].format(len(deleted)), color=self.module_embed_color)
                else:
                    embed = discord.Embed(title=lang["administration_purge_invalid_filter"], color=self.module_embed_color)
            else:
                deleted = await ctx.channel.purge(limit=prune_num, bulk=True)
                embed = discord.Embed(title=lang["administration_purge_delmsg"].format(len(deleted)), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_purge_prmsg"], color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=10)
    
    @commands.command(name='kick', help=main.lang["command_kick_help"], description=main.lang["command_kick_description"], usage="@somebody Spamming")
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, user: discord.Member, *, kick_reason: str = None):   
        await ctx.guild.kick(user, reason=kick_reason)
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["administration_kick_msg"].format(user,kick_reason), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name='ban', help=main.lang["command_ban_help"], description=main.lang["command_ban_description"], usage="@somebody Harassment")
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, user: discord.Member, *, reason: str = None):
        await ctx.guild.ban(user, reason=reason)
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["administration_ban_msg"].format(str(user), reason), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name='tempban', help=main.lang["command_tempban_help"], description=main.lang["command_tempban_description"], usage='@somebody "2 weeks 5 days" Harassment', aliases=['tban'])
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def temp_ban(self, ctx, user: discord.Member, time_period: TimePeriod, *, reason: str = None):
        unix_timestamp = int(time.time() + time_period)
        timestamp = datetime.fromtimestamp(unix_timestamp) + timedelta(seconds=60)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if not TemporaryActions.is_banned(user.id, ctx.guild.id):
            if await TemporaryActions.set_action(user.id, ctx.guild.id, ModerationAction.Ban, unix_timestamp):
                await user.send(lang["administration_tempban_dm"].format(ctx.guild.name, timestamp.strftime('%d/%m/%Y at %H:%M')))
                await ctx.guild.ban(user, reason=reason)
                await ctx.message.delete()
                embed = discord.Embed(title=lang["administration_tempban_ban"].format(str(user), timestamp.strftime('%d/%m/%Y at %H:%M'), reason), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["administration_tempban_error"].format(str(user)), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_tempban_already_banned"].format(str(user)), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name='unban', help=main.lang["command_unban_help"], description=main.lang["command_unban_description"], usage="User#1234 OR 116267141744820233")
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, user: BannedUser):
        await TemporaryActions.clear_action(user.id, ctx.guild.id, ModerationAction.Ban)
        await ctx.guild.unban(user)
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["administration_unban_msg"].format(str(user)), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name='softban', help=main.lang["command_softban_help"], description=main.lang["command_softban_description"], usage="@somebody Harassment")
    @commands.has_permissions(kick_members=True, manage_messages=True)
    @commands.guild_only()
    async def softban(self, ctx, user: discord.Member, *, reason: str = None):
        await ctx.guild.ban(user, reason=reason)
        await ctx.guild.unban(user, reason=reason)
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["administration_softban_msg"].format(str(user), reason), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name='mute', help=main.lang["empty_string"], description=main.lang["command_mute_description"], usage='@somebody')
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def mute(self, ctx, user: discord.Member):
        async with ctx.channel.typing():
            role = await Moderation.get_mute_role(ctx.guild)
        user_rlist = [x.id for x in user.roles]
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if role.id not in user_rlist:
            await user.add_roles(role)
            embed = discord.Embed(title=lang["administration_mute_success"].format(str(user)), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_mute_muted"].format(str(user)), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name='tempmute', help=main.lang["command_tempmute_help"], description=main.lang["command_tempmute_description"], usage='@somebody 2 weeks 5 days', aliases=['tmute'])
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def temp_mute(self, ctx, user: discord.Member, *, time_period: TimePeriod):
        async with ctx.channel.typing():
            role = await Moderation.get_mute_role(ctx.guild)
        user_rlist = [x.id for x in user.roles]
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if role.id not in user_rlist and not TemporaryActions.is_textmuted(user.id, ctx.guild.id):
            await user.add_roles(role)
            unix_timestamp = int(time.time() + time_period)
            timestamp = datetime.fromtimestamp(unix_timestamp) + timedelta(seconds=60)
            await TemporaryActions.set_action(user.id, ctx.guild.id,ModerationAction.TextMute, unix_timestamp)
            await user.send(lang["administration_tempmute_dm"].format(ctx.guild.name, timestamp.strftime('%d/%m/%Y at %H:%M')))
            embed = discord.Embed(title=lang["administration_tempmute_mute"].format(str(user), timestamp.strftime('%d/%m/%Y at %H:%M')), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_mute_muted"].format(str(user)), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name='unmute', help=main.lang["empty_string"], description=main.lang["command_unmute_description"], usage='@somebody')
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def unmute(self, ctx, user: discord.Member):
        async with ctx.channel.typing():
            role = await Moderation.get_mute_role(ctx.guild)
        user_rlist = [x.id for x in user.roles]
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if role.id in user_rlist:
            await user.remove_roles(role)
            await TemporaryActions.clear_action(user.id, ctx.guild.id, ModerationAction.TextMute)
            embed = discord.Embed(title=lang["administration_unmute_success"].format(str(user)), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_unmute_unmuted"].format(str(user)), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)

    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.group(name='slowmode', invoke_without_command=True, help=main.lang["command_slowmode_help"], description=main.lang["command_slowmode_description"], usage='15', aliases=['sm'])
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    @commands.guild_only()
    async def slowmode(self, ctx, *, time_period: SmallTimePeriod):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if time_period <= self.max_slowmode_value:
                await ctx.channel.edit(slowmode_delay=time_period)
                if time_period == 0:
                    embed = discord.Embed(title=lang["administration_slowmode_disabled"], color=self.module_embed_color)
                else:
                    hours = int(time_period/3600)
                    hour_string = lang["hours_string"] if hours != 1 else lang["hour_string"]
                    minutes = int((time_period/60)%60)
                    minutes_string = lang["minutes_string"] if minutes != 1 else lang["minute_string"]
                    seconds = int(time_period%60)
                    seconds_string = lang["seconds_string"] if seconds != 1 else lang["second_string"]

                    formatted_time_string = f"{f'{hours} {hour_string} ' if hours != 0 else ''}{f'{minutes} {minutes_string} ' if minutes != 0 else ''}{f'{seconds} {seconds_string}' if seconds != 0 else ''}"
                    
                    embed = discord.Embed(title=lang["administration_slowmode_enabled"].format(formatted_time_string), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["administration_slowmode_max"].format(int(self.max_slowmode_value/3600)), color=self.module_embed_color)    
            await ctx.send(embed=embed, delete_after=15)

    @commands.cooldown(5, 30, commands.BucketType.user)
    @slowmode.command(name='disable', help=main.lang["empty_string"], description=main.lang["command_slowmode_disable_description"], aliases=['off'])
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    @commands.guild_only()
    async def slowmode_disable(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.channel.edit(slowmode_delay=0)
        embed = discord.Embed(title=lang["administration_slowmode_disabled"], color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=15)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(send_messages=True)
    @commands.guild_only()
    @commands.group(name='report', invoke_without_command=True, help=main.lang["command_report_help"], description=main.lang["command_report_description"], usage='@somebody Spamming')
    async def report_group(self, ctx, user: discord.User, *, reason: str):
        if not ctx.invoked_subcommand:
            if user.id != ctx.author.id:
                channel_id = await self.Reports.get_channel(ctx.guild.id)
                if channel_id:
                    await ctx.message.delete()
                    channel = self.bot.get_channel(channel_id)
                    lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
                    embed = discord.Embed(title=lang["administration_report_title"], color=self.module_embed_color)
                    embed.add_field(name=lang["user_string"], value=user, inline=True)
                    embed.add_field(name=lang["reason_string"], value=reason, inline=True)
                    embed.set_footer(text=lang["administration_report_reportedby"].format(ctx.author))
                    await channel.send(embed=embed)
            else:
                raise commands.BadArgument("Failed to report user. Message author matches target user.")

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @report_group.command(name='setchannel', help=main.lang["command_setchannel_help"], description=main.lang["command_setchannel_description"], usage='#general')
    async def report_setchannel(self, ctx, channel: discord.TextChannel):
        await self.Reports.set_channel(ctx.guild.id, channel.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["administration_setchannel_msg"].format(str(channel)), color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @report_group.command(name='disable', help=main.lang["command_report_disable_help"], description=main.lang["command_report_disable_description"])
    async def report_disable(self, ctx):
        channel_id = await self.Reports.get_channel(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if channel_id:
            await self.Reports.disable(ctx.guild.id)
            embed = discord.Embed(title=lang["administration_report_disable_success"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_report_disable_fail"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.has_permissions(kick_members=True, ban_members=True)
    @commands.guild_only()
    @commands.command(name='warn', help=main.lang["command_warn_help"], description=main.lang["command_warn_description"], usage='@someone Spamming')
    async def warn_user(self, ctx, user: discord.Member, *, warning: str):
        if user.id != ctx.author.id:
            await ctx.message.delete()
            user_warnings = await self.Warnings.get_warning_count(ctx.guild.id, user.id)
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if user_warnings < self.max_warnings:
                await self.Warnings.add_warning(user.id, warning, ctx.author.id, ctx.guild.id)
                dm_embed = discord.Embed(title=lang["administration_warn_dm_title"], color=self.module_embed_color)
                dm_embed.add_field(name=lang["warning_string"], value=warning, inline=True)
                dm_embed.add_field(name=lang["administration_warn_dm_warnedby"], value=str(ctx.author), inline=True)
                dm_embed.set_footer(text=lang["administration_warn_dm_footer"].format(str(ctx.guild)))
                await user.send(embed=dm_embed)

                embed = discord.Embed(title=lang["administration_warn_success"].format(str(user)), color=self.module_embed_color)
                await ctx.send(embed=embed, delete_after=5)

                user_warnings = user_warnings + 1

                actions = await self.AutoActions.get_actions(ctx.guild.id)
                if actions:
                    #Automatic Ban (Takes priority over kick if they both trigger on the same number)
                    if actions[2] != None and user_warnings >= actions[2]:
                        await ctx.guild.ban(user, reason=lang["administration_autoaction_ban"])
                        return
                    #Automatic Kick
                    if actions[1] != None and user_warnings >= actions[1]:
                        await ctx.guild.kick(user, reason=lang["administration_autoaction_kick"])
                        return
                    #Automatic Mute
                    if actions[0] != None and user_warnings >= actions[0]:
                        async with ctx.channel.typing():
                            role = await Moderation.get_mute_role(ctx.guild)
                        role_find = discord.utils.get(user.roles, id=role.id)
                        if not role_find:
                           await user.add_roles(role)
            else:
                embed = discord.Embed(title=lang["administration_warn_max"].format(self.max_warnings), color=self.module_embed_color)
                await ctx.send(embed=embed, delete_after=30)
        else:
            raise commands.BadArgument("Failed to warn user. Message author matches target user.")

    @commands.has_permissions(kick_members=True, ban_members=True)
    @commands.guild_only()
    @commands.group(name='warnings', invoke_without_command=True, help=main.lang["command_warnings_help"], description=main.lang["command_warnings_description"], usage='@someone 2')
    async def warnings_group(self, ctx, user: discord.User, page: int = 1):
        if not ctx.invoked_subcommand:
            if page >= 1:
                page_index = page - 1
                await ctx.message.delete()
                warnings = await self.Warnings.get_warnings(ctx.guild.id, user.id)
                pages = int(len(warnings)/5)
                lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
                if len(warnings[(page_index*5):(page_index*5 + 5)]) > 0:
                    embed = discord.Embed(title=lang["administration_warnings_title"].format(str(user)), color=self.module_embed_color)
                    embed.set_footer(text=f'{lang["page_string"]} {page}/{pages}')
                    for warning in warnings[(page_index*5):(page_index*5 + 5)]:
                        warned_by = self.bot.get_user(warning[1])
                        embed.add_field(name=f'{lang["warning_string"]}: **{warning[0]}**', value=lang["administration_warnings_issuedby"].format(warned_by), inline=False)
                else:
                    embed = discord.Embed(title=lang["pager_outofrange"], color=self.module_embed_color)
                await ctx.send(embed=embed)
            else:
                raise commands.BadArgument("User warnings page index is out of range.")

    @warnings_group.command(name='reset', help=main.lang["command_warnings_reset_help"], description=main.lang["command_warnings_reset_description"], usage='@someone', aliases=['clear'])
    async def warnings_reset(self, ctx, *, user: discord.User):
        await ctx.message.delete()
        await self.Warnings.reset_warnings(ctx.guild.id, user.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["administration_warnings_reset"].format(str(user)), color=self.module_embed_color)
        await ctx.send(embed=embed)

    @warnings_group.command(name='delete', help=main.lang["command_warnings_delete_help"], description=main.lang["command_warnings_delete_description"], usage='@someone 3', aliases=['remove'])
    async def warnings_delete(self, ctx, user: discord.User, number: int):
        if number >= 1:
            index = number - 1
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            try:
                await ctx.message.delete()
                await self.Warnings.delete_warning(ctx.guild.id, user.id, index)
                embed = discord.Embed(title=lang["administration_warnings_delete"].format(number, str(user)), color=self.module_embed_color)
            except IndexError:
                embed = discord.Embed(title=lang["administration_warnings_outofrange"], color=self.module_embed_color)
            await ctx.send(embed=embed)

    @warnings_group.group(name='auto', invoke_without_command=True, help=main.lang["command_autoaction_help"], description=main.lang["command_autoaction_description"], usage='mute/kick/ban 5')
    async def warnings_autoaction(self, ctx, action: str, number: int):
        if not ctx.invoked_subcommand:
            if number > 0:
                lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
                if number <= self.max_warnings:
                    if action.lower() in ('mute', 'kick', 'ban'):
                        await self.AutoActions.set_value(ctx.guild.id, action, number)
                        embed = discord.Embed(title=lang["administration_autoaction_msg"].format(action.lower(), number), color=self.module_embed_color)
                else:
                    embed = discord.Embed(title=lang["administration_autoaction_max"].format(self.max_warnings), color=self.module_embed_color)
                await ctx.send(embed=embed)

    @warnings_autoaction.command(name='disable', help=main.lang["command_autoaction_disable_help"], description=main.lang["command_autoaction_disable_description"], usage='mute/kick/ban')
    async def warnings_disable_autoaction(self, ctx, action: str):
        if action.lower() in ('mute', 'kick', 'ban'):
            await self.AutoActions.disable_autoaction(ctx.guild.id, action)
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            embed = discord.Embed(title=lang["administration_autoaction_disable_msg"].format(action.lower()), color=self.module_embed_color)
            await ctx.send(embed=embed)

    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.group(name='blacklist', invoke_without_command=True, help=main.lang["command_blacklist_help"], description=main.lang["command_blacklist_description"], usage='@someone')
    async def blacklist(self, ctx, member: discord.Member):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if not ctx.invoked_subcommand:
            if ctx.message.author.id != member.id:
                if not BlacklistedUsers.is_blacklisted(member.id, ctx.guild.id):
                    await BlacklistedUsers.blacklist(member.id, ctx.guild.id)
                    embed = discord.Embed(title=lang["administration_blacklist_add"].format(str(member)), color=self.module_embed_color)
                else:
                    await BlacklistedUsers.remove_blacklist(member.id, ctx.guild.id)
                    embed = discord.Embed(title=lang["administration_blacklist_remove"].format(str(member)), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["administration_blacklist_self"], color=self.module_embed_color)
            await ctx.send(embed=embed, delete_after=15)

    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @blacklist.command(name='add', help=main.lang["command_blacklist_help"], description=main.lang["command_blacklist_add_description"], usage='@someone', aliases=['a'])
    async def blacklist_add(self, ctx, member: discord.Member):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if ctx.message.author.id != member.id:
            if not BlacklistedUsers.is_blacklisted(member.id, ctx.guild.id):
                await BlacklistedUsers.blacklist(member.id, ctx.guild.id)
                embed = discord.Embed(title=lang["administration_blacklist_add"].format(str(member)), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["administration_blacklist_in_list"].format(str(member)), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_blacklist_self"], color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=15)

    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @blacklist.command(name='remove', help=main.lang["command_blacklist_help"], description=main.lang["command_blacklist_remove_description"], usage='@someone', aliases=['r'])
    async def blacklist_remove(self, ctx, member: discord.Member):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if ctx.message.author.id != member.id:
            if BlacklistedUsers.is_blacklisted(member.id, ctx.guild.id):
                await BlacklistedUsers.remove_blacklist(member.id, ctx.guild.id)
                embed = discord.Embed(title=lang["administration_blacklist_remove"].format(str(member)), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["administration_blacklist_not_in_list"].format(str(member)), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_blacklist_remove_self"], color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=15)

    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.group(name='greet', help=main.lang["command_greetings_help"], description=main.lang["command_greetings_description"], aliases=['greetings'])
    async def server_greetings(self, ctx):
        if not ctx.invoked_subcommand:
            status = await self.Toggles.get_greet_status(ctx.guild.id)
            if status:
                await ctx.invoke(self.greetings_disable)
            else:
                await ctx.invoke(self.greetings_enable)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @server_greetings.command(name='enable', aliases=['on'], help=main.lang["command_greetings_enable_help"], description=main.lang["command_greetings_enable_description"], ignore_extra=True)
    async def greetings_enable(self, ctx):
        status = await self.Toggles.get_greet_status(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if status != 1:
            await self.Toggles.enable_greeting(ctx.guild.id, False)
            embed = discord.Embed(title=lang["administration_genable_success"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_genable_enabled"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @server_greetings.command(name='disable', aliases=['off'], help=main.lang["command_greetings_disable_help"], description=main.lang["command_greetings_disable_description"], ignore_extra=True)
    async def greetings_disable(self, ctx):
        status = await self.Toggles.get_greet_status(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if status:
            await self.Toggles.disable_greeting(ctx.guild.id)
            embed = discord.Embed(title=lang["administration_gdisable_success"], color=self.module_embed_color)   
        else:
            embed = discord.Embed(title=lang["administration_gdisable_disabled"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @server_greetings.command(name='dm', help=main.lang["command_greetings_dm_help"], description=main.lang["command_greetings_dm_description"], ignore_extra=True)
    async def greetings_enable_dm(self, ctx):
        await self.Toggles.enable_greeting(ctx.guild.id, True)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["administration_gdm_msg"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @server_greetings.command(name='test', help=main.lang["command_greetings_test_help"], description=main.lang["command_greetings_test_description"], ignore_extra=True)
    @commands.has_permissions(administrator=True)
    async def greetings_test(self, ctx):
        await self.on_member_join(ctx.message.author)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @server_greetings.group(name='message', invoke_without_command=True, help=main.lang["command_greetings_message_help"], description=main.lang["command_greetings_message_description"], usage="Welcome {mention} to {server}!")
    async def greetings_custom_message(self, ctx, *, message: str):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if len(message) <= self.max_characters:
            if await self.Toggles.get_greet_status(ctx.guild.id):
                try:
                    message = message.lstrip()
                    message = message.replace("\\n", "\n")
                    await self.Toggles.set_greet_msg(ctx.guild.id, message)
                    embed = discord.Embed(title=lang["administration_gmessage_success"], color=self.module_embed_color)
                except ValueError:
                    embed = discord.Embed(title=lang["administration_gmessage_invalid"], color=self.module_embed_color) 
            else:
                embed = discord.Embed(title=lang["administration_gmessage_disabled"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_gmessage_limit"].format(self.max_characters), color=self.module_embed_color)
        await ctx.send(embed=embed)

    @greetings_custom_message.command(name='default', help=main.lang["command_greetings_mdefault_help"], description=main.lang["command_greetings_mdefault_description"])
    async def greetings_custom_message_reset(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.Toggles.has_custom_greeting(ctx.guild.id):
            await self.Toggles.reset_greet_msg(ctx.guild.id)
            embed = discord.Embed(title=lang["administration_gmessage_default_success"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_gmessage_default_used"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @server_greetings.group(name='setchannel', invoke_without_command=True, help=main.lang["command_greetings_setchannel_help"], description=main.lang["command_greetings_setchannel_description"], usage="#general")
    async def greetings_setchannel(self, ctx, *, channel: discord.TextChannel):
        await self.Toggles.set_channel(ctx.guild.id, channel.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["administration_gsetchannel"].format(channel.name), color=self.module_embed_color)
        await ctx.send(embed=embed)

    @greetings_setchannel.command(name='default', help=main.lang["command_greetings_scdefault_help"], description=main.lang["command_greetings_scdefault_description"])
    async def greetings_setchannel_reset(self, ctx):
        await self.Toggles.set_channel(ctx.guild.id, None)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["administration_gscdefault_msg"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        status = await self.Toggles.get_greet_status(member.guild.id)
        if status:
            channel_id = await self.Toggles.get_channel(member.guild.id)
            if channel_id:
                channel = await self.bot.fetch_channel(channel_id)
            else:
                channel = discord.utils.find(lambda c: c.name == "general", member.guild.text_channels)
                if not channel:
                    channel = discord.utils.find(lambda c: member.guild.me.permissions_in(c).send_messages == True, member.guild.text_channels)
            if channel:
                if await self.Toggles.has_custom_greeting(member.guild.id):
                    message = await self.Toggles.get_custom_greeting(member.guild.id)
                    message = await Moderation.format_message(message, member)
                else:
                    lang = main.get_lang(member.guild.id)
                    message = lang["administration_greet_default"].format(member.mention, member.guild.name)

                if status == 2:
                    await member.send(message)
                else:
                    await channel.send(message)

    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.group(name='bye', help=main.lang["command_goodbye_help"], description=main.lang["command_goodbye_description"], aliases=['goodbye'])
    async def server_goodbye(self, ctx):
        if not ctx.invoked_subcommand:
            status = await self.Toggles.get_bye_status(ctx.guild.id)
            if status:
                await ctx.invoke(self.goodbye_disable)
            else:
                await ctx.invoke(self.goodbye_enable)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @server_goodbye.command(name='enable', aliases=['on'], help=main.lang["command_goodbye_enable_help"], description=main.lang["command_goodbye_enable_description"], ignore_extra=True)
    async def goodbye_enable(self, ctx):
        status = await self.Toggles.get_bye_status(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if status != 1:
            await self.Toggles.enable_goodbye(ctx.guild.id)
            embed = discord.Embed(title=lang["administration_gbenable_success"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_gbenable_enabled"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @server_goodbye.command(name='disable', aliases=['off'], help=main.lang["command_goodbye_disable_help"], description=main.lang["command_goodbye_disable_description"], ignore_extra=True)
    async def goodbye_disable(self, ctx):
        status = await self.Toggles.get_bye_status(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if status:
            await self.Toggles.disable_goodbye(ctx.guild.id)
            embed = discord.Embed(title=lang["administration_gbdisable_success"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_gbdisable_disabled"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @server_goodbye.command(name='test', help=main.lang["command_goodbye_test_help"], description=main.lang["command_goodbye_test_description"], ignore_extra=True)
    @commands.has_permissions(administrator=True)
    async def goodbye_test(self, ctx):
        await self.on_member_remove(ctx.message.author)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @server_goodbye.group(name='message', invoke_without_command=True, help=main.lang["command_goodbye_message_help"], description=main.lang["command_goodbye_message_description"], usage="Goodbye, {mention}!")
    async def goodbye_custom_message(self, ctx, *, message: str):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if len(message) <= self.max_characters:
            if await self.Toggles.get_bye_status(ctx.guild.id):
                try:
                    message = message.lstrip()
                    message = message.replace("\\n", "\n")
                    await self.Toggles.set_bye_msg(ctx.guild.id, message)
                    embed = discord.Embed(title=lang["administration_gbmessage_success"], color=self.module_embed_color)
                except ValueError:
                    embed = discord.Embed(title=lang["administration_gbmessage_invalid"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["administration_gbmessage_disabled"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_gmessage_limit"].format(self.max_characters), color=self.module_embed_color)
        await ctx.send(embed=embed)

    @goodbye_custom_message.command(name='default', help=main.lang["command_goodbye_mdefault_help"], description=main.lang["command_goodbye_mdefault_description"])
    async def goodbye_custom_message_reset(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.Toggles.has_custom_goodbye(ctx.guild.id):
            await self.Toggles.reset_bye_msg(ctx.guild.id)
            embed = discord.Embed(title=lang["administration_gbmessage_default_success"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_gbmessage_default_used"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @server_goodbye.group(name='setchannel', invoke_without_command=True, help=main.lang["command_greetings_setchannel_help"], description=main.lang["command_greetings_setchannel_description"], usage="#general")
    async def goodbye_setchannel(self, ctx, *, channel: discord.TextChannel):
        await ctx.invoke(self.greetings_setchannel, channel=channel)

    @goodbye_setchannel.command(name='default', help=main.lang["command_greetings_scdefault_help"], description=main.lang["command_greetings_scdefault_description"])
    async def goodbye_setchannel_reset(self, ctx):
        await ctx.invoke(self.greetings_setchannel_reset)

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_guild_remove(self, guild):
        await BlacklistedUsers.remove_blacklist_guild(guild.id)
        await TemporaryActions.wipe_guild_data(guild.id)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        status = await self.Toggles.get_bye_status(member.guild.id)
        if member and member.id != self.bot.user.id and status:
            channel_id = await self.Toggles.get_channel(member.guild.id)
            if channel_id:
                channel = await self.bot.fetch_channel(channel_id)
            else:
                channel = discord.utils.find(lambda c: c.name == "general", member.guild.text_channels)
                if not channel:
                    channel = discord.utils.find(lambda c: member.guild.me.permissions_in(c).send_messages == True, member.guild.text_channels)
            if channel:
                if await self.Toggles.has_custom_goodbye(member.guild.id):
                    message = await self.Toggles.get_custom_goodbye(member.guild.id)
                    message = await Moderation.format_message(message, member)
                else:
                    lang = main.get_lang(member.guild.id)
                    message = lang["administration_bye_default"].format(str(member), member.guild.name)
                await channel.send(message)

    @staticmethod
    async def get_mute_role(guild: discord.Guild):
        mute_role = await MuteRole.get_mute_role(guild.id)
        role = discord.utils.get(guild.roles, name='Muted')
        if not role:
            role = await guild.create_role(name="Muted", permissions=discord.Permissions(send_messages = False), reason="Created mute role to support bot moderation functionality.")
        if mute_role == None or mute_role != role.id:
            await Moderation.update_mute_role(role, guild)
            await MuteRole.set_mute_role(guild.id, role.id)
        
        return role

    @staticmethod
    async def update_mute_role(role: discord.Role, guild: discord.Guild):
        for channel in guild.text_channels:
            perms = channel.permissions_for(guild.me)
            if perms.manage_roles:
                channel_overwrite = channel.overwrites_for(role)
                channel_overwrite.send_messages = False
                channel_overwrite.add_reactions = False
                
                await channel.set_permissions(role, overwrite=channel_overwrite)

    @staticmethod
    async def format_message(message: str, member: discord.Member):
        message = message.replace("{mention}", member.mention)
        message = message.replace("{user}", str(member))
        message = message.replace("{server}", member.guild.name)
        message = message.replace("{membercount}", str(member.guild.member_count))
        return message

def setup(bot):
    bot.add_cog(Moderation(bot))