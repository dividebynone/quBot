from main import config, bot_starttime, bot_path
from discord.ext import tasks, commands
from libs.qulib import ExtendedCommand, ExtendedGroup
import libs.utils.servertoggles as servertoggles
import libs.qulib as qulib
import discord
import main
import os

# Cog (Automation) - Collection of commands and assets used to automate actions
class Automation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.embed_color = 0x347aeb

        self.max_characters = 1500

        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = False
        self.module_dependencies = []

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)
     
        self.Toggles = servertoggles.ServerToggles()

        print(f'Module {self.__class__.__name__} loaded')

    @staticmethod
    async def format_message(message: str, member: discord.Member):
        message = message.replace("{mention}", member.mention)
        message = message.replace("{user}", str(member))
        message = message.replace("{server}", member.guild.name)
        message = message.replace("{membercount}", str(member.guild.member_count))
        return message

    #TODO: Add proper comments

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_guild_remove(self, guild):
        pass
        # TODO: Clear toggle data here
        # await BlacklistedUsers.remove_blacklist_guild(guild.id)
        # await TemporaryActions.wipe_guild_data(guild.id)

    # TEMP: Server Member greetings

    @commands.cooldown(5, 30, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.group(cls=ExtendedGroup, name='greet', description=main.lang["command_greetings_description"], aliases=['greetings'], permissions=['Manage Server'])
    async def server_greetings(self, ctx):
        if not ctx.invoked_subcommand:
            status = await self.Toggles.get_greet_status(ctx.guild.id)
            if status:
                await ctx.invoke(self.greetings_disable)
            else:
                await ctx.invoke(self.greetings_enable)

    @commands.cooldown(5, 30, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @server_greetings.command(cls=ExtendedCommand, name='enable', description=main.lang["command_greetings_enable_description"], ignore_extra=True, aliases=['e', 'on'], permissions=['Manage Server'])
    async def greetings_enable(self, ctx):
        status = await self.Toggles.get_greet_status(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if status != 1:
            await self.Toggles.enable_greeting(ctx.guild.id, False)
            embed = discord.Embed(title=lang["administration_genable_success"], color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["administration_genable_enabled"], color=self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(5, 30, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @server_greetings.command(cls=ExtendedCommand, name='disable', description=main.lang["command_greetings_disable_description"], ignore_extra=True, aliases=['d', 'off'], permissions=['Manage Server'])
    async def greetings_disable(self, ctx):
        status = await self.Toggles.get_greet_status(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if status:
            await self.Toggles.disable_greeting(ctx.guild.id)
            embed = discord.Embed(title=lang["administration_gdisable_success"], color=self.embed_color)   
        else:
            embed = discord.Embed(title=lang["administration_gdisable_disabled"], color=self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(5, 30, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @server_greetings.command(cls=ExtendedCommand, name='dm', description=main.lang["command_greetings_dm_description"], ignore_extra=True, permissions=['Manage Server'])
    async def greetings_enable_dm(self, ctx):
        await self.Toggles.enable_greeting(ctx.guild.id, True)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["administration_gdm_msg"], color=self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(5, 30, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @server_greetings.command(cls=ExtendedCommand, name='test', description=main.lang["command_greetings_test_description"], ignore_extra=True, permissions=['Manage Server'])
    async def greetings_test(self, ctx):
        await self.on_member_join(ctx.message.author)

    @commands.cooldown(5, 30, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @server_greetings.group(cls=ExtendedGroup, name='message', invoke_without_command=True, help=main.lang["command_greetings_message_help"], description=main.lang["command_greetings_message_description"], usage="Welcome {mention} to {server}!", permissions=['Manage Server'])
    async def greetings_custom_message(self, ctx, *, message: str):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if len(message) <= self.max_characters:
            if await self.Toggles.get_greet_status(ctx.guild.id):
                try:
                    message = message.lstrip()
                    message = message.replace("\\n", "\n")
                    await self.Toggles.set_greet_msg(ctx.guild.id, message)
                    embed = discord.Embed(title=lang["administration_gmessage_success"], color=self.embed_color)
                except ValueError:
                    embed = discord.Embed(title=lang["administration_gmessage_invalid"], color=self.embed_color) 
            else:
                embed = discord.Embed(title=lang["administration_gmessage_disabled"], color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["administration_gmessage_limit"].format(self.max_characters), color=self.embed_color)
        await ctx.send(embed=embed)

    @greetings_custom_message.command(cls=ExtendedCommand, name='default', description=main.lang["command_greetings_mdefault_description"], permissions=['Manage Server'])
    async def greetings_custom_message_reset(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.Toggles.has_custom_greeting(ctx.guild.id):
            await self.Toggles.reset_greet_msg(ctx.guild.id)
            embed = discord.Embed(title=lang["administration_gmessage_default_success"], color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["administration_gmessage_default_used"], color=self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @server_greetings.group(cls=ExtendedCommand, name='setchannel', invoke_without_command=True, help=main.lang["command_greetings_setchannel_help"], description=main.lang["command_greetings_setchannel_description"], usage="#general", permissions=['Manage Server'])
    async def greetings_setchannel(self, ctx, *, channel: discord.TextChannel):
        await self.Toggles.set_channel(ctx.guild.id, channel.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["administration_gsetchannel"].format(channel.name), color=self.embed_color)
        await ctx.send(embed=embed)

    @greetings_setchannel.command(cls=ExtendedCommand, name='default', description=main.lang["command_greetings_scdefault_description"], permissions=['Manage Server'])
    async def greetings_setchannel_reset(self, ctx):
        await self.Toggles.set_channel(ctx.guild.id, None)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["administration_gscdefault_msg"], color=self.embed_color)
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
                    message = await Automation.format_message(message, member)
                else:
                    lang = main.get_lang(member.guild.id)
                    message = lang["administration_greet_default"].format(member.mention, member.guild.name)

                if status == 2:
                    await member.send(message)
                else:
                    await channel.send(message)

    # TEMP: Server Member goodbyes

    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.group(cls=ExtendedGroup, name='bye', description=main.lang["command_goodbye_description"], aliases=['goodbye'], permissions=['Manage Server'])
    async def server_goodbye(self, ctx):
        if not ctx.invoked_subcommand:
            status = await self.Toggles.get_bye_status(ctx.guild.id)
            if status:
                await ctx.invoke(self.goodbye_disable)
            else:
                await ctx.invoke(self.goodbye_enable)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @server_goodbye.command(cls=ExtendedCommand, name='enable', description=main.lang["command_goodbye_enable_description"], ignore_extra=True, aliases=['e', 'on'], permissions=['Manage Server'])
    async def goodbye_enable(self, ctx):
        status = await self.Toggles.get_bye_status(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if status != 1:
            await self.Toggles.enable_goodbye(ctx.guild.id)
            embed = discord.Embed(title=lang["administration_gbenable_success"], color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["administration_gbenable_enabled"], color=self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @server_goodbye.command(cls=ExtendedCommand, name='disable', description=main.lang["command_goodbye_disable_description"], ignore_extra=True, aliases=['d', 'off'], permissions=['Manage Server'])
    async def goodbye_disable(self, ctx):
        status = await self.Toggles.get_bye_status(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if status:
            await self.Toggles.disable_goodbye(ctx.guild.id)
            embed = discord.Embed(title=lang["administration_gbdisable_success"], color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["administration_gbdisable_disabled"], color=self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @server_goodbye.command(cls=ExtendedCommand, name='test', description=main.lang["command_goodbye_test_description"], ignore_extra=True, permissions=['Manage Server'])
    @commands.has_permissions(manage_guild=True)
    async def goodbye_test(self, ctx):
        await self.on_member_remove(ctx.message.author)

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @server_goodbye.group(cls=ExtendedGroup, name='message', invoke_without_command=True, help=main.lang["command_goodbye_message_help"], description=main.lang["command_goodbye_message_description"], usage="Goodbye, {mention}!", permissions=['Manage Server'])
    async def goodbye_custom_message(self, ctx, *, message: str):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if len(message) <= self.max_characters:
            if await self.Toggles.get_bye_status(ctx.guild.id):
                try:
                    message = message.lstrip()
                    message = message.replace("\\n", "\n")
                    await self.Toggles.set_bye_msg(ctx.guild.id, message)
                    embed = discord.Embed(title=lang["administration_gbmessage_success"], color=self.embed_color)
                except ValueError:
                    embed = discord.Embed(title=lang["administration_gbmessage_invalid"], color=self.embed_color)
            else:
                embed = discord.Embed(title=lang["administration_gbmessage_disabled"], color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["administration_gmessage_limit"].format(self.max_characters), color=self.embed_color)
        await ctx.send(embed=embed)

    @goodbye_custom_message.command(cls=ExtendedCommand, name='default', description=main.lang["command_goodbye_mdefault_description"], permissions=['Manage Server'])
    async def goodbye_custom_message_reset(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.Toggles.has_custom_goodbye(ctx.guild.id):
            await self.Toggles.reset_bye_msg(ctx.guild.id)
            embed = discord.Embed(title=lang["administration_gbmessage_default_success"], color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["administration_gbmessage_default_used"], color=self.embed_color)
        await ctx.send(embed=embed)

    #TODO: Add a seperate channel controller for goodbye messages

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @server_goodbye.group(cls=ExtendedCommand, name='setchannel', invoke_without_command=True, help=main.lang["command_greetings_setchannel_help"], description=main.lang["command_greetings_setchannel_description"], usage="#general", permissions=['Manage Server'])
    async def goodbye_setchannel(self, ctx, *, channel: discord.TextChannel):
        await ctx.invoke(self.greetings_setchannel, channel=channel)

    @goodbye_setchannel.command(cls=ExtendedCommand, name='default', description=main.lang["command_greetings_scdefault_description"], permissions=['Manage Server'])
    async def goodbye_setchannel_reset(self, ctx):
        await ctx.invoke(self.greetings_setchannel_reset)

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
                    message = await Automation.format_message(message, member)
                else:
                    lang = main.get_lang(member.guild.id)
                    message = lang["administration_bye_default"].format(str(member), member.guild.name)
                await channel.send(message)

def setup(bot):
    bot.add_cog(Automation(bot))