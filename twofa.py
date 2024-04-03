import json
import re
import time

import pyotp
from flask import (
    Blueprint,
    Response,
    jsonify,
    request,
)


twofa = Blueprint(__name__, "twofa")

@twofa.route("/", methods=['POST'])
def home():
  res = request.get_json()
  if res.get("key") is None:
    return Response(json.dumps({"message":"Invalid Key"}), 500, mimetype="application/json")

  try:
    secret_key = res["key"]
    code = pyotp.TOTP(re.sub(r'\s+','',secret_key))
    time.sleep(0.1)
    return jsonify({"result": code.now()})
  except:
    return Response(json.dumps({"message":"Invalid Key"}), 500, mimetype="application/json")
