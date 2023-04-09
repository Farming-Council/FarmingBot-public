# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import NamedTuple


class HypixelSocialMedia(NamedTuple):
    instagram: str | None = None
    youtube: str | None = None
    twitch: str | None = None
    twitter: str | None = None
    hypixel: str | None = None
    discord: str | None = None

    @classmethod
    def from_dict(cls, links: dict[str, str | None], /) -> HypixelSocialMedia:
        return HypixelSocialMedia(
            instagram=links.get("INSTAGRAM"),
            youtube=links.get("YOUTUBE"),
            hypixel=links.get("HYPIXEL"),
            twitter=links.get("TWITTER"),
            discord=links.get("DISCORD"),
            twitch=links.get("TWITCH")
        )


class HypixelPlayer(NamedTuple):
    username: str
    uuid: str
    social_media: HypixelSocialMedia
