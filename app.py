from flask import Flask
from config import Config
from models import extensions

app = Flask(__name__)
app.config.from_object(Config)

extensions.db.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)