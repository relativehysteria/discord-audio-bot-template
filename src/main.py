#!/usr/bin/env python
from time import strftime
from time import gmtime
from pathlib import Path
import os

import discord
import youtube_dl
from discord.ext import commands

from song import Song
from songqueue import SongQueue
from settings import *

## Global variables and stuff ##################################################

# Bot
bot = commands.Bot(command_prefix="naga ")

# Current active voice clients, or the voice channels the bot is in
# { serverID: SongQueue }
currentVCs = dict()

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
        await currentVCs[guildID].voice.disconnect()
        del currentVCs[guildID]

    # Join the voice chat and create an empty queue
    if voiceChannel:
        currentVCs[guildID]       = SongQueue()
        currentVCs[guildID].voice = await voiceChannel.connect()
        currentVCs[guildID].text  = ctx.message.channel


@bot.command()
async def pause(ctx, *args):
    """Pauses the currently playing song"""
    queue = currentVCs.get(ctx.message.guild.id)
    if queue:
        queue.pause()


@bot.command()
async def skip(ctx, *args):
    """Skips the currently playing song"""
    queue = currentVCs.get(ctx.message.guild.id)
    if queue:
        queue.skip()


@bot.command()
async def shuffle(ctx, *args):
    """Shuffles the queue"""
    queue = currentVCs.get(ctx.message.guild.id)
    if queue:
        queue.shuffle()


@bot.command()
async def queue(ctx, *args):
    """Shows the currently played queue"""
    queue = currentVCs.get(ctx.message.guild.id)
    if not queue:
        return

    if len(queue.queue) == 0 and not queue.current:
        await ctx.send("Queue empty.")
        return

    embed = discord.Embed(title="Queue")

    status = "LOOP:"if queue._loop else "00"
    embed.add_field(
        name="Current",
        value=f"`{status}` [{queue.current.title}]({queue.current.url})\n\n"
    )

    counter = 0
    msg = ""
    for i in queue.queue:
        counter += 1
        msg += f"`{counter:02}` [{i.title}]({i.url})\n"
        if counter == 20:
            msg += "`...`"
            break
    if msg != "":
        embed.insert_field_at(0, name="Next up...", value=msg)

    await ctx.send(embed=embed)


@bot.command()
async def clear(ctx, *args):
    """Clears the queue"""
    queue = currentVCs.get(ctx.message.guild.id)
    if queue:
        queue.clear()


@bot.command()
async def loop(ctx, *args):
    queue = currentVCs.get(ctx.message.guild.id)
    if queue:
        queue.loop()


@bot.command()
async def remove(ctx, *args):
    """Removes a song from the queue"""
    queue = currentVCs.get(ctx.message.guild.id)
    if not queue:
        return
    if len(args) < 1:
        return

    idx = 0
    try:
        idx = int(args[0])
    except:
        return
    if idx < 0:
        return
    if idx == 0:
        queue.skip()
        return
    if idx > len(queue.queue):
        return
    queue.remove(idx-1)


@bot.command()
async def play(ctx, *args):
    """Plays something in your voice chat"""
    guildID = ctx.message.guild.id

    query = ' '.join(args)
    if query == "":
        return

    # Only try to play something if the bot is currently in a voice chat
    if guildID not in currentVCs:
        return

    song = get_song(query)

    print(f'{strftime(TIME_FORMAT, gmtime())} > ', end='')
    print(f'{CLR_NOTICE}{query}{CLR_NORMAL}')

    # Send out a status message and put the stream to a queue
    if not song.valid:
        await ctx.send("Not found.")
    else:
        await currentVCs[guildID].queue.put(song)


def get_song(query: str) -> Song:
    """Get the stream url to an audio file from a general url"""
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
            return Song(dict())  # invalid Song
        res = res[0]

    return Song(res)


@bot.command()
async def leave(ctx):
    """Leaves the voice chat"""
    guildID = ctx.message.guild.id
    if guildID in currentVCs:
        await currentVCs[guildID].voice.disconnect()
        del currentVCs[guildID]

################################################################################

if __name__ == "__main__":
    with open(TOKEN_FILE) as f:
        TOKEN = f.read().strip()
    bot.run(TOKEN)
