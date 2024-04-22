from __future__ import annotations

import json
from typing import Union, Optional, Dict, Any, TYPE_CHECKING

from HDrezka import connector, exceptions
from HDrezka import player
from .file_manager import SafeFileLoader
from .progress_bar import ProgressBar

if TYPE_CHECKING:
    from HDrezka.player import Film, Serial


def load_file(  # pylint: disable=R0913
    file_name: str,
    length_data: int,
    requests_obj: Any,
    data_to_recover: Dict[str, Any],
    create_dump_file: bool = False,
    boot_recovery: bool = False,
    chunk_size: int = 2**10 * 512,
    unit: Optional[str] = "MB",
    length_bar: int = 30,
    processed_chunks_count: int = 0,
    number_of_timestamps: int = 1000,
) -> None:
    with SafeFileLoader(file_name, data_to_recover, create_dump_file, boot_recovery) as file:
        with ProgressBar(
            length_data, chunk_size, unit, length_bar, processed_chunks_count, number_of_timestamps
        ) as progress:
            for chunk in requests_obj.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                file.write(chunk)
                progress.update()


def load_from_url(url, file_name, chunk_size=2**10 * 512):
    response = connector.NetworkClient().get(url=url, headers={}, stream=True, timeout=60)
    load_file(
        file_name=file_name,
        length_data=int(response.headers["Content-Length"]),
        requests_obj=response,
        data_to_recover={},
        create_dump_file=False,
        boot_recovery=False,
        chunk_size=chunk_size,
        unit="MB",
    )


def load_from_player(
    video_player: Union[Film, Serial], file_name, quality="1080p", create_dump_file=False, chunk_size=2**10 * 512
):
    if video_player is None:
        raise AttributeError("Attribute 'player' is None")
    client = connector.NetworkClient()
    response = client.get(url=video_player.get_video_url(quality), headers={}, stream=True, timeout=60)
    data_to_recover = {"metadata": video_player.metadata, "quality": quality, "chunk_size": chunk_size}
    load_file(
        file_name=file_name,
        length_data=int(response.headers["Content-Length"]),
        requests_obj=response,
        data_to_recover=data_to_recover,
        create_dump_file=create_dump_file,
        boot_recovery=False,
        chunk_size=chunk_size,
        unit="MB",
    )


def reload_file(path_json_file):
    """
    Позволяет продолжить загрузку видео с места
    где она была прервана, по окончанию загрузки
    дамп файл удалиться автоматически
    """
    with open(path_json_file, "r", encoding="utf-8") as file:
        json_data = json.load(file)

    file_name, data_to_recover, bytes_loaded, create_dump_file, boot_recovery = json_data.values()
    metadata, quality, chunk_size = data_to_recover.values()

    movie = player.Serial(metadata, {}, {}, {}) if metadata["action"] == "get_stream" else player.Film(metadata, {}, {})
    player.Film.update_inside_state(movie)

    client = connector.NetworkClient()
    headers = {"Range": f"bytes={bytes_loaded}-"}
    response = client.get(url=movie.get_video_url(quality), headers=headers, stream=True, timeout=60)

    if 200 < response.status_code >= 300:
        raise exceptions.LoadingError(f"Status code = {response.status_code}, {response.reason}")
    load_file(
        file_name=file_name,
        length_data=int(response.headers["Content-Length"]) + bytes_loaded,
        requests_obj=response,
        data_to_recover=data_to_recover,
        create_dump_file=create_dump_file,
        boot_recovery=boot_recovery,
        chunk_size=chunk_size,
        unit="MB",
        processed_chunks_count=bytes_loaded // chunk_size,
    )
