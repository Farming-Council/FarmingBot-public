# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from discord import Button, ButtonStyle
import aiohttp
import datetime
import time
from utils import FARMING_ITEMS
if TYPE_CHECKING:
    from utils import FarmingCouncil

class MyView(discord.ui.View):
    def __init__(self, bot: FarmingCouncil, ign, profile, farming_level, farming_total_xp, farming_xp_to_next_level, farming_collections, farming_minions, farming_tools, farming_weight, highest_collection_name, highest_collection_amount):
        self.bot: FarmingCouncil = bot
        self.ign = ign
        self.profile = profile
        self.farming_level = farming_level
        self.farming_total_xp = farming_total_xp
        self.farming_xp_to_next_level = farming_xp_to_next_level
        self.farming_collections = farming_collections
        self.farming_minions = farming_minions
        self.farming_tools = farming_tools
        self.farming_weight = farming_weight
        self.highest_collection_name = highest_collection_name
        self.highest_collection_amount = highest_collection_amount
        super().__init__()

    @discord.ui.button(label="Farming Stats", style=discord.ButtonStyle.green)
    async def farming_stats(self, interaction, button):
        embed = discord.Embed(title=f"{self.ign}'s Farming Stats ({self.profile})",
                              color=0x08f730)

        embed.add_field(name="Farming Level",
                        value=f"{self.farming_level}",
                        inline=True)
        embed.add_field(name="Total Farming XP",
                        value=f"{self.farming_total_xp}",
                        inline=True)
        if(self.farming_xp_to_next_level == "MAX"):
            embed.add_field(name="XP to Next Level",
                            value=f"{self.farming_xp_to_next_level}",
                            inline=True)
        else:
            embed.add_field(name="XP to Next Level",
                            value=f"{self.farming_xp_to_next_level}",
                            inline=True)
        embed.add_field(name="Farming Weight",
                        value=f"{self.farming_weight}",
                        inline=True)
        embed.add_field(name="Best Collection",
                        value=f"{self.highest_collection_name}: {self.highest_collection_amount}",
                        inline=True)

        embed.set_footer(text="Made By Farming Council",
                         icon_url="https://i.imgur.com/4YXjLqq.png")

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Collections", style=discord.ButtonStyle.green)
    async def collections(self, interaction, button):
        embed = discord.Embed(title=f"{self.ign}'s Farming Collections ({self.profile})",
                              color=0x08f730)

        embed.add_field(name="Collections",
                        value=f"{self.farming_collections}",
                        inline=True)

        embed.add_field(name="Minions",
                        value=f"{self.farming_minions}",
                        inline=True)

        embed.set_footer(text="Made By Farming Council",
                         icon_url="https://i.imgur.com/4YXjLqq.png")

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Tools and Armor", style=discord.ButtonStyle.green)
    async def tools_and_armor(self, interaction, button):
        embed = discord.Embed(title=f"{self.ign}'s Farming Tools and Armor ({self.profile})",
                              color=0x08f730)

        embed.add_field(name="Farming Tools",
                        value=f"{self.farming_tools}",
                        inline=True)

        embed.set_footer(text="Made By Farming Council",
                         icon_url="https://i.imgur.com/4YXjLqq.png")

        await interaction.response.edit_message(embed=embed, view=self)

