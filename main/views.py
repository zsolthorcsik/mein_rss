from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.contrib.auth.views import LoginView

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Topic, Feed,  UserTopic, UserFeed, UserTopic




class CustomLoginView(LoginView):
    template_name = 'login.html'


@login_required
def profile(request):
    return render(request, 'profile.html')


def home(request):    
    """
    Home page request
    """
    context = {}
    # If not authenticated
    if not request.user.is_authenticated:                
        return render(request=request, context = context, template_name='home.html')
    else:
        context['user_feeds'] = list(UserFeed.objects.filter(user=request.user))        
        context['user_topics'] = list(UserTopic.objects.filter(user=request.user))        
        return render(request=request, template_name='home_feed.html', context=context)


@login_required
def profile(request):
    if request.method == 'POST':
        topics = request.POST.getlist('topics')
        feeds = request.POST.getlist('feeds')
        UserTopic.objects.filter(user=request.user).delete() # Remove existing selections
        UserFeed.objects.filter(user=request.user).delete() # Remove existing selections
        for topic_id in topics:
            topic = Topic.objects.get(pk=topic_id)
            user_topic = UserTopic(user=request.user, topic=topic)
            user_topic.save()
        for feed_id in feeds:
            feed = Feed.objects.get(pk=feed_id)
            user_feed = UserFeed(user=request.user, feed=feed)
            user_feed.save()
        return redirect('main:profile')
    else:
        topics = Topic.objects.all()
        feeds = Feed.objects.all()        
        selected_topics = UserTopic.objects.filter(user=request.user).values_list('topic_id', flat=True)
        selected_feeds = UserFeed.objects.filter(user=request.user).values_list('feed_id', flat=True)
        context = {'topics': topics, 'selected_topics': selected_topics, 'feeds':feeds, 'selected_feeds':selected_feeds}
        return render(request, 'profile.html', context)

@login_required
def my_topics(request):
    # Get the current user's preferred topics
    current_topics = request.user.topics.all()

    if request.method == 'POST':
        # Get the selected topics from the form
        selected_topics = request.POST.getlist('topics')

        # Clear the user's current topic preferences
        request.user.topics.clear()

        # Add the selected topics to the user's preferences
        for topic_id in selected_topics:
            topic = Topic.objects.get(id=topic_id)
            request.user.topics.add(topic)

        return redirect('home')

    # Render the form template with the current topics and all available topics
    all_topics = Topic.objects.all()
    return render(request, 'my_topics.html', {'current_topics': current_topics, 'all_topics': all_topics})


@login_required
def add_topic(request):
    if request.method == 'POST':
        # Create a new topic object from the form data
        if len(Topic.objects.filter(name=request.POST.get('topics'))) == 0:
            name = request.POST.get('name')
            description = request.POST.get('description')
            topic = Topic(name=name, description=description)
            topic.save()
            # Redirect the user to the topics page
        return redirect('main:profile')
    else:
        # Render the form template
        return render(request, 'add_topic.html')
    


@login_required
def add_feed(request):
    if request.method == 'POST':
        # Create a new feed object from the form data
        name = request.POST.get('name')
        url = request.POST.get('url')
        feed = Feed(name=name, url=url)
        feed.save()
        # Redirect the user to the feeds page
        return redirect('main:profile')
    else:
        # Render the form template
        return render(request, 'add_feed.html')

@login_required
def feed_detail(request, feed_slug):
    feed = get_object_or_404(Feed, slug=feed_slug)
    articles = feed.article_set.order_by('-date_published')[:5]
    context = {'feed': feed, 'articles': articles}
    return render(request, 'feed_detail.html', context)



# TODO:
# 1. Create models. Copy from hirek.sess.hu
# 2. Copy the rss_collecion method
# 3. Copy the topic_finding method
# 4. Associate the rss_collecion with the users
# 5. Display rss content to the user