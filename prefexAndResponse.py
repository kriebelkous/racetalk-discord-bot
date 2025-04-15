from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

def setup_commands(bot):
    @bot.group(invoke_without_command=True)
    async def tijden(ctx):
        """Show available tijden options when !tijden is used alone."""
        logger.debug(f'!tijden called by {ctx.author}')
        await ctx.send("Available options: f1, f2, f3\nUse `!tijden <option>` (e.g., `!tijden f1`)")

    @tijden.command(name='f1')
    async def tijden_f1(ctx):
        """Respond to !tijden f1."""
        logger.debug(f'!tijden f1 called by {ctx.author}')
        await ctx.send("hier zijn de f1 tijden")

    @tijden.command(name='f2')
    async def tijden_f2(ctx):
        """Respond to !tijden f2."""
        logger.debug(f'!tijden f2 called by {ctx.author}')
        await ctx.send("hier zijn de f2 tijden")

    @tijden.command(name='f3')
    async def tijden_f3(ctx):
        """Respond to !tijden f3."""
        logger.debug(f'!tijden f3 called by {ctx.author}')
        await ctx.send("hier zijn de f3 tijden")