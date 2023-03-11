# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from utils import FarmingCouncil

class Roles(commands.Cog):
    def __init__(self, bot: FarmingCouncil) -> None:
        self.bot: FarmingCouncil = bot

    # @app_commands.command(description="Updates your information in linked roles.")
    # @app_commands.guild_only()
    # async def update(self, interaction: discord.Interaction):
    #     await interaction.response.defer()
        
    #     async with self.bot.session.post(f"https://link.farmingcouncil.com/api/update?key1=YHhGf6niyg4miqO20bvb0nedlgFSjjDW&key2=GFNYr8Mvh4ARYWAOpwBU5VgcjGlE2785&key3=F4bornqOxsJp20oSztUXfulHVBcKzB2S&id={interaction.user.id}") as req:
    #         if req.status == 200:
    #             json = await req.json()
    #             if json["status"] == 1:
    #                 embed = discord.Embed(title="Success", description=json["msg"], color=discord.Color.green())
    #                 await interaction.followup.send(embed=embed)
    #             else:
    #                 embed = discord.Embed(title="Error", description=json["msg"], color=discord.Color.red())
    #                 await interaction.followup.send(embed=embed)
    #         else:
    #             embed = discord.Embed(title="Error", description="An error occurred while updating your roles.", color=discord.Color.red())
    #             await interaction.followup.send(embed=embed)


async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(Roles(bot))