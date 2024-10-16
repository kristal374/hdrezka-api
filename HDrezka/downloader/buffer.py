from __future__ import annotations

import io
import string
import sys
from typing import Callable, Optional


class ModifiedBuffer(io.StringIO):
    def __init__(self, function: Optional[Callable[[], str]] = None, **kwargs):
        super().__init__(**kwargs)
        self._default_stdout = sys.stdout
        self._prefix = function
        sys.stdout = self

    def write(self, __s: str) -> int:
        prefix = (self._prefix() if self._prefix is not None else "", "")[__s in string.whitespace or __s[0] == "\r"]
        return self._default_stdout.write(prefix + __s)

    def close(self) -> None:
        sys.stdout = self._default_stdout
        super().close()

    def __enter__(self) -> ModifiedBuffer:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()
