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
from numerize import numerize
import datetime
import json 

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
        embed=discord.Embed(
            title="Price Evaluation",
            description="Our evaluation takes into account multiple factors such as **supply and demand, hoe counter, rarity, enchantments, tier, and more** to provide the most accurate assessment possible.\n\nPlease note that this evaluation only considers items in your inventory and **excludes** items in backpacks or enderchests.",
            color=0x2F3136
        )

        for i in self.hoes[self.page-1]:
            name = i.name
            if "§" in name:
                name =name[2:]
            if "sugar" in name.lower():                
                name = str(discord.PartialEmoji.from_str("<:sugar_cane:1033981883870105651>")) +" "+ name
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
            embed.add_field(name=name, value=f"**Counter:** {i.counter:,}\n" + f"**Evaluated Price:** {numerize.numerize(int(i.value))}\n", inline=True)
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
        embed=discord.Embed(
            title="Price Evaluation",
            description="Our evaluation takes into account multiple factors such as **supply and demand, hoe counter, rarity, enchantments, tier, and more** to provide the most accurate assessment possible.\n\nPlease note that this evaluation only considers items in your inventory and **excludes** items in backpacks or enderchests.",
            color=0x2F3136
        )
        self.page += 1
        if self.page < 1:
            self.back.disabled = True
        else:
            self.back.disabled = False
        
        if self.page+1 > len(self.hoes)-1:
            self.next.disabled = True
        else:
            self.next.disabled = False
        for i in self.hoes[self.page]:
            name = i.name
            if "§" in name:
                name =name[2:]
            if "sugar" in name.lower():                
                name = str(discord.PartialEmoji.from_str("<:sugar_cane:1033981883870105651>")) +" "+ name
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
            embed.add_field(name=name, value=f"**Counter:** {i.counter:,}\n" + f"**Evaluated Price:** {numerize.numerize(int(i.value))}\n", inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self)

