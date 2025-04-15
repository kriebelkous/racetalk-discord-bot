import discord
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

def setup_slash_commands(bot):
    @bot.tree.command(name="slashtest", description="Run slashtest with an option")
    @app_commands.describe(option="Choose test1, test2, or test3")
    @app_commands.choices(option=[
        app_commands.Choice(name="test1", value="test1"),
        app_commands.Choice(name="test2", value="test2"),
        app_commands.Choice(name="test3", value="test3")
    ])
    async def slashtest(interaction: discord.Interaction, option: str):
        """Run slashtest with a selected option."""
        logger.debug(f'/slashtest {option} called by {interaction.user}')
        responses = {
            "test1": "test1response",
            "test2": "test2response",
            "test3": "test3response"
        }
        await interaction.response.send_message(responses.get(option, "Invalid option. Choose test1, test2, or test3"), ephemeral=False)