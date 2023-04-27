from django.urls import path
from .views import CustomLoginView, profile
from django.contrib.auth.views import LogoutView
from main.views import home, my_topics, add_feed, add_topic, feed_detail, topic_detail, all_view, all_view_requests, topic_requests
import main.views as views
app_name = 'main'


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('accounts/profile/', profile, name='profile'),
    path('', home, name='home'),    
    path('add_topic/', add_topic, name='add_topic'),
    path('add_feed/', add_feed, name='add_feed'),
    path('feed/<slug:feed_slug>/', feed_detail, name='feed_detail'),
    path('topic/<slug:topic_slug>/', topic_detail, name='topic_detail'),
    path('all/', all_view, name='all'),
    path('all_requests/', all_view_requests, name='all_requests'),
    path('topic_requests/<slug:topic_slug>/', topic_requests, name='topic_requests'),
    path('add_remove_topic/', views.add_remove_topic, name='add_remove_topic')    
    ]