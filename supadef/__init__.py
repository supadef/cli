from . import platform
from . import cli


def server_task():
    """
    Deploy this function to your servers as a queue-worker
    :return:
    """
    def g(f):
        # intentionally do nothing :)
        return f
    return g


def server_endpoint(method='GET'):
    """
    Deploy this function to your servers as an API endpoint
    :return:
    """
    def g(f):
        # intentionally do nothing :)
        return f
    return g
