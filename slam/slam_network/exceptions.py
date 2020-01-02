"""
This module provide exceptions for slam_network
"""


class NetworkFull(Exception):
    """
    Raised when we want a IP on a full network
    """
    def __init__(self):
        self.message = 'Network have no usued IP address'
