from flask import Flask
from routes.api import api_bp
from flask_cors import CORS
app = Flask(__name__)
app.register_blueprint(api_bp, url_prefix="/api")
CORS(app) # Allows all origins

if __name__ == "__main__":
    app.run(debug=True)
