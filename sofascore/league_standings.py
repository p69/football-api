import requests

from .requests_header import headers
from sofascore.leagues import FootballLeague
from flask_restx import fields

_standings_url_format = "https://sofascores.p.rapidapi.com/v1/seasons/standings?standing_type=total&unique_tournament_id={}&seasons_id={}"

def getLeagueStandings(league:FootballLeague):
  print(f"Getting standings for {league}")
  web_url = _standings_url_format.format(league.id, league.latestSeason)
  response = requests.get(web_url, headers=headers)
  json = response.json()
  # Extract the relevant data
  standings = []
  
  for row in json['data'][0]['rows']:
     team = row['team']['name']
     standing = {
        'team': team,
        'position': row['position'],
        'matches': row['matches'],
        'wins': row['wins'],
        'draws': row['draws'],
        'losses': row['losses'],
        'scoresFor': row['scoresFor'],
        'scoresAgainst': row['scoresAgainst'],
        'points': row['points']
     }
     if 'promotion' in row:
        standing['promotion'] = row['promotion']['text']
     standings.append(standing)     

  return standings

_standing_team_model = None

def get_standings_team_model(api):
   global _standing_team_model
   if _standing_team_model != None:
      return _standing_team_model
   
   _standing_team_model = api.model('StandingTeam', {
      'team': fields.String(readonly=True, description='Team name'),
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

   return _standing_team_model