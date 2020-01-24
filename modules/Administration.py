from discord.ext import commands
from main import bot_starttime
from main import modules as loaded_modules
from datetime import datetime
import main
import discord

class Administration(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0xdc143c
        print(f'Module {self.__class__.__name__} loaded')

    @commands.command(name='purge', help=main.lang["command_purge_help"], description=main.lang["command_purge_description"], usage="10", ignore_extra=True)
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def purge(self, ctx, prune_num: int):
        if prune_num > 0:
            await ctx.message.delete()
            await ctx.channel.purge(limit=prune_num,bulk=True)
            embed = discord.Embed(title=main.lang["administration_purge_delmsg"].format(prune_num), color=self.module_embed_color)
            await ctx.send(embed=embed, delete_after=10)
        else:
            await ctx.send(main.lang["administration_purge_prmsg"], delete_after=10)
    
    @commands.command(name='kick', help=main.lang["command_kick_help"], description=main.lang["command_kick_description"], usage="@somebody Spamming")
    @commands.has_permissions(kick_members=True)
    @commands.guild_only()
    async def kick(self, ctx, user: discord.Member, *, kick_reason: str = None):
        await ctx.message.delete()
        await ctx.guild.kick(user, reason=kick_reason)
        embed = discord.Embed(title=main.lang["administration_kick_msg"].format(user,kick_reason), color=self.module_embed_color)
        await ctx.send(embed=embed, delete_after=10)

    @commands.command(name='ban', help=main.lang["command_ban_help"], description=main.lang["command_ban_description"], usage="@somebody 4 Harassment")
    @commands.has_permissions(ban_members=True)
    @commands.guild_only()
    async def ban(self, ctx, user: discord.Member, delete_msg_days: int = 0, *, ban_reason: str = None):
        await ctx.message.delete()
        if delete_msg_days > 7 or delete_msg_days < 0:
            await ctx.send(main.lang["administration_ban_out_of_range"], delete_after=10)
        else:
            await ctx.guild.ban(user, reason=ban_reason, delete_message_days=delete_msg_days)
            embed = discord.Embed(title=main.lang["administration_ban_msg"].format(user,delete_msg_days,ban_reason), color=self.module_embed_color)
            await ctx.send(embed=embed, delete_after=10)

def setup(bot):
    bot.add_cog(Administration(bot))