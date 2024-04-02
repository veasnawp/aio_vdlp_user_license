import json
import time

import pymongo
from assets import MachineID, isModerator
from bson.objectid import ObjectId
from configs import mongodb_url

# from dotenv import load_dotenv
from flask import Blueprint, Response, request

tcJSON = Blueprint(__name__, "tcJSON")
# load_dotenv()
# MONGODB_URL = os.environ["MONGODB_URL"]

MONGODB_URL = mongodb_url(f"license_app_user","Veasna_9109")

INVALID_CREDENTIAL = json.dumps({"message":"Invalid Credential"})

try:
  client = pymongo.MongoClient(MONGODB_URL,serverSelectionTimeoutMS=1000) #connecting to mongo server
  db = client.tcodettool #creating a new database namely company
  client.server_info()
except:
  try:
    db = client.tcodettool #creating a new database namely company
    client.server_info()
  except:
    time.sleep(5)
    try:
      db = client.tcodettool #creating a new database namely company
      client.server_info()
    except:
      db = None

def usersId():
  if db is None:
    return []
  data = list(db.users.find())
  usersId = [str(user["_id"]) for user in data]
  return usersId

##################################
@tcJSON.route("/users",methods=["GET"])
def get_all_users(): #function to display all the users from database
  if request.args.get("mid") != MachineID.upper():
    return Response(
      json.dumps({"message":"No user, please add one",}),
      200,mimetype="application/json"
    )

  try:
    data=list(db.users.find())
    if len(data) > 0:
      for user in data:
        user["_id"] = str(user["_id"])
      return Response(json.dumps(data),200,mimetype="application/json")
    else:
      return Response(
        json.dumps({"message":"No user, please add one",}),
        200,mimetype="application/json"
      )
  except Exception as ex: #except block used in case any error occures while connecting with database or any other unexpected error occurs
    print(ex)
    return Response(
      json.dumps({"message":"Cannot read user",}),
      500,mimetype="application/json"
    )

##################################
@tcJSON.route("/users/<id>",methods=["GET"])
def get_user(id): #function to get user with specific id from database
  try:
    data=list(db.users.find({"_id": ObjectId(id)}))
    for user in data:
      user["_id"]=str(user["_id"])
    return Response(json.dumps(data),200,mimetype="application/json")
  except Exception as ex: #except block used in case wrong user id is given or any other unexpected error occurs
    print(ex)
    return Response(json.dumps({"message": "Error Cannot Find user"}),500,mimetype="application/json")

##################################
@tcJSON.route("/users",methods=["POST"])
def create_user(): #function to create new user in database
  if request.method != "POST":
    return Response(json.dumps({"message":"Bad Request"}), 500, mimetype="application/json")

  try:
    key = request.args.get('key')
    body:dict = request.get_json()
    user = {
      "name": body["name"],
      "email": body["email"],
      "avatar": body["avatar"] or "",
      # "password": request.form["password"]
    }
    add_info_user = ["password","machineId","license","allProperties"]
    for k in add_info_user:
      if body.get(k) is not None:
        user[k] = body[k]

    if key:
      user_exist = db.users.find_one({"email": user["email"]})
      if user_exist:
        user_exist["_id"] = str(user_exist["_id"])
        return Response(json.dumps(user_exist), 200, mimetype="application/json")
      else:
        dbResponse = db.users.insert_one(user)
        data=list(db.users.find({"_id": ObjectId(dbResponse.inserted_id)}))
        for user in data:
          user["_id"] = str(dbResponse.inserted_id)
          user["message"] = "User created"
      # pprint.pprint(user)
        return Response(
          json.dumps(user),
          200, mimetype="application/json"
        )
    else:
      return Response(INVALID_CREDENTIAL, 200, mimetype="application/json")
  except Exception as ex: #except block used in case any error occur while adding data or any wrong entry is filled or any entry filled with wrong or improper data or any other unexpected error occurs
    print("Error", ex)
    return Response(json.dumps({"message":"Error"}), 500, mimetype="application/json")