class FarmingStats(commands.Cog):
    def __init__(self, bot: FarmingCouncil) -> None:
        self.bot: FarmingCouncil = bot

    @app_commands.command(description="Gets a users farming stats")
    @app_commands.guild_only()
    async def farming(self, interaction: discord.Interaction, ign: str = None, profile: str=""):
        embed = discord.Embed(title=f"Loading",description=f"""Checking {ign}'s Farming Stats!""", color=0x08f730)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Made By Farming Council", 
                    icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed=embed)

        if ign is None:
            ign = await self.bot.get_db_info(interaction.user.id)
        if type(ign) == int or ign == None:
            ign = interaction.user.display_name
        
        try:
            uuid = await self.bot.get_uuid(ign)
        except:
            embed = discord.Embed(title=f"Error",description=f"""{ign} does not exist!""", color=0x08f730)
            embed.set_image(url='attachment://image.png')
            embed.set_footer(text="Made By Farming Council",
                        icon_url="https://i.imgur.com/4YXjLqq.png")
            await interaction.edit_original_response(embed=embed)
            return

        if profile == "":
            profile = await self.bot.get_most_recent_profile(uuid)
        if profile == None:
            profile = await self.bot.get_most_recent_profile(uuid)

        farming_stats = await get_farming_stats(self.bot, ign, profile)
        if farming_stats[0] == 0:
            embed = discord.Embed(title=f"Error",description=f"""{farming_stats[1]}""", color=0x08f730)
            embed.set_image(url='attachment://image.png')
            embed.set_footer(text="Made By Farming Council",
                        icon_url="https://i.imgur.com/4YXjLqq.png")
            await interaction.edit_original_response(embed=embed)
            return
        
        farming_stats = farming_stats[1]
        farming_level = farming_stats["farming_level"]
        farming_total_xp = farming_stats["farming_total_xp"]
        farming_total_xp = f"{farming_total_xp:,}"
        if farming_level == 60:
            farming_xp_to_next_level = "MAX"
        else:
            farming_xp_to_next_level = farming_stats["farming_xp_to_next_level"]
            farming_xp_to_next_level = f"{farming_xp_to_next_level:,}"
        farming_tools = farming_stats["farming_tools"]
        farming_collections = farming_stats["farming_collections"]
        farming_minions = farming_stats["farming_minions"]
        farming_weight = farming_stats["farming_weight"]
        highest_collection_name = farming_stats["highest_collection_name"]
        highest_collection_amount = f"{int(farming_stats['highest_collection_amount']):,}"

        embed = discord.Embed(title=f"{ign}'s Farming Stats ({profile})",
                              color=0x08f730)

        embed.add_field(name="Farming Level",
                        value=f"{farming_level}",
                        inline=True)
        embed.add_field(name="Total Farming XP",
                        value=f"{farming_total_xp}",
                        inline=True)
        if(farming_xp_to_next_level == "MAX"):
            embed.add_field(name="XP to Next Level",
                            value=f"{farming_xp_to_next_level}",
                            inline=True)
        else:
            embed.add_field(name="XP to Next Level",
                            value=f"{farming_xp_to_next_level}",
                            inline=True)
        embed.add_field(name="Farming Weight",
                        value=f"{farming_weight}",
                        inline=True)
        embed.add_field(name="Best Collection",
                        value=f"{highest_collection_name}: {highest_collection_amount}",
                        inline=True)
        embed.set_footer(text="Made By Farming Council",
                 icon_url="https://i.imgur.com/4YXjLqq.png")

        view = MyView(self.bot, ign, profile, farming_level, farming_total_xp, farming_xp_to_next_level, farming_collections, farming_minions, farming_tools, farming_weight, highest_collection_name, highest_collection_amount)
        await self.bot.command_counter(interaction)
        await interaction.edit_original_response(embed=embed, view=view)

async def get_farming_stats(self, ign, profile=""):
    async with self.session.get(f"https://slothpixel.farmingcouncil.com/api/skyblock/profile/{ign}/{profile}") as req:
        try:
            response = await req.json()
        except Exception as e:
            return [0,"Hypixel is down"]
    async with self.session.get(f"https://slothpixel.farmingcouncil.com/api/players/{ign}") as req:
        try:
            player = await req.json()
        except Exception as e:
            return [0,"Hypixel is down"]
    
    json = response
    try:
        error = json["error"]
        return [0,error]
    except:
        pass
    try:
        member = None
        for i in json["members"]:
            if json["members"][i]["uuid"] == player["uuid"]:
                member = json["members"][i]
    except:
        pass

    if member:
        # Farming Level and XP Stats
        try:
            farming_level = int(member["skills"]["farming"]["level"])
        except:
            farming_level = 0
        try:
            farming_total_xp = int(member["skills"]["farming"]["xp"])
        except:
            farming_total_xp = 0
        try:
            farming_xp_to_next_level = int(member["skills"]["farming"]["xpForNext"]) - int(member["skills"]["farming"]["xpCurrent"])
        except:
            farming_xp_to_next_level = 0

        # Farming Tools
        farming_tools = await get_farming_tools(self, member)

        # Farming Collections
        farming_collections, highest_collection_name, highest_collection_amount = await get_farming_collections(self, member)

        # Farming Minions
        farming_minions = await get_farming_minions(self, json)

        # Farming Weight
        farming_weight = await get_farming_weight(self, member, json, profile)
        farming_weight = farming_weight[1]
        farming_weight = round(farming_weight["total"], 2)

        return [1, {"farming_level": farming_level, "farming_total_xp": farming_total_xp, "farming_xp_to_next_level": farming_xp_to_next_level, "farming_tools": farming_tools, "farming_collections": farming_collections, "highest_collection_name": highest_collection_name, "highest_collection_amount": highest_collection_amount ,"farming_minions": farming_minions, "farming_weight": farming_weight}]
    else:
        return [0, "Error: No player found. Please try again later or contact the developer at Mini#9609."]

