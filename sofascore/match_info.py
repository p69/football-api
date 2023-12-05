import requests
from .requests_header import headers
from flask_restx import fields

from utils.datetime import timestampToDate

_event_url_template = "https://sofascores.p.rapidapi.com/v1/events/data?event_id={}"
_lineups_url_template = "https://sofascores.p.rapidapi.com/v1/events/lineups?event_id={}"
_standings_url_format = "https://sofascores.p.rapidapi.com/v1/seasons/standings?standing_type=total&unique_tournament_id={}&seasons_id={}"
_team_form_url_format = "https://sofascores.p.rapidapi.com/v1/teams/recent-form?team_id={}"
_h2h_events_url_format = "https://sofascores.p.rapidapi.com/v1/events/h2h-events?custom_event_id={}"
_team_stats_url_format = "https://sofascores.p.rapidapi.com/v1/teams/statistics/result?season_id={}&unique_tournament_id={}&team_id={}"

def _map_to_team_object(team_json):
   return {
      'id': team_json['id'],
      'name': team_json['fullName'],
      'manager': team_json['manager']['name']
   }

def fetchTeamStats(team_id, season_id, tournament_id):
   web_url = _team_stats_url_format.format(season_id, tournament_id, team_id)
   print(f"Fetching stats for team={team_id}, torunament={tournament_id}, season={season_id}")
   response = requests.get(web_url, headers=headers)
   json = response.json()
   data = json['data']
   return data


