import requests
from sofascore.leagues import FootballLeague

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
_espn_news_for_league_url_template = "http://site.api.espn.com/apis/site/v2/sports/soccer/{}/news"

def getLatestESPNNews(league: FootballLeague):
  print(f"Fetching ESPN news for {league}")
  espn_slug = league.get_espn_slug()
  if espn_slug == None:
    return f"No news sources for league {league}"
  web_url = _espn_news_for_league_url_template.format(league.get_espn_slug())
  response = requests.get(web_url, headers=headers)
  json = response.json()
  return json