async def get_farming_collections(self, member):
    collections = member["collection"]
    collections_string = ""
    collections_dict = {
        "WHEAT": ["Wheat", "<:Wheat:1042829818133217300>"],
        "CARROT_ITEM": ["Carrot", "<:carrot:1042829823741001798>"],
        "POTATO_ITEM": ["Potato", "<:potato:1042829840140750848>"],
        "MELON": ["Melon", "<:Melon:1042829832939126854>"],
        "PUMPKIN": ["Pumpkin", "<:Pumpkin:1042829845203255357>"],
        "INK_SACK:3": ["Cocoa Beans", "<:CocoaBeans:1042829825141919827>"],
        "SUGAR_CANE": ["Sugar Cane", "<:sugar_cane:1042829849456287854>"],
        "CACTUS": ["Cactus", "<:Cactus:1042829821971025951>"],
        "MUSHROOM_COLLECTION": ["Mushroom", "<:mushroom:1042829836894339072>"],
        "NETHER_STALK": ["Nether Wart", "<:NetherWarts:1042829838655959050>"]
    }
    collections_amounts = {}
    for collection_type, name_emoji in collections_dict.items():
        try:
            collections_amounts[collection_type] = collections[collection_type]
        except:
            collections_amounts[collection_type] = 0

    # Get the crop with the highest collection amount, the amounts are a string right now though
    highest_collection = max(collections_amounts, key=collections_amounts.get)
    highest_collection_name = f"{collections_dict[highest_collection][1]} {collections_dict[highest_collection][0]}"
    highest_collection_amount = collections_amounts[highest_collection]

    collections_string += f"""
    {collections_dict["WHEAT"][1]} Wheat: {int(collections_amounts["WHEAT"]):,}
    {collections_dict["CARROT_ITEM"][1]} Carrot: {int(collections_amounts["CARROT_ITEM"]):,}
    {collections_dict["POTATO_ITEM"][1]} Potato: {int(collections_amounts["POTATO_ITEM"]):,}
    {collections_dict["MELON"][1]} Melon: {int(collections_amounts["MELON"]):,}
    {collections_dict["PUMPKIN"][1]} Pumpkin: {int(collections_amounts["PUMPKIN"]):,}
    {collections_dict["INK_SACK:3"][1]} Cocoa: {int(collections_amounts["INK_SACK:3"]):,}
    {collections_dict["SUGAR_CANE"][1]} Sugar Cane: {int(collections_amounts["SUGAR_CANE"]):,}
    {collections_dict["CACTUS"][1]} Cactus: {int(collections_amounts["CACTUS"]):,}
    {collections_dict["MUSHROOM_COLLECTION"][1]} Mushroom: {int(collections_amounts["MUSHROOM_COLLECTION"]):,}
    {collections_dict["NETHER_STALK"][1]} Nether Wart: {int(collections_amounts["NETHER_STALK"]):,}
    """

    return collections_string, highest_collection_name, highest_collection_amount


