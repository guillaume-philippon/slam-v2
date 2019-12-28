from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.inventory_view, name='inventory'),
    re_path(r'(?P<uri_hardware>[\w\.\-]+)/interfaces/(?P<uri_interface>[\w:]+)$',
            views.interface_view,
            name='interfaces'),
    re_path(r'(?P<uri_hardware>[\w\.\-]+)$', views.hardware_view, name='hardware'),
]
