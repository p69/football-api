import requests

from utils.datetime import timestampToDateWithTime
from .requests_header import headers
from sofascore.leagues import FootballLeague
from flask_restx import fields

_next_url_template = "https://sofascores.p.rapidapi.com/v1/seasons/events?course_events=next&unique_tournament_id={}&seasons_id={}&page=0"

def getUpcomingMatches(league:FootballLeague):
  print(f"Getting upcoming matches for {league}")
  web_url = _next_url_template.format(league.id, league.latestSeason)
  response = requests.get(web_url, headers=headers)
  json = response.json()
  matches = []
  for event in json['data']['events']:
    match = {
      'id': event['id'],
      'round': event['roundInfo']['round'],
      'date': timestampToDateWithTime(event['startTimestamp']),
      'homeTeam': event['homeTeam']['name'],
      'awayTeam': event['awayTeam']['name']
    }
    matches.append(match)
  return matches

def get_upcoming_match_model(api):
   return api.model('UpcmoingMatch', {
      'id': fields.Integer(readonly=True, description='Match id'),
      'round': fields.Integer(readonly=True, description='Number of the round'),
      'date': fields.String(required=True, description='Date of the match'),
      'homeTeam': fields.String(required=True, description='Name of the home team'),
      'awayTeam': fields.String(required=True, description='Name of the away team'),
   })