.. _installation:

=========
Установка
=========

**HDrezka-api** - является python библиотекой, а это значит что перед использованием вам следует установить python_
если вы этого не сделали ранее. После установки обновите pip и выполните одну из следующих команд, что бы установить
или обновить библиотеку до последней версии.


Для Linux:

.. code-block:: sh

    python3 -m pip install --upgrade hdrezka-api

или для Windows:

.. code-block:: sh

    python -m pip install --upgrade hdrezka-api

.. _installing-development-versions:

Установка версии для разработчиков
==================================

Если вам нужно получить последние изменения в библиотеке, вы можете запустить следующую команду:

.. code-block:: sh

    python -m pip install --upgrade https://github.com/kristal374/hdrezka-api/archive/refs/heads/master.zip

.. note::

    Версия для разработчиков может содержать ошибки.

.. _verification:

Проверка
========

Чтобы убедиться, что библиотека установлена правильно, выполните следующую команду:

.. code-block:: sh

    python -c "import HDrezka; print(HDrezka.__version__)"

Текущая версия библиотеки должна отобразиться в выводе терминала.

.. _python: https://www.python.org/downloads/