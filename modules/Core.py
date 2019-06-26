from discord.ext import commands
from main import lang, json_data, bot_starttime
from main import modules as loaded_modules
from datetime import datetime
import discord

class Core(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0xf0f3f4
        print(f'Module {self.__class__.__name__} loaded')

    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def module_load(self, ctx, *, module_input: str):
        try:
            module_input_path = f'modules.{module_input}'
            if module_input_path not in loaded_modules:
                self.bot.load_extension(module_input_path) 
        except Exception as e:
            embed = discord.Embed(title=f'**`ERROR:`** {type(e).__name__} - {e}', color=self.module_embed_color)
        else:
            if module_input_path in loaded_modules:
                embed = discord.Embed(title=lang["core_module_load_fail"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_load_success"].format(module_input), color=self.module_embed_color)
                loaded_modules.append(module_input_path)
                with open('./data/modules.mdls', 'a') as modules_file:
                        modules_file.write(f'{module_input}\n')             
        await ctx.send(embed=embed, delete_after=20)

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def module_unload(self, ctx, *, module_input: str):
        try:
            module_input_path = f'modules.{module_input}'
            if module_input_path in loaded_modules:
                 self.bot.unload_extension(module_input_path)
        except Exception as e:
            embed = discord.Embed(title=f'**`ERROR:`** {type(e).__name__} - {e}', color=self.module_embed_color)
        else:
            if module_input_path not in loaded_modules:
                embed = discord.Embed(title=lang["core_module_unload_fail"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_unload_success"].format(module_input), color=self.module_embed_color)
                loaded_modules.remove(module_input_path)
                with open('./data/modules.mdls', 'r+') as modules_file:
                    modules_output = modules_file.read()
                    modules_file.seek(0)
                    for i in modules_output.split():
                        if i != module_input:
                            modules_file.write(f'{i}\n')
                    modules_file.truncate()
                    modules_file.close()
        await ctx.send(embed=embed, delete_after=20)

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def module_reload(self, ctx, *, module_input: str):
        try:
            module_input_path = f'modules.{module_input}'
            if module_input_path in loaded_modules:
                self.bot.unload_extension(module_input_path)
                self.bot.load_extension(module_input_path)
        except Exception as e:
            embed = discord.Embed(title=f'**`ERROR:`** {type(e).__name__} - {e}', color=self.module_embed_color)
        else:
            if module_input_path not in loaded_modules:
                embed = discord.Embed(title=lang["core_module_reload_fail"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_module_reload_success"].format(module_input), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=20)
    
    @commands.command(name='modules', aliases=['mdls'], ignore_extra=True)
    async def modules(self, ctx):
        modules_list = ''
        loaded_modules_names = [i.replace('modules.', '') for i in loaded_modules]
        for i in loaded_modules_names:
            if i not in json_data["hidden_modules"]:
                modules_list += f'\u2022 {i}\n'
        embed = discord.Embed(title=lang["core_modules_list"],description=modules_list, color=self.module_embed_color)
        await ctx.author.send(embed=embed)
    
    @commands.command(name='commands', aliases=['cmds'])
    async def cmds_list(self, ctx, *, module_input: str = None):
        if module_input:
            loaded_modules_names = [i.replace('modules.', '') for i in loaded_modules]
            if module_input in loaded_modules_names:
                commands_list = ''
                isowner = await ctx.bot.is_owner(ctx.author)
                for command in self.bot.get_cog(module_input).get_commands():
                    if not command.hidden or isowner:
                        commands_list += f'\u2022 {command.name}\n'
                if not commands_list:
                    embed = discord.Embed(title=lang["core_cmds_list_empty"].format(module_input), color=self.module_embed_color)
                else:
                    embed = discord.Embed(title=lang["core_cmds_list"].format(module_input),description=commands_list, color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["core_cmds_list_not_found"].format(module_input), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["core_cmds_list_marg"], color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @commands.command(name='userid', hidden=True)
    @commands.is_owner()
    async def userid(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        embed = discord.Embed(title=lang["core_userid_msg"].format(user.name,user.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)
    
    @commands.command(name='serverid', hidden=True, ignore_extra=True)
    @commands.is_owner()
    @commands.guild_only()
    async def serverid(self, ctx):
        embed = discord.Embed(title=lang["core_serverid_msg"].format(ctx.guild.name,ctx.guild.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @commands.command(name='channelid', hidden=True, ignore_extra=True)
    @commands.is_owner()
    @commands.guild_only()
    async def channelid(self, ctx):
        embed = discord.Embed(title=lang["core_channelid_msg"].format(ctx.guild.name, ctx.channel.name, ctx.channel.id), color=self.module_embed_color)
        await ctx.author.send(embed=embed)
    
    @commands.command(name='leave', hidden=True, ignore_extra=True)
    @commands.has_permissions(kick_members=True)
    async def leave(self, ctx):
        embed = discord.Embed(title=lang["core_leave_msg"], color=self.module_embed_color)
        await ctx.send(embed=embed)
        await ctx.guild.leave()

def setup(bot):
    bot.add_cog(Core(bot))