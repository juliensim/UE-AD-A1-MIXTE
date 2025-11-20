from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from flask import Flask, request, jsonify, make_response

import resolvers as r
import requests
import os
from dotenv import load_dotenv

load_dotenv()

PORT = 3002
HOST = '0.0.0.0'
app = Flask(__name__)

# todo create elements for Ariadne
type_defs = load_schema_from_path('booking.graphql')
query = QueryType()
booking = ObjectType('Booking')
bookingDetails = ObjectType('BookingDetails')
bookings = ObjectType('[Booking]')
query.set_field('booking_by_userid', r.booking_by_userid)
query.set_field('all_bookings', r.all_bookings)
query.set_field('booking_details', r.booking_details)

mutation = MutationType()
mutation.set_field('add_booking', r.add_booking)
mutation.set_field('delete_booking', r.delete_booking)

schema = make_executable_schema(type_defs, booking, query, mutation)

@app.before_request
def authentification():
    if requests.get(os.getenv("USER_" + os.getenv("MODE")) + "auth",headers={'X-Token':request.headers.get("X-Token")}).status_code != 200:
        return make_response(jsonify({"error": "Unknown user"}), 401)
    return

# root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Booking service!</h1>",200)

# graphql entry points
@app.route('/graphql', methods=['POST'])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)