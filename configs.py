# # from os import system
# from typing import Optional


def mongodb_url(
  usename,password,
  uri=None,
  query=None
):
  QUERY = query if query else {
    "retryWrites": "true",
    "w": "majority",
  }
  uri = uri if uri else "cluster0.fzpmugq.mongodb.net"
  query_ = '&'.join(f'{key}={value}' for key, value in QUERY.items())
  return "mongodb+srv://{0}:{1}@{2}/?{3}".format(usename, password, uri, query_)
