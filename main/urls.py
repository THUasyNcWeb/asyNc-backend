"""
urls.py for main
created by sxx
2022.10.5
"""
from django.urls import path
from . import views

urlpatterns = [
    path('index', views.index),
    path('allnews', views.news_response),
    path('login', views.user_login),
    path('register', views.user_register),
    path('modifypassword', views.user_modify_password),
    path('checklogin', views.check_login_state),
    path('search', views.keyword_search),
    path('logout', views.user_logout),
    path('userinfo', views.user_info),
    path('modifyavatar', views.modify_avatar),
    path('modifyuserinfo', views.modify_user_info),
    path('favorites', views.user_favorites),
    path('readlater', views.user_readlater),
    path('history', views.user_read_history),
    path('search/suggest', views.search_suggest),
    path('ai/news', views.ai_news),
    path('personalize', views.personalize),
    path('newscount', views.news_count),
]
