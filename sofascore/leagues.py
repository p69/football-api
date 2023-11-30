from enum import Enum

class FootballLeague(Enum):
  ENGLAND=(17, 52186)
  SPAIN=(8, 52376)
  GERMANY=(35, 52608)
  ITALY=(23, 52760)
  FRANCE=(34, 52571)
  CHAMPIONS_LEAGUE=(7, 52162)
  EUROPA_LEAGUE=(679, 53654)
  DUTCH_EREDIVISIE=(37, 52554)
  AUSTRIA=(45, 52524)
  SWITZERLAND=(215, 52366)
  BELGIUM=(38, 52383)
  DENMARK=(39, 52172)
  NORWAY=(20, 47806)
  POLAND=(202, 52176)
  IRELAND=(192, 47946)
  ROMANIA=(152, 52541)
  SCOTLAND=(36, 52588)
  SWEDEN=(40, 47730)
  TURKEY=(52, 53190)

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
    if self not in _league_to_livescore_slug_map:
      return None
    return _league_to_livescore_slug_map[self]
  
  def get_espn_slug(self):
    if self not in _league_to_espn_slug_map:
      return None
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
  FootballLeague.DUTCH_EREDIVISIE: "ned.1",
  FootballLeague.AUSTRIA: "aut.1",
  FootballLeague.SWITZERLAND: "sui.1",
  FootballLeague.BELGIUM: "bel.1",
  FootballLeague.DENMARK: "den.1",
  FootballLeague.NORWAY: "nor.1",
  FootballLeague.IRELAND: "irl.1",
  FootballLeague.ROMANIA: "rou.1",
  FootballLeague.SCOTLAND: "sco.1",
  FootballLeague.SWEDEN: "swe.1",
  FootballLeague.TURKEY: "tur.1",
}