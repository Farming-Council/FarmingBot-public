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
        weight = await self.bot.calculate_farming_weight(uuid)
        embed = discord.Embed(title="Weight",description=f"**{ign}** has `{round(weight, 2)}` farming weight!", color=0x2F3136)
        embed.set_image(url='attachment://image.png')
        embed.set_footer(text="Calculations by Bankhier#2004",
                        icon_url="https://i.imgur.com/4YXjLqq.png")
        await interaction.response.send_message(embed=embed)

async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(Weight(bot))
