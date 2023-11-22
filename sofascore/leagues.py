from enum import Enum

class FootballLeague(Enum):
  ENGLAND=(17, 52186)
  SPAIN=(8, 52376)
  GERMANY=(35, 52608)
  ITALY=(23, 52760)
  FRANCE=(34, 52571)

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

_league_to_livescore_slug_map = {
  FootballLeague.ENGLAND: "england/premier-league/",
  FootballLeague.SPAIN: "spain/laliga/",
  FootballLeague.GERMANY: "germany/bundesliga/",
  FootballLeague.ITALY: "italy/serie-a/",
  FootballLeague.FRANCE: "france/ligue-1/"
}