from flask import Flask, request
from config import Config
from routes.artist_routes import artist_route
from routes.eras_routes import eras_routes
from models.extensions import db



app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
app.register_blueprint(artist_route)
app.register_blueprint(eras_routes)


if __name__ == "__main__":
    app.run(debug=True)