from libs.utils.admintools import Reports, Warnings, MuteRole, AutoWarningActions
from libs.utils.servertoggles import ServerToggles
from discord.ext import commands
from main import bot_starttime
from main import modules as loaded_modules
from datetime import datetime
import libs.qulib as qulib
import discord
import main

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

class Administration(commands.Cog):
    """Administration"""

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0xdc143c
        print(f'Module {self.__class__.__name__} loaded')

        self.max_warnings = 20
        self.max_characters = 1500

        self.Reports = Reports()
        self.Warnings = Warnings()
        self.MuteRole = MuteRole()
        self.AutoActions = AutoWarningActions()
        self.Toggles = ServerToggles()

    @commands.command(name='purge', help=main.lang["command_purge_help"], description=main.lang["command_purge_description"], usage="10", ignore_extra=True)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def purge(self, ctx, prune_num: int):
        lang = main.get_lang(ctx.guild.id)
        if prune_num > 0:
            await ctx.message.delete()
            await ctx.channel.purge(limit=prune_num,bulk=True)
            embed = discord.Embed(title=lang["administration_purge_delmsg"].format(prune_num), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_purge_prmsg"], color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=10)
    
    @commands.command(name='kick', help=main.lang["command_kick_help"], description=main.lang["command_kick_description"], usage="@somebody Spamming")
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, user: discord.Member, *, kick_reason: str = None):   
        await ctx.guild.kick(user, reason=kick_reason)
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id)
        embed = discord.Embed(title=lang["administration_kick_msg"].format(user,kick_reason), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name='ban', help=main.lang["command_ban_help"], description=main.lang["command_ban_description"], usage="@somebody Harassment")
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, user: discord.Member, *, reason: str = None):
        await ctx.guild.ban(user, reason=reason)
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id)
        embed = discord.Embed(title=lang["administration_ban_msg"].format(str(user), reason), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name='unban', help=main.lang["command_unban_help"], description=main.lang["command_unban_description"], usage="User#1234 OR 116267141744820233")
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(self, ctx, user: BannedUser):
        await ctx.guild.unban(user)
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id)
        embed = discord.Embed(title=lang["administration_unban_msg"].format(str(user)), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name='softban', help=main.lang["command_softban_help"], description=main.lang["command_softban_description"], usage="@somebody Harassment")
    @commands.has_permissions(kick_members=True, manage_messages=True)
    @commands.guild_only()
    async def softban(self, ctx, user: discord.Member, *, reason: str = None):
        await ctx.guild.ban(user, reason=reason)
        await ctx.guild.unban(user, reason=reason)
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id)
        embed = discord.Embed(title=lang["administration_softban_msg"].format(str(user), reason), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name='mute', help=main.lang["empty_string"], description=main.lang["command_mute_description"], usage='@somebody')
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def mute(self, ctx, user: discord.Member):
        async with ctx.channel.typing():
            role = await Administration.get_mute_role(ctx.guild)
        user_rlist = [x.id for x in user.roles]
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id)
        if role.id not in user_rlist:
            await user.add_roles(role)
            embed = discord.Embed(title=lang["administration_mute_success"].format(str(user)), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_mute_muted"].format(str(user)), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(name='unmute', help=main.lang["empty_string"], description=main.lang["command_unmute_description"], usage='@somebody')
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def unmute(self, ctx, user: discord.Member):
        async with ctx.channel.typing():
            role = await Administration.get_mute_role(ctx.guild)
        user_rlist = [x.id for x in user.roles]
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id)
        if role.id in user_rlist:
            await user.remove_roles(role)
            embed = discord.Embed(title=lang["administration_unmute_success"].format(str(user)), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_unmute_unmuted"].format(str(user)), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=5)


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
                    lang = main.get_lang(ctx.guild.id)
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
        lang = main.get_lang(ctx.guild.id)
        embed = discord.Embed(title=lang["administration_setchannel_msg"].format(str(channel)), color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_permissions(administrator=True)
    @report_group.command(name='disable', help=main.lang["command_report_disable_help"], description=main.lang["command_report_disable_description"])
    async def report_disable(self, ctx):
        channel_id = await self.Reports.get_channel(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id)
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
            lang = main.get_lang(ctx.guild.id)
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
                            role = await Administration.get_mute_role(ctx.guild)
                        role_find = discord.utils.get(user.roles, id=role.id)
                        if not role_find:
                           await user.add_roles(role)
            else:
                embed = discord.Embed(title=lang["administration_warn_max"].format(self.max_warnings), color=self.module_embed_color)
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
                lang = main.get_lang(ctx.guild.id)
                if len(warnings[(page_index*5):(page_index*5 + 5)]) > 0:
                    embed = discord.Embed(title=lang["administration_warnings_title"].format(str(user)), color=self.module_embed_color)
                    embed.set_footer(text=f'{lang["page_string"]} {page}')
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
        lang = main.get_lang(ctx.guild.id)
        embed = discord.Embed(title=lang["administration_warnings_reset"].format(str(user)), color=self.module_embed_color)
        await ctx.send(embed=embed)

    @warnings_group.command(name='delete', help=main.lang["command_warnings_delete_help"], description=main.lang["command_warnings_delete_description"], usage='@someone 3', aliases=['remove'])
    async def warnings_delete(self, ctx, user: discord.User, number: int):
        if number >= 1:
            index = number - 1
            lang = main.get_lang(ctx.guild.id)
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
                lang = main.get_lang(ctx.guild.id)
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
            lang = main.get_lang(ctx.guild.id)
            embed = discord.Embed(title=lang["administration_autoaction_disable_msg"].format(action.lower()), color=self.module_embed_color)
            await ctx.send(embed=embed)

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
        lang = main.get_lang(ctx.guild.id)
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
        lang = main.get_lang(ctx.guild.id)
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
        lang = main.get_lang(ctx.guild.id)
        embed = discord.Embed(title=lang["administration_gdm_msg"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @server_greetings.group(name='message', invoke_without_command=True, help=main.lang["command_greetings_message_help"], description=main.lang["command_greetings_message_description"], usage="Welcome {mention} to {server}!")
    async def greetings_custom_message(self, ctx, *, message: str):
        lang = main.get_lang(ctx.guild.id)
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
        lang = main.get_lang(ctx.guild.id)
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
        lang = main.get_lang(ctx.guild.id)
        embed = discord.Embed(title=lang["administration_gsetchannel"].format(channel.name), color=self.module_embed_color)
        await ctx.send(embed=embed)

    @greetings_setchannel.command(name='default', help=main.lang["command_greetings_scdefault_help"], description=main.lang["command_greetings_scdefault_description"])
    async def greetings_setchannel_reset(self, ctx):
        await self.Toggles.set_channel(ctx.guild.id, None)
        lang = main.get_lang(ctx.guild.id)
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
                    channel = discord.utils.find(lambda c: c.position == 0, member.guild.text_channels)
            if await self.Toggles.has_custom_greeting(member.guild.id):
                message = await self.Toggles.get_custom_greeting(member.guild.id)
                message = await Administration.format_message(message, member)
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
        lang = main.get_lang(ctx.guild.id)
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
        lang = main.get_lang(ctx.guild.id)
        if status:
            await self.Toggles.disable_goodbye(ctx.guild.id)
            embed = discord.Embed(title=lang["administration_gbdisable_success"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["administration_gbdisable_disabled"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @server_goodbye.group(name='message', invoke_without_command=True, help=main.lang["command_goodbye_message_help"], description=main.lang["command_goodbye_message_description"], usage="Goodbye, {mention}!")
    async def goodbye_custom_message(self, ctx, *, message: str):
        lang = main.get_lang(ctx.guild.id)
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
        lang = main.get_lang(ctx.guild.id)
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
    async def on_member_remove(self, member):
        status = await self.Toggles.get_bye_status(member.guild.id)
        if status:
            channel_id = await self.Toggles.get_channel(member.guild.id)
            if channel_id:
                channel = await self.bot.fetch_channel(channel_id)
            else:
                channel = discord.utils.find(lambda c: c.name == "general", member.guild.text_channels)
                if not channel:
                    channel = discord.utils.find(lambda c: c.position == 0, member.guild.text_channels)
            if await self.Toggles.has_custom_goodbye(member.guild.id):
                message = await self.Toggles.get_custom_goodbye(member.guild.id)
                message = await Administration.format_message(message, member)
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
            await Administration.update_mute_role(role, guild)
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
    bot.add_cog(Administration(bot))