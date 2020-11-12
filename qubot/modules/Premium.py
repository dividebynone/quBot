from discord.ext import commands
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from libs.qulib import ExtendedCommand, ExtendedGroup
import libs.premiumhandler as premiumhandler
import libs.qulib as qulib
import discord
import main
import re


from main import bot_path
from aiohttp import web
import aiohttp_cors
import ssl
import os
import hmac
import hashlib


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

        self.webhook_task = self.bot.loop.create_task(self.webhook())

        print(f'Module {self.__class__.__name__} loaded')

    def cog_unload(self):
        self.webhook_task.cancel()  # pylint: disable=no-member

    async def webhook(self):
        async def webhook_handler(request):
            try:
                message_signature = request.headers.get('X-Patreon-Signature')
                data = await request.text()

                calculated_signature = hmac.new(b"ONSZFHWDM8Q4w02d97wiFZEPAqF0a5iQLrwpAbH7DacQHcEY9x5Rl2pcGIVVTZ85", data.encode(), hashlib.md5).hexdigest()
                if calculated_signature == message_signature:
                    event_type = request.headers.get('X-Patreon-Event')
                    json_data = await request.json()

                    user_id = None
                    patreon_tier = None
                    tiers = {"6232177": premiumhandler.PremiumTier.Standard, "6232178": premiumhandler.PremiumTier.Plus}

                    for snippet in json_data["included"]:
                        if snippet["type"] == "user":
                            user_id = int(snippet["attributes"]["social_connections"]["discord"]["user_id"])
                        elif snippet["type"] in ("reward", "tier"):
                            tier_id = snippet["id"]
                            patreon_tier = tiers.get(tier_id, None)

                    if patreon_tier is None:
                        if "currently_entitled_tiers" in json_data["data"]["relationships"]:
                            for tier in json_data["data"]["relationships"]["currently_entitled_tiers"]:
                                if tier["id"] in tiers:
                                    patreon_tier = tiers.get(tier["id"], None)
                                    break
                        else:
                            patreon_tier = tiers["6232177"]

                    if user_id:
                        if patreon_tier is not None and event_type in ("members:pledge:create", "members:pledge:update"):
                            await self.PremiumHandler.add_patreon_premium(user_id, patreon_tier)
                        elif event_type == "members:pledge:delete":
                            await self.PremiumHandler.end_premium(user_id)

                    return web.Response()
                else:
                    return web.Response(status=401)
            except Exception:
                pass

        web_app = web.Application(loop=self.bot.loop)

        cors = aiohttp_cors.setup(web_app, defaults={
            "https://www.patreon.com": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers=("Accept", "Content-Type", "X-Patreon-Event", "Origin", "X-Patreon-Signature",),
                max_age=3600,
            )
        })

        resource = cors.add(web_app.router.add_resource("/premium"))
        cors.add(resource.add_route("POST", webhook_handler))

        web_runner = web.AppRunner(web_app)
        await web_runner.setup()

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(os.path.join(bot_path, 'data', 'ssl', 'qubot.xyz.crt'), os.path.join(bot_path, 'data', 'ssl', 'qubot.xyz.key'))

        site = web.TCPSite(web_runner, host="0.0.0.0", port=5555, ssl_context=ssl_context)
        await site.start()

    @commands.group(cls=ExtendedGroup, name='premium', hidden=True, permissions=['Bot Owner'])
    @commands.guild_only()
    @commands.is_owner()
    async def premium_group(self, ctx):
        if not ctx.invoked_subcommand:
            pass

    @premium_group.command(cls=ExtendedCommand, name='add', description=main.lang["command_premium_add_description"], usage="<user> <tier> <period>", hidden=True, permissions=['Bot Owner'])
    @commands.guild_only()
    @commands.is_owner()
    async def premium_add(self, ctx, user: discord.User, tier, *, period: TimePeriod):
        tiers = {
            "standard": [premiumhandler.PremiumTier.Standard, "Premium"],
            "premium": [premiumhandler.PremiumTier.Standard, "Premium"],
            "plus": [premiumhandler.PremiumTier.Plus, "Premium Plus"],
            "premiumplus": [premiumhandler.PremiumTier.Plus, "Premium Plus"],
        }
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if tier.lower() in tiers.keys():
            user_premium_unix = await self.PremiumHandler.get_expiration(user.id)
            expiration_unix = int((user_premium_unix if user_premium_unix else datetime.utcnow().timestamp()) + period)
            expiration_time = datetime.fromtimestamp(expiration_unix, tz=timezone.utc)
            added = await self.PremiumHandler.add_limited_premium(user.id, expiration_unix, tiers[tier][0])
            if added:
                await ctx.send(embed=discord.Embed(title=lang["premium_add_success_title"],
                               description=lang["premium_add_success_desc"].format(str(user), expiration_time.strftime('%Y/%m/%d at %H:%M UTC'), tiers[tier][1]), color=self.embed_color))
            else:
                await ctx.send(lang["premium_add_failed"], delete_after=15)
        else:
            await ctx.send(lang["premium_tier_not_found"], delete_after=15)

    @premium_group.command(cls=ExtendedCommand, name='end', description=main.lang["command_premium_end_description"], usage="<user>", hidden=True, permissions=['Bot Owner'])
    @commands.guild_only()
    @commands.is_owner()
    async def premium_end(self, ctx, user: discord.User):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await self.PremiumHandler.end_premium(user.id)
        await ctx.send(embed=discord.Embed(title=lang["premium_end_success_title"], description=lang["premium_end_success_desc"].format(str(user)), color=self.embed_color))


def setup(bot):
    bot.add_cog(Premium(bot))
