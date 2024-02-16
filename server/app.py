import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, make_response, render_template
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Bird

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__,
            static_url_path='',
            static_folder='../client/build',
            template_folder='../client/build')

# Define routes
@app.route('/')
@app.route('/<int:id>')
def index(id=0):
    return render_template("index.html")

# Configure SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json_compact = False

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Error handler for 404 Not Found
@app.errorhandler(404)
def not_found(e):
    return render_template("index.html")

# Initialize Flask-Restful API
api = Api(app)

# Define API resources
class Birds(Resource):
    def get(self):
        birds = [bird.to_dict() for bird in Bird.query.all()]
        return make_response(jsonify(birds), 200)

    def post(self):
        data = request.get_json()
        new_bird = Bird(
            name=data['name'],
            species=data['species'],
            image=data['image'],
        )
        db.session.add(new_bird)
        db.session.commit()
        return make_response(new_bird.to_dict(), 201)

api.add_resource(Birds, '/birds')

class BirdByID(Resource):
    def get(self, id):
        bird = Bird.query.get_or_404(id)
        return make_response(jsonify(bird.to_dict()), 200)

    def patch(self, id):
        data = request.get_json()
        bird = Bird.query.get_or_404(id)
        for attr, value in data.items():
            setattr(bird, attr, value)
        db.session.commit()
        return make_response(jsonify(bird.to_dict()), 200)

    def delete(self, id):
        bird = Bird.query.get_or_404(id)
        db.session.delete(bird)
        db.session.commit()
        return make_response('', 204)

api.add_resource(BirdByID, '/birds/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
