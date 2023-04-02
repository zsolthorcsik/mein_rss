from django.urls import path
from .views import CustomLoginView, profile
from django.contrib.auth.views import LogoutView
from main.views import home, my_topics, add_feed, add_topic, feed_detail

app_name = 'main'


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('accounts/profile/', profile, name='profile'),
    path('', home, name='home'),    
    path('add_topic/', add_topic, name='add_topic'),
    path('add_feed/', add_feed, name='add_feed'),
    path('feed/<slug:feed_slug>/', feed_detail, name='feed_detail'),

    ]