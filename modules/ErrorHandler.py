from discord.ext import commands
from main import lang, bot_starttime
from main import modules as loaded_modules
from datetime import datetime
import discord

class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0xc10000
        print(f'Module {self.__class__.__name__} loaded')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, commands.NoPrivateMessage, commands.UserInputError, commands.MissingPermissions, commands.NotOwner, commands.NoPrivateMessage)
        error = getattr(error, 'original', error)
        embed = None

        if isinstance(error, ignored):
            return
        
        elif isinstance(error, commands.DisabledCommand):
            embed = discord.Embed(title=lang["errorhandler_dcmd"].format(ctx.command), color=self.module_embed_color)
        
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(title=lang["errorhandler_cooldown"].format(ctx.command, "%.1f" % error.retry_after), color=self.module_embed_color)

        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(title=lang["errorhandler_missing_perms"].format(error.missing_perms), color=self.module_embed_color)

        if embed:
            await ctx.send(embed=embed, delete_after=15)

def setup(bot):
    bot.add_cog(ErrorHandler(bot))