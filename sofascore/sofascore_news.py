import requests
from .requests_header import headers
import feedparser
from flask_restx import fields

_news_endpoint = "https://sofascores.p.rapidapi.com/v1/teams/news-feed"

def getLatestNewsForTeam(team_id):
  print(f"Fetching news for team {team_id}")
  querystring = {"team_id": f"{team_id}"}
  response = requests.get(_news_endpoint, headers=headers, params=querystring)
  json = response.json()
  data = json['data']
  result = {}
  if 'GB' in data:
    eng_feed = _read_feed(data['GB'])
    result['English'] = eng_feed
  else:
    polish_feed = _read_feed(data['PL'])
    result['Polish'] = polish_feed
  return result

def _read_feed(feed_url):
  feed = feedparser.parse(feed_url)
  return [
    {
        'title': entry.title,
        'link': entry.link,
        'date': entry.published,
        'description': entry.get('dc_description', entry.description),
        'full_content_encoded': entry.get('content_encoded', 'Not available, use link to read a full content')
    }
    for entry in feed.entries
  ]

def get_sofascore_news_model(api):
   news_entry_model = api.model('NewsEntry', {
      'title': fields.String(readonly=True, description='News title'),
      'link': fields.String(readonly=True, description='Link to the full article page'),
      'date': fields.String(required=True, description='Date of the publishing'),
      'description': fields.String(required=True, description='Short description of the article'),
      'full_content_encoded': fields.String(optional=True, description='Full content, may not be available'),
   })
   return api.model('TeamNews', {
      'English': fields.List(fields.Nested(news_entry_model), optional=True, description='List of news in English'),
      'Polish': fields.List(fields.Nested(news_entry_model), optional=True, description='List of news in Polish'),
   })