import requests
from .requests_header import headers
from flask_restx import fields

_odds_api_model = None
_odds_choice_model = None
_odds_market_model = None

def get_odds_api_model(api):
  global _odds_api_model
  global _odds_choice_model
  global _odds_market_model
  
  if _odds_api_model != None:
    return _odds_api_model
  
  _odds_choice_model = api.model('OddsChoice', {
    'name': fields.String(readonly=True, required=True, description='Name of the odds choice', example="X1, 1, 2, X2, +1.5"),
    'fractionalValue': fields.String(readonly=True, required=True, description='Fractional value of the choice', example="73/100")
  })

  _odds_market_model = api.model('OddsMarket', {
    'choices': fields.List(fields.Nested(_odds_choice_model), required=True, description='Available choices for current market'),
    'id': fields.Integer(required=True, description='Market unique id'),
    'marketName': fields.String(readonly=True, required=True, description='Name of the market odds', example="Full time, "),
    'marketId': fields.Integer(required=True, description='Id for market category'),
  })
  
  _odds_api_model = api.model('Odds', {
    'eventId': fields.Integer(required=True, description='Match unique id'),
    'markets': fields.List(fields.Nested(_odds_market_model), required=True, description='Available markets for current match'),
  })
  return _odds_api_model

_odds_url_template = "https://sofascore.p.rapidapi.com/matches/get-all-odds?matchId={}"

def getMatchOdds(id):
  print(f"Getting odds for match {id}")
  web_url = _odds_url_template.format(id)
  response = requests.get(web_url, headers=headers)
  return response.json()