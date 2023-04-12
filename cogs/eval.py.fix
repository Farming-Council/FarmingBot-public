import re
import utils
from errors import PlayerNotFoundError, InvalidMinecraftUsername, ProfileNotFoundError, HypixelIsDown
from typing import TYPE_CHECKING
import copy
import discord
from discord import app_commands
from discord.ext import commands

from utils import FarmingCouncil
import aiomysql
import asyncio
import sys, os
from numerize import numerize
import datetime
import json 
import aiohttp

if TYPE_CHECKING:
    from utils import FarmingCouncil

FARMING_ITEMS = [
    "COCO_CHOPPER", 
    "MELON_DICER",
    "MELON_DICER_2",
    "MELON_DICER_3",
    "PUMPKIN_DICER",
    "PUMPKIN_DICER_2",
    "PUMPKIN_DICER_3",
    "CACTUS_KNIFE",
    "FUNGI_CUTTER",
    "THEORETICAL_HOE_WHEAT_1",
    "THEORETICAL_HOE_WHEAT_2",
    "THEORETICAL_HOE_WHEAT_3",
    "THEORETICAL_HOE_POTATO_1",
    "THEORETICAL_HOE_POTATO_2",
    "THEORETICAL_HOE_POTATO_3",
    "THEORETICAL_HOE_CARROT_1",
    "THEORETICAL_HOE_CARROT_2",
    "THEORETICAL_HOE_CARROT_3",
    "THEORETICAL_HOE_WARTS_1",
    "THEORETICAL_HOE_WARTS_2",
    "THEORETICAL_HOE_WARTS_3",
    "THEORETICAL_HOE_CANE_1",
    "THEORETICAL_HOE_CANE_2",
    "THEORETICAL_HOE_CANE_3"
]
FARMING_NAMES = {
    (
        "THEORETICAL_HOE_WHEAT_1",
        "THEORETICAL_HOE_WHEAT_2",
        "THEORETICAL_HOE_WHEAT_3"
    ): "WHEAT",
    (
        "THEORETICAL_HOE_POTATO_1",
        "THEORETICAL_HOE_POTATO_2",
        "THEORETICAL_HOE_POTATO_3" 
    ): "POTATO",
    (
        "THEORETICAL_HOE_CANE_1",
        "THEORETICAL_HOE_CANE_2",
        "THEORETICAL_HOE_CANE_3"
    ): "CANE",
    (
        "THEORETICAL_HOE_CARROT_1",
        "THEORETICAL_HOE_CARROT_2",
        "THEORETICAL_HOE_CARROT_3"
    ): "CARROT",
    (
        "THEORETICAL_HOE_WARTS_1",
        "THEORETICAL_HOE_WARTS_2",
        "THEORETICAL_HOE_WARTS_3"
    ): "WARTS",
    (
        "COCO_CHOPPER"
    ): "COCO",
    (
        "MELON_DICER",
        "MELON_DICER_2",
        "MELON_DICER_3"
    ): "MELON",
    (
        "PUMPKIN_DICER",
        "PUMPKIN_DICER_2",
        "PUMPKIN_DICER_3"
    ): "PUMPKIN",
    (
        "FUNGI_CUTTER"
    ): "MUSHROOMS",
    (
        "CACTUS_KNIFE"
    ): "CACTUS"
}

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

class Pages(discord.ui.View):
    def __init__(self, hoes, user):
        super().__init__(timeout=60.0)
        self.hoes = list(divide_chunks(hoes, 9))
        self.user = user
        self.page = 0
        
    @discord.ui.button(label=" ", style=discord.ButtonStyle.gray,disabled=True,emoji=discord.PartialEmoji.from_str("<:Arrow_Left:1076562615456772146>"))
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title = "Evaluate", description="Evaluation considers a variety of factors such as **Enchants**, **Counters**, **Cultivating**, **Reforges**, **Recombulation**, and **other relevant factors** to determine the most precise and current price range at which your hoe can be sold.", color=0x2F3136)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Made by FarmingCouncil",
                    icon_url="https://i.imgur.com/4YXjLqq.png")

        for thing in self.hoes[self.page-1]:
            embed.add_field(name = thing[0], value=thing[1])
        self.page -= 1
        if self.page < 1:
            self.back.disabled = True
        else:
            self.back.disabled = False
        
        if self.page+1 > len(self.hoes):
            self.next.disabled = True
        else:
            self.next.disabled = False
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=" ", style=discord.ButtonStyle.gray, emoji=discord.PartialEmoji.from_str("<:Arrow_Right:1076562621022621716>"))
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title = "Evaluate", description="Evaluation considers a variety of factors such as **Enchants**, **Counters**, **Cultivating**, **Reforges**, **Recombulation**, and **other relevant factors** to determine the most precise and current price range at which your hoe can be sold.", color=0x2F3136)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Made by FarmingCouncil",
                    icon_url="https://i.imgur.com/4YXjLqq.png")
        self.page += 1
        if self.page < 1:
            self.back.disabled = True
        else:
            self.back.disabled = False
        
        if self.page+1 > len(self.hoes)-1:
            self.next.disabled = True
        else:
            self.next.disabled = False
        for thing in self.hoes[self.page]:
            embed.add_field(name = thing[0], value=thing[1])
        
        await interaction.response.edit_message(embed=embed, view=self)

