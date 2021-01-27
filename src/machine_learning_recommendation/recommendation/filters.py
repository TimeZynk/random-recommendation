from datetime import datetime as dt
from datetime import timedelta
import requests
import json
import logging
from bson.objectid import ObjectId

# logger = logging.getLogger(__name__)


def fetch_busy_users(qsse, url, headers):
    """
    For each queried shift, fetch the shifts with time overlaps, then obtain the users from each of them to create a list of users that should not be booked due to overlaps.
    """
    logger = logging.getLogger(__name__)
    logger.debug("fetch_busy_users")

    busy_users = []
    for qs in qsse:
        params = {
            "interval[start]": qs[0],
            "interval[end]": qs[1],
            "interval[match]": "intersects",
        }
        response = requests.request(
            "GET", url + "/shifts", headers=headers, params=params
        )
        overlapped_shifts = json.loads(response.text)
        booked_users = set()
        for shift in overlapped_shifts:
            if shift["booked"]:
                booked_users = booked_users.union(set(shift["booked-users"]))
        busy_users.append(booked_users)

    return busy_users


def fetch_unavailable_users(qsse, url, headers):

    logger = logging.getLogger(__name__)
    logger.debug("fetch_unavailable_users")

    unavailable_users = []
    for qs in qsse:
        params = {
            "interval[start]": qs[0],
            "interval[end]": qs[1],
            "interval[match]": "intersects",
            "available": "false",
        }
        response = requests.request(
            "GET", url + "/availabilities", headers=headers, params=params
        )
        unavailabilities = json.loads(response.text)
        unavailable_list = set(map(lambda x: x["user-id"], unavailabilities))
        unavailable_users.append(unavailable_list)

    return unavailable_users


def fetch_shifts_start_end_created(shifts, url, headers):

    logger = logging.getLogger(__name__)
    logger.debug("fetch_shifts_start_end_created")

    start_end_created_list = []
    for shift in shifts:
        response = requests.request(
            "GET", url + "/shifts", headers=headers, params={"id": shift}
        )
        shift_data = json.loads(response.text)

        start_end_created_list.append(
            (
                shift_data[0]["start"],
                shift_data[0]["end"],
                ObjectId(shift_data[0]["id"]).generation_time,
            )
        )

    return start_end_created_list


def fetch_combinations(shifts, url, headers, user_id):

    logger = logging.getLogger(__name__)
    logger.debug("fetch_combinations")

    params = {"ids": ",".join(shifts)}
    response = requests.request(
        "GET", url + "/ref-data/v1/shifts", headers=headers, params=params
    )
    shifts_refdata = json.loads(response.text)
    registers_it = map(
        lambda x: list(x["registers"].values()) if "registers" in x.keys() else [],
        shifts_refdata.values(),
    )

    params_rs = {"user-id": user_id}

    response_rs = requests.request(
        "GET", url + "/registers/v1/summary", headers=headers, params=params_rs
    )
    registers_summary = json.loads(response_rs.text)

    registry_data = registers_summary["registry-data"]

    return [
        list(
            map(
                lambda z: z["permissions"]["schedule"],
                filter(
                    lambda x: x["id"] in registers and "permissions" in x.keys(),
                    registry_data,
                ),
            )
        )
        for registers in registers_it
    ]


def fetch_ineligible_users(shifts, url, headers, user_id):

    logger = logging.getLogger(__name__)
    logger.debug("fetch_ineligible_users")

    combinations_list = fetch_combinations(shifts, url, headers, user_id)
    response = requests.request("GET", url + "/users", headers=headers)
    users = json.loads(response.text)

    ineligible_users = []
    for combinations in combinations_list:
        elig_it = filter(
            lambda x: "combinations" not in x.keys()
            or not set(combinations).issubset(set(x["combinations"])),
            users,
        )
        ineligible_users.append(set(map(lambda x: x["id"], elig_it)))

    return ineligible_users


