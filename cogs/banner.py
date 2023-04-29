from __future__ import annotations

import urllib.request
from io import BytesIO
from typing import TYPE_CHECKING

import aiohttp
import discord
from PIL import ImageFont, ImageDraw, Image
from discord.ext import commands, tasks

if TYPE_CHECKING:
    from utils import FarmingCouncil


class Banner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.update_banner.start()

    def cog_unload(self) -> None:
        self.update_banner.cancel()

    @tasks.loop(seconds=10.0)
    async def update_banner(self):
        print("task run start")
        # Fetch server information
        guild = await self.bot.fetch_guild(1020742260683448450, with_counts=True)
        url = guild.banner.url
        # Fetch image
        try:
            image = await fetch_image(url)
        except Exception as e:
            print(e)
            return
        # Create drawing context
        draw = ImageDraw.Draw(image) # image is 960x640
        # Load font
        font = ImageFont.truetype("Roboto-Bold.ttf", size=52)

        # light gray rectangle in bottom right corner, high opacity
        draw.rectangle([(800, 500), (960, 640)], fill=(0, 0, 0, 200))

        draw.text((780, 570), f"{guild.approximate_member_count}", font=font, fill=(255, 255, 255), anchor="lt")
        draw.text((780, 500), f"{guild.approximate_presence_count}", font=font, fill=(255, 255, 255), anchor="lt")
        # draw two circles, one for online, one for total
        # Save image (this is just for testing)
        image.save("agony.png")
        print("Image saved to disk!")

        # Upload image as server banner, do not save to disk
        # with BytesIO() as image_binary:
        #     image.save(image_binary, "PNG")
        #     image_binary.seek(0)
        #     await guild.edit(banner=image_binary.read())

    @update_banner.before_loop
    async def before_update_banner(self):
        await self.bot.wait_until_ready()


async def fetch_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            image_bytes = await response.read()
            image = Image.open(BytesIO(image_bytes))
            return image


async def setup(bot: FarmingCouncil) -> None:
    print("setup ran")
    await bot.add_cog(Banner(bot))
