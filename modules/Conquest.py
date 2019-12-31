from discord.ext import commands
from datetime import datetime
from main import config
import libs.qulib as qulib
import configparser
import secrets
import discord
import math
import main
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

    @commands.command(name='ccreate', help=main.lang["command_ccreate_help"], description=main.lang["command_ccreate_description"], usage='"My Settlement Name" <public/private> 100', aliases=['cc'])
    async def ccreate(self, ctx, s_name:str = None, set_type:str = None, entry_fee:int = None):
        user = ctx.author
        if None in {s_name,set_type,entry_fee}:
            embed = discord.Embed(title=main.lang["conquest_create_args"], color = self.module_embed_color)
        else:
            if set_type.lower() in ('public', 'private'):
                cdata = await qulib.conquest_get('user', user.id)
                if not cdata:
                    if entry_fee < self.minetryfee:
                        embed = discord.Embed(title=main.lang["conquest_entry_requirement"], color = self.module_embed_color)
                    else:
                        await qulib.user_init(user)
                        user_data = await qulib.user_get(user)
                        if user_data["currency"] < entry_fee:
                            embed = discord.Embed(title=main.lang["conquest_insufficient_funds"], color = self.module_embed_color)
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
                            embed = discord.Embed(title=main.lang["conquest_create_success"], color = self.module_embed_color)
                        else:
                            embed = discord.Embed(title=main.lang["conquest_create_args"], color = self.module_embed_color)
                else:
                    embed = discord.Embed(title=main.lang["conquest_create_already_has"], color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_create_public_private"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name='cinfo', help=main.lang["command_cinfo_help"], description=main.lang["command_cinfo_description"], usage='<Settlement Name>', aliases=['ci'])
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
                
                embed = discord.Embed(title=main.lang["conquest_info_info"], color=self.module_embed_color)
                embed.add_field(name=main.lang["conquest_info_name"], value=cdata["settlement_name"],inline=True)
                embed.set_thumbnail(url=json_data["Conquest"]["settlement_image_1"])
                embed.add_field(name=main.lang["conquest_info_founder"], value=founder_name, inline=True)
                embed.add_field(name=main.lang["conquest_info_created"], value=cdata["date_created"], inline=True)
                embed.add_field(name=main.lang["conquest_info_population"], value=cdata["settlement_size"], inline=True)
                embed.add_field(name=main.lang["conquest_info_treasury"], value=cdata["treasury"], inline=True)
                embed.add_field(name=main.lang["conquest_info_type"], value =cdata["settlement_type"], inline = True)
                embed.add_field(name=main.lang["conquest_info_level"], value =cdata["settlement_level"], inline = False)
                embed.add_field(name=main.lang["conquest_info_wins_losses"],
                                value =f'```{main.lang["conquest_wins"]}: {cdata["settlement_wins"]} | {main.lang["conquest_losses"]}: {cdata["settlement_losses"]} ({win_ratio}% {main.lang["conquest_info_win_ratio"]})```',
                                inline = True)
            else:
                embed = discord.Embed(title=main.lang["conquest_info_fail"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_info_args"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name='cjoin', help=main.lang["command_cjoin_help"], description=main.lang["command_cjoin_description"], usage='<invite code> <entry fee>', aliases=['cj'])
    async def cjoin(self, ctx, invite_code:str = None, join_fee:int = None):
        user = ctx.author
        if None in {invite_code, join_fee}:
            embed = discord.Embed(title=main.lang["conquest_join_args"], color = self.module_embed_color)
        else:
            await qulib.user_init(user)
            user_info = await qulib.user_get(user)
            cdata = await qulib.conquest_get('code', invite_code)
            if cdata:
                member_list = cdata["member_list"].split(',')
                if isinstance(member_list, str):
                    member_list = [cdata["member_list"]]
                if join_fee < cdata["entry_fee"]:
                    embed = discord.Embed(title=main.lang["conquest_join_min_entry"].format(cdata["entry_fee"]), color = self.module_embed_color)
                elif user_info["currency"] < join_fee:
                    embed = discord.Embed(title=main.lang["conquest_insufficient_funds"], color = self.module_embed_color)
                elif str(user.id) in member_list:
                    embed = discord.Embed(title=main.lang["conquest_join_part_of"], color = self.module_embed_color)
                else:
                    member_list.append(str(user.id))
                    member_list = ",". join(member_list)
                    cdata["member_list"] = member_list
                    cdata["settlement_size"] += 1
                    cdata["treasury"] += join_fee
                    user_info["currency"] -= join_fee
                    await qulib.user_set(user, user_info)
                    await qulib.conquest_set('invite', invite_code, cdata)
                    embed = discord.Embed(title=main.lang["conquest_join_success"].format(cdata["settlement_name"]), color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_join_not_found"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name='ccode', help=main.lang["command_ccode_help"], description=main.lang["command_ccode_description"], ignore_extra=True)
    async def ccode(self, ctx):
        user = ctx.author
        cdata = await qulib.conquest_get('user', user.id)
        if cdata and user.id in {cdata["founderid"],cdata["leaderid"]}:
            embed = discord.Embed(title=main.lang["conquest_code_success"].format(cdata["invite_string"]), color = self.module_embed_color)     
        else:
            embed = discord.Embed(title=main.lang["conquest_code_fail"].format(cdata["invite_string"]), color = self.module_embed_color)    
        await ctx.author.send(embed=embed)

    @commands.cooldown(1, 600,commands.BucketType.user)
    @commands.command(name='cattack', help=main.lang["command_cattack_help"], description=main.lang["command_cattack_description"], usage='@somebody', ignore_extra=True)
    async def cattack(self, ctx, *, defence_user: discord.User = None):
        attack_user = ctx.author
        if defence_user is None:
            embed = discord.Embed(title=main.lang["conquest_attack_args"], color = self.module_embed_color)
        elif attack_user.id is defence_user.id:
            embed = discord.Embed(title=main.lang["conquest_attack_self"], color = self.module_embed_color)
        else:
            cdata_defence = await qulib.conquest_get('user', defence_user.id)
            if cdata_defence:
                cdata_offence = await qulib.conquest_get('user', attack_user.id)
                if cdata_offence:
                    json_data = await qulib.data_get()
                    attack_score = (cdata_offence["settlement_size"] + (1/4)*cdata_offence["tech_attack"])/(cdata_defence["settlement_size"] + (1/4)*cdata_defence["tech_defence"])
                    if attack_score <=1:
                        attack_score_calculated = (50*attack_score)*100
                    else:
                        attack_score_calculated = (50 + 8.35*attack_score)*100
                        if attack_score_calculated > 10000:
                            attack_score_calculated = 10000
                    result = rand_generator.randint(0,10000)
                    experience = math.ceil((10000-result)/10)
                    result_loot = math.ceil((1/20)*cdata_defence["treasury"])

                    if result <= attack_score_calculated:
                        embed = discord.Embed(title=f'{cdata_offence["settlement_name"]} **VS** {cdata_defence["settlement_name"]}', colour=self.module_embed_color, description=main.lang["conquest_attack_result_victory"])
                        cdata_offence["settlement_xp"] += experience
                        cdata_offence["settlement_wins"]+= 1
                        cdata_offence["treasury"] += result_loot
                        cdata_defence["treasury"] -= result_loot
                        cdata_defence["settlement_losses"]+= 1
                        result_string = json_data["Conquest"]["win_string_1"].format(cdata_defence["settlement_name"])
                    else:
                        embed = discord.Embed(title=f'{cdata_offence["settlement_name"]} **VS** {cdata_defence["settlement_name"]}', colour=self.module_embed_color, description=main.lang["conquest_attack_result_defeat"])
                        cdata_defence["settlement_xp"] += math.ceil(experience/10)
                        cdata_defence["settlement_wins"]+= 1
                        cdata_offence["settlement_losses"] += 1
                        result_string = json_data["Conquest"]["defeat_string_1"].format(cdata_defence["settlement_name"])
                        result_loot = 0
                        experience = 0

                    embed.set_thumbnail(url=json_data["Conquest"]["fight"])
                    embed.add_field(name=main.lang["conquest_win_percentage"], value=main.lang["conquest_chances"].format(attack_score_calculated/100), inline=True)
                    embed.add_field(name=main.lang["conquest_roll"], value=result, inline=True)
                    embed.add_field(name=main.lang["conquest_attack_wd"], value=f'  {cdata_offence["settlement_wins"]}       /      {cdata_offence["settlement_losses"]}', inline=True)
                    embed.add_field(name=main.lang["conquest_summary"], value=result_string, inline=True)
                    embed.add_field(name=main.lang["conquest_experience"], value=f'{experience} {main.lang["conquest_exp"]}', inline=True)
                    embed.add_field(name=main.lang["conquest_pillaged_gold"], value=f'{result_loot} G', inline=True)

                    await qulib.conquest_set('invite', cdata_offence["invite_string"], cdata_offence)
                    await qulib.conquest_set('invite', cdata_defence["invite_string"], cdata_defence)
                else:
                    embed = discord.Embed(title=main.lang["conquest_attack_you_no"], color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_attack_enemy_no"], color = self.module_embed_color)
        await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Conquest(bot))