from discord import Interaction, app_commands as app_cmds 
from discord.ext.commands import Cog, Bot

### Initializes all commands from the Cog
async def setup(bot_client: Bot):
    pass
    #await bot_client.add_cog(UserCommands())