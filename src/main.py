#!/bin/env python
from discord.ext.commands import Bot
from settings import TOKEN_FILE
from bot import Naga
from log import globalLog as gLog

if __name__ != "__main__":
    gLog.debug(f"{__file__} executed but is not __main__")
    exit(0)

# Read the token from the token file
try:
    with open(TOKEN_FILE) as f:
        token = f.read().strip()
except Exception as e:
    gLog.critical(f"{e}")
    raise e

# Run the bot
naga = Bot("TODO MULTIPLE PREFIXES")
naga.add_cog(Naga(naga))

@naga.event
async def on_ready():
    latency = int(naga.latency * 1000)
    gLog.info("READY!")
    gLog.info(f"Startup latency: {latency}ms")

naga.run(token)
