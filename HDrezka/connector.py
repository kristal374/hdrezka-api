from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Union, Any, Type, Dict, TypeVar
from urllib.parse import urlsplit

import requests
from requests import Response
from requests.structures import CaseInsensitiveDict

ObjectConnector = TypeVar("ObjectConnector")

DEFAULT_USERAGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/117.0"


class Connector(ABC):
    """
    `Connector` is an abstract base class that provides a common interface
    for making HTTP requests using various HTTP methods. It includes methods
    for GET and POST requests.
    """

    def __init__(self, domain, user_agent, proxies):
        """
        Initialize a new instance of the class.

        :param domain: The domain of the website.
        :param user_agent: The user agent string to be used for making requests.
        :param proxies: A dictionary containing proxy definitions.
        """
        self.domain = domain
        self.user_agent = user_agent
        self.proxies = proxies

    @property
    def url(self):
        """
        This method returns the URL with the specified domain.

        :return: The URL in the format "https://domain".
        """
        return f"https://{self.domain}"

    def get_headers(self, url):
        """
        Get the headers for making a request to the given URL.

        :param url: The URL to retrieve headers for.
        :return: A dictionary containing the headers.
        """
        domain = urlsplit(str(url)).netloc
        header = {
            "Host": domain,
            "Origin": f"https://{domain}",
            "Referer": f"https://{domain}",
            "User-Agent": self.user_agent,
            "X-Requested-With": "XMLHttpRequest",
        }
        return CaseInsensitiveDict(header)

    @abstractmethod
    def get(self, url: Union[str, bytes], **kwargs: Dict[str, Any]):
        """
        Abstract implementation of the GET method
        """

    @abstractmethod
    def post(self, url: Union[str, bytes], **kwargs: Dict[str, Any]):
        """
        Abstract implementation of the GET method
        """


class Singleton(type):
    """
    Metaclass that implements the Singleton design pattern.

    This metaclass ensures that only one instance of a class is created throughout the entire program.
    It achieves this by overriding the __call__ method and maintaining a dictionary of instances.

    Usage:
        class MyClass(metaclass=Singleton):
            pass

    Notes:
        - The Singleton metaclass should be used as a metaclass by any class that needs to be a singleton,
          by specifying it in the `metaclass` argument of the class definition.
          Example: `class MyClass(metaclass=Singleton):`
        - The metaclass stores instances in a dictionary `_instances` based on their class type.
        - When the `__call__` method of a singleton class is invoked to create a new instance,
          it checks if an instance of that class type already exists.
          If an instance exists, the same instance is returned;
          otherwise, a new instance is created and added to the dictionary _instances.
    """

    _instances: Dict[Singleton, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class RequestConnector(Connector):
    """
    The `RequestConnector` class is a subclass of the `Connector` class that provides methods for making HTTP requests.

    This class inherits from `Connector`.
    """

    def __init__(
            self,
            domain="rezka.ag",
            user_agent=DEFAULT_USERAGENT,
            proxies=None,
    ):
        """
        Initialize a new instance of the class.

        :param domain: The domain of the website.
        :param user_agent: The user agent string to be used for making requests.
        :param proxies: A dictionary containing proxy definitions.
        """
        super().__init__(domain, user_agent, proxies)

    def get(self, url: Union[str, bytes], **kwargs: Any) -> Response:
        """
        Method: `get`

        This method sends a GET request to the specified URL with the provided parameters and
        returns the response as a Response object. If the optional timeout parameter is not provided,
        a default timeout of 15 seconds is used. If the optional headers parameter is not provided,
        the default headers for the URL are used. Any additional keyword arguments are passed directly
        to the underlying requests.get() function.

        :param url: The URL to send the GET request to. It can be either a string or bytes.
        :param kwargs: Additional keyword arguments to be passed to the `requests.post` method.
        :return: A Response object containing the response from the GET request.
        """
        timeout = 15 if kwargs.get("timeout") is None else kwargs.pop("timeout")
        headers = self.get_headers(url) if kwargs.get("headers") is None else kwargs.pop("headers")
        return requests.get(url, headers=headers, proxies=self.proxies, **kwargs, timeout=timeout)

    def post(self, url: Union[str, bytes], **kwargs: Any) -> Response:
        """
        Method: `post`

        This method sends a POST request to the specified URL with the provided parameters and
        returns the response as a Response object. If the optional timeout parameter is not provided,
        a default timeout of 15 seconds is used. If the optional headers parameter is not provided,
        the default headers for the URL are used. Any additional keyword arguments are passed directly
        to the underlying requests.post() function.

        :param url: The URL for the POST request. It can be either a string or bytes.
        :param kwargs: Additional keyword arguments to be passed to the `requests.post` method.
            - timeout: Optional. The timeout value for the POST request in seconds.
            If not provided, the default value is 15.
            - headers: Optional. The headers to be included in the POST request.
            If not provided, the headers will be retrieved using the `get_headers` method.
        :return: A Response object containing the response from the POST request.
        """
        timeout = 15 if kwargs.get("timeout") is None else kwargs.pop("timeout")
        headers = self.get_headers(url) if kwargs.get("headers") is None else kwargs.pop("headers")
        return requests.post(url, headers=headers, proxies=self.proxies, **kwargs, timeout=timeout)


class SessionConnector(requests.sessions.Session, Connector):
    """A class that represents a session connector for making HTTP requests.

    This class inherits from `requests.sessions.Session` and `Connector`.
    """

    def __init__(
            self,
            domain="rezka.ag",
            user_agent=DEFAULT_USERAGENT,
            proxies=None,
    ):
        """
        Initialize a new instance of the class.

        :param domain: The domain of the website.
        :param user_agent: The user agent string to be used for making requests.
        :param proxies: A dictionary containing proxy definitions.
        """
        Connector.__init__(self, domain, user_agent, proxies)
        super().__init__()
        self.headers = self.get_headers(self.url)


class NetworkClient(metaclass=Singleton):
    """
    This class provides a client for making network requests.
    It is a Singleton class, and therefore any changes will affect all places where this class is used.

    Allows you to access the self.adapter directly as if it were its own methods.
    """

    def __init__(
            self,
            domain="rezka.ag",
            user_agent=DEFAULT_USERAGENT,
            proxies=None,
            connector: Type[Connector] = RequestConnector,
    ):
        """
        Initialize a new instance of the class.

        :param domain: The domain of the website.
        :param user_agent: The user agent string to be used for making requests.
        :param proxies: A dictionary containing proxy definitions.
        :param connector: The connector class to be used for making requests.
        """
        self.adapter = connector(domain, user_agent, proxies)

    def __setattr__(self, key: str, value: Any):
        """
        Sets the value of the attribute with the given key.

        :param key: The name of the attribute to set.
        :param value: The value to set for the attribute.
        :return: None
        """
        if key == "adapter":
            return super().__setattr__(key, value)
        if hasattr(self.adapter, key):
            return self.adapter.__setattr__(key, value)
        return super().__setattr__(key, value)

    def __getattr__(self, item: str):
        """
        Retrieve the value of the specified attribute from the adapter.

        :param item: The name of the attribute to retrieve.
        :return: The value of the specified attribute.
        """
        return self.adapter.__getattribute__(item)
