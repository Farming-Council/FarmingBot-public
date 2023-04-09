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
        embed = discord.Embed(title = "Loading", description="Evaluating your Hoe's . . .", color=0x2F3136)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Made by FarmingCouncil",
                    icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed = embed)
        try:
            if ign == "":
                ign = await self.bot.get_db_info(int(interaction.user.id))
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
            await interaction.response.send_message(embed=embed)
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
            ratios = {"Cultivating": .25, "Counter": .30, "Dedication": .12, "Replenish": .8, "Turbo": .8, "Harvesting": .5, "Reforge": .12}
            roman = {"I": 0, "II": 1000, "III": 5000,
                     "IV": 25000, "V": 100000, "VI": 300000,
                     "VII": 1500000, "VIII": 5000000, "IX": 20000000,
                     "X": 100000000}
            for hoe in ownedHoes:
                hoeCounter = "0"
                hoeCultivating = "0"
                allAuctionHoes = {}
                hoeStats = ownedHoes[hoe]
                hoeAuctions = await self.bot.get_auction(hoe)
                for item in hoeStats["lore"]:
                    if "Cultivating" in item:
                        try:
                            hoeCultivating = item.split("§")[2][1:]
                            if hoeCultivating == ",":
                                hoeCultivating = item.split(" ")[1].split("§")[0]
                                hoeCultivating = roman[hoeCultivating]
                        except:
                            hoeCultivating = "0" 
                            pass
                    elif "Counter:" in item:
                        hoeCounter = item.split("§e")[1].split(" ")[0]
                try:
                    hoeReforge = hoeStats["attributes"]["modifier"]
                except:
                    hoeReforge = False
                try:
                    for enchantment in hoeStats["attributes"]["enchantments"]:
                        level = hoeStats["attributes"]["enchantments"][enchantment]
                        if "harvesting" in enchantment:
                            hoeHarvesting = level
                        elif "turbo_" in enchantment:
                            hoeTurbo = level
                        if "replenish" in enchantment:
                            hoeReplenish = True
                        else:
                            hoeReplenish = False
                        if "dedication" in enchantment:
                                hoeDedication = level
                except:
                    pass
                for auction in hoeAuctions["auctions"]:
                    cost = auction['starting_bid']
                    cost = cost/100
                    if auction["bin"] == False:
                        continue
                    auction = auction["item"]
                    for item in auction["lore"]:
                        if "Cultivating" in item:
                            try:
                                auctionHoeCultivating = item.split("§")[2][1:]
                                if auctionHoeCultivating == ",":
                                    auctionHoeCultivating = item.split(" ")[1].split("§")[0]
                                    auctionHoeCultivating = roman[auctionHoeCultivating]
                            except:
                                auctionHoeCultivating = "0"
                                pass
                        elif "Counter:" in item:
                            auctionHoeCounter = item.split("§e")[1].split(" ")[0]
                    try:
                        auctionHoeReforge = auction["attributes"]["modifier"]
                    except:
                        auctionHoeReforge = False
                    try:
                        for enchantment in auction["attributes"]["enchantments"]:
                            level = auction["attributes"]["enchantments"][enchantment]
                            if "harvesting" in enchantment:
                                auctionHoeHarvesting = level
                            elif "turbo_" in enchantment:
                                auctionHoeTurbo = level
                            if "replenish" in enchantment:
                                auctionHoeReplenish = True
                            else:
                                auctionHoeReplenish = False
                            if "dedication" in enchantment:
                                auctionHoeDedication = level
                    except:
                        pass
                    try:
                        cult = [int(auctionHoeCultivating.replace(',', '')), int(hoeCultivating.replace(',', ''))]
                    except:
                        cult = 0.00
                        hoeCultivating = 0
                        auctionHoeCultivating = 0
                    try:
                        counter = [int(auctionHoeCounter.replace(',', '')), int(hoeCounter.replace(',', ''))]
                    except:
                        hoeCounter = 0
                        auctionHoeCounter = 0
                        counter = 0.00
                    try:
                        reforge = [auctionHoeReforge, hoeReforge]
                    except:
                        pass
                    try:
                        harvesting = [auctionHoeHarvesting, hoeHarvesting]
                    except:
                        pass
                    try:
                        turbo = [auctionHoeTurbo, hoeTurbo]
                    except:
                        pass
                    try:
                        replenish = [auctionHoeReplenish, hoeReplenish]
                    except:
                        pass
                    try:
                        dedication = [auctionHoeDedication, hoeDedication]
                    except:
                        pass
                    try:
                        cultScore = min(cult)/max(cult)*100*ratios["Cultivating"]
                    except:
                        cultScore = 0.0
                    try:
                        counterScore = min(counter)/max(counter)*100*ratios["Counter"]
                    except:
                        counterScore = 0.0
                    try:
                        if reforge[0] == reforge[1]:
                            reforgeScore = 100*ratios["Reforge"]
                        else:
                            reforgeScore = 0.0
                    except:
                        reforgeScore = 0.0
                    try:
                        harvestingScore = min(harvesting)/max(harvesting)*10*ratios["Harvesting"]
                    except:
                        harvestingScore = 0.0
                    try:
                        turboScore = min(turbo)/max(turbo)*10*ratios["Turbo"]
                    except:
                        turboScore = 0.0
                    try:
                        if replenish[0] == replenish[1]:
                            replenishScore = 10*ratios["Replenish"]
                        else:
                            replenishScore = 0.0
                    except:
                        replenishScore = 0.0
                    try:
                        dedicationScore = min(dedication)/max(dedication)*10*ratios["Dedication"]
                    except:
                        dedicationScore = 0.0
                    hoeScore = cultScore+counterScore+reforgeScore+harvestingScore+turboScore+replenishScore+dedicationScore
                    hoePriceRange = 100-hoeScore
                    hoeMinCost = str(round(int(cost)*int(hoePriceRange), 2)-int(cost))
                    hoeMaxCost = str(round(int(cost)*int(hoePriceRange), 2)+int(cost))
                    if hoeScore < 20:
                        allAuctionHoes[hoeScore] = f"Not enough data on the auction house."
                    else:
                        allAuctionHoes[hoeScore] = f"Counter: **{hoeCounter}**\nCultivating: **{hoeCultivating}**\nEstimated Pricerange: **{numerize.numerize(int(hoeMinCost))} - {numerize.numerize(int(hoeMaxCost))}**"
                    allAuctionHoes = dict(reversed(allAuctionHoes.items()))
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
                    send.append([name, allAuctionHoes[next(iter(allAuctionHoes))]])
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