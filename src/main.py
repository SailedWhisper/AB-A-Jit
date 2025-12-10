"""
    The main module of the bot
    In charge of handling the initializing of the Bot client 
    Core checks such as pre-interaction permissions are also done here.
"""

import os
import discord
import dotenv
import colorlog
import json
import requests
import dotenv
from pathlib import Path
from discord.ext import commands

class CommandTree(discord.app_commands.CommandTree):
    async def on_error(self, ctx: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
        """
            Currently hooks up to the native error handler to catch specific errors
            and show them to the user.
        """

        if isinstance(error, discord.app_commands.CommandInvokeError):
            match error.original:
                case requests.HTTPError:
                    if not ctx.response.is_done():
                        await ctx.response.send_message(
                            delete_after = 10,
                            embed = discord.Embed.set_footer(discord.Embed(
                                description = f"**HTTP Error** \n```{error.original}```",
                                colour = discord.Colour.dark_red()
                            ), text = "Consider checking Discord and Roblox's site status")
                        )
                    else:
                        await ctx.edit_original_response(
                            embed = discord.Embed.set_footer(discord.Embed(
                                description = f"**HTTP Error** \n```{error.original}```",
                                colour = discord.Colour.dark_red()
                            ), text = "Consider checking Discord and Roblox's site status")
                        )
                case _:
                    return await super().on_error(ctx, error)
        else:
            return await super().on_error(ctx, error)
    
    async def interaction_check(self, ctx: discord.Interaction) -> bool:
        """
            Check for valid permission before running a command
            If passed, the rest is done by the native handler.
        """

        with open(os.environ["CONFIG_PATH"], "r", encoding = "UTF-8") as file:
            json_data = json.load(file)

            try:
                perms_server = ctx.client.get_guild(json_data['perms_server'])
                assert perms_server is not None
                
                server_member = perms_server.get_member(ctx.user.id)
                assert server_member is not None, "User not in perms server."
                assert server_member.get_role(json_data['perms_role']) is not None, "User doesnt have perms role."
            except AssertionError:
                await ctx.response.send_message(embed = discord.Embed(
                    description = "Missing permissions."
                ))

                return False

        return await super().interaction_check(ctx)

if __name__ == "__main__":
    bot_client = commands.Bot("jitnew", intents = discord.Intents.all(), tree_cls = CommandTree)
    os.environ["CONFIG_PATH"] = os.path.join("data", "config.json")
    dotenv.load_dotenv()

    ## Colored logging for better visualization
    log_streamhandler = colorlog.StreamHandler()
    log_streamhandler.setFormatter(colorlog.ColoredFormatter(
        "%(black)s%(asctime)s %(log_color)s%(levelname)-8s %(white)s%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        style = "%",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    ))

    logger_instance = colorlog.getLogger()
    logger_instance.addHandler(log_streamhandler)
    logger_instance.setLevel(10)

    @bot_client.event
    async def on_ready():
        """
            In charge of synchronizing commands with the server & clients
            Also handles stuff like the bot's activity and etc.
        """
        logger_instance.info("Initializing command modules..\n")
        
        ## Loads all commands automatically
        for commandFile in Path("src", "commands").glob("*.py"):
          if commandFile.name != "__init__.py":
            await bot_client.load_extension(f'src.commands.{commandFile.name[:-3]}')
            logger_instance.debug(f"Module {commandFile.name} loaded successfully")

        logger_instance.info("Synchronizing with Discord servers.")
        logger_instance.info(f"Complete. Synchronized {len(await bot_client.tree.sync())} command(s).")
        
    bot_client.run(token = os.environ["BOT_TOKEN"])
