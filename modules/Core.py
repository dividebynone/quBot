from discord.ext import commands
from main import lang, bot_starttime
from main import modules as loaded_modules
from libs.qulib import data_get, data_set
from datetime import datetime
import discord
import json

class Core(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0xf0f3f4
        print(f'Module {self.__class__.__name__} loaded')

    @commands.command(name='load', help=lang["command_module_help"], description=lang["command_load_description"], usage="<module name>", hidden=True)
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
                embed = discord.Embed(title=lang["core_module_load_fail"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_load_success"].format(input_module), color=self.module_embed_color)
                loaded_modules.append(input_module_path)
                with open('./data/modules.mdls', 'a') as modules_file:
                        modules_file.write(f'{input_module}\n')             
        await ctx.send(embed=embed, delete_after=20)

    @commands.command(name='unload', help=lang["command_module_help"], description=lang["command_unload_description"], usage="<module name>", hidden=True)
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
                embed = discord.Embed(title=lang["core_module_unload_fail"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_unload_success"].format(input_module), color=self.module_embed_color)
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

    @commands.command(name='reload', help=lang["command_module_help"], description=lang["command_reload_description"], usage="<module name>", hidden=True)
    @commands.is_owner()
    async def module_reload(self, ctx, *, input_module: str):
        try:
            input_module_path = f'modules.{input_module}'
            if input_module_path in loaded_modules:
                self.bot.unload_extension(input_module_path)
                self.bot.load_extension(input_module_path)
        except Exception as e:
            embed = discord.Embed(title=f'**`ERROR:`** {type(e).__name__} - {e}', color=self.module_embed_color)
        else:
            if input_module_path not in loaded_modules:
                embed = discord.Embed(title=lang["core_module_reload_fail"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_reload_success"].format(input_module), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=20)
    
    @commands.group(name='modules', aliases=['mdls'], help=lang["empty_string"], description=lang["command_modules_description"])
    async def modules(self, ctx):
        if not ctx.invoked_subcommand:
            modules_list = ''
            loaded_modules_names = [i.replace('modules.', '') for i in loaded_modules]
            data = await data_get()
            for i in loaded_modules_names:
                if i not in data["hidden_modules"]:
                    modules_list += f'\u2022 {i}\n'
            embed = discord.Embed(title=lang["core_modules_list"],description=modules_list, color=self.module_embed_color)
            await ctx.author.send(embed=embed)
    
    @modules.command(help=lang["command_modules_hide_help"], description=lang["command_modules_hide_description"], usage="<module name>")
    @commands.is_owner()
    async def hide(self, ctx, *, input_module: str):
        input_module_path = f'modules.{input_module}'
        if input_module_path in loaded_modules:
            data = await data_get()
            if input_module not in data["hidden_modules"]:
                data["hidden_modules"].append(input_module)
                await data_set(data)
                embed = discord.Embed(title=lang["core_module_hide_success"].format(input_module), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_hide_hidden"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["core_module_hide_fail"], color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @modules.command(help=lang["command_modules_unhide_help"], description=lang["command_modules_unhide_description"], usage="<module name>")
    @commands.is_owner()
    async def unhide(self, ctx, *, input_module: str):
        input_module_path = f'modules.{input_module}'
        if input_module_path in loaded_modules:
            data = await data_get()
            if input_module in data["hidden_modules"]:
                data["hidden_modules"].remove(input_module)
                await data_set(data)
                embed = discord.Embed(title=lang["core_module_unhide_success"].format(input_module), color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_unhide_visible"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["core_module_unhide_fail"], color=self.module_embed_color)
        await ctx.author.send(embed=embed)
    
    @commands.command(name='commands', aliases=['cmds'], help=lang["empty_string"], description=lang["command_cmds_description"], usage="<module name>")
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
                    embed = discord.Embed(title=lang["core_cmds_list_empty"].format(input_module), color=self.module_embed_color)
                else:
                    embed = discord.Embed(title=lang["core_cmds_list"].format(input_module),description=commands_list, color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_cmds_list_not_found"].format(input_module), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["core_cmds_list_marg"], color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @commands.command(name='userid', help=lang["command_userid_help"], description=lang["command_userid_description"], usage="@somebody", hidden=True)
    @commands.is_owner()
    async def userid(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        embed = discord.Embed(title=lang["core_userid_msg"].format(user.name,user.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)
    
    @commands.command(name='serverid', help=lang["command_owner_only"], description=lang["command_serverid_description"], hidden=True, ignore_extra=True)
    @commands.is_owner()
    @commands.guild_only()
    async def serverid(self, ctx):
        embed = discord.Embed(title=lang["core_serverid_msg"].format(ctx.guild.name,ctx.guild.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @commands.command(name='channelid', help=lang["command_owner_only"], description=lang["command_channelid_description"], hidden=True, ignore_extra=True)
    @commands.is_owner()
    @commands.guild_only()
    async def channelid(self, ctx):
        embed = discord.Embed(title=lang["command_owner_only"].format(ctx.guild.name, ctx.channel.name, ctx.channel.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)
    
    @commands.command(name='leave', help=lang["empty_string"], description=lang["command_leave_description"], hidden=True, ignore_extra=True)
    @commands.has_permissions(kick_members=True)
    async def leave(self, ctx):
        embed = discord.Embed(title=lang["core_leave_msg"], color=self.module_embed_color)
        await ctx.send(embed=embed)
        await ctx.guild.leave()

    @commands.command(name='latencies', help=lang["command_owner_only"], description=lang["command_latencies_description"], hidden=True, ignore_extra=True)
    @commands.is_owner()
    async def latencies(self, ctx):
        string_output = ''
        for shard in self.bot.latencies:
            shards_guild_counter = 0
            guild_list = (g for g in self.bot.guilds if g.shard_id is shard[0])
            for _ in guild_list:
                shards_guild_counter += 1
            string_output += lang["core_latencies"].format(shard[0], shards_guild_counter, "%.4f" % float(shard[1]*1000))
        embed = discord.Embed(title=lang["core_latencies_msg"], description=string_output, color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @commands.command(name='setname', help=lang["command_owner_only"], description=lang["command_setname_description"], usage="<new name>", hidden=True)
    @commands.is_owner()
    async def setname(self, ctx, *, input_name: str):
        await self.bot.user.edit(username=input_name)
    
    @commands.command(name='setstatus', help=lang["command_setstatus_help"], description=lang["command_setstatus_description"], usage="dnd", hidden=True)
    @commands.is_owner()
    async def setstatus(self, ctx, input_status: str):
        if input_status in ('online', 'offline', 'idle', 'dnd', 'invisible'):
            await self.bot.change_presence(status=input_status, shard_id=None)
    
    @commands.command(name='setactivity', help=lang["command_setactivity_help"], description=lang["command_setactivity_description"], usage="playing with corgis", hidden=True)
    @commands.is_owner()
    async def setactivity(self, ctx, input_activity:str = None, *, input_string:str = None):
        if input_activity:
            if input_activity in ('playing', 'streaming', 'listening', 'watching'):
                type_dict= {'playing': 0, 'listening': 2, 'watching': 3}
                activity = discord.Activity(type=type_dict[input_activity],name = input_string)
                await ctx.bot.change_presence(activity=activity, shard_id=None)
        else:
            await ctx.bot.change_presence(activity=None, shard_id=None)
    
def setup(bot):
    bot.add_cog(Core(bot))