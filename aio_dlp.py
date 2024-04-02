import json
from datetime import datetime
from urllib.parse import quote

from flask import Blueprint, Response, request
from yt_dlp import YoutubeDL
from yt_dlp.utils import format_bytes


def dict_to_url_quote(info_dict, url_dl):
    # update_info_dict = {"info_dict": {**info_dict}}
    update_info_dict = {"info_dict": {**info_dict}}
    url_dl = url_dl + ("&download_with_info_dict=%s" % quote(json.dumps(update_info_dict)))
    return { **update_info_dict, "url_dl": url_dl }

def format_bytes_tbr(duration, tbr):
  return int(duration * tbr * (1024 / 8))

def infoDict(info_dict):
  formats = info_dict["formats"]

  video_only = []
  audio_only = []
  both = []

  def getfilesize(info):
    filesize = 'N/A'
    filesize_num = 0
    if(info.get("filesize") is not None):
      filesize = format_bytes(info["filesize"])
      filesize_num:int = info["filesize"]
    elif(info.get("filesize_approx") is not None):
      filesize = format_bytes(info["filesize_approx"])
      filesize_num:int = info["filesize_approx"]
    elif(str(info["protocol"]).__contains__("m3u8") and info.get("tbr") is not None):
      _filesize = format_bytes_tbr(info_dict['duration'], info['tbr'])
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
        if(key["vcodec"] == "none" and not str(key["protocol"]).__contains__("m3u8")) and key.get("resolution") == "audio only":
          audio_only.append(getValues)
      if(isAcode and isVcode):
        if(key["acodec"] != "none" and key["vcodec"] != "none"):
          if key.get("width") is not None and key.get("width") is not None:
            getValues["width"] = key["width"]
            getValues["height"] = key["height"]
            both.append(getValues)
          else:
            both.append(getValues)


  deleteInfo_dict_chunks = []
  requested_download = []

  key_request_dl = "requested_downloads"
  requested_formats = info_dict.get("requested_formats")
  if info_dict.get(key_request_dl) is not None:
    for req_dl in info_dict[key_request_dl]:
      for key in req_dl:
        if type(req_dl[key]) is list:
          for val in req_dl[key]:
            if type(val) not in (str, list, dict, int, float):
              req_dl[key] = []
              # print(req_dl[key])
              continue
      # osA.AOS.write("vdo_youtube_extract_not_none.json", json.dumps(info_dict["requested_downloads"], indent=2))
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
    if requested_formats is not None:
      for req_fm in info_dict["requested_formats"]:
        if not str(req_fm["resolution"]).__contains__("audio"):
          filesize, filesize_num = getfilesize(req_fm)
          get_request_dl = {
            "title": info_dict["title"],
            "ext": req_fm["ext"],
            "filesize": filesize,
            "filesize_num": filesize_num,
            "width": req_fm["width"],
            "height": req_fm["height"],
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

  # is_youtube = info_dict["extractor_key"].lower() == "youtube"
  # if is_youtube and info_dict.get("requested_formats") is not None:
  #   format_video = requested_formats[0]
  #   format_audio = requested_formats[1]
  #   filesize_num = int(info_dict['duration'] * format_video['tbr'] * (1024 / 8)) + format_audio['filesize']
  #   filesize = format_bytes(filesize_num)
  #   width = format_video["width"]
  #   height = format_video["height"]
  #   requested_download = [{
  #     "title": info_dict["title"],
  #     "ext": format_video["video_ext"],
  #     "filesize": filesize,
  #     "filesize_num": filesize_num,
  #     "width": width,
  #     "height": height,
  #     "resolution": f"{width}x{height}",
  #     "url": info_dict["webpage_url"],
  #   }]

  final_info_dict = {
    "info_dict": info_dict,
    "video_only": video_only,
    "audio_only": audio_only,
    "both": both,
    "requested_download": requested_download,
  }
  # osA.AOS.write("vdo_youtube_extract_not_none.json", json.dumps(final_info_dict, indent=2))
  # AOS.write("video-final-formats-%s.json"%info_dict["extractor_key"].lower(), json.dumps(final_info_dict, indent=2))
  return final_info_dict

def extract_node_yt_dlp(
  url, only_url_dl=False, yt_opts={"quiet": True}
) -> dict[str,any]:
  with YoutubeDL(yt_opts) as tdl:
    info_dict = tdl.extract_info(url, False)
    video_info = info_dict.copy()
    has_generic = video_info.get("url") is not None
    url_dl = info_dict["original_url"]

    formats = video_info.get("formats",[{}])
    extractor_key = video_info.get("extractor_key","").lower()
    if has_generic:
      info_dict["sd"] = video_info["url"]
      info_dict["hd"] = video_info["url"]
      url_dl = video_info["url"]
    else:
      if extractor_key == "youtube":
        info_dict["original_url"] = video_info["webpage_url"]
        formats_url_dl = [
          f_info for f_info in formats
          if (not f_info.get("manifest_url")
            and isinstance(f_info.get("height"), int) and f_info.get("height") >= 360 and f_info.get("acodec") != "none" and f_info.get("vcodec") != "none"
          )
        ]
        len_url_dl = len(formats_url_dl)
        if len_url_dl >= 2:
          info_dl = formats_url_dl[len_url_dl - 1]
          width, height = info_dl.get("width",0), info_dl.get("height",0)
          info_dict["sd"] = formats_url_dl[len_url_dl - 2].get("url")
          info_dict["hd"] = info_dl.get("url")
          info_dict["width"] = width
          info_dict["height"] = height
          info_dict["resolution"] = f"{width}x{height}"
        elif len_url_dl == 1:
          info_dl = formats_url_dl[0]
          width, height = info_dl.get("width",0), info_dl.get("height",0)
          info_dict["sd"] = info_dl.get("url")
          info_dict["hd"] = info_dl.get("url")
          info_dict["width"] = info_dl.get("width",0)
          info_dict["height"] = info_dl.get("height",0)
          info_dict["resolution"] = f"{width}x{height}"
        else:
          info_dict["sd"] = video_info["original_url"]
          info_dict["hd"] = video_info["original_url"]
      elif extractor_key == "facebook":
        for info in formats:
          if isinstance(info_dict.get("hd"), str) and isinstance(info_dict.get("sd"), str):
            break
          if info.get("format_id") == "hd":
            info_dict["hd"] = info.get("url")
            url_dl = info_dict["hd"]
          elif info.get("format_id") == "sd":
            info_dict["sd"] = info.get("url")
      elif extractor_key == "tiktok":
        if len(formats) > 0:
          info_dict["dl_with_watermark"] = formats[0].get("url")

    timestamp = info_dict.get("timestamp") or info_dict.get("release_timestamp")
    if timestamp is not None and isinstance(timestamp, int):
      info_dict["release_timestamp"] = timestamp
      info_dict["timestamp"] = timestamp
      info_dict["upload_date"] = datetime.fromtimestamp(timestamp).__str__()


    info_dict["url"] = info_dict["original_url"]
    info_dict = infoDict(info_dict)
    video_info = info_dict["info_dict"]
    info_dict["info_dict"]["requested_download"] = [{
      "title": video_info.get("title"),
      "width": video_info.get("width", 0),
      "height": video_info.get("height", 0),
      "resolution": video_info.get("resolution"),
      "url": video_info.get("original_url"),
    }]
    info_dict = {
      **info_dict["info_dict"],
      # "formats": formats,
      "video_only": info_dict["video_only"],
      "audio_only": info_dict["audio_only"],
      "both": info_dict["both"],
    }

  if only_url_dl is True:
    return dict_to_url_quote(info_dict, url_dl)

  return info_dict


def aio_downloader(url, options):
  # yt_opts = {
  #   # 'verbose': True,
  #   # 'skip_download': True,
  #   # 'listformats': True,
  #   'overwrites': True,
  #   # 'outtmpl': outtmpl,
  #   # **yt_opts_logger
  # }
  yt_opts = { "quiet": True }
  if isinstance(options, dict):
    for k, v in options.items():
      yt_opts[k] = v
  info_dict = extract_node_yt_dlp(url, yt_opts=yt_opts)

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
