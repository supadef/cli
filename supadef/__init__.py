def task():
    """
    Make a function runnable as a scalable, cloud-hosted task.
    :return:
    """
    def g(f):
        # intentionally do nothing :)
        return f
    return g


def endpoint(method='GET'):
    """
    Make a function runnable as a scalable, cloud-hosted API Endpoint.
    :return:
    """
    def g(f):
        # intentionally do nothing :)
        return f
    return g
