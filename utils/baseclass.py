# -*- coding: utf-8 -*-
from __future__ import annotations

import pkgutil

from typing import Any, ClassVar

import aiohttp
import aiomysql
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

from errors import InvalidMinecraftUsername, PlayerNotFoundError, ProfileNotFoundError, HypixelIsDown
from _types import HypixelPlayer, HypixelSocialMedia

load_dotenv()

class FarmingCouncil(commands.Bot):
    API_KEY: ClassVar[str] = os.environ.get("hypixel_api_key")
    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=discord.Intents.default(), help_command=None, owner_id=702385226407608341)
        self.session: aiohttp.ClientSession | None = None
        self.pool: aiomysql.Pool = None  # type: ignore

    async def on_command_error(
            self,
            context: commands.Context[FarmingCouncil],
            exception: commands.CommandError,
            /
    ) -> None:
        if isinstance(exception, commands.NotOwner):
            await context.send(
                embed=discord.Embed(
                    title="\U00002757 Error",
                    description="You need to own this bot to use this command!",
                    colour=discord.Colour.red()
                )
            )
        else:
            raise exception

    async def setup_hook(self) -> None:
        #await self.load_extension("cogs.rent_calc")
        self.session = aiohttp.ClientSession()
        self.pool = await aiomysql.create_pool(
            host=os.environ.get("DATABASE_HOST"),
            user=os.environ.get("DB_USERNAME"),
            password=os.environ.get("DB_PASSWORD"),
            db=os.environ.get("DB_NAME"),
            loop=self.loop,
            port = 32813
        )
        async with self.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(
                    """CREATE TABLE IF NOT EXISTS verification (
                        user_id BIGINT NOT NULL UNIQUE,
                        ign TEXT NOT NULL,
                        profile TEXT NOT NULL,
                        timestamp BIGINT DEFAULT CURRENT_TIMESTAMP NOT NULL
                    )"""
                )
                await cursor.execute(
                    """CREATE TABLE IF NOT EXISTS tutorial (
                        cropname TEXT UNIQUE,
                        link TEXT
                    )"""
                )
                await cursor.execute(
                    """CREATE TABLE IF NOT EXISTS commandcounter (
                        cmd_name TEXT NOT NULL,
                        user_id BIGINT,
                        timestamp BIGINT DEFAULT CURRENT_TIMESTAMP NOT NULL
                    )"""
                )
                await conn.commit()


        for cog in pkgutil.iter_modules(["cogs"], prefix="cogs."):
            await self.load_extension(cog.name)

    async def on_ready(self) -> None:
        #await self.tree.sync()
        await self.tree.sync()
        print(f"Logged in as {self.user} ({self.user.id})")  # type: ignore

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()
        if self.pool is not None:
            self.pool.close()
            await self.pool.wait_closed()
        await super().close()
    async def get_crop(self,cropname):
        async with self.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute("SELECT * FROM tutorial WHERE cropname = %s", (str(cropname),))
                data = await cursor.fetchone()
        return data


    async def command_counter(self,interaction: discord.Interaction):
        async with self.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute("INSERT INTO commandcounter (cmd_name, user_id) VALUES (%s, %s)", (str(interaction.command.name), int(interaction.user.id)))
                await conn.commit()


    async def get_uuid(self, username: str) -> str:
        """Gets the UUID of a Minecraft player with the given username.
        Parameters
        ----------
        username: :class:`str`
            The username of the player.
        Returns
        -------
        :class:`str`
            The UUID of the player.
        Raises
        ------
        ConnectionError
            The aiohttp session has not been instantiated.
        InvalidMinecraftUsername
            The given username contained special characters that weren't valid.
        KeyError
            The given username was invalid.
        """
        if self.session is None:
            raise ConnectionError("aiohttp session has not been set")
        if not username.isalnum() and "_" not in username:
            raise InvalidMinecraftUsername(username)
        async with self.session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as req:
            if req.status != 200:
                raise KeyError(f"Recieved status code: {req.status}")
            js = await req.json()
            return js["id"]

    async def get_hypixel_player(self, uuid: str) -> HypixelPlayer:
        """Gets a Hypixel player object from the given UUID.

        Parameters
        ----------
        uuid: :class:`str`
            The UUID of the player.

        Returns
        -------
        :class:`HypixelPlayer`
            The constructed player object.

        Raises
        ------
        ConnectionError
            The aiohttp session has not been instantiated.
        PlayerNotFoundError
            The player could not be located by the Hypixel API.
        """
        if self.session is None:
            raise ConnectionError("aiohttp session has not been set")
        async with self.session.get(
            f"https://api.hypixel.net/player?uuid={uuid}",
            headers={"API-Key": self.API_KEY}
        ) as req:
            info = await req.json()
            if not info["success"] or not info["player"]:
                raise PlayerNotFoundError(uuid=uuid)
            social_media = HypixelSocialMedia.from_dict(info["player"]["socialMedia"])
            return HypixelPlayer(
                username=info["player"]["displayname"],
                uuid=info["player"]["uuid"],
                social_media=social_media
            )

    async def get_skyblock_data(self, uuid: str, profile: str | None) -> HypixelPlayer:
        """Gets a player's SkyBolock data from the given UUID

        Parameters
        ----------
        uuid: :class:`str`
            The UUID of the player.
        profile: Union[:class:`str`, :class:None]
            The profile name.

        Returns
        -------
        :class:`dict`
            The profile data returned by the API

        Raises
        ------
        ConnectionError
            The aiohttp session has not been instantiated.
        PlayerNotFoundError
            The player could not be located by the Hypixel API.
        """
        if self.session is None:
            raise ConnectionError("aiohttp session has not been set")
        async with self.session.get(
            f"https://api.hypixel.net/skyblock/profiles?uuid={uuid}",
            headers={"API-Key": self.API_KEY}
        ) as req:
            try:
                info = await req.json()
            except:
                raise HypixelIsDown()

            if not info["success"] or not info["profiles"]:
                raise PlayerNotFoundError(uuid=uuid)

            profiles = info["profiles"]
            if len(profiles) == 0:
                raise PlayerNotFoundError(uuid=uuid)

            if profile is not None:
                for profileData in profiles:
                    if profileData["cute_name"].lower() == profile.lower():
                        return profileData["members"][uuid]
                raise ProfileNotFoundError(uuid=uuid, profile=profile)

            latest_profile_index = 0
            latest_profile_last_save = 0

            i = 0
            for profileData in profiles:
                if "last_save" in profileData:  # Not all profiles have this
                    last_save = profileData["last_save"]
                    if last_save > latest_profile_last_save:
                        latest_profile_index = i
                        latest_profile_last_save = last_save
                i += 1

            return profiles[latest_profile_index]["members"][uuid]
    async def get_skyblock_data_SLOTHPIXEL(self, ign: str, profile: str | None, uuid: str) -> HypixelPlayer:
        if self.session is None:
            raise ConnectionError("aiohttp session has not been set")
        async with self.session.get(
            f"https://api.slothpixel.me/api/skyblock/profile/{ign}/{profile}",
            headers={"API-Key": self.API_KEY}
        ) as req:
            try:
                info = await req.json()
            except:
                raise HypixelIsDown()
            return info["members"][uuid]
    async def get_bazzar_data(self):
        if self.session is None:
            raise ConnectionError("aiohttp session has not been set")
        async with self.session.get(
            f"https://api.slothpixel.me/api/skyblock/bazaar",
            headers={"API-Key": self.API_KEY}
        ) as req:
            try:
                info = await req.json()
            except:
                raise HypixelIsDown()
            return info
    async def get_most_recent_profile(self, uuid):
        if self.session is None:
            raise ConnectionError("aiohttp session has not been set")
        async with self.session.get(
            f"https://api.hypixel.net/skyblock/profiles?uuid={uuid}",
            headers={"API-Key": self.API_KEY}
        ) as req:
            try:
                info = await req.json()
            except:
                raise HypixelIsDown()

            if not info["success"] or not info["profiles"]:
                raise PlayerNotFoundError(uuid=uuid)

            profiles = info["profiles"]
            if len(profiles) == 0:
                raise PlayerNotFoundError(uuid=uuid)

            latest_profile_index = 0
            latest_profile_last_save = 0
            i = 0
            for profileData in profiles:
                if "last_save" in profileData:  # Not all profiles have this
                    last_save = profileData["last_save"]
                    if last_save > latest_profile_last_save:
                        latest_profile_index = i
                        latest_profile_last_save = last_save
                i += 1
            return(profiles[latest_profile_index]["cute_name"])
    async def get_db_info(self,discord_id):
        async with self.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute("SELECT * FROM verification WHERE user_id = %s", (discord_id,))
                ign = await cursor.fetchone()
        if ign:
            return ign[0]
        else:
            return None
