from discord.ext import commands
from main import bot_starttime
from main import modules as loaded_modules
from datetime import datetime
import libs.qulib as qulib
import urllib.request
import main
import discord
from PIL import Image, ImageDraw, ImageFont
import libs.roundedrectangles
from libs.profileshandler import ProfilesHandler
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

        self.ProfilesHandler = ProfilesHandler()
        self.bio_char_limit = 150

        self.background_image = Image.open(os.path.join(main.bot_path, 'data', 'images', 'profile-background.jpg'))

        self.title_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'HelveticaNowMedium.ttf'), 30)
        self.medium_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'HelveticaNowBold.ttf'), 22)
        self.body_font = ImageFont.truetype(os.path.join(main.bot_path, 'data', 'fonts', 'HelveticaNow.ttf'), 19)

        self.avatar_size = 128
        self.levelbar_size = (375, 30)

        self.leveling_constant = 0.2
        self.experience = 5

        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 300, commands.BucketType.member)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        if not message.guild:
            return

        cooldown = self.cd_mapping.get_bucket(message)
        retry_after = cooldown.update_rate_limit()

        if not retry_after:
            user_data = await ProfilesHandler.get(message.author.id, message.guild.id)

            user_data['experience'] += self.experience
            next_lvl_experience = int(math.pow((user_data['level']+1)/self.leveling_constant, 2))

            if user_data['experience'] >= next_lvl_experience:
                user_data['level'] += 1
                user_data['experience'] -= next_lvl_experience
                await message.channel.send(f"Congratulations {message.author.mention}, You've reached level **{user_data['level']}!")

            await ProfilesHandler.update_experience(message.author.id, message.guild.id, user_data)
            
    @commands.command(name='profile')
    @commands.guild_only()
    async def profile(self, ctx, *, user: discord.User = None):
        user = user or ctx.author
        user_data = await ProfilesHandler.get(user.id, ctx.guild.id)

        image = self.background_image.copy().convert("RGBA")
        draw = ImageDraw.Draw(image)

        # Custom background
        custom_background = Image.open(os.path.join(main.bot_path, 'data', 'images', 'banner-2.jpg')).convert("RGBA")
        overlay = Image.new('RGBA', custom_background.size, (0, 0, 0, 100))
        custom_background = Image.alpha_composite(custom_background, overlay)
        image.paste(custom_background, (0, 0))

        user_title = (user.name[:25] + '..') if len(user.name) > 25 else user.name
        draw.text((175, 50), user_title, fill=(255,255,255,255), font=self.title_font)
        draw.text((180 + self.title_font.getsize(user_title)[0], 55), f'#{user.discriminator}', fill=(210, 210, 210, 255), font=self.medium_font)
        draw.text((10, 185), 'Bio', fill=(255,255,255,255), font=self.title_font)

        offset = 220
        user_bio = user_data['bio'] if user_data['bio'] else "Empty"

        for line in textwrap.wrap(user_bio, width=62):
            draw.text((10, offset), line, font=self.body_font, fill=(255,255,255,255))
            offset += self.body_font.getsize(line)[1]

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

        xp_message = f'{user_experience}/{user_next_lvl_experience} EXP'
        xp_w, xp_h = self.body_font.getsize(xp_message)
        draw.text(((175 + (self.levelbar_size[0]-xp_w)/2), (90 + (self.levelbar_size[1]-xp_h)/2)), xp_message, fill=(0, 0, 0, 255), font=self.body_font)
        
        level_message = f'Level: {user_level}'
        user_rank = await ProfilesHandler.get_rank(user.id, ctx.guild.id)
        rank_message = f'Rank: {user_rank if user_rank else ctx.guild.member_count}'
        
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

    @commands.command(name='bio')
    @commands.guild_only()
    async def bio_command(self, ctx, *, message: str = None):
        if message:
            if len(message) <= self.bio_char_limit:
                await ProfilesHandler.set_bio(ctx.author.id, ctx.guild.id, message)
                embed = discord.Embed(title="Successfully changed bio", color=self.module_embed_color)
            else:
                embed = discord.Embed(title=f"Your biography paragraph exceeds the {self.bio_char_limit} character limit.", color=self.module_embed_color)
        else:
            await ProfilesHandler.set_bio(ctx.author.id, ctx.guild.id, None)
            embed = discord.Embed(title=f"Successfully reset bio back to default.", color=self.module_embed_color)
        await ctx.author.send(embed=embed)

def setup(bot):
    bot.add_cog(Profiles(bot))