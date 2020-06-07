"""Find torrents on seedbox that can be safely removed."""
from dataclasses import dataclass
from datetime import datetime
from functools import reduce
from typing import List, Optional

import radarr
import rtorrent


@dataclass
class Movie:
    """Movie with path and torrent information."""

    radarr: radarr.RadarrMovie
    torrent: Optional[rtorrent.Torrent]

    def delete(self):  # noqa: D102
        # TODO: figure out how to handle deleting of files
        pass

    @property
    def pretty(self) -> str:
        """Nice nested text representation of a movie and its objects."""
        if self.torrent:
            days_old = (datetime.today() - self.torrent.finished).days  # type: ignore
            return f"""Movie
└─ Path: {self.radarr.fullpath}
  └─ size: {human_readable_size(self.radarr.size, decimal_places=1)}
  └─ original: {self.radarr.original}
└─ Torrent: {self.torrent.name}
  └─ label: {self.torrent.label}
  └─ ratio: {self.torrent.ratio}
  └─ finished: {self.torrent.finished} ({days_old} days old)"""
        else:
            return f"""Movie
└─ Path: {self.radarr.fullpath}
  └─ size: {human_readable_size(self.radarr.size, decimal_places=1)}
  └─ original: {self.radarr.original}"""

    def __repr__(self):
        return f"Movie({self.radarr.original})"


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


def get_deletable_movies() -> List[Movie]:
    """List of movies that satisfy the conditions of deletion.

    Conditions (mutually exclusive):
        - movie does not exist in rtorrent but does in radarr
        - movie exists in rtorrent but has finished more than 30 days ago

    Returns:
        List[Movie]: A list of movies that have satisfied the conditions.
    """
    movie_paths = radarr.get_movie_filepaths()
    all_torrents = rtorrent.get_all_torrents()

    old_torrents = filter(finished_time_filter, all_torrents)

    # get the union of torrents that exist in rTorrent and Radarr
    # TODO: limit to specifc tracker?
    movies_in_both = []
    for torrent in old_torrents:
        path = movie_paths.get(torrent.name, None)

        if path:
            movies_in_both.append(Movie(radarr=path, torrent=torrent))

    # find the movies that exist in radarr but have already been deleted in rTorrent
    torrent_names = list(map(lambda torrent: torrent.name, all_torrents))
    movies_in_radarr_only = []
    for path in movie_paths.values():
        if path.original not in torrent_names:
            movies_in_radarr_only.append(Movie(radarr=path, torrent=None))

    return movies_in_radarr_only + movies_in_both


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


if __name__ == "__main__":
    paths = get_deletable_movies()
    size = reduce(lambda a, b: a + b, [movie.radarr.size for movie in paths])
    for path in paths:
        print(path.pretty)
    print(len(paths))
    print(f"total size: {human_readable_size(size)}")
