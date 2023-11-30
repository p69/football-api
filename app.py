from dotenv import load_dotenv
load_dotenv()
from sofascore.leagues import FootballLeague
from sofascore.next_matches import getUpcomingMatches
from flask import Flask, request
from flask_restx import Api, Namespace, fields, reqparse
from flask_restx import Resource
from sofascore.match_info import getMatchInfo
from sofascore.match_odds import get_odds_api_model, getMatchOdds
from sofascore.livescore_news import getLatestNews
from sofascore.espn_news import getLatestESPNNews
from flask_caching import Cache

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
api.add_namespace(match_ns, path='/match')
api.add_namespace(league_ns, path='/league')


standing_team_model = api.model('StandingTeam', {
    'name': fields.String(readonly=True, description='Team name'),
    'position': fields.Integer(required=True, description='Team position in the table'),
    'matches': fields.Integer(required=True, description='Total matches played'),
    'wins': fields.Integer(required=True, description='Total wins'),
    'draws': fields.Integer(required=True, description='Total draws'),
    'losses': fields.Integer(required=True, description='Total losses'),
    'scoresFor': fields.Integer(required=True, description='Total goals scored'),
    'scoresAgainst': fields.Integer(required=True, description='Total goals conceded'),
    'points': fields.Integer(required=True, description='Total points'),
    'promotion': fields.String(readonly=True, optional=True, description='Promotion or resegnation if the season is over')
})

team_model = api.model('Team', {
    'id': fields.Integer(readonly=True, description='The team identifier'),
    'name': fields.String(required=True, description='Full team name'),
    'manager': fields.String(required=True, description='Name of the manager'),
    'lineup': fields.String(required=True, description='Lineup for current match. Will be "Not Available" if its not available yet'),
    'form': fields.String(required=True, description='Latets results for current team across all tournaments')
})

match_model = api.model('Match', {
    'id': fields.Integer(readonly=True, description='The match identifier'),
    'date': fields.String(required=True, description='Match start date in format "YYYY-MM-DD"'),
    'match_name': fields.String(required=True, description='Match name'),
    'home_team': fields.Nested(team_model, required=True, description="Information about home team"),
    'away_team': fields.Nested(team_model, required=True, description="Information about away team"),
    'h2h_results': fields.String(required=True, description='Head to Head results for current teams across all tournaments'),
    'standings': fields.List(fields.Nested(standing_team_model), required=True, description='Teams standing in the league')
})

odds_model = get_odds_api_model(api)

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
    @match_ns.marshal_with(odds_model)
    def get(self, id):
        match_odds_json = getMatchOdds(id)
        return match_odds_json

@league_ns.route('/<string:league_name>/upcoming')
class UpcomingMatches(Resource):
    @league_ns.doc(params={'league_name': {'description': 'Name of the football league',
                                           'enum': allowed_league_names,
                                           'required': True}})
    def get(self, league_name):
        league = FootballLeague.from_string(league_name.upper())
        if league is None:
            api.abort(400, "Bad Request")
        result = getUpcomingMatches(league)
        return result
    

def make_cache_key(*args, **kwargs):
    return request.path

@cache.cached(timeout=3600, key_prefix=make_cache_key)
def fetch_all_news_for_league(league:FootballLeague):
    return getLatestNews(league)


@league_ns.route('/<string:league_name>/news')
class LeagueNews(Resource):
    @league_ns.doc(params={'league_name': {'description': 'Name of the football league',
                                           'enum': allowed_league_names,
                                           'required': True}})    
    # @league_ns.expect(parser)
    def get(self, league_name):
        league = FootballLeague.from_string(league_name.upper())
        if league is None:
            api.abort(400, "Bad Request")

        full_json = getLatestESPNNews(league)
        return full_json