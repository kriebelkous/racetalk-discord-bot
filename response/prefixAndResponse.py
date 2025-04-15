from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

def setup_commands(bot):
    @bot.group(invoke_without_command=True)
    async def prefixtest(ctx):
        """Show available prefixtest options when !prefixtest is used alone."""
        logger.debug(f'{bot.command_prefix}prefixtest called by {ctx.author}')
        await ctx.send(f"Available options: test1, test2, test3\nUse `{bot.command_prefix}prefixtest <option>` (e.g., `{bot.command_prefix}prefixtest test1`)")

    @prefixtest.command(name='test1')
    async def prefixtest_test1(ctx):
        """Respond to !prefixtest test1."""
        logger.debug(f'{bot.command_prefix}prefixtest test1 called by {ctx.author}')
        await ctx.send("test1response")

    @prefixtest.command(name='test2')
    async def prefixtest_test2(ctx):
        """Respond to !prefixtest test2."""
        logger.debug(f'{bot.command_prefix}prefixtest test2 called by {ctx.author}')
        await ctx.send("test2response")

    @prefixtest.command(name='test3')
    async def prefixtest_test3(ctx):
        """Respond to !prefixtest test3."""
        logger.debug(f'{bot.command_prefix}prefixtest test3 called by {ctx.author}')
        await ctx.send("test3response")

    @bot.command()
    async def testcommands(ctx):
        """Show a list of test commands."""
        logger.debug(f'{bot.command_prefix}testcommands called by {ctx.author}')
        await ctx.send(
            "trigger and response test:\n"
            "wildcardtest\n"
            "test wildcardtest\n"
            "standalonetest\n"
            "test standalonetest\n"
            "sentencetest\n"
            "test sentencetest\n"
            "userspecifictest\n"
            "randomtest\n"
            "sequencetest\n"
            "\n"
            "mention test:\n"
            "test\n"
            "userspecific\n"
            "\n"
            "slash command test:\n"
            "/slashtest\n"
            "\n"
            "prefix command test:\n"
            "(prefix)prefixtest\n"
        )