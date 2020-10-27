from PIL import Image, ImageDraw, ImageFont
from discord.ext import tasks, commands
from datetime import datetime
import datetime as dt
from main import config, bot_path
import libs.qulib as qulib
from libs.prefixhandler import PrefixHandler
import libs.quconquest as quconquest
from libs.quconquest import SettlementAccess
import configparser
import textwrap
import asyncio
import secrets
import discord
import math
import main
import sys
import io
import os

rand_generator = secrets.SystemRandom()

class Conquest(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.embed_color =  0xd59c6d
        
        self.rename_price = 500
        self.sname_limit = 50

        self.daily_cloth_price = rand_generator.randint(5,40)
        self.daily_wood_price = rand_generator.randint(5,40)
        self.daily_stone_price = rand_generator.randint(5,40)
        self.daily_food_price = rand_generator.randint(5,40)

        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = False
        self.module_dependencies = ['Economy']

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)

        self.quConquest = quconquest.quConquest()

        if 'Conquest' not in config.sections():
            config.add_section('Conquest')
        if 'MinEntryFee' not in config['Conquest']:
            config.set('Conquest', 'MinEntryFee', '100')
        if 'TaxRate' not in config['Conquest']:
            config.set('Conquest', 'TaxRate', '10')

        with open(os.path.join(bot_path, 'config.ini'), 'w', encoding="utf_8") as config_file:
            config.write(config_file)
        config_file.close()

        with open(os.path.join(bot_path, 'config.ini'), 'r', encoding="utf_8") as config_file:
            config.read_file(config_file)
            self.minetryfee = int(config.get('Conquest', 'MinEntryFee'))
            self.tax_rate = int(config.get('Conquest', 'TaxRate'))
        config_file.close()

        data = qulib.sync_data_get()
        time_on_init = datetime.today().replace(microsecond=0)
        if "resources_time" not in data["Conquest"]:
            data["Conquest"]["resources_time"] = time_on_init.strftime('%Y-%m-%d %H:%M:%S')

        self.background_image = Image.open(os.path.join(main.bot_path, 'data', 'images', 'conquest', 'settlement-background.jpg'))
        self.attack_image = Image.open(os.path.join(main.bot_path, 'data', 'images', 'conquest', 'settlement-attack.jpg'))
        self.level_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'LEMONMILK-Medium.otf'), 50)
        self.title_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'LEMONMILK-Regular.otf'), 28)
        self.medium_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'LEMONMILK-Medium.otf'), 22)
        self.body_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'LEMONMILK-Medium.otf'), 20)

        self.left = '⬅️'
        self.right = '➡️'
        self.pagination_timeout = '⏹️'

        qulib.sync_data_set(data)
        self.resources_daily.start() # pylint: disable=no-member

        print(f'Module {self.__class__.__name__} loaded')

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
            await self.quConquest.send_resource_dailies()
            self.daily_cloth_price = rand_generator.randint(15,20)
            self.daily_wood_price = rand_generator.randint(15,20)
            self.daily_stone_price = rand_generator.randint(15,20)
            self.daily_food_price = rand_generator.randint(15,20)
            main.logger.info(f"[{time_on_loop}][Conquest] Sent settlement resources dailies.")

    def predicate(self, message, l, r):
        def check(reaction, user):
            if reaction.message.id != message.id or user.id == self.bot.user.id:
                return False
            if l and reaction.emoji == self.left:
                return True
            if r and reaction.emoji == self.right:
                return True
            return False
        return check

    @commands.command(name='screate', help=main.lang["command_ccreate_help"], description=main.lang["command_ccreate_description"], usage='<public/private> <entry fee> <name>', aliases=['sc'])
    @commands.guild_only()
    async def conquest_create(self, ctx, set_type: str, entry_fee: int, *, s_name: str):
        user = ctx.author
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if not await self.quConquest.find_member(user.id):
            if len(s_name) <= self.sname_limit and len(s_name) > 3:
                if all(x.isalnum() or x.isspace() for x in s_name):
                    set_type_lowered = set_type.lower()
                    if set_type_lowered in ('public', 'private'):
                        if entry_fee < self.minetryfee:
                            await ctx.send(lang["conquest_entry_requirement"], delete_after=15)
                        else:
                            user_data = await qulib.user_get(user.id)
                            if user_data["currency"] < entry_fee:
                                await ctx.send(lang["conquest_insufficient_funds"], delete_after=15)
                            else:
                                access_dict = {'public': SettlementAccess.Public, 'private': SettlementAccess.Private}
                                dict_input = {}
                                dict_input["entry_fee"] = entry_fee
                                dict_input["invite_string"] = await self.quConquest.get_unique_code()
                                dict_input["date_created"] = datetime.today().replace(microsecond=0)
                                dict_input["name"] = s_name
                                dict_input["type"] = access_dict[set_type_lowered]
                                user_data["currency"] -= entry_fee

                                await qulib.user_set(user.id, user_data)
                                settlement_id = await self.quConquest.create_settlement(user.id, dict_input)
                                if settlement_id:
                                    await self.quConquest.add_member(user.id, settlement_id)
                                await ctx.send(embed = discord.Embed(title=lang["conquest_create_title"], description=lang["conquest_create_success"].format(ctx.author.mention), color = self.embed_color))
                    else:
                        await ctx.send(lang["conquest_create_public_private"], delete_after=15)
                else:
                    await ctx.send(lang["conquest_invalid_settlement_name"], delete_after=15)
            else:
                await ctx.send(lang["conquest_sname_too_long"].format(self.sname_limit), delete_after=15)
        else:
            await ctx.send(lang["conquest_create_part_of"], delete_after=15)

    @commands.cooldown(5, 60, commands.BucketType.user)
    @commands.command(name='sinfo', help=main.lang["command_cinfo_help"], description=main.lang["command_cinfo_description"], usage='{user}', aliases=['si','settlement'])
    @commands.guild_only()
    async def conquest_info(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.quConquest.find_member(user.id):
            async with ctx.channel.typing():
                cdata = await self.quConquest.get_settlement('id', await self.quConquest.get_settlement_id(user.id))
                if cdata:
                    founder = ctx.guild.get_member(cdata["founderid"]) or cdata["founderid"]
                    leader = ctx.guild.get_member(cdata["leaderid"]) or cdata["leaderid"]
                    if cdata["wins"] == cdata["losses"] == 0:
                        win_ratio = 0
                    elif cdata["wins"] > 0 and cdata["losses"] == 0:
                        win_ratio = 100
                    elif cdata["losses"] > 0 and cdata["wins"] == 0:
                        win_ratio = 0
                    else:
                        win_ratio = "%.2f" % float((cdata["wins"]/(cdata["losses"]+cdata["wins"]))*100)

                    image = self.background_image.copy().convert("RGBA")
                    draw = ImageDraw.Draw(image)

                    # Text
                    settlement_level = cdata['tech_tree'][0] if cdata['tech_tree'][0] != "X" else 10
                    level_color = (255, 255, 255, 255) if settlement_level != 10 else (216, 62, 62, 255)
                    level_w, level_h = self.level_font.getsize(str(settlement_level))
                    draw.text(((33 + (85-level_w)/2), (60 + (30-level_h)/2)), str(settlement_level), fill=level_color, font=self.level_font)

                    title_w, title_h = self.title_font.getsize(lang["conquest_info_settlement"])
                    draw.text(((450 + (500-title_w)/2), (10 + (30-title_h)/2)), lang["conquest_info_settlement"], fill=(255, 255, 255, 255), font=self.title_font)
                    draw.line((515, 20 + title_h, 885, 20 + title_h), width=2, fill=(255, 255, 255, 255))

                    offset = 50
                    for line in textwrap.wrap(cdata["name"], width=30):
                        name_w, name_h = self.medium_font.getsize(line)
                        draw.text(((450 + (500-name_w)/2), (offset + (40-name_h)/2)), line, font=self.medium_font, fill=(255,255,255,255))
                        offset += self.medium_font.getsize(line)[1]

                    founder_name = (founder.name[:20] + f'..#{founder.discriminator}') if len(str(founder)) > 20 else str(founder)
                    leader_name = (leader.name[:20] + f'..#{leader.discriminator}') if len(str(leader)) > 20 else str(leader)
                    draw.text((575, 175), leader_name, fill=(255, 255, 255, 255), font=self.body_font)
                    draw.text((575, 262), founder_name, fill=(255, 255, 255, 255), font=self.body_font)
                    draw.text((620, 342),cdata["date_created"], fill=(255, 255, 255, 255), font=self.body_font)

                    population_title_w, population_title_h = self.title_font.getsize(lang["conquest_info_population"])
                    draw.text(((620 + (300-population_title_w)/2), (390 + (30-population_title_h)/2)), lang["conquest_info_population"], fill=(255, 255, 255, 255), font=self.title_font)
                    population_w, population_h = self.title_font.getsize(str(cdata["size"]))
                    draw.text(((620 + (300-population_w)/2), (425 + (30-population_h)/2)), str(cdata["size"]), fill=(255, 255, 255, 255), font=self.title_font)

                    gold_w, gold_h = self.title_font.getsize(f'{cdata["treasury"]} {lang["conquest_resources_gold"]}')
                    draw.text(((575 + (300-gold_w)/2), (480 + (30-gold_h)/2)), f'{cdata["treasury"]} {lang["conquest_resources_gold"]}', fill=(255, 255, 255, 255), font=self.title_font)

                    draw.text((580, 580), lang["conquest_wins"], fill=(255, 255, 255, 255), font=self.medium_font)
                    draw.text((755, 580), lang["conquest_losses"], fill=(255, 255, 255, 255), font=self.body_font)
                    wins_w, wins_h = self.title_font.getsize(str(cdata["wins"]))
                    draw.text(((540 + (140-wins_w)/2), (618 + (30-wins_h)/2)), str(cdata["wins"]), fill=(255, 255, 255, 255), font=self.title_font)
                    wins_w, wins_h = self.title_font.getsize(str(cdata["losses"]))
                    draw.text(((725 + (140-wins_w)/2), (618 + (30-wins_h)/2)), str(cdata["losses"]), fill=(255, 255, 255, 255), font=self.title_font)
                    win_ratio_w, win_ratio_h = self.title_font.getsize(f'{win_ratio} %')
                    draw.text(((605 + (200-win_ratio_w)/2), (682 + (30-win_ratio_h)/2)), f'{win_ratio} %', fill=(255, 255, 255, 255), font=self.title_font)

                    #Settlement Building
                    settlement_building = Image.open(os.path.join(main.bot_path, 'data', 'images', 'conquest', f'settlement-level-{settlement_level}.png'))
                    image.paste(settlement_building, (0, 0), mask=settlement_building)

                    #Trees
                    settlement_overlay = Image.open(os.path.join(main.bot_path, 'data', 'images', 'conquest', f'settlement-overlay.png'))
                    image.paste(settlement_overlay, (0, 0), mask=settlement_overlay)

                    #Settlement Access
                    access_icon = Image.open(os.path.join(main.bot_path, 'data', 'images', 'conquest', f'{cdata["type"]}-settlement.png'))
                    image.paste(access_icon, (482, 408), mask=access_icon)

                    # Sending image
                    buffer_output = io.BytesIO()                # Create buffer
                    image.save(buffer_output, format='PNG')
                    buffer_output.seek(0)

                    await ctx.send(file=discord.File(buffer_output, f'settlement-{cdata["settlement_id"]}.png'))
        else:
            await ctx.send(lang["conquest_sinfo_part_of"].format(ctx.author.mention), delete_after=15)

    @commands.group(name='join', description=main.lang["command_cjoin_description"], usage='<private/public> ...')
    async def conquest_join(self, ctx):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            guild_prefix = PrefixHandler.get_prefix(ctx.guild.id, main.prefix) if ctx.guild else main.prefix
            await ctx.send(embed = discord.Embed(title=lang["conquest_join_embed_title"], description=lang["conquest_join_embed_description"].format("\U0001f513", guild_prefix, "\U0001F512", guild_prefix), color = self.embed_color))

    @conquest_join.command(name='private', description=main.lang["command_jprivate_description"], usage="<code>", ignore_extra=True)
    async def private(self, ctx, invite_code: str):
        user = ctx.author
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        age_restriction = ctx.author.created_at + dt.timedelta(weeks=1)
        if datetime.now() < age_restriction:
            await ctx.send(lang["conquest_join_age_restriction"], delete_after=15)
        else:
            user_info = await qulib.user_get(user.id)
            cdata = await self.quConquest.get_settlement('code', invite_code)
            if cdata:
                if await self.quConquest.find_member(user.id):
                    await ctx.send(lang["conquest_join_part_of"], delete_after=15)
                elif int(user_info["currency"]) < int(cdata["entry_fee"]):
                    await ctx.send(lang["conquest_join_min_entry"].format(cdata["entry_fee"]), delete_after=15)
                else:
                    await self.quConquest.add_member(user.id, cdata["settlement_id"])
                    cdata["size"] += 1
                    cdata["treasury"] += int(cdata["entry_fee"])
                    user_info["currency"] -= int(cdata["entry_fee"])
                    await qulib.user_set(user.id, user_info)
                    await self.quConquest.update_settlement('invite', invite_code, cdata)
                    await ctx.send(embed = discord.Embed(title=lang["conquest_join_success"].format(cdata["name"]), color = self.embed_color))
            else:
                await ctx.send(lang["conquest_join_not_found"], delete_after=15)

    @conquest_join.command(name='public', description=main.lang["command_jpublic_description"], usage="<user>")
    @commands.guild_only()
    async def public(self, ctx, *, target_user: discord.User):
        user = ctx.author
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.quConquest.find_member(target_user.id):
            age_restriction = ctx.author.created_at + dt.timedelta(weeks=1)
            if datetime.now() < age_restriction:
                await ctx.send(lang["conquest_join_age_restriction"], delete_after=15)
            else:
                user_info = await qulib.user_get(user.id)
                cdata = await self.quConquest.get_settlement('member', target_user.id)
                if cdata:
                    if await self.quConquest.find_member(user.id):
                        await ctx.send(lang["conquest_join_part_of"], delete_after=15)
                    elif cdata["type"] == SettlementAccess.Private:
                        await ctx.send(lang["conquest_join_private_msg"], delete_after=15)
                    elif int(user_info["currency"]) < int(cdata["entry_fee"]):
                        await ctx.send(lang["conquest_join_min_entry"].format(cdata["entry_fee"]), delete_after=15)
                    else:
                        await self.quConquest.add_member(user.id, cdata["settlement_id"])
                        cdata["size"] += 1
                        cdata["treasury"] += int(cdata["entry_fee"])
                        user_info["currency"] -= int(cdata["entry_fee"])
                        await qulib.user_set(user.id, user_info)
                        await self.quConquest.update_settlement('id', cdata['settlement_id'], cdata)
                        await ctx.send(embed = discord.Embed(title=lang["conquest_join_success"].format(cdata["name"]), color = self.embed_color))
                else:
                    await ctx.send(lang["conquest_join_not_found"], delete_after=15)
        else:
            await ctx.send(lang["conquest_join_target_fail"], delete_after=15)

    @commands.group(name='code', description=main.lang["command_code_description"], usage='{show/new}')
    async def conquest_code(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.invoke(self.code_show)

    @commands.cooldown(5, 30, commands.BucketType.user)
    @conquest_code.command(name='show', help=main.lang["command_code_help"], description=main.lang["command_code_show_description"], ignore_extra=True)
    async def code_show(self, ctx):
        cdata = await self.quConquest.get_settlement('user', ctx.author.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if cdata and ctx.author.id == cdata["leaderid"]:
            await ctx.author.send(embed = discord.Embed(title=lang["conquest_code_success"].format(cdata["invite_string"]), color = self.embed_color))  
        else:
            await ctx.send(lang["conquest_code_fail"], delete_after=15)      

    @commands.cooldown(5, 600, commands.BucketType.user)
    @conquest_code.command(name='new', help=main.lang["command_code_help"], description=main.lang["command_code_new_description"], ignore_extra=True)
    async def code_new(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.quConquest.generate_new_code(ctx.author.id):
            new_code = await self.quConquest.get_code(ctx.author.id)
            await ctx.author.send(embed = discord.Embed(title=lang["conquest_code_new_success"].format(new_code), color = self.embed_color))
        else:
            await ctx.send(lang["conquest_code_new_fail"], delete_after=15)

    @commands.cooldown(1, 1800, commands.BucketType.user)
    @commands.command(name='attack', help=main.lang["command_cattack_help"], description=main.lang["command_cattack_description"], usage='<user>', ignore_extra=True, cooldown_after_parsing = True)
    @commands.guild_only()
    async def conquest_attack(self, ctx, *, defence_user: discord.User):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        attack_user = ctx.author
        if attack_user.id is defence_user.id:
            await ctx.send(lang["conquest_attack_self"], delete_after=15)
        elif await self.quConquest.find_member(defence_user.id):
            cdata_defence = await self.quConquest.get_settlement('id', await self.quConquest.get_settlement_id(defence_user.id))
            if cdata_defence:
                cdata_offence = await self.quConquest.get_settlement('user', attack_user.id)
                if cdata_offence:
                    attack_score = (cdata_offence["size"] + (1/4)*cdata_offence["tech_attack"])/(cdata_defence["size"] + (1/4)*cdata_defence["tech_defence"])
                    attack_score_calculated = (50*attack_score)*100 if attack_score <=1 else (50 + 8.35*attack_score)*100
                    if attack_score_calculated > 10000:
                        attack_score_calculated = 10000
                    result = rand_generator.randint(0,10000)
                    experience = math.ceil((10000-result)/10)
                    result_loot = math.ceil((1/20)*cdata_defence["treasury"])
                    win_percentage = "%.2f" % float(attack_score_calculated/100)

                    if result <= attack_score_calculated:
                        result_text = lang["conquest_attack_result_victory"]
                        outcome_string = "win"
                        cdata_offence["experience"] += experience
                        cdata_offence["wins"] += 1
                        cdata_offence["treasury"] += result_loot
                        cdata_defence["treasury"] -= result_loot
                        cdata_defence["losses"] += 1
                    else:
                        result_text = lang["conquest_attack_result_defeat"]
                        outcome_string = "defeat"
                        cdata_defence["experience"] += math.ceil(experience/10)
                        cdata_defence["wins"] += 1
                        cdata_offence["losses"] += 1
                        experience = 0
                        result_loot = 0

                    image = self.attack_image.copy().convert("RGBA")
                    draw = ImageDraw.Draw(image)

                    settlement_level_offence = cdata_offence['tech_tree'][0] if cdata_offence['tech_tree'][0] != "X" else 10
                    settlement_level_defence = cdata_defence['tech_tree'][0] if cdata_defence['tech_tree'][0] != "X" else 10

                    #Text
                    result_w, result_h = self.title_font.getsize(result_text)
                    draw.text(((520 + (210-result_w)/2), (468 + (30-result_h)/2)), result_text, fill=(255, 255, 255, 255), font=self.title_font)

                    win_percent_w, win_percent_h = self.medium_font.getsize(f'{win_percentage} %')
                    draw.text(((775 + (115-win_percent_w)/2), (468 + (30-win_percent_h)/2)), f'{win_percentage} %', fill=(255, 255, 255, 255), font=self.medium_font)

                    roll_w, roll_h = self.title_font.getsize(str(result))
                    draw.text(((575 + (300-roll_w)/2), (545 + (30-roll_h)/2)), str(result), fill=(255, 255, 255, 255), font=self.title_font)

                    gold_title_w, gold_title_h = self.title_font.getsize(lang["conquest_pillaged_gold"])
                    draw.text(((620 + (300-gold_title_w)/2), (596 + (30-gold_title_h)/2)), lang["conquest_pillaged_gold"], fill=(255, 255, 255, 255), font=self.title_font)
                    gold_w, gold_h = self.title_font.getsize(f'{result_loot} G')
                    draw.text(((620 + (300-gold_w)/2), (631 + (30-gold_h)/2)), f'{result_loot} G', fill=(255, 255, 255, 255), font=self.title_font)

                    exp_w, exp_h = self.title_font.getsize(f'{experience} {lang["exp_string"]}')
                    draw.text(((575 + (300-exp_w)/2), (685 + (30-exp_h)/2)), f'{experience} {lang["exp_string"]}', fill=(255, 255, 255, 255), font=self.title_font)

                    # Level
                    level_color_offence = (255, 255, 255, 255) if settlement_level_offence != 10 else (216, 62, 62, 255)
                    level_color_defence = (255, 255, 255, 255) if settlement_level_defence != 10 else (216, 62, 62, 255)
                    level_w_offence, level_h_offence = self.level_font.getsize(str(settlement_level_offence))
                    level_w_defence, level_h_defence = self.level_font.getsize(str(settlement_level_defence))
                    draw.text(((70 + (85-level_w_offence)/2), (60 + (30-level_h_offence)/2)), str(settlement_level_offence), fill=level_color_offence, font=self.level_font)
                    draw.text(((1237 + (85-level_w_defence)/2), (60 + (30-level_h_defence)/2)), str(settlement_level_defence), fill=level_color_defence, font=self.level_font)

                    #Settlement Building
                    settlement_building_offence = Image.open(os.path.join(main.bot_path, 'data', 'images', 'conquest', f'settlement-level-{settlement_level_offence}.png'))
                    settlement_building_defence = Image.open(os.path.join(main.bot_path, 'data', 'images', 'conquest', f'settlement-level-{settlement_level_defence}.png'))
                    image.paste(settlement_building_offence, (0, 0), mask=settlement_building_offence)
                    image.paste(settlement_building_defence, (950, 0), mask=settlement_building_defence)

                    #Trees
                    settlement_overlay = Image.open(os.path.join(main.bot_path, 'data', 'images', 'conquest', f'settlement-overlay.png'))
                    image.paste(settlement_overlay, (0, 0), mask=settlement_overlay)
                    image.paste(settlement_overlay, (950, 0), mask=settlement_overlay)

                    # Sending image
                    buffer_output = io.BytesIO()                # Create buffer
                    image.save(buffer_output, format='PNG')
                    buffer_output.seek(0)

                    result_string = lang[f"conquest_{outcome_string}_string_{math.ceil(result/2000)}"].format(cdata_defence["name"])
                    embed = discord.Embed(title=f'{cdata_offence["name"]} **VS** {cdata_defence["name"]}', description=f'Result: **{result_text}**', colour=self.embed_color)
                    embed.add_field(name="Summary", value=result_string)
                    embed.set_image(url=f'attachment://attack-{cdata_offence["settlement_id"]}-{cdata_defence["settlement_id"]}.png')
                    await ctx.send(file=discord.File(buffer_output, f'attack-{cdata_offence["settlement_id"]}-{cdata_defence["settlement_id"]}.png'), embed=embed)

                    await self.quConquest.update_settlement('invite', cdata_offence["invite_string"], cdata_offence)
                    await self.quConquest.update_settlement('invite', cdata_defence["invite_string"], cdata_defence)
                    return
                else:
                    await ctx.send(lang["conquest_attack_you_no"], delete_after=15)
            else:
                await ctx.send(lang["conquest_attack_enemy_no"], delete_after=15)
        else:
            await ctx.send(lang["conquest_attack_enemy_part_of"], delete_after=15)
        self.bot.get_command(ctx.command.name).reset_cooldown(ctx)

    @commands.cooldown(5, 60, commands.BucketType.user)
    @commands.command(name="sleaderboard", help=main.lang["command_sleaderboard_help"], description=main.lang["command_sleaderboard_description"], usage="{page}", aliases=['slb'], ignore_extra=True)
    @commands.guild_only()
    async def conquest_leaderboard(self, ctx, page: int = 1):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        leaderboard_data = await self.quConquest.get_leaderboard()
        if len(leaderboard_data) > 0:
            last_index = math.floor(len(leaderboard_data)/10)
            if len(leaderboard_data) % 10 == 0:
                last_index -= 1
            page = min(last_index, (page - 1)) if page and page >= 1 else 0
            index = page
            
            member_rank = await self.quConquest.get_rank(ctx.author.id)
            msg = None
            action = ctx.send
            try:
                while True:
                    output = f'{lang["conquest_leaderboard_description"].format(ctx.guild.name)}\n' + f'{lang["conquest_leaderboard_ranked"].format(member_rank)}\n\n' if member_rank else '\n'
                    for item in leaderboard_data[(index*10):(index*10 + 10)]:
                        output += f'**#{item[3]}** {item[1]} [{lang["id_string"]}: {item[0]}] - **{item[2]} {lang["exp_string"]}**\n'
                    embed = discord.Embed(title=lang["conquest_leaderboard_title"], description=output, color = self.embed_color)
                    if last_index == 0:
                        await ctx.send(embed=embed)
                        return
                    embed.set_footer(text=f"{lang['page_string']} {index+1}/{last_index+1}")
                    res = await action(embed=embed)
                    if res is not None:
                        msg = res
                    l = index != 0
                    r = index != last_index
                    await msg.add_reaction(self.left)
                    if l:
                        await msg.add_reaction(self.left)
                    if r:
                        await msg.add_reaction(self.right)

                    react = (await self.bot.wait_for('reaction_add', check=self.predicate(msg, l, r), timeout=30.0))[0]
                    if react.emoji == self.left:
                        index -= 1
                    elif react.emoji == self.right:
                        index += 1
                    action = msg.edit
            except asyncio.TimeoutError:
                await msg.add_reaction(self.pagination_timeout)
                return
        else:
            await ctx.send(lang["conquest_leaderboard_empty"], delete_after=15)

    @commands.command(name="sleave", help=main.lang["command_sleave_help"], description=main.lang["command_sleave_description"], ignore_extra=True)
    async def conquest_leave(self, ctx):
        user = ctx.author
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.quConquest.find_member(user.id):
            cdata = await self.quConquest.get_settlement('member', user.id)
            if cdata:
                if cdata["size"] > 1 and user.id == cdata["leaderid"]:
                    await ctx.send(lang["conquest_leave_leader"], delete_after=15)
                else:
                    await ctx.send(embed = discord.Embed(title=lang["conquest_leave_confirmation_title"],
                                   description=(lang["conquest_leave_confirmation_description"] + f'\n\n**{lang["conquest_leave_single"]}**' if cdata["size"] == 1 else ''),
                                   color = self.embed_color))
                    try:
                        msg = await self.bot.wait_for('message', check=lambda m: (m.content.lower() in ['yes', 'y', 'no', 'n']) and m.channel == ctx.channel and m.author == ctx.author, timeout=60.0)
                        if msg.content.lower() == 'yes' or msg.content.lower() == 'y':
                            if cdata["size"] > 1:
                                    cdata["size"] -= 1
                                    await self.quConquest.update_settlement('id', cdata['settlement_id'], cdata)          
                            else:
                                await self.quConquest.delete_settlement(cdata['settlement_id'])
                            await self.quConquest.remove_member(user.id)
                            await ctx.send(embed = discord.Embed(title=lang["conquest_leave_success"], color = self.embed_color))  
                        else:
                            await ctx.send(lang["wait_for_cancelled"], delete_after=15)
                    except asyncio.TimeoutError:
                        await ctx.send(lang["wait_for_timeout"], delete_after=15)
            else:
                await ctx.send(lang["conquest_leave_not_found"], delete_after=15)
        else:
            await ctx.send(lang["conquest_not_part_of"], delete_after=15)

    @commands.command(name="promote", help=main.lang["command_promote_help"], description=main.lang["command_promote_description"], usage='<user>')
    @commands.guild_only()
    async def conquest_promote(self, ctx, *, user: discord.User):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if user != ctx.author:
            if await self.quConquest.find_member(ctx.author.id):
                cdata = await self.quConquest.get_settlement('member', ctx.author.id)
                if await self.quConquest.find_member(user.id):
                    if cdata['settlement_id'] == await self.quConquest.get_settlement_id(user.id):
                        if ctx.author.id == cdata["leaderid"]:
                            await ctx.send(embed = discord.Embed(title=lang["conquest_promote_confirmation"].format(user), color = self.embed_color))
                            try:
                                msg = await self.bot.wait_for('message', check=lambda m: (m.content.lower() in ['yes', 'y', 'no', 'n']) and m.channel == ctx.channel and m.author == ctx.author, timeout=60.0)
                                if msg.content.lower() == 'yes' or msg.content.lower() == 'y':
                                    cdata["leaderid"] = user.id
                                    await self.quConquest.update_settlement('id', cdata['settlement_id'], cdata)
                                    await ctx.send(embed = discord.Embed(title=lang["conquest_promote_success"].format(user), color = self.embed_color))
                                else:
                                    await ctx.send(lang["wait_for_cancelled"], delete_after=15)
                            except asyncio.TimeoutError:
                                await ctx.send(lang["wait_for_timeout"], delete_after=15)
                        else:
                            await ctx.send(lang["conquest_not_leader"], delete_after=15)
                    else:
                        await ctx.send(lang["conquest_promote_settlement_fail"], delete_after=15)
                else:
                    await ctx.send(lang["conquest_target_not_part_of"], delete_after=15)
            else:
                await ctx.send(lang["conquest_not_part_of"], delete_after=15)
        else:
            await ctx.send(lang["conquest_promote_self"], delete_after=15)

    @commands.command(name='skick', help=main.lang["command_sleader"], description=main.lang["command_skick_description"], usage='<user>')
    @commands.guild_only()
    async def conquest_kick(self, ctx, *, user: discord.User):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if user != ctx.author:
            if await self.quConquest.find_member(ctx.author.id):
                cdata = await self.quConquest.get_settlement('member', ctx.author.id)
                if await self.quConquest.find_member(user.id):
                    if ctx.author.id == cdata["leaderid"]:
                        cdata["size"] -= 1
                        await self.quConquest.update_settlement('id', cdata['settlement_id'], cdata)
                        await self.quConquest.remove_member(user.id)
                        await ctx.send(embed = discord.Embed(title=lang["conquest_skick_success"].format(user), color = self.embed_color))
                    else:
                        await ctx.send(lang["conquest_not_leader"], delete_after=15)
                else:
                    await ctx.send(lang["conquest_target_not_part_of"], delete_after=15)
            else:
                await ctx.send(lang["conquest_not_part_of"], delete_after=15)
        else:
            await ctx.send(lang["conquest_skick_self"], delete_after=15)

    @commands.command(name='resources', description=main.lang["command_resources_description"], ignore_extra=True)
    async def conquest_resources(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.quConquest.find_member(ctx.author.id):
            settlement_id = await self.quConquest.get_settlement_id(ctx.author.id)
            cdata = await self.quConquest.get_settlement('id', settlement_id)
            if ctx.author.id == cdata["leaderid"]:
                resources = await self.quConquest.get_resources(settlement_id)
                if resources:
                    json_data = await qulib.data_get()
                    embed = discord.Embed(title=lang["conquest_warehouse_title"].format(cdata["name"]), color=self.embed_color)
                    embed.set_thumbnail(url=json_data['Conquest']['resources_image'])
                    embed.add_field(name=lang["conquest_resources_gold"], value=f'{cdata["treasury"]} {json_data["Conquest"]["gold_icon"]}',inline=True)
                    embed.add_field(name=f'{lang["conquest_resources_wood"]} (+{await self.quConquest.get_resource_production_rate(8, settlement_id)}/{lang["day_string"]})',
                                    value=f'{resources["wood"]} {json_data["Conquest"]["resources_wood"]}',inline=True)
                    embed.add_field(name=f'{lang["conquest_resources_stone"]} (+{await self.quConquest.get_resource_production_rate(5, settlement_id)}/{lang["day_string"]})',
                                    value=f'{resources["stone"]} {json_data["Conquest"]["resources_stone"]}',inline=True)
                    embed.add_field(name=f'{lang["conquest_resources_food"]} (+{await self.quConquest.get_resource_production_rate(6, settlement_id)}/{lang["day_string"]})',
                                    value=f'{resources["food"]} {json_data["Conquest"]["resources_food"]}',inline=True)
                    embed.add_field(name=f'{lang["conquest_resources_cloth"]}  (+{await self.quConquest.get_resource_production_rate(7, settlement_id)}/{lang["day_string"]})',
                                    value=f'{resources["cloth"]} {json_data["Conquest"]["resources_cloth"]}',inline=True)
            else:
                embed = discord.Embed(title=lang["conquest_not_leader"], color = self.embed_color)
        else:
            embed = discord.Embed(title=lang["conquest_not_part_of"], color = self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(2, 30, commands.BucketType.user)
    @commands.group(name='buildings', invoke_without_command=True, description=main.lang["command_buildings_description"], aliases=['building'])
    async def conquest_buildings(self, ctx, building_id: int = None):
        if not ctx.invoked_subcommand:
            await self.buildings_list(ctx, building_id)

    @commands.cooldown(2, 30, commands.BucketType.user)
    @conquest_buildings.command(name='list', description=main.lang["command_blist_description"], ignore_extra=True)
    async def buildings_list(self, ctx, building_id: int = None):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.quConquest.find_member(ctx.author.id):
            cdata = await self.quConquest.get_settlement('member', ctx.author.id)
            json_data = await qulib.data_get()
            buildings = await self.quConquest.get_buildings()
            embed = discord.Embed(title=lang["conquest_buildings_title"], color=self.embed_color)
            th_level = await self.quConquest.level_converter(cdata["tech_tree"][0])

            last_index = len(buildings) - 1
            if building_id and building_id > 0:
                building_id = last_index if building_id > (len(buildings) - 1) else (building_id - 1)
            else:
                building_id = 0
            index = start_index = building_id
                
            msg = None
            action = ctx.send
            try:
                while True:
                    level = await self.quConquest.level_converter(cdata["tech_tree"][index])
                    upgrade_requirements = ""
                    if level == 10 or (level == 1 and (index+1) in (3, 9)):
                        level_string = f"{lang['level_string']} {level} **(MAX)**"
                    else:
                        gold = f"{pow(2, level+1)*buildings[index]['mltplr_gold']} {json_data['Conquest']['gold_icon']}" if buildings[index]['mltplr_gold'] != 0 else ""
                        wood = f"{pow(level+1, 2)*(level+1)*buildings[index]['mltplr_wood']} {json_data['Conquest']['resources_wood']}" if (buildings[index]['mltplr_wood'] != 0) else ""
                        stone = f"{pow(level+1, 2)*(level+1)*buildings[index]['mltplr_stone']} {json_data['Conquest']['resources_stone']}" if (buildings[index]['mltplr_stone'] != 0) else ""
                        food = f"{pow(level+1, 2)*(level+1)*buildings[index]['mltplr_food']} {json_data['Conquest']['resources_food']}" if (buildings[index]['mltplr_food'] != 0) else ""
                        cloth = f"{pow(level+1, 2)*(level+1)*buildings[index]['mltplr_cloth']} {json_data['Conquest']['resources_cloth']}" if (buildings[index]['mltplr_cloth'] != 0) else ""
                        if int(level) == 0 and index in (0,4,5,6,7):
                            wood = stone = food = cloth = ""
                        level_string = f"{lang['level_string']} {level} ⮕ {int(level)+1}"
                        upgrade_requirements = f'*{lang["conquest_upgrade_th"]}*' if (index > 0 and ((level+1) > int(th_level))) else f'**{lang["conquest_resources_needed"]}:** {gold} {wood} {stone} {food} {cloth}'

                    embed = discord.Embed(title=f"{index+1} ) {buildings[index]['name']} | Status", color=self.embed_color)
                    embed.set_thumbnail(url=json_data['Conquest'][f'building_icon_{index+1}'])
                    embed.add_field(name=lang["conquest_building_next_upgrade"], value=f'{level_string}\n{upgrade_requirements}', inline=False)
                    embed.add_field(name=lang["description_string"], value=lang[f"conquest_building_description_{index+1}"], inline=False)
                    embed.set_footer(text=f"{lang['conquest_building_string']} {index+1}/{last_index+1} - {cdata['name']}" if start_index != last_index else cdata['name'])
                    if start_index == last_index and len(buildings) == 1:
                        await ctx.send(embed=embed)
                        return
                    res = await action(embed=embed)
                    if res is not None:
                        msg = res
                    l = index != 0
                    r = index != last_index
                    await msg.add_reaction(self.left)
                    if l:
                        await msg.add_reaction(self.left)
                    if r:
                        await msg.add_reaction(self.right)

                    react = (await self.bot.wait_for('reaction_add', check=self.predicate(msg, l, r), timeout=30.0))[0]
                    if react.emoji == self.left:
                        index -= 1
                    elif react.emoji == self.right:
                        index += 1
                    action = msg.edit
            except asyncio.TimeoutError:
                await msg.add_reaction(self.pagination_timeout)
                return
        else:
            embed = discord.Embed(title=lang["conquest_not_part_of"], color = self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(2, 30, commands.BucketType.user)
    @conquest_buildings.command(name='compact', description=main.lang["command_blist_description"], ignore_extra=True)
    async def buildings_list_compact(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.quConquest.find_member(ctx.author.id):
            cdata = await self.quConquest.get_settlement('member', ctx.author.id)
            json_data = await qulib.data_get()
            buildings = await self.quConquest.get_buildings()
            embed = discord.Embed(title=lang["conquest_buildings_title"], color=self.embed_color)
            embed.set_footer(text=lang["conquest_settlement_footer"].format(cdata['name']))
            th_level = await self.quConquest.level_converter(cdata["tech_tree"][0])
            for i in range(len(buildings)):
                level = await self.quConquest.level_converter(cdata["tech_tree"][i])
                if level == 10 or (level == 1 and (i+1) in (3, 9)):
                    embed.add_field(name=f"**{i+1} ) {buildings[i]['name']}: {lang['level_string']} {level}** *MAX*", value=lang["conquest_max_reached"],inline=False)
                else:
                    gold = f"{pow(2, level+1)*buildings[i]['mltplr_gold']} {json_data['Conquest']['gold_icon']}" if buildings[i]['mltplr_gold'] != 0 else ""
                    wood = f"{pow(level+1, 2)*(level+1)*buildings[i]['mltplr_wood']} {json_data['Conquest']['resources_wood']}" if (buildings[i]['mltplr_wood'] != 0) else ""
                    stone = f"{pow(level+1, 2)*(level+1)*buildings[i]['mltplr_stone']} {json_data['Conquest']['resources_stone']}" if (buildings[i]['mltplr_stone'] != 0) else ""
                    food = f"{pow(level+1, 2)*(level+1)*buildings[i]['mltplr_food']} {json_data['Conquest']['resources_food']}" if (buildings[i]['mltplr_food'] != 0) else ""
                    cloth = f"{pow(level+1, 2)*(level+1)*buildings[i]['mltplr_cloth']} {json_data['Conquest']['resources_cloth']}" if (buildings[i]['mltplr_cloth'] != 0) else ""
                    if int(level) == 0 and i in (0,4,5,6,7):
                        wood = stone = food = cloth = ""
                    if i > 0 and ((level+1) > int(th_level)):
                        embed.add_field(name=f"**{i+1} ) {buildings[i]['name']}: {lang['level_string']} {level}** ⮕ {int(level)+1}",
                                        value=f'*{lang["conquest_upgrade_th"]}*',inline=False)
                    else:
                        embed.add_field(name=f"**{i+1} ) {buildings[i]['name']}: {lang['level_string']} {level}** ⮕ {int(level)+1}",
                                        value=f"**{lang['conquest_resources_needed']}:** {gold} {wood} {stone} {food} {cloth}",inline=False)
        else:
            embed = discord.Embed(title=lang["conquest_not_part_of"], color = self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(5, 30, commands.BucketType.user)
    @conquest_buildings.command(name='upgrade', help=main.lang["command_sleader"], description=main.lang["command_bupgrade_description"], usage='<building id>', ignore_extra=True)
    async def buildings_upgrade(self, ctx, building_id: int):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if 1 <= building_id <=10:
            if await self.quConquest.find_member(ctx.author.id):
                cdata = await self.quConquest.get_settlement('member', ctx.author.id)
                if ctx.author.id == cdata["leaderid"]:
                    building = await self.quConquest.get_building(building_id)
                    resources = await self.quConquest.get_resources(cdata['settlement_id'])
                    level = int(cdata["tech_tree"][building_id-1]) if cdata['tech_tree'][building_id-1] != "X" else 10
                    th_level = cdata['tech_tree'][0] if cdata['tech_tree'][0] != "X" else 10
                    if (level+1) <= int(th_level) or (building_id == 1):
                        if level != 10:
                            if level == 1 and building_id in (3, 9):
                                await ctx.send(lang["conquest_upgrade_max_level"], delete_after=15)
                            else:
                                gold = pow(2, int(level)+1)*building['gold']
                                wood = pow(int(level)+1, 2)*(level+1)*building['wood']
                                stone = pow(int(level)+1, 2)*(level+1)*building['stone']
                                food = pow(int(level)+1, 2)*(level+1)*building['food']
                                cloth = pow(int(level)+1, 2)*(level+1)*building['cloth']

                                if (building_id in (1,5,6,7,8) and level == 0):
                                    wood = stone = food = cloth = 0

                                if (cdata['treasury']>=gold and resources['cloth']>=cloth and resources['stone']>=stone and resources['food']>=food and resources['wood']>=wood):
                                    tech_tree = list(cdata['tech_tree'])
                                    tech_tree[building_id-1] = str(level+1) if (level+1) != 10 else "X"
                                    cdata['tech_tree'] = "".join(tech_tree)
                                    cdata['treasury'] -= gold
                                    resources['cloth'] -= cloth
                                    resources['food'] -= food
                                    resources['stone'] -= stone
                                    resources['wood'] -= wood
                                    await self.quConquest.update_resources(cdata['settlement_id'], resources)
                                    await self.quConquest.update_settlement('id', cdata['settlement_id'], cdata)
                                    await self.quConquest.upgrade_building(cdata['settlement_id'], building_id)
                                    await ctx.send(embed = discord.Embed(title=lang["conquest_upgrade_success"].format(building['name'], level+1), color=self.embed_color))
                                else:
                                    await ctx.send(lang["conquest_upgrade_fail"].format(building['name']), delete_after=15)
                        else:
                            await ctx.send(lang["conquest_upgrade_max_level"], delete_after=15)
                    else:
                        await ctx.send(lang["conquest_upgrade_th"], delete_after=15)
                else:
                    await ctx.send(lang["conquest_not_leader"], delete_after=15)
            else:
                await ctx.send(lang["conquest_not_part_of"], delete_after=15)
        else:
            await ctx.send(lang["conquest_requirements_range"], delete_after=15)

    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.command(name='requirements', description=main.lang["command_reqs_description"], usage="<building id>", aliases=['reqs'])
    async def conquest_requirements(self, ctx, *, building_id: int):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if 1 <= building_id <=10:
            if await self.quConquest.find_member(ctx.author.id):
                json_data = await qulib.data_get()
                building = await self.quConquest.get_building(building_id)
                description = f"**{lang['conquest_requirements_header']}**\n"
                for level in range(0, 10):
                    gold = f"{pow(2, int(level)+1)*building['gold']} {json_data['Conquest']['gold_icon']}" if building['gold'] != 0 else ""
                    wood = f"{pow(int(level)+1, 2)*(level+1)*building['wood']} {json_data['Conquest']['resources_wood']}" if (building['wood'] != 0) else ""
                    stone = f"{pow(int(level)+1, 2)*(level+1)*building['stone']} {json_data['Conquest']['resources_stone']}" if (building['stone'] != 0) else ""
                    food = f"{pow(int(level)+1, 2)*(level+1)*building['food']} {json_data['Conquest']['resources_food']}" if (building['food'] != 0) else ""
                    cloth = f"{pow(int(level)+1, 2)*(level+1)*building['cloth']} {json_data['Conquest']['resources_cloth']}" if (building['cloth'] != 0) else ""
                    if level == 0 and building_id in (1,5,6,7,8):
                        wood = stone = food = cloth = ""
                    description += f"**{lang['level_string']} {level} ⮕ {int(level)+1}:** {gold} {wood} {stone} {food} {cloth}\n"
                    if building_id in (3, 9):
                        break
                await ctx.send(embed = discord.Embed(title=lang["conquest_requirements_title"].format(building['name']), description=description, color=self.embed_color))
            else:
                await ctx.send(lang["conquest_not_part_of"], delete_after=15)
        else:
            await ctx.send(lang["conquest_requirements_range"], delete_after=15)

    @commands.cooldown(5, 30, commands.BucketType.user)
    @commands.group(name='market', help=main.lang["command_market_help"], description=main.lang["command_market_description"])
    async def conquest_market(self, ctx):
        if not ctx.invoked_subcommand:
            json_data = await qulib.data_get()
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            embed = discord.Embed(title=lang["conquest_market_title"], color=self.embed_color)
            embed.set_thumbnail(url=json_data['Conquest']['market_image'])
            embed.add_field(name=f"1 )  {json_data['Conquest']['resources_cloth']} **{lang['conquest_resources_cloth']}**",
                            value=f"{lang['conquest_sell_price']}: **{self.daily_cloth_price}  {json_data['Conquest']['gold_icon']} /{lang['conquest_piece']}**",inline=False)
            embed.add_field(name=f"2 )  {json_data['Conquest']['resources_wood']} **{lang['conquest_resources_wood']}**",
                            value=f"{lang['conquest_sell_price']}: **{self.daily_wood_price}  {json_data['Conquest']['gold_icon']} /{lang['conquest_piece']}**",inline=False)
            embed.add_field(name=f"3 )  {json_data['Conquest']['resources_stone']} **{lang['conquest_resources_stone']}**",
                            value=f"{lang['conquest_sell_price']}: **{self.daily_stone_price}  {json_data['Conquest']['gold_icon']} /{lang['conquest_piece']}**",inline=False)
            embed.add_field(name=f"4 )  {json_data['Conquest']['resources_food']} **{lang['conquest_resources_food']}**",
                            value=f"{lang['conquest_sell_price']}: **{self.daily_food_price}  {json_data['Conquest']['gold_icon']} /{lang['conquest_piece']}**",inline=False)
            embed.set_footer(text=lang["conquest_market_reminder"])
            await ctx.send(embed=embed)

    @conquest_market.command(name='sell', help=main.lang["command_sleader"], description=main.lang["command_msell_description"], usage='<resource> <amount>')
    async def market_sell(self, ctx, item: str, quantity: int):
        if item.lower() in ("cloth", "wood", "stone", "food", "1", "2", "3", "4"):
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if await self.quConquest.find_member(ctx.author.id):
                cdata = await self.quConquest.get_settlement('member', ctx.author.id)
                if cdata['tech_tree'][2] == "1":
                    if ctx.author.id == cdata["leaderid"]:
                        json_data = await qulib.data_get()
                        resources_dict = {"1":"cloth", "2":"wood", "3":"stone", "4":"food"}
                        prices_dict = {"cloth":self.daily_cloth_price, "wood":self.daily_wood_price, "stone":self.daily_stone_price, "food":self.daily_food_price}
                        resources = await self.quConquest.get_resources(cdata['settlement_id'])
                        index = resources_dict[item] if item in resources_dict else item
                        if quantity > 0 and quantity <= resources[index]:
                            resources[index] -= quantity
                            cdata['treasury'] += quantity*prices_dict[index]
                            await self.quConquest.update_resources(cdata['settlement_id'], resources)
                            await self.quConquest.update_settlement("id", cdata['settlement_id'], cdata)
                            await ctx.send(embed = discord.Embed(title=lang["conquest_market_sell_success"].format(quantity, index, quantity*prices_dict[index], json_data['Conquest']['gold_icon']), color = self.embed_color))
                        else:
                            await ctx.send(lang["conquest_market_sell_fail"], delete_after=15)
                    else:
                        await ctx.send(lang["conquest_not_leader"], delete_after=15)
                else:
                    await ctx.send(lang["conquest_sell_no_market"], delete_after=15)
            else:
                await ctx.send(lang["conquest_not_part_of"], delete_after=15)

    @conquest_market.command(name='buy', help=main.lang["command_sleader"], description=main.lang["command_mbuy_description"], usage='<resource> <amount>')
    async def market_buy(self, ctx, item: str, quantity: int):
        if item.lower() in ("cloth", "wood", "stone", "food", "1", "2", "3", "4"):
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if await self.quConquest.find_member(ctx.author.id):
                cdata = await self.quConquest.get_settlement('member', ctx.author.id)
                if cdata['tech_tree'][2] == "1":
                    if ctx.author.id == cdata["leaderid"]:
                        json_data = await qulib.data_get()
                        resources_dict = {"1":"cloth", "2":"wood", "3":"stone", "4":"food"}
                        prices_dict = {"cloth":self.daily_cloth_price, "wood":self.daily_wood_price, "stone":self.daily_stone_price, "food":self.daily_food_price}
                        resources = await self.quConquest.get_resources(cdata['settlement_id'])
                        index = resources_dict[item] if item in resources_dict else item
                        if quantity > 0 and quantity*prices_dict[index] <= cdata['treasury']:
                            if int(cdata['tech_tree'][8]) == 0 and (resources[index] + quantity) > 1000:
                                await ctx.send(lang["conquest_market_buy_warehouse"], delete_after=15)
                            else:
                                resources[index] += quantity
                                cdata['treasury'] -= quantity*prices_dict[index]
                                await self.quConquest.update_resources(cdata['settlement_id'], resources)
                                await self.quConquest.update_settlement("id", cdata['settlement_id'], cdata)
                                await ctx.send(embed = discord.Embed(title=lang["conquest_market_buy_success"].format(quantity, index, quantity*prices_dict[index], json_data['Conquest']['gold_icon']), color = self.embed_color))
                        else:
                            await ctx.send(lang["conquest_market_buy_fail"], delete_after=15)
                    else:
                        await ctx.send(lang["conquest_not_leader"], delete_after=15)
                else:
                    await ctx.send(lang["conquest_buy_no_market"], delete_after=15)
            else:
                await ctx.send(lang["conquest_not_part_of"], delete_after=15)

    @commands.cooldown(5, 60, commands.BucketType.user)
    @commands.command(name="deposit", help=main.lang["command_deposit_help"], description=main.lang["command_deposit_description"], usage='<amount>')
    async def conquest_deposit(self, ctx, number: int):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.quConquest.find_member(ctx.author.id):
            settlement_id = await self.quConquest.get_settlement_id(ctx.author.id)
            cdata = await self.quConquest.get_settlement('id', settlement_id)
            author_info = await qulib.user_get(ctx.author.id)
            json_data = await qulib.data_get()
            if number > 0:
                if author_info['currency'] <= 0 or number > author_info['currency']:
                    await ctx.send(lang["economy_insufficient_funds"], delete_after=15)
                else:
                    author_info['currency'] -= number
                    cdata['treasury'] += number
                    await qulib.user_set(ctx.author.id, author_info)
                    await self.quConquest.update_settlement("id", settlement_id, cdata)
                    await ctx.send(embed = discord.Embed(title=lang["conquest_deposit_success"].format(number, json_data['Conquest']['gold_icon']), color=self.embed_color))
        else:
            await ctx.send(lang["conquest_not_part_of"], delete_after=15)

    @commands.cooldown(5, 60, commands.BucketType.user)
    @commands.command(name='rename', help=main.lang["command_srename_help"], description=main.lang["command_srename_description"], usage='<new name>')
    async def conquest_settlement_rename(self, ctx, *, name: str):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if len(name) <= self.sname_limit  and len(name) > 3:
            if all(x.isalnum() or x.isspace() for x in name):
                if await self.quConquest.find_member(ctx.author.id):
                    cdata = await self.quConquest.get_settlement('member', ctx.author.id)
                    if ctx.author.id == cdata["leaderid"]:
                        json_data = await qulib.data_get()
                        if cdata['treasury'] >= self.rename_price:
                            cdata['name'] = name
                            cdata['treasury'] -= self.rename_price
                            await self.quConquest.update_settlement("id", cdata['settlement_id'], cdata)
                            await ctx.send(embed = discord.Embed(title=lang["conquest_rename_success"].format(name, self.rename_price, json_data['Conquest']['gold_icon']), color = self.embed_color))
                        else:
                            await ctx.send(lang["conquest_rename_no_funds"].format(self.rename_price, json_data['Conquest']['gold_icon']), delete_after=15)
                    else:
                        await ctx.send(lang["conquest_not_leader"], delete_after=15)
                else:
                    await ctx.send(lang["conquest_not_part_of"], delete_after=15)
            else:
                await ctx.send(lang["conquest_invalid_settlement_name"], delete_after=15)
        else:
            await ctx.send(lang["conquest_sname_too_long"].format(self.sname_limit), delete_after=15)

    @commands.cooldown(5, 600, commands.BucketType.user)
    @commands.command(name='sconvert', help=main.lang["command_sconvert_help"], description=main.lang["command_sconvert_description"], ignore_extra=True)
    async def settlement_convert(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if await self.quConquest.find_member(ctx.author.id):
            cdata = await self.quConquest.get_settlement('member', ctx.author.id)
            if cdata:
                if cdata['leaderid'] == ctx.author.id:
                    cdata['type'] = SettlementAccess.Private if cdata['type'] == SettlementAccess.Public else SettlementAccess.Public
                    await self.quConquest.update_settlement("id", cdata['settlement_id'], cdata)
                    embed = discord.Embed(title=lang["conquest_convert_success"].format(SettlementAccess(cdata['type']).name.lower()), color = self.embed_color)
                    embed.set_footer(text=lang["conquest_settlement_footer"].format(cdata['name']))
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(lang["conquest_not_leader"], delete_after=15)
        else:
            await ctx.send(lang["conquest_not_part_of"], delete_after=15)

def setup(bot):
    bot.add_cog(Conquest(bot))
