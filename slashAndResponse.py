import discord
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

def setup_slash_commands(bot):
    @bot.tree.command(name="slashtest", description="Show available slashtest options")
    async def slashtest(interaction: discord.Interaction):
        """Show available slashtest options."""
        logger.debug(f'/slashtest called by {interaction.user}')
        await interaction.response.send_message(
            "Available options: test1, test2, test3\nUse `/slashtest_<option>` (e.g., `/slashtest_test1`)",
            ephemeral=False
        )

    @bot.tree.command(name="slashtest_test1", description="Get test1 response")
    async def slashtest_test1(interaction: discord.Interaction):
        """Respond with test1response."""
        logger.debug(f'/slashtest_test1 called by {interaction.user}')
        await interaction.response.send_message("test1response", ephemeral=False)

    @bot.tree.command(name="slashtest_test2", description="Get test2 response")
    async def slashtest_test2(interaction: discord.Interaction):
        """Respond with test2response."""
        logger.debug(f'/slashtest_test2 called by {interaction.user}')
        await interaction.response.send_message("test2response", ephemeral=False)

    @bot.tree.command(name="slashtest_test3", description="Get test3 response")
    async def slashtest_test3(interaction: discord.Interaction):
        """Respond with test3response."""
        logger.debug(f'/slashtest_test3 called by {interaction.user;}
        await interaction.response.send_message("test3response", ephemeral=False)