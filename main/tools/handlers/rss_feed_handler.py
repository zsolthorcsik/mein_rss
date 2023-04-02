import feedparser
from bs4 import BeautifulSoup
from main.models import Article, Feed
from main.tools.handlers.article_scraper import Article_Scraper
#from django.core.exceptions import ObjectDoesNotExist
import pytz
from dateutil import parser

class RSS_Feed_Handler(object):
    """docstring for RSS_Feed_Handler"""
    article_scraper = None
    
    def __init__(self):
        super(RSS_Feed_Handler, self).__init__()        
        self.article_scraper = Article_Scraper()

    def get_articles_from_feed(self, url):                
        d = feedparser.parse(url)
        articles = []
        vienna_tz = pytz.timezone("Europe/Vienna")
        for entry in d.entries:                              
            article = Article()
            article.title = entry.title
            article.link = entry.link
            #article.description = entry.summary            
            soup = BeautifulSoup(entry.summary, 'html.parser')
            article.description = soup.get_text()
            if 'published' in entry.keys():
                article.date_published = parser.parse(entry.published)
            elif 'updated' in entry.keys():
                article.date_published = parser.parse(entry.updated)

            if not article.date_published.tzinfo:
                article.date_published = vienna_tz.localize(article.date_published)
            article.source = Feed.objects.filter(url=url)[0]            
            articles.append(article)            
        return articles

    def get_all_articles(self, save=False):
        """
        Function to get all the articles from all of the feeds in the database.

        :return: List of articles
        """
        articles = []
        for feed in Feed.objects.all():
            articles.extend(self.get_articles_from_feed(feed.url))
        if save:
            for article in articles:
                if len(Article.objects.filter(link=article.link)) == 0:
                        
                    article.save()
                    self.article_scraper.save_og_image(article)
                    print('{} saved'.format(article.title))
        return articles