from flask import Flask, render_template, request, jsonify, make_response, g
import json
from pymongo import MongoClient

def Initialisation():
    with open('{}/data/movies.json'.format("."), "r") as jsf:
        movies_json = json.load(jsf).get("movies", [])

    client = MongoClient("mongodb://username:password@127.0.0.1:3000/") #version locale
    #client = MongoClient("mongodb://username:password@mongo:27017/") 
    db = client["movies"]
    collection = db["movies"]
    
    if list(collection.find()) == [] :
        collection.insert_many(movies_json)
    return collection

movies = Initialisation()
print(movies)
def movie_with_id(_,info,_id):
    movie = movies.find_one({"id": _id},{"_id":0,"access_token":0})
    return movie
            
def movie_by_title(_,info,_title):
    movie = movies.find_one({"title": _title},{"_id":0,"access_token":0})
    return movie

def add_movie(_,info,_id,_title,_rate,_director):
    newmovie = {
            "id": _id,
            "title": _title,
            "rating": _rate,
            "director": _director
    }
    existing_movie = movies.find_one({"id": _id},{"_id":0,"access_token":0})
    if existing_movie:
        return None
    movies.insert_one(newmovie)
    return newmovie



def update_movie_rate(_,info,_id,_rate):
    myquery = { "id": _id }
    newvalues = { "$set": { "rating": float(_rate) } }
    res = movies.update_one(myquery, newvalues)

    if res.matched_count == 0:
        return None 
    else:
        updated_movie = movies.find_one({"id": _id}, {"_id": 0})
        return updated_movie

def delete_movie(_,info,_id):
    deleted_movie = movies.find_one({"id": _id}, {"_id": 0})
    result = movies.delete_one({"id": _id})
    if result.deleted_count == 0:
        return None
    else:
        return deleted_movie


def resolve_actors_in_movie(movie, info):
    with open('{}/data/actors.json'.format("."), "r") as file:
        actors = json.load(file)
        result = [actor for actor in actors['actors'] if movie['id'] in actor['films']]
        return result

def all_movies(_,info):
    res = list(movies.find({}, {"_id": 0}))
    return res