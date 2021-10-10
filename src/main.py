#!/usr/bin/env python
from time import strftime
from time import gmtime
from pathlib import Path
import os

import discord
import youtube_dl
from discord.ext import commands

## Global variables and stuff ##################################################

# Bot
bot = commands.Bot(command_prefix="naga ")

# Current active voice clients, or the voice channels the bot is in
# { serverID: VoiceClient }
currentVCs = dict()

## Settings ####################################################################

# File where the token for the bot is stored
TOKEN_FILE  = "TOKEN"

# Text color settings used by the bot in different messages.
# If your terminal (or whatever you're running this bot in) doesn't support ANSI
# escape sequences, you might want to set all of these values to "".
CLR_WARNING = "\033[31m"
CLR_SUCCESS = "\033[92m"
CLR_NOTICE  = "\033[36m"
CLR_NORMAL  = "\033[0m"

# Time format given to strftime
TIME_FORMAT = "%H:%M:%S"

## Bot commands and other related functions ####################################

@bot.event
async def on_connect():
    print(f"{CLR_NOTICE}Startup latency: {int(bot.latency * 1000)}ms{CLR_NORMAL}")

@bot.event
async def on_ready():
    print(f"{CLR_SUCCESS}READY{CLR_NORMAL} ({strftime(TIME_FORMAT, gmtime())})")

@bot.command()
async def join(ctx, *args):
    """Joins your voice chat"""
    voiceChannel = None
    guildID      = ctx.message.guild.id

    # If someone sends an ID of a voice chat, the bot joins said voice chat
    if len(args) == 1:
        try:
            voiceChannel = discord.utils.get(ctx.guild.voice_channels,
                                             id=int(args[0]))
        except Exception as err:
            print(f"{CLR_WARNING}{err}{CLR_NORMAL}")
            return
    # Otherwise join the author's VC, if they are in one
    elif ctx.author.voice:
        voiceChannel = ctx.author.voice.channel

    # The bot CAN be hijacked from other VCs
    if guildID in currentVCs:
        await currentVCs[guildID].disconnect()
        del currentVCs[guildID]

    # Join the voice chat
    if voiceChannel:
        currentVCs[guildID] = await voiceChannel.connect()

@bot.command()
async def play(ctx, *args):
    """Plays something in your voice chat"""
    guildID = ctx.message.guild.id

    filename = ' '.join(args)

    # Only try to play something if the bot is currently in a voice chat
    if guildID not in currentVCs:
        return

    # We don't implement a queue for audio, so we simply interrupt the one that
    # is currenty playing
    if currentVCs[guildID].is_playing:
        currentVCs[guildID].stop()

    source = get_stream_url(filename)

    print(f'{strftime(TIME_FORMAT, gmtime())} > ', end='')
    print(f'{CLR_NOTICE}{filename}{CLR_NORMAL}')

    # FFMPEG options to prevent stream closing on lost connections
    before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"

    # Play the file
    if source is None:
        ctx.send("Not found.")
    else:
        currentVCs[guildID].play(
            discord.FFmpegPCMAudio(source, before_options=before_options)
        )

# Get the stream url to an audio file from a general url
def get_stream_url(query: str) -> str:
    query = query.strip()

    if not query.startswith("http"):
        query = "ytsearch: " + query

    ydl_opts = {'youtube_include_dash_manifest': False}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        res = ydl.extract_info(query, download=False)

    # Get the first audio url that we can get
    if 'entries' in res:
        res = res['entries']

    # Youtube turns it into a list ._.
    if isinstance(res, list):
        if len(res) == 0:
            return None
        res = res[0]

    for i in res['formats']:
        if i['acodec'] != "none":
            return i['url']


@bot.command()
async def leave(ctx):
    """Leaves the voice chat"""
    guildID = ctx.message.guild.id
    if guildID in currentVCs:
        await currentVCs[guildID].disconnect()
        del currentVCs[guildID]

################################################################################

if __name__ == "__main__":
    with open(TOKEN_FILE) as f:
        TOKEN = f.read().strip()
    bot.run(TOKEN)
