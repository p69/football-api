# from bs4 import BeautifulSoup
import requests
from datetime import datetime
import re
from sofascore.leagues import FootballLeague


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
_events_for_league_url_template = "https://prod-public-api.livescore.com/v1/api/app/stage/soccer/{}-5?locale=en&MD=1"
_articles_url_template = "https://content.api.uk1.sportal365.com/articles/search/?query=*&page=1&status=active&optional_data=sports_related&category={}&teamIds={}"
_articles_token_url = "https://www.livescore.com/api/sportal/token"


def _format_date(date_number):
    # Convert the number to a string
    date_str = str(date_number)

    # Ensure the string has the correct length
    if len(date_str) != 14:
        return "Invalid Date Format"

    # Parse the string using datetime
    try:
        date_obj = datetime.strptime(date_str, '%Y%m%d%H%M%S')
        return date_obj.strftime('%Y - %b %d - %H:%M')
    except ValueError:
        return "Invalid Date Format"
    
def _current_date_as_number():
    # Get the current date
    current_date = datetime.now()

    # Format the date as a string in the desired format
    formatted_date_str = current_date.strftime("%Y%m%d") + "000000"

    # Convert the string to an integer
    return int(formatted_date_str)
    
def _extract_category_and_team_id(tag):
    # Regular expression to match the pattern
    matches = re.findall(r'(\d+)-(\d+)/$', tag)

    # Extracting the numbers
    if matches:
        first_number, second_number = matches[0]
        return (first_number, second_number)
    else:
        return ("No matches found", "No matches found")


def _fetch_all_events(league_slug):
    print(f"Fetching Livescore events for {league_slug}")
    web_url = _events_for_league_url_template.format(league_slug)
    print(web_url)
    response = requests.get(web_url, headers=headers)
    json = response.json()
    events = json['Stages'][0]['Events']
    current_date = _current_date_as_number()
    first_item_without_edf = next(
        (item for item in events if "Edf" not in item and item['Esd'] > current_date), None)
    if first_item_without_edf == None:
        return {'Error': "no upcoming matches"}
    round_name = first_item_without_edf['ErnInf']
    print(f"Getting events for round {round_name}")
    events_in_current_round = [
        item for item in events if item["ErnInf"] == round_name]
    print(f"Events count {len(events_in_current_round)}")
    mapped_objects = []
    for event in events_in_current_round:
        home_team = event['T1'][0]
        away_team = event['T2'][0]
        name = f"{home_team['Nm']} - {away_team['Nm']}"
        date = _format_date(event['Esd'])
        home_team_news_tag = home_team['NewsTag']
        away_team_news_tag = away_team['NewsTag']
        home_team_category, home_team_id = _extract_category_and_team_id(home_team_news_tag)        
        away_team_category, away_team_id = _extract_category_and_team_id(away_team_news_tag)
        obj = {
            'name': name,
            'date': date,
            'home': {
                'name': home_team['Nm'],
                'category': home_team_category,
                'id': home_team_id
            },
            'away': {
                'name': away_team['Nm'],
                'category': away_team_category,
                'id': away_team_id
            }
        }
        mapped_objects.append(obj)
    return mapped_objects

def fetch_token():    
    print("Obtaining token")
    response = requests.get(_articles_token_url, headers=headers)
    json = response.json()
    return json['token']

def _fetch_and_parse_articles(category, team):
    print(f"Fetching news for category {category} and team {team}")
    token = fetch_token()
    print("Token obtained")
    web_url = _articles_url_template.format(category, team)
    response = requests.get(web_url, headers={**headers, **{"project": "livescore.com", "origin": "https://www.livescore.com", "authorization": f"Bearer {token}"}})

    if response.status_code == 401:
        token = fetch_token
        response = requests.get(web_url, headers={**headers, **{"project": "livescore.com", "origin": "https://www.livescore.com", "authorization": f"Bearer {token}"}})

    if response.status_code != 200:
        print(f"Skipping articles for {category}-{team}. Response status {response.status_code}")
        return []
    
    json = response.json()
    articles = []
    for article_data in json['data']:
        content = "".join([part['data']['content'] for part in article_data['body'] if 'data' in part and 'content' in part['data']])
        article = {
            'id': article_data['id'],
            'title': article_data.get('title', 'No Title'),
            'subtitle': article_data.get('subtitle', 'No Subtitle'),
            'content': content
        }
        articles.append(article)
    return articles

def getLatestNews(league: FootballLeague):
    print(f"Fetching Livescore news for {league}")
    events = _fetch_all_events(league.get_livescore_slug())

    for event in events:
      print(f"Fetching news for {event['name']}")      
      home_team_articles = _fetch_and_parse_articles(event['home']['category'], event['home']['id'])
      away_team_articles = _fetch_and_parse_articles(event['away']['category'], event['away']['id'])
      event['home_team_news'] = home_team_articles
      event['away_team_news'] = away_team_articles
    
    return events
    
