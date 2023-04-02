from django.core.management.base import BaseCommand
from main.models import Article, Topic

class Command(BaseCommand):
    help = 'Find topics for all articles'

    def handle(self, *args, **options):
        articles = Article.objects.all()
        for article in articles:
            topics = Topic.objects.all()
            for topic in topics:
                if topic.name.lower() in article.title.lower() or topic.name.lower() in article.description.lower():
                    article.topics.add(topic)
        self.stdout.write(self.style.SUCCESS('Successfully found topics for all articles'))