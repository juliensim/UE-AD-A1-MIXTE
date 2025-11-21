import json, requests
import os
from dotenv import load_dotenv
from graphql import GraphQLError
from pymongo import MongoClient

load_dotenv()

movies = None
actors = None
bookings = None

def Initialisation():
    global movies, actors, bookings

    client = MongoClient(os.getenv("MONGO_" + os.getenv("MODE")))
    
    # Init bookings
    with open('{}/data/bookings.json'.format("."), "r") as jsf:
        movies_json = json.load(jsf).get("bookings", [])

    db_bookings = client["bookings"]
    collection_bookings = db_bookings["bookings"]
    
    if list(collection_bookings.find()) == [] :
        collection_bookings.insert_many(movies_json)
    bookings = collection_bookings

    # Init movies
    with open('{}/../movie/data/movies.json'.format("."), "r") as jsf:
        movies_json = json.load(jsf).get("movies", [])

    db_movie = client["movies"]
    collection_movie = db_movie["movies"]
    if list(collection_movie.find()) == [] :
        collection_movie.insert_many(movies_json)
    movies = collection_movie
    
    # Init actors
    with open('{}/../movie/data/actors.json'.format("."), "r") as jsf:
        actors_json = json.load(jsf).get("actors", [])
    db_movie = client["actors"]
    collection_movie = db_movie["actors"]
    if list(collection_movie.find()) == [] :
        collection_movie.insert_many(actors_json)
    actors = collection_movie

Initialisation()

def check_permission(permission_required,info):
    return requests.get(os.getenv("USER_" + os.getenv("MODE")) + "check/" + permission_required,headers={'X-Token':info.context.headers.get("X-Token")}).status_code == 200

def booking_by_userid(_,info,_userid):
    if not(check_permission("user",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    booking = bookings.find_one({"userid": _userid},{"_id":0})
    return booking


def add_booking(_,info,_userid,_new_booking):
    if not(check_permission("admin",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    newbooking = {
        "userid": _new_booking["new_userid"],
        "dates": [
            {
                "date": d["new_date"],
                "movies": d["new_movies"]
            } for d in _new_booking["new_dates"]
        ]
    }

    result = bookings.insert_one(newbooking)
    inserted_booking = bookings.find_one({"_id": result.inserted_id}, {"_id": 0})
    return inserted_booking

def delete_booking(_,info,_userid):
    if not(check_permission("admin",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    result = bookings.delete_many({"userid": _userid})
    return f"{_userid} - deleted {result.deleted_count} bookings"

def all_bookings(_,info):
    if not(check_permission("admin",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    res = bookings.find({}, {"_id": 0})
    return res
    
def booking_details(_,info,_userid):
    if not(check_permission("user",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    user_bookings = list(bookings.find({"userid": _userid}, {"_id": 0}))

    if not user_bookings:
        raise GraphQLError(
            f"No bookings found for user {_userid}",
            extensions={"code": "NOT_FOUND"}
        )

    movies_list = []
    movie_ids = set()
    for booking in user_bookings:
        for date in booking.get("dates", []):
            for movieid in date.get("movies", []):
                if movieid in movie_ids:
                    continue
                movie_ids.add(movieid)

                movie = movies.find_one({"id": movieid}, {"_id": 0})
                if not movie:
                    continue

                enriched_actors = list(actors.find({"films": movie.get("id")}, {"_id": 0}))
                if not enriched_actors:
                    actor_ids = movie.get("actors") or []
                    if actor_ids:
                        enriched_actors = list(actors.find({"id": {"$in": actor_ids}}, {"_id": 0}))

                movie["actors"] = enriched_actors
                movies_list.append(movie)
    booking_details_res = {"userid": _userid, "movies": movies_list}
    return booking_details_res