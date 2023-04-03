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

if TYPE_CHECKING:
    from utils import FarmingCouncil

class contesttracker(commands.Cog):
    def __init__(self, bot: FarmingCouncil):
        self.bot: FarmingCouncil = bot
        self.session: aiohttp.ClientSession | None = None

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()

    @app_commands.command(description="Find Contests in a given time period")
    @app_commands.describe(ign="Hypixel username", profile= "choose the hypixel skyblock profile", time_period="Use the time range ['1 year', '1month', '6days', '2 weeks']")
    async def contests(self, interaction: discord.Interaction, ign: str, profile: str = None, time_period: str = "1 week"):
        await self.bot.command_counter(interaction)
        try:
            await interaction.response.send_message("Loading Graph")
            try:
                uuid = await self.bot.get_uuid(ign)
                if profile == None:
                    profile = await self.bot.get_most_recent_profile(uuid)
                skyblock_data = await self.bot.get_skyblock_data_SLOTHPIXEL(ign, profile, uuid)
            except Exception as e:
                await interaction.edit_original_response(content="Name Invalid, try another IGN")
                return
            contests = skyblock_data["jacob2"]["contests"]
            currenttime = int(time.time())
            currenttime = str(datetime.datetime.fromtimestamp(currenttime))
            time_period_fixed = ""
            amount = ""
            for i in time_period:
                if i not in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                    time_period_fixed += i
                else:
                    amount += i
            time_period = time_period_fixed
            a = amount
            days = ["d", " d", "days", " days", "day", " day"]
            weeks = ["w", " w", "weeks", " weeks", "week", " week"]
            months = ["m", " m", "months", " months", "month", " month"]
            years = ["y", " y", "years", " years", "year", " year"]
            if time_period.lower() in days:
                amount = int(amount)
            elif time_period.lower() in weeks:
                amount = int(amount) * 7
            elif time_period.lower() in months:
                amount = int(amount) * 31
            elif time_period.lower() in years:
                amount = int(amount) * 365
            contestsInTimePeriod = {}
            for contest in contests:
                day_data = contest.split(":")
                day = day_data[0] + "_" + day_data[1]
                skyblockday = day.split("_")
                year, month, day = skyblockday[0], skyblockday[1], skyblockday[2]
                epochSeconds = 1560275700 - 14400 - 432000 - 3600
                totalDays = ((int(year)+1) * 372) + ((int(month)-1) * 31) + (int(day))
                realLifeSeconds = ((totalDays * 20 ) * 60)
                skyblockunix = epochSeconds + realLifeSeconds
                skyblocktime = str(datetime.datetime.fromtimestamp(skyblockunix))
                difference =  datetime.datetime.fromtimestamp(int(time.time())) - datetime.datetime.fromtimestamp(skyblockunix)
                difference = str(difference)
                hours = None
                try: 
                    days = int(difference.split(" day, ")[0])
                except:
                    try:
                        days = int(difference.split(" days, ")[0])
                    except:
                        hours = difference.split(" days, ")[0].split(":")[0]
                if hours == None:
                    if days < amount:
                        contestsInTimePeriod[skyblocktime] = day_data[2]
                else:
                    amount = 24*amount
                    if int(hours) < amount:
                        contestsInTimePeriod[skyblocktime] = day_data[2]
            send = {}
            for contest in contestsInTimePeriod:
                contest = datetime.datetime.strptime(str(contest), '%Y-%m-%d %H:%M:%S')
                
                try:
                    send[contest.hour] = send[contest.hour] + 1
                except:
                    send[contest.hour] = 1
            counter = 0
            timers = []
            timecounter = 0
            counters = ()
            for line in range(0, 24):
                timers.append(counter)
                try:
                    timecounter += int(send[counter])
                    counters += (int(send[counter]),)
                except:
                    counters += (0,)
                counter += 1
            fig, ax = plt.subplots()
            plt.xticks(timers, ["12am", " ", "2am", "", "4am", "", "6am", "", "8am", "", "10am", "", "12pm", " ", "2pm", "", "4pm", "", "6pm", "", "8pm", "", "10pm", " "], rotation=45)
            bars = ax.bar(timers, counters, color="#ec5635")
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_color(None)
            ax.spines['left'].set_color('white')
            ax.spines['right'].set_color(None)
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.tick_params(axis='x', colors='white')
            ax.tick_params(axis='y', colors='white')
            ax.bar_label(bars, color="white", rotation=90,
                        label_type="edge", padding=5)
            plt.savefig('image.png', transparent=True)
            image = discord.File("image.png")
            embed = discord.Embed(
                title="Contests Tracker", description=f"The chart displays the player's **Jacob Contest's** participation hours in a day (UTC) over the past `{a}{time_period}`.  This information provides a comprehensive view of when the player `{ign}` was online and participated in the contest during this time period.\nTotal amount of Jacob Contest participations: `{timecounter}`", color=0x2F3136)
            embed.set_image(url='attachment://image.png')
            embed.set_footer(text="Made by FarmingCouncil",
                            icon_url="https://i.imgur.com/4YXjLqq.png")
            if send == {}:
                embed = discord.Embed(
                    title="Contests Tracker", description=f"`{ign}` has not particpated in any **Jacob Contest's** in the past `{time_period}`", color=0x2F3136)
                await interaction.edit_original_response(content="", embed=embed)
            else:
                await interaction.edit_original_response(content="", embed=embed, attachments=[image])
        except Exception as e:
            print(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)


async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(contesttracker(bot))