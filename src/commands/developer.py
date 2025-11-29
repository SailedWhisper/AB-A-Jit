from discord import Interaction, app_commands as app_cmds 
from discord.ext.commands import Cog, Bot
from libraries import utils

@app_cmds.guild_only()
class Debug(Cog):
    """
        Commands exclusive to the game's / Bots debuggers.
    """
    def interaction_check(self, interaction: Interaction) -> bool:
       return super().interaction_check(interaction)
    
    @app_cmds.command()
    async def shutdown(self, ctx: Interaction):
       await utils.ChannelLog(
            ctx,
            "Test Action",
            "Test reason",
            utils.datetime.now()
        ).send()

### Initializes all commands from the Cog
async def setup(bot_client: Bot):
  pass
  #await bot_client.add_cog(Debug())