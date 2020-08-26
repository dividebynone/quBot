from discord.ext import commands
from main import bot_starttime, config, bot_path
from main import modules as loaded_modules
from datetime import datetime
import libs.qulib as qulib
import urllib.request
import main
import discord
from PIL import Image, ImageDraw, ImageFont
import libs.roundedrectangles
from libs.profileshandler import ProfilesHandler, ProfileBackgrounds, LevelingToggle
from libs.prefixhandler import PrefixHandler
from libs.qulib import user_get, user_set
import configparser
import asyncio
import textwrap
import math
import io
import os

class Profiles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.module_embed_color =  0x6e78cc
        print(f'Module {self.__class__.__name__} loaded')

        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = False
        self.module_dependencies = ['Economy']

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)

        if 'Economy' not in config.sections():
            config.add_section('Economy')
            if 'CurrencySymbol' not in config['Economy']:
                config.set('Economy', 'CurrencySymbol', '💵')
        
        with open(os.path.join(bot_path, 'config.ini'), 'w', encoding="utf_8") as config_file:
            config.write(config_file)
        config_file.close()

        with open(os.path.join(bot_path, 'config.ini'), 'r', encoding="utf_8") as config_file:
            config.read_file(config_file)
            self.currency_symbol = config.get('Economy', 'CurrencySymbol')
        config_file.close()

        self.ProfilesHandler = ProfilesHandler()
        self.ProfileBackgrounds = ProfileBackgrounds()
        self.LevelingToggle = LevelingToggle()
        self.PrefixHandler = PrefixHandler()
        self.bio_char_limit = 150

        self.background_image = Image.open(os.path.join(main.bot_path, 'data', 'images', 'profile-background.jpg'))

        self.title_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'HelveticaNowMedium.ttf'), 30)
        self.medium_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'HelveticaNowBold.ttf'), 22)
        self.body_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'HelveticaNow.ttf'), 19)
        self.bio_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'OpenSans-SemiBold.ttf'), 19)

        self.avatar_size = 128
        self.levelbar_size = (375, 30)

        self.leveling_constant = 0.2
        self.experience = 5

        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 300, commands.BucketType.member)
        
        self.left = '⬅️'
        self.right = '➡️'
        self.pagination_timeout = '⏹️'
    
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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id or message.author.bot:
            return
        if not message.guild:
            return

        lang = main.get_lang(message.guild.id) if message.guild else main.lang
        cooldown = self.cd_mapping.get_bucket(message)
        retry_after = cooldown.update_rate_limit()

        if not retry_after and not LevelingToggle.is_disabled(message.guild.id):
            user_data = await ProfilesHandler.get(message.author.id, message.guild.id)

            user_data['experience'] += self.experience
            next_lvl_experience = int(math.pow((user_data['level']+1)/self.leveling_constant, 2))

            if user_data['experience'] >= next_lvl_experience:
                user_data['level'] += 1
                user_data['experience'] -= next_lvl_experience
                
                await message.channel.send(lang["profile_level_up_message"].format(message.author.mention, user_data['level']))

            await ProfilesHandler.update_experience(message.author.id, message.guild.id, user_data)
    
    @commands.cooldown(5, 30, commands.BucketType.member)
    @commands.command(name='profile', help=main.lang["command_profile_help"], description=main.lang["command_profile_description"], usage="", aliases=['p', 'me', 'level'])
    @commands.guild_only()
    async def profile(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        user_data = await ProfilesHandler.get(user.id, ctx.guild.id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang

        image = self.background_image.copy().convert("RGBA")
        draw = ImageDraw.Draw(image)

        # Custom background
        if user_data['background'] != None:
            custom_background = Image.open(os.path.join(main.bot_path, 'data', 'images', f'banner-{user_data["background"]}.jpg')).convert("RGBA")
            overlay = Image.new('RGBA', custom_background.size, (0, 0, 0, 100))
            custom_background = Image.alpha_composite(custom_background, overlay)
            image.paste(custom_background, (0, 0))

        user_title = (user.name[:25] + '..') if len(user.name) > 25 else user.name
        draw.text((175, 50), user_title, fill=(255,255,255,255), font=self.title_font)
        draw.text((180 + self.title_font.getsize(user_title)[0], 55), f'#{user.discriminator}', fill=(210, 210, 210, 255), font=self.medium_font)
        draw.text((10, 185), lang["profile_bio_title"], fill=(255,255,255,255), font=self.title_font)

        offset = 220
        user_bio = user_data['bio'] if user_data['bio'] else lang["profile_empty_bio"]

        for line in textwrap.wrap(user_bio, width=62):
            draw.text((10, offset), line, font=self.bio_font, fill=(255,255,255,255))
            offset += self.bio_font.getsize(line)[1]

        # Leveling
        user_experience = user_data['experience']
        user_level = user_data['level']
        user_next_lvl_experience = int(math.pow((user_level+1)/self.leveling_constant, 2))

        levelbar_image = Image.new('RGBA', (self.levelbar_size[0] * 3, self.levelbar_size[1] * 3), (0,0,0,0))
        levelbar_draw = ImageDraw.Draw(levelbar_image)

        levelbar_draw.rounded_rectangle([(0, 0), (self.levelbar_size[0] * 3, self.levelbar_size[1] * 3),], corner_radius=45, fill=(255, 255, 255, 255))
        if (user_experience/user_next_lvl_experience) >= 0.06 :
            levelbar_draw.rounded_rectangle([(6, 6), ((int(self.levelbar_size[0]*(user_experience/user_next_lvl_experience)) * 3) - 6, (self.levelbar_size[1]* 3) - 6),], corner_radius=39, fill=(115, 139, 215, 255))
        else:
            levelbar_draw.rounded_rectangle([(6, 6), ((int(self.levelbar_size[0]*(0.065)) * 3) - 6, (self.levelbar_size[1]* 3) - 6),], corner_radius=35, fill=(115, 139, 215, 255))

        levelbar_image = levelbar_image.resize((self.levelbar_size[0], self.levelbar_size[1]), Image.ANTIALIAS)
        image.paste(levelbar_image, (175, 92), levelbar_image)

        disabled_leveling = LevelingToggle.is_disabled(ctx.guild.id)

        xp_message = f'{user_experience}/{user_next_lvl_experience} {lang["exp_string"]}' if not disabled_leveling else lang["profile_disabled_exp"]
        xp_w, xp_h = self.body_font.getsize(xp_message)
        draw.text(((175 + (self.levelbar_size[0]-xp_w)/2), (90 + (self.levelbar_size[1]-xp_h)/2)), xp_message, fill=(0, 0, 0, 255), font=self.body_font)

        if not disabled_leveling: 
            level_message = f'{lang["level_string"]}: {user_level}'
            user_rank = await ProfilesHandler.get_rank(user.id, ctx.guild.id)
            rank_message = f'{lang["profile_rank"]}: {user_rank if user_rank else ctx.guild.member_count}'
            
            draw.text((175, 125), level_message, fill=(255, 255, 255, 255), font=self.medium_font)
            draw.text((175 + self.levelbar_size[0] - self.medium_font.getsize(rank_message)[0], 125), rank_message, fill=(255, 255, 255, 255), font=self.medium_font)

        # Avatar background
        avatarbg_size = self.avatar_size + 12
        avatarbg_image = Image.new('RGBA', (avatarbg_size, avatarbg_size), (86, 86, 86, 100))
        avatar_bigsize = (avatarbg_size * 3, avatarbg_size * 3)
        avatarbg_mask = Image.new('L', avatar_bigsize, 0)
        avatarbg_draw = ImageDraw.Draw(avatarbg_mask) 
        avatarbg_draw.ellipse((0, 0) + avatar_bigsize, fill=100)
        avatarbg_mask = avatarbg_mask.resize(avatarbg_image.size, Image.ANTIALIAS)

        image.paste(avatarbg_image, (14, 14), mask=avatarbg_mask)

        # Avatar
        avatar_asset = user.avatar_url_as(format='jpg', size=self.avatar_size)
        buffer_avatar = io.BytesIO(await avatar_asset.read())
        avatar_image = Image.open(buffer_avatar)

        # Masks
        bigsize = (avatar_image.size[0] * 3, avatar_image.size[1] * 3)
        mask = Image.new('L', bigsize, 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(avatar_image.size, Image.ANTIALIAS)
        avatar_image.putalpha(mask)

        image.paste(avatar_image, (20, 20), mask=mask)

        # Sending image
        buffer_output = io.BytesIO()                # Create buffer
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)

        await ctx.send(file=discord.File(buffer_output, 'profile.png'))

    @commands.cooldown(3, 60, commands.BucketType.member)
    @commands.command(name='bio', help=main.lang["command_bio_help"], description=main.lang["command_bio_description"], usage="Some information about me...")
    @commands.guild_only()
    async def bio_command(self, ctx, *, message: str = None):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if message:
            if len(message) <= self.bio_char_limit:
                await ProfilesHandler.set_bio(ctx.author.id, ctx.guild.id, message)
                embed = discord.Embed(title=lang["profile_bio_success"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["profile_bio_char_limit"].format(self.bio_char_limit), color=self.module_embed_color)
        else:
            await ProfilesHandler.set_bio(ctx.author.id, ctx.guild.id, None)
            embed = discord.Embed(title=lang["profile_bio_reset"], color=self.module_embed_color)
        await ctx.author.send(embed=embed)

    @commands.cooldown(5, 30, commands.BucketType.member)
    @commands.group(name='background', invoke_without_command=True, help=main.lang["command_background_help"], description=main.lang["command_background_description"], usage="General", aliases=['backgrounds', 'bg', 'bgs'])
    async def background(self, ctx, value = None):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if value is not None:
                if value.isnumeric():
                    background_info = await ProfileBackgrounds.get_background_info(value)
                    if background_info:
                        embed = discord.Embed(title=lang['profiles_background_specific_title'], description=f"{background_info['description']}\n\n**{lang['price_string']}:** {background_info['price']} {self.currency_symbol}", color=self.module_embed_color)
                        embed.set_thumbnail(url=background_info['url'])
                        embed.set_footer(text=f"{lang['category_string']}: {background_info['category']}")
                    else:
                        embed = discord.Embed(title=lang["profiles_background_specific_not_found"], color=self.module_embed_color)
                else:
                    category_info = await ProfileBackgrounds.get_category(value.capitalize())
                    if category_info:
                        index = start_index = 0
                        last_index = math.floor(len(category_info)/5)
                        unlocked_backgrounds = await ProfileBackgrounds.unlocked_backgrounds(ctx.author.id)
                         
                        msg = None
                        action = ctx.send
                        try:
                            while True:
                                description = ""
                                for background in category_info[(index*5):(index*5 + 5)]:
                                    description += f'\u2022 **{background[0]}** - {background[1]}\n\t{f"""**{lang["price_string"]}**: {background[2]} {self.currency_symbol}""" if int(background[0]) not in unlocked_backgrounds else lang["profiles_background_owned"]}\n\n'
                                embed = discord.Embed(title=lang["profiles_background_category_title"].format(value.capitalize()), description=description, color=self.module_embed_color)
                                embed.set_footer(text=f"{lang['page_string']} {index+1}/{last_index+1} - {str(ctx.author)}" if start_index != last_index else str(ctx.author))
                                if start_index == last_index:
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
                        embed = discord.Embed(title=lang["profiles_background_category_not_found"], color=self.module_embed_color)
            else:
                categories = await ProfileBackgrounds.get_categories()
                prefix = PrefixHandler.get_prefix(ctx.guild.id, main.prefix)
                embed = discord.Embed(title=lang["profiles_background_general_title"], description=lang["profiles_background_general_body"].format(', '.join(categories), prefix, prefix), color=self.module_embed_color)
                embed.set_footer(text=lang["profiles_background_footer"])
            await ctx.send(embed=embed)

    @commands.cooldown(10, 60, commands.BucketType.member)
    @background.command(name='buy', help=main.lang["command_bg_buy_help"], description=main.lang["command_bg_buy_description"], usage='3', aliases=['purchase'])
    async def background_buy(self, ctx, bg_id: int):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        user = ctx.author
        user_info = await user_get(user)
        background_info = await ProfileBackgrounds.get_background_info(bg_id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if background_info:
            if bg_id > 0:
                unlocked_backgrounds = await ProfileBackgrounds.unlocked_backgrounds(user.id)
                if not unlocked_backgrounds or bg_id not in unlocked_backgrounds:
                    if user_info['currency'] <= 0 or background_info['price'] > user_info['currency']:
                        embed = discord.Embed(title=lang["profiles_buy_insufficient_funds"].format(background_info['price'] - user_info['currency'], self.currency_symbol), color=self.module_embed_color)
                    else:
                        await ctx.send(embed = discord.Embed(title=lang["profiles_buy_confirmation"].format(background_info['price'], self.currency_symbol), color = self.module_embed_color))
                        try:
                            msg = await self.bot.wait_for('message', check=lambda m: (m.content.lower() in ['yes', 'y', 'no', 'n']) and m.channel == ctx.channel, timeout=60.0)
                            if msg.content.lower() == 'yes' or msg.content.lower() == 'y':
                                embed = discord.Embed(title=lang["profiles_buy_success"].format(bg_id, background_info['price'], self.currency_symbol), color=self.module_embed_color)
                                user_info['currency'] -= background_info['price']
                                await ProfileBackgrounds.unlock_background(user.id, bg_id)
                                await user_set(user, user_info)
                            else:
                                embed = discord.Embed(title=lang["wait_for_cancelled"], color=self.module_embed_color)
                        except asyncio.TimeoutError:
                            embed = discord.Embed(title=lang["wait_for_timeout"], color=self.module_embed_color)

                        
                else:
                    embed = discord.Embed(title=lang["profiles_buy_owned"].format(bg_id), description=background_info['description'], color=self.module_embed_color)
                    embed.set_thumbnail(url=background_info['url'])
            else:
                return
        else:
            embed = discord.Embed(title=lang["profiles_buy_not_found"], color=self.module_embed_color)
        await ctx.send(embed=embed)
    
    @commands.cooldown(3, 60, commands.BucketType.member)
    @background.command(name='inventory', help=main.lang["command_bg_inventory_help"], description=main.lang["command_bg_inventory_description"], ignore_extra=True, aliases=['inv'])
    async def background_inventory(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        unlocked_backgrounds = await ProfileBackgrounds.user_backgrounds(ctx.author.id)
        if unlocked_backgrounds:
            index = start_index = 0
            last_index = math.floor(len(unlocked_backgrounds)/5)

            msg = None
            action = ctx.send
            try:
                while True:
                    description = ""
                    for background in unlocked_backgrounds[(index*5):(index*5 + 5)]:
                        description += f'\u2022 **{background[0]}** - {background[1]}\n'
                    embed = discord.Embed(title=lang["profiles_inventory_title"].format(ctx.author.name), description=description, color=self.module_embed_color)
                    if start_index == last_index:
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
            embed = discord.Embed(title=lang["profiles_inventory_empty"], color=self.module_embed_color)
        await ctx.send(embed=embed)
    
    @commands.cooldown(10, 30, commands.BucketType.member)
    @commands.guild_only()
    @background.command(name='equip', help=main.lang["command_bg_equip_help"], description=main.lang["command_bg_equip_description"], usage='1')
    async def background_equip(self, ctx, bg_id: int = None):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if bg_id == None:
            embed = discord.Embed(title=lang["profiles_unequip_message"].format(str(ctx.author)), color=self.module_embed_color)
            await ProfilesHandler.equip_background(ctx.author.id, ctx.guild.id, bg_id)
        else:
            background_info = await ProfileBackgrounds.get_background_info(bg_id)
            if background_info:
                unlocked_backgrounds = await ProfileBackgrounds.unlocked_backgrounds(ctx.author.id)
                if bg_id in unlocked_backgrounds:
                    embed = discord.Embed(title=lang["profiles_equip_success"].format(str(ctx.author), bg_id), color=self.module_embed_color)
                    await ProfilesHandler.equip_background(ctx.author.id, ctx.guild.id, bg_id)
                else:
                    embed = discord.Embed(title=lang["profiles_equip_not_owned"], color=self.module_embed_color)
            else:
                embed = discord.Embed(title=lang["profiles_equip_not_found"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(5, 60, commands.BucketType.member)
    @commands.guild_only()
    @background.command(name='unequip', help=main.lang["empty_string"], description=main.lang["command_bg_unequip_description"], ignore_extra=True, aliases=['default'])
    async def background_unequip(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await ProfilesHandler.equip_background(ctx.author.id, ctx.guild.id, None)
        embed = discord.Embed(title=lang["profiles_unequip_message"].format(str(ctx.author)), color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(5, 60, commands.BucketType.member)
    @commands.guild_only()
    @commands.command(name='leaderboard', help=main.lang["empty_string"], description=main.lang["command_leaderboard_description"], ignore_extra=True, aliases=['lb', 'xplb', 'top'])
    async def profiles_leaderboard(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if not LevelingToggle.is_disabled(ctx.guild.id):
            leaderboard = await ProfilesHandler.leaderboard(ctx.guild.id)
            if leaderboard:
                index = start_index = 0
                last_index = math.floor(len(leaderboard)/10)

                msg = None
                action = ctx.send
                try:
                    while True:
                        description = ""
                        for person in leaderboard[(index*10):(index*10 + 10)]:
                            user = self.bot.get_user(person[0])
                            description += f"**#{person[1]} {str(user)}** ({lang['level_string']} {person[2]} : {person[3]} {lang['exp_string']})\n"
                        embed = discord.Embed(title=lang["profiles_leaderboard_title"], description=description, color=self.module_embed_color)
                        if start_index == last_index:
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
                embed = discord.Embed(title=lang["profiles_leaderboard_empty"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["profiles_leaderboard_disabled"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(5, 60, commands.BucketType.member)
    @commands.has_permissions(administrator=True)
    @commands.group(name='leveling', help=main.lang["command_leveling_help"], description=main.lang["command_leveling_toggle_description"], invoke_without_command=True)
    @commands.guild_only()
    async def leveling_toggle(self, ctx):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if not LevelingToggle.is_disabled(ctx.guild.id):
                await LevelingToggle.disable_leveling(ctx.guild.id)
                embed = discord.Embed(title=lang["profiles_leveling_disabled"], color=self.module_embed_color)
            else:
                await LevelingToggle.enable_leveling(ctx.guild.id)
                embed = discord.Embed(title=lang["profiles_leveling_enabled"], color=self.module_embed_color)
            await ctx.send(embed=embed)

    @commands.cooldown(5, 60, commands.BucketType.member)
    @commands.has_permissions(administrator=True)
    @leveling_toggle.command(name='enable', help=main.lang["command_leveling_help"], description=main.lang["command_leveling_enable_description"], aliases=['e'], ignore_extra=True)
    async def leveling_enable(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if LevelingToggle.is_disabled(ctx.guild.id):
            await LevelingToggle.enable_leveling(ctx.guild.id)
            embed = discord.Embed(title=lang["profiles_leveling_enabled"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["profiles_leveling_already_enabled"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(5, 60, commands.BucketType.member)
    @commands.has_permissions(administrator=True)
    @leveling_toggle.command(name='disable', help=main.lang["command_leveling_help"], description=main.lang["command_leveling_disable_description"], aliases=['d'], ignore_extra=True)
    async def leveling_disable(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if not LevelingToggle.is_disabled(ctx.guild.id):
            await LevelingToggle.disable_leveling(ctx.guild.id)
            embed = discord.Embed(title=lang["profiles_leveling_disabled"], color=self.module_embed_color)
        else:
            embed = discord.Embed(title=lang["profiles_leveling_already_disabled"], color=self.module_embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(5, 60, commands.BucketType.member)
    @leveling_toggle.command(name='reset', help=main.lang["command_leveling_reset_help"], description=main.lang["command_leveling_reset_description"], ignore_extra=True)
    async def leveling_reset(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if ctx.author.id == ctx.guild.owner.id:
            await ctx.send(embed = discord.Embed(title=lang["profiles_leveling_reset_confirmation"], color = self.module_embed_color))
            try:
                msg = await self.bot.wait_for('message', check=lambda m: (m.content.lower() in ['yes', 'y', 'no', 'n']) and m.channel == ctx.channel, timeout=60.0)
                if msg.content.lower() == 'yes' or msg.content.lower() == 'y':
                    await ProfilesHandler.reset_leveling(ctx.guild.id)
                    embed = discord.Embed(title=lang["profiles_leveling_reset_message"], color=self.module_embed_color)
                else:
                    embed = discord.Embed(title=lang["wait_for_cancelled"], color=self.module_embed_color)
            except asyncio.TimeoutError:
                embed = discord.Embed(title=lang["wait_for_timeout"], color=self.module_embed_color)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Profiles(bot))