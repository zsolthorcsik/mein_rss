from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q

# Create your views here.
from django.core.paginator import Paginator
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import Article, Topic, Feed,  UserTopic, UserFeed, UserTopic




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
        

         # Count the number of articles created in the last 24 hours for each topic
        now = timezone.now()
        yesterday = now - timezone.timedelta(days=1)
        user_topics = UserTopic.objects.filter(user=request.user).annotate(
            article_count=Count('topic__article', filter=Q(topic__article__date_published__gte=yesterday))
        ).order_by('-article_count')
        #context['user_topics'] = list(UserTopic.objects.filter(user=request.user))        
        context['user_topics'] = user_topics
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


def topic_detail(request, topic_slug):
    topic = get_object_or_404(Topic, slug=topic_slug)    
    is_user_topic = UserTopic.objects.filter(user=request.user).filter(topic=topic)
    print(is_user_topic)
    return render(request=request, template_name='details/topic_detail.html', context={'topic': topic, 'is_user_topic': is_user_topic})

@csrf_exempt
def all_view(request):
    """
    This function returns html for all the articles in the detailed_search view.
    """    
    #return render(request=request, template_name='all.html')
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    offset = (page - 1) * per_page
    articles = Article.objects.order_by('-date_published')[offset:offset+per_page]
    data = [{'title': a.title, 'description': a.description, 'image': a.og_image, 'source': a.source.name, 'source_slug':a.source.slug, 'date_published': a.date_published.strftime('%Y-%m-%d %H:%M:%S'), 'link': a.link} for a in articles]
    return render(request, 'all.html')

@csrf_exempt
def all_view_requests(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    offset = (page - 1) * per_page
    articles = Article.objects.order_by('-date_published')[offset:offset+per_page]    
    data = [{'title': a.title, 'description': a.description, 'image': a.og_image, 'source': a.source.name, 'source_slug':a.source.slug,  'date_published': a.date_published.strftime('%Y-%m-%d %H:%M:%S'), 'link': a.link} for a in articles]
    return JsonResponse(data=data, safe=False)

@csrf_exempt
def topic_requests(request, topic_slug):
    """
    Returns json for the ajax request on the topic page
    """        
    topic = get_object_or_404(Topic, slug=topic_slug)    
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    offset = (page - 1) * per_page
    articles = topic.article_set.order_by('-date_published')[offset:offset+per_page]    
    data = [{'title': a.title, 'description': a.description, 'image': a.og_image, 'source': a.source.name, 'source_slug':a.source.slug,  'date_published': a.date_published.strftime('%Y-%m-%d %H:%M:%S'), 'link': a.link} for a in articles]
    return JsonResponse(data=data, safe=False)
    

@login_required
def add_remove_topic(request):
    if request.method == 'POST':
        topic_id = request.POST.get('topic_id')
        topic = Topic.objects.get(id=topic_id)
        action = request.POST.get('action')
        if action == 'add':
            UserTopic.objects.create(user=request.user, topic=topic)
        elif action == 'remove':
            UserTopic.objects.filter(user=request.user, topic=topic).delete()
        return redirect('main:topic_detail', topic_slug=topic.slug)
    else:
        return HttpResponseNotAllowed(['POST'])



