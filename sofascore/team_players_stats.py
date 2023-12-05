import requests
from .requests_header import headers
from flask_restx import fields

from utils.datetime import timestampToDate

_team_players_stats_url_format = "https://sofascores.p.rapidapi.com/v1/teams/player-statistics/result?season_id={}&unique_tournament_id={}&team_id={}"
_team_seasons_url_format = "https://sofascores.p.rapidapi.com/v1/teams/statistics/seasons?team_id={}"

_team_players_stats_model = None


def get_team_players_api_model(api):
    global _team_players_stats_model
    if _team_players_stats_model != None:
        return _team_players_stats_model

    statistics_model = api.model('Statistics', {
        'rating': fields.Float(description='Player rating'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    player_model = api.model('Player', {
        'name': fields.String(description='Player name'),
        'slug': fields.String(description='Player slug'),
        'shortName': fields.String(description='Player short name'),
        'position': fields.String(description='Playing position'),
        'userCount': fields.Integer(description='User count'),
        'id': fields.Integer(description='Player ID')
    })

    rating_model = api.model('Rating', {
        'statistics': fields.Nested(statistics_model, description='Player statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    goals_statistics_model = api.model('GoalsStatistics', {
        'goals': fields.Integer(description='Number of goals'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    goals_model = api.model('Goals', {
        'statistics': fields.Nested(goals_statistics_model, description='Player goal statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    expected_goals_statistics_model = api.model('ExpectedGoalsStatistics', {
        'goals': fields.Integer(description='Number of goals'),
        'expectedGoals': fields.Float(description='Expected number of goals'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    expected_goals_model = api.model('ExpectedGoals', {
        'statistics': fields.Nested(expected_goals_statistics_model, description='Player expected goal statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    assists_statistics_model = api.model('AssistsStatistics', {
        'id': fields.Integer(description='Statistics ID'),
        'assists': fields.Integer(description='Number of assists'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    # Define the Assists model
    assists_model = api.model('Assists', {
        'statistics': fields.Nested(assists_statistics_model, description='Player assist statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    expected_assists_statistics_model = api.model('ExpectedAssistsStatistics', {
        'id': fields.Integer(description='Statistics ID'),
        'expectedAssists': fields.Float(description='Expected number of assists'),
        'assists': fields.Integer(description='Number of assists'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    expected_assists_model = api.model('ExpectedAssists', {
        'statistics': fields.Nested(expected_assists_statistics_model, description='Player expected assist statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    goals_assists_sum_statistics_model = api.model('GoalsAssistsSumStatistics', {
        'goalsAssistsSum': fields.Integer(description='Sum of goals and assists'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    goals_assists_sum_model = api.model('GoalsAssistsSum', {
        'statistics': fields.Nested(goals_assists_sum_statistics_model, description='Sum of player goals and assists statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    penalty_goals_statistics_model = api.model('PenaltyGoalsStatistics', {
        'penaltiesTaken': fields.Integer(description='Number of penalties taken'),
        'penaltyGoals': fields.Integer(description='Number of penalty goals'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    penalty_goals_model = api.model('PenaltyGoals', {
        'statistics': fields.Nested(penalty_goals_statistics_model, description='Player penalty goals statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    scoring_frequency_statistics_model = api.model('ScoringFrequencyStatistics', {
        'scoringFrequency': fields.Float(description='Scoring frequency (minutes per goal/assist)'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    scoring_frequency_model = api.model('ScoringFrequency', {
        'statistics': fields.Nested(scoring_frequency_statistics_model, description='Player scoring frequency statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    total_shots_statistics_model = api.model('TotalShotsStatistics', {
        'totalShots': fields.Integer(description='Total number of shots'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    total_shots_model = api.model('TotalShots', {
        'statistics': fields.Nested(total_shots_statistics_model, description='Player total shots statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    shots_on_target_statistics_model = api.model('ShotsOnTargetStatistics', {
        'shotsOnTarget': fields.Integer(description='Number of shots on target'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    shots_on_target_model = api.model('ShotsOnTarget', {
        'statistics': fields.Nested(shots_on_target_statistics_model, description='Player shots on target statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    big_chances_missed_statistics_model = api.model('BigChancesMissedStatistics', {
        'bigChancesMissed': fields.Integer(description='Number of big chances missed'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    big_chances_missed_model = api.model('BigChancesMissed', {
        'statistics': fields.Nested(big_chances_missed_statistics_model, description='Player big chances missed statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    big_chances_created_statistics_model = api.model('BigChancesCreatedStatistics', {
        'bigChancesCreated': fields.Integer(description='Number of big chances created'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    big_chances_created_model = api.model('BigChancesCreated', {
        'statistics': fields.Nested(big_chances_created_statistics_model, description='Player big chances created statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    accurate_passes_statistics_model = api.model('AccuratePassesStatistics', {
        'accuratePasses': fields.Integer(description='Number of accurate passes'),
        'accuratePassesPercentage': fields.Float(description='Percentage of accurate passes'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    accurate_passes_model = api.model('AccuratePasses', {
        'statistics': fields.Nested(accurate_passes_statistics_model, description='Player accurate passes statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    key_passes_statistics_model = api.model('KeyPassesStatistics', {
        'keyPasses': fields.Integer(description='Number of key passes'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    key_passes_model = api.model('KeyPasses', {
        'statistics': fields.Nested(key_passes_statistics_model, description='Player key passes statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    accurate_long_balls_statistics_model = api.model('AccurateLongBallsStatistics', {
        'accurateLongBalls': fields.Integer(description='Number of accurate long balls'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    accurate_long_balls_model = api.model('AccurateLongBalls', {
        'statistics': fields.Nested(accurate_long_balls_statistics_model, description='Player accurate long balls statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    successful_dribbles_statistics_model = api.model('SuccessfulDribblesStatistics', {
        'successfulDribbles': fields.Integer(description='Number of successful dribbles'),
        'successfulDribblesPercentage': fields.Float(description='Percentage of successful dribbles'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    successful_dribbles_model = api.model('SuccessfulDribbles', {
        'statistics': fields.Nested(successful_dribbles_statistics_model, description='Player successful dribbles statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    penalty_won_statistics_model = api.model('PenaltyWonStatistics', {
        'penaltyWon': fields.Integer(description='Number of penalties won'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    penalty_won_model = api.model('PenaltyWon', {
        'statistics': fields.Nested(penalty_won_statistics_model, description='Player penalty won statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    tackles_statistics_model = api.model('TacklesStatistics', {
        'tackles': fields.Integer(description='Number of tackles made'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    tackles_model = api.model('Tackles', {
        'statistics': fields.Nested(tackles_statistics_model, description='Player tackles statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    interceptions_statistics_model = api.model('InterceptionsStatistics', {
        'interceptions': fields.Integer(description='Number of interceptions made'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    interceptions_model = api.model('Interceptions', {
        'statistics': fields.Nested(interceptions_statistics_model, description='Player interceptions statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    clearances_statistics_model = api.model('ClearancesStatistics', {
        'clearances': fields.Integer(description='Number of clearances made'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    clearances_model = api.model('Clearances', {
        'statistics': fields.Nested(clearances_statistics_model, description='Player clearances statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    possession_lost_statistics_model = api.model('PossessionLostStatistics', {
        'possessionLost': fields.Integer(description='Number of times possession was lost'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    possession_lost_model = api.model('PossessionLost', {
        'statistics': fields.Nested(possession_lost_statistics_model, description='Player possession lost statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    yellow_cards_statistics_model = api.model('YellowCardsStatistics', {
        'yellowCards': fields.Integer(description='Number of yellow cards received'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    yellow_cards_model = api.model('YellowCards', {
        'statistics': fields.Nested(yellow_cards_statistics_model, description='Player yellow cards statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    red_cards_statistics_model = api.model('RedCardsStatistics', {
        'redCards': fields.Integer(description='Number of red cards received'),
        'id': fields.Integer(description='Statistics ID'),
        'type': fields.String(description='Type of statistics'),
        'appearances': fields.Integer(description='Number of appearances')
    })

    red_cards_model = api.model('RedCards', {
        'statistics': fields.Nested(red_cards_statistics_model, description='Player red cards statistics'),
        'playedEnough': fields.Boolean(description='Has the player played enough'),
        'player': fields.Nested(player_model, description='Player information')
    })

    _team_players_stats_model = api.model('TeamPlayerStats', {
        'rating': fields.List(fields.Nested(rating_model), description='List of player ratings'),
        'goals': fields.List(fields.Nested(goals_model), description='List of player goals'),
        'expectedGoals': fields.List(fields.Nested(expected_goals_model), description='List of player expected goals'),
        'assists': fields.List(fields.Nested(assists_model), description='List of player assists'),
        'expectedAssists': fields.List(fields.Nested(expected_assists_model), description='List of player expected assists'),
        'goalsAssistsSum': fields.List(fields.Nested(goals_assists_sum_model), description='List of player goals and assists sum'),
        'penaltyGoals': fields.List(fields.Nested(penalty_goals_model), description='List of player penalty goals'),
        'scoringFrequency': fields.List(fields.Nested(scoring_frequency_model), description='List of player scoring frequencies'),
        'totalShots': fields.List(fields.Nested(total_shots_model), description='List of player total shots'),
        'shotsOnTarget': fields.List(fields.Nested(shots_on_target_model), description='List of player shots on target'),
        'bigChancesMissed': fields.List(fields.Nested(big_chances_missed_model), description='List of player big chances missed'),
        'bigChancesCreated': fields.List(fields.Nested(big_chances_created_model), description='List of player big chances created'),
        'accuratePasses': fields.List(fields.Nested(accurate_passes_model), description='List of player accurate passes'),
        'keyPasses': fields.List(fields.Nested(key_passes_model), description='List of player key passes'),
        'accurateLongBalls': fields.List(fields.Nested(accurate_long_balls_model), description='List of player accurate long balls'),
        'successfulDribbles': fields.List(fields.Nested(successful_dribbles_model), description='List of player successful dribbles'),
        'penaltyWon': fields.List(fields.Nested(penalty_won_model), description='List of player penalties won'),
        'tackles': fields.List(fields.Nested(tackles_model), description='List of player tackles'),
        'interceptions': fields.List(fields.Nested(interceptions_model), description='List of player interceptions'),
        'clearances': fields.List(fields.Nested(clearances_model), description='List of player clearances'),
        'possessionLost': fields.List(fields.Nested(possession_lost_model), description='List of player possessions lost'),
        'yellowCards': fields.List(fields.Nested(yellow_cards_model), description='List of player yellow cards'),
        'redCards': fields.List(fields.Nested(red_cards_model), description='List of player red cards')
    })

    return _team_players_stats_model


def _get_season_info(team_id):
    web_url = _team_seasons_url_format.format(team_id)
    print(f"Fetching team seasons info for team={team_id}")
    response = requests.get(web_url, headers=headers)
    json = response.json()
    data = json['data']
    tournamentSeason = data['uniqueTournamentSeasons'][0]
    tournament_id = tournamentSeason['uniqueTournament']['id']
    season_id = tournamentSeason['seasons'][0]['id']
    return {
        'tournament': tournament_id,
        'season': season_id
    }


def fetchTeamPlayerStats(team_id):
    season_info = _get_season_info(team_id)
    web_url = _team_players_stats_url_format.format(
        season_info['season'], season_info['tournament'], team_id)
    print(
        f"Fetching players stats for team={team_id}, {season_info}")
    response = requests.get(web_url, headers=headers)
    json = response.json()
    data = json['data']
    return data
