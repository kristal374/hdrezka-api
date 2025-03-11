.. _connector:

======================
Взаимодействие с сетью
======================

.. _working_with_mirrors:

Работа с зеркалами
==================

Для начала стоит упомянуть что сайт `rezka.ag <https://rezka.ag/>`_ имеет множество постоянно меняющихся зеркал, с которыми библиотека так же
умеет работать:

.. code-block:: python

    from HDrezka import HDrezka


    # Установив зеркало, все запросы будут направляться через него
    main_page = HDrezka(mirror="https://hdrezka8benxe.org").get()
    print(main_page.url)
    # >>> https://hdrezka8benxe.org/


    # Однако любые запросы сделанные напрямую с использованием url не будут использовать зеркало
    main_page = HDrezka().get(url="https://rezka.ag/")
    print(main_page.url)
    # >>> https://rezka.ag/

.. note::

    После установки зеркала, все запросы отправленные с помощью библиотеки будут отправляться на данное зеркало
    до тех пор, пока программа не прекратит свою работу или зеркало не будет изменено повторно.

.. _connector-and-working-with-it:

Connector и работа с ним
========================

Механизм который позволяет работать с зеркалами(и не только) называется коннектором. Connector - это фундаментальный
объект для работы с сетью в данной библиотеке. Именно через него будут проходить все ваши интернет запросы, а понимание
принципов его работы позволит вам работать с библиотекой более гибко. Библиотека предоставляет собственный
**RequestConnector**, что установлен по умолчанию:

.. code-block:: python

    from HDrezka.connector import RequestConnector

    my_connector = RequestConnector()
    print(my_connector.user_agent)  # Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/119.0
    response = my_connector.get(url="https://httpstat.us/200")
    print(response.status_code)
    # >>> 200
    print(response.text)
    # >>> 200 OK

Но сам по себе коннектор не особо полезен, ведь по большей части он реализует те же возможности что доступны напрямую
из **requests**. Однако, если передать коннектор в **NetworkClient**, в качестве аргумента, тогда все запросы из
библиотеки будут проходить через данный коннектор. Это происходит за счёт того что класс **NetworkClient** является
одиночкой и любые изменения в любом из его экземпляров затронут и все остальные.

.. code-block:: python

    from HDrezka import HDrezka
    from HDrezka.connector import RequestConnector, NetworkClient

    client = NetworkClient(connector=RequestConnector)

    # Обратите внимание на то что NetworkClient позволяет напрямую обращаться к RequestConnector
    client.domain = "hdrezka8benxe.org"  # устанавливаем домен зеркала

    main_page = HDrezka().get()
    print(main_page.url)
    # >>> https://hdrezka8benxe.org/

    # Всё ещё любые запросы сделанные напрямую с использованием url не будут использовать зеркало
    main_page = HDrezka().get(url="https://rezka.ag/")
    print(main_page.url)
    # >>> https://rezka.ag/

.. _creating-your-own-connectors:

Создание собственных коннекторов
================================

Базовый **RequestConnector** хоть и позволяет работать с сетью на базовом уровне, но всё же имеет довольно примитивную
реализацию. Поэтому вполне возможно что вам однажды станет его недостаточно, на этот случай предусмотрено создание
собственных коннекторов. Как и **RequestConnector** который является наследником базового абстрактного класса
**Connector** любой ваш собственный коннектор должен быть его потомком, а так же согласно базовой структуре
должен иметь методы get и post. В качестве примера давайте создадим коннектор с возможностью логирования всех
проходящих через него запросов:

.. code-block:: python

    import logging
    import sys
    from typing import Union, Dict, Any

    import requests

    from HDrezka import HDrezka
    from HDrezka.connector import NetworkClient, Connector

    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(asctime)s | %(levelname)-8s | %(message)s")


    class MyConnector(Connector):
        def get(self, url: Union[str, bytes], **kwargs: Dict[str, Any]):
            logging.info("GET request to url = %s with kwargs = %s", url, kwargs)
            return requests.get(url, headers=self.get_headers(url), proxies=self.proxies, **kwargs, timeout=15)

        def post(self, url: Union[str, bytes], **kwargs: Dict[str, Any]):
            logging.info("POST request to url = %s with kwargs = %s", url, kwargs)
            return requests.post(url, headers=self.get_headers(url), proxies=self.proxies, **kwargs, timeout=15)


    NetworkClient(connector=MyConnector)

    hdrezka = HDrezka()
    collections = hdrezka.collections().get()
    list_posters = collections[0].get()
    print(list_posters)

    # >>> 2024-04-01 18:21:55,46 | INFO     | GET request to url = https://rezka.ag/collections/ with kwargs = {}
    # >>> 2024-04-01 18:21:55,97 | INFO     | GET request to url = https://rezka.ag/collections/3482-serialy-okko/ wit...
    # >>> [Poster("Михаил Горшенёв. Легенда о Короле и Шуте"), Poster("Ласт квест"), Poster("Волшебный участок"), Poste...

Как видим, теперь все запросы, создаваемые библиотекой, проходят через наш коннектор и логируются. Использование данного
коннектора ограничивается исключительно вашими потребностями. В качестве дополнительной идеи можно добавить кэширование
запросов в базу данных (БД) и при повторении запросов извлекать их оттуда, вместо создания нового запроса к серверу.
