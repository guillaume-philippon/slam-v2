"""
This module provide some usefull function to avoid copy / paste.
"""
from datetime import datetime
from django.core.files import locks


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
