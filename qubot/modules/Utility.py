from discord.ext import commands
from main import bot_starttime
from main import modules as loaded_modules
from datetime import datetime
from libs.qulib import ExtendedCommand, ExtendedGroup
import libs.qulib as qulib
import main
import discord
import secrets
import random

class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.embed_color =  0xaa6cba

        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = False
        self.module_dependencies = []

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)

        print(f'Module {self.__class__.__name__} loaded')

    # Method used internally to shorten the user list if it exceeds a set number of lines
    def slice_userlist(self, istring: str, lines: int, langset):
        if istring.count('\n') > lines:
            other_count = istring.count('\n') - lines
            istring = '\n'.join(istring.split('\n')[:lines]) + "\n(+ {} {})".format(other_count, langset["others_string"] if other_count > 1 else langset["other_string"])
        return istring

    @commands.command(name='avatar', help=main.lang["command_avatar_help"], description=main.lang["command_avatar_description"], usage="<user>")
    async def avatar(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["utility_avatar_msg"].format(user.name), color=self.embed_color)
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='roll', help=main.lang["command_roll_help"], description=main.lang["command_roll_description"], usage="<number>", aliases=['r'], ignore_extra=True)
    async def roll(self, ctx, number: int = 100):
        random.seed()
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(title=lang["utility_roll_msg"].format(random.randrange(number + 1)), color=self.embed_color))

    @commands.command(cls=ExtendedCommand, name='uptime', description=main.lang["command_uptime_description"], ignore_extra=True, permissions=['Administrator'])
    @commands.has_permissions(administrator=True)
    async def uptime(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(title=lang["utility_uptime_msg"].format(qulib.humanize_time(lang, bot_starttime)), color=self.embed_color))

    @commands.command(name='userinfo', help=main.lang["command_uinfo_help"], description=main.lang["command_uinfo_description"], usage="<user>", aliases=['uinfo'])
    @commands.guild_only()
    async def userinfo(self, ctx, *, user: discord.Member = None):
        user = user or ctx.author
        user_roles_dict = [x.name for x in user.roles if x.name != '@everyone']
        user_roles = ', '.join(user_roles_dict) or "-"
        user_created_at = user.created_at.strftime("%d %b %Y %H:%M:%S")
        user_joined_at = user.joined_at.strftime("%d %b %Y %H:%M:%S")
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=f'{user}', color = self.embed_color)
        embed.set_thumbnail(url="{}".format(user.avatar_url))
        embed.add_field(name=lang["utility_uinfo_id"], value=user.id, inline=True)
        embed.add_field(name=lang["utility_uinfo_nickname"], value=user.nick, inline=True)
        embed.add_field(name=lang["utility_uinfo_created"], value=f'{user_created_at} UTC', inline=False)
        embed.add_field(name=lang["utility_uinfo_joined"], value=f'{user_joined_at} UTC', inline=True)
        embed.add_field(name=lang["utility_uinfo_sroles"].format(len(user_roles_dict)), value=user_roles, inline=False)
        await ctx.send(embed=embed)

    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.command(name='botinfo', help=main.lang["command_binfo_help"], description=main.lang["command_binfo_description"], aliases=['binfo', 'status', 'about'], ignore_extra=True)
    async def botinfo(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        shards_guild_counter = 0
        total_guild_users = 0
        current_shard_latency = None
        for shard in self.bot.latencies:
            guild_list = (g for g in self.bot.guilds if g.shard_id is shard[0])
            for guild in guild_list:
                shards_guild_counter += 1
                total_guild_users += guild.member_count
                if guild.shard_id == shard[0]:
                    current_shard_latency = "%.4f" % float(shard[1]*1000)

        app_info = await self.bot.application_info()

        embed = discord.Embed(title=lang["utility_binfo_title"] ,color = self.embed_color)
        embed.set_thumbnail(url=f"{self.bot.user.avatar_url}")
        embed.add_field(name=lang["utility_binfo_bname"], value=app_info.name, inline=True)
        embed.add_field(name=lang["owner_string"], value=str(app_info.owner), inline=True)
        embed.add_field(name=lang["version_string"], value=main.version, inline=True)
        embed.add_field(name=lang["guilds_string"], value=shards_guild_counter, inline=True)
        embed.add_field(name=lang["users_string"], value=total_guild_users, inline=True)
        embed.add_field(name=lang["utility_binfo_latency"], value=f'{current_shard_latency} ms', inline=True)
        embed.add_field(name=lang["uptime_string"], value=f"```{qulib.humanize_time(lang, bot_starttime)}```", inline=False)
        embed.set_footer(text=lang["utility_binfo_author_footer"])
        await ctx.send(embed=embed)

    @commands.command(name='8ball', description=main.lang["command_8ball_description"], usage="<question>", aliases=['8b'])
    async def eight_ball(self, ctx, *, string: str):
        random.seed()
        ball_answer = random.randrange(1,21)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(description=f'\U0001F3B1 {lang[f"utility_8ball_{ball_answer}"]}', color=self.embed_color))

    @commands.command(name='choose', description=main.lang["command_choose_description"], usage="item 1; item 2; item 3...", aliases=['pick'])
    async def choose_random_items(self, ctx, *, choices: str):
        items = choices.split(';')
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(description=lang["utility_choose_msg"].format("\U0001F3B2", secrets.choice(items).lstrip()), color=self.embed_color))

    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.group(cls=ExtendedGroup, name='massnick', invoke_without_command=True, description=main.lang["command_massnick_description"], usage="<user(s)> <nickname>", aliases=['mnick'], permissions=['Administrator'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def mass_nickname(self, ctx, members: commands.Greedy[discord.Member], *, nickname: str):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if members:
                output = ""
                for member in members:
                    try:
                        await member.edit(nick=nickname)
                        output += f'{str(member)} ({member.mention})\n'
                    except discord.Forbidden:
                        pass
                await ctx.message.delete()

                output = self.slice_userlist(output, 20, lang)
                if len(output.strip()) > 0:
                    embed = discord.Embed(title=lang["utility_massnick_embed_title"], description=lang["utility_massnick_embed_desc"].format(nickname), timestamp=datetime.utcnow(), color=self.embed_color)
                    embed.add_field(name=lang["users_string"], value=output or lang["empty_string"], inline=True)
                    embed.set_footer(text=lang["utility_massnick_embed_footer"].format(str(ctx.author)))
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(lang["utility_massnick_empty"].format(ctx.author.mention), delete_after=15)
            else:
                await ctx.send(lang["utility_massnick_not_found"].format(ctx.author.mention), delete_after=15)

    @commands.cooldown(5, 30, commands.BucketType.user)
    @mass_nickname.command(cls=ExtendedCommand, name='reset', description=main.lang["command_massnick_reset_description"], usage="<user(s)>", aliases=['remove'], permissions=['Administrator'])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def mass_nickname_reset(self, ctx, members: commands.Greedy[discord.Member]):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if members:
            output = ""
            for member in members:
                try:
                    await member.edit(nick=None)
                    output += f'{str(member)} ({member.mention})\n'
                except discord.Forbidden:
                    pass
            await ctx.message.delete()

            output = self.slice_userlist(output, 20, lang)
            if len(output.strip()) > 0:
                embed = discord.Embed(title=lang["utility_massnick_reset_embed_title"], description=lang["utility_massnick_reset_embed_desc"], timestamp=datetime.utcnow(), color=self.embed_color)
                embed.add_field(name=lang["users_string"], value=output or lang["empty_string"], inline=True)
                embed.set_footer(text=lang["utility_massnick_reset_embed_footer"].format(str(ctx.author)))
                await ctx.send(embed=embed)
            else:
                await ctx.send(lang["utility_massnick_empty"].format(ctx.author.mention), delete_after=15)
        else:
            await ctx.send(lang["utility_massnick_not_found"].format(ctx.author.mention), delete_after=15)

def setup(bot):
    bot.add_cog(Utility(bot))