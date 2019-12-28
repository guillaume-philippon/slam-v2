"""
As this is a django internal template, we disable pylint
"""
# pylint: disable=C0115
from django.apps import AppConfig


class SlamCoreConfig(AppConfig):
    name = 'slam_core'
