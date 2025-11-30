import os
import discord
import requests
import json
from datetime import datetime, timedelta

class APIs():
    ## Old APIs / Sites
    base_url = "https://apis.roblox.com"
    users = "https://users.roblox.com/v1/"
    universe_url = f"https://apis.roblox.com/cloud/v2/universes/{os.environ['UNIVERSE_ID']}"
    status_page = "https://status.roblox.com/pages/59db90dbcdeb2f04dadcf16d"

    ## Extra data
    universe_id = int(os.environ["UNIVERSE_ID"])
    rbx_header = {"x-api-key": os.environ["RBX_API_KEY"]} #"insert-future-key-here"}

class ChannelLog():
    def __init__(self, ctx: discord.Interaction, action: str, reason: str, expires: datetime | None = None) -> None:
        self.ctx = ctx
        self.action = action
        self.reason = reason
        self.expires = to_timestamp(expires) if expires is not None else "Never"
        
        ### Log-related stuff
        self.Embed = discord.Embed(
            timestamp = datetime.now(),
            description = f"**Action:** {self.action}\n**Reason:** {self.reason}"
        )

        self.Embed.set_author(name = ctx.user.global_name, icon_url = ctx.user.avatar)
        self.Embed.add_field(name = "Executor:", value = f'<@{ctx.user.id}>', inline = True)
        self.Embed.add_field(name = "Expires:", value = self.expires, inline = True)

    async def send(self):
        with open(os.environ["CONFIG_PATH"], "r", encoding = "UTF-8") as file:
            for _, channel_list in json.load(file).get("logging", {}).items():
                for channel in channel_list:
                    log_channel = self.ctx.client.get_channel(channel)

                    if isinstance(log_channel, discord.TextChannel):
                        await log_channel.send(embed = self.Embed)

            file.close()

def assert_request(response: requests.Response):
    if response.status_code != 200:
        raise requests.HTTPError(f"{response.status_code} | {json.dumps(response.json())}")

    return response

def to_timestamp(datetime: datetime) -> str:
    """Returns a dynamic discord timestamp string"""
    return f'<t:{int(datetime.timestamp())}:f>'