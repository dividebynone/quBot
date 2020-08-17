from discord.ext import commands
from main import bot_starttime, config, bot_path
from main import modules as loaded_modules
from main import logger
import libs.qulib as qulib
from libs.utils.admintools import BlacklistedUsers
from libs.prefixhandler import PrefixHandler
from libs.localizations import Localizations
from libs.commandscontroller import CommandController, CogController
from datetime import datetime
import discord
import json
import os
import sys
import psutil
import main

class Core(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0xf0f3f4
        print(f'Module {self.__class__.__name__} loaded')

        self.BlacklistedUsers = BlacklistedUsers()
        self.CommandController = CommandController()
        self.CogController = CogController()
        self.PrefixHandler = PrefixHandler()

        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = True
        self.module_dependencies = []

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)

    def bot_check(self, ctx):
        if ctx.guild:
            if not CogController.is_disabled(ctx.command.cog_name, ctx.guild.id):
                if not CommandController.is_disabled(ctx.command.qualified_name, ctx.guild.id):
                    if not BlacklistedUsers.is_blacklisted(ctx.author.id, ctx.guild.id):
                        return True
                    else:
                        raise commands.CheckFailure("Failed global check because user is blacklisted.")
                else:
                    raise commands.DisabledCommand("This command is disabled on the server.")
            else:
                raise commands.DisabledCommand("Failed attempt to use command from a disabled module.")
        else:
            return True

    @commands.command(name='load', help=main.lang["command_module_help"], description=main.lang["command_load_description"], usage="<module name>", hidden=True)
    @commands.is_owner()
    async def module_load(self, ctx, *, input_module: str):
        try:
            input_module_path = f'modules.{input_module}'
            if input_module_path not in loaded_modules:
                self.bot.load_extension(input_module_path)
        except Exception as e:
            embed = discord.Embed(title=f'**`ERROR:`** {type(e).__name__} - {e}', color=self.module_embed_color)
        else:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if input_module_path in loaded_modules:
                embed = discord.Embed(title=lang["core_module_load_fail"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_load_success"].format(input_module), color=self.module_embed_color)
                loaded_modules.append(input_module_path)
                with open(os.path.join(bot_path, 'data/modules.mdls'), 'a') as modules_file:
                        modules_file.write(f'{input_module}\n')             
        await ctx.send(embed=embed, delete_after=20)

    @commands.command(name='unload', help=main.lang["command_module_help"], description=main.lang["command_unload_description"], usage="<module name>", hidden=True)
    @commands.is_owner()
    async def module_unload(self, ctx, *, input_module: str):
        try:
            input_module_path = f'modules.{input_module}'
            if input_module_path in loaded_modules:
                 self.bot.unload_extension(input_module_path)
        except Exception as e:
            embed = discord.Embed(title=f'**`ERROR:`** {type(e).__name__} - {e}', color=self.module_embed_color)
        else:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if input_module_path not in loaded_modules:
                embed = discord.Embed(title=lang["core_module_unload_fail"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_unload_success"].format(input_module), color=self.module_embed_color)
                loaded_modules.remove(input_module_path)
                with open(os.path.join(bot_path, 'data/modules.mdls'), 'r+') as modules_file:
                    modules_output = modules_file.read()
                    modules_file.seek(0)
                    for i in modules_output.split():
                        if i != input_module:
                            modules_file.write(f'{i}\n')
                    modules_file.truncate()
                    modules_file.close()
        await ctx.send(embed=embed, delete_after=20)

    @commands.command(name='reload', help=main.lang["command_module_help"], description=main.lang["command_reload_description"], usage="<module name>", hidden=True)
    @commands.is_owner()
    async def module_reload(self, ctx, *, input_module: str):
        try:
            input_module_path = f'modules.{input_module}'
            if input_module_path in loaded_modules:
                self.bot.reload_extension(input_module_path)
        except Exception as e:
            embed = discord.Embed(title=f'**`ERROR:`** {type(e).__name__} - {e}', color=self.module_embed_color)
        else:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if input_module_path not in loaded_modules:
                embed = discord.Embed(title=lang["core_module_reload_fail"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_reload_success"].format(input_module), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=20)
    
    @commands.group(name='modules', invoke_without_command=True, help=main.lang["empty_string"], description=main.lang["command_modules_description"], aliases=['mdls'])
    async def modules(self, ctx):
        if not ctx.invoked_subcommand:
            modules_list = ''
            loaded_modules_names = [i.replace('modules.', '') for i in loaded_modules]
            modules_config = qulib.get_module_config()
            for i in loaded_modules_names:
                if i not in modules_config.setdefault("hidden_modules", []):
                    modules_list += f'\u2022 {i}\n'
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            embed = discord.Embed(title=lang["core_modules_list"],description=modules_list, color=self.module_embed_color)
            await ctx.author.send(embed=embed)

    @commands.cooldown(10, 60, commands.BucketType.guild)
    @modules.command(name='enable', help=main.lang["command_modules_change_help"], description=main.lang["command_modules_enable_description"], usage="<module name>", aliases=['e'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def modules_enable(self, ctx, *, input_module: str):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        modules_config = qulib.get_module_config()
        loaded_modules_names = [i.replace('modules.', '') for i in loaded_modules]
        loaded_modules_lowercase = [i.lower() for i in loaded_modules_names]
        if input_module.lower() in loaded_modules_lowercase:
            cog_name = loaded_modules_names[loaded_modules_lowercase.index(input_module.lower())]
            if CogController.is_disabled(cog_name, ctx.guild.id):
                if cog_name in modules_config.setdefault("dependencies", {}):
                    disabled_cogs = CogController.disabled_cogs(ctx.guild.id)
                    unloaded_dependencies = set(modules_config.setdefault("dependencies", {})[cog_name]).intersection(disabled_cogs)
                    if len(unloaded_dependencies) > 0:
                        embed = discord.Embed(title=lang["core_module_enable_dependencies"].format(', '.join(str(e) for e in unloaded_dependencies)), color=self.module_embed_color)
                        await ctx.send(embed=embed, delete_after=30)
                        return

                await CogController.enable_cog(cog_name, ctx.guild.id)
                embed = discord.Embed(title=lang["core_module_enable_msg"].format(cog_name), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_enable_already_enabled"].format(cog_name), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["core_module_enable_not_found"], color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=30)

    @commands.cooldown(10, 60, commands.BucketType.guild)
    @modules.command(name='disable', help=main.lang["command_modules_change_help"], description=main.lang["command_modules_disable_description"], usage="<module name>", aliases=['d'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def modules_disable(self, ctx, *, input_module: str):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        modules_config = qulib.get_module_config()
        loaded_modules_names = [i.replace('modules.', '') for i in loaded_modules]
        loaded_modules_lowercase = [i.lower() for i in loaded_modules_names]
        if input_module.lower() in loaded_modules_lowercase:
            cog_name = loaded_modules_names[loaded_modules_lowercase.index(input_module.lower())]
            if not CogController.is_disabled(cog_name, ctx.guild.id):
                if cog_name in modules_config.setdefault("dependencies", {}):
                    disabled_cogs = CogController.disabled_cogs(ctx.guild.id)
                    loaded_dependencies = set(loaded_modules_names).intersection(modules_config.setdefault("dependencies", {})[cog_name]) - (set(disabled_cogs) if disabled_cogs else set())
                    if len(loaded_dependencies) > 0:
                        embed = discord.Embed(title=lang["core_module_disable_dependencies"].format(', '.join(str(e) for e in loaded_dependencies)), color=self.module_embed_color)
                        await ctx.send(embed=embed, delete_after=30)
                        return

                if cog_name not in modules_config["restricted_modules"]:
                    await CogController.disable_cog(cog_name, ctx.guild.id)
                    embed = discord.Embed(title=lang["core_module_disable_msg"].format(cog_name), color=self.module_embed_color)
                else:
                    embed = discord.Embed(title=lang["core_module_disable_restricted"].format(cog_name), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_disable_already_disabled"].format(cog_name), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["core_module_disable_not_found"], color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=30)
        
    @modules.command(name='hide', help=main.lang["command_modules_hide_help"], description=main.lang["command_modules_hide_description"], usage="<module name>")
    @commands.is_owner()
    async def hide(self, ctx, *, input_module: str):
        input_module_path = f'modules.{input_module}'
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if input_module_path in loaded_modules:
            modules_config = qulib.get_module_config()
            if input_module not in modules_config.setdefault("hidden_modules", []):
                modules_config.setdefault("hidden_modules", []).append(input_module)
                qulib.update_module_config(modules_config)
                embed = discord.Embed(title=lang["core_module_hide_success"].format(input_module), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_hide_hidden"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["core_module_hide_fail"], color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @modules.command(name='unhide', help=main.lang["command_modules_unhide_help"], description=main.lang["command_modules_unhide_description"], usage="<module name>")
    @commands.is_owner()
    async def unhide(self, ctx, *, input_module: str):
        input_module_path = f'modules.{input_module}'
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if input_module_path in loaded_modules:
            modules_config = qulib.get_module_config()
            if input_module in modules_config.setdefault("hidden_modules", []):
                modules_config.setdefault("hidden_modules", []).remove(input_module)
                qulib.update_module_config(modules_config)
                embed = discord.Embed(title=lang["core_module_unhide_success"].format(input_module), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_unhide_visible"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["core_module_unhide_fail"], color=self.module_embed_color)
        await ctx.author.send(embed=embed)
    
    @commands.group(name='commands', invoke_without_command=True, help=main.lang["empty_string"], description=main.lang["command_cmds_description"], usage="<module name>", aliases=['cmds'])
    async def cmds_list(self, ctx, *, input_module: str = None):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if input_module:
                loaded_modules_names = [i.replace('modules.', '') for i in loaded_modules]
                input_module = input_module.capitalize()
                if input_module in loaded_modules_names:
                    display_list = ''
                    isowner = await ctx.bot.is_owner(ctx.author)

                    for command in self.bot.get_cog(input_module).walk_commands():
                        if not command.hidden or isowner:
                            if command.parent:
                                display_list += f'\u002d\u002d\u002d {" ".join(command.qualified_name.split()[1:])}\n'
                            else:
                                display_list += f'\u2022 {command.name}\n'
                    if not display_list:
                        embed = discord.Embed(title=lang["core_cmds_list_empty"].format(input_module), color=self.module_embed_color)
                    else:
                        embed = discord.Embed(title=lang["core_cmds_list"].format(input_module),description=display_list, color=self.module_embed_color)
                else:
                    embed = discord.Embed(title=lang["core_cmds_list_not_found"].format(input_module), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_cmds_list_marg"], color=self.module_embed_color)
            await ctx.author.send(embed=embed)

    @commands.cooldown(10, 30, commands.BucketType.guild)
    @cmds_list.command(name='enable', help=main.lang["command_command_help"], description=main.lang["command_command_enable_description"], usage='userid', aliases=['e'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def commands_enable(self, ctx, *, command:str):
        cmds_list = [x.name for x in self.bot.commands]
        aliases_list = [x.aliases for x in self.bot.commands if len(x.aliases) > 0]
        aliases_list = [item for sublist in aliases_list for item in sublist]
        if ctx.command.root_parent and str(ctx.command.root_parent).strip() in cmds_list: 
            cmds_list.remove(str(ctx.command.root_parent).strip())
            if len(ctx.command.root_parent.aliases) > 0:
                for alias in ctx.command.root_parent.aliases: aliases_list.remove(alias.strip())    

        if command.lower() in cmds_list or command.lower() in aliases_list:
            command_obj = self.bot.get_command(command)
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if CommandController.is_disabled(command_obj.name, ctx.guild.id):
                await CommandController.enable_command(command_obj.name, ctx.guild.id)
                embed = discord.Embed(title=lang["core_command_enable"].format(command_obj.name), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_command_already_enabled"].format(command_obj.name), color=self.module_embed_color)
            await ctx.send(embed=embed, delete_after=15)
        else:
            raise commands.errors.BadArgument("Could not enable/disable command. Command not found.")

    @commands.cooldown(10, 30, commands.BucketType.guild)
    @cmds_list.command(name='disable', help=main.lang["command_command_help"], description=main.lang["command_command_disable_description"], usage='userid', aliases=['d'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def commands_disable(self, ctx, *, command:str):
        cmds_list = [x.name for x in self.bot.commands]
        aliases_list = [x.aliases for x in self.bot.commands if len(x.aliases) > 0]
        aliases_list = [item for sublist in aliases_list for item in sublist]
        if ctx.command.root_parent and str(ctx.command.root_parent).strip() in cmds_list: # Removes command from list to prevent from it disabling its own command
            cmds_list.remove(str(ctx.command.root_parent).strip())
            if len(ctx.command.root_parent.aliases) > 0:
                for alias in ctx.command.root_parent.aliases: aliases_list.remove(alias.strip())    

        if command.lower() in cmds_list or command.lower() in aliases_list:
            command_obj = self.bot.get_command(command)
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            modules_config = qulib.get_module_config()
            if command_obj.cog_name not in modules_config["restricted_modules"]:
                if not CommandController.is_disabled(command_obj.name, ctx.guild.id):
                    await CommandController.disable_command(command_obj.name, ctx.guild.id)
                    embed = discord.Embed(title=lang["core_command_disable"].format(command_obj.name), color=self.module_embed_color)
                else:
                    embed = discord.Embed(title=lang["core_command_already_disabled"].format(command_obj.name), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_command_restricted_module"].format(command_obj.cog_name), color=self.module_embed_color)
            await ctx.send(embed=embed, delete_after=15)
        else:
            raise commands.errors.BadArgument("Could not enable/disable command. Command not found.")

    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command(name='userid', help=main.lang["command_userid_help"], description=main.lang["command_userid_description"], aliases=['uid'], usage="@somebody", hidden=True)
    async def userid(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["core_userid_msg"].format(user.name,user.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)
    
    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command(name='serverid', help=main.lang["empty_string"], description=main.lang["command_serverid_description"], aliases=['sid'], hidden=True, ignore_extra=True)
    @commands.guild_only()
    async def serverid(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["core_serverid_msg"].format(ctx.guild.name,ctx.guild.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command(name='channelid', help=main.lang["empty_string"], description=main.lang["command_channelid_description"], aliases=['cid'], hidden=True, ignore_extra=True)
    @commands.guild_only()
    async def channelid(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["core_channelid_msg"].format(ctx.guild.name, ctx.channel.name, ctx.channel.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.command(name='roleid', help=main.lang["empty_string"], description=main.lang["command_roleid_description"], aliases=['rid'], usage="Moderator", hidden=True)
    @commands.guild_only()
    async def roleid(self, ctx, *, role: discord.Role):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["core_roleid_msg"].format(ctx.guild.name, role.name, role.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)
    
    @commands.command(name='remove', help=main.lang["empty_string"], description=main.lang["command_remove_description"], hidden=True, ignore_extra=True)
    @commands.has_permissions(kick_members=True)
    async def remove(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["core_remove_msg"], color=self.module_embed_color)
        await ctx.send(embed=embed)
        await ctx.guild.leave()

    @commands.command(name='latencies', help=main.lang["command_owner_only"], description=main.lang["command_latencies_description"], hidden=True, ignore_extra=True)
    @commands.is_owner()
    async def latencies(self, ctx):
        string_output = ''
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        for shard in self.bot.latencies:
            shards_guild_counter = 0
            guild_list = (g for g in self.bot.guilds if g.shard_id is shard[0])
            for _ in guild_list:
                shards_guild_counter += 1
            string_output += lang["core_latencies"].format(shard[0], shards_guild_counter, "%.4f" % float(shard[1]*1000))
        embed = discord.Embed(title=lang["core_latencies_msg"], description=string_output, color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @commands.command(name='setname', help=main.lang["command_owner_only"], description=main.lang["command_setname_description"], usage="<new name>", hidden=True)
    @commands.is_owner()
    async def setname(self, ctx, *, input_name: str):
        await self.bot.user.edit(username=input_name)
    
    @commands.command(name='setstatus', help=main.lang["command_setstatus_help"], description=main.lang["command_setstatus_description"], usage="dnd", hidden=True)
    @commands.is_owner()
    async def setstatus(self, ctx, input_status: str):
        if input_status in ('online', 'offline', 'idle', 'dnd', 'invisible'):
            await self.bot.change_presence(status=input_status, shard_id=None)
    
    @commands.command(name='setactivity', help=main.lang["command_setactivity_help"], description=main.lang["command_setactivity_description"], usage="playing with corgis", hidden=True)
    @commands.is_owner()
    async def setactivity(self, ctx, input_activity:str = None, *, input_string:str = None):
        if input_activity:
            if input_activity in ('playing', 'streaming', 'listening', 'watching'):
                type_dict= {'playing': 0, 'listening': 2, 'watching': 3}
                activity = discord.Activity(type=type_dict[input_activity],name = input_string)
                await ctx.bot.change_presence(activity=activity, shard_id=None)
        else:
            await ctx.bot.change_presence(activity=None, shard_id=None)

    @commands.command(name='restart', help=main.lang["command_owner_only"], description=main.lang["command_restart_description"], hidden=True, ignore_extra=True)
    @commands.is_owner()
    async def restart(self, ctx):
        embed = discord.Embed(title="Restarting bot...", color=self.module_embed_color)
        await ctx.send(embed=embed)
        try:
            process = psutil.Process(os.getpid())
            for handler in process.open_files() + process.connections():
                os.close(handler.fd)
        except Exception as e:
            logger.error(e)
        os.execl(sys.executable, sys.executable, *sys.argv)

    @commands.command(name='shutdown', help=main.lang["command_owner_only"], description=main.lang["command_shutdown_description"], hidden=True, ignore_extra=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        embed = discord.Embed(title="Shutting down bot...", color=self.module_embed_color)
        await ctx.send(embed=embed)
        await self.bot.http.close()
        await self.bot.close()

    @commands.command(name="langs", help=main.lang["empty_string"], description=main.lang["command_langs_description"], aliases=['languages'], hidden=True, ignore_extra=True)
    async def lang_list(self, ctx):
        lang_directory_list = [os.path.splitext(i)[0] for i in os.listdir(os.path.join(bot_path, 'data/localization')) if ("language" in os.path.splitext(i)[0] and os.path.splitext(i)[1] == ".json")]
        lang_list = [x.replace('language_', '') for x in lang_directory_list]
        lang_string = ''
        for lang_item in lang_list:
            lang_string += f'\u2022 {lang_item}\n'
        localization = Localizations()
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["core_langs_title"], description=lang_string, color=self.module_embed_color)
        embed.set_footer(text=f'{lang["core_langs_footer"]}: {localization.get_language(ctx.guild.id, main.languagecode)}')
        await ctx.send(embed=embed)

    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.command(name="langset", help=main.lang["command_langset_help"], description=main.lang["command_langset_description"], usage="en-US", hidden=True)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def lang_set(self, ctx, lang_code: str = None):
        lang_directory_list = [os.path.splitext(i)[0] for i in os.listdir(os.path.join(bot_path, 'data/localization')) if ("language" in os.path.splitext(i)[0] and os.path.splitext(i)[1] == ".json")]
        lang_list = [x.replace('language_', '') for x in lang_directory_list]
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if lang_code in lang_list:
            localization = Localizations()
            if lang_code != localization.get_language(ctx.guild.id, main.languagecode):
                localization.set_language(ctx.guild.id, lang_code)
                embed = discord.Embed(title=lang["core_langset_success"].format(lang_code), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_langset_same"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["core_langset_notfound"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.group(name='prefix', invoke_without_command=True, help=main.lang["command_prefix_help"], description=main.lang["command_prefix_description"], usage="q!")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def prefix(self, ctx, *, new_prefix: str = None):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if not new_prefix:
                embed = discord.Embed(title=lang["core_prefix_info"].format(PrefixHandler.get_prefix(ctx.guild.id, main.prefix)), color=self.module_embed_color)
            elif len(new_prefix) > main.max_prefix_length:
                embed = discord.Embed(title=lang["core_prefix_length_limit"].format(main.max_prefix_length), color=self.module_embed_color)
            else:
                PrefixHandler.set_prefix(ctx.guild.id, new_prefix)
                embed = discord.Embed(title=lang["core_prefix_success"].format(new_prefix), color=self.module_embed_color)
            await ctx.send(embed=embed)

    @prefix.command(name='reset', help=main.lang["command_prefix_reset_help"], description=main.lang["command_prefix_reset_description"], ignore_extra=True)
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def prefix_reset(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        PrefixHandler.set_prefix(ctx.guild.id, main.prefix)
        await ctx.send(embed=discord.Embed(title=lang["core_prefix_reset"].format(main.prefix), color=self.module_embed_color))

    @prefix.command(name='show', help=main.lang["empty_string"], description=main.lang["command_prefix_show_description"], ignore_extra=True)
    @commands.guild_only()
    async def prefix_show(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed=discord.Embed(title=lang["core_prefix_info"].format(PrefixHandler.get_prefix(ctx.guild.id, main.prefix)), color=self.module_embed_color))

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_guild_join(self, guild):
        lang = main.get_lang(guild.id) if guild else main.lang
        guild_prefix = PrefixHandler.get_prefix(guild.id, main.prefix) if guild else main.prefix
        app_info = await self.bot.application_info()

        channel = discord.utils.find(lambda c: c.name == "general", guild.text_channels)
        if not channel:
            channel = discord.utils.find(lambda c: guild.me.permissions_in(c).send_messages == True, guild.text_channels)
        if channel:
            embed = discord.Embed(title=lang["bot_guild_join_title"], description=lang["bot_guild_join_description"].format(app_info.name, guild_prefix), color = self.module_embed_color)
            embed.set_thumbnail(url=f"{self.bot.user.avatar_url}")
            await channel.send(embed=embed)

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_guild_remove(self, guild):
        PrefixHandler.remove_guild(guild.id) # PrefixHandler takes care of language data removal as well since its tied to the same table
        await CommandController.remove_disabled_commands(guild.id)
        await CogController.remove_disabled_cogs(guild.id)

def setup(bot):
    bot.add_cog(Core(bot))