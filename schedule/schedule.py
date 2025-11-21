import grpc
from concurrent import futures
import schedule_pb2
import schedule_pb2_grpc
import json
import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

class ScheduleServicer(schedule_pb2_grpc.ScheduleServicer):

    def __init__(self):
        client = MongoClient(os.getenv("MONGO_" + os.getenv("MODE")))
        db = client["schedules"]
        self.schedules = db["schedules"]
        with open('{}/data/times.json'.format("."), "r") as jsf:
            self.schedules_json = json.load(jsf)["schedule"]
        
        if list(self.schedules.find()) == [] :
            self.schedules.insert_many(self.schedules_json)


    def authentification(self,context):
        return requests.get(os.getenv("USER_" + os.getenv("MODE")) + "auth",headers={'X-Token':dict(context.invocation_metadata()).get("x-token")}).status_code == 200

    def check_permission(self,permission_required,context):
        return requests.get(os.getenv("USER_" + os.getenv("MODE")) + "check/" + permission_required,headers={'X-Token':dict(context.invocation_metadata()).get("x-token")}).status_code == 200

    def GetMoviesByDate(self, request, context):
        if not(self.authentification(context)):
            context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Authentifation token missing or incorrect"
            )
        if not(self.check_permission("user",context)):
            context.abort(
                grpc.StatusCode.PERMISSION_DENIED,
                "Insufficient permissions"
            )
        moviesid = []

        schedule_docs = list(
            self.schedules.find(
                {"date": request.date},
                {"movies": 1, "_id": 0}
            )
        )
        for doc in schedule_docs:
            for movie_id in doc.get("movies", []):
                moviesid.append(schedule_pb2.MovieID(id=movie_id))

        return schedule_pb2.MoviesID(moviesid=moviesid)
    
    def GetDatesForMovie(self, request, context):
        if not(self.authentification(context)):
            context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Authentifation token missing or incorrect"
            )
        if not(self.check_permission("user",context)):
            context.abort(
                grpc.StatusCode.PERMISSION_DENIED,
                "Insufficient permissions"
            )
        dates = []
        schedule_docs = self.schedules.find(
            {"movies": request.id},
            {"date": 1, "_id": 0}
        )
        for doc in schedule_docs:
            dates.append(schedule_pb2.Date(date=doc["date"]))
        return schedule_pb2.Dates(dates=dates)
    
    def AddSchedule(self, request, context):
        if not(self.authentification(context)):
            context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Authentifation token missing or incorrect"
            )
        if not(self.check_permission("admin",context)):
            context.abort(
                grpc.StatusCode.PERMISSION_DENIED,
                "Insufficient permissions"
            )
        result = self.schedules.update_one(
            {"date": request.date},
            {"$addToSet": {"movies": {"$each": list(request.movies)}}}
        )
        if result.matched_count == 0:
            self.schedules.insert_one({
                "date": request.date,
                "movies": list(request.movies)
            })
        return request
    
    def DeleteSchedule(self, request, context):
        if not(self.authentification(context)):
            context.abort(
                grpc.StatusCode.UNAUTHENTICATED,
                "Authentifation token missing or incorrect"
            )
        if not(self.check_permission("admin",context)):
            context.abort(
                grpc.StatusCode.PERMISSION_DENIED,
                "Insufficient permissions"
            )
        self.schedules.update_one(
            {"date": request.date},
            {"$pull": {"movies": {"$in": list(request.movies)}}}
        )
        self.schedules.delete_many(
            {"date": request.date, "movies": {"$size": 0}}
        )
        return request

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    schedule_pb2_grpc.add_ScheduleServicer_to_server(ScheduleServicer(), server)
    server.add_insecure_port('[::]:3003')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
