from discord.ext import commands
from datetime import datetime
from main import lang, config
import libs.qulib as qulib
import configparser
import secrets
import discord
import sys

rand_generator = secrets.SystemRandom()

class Conquest(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0xd59c6d
        print(f'Module {self.__class__.__name__} loaded')

        qulib.conquest_database_init()

        if 'Conquest' not in config.sections():
            config.add_section('Conquest')
            if 'MinEntryFee' not in config['Conquest']:
                config.set('Conquest', 'MinEntryFee', '100')
     
        with open('config.ini', 'w', encoding="utf_8") as config_file:
            config.write(config_file)
        config_file.close()

        with open('config.ini', 'r', encoding="utf_8") as config_file:
            config.read_file(config_file)
            self.minetryfee = int(config.get('Conquest', 'MinEntryFee'))
        config_file.close()

    @commands.command(name='ccreate', aliases=['cc'])
    async def ccreate(self, ctx, s_name:str = None, set_type:str = None, entry_fee:int = None):
        user = ctx.author
        if None in {s_name,set_type,entry_fee}:
            embed = discord.Embed(title=lang["conquest_create_args"], color = self.module_embed_color)
        else:
            cdata = await qulib.conquest_get('user', user.id)
            if not cdata:
                if entry_fee < self.minetryfee:
                    embed = discord.Embed(title=lang["conquest_entry_requirement"], color = self.module_embed_color)
                else:
                    await qulib.user_init(user)
                    user_data = await qulib.user_get(user)
                    if user_data["currency"] < entry_fee:
                        embed = discord.Embed(title=lang["conquest_insufficient_funds"], color = self.module_embed_color)
                    elif set_type in ('public', 'private'):
                        temp_invite_string = qulib.string_generator(15)
                        cinvite_data = await qulib.conquest_get('code', temp_invite_string)
                        if cinvite_data:
                            while temp_invite_string is cinvite_data["invite_string"]:
                                temp_invite_string = qulib.string_generator(15)
                                cinvite_data = await qulib.conquest_get('code', temp_invite_string)
                        member_list = []
                        member_list.append(str(user.id))

                        dict_input = {}
                        dict_input["entry_fee"] = entry_fee
                        dict_input["invite_string"] = temp_invite_string
                        dict_input["date_created"] = datetime.today().replace(microsecond=0)
                        dict_input["settlement_name"] = s_name
                        dict_input["settlement_type"] = set_type
                        dict_input["member_list"] = member_list

                        user_data["currency"] -= entry_fee
                        await qulib.user_set(user,user_data)
                        await qulib.conquest_set('new', user.id, dict_input)
                        embed = discord.Embed(title=lang["conquest_create_success"], color = self.module_embed_color)
                    else:
                        embed = discord.Embed(title=lang["conquest_create_args"], color = self.module_embed_color)
            else:
                  embed = discord.Embed(title=lang["conquest_create_already_has"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name='cinfo', aliases=['ci'])
    async def cinfo(self, ctx, *, s_name: str = None):
        if s_name:
            cdata = await qulib.conquest_get('settlement', s_name)
            json_data = await qulib.data_get()
            if cdata:
                founder_name = ctx.guild.get_member(cdata["founderid"]) or cdata["founderid"]
                if cdata["settlement_wins"] == cdata["settlement_losses"] == 0:
                    win_ratio = 0
                elif cdata["settlement_wins"] > 0 and cdata["settlement_losses"] is 0:
                    win_ratio = 100
                elif cdata["settlement_losses"] > 0 and cdata["settlement_wins"] is 0:
                    win_ratio = 0
                else:
                    win_ratio = "%.2f" % float((cdata["settlement_wins"]/(cdata["settlement_losses"]+cdata["settlement_wins"]))*100)
                
                embed = discord.Embed(title=lang["conquest_info_info"], color=self.module_embed_color)
                embed.add_field(name=lang["conquest_info_name"], value=cdata["settlement_name"],inline=True)
                embed.set_thumbnail(url=json_data["Conquest"]["settlement_image_1"])
                embed.add_field(name=lang["conquest_info_founder"], value=founder_name, inline=True)
                embed.add_field(name=lang["conquest_info_created"], value=cdata["date_created"], inline=True)
                embed.add_field(name=lang["conquest_info_population"], value=cdata["settlement_size"], inline=True)
                embed.add_field(name=lang["conquest_info_treasury"], value=cdata["treasury"], inline=True)
                embed.add_field(name=lang["conquest_info_type"], value =cdata["settlement_type"], inline = True)
                embed.add_field(name=lang["conquest_info_level"], value =cdata["settlement_level"], inline = False)
                embed.add_field(name=lang["conquest_info_wins_losses"], value =f'```{lang["conquest_wins"]}: {cdata["settlement_wins"]} | {lang["conquest_losses"]}: {cdata["settlement_losses"]} ({win_ratio}% {lang["conquest_info_win_ratio"]})```', inline = True)
            else:
                embed = discord.Embed(title=lang["conquest_info_fail"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["conquest_info_args"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name='cjoin', aliases=['cj'])
    async def cjoin(self, ctx, invite_code:str = None, join_fee:int = None):
        user = ctx.author
        if None in {invite_code, join_fee}:
            embed = discord.Embed(title=lang["conquest_join_args"], color = self.module_embed_color)
        else:
            await qulib.user_init(user)
            user_info = await qulib.user_get(user)
            cdata = await qulib.conquest_get('code', invite_code)
            if cdata:
                member_list = cdata["member_list"].split(',')
                if isinstance(member_list, str):
                    member_list = [cdata["member_list"]]
                if join_fee < cdata["entry_fee"]:
                    embed = discord.Embed(title=lang["conquest_join_min_entry"], color = self.module_embed_color)
                elif user_info["currency"] < join_fee:
                    embed = discord.Embed(title=lang["conquest_insufficient_funds"], color = self.module_embed_color)
                elif str(user.id) in member_list:
                    embed = discord.Embed(title=lang["conquest_join_part_of"], color = self.module_embed_color)
                else:
                    member_list.append(str(user.id))
                    cdata["member_list"] = member_list
                    cdata["settlement_size"] += 1
                    cdata["treasury"] += join_fee
                    user_info["currency"] -= join_fee
                    await qulib.user_set(user, user_info)
                    await qulib.conquest_set('invite', invite_code, cdata)
                    embed = discord.Embed(title=lang["conquest_join_success"].format(cdata["settlement_name"]), color = self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["conquest_join_not_found"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(ignore_extra=True)
    async def ccode(self, ctx):
        user = ctx.author
        cdata = await qulib.conquest_get('user', user.id)
        if cdata and user.id in {cdata["founderid"],cdata["leaderid"]}:
            embed = discord.Embed(title= lang["conquest_code_success"].format(cdata["invite_string"]), color=0x4e4eb7)     
        else:
            embed = discord.Embed(title= lang["conquest_code_fail"].format(cdata["invite_string"]), color=0x4e4eb7)    
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Conquest(bot))