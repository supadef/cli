def task():
    """
    Make a function runnable as a scalable, cloud-hosted task.
    :return:
    """
    def g(f):
        return f
    return g
