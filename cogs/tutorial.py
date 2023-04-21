# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import discord
from discord import app_commands
from discord.ext import commands
from utils import EMBED_COLOR

if TYPE_CHECKING:
    from utils import FarmingCouncil
class Links(discord.ui.View):
    def __init__(self, url: str):
        super().__init__()
        self.add_item(discord.ui.Button(label='Click Here', url=url))

class CropView(discord.ui.View):
    def __init__(self, crop):
        super().__init__()
        self.crop = crop

    @discord.ui.button(label='Written', style=discord.ButtonStyle.danger)
    async def written(self, interaction: discord.Interaction, button: discord.ui.Button):
        e = discord.Embed(title=f"{self.crop} Guide", description=f"To look at the written guide on `{self.crop}`, join our support server by clicking [**here**](https://discord.gg/farmers). Then head to the **Guides and Tutorials Category** where you will find the {self.crop} guide channel.", color=EMBED_COLOR)
        e.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed=e)

    @discord.ui.button(label="Video", style=discord.ButtonStyle.green)
    async def video(self, interaction: discord.Interaction, button: discord.ui.Button):
        link = await interaction.client.get_crop(self.crop.lower())
        if link:
            link = link[1]
            e = discord.Embed(title=f"{self.crop} Guide", description=f"Here is a video of `{self.crop}` guide\nYou can also join our discord server for more information!", color=EMBED_COLOR)
            e.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
            await interaction.response.send_message(embed=e, view=Links(link))
        else:
            e = discord.Embed(title=f"{self.crop} Guide", description=f"Sorry, but we don't have a video guide for `{self.crop}` yet. Please let us know if you would like to make one! Btw: If you are seeing this, then something very bad happend...", color=EMBED_COLOR)
            e.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
            await interaction.response.send_message(embed=e)


class Tutorial(commands.Cog):
    def __init__(self, bot: FarmingCouncil) -> None:
        self.bot: FarmingCouncil = bot

    @app_commands.command(description="Tell a user how to use our shop")
    @app_commands.guild_only()
    async def tutorial(self, interaction: discord.Interaction, topic: Literal["Carrots", "Potato", "Wheat", "Sugar Cane", "Pumpkin", "Melon", "Teleport Pads"]):
        e = discord.Embed(title=f"{topic} Guide", description=f"Please let us know if you want the guide to be **written** or **video** form!", color=EMBED_COLOR)
        e.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed=e, view=CropView(topic))
        await self.bot.command_counter(interaction)

async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(Tutorial(bot))