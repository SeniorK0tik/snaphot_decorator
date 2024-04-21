from __future__ import annotations

import inspect
import json
import os
import time
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, List

import aiofiles.os



if TYPE_CHECKING:
    from snapshot_deco.snaphot_timer import SnapShotTimer



async def write_file(
        filepath: str | os.PathLike,
        content: str,
        mode: str = "w"
) -> None:
    """Запись файла"""
    async with aiofiles.open(filepath, mode) as file:
        await file.write(content)


async def find_all_files(dir_path: str | os.PathLike) -> list:
    """Находит все файлы в указанной директории"""
    files = []
    os.makedirs(dir_path, exist_ok=True)

    found_files = await aiofiles.os.scandir(dir_path)
    for file in found_files:
        files.append(Path(file.path))

    return files


async def write_new_snapshot(
        files: List[str | os.PathLike],
        dir_path: str | os.PathLike,
        content: dict | list,
        max_files_count: int
) -> None:
    """Запись результатов"""
    if len(files) > max_files_count:
        # Сортировка по дате со создания
        files.sort(key=os.path.getctime)
        # Удаляется самый старый
        filepath = files[0]
        await aiofiles.os.remove(filepath)

    content = json.dumps(content)
    filepath = os.path.join(dir_path, f"{int(time.time())}.json")
    await write_file(filepath, content)


async def snapshot_process(
        snapshot_timer: SnapShotTimer,
        content: dict | list,
        max_files_count: int,
        dirpath: str | os.PathLike

) -> None:
    # Проверка, что текущее время больше предполагаемого
    current_time = time.time()
    if current_time >= snapshot_timer.suppose_time():
        snapshot_timer.upd_previous_snapshot_time(current_time)

        # Поиск всех файлов в указаной директории
        files = await find_all_files(dirpath)
        # Запись файла
        await write_new_snapshot(
            files=files,
            dir_path=dirpath,
            content=content,
            max_files_count=max_files_count
        )



def snapshot(  # noqa: C901
        dirpath: str | os.PathLike,
        snapshot_timer: SnapShotTimer,
        max_files_count: int
) -> Callable:
    """
    dirpath: Путь до конечной папки.
    previous_snapshot_time: Ссылка на предыдущее время записи
    timeout: Промежуток времени между снепшотами
    max_files_count: Максимальное количество файлов в истории

    Декоратор делает снепшот результатов выполнения функции.
    Записывает их в указанную директорию.
    """
    def decorator(func: Callable) -> Callable:  # noqa: C901
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Callable[..., Any]:
                res = await func(*args, **kwargs)

                await snapshot_process(
                    snapshot_timer=snapshot_timer,
                    content=res,
                    max_files_count=max_files_count,
                    dirpath=dirpath
                )
                return res

        elif inspect.isasyncgenfunction(func):
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Callable[..., Any]:
                async for res in func(*args, **kwargs):
                    await snapshot_process(
                        snapshot_timer=snapshot_timer,
                        content=res,
                        max_files_count=max_files_count,
                        dirpath=dirpath
                    )
                    yield res
        else:
            raise TypeError("Not implemented type for snapshot decorator")

        return wrapper
    return decorator
