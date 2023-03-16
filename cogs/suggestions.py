# -*- coding: utf-8 -*-
from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from errors import PlayerNotFoundError, InvalidMinecraftUsername

if TYPE_CHECKING:
    import aiomysql
    from utils import FarmingCouncil


class Suggestion(commands.Cog):
    def __init__(self, bot: FarmingCouncil) -> None:
        self.bot: FarmingCouncil = bot

    @app_commands.command(description="Suggest something to the FarmingCouncil Staff Team!")
    @app_commands.guild_only()
    @app_commands.checks.cooldown(3, 86400, key=lambda i: (i.user.id))
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
        channel = self.bot.get_channel(1071503868925575249)
        e = discord.Embed(title="Suggestion", description=f"{suggestion}\n\nSent by: {interaction.user.name}#{interaction.user.discriminator} ({interaction.user.id})\nFrom server: {interaction.guild.name} ({interaction.guild.id})", color=0x2F3136)
        e.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
        if channel:
            await channel.send(embed=e)
        await interaction.response.send_message("Your suggestion has been sent!", ephemeral=True)
        await self.bot.command_counter(interaction)
    @suggest.error
    async def suggest_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            retry_hours = error.retry_after / 3600
            if int(retry_hours) == 0:
                retry_minutes = error.retry_after / 60
                if int(retry_minutes) == 0:
                    return await interaction.response.send_message(
                        f"This command is on cooldown, you can retry in {int(error.retry_after)} seconds.",
                        ephemeral=True,
                    )
                return await interaction.response.send_message(
                    f"This command is on cooldown, you can retry in {int(retry_minutes)} minutes.",
                    ephemeral=True,
                )
            return await interaction.response.send_message(
                f"This command is on cooldown, you can retry in {int(retry_hours)} hours.",
                ephemeral=True,
            )
        raise error

async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(Suggestion(bot))
