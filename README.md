<div align="center">

# HDrezka API

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Documentation](https://img.shields.io/badge/docs-readthedocs-informational?style=flat-square&logo=readthedocs)
[![Documentation Status](https://readthedocs.org/projects/hdrezka-api/badge/?version=latest)](https://hdrezka-api.readthedocs.io/)
</div>

**HDrezka API** — Неофициальная Python-библиотека для работы с сайтом [hdrezka.ag](https://hdrezka.ag), 
предоставляющая удобный программный интерфейс для взаимодействия с сайтом.

С её помощью можно:

- 🔍 **Искать** фильмы, сериалы, мультфильмы и аниме по названию
- 📋 **Получать** подробную информацию о контенте: название, оригинальный заголовок, описание, рейтинг, постер и другие
  метаданные
- 🎬 **Загружать** видео в нужном качестве прямо из Python-кода

## Установка

```bash
pip install git+https://github.com/kristal374/hdrezka-api.git
```

**Требования:** Python 3.9+

## Примеры использования

```python
from HDrezka import HDrezka

# Создаём клиент
hdrezka = HDrezka()

# Ищем фильм и получаем список результатов
posters_list = hdrezka.search("How To Train Your Dragon").get()

# Получаем подробную информацию по первому результату
movie = posters_list[0].get()

print(movie.title)  # Как приручить дракона
print(movie.original_title)  # How to Train Your Dragon

# Загружаем видео в качестве 1080p Ultra
movie.player.load_video(
    file_name=f"{movie.original_title}.mp4",
    quality="1080p Ultra"
)
```

## Отказ от ответственности

> [!CAUTION]
> Эта библиотека создана исключительно в образовательных целях.
> Она не является официальным продуктом HDRezka и не аффилирована с командой сайта.
> Используйте ответственно и в соответствии с условиями использования ресурса.

## Лицензия

[MIT License](LICENSE)
