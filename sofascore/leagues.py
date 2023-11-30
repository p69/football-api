from enum import Enum

class FootballLeague(Enum):
  ENGLAND=(17, 52186)
  SPAIN=(8, 52376)
  GERMANY=(35, 52608)
  ITALY=(23, 52760)
  FRANCE=(34, 52571)
  CHAMPIONS_LEAGUE=(7, 52162)
  EUROPA_LEAGUE=(679, 53654)

  def __init__(self, id, latestSeason):
    self.id = id
    self.latestSeason = latestSeason

  @staticmethod
  def from_string(name):
    try:
      return FootballLeague[name]
    except KeyError:
      return None
    
  def get_livescore_slug(self):
    return _league_to_livescore_slug_map[self]
  
  def get_espn_slug(self):
    return _league_to_espn_slug_map[self]

_league_to_livescore_slug_map = {
  FootballLeague.ENGLAND: "england/premier-league/",
  FootballLeague.SPAIN: "spain/laliga/",
  FootballLeague.GERMANY: "germany/bundesliga/",
  FootballLeague.ITALY: "italy/serie-a/",
  FootballLeague.FRANCE: "france/ligue-1/",
  FootballLeague.CHAMPIONS_LEAGUE: "uefa.champions",
  FootballLeague.EUROPA_LEAGUE: "uefa.europa",
}

_league_to_espn_slug_map = {
  FootballLeague.ENGLAND: "eng.1",
  FootballLeague.SPAIN: "esp.1",
  FootballLeague.GERMANY: "ger.1",
  FootballLeague.ITALY: "ita.1",
  FootballLeague.FRANCE: "fra.1",
  FootballLeague.CHAMPIONS_LEAGUE: "uefa.champions",
  FootballLeague.EUROPA_LEAGUE: "uefa.europa",
}