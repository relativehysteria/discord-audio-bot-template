#!/usr/bin/env python
from time import strftime
from time import gmtime
from pathlib import Path
import os

import discord
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

    status = "LOOP:"if queue._loop else "00"
    embed = discord.Embed(title=f"Queue `[{len(queue.queue)}]`", inline=False)

    msg  = f"`{status}` `[{queue.current.duration_formatted}]`"
    msg += f" [{queue.current.title}]({queue.current.url})\n\n"
    embed.add_field(name="Current", value=msg, inline=False)

    msg = ""
    for (counter, song) in enumerate(queue.queue, start=1):
        pre_msg  = f"`{counter:02}` `[{song.duration_formatted}]`"
        pre_msg += f" [{song.title}]({song.url})\n"

        # Embed value limit is 1024 chars
        if len(msg + pre_msg) >= 1020:
            msg += "`...`"
            break
        msg += pre_msg

    if msg != "":
        embed.add_field(name="Next up...", value=msg, inline=False)

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
    queue = currentVCs.get(ctx.message.guild.id)
    if not queue:
        return

    query = ' '.join(args)
    if query == "":
        return

    print(f'{strftime(TIME_FORMAT, gmtime())} > ', end='')
    print(f'{CLR_NOTICE}{query}{CLR_NORMAL}')

    await queue.enqueue(query)


@bot.command()
async def leave(ctx):
    """Leaves the voice chat"""
    guildID = ctx.message.guild.id
    if guildID in currentVCs:
        await currentVCs[guildID].voice.disconnect()
        del currentVCs[guildID]


@bot.group()
async def playlist(ctx):
    """Manipulate playlists"""
    if ctx.invoked_subcommand is None:
        await ctx.send(format_playlists())


@playlist.command()
async def save(ctx, *args):
    """Saves the current queue into a playlist that can be loaded later on."""
    if len(args) < 1:
        await ctx.send("No name specified.")

    queue = currentVCs.get(ctx.message.guild.id)
    if queue:
        queue.save(' '.join(args))


@playlist.command()
async def load(ctx, *args):
    """Loads a saved playlist into the queue."""
    if len(args) < 1:
        await ctx.send(format_playlists())
        return

    queue = currentVCs.get(ctx.message.guild.id)
    if queue:
        await queue.load(' '.join(args))
    return



@playlist.command()
async def show(ctx, *args):
    """Show the contents of a playlist"""
    if len(args) < 1:
        await ctx.send(format_playlists())
        return

    name = " ".join(args)
    path = f"{PLAYLISTDIR}/{name}.txt"
    if not os.path.exists(path):
        await ctx.send(f"Playlist `{name}` doesn't exist.")
        return

    with open(path) as f:
        await ctx.send(file=discord.File(f))


def format_playlists() -> str:
    """Format the playlist directory into a nicely printable message"""
    # https://stackoverflow.com/a/4500607
    mtime      = lambda f: os.stat(os.path.join(f"{PLAYLISTDIR}", f)).st_mtime
    sortedlist = list(sorted(os.listdir(f"{PLAYLISTDIR}"), key=mtime))

    msg = "**Playlists:**```\n"
    for fname in sortedlist:
        msg += f"{os.path.splitext(fname)[0]}\n"
    msg += "```"
    return msg

################################################################################

if __name__ == "__main__":
    with open(TOKEN_FILE) as f:
        TOKEN = f.read().strip()
    bot.run(TOKEN)
