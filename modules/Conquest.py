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

    @commands.command(name='screate', help=main.lang["command_ccreate_help"], description=main.lang["command_ccreate_description"], usage='"My Settlement Name" <public/private> 100', aliases=['sc'])
    @commands.guild_only()
    async def conquest_create(self, ctx, s_name:str = None, set_type:str = None, entry_fee:int = None):
        user = ctx.author
        if None in {s_name,set_type,entry_fee}:
            embed = discord.Embed(title=main.lang["conquest_create_args"], color = self.module_embed_color)
        elif not await qulib.conquest_find_member(user):
            if len(s_name) < 50:
                if set_type.lower() in ('public', 'private'):
                    cdata = await qulib.conquest_get('user', user.id)
                    if not cdata:
                        if entry_fee < self.minetryfee:
                            embed = discord.Embed(title=main.lang["conquest_entry_requirement"], color = self.module_embed_color)
                        else:
                            user_data = await qulib.user_get(user)
                            if user_data["currency"] < entry_fee:
                                embed = discord.Embed(title=main.lang["conquest_insufficient_funds"], color = self.module_embed_color)
                            elif set_type in ('public', 'private'):
                                temp_invite_string = qulib.string_generator(15)
                                cinvite_data = await qulib.conquest_find_code(temp_invite_string)
                                if cinvite_data:
                                    while temp_invite_string is cinvite_data:
                                        temp_invite_string = qulib.string_generator(15)
                                        cinvite_data = await qulib.conquest_find_code(temp_invite_string)

                                dict_input = {}
                                dict_input["entry_fee"] = entry_fee
                                dict_input["invite_string"] = temp_invite_string
                                dict_input["date_created"] = datetime.today().replace(microsecond=0)
                                dict_input["name"] = s_name
                                dict_input["type"] = set_type
                                user_data["currency"] -= entry_fee

                                await qulib.user_set(user,user_data)
                                settlement_id = await qulib.conquest_set('new', user.id, dict_input)
                                if settlement_id:
                                    await qulib.conquest_add_member(user, settlement_id)
                                embed = discord.Embed(title=main.lang["conquest_create_success"], color = self.module_embed_color)
                            else:
                                embed = discord.Embed(title=main.lang["conquest_create_args"], color = self.module_embed_color)
                    else:
                        embed = discord.Embed(title=main.lang["conquest_create_already_has"], color = self.module_embed_color)
                else:
                    embed = discord.Embed(title=main.lang["conquest_create_public_private"], color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_create_sname_too_long"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_create_part_of"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name='sinfo', help=main.lang["command_cinfo_help"], description=main.lang["command_cinfo_description"], usage='<Settlement Member> (Optional)', aliases=['si','settlement'])
    @commands.guild_only()
    async def conquest_info(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        if await qulib.conquest_find_member(user):
            cdata = await qulib.conquest_get('id', await qulib.conquest_get_settlementid(user))
            json_data = await qulib.data_get()
            if cdata:
                founder_name = ctx.guild.get_member(cdata["founderid"]) or cdata["founderid"]
                leader_name = ctx.guild.get_member(cdata["leaderid"]) or cdata["leaderid"]
                if cdata["wins"] == cdata["losses"] == 0:
                    win_ratio = 0
                elif cdata["wins"] > 0 and cdata["losses"] is 0:
                    win_ratio = 100
                elif cdata["losses"] > 0 and cdata["wins"] is 0:
                    win_ratio = 0
                else:
                    win_ratio = "%.2f" % float((cdata["wins"]/(cdata["losses"]+cdata["wins"]))*100)

                embed = discord.Embed(title=main.lang["conquest_info_info"], color=self.module_embed_color)
                embed.add_field(name=main.lang["conquest_info_name"], value=cdata["name"],inline=True)
                embed.add_field(name=main.lang["conquest_info_created"], value=cdata["date_created"], inline=True)
                embed.set_thumbnail(url=json_data["Conquest"]["settlement_image_1"])
                embed.add_field(name=main.lang["conquest_info_founder"], value=founder_name, inline=False)
                embed.add_field(name=main.lang["conquest_info_leader"], value=leader_name, inline=False)
                embed.add_field(name=main.lang["conquest_info_population"], value=cdata["size"], inline=True)
                embed.add_field(name=main.lang["conquest_info_treasury"], value=cdata["treasury"], inline=True)
                embed.add_field(name=main.lang["conquest_info_type"], value =cdata["type"], inline = True)
                embed.add_field(name=main.lang["conquest_info_level"], value =cdata["level"], inline = False)
                embed.add_field(name=main.lang["conquest_info_wins_losses"],
                                value =f'```{main.lang["conquest_wins"]}: {cdata["wins"]} | {main.lang["conquest_losses"]}: {cdata["losses"]} ({win_ratio}% {main.lang["conquest_info_win_ratio"]})```',
                                inline = True)
            else:
                embed = discord.Embed(title=main.lang["conquest_info_fail"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_join_fail_user"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.group(name='join', help=main.lang["command_cjoin_help"], description=main.lang["command_cjoin_description"], usage='private/public ...')
    @commands.guild_only()
    async def conquest_join(self, ctx):
        if not ctx.invoked_subcommand:
            embed = discord.Embed(title=main.lang["conquest_join_no_subcommands"], color = self.module_embed_color)
            await ctx.send(embed=embed)

    @conquest_join.command()
    async def private(self, ctx, invite_code: str = None, join_fee: int = None):
        user = ctx.author
        if None in {invite_code, join_fee}:
            embed = discord.Embed(title=main.lang["conquest_join_args"], color = self.module_embed_color)
        else:
            user_info = await qulib.user_get(user)
            cdata = await qulib.conquest_get('code', invite_code)
            if cdata:
                if await qulib.conquest_find_member(user):
                    embed = discord.Embed(title=main.lang["conquest_join_part_of"], color = self.module_embed_color)
                elif user_info["currency"] < join_fee:
                    embed = discord.Embed(title=main.lang["conquest_insufficient_funds"], color = self.module_embed_color)
                elif join_fee < cdata["entry_fee"]:
                    embed = discord.Embed(title=main.lang["conquest_join_min_entry"].format(cdata["entry_fee"]), color = self.module_embed_color)
                else:
                    await qulib.conquest_add_member(user, cdata["settlement_id"])
                    cdata["size"] += 1
                    cdata["treasury"] += join_fee
                    user_info["currency"] -= join_fee
                    await qulib.user_set(user, user_info)
                    await qulib.conquest_set('invite', invite_code, cdata)
                    embed = discord.Embed(title=main.lang["conquest_join_success"].format(cdata["name"]), color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_join_not_found"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @conquest_join.command()
    async def public(self, ctx, target_user: discord.User = None, join_fee: int = None):
        user = ctx.author
        if None in {target_user, join_fee}:
            embed = discord.Embed(title=main.lang["conquest_join_args"], color = self.module_embed_color)
        elif await qulib.conquest_find_member(target_user):
            user_info = await qulib.user_get(user)
            settlementid = await qulib.conquest_get_settlementid(target_user)
            cdata = await qulib.conquest_get('id', settlementid)
            if cdata:
                if await qulib.conquest_find_member(user):
                    embed = discord.Embed(title=main.lang["conquest_join_part_of"], color = self.module_embed_color)
                elif cdata["type"] == "private":
                    embed = discord.Embed(title=main.lang["conquest_join_private_msg"], color = self.module_embed_color)   
                elif user_info["currency"] < join_fee:
                    embed = discord.Embed(title=main.lang["conquest_insufficient_funds"], color = self.module_embed_color)
                elif join_fee < cdata["entry_fee"]:
                    embed = discord.Embed(title=main.lang["conquest_join_min_entry"].format(cdata["entry_fee"]), color = self.module_embed_color)
                else:
                    await qulib.conquest_add_member(user, cdata["settlement_id"])
                    cdata["size"] += 1
                    cdata["treasury"] += join_fee
                    user_info["currency"] -= join_fee
                    await qulib.user_set(user, user_info)
                    await qulib.conquest_set('id', settlementid, cdata)
                    embed = discord.Embed(title=main.lang["conquest_join_success"].format(cdata["name"]), color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_join_not_found"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_join_target_fail"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.group(name='code', help=main.lang["empty_string"], description=main.lang["command_code_description"], usage='show/new')
    async def conquest_code(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.invoke(self.show)

    @conquest_code.command(help=main.lang["command_code_help"], description=main.lang["command_code_show_description"], ignore_extra=True)
    async def show(self, ctx):
        user = ctx.author
        cdata = await qulib.conquest_get('user', user.id)
        if cdata and user.id in {cdata["founderid"],cdata["leaderid"]}:
            embed = discord.Embed(title=main.lang["conquest_code_success"].format(cdata["invite_string"]), color = self.module_embed_color)     
        else:
            embed = discord.Embed(title=main.lang["conquest_code_fail"].format(cdata["invite_string"]), color = self.module_embed_color)    
        await ctx.author.send(embed=embed)

    @conquest_code.command(help=main.lang["command_code_help"], description=main.lang["command_code_new_description"], ignore_extra=True)
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def new(self, ctx):
        new_invite_string = qulib.string_generator(15)
        cinvite_data = await qulib.conquest_find_code(new_invite_string)
        if cinvite_data:
            while new_invite_string is cinvite_data:
                new_invite_string = qulib.string_generator(15)
                cinvite_data = await qulib.conquest_find_code(new_invite_string)
        if await qulib.conquest_new_code(new_invite_string, ctx.author.id):
            embed = discord.Embed(title=main.lang["conquest_code_new_success"].format(new_invite_string), color = self.module_embed_color)  
        else:
            embed = discord.Embed(title=main.lang["conquest_code_new_fail"], color = self.module_embed_color)
        await ctx.author.send(embed=embed) 

    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.command(name='attack', help=main.lang["command_cattack_help"], description=main.lang["command_cattack_description"], usage='@somebody', ignore_extra=True)
    @commands.guild_only()
    async def conquest_attack(self, ctx, *, defence_user: discord.User = None):
        attack_user = ctx.author
        completed_attack = False
        if defence_user is None:
            embed = discord.Embed(title=main.lang["conquest_attack_args"], color = self.module_embed_color)
        elif attack_user.id is defence_user.id:
            embed = discord.Embed(title=main.lang["conquest_attack_self"], color = self.module_embed_color)
        elif await qulib.conquest_find_member(defence_user):
            cdata_defence = await qulib.conquest_get('id', await qulib.conquest_get_settlementid(defence_user))
            if cdata_defence:
                cdata_offence = await qulib.conquest_get('user', attack_user.id)
                if cdata_offence:
                    json_data = await qulib.data_get()
                    attack_score = (cdata_offence["size"] + (1/4)*cdata_offence["tech_attack"])/(cdata_defence["size"] + (1/4)*cdata_defence["tech_defence"])
                    attack_score_calculated = (50*attack_score)*100 if attack_score <=1 else (50 + 8.35*attack_score)*100
                    if attack_score_calculated > 10000:
                        attack_score_calculated = 10000
                    result = rand_generator.randint(0,10000)
                    experience = math.ceil((10000-result)/10)
                    result_loot = math.ceil((1/20)*cdata_defence["treasury"])

                    if result <= attack_score_calculated:
                        embed = discord.Embed(title=f'{cdata_offence["name"]} **VS** {cdata_defence["name"]}', colour=self.module_embed_color, description=main.lang["conquest_attack_result_victory"])
                        cdata_offence["experience"] += experience
                        cdata_offence["wins"]+= 1
                        cdata_offence["treasury"] += result_loot
                        cdata_defence["treasury"] -= result_loot
                        cdata_defence["losses"]+= 1
                        result_string = json_data["Conquest"]["win_string_1"].format(cdata_defence["name"])
                    else:
                        embed = discord.Embed(title=f'{cdata_offence["name"]} **VS** {cdata_defence["name"]}', colour=self.module_embed_color, description=main.lang["conquest_attack_result_defeat"])
                        cdata_defence["experience"] += math.ceil(experience/10)
                        cdata_defence["wins"]+= 1
                        cdata_offence["losses"] += 1
                        result_string = json_data["Conquest"]["defeat_string_1"].format(cdata_defence["name"])
                        result_loot = 0
                        experience = 0

                    embed.set_thumbnail(url=json_data["Conquest"]["fight"])
                    embed.add_field(name=main.lang["conquest_win_percentage"], value=main.lang["conquest_chances"].format(attack_score_calculated/100), inline=True)
                    embed.add_field(name=main.lang["conquest_roll"], value=result, inline=True)
                    embed.add_field(name=main.lang["conquest_attack_wd"], value=f'  {cdata_offence["wins"]}       /      {cdata_offence["losses"]}', inline=True)
                    embed.add_field(name=main.lang["conquest_summary"], value=result_string, inline=True)
                    embed.add_field(name=main.lang["conquest_experience"], value=f'{experience} {main.lang["conquest_exp"]}', inline=True)
                    embed.add_field(name=main.lang["conquest_pillaged_gold"], value=f'{result_loot} G', inline=True)

                    await qulib.conquest_set('invite', cdata_offence["invite_string"], cdata_offence)
                    await qulib.conquest_set('invite', cdata_defence["invite_string"], cdata_defence)
                    completed_attack = True
                else:
                    embed = discord.Embed(title=main.lang["conquest_attack_you_no"], color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_attack_enemy_no"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_attack_enemy_part_of"], color = self.module_embed_color)
        await ctx.send(embed=embed)
        if not completed_attack:
            self.bot.get_command(ctx.command.name).reset_cooldown(ctx)

    @commands.command(name="leaderboard", help=main.lang["command_leaderboard_help"], description=main.lang["command_leaderboard_description"], aliases=['lb'])
    @commands.guild_only()
    async def conquest_leaderboard(self, ctx, page: int = 1):
        if page >= 1:
            page_index = page - 1
            leaderboard_data = await qulib.conquest_get_leaderboard()           
            if len(leaderboard_data[(page_index*10):(page_index*10 + 9)]) > 0:
                counter = 1
                embed = discord.Embed(title=main.lang["conquest_leaderboard_title"], color = self.module_embed_color)
                embed.set_footer(text=f'{main.lang["page_string"]} {page}')
                for item in leaderboard_data[(page_index*10):(page_index*10 + 9)]:
                    inline_bool = False if page%2 == 0 else True
                    embed.add_field(name=f'#{counter} {item[1]} (ID:{item[0]})', value=f'{item[2]} {main.lang["conquest_exp"]}',
                                    inline=inline_bool)
                    counter += 1  
            else:
                embed = discord.Embed(title=main.lang["conquest_leaderboard_outofrange"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_leaderboard_negative"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name="sleave", help=main.lang["command_sleave_help"], description=main.lang["command_sleave_description"], ignore_extra=True)
    async def conquest_leave(self, ctx):
        user = ctx.author
        if await qulib.conquest_find_member(user):
            settlementid = await qulib.conquest_get_settlementid(user)
            cdata = await qulib.conquest_get('id', settlementid)
            if cdata:
                if cdata["size"] > 1:
                    if user.id == cdata["leaderid"]:
                        embed = discord.Embed(title=main.lang["conquest_leave_leader"], color = self.module_embed_color)
                    else:
                        cdata["size"] -= 1
                        await qulib.conquest_set('id', settlementid, cdata)
                        await qulib.conquest_remove_member(user)
                        embed = discord.Embed(title=main.lang["conquest_leave_success"], color = self.module_embed_color)                  
                else:
                    await qulib.conquest_delete_settlement(settlementid)
                    await qulib.conquest_remove_member(user)
                    embed = discord.Embed(title=main.lang["conquest_leave_success_alone"], color = self.module_embed_color)      
            else:
                embed = discord.Embed(title=main.lang["conquest_leave_not_found"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_not_part_of"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name="promote", help=main.lang["command_promote_help"], description=main.lang["command_promote_description"], usage='@somebody')
    @commands.guild_only()
    async def conquest_promote(self, ctx, *, user: discord.User):
        if user != ctx.author:
            if await qulib.conquest_find_member(ctx.author):
                settlementid = await qulib.conquest_get_settlementid(ctx.author)
                cdata = await qulib.conquest_get('id', settlementid)
                if await qulib.conquest_find_member(user):              
                    if settlementid == await qulib.conquest_get_settlementid(user):
                        if ctx.author.id == cdata["leaderid"]:  
                            await ctx.send(embed = discord.Embed(title=main.lang["conquest_promote_confirmation"].format(user), color = self.module_embed_color))
                            msg = await self.bot.wait_for('message', check=lambda m: (m.content == 'yes' or m.content == 'no') and m.channel == ctx.channel, timeout=60.0)
                            if msg.content == 'yes':
                                cdata["leaderid"] = user.id
                                await qulib.conquest_set('id', settlementid, cdata)
                                embed = discord.Embed(title=main.lang["conquest_promote_success"].format(user), color = self.module_embed_color)
                        else:
                            embed = discord.Embed(title=main.lang["conquest_not_leader"], color = self.module_embed_color)
                    else:
                        embed = discord.Embed(title=main.lang["conquest_promote_settlement_fail"], color = self.module_embed_color)
                else:
                    embed = discord.Embed(title=main.lang["conquest_target_not_part_of"], color = self.module_embed_color)
            else:
                 embed = discord.Embed(title=main.lang["conquest_not_part_of"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_promote_self"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name='skick', help=main.lang["command_skick_help"], description=main.lang["command_skick_description"], usage='@somebody')
    @commands.guild_only()
    async def conquest_kick(self, ctx, *, user: discord.User):
        if user != ctx.author:
            if await qulib.conquest_find_member(ctx.author):
                settlementid = await qulib.conquest_get_settlementid(ctx.author)
                cdata = await qulib.conquest_get('id', settlementid)
                if await qulib.conquest_find_member(user):
                    if ctx.author.id == cdata["leaderid"]:
                        cdata["size"] -= 1
                        await qulib.conquest_set('id', settlementid, cdata)
                        await qulib.conquest_remove_member(user)
                        embed = discord.Embed(title=main.lang["conquest_skick_success"].format(user), color = self.module_embed_color)
                    else:
                        embed = discord.Embed(title=main.lang["conquest_not_leader"], color = self.module_embed_color)
                else:
                    embed = discord.Embed(title=main.lang["conquest_target_not_part_of"], color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_not_part_of"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_skick_self"], color = self.module_embed_color)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Conquest(bot))