#!/usr/bin/env python
import discord
from discord import app_commands
from settings import TOKEN_FILE, APPLICATION_FILE
from log import globalLog as gLog
from bot import Naga

if __name__ != "__main__":
    gLog.debug(f"{__file__} executed but is not __main__")
    exit(1)

try:

    # Read the token and the app_id
    with open(TOKEN_FILE) as f:
        token = f.read().strip()
    with open(APPLICATION_FILE) as f:
        app_id = f.read().strip()

    # Run the bot
    Naga(app_id).run(token)

except Exception as e:
    gLog.critical(f"{e}")
    raise e
