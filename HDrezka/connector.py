import requests
from HDrezka.constants import USER_AGENT, DOMAIN


class SiteConnector:
    """
    SiteConnector предназначен для удобной реализации запросов без необходимости повторной генерации данных запроса
    """
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(SiteConnector, cls).__new__(cls)
        return cls.instance

    def __init__(self, domain=DOMAIN, user_agent=USER_AGENT, proxy: dict = None):
        """
        Генерирует стартовые настройки для запросов

        :param domain: домен сайта
        :param user_agent: можно загрузить своего юзер-агента или оставить стандартного
        :param proxy: IP адрес прокси, изначально отсутствует
        """
        self.domain = domain
        self.url = f"https://{self.domain}/"
        self.user_agent = user_agent
        self.proxy = proxy

        self.session = requests.Session()
        self.session.headers = self.header()
        self.session.proxies = self.proxy

    def header(self):
        """
        Функция генерирует и возвращает заголовок запроса

        :return: заголовок запроса
        """
        return {
            "Host": self.domain,
            "Origin": "http://" + self.domain,
            "Referer": self.url,
            "User-Agent": self.user_agent,
            "X-Requested-With": "XMLHttpRequest"
        }
