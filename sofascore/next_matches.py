import requests

from utils.datetime import timestampToDateWithTime
from .requests_header import headers
from sofascore.leagues import FootballLeague

_next_url_template = "https://sofascore.p.rapidapi.com/tournaments/get-next-matches?tournamentId={}&seasonId={}&pageIndex=0"

def getUpcomingMatches(league:FootballLeague):
  print(f"Getting upcoming matches for {league}")
  web_url = _next_url_template.format(league.id, league.latestSeason)
  response = requests.get(web_url, headers=headers)
  json = response.json()
  matches = []
  for event in json['events']:
    match = {
      'id': event['id'],
      'round': event['roundInfo']['round'],
      'date': timestampToDateWithTime(event['startTimestamp']),
      'homeTeam': event['homeTeam']['name'],
      'awayTeam': event['awayTeam']['name']
    }
    matches.append(match)
  return matches
