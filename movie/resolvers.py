import json, requests
import os
from dotenv import load_dotenv
from graphql import GraphQLError
from flask import Flask, render_template, request, jsonify, make_response, g
from pymongo import MongoClient


load_dotenv()

def check_permission(permission_required,info):
    return requests.get(os.getenv("USER_" + os.getenv("MODE")) + "check/" + permission_required,headers={'X-Token':info.context.headers.get("X-Token")}).status_code == 200

def Initialisation():
    with open('{}/data/movies.json'.format("."), "r") as jsf:
        movies_json = json.load(jsf).get("movies", [])

    #client = MongoClient("mongodb://username:password@127.0.0.1:3000/") #version locale
    client = MongoClient("mongodb://username:password@mongo:27017/") 
    db = client["movies"]
    collection = db["movies"]
    
    if list(collection.find()) == [] :
        collection.insert_many(movies_json)
    return collection

movies = Initialisation()

def movie_with_id(_,info,_id):
    if not(check_permission("user",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    movie = movies.find_one({"id": _id},{"_id":0,"access_token":0})
    return movie
            
def movie_by_title(_,info,_title):
    if not(check_permission("user",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    movie = movies.find_one({"title": _title},{"_id":0,"access_token":0})
    return movie
            
def add_movie(_,info,_id,_title,_rate,_director):
    if not(check_permission("admin",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
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
    if not(check_permission("admin",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    myquery = { "id": _id }
    newvalues = { "$set": { "rating": float(_rate) } }
    res = movies.update_one(myquery, newvalues)

    if res.matched_count == 0:
        return None 
    else:
        updated_movie = movies.find_one({"id": _id}, {"_id": 0})
        return updated_movie
def delete_movie(_,info,_id):
    if not(check_permission("admin",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
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
    if not(check_permission("user",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    res = list(movies.find({}, {"_id": 0}))
    return res