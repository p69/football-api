import requests
from .requests_header import headers
from flask_restx import fields

from utils.datetime import timestampToDate

_team_recent_events_url = "https://sofascores.p.rapidapi.com/v1/teams/events"
_event_stats_url = "https://sofascores.p.rapidapi.com/v1/events/statistics"

def _fetchEventStats(event_id):
    querystring = {"event_id": f"{event_id}"}
    print(f"Fetching tgame stats for game={event_id}")
    response = requests.get(_event_stats_url, headers=headers, params=querystring)
    json = response.json()
    return json

def fetchTeamRecentEventsStats(team_id):
    querystring = {"page":"0","team_id":f"{team_id}","course_events":"last"}
    print(f"Fetching team recent games for team={team_id}")
    response = requests.get(_team_recent_events_url, headers=headers, params=querystring)
    json = response.json()
    data = json['data']
    latest_events = data['events'][-5:]
    result = []
    for event in latest_events:
        stats = _fetchEventStats(event['id'])
        item = {
            'id': event['id'],
            'homeTeamName': event['homeTeam']['name'],
            'homeTeamId': event['homeTeam']['id'],
            'awayTeamName': event['awayTeam']['name'],
            'awayTeamId': event['awayTeam']['id'],
            'startDate': timestampToDate(event['startTimestamp']),
            'homeScore': event['homeScore'],
            'awayScore': event['awayScore'],
            'matchStatistics': stats
        }
        result.append(item)
    return result