def fetch_work_hour_templates(url, headers, contracts):

    logger = logging.getLogger(__name__)
    logger.debug("fetch_work_hour_templates")

    fmt = "%Y-%m-%d"
    users_dict = {}
    for contract in contracts:
        response_wh = requests.request(
            "GET",
            url + "/work-hours-templates",
            headers=headers,
            params={"id": contract["template-id"]},
        )
        wh = json.loads(response_wh.text)
        template_dict = {
            "start-date": dt.strptime(contract["start-date"], fmt),
            "work-hours": wh[0]["rows"],
            "fulltime-hours": wh[0]["fulltime-hours"],
        }
        if "end-date" in contract.keys():
            template_dict["end-date"] = dt.strptime(contract["end-date"], fmt)

        if contract["user-id"] in users_dict.keys():
            users_dict[contract["user-id"]].append(template_dict)
        else:
            users_dict[contract["user-id"]] = [template_dict]
    return users_dict


def week_start_end(shift_time):

    logger = logging.getLogger(__name__)
    logger.debug("week_start_end")

    week_start = shift_time - timedelta(days=shift_time.weekday())
    week_end = week_start + timedelta(days=7)
    week_start_real = dt(week_start.year, week_start.month, week_start.day)
    week_end_real = dt(week_end.year, week_end.month, week_end.day) - timedelta(
        microseconds=1
    )
    return (week_start_real, week_end_real)


def fulltime_hrs_and_work_hrs(qsse, work_hours_data, url, headers):
    """
    In the current implementation we're under the assumption that the shifts
     are short and not exdended over several contracts.
    """

    logger = logging.getLogger(__name__)
    logger.debug("fulltime_hrs_and_work_hrs")

    fmt = "%Y-%m-%dT%H:%M:%S.%f"
    no_hrs_users = []
    for qs in qsse:
        no_hrs_set = set()
        shift_start = dt.strptime(qs[0], fmt)
        shift_end = dt.strptime(qs[1], fmt)
        for user, work_hours_list in work_hours_data.items():
            for wh in work_hours_list:
                week_start, week_end = week_start_end(shift_start)
                # not considering the possibility of shifts bring longer than
                #  24hrs and could overlap with a contract by a late portion.
                if shift_start >= wh["start-date"] and "end-date" not in wh.keys():
                    intersection = (
                        max(week_start, wh["start-date"]),
                        week_end,
                    )
                # Again not considering the situation of a shift last passing
                #  the end-date of a contract.
                elif shift_start >= wh["start-date"] and shift_end <= wh["end-date"]:
                    intersection = (
                        max(week_start, wh["start-date"]),
                        min(week_end, wh["end-date"]),
                    )
                else:
                    continue
                # what happens if user is included in a list of booked-users
                #  is not considered.
                params = {
                    "booked-users": user,
                    "interval[start]": str(intersection[0]),
                    "interval[end]": str(intersection[1]),
                    "interval[match]": "intersects",
                }
                response = requests.request(
                    "GET", url + "/shifts", headers=headers, params=params
                )
                booked_shifts = json.loads(response.text)
                time_diff = map(
                    lambda x: min(dt.strptime(x["end"], fmt), week_end)
                    - max(dt.strptime(x["start"], fmt), week_start),
                    booked_shifts,
                )
                # sum of iter not supported.
                accumulated = timedelta(0)
                for x in time_diff:
                    accumulated = accumulated + x
                accumulated = accumulated + shift_end - shift_start
                if accumulated > timedelta(hours=wh["fulltime-hours"]):
                    no_hrs_set.add(user)
        no_hrs_users.append(no_hrs_set)
    return no_hrs_users


def fetch_no_work_hrs(qsse, url, headers):

    logger = logging.getLogger(__name__)
    logger.debug("fetch_no_work_hrs")

    response = requests.request(
        "GET",
        url + "/employment-contracts",
        headers=headers,
        params={"archived": "null"},
    )
    contracts = json.loads(response.text)

    work_hours_data = fetch_work_hour_templates(url, headers, contracts)

    no_hrs_users = fulltime_hrs_and_work_hrs(qsse, work_hours_data, url, headers)
    return no_hrs_users
