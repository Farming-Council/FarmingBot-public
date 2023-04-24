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
from utils import FARMING_ITEMS, EMBED_COLOR
if TYPE_CHECKING:
    from utils import FarmingCouncil

MEDAL_EMOJIS = {
    "gold": "<:Top1:1085659408824029355>",
    "silver": "<:Top3:1085659431380996186>",
    "bronze": "<:Top10:1085659447562621049>"
}

COLLECTIONS_DICT = {
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

TOOL_EMOJIS = {
    "COCO_CHOPPER": "<:coco_chopper:1099036047763066880>", 
    "MELON_DICER": "<:melon_dicer:1099036046366359576>",
    "MELON_DICER_2": "<:melon_dicer:1099036046366359576>",
    "MELON_DICER_3": "<:melon_dicer:1099036046366359576>",
    "PUMPKIN_DICER": "<:pumpkin_dicer:1099036044868997140>",
    "PUMPKIN_DICER_2": "<:pumpkin_dicer:1099036044868997140>",
    "PUMPKIN_DICER_3": "<:pumpkin_dicer:1099036044868997140>",
    "CACTUS_KNIFE": "<:cactus_knife:1099058659918630972>",
    "FUNGI_CUTTER": "<:fungi_cutter:1099058661990617172>",
    "THEORETICAL_HOE_WHEAT_1": "<:euclids_wheat_hoe_t1:1099036301426180106>",
    "THEORETICAL_HOE_WHEAT_2": "<:euclids_wheat_hoe_t2:1099036302709633168>",
    "THEORETICAL_HOE_WHEAT_3": "<:euclids_wheat_hoe_t3:1099036062669623386>",
    "THEORETICAL_HOE_POTATO_1": "<:pythagorean_potato_hoe_t1:1099036051491786852>",
    "THEORETICAL_HOE_POTATO_2": "<:pythagorean_potato_hoe_t2:1099036049910542367>",
    "THEORETICAL_HOE_POTATO_3": "<:pythagorean_potato_hoe_t3:1099036048723542076>",
    "THEORETICAL_HOE_CARROT_1": "<:gauss_carrot_hoe_t1:1099036303745622177>",
    "THEORETICAL_HOE_CARROT_2": "<:gauss_carrot_hoe_t2:1099036053920288810>",
    "THEORETICAL_HOE_CARROT_3": "<:gauss_carrot_hoe_t3:1099036052360024175>",
    "THEORETICAL_HOE_WARTS_1": "<:newton_nether_warts_hoe_t1:1099036059200934029>",
    "THEORETICAL_HOE_WARTS_2": "<:newton_nether_warts_hoe_t2:1099036057611280425>",
    "THEORETICAL_HOE_WARTS_3": "<:newton_nether_warts_hoe_t3:1099036305578528929>",
    "THEORETICAL_HOE_CANE_1": "<:turing_sugar_cane_hoe_t1:1099036300360826920>",
    "THEORETICAL_HOE_CANE_2": "<:turing_sugar_cane_hoe_t2:1099036298616000552>",
    "THEORETICAL_HOE_CANE_3": "<:turing_sugar_cane_hoe_t3:1099036306929111141>"
}

IRONMAN_EMOJI = "<:ironman:1099050581454246000>"

class MyView(discord.ui.View):
    def __init__(self, bot: FarmingCouncil, ign, profile, farming_level, farming_total_xp, farming_xp_to_next_level, farming_collections, farming_minions, farming_tools, farming_weight, highest_collection_name, highest_collection_amount, skyblock_level, last_10_contests,best_contest, medal_inventory, unique_golds, total_number_of_contests, total_medals, ironman):
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
        self.skyblock_level = skyblock_level
        self.last_10_contests = last_10_contests
        self.best_contest = best_contest
        self.medal_inventory = medal_inventory
        self.unique_golds = unique_golds
        self.total_number_of_contests = total_number_of_contests
        self.total_medals = total_medals
        self.ironman = ironman
        super().__init__()

    @discord.ui.button(label="Farming Stats", style=discord.ButtonStyle.green)
    async def farming_stats(self, interaction, button):
        embed = discord.Embed(title=f"{self.ign}'s Stats ({self.profile}{self.ironman}) - Lvl {self.skyblock_level}",
                              color=EMBED_COLOR)

        embed.add_field(name="Farming Level",
                        value=f"{self.farming_level}",
                        inline=True)

        if(self.farming_xp_to_next_level == "MAX"):
            embed.add_field(name="XP to Next Level",
                            value=f"{self.farming_xp_to_next_level}",
                            inline=True)
        else:
            embed.add_field(name="XP to Next Level",
                            value=f"{self.farming_xp_to_next_level}",
                            inline=True)

        embed.add_field(name="Total Farming XP",
                        value=f"{self.farming_total_xp}",
                        inline=True)

        embed.add_field(name="Farming Weight",
                        value=f"{self.farming_weight}",
                        inline=True)

        embed.add_field(name="Best Collection",
                        value=f"{self.highest_collection_name}: **{self.highest_collection_amount}**",
                        inline=True)

        embed.set_footer(text="Made by Farming Council - Weight by Elite Bot",
                         icon_url="https://i.imgur.com/4YXjLqq.png")

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Collections", style=discord.ButtonStyle.green)
    async def collections(self, interaction, button):
        embed = discord.Embed(title=f"{self.ign}'s Collections ({self.profile}{self.ironman}) - Lvl {self.skyblock_level}",
                              color=EMBED_COLOR)

        embed.add_field(name="Collections",
                        value=f"{self.farming_collections}",
                        inline=True)

        embed.add_field(name="Minions",
                        value=f"{self.farming_minions}",
                        inline=True)

        embed.set_footer(text="Made by Farming Council",
                         icon_url="https://i.imgur.com/4YXjLqq.png")

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Tools", style=discord.ButtonStyle.green)
    async def tools(self, interaction, button):
        embed = discord.Embed(title=f"{self.ign}'s Tools ({self.profile}{self.ironman}) - Lvl {self.skyblock_level}",
                              color=EMBED_COLOR)

        embed.add_field(name="Farming Tools",
                        value=f"{self.farming_tools}",
                        inline=True)

        embed.set_footer(text="Made by Farming Council",
                         icon_url="https://i.imgur.com/4YXjLqq.png")

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Contests", style=discord.ButtonStyle.green)
    async def contests(self, interaction, button):
        embed = discord.Embed(title=f"{self.ign}'s Contests ({self.profile}{self.ironman}) - Lvl {self.skyblock_level}",
                                color=EMBED_COLOR)

        embed.add_field(name="Last 10 Contests",
                        value=f"{self.last_10_contests}",
                        inline=True)

        embed.add_field(name="Unique Golds",
                        value=f"{self.unique_golds}",
                        inline=True)

        embed.add_field(name="Medals (Owned/Total)",
                        value=f"{self.medal_inventory}",
                        inline=True)
        
        embed.add_field(name="Total Contest Stats",
                        value=f"Best Contest: {self.best_contest}Total Contests: **{self.total_number_of_contests}**\nTotal Medals: **{self.total_medals}**",
                        inline=True)

        embed.set_footer(text="Made by Farming Council",
                        icon_url="https://i.imgur.com/4YXjLqq.png")

        await interaction.response.edit_message(embed=embed, view=self)


class Profile(commands.Cog):
    def __init__(self, bot: FarmingCouncil) -> None:
        self.bot: FarmingCouncil = bot

    @app_commands.command(description="Get a user's farming profile!")
    @app_commands.guild_only()
    async def profile(self, interaction: discord.Interaction, ign: str, profile: str=""):

        try:
            if ign is None:
                uuid = await self.bot.get_db_info(interaction.user.id)
                ign = await self.bot.get_ign(uuid)
            if type(ign) == int or ign == None:
                ign = interaction.user.display_name
        except:
            embed = discord.Embed(title=f"Error",description=f"""{ign} does not exist!""", color=EMBED_COLOR)
            embed.set_image(url='attachment://image.png')
            embed.set_footer(text="Made by Farming Council",
                        icon_url="https://i.imgur.com/4YXjLqq.png")
            await interaction.response.send_message(embed=embed)
            return

        embed = discord.Embed(title=f"Loading",description=f"""Checking {ign}'s Farming Profile!""", color=EMBED_COLOR)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Made By Farming Council", 
                    icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed=embed)
        
        try:
            uuid = await self.bot.get_uuid(ign)
        except:
            embed = discord.Embed(title=f"Error",description=f"""{ign} does not exist!""", color=EMBED_COLOR)
            embed.set_image(url='attachment://image.png')
            embed.set_footer(text="Made by Farming Council",
                        icon_url="https://i.imgur.com/4YXjLqq.png")
            await interaction.edit_original_response(embed=embed)
            return

        if profile == "":
            profile = 0
        if profile == None:
            profile = 0

        skyblock_data = await self.bot.get_skyblock_data_SLOTHPIXEL(ign, profile, uuid)

        try:
            profile = skyblock_data["cute_name"]
            gamemode = skyblock_data["game_mode"]
        except:
            if profile == 0:
                embed = discord.Embed(title=f"Error",description=f"""{ign} does not have a profile!""", color=EMBED_COLOR)
            else:
                embed = discord.Embed(title=f"Error",description=f"""{profile} is not a valid profile for {ign}!\nIf you think this is an error, please open a support ticket.""", color=EMBED_COLOR)
            embed.set_image(url='attachment://image.png')
            embed.set_footer(text="Made by Farming Council",
                        icon_url="https://i.imgur.com/4YXjLqq.png")
            await interaction.edit_original_response(embed=embed)
            return

        farming_stats = await get_farming_stats(self.bot, skyblock_data, uuid)
        if farming_stats[0] == 0:
            embed = discord.Embed(title=f"Error",description=f"""{farming_stats[1]}""", color=EMBED_COLOR)
            embed.set_image(url='attachment://image.png')
            embed.set_footer(text="Made by Farming Council",
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
        skyblock_level =  farming_stats["skyblock_level"]
        last_10_contests = farming_stats["last_10_contests"]
        best_contest = farming_stats["best_contest"]
        medal_inventory = farming_stats["medal_inventory"]
        unique_golds = farming_stats["unique_golds"]
        total_number_of_contests = farming_stats["total_number_of_contests"]
        total_medals = farming_stats["total_medals"]

        is_ironman = False
        ironman_string = ""
        if gamemode == "ironman":
            is_ironman = True
        
        if is_ironman:
            ironman_string += f" {IRONMAN_EMOJI}"

        embed = discord.Embed(title=f"{ign}'s Farming Stats ({profile}{ironman_string}) - Lvl {skyblock_level}",
                              color=EMBED_COLOR)

        embed.add_field(name="Farming Level",
                        value=f"{farming_level}",
                        inline=True)
        
        if(farming_xp_to_next_level == "MAX"):
            embed.add_field(name="XP to Next Level",
                            value=f"{farming_xp_to_next_level}",
                            inline=True)
        else:
            embed.add_field(name="XP to Next Level",
                            value=f"{farming_xp_to_next_level}",
                            inline=True)

        embed.add_field(name="Total Farming XP",
                        value=f"{farming_total_xp}",
                        inline=True)

        embed.add_field(name="Farming Weight",
                        value=f"{farming_weight}",
                        inline=True)

        embed.add_field(name="Best Collection",
                        value=f"{highest_collection_name}: **{highest_collection_amount}**",
                        inline=True)

        embed.set_footer(text="Made by Farming Council - Weight by Elite Bot",
                 icon_url="https://i.imgur.com/4YXjLqq.png")

        view = MyView(self.bot, ign, profile, farming_level, farming_total_xp, farming_xp_to_next_level, farming_collections, farming_minions, farming_tools, farming_weight, highest_collection_name, highest_collection_amount, skyblock_level, last_10_contests,best_contest, medal_inventory, unique_golds, total_number_of_contests, total_medals, ironman_string)
        await self.bot.command_counter(interaction)
        await interaction.edit_original_response(embed=embed, view=view)

async def get_farming_stats(self, skyblock_data, uuid):
    try:
        error = skyblock_data["error"]
        return [0,error]
    except:
        pass
    try:
        member = None
        for i in skyblock_data["members"]:
            if skyblock_data["members"][i]["uuid"] == uuid:
                member = skyblock_data["members"][i]
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
        farming_minions = await get_farming_minions(self, skyblock_data)

        # Farming Weight
        farming_weight = await get_farming_weight(self, member, skyblock_data)
        farming_weight = farming_weight[1]
        farming_weight = round(farming_weight["total"], 2)
        skyblock_level = int(member["leveling"]["experience"] / 100)
        last_10_contests, best_contest, medal_inventory, unique_golds, total_number_of_contests, total_medals = await get_farming_contests(self, member)
        
        return [1, {
            "farming_level": farming_level,
            "farming_total_xp": farming_total_xp,
            "farming_xp_to_next_level": farming_xp_to_next_level,
            "farming_tools": farming_tools,
            "farming_collections": farming_collections,
            "highest_collection_name": highest_collection_name,
            "highest_collection_amount": highest_collection_amount, 
            "farming_minions": farming_minions, 
            "farming_weight": farming_weight, 
            "skyblock_level": skyblock_level,
            "last_10_contests": last_10_contests,
            "best_contest": best_contest, 
            "medal_inventory": medal_inventory,
            "unique_golds": unique_golds,
            "total_number_of_contests": total_number_of_contests,
            "total_medals": total_medals
            }]
    else:
        return [0, "Error: No player found. Please try again later or open a support ticket."]

async def get_farming_collections(self, member):
    collections = member["collection"]
    collections_string = ""
    collections_amounts = {}
    for collection_type, name_emoji in COLLECTIONS_DICT.items():
        try:
            collections_amounts[collection_type] = collections[collection_type]
        except:
            collections_amounts[collection_type] = 0

    highest_collection = max(collections_amounts, key=collections_amounts.get)
    highest_collection_name = f"{COLLECTIONS_DICT[highest_collection][1]} {COLLECTIONS_DICT[highest_collection][0]}"
    highest_collection_amount = collections_amounts[highest_collection]

    collections_string += f"""
    {COLLECTIONS_DICT["WHEAT"][1]} Wheat: **{int(collections_amounts["WHEAT"]):,}**
    {COLLECTIONS_DICT["CARROT_ITEM"][1]} Carrot: **{int(collections_amounts["CARROT_ITEM"]):,}**
    {COLLECTIONS_DICT["POTATO_ITEM"][1]} Potato: **{int(collections_amounts["POTATO_ITEM"]):,}**
    {COLLECTIONS_DICT["MELON"][1]} Melon: **{int(collections_amounts["MELON"]):,}**
    {COLLECTIONS_DICT["PUMPKIN"][1]} Pumpkin: **{int(collections_amounts["PUMPKIN"]):,}**
    {COLLECTIONS_DICT["INK_SACK:3"][1]} Cocoa: **{int(collections_amounts["INK_SACK:3"]):,}**
    {COLLECTIONS_DICT["SUGAR_CANE"][1]} Sugar Cane: **{int(collections_amounts["SUGAR_CANE"]):,}**
    {COLLECTIONS_DICT["CACTUS"][1]} Cactus: **{int(collections_amounts["CACTUS"]):,}**
    {COLLECTIONS_DICT["MUSHROOM_COLLECTION"][1]} Mushroom: **{int(collections_amounts["MUSHROOM_COLLECTION"]):,}**
    {COLLECTIONS_DICT["NETHER_STALK"][1]} Nether Wart: **{int(collections_amounts["NETHER_STALK"]):,}**
    """

    return collections_string, highest_collection_name, highest_collection_amount


async def get_farming_tools(self, member):
    tools = []
    inventory = member["inventory"]
    ender_chest = member["ender_chest"]
    backpacks = member["backpack"]
    for item in inventory:
        if "attributes" in item:
            if "id" in item["attributes"]:
                if item["attributes"]["id"] in FARMING_ITEMS:
                    tools.append(f"{TOOL_EMOJIS[item['attributes']['id']]} {item['name'][2:]}")
    for item in ender_chest:
        if "attributes" in item:
            if "id" in item["attributes"]:
                if item["attributes"]["id"] in FARMING_ITEMS:
                    tools.append(f"{TOOL_EMOJIS[item['attributes']['id']]} {item['name'][2:]}")
    for backpack in backpacks:
        for item in backpack:
            if "attributes" in item:
                if "id" in item["attributes"]:
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
    <:Wheat:1042829818133217300> Wheat: **{minion_levels["WHEAT"]}**
    <:carrot:1042829823741001798> Carrot: **{minion_levels["CARROT"]}**
    <:potato:1042829840140750848> Potato: **{minion_levels["POTATO"]}**
    <:Melon:1042829832939126854> Melon: **{minion_levels["MELON"]}**
    <:Pumpkin:1042829845203255357> Pumpkin: **{minion_levels["PUMPKIN"]}**
    <:CocoaBeans:1042829825141919827> Cocoa: **{minion_levels["COCOA"]}**
    <:sugar_cane:1042829849456287854> Sugar Cane: **{minion_levels["SUGAR_CANE"]}**
    <:Cactus:1042829821971025951> Cactus: **{minion_levels["CACTUS"]}**
    <:mushroom:1042829836894339072> Mushroom: **{minion_levels["MUSHROOM"]}**
    <:NetherWarts:1042829838655959050> Nether Wart: **{minion_levels["NETHER_WARTS"]}**
    """

    return minions_string

async def get_farming_contests(self, member):
    jacob_contents = member["jacob2"]
    medals_inv = jacob_contents["medals_inv"]
    contests = jacob_contents["contests"]

    best_contest_string = ""
    medal_inventory_string = ""
    unique_golds_string = ""
    last_10_contests_string = ""

    total_number_of_contests = len(contests)
    total_gold_medals = 0
    total_silver_medals = 0
    total_bronze_medals = 0

    for contestKey in contests:
        contest = contests[contestKey]
        try:
            medal = contest["claimed_medal"]
        except:
            medal = None
        try:
            position = contest["claimed_position"]
        except:
            position = None
        try:
            participants = contest["claimed_participants"]
        except:
            participants = None

        if medal is not None and medal in ['bronze', 'silver', 'gold']:
            if medal == 'gold':
                total_gold_medals += 1
            elif medal == 'silver':
                total_silver_medals += 1
            elif medal == 'bronze':
                total_bronze_medals += 1
        elif position is not None and participants:
            if position <= participants * 0.05 + 1:
                total_gold_medals += 1
            elif position <= participants * 0.25 + 1:
                total_silver_medals += 1
            elif position <= participants * 0.6 + 1:
                total_bronze_medals += 1
    
    total_medals = total_gold_medals + total_silver_medals + total_bronze_medals

    contest_names = sorted(contests.keys(), reverse=True)
    last_10_contests = contest_names[:10]

    for contest in last_10_contests:
        contest_data = contests[contest]
        if "INK_SACK:3" in contest:
            contest = "INK_SACK:3"
        else:
            contest = contest.split(":")[2]
        try:
            medal = contest_data["claimed_medal"]
            last_10_contests_string += f"{MEDAL_EMOJIS[medal]} {COLLECTIONS_DICT[contest][1]} {COLLECTIONS_DICT[contest][0]} - **{int(contest_data['collected']):,}**\n"
        except:
            last_10_contests_string += f"{COLLECTIONS_DICT[contest][1]} {COLLECTIONS_DICT[contest][0]} - **{int(contest_data['collected']):,}**\n"

    try:
        unique_golds = jacob_contents["unique_golds2"]
        if len(unique_golds) == 0:
            unique_golds_string = "No Unique Golds\n"
        else:
            for unique_gold in unique_golds:
                unique_golds_string += f"{COLLECTIONS_DICT[unique_gold][1]} {COLLECTIONS_DICT[unique_gold][0]}\n"
    except:
        unique_golds_string = "No Unique Golds\n"

    
    best_collected = 0
    best_contest = ""


    for contest, data in contests.items():
        if data["collected"] > best_collected:
            best_collected = data["collected"]
            best_contest = contest

    best_contest_amount = best_collected

    if "INK_SACK:3" in best_contest:
        best_contest_type = "INK_SACK:3"
    else:
        best_contest_type = best_contest.split(":")[2]

    best_contest_string += f"{COLLECTIONS_DICT[best_contest_type][1]} {COLLECTIONS_DICT[best_contest_type][0]} - **{int(best_contest_amount):,}**\n"

    medal_inventory_string += f"""
    {MEDAL_EMOJIS["gold"]} Gold: **{medals_inv["gold"]}** / **{total_gold_medals}**
    {MEDAL_EMOJIS["silver"]} Silver: **{medals_inv["silver"]}** / **{total_silver_medals}**
    {MEDAL_EMOJIS["bronze"]} Bronze: **{medals_inv["bronze"]}** / **{total_bronze_medals}**
    """

    return last_10_contests_string, best_contest_string, medal_inventory_string, unique_golds_string, total_number_of_contests, total_medals

async def get_farming_weight(self, member, json):
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
        
        return [1,{"total":weight,"collection_total":{"total":total+mushroomWeight,"cactus":cactus,"carrot":carrot,"cocoa":cocoa,"melon":melon,"wart":wart,"potato":potato,"pumpkin":pumpkin,"sugar":sugar,"wheat":wheat,"mushroom":mushroomWeight},"farming_weight":{"farming_weight":farming_weight,"farming_level":farming_level},"minions":{"minion_weight":minion_weight,"minions":minions},"jacub":{"jacub_weight":jacub_weight,"jacub_perks":jacub_perks},"gold":{"golds":gold,"gold_weight":gold_weight}}]
    else:
        return [0,"Error: No player found. Please try again later or contact the developer at CosmicCrow#6355."]

async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(Profile(bot))