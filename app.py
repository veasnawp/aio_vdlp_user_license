import json
import os

from flask import (
    Flask,
    Response,
    jsonify,
    render_template,
    request,
    send_from_directory,
)

# from flask_jsglue import JSGlue
from flask_minify import Minify

from assets import MachineID, mainAssets
from rest_api import tcJSON

app = Flask(__name__)
# openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 (RUN with SSL)
# jsglue = JSGlue(app)
# Minify(app=app, passive=True)
Minify(app=app, html=True, js=True, cssless=True)

assets = mainAssets("1450582494671355516", "pages")

script_src = assets["script"]["tctt$video_downloader$moderators"] if assets.get("script") else ""
# script_src = "https://rawcdn.githack.com/veasnawp/AIOVD-Frontent-React-JS/d8d5b27dcb58d1e54339fd826d68ea2801a9c01e/public/moderator.js"
# script_src = "https://phumikhmermov.local/assets/python/admin/dist/assets/js/bundle.js"

publish_link = assets["publish$link"] if assets.get("publish$link") else {}
moderators = assets["moderators"] if assets.get("moderators") else []

@app.route('/')
def index():
  return render_template('custom.html', title="Home", script_src=script_src, machineId=MachineID)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.icon',mimetype='image/vnd.microsoft.icon')

@app.route('/assets', methods=['GET'])
def appassets():
  key = request.args.get("key")
  if key:
    return jsonify({"publish$link": publish_link, "moderators": moderators})
  else:
    return Response(json.dumps({"message":"Invalid Link"}), 500, mimetype="application/json")

@app.route('/dashboard')
def dashboard():
  return render_template('custom.html', title="Dashboard", script_src=script_src, machineId=MachineID)

@app.route('/refresh')
def refresh():
  return render_template('custom.html', title="Refresh", script_src=script_src, machineId=MachineID)

@app.route('/login')
def login():
  return render_template('custom.html', title="Login", script_src=script_src, machineId=MachineID)

@app.route('/machineid', methods=['POST'])
def machineid():
  res:dict = request.get_json()
  if res.get("machine_id") is not None:
    return jsonify({"machine_id": MachineID})
  else:
    return Response(json.dumps({"message":"Invalid Link"}), 500, mimetype="application/json")

app.register_blueprint(tcJSON, url_prefix="/tc-json/v1")

# def runApp():
#   port = 5500
#   # app.run('localhost', port=port, debug=True)#ssl_context=('cert.pem', 'key.pem')
#   from waitress import serve
#   serve(app, host="localhost", port=port)

if __name__ == "__main__":
  # runApp()
  app.run()