class FarmingItems(commands.Cog):
    def __init__(self, bot: FarmingCouncil) -> None:
        self.bot: FarmingCouncil = bot
    async def on_cog_load(self):
        await self.load_prices()
    
    async def load_prices(self):
        async with self.bot.session.get("https://api.hypixel.net/skyblock/bazaar") as req:
            bazaar = await req.json()
            self.prices = {}
            self.get_price = get_price = lambda name: round(bazaar["products"][name]["quick_status"]["buyPrice"] if name in bazaar["products"] else 0)
            self.prices["JACOBS_TICKET"] = ticket = get_price("JACOBS_TICKET")
            self.prices["RECOMBOBULATOR_3000"] = get_price("RECOMBOBULATOR_3000")
            self.prices["FARMING_FOR_DUMMIES"] = get_price("FARMING_FOR_DUMMIES")
            self.prices["ENCHANTMENT_REPLENISH_1"] = get_price("ENCHANTMENT_REPLENISH_1")
            self.prices["ENCHANTMENT_CULTIVATING_1"] = get_price("ENCHANTMENT_CULTIVATING_1")

            self.prices["PRISMAPUMP"] = int((utils.BRONZE_MEDAL + (ticket * 2)) / 4)
            self.prices["HOE_OF_GREAT_TILLING"] = utils.BRONZE_MEDAL + (ticket * 5)
            self.prices["HOE_OF_GREATER_TILLING"] = utils.SILVER_MEDAL + (ticket * 10)
            self.prices["BASKET_OF_SEEDS"] = (utils.SILVER_MEDAL * 2) + (ticket * 30)
            self.prices["THEORETICAL_HOE"] = utils.GOLD_MEDAL + (ticket * 32)
            self.prices["COCO_CHOPPER"] = utils.GOLD_MEDAL + (ticket * 32)
            self.prices["MELON_DICER"] = utils.GOLD_MEDAL + (ticket * 32)
            self.prices["PUMPKIN_DICER"] = utils.GOLD_MEDAL + (ticket * 32)
            self.prices["FUNGI_CUTTER"] = utils.GOLD_MEDAL + (ticket * 32)
            self.prices["CACTUS_KNIFE"] = utils.GOLD_MEDAL + (ticket * 32)

            for name, items in {
                "CARROT": utils.CARROT_ITEMS,
                "POTATO": utils.POTATO_ITEMS,
                "WARTS": utils.WART_ITEMS,
                "WHEAT": utils.WHEAT_ITEMS,
                "CANE": utils.CANE_ITEMS
            }.items():
                for item in items:
                    self.prices[item] = get_price(item)
                self.prices[f"THEORETICAL_HOE_{name}_1"] = self.prices["THEORETICAL_HOE"] + (
                            512 * self.prices[items[0]])
                self.prices[f"THEORETICAL_HOE_{name}_2"] = self.prices[f"THEORETICAL_HOE_{name}_1"] + (ticket * 64) + (
                            256 * self.prices[items[1]])
                self.prices[f"THEORETICAL_HOE_{name}_3"] = self.prices[f"THEORETICAL_HOE_{name}_2"] + (ticket * 256) + (
                            256 * self.prices[items[2]])
            self.prices["bazaar"] = bazaar
            with open ("price.json", "w") as f:
                json.dump(self.prices,f)
            
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        guild = self.bot.get_guild(1040291074410819594)
        assert guild is not None
        self.staff_role: discord.Role = discord.utils.get(guild.roles, name="Staff")  # type: ignore
        assert self.staff_role is not None




    @app_commands.command(description="Scans for and appraises farming items on your SkyBlock profile.")
    @app_commands.guild_only()
    async def evaluate(self, interaction: discord.Interaction, ign: str, profile: str = None):
        await interaction.response.defer()

        try:
            uuid = await self.bot.get_uuid(ign)
        except ConnectionError as exception:
            print(exception)  # Not caused by user, print for further investigation
            return await self.send_error_response(interaction, "Internal Server Error",
                                                  "Our backend servers encountered an error fetching this information.  If this issue persists, please contact a developer.")
        except (InvalidMinecraftUsername, KeyError):
            return await self.send_error_response(interaction, "Invalid User", "This account doesn't exist!")
        try:
            data = await self.bot.get_skyblock_data(uuid, profile)
        except ConnectionError as exception:
            print(exception)  # Not caused by user, print for further investigation
            return await self.send_error_response(interaction, "Internal Server Error",
                                                  "Our backend servers encountered an error fetching this information.  If this issue persists, please contact a developer.")
            pass
        except PlayerNotFoundError:
            return await self.send_error_response(interaction, "Invalid User",
                                                  "This player hasn't joined SkyBlock before!")
        except ProfileNotFoundError:
            return await self.send_error_response(interaction, "Invalid Profile",
                                                  "This profile doesn't exist!  Try a different profile name or leave it blank to default to their most recently played profile.")

        if "inv_contents" not in data:
            return await self.send_error_response(interaction, "API Disabled",
                                                  "This user has their inventory API disabled!")

        foundItems = await self.findFarmingItems(data["inv_contents"]["data"])
        try:
            for i in data["backpack_contents"]:
                temp_item = await self.findFarmingItems(str(data["backpack_contents"][i]["data"]))
                if temp_item:
                    for item in temp_item:
                        foundItems.append(item)
            enderchest_contents = await self.findFarmingItems(data["ender_chest_contents"]["data"])
        except KeyError:
            enderchest_contents = None
            pass
        if enderchest_contents:
            for i in enderchest_contents:
                foundItems.append(i)
        embed=discord.Embed(
            title="Price Evaluation",
            description="This user has no farming items in their inventory!\nNote: The API takes 2-3 minutes to update." if len(foundItems) == 0 else ("Our evaluation takes into account multiple factors such as **supply and demand, hoe counter, rarity, enchantments, tier, and more** to provide the most accurate assessment possible.\n\nPlease note that this evaluation only considers items in your inventory and **excludes** items in backpacks or enderchests."),
            color=0x2F3136
        )
        for i in foundItems[0:9]:
            name  = i.name
            if "§" in name:
                name =name[2:]
            if "sugar" in name.lower():                
                name = str(discord.PartialEmoji.from_str("<:sugar_cane:1033981883870105651>")) +" "+ name
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
            embed.add_field(name=name, value=f"**Counter:** {i.counter:,}\n" + f"**Evaluated Price:** {numerize.numerize(int(i.value))}\n", inline=True)
        embed.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
        if len(foundItems) > 9:
            await interaction.followup.send(embed=embed,view = Pages(foundItems,interaction.user))
        else:
            await interaction.followup.send(embed=embed)

    async def send_error_response(self, interaction: discord.Interaction, error: str, description: str) -> None:
        return await interaction.followup.send(
            embed=discord.Embed(
                title=error,
                description=description,
                color=discord.Colour.red()
            )
        )
    
    async def send_channel_error_response(self, channel: discord.TextChannel, error: str, description: str) -> None:
        return await channel.send(
            embed=discord.Embed(
                title=error,
                description=description,
                color=discord.Colour.red()
            )
        )

    async def findFarmingItems(self, encoded_data: str) -> list:
        decoded = utils.decode_skyblock_item_data(encoded_data)
        found = []
        for val in decoded["i"]:
            if val == {}:
                continue
            try:
                quantity = val["Count"]
                tag = val["tag"]

                display = tag["display"]
                name = display["Name"]
                lore = display["Lore"]

                attributes = tag["ExtraAttributes"]
                item_id = attributes["id"]

                if str(item_id) not in utils.FARMING_ITEMS:
                    continue
                enchantments = attributes["enchantments"]  if "enchantments" in attributes else {}
                recom = ("rarity_upgrades" in attributes) and str(attributes["rarity_upgrades"]) == "1"
                cultivating = int(str(attributes["farmed_cultivating"])) if "farmed_cultivating" in attributes else 0
                mined = int(str(attributes["mined_crops"])) if "mined_crops" in attributes else 0
                ffd = int(str(attributes["farming_for_dummies_count"])) if "farming_for_dummies_count" in attributes else 0

                found.append(FarmingItem(self, name, lore, item_id, quantity, recom, cultivating, mined, ffd, enchantments
                ))
            except KeyError:
                continue
        return found

