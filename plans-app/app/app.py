from flask import Flask
from database import Base, engine
from models import Event
from routes import register_routes

app = Flask(__name__)

app.json.sort_keys = False
app.json.ensure_ascii = False
app.config["SECRET_KEY"] = "super-secret-key"

Base.metadata.create_all(engine)

register_routes(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
