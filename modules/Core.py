from discord.ext import commands
from main import bot_starttime, config
from main import modules as loaded_modules
from main import logger
from libs.qulib import data_get, data_set
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
            if input_module_path in loaded_modules:
                embed = discord.Embed(title=main.lang["core_module_load_fail"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["core_module_load_success"].format(input_module), color=self.module_embed_color)
                loaded_modules.append(input_module_path)
                with open('./data/modules.mdls', 'a') as modules_file:
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
            if input_module_path not in loaded_modules:
                embed = discord.Embed(title=main.lang["core_module_unload_fail"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["core_module_unload_success"].format(input_module), color=self.module_embed_color)
                loaded_modules.remove(input_module_path)
                with open('./data/modules.mdls', 'r+') as modules_file:
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
            if input_module_path not in loaded_modules:
                embed = discord.Embed(title=main.lang["core_module_reload_fail"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["core_module_reload_success"].format(input_module), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=20)
    
    @commands.group(name='modules', aliases=['mdls'], help=main.lang["empty_string"], description=main.lang["command_modules_description"])
    async def modules(self, ctx):
        if not ctx.invoked_subcommand:
            modules_list = ''
            loaded_modules_names = [i.replace('modules.', '') for i in loaded_modules]
            data = await data_get()
            for i in loaded_modules_names:
                if i not in data["hidden_modules"]:
                    modules_list += f'\u2022 {i}\n'
            embed = discord.Embed(title=main.lang["core_modules_list"],description=modules_list, color=self.module_embed_color)
            await ctx.author.send(embed=embed)
    
    @modules.command(help=main.lang["command_modules_hide_help"], description=main.lang["command_modules_hide_description"], usage="<module name>")
    @commands.is_owner()
    async def hide(self, ctx, *, input_module: str):
        input_module_path = f'modules.{input_module}'
        if input_module_path in loaded_modules:
            data = await data_get()
            if input_module not in data["hidden_modules"]:
                data["hidden_modules"].append(input_module)
                await data_set(data)
                embed = discord.Embed(title=main.lang["core_module_hide_success"].format(input_module), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["core_module_hide_hidden"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["core_module_hide_fail"], color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @modules.command(help=main.lang["command_modules_unhide_help"], description=main.lang["command_modules_unhide_description"], usage="<module name>")
    @commands.is_owner()
    async def unhide(self, ctx, *, input_module: str):
        input_module_path = f'modules.{input_module}'
        if input_module_path in loaded_modules:
            data = await data_get()
            if input_module in data["hidden_modules"]:
                data["hidden_modules"].remove(input_module)
                await data_set(data)
                embed = discord.Embed(title=main.lang["core_module_unhide_success"].format(input_module), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["core_module_unhide_visible"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["core_module_unhide_fail"], color=self.module_embed_color)
        await ctx.author.send(embed=embed)
    
    @commands.command(name='commands', aliases=['cmds'], help=main.lang["empty_string"], description=main.lang["command_cmds_description"], usage="<module name>")
    async def cmds_list(self, ctx, *, input_module: str = None):
        if input_module:
            loaded_modules_names = [i.replace('modules.', '') for i in loaded_modules]
            if input_module in loaded_modules_names:
                commands_list = ''
                isowner = await ctx.bot.is_owner(ctx.author)
                for command in self.bot.get_cog(input_module).walk_commands():
                    if not command.hidden or isowner:
                        if command.parent:
                            commands_list += f'\u002d\u002d\u002d {command.name}\n'
                        else:
                            commands_list += f'\u2022 {command.name}\n'
                if not commands_list:
                    embed = discord.Embed(title=main.lang["core_cmds_list_empty"].format(input_module), color=self.module_embed_color)
                else:
                    embed = discord.Embed(title=main.lang["core_cmds_list"].format(input_module),description=commands_list, color=self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["core_cmds_list_not_found"].format(input_module), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["core_cmds_list_marg"], color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @commands.command(name='userid', help=main.lang["command_userid_help"], description=main.lang["command_userid_description"], aliases=['uid'], usage="@somebody", hidden=True)
    @commands.is_owner()
    async def userid(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        embed = discord.Embed(title=main.lang["core_userid_msg"].format(user.name,user.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)
    
    @commands.command(name='serverid', help=main.lang["command_owner_only"], description=main.lang["command_serverid_description"], aliases=['sid'], hidden=True, ignore_extra=True)
    @commands.is_owner()
    @commands.guild_only()
    async def serverid(self, ctx):
        embed = discord.Embed(title=main.lang["core_serverid_msg"].format(ctx.guild.name,ctx.guild.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @commands.command(name='channelid', help=main.lang["command_owner_only"], description=main.lang["command_channelid_description"], aliases=['cid'], hidden=True, ignore_extra=True)
    @commands.is_owner()
    @commands.guild_only()
    async def channelid(self, ctx):
        embed = discord.Embed(title=main.lang["core_channelid_msg"].format(ctx.guild.name, ctx.channel.name, ctx.channel.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @commands.command(name='roleid', help=main.lang["command_owner_only"], description=main.lang["command_roleid_description"], aliases=['rid'], usage="Moderator", hidden=True)
    @commands.is_owner()
    @commands.guild_only()
    async def roleid(self, ctx, *, role: discord.Role):
        embed = discord.Embed(title=main.lang["core_roleid_msg"].format(ctx.guild.name, role.name, role.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)
    
    @commands.command(name='leave', help=main.lang["empty_string"], description=main.lang["command_leave_description"], hidden=True, ignore_extra=True)
    @commands.has_permissions(kick_members=True)
    async def leave(self, ctx):
        embed = discord.Embed(title=main.lang["core_leave_msg"], color=self.module_embed_color)
        await ctx.send(embed=embed)
        await ctx.guild.leave()

    @commands.command(name='latencies', help=main.lang["command_owner_only"], description=main.lang["command_latencies_description"], hidden=True, ignore_extra=True)
    @commands.is_owner()
    async def latencies(self, ctx):
        string_output = ''
        for shard in self.bot.latencies:
            shards_guild_counter = 0
            guild_list = (g for g in self.bot.guilds if g.shard_id is shard[0])
            for _ in guild_list:
                shards_guild_counter += 1
            string_output += main.lang["core_latencies"].format(shard[0], shards_guild_counter, "%.4f" % float(shard[1]*1000))
        embed = discord.Embed(title=main.lang["core_latencies_msg"], description=string_output, color=self.module_embed_color)
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

    @commands.command(name="langs", help=main.lang["command_owner_only"], description=main.lang["command_langs_description"], aliases=['languages'], hidden=True, ignore_extra=True)
    @commands.is_owner()
    async def lang_list(self, ctx):
        lang_directory_list = [os.path.splitext(i)[0] for i in os.listdir('./data/localization') if ("language" in os.path.splitext(i)[0] and os.path.splitext(i)[1] == ".json")]
        lang_list = [x.replace('language_', '') for x in lang_directory_list]
        lang_string = ''
        for lang_item in lang_list:
            lang_string += f'\u2022 {lang_item}\n'
        embed = discord.Embed(title=main.lang["core_langs_title"], description=lang_string, color=self.module_embed_color)
        embed.set_footer(text=f'{main.lang["core_langs_footer"]}: {main.languagecode}')
        await ctx.send(embed=embed)

    @commands.command(name="langset", help=main.lang["command_owner_only"], description=main.lang["command_langset_description"], usage="en-US", hidden=True)
    @commands.is_owner()
    async def lang_set(self, ctx, lang_code: str = None):
        lang_directory_list = [os.path.splitext(i)[0] for i in os.listdir('./data/localization') if ("language" in os.path.splitext(i)[0] and os.path.splitext(i)[1] == ".json")]
        lang_list = [x.replace('language_', '') for x in lang_directory_list]
        if lang_code in lang_list:
            if lang_code != main.languagecode:
                with open('./data/localization/language_{}.json'.format(lang_code), 'r', encoding="utf-8") as json_file:
                    main.lang = json.load(json_file)
                    main.languagecode = lang_code
                    config['Language']['CommandLanguageCode'] = lang_code
                    with open('config.ini', 'w', encoding="utf_8") as config_file:
                        config.write(config_file)
                    config_file.close()
                    embed = discord.Embed(title=main.lang["core_langset_success"].format(lang_code), color=self.module_embed_color)
                    for module in loaded_modules:
                        self.bot.reload_extension(module)
                json_file.close()
            else:
                embed = discord.Embed(title=main.lang["core_langset_same"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["core_langset_notfound"], color=self.module_embed_color)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Core(bot))