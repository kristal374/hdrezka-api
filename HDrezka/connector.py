import requests


class SiteConnector:
    instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(SiteConnector, cls).__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self):
        pass



