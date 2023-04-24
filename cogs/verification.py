# -*- coding: utf-8 -*-
from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from errors import PlayerNotFoundError, InvalidMinecraftUsername, ProfileNotFoundError, HypixelIsDown
import pymysql
from discord.utils import get

import sys, os
if TYPE_CHECKING:
    import aiomysql
    from utils import FarmingCouncil

main_guild = discord.Object(1020742260683448450)
test_guild = discord.Object(1040291074410819594)


class users(commands.Cog):
    def __init__(self, bot: FarmingCouncil) -> None:
        self.bot: FarmingCouncil = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if message.channel.id == 1060834422179495946:
            await message.delete()
        
    @app_commands.command(description="Unlink your in-game hypixel account")
    @app_commands.guild_only()
    async def unlink(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.bot.command_counter(interaction)
        async with self.bot.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute("SELECT * FROM users WHERE user_id = %s", (interaction.user.id))
                result = await cursor.fetchone()
        if result is None:
            return await interaction.followup.send("You are not linked!", ephemeral=True)
        async with self.bot.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute("DELETE FROM users WHERE user_id = %s", (interaction.user.id))
                await conn.commit()
        if interaction.guild.id in [1040291074410819594,1020742260683448450]:
            try:
                verified_role = discord.utils.get(interaction.guild.roles, name="Linked")
                unverified_role = discord.utils.get(interaction.guild.roles, name="Unlinked")
                await interaction.user.remove_roles(verified_role)
                await interaction.user.add_roles(unverified_role)
            except:
                embed = discord.Embed(title="\U0000274c Failed", description="There was an issue while unverifying, please contact a staff member.", color=discord.Colour.red())
                return await interaction.followup.send(embed=embed, ephemeral=True)
        embed = discord.Embed(title="Success", description="You have successfully unlinked your account. To re-link run </link:1082814958871527566>.", color=0x2F3136)
        
        await interaction.followup.send(embed=embed, ephemeral=True)



    @app_commands.command(description="Link your in-game hypixel account")
    @app_commands.guild_only()
    @app_commands.describe(ign="Your Minecraft username", profile="Your Hypixel profile, leave blank for most recently played.")
    async def link(self, interaction: discord.Interaction, ign: str, profile: str=None):
        await interaction.response.defer(ephemeral=True)
        assert isinstance(interaction.user, discord.Member)
        ign = ign or interaction.user.display_name
        await self.bot.command_counter(interaction)
        try:
            uuid = await self.bot.get_uuid(ign)
        except (KeyError, InvalidMinecraftUsername):
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="\U0000274c Failed",
                    description="The given username is invalid or contains special characters.",
                    color=discord.Colour.red()
                )
            )
        try:
            player = await self.bot.get_hypixel_player(uuid)
        except KeyError:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="\U0000274c Failed",
                    description=f"You do not have a linked Discord account.",
                    color=discord.Color.red()
                )
            )
        assert interaction.guild is not None
        if profile == None:
            profile = 0
        try:
            if profile == None:
                profile = await self.bot.get_most_recent_profile(uuid)
            await self.bot.get_skyblock_data_SLOTHPIXEL(ign, profile, uuid)
        except ProfileNotFoundError:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="\U0000274c Failed",
                    description=f"Profile `{profile}` not found.",
                    color=discord.Colour.red()
                )
            )
        except HypixelIsDown:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="\U0000274c Failed",
                    description="Hypixel is currently down, please try again later.",
                    color=discord.Colour.red()
                )
            )
        
        async with self.bot.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute("SELECT * FROM users WHERE user_id = %s", (interaction.user.id))
                result = await cursor.fetchone()
        if result is not None:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="\U0000274c Failed",
                    description="You are already linked! \nUnlink your account with </unlink:1082814958871527565>).",
                    color=discord.Colour.red()
                )
            )
        async with self.bot.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute("SELECT * FROM users WHERE uuid = %s", (uuid))
                result = await cursor.fetchone()
        if result is not None:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="\U0000274c Failed",
                    description="You are already linked! \nUnlink your account with </unlink:1082814958871527565>).",
                    color=discord.Colour.red()
                )
            )
        discord_name = str(interaction.user)
        if player.social_media.discord == discord_name:
            if interaction.guild.id in [1040291074410819594,1020742260683448450]:
                try:
                    verified_role = discord.utils.get(interaction.guild.roles, name="Linked")
                    unverified_role = discord.utils.get(interaction.guild.roles, name="Unlinked")
                    await interaction.user.add_roles(verified_role)
                    await interaction.user.remove_roles(unverified_role)
                except:
                    embed = discord.Embed(title="\U0000274c Failed", description="There was an issue while verifying, please contact an administrator regarding this issue.", color=discord.Color.red())
                    return await interaction.followup.send(embed=embed)
                try:
                    await interaction.user.edit(nick=player.username)
                except:
                    pass
            try:
                async with self.bot.pool.acquire() as conn:
                    conn: aiomysql.Connection
                    async with conn.cursor() as cursor:
                        cursor: aiomysql.Cursor
                        await cursor.execute("INSERT INTO users (user_id, uuid, profile) VALUES (%s, %s, %s)", (interaction.user.id, uuid, profile))
                    await conn.commit()
            except pymysql.IntegrityError as e:
                if e.args[0] == 1062:
                    await interaction.followup.send("Please wait before doing this.", ephemeral=True)
                    return
            embed=discord.Embed(
                title="Success",
                description=f"Linked to `{player.username}`!",
                colour=0x2F3136
            )
            embed.set_footer(text="Made by FarmingCouncil", icon_url="https://i.imgur.com/4YXjLqq.png")
            try:
                uuid = await self.bot.get_uuid(ign)
                weight = await calculate_farming_weight(self.bot, uuid)
                role = get(interaction.guild.roles, name = "Certified Farmer")
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
            except Exception as e:
                print(e)
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
            return await interaction.followup.send(embed=embed)
        await interaction.followup.send(
            embed=discord.Embed(
                title="\U0000274c Failed",
                description="Your Discord account is not linked to your Hypixel account.",
                colour=discord.Colour.red()
            )
        )
async def calculate_farming_weight(self, uuid):
    # Get profile and player data
    async with self.session.get(f"https://elitebot.dev/api/weight/{uuid}") as req:
        try:
            response = await req.json()
        except Exception as e:
            return [0,"Hypixel is down"]
    return response['highest']['farming']['weight']


async def setup(bot: FarmingCouncil) -> None:
    await bot.add_cog(users(bot))


