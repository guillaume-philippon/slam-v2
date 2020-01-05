"""
This module provide some usefull function to avoid copy / paste.
"""
import re

from django.core.exceptions import ValidationError


def error_message(plugin, value, message):
    """
    This function return a dict construction for error message

    :param plugin: plugin name
    :param value: value of plugin name
    :param message: error message
    :return:
    """
    result = dict()
    result[plugin] = value
    result['status'] = 'failed'
    result['message'] = '{}'.format(message)
    return result


def name_validator(name):
    """
    This function check if a name haven't some wierd char

    :param name: mac-address provided by user
    :return:
    """
    regex = r"^(([a-zA-Z0-9-_\.])*)*$"
    pattern = re.compile(regex)
    if not pattern.match(name):
        raise ValidationError('Invalid name not match {}'.format(regex))
