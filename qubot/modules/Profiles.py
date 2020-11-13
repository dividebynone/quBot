from libs.qulib import user_get, user_set, ExtendedCommand, ExtendedGroup
from discord.ext import commands
from main import config, bot_path
from PIL import Image, ImageDraw, ImageFont
import libs.roundedrectangles  # noqa: F401
import libs.profileshandler as profileshandler
import libs.prefixhandler as prefixhandler
import libs.premiumhandler as premium
import libs.Colors as colors
import libs.qulib as qulib
import textwrap
import asyncio
import discord
import math
import main
import io
import os
import re


class Profiles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.embed_color = 0x6e78cc

        # Module configuration
        self.module_name = str(self.__class__.__name__)
        self.is_restricted_module = False
        self.module_dependencies = ['Economy']

        qulib.module_configuration(self.module_name, self.is_restricted_module, self.module_dependencies)

        if 'Economy' not in config.sections():
            config.add_section('Economy')
            if 'CurrencySymbol' not in config['Economy']:
                config.set('Economy', 'CurrencySymbol', '💵')

        if 'Profiles' not in config.sections():
            config.add_section('Profiles')
            if 'MaxLevelingRoles' not in config['Economy']:
                config.set('Profiles', 'MaxLevelingRoles', '20')

        with open(os.path.join(bot_path, 'config.ini'), 'w', encoding="utf_8") as config_file:
            config.write(config_file)
        config_file.close()

        with open(os.path.join(bot_path, 'config.ini'), 'r', encoding="utf_8") as config_file:
            config.read_file(config_file)
            self.currency_symbol = config.get('Economy', 'CurrencySymbol')
            self.max_roles = int(config.get('Profiles', 'MaxLevelingRoles'))
        config_file.close()

        self.ProfilesHandler = profileshandler.ProfilesHandler()
        self.ProfileBackgrounds = profileshandler.ProfileBackgrounds()
        self.PremiumHandler = premium.PremiumHandler()
        self.LevelingToggle = profileshandler.LevelingToggle()
        self.PrefixHandler = prefixhandler.PrefixHandler()
        self.Customization = profileshandler.ProfilesCustomization()
        self.LevelingRoles = profileshandler.LevelingRoles()
        self.LevelingNotifications = profileshandler.LevelingNotifications()
        self.bio_char_limit = 150

        self.background_image = Image.open(os.path.join(main.bot_path, 'data', 'images', 'profile-background.jpg'))
        self.premium_badge = Image.open(os.path.join(main.bot_path, 'data', 'images', 'premium-badge.png'))
        self.premium_plus_badge = Image.open(os.path.join(main.bot_path, 'data', 'images', 'premium-badge-plus.png'))

        self.title_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'HelveticaNowMedium.ttf'), 30)
        self.medium_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'HelveticaNowBold.ttf'), 22)
        self.body_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'HelveticaNow.ttf'), 19)
        self.bio_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'OpenSans-SemiBold.ttf'), 18)

        self.avatar_size = 128
        self.levelbar_size = (375, 30)

        self.leveling_constant = 0.2
        self.experience = 5

        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 300, commands.BucketType.member)

        self.left = '⬅️'
        self.right = '➡️'
        self.pagination_timeout = '⏹️'

        print(f'Module {self.__class__.__name__} loaded')

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

        if not retry_after and not self.LevelingToggle.is_disabled(message.guild.id):
            user_data = await self.ProfilesHandler.get(message.author.id, message.guild.id)

            user_data['experience'] += self.experience
            next_lvl_experience = int(math.pow((user_data['level'] + 1) / self.leveling_constant, 2))

            if user_data['experience'] >= next_lvl_experience:
                user_data['level'] += 1
                user_data['experience'] -= next_lvl_experience

                role_ids = await self.LevelingRoles.get_roles(message.guild.id, user_data['level'])

                try:
                    if role_ids:
                        guild_roles = message.guild.roles
                        roles_to_add = []
                        for role in guild_roles:
                            if role.id in role_ids:
                                roles_to_add.append(role)

                        if len(roles_to_add) > 0:
                            await message.author.add_roles(*roles_to_add, reason=lang["profiles_levelrole_reason"])

                    action = message.channel
                    lvlup_message = lang["profile_level_up_message"].format(message.author.mention, user_data['level'])

                    leveling_settings = await self.LevelingNotifications.get_guild(message.guild.id)
                    if leveling_settings:
                        if leveling_settings[0] == profileshandler.NotificationType.DM:
                            action = message.author
                            lvlup_message = lang["profile_level_up_message_dm"].format(message.author.mention, user_data['level'], message.guild.name)
                        elif leveling_settings[0] == profileshandler.NotificationType.Channel and leveling_settings[1]:
                            channel = message.guild.get_channel(leveling_settings[1])
                            if not channel:
                                await self.LevelingNotifications.reset_guild(message.guild.id)
                            else:
                                action = channel

                    if action:
                        await action.send(lvlup_message)
                except discord.errors.Forbidden:
                    pass

            await self.ProfilesHandler.update_experience(message.author.id, message.guild.id, user_data)

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_guild_remove(self, guild):
        await self.LevelingRoles.reset_guild(guild.id)
        await self.LevelingNotifications.reset_guild(guild.id)

    @commands.cooldown(5, 60, commands.BucketType.member)
    @commands.command(name='profile', help=main.lang["command_profile_help"], description=main.lang["command_profile_description"], aliases=['p', 'me', 'level'])
    @commands.guild_only()
    async def profile(self, ctx, *, user: discord.User = None):
        async with ctx.channel.typing():
            user = user or ctx.author
            user_data = await self.ProfilesHandler.get(user.id, ctx.guild.id)
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
            draw.text((175, 50), user_title, fill=(255, 255, 255, 255), font=self.title_font)
            draw.text((180 + self.title_font.getsize(user_title)[0], 55), f'#{user.discriminator}', fill=(210, 210, 210, 255), font=self.medium_font)
            draw.text((10, 185), lang["profile_bio_title"], fill=(255, 255, 255, 255), font=self.title_font)

            offset = 220
            user_bio = user_data['bio'] if user_data['bio'] else lang["profile_empty_bio"]

            for line in textwrap.wrap(user_bio, width=55):
                draw.text((10, offset), line, font=self.bio_font, fill=(255, 255, 255, 255))
                offset += self.bio_font.getsize(line)[1]

            # Leveling
            user_experience = user_data['experience']
            user_level = user_data['level']
            user_next_lvl_experience = int(math.pow((user_level + 1) / self.leveling_constant, 2))

            levelbar_image = Image.new('RGBA', (self.levelbar_size[0] * 3, self.levelbar_size[1] * 3), (0, 0, 0, 0))
            levelbar_draw = ImageDraw.Draw(levelbar_image)

            # Default color: (115, 139, 215, 255)
            levelbar_color = await self.Customization.get_levelbar_color(ctx.author.id, ctx.guild.id) or "#738BD7"
            luma = colors.calculate_luminance(levelbar_color)
            if luma > 150:
                levelbar_bg = "#555555"
                text_color = "#000000"
            elif luma > 40:
                levelbar_bg = "#ffffff"
                text_color = "#000000"
            else:
                levelbar_bg = "#555555"
                text_color = "#ffffff"

            levelbar_draw.rounded_rectangle([(0, 0), (self.levelbar_size[0] * 3, self.levelbar_size[1] * 3)], corner_radius=45, fill=levelbar_bg)
            if (user_experience / user_next_lvl_experience) >= 0.06:
                levelbar_draw.rounded_rectangle([(6, 6), ((int(self.levelbar_size[0] * (user_experience / user_next_lvl_experience)) * 3) - 6, (self.levelbar_size[1] * 3) - 6)], corner_radius=39, fill=levelbar_color)
            else:
                levelbar_draw.rounded_rectangle([(6, 6), ((int(self.levelbar_size[0] * (0.065)) * 3) - 6, (self.levelbar_size[1] * 3) - 6)], corner_radius=35, fill=levelbar_color)

            levelbar_image = levelbar_image.resize((self.levelbar_size[0], self.levelbar_size[1]), Image.ANTIALIAS)
            image.paste(levelbar_image, (175, 92), levelbar_image)

            disabled_leveling = self.LevelingToggle.is_disabled(ctx.guild.id)

            xp_message = f'{user_experience:,}/{user_next_lvl_experience:,} {lang["exp_string"]}' if not disabled_leveling else lang["profile_disabled_exp"]
            xp_w, xp_h = self.body_font.getsize(xp_message)
            draw.text(((175 + (self.levelbar_size[0] - xp_w) / 2), (92 + (self.levelbar_size[1] - xp_h) / 2)), xp_message, fill=text_color, font=self.body_font)

            if not disabled_leveling:
                level_message = f'{lang["level_string"]}: {user_level}'
                user_rank = await self.ProfilesHandler.get_rank(user.id, ctx.guild.id)
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

            # Premium Badge
            tier = await self.PremiumHandler.get_tier(user.id)
            if tier == premium.PremiumTier.Standard:
                image.paste(self.premium_badge, (20, 110), mask=self.premium_badge)
            elif tier == premium.PremiumTier.Plus:
                image.paste(self.premium_plus_badge, (20, 110), mask=self.premium_plus_badge)

            # Sending image
            image = image.convert('RGB')
            buffer_output = io.BytesIO()  # Create buffer
            image.save(buffer_output, optimize=True, quality=95, format='PNG')
            buffer_output.seek(0)

            await ctx.send(file=discord.File(buffer_output, 'profile.png'))

    @commands.cooldown(3, 60, commands.BucketType.member)
    @commands.command(name='bio', help=main.lang["command_bio_help"], description=main.lang["command_bio_description"], usage="<text>")
    @commands.guild_only()
    async def bio_command(self, ctx, *, message: str = None):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if message:
            if len(message) <= self.bio_char_limit:
                await self.ProfilesHandler.set_bio(ctx.author.id, ctx.guild.id, message)
                embed = discord.Embed(title=lang["profile_bio_success"], color=self.embed_color)
            else:
                embed = discord.Embed(title=lang["profile_bio_char_limit"].format(self.bio_char_limit), color=self.embed_color)
        else:
            await self.ProfilesHandler.set_bio(ctx.author.id, ctx.guild.id, None)
            embed = discord.Embed(title=lang["profile_bio_reset"], color=self.embed_color)
        await ctx.author.send(embed=embed)

    @commands.cooldown(10, 30, commands.BucketType.member)
    @commands.group(cls=ExtendedGroup, name='levelbar', invoke_without_command=True, description=main.lang["command_levelbar_description"], usage="<color>", aliases=['lbar'], permissions=['Premium Only'])
    @premium.premium_only()
    @commands.guild_only()
    async def levelbar_customization(self, ctx, *, color: str):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            r = re.compile('^#(([0-9a-fA-F]{2}){3}|([0-9a-fA-F]){3})$')
            if r.match(color):
                await self.Customization.set_levelbar_color(ctx.author.id, ctx.guild.id, color)
            else:
                hex_value = colors.get_color(color)
                if hex_value:
                    await self.Customization.set_levelbar_color(ctx.author.id, ctx.guild.id, hex_value)
                else:
                    await ctx.send(embed=discord.Embed(title=lang["profiles_customization_not_found_title"], description=lang["profiles_levelbar_not_found"].format(ctx.author.mention), color=self.embed_color))
                    return
            await ctx.send(embed=discord.Embed(title=lang["profiles_customization_title"], description=lang["profiles_levelbar_success"].format(ctx.author.mention, color.title()), color=self.embed_color))

    @commands.cooldown(10, 30, commands.BucketType.member)
    @levelbar_customization.command(cls=ExtendedCommand, name='reset', description=main.lang["command_levelbar_reset_description"], aliases=['default', 'clear'], permissions=['Premium Only'])
    @premium.premium_only()
    @commands.guild_only()
    async def levelbar_customization_reset(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await self.Customization.clear_levelbar(ctx.author.id, ctx.guild.id)
        await ctx.send(embed=discord.Embed(title=lang["profiles_customization_reset_title"], description=lang["profiles_levelbar_reset_description"].format(ctx.author.mention), color=self.embed_color))

    @commands.cooldown(5, 30, commands.BucketType.member)
    @commands.group(name='background', invoke_without_command=True, help=main.lang["command_background_help"], description=main.lang["command_background_description"], usage="{category or background id}", aliases=['backgrounds', 'bg', 'bgs'])
    async def background(self, ctx, value=None):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if value is not None:
                if value.isnumeric():
                    background_info = await self.ProfileBackgrounds.get_background_info(value)
                    if background_info:
                        embed = discord.Embed(title=lang['profiles_background_specific_title'], description=f"{background_info['description']}\n\n**{lang['price_string']}:** {background_info['price']:,} {self.currency_symbol}", color=self.embed_color)
                        embed.set_thumbnail(url=background_info['url'])
                        embed.set_footer(text=f"{lang['category_string']}: {background_info['category']}")
                    else:
                        embed = discord.Embed(title=lang["profiles_background_specific_not_found"], color=self.embed_color)
                else:
                    category_info = await self.ProfileBackgrounds.get_category(value.capitalize())
                    if category_info:
                        index = start_index = 0
                        last_index = math.floor(len(category_info) / 5)
                        if len(category_info) % 5 == 0:
                            last_index -= 1
                        unlocked_backgrounds = await self.ProfileBackgrounds.unlocked_backgrounds(ctx.author.id)

                        msg = None
                        action = ctx.send
                        try:
                            while True:
                                description = ""
                                for background in category_info[(index * 5):(index * 5 + 5)]:
                                    description += f'\u2022 **{background[0]}** - {background[1]}\n\t{f"""**{lang["price_string"]}**: {background[2]:,} {self.currency_symbol}""" if int(background[0]) not in unlocked_backgrounds else lang["profiles_background_owned"]}\n\n'
                                embed = discord.Embed(title=lang["profiles_background_category_title"].format(value.capitalize()), description=description, color=self.embed_color)
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
                        embed = discord.Embed(title=lang["profiles_background_category_not_found"], color=self.embed_color)
            else:
                categories = await self.ProfileBackgrounds.get_categories()
                prefix = self.PrefixHandler.get_prefix(ctx.guild.id, main.prefix)
                embed = discord.Embed(title=lang["profiles_background_general_title"], description=lang["profiles_background_general_body"].format(', '.join(categories), prefix, prefix), color=self.embed_color)
                embed.set_footer(text=lang["profiles_background_footer"])
            await ctx.send(embed=embed)

    @commands.cooldown(10, 60, commands.BucketType.member)
    @background.command(name='buy', help=main.lang["command_bg_buy_help"], description=main.lang["command_bg_buy_description"], usage='<background id>', aliases=['purchase'])
    async def background_buy(self, ctx, bg_id: int):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        user = ctx.author
        user_info = await user_get(user.id)
        background_info = await self.ProfileBackgrounds.get_background_info(bg_id)
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if background_info:
            if bg_id > 0:
                unlocked_backgrounds = await self.ProfileBackgrounds.unlocked_backgrounds(user.id)
                if not unlocked_backgrounds or bg_id not in unlocked_backgrounds:
                    if user_info['currency'] <= 0 or background_info['price'] > user_info['currency']:
                        embed = discord.Embed(title=lang["profiles_buy_insufficient_funds"].format(background_info['price'] - user_info['currency'], self.currency_symbol), color=self.embed_color)
                    else:
                        await ctx.send(embed=discord.Embed(title=lang["profiles_buy_confirmation"].format(background_info['price'], self.currency_symbol), color=self.embed_color))
                        try:
                            msg = await self.bot.wait_for('message', check=lambda m: (m.content.lower() in ['yes', 'y', 'no', 'n']) and m.channel == ctx.channel and m.author == ctx.author, timeout=60.0)
                            if msg.content.lower() == 'yes' or msg.content.lower() == 'y':
                                embed = discord.Embed(title=lang["profiles_buy_success"].format(bg_id, background_info['price'], self.currency_symbol), color=self.embed_color)
                                user_info['currency'] -= background_info['price']
                                await self.ProfileBackgrounds.unlock_background(user.id, bg_id)
                                await user_set(user.id, user_info)
                            else:
                                embed = discord.Embed(title=lang["wait_for_cancelled"], color=self.embed_color)
                        except asyncio.TimeoutError:
                            embed = discord.Embed(title=lang["wait_for_timeout"], color=self.embed_color)
                else:
                    embed = discord.Embed(title=lang["profiles_buy_owned"].format(bg_id), description=background_info['description'], color=self.embed_color)
                    embed.set_thumbnail(url=background_info['url'])
            else:
                return
        else:
            embed = discord.Embed(title=lang["profiles_buy_not_found"], color=self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(3, 60, commands.BucketType.member)
    @background.command(name='inventory', help=main.lang["command_bg_inventory_help"], description=main.lang["command_bg_inventory_description"], ignore_extra=True, aliases=['inv'])
    async def background_inventory(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        unlocked_backgrounds = await self.ProfileBackgrounds.user_backgrounds(ctx.author.id)
        if unlocked_backgrounds:
            index = start_index = 0
            last_index = math.floor(len(unlocked_backgrounds) / 5)
            if len(unlocked_backgrounds) % 5 == 0:
                last_index -= 1

            msg = None
            action = ctx.send
            try:
                while True:
                    description = ""
                    for background in unlocked_backgrounds[(index * 5):(index * 5 + 5)]:
                        description += f'\u2022 **{background[0]}** - {background[1]}\n'
                    embed = discord.Embed(title=lang["profiles_inventory_title"].format(ctx.author.name), description=description, color=self.embed_color)
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
            embed = discord.Embed(title=lang["profiles_inventory_empty"], color=self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(10, 30, commands.BucketType.member)
    @commands.guild_only()
    @background.command(name='equip', help=main.lang["command_bg_equip_help"], description=main.lang["command_bg_equip_description"], usage='<background id>')
    async def background_equip(self, ctx, bg_id: int = None):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if bg_id == None:
            embed = discord.Embed(title=lang["profiles_unequip_message"].format(str(ctx.author)), color=self.embed_color)
            await self.ProfilesHandler.equip_background(ctx.author.id, ctx.guild.id, bg_id)
        else:
            background_info = await self.ProfileBackgrounds.get_background_info(bg_id)
            if background_info:
                unlocked_backgrounds = await self.ProfileBackgrounds.unlocked_backgrounds(ctx.author.id)
                if bg_id in unlocked_backgrounds:
                    embed = discord.Embed(title=lang["profiles_equip_success"].format(str(ctx.author), bg_id), color=self.embed_color)
                    await self.ProfilesHandler.equip_background(ctx.author.id, ctx.guild.id, bg_id)
                else:
                    embed = discord.Embed(title=lang["profiles_equip_not_owned"], color=self.embed_color)
            else:
                embed = discord.Embed(title=lang["profiles_equip_not_found"], color=self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(5, 60, commands.BucketType.member)
    @commands.guild_only()
    @background.command(name='unequip', description=main.lang["command_bg_unequip_description"], ignore_extra=True, aliases=['default'])
    async def background_unequip(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await self.ProfilesHandler.equip_background(ctx.author.id, ctx.guild.id, None)
        await ctx.send(embed=discord.Embed(title=lang["profiles_unequip_message"].format(str(ctx.author)), color=self.embed_color))

    @commands.cooldown(5, 60, commands.BucketType.member)
    @commands.guild_only()
    @commands.command(name='leaderboard', description=main.lang["command_leaderboard_description"], usage="{page}", aliases=['lb', 'xplb', 'top'], ignore_extra=True)
    async def profiles_leaderboard(self, ctx, page: int = 1):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if not self.LevelingToggle.is_disabled(ctx.guild.id):
            leaderboard = await self.ProfilesHandler.leaderboard(ctx.guild.id)
            if leaderboard:

                last_index = math.floor(len(leaderboard) / 10)
                if len(leaderboard) % 10 == 0:
                    last_index -= 1
                page = min(last_index, (page - 1)) if page and page >= 1 else 0
                index = page

                user_rank = await self.ProfilesHandler.get_rank(ctx.author.id, ctx.guild.id)

                msg = None
                action = ctx.send
                try:
                    while True:
                        description = lang["profiles_leaderboard_description"].format(ctx.guild.name, user_rank)
                        for person in leaderboard[(index * 10):(index * 10 + 10)]:
                            user = self.bot.get_user(person[0]) or person[0]
                            description += f"**#{person[1]} {str(user)}** ({lang['level_string']} {person[2]} : {person[3]:,} {lang['exp_string']})\n"
                        embed = discord.Embed(title=lang["profiles_leaderboard_title"], description=description, color=self.embed_color)
                        embed.set_thumbnail(url=str(ctx.guild.icon_url))
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
                embed = discord.Embed(title=lang["profiles_leaderboard_empty"], color=self.embed_color)
        else:
            embed = discord.Embed(title=lang["profiles_leaderboard_disabled"], color=self.embed_color)
        await ctx.send(embed=embed)

    @commands.cooldown(5, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.group(cls=ExtendedGroup, name='leveling', description=main.lang["command_leveling_toggle_description"], invoke_without_command=True, permissions=['Administrator'])
    @commands.guild_only()
    async def leveling_toggle(self, ctx):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            if not self.LevelingToggle.is_disabled(ctx.guild.id):
                await self.LevelingToggle.disable_leveling(ctx.guild.id)
                embed = discord.Embed(title=lang["profiles_leveling_disabled"], color=self.embed_color)
            else:
                await self.LevelingToggle.enable_leveling(ctx.guild.id)
                embed = discord.Embed(title=lang["profiles_leveling_enabled"], color=self.embed_color)
            await ctx.send(embed=embed)

    @commands.cooldown(5, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @leveling_toggle.command(cls=ExtendedCommand, name='enable', description=main.lang["command_leveling_enable_description"], aliases=['e'], ignore_extra=True, permissions=['Administrator'])
    async def leveling_enable(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if self.LevelingToggle.is_disabled(ctx.guild.id):
            await self.LevelingToggle.enable_leveling(ctx.guild.id)
            await ctx.send(embed=discord.Embed(title=lang["profiles_leveling_enabled"], color=self.embed_color))
        else:
            await ctx.send(lang["profiles_leveling_already_enabled"], delete_after=15)

    @commands.cooldown(5, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @leveling_toggle.command(cls=ExtendedCommand, name='disable', description=main.lang["command_leveling_disable_description"], aliases=['d'], ignore_extra=True, permissions=['Administrator'])
    async def leveling_disable(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if not self.LevelingToggle.is_disabled(ctx.guild.id):
            await self.LevelingToggle.disable_leveling(ctx.guild.id)
            await ctx.send(embed=discord.Embed(title=lang["profiles_leveling_disabled"], color=self.embed_color))
        else:
            await ctx.send(lang["profiles_leveling_already_disabled"], delete_after=15)

    @commands.cooldown(5, 60, commands.BucketType.guild)
    @commands.guild_only()
    @leveling_toggle.command(cls=ExtendedCommand, name='reset', description=main.lang["command_leveling_reset_description"], ignore_extra=True, permissions=['Server Owner'])
    async def leveling_reset(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if ctx.author.id == ctx.guild.owner.id:
            await ctx.send(embed=discord.Embed(title=lang["profiles_leveling_reset_confirmation"], color=self.embed_color))
            try:
                msg = await self.bot.wait_for('message', check=lambda m: (m.content.lower() in ['yes', 'y', 'no', 'n']) and m.channel == ctx.channel and m.author == ctx.author, timeout=60.0)
                if msg.content.lower() == 'yes' or msg.content.lower() == 'y':
                    await self.ProfilesHandler.reset_leveling(ctx.guild.id)
                    embed = discord.Embed(title=lang["profiles_leveling_reset_message"], color=self.embed_color)
                else:
                    embed = discord.Embed(title=lang["wait_for_cancelled"], color=self.embed_color)
            except asyncio.TimeoutError:
                embed = discord.Embed(title=lang["wait_for_timeout"], color=self.embed_color)
            await ctx.send(embed=embed)

    @commands.cooldown(10, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.group(cls=ExtendedGroup, name='levelrole', invoke_without_command=True, description=main.lang["command_levelrole_description"], aliases=['lvlrole', 'levelroles', 'lvlroles'], usage="<level> <role>", permissions=['Administrator'])
    async def levelrole(self, ctx, level: int, role: discord.Role):
        if not ctx.invoked_subcommand:
            if level > 0:
                lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
                role_count = await self.LevelingRoles.get_role_count(ctx.guild.id)
                if role_count < self.max_roles:
                    await self.LevelingRoles.add_role(ctx.guild.id, role.id, level)
                    await ctx.send(embed=discord.Embed(title=lang["profiles_levelrole_title"], description=lang["profiles_levelrole_desc"].format(role.mention, level), color=self.embed_color))
                else:
                    await ctx.send(embed=discord.Embed(title=lang["profiles_levelrole_max_title"], description=lang["profiles_levelrole_max"].format(self.max_roles), color=self.embed_color))

    @commands.cooldown(5, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @levelrole.command(cls=ExtendedCommand, name='remove', description=main.lang["command_levelrole_remove_description"], usage="<level>", aliases=['delete', 'del'], permissions=['Administrator'])
    async def levelrole_remove(self, ctx, level: int):
        if level > 0:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            await self.LevelingRoles.remove_role(ctx.guild.id, level)
            await ctx.send(embed=discord.Embed(title=lang["profiles_levelrole_remove_title"], description=lang["profiles_levelrole_remove"].format(level), color=self.embed_color))

    @commands.cooldown(5, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @levelrole.command(cls=ExtendedCommand, name='dashboard', description=main.lang["command_levelrole_dashboard_description"], aliases=['settings', 'config'], permissions=['Administrator'])
    async def levelrole_dashboard(self, ctx):
        roles_set = await self.LevelingRoles.get_all_roles(ctx.guild.id)
        guild_roles = ctx.guild.roles

        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        description = f'{lang["profiles_levelrole_dashboard_desc"]}\n\n'

        if len(roles_set) > 0:
            for entry in roles_set:
                entry_role = None
                for role in guild_roles:
                    if role.id == entry[1]:
                        entry_role = role
                        break

                if entry_role:
                    description += f'**{lang["level_string"]} {entry[0]}:** {role.mention}\n'
        else:
            description += f'**{lang["profiles_levelrole_dashboard_empty"]}**'

        embed = discord.Embed(description=description, color=self.embed_color)
        embed.set_author(name=lang["profiles_levelrole_dashboard_header"].format(ctx.guild.name), icon_url=str(ctx.guild.icon_url))
        await ctx.send(embed=embed)

    @commands.cooldown(10, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @commands.group(cls=ExtendedGroup, name='levelnotify', invoke_without_command=True, description=main.lang["command_lvlnotify_description"], aliases=['lvlnotify', 'lvln'], permissions=['Administrator'])
    async def leveling_notify(self, ctx):
        if not ctx.invoked_subcommand:
            lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
            embed = discord.Embed(description=lang["profile_lvlnotify_desc"], color=self.embed_color)
            embed.set_author(name=lang["profile_lvlnotify_header"].format(ctx.guild.name), icon_url=str(ctx.guild.icon_url))
            leveling_settings = await self.LevelingNotifications.get_guild(ctx.guild.id)
            type_dict = {int(profileshandler.NotificationType.DM): lang["dm_string"], None: lang["default_string"]}
            if leveling_settings and leveling_settings[1]:
                channel = ctx.guild.get_channel(leveling_settings[1])
                if not channel:
                    await self.LevelingNotifications.reset_guild(ctx.guild.id)
                else:
                    type_dict[int(profileshandler.NotificationType.Channel)] = f'{lang["channel_string"]}: {channel.mention}'
            embed.add_field(name=lang["profile_lvlnotify_type"], value=(type_dict[leveling_settings[0]] if leveling_settings else lang["default_string"]), inline=True)
            await ctx.send(embed=embed)

    @commands.cooldown(10, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @leveling_notify.command(cls=ExtendedCommand, name='default', description=main.lang["command_lvlnotify_default_description"], aliases=['reset'], permissions=['Administrator'])
    async def leveling_notify_default(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await self.LevelingNotifications.reset_guild(ctx.guild.id)
        await ctx.send(embed=discord.Embed(title=lang["profile_lvlnotify_reset_title"], description=lang["profile_lvlnotify_reset"], color=self.embed_color))

    @commands.cooldown(10, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @leveling_notify.command(cls=ExtendedCommand, name='dm', description=main.lang["command_lvlnotify_dm_description"], permissions=['Administrator'])
    async def leveling_notify_dm(self, ctx):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        await self.LevelingNotifications.change_type(ctx.guild.id, profileshandler.NotificationType.DM)
        await ctx.send(embed=discord.Embed(title=lang["profile_lvlnotify_change_title"], description=lang["profile_lvlnotify_change_dm"], color=self.embed_color))

    @commands.cooldown(10, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @leveling_notify.command(cls=ExtendedCommand, name='channel', description=main.lang["command_lvlnotify_channel_description"], usage="<channel>", aliases=['chnl'], permissions=['Administrator'])
    async def leveling_notify_channel(self, ctx, channel: discord.TextChannel):
        lang = main.get_lang(ctx.guild.id) if ctx.guild else main.lang
        if ctx.guild.me.permissions_in(channel).send_messages:
            await self.LevelingNotifications.set_channel(ctx.guild.id, channel.id)
            await ctx.send(embed=discord.Embed(title=lang["profile_lvlnotify_change_title"], description=lang["profile_lvlnotify_change_channel"].format(channel.mention), color=self.embed_color))
        else:
            await ctx.send(lang["profile_lvlnotify_channel_permissions"], delete_after=15)


def setup(bot):
    bot.add_cog(Profiles(bot))
