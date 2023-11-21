import requests
import os
# from bs4 import BeautifulSoup

from utils.datetime import timestampToDate

rapid_api_key = os.getenv('RAPIDAPI_KEY')
print(f"key = {rapid_api_key}")
_headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'X-RapidAPI-Key': rapid_api_key
}

_event_url_template = "https://sofascore.p.rapidapi.com/matches/detail?matchId={}"
_lineups_url_template = "https://sofascore.p.rapidapi.com/matches/get-lineups?matchId={}"
_standings_url_format = "https://sofascore.p.rapidapi.com/tournaments/get-standings?tournamentId={}&seasonId={}"
_team_form_url_format = "https://sofascore.p.rapidapi.com/teams/get-last-matches?teamId={}&page=0"
_h2h_events_url_format = "https://sofascore.p.rapidapi.com/matches/get-head2head?matchId={}"


def fetchTeamsAndDate(event_id):
   web_url = _event_url_template.format(event_id)
   response = requests.get(web_url, headers=_headers)
   print(response)      
   json = response.json()
   event = json['event']
   return {
      'date': timestampToDate(event['startTimestamp']),
      'home': event['homeTeam'],
      'away': event['awayTeam'],
      'season': {
         'tournament': event['tournament']['uniqueTournament']['id'],
         'id': event['season']['id']
      }
   }

def parseLineups(team):
  formation = team['formation']
  starting = ', '.join(player['player']['name'] for player in team['players'] if player['substitute'] == False)
  subs = ', '.join(player['player']['name'] for player in team['players'] if player['substitute'] == True)
  missing = ', '.join(player['player']['name'] for player in team['missingPlayers'])
  return {
     'formation': formation,
     'starting': starting,
     'substitues': subs,
     'missing': missing
  }

def fetchLineups(event_id):
   web_url = _lineups_url_template.format(event_id)
   response = requests.get(web_url, headers=_headers)
   if response.status_code != 200:
      return {
         'home': 'Not available',
         'away': 'Not available'
      }
   json = response.json()

   homeLineup = 'Not available'
   if 'home' in json:
      homeLineup = parseLineups(json['home'])
   
   awayLineup = 'Not available'
   if 'away' in json:
      awayLineup = parseLineups(json['away'])

   return {
      'home': homeLineup,
      'away': awayLineup
   }

def fetchTableStandings(season):
  web_url = _standings_url_format.format(season['tournament'], season['id'])
  response = requests.get(web_url, headers=_headers)
  json = response.json()
  # Extract the relevant data
  standings = json['standings'][0]['rows']
  return standings

def fetchForm(team):
   web_url = _team_form_url_format.format(team['id'])
   response = requests.get(web_url, headers=_headers)
   json = response.json()
   filtered_sorted_matches = sorted(
    [item for item in json['events'] if item['status']['type'] == "finished"],
    key=lambda x: x['startTimestamp'])
   
   return "; ".join(f"{timestampToDate(event['startTimestamp'])}: {event['homeTeam']['name']} {event['homeScore']['current']}-{event['awayScore']['current']} {event['awayTeam']['name']}" for event in filtered_sorted_matches)

def fetchH2HResults(matchId):
   web_url = _h2h_events_url_format.format(matchId)
   response = requests.get(web_url, headers=_headers)
   json = response.json()
   events = [event for tournament in json["tournaments"] for event in tournament["events"]]
   filtered_sorted_matches = sorted(
    [item for item in events if item['status']['type'] == "finished"],
    key=lambda x: x['startTimestamp'])
   
   return "; ".join(f"{timestampToDate(event['startTimestamp'])}: {event['homeTeam']['name']} {event['homeScore']['current']}-{event['awayScore']['current']} {event['awayTeam']['name']}" for event in filtered_sorted_matches)

def getMatchInfo(event_id):
  print('Fetching match info')
  matchInfo = fetchTeamsAndDate(event_id)
  print("Success")
  homeTeam = matchInfo['home']
  awayTeam = matchInfo['away']
  print('Fetching match info')
  lineups = fetchLineups(event_id)
  print("Success")
  homeTeam['lineup'] = lineups['home']
  awayTeam['lineup'] = lineups['away']
  homeTeam['form'] = fetchForm(homeTeam)
  awayTeam['form'] = fetchForm(awayTeam)
  print('Fetching Standings')
  standings = fetchTableStandings(matchInfo['season'])
  print("Success")
  print('Fetching H2H')
  h2hResults = fetchH2HResults(event_id)
  print("Success")
  event_name = f"{matchInfo['date']}: {homeTeam['name']} vs {awayTeam['name']}"

  return {
     "id": event_id,
     "match_name": event_name,
     "date": matchInfo['date'],
     "home_team": homeTeam,
     "away_team": awayTeam,
     "standings": standings,
     "h2h_results": h2hResults
  }