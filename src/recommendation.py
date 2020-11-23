from flask import jsonify, request, Blueprint
from datetime import datetime as dt
import requests
import json
import random
import os

recommendation = Blueprint('recommendation',__name__)

def fetch_busy_users(qsse, url, headers):
    busy_users = []
    for qs in qsse:
        params = {'interval[start]' : qs[0], 'interval[end]': qs[1], 'interval[match]': "intersects"}
        response = requests.request("GET", url + '/shifts', headers=headers, params = params)
        overlapped_shifts = json.loads(response.text)
        booked_users = []
        for shift in overlapped_shifts:
            if shift['booked']:
                [booked_users.append(user) for user in shift['booked-users'] if user not in booked_users]
        busy_users.append(booked_users)

    return busy_users

def fetch_shifts_start_end(shifts, url, headers):
    response = requests.request("GET", url + '/shifts', headers=headers)
    all_shifts = json.loads(response.text)

    selected_shifts = filter(lambda shift: shift['id'] in shifts, all_shifts)
    return list((shift['start'], shift['end']) for shift in selected_shifts)

@recommendation.route("/api/ml/v1/recommendation", methods=['GET'])
def recommend_and_return():
    number = int(request.args.get("limit"))

    ids_qp = request.args.get("ids")
    query_shifts = [id.strip() for id in ids_qp.split(',')]

    headers = {"Authorization":request.headers["Authorization"]}

    TZBACKEND_URL = os.getenv('TZBACKEND_URL')

    qsse = fetch_shifts_start_end(query_shifts, TZBACKEND_URL, headers)

    busy_users_list = fetch_busy_users(qsse, TZBACKEND_URL, headers)

    users = requests.request("GET", TZBACKEND_URL + '/users', headers=headers)
    users_data = json.loads(users.text)
    user_ids = [user['id'] for user in users_data]
    avail_list = [[user for user in user_ids if user not in busy_users] for busy_users in busy_users_list]
    res_list = []
    for users in avail_list:
        random.shuffle(users)
        res_ids = users[:number] if len(users)>number else users
        res_list.append(res_ids)

    return jsonify(res_list)
