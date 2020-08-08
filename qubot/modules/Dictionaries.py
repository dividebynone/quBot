from discord.ext import commands
from main import bot_starttime
from main import modules as loaded_modules
from libs.qudict import quDict
import main
import discord
import random

class Dictionaries(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0x80e093
        print(f'Module {self.__class__.__name__} loaded')

    @commands.command(name='dict', help=main.lang["dictionaries_english_only"], description=main.lang["command_meanings_description"], aliases=['whatis', 'meaning', 'meanings'])
    @commands.is_nsfw()
    async def dictionary_getmeanings(self, ctx, *, input: str):
        result = await quDict.get_top_meanings(input)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if result != None:
            embed = discord.Embed(title=lang["dictionaries_term"].format(input), color=self.module_embed_color)
            for category in result:
                meanings = ""
                for item in result[category]:
                    meanings += f"- {item};\n"
                embed.add_field(name=f"**{category}**", value=meanings, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(lang["dictionaries_word_not_found"])

    @commands.command(name='synonym', help=main.lang["dictionaries_english_only"], description=main.lang["command_synonyms_description"], usage="hot", aliases=['synonyms'])
    @commands.is_nsfw()
    async def dictionary_getsynonyms(self, ctx, *, input: str):
        result = await quDict.get_top_synonyms(input)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if result != None:
            embed = discord.Embed(title=lang["dictionaries_term"].format(input), color=self.module_embed_color)
            formatted = ', '.join(result)
            embed.add_field(name=lang["dictionaries_synonyms"], value=formatted, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(lang["dictionaries_word_not_found"])

    @commands.command(name='antonym', help=main.lang["dictionaries_english_only"], description=main.lang["command_antonyms_description"], usage="hot", aliases=['antonyms'])
    @commands.is_nsfw()
    async def dictionary_getantonyms(self, ctx, *, input: str):
        result = await quDict.get_top_antonyms(input)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if result != None:
            embed = discord.Embed(title=lang["dictionaries_term"].format(input), color=self.module_embed_color)
            formatted = ', '.join(result)
            embed.add_field(name=lang["dictionaries_antonyms"], value=formatted, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(lang["dictionaries_word_not_found"])

    @commands.command(name='urbandict', help=main.lang["dictionaries_english_only"], description=main.lang["command_urbandict_description"], usage="hello", aliases=['ud'])
    @commands.is_nsfw()
    async def dictionary_get_urbandict(self, ctx, *, input: str):
        result = await quDict.get_urbandict_definitions(input)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if result != None:
            embed = discord.Embed(title=lang["dictionaries_term"].format(input), color=self.module_embed_color)
            formatted = '\n'.join(result)
            embed.add_field(name=lang["dictionaries_urbandict_title"], value=formatted, inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(lang["dictionaries_word_not_found"])

def setup(bot):
    bot.add_cog(Dictionaries(bot))