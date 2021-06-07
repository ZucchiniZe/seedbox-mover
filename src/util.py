"""Utility functions and business logic."""
from datetime import datetime
from pathlib import PurePath

import rtorrent


def human_readable_size(size: float, decimal_places: int = 3) -> str:
    """Formatter for num in bytes.

    Gotten from https://stackoverflow.com/a/43690506/3453207

    Args:
        size (float): number of bytes
        decimal_places (int, optional): number of decimal places to report.
                                        Defaults to 3.

    Returns:
        str: String formatted with the correct unit suffix
    """
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f}{unit}"


def transform_path(path: PurePath, torrent: bool = False) -> str:
    """Turns a PurePath into a directory name for cupid.

    Args:
        path (PurePath): directory
        torrent (bool, optional): if exists locally through rtorrent

    Returns:
        str: unix directory with escaped values
    """
    parsed = path.as_posix().replace("'", "\\'").replace("(", "\(").replace(")", "\)")

    replaced = parsed if torrent else parsed.replace("mount", "media")

    return f'"{replaced}"'


def finished_time_filter(
    torrent: rtorrent.Torrent, invert: bool = False, days: int = 30
) -> bool:
    """Filter function torrents finished older than `days`.

    Args:
        torrent (rtorrent.Torrent): torrent object to filter upon
        invert (bool, optional): invert filter so its days young. Defaults to False.
        days (int, optional): number of days filter should be. Defaults to 30.

    Returns:
        bool: value to filter older torrents
    """
    if torrent.finished is not None and torrent.label == "radarr":
        if invert:
            return (datetime.today() - torrent.finished).days < days
        else:
            return (datetime.today() - torrent.finished).days > days
    else:
        return False
