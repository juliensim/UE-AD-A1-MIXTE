import grpc
from concurrent import futures
import schedule_pb2
import schedule_pb2_grpc
import json

class ScheduleServicer(schedule_pb2_grpc.ScheduleServicer):

    def __init__(self):
        with open('{}/data/times.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["schedule"]

    def GetMoviesByDate(self, request, context):
        moviesid = []
        for date in self.db:
            if date['date'] == request.date:
                for movieid in date["movies"]:
                    moviesid.append(schedule_pb2.MovieID(id=movieid))
        return schedule_pb2.MoviesID(moviesid=moviesid)
    
    def GetDatesForMovie(self, request, context):
        dates = []
        for date in self.db:
            for movie in date["movies"]:
                if movie == request.id:
                    dates.append(schedule_pb2.Date(date=date["date"]))
        return schedule_pb2.Dates(dates=dates)
    
    def AddSchedule(self, request, context):
        for date in self.db:
            if date["date"] == request.date:
                for newmovie in request.movies:
                    date["movies"].append(newmovie)
                    return request
        self.db.append({"date":request.date, "movies":request.movies})
        return request
    
    def DeleteSchedule(self, request, context):
        for date in self.db:
            if date["date"] == request.date:
                for movie in date["movies"]:
                    for deleting_movie in request.movies:
                        if movie == deleting_movie:
                            date["movies"].remove(movie)
                            if len(date["movies"]) == 0:
                                self.db.remove(date)
        return request

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    schedule_pb2_grpc.add_ScheduleServicer_to_server(ScheduleServicer(), server)
    server.add_insecure_port('[::]:3002')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
