import json
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Count, Q

# Create your views here.
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from .models import Article, Topic, Feed, Thread, UserTopic, UserFeed, UserTopic




class CustomLoginView(LoginView):
    template_name = 'login.html'



def home(request):    
    """
    Home page request
    """
    context = {}
    # If not authenticated
    if not request.user.is_authenticated:                
        return render(request=request, context=context, template_name='home.html')
    else:
        # Get the feeds and topics that the user has subscribed to
        context['user_feeds'] = UserFeed.objects.filter(user=request.user)        
        user_topics = UserTopic.objects.filter(user=request.user).annotate(
            article_count=Count('topic__article', filter=Q(topic__article__date_published__gte=timezone.now()-timezone.timedelta(days=1)))
        ).order_by('-article_count')
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
        user_threads = Thread.objects.filter(user=request.user)
        selected_topics = UserTopic.objects.filter(user=request.user).values_list('topic_id', flat=True)
        selected_feeds = UserFeed.objects.filter(user=request.user).values_list('feed_id', flat=True)
        context = {'topics': topics, 'selected_topics': selected_topics, 'feeds':feeds, 'selected_feeds':selected_feeds, 'user_threads':user_threads}
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
def add_thread(request):
    if request.method == 'POST':
        # Create a new thread object from the form data
        name = request.POST.get('name')        
        description = request.POST.get('description', None)
        thread = Thread(name=name, user=request.user)
        thread.save()
        # Redirect the user to the threads page
        return redirect('main:profile')
    else:
        # Render the form template
        return render(request, 'add_thread.html')


@login_required
def feed_detail(request, feed_slug):
    feed = get_object_or_404(Feed, slug=feed_slug)
    # Getting the most common topics for the feed together with the number of articles in each topic.
    topics = Topic.objects.filter(article__source=feed).annotate(article_count=Count('article')).order_by('-article_count')    
    # Print number of articles in each topic    
    context = {'feed': feed, 'topics': topics}    
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
    # Getting the topic object according to the get parameter
    context = {}
    topic_name = request.GET.get('topic')
    feed_slug = request.GET.get('feed')
    if topic_name:
        topic = get_object_or_404(Topic, name=topic_name)
        context['topic'] = topic
    if feed_slug:
        feed = get_object_or_404(Feed, slug=feed_slug)
        context['feed'] = feed    
    return render(request, 'all.html', context=context)


@csrf_exempt
def all_view_requests(request):
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    offset = (page - 1) * per_page

    # Get the topic and feed query parameters
    topic_name = request.GET.get('topic')
    feed_slug = request.GET.get('feed')

    print(feed_slug)
    # Filter the queryset based on the topic and feed parameters
    articles = Article.objects.order_by('-date_published')
    if topic_name:
        articles = articles.filter(topics__name__iexact=topic_name)
    if feed_slug:
        articles = articles.filter(source__slug=feed_slug)

    # Paginate the queryset and serialize it to JSON
    articles = articles[offset:offset+per_page]
    data = [{'title': a.title, 'description': a.description, 'image': a.og_image, 'source': a.source.name, 'source_slug': a.source.slug, 'date_published': a.date_published.strftime('%Y-%m-%d %H:%M:%S'), 'link': a.link} for a in articles]            
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


@csrf_exempt
def feed_requests(request, feed_slug):
    # DOing the same for requests as for topics.
    feed = get_object_or_404(Feed, slug=feed_slug)
    page = int(request.GET.get('page', 1))
    per_page = int(request.GET.get('per_page', 10))
    offset = (page - 1) * per_page
    articles = feed.article_set.order_by('-date_published')[offset:offset+per_page]
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

@login_required
def get_user_threads(request):
    """
    Returns the threads of the user in json format
    """
    threads = Thread.objects.filter(user=request.user)
    
    data = [{'name': t.name, 'id': t.id} for t in threads]
    return JsonResponse(data=data, safe=False)


@login_required
def add_topic_to_thread(request, thread_id):
    print('add_topic_to_thread')
    print(thread_id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse the JSON data
            topic_id = data.get('topicId')
            topic_name = data.get('topicName')
            thread = Thread.objects.get(id=thread_id)            
            print(thread_id)
            topic = Topic.objects.get(id=topic_id, name=topic_name)
            print(topic)
            thread.topics.add(topic)
            thread.save()
            print("success")
            return JsonResponse({'threadId': thread.id})
        except (Thread.DoesNotExist, Topic.DoesNotExist):
            return JsonResponse({'error': 'Invalid thread or topic.'}, status=400)
        except Exception as e:
            print(e)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)