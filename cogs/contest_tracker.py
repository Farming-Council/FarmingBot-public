# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING,Literal

import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import aiomysql
import json
import time
import datetime
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from utils import FarmingCouncil


class contesttracker(commands.Cog):
    def __init__(self, bot: FarmingCouncil):
        self.bot: FarmingCouncil = bot
        self.session: aiohttp.ClientSession | None = None
        
    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
    
    @app_commands.command(description="Find Contests in a given time period")
    @app_commands.guild_only()
    @app_commands.describe(ign = "Hypixel username", time_period = "Time range you want to")
    async def contests(self, interaction: discord.Interaction, ign: str, time_period: Literal["1 day", "1 week", "1 month", "6 months", "1 year", "2 years", "3 years"] = "1 week"):
        try:
            uuid = await self.bot.get_uuid(ign)
            profile = await self.bot.get_most_recent_profile(uuid)
            skyblock_data = await self.bot.get_skyblock_data_SLOTHPIXEL(ign, profile, uuid)
        except Exception as e:
            await interaction.response.send_message("Name Invalid, try another IGN", ephemeral=True)
            return
        await interaction.response.send_message("Loading Graph")
        contests = skyblock_data["jacob2"]["contests"]
        currenttime = int(time.time())
        timestable = {"1 day": 86400, "1 week": 604800, "1 month": 2629743, "6 months": 15778458, "1 year": 31556926, "2 years": 31556926*2, "3 years": 31556926*3}
        contestsInTimePeriod = {}
        for contest in contests:
            day_data = contest.split(":")
            day = day_data[0] + "_"+ day_data[1]
            skyblockday  = day.split("_")
            year, month, day = skyblockday[0], skyblockday[1], skyblockday[2]
            skyblockunix = ((int(year)+1)*365*60*20)+(int(day)*31*60*20)+(int(month)*60*20)+1560275700
            if currenttime // timestable[time_period] == ((skyblockunix // timestable[time_period])+1):
                contestsInTimePeriod[skyblockunix] = day_data[2]
        send = {}
        for contest in contestsInTimePeriod:
            try:
                send[datetime.datetime.fromtimestamp(contest).hour] = send[datetime.datetime.fromtimestamp(contest).hour] + 1
            except:
                send[datetime.datetime.fromtimestamp(contest).hour] = 1
        counter = 0
        timers = []
        timecounter = 0
        counters = ()
        for line in range(0, 24):
            timers.append(line)
            try:
                timecounter += int(send[counter])
                counters += (int(send[counter]),)
            except:
                counters += (0,)
            counter += 1
        fig, ax = plt.subplots()
        plt.xticks(timers, ["12am ", "", "2am",  "", "4am",  "", "6am",  "", "8am",  "", "10am",  "", "12pm",  "", "2pm",  "", "4pm",  "", "6pm",  "", "8pm",  "", "10pm", ""], rotation=45)
        bars = ax.bar(timers, counters, color="#ec5635")
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color(None)
        ax.spines['left'].set_color('white')
        ax.spines['right'].set_color(None)
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.bar_label(bars, color="white", rotation=90, label_type= "edge", padding=5) 
        plt.savefig('image.png', transparent=True) 
        image = discord.File("image.png")    
        embed = discord.Embed(title = "Contests Tracker", description = f"The chart displays the player's **Jacob Contest's** participation hours in a day (UTC) over the past `{time_period}`.  This information provides a comprehensive view of when the player `{ign}` was online and participated in the contest during this time period.\nTotal amount of Jacob Contest participations: `{timecounter}`",color=0x2F3136)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
        if send == {}:
            embed = discord.Embed(title = "Contests Tracker", description = f"`{ign}` has not particpated in any **Jacob Contest's** in the past `{time_period}`",color=0x2F3136)
            await interaction.edit_original_response(content="", embed = embed)
        else:
            await interaction.edit_original_response(content="", embed = embed, attachments= [image])

async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(contesttracker(bot))