#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods = ['GET', 'POST'])
def campers():
    if request.method == "GET":
        campers = []
        for camper in Camper.query.all():
            camper_dict = camper.to_dict(rules=('-signups',))
            campers.append(camper_dict)
            
        return make_response(campers, 200)
    
    if request.method == 'POST':
        try:
            new_camper = Camper(
                name=request.get_json()['name'],
                age=request.get_json()['age']
            )
            db.session.add(new_camper)
            db.session.commit()
            return make_response(new_camper.to_dict(), 201)
        except ValueError:
            return make_response({ "errors": ["validation errors"] }, 400)
    
@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def campers_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()
    
    if camper == None:
        return make_response({"error": "Camper not found"}, 404)
    
    else:
        if request.method == 'GET':
            camper_dict = camper.to_dict()
            return make_response(camper_dict, 200)
        
        elif request.method == "PATCH":
            try:
                setattr(camper, 'name', request.get_json()['name'])
                setattr(camper, 'age', request.get_json()['age'])
                db.session.add(camper)
                db.session.commit()

                return make_response(camper.to_dict(rules=('-signups',)), 202)

            except ValueError:
                return make_response({"errors": ["validation errors"]}, 400)
            
@app.route('/activities')
def activities():
    activities = []
    for activity in Activity.query.all():
        activity_dict = activity.to_dict(rules=('-signups',))
        activities.append(activity_dict)
    return make_response(activities, 200)

@app.route('/activities/<int:id>', methods=['DELETE'])
def activities_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()

    if activity == None:
        return make_response({"error": "Activity not found"}, 404)
    
    else:
        if request.method == 'DELETE':
            db.session.delete(activity)
            db.session.commit()
            return make_response({}, 204)
        
@app.route('/signups', methods=['POST'])
def signups():
    try:
        new_signup = Signup(
            camper_id = request.get_json()['camper_id'],
            activity_id = request.get_json()['activity_id'],
            time = request.get_json()['time']
        )
        db.session.add(new_signup)
        db.session.commit()
        return make_response(new_signup.to_dict(), 201)
    
    except ValueError:
        return make_response({"errors": ["validation errors"]}, 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
