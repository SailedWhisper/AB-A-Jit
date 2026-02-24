import json
from src.libraries import utils

class DataStoreEntry:
    """
        DataType that corresponds to a DataStore entry, 
    """

    def __init__(self, entry_url: str) -> None:
        entry_data = utils.assert_request(utils.requests.get(
            url = entry_url,
            headers = utils.APIs.rbx_header
        )).json()

        self.value = entry_data['value']
        self.revision_id = entry_data['revisionId']
        self.create_time = utils.datetime.fromisoformat(entry_data['createTime'])
        self.revision_create_time = utils.datetime.fromisoformat(entry_data['revisionCreateTime'])
        self.users = map(lambda x: int(x), entry_data['users'])

def index_scoped(datastore_name: str, scope: str, key: str | int) -> DataStoreEntry:
    return DataStoreEntry(
        utils.APIs.universe_url + "/data-stores/{}/scopes/{}/entries/{}".format(
            datastore_name,
            scope,
            key
        )
    )

def index_nonscoped(datastore_name: str, key: str | int) -> DataStoreEntry:
    return DataStoreEntry(f"{utils.APIs.universe_url}/data-stores/{datastore_name}/entries/{key}")