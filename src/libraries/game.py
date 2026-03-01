from collections import namedtuple
from src.libraries import utils
from typing import List

ActiveRestriction = namedtuple("ActiveRestriction", [
    "active", "startTime", "duration", "privateReason", "displayReason",
    "excludeAltAccounts", "inherited"
], defaults = [False, None, None, "", "", False, False])

class JoinRestriction:
    def __init__(self,
                 userid: int,
                 public_reason: str,
                 private_reason: str,
                 duration: utils.timedelta = utils.timedelta(days = -1),
                 exclude_alts: bool = False,
                 active: bool = True,
                 ):

        self.userid = userid 
        self.active = active
        self.duration = duration
        self.private_reason = private_reason
        self.display_reason = public_reason
        self.exclude_alts = exclude_alts

    def post(self) -> bool:
        total_time = self.duration.total_seconds()
        utils.assert_request(utils.requests.patch(
            f'{utils.APIs.universe_url}/user-restrictions/{self.userid}',
            headers = utils.APIs.rbx_header, 
            json = {
                "gameJoinRestriction": {
                    "active": self.active,
                    "duration": f'{total_time}s' if total_time > 0 else None,
                    "privateReason": self.private_reason,
                    "displayReason": self.display_reason,
                    "excludeAltAccounts": self.exclude_alts
                }
            }
        ))
  
        return True

def ban_status(user_id: int) -> ActiveRestriction:
    restriction_info: dict = utils.assert_request(utils.requests.get(
        url = f'{utils.APIs.universe_url}/user-restrictions/{user_id}',
        headers = utils.APIs.rbx_header
    )).json().get('gameJoinRestriction', {})

    return ActiveRestriction(**restriction_info)


def kick(userids: List[int], reason: str) -> bool:
    utils.assert_request(utils.requests.post(
        url = f"{utils.APIs.universe_url}:publishMessage",
        headers = utils.APIs.rbx_header,
        json = {
            'topic': "PlayerAction",
            'message': utils.json.dumps({
                'Action': "Kick",
                'Players': userids,
                'Reason': reason
            })
        }
    ))

    return True