class eval(commands.Cog):
    def __init__(self, bot: FarmingCouncil):
        self.bot: FarmingCouncil = bot
        self.session: aiohttp.ClientSession | None = None

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

    @app_commands.command(description="Evaluate the price of your hoes!")
    @app_commands.describe(ign="Hypixel username", profile= "choose the hypixel skyblock profile")
    async def evaluate(self, interaction: discord.Interaction, ign: str = "", profile: str = None):
        #* Get skyblock data
        await self.bot.command_counter(interaction)
        embed = discord.Embed(title = "Loading", description="Evaluating your Farming tool's . . .", color=0x2F3136)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Made by FarmingCouncil",
                    icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed = embed)
        try:
            if ign == "":
                ign = await self.bot.get_db_info(int(interaction.user.id))
            if ign == None:
                embed = discord.Embed(title= "Error", description="Name Invalid or Hypixel API is Down, retry later", color=0xFF0000)
                embed.set_image(url='attachment://image.png')
                embed.set_footer(text="Made by FarmingCouncil",
                            icon_url="https://i.imgur.com/4YXjLqq.png")
                await interaction.edit_original_response(embed=embed)
                return
            uuid = await self.bot.get_uuid(ign)
            if profile == None:
                profile = 0
            skyblockData = await self.bot.get_skyblock_data_SLOTHPIXEL(ign, profile, uuid)
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            embed = discord.Embed(title= "Error", description="Name Invalid or Hypixel API is Down, retry later", color=0xFF0000)
            embed.set_image(url='attachment://image.png')
            embed.set_footer(text="Made by FarmingCouncil",
                        icon_url="https://i.imgur.com/4YXjLqq.png")
            await interaction.edit_original_response(embed=embed)
            return
        
        #* Make giant list of all items in (inv, enderchest, etc.)
        allItems = [skyblockData["inventory"], skyblockData["ender_chest"], skyblockData["backpack"]]
        send = []
        #* Get all of the Hoes
        ownedHoes = {}
        try:
            for item in skyblockData["inventory"]:
                try:
                    if item["attributes"]["id"] in FARMING_ITEMS:
                        ownedHoes[item["attributes"]["id"]] = item
                except Exception as e:
                    pass
            for item in skyblockData["ender_chest"]:
                try:
                    if item["attributes"]["id"] in FARMING_ITEMS:
                        ownedHoes[item["attributes"]["id"]] = item
                except Exception as e:
                    pass
            for bag in skyblockData["backpack"]:
                bags = bag
                for item in bags:
                    try:
                        if item["attributes"]["id"] in FARMING_ITEMS:
                            ownedHoes[item["attributes"]["id"]] = item
                    except Exception as e:
                        pass
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        
        #* Search the auction house for those hoes
        try:
            theoreticalHoes = (await self.bot.get_auction("THEORETICAL_HOE"))["auctions"]
            bazaar = await self.bot.get_bazzar_data()
            bazaarEnchants = {
                    "dedication": "ENCHANTMENT_DEDICATION_1",
                    "turbo_": "ENCHANTMENT_TURBO_",
                    "replenish": "ENCHANTMENT_REPLENISH_1",
                    "harvesting": "ENCHANTMENT_HARVESTING_",
                    "cultivating": "ENCHANTMENT_CULTIVATING_1"
            }
            roman = {
                1: 0, 2: 1000, 3: 5000, 
                4: 25000, 5: 100000, 6: 300000, 
                7: 1500000, 8: 5000000, 9: 20000000, 
                10: 100000000
            }
            actualROMAN = {
                "I": 0, "II": 1000,"III": 5000, 
                "IV": 25000, "V": 100000, "VI": 300000, 
                "VII": 1500000,"VIII": 5000000, "IX": 20000000, 
                "X": 100000000
            }
            for hoe in ownedHoes:
                hoeStats = ownedHoes[hoe]
                for item in hoeStats["lore"]:
                    if "Cultivating" in item:
                        try:
                            hoeCultivating = int((item.split("§")[2][1:]).replace(",", ""))
                        except:
                            try:
                                hoeCultivating = actualROMAN[(item.split(" ")[1])]
                            except:
                                hoeCUltivating = 0
                try:
                    hoeCultivating = int(hoeCultivating)
                except:
                    hoeCultivating = 0
                allAuctionHoes = {}
                for hoes in theoreticalHoes:
                    if hoes["bin"] == True:
                        baseHoePrice = hoes["starting_bid"]
                        theoreticalPrice = hoes["starting_bid"]
                        break
                try:
                    tier = int(hoe.split("_")[2])
                except:
                    try:
                        tier = int(hoe.split("_")[3])
                    except:
                        tier = 1
                for crop in FARMING_NAMES:
                    if hoe in crop:
                        cropName = FARMING_NAMES[crop]
                        break
                upgradeCost = await self.bot.hoeTierPrice(f"tier{tier}", cropName, bazaar)
                baseHoePrice = baseHoePrice +  upgradeCost
                try:
                    hoeEnchants = ownedHoes[hoe]["attributes"]['enchantments']
                except KeyError:
                    hoeEnchants = {}
                enchantCost = 0
                for enchant in bazaarEnchants:
                    if enchant in list(dict(hoeEnchants).keys()):
                        if enchant not in ["dedication", "cultivating", "replenish"]:
                            enchantCost += bazaar[f"{bazaarEnchants[enchant]}{hoeEnchants[enchant]}"]["quick_status"]["sellPrice"]
                        else:
                            enchantCost += bazaar[f"{bazaarEnchants[enchant]}"]["quick_status"]["sellPrice"]
                enchantedHoePrice = baseHoePrice + enchantCost
                auctionHoes = (await self.bot.get_past_auction(hoe))
                averageCultivating = []
                for auction in auctionHoes:
                    if auction["bin"] == True and str(auction["bids"]) != "null":  
                        price = auction["startingBid"]
                        e = {}
                        try:
                            enchants = auction['enchantments']
                            for dictionary in enchants:
                                e[dictionary["type"]] = dictionary["level"]
                            enchants = e
                        except KeyError:
                            enchants = {}
                        enchantCost = 0
                        for enchant in bazaarEnchants:
                            if enchant in list(dict(enchants).keys()):
                                if enchant not in ["dedication", "cultivating", "replenish"]:
                                    enchantCost += bazaar[f"{bazaarEnchants[enchant]}{enchants[enchant]}"]["quick_status"]["sellPrice"]
                                else:
                                    enchantCost += bazaar[f"{bazaarEnchants[enchant]}"]["quick_status"]["sellPrice"]
                        prices = price - enchantCost - upgradeCost - theoreticalPrice
                        try:
                            auctionHoeCultivating = auction["nbtData"]["data"]["farmed_cultivating"]
                        except:
                            auctionHoeCultivating = 0
                        try:
                            counterToCoinPrice = auctionHoeCultivating/prices
                            if counterToCoinPrice <= 0:
                                counterToCoinPrice = 1
                        except:
                            counterToCoinPrice = 1
                        if counterToCoinPrice > 0:
                            averageCultivating.append(counterToCoinPrice)
                try:
                    averagePrice = (sum(averageCultivating) / float(len(averageCultivating)))
                except:
                    averagePrice = 1
                hoeCounterPrice = averagePrice * hoeCultivating
                finalHoePrice = enchantedHoePrice + hoeCounterPrice
                
                name = hoeStats['name'][2:]
                if "sugar" in name.lower():                
                    name = str(discord.PartialEmoji.from_str("<:sugar_cane:1042829849456287854>")) +" "+ name
                elif "carrot" in name.lower():                
                    name = str(discord.PartialEmoji.from_str("<:carrot:1042829823741001798>")) +" "+ name
                elif "wart" in name.lower():                
                    name = str(discord.PartialEmoji.from_str("<:NetherWarts:1042829838655959050>")) +" "+ name
                elif "fungi" in name.lower():                
                    name = str(discord.PartialEmoji.from_str("<:mushroom:1042829836894339072>")) +" "+ name
                elif "wheat" in name.lower():                
                    name = str(discord.PartialEmoji.from_str("<:Wheat:1042829818133217300>")) +" "+ name
                elif "potato" in name.lower():                
                    name = str(discord.PartialEmoji.from_str("<:potato:1042829840140750848>")) +" "+ name
                elif "melon" in name.lower():                
                    name = str(discord.PartialEmoji.from_str("<:Melon:1042829832939126854>")) +" "+ name
                elif "pumpkin" in name.lower():                
                    name = str(discord.PartialEmoji.from_str("<:Pumpkin:1042829845203255357>")) +" "+ name
                elif "coco" in name.lower():                
                    name = str(discord.PartialEmoji.from_str("<:CocoaBeans:1042829825141919827>")) +" "+ name
                elif "cactus" in name.lower():
                    name = str(discord.PartialEmoji.from_str("<:Cactus:1042829821971025951>")) +" "+ name
                try:
                    send.append([name, f"Cultivating: **{hoeCultivating:,}**\nPrice: **{round(enchantedHoePrice, 2):,}**"])
                except:
                    send.append([name, f"Not enough data on the auction house."])
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        
        #* embed
        embed = discord.Embed(title = "Evaluate", description="Evaluation considers a variety of factors such as **Enchants**, **Counters**, **Cultivating**, **Reforges**, **Recombulation**, and **other relevant factors** to determine the most precise and current price range at which your hoe can be sold.", color=0x2F3136)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Made by FarmingCouncil",
                    icon_url="https://i.imgur.com/4YXjLqq.png")
        for item in send[0:9]:
            embed.add_field(name = item[0], value=item[1])
        if len(send) > 9:
            await interaction.edit_original_response(embed=embed,view = Pages(send,interaction.user))
        else:
            await interaction.edit_original_response(embed=embed)
        
        
async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(eval(bot))