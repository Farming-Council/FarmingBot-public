# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from utils import FarmingCouncil

class CropView(discord.ui.View):
    def __init__(self, crop):
        super().__init__()
        self.crop = crop

    @discord.ui.button(label='Written', style=discord.ButtonStyle.danger)
    async def written(self, interaction: discord.Interaction, button: discord.ui.Button):
        e = discord.Embed(title=f"{self.crop} Guide", description=f"To look at the written guide on `{self.crop}`, join our support server by clicking [**here**](https://discord.gg/farmingcouncil). Then head to the **Guides and Tutorials Category** where you will find the {self.crop} guide channel.", color=0x2F3136)
        e.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed=e)

    @discord.ui.button(label="Video", style=discord.ButtonStyle.green)
    async def video(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.crop.lower() == "carrots":
            link = await get_crop("carrots")
        elif self.crop.lower() == "potato":
            link = await get_crop("potato")
        elif self.crop.lower() == "wheat":
            link = await get_crop("wheat")
        elif self.crop.lower() == "sugar cane":
            link = await get_crop("sugar cane")
        elif self.crop.lower() == "pumpkin":
            link = await get_crop("pumpkin")
        elif self.crop.lower() == "melon":
            link = await get_crop("melon")
        elif self.crop.lower() == "teleport pads":
            link = await get_crop("teleport pads")
        e = discord.Embed(title=f"{self.crop} Guide", description=f"Here is a video of `{self.crop}` guide:\n{link}", color=0x2F3136)
        e.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed=e)

class Tutorial(commands.Cog):
    def __init__(self, bot: FarmingCouncil) -> None:
        self.bot: FarmingCouncil = bot

    @app_commands.command(description="Tell a user how to use our shop")
    @app_commands.guild_only()
    async def tutorial(self, interaction: discord.Interaction, topic: Literal["Carrots", "Potato", "Wheat", "Sugar Cane", "Pumpkin", "Melon", "Teleport Pads"]):
        e = discord.Embed(title=f"{topic} Guide", description=f"Please let us know if you want the guide to be **written** or **video** form!", color=0x2F3136)
        e.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed=e, view=CropView(topic))
        
    @app_commands.command(description="Tell a user how to use our shop")
    @app_commands.guild_only()
    async def addtutorial(self, interaction: discord.Interaction, topic: Literal["Carrots", "Potato", "Wheat", "Sugar Cane", "Pumpkin", "Melon", "Teleport Pads"], video: str):
        userRoles = [id.id for id in interaction.user.roles]
        if 1028636883879743558 not in userRoles:
            await interaction.response.send_message("This command is not for you", ephemeral=True)
            return
        await add_crop(str(topic), str(video))
        await interaction.response.send_message("Done lol")
        
    @app_commands.command(description="Tell a user how to use our shop")
    @app_commands.guild_only()
    async def removetutorial(self, interaction: discord.Interaction, topic: Literal["Carrots", "Potato", "Wheat", "Sugar Cane", "Pumpkin", "Melon", "Teleport Pads"]):
        userRoles = [id.id for id in interaction.user.roles]
        if 1028636883879743558 not in userRoles:
            await interaction.response.send_message("This command is not for you", ephemeral=True)
            return
        await remove_crop(str(topic))
        await interaction.response.send_message("Done lol")

        

async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(Tutorial(bot))