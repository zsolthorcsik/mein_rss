from django.core.management.base import BaseCommand
from main.tools.handlers.rss_feed_handler import RSS_Feed_Handler

class Command(BaseCommand):
    help = 'Gets all the articles.'

    def handle(self, *args, **kwargs):
        rss_feed_handler = RSS_Feed_Handler()        
        #articles = rss_feed_handler.get_articles_from_feed(url = url)
        articles = rss_feed_handler.get_all_articles(save=True)