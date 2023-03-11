# -*- coding: utf-8 -*-
from __future__ import annotations

from utils import FarmingCouncil
from dotenv import load_dotenv
import os

load_dotenv()

bot = FarmingCouncil()

if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))