import discord
from discord.ext import commands
from log import globalLog as gLog

class Naga(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
