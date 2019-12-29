from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.hosts_view, name='hosts'),
    # re_path(r'(?P<uri_hardware>[\w\.\-]+)/(?P<uri_interface>[\w:]+)$',
    #        views.host_view,
    #        name='host'),
    re_path(r'(?P<uri_host>[\w\.\-:]+)$', views.host_view, name='host'),
]
