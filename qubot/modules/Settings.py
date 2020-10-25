from discord.ext import commands
from main import bot_path
from main import modules as loaded_modules
from libs.qulib import ExtendedCommand, ExtendedGroup
import libs.commandscontroller as ccontroller
import libs.prefixhandler as prefixhandler
import libs.localizations as localizations
import libs.utils.servertoggles as servertoggles
from libs.utils.admintools import ModlogSetup
from babel import Locale
import libs.qulib as qulib
import asyncio
import discord
import main
import os

class Settings(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.embed_color =  0x91becc

        self.Localization = localizations.Localizations()
        self.PrefixHandler = prefixhandler.PrefixHandler()
        self.CommandController = ccontroller.CommandController()
        self.CogController = ccontroller.CogController()
        self.Toggles = servertoggles.ServerToggles()
        self.Modlog = ModlogSetup()

        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = True
        self.module_dependencies = []

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)

        print(f'Module {self.__class__.__name__} loaded')

    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.group(name='settings', invoke_without_command=True, description=main.lang["command_settings_description"])
    @commands.guild_only()
    async def settings_command(self, ctx):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            #Localization
            lang_code = self.Localization.get_language(ctx.guild.id, main.languagecode).replace('-', "_")
            l = Locale.parse(lang_code)

            embed = discord.Embed(description=lang["settings_info_description"].format(ctx.guild.name), color = self.embed_color)
            embed.set_author(name=lang["settings_info_header"].format(ctx.guild.name), icon_url=str(ctx.guild.icon_url))
            embed.add_field(name=f'**{lang["prefix_string"]}**', value=f"{self.PrefixHandler.get_prefix(ctx.guild.id, main.prefix)}", inline=True)
            embed.add_field(name=f'**{lang["language_string"]}**', value=f"{l.get_language_name(lang_code)}", inline=True)
            embed.add_field(name=f'**{lang["guild_status_string"]}**', value=lang["guild_status_standard"], inline=True)

            if 'Automation' in self.bot.cogs.keys() and not self.CogController.is_disabled('Automation', ctx.guild.id):
                #Automation Settings
                greetings_channel_id = await self.Toggles.get_greetings_channel(ctx.guild.id)
                greetings_channel = (await self.bot.fetch_channel(greetings_channel_id)).mention if greetings_channel_id else lang["settings_greetings_default"]
                goodbye_channel_id = await self.Toggles.get_bye_channel(ctx.guild.id)
                goodbye_channel = (await self.bot.fetch_channel(goodbye_channel_id)).mention if goodbye_channel_id else lang["settings_goodbye_default"]

                embed.add_field(name=f'**{lang["greetings_channel_string"]}**', value=(greetings_channel or lang["empty_string"]), inline=True)
                embed.add_field(name=f'**{lang["goodbye_channel_string"]}**', value=(goodbye_channel or lang["empty_string"]), inline=True)
            
            if 'Moderation' in self.bot.cogs.keys() and not self.CogController.is_disabled('Moderation', ctx.guild.id):
                #Moderation Settings
                modlog_channel_id = await self.Modlog.get_channel(ctx.guild.id)
                modlog_channel = (await self.bot.fetch_channel(modlog_channel_id)).mention if modlog_channel_id else lang["settings_modlog_default"]
                embed.add_field(name=f'**{lang["modlog_channel_string"]}**', value=(modlog_channel or lang["empty_string"]), inline=True)
            
            disabled_cogs = await self.CogController.disabled_cogs(ctx.guild.id)
            embed.add_field(name=f'**{lang["disabled_modules_string"]}**', value=f"```{', '.join(disabled_cogs) if disabled_cogs else lang['settings_disabled_modules_default']}```", inline=False)
            disabled_commands = await self.CommandController.disabled_commands(ctx.guild.id)
            embed.add_field(name=f'**{lang["disabled_modules_string"]}**', value=f"```{', '.join(disabled_commands) if disabled_commands else lang['settings_disabled_cmds_default']}```", inline=False)
            embed.add_field(name=f'**{lang["other_settings_string"]}**', value=lang["settings_info_other_settings"], inline=False)
            await ctx.send(embed=embed)

    @commands.cooldown(5, 60, commands.BucketType.user)
    @settings_command.command(cls=ExtendedGroup, name='reset', description=main.lang["command_settings_reset_description"], permissions=['Administrator'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def settings_reset(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["settings_reset_confirmation_title"], description=lang["settings_reset_confirmation_description"], color = self.embed_color)
        embed.set_footer(text=lang["settings_reset_confirmation_footer"])
        await ctx.send(embed = embed)
        try:
            msg = await self.bot.wait_for('message', check=lambda m: (m.content.lower() in ['yes', 'y', 'no', 'n']) and m.channel == ctx.channel, timeout=60.0)
            if msg.content.lower() == 'yes' or msg.content.lower() == 'y':
                self.PrefixHandler.remove_guild(ctx.guild.id) # PrefixHandler takes care of language data removal as well since its tied to the same table
                await self.CommandController.remove_disabled_commands(ctx.guild.id)
                await self.CogController.remove_disabled_cogs(ctx.guild.id)
                await self.Toggles.wipe_guild_data(ctx.guild.id)
                await self.Modlog.wipe_data(ctx.guild.id)
                await ctx.send(embed = discord.Embed(title=lang["settings_reset_success_title"], description=lang["settings_reset_success_description"], color = self.embed_color))
            else:
                await ctx.send(lang["wait_for_cancelled"], delete_after=15)
        except asyncio.TimeoutError:
            await ctx.send(lang["wait_for_timeout"], delete_after=15)

    @commands.command(name="languages", description=main.lang["command_langs_description"], aliases=['langs', 'langlist'], ignore_extra=True)
    async def lang_list(self, ctx):
        lang_directory_list = [os.path.splitext(i)[0] for i in os.listdir(os.path.join(bot_path, 'data', 'localization')) if ("language" in os.path.splitext(i)[0] and os.path.splitext(i)[1] == ".json")]
        lang_list = [x.replace('language_', '') for x in lang_directory_list]
        lang_string = ''
        for lang_item in lang_list:
            lang_code = lang_item.replace('-', "_")
            l = Locale.parse(lang_code)
            lang_string += f'\u2022 `{lang_item}` - {l.get_display_name(lang_code)}\n'
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["settings_langs_title"], description=lang_string, color=self.embed_color)
        if ctx.guild:
            embed.set_footer(text=f'{lang["settings_langs_footer"]}: {self.Localization.get_language(ctx.guild.id, main.languagecode)}')
        await ctx.send(embed=embed)

    @commands.cooldown(5, 60, commands.BucketType.user)
    @commands.command(cls=ExtendedCommand, name="langset", description=main.lang["command_langset_description"], usage="<language code>", permissions=['Administrator'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def lang_set(self, ctx, lang_code: str = None):
        lang_directory_list = [os.path.splitext(i)[0] for i in os.listdir(os.path.join(bot_path, 'data', 'localization')) if ("language" in os.path.splitext(i)[0] and os.path.splitext(i)[1] == ".json")]
        lang_list = [x.replace('language_', '') for x in lang_directory_list]
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if lang_code in lang_list:
            if lang_code != self.Localization.get_language(ctx.guild.id, main.languagecode):
                self.Localization.set_language(ctx.guild.id, lang_code)
                await ctx.send(embed = discord.Embed(title=lang["settings_langset_success"].format(lang_code), color=self.embed_color))
            else:
                await ctx.send(lang["settings_langset_same"], delete_after=15)
        else:
            await ctx.send(lang["settings_langset_notfound"], delete_after=15)

    @commands.group(cls=ExtendedGroup, name='prefix', invoke_without_command=True, help=main.lang["command_prefix_help"], description=main.lang["command_prefix_description"], usage="<prefix>", permissions=['Administrator'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def prefix(self, ctx, *, new_prefix: str = None):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if not new_prefix:
                await ctx.invoke(self.prefix_show)
            elif len(new_prefix) > main.max_prefix_length:
                await ctx.send(lang["settings_prefix_length_limit"].format(main.max_prefix_length), delete_after=15)
            else:
                self.PrefixHandler.set_prefix(ctx.guild.id, new_prefix)
                await ctx.send(embed = discord.Embed(title=lang["settings_prefix_success"].format(new_prefix), color=self.embed_color))

    @prefix.command(cls=ExtendedCommand, name='reset', description=main.lang["command_prefix_reset_description"], ignore_extra=True, permissions=['Administrator'])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def prefix_reset(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        self.PrefixHandler.set_prefix(ctx.guild.id, main.prefix)
        await ctx.send(embed=discord.Embed(title=lang["settings_prefix_reset"].format(main.prefix), color=self.embed_color))

    @prefix.command(cls=ExtendedCommand, name='show', description=main.lang["command_prefix_show_description"], ignore_extra=True, permissions=['Administrator'])
    @commands.guild_only()
    async def prefix_show(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed=discord.Embed(title=lang["settings_prefix_info"].format(self.PrefixHandler.get_prefix(ctx.guild.id, main.prefix)), color=self.embed_color))

def setup(bot):
    bot.add_cog(Settings(bot))