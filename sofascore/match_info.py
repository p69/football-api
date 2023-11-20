import requests
# from bs4 import BeautifulSoup

from utils.datetime import timestampToDate

_headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}

_event_url_template = "https://api.sofascore.com/api/v1/event/{}"
_lineups_path = "/lineups"
_standings_url_format = "https://api.sofascore.com/api/v1/tournament/{}/season/{}/standings/total"
_team_form_url_format = "https://api.sofascore.com/api/v1/team/{}/events/last/0"
_h2h_events_url_format = "https://api.sofascore.com/api/v1/event/{}/h2h/events"


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
         'tournament': event['tournament']['id'],
         'id': event['season']['id']
      },
      'h2h_event_id': event['customId']
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
   web_url = _event_url_template.format(event_id) + _lineups_path
   response = requests.get(web_url, headers=_headers)
   if response.status_code != 200:
      return {
         'home': 'Not available',
         'away': 'Not available'
      }
   json = response.json()
   return {
      'home': parseLineups(json['home']),
      'away': parseLineups(json['away'])
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

def fetchH2HResults(custom_id):
   web_url = _h2h_events_url_format.format(custom_id)
   response = requests.get(web_url, headers=_headers)
   json = response.json()
   filtered_sorted_matches = sorted(
    [item for item in json['events'] if item['status']['type'] == "finished"],
    key=lambda x: x['startTimestamp'])
   
   return "; ".join(f"{timestampToDate(event['startTimestamp'])}: {event['homeTeam']['name']} {event['homeScore']['current']}-{event['awayScore']['current']} {event['awayTeam']['name']}" for event in filtered_sorted_matches)

def getMatchInfo(event_id):
  matchInfo = fetchTeamsAndDate(event_id)
  homeTeam = matchInfo['home']
  awayTeam = matchInfo['away']
  lineups = fetchLineups(event_id)
  homeTeam['lineup'] = lineups['home']
  awayTeam['lineup'] = lineups['away']
  homeTeam['form'] = fetchForm(homeTeam)
  awayTeam['form'] = fetchForm(awayTeam)
  standings = fetchTableStandings(matchInfo['season'])
  h2hResults = fetchH2HResults(matchInfo['h2h_event_id'])
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