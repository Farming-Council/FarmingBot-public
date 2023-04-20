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
    def __init__(self, bot: FarmingCouncil, ign, profile, farming_level, farming_total_xp, farming_xp_to_next_level, farming_collections, farming_minions, farming_tools):
        self.bot: FarmingCouncil = bot
        self.ign = ign
        self.profile = profile
        self.farming_level = farming_level
        self.farming_total_xp = farming_total_xp
        self.farming_xp_to_next_level = farming_xp_to_next_level
        self.farming_collections = farming_collections
        self.farming_minions = farming_minions
        self.farming_tools = farming_tools
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
        embed.add_field(name="Collections",
                        value=f"{farming_collections}",
                        inline=True)
        embed.add_field(name="Minions",
                        value=f"{farming_minions}",
                        inline=True)
        embed.set_footer(text="Made By Farming Council",
                 icon_url="https://i.imgur.com/4YXjLqq.png")

        view = MyView(self.bot, ign, profile, farming_level, farming_total_xp, farming_xp_to_next_level, farming_collections, farming_minions, farming_tools)
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
        farming_collections = await get_farming_collections(self, member)

        # Farming Minions
        farming_minions = await get_farming_minions(self, json)

        return [1, {"farming_level": farming_level, "farming_total_xp": farming_total_xp, "farming_xp_to_next_level": farming_xp_to_next_level, "farming_tools": farming_tools, "farming_collections": farming_collections, "farming_minions": farming_minions}]
    else:
        return [0, "Error: No player found. Please try again later or contact the developer at Mini#9609."]

async def get_farming_collections(self, member):
    collections_string = ""
    try:
        wheat_collection = member['collection']['WHEAT']
    except:
        wheat_collection = 0
    try:
        carrot_collection = member["collection"]["CARROT_ITEM"]
    except:
        carrot_collection = 0
    try:
        potato_collection = member["collection"]["POTATO_ITEM"]
    except:
        potato_collection = 0
    try:
        melon_collection = member["collection"]["MELON"]
    except:
        melon_collection = 0
    try:
        pumpkin_collection = member["collection"]["PUMPKIN"]
    except:
        pumpkin_collection = 0
    try:
        cocoa_collection = member["collection"]["INK_SACK:3"]
    except:
        cocoa_collection = 0
    try:
        sugar_cane_collection = member["collection"]["SUGAR_CANE"]
    except:
        sugar_cane_collection = 0
    try:
        cactus_collection = member["collection"]["CACTUS"]
    except:
        cactus_collection = 0
    try:
        mushroom_collection = member["collection"]["MUSHROOM_COLLECTION"]
    except:
        mushroom_collection = 0
    try:
        nether_wart_collection = member["collection"]["NETHER_STALK"]
    except:
        nether_wart_collection = 0

    collections_string += f"""
    <:Wheat:1042829818133217300> Wheat: {int(wheat_collection):,}
    <:carrot:1042829823741001798> Carrot: {int(carrot_collection):,}
    <:potato:1042829840140750848> Potato: {int(potato_collection):,}
    <:Melon:1042829832939126854> Melon: {int(melon_collection):,}
    <:Pumpkin:1042829845203255357> Pumpkin: {int(pumpkin_collection):,}
    <:CocoaBeans:1042829825141919827> Cocoa: {int(cocoa_collection):,}
    <:sugar_cane:1042829849456287854> Sugar Cane: {int(sugar_cane_collection):,}
    <:Cactus:1042829821971025951> Cactus: {int(cactus_collection):,}
    <:mushroom:1042829836894339072> Mushroom: {int(mushroom_collection):,}
    <:NetherWarts:1042829838655959050> Nether Wart: {int(nether_wart_collection):,}
    """


    return collections_string


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
                # Append the tool emoji and the name of the tool
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
    if(unlocked_minions == None):
        return "Error obtaining farming minions\n"
    minions_string = ""
    try:
        wheat_minion = unlocked_minions["WHEAT"]
    except:
        wheat_minion = 0
    try:
        carrot_minion = unlocked_minions["CARROT"]
    except:
        carrot_minion = 0
    try:
        potato_minion = unlocked_minions["POTATO"]
    except:
        potato_minion = 0
    try:
        melon_minion = unlocked_minions["MELON"]
    except:
        melon_minion = 0
    try:
        pumpkin_minion = unlocked_minions["PUMPKIN"]
    except:
        pumpkin_minion = 0
    try:
        cocoa_minion = unlocked_minions["COCOA"]
    except:
        cocoa_minion = 0
    try:
        sugar_cane_minion = unlocked_minions["SUGAR_CANE"]
    except:
        sugar_cane_minion = 0
    try:
        cactus_minion = unlocked_minions["CACTUS"]
    except:
        cactus_minion = 0
    try:
        mushroom_minion = unlocked_minions["MUSHROOM"]
    except:
        mushroom_minion = 0
    try:
        nether_wart_minion = unlocked_minions["NETHER_WARTS"]
    except:
        nether_wart_minion = 0

    minions_string += f"""
    Wheat: {wheat_minion}
    Carrot: {carrot_minion}
    Potato: {potato_minion}
    Melon: {melon_minion}
    Pumpkin: {pumpkin_minion}
    Cocoa: {cocoa_minion}
    Sugar Cane: {sugar_cane_minion}
    Cactus: {cactus_minion}
    Mushroom: {mushroom_minion}
    Nether Wart: {nether_wart_minion}
    """

    return minions_string

async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(FarmingStats(bot))