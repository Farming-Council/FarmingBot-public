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
from discord import Button, ButtonStyle
from utils import EMBED_COLOR

if TYPE_CHECKING:
    from utils import FarmingCouncil
    
class MyView(discord.ui.View):
    def __init__(self, bot: FarmingCouncil, farming_fortune):
        self.bot: FarmingCouncil = bot
        self.farming_fortune = farming_fortune
        super().__init__()
    
    @discord.ui.button(label="NPC Price", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction, button):
        sorting = {}
        send =""
        crops = {"ENCHANTED_CARROT": ["Carrot", 3, "<:Carrot:1112740251371323493>", 4], 
                "ENCHANTED_POTATO": ["Potato", 3, "<:Potato:1112740239300116530>", 4], 
                "ENCHANTED_NETHER_STALK": ["Nether Wart", 2.5, "<:NetherWart:1112740241732817028>", 5], 
                "ENCHANTED_HAY_BLOCK": ["Wheat", 1, "<:Wheat:1112740232278847570>", 6], 
                "ENCHANTED_SUGAR": ["Sugar", 2, "<:SugarCane:1112740234422136892>", 5], 
                "ENCHANTED_CACTUS_GREEN": ["Cactus", 2, "<:Cactus:1112755808804024340>", 3], 
                "ENCHANTED_COCOA": ["Cocoa", 3, "<:CocoaBean:1112740248833765456>", 3],
                "ENCHANTED_PUMPKIN": ["Pumpkin", 1, "<:Pumpkin:1112740237605609513>", 10],
                "ENCHANTED_MELON": ["Melon", 5, "<:Melon:1112740247017623592>", 2],
                "ENCHANTED_RED_MUSHROOM": ["Red Mushroom", 1, "<:Mushroom:1112740243527966721>", 10],
                "ENCHANTED_BROWN_MUSHROOM": ["Brown Mushroom", 1, "<:Mushroom:1112740243527966721>", 10]
        }
        if button.label == "Bazaar Price":
            button.label = "NPC Price"
            button.style = discord.ButtonStyle.red
            bazzar = await self.bot.get_bazzar_data()
            for crop in crops:
                if crop == "ENCHANTED_HAY_BLOCK":
                    profit = round((bazzar[crop]["quick_status"]["sellPrice"]/1296*(crops[crop][1]*(self.farming_fortune/100+1))+bazzar["ENCHANTED_SEEDS"]["quick_status"]["sellPrice"]/160*1.5*(self.farming_fortune/100+1))*20.0*3600, 2)
                else:
                    profit = round(bazzar[crop]["quick_status"]["sellPrice"]/160*(crops[crop][1]*((self.farming_fortune/100)+1))*20.0*3600, 2)
                sorting[f"""{crops[crop][2]} **{"{:,}".format(profit)}**\n"""] = float(profit)
            sorting = sorted(sorting.items(), key=lambda x:x[1], reverse=True) 
            for i in sorting:
                send += i[0]
            embed = discord.Embed(title = f"Crop Profits at `{self.farming_fortune}` Farming Fortune in Coins/hour", description = f"This value is based on the current bazaar **Sell Price** and that you run at a speed of 20 blocks per second while farming. In addition to that we assume that you sell the **Enchanted** variant of each crop!\n\n__**BAZZAR PRICE**__\n{send}", color=EMBED_COLOR)
        else:
            button.label = "Bazaar Price"
            button.style = discord.ButtonStyle.green
            for crop in crops:
                if crop == "ENCHANTED_HAY_BLOCK":
                    profit = round(((crops[crop][3]*crops[crop][1]*(self.farming_fortune/100+1))+(3*(2.5-1)*(self.farming_fortune/100+1)))*20.0*3600, 2)
                else:
                    profit = round(crops[crop][3]*crops[crop][1]*((self.farming_fortune/100)+1)*20.0*3600, 2)

                sorting[f"""{crops[crop][2]} **{"{:,}".format(profit)}**\n"""] = float(profit)
            sorting = sorted(sorting.items(), key=lambda x:x[1], reverse=True) 
            for i in sorting:
                send += i[0]
            
            embed = discord.Embed(title = f"Crop Profits at `{self.farming_fortune}` Farming Fortune in Coins/hour", description = f"This value is based on the NPC **Sell Price** and that you run at a speed of 20 blocks per second while farming. In addition to that we assume that you sell the **Enchanted** variant of each crop!\n\n__**NPC PRICE**__\n{send}", color=EMBED_COLOR)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Made by FarmingCouncil",
                    icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.edit_message(embed=embed, view = self)

