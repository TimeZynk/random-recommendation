from flask import Flask, jsonify, request
from flask_restful import Api
import requests
import json
import random
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

TZBACKEND_URL = os.getenv('TZBACKEND_URL')

app = Flask(__name__)
api = Api(app)

#base = "http://localhost:8989/"

@app.route("/api/ml/v1/recommendation", methods=['GET'])
def recommend_and_return():
    payload = ""
    number = int(request.args.get("limit"))
    headers = {"Authorization":request.headers["Authorization"]}
    #users = requests.request("GET", base + 'api/users', data=payload, headers=headers)
    users = requests.request("GET", TZBACKEND_URL + '/users', data=payload, headers=headers)

    data = json.loads(users.text)

    ids = [person['id'] for person in data]
    random.shuffle(ids)
    res = ids[:number] if len(ids)>number else ids
    return jsonify(res)



if __name__ == "__main__":
    app.run(debug=True)
