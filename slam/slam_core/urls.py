from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('csrf', views.csrf, name='csrf'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('domains', include('slam_domain.urls')),
    path('networks', include('slam_network.urls')),
    path('hardware', include('slam_hardware.urls'))
]
