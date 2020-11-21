from flask import Flask, jsonify, request
from flask_restful import Api
from datetime import datetime as dt
import requests
import json
import random
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

TZBACKEND_URL = os.getenv('TZBACKEND_URL')

app = Flask(__name__)
api = Api(app)

def get_bookable_users(query_shifts, shifts_data, users_data):
    format_string = "%Y-%m-%dT%H:%M:%S.%f"
    query_shifts_startend = [
            (dt.strptime(shift_data['start'], format_string), dt.strptime(shift_data['end'], format_string)) 
            for shift_data in shifts_data 
            if shift_data['id'] in query_shifts
        ]

    candidates_list = []
    for qsse in query_shifts_startend:
        candidates = [user['id'] for user in users_data]
        for shift in shifts_data:
            if shift['booked'] and dt.strptime(shift['start'],format_string) < qsse[1] and dt.strptime(shift['end'],format_string) > qsse[0]:
                [candidates.remove(user) for user in shift["booked-users"] if user in candidates] 
        candidates_list.append(candidates)
    return candidates_list
        

@app.route("/api/ml/v1/recommendation", methods=['GET'])
def recommend_and_return():
    payload = ""
    number = int(request.args.get("limit"))

    #shift_ids acquired, but not doing anything with it yet.
    ids_qp = request.args.get("ids")
    query_shifts = [id.strip() for id in ids_qp.split(',')]

    headers = {"Authorization":request.headers["Authorization"]}
    users = requests.request("GET", TZBACKEND_URL + '/users', data=payload, headers=headers)
    shifts = requests.request("GET", TZBACKEND_URL + '/shifts', data=payload, headers=headers)

    users_data = json.loads(users.text)
    shifts_data = json.loads(shifts.text)

    bookable_users = get_bookable_users(query_shifts, shifts_data, users_data)

    res_list = []
    for users in bookable_users:
        random.shuffle(users)
        res_ids = users[:number] if len(users)>number else users            
        res_list.append(res_ids)

    return jsonify(res_list)



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
