import json
import os
from urllib.error import URLError
# from typing import Literal
from urllib.request import Request, urlopen

KEY_URLOPENRET = [
    # "fp", # <_io.BufferedReader name=400>
    "debuglevel", # int
    "_method", # Literal["GET", "POST", "PUT", ...]
    "version", # int
    "headers", # <http.client.HTTPMessage object at 0x00000201B0297910>
    "msg", "reason", # Literal["OK", ...]
    "status", "code", # Literal[200, 404, 500, ...]
    "chunked", # bool
    "chunk_left", # str(UNKNOWN)
    "length", # content-length: int
    "will_close", # bool
    "url", # redirect url
]

def _execute_request(
    url,
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

def get_execute_request(url:str, resp_option:dict[str,any]=None):
    options = {
        "url": url
    }
    if isinstance(resp_option, dict):
        for key, val in resp_option.items():
            if resp_option.get(key) is not None:
                options[key] = val
    response_dict = {}

    # print(options)
    headers = {}
    r = _execute_request(**options)
    r_dict = r.__dict__
    for key in KEY_URLOPENRET:
        if key == "headers":
            r_headers = dict(r_dict["headers"])
            for k, v in r_headers.items():
                val = str(v).strip()
                if not val.startswith("{") and not val.endswith("}"):
                    headers[k] = v
        else:
            response_dict[key] = r_dict[key]

    if response_dict.get("status") == 200:
        response_dict["data"] = bytes.decode(r.read())

    response_dict["headers"] = headers
    return response_dict



def isOnline():
    url = 'https://www.google.com'
    try:
      r = _execute_request(url)
      return True
    except URLError as err:
      # print(err.__dict__)
      return False

MachineID = "2D5BE66F-6DA9-434E-A0AC-518722E39A8E"
domain = os.environ.get("DOMAIN")

def mainAssets(id, type_):

    url = f'{domain}/feeds/{type_}/default/{id}?alt=json'
    r = _execute_request(url)
    data_dict:dict = json.loads(bytes.decode(r.read()))
    return json.loads(data_dict['entry']['content']['$t'])

def isModerator(userId=None, id="1450582494671355516", type="pages"):
  assets = mainAssets(id, type)
  moderators = [user.get("userId") for user in assets["moderators"]]
  if userId in moderators:
    # print("Moderators: ", moderators)
    return True
  else:
    # print("Moderators: ", assets["moderators"])
    return False

# if __name__ == "__main__":
#     pageId = '1450582494671355516'
#     print(machineid.id())
#     print(MachineID)
    # print(machineid.hashed_id(machineid.id()))
    # print(machineid.hashed_id())
