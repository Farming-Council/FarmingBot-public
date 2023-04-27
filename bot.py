# -*- coding: utf-8 -*-
from __future__ import annotations

from utils import FarmingCouncil
from dotenv import load_dotenv
import os, sys

load_dotenv()

bot = FarmingCouncil()
TEST_TOKEN = str("MTA1NzE2ODU3OTcxMzMxMDgyMQ.GXgQ7N.do1zwgAUZq3QmLyO8uQHepetNl7k7ObYpJx96s")
if __name__ == "__main__":
    try:
        bot.run(os.environ.get("TOKEN"))
    except Exception as e:
        print(e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
    # MTA1NzE2ODU3OTcxMzMxMDgyMQ.GXgQ7N.do1zwgAUZq3QmLyO8uQHepetNl7k7ObYpJx96s
    # os.environ.get("TOKEN")
    # switch out these two to test the bot, make sure to replace, + do .env -> .env and back when done!
