from flask import Flask, jsonify, request
from flask_restful import Api
import requests
import json
import random
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
api = Api(app)

base = "http://localhost:8989/"

@app.route("/recommend/<int:number>", methods=['GET'])
def recommend_and_return(number):
    payload = ""
    headers = request.headers
    users = requests.request("GET", base + 'api/users', data=payload, headers=headers)
    data = json.loads(users.text)

    ids = []
    [ids.append({"id":person['id']}) for person in data]
    random.shuffle(ids)
    res = ids[:number] if len(ids)>number else ids
    return jsonify(res)



if __name__ == "__main__":
    app.run(debug=True)
