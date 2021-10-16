from flask import Flask, jsonify, request
from datetime import datetime
from functools import wraps
import os

from Generators import CaptchaService

app = Flask(__name__)
start = datetime.now()

def authorized_only(f):
    @wraps(f)
    def checker(*args, **kwargs):
        token = request.headers.get('Authorization')
        key = os.environ['KEY']
        if token != key:
            return jsonify(message="You are unauthorized to use this endpoint"), 401
        return f(*args, **kwargs)
    return checker


@app.route("/")
@authorized_only
def main():
    return jsonify(message="Hello! I am running.", uptime=str((datetime.now() - start).seconds) + " seconds"), 200

"""
Data sent as 
{
  "text:": {
    "length": 5,
    "color": "#03fc3d"
  },
  "decoy:": {
    "length": 4,
    "color": "#757373"
  },
  "noise:": {
    "count": 1,
    "color": "#b5d439"
  },
  "confusables": {
    "filter": false,
    "char": []
  }
}
"""
@app.route("/generate/<img>", methods=["POST"])
@authorized_only
def gen(img):
    if(img != "captcha"):
        return jsonify(message="Invalid endpoint."), 404
    
    if not request.is_json:
        return jsonify(message='Was expecting JSON format'), 400
    try:
        body = request.get_json(force=True, silent=True) or {}
        text = body.get('text') or {}
        decoy = body.get('decoy') or {}
        confusables = body.get('confusables') or {}
        captcha = CaptchaService.Captcha(text.get('length'), decoy.get('length'), text.get('color'), decoy.get('color'), filter=confusables.get('filter'), filter_chars=confusables.get('char')).generate()
        return captcha, 200
    except Exception as error:
        return jsonify(message="Bad Request :(", error=str(error)), 400
       
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)

# Development Server
# app.run(host='0.0.0.0', port=5000, debug=True)