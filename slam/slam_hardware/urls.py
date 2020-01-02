"""
This modules is the URL dispatcher for hardware. We have 3 different route
 - https://slam.example.com/hardware: to act on all hardware
 - https://slam.example.com/hardware/my-computer: to act on my-computer
 - https://slam.example.com/domains/my-computer/interfaces/mac-address: to act on interface

urlpatterns do not respect pylint name style, so we disable C0103 (invalid-name) check on this file
"""
# pylint: disable=C0103
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.inventory_view, name='inventory'),
    re_path(r'(?P<uri_hardware>[\w\.:\-]+)/interfaces/(?P<uri_interface>[\w:]+)$',
            views.interface_view,
            name='interfaces'),
    re_path(r'(?P<uri_hardware>[\w\.:\-]+)$', views.hardware_view, name='hardware'),
]
