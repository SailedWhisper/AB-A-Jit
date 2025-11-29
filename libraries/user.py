from libraries import utils

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
        return ""

    def title_str(self):
        return f"[{str(self)}]({self.profile_url})"

    def __str__(self) -> str:
        return f'@{self.username} ({self.display_name})'

    def __int__(self) -> int:
        return self.userid

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