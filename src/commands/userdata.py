from os import environ
from typing import Any
from discord import Interaction, app_commands as app_cmds, Embed
from discord import ui
from discord.ext.commands import GroupCog, Bot
from src.libraries.datastore import index_scoped as index_datastore
from src.libraries.user import User, get_userid
from src.libraries import utils

class DataStoreView(ui.View):
    def __init__(self, user_id: int, author_id: int):
        super().__init__(timeout = None)
        self.userid = user_id
        self.authorid = author_id

    async def interaction_check(self, ctx: Interaction) -> bool:
        if await super().interaction_check(ctx):
            return ctx.user.id == self.authorid

        return False

    @ui.button(label = "View Game Data")
    async def get_datastore(self, ctx: Interaction, button: ui.Button):
        button.disabled = True ## Only read datastore once

        ### Fetch datastore
        try:
            ds_result = index_datastore("MainData", environ['DATASTORE_SCOPE'], self.userid)
            display_embed = Embed()
            playtime = utils.timedelta(seconds = ds_result.value['Info']['PlayTime'])

            ### Last time they played the game
            display_embed.add_field(
                name = "Last Played:",
                value = utils.to_timestamp(ds_result.value['Info']['LastPlay'])
            )

            ### Total accumulated playitme
            display_embed.add_field(
                name = "Total Playtime:",
                value = f'{playtime.days}d {playtime.seconds//3600}h {(playtime.seconds//60)%60}m'
            )

            if ctx.message is not None:
                original_msg = ctx.message
                edited_embeds = original_msg.embeds.copy()
                edited_embeds.append(display_embed)

                await original_msg.edit(embeds = edited_embeds, view = None)
                return
            
            await ctx.response.send_message(embed = display_embed)
        except utils.requests.exceptions.HTTPError as exception:
            if exception.response.status_code == 404:
                await ctx.response.send_message(content = "No DataStore entries found.", delete_after = 5)
                return
            
            raise exception ## Unexpected exception, let it pass to handler

@app_cmds.guild_only()
class UserCommands(GroupCog, name = "user", description = "Common related to specific user queries."):

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
        info_embed.add_field(name = "Created:", value = utils.to_timestamp(user_data.created.timestamp()))

        await ctx.response.send_message(embed = info_embed, view = DataStoreView(user_data.userid, ctx.user.id))

### Initializes all commands from the Cog
async def setup(bot_client: Bot):
  await bot_client.add_cog(UserCommands())