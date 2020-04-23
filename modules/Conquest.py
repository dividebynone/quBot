from discord.ext import tasks, commands
from datetime import datetime
import datetime as dt
from main import config
import libs.qulib as qulib
from libs.quconquest import quConquest
import configparser
import asyncio
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
        self.daily_cloth_price = rand_generator.randint(5,40)
        self.daily_wood_price = rand_generator.randint(5,40)
        self.daily_stone_price = rand_generator.randint(5,40)
        self.daily_food_price = rand_generator.randint(5,40)
        self.rename_price = 500
        print(f'Module {self.__class__.__name__} loaded')

        quConquest.database_init()

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

        data = qulib.sync_data_get()
        time_on_init = datetime.today().replace(microsecond=0)
        if "resources_time" not in data["Conquest"]:
            data["Conquest"]["resources_time"] = time_on_init.strftime('%Y-%m-%d %H:%M:%S')

        qulib.sync_data_set(data)
        self.resources_daily.start() # pylint: disable=no-member
        
    def cog_unload(self):
        self.resources_daily.cancel() # pylint: disable=no-member
    
    @tasks.loop(hours=24.0, reconnect=True)
    async def resources_daily(self):
        data = await qulib.data_get()
        time_on_loop = datetime.today().replace(microsecond=0)
        daily_converted = datetime.strptime(data["Conquest"]["resources_time"], '%Y-%m-%d %H:%M:%S')
        daily_active = daily_converted + dt.timedelta(days=1)
        if time_on_loop < daily_active:    
            time_left = (daily_active - time_on_loop).total_seconds()
            await asyncio.sleep(time_left)
            self.resources_daily.restart() # pylint: disable=no-member
        else:
            data["Conquest"]["resources_time"] = time_on_loop.strftime('%Y-%m-%d %H:%M:%S')
            await qulib.data_set(data)
            await quConquest.send_resource_dailies()
            self.daily_cloth_price = rand_generator.randint(5,40)
            self.daily_wood_price = rand_generator.randint(5,40)
            self.daily_stone_price = rand_generator.randint(5,40)
            self.daily_food_price = rand_generator.randint(5,40)
            main.logger.info(f"[{time_on_loop}][Conquest] Sent settlement resources dailies.")

    @commands.command(name='screate', help=main.lang["command_ccreate_help"], description=main.lang["command_ccreate_description"], usage='"My Settlement Name" <public/private> 100', aliases=['sc'])
    @commands.guild_only()
    async def conquest_create(self, ctx, s_name:str = None, set_type:str = None, entry_fee:int = None):
        user = ctx.author
        if None in {s_name,set_type,entry_fee}:
            embed = discord.Embed(title=main.lang["conquest_create_args"], color = self.module_embed_color)
        elif not await quConquest.find_member(user.id):
            if len(s_name) < 50:
                if set_type.lower() in ('public', 'private'):
                    cdata = await quConquest.get_settlement('user', user.id)
                    if not cdata:
                        if entry_fee < self.minetryfee:
                            embed = discord.Embed(title=main.lang["conquest_entry_requirement"], color = self.module_embed_color)
                        else:
                            user_data = await qulib.user_get(user)
                            if user_data["currency"] < entry_fee:
                                embed = discord.Embed(title=main.lang["conquest_insufficient_funds"], color = self.module_embed_color)
                            elif set_type in ('public', 'private'):
                                dict_input = {}
                                dict_input["entry_fee"] = entry_fee
                                dict_input["invite_string"] = await quConquest.get_unique_code()
                                dict_input["date_created"] = datetime.today().replace(microsecond=0)
                                dict_input["name"] = s_name
                                dict_input["type"] = set_type
                                user_data["currency"] -= entry_fee

                                await qulib.user_set(user,user_data)
                                settlement_id = await quConquest.create_settlement(user.id, dict_input)
                                if settlement_id:
                                    await quConquest.add_member(user.id, settlement_id)
                                embed = discord.Embed(title=main.lang["conquest_create_success"], color = self.module_embed_color)
                            else:
                                embed = discord.Embed(title=main.lang["conquest_create_args"], color = self.module_embed_color)
                    else:
                        embed = discord.Embed(title=main.lang["conquest_create_already_has"], color = self.module_embed_color)
                else:
                    embed = discord.Embed(title=main.lang["conquest_create_public_private"], color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_sname_too_long"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_create_part_of"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name='sinfo', help=main.lang["command_cinfo_help"], description=main.lang["command_cinfo_description"], usage='<Settlement Member> (Optional)', aliases=['si','settlement'])
    @commands.guild_only()
    async def conquest_info(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        if await quConquest.find_member(user.id):
            cdata = await quConquest.get_settlement('id', await quConquest.get_settlement_id(ctx.author.id))
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

    @conquest_join.command(help=main.lang["empty_string"], description=main.lang["command_jprivate_description"], usage="<code here> 100")
    async def private(self, ctx, invite_code: str = None, join_fee: int = None):
        user = ctx.author
        if None in {invite_code, join_fee}:
            embed = discord.Embed(title=main.lang["conquest_join_args"], color = self.module_embed_color)
        else:
            user_info = await qulib.user_get(user)
            cdata = await quConquest.get_settlement('code', invite_code)
            if cdata:
                if await quConquest.find_member(user.id):
                    embed = discord.Embed(title=main.lang["conquest_join_part_of"], color = self.module_embed_color)
                elif user_info["currency"] < join_fee:
                    embed = discord.Embed(title=main.lang["conquest_insufficient_funds"], color = self.module_embed_color)
                elif join_fee < cdata["entry_fee"]:
                    embed = discord.Embed(title=main.lang["conquest_join_min_entry"].format(cdata["entry_fee"]), color = self.module_embed_color)
                else:
                    await quConquest.add_member(user.id, cdata["settlement_id"])
                    cdata["size"] += 1
                    cdata["treasury"] += join_fee
                    user_info["currency"] -= join_fee
                    await qulib.user_set(user, user_info)
                    await quConquest.update_settlement('invite', invite_code, cdata)
                    embed = discord.Embed(title=main.lang["conquest_join_success"].format(cdata["name"]), color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_join_not_found"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @conquest_join.command(help=main.lang["empty_string"], description=main.lang["command_jpublic_description"], usage="@somebody 100")
    async def public(self, ctx, target_user: discord.User = None, join_fee: int = None):
        user = ctx.author
        if None in {target_user, join_fee}:
            embed = discord.Embed(title=main.lang["conquest_join_args"], color = self.module_embed_color)
        elif await quConquest.find_member(target_user.id):
            user_info = await qulib.user_get(user)
            settlementid = await quConquest.get_settlement_id(target_user.id)
            cdata = await quConquest.get_settlement('id', settlementid)
            if cdata:
                if await quConquest.find_member(user.id):
                    embed = discord.Embed(title=main.lang["conquest_join_part_of"], color = self.module_embed_color)
                elif cdata["type"] == "private":
                    embed = discord.Embed(title=main.lang["conquest_join_private_msg"], color = self.module_embed_color)   
                elif user_info["currency"] < join_fee:
                    embed = discord.Embed(title=main.lang["conquest_insufficient_funds"], color = self.module_embed_color)
                elif join_fee < cdata["entry_fee"]:
                    embed = discord.Embed(title=main.lang["conquest_join_min_entry"].format(cdata["entry_fee"]), color = self.module_embed_color)
                else:
                    await quConquest.add_member(user.id, cdata["settlement_id"])
                    cdata["size"] += 1
                    cdata["treasury"] += join_fee
                    user_info["currency"] -= join_fee
                    await qulib.user_set(user, user_info)
                    await quConquest.update_settlement('id', settlementid, cdata)
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
        cdata = await quConquest.get_settlement('user', user.id)
        if cdata and user.id in {cdata["founderid"], cdata["leaderid"]}:
            embed = discord.Embed(title=main.lang["conquest_code_success"].format(cdata["invite_string"]), color = self.module_embed_color)     
        else:
            embed = discord.Embed(title=main.lang["conquest_code_fail"], color = self.module_embed_color)    
        await ctx.author.send(embed=embed)

    @commands.cooldown(1, 600, commands.BucketType.user)
    @conquest_code.command(help=main.lang["command_code_help"], description=main.lang["command_code_new_description"], ignore_extra=True) 
    async def new(self, ctx):
        if await quConquest.generate_new_code(ctx.author.id):
            new_code = await quConquest.get_code(ctx.author.id)
            embed = discord.Embed(title=main.lang["conquest_code_new_success"].format(new_code), color = self.module_embed_color)  
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
        elif await quConquest.find_member(defence_user.id):
            cdata_defence = await quConquest.get_settlement('id', await quConquest.get_settlement_id(defence_user.id))
            if cdata_defence:
                cdata_offence = await quConquest.get_settlement('user', attack_user.id)
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
                        cdata_defence["wins"] += 1
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

                    await quConquest.update_settlement('invite', cdata_offence["invite_string"], cdata_offence)
                    await quConquest.update_settlement('invite', cdata_defence["invite_string"], cdata_defence)
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

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="leaderboard", help=main.lang["command_leaderboard_help"], description=main.lang["command_leaderboard_description"], aliases=['lb'])
    @commands.guild_only()
    async def conquest_leaderboard(self, ctx, page: int = 1):
        if page >= 1:
            page_index = page - 1
            leaderboard_data = await quConquest.get_leaderboard()     
            if len(leaderboard_data[(page_index*10):(page_index*10 + 9)]) > 0:
                counter = page_index*10 + 1 - page_index
                embed = discord.Embed(title=main.lang["conquest_leaderboard_title"], color = self.module_embed_color)
                embed.set_footer(text=f'{main.lang["page_string"]} {page}')
                for item in leaderboard_data[(page_index*10):(page_index*10 + 9)]:
                    embed.add_field(name=f'#{counter} {item[1]} (ID:{item[0]})', value=f'{item[2]} {main.lang["conquest_exp"]}',
                                    inline=True)
                    counter += 1  
            else:
                embed = discord.Embed(title=main.lang["pager_outofrange"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_leaderboard_negative"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name="sleave", help=main.lang["command_sleave_help"], description=main.lang["command_sleave_description"], ignore_extra=True)
    async def conquest_leave(self, ctx):
        user = ctx.author
        if await quConquest.find_member(user.id):
            settlementid = await quConquest.get_settlement_id(user.id)
            cdata = await quConquest.get_settlement('id', settlementid)
            if cdata:
                if cdata["size"] > 1:
                    if user.id == cdata["leaderid"]:
                        embed = discord.Embed(title=main.lang["conquest_leave_leader"], color = self.module_embed_color)
                    else:
                        cdata["size"] -= 1
                        await quConquest.update_settlement('id', settlementid, cdata)
                        await quConquest.remove_member(user.id)
                        embed = discord.Embed(title=main.lang["conquest_leave_success"], color = self.module_embed_color)                  
                else:
                    await quConquest.delete_settlement(settlementid)
                    await quConquest.remove_member(user.id)
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
            if await quConquest.find_member(ctx.author.id):
                settlementid = await quConquest.get_settlement_id(ctx.author.id)
                cdata = await quConquest.get_settlement('id', settlementid)
                if await quConquest.find_member(user.id):              
                    if settlementid == await quConquest.get_settlement_id(user.id):
                        if ctx.author.id == cdata["leaderid"]:  
                            await ctx.send(embed = discord.Embed(title=main.lang["conquest_promote_confirmation"].format(user), color = self.module_embed_color))
                            msg = await self.bot.wait_for('message', check=lambda m: (m.content == 'yes' or m.content == 'no') and m.channel == ctx.channel, timeout=60.0)
                            if msg.content == 'yes':
                                cdata["leaderid"] = user.id
                                await quConquest.update_settlement('id', settlementid, cdata)
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
            if await quConquest.find_member(ctx.author.id):
                settlementid = await quConquest.get_settlement_id(ctx.author.id)
                cdata = await quConquest.get_settlement('id', settlementid)
                if await quConquest.find_member(user.id):
                    if ctx.author.id == cdata["leaderid"]:
                        cdata["size"] -= 1
                        await quConquest.update_settlement('id', settlementid, cdata)
                        await quConquest.remove_member(user.id)
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

    @commands.command(name='resources', help=main.lang["empty_string"], description=main.lang["command_resources_description"], ignore_extra=True)
    async def conquest_resources(self, ctx):
        if await quConquest.find_member(ctx.author.id):
            settlement_id = await quConquest.get_settlement_id(ctx.author.id)
            cdata = await quConquest.get_settlement('id', settlement_id)
            if ctx.author.id == cdata["leaderid"]:
                resources = await quConquest.get_resources(settlement_id)
                if resources:
                    json_data = await qulib.data_get()
                    embed = discord.Embed(title=main.lang["conquest_warehouse_title"].format(cdata["name"]), color=self.module_embed_color)
                    embed.set_thumbnail(url=json_data['Conquest']['warehouse_image'])
                    embed.add_field(name=main.lang["conquest_resources_gold"], value=f'{cdata["treasury"]} {json_data["Conquest"]["gold_icon"]}',inline=True)
                    embed.add_field(name=f'{main.lang["conquest_resources_wood"]} (+{await quConquest.get_resource_production_rate(8, settlement_id)}/{main.lang["day_string"]})',
                                    value=f'{resources["wood"]} {json_data["Conquest"]["resources_wood"]}',inline=True)
                    embed.add_field(name=f'{main.lang["conquest_resources_stone"]} (+{await quConquest.get_resource_production_rate(5, settlement_id)}/{main.lang["day_string"]})',
                                    value=f'{resources["stone"]} {json_data["Conquest"]["resources_stone"]}',inline=True)
                    embed.add_field(name=f'{main.lang["conquest_resources_food"]} (+{await quConquest.get_resource_production_rate(6, settlement_id)}/{main.lang["day_string"]})',
                                    value=f'{resources["food"]} {json_data["Conquest"]["resources_food"]}',inline=True)
                    embed.add_field(name=f'{main.lang["conquest_resources_cloth"]}  (+{await quConquest.get_resource_production_rate(7, settlement_id)}/{main.lang["day_string"]})',
                                    value=f'{resources["cloth"]} {json_data["Conquest"]["resources_cloth"]}',inline=True)
            else:
                embed = discord.Embed(title=main.lang["conquest_not_leader"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_not_part_of"], color = self.module_embed_color)
        await ctx.send(embed=embed)
 
    @commands.group(name='buildings', help=main.lang["empty_string"], description=main.lang["command_buildings_description"])
    async def conquest_buildings(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.invoke(self.buildings_list)

    @conquest_buildings.command(name='list', help=main.lang["empty_string"], description=main.lang["command_blist_description"], ignore_extra=True)
    async def buildings_list(self, ctx):
        if await quConquest.find_member(ctx.author.id):
            settlementid = await quConquest.get_settlement_id(ctx.author.id)
            cdata = await quConquest.get_settlement('id', settlementid)
            json_data = await qulib.data_get()
            buildings = await quConquest.get_buildings()
            embed = discord.Embed(title=main.lang["conquest_buildings_title"].format(cdata['name']), color=self.module_embed_color)
            th_level = await quConquest.level_converter(cdata["tech_tree"][0])
            for i in range(len(buildings)):
                level = await quConquest.level_converter(cdata["tech_tree"][i])
                if level == 10 or (level == 1 and (i+1) in (3, 9)):
                    embed.add_field(name=f"**{i+1} | {buildings[i]['name']} - {main.lang['conquest_level']} {level}** *MAX*", value=main.lang["conquest_max_reached"],inline=False)
                else:
                    gold = f"{pow(2, level+1)*buildings[i]['mltplr_gold']} {json_data['Conquest']['gold_icon']}" if buildings[i]['mltplr_gold'] != 0 else ""
                    wood = f"{pow(level+1, 2)*(level+1)*buildings[i]['mltplr_wood']} {json_data['Conquest']['resources_wood']}" if (buildings[i]['mltplr_wood'] != 0) else ""
                    stone = f"{pow(level+1, 2)*(level+1)*buildings[i]['mltplr_stone']} {json_data['Conquest']['resources_stone']}" if (buildings[i]['mltplr_stone'] != 0) else ""
                    food = f"{pow(level+1, 2)*(level+1)*buildings[i]['mltplr_food']} {json_data['Conquest']['resources_food']}" if (buildings[i]['mltplr_food'] != 0) else ""
                    cloth = f"{pow(level+1, 2)*(level+1)*buildings[i]['mltplr_cloth']} {json_data['Conquest']['resources_cloth']}" if (buildings[i]['mltplr_cloth'] != 0) else ""
                    if int(level) == 0 and i in (0,4,5,6,7):
                        wood = stone = food = cloth = ""
                    if i > 0 and ((level+1) > int(th_level)):
                        embed.add_field(name=f"**{i+1} | {buildings[i]['name']} - {main.lang['conquest_level']} {level}** -> *{main.lang['conquest_level']} {int(level)+1}*",
                                        value=f'*{main.lang["conquest_upgrade_th"]}*',inline=False)
                    else:
                        embed.add_field(name=f"**{i+1} | {buildings[i]['name']} - {main.lang['conquest_level']} {level}** -> *{main.lang['conquest_level']} {int(level)+1}*",
                                        value=f"**{main.lang['conquest_resources_needed']}:** {gold} {wood} {stone} {food} {cloth}",inline=False)
        else:
            embed = discord.Embed(title=main.lang["conquest_not_part_of"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.user) 
    @conquest_buildings.command(name='upgrade', help=main.lang["command_sleader"], description=main.lang["command_bupgrade_description"], usage='1', ignore_extra=True)
    async def buildings_upgrade(self, ctx, building_id: int):
        if 1 <= building_id <=10:
            if await quConquest.find_member(ctx.author.id):
                settlementid = await quConquest.get_settlement_id(ctx.author.id)
                cdata = await quConquest.get_settlement('id', settlementid)
                if ctx.author.id == cdata["leaderid"]:
                    building = await quConquest.get_building(building_id)
                    resources = await quConquest.get_resources(settlementid)
                    level = int(cdata["tech_tree"][building_id-1]) if cdata['tech_tree'][building_id-1] != "X" else 10
                    th_level = cdata['tech_tree'][0] if cdata['tech_tree'][0] != "X" else 10
                    if (level+1) <= int(th_level) or (building_id == 1):
                        if level != 10:
                            if level == 1 and building_id in (3, 9):
                                embed = discord.Embed(title=main.lang["conquest_upgrade_max_level"], color=self.module_embed_color)
                            else:
                                gold = pow(2, int(level)+1)*building['gold']
                                wood = pow(int(level)+1, 2)*(level+1)*building['wood']
                                stone = pow(int(level)+1, 2)*(level+1)*building['stone']
                                food = pow(int(level)+1, 2)*(level+1)*building['food']
                                cloth = pow(int(level)+1, 2)*(level+1)*building['cloth']
                                
                                if (building_id in (1,5,6,7,8) and level == 0):
                                    wood = stone = food = cloth = 0
                                
                                if (cdata['treasury']>=gold and resources['cloth']>=cloth and resources['stone']>=stone and resources['food']>=food and resources['wood']>=wood):
                                    embed = discord.Embed(title=main.lang["conquest_upgrade_success"].format(building['name'], level+1), color=self.module_embed_color)
                                    tech_tree = list(cdata['tech_tree'])
                                    tech_tree[building_id-1] = str(level+1) if (level+1) != 10 else "X"
                                    cdata['tech_tree'] = "".join(tech_tree)
                                    cdata['treasury'] -= gold
                                    resources['cloth'] -= cloth
                                    resources['food'] -= food
                                    resources['stone'] -= stone
                                    resources['wood'] -= wood
                                    await quConquest.update_resources(settlementid, resources)
                                    await quConquest.update_settlement('id', settlementid, cdata)
                                    await quConquest.upgrade_building(settlementid, building_id)
                                else:
                                    embed = discord.Embed(title=main.lang["conquest_upgrade_fail"].format(building['name']), color=self.module_embed_color)
                        else:
                            embed = discord.Embed(title=main.lang["conquest_upgrade_max_level"], color=self.module_embed_color)
                    else:
                        embed = discord.Embed(title=main.lang["conquest_upgrade_th"], color = self.module_embed_color)
                else:
                    embed = discord.Embed(title=main.lang["conquest_not_leader"], color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_not_part_of"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_requirements_range"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name='requirements', help=main.lang["empty_string"], description=main.lang["command_reqs_description"], usage="1", aliases=['reqs'])
    async def conquest_requirements(self, ctx, *, building_id: int):
        if 1 <= building_id <=10:
            if await quConquest.find_member(ctx.author.id):
                json_data = await qulib.data_get()
                building = await quConquest.get_building(building_id)
                embed = discord.Embed(title=main.lang["conquest_requirements_title"].format(building['name']), color=self.module_embed_color)
                for level in range(0, 10):
                    gold = f"{pow(2, int(level)+1)*building['gold']} {json_data['Conquest']['gold_icon']}" if building['gold'] != 0 else ""
                    wood = f"{pow(int(level)+1, 2)*(level+1)*building['wood']} {json_data['Conquest']['resources_wood']}" if (building['wood'] != 0) else ""
                    stone = f"{pow(int(level)+1, 2)*(level+1)*building['stone']} {json_data['Conquest']['resources_stone']}" if (building['stone'] != 0) else ""
                    food = f"{pow(int(level)+1, 2)*(level+1)*building['food']} {json_data['Conquest']['resources_food']}" if (building['food'] != 0) else ""
                    cloth = f"{pow(int(level)+1, 2)*(level+1)*building['cloth']} {json_data['Conquest']['resources_cloth']}" if (building['cloth'] != 0) else ""
                    if level == 0 and building_id in (1,5,6,7,8):
                        wood = stone = food = cloth = ""
                    embed.add_field(name=f"**{main.lang['conquest_level']} {level}** -> *{main.lang['conquest_level']} {int(level)+1}*",
                                    value=f"**{main.lang['conquest_resources_needed']}:** {gold} {wood} {stone} {food} {cloth}",inline=False)
                    if building_id in (3, 9):
                        break
            else:
                embed = discord.Embed(title=main.lang["conquest_not_part_of"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_requirements_range"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user) 
    @commands.group(name='market', help=main.lang["command_market_help"], description=main.lang["command_market_description"])
    async def conquest_market(self, ctx):
        if not ctx.invoked_subcommand:
            json_data = await qulib.data_get()
            embed = discord.Embed(title=main.lang["conquest_market_title"], color=self.module_embed_color)
            embed.set_thumbnail(url=json_data['Conquest']['market_image'])
            embed.add_field(name=f"1 )  {json_data['Conquest']['resources_cloth']} **{main.lang['conquest_resources_cloth']}**",
                            value=f"{main.lang['conquest_sell_price']}: **{self.daily_cloth_price}  {json_data['Conquest']['gold_icon']} /{main.lang['conquest_piece']}**",inline=False)
            embed.add_field(name=f"2 )  {json_data['Conquest']['resources_wood']} **{main.lang['conquest_resources_wood']}**",
                            value=f"{main.lang['conquest_sell_price']}: **{self.daily_wood_price}  {json_data['Conquest']['gold_icon']} /{main.lang['conquest_piece']}**",inline=False)
            embed.add_field(name=f"3 )  {json_data['Conquest']['resources_stone']} **{main.lang['conquest_resources_stone']}**",
                            value=f"{main.lang['conquest_sell_price']}: **{self.daily_stone_price}  {json_data['Conquest']['gold_icon']} /{main.lang['conquest_piece']}**",inline=False)
            embed.add_field(name=f"4 )  {json_data['Conquest']['resources_food']} **{main.lang['conquest_resources_food']}**",
                            value=f"{main.lang['conquest_sell_price']}: **{self.daily_food_price}  {json_data['Conquest']['gold_icon']} /{main.lang['conquest_piece']}**",inline=False)
            embed.set_footer(text=main.lang["conquest_market_reminder"])
            await ctx.send(embed=embed)

    @conquest_market.command(name='sell', help=main.lang["command_sleader"], description=main.lang["command_msell_description"], usage='wood 150')
    async def market_sell(self, ctx, item: str, quantity: int):
        if item.lower() in ("cloth", "wood", "stone", "food", "1", "2", "3", "4"):
            if await quConquest.find_member(ctx.author.id):
                settlementid = await quConquest.get_settlement_id(ctx.author.id)
                cdata = await quConquest.get_settlement('id', settlementid)
                if cdata['tech_tree'][2] == "1":
                    if ctx.author.id == cdata["leaderid"]:
                        json_data = await qulib.data_get()
                        resources_dict = {"1":"cloth", "2":"wood", "3":"stone", "4":"food"}
                        prices_dict = {"cloth":self.daily_cloth_price, "wood":self.daily_wood_price, "stone":self.daily_stone_price, "food":self.daily_food_price}
                        resources = await quConquest.get_resources(settlementid)
                        index = resources_dict[item] if item in resources_dict else item
                        if quantity > 0 and quantity <= resources[index]:
                            resources[index] -= quantity
                            cdata['treasury'] += quantity*prices_dict[index]  
                            await quConquest.update_resources(settlementid, resources)
                            await quConquest.update_settlement("id", settlementid, cdata)
                            embed = discord.Embed(title=main.lang["conquest_market_sell_success"].format(quantity, index, quantity*prices_dict[index], json_data['Conquest']['gold_icon']), color = self.module_embed_color)
                        else:
                            embed = discord.Embed(title=main.lang["conquest_market_sell_fail"], color = self.module_embed_color)
                    else:
                        embed = discord.Embed(title=main.lang["conquest_not_leader"], color = self.module_embed_color)
                else:
                    embed = discord.Embed(title=main.lang["conquest_sell_no_market"], color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_not_part_of"], color = self.module_embed_color)
            await ctx.send(embed=embed)

    @conquest_market.command(name='buy', help=main.lang["command_sleader"], description=main.lang["command_mbuy_description"], usage='cloth 50')
    async def market_buy(self, ctx, item: str, quantity: int):
        if item.lower() in ("cloth", "wood", "stone", "food", "1", "2", "3", "4"):
            if await quConquest.find_member(ctx.author.id):
                settlementid = await quConquest.get_settlement_id(ctx.author.id)
                cdata = await quConquest.get_settlement('id', settlementid)
                if cdata['tech_tree'][2] == "1":
                    if ctx.author.id == cdata["leaderid"]:
                        json_data = await qulib.data_get()
                        resources_dict = {"1":"cloth", "2":"wood", "3":"stone", "4":"food"}
                        prices_dict = {"cloth":self.daily_cloth_price, "wood":self.daily_wood_price, "stone":self.daily_stone_price, "food":self.daily_food_price}
                        resources = await quConquest.get_resources(settlementid)
                        index = resources_dict[item] if item in resources_dict else item
                        if quantity > 0 and quantity*prices_dict[index] <= resources[index]:
                            resources[index] += quantity
                            cdata['treasury'] -= quantity*prices_dict[index]  
                            await quConquest.update_resources(settlementid, resources)
                            await quConquest.update_settlement("id", settlementid, cdata)
                            embed = discord.Embed(title=main.lang["conquest_market_buy_success"].format(quantity, index, quantity*prices_dict[index], json_data['Conquest']['gold_icon']), color = self.module_embed_color)
                        else:
                            embed = discord.Embed(title=main.lang["conquest_market_buy_fail"], color = self.module_embed_color)
                    else:
                        embed = discord.Embed(title=main.lang["conquest_not_leader"], color = self.module_embed_color)
                else:
                    embed = discord.Embed(title=main.lang["conquest_buy_no_market"], color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_not_part_of"], color = self.module_embed_color)
            await ctx.send(embed=embed)

    @commands.command(name="deposit", help=main.lang["command_deposit_help"], description=main.lang["command_deposit_description"], usage='100')
    async def conquest_deposit(self, ctx, number: int):
        if await quConquest.find_member(ctx.author.id):
            settlement_id = await quConquest.get_settlement_id(ctx.author.id)
            cdata = await quConquest.get_settlement('id', settlement_id)
            author_info = await qulib.user_get(ctx.author)
            json_data = await qulib.data_get()
            if number > 0:
                if author_info['currency'] <= 0 or number > author_info['currency']:
                    embed = discord.Embed(title=main.lang["economy_insufficient_funds"], color=self.module_embed_color)
                else:
                    embed = discord.Embed(title=main.lang["conquest_deposit_success"].format(number, json_data['Conquest']['gold_icon']), color=self.module_embed_color)
                    author_info['currency'] -= number
                    cdata['treasury'] += number
                    await qulib.user_set(ctx.author, author_info)
                    await quConquest.update_settlement("id", settlement_id, cdata)
        else:
            embed = discord.Embed(title=main.lang["conquest_not_part_of"], color = self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.command(name='rename', help=main.lang["command_srename_help"], description=main.lang["command_srename_description"], usage='My new settlement name')
    async def conquest_settlement_rename(self, ctx, *, name: str):
        if len(name) < 50:
            if await quConquest.find_member(ctx.author.id):
                settlementid = await quConquest.get_settlement_id(ctx.author.id)
                cdata = await quConquest.get_settlement('id', settlementid)
                if ctx.author.id == cdata["leaderid"]:
                    json_data = await qulib.data_get()
                    if cdata['treasury'] >= self.rename_price:
                        cdata['name'] = name
                        cdata['treasury'] -= self.rename_price
                        await quConquest.update_settlement("id", settlementid, cdata)
                        embed = discord.Embed(title=main.lang["conquest_rename_success"].format(name, self.rename_price, json_data['Conquest']['gold_icon']), color = self.module_embed_color)
                    else:
                        embed = discord.Embed(title=main.lang["conquest_rename_no_funds"].format(self.rename_price, json_data['Conquest']['gold_icon']), color = self.module_embed_color)
                else:
                    embed = discord.Embed(title=main.lang["conquest_not_leader"], color = self.module_embed_color)
            else:
                embed = discord.Embed(title=main.lang["conquest_not_part_of"], color = self.module_embed_color)
        else:
            embed = discord.Embed(title=main.lang["conquest_sname_too_long"], color = self.module_embed_color)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Conquest(bot))