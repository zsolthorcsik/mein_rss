from datetime import datetime, timezone, timedelta
from main.models import Article, Topic

# Get the Orbán Viktor topic
topic = Topic.objects.get(name='Máv-Start')

# Get the start and end dates for the previous month
now = datetime.now(timezone.utc)
start_date = datetime(now.year, now.month-1, 1, tzinfo=timezone.utc)
end_date = now

# Get all articles published in the previous month that are related to the Orbán Viktor topic
articles = Article.objects.filter(date_published__range=(start_date, end_date), topics=topic)

# Print the source, title, and a portion of the description for each article
for article in articles:
    truncated_desc = article.description[:100].rstrip() + "..." if len(article.description) > 100 else article.description
    print(f"{article.source}: {article.title} - {truncated_desc}")