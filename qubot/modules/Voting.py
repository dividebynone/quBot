from discord.ext import tasks, commands
from main import bot_path, config
import libs.qulib as qulib
import libs.votingtracker as votingtracker
import libs.premiumhandler as premiumhandler
from aiohttp import web
from datetime import datetime, timedelta, timezone
import aiohttp_cors
import configparser
import requests
import discord
import main
import time
import dbl  # noqa: F401
import ssl
import os


class Voting(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.embed_color = 0xffd426

        self.VotingTracker = votingtracker.VotingTracker()
        self.PremiumHandler = premiumhandler.PremiumHandler()

        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = True
        self.module_dependencies = ['Economy']

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)

        # Main Config.ini Configuration
        if 'Economy' not in config.sections():
            config.add_section('Economy')
            if 'CurrencySymbol' not in config['Economy']:
                config.set('Economy', 'CurrencySymbol', '💵')
            if 'DailyAmount' not in config['Economy']:
                config.set('Economy', 'DailyAmount', '100')

        with open(os.path.join(bot_path, 'config.ini'), 'w', encoding="utf_8") as config_file:
            config.write(config_file)
        config_file.close()

        with open(os.path.join(bot_path, 'config.ini'), 'r', encoding="utf_8") as config_file:
            config.read_file(config_file)
            self.vote_reward = int(int(config.get('Economy', 'DailyAmount')) / 2)
            self.currency_symbol = config.get('Economy', 'CurrencySymbol')
        config_file.close()

        # Voting.ini Configuration
        voting_config = configparser.ConfigParser(allow_no_value=False)
        voting_config.optionxform = str

        if not os.path.isfile(os.path.join(bot_path, 'voting.ini')):
            voting_config['TopGG'] = {'Token': '<token here>', 'WeebhookAuth': '<auth key here>'}
            voting_config['DiscordBotList'] = {'Token': '<token here>', 'WeebhookAuth': '<auth key here>'}

            with open(os.path.join(bot_path, 'voting.ini'), 'w', encoding="utf_8") as config_file:
                voting_config.write(config_file)
                config_file.close()
                print("Successfully created voting.ini file. Please configure the file before loading in the module again.")
                self.bot.unload_extension(f'modules.{self.module_name}')
        else:
            with open(os.path.join(bot_path, 'voting.ini'), 'r', encoding="utf_8") as config_file:
                voting_config.read_file(config_file)
                self.topgg_token = voting_config.get('TopGG', 'Token')
                self.topgg_webhook_auth = voting_config.get('TopGG', 'WeebhookAuth')
                self.dbl_token = voting_config.get('DiscordBotList', 'Token')
                self.dbl_webhook_auth = voting_config.get('DiscordBotList', 'WeebhookAuth')
                config_file.close()

        # self.dblpy = dbl.DBLClient(self.bot, self.token, webhook_path='/dblwebhook', webhook_auth=self.webhook_auth, webhook_port=5000, autopost=True) # Autopost will post your guild count every 30 minutes

        self.webhook_task = self.bot.loop.create_task(self.webhook())
        self.dbl_update_stats.start()  # pylint: disable=no-member

        print(f'Module {self.__class__.__name__} loaded')

    def cog_unload(self):
        self.webhook_task.cancel()  # pylint: disable=no-member

    # @tasks.loop(minutes=30.0)
    # async def update_stats(self):
    #     main.logger.info('Attempting to post server count')
    #     try:
    #         await self.dblpy.post_guild_count()
    #         main.logger.info('Posted server count ({}) on TopGG'.format(self.dblpy.guild_count()))
    #     except Exception as e:
    #         main.logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

    @tasks.loop(minutes=30.0)
    async def dbl_update_stats(self):
        try:
            shards_guild_counter = 0
            for shard in self.bot.latencies:
                guild_list = (g for g in self.bot.guilds if g.shard_id is shard[0])
                for _ in guild_list:
                    shards_guild_counter += 1

            app_info = await self.bot.application_info()
            url = f'https://discordbotlist.com/api/v1/bots/{app_info.id}/stats'
            headers = {'Authorization': self.dbl_token}
            requests.post(url, headers=headers, data={'guilds': shards_guild_counter}, verify=True)
            main.logger.info('Posted server count ({}) on discordbotlist.com'.format(shards_guild_counter))
        except Exception as e:
            main.logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        main.logger.info('[TOP.GG] Bot received an upvote!')
        try:
            user = self.bot.get_user(int(data['user']))
            if user is not None:
                isWeekend = bool(data['isWeekend'])
                reward = int(self.vote_reward * 2) if isWeekend else self.vote_reward

                voting_info, vote_multiplier, premium_multiplier = await self.vote_handler(user.id, reward)
                if voting_info:
                    await user.send(embed=discord.Embed(title=main.lang["voting_user_vote_embed_title"], description=main.lang["voting_user_vote_embed_description"].format("top.gg", int(reward * vote_multiplier * premium_multiplier), self.currency_symbol, voting_info['combo']), color=self.embed_color))
        except Exception:
            pass

    async def webhook(self):
        async def webhook_handler(request):
            try:
                req_auth = request.headers.get('Authorization')
                if self.dbl_webhook_auth == req_auth.strip():
                    main.logger.info('[Discordbotlist.com] Bot received an upvote!')
                    data = await request.json()
                    user = self.bot.get_user(int(data['id']))
                    if user is not None:
                        voting_info, vote_multiplier, premium_multiplier = await self.vote_handler(user.id, self.vote_reward)
                        if voting_info:
                            await user.send(embed=discord.Embed(title=main.lang["voting_user_vote_embed_title"],
                                                                description=main.lang["voting_user_vote_embed_description"].format("discordbotlist.com", int(self.vote_reward * vote_multiplier * premium_multiplier), self.currency_symbol, voting_info['combo']),
                                                                color=self.embed_color))
                            return web.Response()
                else:
                    return web.Response(status=401)
            except Exception:
                pass

        web_app = web.Application(loop=self.bot.loop)

        cors = aiohttp_cors.setup(web_app, defaults={
            "https://discordbotlist.com": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers=("Accept", "Authorization", "Content-Type", "X-DBL-Signature", "Origin", "X-Requested-With",),
                max_age=3600,
            )
        })

        resource = cors.add(web_app.router.add_resource("/discordbotlist"))
        cors.add(resource.add_route("POST", webhook_handler))

        web_runner = web.AppRunner(web_app)
        await web_runner.setup()

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(os.path.join(bot_path, 'data', 'ssl', 'qubot.xyz.crt'), os.path.join(bot_path, 'data', 'ssl', 'qubot.xyz.key'))

        site = web.TCPSite(web_runner, host="0.0.0.0", port=5050, ssl_context=ssl_context)
        await site.start()

    async def vote_handler(self, user_id: int, vote_amount: int):
        try:
            voting_info = await self.VotingTracker.get_user(user_id)
            user_info = await qulib.user_get(user_id)
            if None not in (voting_info, user_info):
                unix_now = int(time.time())
                vote_multiplier = 1
                if voting_info['last_voted'] is not None:
                    timestamp_now = datetime.fromtimestamp(unix_now, tz=timezone.utc)
                    last_voted_timestamp = datetime.fromtimestamp(voting_info['last_voted'], tz=timezone.utc) + timedelta(days=2)
                    if last_voted_timestamp >= timestamp_now:
                        if voting_info['combo'] < 3:
                            vote_multiplier = 1.5
                        elif voting_info['combo'] < 6:
                            vote_multiplier = 2
                        else:
                            vote_multiplier = 2.5
                    else:
                        voting_info['combo'] = 0

                premium_tier = await self.PremiumHandler.get_tier(user_id)
                premium_multiplier = 1
                if premium_tier:
                    if premium_tier == premiumhandler.PremiumTier.Standard:
                        premium_multiplier = 1.5
                    elif premium_tier == premiumhandler.PremiumTier.Plus:
                        premium_multiplier = 2.0

                user_info['currency'] += int(vote_amount * vote_multiplier * premium_multiplier)
                voting_info['combo'] += 1
                voting_info['last_voted'] = unix_now
                await self.VotingTracker.update_user(user_id, voting_info)
                await qulib.user_set(user_id, user_info)
                return voting_info, vote_multiplier, premium_multiplier
            return None
        except Exception:
            raise


def setup(bot):
    bot.add_cog(Voting(bot))
