========================
HDrezka-api documentation
========================

.. code-block:: python
    from HDrezka import HDrezka

    hdrezka = HDrezka()
    posters_list = hdrezka.search("How To Train Your Dragon").get()
    movie = posters_list[0].get()
    print(movie.title)  # Как приручить дракона
    movie.player.load_video(file_name=f"{movie.original_title}.mp4", quality="1080p Ultra")


* Are you new here? Jump straight into :ref:`installation`!
# * Looking for more examples? See :ref:`quick-references`.


.. toctree::
    :hidden:
    :caption: First Steps

    basic/installation
    basic/quick-start
    basic/next-steps

.. toctree::
    :hidden:
    :caption: Quick References
