from discord import Interaction, app_commands as app_cmds, Embed
from discord.ext.commands import GroupCog, Bot
from libraries.user import User, get_userid
from libraries import utils

@app_cmds.guild_only()
class UserCommands(GroupCog, name = "user", description = "Common related to specific user queries."):
    """
       The class in charge of handling user-related queries
       Currently holds the following commands: getinfo
    """

    @app_cmds.command()
    async def getinfo(self, ctx: Interaction, user: str):
        """
            Fetches available information from the specified user profile

            Args: 
                user (str): The user to fetch the information from.
        """

        user_data = User(get_userid(user))
        info_embed = Embed(
           colour = utils.discord.Colour.dark_grey(),
           title = str(user_data),
           url = user_data.profile_url,
           description = f'**About:** {user_data.description}'
        )

        info_embed.add_field(name = "User ID:", value = user_data.userid)
        info_embed.add_field(name = "Created:", value = utils.to_timestamp(user_data.created))

        await ctx.response.send_message(embed = info_embed)

### Initializes all commands from the Cog
async def setup(bot_client: Bot):
  await bot_client.add_cog(UserCommands())