##################################
@tcJSON.route("/users/<id>",methods=["PUT"])
def insert_any_to_user(id): #function to update the data of user with specific id in database
  try:
    key = request.args.get('key')
    if key is None:
      return Response(INVALID_CREDENTIAL, 200, mimetype="application/json")

    body:dict[str, any] = request.get_json()
    if body.get("email") is None or body.get("name") is None:
      return Response(json.dumps({"message": "invalid name or email"}), 200, mimetype="application/json")

    dbResponse=db.users.update_one({"_id": ObjectId(id)},{
      "$set": body
    })

    data=list(db.users.find({"_id": ObjectId(id)}))
    user:dict = data[0]
    user["_id"] = str(user["_id"])
    if dbResponse.modified_count == 1:
      user["message"] = "user updated"
      return Response(
        json.dumps(user),
        200,mimetype="application/json"
      )
    else:
      user["message"] = "nothing to modify"
      return Response(
        json.dumps(user),
        200,mimetype="application/json"
      )
  except Exception as ex: #excep block ised in case wrong id is used or user with the id is not present or any other unexpected error occurs
    print(ex)
    return Response(
      json.dumps({"message": "Error Cannot update"}),
      500,mimetype="application/json"
    )

##################################
@tcJSON.route("/users/<id>",methods=["PATCH"])
def update_user(id): #function to update the data of user with specific id in database
  try:
    key = request.args.get('key')
    if key is None:
      return Response(INVALID_CREDENTIAL, 200, mimetype="application/json")

    body:dict = request.get_json()
    user = {
      "name": body["name"],
      "email": body["email"],
      "avatar": body["avatar"],
      # "password": request.form["password"]
    }
    # add_info_user = list(body["add_info_user"]) if body.get("add_info_user") is not None else []
    if body.get("add_info_user") is not None:
      add_info_user:dict[str,any] = body["add_info_user"]
      for k, v in dict(add_info_user).items():
        if add_info_user.get(k) is not None:
          user[k] = v

    dbResponse=db.users.update_one({"_id": ObjectId(id)},{
      "$set": user
    })
    if dbResponse.modified_count == 1:
      return Response(
        json.dumps({"message": "user updated"}),
        200,mimetype="application/json"
      )
    else:
      return Response(
        json.dumps({"message": "nothing to modify"}),
        200,mimetype="application/json"
      )
  except Exception as ex: #excep block ised in case wrong id is used or user with the id is not present or any other unexpected error occurs
    print(ex)
    return Response(
      json.dumps({"message": "Error Cannot update"}),
      500,mimetype="application/json"
    )

##################################
@tcJSON.route("/users/<id>",methods=["DELETE"])
def delete_user(id): #fucntion to delete user from database
  try:
    body = request.get_json()
    if isinstance(body, dict) and not isModerator(body.get("userId")):
      return Response(INVALID_CREDENTIAL, 200, mimetype="application/json")

    user = db.users.find_one({"_id": ObjectId(id)})
    # data=list(db.users.find({"_id": ObjectId(id)}))
    # for user in data:
    #   user["_id"]=str(user["_id"])
    dbResponse=db.users.delete_one({"_id": ObjectId(id)})
    if dbResponse.deleted_count == 1:
      user["_id"] = str(user["_id"])
      user["message"] = "User Deleted Successfully"
      return Response(
        json.dumps(user),
        200,mimetype="application/json"
      )
    else:
      return Response(
        json.dumps({"message": "User not found"}),
        500,mimetype="application/json"
      )
  except Exception as ex:
    return Response(json.dumps({"message": "Cannot delete user"}),500,mimetype="application/json")
##################################
# if __name__=="__main__":
#   app.run(debug=True, port=8080)
#   try:
#   client = pymongo.MongoClient(MONGODB_URL,serverSelectionTimeoutMS=1000) #connecting to mongo server
#   db = client.test #creating a new database namely company
#   users_collection = db.users
#   client.server_info()
#   data = users_collection.find_one({"_id": ObjectId("64982d071c4753c16a8f034f")})
#   print(data)
#   client.close()
#   except:
#     print("ERROR")
