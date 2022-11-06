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
    path('modifyusername', views.user_modify_username),
    path('userinfo', views.user_info),
    path('modifyuserinfo', views.modify_user_info),
]
