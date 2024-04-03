import json
import os

from assets import MachineID, get_execute_request, isOnline, mainAssets
from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    send_from_directory,
)
from flask_cors import CORS
from flask_minify import Minify
from rest_api import tcJSON

from aio_dlp import aiodownloader
from twofa import twofa

app = Flask(__name__)
ALLOW_ORIGINGS = os.environ.get("ALLOW_ORIGINGS")
origins = ALLOW_ORIGINGS.split(",")

CORS(app, origins=origins, methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
  allow_headers=["*"], supports_credentials=True)

Minify(app=app, html=True, js=True, cssless=True)


def flask_response(obj, status=200, **kwargs):
  return Response(json.dumps(obj), status, mimetype="application/json", **kwargs)

@app.route('/')
def index():
  is_online = isOnline()
  return render_template('custom.html', title="Home", is_online=is_online, machineId=MachineID)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.icon',mimetype='image/vnd.microsoft.icon')

@app.route('/assets', methods=['GET'])
def appassets():
  key = request.args.get("key")
  assets = mainAssets("1450582494671355516", "pages")
  publish_link = assets["publish$link"] if assets.get("publish$link") is not None else {}
  moderators = assets["moderators"] if assets.get("moderators") is not None else []

  if key:
    return jsonify({
      "publish$link": publish_link,
      "moderators": moderators,
    })
  else:
    return Response(json.dumps({"message":"Invalid Link"}), 500, mimetype="application/json")

@app.route('/main_js', methods=['GET'])
def mainjs():
  try:
    assets = mainAssets("1450582494671355516", "pages")
    mainJs = str(assets["script"]["tctt$video_downloader$moderators"])
    return jsonify({ "dev": mainJs, "main": mainJs})
  except:
    return Response(json.dumps({"message":"Invalid Link"}), 500, mimetype="application/json")

@app.route('/dashboard')
def dashboard():
  is_online = isOnline()
  return render_template('custom.html', title="Dashboard",  is_online=is_online, machineId=MachineID)

@app.route('/refresh')
def refresh():
  is_online = isOnline()
  return render_template('custom.html', title="Refresh", is_online=is_online, machineId=MachineID)

@app.route('/login')
def login():
  is_online = isOnline()
  return render_template('custom.html', title="Login", is_online=is_online, machineId=MachineID)


@app.route('/more_assets', methods=['POST'])
def moreAssets():
  body = request.get_json()
  postId = body.get("postId")
  postType = body.get("postType")

  if not postId and not isinstance(postId, str):
    Response(json.dumps({"message":"Invalid Post ID"}), 200, mimetype="application/json")

  try:
    assets = mainAssets(postId, postType or "posts")
    return Response(json.dumps(assets), 200, mimetype="application/json")
  except:
    return Response(json.dumps({"message":"Invalid Link"}), 500, mimetype="application/json")


@app.route('/await', methods=['GET'])
def waitingfor():
  try:
    return jsonify({"message": "success"})
  except:
    return Response(json.dumps({"message":"Invalid Link"}), 500, mimetype="application/json")

@app.errorhandler(404)
def own_404_page(error):
  return jsonify({"error": str(error)})

@app.route('/request', methods=['POST'])
def fetch():
  try:
    resp:dict = request.get_json()
    url = resp.get("url")
    if url is None:
      return flask_response({"message":"Invalid URL"}, 500)

    del resp["url"]
    resp_dict = get_execute_request(url, resp)
    return flask_response(resp_dict)
  except:
    return Response(json.dumps({"message":"Invalid Link"}), 500, mimetype="application/json")


app.register_blueprint(tcJSON, url_prefix="/tc-json/v1")
app.register_blueprint(aiodownloader, url_prefix="/aio_dlp")
app.register_blueprint(twofa, url_prefix="/2fa")

if __name__ == "__main__":
  app.run()
