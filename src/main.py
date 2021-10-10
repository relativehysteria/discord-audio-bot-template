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

# Names of the audio files that this bot can play
audioList  = list()

## Settings ####################################################################

# Directory where the audio files (used in the `play` command) are stored.
AUDIO_DIR   = "audio"

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

# Messages to send when a specific situation occurs. Can be `None`.
#
# The bot is already in a voice channel and someone tries to hijack it
ALREADY_TAKEN_MSG = "I'm in one channel already"

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

    # The bot must not be in a voice chat already
    if guildID in currentVCs:
        if ALREADY_TAKEN_MSG: await ctx.send(ALREADY_TAKEN_MSG)
        return

    # Join the voice chat
    if voiceChannel:
        currentVCs[guildID] = await voiceChannel.connect()


def format_audio() -> str:
    """
    Formats the filenames in audioList into a readable message;
    ID > Filename
    """
    message = ""
    # We skip the first element, because it is `None`
    for i in range(1, len(audioList)):
        message += f"{i} > {audioList[i].replace('.mp3', '').replace('_', ' ')}"
        message += '\n'
    return message


@bot.command()
async def play(ctx, *args):
    """Plays something in your voice chat"""
    guildID = ctx.message.guild.id

    # If no argument (filename) was given, send the list of files to play
    # together with their ID
    if len(args) == 0:
        message  = "```\n"
        message += format_audio()
        message += "```"
        await ctx.send(message)
        return

    filename = ' '.join(args)

    # Only try to play something if the bot is currently in a voice chat
    if guildID not in currentVCs:
        return

    # We don't implement a queue for audio, so we simply interrupt the one that
    # is currenty playing
    if currentVCs[guildID].is_playing:
        currentVCs[guildID].stop()

    # Get the name of the audio file we want to play.
    # We either got its ID or its filename
    is_num = True
    try:
        # Number
        filename = audioList[int(filename)]
        source   = f"{AUDIO_DIR}/{filename}"
    except:
        # Url or query
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
    # Load audio file names into audioList
    # https://stackoverflow.com/a/4500607
    mtime = lambda f: os.stat(os.path.join(AUDIO_DIR, f)).st_mtime
    audioList.append(None)
    audioList += list(sorted(os.listdir(AUDIO_DIR), key=mtime))

    with open(TOKEN_FILE) as f:
        TOKEN = f.read().strip()
    bot.run(TOKEN)
