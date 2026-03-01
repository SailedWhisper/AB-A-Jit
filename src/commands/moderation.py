from discord import Interaction, app_commands as app_cmds, Embed, Colour, ui
from discord.ext.commands import Cog, Bot
from src.libraries import game, utils
from src.libraries.user import User as NewUser, UserCardComponent


@app_cmds.guild_only()
class GameModeration(Cog):
    """
        The class that handles all moderation-related commands
        Currently holds the following commands: Ban, Unban, Kick
    """

    @app_cmds.command()
    async def ban(self, ctx: Interaction, user: str, reason: str, duration: int = -1):
        """
            Bans a player from the game

            Args:
                user (str): The username (or userid) to ban.
                reason (str): The reason of the ban.
                duration (int): The duration of the ban (optional).
        """

        user_info = NewUser(user)
        restriction = game.JoinRestriction(
            userid = user_info.userid,
            public_reason = reason,
            private_reason = f"Banned by @{ctx.user.name} via jit.",
            duration = utils.timedelta(duration),
            active = True
        )

        if restriction.post():
            expire_date = utils.datetime.now() + restriction.duration
            log_embed = Embed(
                title = "User Banned",
                colour = Colour.dark_red(),
                timestamp = utils.datetime.now(),
                description = f"User **{user_info.title_str()}** has been banned.\n\n"
            )

            log_embed.add_field(name = "User ID:", value = user_info.userid, inline = True)
            log_embed.add_field(
                name = "Expires:",
                value = utils.to_timestamp(expire_date.timestamp()) if duration > 0 else "Never.",
                inline = True
            )

            log_embed.add_field(name = "Reason:", value = reason, inline = False)

            await ctx.response.send_message(embed = log_embed)
            await utils.ChannelLog(ctx,
                action = f"Banned user {user_info.title_str()}",
                reason = reason,
                expires = expire_date if duration > 0 else None
            ).send()

    @app_cmds.command()
    async def unban(self, ctx: Interaction, user: str, reason: str):
        """
            Unbans a player from the game.
            
            Args:
                user (str): The user to unban.
                reason (str): The reason for the unban.
        """
        
        user_info = NewUser(user)
        restriction = game.JoinRestriction(
            userid = user_info.userid,
            public_reason = reason,
            private_reason = f"Unbanned by @{ctx.user.name} via jit.",
            active = False
        )

        if restriction.post():
            log_embed = Embed(
                title = "User Unbanned",
                colour = Colour.dark_gray(),
                timestamp = utils.datetime.now(),
                description = f"User **{user_info.title_str()}** has been unbanned.\n\n"
            )

            log_embed.add_field(name = "User ID:", value = user_info.userid, inline = True)
            log_embed.add_field(name = "Reason:", value = reason, inline = True)

            await ctx.response.send_message(embed = log_embed)
            await utils.ChannelLog(ctx, f"Unbanned user {user_info.title_str()}", reason).send()
    
    @app_cmds.command()
    async def kick(self, ctx: Interaction, user: str, reason: str):
        """
            Kicks a player from the game

            Args:
                user (str): The user to unban.
                reason (str): The reason for the unban.
        """
        
        user_info = NewUser(user)

        if game.kick([user_info.userid], reason):
            info_embed = Embed(
                title = "User Kicked",
                description = f"User **{user_info.title_str()}** has been kicked from the game.",
                colour = Colour.dark_red(),
                timestamp = utils.datetime.now()
            )
            
            info_embed.add_field(name = "User ID:", value = user_info.userid, inline = True)
            info_embed.add_field(name = "Reason:", value = reason, inline = True)

            await ctx.response.send_message(embed = info_embed)
            await utils.ChannelLog(ctx, f"Kicked user {user_info.title_str()}", reason).send()

    @app_cmds.command()
    async def banstatus(self, ctx: Interaction, user: str):
        """
            Returns the current ban status of the user.

            Args:
            user (str): The user to unban.
        """

        user_info = NewUser(user)
        status = game.ban_status(user_info.userid)
        card_component = UserCardComponent(timeout = 180, info = user_info)
        card_component.container.add_item(ui.Separator())
        
        if status.active:
            issued = utils.datetime.fromisoformat(status.startTime).timestamp()
            contents = [
                f'**Issued:** {utils.to_timestamp(issued)}',
                f'**Effective Until:** {utils.to_timestamp(issued + status.duration) if status.duration else "Forever."}',
                f'**Reason:** {status.displayReason}'
            ]

            card_component.container.add_item(ui.TextDisplay("\n".join(contents).strip()))
        else:
            card_component.container.add_item(ui.TextDisplay("User does not have any active restrictions."))

        card_component.container.add_item(ui.Separator())
        card_component.container.add_item(ui.TextDisplay(
            f"-# {utils.to_timestamp(utils.datetime.now().timestamp())} • ID {user_info.userid}"
        ))

        #info_embed.set_thumbnail(url = user_info.thumbnail())
        #info_embed.set_footer(text = f'User ID: {user_info.userid}')
        #info_embed.add_field(name = "Banned:", value = status.active, inline = True)
        #
        #if status.active: ## User is banend
        #    issued = utils.datetime.fromisoformat(status.startTime).timestamp()
        #    info_embed.add_field(name = "Issued:", value = utils.to_timestamp(issued), inline = True)
        #    info_embed.add_field(
        #        name = "Duration:",
        #        value = f"Until {utils.to_timestamp(issued + status.duration)}" if status.duration else "Permanent" ,
        #        inline = False
        #    )
        #
        #    info_embed.add_field(name = "Reason:", value = status.displayReason, inline = True)

        await ctx.response.send_message(view = card_component)

### Initializes all commands from the Cog
async def setup(bot_client: Bot):
  await bot_client.add_cog(GameModeration())