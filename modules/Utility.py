from discord.ext import commands
from main import lang, bot_starttime
from main import modules as loaded_modules
from datetime import datetime
import discord

class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0xf0f3f4
        print(f'Module {self.__class__.__name__} loaded')

    @commands.command(name='test')
    async def test(self, ctx, *, stringfd: str):
        await ctx.send(stringfd)

def setup(bot):
    bot.add_cog(Utility(bot))