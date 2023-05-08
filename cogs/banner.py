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
        font = ImageFont.truetype("Uni Sans Heavy.otf", size=52)

        # light gray rectangle in bottom right corner, high opacity, rounded top left corner
        # draw.rectangle([(700, 475), (960, 640)], fill=(0, 0, 0))
        # draw.rounded_rectangle([(700, 475), (960, 640)], radius=20, fill=(0, 0, 0))
        draw.text((780, 570), f"{guild.approximate_member_count}", font=font, fill=(255, 255, 255), anchor="lt")
        draw.text((780, 500), f"{guild.approximate_presence_count}", font=font, fill=(255, 255, 255), anchor="lt", stroke_width=5, stroke_fill=(0, 0, 0))
        # draw circle directly to the left of the first text, fill gray
        draw.ellipse([(720, 563), (770, 613)], fill=(128, 132, 142))
        # draw circle directly to the left of the second text, fill green
        draw.ellipse([(720, 493), (770, 543)], fill=(67, 181, 129))
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
