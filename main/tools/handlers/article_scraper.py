import requests
from bs4 import BeautifulSoup

class Article_Scraper(object):
    """Handles article scraping where needed"""
    def save_og_image(self, article):
        try:
            response = requests.get(article.link)
            soup = BeautifulSoup(response.text, 'html.parser')
            og_image = soup.find("meta",  property="og:image")
            if og_image:
                article.og_image = og_image["content"]
                article.save()
        except Exception as e:
            print(e)