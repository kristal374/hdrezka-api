.. _hdrezka:

=======
HDrezka
=======

Вероятно первое с чем вы столкнётесь в библиотеке - главный класс **HDrezka**.

.. py:class:: HDrezka.main_page.HDrezka

   .. py:method:: __init__(mirror: Optional[str] = None):
   .. py:method:: films(genre: Optional[GenreFilm] = None) -> Films:
   .. py:method:: cartoons(genre: Optional[GenreCartoons] = None) -> Cartoons:
   .. py:method:: series(genre: Optional[GenreSeries] = None) -> Series:
   .. py:method:: animation(genre: Optional[GenreAnimation] = None) -> Animation:
   .. py:method:: new() -> New:
   .. py:method:: announce() -> Announce:
   .. py:method:: collections() -> Collections:
   .. py:method:: search(text: str) -> Search:
   .. py:method:: filter(self, pattern: Optional[Union[Filters, str]] = Filters.LAST):
   .. py:method:: show_only(self, pattern: Optional[Union[ShowCategory, int]] = ShowCategory.ALL):
   .. py:method:: get(self, url: Optional[str] = None):


