.. _quick-start:

=============
Быстрый старт
=============

Давайте рассмотрим несколько иных примеров, чтобы изучить на что способна библиотека.

.. _site-navigation:

Навигация по сайту
==================

Для взаимодействия с сайтом необходимо иметь возможность по нему перемещаться. Библиотека реализует такую возможность следующим образом:

.. code-block:: python

    from HDrezka import HDrezka, GenreFilm


    hdrezka = HDrezka()  # Создаём экземпляр главного класса

    films_navigation = hdrezka.films(genre=GenreFilm.FICTION)  # Переходим в раздел фильмов и указываем жанр "фантастика"
    films_navigation = films_navigation.page(5)  # Переходим на 5 страницу
    posters_list = films_navigation.get()  # Получаем всю информацию со страницы навигации

    poster = posters_list[0]  # Получаем первый постер со страницы
    print(poster.title)  # Печатаем название фильма
    # >>> Буйство смерти
    print(poster.entity)  # Печатаем тип видео(Фильм, сериал, мультфильм...)
    # >>> Фильм
    print(poster.genre)  # Печатаем жанр фильма
    # >>> Ужасы
    print(poster.year)  # Печатаем год выхода фильма
    # >>> 1984

Показанный способ удобен если мы заранее знаем куда мы хотим перейти, если же нам надо перебрать все страницы выбранной категории можно воспользоваться следующим способом:

.. code-block:: python

    from HDrezka import HDrezka


    for posters_list in HDrezka().films():  # Все объекты имеющие возможность перемещаться по страницам являются итераторами
        print(posters_list)
        # >>> [Poster("Домашние учителя"), Poster("В этом мире"), Poster("В тени дюн"), Poster("Укусы рассвета"), ...
        # >>> [Poster("Смертельная тайна"), Poster("Мясник, повар и меченосец"), Poster("Мексиканский ниндзя"), ...
        # >>> ...

.. _working_with_movie_pages:

Работа со страницами фильмов
============================

Любая страница на текущий момент имеющая плеер для воспроизведения фильмов или сериалов может обрабатываться следующим образом:

.. code-block:: python

    from HDrezka import HDrezka


    hdrezka = HDrezka()  # Создаём экземпляр главного класса
    movie = hdrezka.get("https://rezka.ag/cartoons/fiction/43477-arkeyn-2021.html")  # Получаем всю информацию по ссылке

    print(movie.title)  # Печатаем название сериала
    # >>> Аркейн
    print(movie.description)  # Печатаем описание сериала
    # >>> В основе сюжета лежит вселенная игры League of Legends, где рассказывается предыстория двух городов-государ...
    print(type(movie.player).__name__)  # Получаем информацию о том хранит ли в себе плеер фильм или сериал
    # >>> Serial
    print(movie.info_table.rates)  # Печатаем информацию о рейтинге на разных площадках
    # >>> [<Rating(IMDb: 9.0(265870))>, <Rating(Кинопоиск: 8.75(142071))>, <Rating(HDrezka: 9.44(16584))>]

Как видим мы можем получить любую информацию присутствующую на оригинальной странице сайта.
Аналогичным образом мы можем работать с информацией о плеере:

.. code-block:: python

    from HDrezka import HDrezka


    hdrezka = HDrezka()  # Создаём экземпляр главного класса
    movie = hdrezka.get("https://rezka.ag/cartoons/fiction/43477-arkeyn-2021.html")  # Получаем всю информацию по ссылке

    print(movie.player.translators_dict)  # Печатаем информацию об озвучках
    # {'HDrezka Studio (ua)': 376, 'HDrezka Studio': 111, 'Дубляж': 56, 'TVShows': 232, 'лостфильм (LostFilm)': 1, ...

    # Если озвучка с именем "Дубляж" присутствует в озвучках плеера
    if "Дубляж" in movie.player.translators_dict:
        translate_id = movie.player.translators_dict.get("Дубляж")  # Получаем идентификатор озвучки с названием "Дубляж"
        movie.player.set_translate(translate_id)  # Устанавливаем выбранную озвучку в качестве желаемой

    print(movie.player.get_video_url("720p"))  # Печатаем ссылку по которой можно напрямую получить видео
    # https://stream.voidboost.cc/70042ecfc45cdac808e3e75b61bbd2fb:2024042415:RE1BY3l1LzRhRVJFNVhPZEloYzNOR24rbk9VS...

    # Загружаем видео с именем которое составляем из названия с припиской .mp4 с качеством 1080p
    movie.player.load_video(file_name=f"{movie.original_title}.mp4", quality="1080p")

