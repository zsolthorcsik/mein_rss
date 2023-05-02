from django.core.management.base import BaseCommand
from main.models import Article, Topic

class Command(BaseCommand):
    help = 'Find topics for all articles'

    def handle(self, *args, **options):
        # Iterating through all topics
        for topic in Topic.objects.all():
            # Finding articles that have the topic title in the title or description and don't have the topic already.
            articles = Article.objects.filter(
                title__icontains=topic.name
            ).exclude(
                topics=topic
            ) | Article.objects.filter(
                description__icontains=topic.name
            ).exclude(
                topics=topic
            )
            # Iterating through all articles that have the topic title in the title or description.
            for article in articles:                
                article.topics.add(topic)
                # Saving the article.
                article.save()
                # Printing the article title and topic name.
                print(topic.name, article.title)

            
            
        