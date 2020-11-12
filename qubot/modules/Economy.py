from libs.qulib import user_get, user_set, ExtendedCommand, ExtendedGroup
from libs.giveaways import GiveawayHandler
from main import bot_path
from discord.ext import commands
from datetime import datetime
import datetime as dt
import libs.qulib as qulib
from main import config
import main
import discord
import asyncio
import random
import os


class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.embed_color = 0x28b463

        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = False
        self.module_dependencies = []

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)

        qulib.user_database_init()

        self.GiveawayHandler = GiveawayHandler()

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

        print(f'Module {self.__class__.__name__} loaded')

    @commands.cooldown(5, 60, commands.BucketType.user)
    @commands.command(name='daily', help=main.lang["command_daily_help"], description=main.lang["command_daily_description"], usage="{user}")
    async def daily(self, ctx, *, user: discord.User = None):
        author_info = await user_get(ctx.author.id)
        user = user or ctx.author
        if user.id is not ctx.author.id:
            user_info = await user_get(user.id)
        time_on_command = datetime.utcnow().replace(microsecond=0)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if author_info['daily_time']:
            daily = datetime.strptime(author_info['daily_time'], '%Y-%m-%d %H:%M:%S')
            daily_active = daily + dt.timedelta(days=1)
            if time_on_command < daily_active:
                await ctx.send(embed=discord.Embed(title=lang["economy_daily_claimed_title"],
                               description=lang["economy_daily_claimed_description"].format(f'**{qulib.humanize_time(lang, daily_active)}**'),
                               color=self.embed_color))
                return
        if user.id is ctx.author.id:
            author_info['currency'] += self.daily_amount
            embed = discord.Embed(title=lang["economy_daily_received"].format(user, self.daily_amount, self.currency_symbol), color=self.embed_color)
        else:
            user_info['currency'] += self.daily_amount
            await user_set(user.id, user_info)
            embed = discord.Embed(title=lang["economy_daily_gifted"].format(ctx.author, self.daily_amount, self.currency_symbol, user), color=self.embed_color)
        author_info['daily_time'] = time_on_command
        await user_set(ctx.author.id, author_info)
        await ctx.send(embed=embed)

    @commands.command(name="currency", help=main.lang["command_currency_help"], description=main.lang["command_currency_description"], usage="{user}", aliases=['$', 'money', 'cash', 'balance'])
    async def currency(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        user_info = await user_get(user.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ctx.send(embed=discord.Embed(title=lang["economy_currency_msg"].format(user, user_info['currency'], self.currency_symbol), color=self.embed_color))

    @commands.command(cls=ExtendedCommand, name="adjust", description=main.lang["command_adjust_description"], usage="<amount> <user>", permissions=['Bot Owner'])
    @commands.is_owner()
    @commands.guild_only()
    async def adjust(self, ctx, value: int, *, user: discord.User):
        await ctx.message.delete()
        user_info = await user_get(user.id)
        user_info['currency'] += value
        await user_set(user.id, user_info)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if value > 0:
            embed = discord.Embed(title=lang["economy_adjust_award_msg"].format(user, value, self.currency_symbol), color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["economy_adjust_subtract_msg"].format(user, abs(value), self.currency_symbol), color=self.embed_color)
        await ctx.send(embed=embed)

    @commands.command(name="give", description=main.lang["command_give_description"], usage="<amount> <user>")
    @commands.guild_only()
    async def give(self, ctx, amount, *, user: discord.User):
        author = ctx.author
        author_info = await user_get(author.id)
        user_info = await user_get(user.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if author != user:
            try:
                amount = int(amount)
                if amount > 0:
                    if author_info['currency'] <= 0 or amount > author_info['currency']:
                        await ctx.send(lang["economy_insufficient_funds"], delete_after=15)
                        return
                else:
                    raise commands.UserInputError("This command accepts only positive values.")
            except ValueError:
                if isinstance(amount, str) and amount.lower() == "all":
                    amount = author_info['currency']
                else:
                    raise commands.UserInputError(f"Invalid user input provided to the command '{ctx.command.qualified_name}'.")          

            author_info['currency'] -= amount
            user_info['currency'] += amount
            await user_set(author.id, author_info)
            await user_set(user.id, user_info)
            await ctx.send(embed=discord.Embed(title=lang["economy_give_success"].format(author, user, amount, self.currency_symbol), color=self.embed_color))
        else:
            await ctx.send(lang["economy_give_self"], delete_after=15)

    @commands.command(name="roulette", description=main.lang["command_betroll_description"], usage="<amount>", aliases=['br', 'betroll', 'broll'])
    async def roulette(self, ctx, number: int):
        user = ctx.author
        user_info = await user_get(user.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if number > 0:
            if user_info['currency'] <= 0 or number > user_info['currency']:
                embed = discord.Embed(title=lang["economy_insufficient_funds"], color=self.embed_color)
            else:
                random.seed()
                number_gen = random.randrange(0, 100)
                multiplier = 1
                if number_gen < 60:
                    embed = discord.Embed(title=lang["economy_betroll_fail_msg"].format(number_gen), color=self.embed_color)
                    multiplier = -1
                elif number_gen < 90:
                    embed = discord.Embed(title=lang["economy_betroll_msg"].format(number_gen, number, self.currency_symbol), color=self.embed_color)
                elif number_gen < 100:
                    multiplier = 4
                    embed = discord.Embed(title=lang["economy_betroll_msg"].format(number_gen, multiplier * number, self.currency_symbol), color=self.embed_color)
                else:
                    multiplier = 10
                    embed = discord.Embed(title=lang["economy_betroll_jackpot"].format(number_gen, multiplier * number, self.currency_symbol), color=self.embed_color)
                user_info['currency'] += multiplier * number
                await user_set(user.id, user_info)
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_raw_reaction_add(self, payload):
        try:
            user = await self.bot.fetch_user(payload.user_id)
            channel = await self.bot.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            if not [x for x in (user, channel, message) if x is None]:
                if message.author.id == self.bot.user.id and not user.bot:
                    giveaways = await GiveawayHandler.get_giveaway_list()
                    if giveaways:
                        if message.id in giveaways:
                            if payload.emoji.name == self.currency_symbol:
                                if await GiveawayHandler.has_entered_giveaway(user.id, message.id) == False:
                                    value = await GiveawayHandler.get_giveaway_value(message.id)
                                    if value:
                                        await GiveawayHandler.enter_giveaway(user.id, message.id)
                                        user_info = await user_get(user.id)
                                        user_info['currency'] += value
                                        await user_set(user.id, user_info)
        except discord.errors.Forbidden:
            pass

    @commands.group(cls=ExtendedGroup, name="giveaway", description=main.lang["command_giveaway_group_description"], permissions=['Bot Owner'])
    @commands.guild_only()
    @commands.is_owner()
    async def giveaway_group(self, ctx):
        if not ctx.invoked_subcommand:
            pass

    @giveaway_group.command(cls=ExtendedCommand, name="start", description=main.lang["command_giveaway_start_description"], usage="<amount>", permissions=['Bot Owner'])
    async def giveaway_start(self, ctx, value: int):
        await ctx.message.delete()
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        embed = discord.Embed(title=lang["economy_cgiveaway_title"], description=lang["economy_cgiveaway_msg"].format(self.currency_symbol, value, self.currency_symbol), color=self.embed_color)
        message = await ctx.send(embed=embed)
        await message.add_reaction(self.currency_symbol)
        await GiveawayHandler.start_giveaway(message.id, value)

    @giveaway_group.command(cls=ExtendedCommand, name="end", description=main.lang["command_giveaway_end_description"], usage="<message id>", permissions=['Bot Owner'])
    async def giveaway_end(self, ctx, *, message_id: int):
        await ctx.message.delete()
        result = await GiveawayHandler.end_giveaway(message_id)
        if result:
            message = await ctx.channel.fetch_message(message_id)
            await ctx.channel.delete_messages([message])

    @commands.command(name='duel', description=main.lang["command_duel_description"], usage="<amount> <user>")
    @commands.guild_only()
    async def economy_duel(self, ctx, number: int, *, user: discord.User):
        if number > 0:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if ctx.author.id != user.id:
                author_info = await user_get(ctx.author.id)
                target_info = await user_get(user.id)
                if number <= author_info['currency']:
                    if number <= target_info['currency']:
                        await ctx.send(embed=discord.Embed(title=lang["economy_duel_confirm_title"],
                                       description=lang["economy_duel_confirm_description"].format("\U0001F94A", user.mention, ctx.author.mention, number, self.currency_symbol),
                                       color=self.embed_color))
                        try:
                            msg = await self.bot.wait_for('message', check=lambda m: (m.content.lower() in ['yes', 'y', 'no', 'n']) and m.channel == ctx.channel and m.author == user, timeout=120.0)
                            if msg.content.lower() == 'yes' or msg.content.lower() == 'y':
                                random.seed()
                                result = random.randint(0, 1)
                                if result == 0:
                                    # Opponent wins
                                    author_info['currency'] -= number
                                    target_info['currency'] += number
                                    embed = discord.Embed(description=lang["economy_duel_result"].format("\U0001F3C6", user.mention, number, self.currency_symbol), color=self.embed_color)
                                else:
                                    # Author wins
                                    author_info['currency'] += number
                                    target_info['currency'] -= number
                                    embed = discord.Embed(description=lang["economy_duel_result"].format("\U0001F3C6", ctx.author.mention, number, self.currency_symbol), color=self.embed_color)
                                await user_set(ctx.author.id, author_info)
                                await user_set(user.id, target_info)
                                await ctx.send(embed=embed)
                            else:
                                await ctx.send(lang["economy_duel_cancel"].format(ctx.author.mention, str(user)))
                        except asyncio.TimeoutError:
                            await ctx.send(lang["economy_duel_timeout"].format(ctx.author.mention))
                    else:
                        await ctx.send(lang["economy_duel_target_no_funds"].format(ctx.author.mention))
                else:
                    await ctx.send(lang["economy_duel_author_no_funds"].format(ctx.author.mention))
            else:
                await ctx.send(lang["economy_duel_duel_self"].format(ctx.author.mention))


def setup(bot):
    bot.add_cog(Economy(bot))
