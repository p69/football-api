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

class FlexibleNumber(fields.Raw):
    def format(self, value):
        try:
            return float(value)
        except ValueError:
            try:
                return int(value)
            except ValueError:
                return value


def get_recent_matches_model(api):
    statistics_item_model = api.model('StatisticsItemModel', {
        'name': fields.String(required=True, description='Statistic Name'),
        'home': fields.String(description='Home Value (string representation)'),
        'away': fields.String(description='Away Value (string representation)'),
        'compareCode': fields.Integer(description='Compare Code'),
        'statisticsType': fields.String(description='Type of Statistic (positive/negative)'),
        'valueType': fields.String(description='Value Type (event/team)')        
    })

    statistics_group_model = api.model('StatisticsGroupModel', {
        'groupName': fields.String(required=True, description='Group Name'),
        'statisticsItems': fields.List(fields.Nested(statistics_item_model))
    })

    statistics_data_model = api.model('StatisticsDataModel', {
        'period': fields.String(required=True, description='Period (can be 1st, 2nd or All)'),
        'groups': fields.List(fields.Nested(statistics_group_model))
    })

    statistics_model = api.model('StatisticsModel', {
        'data': fields.Nested(statistics_data_model)
    })

    score_model = api.model('ScoreModel', {
        'current': fields.Integer(required=True, description='Current score'),
        'display': fields.Integer(required=True, description='Display score'),
        'period1': fields.Integer(required=True, description='Score in first period'),
        'period2': fields.Integer(required=True, description='Score in second period'),
        'normaltime': fields.Integer(required=True, description='Score in normal time')
    })

    return api.model('RecentMatchModel', {
        'id': fields.Integer(required=True, description='Match ID'),
        'homeTeamName': fields.String(required=True, description='Home Team Name'),
        'homeTeamId': fields.Integer(required=True, description='Home Team ID'),
        'awayTeamName': fields.String(required=True, description='Away Team Name'),
        'awayTeamId': fields.Integer(required=True, description='Away Team ID'),
        'startDate': fields.String(required=True, description='Start Date'),
        'homeScore': fields.Nested(score_model),
        'awayScore': fields.Nested(score_model),
        'matchStatistics': fields.Nested(statistics_model)
    })