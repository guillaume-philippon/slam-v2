"""
This modules is the main URL dispatcher. There are 4 local routing and 3 apps routing
 - https://slam.example.com/: to look at the home page
 - https://slam.example.com/csrf: to retrieve a new CSRF token
 - https://slam.example.com/login: to sign in
 - https://slam.example.com/logout: to sign out

 - https://slam.example.com/domains: route to slam_domain app
 - https://slam.example.com/networks: route to slam_network app
 - https://slam.example.com/hardware: route to slam_hardware app
 - https://slam.example.com/hosts: route to slam_host app

urlpatterns do not respect pylint name style, so we disable C0103 (invalid-name) check on this file
"""
# pylint: disable=C0103
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('csrf', views.csrf, name='csrf'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('search', views.search, name='search'),
    path('producer/commit/', views.commit, name='commit'),
    path('producer/publish/', views.publish, name='publish'),
    path('producer/diff', views.diff, name='diff'),

    path('domains', include('slam_domain.urls')),
    path('networks', include('slam_network.urls')),
    path('hardware', include('slam_hardware.urls')),
    path('hosts', include('slam_host.urls')),
]
