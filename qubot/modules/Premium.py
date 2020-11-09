from discord.ext import commands
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from libs.qulib import ExtendedCommand, ExtendedGroup
import libs.premiumhandler as premiumhandler
import libs.qulib as qulib
import discord
import main
import re


# Standard time converter - Converts a string into a seconds-based time interval
# Usage: Converts string input of a time interval into seconds
class TimePeriod(commands.Converter):

    def __init__(self):
        self.time_units = {'w': 'weeks', 'm': 'months', 'y': 'years'}

    async def convert(self, ctx, argument):
        rd = relativedelta(**{self.time_units.get(m.group('unit').lower(), 'months'): int(m.group('val')) for m in re.finditer(r'(?P<val>\d+)(\s?)(?P<unit>[wmy]?)', argument, flags=re.I)})
        now = datetime.utcnow()

        then = now - rd
        diff = now - then

        time_in_seconds = int(diff.total_seconds())

        if time_in_seconds == 0:
            raise commands.BadArgument("Failed to convert user input to a valid time frame.")
        return time_in_seconds


class Premium(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.embed_color = 0xffd663

        self.PremiumHandler = premiumhandler.PremiumHandler()

        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = True
        self.module_dependencies = []

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)

        print(f'Module {self.__class__.__name__} loaded')

    @commands.group(cls=ExtendedGroup, name='premium', hidden=True, permissions=['Bot Owner'])
    @commands.guild_only()
    @commands.is_owner()
    async def premium_group(self, ctx):
        if not ctx.invoked_subcommand:
            pass

    @premium_group.command(cls=ExtendedCommand, name='add', description=main.lang["command_premium_add_description"], usage="<user> <period>", hidden=True, permissions=['Bot Owner'])
    @commands.guild_only()
    @commands.is_owner()
    async def premium_add(self, ctx, user: discord.User, period: TimePeriod):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        user_premium_unix = await self.PremiumHandler.get_expiration(user.id)
        expiration_unix = int((user_premium_unix if user_premium_unix else datetime.utcnow().timestamp()) + period)
        expiration_time = datetime.fromtimestamp(expiration_unix, tz=timezone.utc)
        added = await self.PremiumHandler.update_premium(user.id, expiration_unix)
        if added:
            await ctx.send(embed=discord.Embed(title=lang["premium_add_success_title"],
                           description=lang["premium_add_success_desc"].format(str(user), expiration_time.strftime('%Y/%m/%d at %H:%M UTC')), color=self.embed_color))
        else:
            await ctx.send(lang["premium_add_failed"], delete_after=15)

    @premium_group.command(cls=ExtendedCommand, name='end', description=main.lang["command_premium_end_description"], usage="<user>", hidden=True, permissions=['Bot Owner'])
    @commands.guild_only()
    @commands.is_owner()
    async def premium_end(self, ctx, user: discord.User):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await self.PremiumHandler.end_premium(user.id)
        await ctx.send(embed=discord.Embed(title=lang["premium_end_success_title"], description=lang["premium_end_success_desc"].format(str(user)), color=self.embed_color))


def setup(bot):
    bot.add_cog(Premium(bot))
