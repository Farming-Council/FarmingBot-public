# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
import discord.utils
from discord.utils import get
if TYPE_CHECKING:
    from utils import FarmingCouncil


class Roles(commands.Cog):
    def __init__(self, bot: FarmingCouncil) -> None:
        self.bot: FarmingCouncil = bot

    @app_commands.command(description="Updates your information in linked roles.")
    @app_commands.guild_only()
    async def update(self, interaction: discord.Interaction):
        await interaction.response.defer()
        async with self.bot.session.get(
                f"https://link.farmingcouncil.com/update?code=adf98hsa098poijddsasoijsad87sada8oi&id={interaction.user.id}") as req:
            if req.status == 200:
                json = await req.json()
                if json["status"] == 1:
                    embed = discord.Embed(title="Success", description="Updated your stats!", color=discord.Color.green())
                    await interaction.followup.send(embed=embed)
                else:
                    embed = discord.Embed(title="Error", description=json["msg"], color=discord.Color.red())
                    await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(title="Error", description="An error occurred while updating your roles.", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
        uuid = await self.bot.get_db_info(interaction.user.id)
        weight = await self.bot.calculate_farming_weight(self.bot, uuid)
        role = get(interaction.guild.roles, name="Certified Farmer")
        try:
            if weight >= 3500:
                await interaction.user.add_roles(role)
        except:
            pass
        try:
            if weight < 3500:
                await interaction.user.remove_roles(role)
        except:
            pass


async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(Roles(bot))