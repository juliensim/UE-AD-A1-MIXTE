import json, requests
import os
from dotenv import load_dotenv
from graphql import GraphQLError

load_dotenv()

def check_permission(permission_required,info):
    return requests.get(os.getenv("USER_" + os.getenv("MODE")) + "check/" + permission_required,headers={'X-Token':info.context.headers.get("X-Token")}).status_code == 200

def movie_with_id(_,info,_id):
    if not(check_permission("user",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if movie['id'] == _id:
                return movie
            
def movie_by_title(_,info,_title):
    if not(check_permission("user",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)["movies"]
        for movie in movies:
            if movie['title'] == _title:
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
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies["movies"]:
            if movie["id"] == _id:
                return None
        movies["movies"].append(newmovie)
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(movies, wfile)
    return newmovie

        

def update_movie_rate(_,info,_id,_rate):
    if not(check_permission("admin",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    newmovies = {}
    newmovie = {}
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies['movies']:
            if movie['id'] == _id:
                movie['rating'] = _rate
                newmovie = movie
                newmovies = movies
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(newmovies, wfile)
    return newmovie

def delete_movie(_,info,_id):
    if not(check_permission("admin",info)):
        raise GraphQLError(
            "Insufficient permissions",
            extensions={"code": "UNAUTHORIZED"}
        )
    newmovies = {}
    delmovie = {}
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies["movies"]:
            if movie["id"] == _id:
                newmovies = movies
                newmovies["movies"].remove(movie)
                delmovie = movie
                break
    if delmovie == {}:
        return None
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(newmovies, wfile)
    return delmovie

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
    with open('{}/data/movies.json'.format("."), "r") as file:
        return json.load(file)["movies"]