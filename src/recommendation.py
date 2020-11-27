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
        booked_users = set()
        for shift in overlapped_shifts:
            if shift['booked']:
                booked_users = booked_users.union(set(shift['booked-users']))  
        busy_users.append(booked_users)

    return busy_users

def fetch_unavailable_users(qsse, url, headers):
    unavailable_users = []
    for qs in qsse:
        params = {'interval[start]' : qs[0], 'interval[end]': qs[1], 'interval[match]': 'intersects', 'available': 'false'}
        response = requests.request("GET", url + '/availabilities', headers=headers, params = params)
        unavailabilities = json.loads(response.text)
        unavailable_list = set(map(lambda x: x['user-id'], unavailabilities))
        unavailable_users.append(unavailable_list)

    return unavailable_users

def fetch_shifts_start_end(shifts, url, headers):
    response = requests.request("GET", url + '/shifts', headers=headers)
    all_shifts = json.loads(response.text)

    selected_shifts = filter(lambda shift: shift['id'] in shifts, all_shifts)
    return list((shift['start'], shift['end']) for shift in selected_shifts)

def fetch_combinations(shifts, url, headers):
    params = {"ids" : ",".join(shifts)}
    response = requests.request("GET", url + '/ref-data/v1/shifts', headers=headers, params = params)
    shifts_refdata = json.loads(response.text)
    registers_it = map(lambda x: list(x['registers'].values()) if 'registers' in x.keys() else [], shifts_refdata.values())

    
    user_id = {"user-id": "5fae44a05866602bef205abb"}
    response_rs = requests.request("GET", url + '/registers/v1/summary', headers=headers, params = user_id)
    registers_summary = json.loads(response_rs.text)
    registry_data = registers_summary['registry-data']

    return [list(map(lambda z: z['permissions']['schedule'], filter(lambda x: x['id'] in registers and 'permissions' in x.keys(), registry_data))) for registers in registers_it]

def fetch_ineligible_users(shifts, url, headers):
    combinations_list = fetch_combinations(shifts, url, headers)
    response = requests.request("GET", url + '/users', headers=headers)
    users = json.loads(response.text)

    ineligible_users = []
    for combinations in combinations_list:
        elig_it = filter(lambda x: 'combinations' not in x.keys() or not set(combinations).issubset(set(x['combinations'])), users)
        ineligible_users.append(set(map(lambda x: x['id'], elig_it)))
        
    return ineligible_users

@recommendation.route("/api/ml/v1/recommendation", methods=['GET'])
def recommend_and_return():
    number = int(request.args.get("limit"))

    ids_qp = request.args.get("ids")
    query_shifts = [id.strip() for id in ids_qp.split(',')]

    headers = {"Authorization":request.headers["Authorization"]}

    TZBACKEND_URL = os.getenv('TZBACKEND_URL')

    qsse = fetch_shifts_start_end(query_shifts, TZBACKEND_URL, headers)

    busy_users_list = fetch_busy_users(qsse, TZBACKEND_URL, headers)

    unavailable_list = fetch_unavailable_users(qsse, TZBACKEND_URL, headers)

    ineligible_users_list = fetch_ineligible_users(query_shifts, TZBACKEND_URL, headers)

    excluded_users_list = list(map(lambda x,y,z: x.union(y,z), busy_users_list, unavailable_list, ineligible_users_list))

    users = requests.request("GET", TZBACKEND_URL + '/users', headers=headers)
    users_data = json.loads(users.text)
    user_ids = [user['id'] for user in users_data]
    avail_list = [[user for user in user_ids if user not in excluded_users] for excluded_users in excluded_users_list]
    res_list = []
    for users in avail_list:
        random.shuffle(users)
        res_ids = users[:number] if len(users)>number else users
        res_list.append(res_ids)

    return jsonify(res_list)
