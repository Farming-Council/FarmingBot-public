# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
if TYPE_CHECKING:
    from utils import FarmingCouncil
    

class Weight(commands.Cog):
    def __init__(self, bot: FarmingCouncil) -> None:
        self.bot: FarmingCouncil = bot

    @app_commands.command(description="Gets a users weight")
    @app_commands.guild_only()
    async def weight(self, interaction: discord.Interaction, ign: str, profile: str=""):
        if ign is None:
            ign = await self.bot.get_db_info(interaction.user.id)
        if type(ign) == int or ign == None:
            ign = interaction.user.display_name
        uuid = await self.bot.get_uuid(ign)
        if profile == None:
            profile = await self.bot.get_most_recent_profile(uuid)
        weight = await calculate_farming_weight(self.bot, ign, profile)
        weight = weight[1]
        embed = discord.Embed(title=f"{ign}'s Weight",description=f"""Collection: **{round(weight["collection_total"]["total"], 2)}**\nFarming Levels: **{round(weight['farming_weight']['farming_weight'], 2)}**\nMinions: **{round(weight['minions']['minion_weight'], 2)}**\nJacob/Gold: **{round(weight["jacub"]['jacub_weight']+weight["gold"]["gold_weight"], 2)}**\n\nTotal: `{round(weight["total"], 2)}`""", color=0x2F3136)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Made by Farming Council",
                        icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed=embed)

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
            weight += gold*0.50
            gold_weight += gold*0.50
        
        return [1,{"profile":profile,"total":weight,"collection_total":{"total":total+mushroomWeight,"cactus":cactus,"carrot":carrot,"cocoa":cocoa,"melon":melon,"wart":wart,"potato":potato,"pumpkin":pumpkin,"sugar":sugar,"wheat":wheat,"mushroom":mushroomWeight},"farming_weight":{"farming_weight":farming_weight,"farming_level":farming_level},"minions":{"minion_weight":minion_weight,"minions":minions},"jacub":{"jacub_weight":jacub_weight,"jacub_perks":jacub_perks},"gold":{"golds":gold,"gold_weight":gold_weight}}]
    else:
        return [0,"Error: No player found. Please try again later or contact the developer at CosmicCrow#6355."]


async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(Weight(bot))
