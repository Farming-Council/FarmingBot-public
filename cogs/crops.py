# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import aiomysql
import json
import sys, os
import time
import datetime
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from utils import FarmingCouncil

class crops(commands.Cog):
    def __init__(self, bot: FarmingCouncil):
        self.bot: FarmingCouncil = bot
        self.session: aiohttp.ClientSession | None = None

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

    @app_commands.command(description="Profit Table for Crops Per Hour")
    @app_commands.guild_only()
    @app_commands.describe(farming_fortune="Amount of Farming Fortune you have")
    async def cropprofits(self, interaction: discord.Interaction, farming_fortune: int = 800):
        send = ""
        if farming_fortune > 1800:
            await interaction.response.send_message("Sorry, you cannot input farming fortunes over **1800**", ephemeral=True)
            return
        sorting = {}
        crops = {"ENCHANTED_CARROT": ["Carrot", 3, "<:carrot:1042829823741001798>"], 
                 "ENCHANTED_POTATO": ["Potato", 3, "<:potato:1042829840140750848>"], 
                 "ENCHANTED_NETHER_STALK": ["Nether Wart", 2.5, "<:NetherWarts:1042829838655959050>"], 
                 "ENCHANTED_HAY_BLOCK": ["Wheat", 1, "<:Wheat:1042829818133217300>"], 
                 "ENCHANTED_SUGAR": ["Sugar", 2, "<:sugar_cane:1042829849456287854>"], 
                 "ENCHANTED_CACTUS_GREEN": ["Cactus", 2, "<:Cactus:1042829821971025951>"], 
                 "ENCHANTED_COCOA": ["Cocoa", 3, "<:CocoaBeans:1042829825141919827>"],
                 "ENCHANTED_PUMPKIN": ["Pumpkin", 1, "<:Pumpkin:1042829845203255357>"],
                 "ENCHANTED_MELON": ["Melon", 5, "<:Melon:1042829832939126854>"],
                 "ENCHANTED_RED_MUSHROOM": ["Red Mushroom", 1, "<:mushroom:1042829836894339072>"],
                 "ENCHANTED_BROWN_MUSHROOM": ["Brown Mushroom", 1, "<:mushroom:1042829836894339072>"]
        }
        bazzar = await self.bot.get_bazzar_data()
        for crop in crops:
            if crop == "ENCHANTED_HAY_BLOCK":
                profit = round((bazzar[crop]["quick_status"]["sellPrice"]/1296*(crops[crop][1]*(farming_fortune/100+1))+bazzar["ENCHANTED_SEEDS"]["quick_status"]["sellPrice"]/160*1.5*(800/100+1))*20.0*3600, 2)
            else:
                profit = round(bazzar[crop]["quick_status"]["sellPrice"]/160*(crops[crop][1]*((farming_fortune/100)+1))*20.0*3600, 2)
            sorting[f"""{crops[crop][2]} **{"{:,}".format(profit)}**\n"""] = float(profit)
        sorting = sorted(sorting.items(), key=lambda x:x[1], reverse=True) 
        for i in sorting:
            send += i[0]
        embed = discord.Embed(title = f"Crop Profits at `{farming_fortune}` Farming Fortune in Coins/hour", description = f"This value is based on the current bazaar **Sell Price** and that you run at a speed of 20 blocks per second while farming. In addition to that we assume that you sell the **Enchanted** variant of each crop!\n\n{send}", color=0x2F3136)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Made by FarmingCouncil",
                    icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed = embed)
async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(crops(bot))