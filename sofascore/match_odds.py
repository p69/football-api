import requests
from .requests_header import headers

_odds_url_template = "https://sofascore.p.rapidapi.com/matches/get-all-odds?matchId={}"

def getMatchOdds(id):
  print(f"Getting odds for match {id}")
  web_url = _odds_url_template.format(id)
  response = requests.get(web_url, headers=headers)
  return response.json()