import aiohttp
class FarmingItem:
    def __init__(self, items_cog: FarmingItems, name: str, lore: list, item_id: str, quantity: int, recom: bool,
                 cultivating: int, mined: int, ffd: int, enchantments: dict):
        self.items_cog = items_cog
        self.name = name
        self.lore = lore
        self.item_id = item_id
        self.quantity = quantity
        self.recom = recom
        self.cultivating = cultivating
        self.mined = mined
        self.ffd = ffd
        self.enchantments = enchantments
        self.counter: int
        with open ("price.json", "r") as f:
            self.prices = json.load(f)
            bazaar = self.prices["bazaar"]
        self.get_price = get_price = lambda name: round(bazaar["products"][name]["quick_status"]["buyPrice"] if name in bazaar["products"] else 0)
        self.value = self.valuate()
    
    def valuate(self):
        if "WHEAT" in self.item_id: 
            price = self.prices[str(self.item_id)] * 0.90
        elif "WARTS" in self.item_id:
            price = self.prices[str(self.item_id)] * 0.50
        else:
            price = self.prices[str(self.item_id)] * 0.75
        if self.recom:
            price += self.prices["RECOMBOBULATOR_3000"]
        enchantment_price = 0
        for enchantment, level in self.enchantments.items():
            id = f"ENCHANTMENT_{str(enchantment).upper()}_{level}"
            if id not in self.prices:
                self.prices[id] = int(self.get_price(id))
            enchantment_price += self.prices[id]
        if "1" in self.item_id or "2" in self.item_id:
            price += enchantment_price
        else:
            price += enchantment_price * 0.20
        if "MELON" in self.item_id or "PUMPKIN" in self.item_id or "CACTUS" in self.item_id or "COCO" in self.item_id or "FUNGI" in self.item_id:
            price += mined_value(self.cultivating, self.item_id)
            self.counter = self.cultivating
        else:
            if self.mined > 2147483647:
                price += mined_value(self.mined, self.item_id)
                self.counter = self.mined
            elif self.cultivating == 0:
                price += mined_value(self.mined, self.item_id)
                self.counter = self.mined
            else:
                if self.mined > self.cultivating:
                    difference = self.mined - self.cultivating
                    value = mined_value(difference, self.item_id) * 0.10
                    price += value
                price += mined_value(self.cultivating, self.item_id)
                self.counter = self.cultivating
        return price * int(str(self.quantity))

async def setup(bot: FarmingCouncil) -> None:
    items_cog = FarmingItems(bot)
    await bot.add_cog(items_cog)
    await items_cog.load_prices()