def fetchTeamsAndDate(event_id):
   web_url = _event_url_template.format(event_id)
   response = requests.get(web_url, headers=headers)
   json = response.json()
   event = json['data']
   season_data = {
         'tournament': event['tournament']['uniqueTournament']['id'],
         'id': event['season']['id']
      }
   home_team = _map_to_team_object(event['homeTeam'])
   away_team = _map_to_team_object(event['awayTeam'])
   home_stats = fetchTeamStats(home_team['id'], season_data['id'], season_data['tournament'])
   away_stats = fetchTeamStats(away_team['id'], season_data['id'], season_data['tournament'])
   home_team['overallStatistics'] = home_stats
   away_team['overallStatistics'] = away_stats
   return {
      'date': timestampToDate(event['startTimestamp']),
      'home': home_team,
      'away': away_team,
      'customId': event.get('customId', ""),
      'season': season_data
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
   response = requests.get(web_url, headers=headers)
   if response.status_code != 200:
      return {
         'home': 'Not available',
         'away': 'Not available'
      }
   json = response.json()

   if 'data' not in json:
      return {
         'home': 'Not available',
         'away': 'Not available'
      }
   
   data = json['data']

   homeLineup = 'Not available'
   if 'home' in data:
      homeLineup = parseLineups(data['home'])
   
   awayLineup = 'Not available'
   if 'away' in data:
      awayLineup = parseLineups(data['away'])

   return {
      'home': homeLineup,
      'away': awayLineup
   }

def fetchTableStandings(season):
  web_url = _standings_url_format.format(season['tournament'], season['id'])
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

def fetchForm(team):
   web_url = _team_form_url_format.format(team['id'])
   response = requests.get(web_url, headers=headers)
   json = response.json()['data']
   filtered_sorted_matches = sorted(
    [item for item in json['events'] if item['status']['type'] == "finished"],
    key=lambda x: x['startTimestamp'])
   
   return "; ".join(f"{timestampToDate(event['startTimestamp'])}: {event['homeTeam']['name']} {event['homeScore']['current']}-{event['awayScore']['current']} {event['awayTeam']['name']}" for event in filtered_sorted_matches)

def fetchH2HResults(matchId):
   web_url = _h2h_events_url_format.format(matchId)
   response = requests.get(web_url, headers=headers)
   json = response.json()
   events = json['data'] # [event for tournament in json["tournaments"] for event in tournament["events"]]
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
  h2hResults = "Not Available"
  if matchInfo['customId'] != "":
     h2hResults = fetchH2HResults(matchInfo['customId'])     
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

_match_info_model = None

def get_match_info_api_model(api):
   global _match_info_model
   if _match_info_model != None:
      return _match_info_model
   
   standing_team_model = api.model('StandingTeam', {
      'name': fields.String(readonly=True, description='Team name'),
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

   overall_statistics_model = api.model('OverallStatistics', {
      'goalsScored': fields.Integer(description='Number of goals scored'),
      'goalsConceded': fields.Integer(description='Number of goals conceded'),
      'ownGoals': fields.Integer(description='Number of own goals'),
      'assists': fields.Integer(description='Number of assists'),
      'shots': fields.Integer(description='Total number of shots'),
      'penaltyGoals': fields.Integer(description='Number of penalty goals'),
      'penaltiesTaken': fields.Integer(description='Number of penalties taken'),
      'freeKickGoals': fields.Integer(description='Number of goals scored from free kicks'),
      'freeKickShots': fields.Integer(description='Number of free kick shots'),
      'goalsFromInsideTheBox': fields.Integer(description='Number of goals scored from inside the penalty box'),
      'goalsFromOutsideTheBox': fields.Integer(description='Number of goals scored from outside the penalty box'),
      'shotsFromInsideTheBox': fields.Integer(description='Number of shots taken from inside the penalty box'),
      'shotsFromOutsideTheBox': fields.Integer(description='Number of shots taken from outside the penalty box'),
      'headedGoals': fields.Integer(description='Number of goals scored with headers'),
      'leftFootGoals': fields.Integer(description='Number of goals scored with the left foot'),
      'rightFootGoals': fields.Integer(description='Number of goals scored with the right foot'),
      'bigChances': fields.Integer(description='Number of big chances'),
      'bigChancesCreated': fields.Integer(description='Number of big chances created'),
      'bigChancesMissed': fields.Integer(description='Number of big chances missed'),
      'shotsOnTarget': fields.Integer(description='Number of shots on target'),
      'shotsOffTarget': fields.Integer(description='Number of shots off target'),
      'blockedScoringAttempt': fields.Integer(description='Number of blocked scoring attempts'),
      'successfulDribbles': fields.Integer(description='Number of successful dribbles'),
      'dribbleAttempts': fields.Integer(description='Number of dribble attempts'),
      'corners': fields.Integer(description='Number of corners'),
      'hitWoodwork': fields.Integer(description='Number of times the ball hit the woodwork'),
      'fastBreaks': fields.Integer(description='Number of fast breaks'),
      'fastBreakGoals': fields.Integer(description='Number of goals scored from fast breaks'),
      'fastBreakShots': fields.Integer(description='Number of shots taken during fast breaks'),
      'averageBallPossession': fields.Float(description='Average ball possession percentage'),
      'totalPasses': fields.Integer(description='Total number of passes'),
      'accuratePasses': fields.Integer(description='Number of accurate passes'),
      'accuratePassesPercentage': fields.Float(description='Percentage of accurate passes'),
      'totalOwnHalfPasses': fields.Integer(description='Total number of passes in own half'),
      'accurateOwnHalfPasses': fields.Integer(description='Number of accurate passes in own half'),
      'accurateOwnHalfPassesPercentage': fields.Float(description='Percentage of accurate passes in own half'),
      'totalOppositionHalfPasses': fields.Integer(description='Total number of passes in opposition half'),
      'accurateOppositionHalfPasses': fields.Integer(description='Number of accurate passes in opposition half'),
      'accurateOppositionHalfPassesPercentage': fields.Float(description='Percentage of accurate passes in opposition half'),
      'totalLongBalls': fields.Integer(description='Total number of long balls'),
      'accurateLongBalls': fields.Integer(description='Number of accurate long balls'),
      'accurateLongBallsPercentage': fields.Float(description='Percentage of accurate long balls'),
      'totalCrosses': fields.Integer(description='Total number of crosses'),
      'accurateCrosses': fields.Integer(description='Number of accurate crosses'),
      'accurateCrossesPercentage': fields.Float(description='Percentage of accurate crosses'),
      'cleanSheets': fields.Integer(description='Number of clean sheets'),
      'tackles': fields.Integer(description='Total number of tackles'),
      'interceptions': fields.Integer(description='Total number of interceptions'),
      'saves': fields.Integer(description='Total number of saves by the goalkeeper'),
      'errorsLeadingToGoal': fields.Integer(description='Number of errors leading to a goal'),
      'errorsLeadingToShot': fields.Integer(description='Number of errors leading to a shot'),
      'penaltiesCommited': fields.Integer(description='Number of penalties committed'),
      'penaltyGoalsConceded': fields.Integer(description='Number of penalty goals conceded'),
      'clearances': fields.Integer(description='Total number of clearances'),
      'clearancesOffLine': fields.Integer(description='Number of clearances off the line'),
      'lastManTackles': fields.Integer(description='Number of last man tackles'),
      'totalDuels': fields.Integer(description='Total number of duels'),
      'duelsWon': fields.Integer(description='Number of duels won'),
      'duelsWonPercentage': fields.Float(description='Percentage of duels won'),
      'totalGroundDuels': fields.Integer(description='Total number of ground duels'),
      'groundDuelsWon': fields.Integer(description='Number of ground duels won'),
      'groundDuelsWonPercentage': fields.Float(description='Percentage of ground duels won'),
      'totalAerialDuels': fields.Integer(description='Total number of aerial duels'),
      'aerialDuelsWon': fields.Integer(description='Number of aerial duels won'),
      'aerialDuelsWonPercentage': fields.Float(description='Percentage of aerial duels won'),
      'possessionLost': fields.Integer(description='Number of times possession was lost'),
      'offsides': fields.Integer(description='Total number of offsides'),
      'fouls': fields.Integer(description='Total number of fouls committed'),
      'yellowCards': fields.Integer(description='Number of yellow cards received'),
      'yellowRedCards': fields.Integer(description='Number of yellow-red cards received'),
      'redCards': fields.Integer(description='Number of red cards received'),
      'avgRating': fields.Float(description='Average rating of the team'),
      'accurateFinalThirdPassesAgainst': fields.Integer(description='Number of accurate final third passes against the team'),
      'accurateOppositionHalfPassesAgainst': fields.Integer(description='Number of accurate opposition half passes against the team'),
      'accurateOwnHalfPassesAgainst': fields.Integer(description='Number of accurate own half passes against the team'),
      'accuratePassesAgainst': fields.Integer(description='Number of accurate passes against the team'),
      'bigChancesAgainst': fields.Integer(description='Number of big chances against the team'),
      'bigChancesCreatedAgainst': fields.Integer(description='Number of big chances created against the team'),
      'bigChancesMissedAgainst': fields.Integer(description='Number of big chances missed against the team'),
      'clearancesAgainst': fields.Integer(description='Total number of clearances against the team'),
      'cornersAgainst': fields.Integer(description='Number of corners against the team'),
      'crossesSuccessfulAgainst': fields.Integer(description='Number of successful crosses against the team'),
      'crossesTotalAgainst': fields.Integer(description='Total number of crosses against the team'),
      'dribbleAttemptsTotalAgainst': fields.Integer(description='Total number of dribble attempts against the team'),
      'dribbleAttemptsWonAgainst': fields.Integer(description='Number of dribble attempts won against the team'),
      'errorsLeadingToGoalAgainst': fields.Integer(description='Number of errors leading to a goal against the team'),
      'errorsLeadingToShotAgainst': fields.Integer(description='Number of errors leading to a shot against the team'),
      'hitWoodworkAgainst': fields.Integer(description='Number of times the opposition hit the woodwork against the team'),
      'interceptionsAgainst': fields.Integer(description='Total number of interceptions against the team'),
      'keyPassesAgainst': fields.Integer(description='Number of key passes against the team'),
      'longBallsSuccessfulAgainst': fields.Integer(description='Number of successful long balls against the team'),
      'longBallsTotalAgainst': fields.Integer(description='Total number of long balls against the team'),
      'offsidesAgainst': fields.Integer(description='Total number of offsides against the team'),
      'redCardsAgainst': fields.Integer(description='Number of red cards against the team'),
      'shotsAgainst': fields.Integer(description='Total number of shots against the team'),
      'shotsBlockedAgainst': fields.Integer(description='Number of shots blocked against the team'),
      'shotsFromInsideTheBoxAgainst': fields.Integer(description='Number of shots from inside the box against the team'),
      'shotsFromOutsideTheBoxAgainst': fields.Integer(description='Number of shots from outside the box against the team'),
      'shotsOffTargetAgainst': fields.Integer(description='Number of shots off target against the team'),
      'shotsOnTargetAgainst': fields.Integer(description='Number of shots on target against the team'),
      'blockedScoringAttemptAgainst': fields.Integer(description='Number of blocked scoring attempts against the team'),
      'tacklesAgainst': fields.Integer(description='Total number of tackles against the team'),
      'totalFinalThirdPassesAgainst': fields.Integer(description='Total number of final third passes against the team'),
      'oppositionHalfPassesTotalAgainst': fields.Integer(description='Total number of opposition half passes against the team'),
      'ownHalfPassesTotalAgainst': fields.Integer(description='Total number of own half passes against the team'),
      'totalPassesAgainst': fields.Integer(description='Total number of passes against the team'),
      'yellowCardsAgainst': fields.Integer(description='Number of yellow cards against the team'),
      'throwIns': fields.Integer(description='Total number of throw-ins'),
      'goalKicks': fields.Integer(description='Total number of goal kicks'),
      'ballRecovery': fields.Integer(description='Total number of times the ball was recovered'),
      'freeKicks': fields.Integer(description='Total number of free kicks'),
      'id': fields.Integer(description='Unique identifier for the statistics'),
      'matches': fields.Integer(description='Number of matches played'),
      'awardedMatches': fields.Integer(description='Number of matches awarded')
   })

   team_model = api.model('Team', {
      'id': fields.Integer(readonly=True, description='The team identifier'),
      'name': fields.String(required=True, description='Full team name'),
      'manager': fields.String(required=True, description='Name of the manager'),
      'lineup': fields.String(required=True, description='Lineup for current match. Will be "Not Available" if its not available yet'),
      'form': fields.String(required=True, description='Latets results for current team across all tournaments'),
      'overallStatistics': fields.Nested(overall_statistics_model, description='Overall statistics of the team')
   })

   _match_info_model = api.model('Match', {
      'id': fields.Integer(readonly=True, description='The match identifier'),
      'date': fields.String(required=True, description='Match start date in format "YYYY-MM-DD"'),
      'match_name': fields.String(required=True, description='Match name'),
      'home_team': fields.Nested(team_model, required=True, description="Information about home team"),
      'away_team': fields.Nested(team_model, required=True, description="Information about away team"),
      'h2h_results': fields.String(required=True, description='Head to Head results for current teams across all tournaments'),
      'standings': fields.List(fields.Nested(standing_team_model), required=True, description='Teams standing in the league'),      
   })

   return _match_info_model