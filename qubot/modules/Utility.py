from discord.ext import commands
from main import bot_starttime
from main import modules as loaded_modules
from datetime import datetime
from libs.qulib import ExtendedCommand
import libs.qulib as qulib
import main
import discord
import secrets
import random

class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.embed_color =  0xb405e3

        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = False
        self.module_dependencies = []

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)

        print(f'Module {self.__class__.__name__} loaded')

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
        time_on_command = datetime.today().replace(microsecond=0)
        bot_uptime = time_on_command - bot_starttime
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(title=lang["utility_uptime_msg"].format(bot_uptime.days,int(bot_uptime.seconds/3600), int((bot_uptime.seconds/60)%60),int(bot_uptime.seconds%60)), color=self.embed_color))

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
        time_on_command = datetime.today().replace(microsecond=0)
        bot_uptime = time_on_command - main.bot_starttime
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

        day_string = lang["days_string"] if bot_uptime.days != 1 else lang["day_string"]
        hours = int(bot_uptime.seconds/3600)
        hour_string = lang["hours_string"] if hours != 1 else lang["hour_string"]
        minutes = int((bot_uptime.seconds/60)%60)
        minutes_string = lang["minutes_string"] if minutes != 1 else lang["minute_string"]

        embed = discord.Embed(title=lang["utility_binfo_title"] ,color = self.embed_color)
        embed.set_thumbnail(url=f"{self.bot.user.avatar_url}")
        embed.add_field(name=lang["utility_binfo_bname"], value=app_info.name, inline=True)
        embed.add_field(name=lang["utility_binfo_owner"], value=str(app_info.owner), inline=True)
        embed.add_field(name=lang["utility_binfo_version"], value=main.version, inline=True)
        embed.add_field(name=lang["utility_binfo_guilds"], value=shards_guild_counter, inline=True)
        embed.add_field(name=lang["utility_binfo_users"], value=total_guild_users, inline=True)
        embed.add_field(name=lang["utility_binfo_latency"], value=f'{current_shard_latency} ms', inline=True)
        embed.add_field(name=lang["utility_binfo_uptime"], value=lang["utility_binfo_uptime_format"].format(bot_uptime.days, day_string, hours, hour_string, minutes, minutes_string), inline=False)
        embed.set_footer(text=lang["utility_binfo_author_footer"])
        await ctx.send(embed=embed)

    @commands.command(name='8ball', description=main.lang["command_8ball_description"], usage="<question>", aliases=['8b'])
    async def eight_ball(self, ctx, *, string: str):
        random.seed()
        ball_answer = random.randrange(1,21)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(title=lang[f"utility_8ball_{ball_answer}"], color=self.embed_color))

    @commands.command(name='choose', description=main.lang["command_choose_description"], usage="item 1; item 2; item 3...", aliases=['pick'])
    async def choose_random_items(self, ctx, *, choices: str):
        items = choices.split(';')
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed = discord.Embed(title=lang["utility_choose_msg"].format(secrets.choice(items).lstrip()), color=self.embed_color))

def setup(bot):
    bot.add_cog(Utility(bot))