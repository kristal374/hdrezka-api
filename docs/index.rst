========================
Документация HDrezka-api
========================

.. code-block:: python

    from HDrezka import HDrezka

    hdrezka = HDrezka()
    posters_list = hdrezka.search("How To Train Your Dragon").get()
    movie = posters_list[0].get()
    print(movie.title)  # Как приручить дракона
    movie.player.load_video(file_name=f"{movie.original_title}.mp4", quality="1080p Ultra")


* Ты здесь новенький? Перейди к шагу ":ref:`installation`"!
* Хочешь увидеть больше примеров? Смотри раздел ":ref:`examples`".

____

.. _what-is-this:

Что это?
~~~~~~~~

**HDrezka-api** - это неофициальный API довольно популярного сайта `rezka.ag <https://rezka.ag/>`_ позволяющего
просматривать фильмы и сериалы. Основной целью проекта является создание удобного программного интерфейса позволяющего
легко создавать собственные альтернативные приложения. Где главным принципом было минимизация исходящих запросов и
предоставление максимально возможного, но минимально требуемого количества данных с точным повторением реальных объектов
сайта. Помимо этого была реализована загрузка фильмов и сериалов с удобным выводом прогресса в терминал.

.. toctree::
    :hidden:
    :caption: Первые шаги

    basic/installation
    basic/quick-start
    basic/next-steps

.. toctree::
    :hidden:
    :caption: Connector и работа с ним

    connector/general

.. toctree::
    :hidden:
    :caption: Основные сущности

    base-entity/entities
    base-entity/main-page
    base-entity/collections
    base-entity/posters
    base-entity/trailer
    base-entity/movie-detail
    base-entity/player
    base-entity/comments
    base-entity/persons
    base-entity/franchises
    base-entity/questions-asked

.. toctree::
    :hidden:
    :caption: Загрузчик

    downloader/settings

.. toctree::
    :hidden:
    :caption: Примеры

    examples/simple-example

.. toctree::
    :hidden:
    :caption: Модули HDrezka-api

    hdrezka-modules/html-representation
