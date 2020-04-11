from libs.qulib import user_get, user_set
from discord.ext import commands
from datetime import datetime
import datetime as dt
import libs.qulib as qulib
from main import config
import main
import configparser
import discord
import random

class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0x28b463
        print(f'Module {self.__class__.__name__} loaded')

        qulib.user_database_init()

        if 'Economy' not in config.sections():
            config.add_section('Economy')
            if 'CurrencySymbol' not in config['Economy']:
                config.set('Economy', 'CurrencySymbol', '💵')
            if 'DailyAmount' not in config['Economy']:
                config.set('Economy', 'DailyAmount', '100')
        
        with open('config.ini', 'w', encoding="utf_8") as config_file:
            config.write(config_file)
        config_file.close()

        with open('config.ini', 'r', encoding="utf_8") as config_file:
            config.read_file(config_file)
            self.daily_amount = int(config.get('Economy', 'DailyAmount'))
            self.currency_symbol = config.get('Economy', 'CurrencySymbol')
        config_file.close()

    @commands.cooldown(1, 30,commands.BucketType.user)
    @commands.command(name='daily', help=main.lang["command_daily_help"], description=main.lang["command_daily_description"], usage="@somebody (Optional Argument)")
    async def daily(self, ctx, *, user: discord.User = None):
        author_info = await user_get(ctx.author)
        user = user or ctx.author
        if user.id is not ctx.author.id:
            user_info = await user_get(user)
        time_on_command = datetime.today().replace(microsecond=0)
        if author_info['daily_time']:
            daily = datetime.strptime(author_info['daily_time'], '%Y-%m-%d %H:%M:%S')
            daily_active = daily + dt.timedelta(days=1)
            if time_on_command < daily_active:
                wait_time = daily_active - time_on_command
                embed = discord.Embed(
                    title=main.lang["economy_daily_claimed"].format(int(wait_time.seconds/3600), 
                                                                    int((wait_time.seconds/60)%60),
                                                                    int(wait_time.seconds%60)), 
                    color=self.module_embed_color)
                await ctx.send(embed=embed)
                return 
        if user.id is ctx.author.id:
            author_info['currency'] += self.daily_amount
            embed = discord.Embed(
                    title=main.lang["economy_daily_received"].format(user, self.daily_amount, self.currency_symbol),
                    color=self.module_embed_color)
        else:
            user_info['currency'] += self.daily_amount         
            await user_set(user, user_info)
            embed = discord.Embed(
                    title=main.lang["economy_daily_gifted"].format(ctx.author, self.daily_amount, self.currency_symbol, user),
                    color=self.module_embed_color)
        author_info['daily_time'] = time_on_command
        await user_set(ctx.author, author_info)
        await ctx.send(embed=embed)
    
    @commands.command(name="currency", help=main.lang["command_currency_help"], description=main.lang["command_currency_description"], usage="@somebody", aliases=['$', 'money','cash'])
    async def currency(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        user_info = await user_get(user)
        embed = discord.Embed(title=main.lang["economy_currency_return_msg"].format(user, user_info['currency'], self.currency_symbol), color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name="adjust", help=main.lang["command_adjust_help"], description=main.lang["command_adjust_description"],  usage="@somebody 100")
    @commands.is_owner()
    @commands.guild_only()
    async def adjust(self, ctx, user: discord.User, value: int):
        await ctx.message.delete()
        user_info = await user_get(user)
        user_info['currency'] += value
        await user_set(user,user_info)
        if value > 0:
            embed = discord.Embed(title=main.lang["economy_adjust_award_msg"].format(user, value, self.currency_symbol), color=self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["economy_adjust_subtract_msg"].format(user, abs(value), self.currency_symbol), color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name="give", help=main.lang["command_give_help"], description=main.lang["command_give_description"], usage="@somebody 50")
    @commands.guild_only()
    async def give(self, ctx, user: discord.User, number: int):
        author = ctx.author
        author_info = await user_get(author)
        user_info = await user_get(user)
        if number > 0:
            if author_info['currency'] <= 0 or number > author_info['currency']:
                embed = discord.Embed(title=main.lang["economy_insufficient_funds"], color=self.module_embed_color)
            elif author == user:
                embed = discord.Embed(title=main.lang["economy_give_self"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["economy_give_success"].format(author, user, number, self.currency_symbol), color=self.module_embed_color)
                author_info['currency'] -= number
                user_info['currency'] += number
                await user_set(author,author_info)
                await user_set(user,user_info)
            await ctx.send(embed=embed)

    @commands.command(name="broll", help=main.lang["command_betroll_help"], description=main.lang["command_betroll_description"], usage="50", aliases=['br', 'betroll'])
    async def bet_roll(self, ctx, number: int):
        user = ctx.author
        user_info = await user_get(user)
        if number > 0:
            if user_info['currency'] <= 0 or number > user_info['currency']:
                embed = discord.Embed(title=main.lang["economy_insufficient_funds"], color=self.module_embed_color)
            else:
                number_gen = random.randrange(0, 100)
                multiplier = 1
                if number_gen < 60:
                    embed = discord.Embed(title=main.lang["economy_betroll_fail_msg"].format(number_gen), color=self.module_embed_color)
                    multiplier = -1
                elif number_gen < 90:
                    embed = discord.Embed(title=main.lang["economy_betroll_msg"].format(number_gen, number, self.currency_symbol), color=self.module_embed_color)
                elif number_gen < 100:
                    multiplier = 4
                    embed = discord.Embed(title=main.lang["economy_betroll_msg"].format(number_gen, multiplier*number, self.currency_symbol), color=self.module_embed_color)
                else:
                    multiplier = 10
                    embed = discord.Embed(title=main.lang["economy_betroll_jackpot"].format(number_gen, multiplier*number, self.currency_symbol), color=self.module_embed_color)
                user_info['currency'] += multiplier*number
                await user_set(user, user_info)
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.author.id == self.bot.user.id and not user.bot:
            giveaways = await qulib.get_giveaway_list()
            if giveaways:
                if (reaction.message.id in giveaways):
                    if reaction.emoji == self.currency_symbol:
                        if await qulib.has_entered_giveaway(user.id, reaction.message.id) == False:
                            print("entered giveaway")
                            value = await qulib.get_giveaway_value(reaction.message.id)
                            if value:
                                await qulib.enter_giveaway(user.id, reaction.message.id)
                                user_info = await user_get(user)
                                user_info['currency'] += value
                                await user_set(user, user_info)

    @commands.is_owner()
    @commands.guild_only()
    @commands.group(name="giveaway", help=main.lang["empty_string"], description=main.lang["command_giveaway_group_description"])
    async def giveaway_group(self, ctx):
        if not ctx.invoked_subcommand:
            pass

    @giveaway_group.command(name="start", help=main.lang["command_owner_only"], description=main.lang["command_giveaway_start_description"], usage=100)
    async def giveaway_start(self, ctx, value: int):
        await ctx.message.delete()
        embed = discord.Embed(title="Currency Giveaway", description=f"React with {self.currency_symbol} to this message to claim **{value} {self.currency_symbol}**", color=self.module_embed_color)
        message = await ctx.send(embed=embed)
        await message.add_reaction(self.currency_symbol)
        await qulib.start_giveaway(message.id, value)

    @giveaway_group.command(name="end", help=main.lang["command_owner_only"], description=main.lang["command_giveaway_end_description"])
    async def giveaway_end(self, ctx, *, message_id: int):
        await ctx.message.delete()
        result = await qulib.end_giveaway(message_id)
        if result:
            message = await ctx.channel.fetch_message(message_id)
            await ctx.channel.delete_messages([message])

def setup(bot):
    bot.add_cog(Economy(bot))