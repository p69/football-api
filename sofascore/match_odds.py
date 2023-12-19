import requests
from .requests_header import headers
from flask_restx import fields

def get_odds_api_model(api):  
  odds_choice_model = api.model('OddsChoice', {
    'name': fields.String(readonly=True, required=True, description='Name of the odds choice', example="X1, 1, 2, X2, +1.5"),
    'fractionalValue': fields.String(readonly=True, required=True, description='Fractional value of the choice', example="73/100")
  })

  return api.model('OddsMarket', {
    'choices': fields.List(fields.Nested(odds_choice_model), required=True, description='Available choices for current market'),
    'id': fields.Integer(required=True, description='Market unique id'),
    'marketName': fields.String(readonly=True, required=True, description='Name of the market odds', example="Full time, "),
    # 'choiceGroup': fields.String(readonly=True, required=False, description='Group of the market odds', example="Number of goals: 0.5, 1.5, 2 etc"),
    'marketId': fields.Integer(required=True, description='Id for market category'),
  })
  
  # return api.model('Odds', {
  #   'id': fields.Integer(required=True, description='Match unique id'),
  #   'markets': fields.List(fields.Nested(odds_market_model), required=True, description='Available markets for current match'),
  # })

_odds_url_template = "https://sofascores.p.rapidapi.com/v1/events/odds/all?event_id={}&odds_format=decimal&provider_id=1"

def getMatchOdds(id):
  print(f"Getting odds for match {id}")
  web_url = _odds_url_template.format(id)
  response = requests.get(web_url, headers=headers)
  return response.json()['data']