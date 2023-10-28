import json

# from typing import Literal
from urllib.request import Request, urlopen


def _execute_request(
    url:str,
    method=None,
    headers=None,
    data=None,
    timeout=30000
):
    base_headers = {"User-Agent": "Mozilla/5.0", "accept-language": "en-US,en"}
    if headers:
        base_headers.update(headers)
    if data:
        # encode data for request
        if not isinstance(data, bytes):
            data = bytes(json.dumps(data), encoding="utf-8")
        # bindata = data if type(data) == bytes else data.encode('utf-8')

    # print(data)
    if url.lower().startswith("http"):
        request = Request(url, headers=base_headers, method=method, data=data)
    else:
        raise ValueError("Invalid URL")
    return urlopen(request, timeout=timeout)  # nosec

MachineID = "2D5BE66F-6DA9-434E-A0AC-518722E39A8E"
domain = 'https://veasnapythonusers.blogspot.com'


def mainAssets(id) -> dict[str,any]:

    url = f'{domain}/feeds/pages/default/{id}?alt=json'
    r = _execute_request(url)
    data_dict:dict = json.loads(bytes.decode(r.read()))
    return json.loads(data_dict['entry']['content']['$t'])


# if __name__ == "__main__":
#     pageId = '1450582494671355516'
#     print(machineid.id())
#     print(MachineID)
    # print(machineid.hashed_id(machineid.id()))
    # print(machineid.hashed_id())
