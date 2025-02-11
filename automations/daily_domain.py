import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# Function to fetch the latest AI news from Google News
def fetch_latest_ai_news_from_google():
    # Google News RSS feed for AI-related news
    rss_url = 'https://news.google.com/rss/search?q=Artificial+Intelligence+OR+AI&hl=en-US&gl=US&ceid=US:en'

    # Fetch the RSS feed
    response = requests.get(rss_url)
    
    # Parse the RSS feed
    root = ET.fromstring(response.content)
    
    # Namespace for parsing
    ns = {'ns': 'http://www.w3.org/2005/Atom'}

    # Filter news items from the last 24 hours
    last_24_hours = datetime.now() - timedelta(days=1)
    
    # Iterate through each item in the feed
    for item in root.findall('./channel/item'):
        title = item.find('title').text
        link = item.find('link').text
        pub_date = item.find('pubDate').text
        
        # Convert the publication date to a datetime object
        pub_date_dt = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %Z')
        
        if pub_date_dt > last_24_hours:
            print(f"Title: {title}")
            print(f"Published At: {pub_date_dt}")
            print(f"Link: {link}\n")

# Fetch and print the latest AI news from Google News
fetch_latest_ai_news_from_google()
