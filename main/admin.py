# admin.py

from django.contrib import admin
from .models import Feed, Topic, Article, ArticleTopic, UserTopic, UserFeed, Thread, ThreadTopic, ThreadFeed, ThreadArticle

# Register your models here.
admin.site.register(Feed)
admin.site.register(Topic)
admin.site.register(Article)
admin.site.register(Thread)
admin.site.register(ThreadTopic)
admin.site.register(ArticleTopic)
admin.site.register(UserTopic)
admin.site.register(UserFeed)