async def get_farming_tools(self, member):
    TOOL_EMOJIS = {
        "COCO_CHOPPER": "<:enGoldHoe:1098448729150853120>", 
        "MELON_DICER": "<:enDiamondAxe:1098448295820533811>",
        "MELON_DICER_2": "<:enDiamondAxe:1098448295820533811>",
        "MELON_DICER_3": "<:enDiamondAxe:1098448295820533811>",
        "PUMPKIN_DICER": "<:enGoldenAxe:1098447886301266013>",
        "PUMPKIN_DICER_2": "<:enGoldenAxe:1098447886301266013>",
        "PUMPKIN_DICER_3": "<:enGoldenAxe:1098447886301266013>",
        "CACTUS_KNIFE": "<:enGoldHoe:1098448729150853120>",
        "FUNGI_CUTTER": "<:enGoldHoe:1098448729150853120>",
        "THEORETICAL_HOE_WHEAT_1": "<:enStoneHoe:1098449459244978197>",
        "THEORETICAL_HOE_WHEAT_2": "<:enIronHoe:1098448660414599189>",
        "THEORETICAL_HOE_WHEAT_3": "<:enDiamondHoe:1098449376512311366>",
        "THEORETICAL_HOE_POTATO_1": "<:enStoneHoe:1098449459244978197>",
        "THEORETICAL_HOE_POTATO_2": "<:enIronHoe:1098448660414599189>",
        "THEORETICAL_HOE_POTATO_3": "<:enDiamondHoe:1098449376512311366>",
        "THEORETICAL_HOE_CARROT_1": "<:enStoneHoe:1098449459244978197>",
        "THEORETICAL_HOE_CARROT_2": "<:enIronHoe:1098448660414599189>",
        "THEORETICAL_HOE_CARROT_3": "<:enDiamondHoe:1098449376512311366>",
        "THEORETICAL_HOE_WARTS_1": "<:enStoneHoe:1098449459244978197>",
        "THEORETICAL_HOE_WARTS_2": "<:enIronHoe:1098448660414599189>",
        "THEORETICAL_HOE_WARTS_3": "<:enDiamondHoe:1098449376512311366>",
        "THEORETICAL_HOE_CANE_1": "<:enStoneHoe:1098449459244978197>",
        "THEORETICAL_HOE_CANE_2": "<:enIronHoe:1098448660414599189>",
        "THEORETICAL_HOE_CANE_3": "<:enDiamondHoe:1098449376512311366>"
    }
    tools = []
    inventory = member["inventory"]
    ender_chest = member["ender_chest"]
    backpacks = member["backpack"]
    for item in inventory:
        if "attributes" in item:
            if item["attributes"]["id"] in FARMING_ITEMS:
                tools.append(f"{TOOL_EMOJIS[item['attributes']['id']]} {item['name'][2:]}")
    for item in ender_chest:
        if "attributes" in item:
            if item["attributes"]["id"] in FARMING_ITEMS:
                tools.append(f"{TOOL_EMOJIS[item['attributes']['id']]} {item['name'][2:]}")
    for backpack in backpacks:
        for item in backpack:
            if "attributes" in item:
                if item["attributes"]["id"] in FARMING_ITEMS:
                    tools.append(f"{TOOL_EMOJIS[item['attributes']['id']]} {item['name'][2:]}")

    if len(tools) == 0:
        return "No Farming Tools\n"
    else:
        tools_string = ""
        for tool in tools:
            tools_string += f"{tool}\n"
        return tools_string

async def get_farming_minions(self, json):
    unlocked_minions = json["unlocked_minions"]
    if unlocked_minions == None:
        return "Error obtaining farming minions\n"
    
    minions_string = ""
    minion_types = ["WHEAT", "CARROT", "POTATO", "MELON", "PUMPKIN", "COCOA", "SUGAR_CANE", "CACTUS", "MUSHROOM", "NETHER_WARTS"]
    minion_levels = {}
    for minion_type in minion_types:
        try:
            minion_levels[minion_type] = unlocked_minions[minion_type]
        except:
            minion_levels[minion_type] = 0

    minions_string += f"""
    <:Wheat:1042829818133217300> Wheat: {minion_levels["WHEAT"]}
    <:carrot:1042829823741001798> Carrot: {minion_levels["CARROT"]}
    <:potato:1042829840140750848> Potato: {minion_levels["POTATO"]}
    <:Melon:1042829832939126854> Melon: {minion_levels["MELON"]}
    <:Pumpkin:1042829845203255357> Pumpkin: {minion_levels["PUMPKIN"]}
    <:CocoaBeans:1042829825141919827> Cocoa: {minion_levels["COCOA"]}
    <:sugar_cane:1042829849456287854> Sugar Cane: {minion_levels["SUGAR_CANE"]}
    <:Cactus:1042829821971025951> Cactus: {minion_levels["CACTUS"]}
    <:mushroom:1042829836894339072> Mushroom: {minion_levels["MUSHROOM"]}
    <:NetherWarts:1042829838655959050> Nether Wart: {minion_levels["NETHER_WARTS"]}
    """

    return minions_string

