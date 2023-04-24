# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import TYPE_CHECKING, List

import discord
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from utils import FarmingCouncil

class Blocked(commands.Cog):
    def __init__(self, bot: FarmingCouncil) -> None:
        self.bot: FarmingCouncil = bot
    async def rps_autocomplete(self,interaction: discord.Interaction,current: str,):
            commands = [c.name for c in self.bot.commands]
            return [
                app_commands.Choice(name=command, value=command)
                for command in commands if current.lower() in command.lower()
            ]
    
    banned = []

    async def if_banned(self, interaction: discord.Interaction):
        if interaction.command.name in self.banned:
            await interaction.response.send_message("This command is disabled right now, if you think this is a error, please contact staff!", ephemeral=True)
            return True
        else:
            return False
        

    @app_commands.command(description="Ban a command")
    @app_commands.guild_only()
    @app_commands.autocomplete(choices=rps_autocomplete)
    async def cmdblock(self, interaction: discord.Interaction, command: str):
        if interaction.user.id not in [650431108370137088, 242063157122564106]:
            return await interaction.response.send_message("You are not allowed to use this command!", ephemeral=True)
        if command not in [c.name for c in self.bot.commands]:
            return await interaction.response.send_message("That command does not exist!", ephemeral=True)
        
        if command in self.banned:
            self.banned.pop(self.banned.index(command))
            return await interaction.response.send_message(f"Unblocked {command}!", ephemeral=True)
        else:
            self.banned.append(command)
            return await interaction.response.send_message(f"Blocked {command}!", ephemeral=True)
        
async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(Blocked(bot))