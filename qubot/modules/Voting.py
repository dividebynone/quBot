from discord.ext import tasks, commands
from main import bot_path, config
import libs.qulib as qulib
from aiohttp import web
import aiohttp_cors
import configparser
import requests
import discord
import main
import dbl
import ssl
import os

class Voting(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.embed_color = 0xffd426

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
            self.daily_amount = int(config.get('Economy', 'DailyAmount'))
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
        
        self.bot.loop.create_task(self.webhook())
        self.dbl_update_stats.start() # pylint: disable=no-member

    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        main.logger.info('Attempting to post server count')
        # try:
        #     await self.dblpy.post_guild_count()
        #     main.logger.info('Posted server count ({}) on TopGG'.format(self.dblpy.guild_count()))
        # except Exception as e:
        #     main.logger.exception('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

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
                user_info = await qulib.user_get(user)
                isWeekend = bool(data['isWeekend'])
                reward = self.daily_amount if isWeekend else int(self.daily_amount/2)
                user_info['currency'] += reward
                await qulib.user_set(user, user_info)
                embed = discord.Embed(title=f"Thank you for supporting this bot on Top.GG\nAs a reward, you were given {reward} {self.currency_symbol}", color = self.embed_color)
                await user.send(embed=embed)
        except Exception:
            pass

    async def webhook(self):
        async def vote_handler(request):
            try:
                req_auth = request.headers.get('Authorization')
                if self.dbl_webhook_auth == req_auth.strip():
                    main.logger.info('[Discordbotlist.com] Bot received an upvote!')
                    data = await request.json()
                    user = self.bot.get_user(int(data['id']))
                    if user is not None:
                        user_info = await qulib.user_get(user)
                        user_info['currency'] += self.daily_amount
                        await qulib.user_set(user, user_info)
                        embed = discord.Embed(title=f"Thank you for supporting this bot on discordbotlist.com\nAs a reward, you were given {self.daily_amount} {self.currency_symbol}", color = self.embed_color)
                        await user.send(embed=embed)
                    return web.Response()
                else:
                    return web.Response(status=401)
            except Exception:
                raise

        web_app = web.Application(loop=self.bot.loop)

        cors = aiohttp_cors.setup(web_app, defaults={
                "https://discordbotlist.com": aiohttp_cors.ResourceOptions (
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers=("Accept", "Authorization", "Content-Type", "X-DBL-Signature", "Origin", "X-Requested-With",),
                    max_age=3600,
                )
            })

        resource = cors.add(web_app.router.add_resource("/discordbotlist"))
        cors.add(resource.add_route("POST", vote_handler))

        web_runner = web.AppRunner(web_app)
        await web_runner.setup()

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(os.path.join(bot_path, 'data', 'ssl', 'qubot.xyz.crt'), os.path.join(bot_path, 'data', 'ssl', 'qubot.xyz.key'))

        site = web.TCPSite(web_runner, host="0.0.0.0", port=5050, ssl_context=ssl_context)
        await site.start()

    @commands.command(name='vote', help="You can vote for the bot only every 12 hours.", description="Gives more information about bot voting.", ignore_extra=True)
    async def topgg_vote(self, ctx):
        embed = discord.Embed(title=f"Voting:", description=f"**Discordbotlist.com:** [Click here](https://discordbotlist.com/bots/qubot/upvote) (24 hour cooldown)\n\n**Voting Rewards:**\n \
            Voting will give you the following currency reward:\n• **Discordbotlist.com** - {self.daily_amount}** {self.currency_symbol}", color = self.embed_color)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Voting(bot))