async def get_farming_weight(self, member, json, profile):
    weight = 0
    if member:   
        try:
            farming_level = int(member["skills"]["farming"]["level"])
        except:
            farming_level = 0
        cactus = int(member["collection"]["CACTUS"])/177254
        carrot = int(member["collection"]["CARROT_ITEM"])/300000
        cocoa = int(member["collection"]["INK_SACK:3"])/267174
        melon = int(member["collection"]["MELON"])/450325
        mushroom = int(member["collection"]["MUSHROOM_COLLECTION"])
        wart = int(member["collection"]["NETHER_STALK"])/250000
        potato = int(member["collection"]["POTATO_ITEM"])/300000
        pumpkin = int(member["collection"]["PUMPKIN"])/90066
        sugar = int(member["collection"]["SUGAR_CANE"])/200000
        wheat = int(member["collection"]["WHEAT"])/100000
        total= cactus + carrot + cocoa + melon + wart + potato + pumpkin + sugar + wheat

        doubleBreakRatio = (cactus/180356 + sugar/200000) / total
        normalRatio = (total - cactus/90178 - sugar/200000) / total
        mushroomWeight = doubleBreakRatio * (mushroom / (2 * 180356)) + normalRatio * (mushroom / 90178)
        weight +=mushroomWeight
        weight += total

        farming_weight = 0

        if farming_level >= 60:
            weight += 250
            farming_weight += 250
        elif farming_level >= 50:
            weight += 100
            farming_weight += 100
        
        minion_weight = 0
        minions= []
        for i in json["unlocked_minions"]:
            if i in ["CACTUS","CARROT","COCOA","MELON","MUSHROOM","NETHER_WARTS","POTATO","PUMPKIN","SUGAR_CANE","WHEAT"]:
                if json["unlocked_minions"][i] == 12:
                    weight+=5
                    minion_weight+=5
                    minions.append(i)
        jacub_weight = 0
        jacub_perks = 0
        try:
            weight += member["jacob2"]["perks"]["double_drops"]*2
            jacub_weight+=member["jacob2"]["perks"]["double_drops"]*2
            jacub_perks+=member["jacob2"]["perks"]["double_drops"]

        except:
            pass

        gold = 0
        gold_weight = 0
        for i in member["jacob2"]["contests"]:
            try:
                if member["jacob2"]["contests"][i]["claimed_medal"] == "gold":
                    gold+=1
            except:
                try:
                    if member["jacob2"]["contests"][i]["claimed_position"]<=member["jacob2"]["contests"][i]["claimed_participants"] * 0.05 + 1:
                        gold+=1
                except:
                    pass
                pass
        if gold >=1000:
            weight += 500
            gold_weight += 500
        else:
            gold = 50 * round(gold / 50)
            gold_weight += gold / 50 *25
        
        return [1,{"profile":profile,"total":weight,"collection_total":{"total":total+mushroomWeight,"cactus":cactus,"carrot":carrot,"cocoa":cocoa,"melon":melon,"wart":wart,"potato":potato,"pumpkin":pumpkin,"sugar":sugar,"wheat":wheat,"mushroom":mushroomWeight},"farming_weight":{"farming_weight":farming_weight,"farming_level":farming_level},"minions":{"minion_weight":minion_weight,"minions":minions},"jacub":{"jacub_weight":jacub_weight,"jacub_perks":jacub_perks},"gold":{"golds":gold,"gold_weight":gold_weight}}]
    else:
        return [0,"Error: No player found. Please try again later or contact the developer at CosmicCrow#6355."]

async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(FarmingStats(bot))