import json

from flask import Blueprint, Response, request
from yt_dlp import YoutubeDL
from yt_dlp.utils import format_bytes


def infoDict(info_dict):
  formats = info_dict["formats"]

  video_only = []
  audio_only = []
  both = []

  def getfilesize(key):
    filesize = 'N/A'
    filesize_num = 0
    if(key.get("filesize") is not None):
      filesize = format_bytes(key["filesize"])
      filesize_num:int = key["filesize"]
    elif(key.get("filesize_approx") is not None):
      filesize = format_bytes(key["filesize_approx"])
      filesize_num:int = key["filesize_approx"]
    elif(str(key["protocol"]).__contains__("m3u8") and key.get("tbr") is not None):
      _filesize = int(info_dict['duration'] * key['tbr'] * (1024 / 8))
      filesize = format_bytes(_filesize)
      filesize_num = _filesize

    return (filesize, filesize_num)

  for key in formats:
    extenstion = 'm3u8' if str(key["protocol"]).__contains__("m3u8") else key["ext"]
    filesize, filesize_num = getfilesize(key)

    isAcode = key.get("acodec") is not None
    isVcode = key.get("vcodec") is not None

    getValues = {
      "title": info_dict["title"],
      "ext": extenstion,
      "filesize": filesize,
      "filesize_num": filesize_num,
      "resolution": key["resolution"],
      "url": key["url"],
    }
    # print(getValues)
    if(key["protocol"] != "mhtml" and key["ext"] not in ['f4f', 'f4m'] and (isAcode or isVcode)):
      if(isAcode):
        if(key["acodec"] == "none" and key["height"] >= 360):
          getValues["width"] = key["width"]
          getValues["height"] = key["height"]
          # print("video only: ", getValues)
          video_only.append(getValues)
      if(isVcode):
        if(key["vcodec"] == "none" and not str(key["protocol"]).__contains__("m3u8")):
          # print("audio only: ", getValues, )
          audio_only.append(getValues)
      if(isAcode and isVcode):
        if(key["acodec"] != "none" and key["vcodec"] != "none"):
          # print("both: ", key["url"], key["resolution"])
          if key.get("width") is not None and key.get("width") is not None:
            getValues["width"] = key["width"]
            getValues["height"] = key["height"]
            both.append(getValues)
          else:
            both.append(getValues)

  deleteInfo_dict_chunks = []
  requested_download = []

  key_request_dl = "requested_downloads"
  if info_dict.get(key_request_dl) is not None:
    for req_dl in info_dict[key_request_dl]:
      for key in req_dl:
        if isinstance(req_dl[key], list):
          for val in req_dl[key]:
            if type(val) not in (str, list, dict):
              req_dl[key] = []
              continue

      filesize, filesize_num = getfilesize(req_dl)
      get_request_dl = {
        "title": info_dict["title"],
        "ext": req_dl["ext"],
        "filesize": filesize,
        "filesize_num": filesize_num,
        "resolution": req_dl["resolution"] if req_dl.get("resolution") is not None else "N/A",
        "url": info_dict["webpage_url"],
        "video": req_dl["url"] if req_dl.get("url") is not None else "",
      }
      requested_download.append(get_request_dl)
  else:
    request_dl = "requested_formats"
    if info_dict.get("requested_formats") is not None:
      for req_fm in info_dict["requested_formats"]:
        if not str(req_fm["resolution"]).__contains__("audio"):
          filesize, filesize_num = getfilesize(req_fm)
          get_request_dl = {
            "title": info_dict["title"],
            "ext": req_fm["ext"],
            "filesize": filesize,
            "filesize_num": filesize_num,
            "resolution": req_fm["resolution"],
            "url": info_dict["webpage_url"],
          }
          requested_download.append(get_request_dl)

  if info_dict.get(key_request_dl) is not None:
    del info_dict[key_request_dl]

  for key in info_dict:
    if type(info_dict[key]) in (list, dict) and key not in ("categories","tags","requested_formats") :

      if(json.dumps(info_dict[key]).__len__() > 1000 or key in ("automatic_captions","subtitles","heatmap")):
        # isManyChunks = json.dumps(info_dict[key]).__len__()
        deleteInfo_dict_chunks.append(key)
        # del info_dict[key]

  # deleteInfo_dict_chunks = ["formats","automatic_captions","heatmap","thumbnails","subtitles"]
  # AOS.write("video-list-1.json", json.dumps(video_only, indent=2))
  for key in deleteInfo_dict_chunks:
    del info_dict[key]

  info_dict["title"] = info_dict["fulltitle"] = info_dict["title"].replace("|", "—")

  final_info_dict = {
    "info_dict": info_dict,
    "video_only": video_only,
    "audio_only": audio_only,
    "both": both,
    "requested_download": requested_download,
  }

  return final_info_dict


def aio_downloader(url, options):
  # yt_opts = {
  #   # 'verbose': True,
  #   # 'skip_download': True,
  #   # 'listformats': True,
  #   'overwrites': True,
  #   # 'outtmpl': outtmpl,
  #   # **yt_opts_logger
  # }
  yt_opts = {}
  if isinstance(options, dict):
    for k, v in options.items():
      yt_opts[k] = v

  with YoutubeDL(yt_opts) as ydl:
    info_dict = ydl.extract_info(url, False)
    info_dict = infoDict(info_dict)
  return info_dict


aiodownloader = Blueprint(__name__, "aiodownloader")

@aiodownloader.route("/", methods=['POST'])
def aio_dlp():
  # url = request.args.get("url")
  res = request.get_json()
  url = res.get("url")
  if url is None:
    return Response(json.dumps({"message":"Invalid Link"}), 500, mimetype="application/json")

  if request.headers.get("Content-Type") is None:
    return Response(
      json.dumps({"message":"Bad Request"}),
      500,mimetype="application/json"
    )

  yt_opts = res["yt_opts"] if isinstance(res.get("yt_opts"), dict) else {}
  try:
    aio_dlp = aio_downloader(url, yt_opts)
    video_info = aio_dlp
    # print(video_info)

    return json.dumps(video_info)
  except ValueError as err:
    return Response(
      json.dumps({"message": "err", "url": url}),
      500,mimetype="application/json"
    )
