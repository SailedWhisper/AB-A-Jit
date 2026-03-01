from discord import ui
from src.libraries import utils

class User():
    def __init__(self, userid: int | str):
        user_data: dict = utils.assert_request(utils.requests.get(
            url = f'{utils.APIs.base_url}/cloud/v2/users/{get_userid(userid)}',
            headers = utils.APIs.rbx_header
        )).json()

        self.userid = user_data.get('id', 0)
        self.username = user_data.get('name', "")
        self.display_name = user_data.get('displayName', "")
        self.description = user_data.get("about", "<Not available>")

        self.created = utils.datetime.fromisoformat(user_data['createTime'])
        self.profile_url = f"https://www.roblox.com/users/{self.userid}/profile"

    def thumbnail(self) -> str:
        response = utils.assert_request(utils.requests.get(
            url = f"https://apis.roblox.com/cloud/v2/users/{self.userid}:generateThumbnail?shape=SQUARE",
            headers = utils.APIs.rbx_header
        )).json()

        return response['response']['imageUri']

    def title_str(self):
        return f"[{str(self)}]({self.profile_url})"

    def __str__(self) -> str:
        return f'@{self.username} ({self.display_name})'

    def __int__(self) -> int:
        return self.userid

class UserCardComponent(ui.LayoutView):
    def __init__(self, *, timeout: float | None = 180, info: User) -> None:
        super().__init__(timeout = timeout)

        name_title = f'## [{info.display_name} (@{info.username})]({info.profile_url})'

        self.user_info = info
        self.container = ui.Container(
            ui.Section(
                ui.TextDisplay(name_title + f'\n"*{info.description}*"'),
                accessory = ui.Thumbnail(info.thumbnail())
            )
        )

        self.add_item(self.container)

def get_userid(name: str | int) -> int:
    if str(name).isnumeric():
        return int(name)
    else:
        request_result = utils.assert_request(utils.requests.post(
            url = "https://users.roblox.com/v1/usernames/users",
            json = {'usernames': [name], 'excludeBannedUsers': False}
        ))

        if len(request_result.json()['data']) > 0:
            return int(request_result.json()['data'][0]['id'])
        
        raise utils.requests.HTTPError("User not found.", response = request_result)