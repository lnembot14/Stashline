from flask import Flask
from config import Config
from models import exstensions

app = Flask(__name__)
app.config.from_object(Config)

exstensions.db.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)