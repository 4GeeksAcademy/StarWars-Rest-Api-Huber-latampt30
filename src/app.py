"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def get_people():

    characters = People.query.all()
    all_characters = list(map(lambda x: x.serialize(), characters))

    return jsonify(all_characters), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_single_character(people_id):

    single_character = People.query.get(people_id)
    if single_character is None:
        return jsonify({"Message": "Error, character no encontrado"}), 404
    return jsonify(single_character), 200

@app.route('/planets', methods=['GET'])
def get_planets():

    planets = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets))

    return jsonify(all_planets), 200

@app.route('/planets/<int:people_id>', methods=['GET'])
def get_single_planet(planet_id):

    single_planet = Planet.query.get(planet_id)
    if single_planet is None:
        return jsonify({"Message": "Error, planeta no encontrado"}), 404
    return jsonify(single_planet), 200


@app.route('/users/favorite', methods=['GET'])
def get_user_favorites():

    user_id = request.args.get('user_id')
    user = User.query.get(user_id)

    if user is None:
        return jsonify({"Message": "No se encontro el ususario"}), 404

    favorites = Favorite.query.filter_by(user_id=user_id).all()

    all_favorites = []
    for favorite in favorites:
        all_favorites.append({
            "id": favorite.id,
            "people": People.query.get(favorite.people_id).serialize(),
            "planet": Planet.query.get(favorite.planet_id).serialize()
        })

    return jsonify(all_favorites), 200


@app.route('/favorites/people/<int:people_id>', methods=['POST'])
def add_character_favorite(people_id):

    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    character = People.query.get(people_id)

    if user is None:
        return jsonify({"Message": "No se encontro el usuario"}), 404

    if character is None:
        return jsonify({"Message": "No se encontro el caracter"}), 404

    new_favorite = Favorite(user_id=user_id, planet_id=people_id)

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({"Message": "Se agrego caracter favorito"}, new_favorite), 201

@app.route('/favorites/people/<int:people_id>', methods=['DELETE'])
def delete_character_favorite(people_id):

    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    character = People.query.get(people_id)

    if user is None:
        return jsonify({"Message": "No se encontro el usuario"}), 404

    if character is None:
        return jsonify({"Message": "No se encontro el caracter"}), 404

    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=people_id).first()

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"Message": "Se elimino caracter"}, favorite), 200


@app.route('/favorites/planets/<int:planet_id>', methods=['POST'])
def add_planet_favorite(planet_id):

    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)

    if user is None:
        return jsonify({"Message": "No se encontro el usuario"}), 404

    if planet is None:
        return jsonify({"Message": "No se encontro el planeta"}), 404

    new_favorite = Favorite(user_id=user_id, planet_id=planet_id)

    db.session.add(new_favorite)
    db.session.commit()

    return jsonify(new_favorite), 201

@app.route('/favorites/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet_favorite(planet_id):

    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)

    if user is None:
        return jsonify({"Message": "No se encontro el usuario"}), 404

    if planet is None:
        return jsonify({"Message": "No se encontro el planeta"}), 404

    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"Message": "Se elimino planeta"}, favorite), 200


@app.route('/user', methods=['GET'])
def get_users():

    users = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users))

    return jsonify(all_users), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
