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

    # Method to format greeting/farewell strings to include specific data
    @staticmethod
    async def format_message(message: str, member: discord.Member):
        message = message.replace("{mention}", member.mention)
        message = message.replace("{user}", str(member))
        message = message.replace("{server}", member.guild.name)
        message = message.replace("{membercount}", str(member.guild.member_count))
        return message

    # Event that handles the removal of unwanted data.
    # Note(s): The event will trigger when the bot is kicked from a guild
    @commands.Cog.listener()
    @commands.guild_only()
    async def on_guild_remove(self, guild):
        await self.Toggles.wipe_guild_data(guild.id)

    #----------------------------------#
    # Server Member Greeting Messages
    #----------------------------------#

    @commands.group(cls=ExtendedGroup, name='greet', description=main.lang["command_greetings_description"], aliases=['greetings', 'welcome'], permissions=['Manage Server'])
    @commands.cooldown(10, 30, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def server_greetings(self, ctx):
        if not ctx.invoked_subcommand:
            status = await self.Toggles.get_greet_status(ctx.guild.id)
            if status:
                await ctx.invoke(self.greetings_disable)
            else:
                await ctx.invoke(self.greetings_enable)

    @server_greetings.command(cls=ExtendedCommand, name='enable', description=main.lang["command_greetings_enable_description"], ignore_extra=True, aliases=['e', 'on'], permissions=['Manage Server'])
    async def greetings_enable(self, ctx):
        status = await self.Toggles.get_greet_status(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if status != 1:
            await self.Toggles.enable_greeting(ctx.guild.id, False)
            await ctx.send(embed = discord.Embed(title=lang["automation_genable_embed_title"], description=lang["automation_genable_embed_description"], color=self.embed_color))
        else:
            await ctx.send(lang["automation_genable_already_enabled"], delete_after=10)
        
    @server_greetings.command(cls=ExtendedCommand, name='disable', description=main.lang["command_greetings_disable_description"], ignore_extra=True, aliases=['d', 'off'], permissions=['Manage Server'])
    async def greetings_disable(self, ctx):
        status = await self.Toggles.get_greet_status(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if status:
            await self.Toggles.disable_greeting(ctx.guild.id)
            await ctx.send(embed = discord.Embed(title=lang["automation_gdisable_embed_title"], description=lang["automation_gdisable_embed_description"], color=self.embed_color))
        else:
            await ctx.send(lang["automation_gdisable_already_disabled"], delete_after=10)

    @server_greetings.command(cls=ExtendedCommand, name='dm', description=main.lang["command_greetings_dm_description"], ignore_extra=True, permissions=['Manage Server'])
    async def greetings_enable_dm(self, ctx):
        status = await self.Toggles.get_greet_status(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if status != 2:
            await self.Toggles.enable_greeting(ctx.guild.id, True)
            await ctx.send(embed = discord.Embed(title=lang["automation_gdm_embed_title"], description=lang["automation_gdm_embed_description"], color=self.embed_color))
        else:
            await ctx.send(lang["automation_genable_already_enabled"], delete_after=10)

    @server_greetings.command(cls=ExtendedCommand, name='test', description=main.lang["command_greetings_test_description"], ignore_extra=True, permissions=['Manage Server'])
    async def greetings_test(self, ctx):
        await self.on_member_join(ctx.message.author)

    @server_greetings.group(cls=ExtendedGroup, name='message', invoke_without_command=True, help=main.lang["command_greetings_message_help"], description=main.lang["command_greetings_message_description"], usage="Welcome {mention} to {server}!", permissions=['Manage Server'])
    async def greetings_custom_message(self, ctx, *, message: str):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if len(message) <= self.max_characters:
            if await self.Toggles.get_greet_status(ctx.guild.id):
                try:
                    message = message.lstrip().replace("\\n", "\n")
                    await self.Toggles.set_greet_msg(ctx.guild.id, message)
                    await ctx.send(embed = discord.Embed(title=lang["automation_gmessage_success"], color=self.embed_color))
                except ValueError:
                    await ctx.send(lang["automation_gmessage_invalid"], delete_after=10)
            else:
                await ctx.send(lang["automation_gmessage_disabled"], delete_after=10)
        else:
            await ctx.send(lang["automation_gmessage_limit"].format(self.max_characters), delete_after=10)
    
    @greetings_custom_message.command(cls=ExtendedCommand, name='default', description=main.lang["command_greetings_mdefault_description"], permissions=['Manage Server'])
    async def greetings_custom_message_reset(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.Toggles.has_custom_greeting(ctx.guild.id):
            await self.Toggles.reset_greet_msg(ctx.guild.id)
            await ctx.send(embed = discord.Embed(title=lang["automation_gmessage_default_success"], color=self.embed_color))
        else:
            await ctx.send(lang["automation_gmessage_default_already_used"], delete_after=10)

    @server_greetings.group(cls=ExtendedGroup, name='setchannel', invoke_without_command=True, help=main.lang["command_greetings_setchannel_help"], description=main.lang["command_greetings_setchannel_description"], usage="#general", permissions=['Manage Server'])
    async def greetings_setchannel(self, ctx, *, channel: discord.TextChannel):
        await self.Toggles.set_greetings_channel(ctx.guild.id, channel.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(title=lang["automation_gsetchannel"].format(channel.name), color=self.embed_color))

    @greetings_setchannel.command(cls=ExtendedCommand, name='default', description=main.lang["command_greetings_scdefault_description"], permissions=['Manage Server'])
    async def greetings_setchannel_reset(self, ctx):
        await self.Toggles.set_greetings_channel(ctx.guild.id, None)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(title=lang["automation_gscdefault"], color=self.embed_color))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        status = await self.Toggles.get_greet_status(member.guild.id)
        if status:
            channel_id = await self.Toggles.get_greetings_channel(member.guild.id)
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
                    lang = main.get_lang(member.guild.id) or main.lang
                    message = lang["automation_greet_default"].format(member.mention, member.guild.name)

                if status == 2:
                    await member.send(message)
                else:
                    await channel.send(message)

    #----------------------------------#
    # Server Member Farewell Messages
    #----------------------------------#

    @commands.group(cls=ExtendedGroup, name='bye', description=main.lang["command_goodbye_description"], aliases=['goodbye', 'farewell'], permissions=['Manage Server'])
    @commands.cooldown(10, 30, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    async def server_goodbye(self, ctx):
        if not ctx.invoked_subcommand:
            status = await self.Toggles.get_bye_status(ctx.guild.id)
            if status:
                await ctx.invoke(self.goodbye_disable)
            else:
                await ctx.invoke(self.goodbye_enable)

    @server_goodbye.command(cls=ExtendedCommand, name='enable', description=main.lang["command_goodbye_enable_description"], ignore_extra=True, aliases=['e', 'on'], permissions=['Manage Server'])
    async def goodbye_enable(self, ctx):
        status = await self.Toggles.get_bye_status(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if status != 1:
            await self.Toggles.enable_goodbye(ctx.guild.id)
            await ctx.send(embed = discord.Embed(title=lang["automation_gbenable_embed_title"], description=lang["automation_gbenable_embed_description"], color=self.embed_color))
        else:
            await ctx.send(lang["automation_gbenable_already_enabled"], delete_after=10)

    @server_goodbye.command(cls=ExtendedCommand, name='disable', description=main.lang["command_goodbye_disable_description"], ignore_extra=True, aliases=['d', 'off'], permissions=['Manage Server'])
    async def goodbye_disable(self, ctx):
        status = await self.Toggles.get_bye_status(ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if status:
            await self.Toggles.disable_goodbye(ctx.guild.id)
            await ctx.send(embed = discord.Embed(title=lang["automation_gbdisable_embed_title"], description=lang["automation_gbdisable_embed_description"], color=self.embed_color))
        else:
            await ctx.send(lang["automation_gbdisable_already_disabled"], delete_after=10)

    @server_goodbye.command(cls=ExtendedCommand, name='test', description=main.lang["command_goodbye_test_description"], ignore_extra=True, permissions=['Manage Server'])
    async def goodbye_test(self, ctx):
        await self.on_member_remove(ctx.message.author)

    @server_goodbye.group(cls=ExtendedGroup, name='message', invoke_without_command=True, help=main.lang["command_goodbye_message_help"], description=main.lang["command_goodbye_message_description"], usage="Goodbye, {mention}!", permissions=['Manage Server'])
    async def goodbye_custom_message(self, ctx, *, message: str):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if len(message) <= self.max_characters:
            if await self.Toggles.get_bye_status(ctx.guild.id):
                try:
                    message = message.lstrip().replace("\\n", "\n")
                    await self.Toggles.set_bye_msg(ctx.guild.id, message)
                    await ctx.send(embed = discord.Embed(title=lang["automation_gbmessage_success"], color=self.embed_color))
                except ValueError:
                    await ctx.send(lang["automation_gbmessage_invalid"], delete_after=10)
            else:
                await ctx.send(lang["automation_gbmessage_disabled"], delete_after=10)
        else:
            await ctx.send(lang["automation_gmessage_limit"].format(self.max_characters), delete_after=10)

    @goodbye_custom_message.command(cls=ExtendedCommand, name='default', description=main.lang["command_goodbye_mdefault_description"], permissions=['Manage Server'])
    async def goodbye_custom_message_reset(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.Toggles.has_custom_goodbye(ctx.guild.id):
            await self.Toggles.reset_bye_msg(ctx.guild.id)
            await ctx.send(embed = discord.Embed(title=lang["automation_gbmessage_default_success"], color=self.embed_color))
        else:
            await ctx.send(lang["automation_gbmessage_default_already_used"], delete_after=10)

    @server_goodbye.group(cls=ExtendedGroup, name='setchannel', invoke_without_command=True, help=main.lang["command_greetings_setchannel_help"], description=main.lang["command_goodbye_setchannel_description"], usage="#general", permissions=['Manage Server'])
    async def goodbye_setchannel(self, ctx, *, channel: discord.TextChannel):
        await self.Toggles.set_bye_channel(ctx.guild.id, channel.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(title=lang["automation_gbsetchannel"].format(channel.name), color=self.embed_color))

    @goodbye_setchannel.command(cls=ExtendedCommand, name='default', description=main.lang["command_goodbye_scdefault_description"], permissions=['Manage Server'])
    async def goodbye_setchannel_reset(self, ctx):
        await self.Toggles.set_bye_channel(ctx.guild.id, None)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(title=lang["automation_gbscdefault"], color=self.embed_color))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        status = await self.Toggles.get_bye_status(member.guild.id)
        if member and member.id != self.bot.user.id and status:
            channel_id = await self.Toggles.get_bye_channel(member.guild.id)
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
                    lang = main.get_lang(member.guild.id) or main.lang
                    message = lang["automation_bye_default"].format(str(member), member.guild.name)
                await channel.send(message)

def setup(bot):
    bot.add_cog(Automation(bot))