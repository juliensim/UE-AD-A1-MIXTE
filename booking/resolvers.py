import json

def bookings_by_id(_,info,_id):
    with open('{}/data/bookings.json'.format("."), "r") as file:
        bookings = json.load(file)["bookings"]
        res = []
        for booking in bookings:
            if (booking["user_id"]) == _id:
                res.append(booking)
        return res


def all_bookings(_,info):
    with open('{}/data/bookings.json'.format("."), "r") as file:
        return json.load(file)["bookings"]