# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from utils import FarmingCouncil

class Public(commands.Cog):
    def __init__(self, bot: FarmingCouncil) -> None:
        self.bot: FarmingCouncil = bot

    @app_commands.command(description="Tells the user how to get support")
    @app_commands.guild_only()
    async def support(self, interaction: discord.Interaction):
        e = discord.Embed(title="Need Support?", description="If you find a bug or need support click [**here**](https://discord.gg/farmingcouncil) to join our support server.", color=0x2F3136)
        e.set_thumbnail(url="https://i.imgur.com/EPbSXCP.png")
        e.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed=e)
        await self.bot.command_counter(interaction)

    @app_commands.command(description="Run this command to see how to get farming equipment")
    @app_commands.guild_only()
    async def shop(self, interaction: discord.Interaction):
        e = discord.Embed(title="Want to buy farming equipment?", description="Our server features a fully working, automated shop for everything that you, as a farmer, might want. From hoes to dicers, we officer everything. Click [**here**](https://discord.gg/farmingcouncil) to join the server and head to the shop category!", color=0x2F3136)
        e.set_thumbnail(url="https://i.imgur.com/nQDKSq9.png")
        e.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed=e)
        await self.bot.command_counter(interaction)
    @app_commands.command(description="Credits for the bot")
    @app_commands.guild_only()
    async def credits(self, interaction: discord.Interaction):
        e = discord.Embed(title="Credits", description="**Director** \n[TheThe](https://www.youtube.com/@FarmingCouncil)\n\n**Development Manager & Lead** \n[CosmicCrow](https://github.com/JeffreyWangDev)\n[NoodlesRush](https://www.youtube.com/watch?v=dQw4w9WgXcQ)\n\n**Developer**\nDyslexus\n\n**Contributers**\nBankhier\nKingRabbit\nLee_Matod", color=0x2F3136)
        e.set_thumbnail(url="https://i.imgur.com/Z75ZL1L.png")
        e.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed=e)
        await self.bot.command_counter(interaction)

    
async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(Public(bot))