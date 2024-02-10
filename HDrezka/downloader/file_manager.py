from __future__ import annotations

import json
import os
from typing import Dict, Any, AnyStr, IO


class SafeFileLoader:
    def __init__(self,
                 path: str,
                 file_name: str,
                 download_data: Dict[str, Any],
                 create_dump_file: bool = False,
                 boot_recovery: bool = False,
                 ):
        self._full_path = os.path.join(path, file_name)
        self._file_obj: IO
        self._download_data = download_data
        self._create_dump_file = create_dump_file
        self._boot_recovery = boot_recovery

    def write(self, s: AnyStr) -> int:
        return self._file_obj.write(s)

    def __enter__(self) -> SafeFileLoader:
        if self._boot_recovery:
            self._file_obj = open(self._full_path, 'ab')
        else:
            self._file_obj = open(self._full_path, 'wb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._file_obj.close()
        file_name = f'{os.path.splitext(self._full_path)[0]}.json'

        if exc_type is None and os.path.exists(file_name):
            os.remove(file_name)
        elif exc_type is None:
            pass
        elif self._create_dump_file:
            dump = {
                "full_path": self._full_path,
                "download_data": self._download_data,
                "bytes_loaded": os.path.getsize(self._full_path),
                "create_dump_file": True,
                "boot_recovery": True
            }

            with open(file_name, "w", encoding="utf-8") as dump_file:
                json.dump(dump, dump_file)
