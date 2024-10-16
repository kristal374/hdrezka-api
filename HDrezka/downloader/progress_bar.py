from __future__ import annotations

import datetime
import math
from collections import deque
from typing import Dict, Union, List, Tuple, Optional

from . import buffer


class ProgressBar:
    progress_element = ("", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█")
    template = (
        "|{progress}| {processed_chunks_count}/{chunks_count} [{percent:>3}%]"
        " in {time_since_start} ({speed:>6} {unit}/s, eta: {time_to_finish})"
    )

    def __init__(
            self,
            length_data: int,
            chunk_size: int = 2 ** 10 * 512,
            unit: Optional[str] = None,
            length_bar: int = 30,
            processed_chunks_count: int = 0,
            number_of_timestamps: int = 1000,
    ):
        self._start_time = datetime.datetime.now()
        self._chunks_count = math.ceil(int(length_data) / int(chunk_size))
        self._bar_length = length_bar
        self._chunk_size = chunk_size
        self._unit = unit
        self._processed_chunks_count = processed_chunks_count
        self._timestamps_list: deque = deque(maxlen=number_of_timestamps)
        self._buffer = buffer.ModifiedBuffer(function=self.__custom_print)

    @property
    def chunk_size(self):
        return self._chunk_size

    def update(self, visibility: bool = True) -> None:
        self._processed_chunks_count += 1
        if visibility:
            print("\r" + self.template.format(**self.get_progress_bar_parameters()), end=" ")

    def get_progress_bar_parameters(self) -> Dict[str, Union[str, int, float]]:
        speed, unit = self.convert(self.__get_update_speed(), custom_unit=self._unit)
        return {
            "progress": self.__get_progress_bar_placeholder(),
            "processed_chunks_count": self._processed_chunks_count,
            "chunks_count": self._chunks_count,
            "percent": round(self.__get_progress_in_percentage()),
            "time_since_start": self.format_time_difference(datetime.datetime.now() - self._start_time),
            "speed": speed,
            "unit": unit,
            "time_to_finish": self.__get_time_to_finish(),
        }

    def __custom_print(self) -> str:
        return f"\ron {self._processed_chunks_count}: "

    def __get_update_speed(self) -> float:
        self._timestamps_list.append(datetime.datetime.now())
        try:
            package_time = (self._timestamps_list[-1] - self._timestamps_list[0]).total_seconds()
            package_size = self._chunk_size * len(self._timestamps_list)
            return package_size / package_time
        except (ZeroDivisionError, IndexError):
            return 0

    def __get_progress_bar_placeholder(self) -> str:
        advance = int(
            self.normalize_value(
                self._processed_chunks_count,
                [0, self._chunks_count],
                [0, self._bar_length * len(self.progress_element)],
            )
        )
        finished, during = divmod(advance, len(self.progress_element))
        return (finished * self.progress_element[-1] + self.progress_element[during]).ljust(self._bar_length)

    def __get_progress_in_percentage(self) -> float:
        return self.normalize_value(self._processed_chunks_count, [0, self._chunks_count], [0, 100])

    def __get_time_to_finish(self) -> str:
        try:
            load_time = datetime.datetime.now() - self._start_time
            return self.format_time_difference((load_time / (self.__get_progress_in_percentage() * 0.01)) - load_time)
        except ZeroDivisionError:
            return "inf"

    @staticmethod
    def normalize_value(
            value: Union[int, float], from_range: List[Union[int, float]], to_range: List[Union[int, float]]
    ) -> float:
        return to_range[0] + (value - from_range[0]) * (to_range[1] - to_range[0]) / (from_range[1] - from_range[0])

    @staticmethod
    def format_time_difference(time_difference: datetime.timedelta) -> str:
        hours, remainder = divmod(time_difference.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        return f"{hours:02}:{minutes:02}:{seconds:02}"

    @staticmethod
    def convert(value: Union[int, float], custom_unit: Optional[str] = None) -> Tuple[float, str]:
        units_list = {
            "B": 1 << 0,
            "KB": 1 << 10,
            "MB": 1 << 20,
            "GB": 1 << 30,
            "TB": 1 << 40,
            "PB": 1 << 50,
            "EB": 1 << 60,
            "ZB": 1 << 70,
            "YB": 1 << 80,
        }
        if custom_unit is not None:
            return round(value / units_list[custom_unit.upper()], 2), custom_unit
        for unit in list(units_list.keys())[::-1]:
            size = units_list[unit]
            if value >= size:
                return round(value / size, 2), unit
        return round(value / units_list["B"], 2), "B"

    def __enter__(self) -> ProgressBar:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._buffer.close()
        print()

    def __del__(self) -> None:
        if self._processed_chunks_count != self._chunks_count:
            raise BufferError("The process was not completed!")
