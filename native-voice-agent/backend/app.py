# Updated CORS Allowed Origins

from flask_cors import CORS  
from flask import Flask  

app = Flask(__name__)

# Explicitly define allowed origins for CORS
CORS(app, resources={"/*": {"origins": ["http://localhost:3000", "http://localhost:5000"]}})  

# Other configurations and routes
@app.route('/')  
def index():  
    return "Hello World!"  

if __name__ == '__main__':  
    app.run()