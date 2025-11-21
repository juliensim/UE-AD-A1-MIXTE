import json, requests
import os
from dotenv import load_dotenv
from graphql import GraphQLError
from pymongo import MongoClient
from flask import Flask, request
import schedule_pb2_grpc,schedule_pb2
import grpc

load_dotenv()

bookings = None

def Initialisation():
    global bookings

    client = MongoClient(os.getenv("MONGO_" + os.getenv("MODE")))
    
    # Init bookings
    with open('{}/data/bookings.json'.format("."), "r") as jsf:
        movies_json = json.load(jsf).get("bookings", [])

    db_bookings = client["bookings"]
    collection_bookings = db_bookings["bookings"]
    
    if list(collection_bookings.find()) == [] :
        collection_bookings.insert_many(movies_json)
    bookings = collection_bookings

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
    if not(check_permission("user",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
          
    booking = bookings.find_one({"userid": _new_booking["new_userid"]})
    if booking:
            raise GraphQLError(
            "booking ID already exists"
            )
    
    channel = grpc.insecure_channel(os.getenv("SCHEDULE_" + os.getenv("MODE")))
    stub = schedule_pb2_grpc.ScheduleStub(channel)
    metadata = [('x-token',info.context.headers.get("X-Token"))]

    for date in _new_booking["new_dates"]:

        schedule = stub.GetMoviesByDate(
            schedule_pb2.Date(date=date["new_date"]),
            metadata=metadata
        )
        if not schedule.moviesid:
            raise GraphQLError(
                "No movies scheduled for the date"
            )
        for movie in date["new_movies"]:
            present = False
            for schedule_movie in schedule.moviesid:
                if schedule_movie.id == movie:
                    present = True
            if not(present):
                raise GraphQLError(
                    "One of the movies is not scheduled for the date"
                )
    channel.close()

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
    if not(check_permission("user",info)):
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
    
def call_movie_service(movie_id, token):
    query = """
    query MovieQuery($id: String!) {
        movie_with_id(_id: $id) {
            title
            rating
            director
        }
    }
    """
    payload = {
        "query": query,
        "variables": {"id": movie_id},
        "operationName": "MovieQuery"
    }
    resp = requests.post(
        os.getenv("MOVIE_" + os.getenv("MODE")),
        json=payload,
        headers={
            "Content-Type": "application/json",
            "X-Token": token
        }
    )
    
    # Si erreur réseau ou réponse vide :
    if resp.status_code != 200:
        print("ERROR calling MOVIE service:", resp.status_code, resp.text)
        return None

    data = resp.json()

    if "data" not in data or data["data"]["movie_with_id"] is None:
        print("Movie not found:", movie_id)
        return None
    
    return data["data"]["movie_with_id"]

def booking_details(_,info,_userid):
    if not(check_permission("user",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    token = info.context.headers.get("X-Token")

    # tous les bookings de l'utilisateur
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

                movie = call_movie_service(movieid, token)
                if not movie:
                    continue
                movies_list.append(movie)
    booking_details_res = {"userid": _userid, "movies": movies_list}
    return booking_details_res