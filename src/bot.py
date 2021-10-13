import discord
from discord.ext import commands
from log import globalLog as gLog
from songqueue import SongQueue
from song import get_song_from_query
from settings import REACTION_OK, REACTION_ERR

class Naga(commands.Cog):
    def __init__(self, bot: commands.Bot):
        # The bot this cog belongs to
        self.bot = bot

        # Queues of all the servers this bot is in.
        # { guild.id: SongQueue }
        self.queues = {}


    async def cog_before_invoke(self, ctx: commands.Context):
        """Sets `ctx.queue` to the server's queue if it exists, otherwise it
        creates a new one
        """
        ctx.queue = self.queues.get(ctx.guild.id)


    @commands.command(name="join")
    async def _join_vc(self, ctx: commands.Context, *,
                       destination_vc: discord.VoiceChannel = None):
        """Joins a voice channel.

        If `destination_vc` is specified, joins the specified voice channel.
        If it isn't specified, joins the voice channel the author is in.
        """
        if not ctx.author.voice and not destination_vc:
            await ctx.send("No voice channel.")
            return

        # `ctx.queue` is initialized by `cog_before_invoke`.
        # If there's no queue (None), it means that this bot is not in
        # a voice channel
        if not ctx.queue:
            ctx.queue = SongQueue()
            self.queues[ctx.guild.id] = ctx.queue

        # Join the destination voice channel
        destination_vc = destination_vc or ctx.author.voice.channel
        if ctx.queue.voice:
            await ctx.queue.voice.disconnect()
        ctx.queue.voice = await destination_vc.connect()
        await ctx.message.add_reaction(REACTION_OK)


    @commands.command(name="leave")
    async def _leave_vc(self, ctx: commands.Context):
        """Leaves a voice channel"""
        if ctx.queue.voice:
            await ctx.queue.voice.disconnect()
            await ctx.message.add_reaction(REACTION_OK)
            del self.queues[ctx.guild.id]


    @commands.command(name="play")
    async def _play(self, ctx: commands.Context, *args):
        """Plays something in a voicechat"""
        query = ' '.join(args)
        if query == "" or ctx.queue == None:
            gLog.debug(f"Query: {query}")
            gLog.debug(f"Queue is not None: {ctx.queue is not None}")
            await ctx.message.add_reaction(REACTION_ERR)
            return

        gLog.info(f"Query: {query}")
        song = get_song_from_query(query)

        # Return on invalid songs but notify the requester
        gLog.debug(f"Song is valid: {song.is_valid}")
        if not song.is_valid:
            await ctx.message.add_reaction(REACTION_ERR)
            return

        # Create an embed and send it to the server
        msg = discord.Embed(title="Enqueued", description=
                            f"[{song.title}]({song.url})")
        msg.add_field(name="Duration", value=
                      song.duration_formatted)
        msg.add_field(name="Uploader", value=
                      f"[{song.uploader}]({song.uploader_url})")
        msg.set_thumbnail(url=song.thumbnail)
        await ctx.message.add_reaction(REACTION_OK)
        await ctx.send(embed=msg)

        ctx.queue.put(song)


    @commands.command(name="skip")
    async def _skip(self, ctx: commands.Context):
        """Skips the currently playing song"""
        if ctx.queue:
            ctx.queue.skip()
            ctx.message.add_reaction(REACTION_OK)
