import json, requests

def booking_by_userid(_,info,_userid):
    with open('{}/data/bookings.json'.format("."), "r") as file:
        bookings = json.load(file)
        for booking in bookings['bookings']:
            if booking['userid'] == _userid:
                return booking

def add_booking(_,info,_userid,_new_booking):
    newbooking = {}
    newbookings = {}
    with open('{}/data/bookings.json'.format("."), "r") as rfile:
        bookings = json.load(rfile)
        newbooking["userid"] = _new_booking["new_userid"]
        newbooking["dates"] = [{} for i in range(len(_new_booking['new_dates']))]
        for i in range(len(_new_booking['new_dates'])):
            newbooking["dates"][i]["date"] = _new_booking["new_dates"][i]["new_date"]
            newbooking["dates"][i]["movies"] = _new_booking["new_dates"][i]["new_movies"]
        newbookings = bookings
        newbookings["bookings"].append(newbooking)
    with open('{}/data/bookings.json'.format("."), "w") as wfile:
        json.dump(newbookings, wfile)
    return newbooking

def delete_booking(_,info,_userid):
    newbookings = {"bookings":[]}
    with open('{}/data/bookings.json'.format("."), "r") as rfile:
        bookings = json.load(rfile)
        for booking in bookings['bookings']:
            if booking['userid'] != _userid:
                newbookings['bookings'].append(booking)
    with open('{}/data/bookings.json'.format("."), "w") as wfile:
        json.dump(newbookings, wfile)
    return _userid

def all_bookings(_,info):
    with open('{}/data/bookings.json'.format("."), "r") as file:
        return json.load(file)["bookings"]
    
def booking_details(_,info,_userid):
    with open('{}/data/bookings.json'.format("."), "r") as file:
        bookings = json.load(file)
        full_res = []
        for booking in bookings['bookings']:
            if booking['userid'] == _userid:
                pre_res = {}
                pre_res["userid"] = booking["userid"]
                pre_res["movies"] = []
                for date in booking["dates"]:
                    for movieid in date["movies"]:
                        movie = requests.post("http://localhost:3001/graphql",json={'query': '{movie_with_id(_id:"96798c08-d19b-4986-a05d-7da856efb697") {title director rating actors{firstname lastname birthyear	films}}}'}).json()
                        pre_res["movies"].append(movie["data"]["movie_with_id"])
                full_res.append(pre_res)
        return pre_res
            
