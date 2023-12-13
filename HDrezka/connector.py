from abc import abstractmethod, ABC
from typing import Union, Any
from urllib.parse import urlsplit

import requests
from requests import Response
from requests.structures import CaseInsensitiveDict


class Connector(ABC):
    def __init__(self, domain, user_agent, proxies):
        self.domain = domain
        self.url = f"https://{domain}"
        self.user_agent = user_agent
        self.proxies = proxies

    def get_headers(self, url):
        domain = urlsplit(str(url)).netloc
        header = {
            "Host": domain,
            "Origin": f"https://{domain}",
            "Referer": f"https://{domain}",
            "User-Agent": self.user_agent,
            "X-Requested-With": "XMLHttpRequest"
        }
        return CaseInsensitiveDict(header)

    @abstractmethod
    def get(self, url: Union[str, bytes], params: Any = None, **kwargs: Any): ...

    @abstractmethod
    def post(self, url: Union[str, bytes], params: Any = None, **kwargs: Any): ...


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class RequestConnector(Connector):
    def __init__(self,
                 domain='rezka.ag',
                 user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/119.0',
                 proxies=None):
        super().__init__(domain, user_agent, proxies)

    def get(self, url: Union[str, bytes], params: Any = None, **kwargs: Any) -> Response:
        return requests.get(url, params, headers=self.get_headers(url), proxies=self.proxies, **kwargs, timeout=15)

    def post(self, url: Union[str, bytes], params: Any = None, **kwargs: Any) -> Response:
        return requests.post(url, params, headers=self.get_headers(url), proxies=self.proxies, **kwargs, timeout=15)


class SessionConnector(requests.sessions.Session, Connector):
    def __init__(self,
                 domain='rezka.ag',
                 user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/119.0',
                 proxies=None):
        Connector.__init__(self, domain, user_agent, proxies)
        super().__init__()
        self.headers = self.get_headers(self.url)


class NetworkClient(metaclass=Singleton):
    def __init__(self,
                 domain='rezka.ag',
                 user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/119.0',
                 proxies=None,
                 connector: Connector = RequestConnector):
        self.session = connector(domain, user_agent, proxies)  # noqa

    def __setattr__(self, key, value):
        """Позволяет устанавливать атрибуты self.session как у NetworkClient"""
        if key == "session":
            return super().__setattr__(key, value)
        if hasattr(self.session, key):
            return self.session.__setattr__(key, value)
        return super().__setattr__(key, value)

    def __getattr__(self, item):
        """Позволяет обращаться к self.session как к экземпляру NetworkClient"""
        return self.session.__getattribute__(item)
