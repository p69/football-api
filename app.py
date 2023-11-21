from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify
from sofascore.match_info import getMatchInfo

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/match/<int:id>', methods=['GET'])
def match_info(id):
    match_info_json = getMatchInfo(id)
    return jsonify(match_info_json)