# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from utils import EMBED_COLOR
if TYPE_CHECKING:
    from utils import FarmingCouncil
    

class Weight(commands.Cog):
    def __init__(self, bot: FarmingCouncil) -> None:
        self.bot: FarmingCouncil = bot

    @app_commands.command(description="Gets a users weight")
    @app_commands.guild_only()
    async def weight(self, interaction: discord.Interaction, ign: str = None, profile: str=""):

        if ign is None:
            uuid = await self.bot.get_db_info(interaction.user.id)
            ign = await self.bot.get_ign(uuid)
        if type(ign) == int or ign == None:
            ign = interaction.user.display_name

        embed = discord.Embed(title=f"Loading",description=f"""Obtaining {ign}'s Farming Weight!""", color=EMBED_COLOR)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Weight By Elite Bot",
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

        weight = await calculate_farming_weight(self.bot, ign, profile)
        if (weight[0] == 0):
            embed = discord.Embed(title=f"Error",description=f"""{weight[1]}""", color=EMBED_COLOR)
            embed.set_image(url='attachment://image.png')
            embed.set_footer(text="Weight By Elite Bot",
                        icon_url="https://i.imgur.com/4YXjLqq.png")
            await interaction.edit_original_response(embed=embed)
            return
        
        weight = weight[1]
        embed = discord.Embed(title=f"{ign}'s Weight",description=f"""Collection: **{round(weight["collection_total"]["total"], 2)}**\nFarming Levels: **{round(weight['farming_weight']['farming_weight'], 2)}**\nMinions: **{round(weight['minions']['minion_weight'], 2)}**\nAnita / Gold medals: **{round(weight["jacob"]['jacob_weight']+weight["gold"]["gold_weight"], 2)}**\n\nTotal: `{round(weight["total"], 2)}`\n\nView full calculations on [elitebot.dev](https://elitebot.dev/)""", color=EMBED_COLOR)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Weight By Elite Bot",
                        icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.edit_original_response(embed=embed)

def try_it(member,collat):
    try:
        return int(member["collection"][collat])
    except:
        return 1

async def calculate_farming_weight(self, ign,profile = ""):
    # Get profile and player data
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
        return [2,error]
    except:
        pass
    try:
        weight = 0
        member = None
        for i in json["members"]:
            if json["members"][i]["uuid"] == player["uuid"]:
                member = json["members"][i]
    except:
        pass
    if member:
        try:
            farming_level = int(member["skills"]["farming"]["level"])
        except:
            farming_level = 0
        cactus = try_it(member,"CACTUS")/177254
        carrot = try_it(member,"CARROT_ITEM")/300000
        cocoa = try_it(member,"INK_SACK:3")/267174
        melon = try_it(member,"MELON")/450325
        mushroom = try_it(member,"MUSHROOM_COLLECTION")
        wart = try_it(member,"NETHER_STALK")/250000
        potato = try_it(member,"POTATO_ITEM")/300000
        pumpkin = try_it(member,"PUMPKIN")/90066
        sugar = try_it(member,"SUGAR_CANE")/200000
        wheat = try_it(member,"WHEAT")/100000
        total= cactus + carrot + cocoa + melon + wart + potato + pumpkin + sugar + wheat

        # Caculate weight for mushrooms dynamically
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
        jacob_weight = 0
        jacob_perks = 0
        try:
            weight += member["jacob2"]["perks"]["double_drops"]*2
            jacob_weight+=member["jacob2"]["perks"]["double_drops"]*2
            jacob_perks+=member["jacob2"]["perks"]["double_drops"]

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
        
        return [1,{"profile":profile,"total":weight,"collection_total":{"total":total+mushroomWeight,"cactus":cactus,"carrot":carrot,"cocoa":cocoa,"melon":melon,"wart":wart,"potato":potato,"pumpkin":pumpkin,"sugar":sugar,"wheat":wheat,"mushroom":mushroomWeight},"farming_weight":{"farming_weight":farming_weight,"farming_level":farming_level},"minions":{"minion_weight":minion_weight,"minions":minions},"jacob":{"jacob_weight":jacob_weight,"jacob_perks":jacob_perks},"gold":{"golds":gold,"gold_weight":gold_weight}}]
    else:
        return [0,"Error Obtaining Weight"]


async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(Weight(bot))