class crops(commands.Cog):
    def __init__(self, bot: FarmingCouncil):
        self.bot: FarmingCouncil = bot
        self.session: aiohttp.ClientSession | None = None

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

    @app_commands.command(description="Profit Table for Crops Per Hour")
    @app_commands.describe(farming_fortune="Amount of Farming Fortune you have")
    async def cropprofits(self, interaction: discord.Interaction, farming_fortune: int = 800):
        send = ""
        if farming_fortune > 1800:
            await interaction.response.send_message("Sorry, you cannot input farming fortunes over **1800**", ephemeral=True)
            return
        sorting = {}
        crops = {"ENCHANTED_CARROT": ["Carrot", 3, "<:Carrot:1112740251371323493>", 4], 
                "ENCHANTED_POTATO": ["Potato", 3, "<:Potato:1112740239300116530>", 4], 
                "ENCHANTED_NETHER_STALK": ["Nether Wart", 2.5, "<:NetherWart:1112740241732817028>", 5], 
                "ENCHANTED_HAY_BLOCK": ["Wheat", 1, "<:Wheat:1112740232278847570>", 6], 
                "ENCHANTED_SUGAR": ["Sugar", 2, "<:SugarCane:1112740234422136892>", 5], 
                "ENCHANTED_CACTUS_GREEN": ["Cactus", 2, "<:Cactus:1112755808804024340>", 3], 
                "ENCHANTED_COCOA": ["Cocoa", 3, "<:CocoaBean:1112740248833765456>", 3],
                "ENCHANTED_PUMPKIN": ["Pumpkin", 1, "<:Pumpkin:1112740237605609513>", 10],
                "ENCHANTED_MELON": ["Melon", 5, "<:Melon:1112740247017623592>", 2],
                "ENCHANTED_RED_MUSHROOM": ["Red Mushroom", 1, "<:Mushroom:1112740243527966721>", 10],
                "ENCHANTED_BROWN_MUSHROOM": ["Brown Mushroom", 1, "<:Mushroom:1112740243527966721>", 10]
        }
        bazzar = await self.bot.get_bazzar_data()
        for crop in crops:
            if crop == "ENCHANTED_HAY_BLOCK":
                profit = round((bazzar[crop]["quick_status"]["sellPrice"]/1296*(crops[crop][1]*(farming_fortune/100+1))+bazzar["ENCHANTED_SEEDS"]["quick_status"]["sellPrice"]/160*1.5*(farming_fortune/100+1))*20.0*3600, 2)
            else:
                profit = round(bazzar[crop]["quick_status"]["sellPrice"]/160*(crops[crop][1]*((farming_fortune/100)+1))*20.0*3600, 2)
            sorting[f"""{crops[crop][2]} **{"{:,}".format(profit)}**\n"""] = float(profit)
        sorting = sorted(sorting.items(), key=lambda x:x[1], reverse=True) 
        for i in sorting:
            send += i[0]
        embed = discord.Embed(title = f"Crop Profits at `{farming_fortune}` Farming Fortune in Coins/hour", description = f"This value is based on the current bazaar **Sell Price** and that you run at a speed of 20 blocks per second while farming. In addition to that we assume that you sell the **Enchanted** variant of each crop!\n\n__**BAZZAR PRICE**__\n{send}", color=EMBED_COLOR)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Made by FarmingCouncil",
                    icon_url="https://i.imgur.com/4YXjLqq.png")
        view = MyView(self.bot, farming_fortune)
        await self.bot.command_counter(interaction)
        await interaction.response.send_message(embed = embed, view=view)




async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(crops(bot))