from discord.ext import commands
from main import lang, bot_starttime
from main import modules as loaded_modules
from datetime import datetime
import discord
import random

class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0xb405e3
        print(f'Module {self.__class__.__name__} loaded')

    @commands.command(name='avatar', help=lang["command_avatar_help"], description=lang["command_avatar_description"], usage="@somebody")
    async def avatar(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        embed = discord.Embed(title=lang["utility_avatar_msg"].format(user.name), color=self.module_embed_color)
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='roll', aliases=['r'], help=lang["command_roll_help"], description=lang["command_roll_description"], usage="9000", ignore_extra=True)
    async def roll(self, ctx, input_number: int = 100):
        embed = discord.Embed(title=lang["utility_roll_msg"].format(random.randrange(input_number + 1)), color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name='uptime', help=lang["empty_string"], description=lang["command_uptime_description"], ignore_extra=True)
    @commands.has_permissions(administrator=True)
    async def uptime(self, ctx):
        time_on_command = datetime.today().replace(microsecond=0)
        bot_uptime = time_on_command - bot_starttime
        embed = discord.Embed(title=lang["utility_uptime_msg"].format(bot_uptime.days,int(bot_uptime.seconds/3600),
                              int((bot_uptime.seconds/60)%60),int(bot_uptime.seconds%60)), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name='userinfo', aliases=['uinfo'], help=lang["command_uinfo_help"], description=lang["command_uinfo_description"], usage="@somebody",)
    @commands.guild_only()
    async def userinfo(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        user_roles = [x.name for x in user.roles if x.name != '@everyone']
        user_roles = ', '.join(user_roles) or "-"
        user_created_at = user.created_at.strftime("%d %b %Y %H:%M:%S")
        user_joined_at = user.joined_at.strftime("%d %b %Y %H:%M:%S")
        embed = discord.Embed(title=f'{user}', color = self.module_embed_color)
        embed.set_thumbnail(url="{}".format(user.avatar_url))
        embed.add_field(name=lang["utility_uinfo_id"], value=user.id, inline=True)
        embed.add_field(name=lang["utility_uinfo_nickname"], value=user.nick, inline=True)
        embed.add_field(name=lang["utility_uinfo_activity"], value=user.activity, inline=True)
        embed.add_field(name=lang["utility_uinfo_created"], value=user_created_at, inline=True)
        embed.add_field(name=lang["utility_uinfo_joined"], value=user_joined_at, inline=True)
        embed.add_field(name=lang["utility_uinfo_sroles"].format(len(user_roles)), value=user_roles, inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Utility(bot))