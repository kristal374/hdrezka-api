from __future__ import annotations

import json
import os
from typing import Dict, Any, AnyStr, IO


class SafeFileLoader:
    def __init__(
        self,
        file_name: str,
        data_to_recover: Dict[str, Any],
        create_dump_file: bool = False,
        boot_recovery: bool = False,
    ):
        self._file_name = file_name
        self._file_obj: IO
        self._data_to_recover = data_to_recover
        self._create_dump_file = create_dump_file
        self._boot_recovery = boot_recovery

    def write(self, s: AnyStr) -> int:
        return self._file_obj.write(s)

    def __enter__(self) -> SafeFileLoader:
        if self._boot_recovery:
            self._file_obj = open(self._file_name, "ab")
        else:
            self._file_obj = open(self._file_name, "wb")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._file_obj.close()
        file_name = f"{os.path.splitext(self._file_name)[0]}.json"

        if exc_type is None and os.path.exists(file_name):
            os.remove(file_name)
        elif exc_type is None:
            pass
        elif self._create_dump_file:
            dump = {
                "full_path": self._file_name,
                "data_to_recover": self._data_to_recover,
                "bytes_loaded": os.path.getsize(self._file_name),
                "create_dump_file": True,
                "boot_recovery": True,
            }

            with open(file_name, "w", encoding="utf-8") as dump_file:
                json.dump(dump, dump_file)
