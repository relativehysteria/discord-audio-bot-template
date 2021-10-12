import discord
from discord.ext import commands
from log import globalLog as gLog
from songqueue import SongQueue

class Naga(commands.Cog):
    def __init__(self, bot: commands.Bot):
        # The bot this cog belongs to
        self.bot = bot

        # Queues of all the servers this bot is in.
        # { guild.id: SongQueue }
        self.queues = {}

        self.default_reaction = "\U0001f44d"


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
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        await destination_vc.connect()
        await ctx.message.add_reaction(self.default_reaction)


    @commands.command(name="leave")
    async def _leave_vc(self, ctx: commands.Context):
        """Leaves a voice channel"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.message.add_reaction(self.default_reaction)
            del self.queues[ctx.guild.id]