def mined_value(mined: int, item_name: str) -> int:
    if "CANE" in item_name or "POTATO" in item_name or "CARROT" in item_name:
        value = min(mined, 100_000_000) * 0.17
        if mined > 100_000_000:
            value += (min(mined, 300_000_000) - 100_000_000) * 0.33
        if mined > 300_000_000:
            value += (min(mined, 500_000_000) - 300_000_000) * 0.05
        if mined > 500_000_000:
            value += (min(mined, 700_000_000) - 500_000_000) * 0.07
        if mined > 700_000_000:
            value += (min(mined, 1_000_000_000) - 700_000_000) * 0.09
        if mined > 1_000_000_000:
            value += (min(mined, 1_500_000_000) - 1_000_000_000) * 0.15
        if mined > 1_500_000_000:
            value += (min(mined, 2_000_000_000) - 1_500_000_000) * 0.14
        if mined > 2_000_000_000:
            value += (min(mined, 3_000_000_000) - 2_000_000_000) * 0.18
        if mined > 3_000_000_000:
            value += (min(mined, 4_000_000_000) - 3_000_000_000) * 0.22
        if mined > 4_000_000_000:
            value += (min(mined, 5_000_000_000) - 4_000_000_000) * 0.26
        # if mined >  5_000_000_000:
            # value += (min(mined, 6_000_000_000) - 5_000_000_000) * 0.15
        if mined > 6_000_000_000:
            value += (mined - 6_000_000_000) * 0.30
        return int(value) if value != None else 0
    if "WHEAT" in item_name:
        value = min(mined, 100_000_000) * 0.30
        if mined > 100_000_000:
            value += (min(mined, 300_000_000) - 100_000_000) * 0.1
        if mined > 300_000_000:
            value += (min(mined, 500_000_000) - 300_000_000) * 0.125
        if mined > 500_000_000:
            value += (min(mined, 700_000_000) - 500_000_000) * 0.16
        if mined > 700_000_000:
            value += (min(mined, 1_000_000_000) - 700_000_000) * 0.19
        if mined > 1_500_000_000:
            value += (min(mined, 2_000_000_000) - 1_000_000_000) * 0.30
        if mined > 2_000_000_000:
            value += (min(mined, 3_000_000_000) - 2_000_000_000) * 0.35
        if mined > 3_000_000_000:
            value += (mined - 3_000_000_000) * 0.40
        return int(value) if value != None else 0
    if "WARTS" in item_name:
        value = min(mined, 100_000_000) * 0.06
        if mined > 100_000_000:
            value += (min(mined, 300_000_000) - 100_000_000) * 0.015
        if mined > 300_000_000:
            value += (min(mined, 500_000_000) - 300_000_000) * 0.0225
        if mined > 500_000_000:
            value += (min(mined, 700_000_000) - 500_000_000) * 0.03
        if mined > 700_000_000:
            value += (min(mined, 1_000_000_000) - 700_000_000) * 0.05
        if mined > 1_500_000_000:
            value += (min(mined, 2_000_000_000) - 1_000_000_000) * 0.09
        if mined > 2_000_000_000:
            value += (min(mined, 3_000_000_000) - 2_000_000_000) * 0.12
        if mined > 3_000_000_000:
            value += (min(mined, 4_000_000_000) - 3_000_000_000) * 0.15
        if mined > 4_000_000_000:
            value += (min(mined, 5_000_000_000) - 4_000_000_000) * 0.17
        if mined > 6_000_000_000:
            value += (mined - 6_000_000_000) * 0.20
        return int(value) if value != None else 0
    if "COCO" in item_name or "MELON" in item_name or "CACTUS" in item_name or "FUNGI" in item_name:
        value = min(mined, 100_000_000) * 0.75
        if mined > 100_000_000:
            value += (min(mined, 300_000_000) - 100_000_000) * 0.05
        if mined > 300_000_000:
            value += (min(mined, 500_000_000) - 300_000_000) * 0.065
        if mined > 500_000_000:
            value += (min(mined, 700_000_000) - 500_000_000) * 0.09
        if mined > 700_000_000:
            value += (min(mined, 1_000_000_000) - 700_000_000) * 0.13
        if mined > 1_500_000_000:
            value += (min(mined, 2_000_000_000) - 1_000_000_000) * 0.19
        if mined > 2_000_000_000:
            value += (min(mined, 3_000_000_000) - 2_000_000_000) * 0.23
        if mined > 3_000_000_000:
            value += (min(mined, 4_000_000_000) - 3_000_000_000) * 0.28
        if mined > 4_000_000_000:
            value += (min(mined, 5_000_000_000) - 4_000_000_000) * 0.33
        return int(value) if value != None else 0
    if "PUMPKIN" in item_name:
        value = min(mined, 100_000_000) * 1
        if mined > 100_000_000:
            value += (min(mined, 300_000_000) - 100_000_000) * 0.1
        if mined > 300_000_000:
            value += (min(mined, 500_000_000) - 300_000_000) * 0.12
        if mined > 500_000_000:
            value += (min(mined, 700_000_000) - 500_000_000) * 0.15
        if mined > 700_000_000:
            value += (min(mined, 1_000_000_000) - 700_000_000) * 0.2
        if mined > 1_500_000_000:
            value += (min(mined, 2_000_000_000) - 1_000_000_000) * 0.32
        if mined > 2_000_000_000:
            value += (mined - 2_000_000_000) * 0.40
        return int(value) if value != None else 0
    if "BASKET_OF_SEEDS" in item_name:
        return 0