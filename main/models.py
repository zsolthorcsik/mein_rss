from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class Topic(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    

# Create your models here.
# Model for Articles
class Article(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    content = models.TextField()
    date_published = models.DateTimeField(auto_now_add=True)
    source = models.ForeignKey('main.Feed', on_delete=models.CASCADE)
    link = models.CharField(max_length=255, blank=True, null=True, unique=True)
    og_image = models.URLField(blank=True, null=True)
    topics = models.ManyToManyField(Topic, through='ArticleTopic')

    def __str__(self):
        return self.title


# Model for Feeds
class Feed(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    slug  = models.SlugField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Thread(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    feeds = models.ManyToManyField('Feed', through='ThreadFeed')
    topics = models.ManyToManyField('Topic', through='ThreadTopic')
    articles = models.ManyToManyField('Article', through='ThreadArticle')

class ThreadFeed(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    feed = models.ForeignKey('Feed', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class ThreadTopic(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    topic = models.ForeignKey('Topic', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class ThreadArticle(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    article = models.ForeignKey('Article', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

# Intermediate model for Topics
class ArticleTopic(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

# Create your models here.
class UserTopic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.topic.name}"
    
class UserFeed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.feed.name}"

