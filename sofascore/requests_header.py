import os

rapid_api_key = os.getenv('RAPIDAPI_KEY')
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'X-RapidAPI-Key': rapid_api_key
}