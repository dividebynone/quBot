from discord.ext import commands
import main
import discord
import asyncio

class ErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0xc10000
        print(f'Module {self.__class__.__name__} loaded')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, commands.MissingPermissions, commands.UserInputError, commands.NotOwner, commands.NoPrivateMessage, asyncio.TimeoutError)
        error = getattr(error, 'original', error)
        embed = None

        if isinstance(error, ignored):
            return
        
        elif isinstance(error, commands.DisabledCommand):
            embed = discord.Embed(title=main.lang["errorhandler_dcmd"].format(ctx.command), color=self.module_embed_color)
        
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(title=main.lang["errorhandler_cooldown"].format(ctx.command, "%.1f" % error.retry_after), color=self.module_embed_color)

        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(title=main.lang["errorhandler_missing_perms"].format(error.missing_perms), color=self.module_embed_color)

        if embed:
            await ctx.send(embed=embed, delete_after=15)

def setup(bot):
    bot.add_cog(ErrorHandler(bot))