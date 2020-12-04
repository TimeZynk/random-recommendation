from flask import jsonify, request, Blueprint
from recommendation.filters import (
    fetch_shifts_start_end,
    fetch_busy_users,
    fetch_unavailable_users,
    fetch_ineligible_users,
    fetch_no_work_hrs,
)
import requests
import json
import random
import os

recommendation = Blueprint("recommendation", __name__)


@recommendation.route("/api/health-check", methods=["GET"])
def health_check():
    return (
        json.dumps({"success": True}),
        200,
        {"ContentType": "application/json"}
    )


@recommendation.route("/api/ml/v1/recommendation", methods=["GET"])
def recommend_and_return():
    number = int(request.args.get("limit"))
    user_id = request.args.get("user-id")

    ids_qp = request.args.get("ids")
    query_shifts = [id.strip() for id in ids_qp.split(",")]

    headers = {"Authorization": request.headers["Authorization"]}

    TZBACKEND_URL = os.getenv("TZBACKEND_URL")

    qsse = fetch_shifts_start_end(query_shifts, TZBACKEND_URL, headers)

    busy_users_list = fetch_busy_users(qsse, TZBACKEND_URL, headers)

    unavailable_list = fetch_unavailable_users(qsse, TZBACKEND_URL, headers)

    ineligible_users_list = fetch_ineligible_users(
        query_shifts, TZBACKEND_URL, headers, user_id
    )

    no_work_hrs_list = fetch_no_work_hrs(qsse, TZBACKEND_URL, headers)

    excluded_users_list = list(
        map(
            lambda x, y, z, a: x.union(y, z, a),
            busy_users_list,
            unavailable_list,
            ineligible_users_list,
            no_work_hrs_list,
        )
    )

    users = requests.request("GET", TZBACKEND_URL + "/users", headers=headers)
    users_data = json.loads(users.text)
    user_ids = [user["id"] for user in users_data]
    avail_list = [
        [user for user in user_ids if user not in excluded_users]
        for excluded_users in excluded_users_list
    ]
    res_list = []
    for users in avail_list:
        random.shuffle(users)
        res_ids = users[:number] if len(users) > number else users
        res_list.append(res_ids)

    return jsonify(res_list)
