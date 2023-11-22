from dotenv import load_dotenv
load_dotenv()
from sofascore.leagues import FootballLeague
from sofascore.next_matches import getUpcomingMatches
from flask import Flask, jsonify
from sofascore.match_info import getMatchInfo
from sofascore.match_odds import getMatchOdds
from sofascore.livescore_news import getLatestNews

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/match/<int:id>', methods=['GET'])
def match_info(id):
    match_info_json = getMatchInfo(id)
    return jsonify(match_info_json)

@app.route('/match_odds/<int:id>', methods=['GET'])
def match_odds(id):
    match_odds_json = getMatchOdds(id)
    return jsonify(match_odds_json)

@app.route('/<string:league_name>/upcoming', methods=['GET'])
def upcoming_matches(league_name):
    league = FootballLeague.from_string(league_name.upper())
    if league == None:
        return "Bad Request", 400
    result = getUpcomingMatches(league)
    return jsonify(result)

@app.route('/<string:league_name>/news', methods=['GET'])
def news(league_name):
    league = FootballLeague.from_string(league_name.upper())
    if league == None:
        return "Bad Request", 400
    result = getLatestNews(league)
    return jsonify(result)