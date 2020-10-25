from discord.ext import commands
from main import bot_starttime, config, bot_path
from main import modules as loaded_modules
from main import logger
import libs.qulib as qulib
from libs.utils.admintools import BlacklistedUsers
from libs.prefixhandler import PrefixHandler
from libs.commandscontroller import CommandController, CogController
from datetime import datetime
from libs.qulib import ExtendedCommand, ExtendedGroup
import asyncio
import math
import discord
import json
import os
import sys
import psutil
import main

class Core(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.embed_color =  0x91becc

        self.BlacklistedUsers = BlacklistedUsers()
        self.CommandController = CommandController()
        self.CogController = CogController()
        self.PrefixHandler = PrefixHandler()

        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = True
        self.module_dependencies = []

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)

        self.left = '⬅️'
        self.right = '➡️'
        self.pagination_timeout = '⏹️'

        print(f'Module {self.__class__.__name__} loaded')

    def predicate(self, message, l, r):
        def check(reaction, user):
            if reaction.message.id != message.id or user.id == self.bot.user.id:
                return False
            if l and reaction.emoji == self.left:
                return True
            if r and reaction.emoji == self.right:
                return True
            return False
        return check

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

    @commands.command(cls=ExtendedCommand, name='load', help=main.lang["command_module_help"], description=main.lang["command_load_description"], usage="<module>", hidden=True, permissions=['Bot Owner'])
    @commands.is_owner()
    async def module_load(self, ctx, *, input_module: str):
        try:
            input_module_path = f'modules.{input_module}'
            if input_module_path not in loaded_modules:
                self.bot.load_extension(input_module_path)
        except Exception as e:
            embed = discord.Embed(title=f'**`ERROR:`** {type(e).__name__} - {e}', color=self.embed_color)
        else:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if input_module_path in loaded_modules:
                embed = discord.Embed(title=lang["core_module_load_fail"], color=self.embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_load_success"].format(input_module), color=self.embed_color)
                loaded_modules.append(input_module_path)
                with open(os.path.join(bot_path, 'data', 'modules.mdls'), 'a') as modules_file:
                        modules_file.write(f'{input_module}\n')             
        await ctx.send(embed=embed, delete_after=15)

    @commands.command(cls=ExtendedCommand, name='unload', help=main.lang["command_module_help"], description=main.lang["command_unload_description"], usage="<module>", hidden=True, permissions=['Bot Owner'])
    @commands.is_owner()
    async def module_unload(self, ctx, *, input_module: str):
        try:
            input_module_path = f'modules.{input_module}'
            if input_module_path in loaded_modules:
                self.bot.unload_extension(input_module_path)
        except Exception as e:
            embed = discord.Embed(title=f'**`ERROR:`** {type(e).__name__} - {e}', color=self.embed_color)
        else:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if input_module_path not in loaded_modules:
                embed = discord.Embed(title=lang["core_module_unload_fail"], color=self.embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_unload_success"].format(input_module), color=self.embed_color)
                loaded_modules.remove(input_module_path)
                with open(os.path.join(bot_path, 'data', 'modules.mdls'), 'r+') as modules_file:
                    modules_output = modules_file.read()
                    modules_file.seek(0)
                    for i in modules_output.split():
                        if i != input_module:
                            modules_file.write(f'{i}\n')
                    modules_file.truncate()
                    modules_file.close()
        await ctx.send(embed=embed, delete_after=15)

    @commands.command(cls=ExtendedCommand, name='reload', help=main.lang["command_module_help"], description=main.lang["command_reload_description"], usage="<module>", hidden=True, permissions=['Bot Owner'])
    @commands.is_owner()
    async def module_reload(self, ctx, *, input_module: str):
        try:
            input_module_path = f'modules.{input_module}'
            if input_module_path in loaded_modules:
                self.bot.reload_extension(input_module_path)
        except Exception as e:
            embed = discord.Embed(title=f'**`ERROR:`** {type(e).__name__} - {e}', color=self.embed_color)
        else:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if input_module_path not in loaded_modules:
                embed = discord.Embed(title=lang["core_module_reload_fail"], color=self.embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_reload_success"].format(input_module), color=self.embed_color)
        await ctx.send(embed=embed, delete_after=15)
    
    @commands.group(name='modules', invoke_without_command=True, description=main.lang["command_modules_description"], aliases=['mdls'])
    async def modules(self, ctx):
        if not ctx.invoked_subcommand:
            modules_list = ''
            loaded_modules_names = [i.replace('modules.', '') for i in loaded_modules]
            modules_config = qulib.get_module_config()
            for i in loaded_modules_names:
                if i not in modules_config.setdefault("hidden_modules", []):
                    modules_list += f'\u2022 {i}\n'
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            await ctx.author.send(embed = discord.Embed(title=lang["core_modules_list"],description=modules_list, color=self.embed_color))

    @commands.cooldown(10, 60, commands.BucketType.guild)
    @modules.command(cls=ExtendedCommand, name='enable', description=main.lang["command_modules_enable_description"], usage="<module>", aliases=['e'], permissions=['Administrator'])
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
                    disabled_cogs = await CogController.disabled_cogs(ctx.guild.id)
                    unloaded_dependencies = set(modules_config.setdefault("dependencies", {})[cog_name]).intersection(disabled_cogs)
                    if len(unloaded_dependencies) > 0:
                        embed = discord.Embed(title=lang["core_module_enable_dependencies"].format(', '.join(str(e) for e in unloaded_dependencies)), color=self.embed_color)
                        await ctx.send(embed=embed, delete_after=30)
                        return

                await CogController.enable_cog(cog_name, ctx.guild.id)
                embed = discord.Embed(title=lang["core_module_enable_msg"].format(cog_name), color=self.embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_enable_already_enabled"].format(cog_name), color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["core_module_enable_not_found"], color=self.embed_color)
        await ctx.send(embed=embed, delete_after=30)

    @commands.cooldown(10, 60, commands.BucketType.guild)
    @modules.command(cls=ExtendedCommand, name='disable', description=main.lang["command_modules_disable_description"], usage="<module>", aliases=['d'], permissions=['Administrator'])
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
                disabled_cogs = await CogController.disabled_cogs(ctx.guild.id)
                loaded_dependencies = []
                for cog in modules_config.setdefault("dependencies", {}):
                    if cog_name in modules_config.setdefault("dependencies", {})[cog]:
                        if not disabled_cogs or cog not in disabled_cogs:
                            loaded_dependencies.append(cog)

                if len(loaded_dependencies) > 0:
                    embed = discord.Embed(title=lang["core_module_disable_dependencies"].format(', '.join(str(e) for e in loaded_dependencies)), color=self.embed_color)
                    embed.set_footer(text=lang["core_module_disable_dependencies_hint"])
                    await ctx.send(embed=embed, delete_after=30)
                    return

                if cog_name not in modules_config["restricted_modules"]:
                    await CogController.disable_cog(cog_name, ctx.guild.id)
                    embed = discord.Embed(title=lang["core_module_disable_msg"].format(cog_name), color=self.embed_color)
                else:
                    embed = discord.Embed(title=lang["core_module_disable_restricted"].format(cog_name), color=self.embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_disable_already_disabled"].format(cog_name), color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["core_module_disable_not_found"], color=self.embed_color)
        await ctx.send(embed=embed, delete_after=30)
        
    @modules.command(cls=ExtendedCommand, name='hide', description=main.lang["command_modules_hide_description"], usage="<module>", hidden=True, permissions=['Bot Owner'])
    @commands.is_owner()
    async def hide(self, ctx, *, input_module: str):
        input_module_path = f'modules.{input_module}'
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if input_module_path in loaded_modules:
            modules_config = qulib.get_module_config()
            if input_module not in modules_config.setdefault("hidden_modules", []):
                modules_config.setdefault("hidden_modules", []).append(input_module)
                qulib.update_module_config(modules_config)
                embed = discord.Embed(title=lang["core_module_hide_success"].format(input_module), color=self.embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_hide_hidden"], color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["core_module_hide_fail"], color=self.embed_color)
        await ctx.author.send(embed=embed)

    @modules.command(cls=ExtendedCommand, name='unhide', description=main.lang["command_modules_unhide_description"], usage="<module>", hidden=True, permissions=['Bot Owner'])
    @commands.is_owner()
    async def unhide(self, ctx, *, input_module: str):
        input_module_path = f'modules.{input_module}'
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if input_module_path in loaded_modules:
            modules_config = qulib.get_module_config()
            if input_module in modules_config.setdefault("hidden_modules", []):
                modules_config.setdefault("hidden_modules", []).remove(input_module)
                qulib.update_module_config(modules_config)
                embed = discord.Embed(title=lang["core_module_unhide_success"].format(input_module), color=self.embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_unhide_visible"], color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["core_module_unhide_fail"], color=self.embed_color)
        await ctx.author.send(embed=embed)
    
    @commands.group(name='commands', invoke_without_command=True, description=main.lang["command_cmds_description"], usage="<module>", aliases=['cmds'])
    async def cmds_list(self, ctx, *, input_module: str = None):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if input_module:
                loaded_modules_names = [i.replace('modules.', '') for i in loaded_modules]
                input_module = input_module.capitalize()
                if input_module in loaded_modules_names:
                    cmds_list = []
                    isowner = await ctx.bot.is_owner(ctx.author)
                    for command in self.bot.get_cog(input_module).walk_commands():
                        if not command.hidden or isowner:
                            cmds_list.append(command)

                    index = start_index = 0
                    last_index = math.floor(len(cmds_list)/10)
                    if len(cmds_list) % 10 == 0:
                        last_index -= 1
                      
                    msg = None
                    action = ctx.author.send
                    try:
                        while True:
                            embed = discord.Embed(title=lang["core_cmds_embed_title"].format(input_module), color=self.embed_color)
                            for command in cmds_list[(index*10):(index*10 + 10)]:
                                embed.add_field(name=f'{main.prefix}{command.qualified_name} {command.signature}', value=command.description or lang["empty_string"], inline=False)
                            if start_index != last_index:
                                embed.set_footer(text=f"{lang['page_string']} {index+1}/{last_index+1}")
                            res = await action(embed=embed)
                            if start_index == last_index:
                                return
                            if res is not None:
                                msg = res
                            l = index != 0
                            r = index != last_index
                            await msg.add_reaction(self.left)
                            if l:
                                await msg.add_reaction(self.left)
                            if r:
                                await msg.add_reaction(self.right)

                            react = (await self.bot.wait_for('reaction_add', check=self.predicate(msg, l, r), timeout=120.0))[0]
                            if react.emoji == self.left:
                                index -= 1
                            elif react.emoji == self.right:
                                index += 1
                            action = msg.edit
                    except asyncio.TimeoutError:
                        await msg.add_reaction(self.pagination_timeout)
                        return
                else:
                    await ctx.author.send(lang["core_cmds_list_not_found"].format(input_module), delete_after=15)
            else:
                await ctx.author.send(lang["core_cmds_list_marg"], delete_after=15)     

    @commands.cooldown(10, 30, commands.BucketType.guild)
    @cmds_list.command(cls=ExtendedCommand, name='enable', description=main.lang["command_command_enable_description"], usage='<command>', aliases=['e'], permissions=['Administrator'])
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
                embed = discord.Embed(title=lang["core_command_enable"].format(command_obj.name), color=self.embed_color)
            else:
                embed = discord.Embed(title=lang["core_command_already_enabled"].format(command_obj.name), color=self.embed_color)
            await ctx.send(embed=embed, delete_after=15)
        else:
            raise commands.errors.BadArgument("Could not enable/disable command. Command not found.")

    @commands.cooldown(10, 30, commands.BucketType.guild)
    @cmds_list.command(cls=ExtendedCommand, name='disable', description=main.lang["command_command_disable_description"], usage='<command>', aliases=['d'], permissions=['Administrator'])
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
                    embed = discord.Embed(title=lang["core_command_disable"].format(command_obj.name), color=self.embed_color)
                else:
                    embed = discord.Embed(title=lang["core_command_already_disabled"].format(command_obj.name), color=self.embed_color)
            else:
                embed = discord.Embed(title=lang["core_command_restricted_module"].format(command_obj.cog_name), color=self.embed_color)
            await ctx.send(embed=embed, delete_after=15)
        else:
            raise commands.errors.BadArgument("Could not enable/disable command. Command not found.")

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name='userid', help=main.lang["command_userid_help"], description=main.lang["command_userid_description"], aliases=['uid'], usage="<user>", hidden=True)
    async def userid(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.author.send(embed = discord.Embed(title=lang["core_userid_msg"].format(user.name,user.id), color=self.embed_color))
    
    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name='serverid', description=main.lang["command_serverid_description"], aliases=['sid'], hidden=True, ignore_extra=True)
    @commands.guild_only()
    async def serverid(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.author.send(embed = discord.Embed(title=lang["core_serverid_msg"].format(ctx.guild.name,ctx.guild.id), color=self.embed_color))

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name='channelid', description=main.lang["command_channelid_description"], aliases=['cid'], hidden=True, ignore_extra=True)
    @commands.guild_only()
    async def channelid(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.author.send(embed = discord.Embed(title=lang["core_channelid_msg"].format(ctx.guild.name, ctx.channel.name, ctx.channel.id), color=self.embed_color))

    @commands.cooldown(10, 30, commands.BucketType.user)
    @commands.command(name='roleid', description=main.lang["command_roleid_description"], aliases=['rid'], usage="<role>", hidden=True)
    @commands.guild_only()
    async def roleid(self, ctx, *, role: discord.Role):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.author.send(embed = discord.Embed(title=lang["core_roleid_msg"].format(ctx.guild.name, role.name, role.id), color=self.embed_color))
    
    @commands.command(cls=ExtendedCommand, name='remove', description=main.lang["command_remove_description"], hidden=True, ignore_extra=True, permissions=['Kick Members'])
    @commands.has_permissions(kick_members=True)
    async def remove(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(title=lang["core_remove_msg"], color=self.embed_color))
        await ctx.guild.leave()

    @commands.command(cls=ExtendedCommand, name='latencies', description=main.lang["command_latencies_description"], hidden=True, ignore_extra=True, permissions=['Bot Owner'])
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
        await ctx.author.send(embed = discord.Embed(title=lang["core_latencies_msg"], description=string_output, color=self.embed_color))

    @commands.command(cls=ExtendedCommand, name='setname', description=main.lang["command_setname_description"], usage="<name>", hidden=True, permissions=['Bot Owner'])
    @commands.is_owner()
    async def setname(self, ctx, *, input_name: str):
        await self.bot.user.edit(username=input_name)
    
    @commands.command(cls=ExtendedCommand, name='setstatus', help=main.lang["command_setstatus_help"], description=main.lang["command_setstatus_description"], usage="<status>", hidden=True, permissions=['Bot Owner'])
    @commands.is_owner()
    async def setstatus(self, ctx, input_status: str):
        input_status = input_status.lower()
        if input_status in ('online', 'offline', 'idle', 'dnd', 'invisible'):
            status_dict = {'online': discord.Status.online, 'offline': discord.Status.offline, 'idle': discord.Status.idle, 'dnd': discord.Status.dnd, 'invisible': discord.Status.invisible}
            await ctx.bot.change_presence(status=status_dict.get(input_status, discord.Status.online), shard_id=None)
    
    @commands.command(cls=ExtendedCommand, name='setactivity', help=main.lang["command_setactivity_help"], description=main.lang["command_setactivity_description"], usage="<activity>", hidden=True, permissions=['Bot Owner'])
    @commands.is_owner()
    async def setactivity(self, ctx, input_activity:str = None, *, input_string:str = None):
        input_activity = input_activity.lower()
        if input_activity:
            if input_activity in ('playing', 'listening', 'watching'):
                type_dict= {'playing': 0, 'listening': 2, 'watching': 3}
                activity = discord.Activity(type=type_dict.get(input_activity, None), name = input_string)
                await ctx.bot.change_presence(activity=activity, shard_id=None)
        else:
            await ctx.bot.change_presence(activity=None, shard_id=None)

    @commands.command(cls=ExtendedCommand, name='restart', description=main.lang["command_restart_description"], hidden=True, ignore_extra=True, permissions=['Bot Owner'])
    @commands.is_owner()
    async def restart(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(title=lang["core_restart"], color=self.embed_color))
        try:
            process = psutil.Process(os.getpid())
            for handler in process.open_files() + process.connections():
                os.close(handler.fd)
        except Exception as e:
            logger.error(e)
        os.execl(sys.executable, sys.executable, *sys.argv)

    @commands.command(cls=ExtendedCommand, name='shutdown', description=main.lang["command_shutdown_description"], hidden=True, ignore_extra=True, permissions=['Bot Owner'])
    @commands.is_owner()
    async def shutdown(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(title=lang["core_shutdown"], color=self.embed_color))
        await self.bot.http.close()
        await self.bot.close()

    @commands.cooldown(5, 60, commands.BucketType.user)
    @commands.command(name="translate", description=main.lang["command_translate_description"], ignore_extra=True)
    async def translate(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["core_translate_title"], description=lang["core_translate_description"], color=self.embed_color)
        embed.set_thumbnail(url=str(self.bot.user.avatar_url))
        await ctx.send(embed=embed)

    @commands.group(cls=ExtendedGroup, name='export', help=main.lang["command_export_help"], description=main.lang["command_export_description"], usage="<function>", hidden=True, permissions=['Bot Owner'])
    @commands.is_owner()
    async def export_group(self, ctx):
        if not ctx.invoked_subcommand:
            pass

    @export_group.command(cls=ExtendedCommand, name='commands', description=main.lang["command_export_commands_description"], aliases=['cmds', 'cmd'], permissions=['Bot Owner'])
    async def export_commands(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        json_export = {}
        for cog_name in self.bot.cogs:
            cog = self.bot.cogs[cog_name]
            for command in cog.walk_commands():
                command_dict = {}
                command_dict['name'] = command.qualified_name
                command_dict['aliases'] = command.aliases
                command_dict['description'] = command.description
                command_dict['help'] = command.help
                command_dict['usage'] = f"{main.prefix}{command.qualified_name} {command.usage}" if command.usage else f"{main.prefix}{command.qualified_name}"
                if hasattr(command, 'permissions'):
                    command_dict['permissions'] = command.permissions
                json_export.setdefault(cog.qualified_name, []).append(command_dict)

        qulib.export_commands(json_export)
        await ctx.send(lang["core_export_commands_success"], delete_after=15)

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
            embed = discord.Embed(title=lang["bot_guild_join_title"], description=lang["bot_guild_join_description"].format(app_info.name, guild_prefix), color = self.embed_color)
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