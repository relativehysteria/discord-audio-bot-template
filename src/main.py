#!/usr/bin/env python
import discord
from discord import app_commands
from settings import TOKEN_FILE
from log import globalLog as gLog

if __name__ != "__main__":
    gLog.debug(f"{__file__} executed but is not __main__")
    exit(1)

# Read the token from the token file
try:
    with open(TOKEN_FILE) as f:
        token = f.read().strip()
except Exception as e:
    gLog.critical(f"{e}")
    raise e

# Prepare the intents, the client and the slash command tree
intents  = discord.Intents.none()
client   = discord.Client(intents=intents)
cmd_tree = app_commands.CommandTree(client)
gLog.debug(f"Intents: {intents} | Client: {client} | Tree: {cmd_tree}")

# Run the bot
@client.event
async def on_ready():
    latency = int(client.latency * 1000)
    gLog.info("READY!")
    gLog.info(f"Startup latency: {latency}ms")

client.run(token)
