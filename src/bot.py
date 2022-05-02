import discord
from log import globalLog as gLog

class Naga(discord.Client):
    def __init__(self, app_id: int):
        # Prepare the bot's intentions
        intents = discord.Intents.none()

        # Run the client initializer
        super().__init__(intents=intents, application_id=app_id)

        # Command tree (for slash commands)
        self.cmd_tree = discord.app_commands.CommandTree(self)


    async def on_ready(self):
        latency = int(self.latency * 1000)
        gLog.info("READY!")
        gLog.info(f"Startup latency: {latency}ms")
