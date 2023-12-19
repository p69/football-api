from dotenv import load_dotenv
load_dotenv()
from sofascore.leagues import FootballLeague
from sofascore.next_matches import getUpcomingMatches, get_upcoming_match_model
from flask import Flask, request
from flask_restx import Api, Namespace, fields, reqparse
from flask_restx import Resource
from sofascore.match_info import getMatchInfo, get_match_info_api_model
from sofascore.match_odds import get_odds_api_model, getMatchOdds
from sofascore.sofascore_news import get_sofascore_news_model, getLatestNewsForTeam
from sofascore.team_players_stats import fetchTeamPlayerStats, get_team_players_api_model
from flask_caching import Cache
from sofascore.league_standings import get_standings_team_model, getLeagueStandings

app = Flask(__name__)

# Configure Cache
app.config['CACHE_TYPE'] = 'simple'  # You can choose different backends like Redis, Memcached
cache = Cache(app)

parser = reqparse.RequestParser()
parser.add_argument('team', type=str, required=False, help='Team name for filtering news')
parser.add_argument('page', type=int, required=False, default=1, help='Page number')
parser.add_argument('page_size', type=int, required=False, default=10, help='Number of items per page')

api = Api(app, version='1.0', title='My simple football API', description='Get upcoming matches, match details, odds and news')

match_ns = Namespace('match', description='Match related operations')
league_ns = Namespace('league', description='Leagues related operations')
teams_ns = Namespace('team', description='Information about teams. Stats and more')

api.add_namespace(match_ns, path='/match')
api.add_namespace(league_ns, path='/league')
api.add_namespace(teams_ns, path='/team')




odds_model = get_odds_api_model(api)
match_model = get_match_info_api_model(api)
team_players_model = get_team_players_api_model(api)
standing_team_model = get_standings_team_model(api)
upcoming_match_model = get_upcoming_match_model(api)
team_news_model = get_sofascore_news_model(api)

allowed_league_names = [league.name.lower() for league in FootballLeague]

@match_ns.route('/<int:id>')
@match_ns.param('id', 'The match identifier')
class MatchInfo(Resource):
    @match_ns.doc('Get match info')
    @match_ns.marshal_with(match_model)
    def get(self, id):
        match_info_json = getMatchInfo(id)
        return match_info_json

@match_ns.route('/odds/<int:id>')
class MatchOdds(Resource):
    @match_ns.doc('Get match odds')
    @match_ns.marshal_with(odds_model, as_list=True)
    def get(self, id):
        match_odds_json = getMatchOdds(id)
        return match_odds_json

@league_ns.route('/<string:league_name>/upcoming')
class UpcomingMatches(Resource):
    @league_ns.doc(params={'league_name': {'description': 'Name of the football league',
                                           'enum': allowed_league_names,
                                           'required': True}})
    @league_ns.marshal_with(upcoming_match_model, as_list=True)
    def get(self, league_name):
        league = FootballLeague.from_string(league_name.upper())
        if league is None:
            api.abort(400, "Bad Request")
        result = getUpcomingMatches(league)
        return result
    
@league_ns.route('/<string:league_name>/standings')
class LeagueStandings(Resource):
    @league_ns.doc(params={'league_name': {'description': 'Name of the football league',
                                           'enum': allowed_league_names,
                                           'required': True}})
    @league_ns.marshal_with(standing_team_model, as_list=True)
    def get(self, league_name):
        league = FootballLeague.from_string(league_name.upper())
        if league is None:
            api.abort(400, "Bad Request")
        result = getLeagueStandings(league)
        return result
    

@teams_ns.route('/<int:id>/news')
@teams_ns.param('id', 'The team identifier')
class TeamNews(Resource):
    @teams_ns.doc('Get latest news for the team')    
    @teams_ns.marshal_with(team_news_model)
    def get(self, id):
        full_json = getLatestNewsForTeam(id)
        return full_json
    

@teams_ns.route('/<int:id>/players_stats')
@teams_ns.param('id', 'The team identifier')
class TeamPlayersInfo(Resource):
    @match_ns.doc('Get team players info')
    @match_ns.marshal_with(team_players_model)
    def get(self, id):
        players_stats_json = fetchTeamPlayerStats(id)
        return players_stats_json
