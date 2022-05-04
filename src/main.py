"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt 
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorites, Planets, People
import requests
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('FLASK_APP_KEY')
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
jwt = JWTManager(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

URL_BASE= "https://www.swapi.tech/api"
@app.route('/population/planets', methods=['POST'])
def handle_population():
    response = requests.get(f"{URL_BASE}/planets/?page=2&limit=3")
    response = response.json()
    all_results = []

    for result in response['results']:
        detail = requests.get(result['url'])
        detail = detail.json()
        all_results.append(detail['result']['properties'])

    instances = []

    for planet in all_results:
        instance = Planets.create(planet)
        instances.append(instance)

    return jsonify(list(map(lambda inst: inst.serialize(), instances))), 200

@app.route('/test')
def handle_test():
    nature = ["people", "planets"]
    url_base = "https://www.swapi.tech/api/"
    pl= "/?page=2&limit=100"
    payload = ""
    payload_list = ""
    planets = []
    people = []
    for each in nature:
        try:
            response = requests.request("GET", url_base + each + pl, data=payload)
            data = response.json()
            lists = ["results"]
            for i in lists:
                request_specific = requests.request("GET", i["url"])
                print(planets)
                if(each == "planets"):
                    planets.append(request_specific.json())
                else:
                    people.append(request_specific.json())

        except Exception:
            print("There was a problem on url_base + each + pl")
    # for each in nature:
    #     try:
    #         response = requests.request("GET", url_base + each + pl, data=payload)
    #         data = response.json()
    #         for i in data:
    #             print(i["results"])
    #     except Exception:
    #         print("There was a problem on url_base + each + pl")
       
    #     if response.ok:
    #         print("is ok")

    #response = requests.request("GET", url, data=payload)


    return response.json() , 200

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/register', methods=['POST'])
def register_user():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if email is None and password is None:
        return jsonify({"msg": "You need to add both email and password"}), 400
    
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"msg": "This email is already registered"}), 401
    else:
        return jsonify({"msg": "Account created"}), 200

@app.route('/login', methods=['POST']) 
def login():
    user = request.json.get("email", None)
    password = request.json.get("password", None)

    if user is None and password is None:
        return jsonify({"msg": "Missing credentials"}), 400

    user = User.query.filter_by(user=user, password=password).first()
    if user is None:
        return jsonify({"msg": "Invalid username or password"}), 401
    else:
        user_token = create_access_token(identity=user.id)
        return jsonify({"token": user_token})

@app.route('/users/favorites', methods=['GET'])
@jwt_required()
def get_user_favorites():
    user_id = get_jwt_identity()
    favs = Favorites.query.filter_by(User_id=user_id)
    results = list(map(lambda favorites: favorites.serialize(), favs))
    results2 = []
    
    for result in results:
        if result.get("planets_id") == None:
            search_people = People.query.get(result.get("people_id"))
            result["name"] = search_people.serialize().get("name")
            add_results.append(result)
        else: 
            search_planets = Planets.query.get(result.get("planets_id"))
            result["name"] = search_planet.serialize().get("name")
            add_results.append(result)

    response_body = {
        "msg": add_results
    }
    
    return jsonify(response_body), 200

@app.route('/users/<int:user_id>/favorites', methods=['POST'])
def add_favorito(user_id):

    rq = request.get_json()
    favs = Favorites(User_id = user_id, planets_id = rq["planets_id"], people_id = rq["people_id"])
    db.session.add(favs)
    db.session.commit()

    return jsonify("ok"), 200

@app.route('/favorite/<int:favorite_id>', methods=['DELETE'])
def delete_favorito(favorite_id):

    delete_fav = Favorites.query.get(favorite_id)
    if delete_fav is None:
        return jsonify({"msg": "No favs"}), 401
    db.session.delete(delete_fav)
    db.session.commit()

    return jsonify("ok"), 200

@app.route('/people', methods=['GET'])
def get_people():

    people = People.query.all()
    results = list(map(lambda People: People.serialize(), people))

    response_body = {
        "msg": results
    }
    return jsonify(response_body), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_id(people_id):

    people = People.query.get(people_id)
    results = people.serialize()
    response_body = {
        "msg": results
    }
    return jsonify(response_body), 200

@app.route('/planets', methods=['GET'])
def get_planets():

    planets = Planets.query.all()
    results = list(map(lambda planets: planets.serialize(), planets))

    response_body = {
        "msg": results
    }
    return jsonify(response_body), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planets_id(planet_id):

    planets = Planets.query.get(planet_id)
    results = planets.serialize()
    response_body = {
        "msg": results
    }
    return jsonify(response_body), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
