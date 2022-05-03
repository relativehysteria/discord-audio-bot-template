import discord
from discord import app_commands
from log import globalLog as gLog

class Naga(discord.Client):
    def __init__(self, app_id: int):
        # Prepare the bot's intentions
        intents = discord.Intents.none()

        # Run the client initializer
        super().__init__(intents=intents, application_id=app_id)

        # Command tree (for slash commands)
        self.cmd_tree = discord.app_commands.CommandTree(self)
        self.cmd_tree.add_command(self.test_cmd)


    async def setup_hook(self):
        # TODO:
        #   Global commands take up to one hour to sync :^)
        #   Maybe copy the commands to every server the bot is connected to
        #   so that we don't have to wait so long...
        gLog.debug(f"Synchronizing commands with Discord...")
        await self.cmd_tree.sync()


    async def on_ready(self):
        latency = int(self.latency * 1000)
        gLog.info("READY!")
        gLog.info(f"Startup latency: {latency}ms")


    @app_commands.command(name="test", description="test command .-.")
    async def test_cmd(self, interaction: discord.Interaction):
        gLog.debug("Called! :D")
        await interaction.response.send_message("test test test")
