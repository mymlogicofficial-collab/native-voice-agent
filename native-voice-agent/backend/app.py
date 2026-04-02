# Updated CORS Allowed Origins

from flask_cors import CORS  
from flask import Flask  

app = Flask(__name__)

# FIXED CORS — allow ALL origins
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')  
def index():  
    return "Hello World!"  

if __name__ == '__main__':  
    app.run()
