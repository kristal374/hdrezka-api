import re
import requests
from typing import Dict, Union

from HDrezka.constants import USER_AGENT, DOMAIN


class SiteConnector:
    """
    SiteConnector предназначен для удобной реализации запросов без необходимости повторной генерации данных запроса
    """
    __shared_state: Dict[str, Union[str, dict, requests.Session]] = {
        "domain": None,
        "url": None,
        "user_agent": None,
        "proxy": None,
        "session": None}

    def __init__(self, domain=DOMAIN, user_agent=USER_AGENT, proxy: dict = None):
        """
        Генерирует стартовые настройки для запросов

        :param domain: домен сайта
        :param user_agent: можно загрузить своего юзер-агента или оставить стандартного
        :param proxy: IP адрес прокси, изначально отсутствует
        """
        if self.domain is None:
            self.__shared_state["domain"]: str = domain
            self.__shared_state["url"] = self._create_url()
            self.__shared_state["user_agent"] = user_agent
            self.__shared_state["proxy"] = proxy
            self._create_session()

        self.__dict__ = self.__shared_state

    @property
    def domain(self) -> str:
        return self.__shared_state.get("domain")

    @domain.setter
    def domain(self, value: str) -> None:
        self.__shared_state["domain"] = value
        self.__shared_state["url"] = self._create_url()
        self._create_session()

    @property
    def url(self) -> str:
        return self.__shared_state.get("url")

    @url.setter
    def url(self, value: str) -> None:
        self.__shared_state["url"] = value
        self.__shared_state["domain"] = re.search(r"(?<=://)[^\n/]*", value).group(0)
        self._create_session()

    @property
    def user_agent(self) -> str:
        return self.__shared_state.get("user_agent")

    @user_agent.setter
    def user_agent(self, value: str) -> None:
        self.__shared_state["user_agent"] = value
        self._create_session()

    @property
    def proxy(self) -> dict:
        return self.__shared_state.get("proxy")

    @proxy.setter
    def proxy(self, value: dict) -> None:
        self.__shared_state["proxy"] = value
        self._create_session()

    @property
    def session(self) -> requests.Session:
        return self.__shared_state.get("session")

    def header(self) -> dict:
        """
        Функция генерирует и возвращает заголовок запроса

        :return: заголовок запроса
        """
        return {
            "Host": self.domain,
            "Origin": "http://" + self.domain,
            "Referer": f"{self.url}/",
            "User-Agent": self.__shared_state.get("user_agent"),
            "X-Requested-With": "XMLHttpRequest"
        }

    def _create_url(self) -> str:
        return f"https://{self.domain}"

    def _create_session(self) -> None:
        if self.__shared_state.get("session") is not None:
            print("close session")
            self.__shared_state.get("session").close()
        self.__shared_state["session"] = requests.Session()
        print("create session")
        self.__shared_state.get("session").headers = self.header()
        self.__shared_state.get("session").proxies = self.__shared_state.get("proxy")
