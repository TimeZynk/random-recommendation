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

@app.route("/api/ml/v1/recommendation", methods=['GET'])
def recommend_and_return():
    payload = ""
    number = int(request.args.get("limit"))

    #shift_ids acquired, but not doing anything with it yet.
    ids_qp = request.args.get("ids")
    shift_ids = [id.strip() for id in ids_qp.split(',')]

    headers = {"Authorization":request.headers["Authorization"]}
    users = requests.request("GET", TZBACKEND_URL + '/users', data=payload, headers=headers)

    data = json.loads(users.text)

    user_ids = [person['id'] for person in data]
    random.shuffle(user_ids)
    res = user_ids[:number] if len(user_ids)>number else user_ids
    return jsonify(res)



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
