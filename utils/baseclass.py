# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import pkgutil
import time
from typing import ClassVar

import aiohttp
import aiomysql
import discord
from discord.ext import commands
from dotenv import load_dotenv

from _types import HypixelPlayer, HypixelSocialMedia
from errors import InvalidMinecraftUsername, PlayerNotFoundError, ProfileNotFoundError, HypixelIsDown

load_dotenv()


class FarmingCouncil(commands.Bot):
    API_KEY: ClassVar[str] = os.environ.get("hypixel_api_key")

    def __init__(self) -> None:
        super().__init__(command_prefix="!", intents=discord.Intents.default(), help_command=None,
                         owner_id=702385226407608341)
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
        # await self.load_extension("cogs.rent_calc")
        self.session = aiohttp.ClientSession()
        self.pool = await aiomysql.create_pool(
            host=os.environ.get("DATABASE_HOST"),
            user=os.environ.get("DB_USERNAME"),
            password=os.environ.get("DB_PASSWORD"),
            db=os.environ.get("DB_NAME"),
            loop=self.loop,
            port=32813
        )
        async with self.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute(
                    """CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT NOT NULL UNIQUE,
                        uuid TEXT NOT NULL,
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
        # await self.tree.sync()
        await self.tree.sync()
        print(f"Logged in as {self.user} ({self.user.id})")  # type: ignore

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()
        if self.pool is not None:
            self.pool.close()
            await self.pool.wait_closed()
        await super().close()

    async def get_crop(self, cropname):
        async with self.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute("SELECT * FROM tutorial WHERE cropname = %s", (str(cropname),))
                data = await cursor.fetchone()
        return data

    async def command_counter(self, interaction: discord.Interaction):
        try:
            name = str(interaction.command.name)
        except:
            name = "None"
        async with self.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute("INSERT INTO commandcounter (cmd_name, user_id, timestamp) VALUES (%s, %s, %s)",
                                     (name, int(interaction.user.id), int(time.time())))
                await conn.commit()

    async def get_commands(self):
        async with self.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute("select * from commandcounter")
                commands = await cursor.fetchall()
        return commands

    async def get_uuid(self, username: str) -> str:
        if self.session is None:
            raise ConnectionError("aiohttp session has not been set")
        if not username.isalnum() and "_" not in username:
            raise InvalidMinecraftUsername(username)
        async with self.session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as req:
            if req.status != 200:
                raise KeyError(f"Recieved status code: {req.status}")
            js = await req.json()
            try:
                return js["id"]
            except KeyError:
                return None

    async def get_ign(self, uuid: str) -> str:
        if self.session is None:
            raise ConnectionError("aiohttp session has not been set")
        async with self.session.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}") as req:
            if req.status != 200:
                raise KeyError(f"Recieved status code: {req.status}")
            js = await req.json()
            try:
                return js["name"]
            except KeyError:
                return None

    async def get_hypixel_player(self, uuid: str) -> HypixelPlayer:

        if self.session is None:
            raise ConnectionError("aiohttp session has not been set")
        async with self.session.get(
                f"https://api.slothpixel.me/api/players/{uuid}?key={self.API_KEY}"
        ) as req:
            info = await req.json()
            if req.status != 200:
                raise PlayerNotFoundError(uuid=uuid)
            social_media = HypixelSocialMedia.from_dict(info["links"])
            return HypixelPlayer(
                username=info["username"],
                uuid=info["uuid"],
                social_media=social_media
            )

    async def get_skyblock_data(self, uuid: str, profile: str | None) -> HypixelPlayer:
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
                        return profileData
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

            return profiles[latest_profile_index]

    async def get_auction(self, id: str, sortOrder="asc"):
        if self.session is None:
            raise ConnectionError("aiohttp session has not been set")
        async with self.session.get(
                f"https://api.slothpixel.me/api/skyblock/auctions?id={id}&sortOrder={sortOrder}",
                headers={"API-Key": self.API_KEY}
        ) as req:
            try:
                info = await req.json()
            except:
                raise HypixelIsDown()
            return info

    async def get_past_auction(self, id: str):
        if self.session is None:
            raise ConnectionError("aiohttp session has not been set")
        async with self.session.get(
                f"https://sky.coflnet.com/api/auctions/tag/{id}/sold?page=0&pageSize=100",
                headers={"API-Key": self.API_KEY}
        ) as req:
            try:
                info = await req.json()
            except:
                raise HypixelIsDown()
            return info

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

    async def hoeTierPrice(self, tier, cropType, bazaar):
        typeHoe = {
            "WHEAT": {
                "tier1": {
                    "WHEAT": 512
                },
                "tier2": {
                    "WHEAT": 512,
                    "ENCHANTED_HAY_BLOCK": 256,
                    "JACOBS_TICKET": 64
                },
                "tier3": {
                    "WHEAT": 512,
                    "ENCHANTED_HAY_BLOCK": 256,
                    "TIGHTLY_TIED_HAY_BALE": 64,
                    "JACOBS_TICKET": 320
                }
            },
            "CARROT": {
                "tier1": {
                    "CARROT_ITEM": 512,
                },
                "tier2": {
                    "CARROT_ITEM": 512,
                    "ENCHANTED_CARROT": 256,
                    "JACOBS_TICKET": 64
                },
                "tier3": {
                    "CARROT_ITEM": 512,
                    "ENCHANTED_CARROT": 256,
                    "ENCHANTED_GOLDEN_CARROT": 256,
                    "JACOBS_TICKET": 320
                }
            },
            "POTATO": {
                "tier1": {
                    "POTATO_ITEM": 512,
                },
                "tier2": {
                    "POTATO_ITEM": 512,
                    "ENCHANTED_POTATO": 256,
                    "JACOBS_TICKET": 64
                },
                "tier3": {
                    "POTATO_ITEM": 512,
                    "ENCHANTED_POTATO": 256,
                    "ENCHANTED_BAKED_POTATO": 256,
                    "JACOBS_TICKET": 320
                }
            },
            "CANE": {
                "tier1": {
                    "SUGAR_CANE": 512
                },
                "tier2": {
                    "SUGAR_CANE": 512,
                    "ENCHANTED_SUGAR": 256,
                    "JACOBS_TICKET": 64
                },
                "tier3": {
                    "SUGAR_CANE": 512,
                    "ENCHANTED_SUGAR": 256,
                    "ENCHANTED_SUGAR_CANE": 256,
                    "JACOBS_TICKET": 320
                }
            },
            "WARTS": {
                "tier1": {
                    "NETHER_STALK": 512
                },
                "tier2": {
                    "NETHER_STALK": 512,
                    "ENCHANTED_NETHER_STALK": 256,
                    "JACOBS_TICKET": 64
                },
                "tier3": {
                    "NETHER_STALK": 512,
                    "ENCHANTED_NETHER_STALK": 256,
                    "MUTANT_NETHER_STALK": 256,
                    "JACOBS_TICKET": 320
                }
            },
            "COCO": {
                "tier1": {

                },
                "tier2": {

                },
                "tier3": {

                }
            },
            "MELON": {
                "tier1": {

                },
                "tier2": {
                    "ENCHANTED_MELON_BLOCK": 64
                },
                "tier3": {
                    "ENCHANTED_MELON_BLOCK": 192
                }
            },
            "PUMPKIN": {
                "tier1": {

                },
                "tier2": {
                    "POLISHED_PUMPKIN": 16
                },
                "tier3": {
                    "POLISHED_PUMPKIN": 48
                }
            },
            "MUSHROOMS": {
                "tier1": {

                },
                "tier2": {

                },
                "tier3": {

                }
            },
            "CACTUS": {
                "tier1": {

                },
                "tier2": {

                },
                "tier3": {

                }
            }
        }
        cost = typeHoe[cropType][tier]
        upgradeCost = 0
        for item in cost:
            upgradeCost += bazaar[item]["quick_status"]["sellPrice"] * cost[item]
        return upgradeCost

    async def get_skyblock_data_SLOTHPIXEL(self, ign: str, profile: str | None, uuid: str) -> HypixelPlayer:
        if self.session is None:
            raise ConnectionError("aiohttp session has not been set")
        if profile == 0:
            url = f"https://api.slothpixel.me/api/skyblock/profile/{uuid}"
        else:
            url = f"https://api.slothpixel.me/api/skyblock/profile/{ign}/{profile}"
        async with self.session.get(
                f"{url}",
                headers={"API-Key": self.API_KEY}
        ) as req:
            try:
                info = await req.json()
            except:
                raise HypixelIsDown()
            return info

    async def calculate_farming_weight(self, uuid):
        # Get profile and player data
        async with self.session.get(f"https://elitebot.dev/api/weight/{uuid}") as req:
            try:
                response = await req.json()
            except Exception as e:
                return [0, "Hypixel is down"]
        return response['highest']['farming']['weight']

    async def get_most_recent_profile(self, uuid):
        if self.session is None:
            raise ConnectionError("aiohttp session has not been set")
        async with self.session.get(
                f"https://api.slothpixel.me/api/skyblock/profile/{uuid}?key={self.API_KEY}"
        ) as req:
            try:
                info = await req.json()
            except:
                raise HypixelIsDown()

            if req.status != 200:
                raise PlayerNotFoundError(uuid=uuid)

            if not info:
                raise PlayerNotFoundError(uuid=uuid)

            return info["cute_name"]

    async def get_db_info(self, discord_id):
        """Returns the uuid of a user from discord iffrom the database"""
        async with self.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as cursor:
                cursor: aiomysql.Cursor
                await cursor.execute("SELECT * FROM users WHERE user_id = %s", (discord_id,))
                uuid = await cursor.fetchone()
        if uuid:
            return uuid[1]
        else:
            return None
