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
-- Path: {self.radarr.fullpath}
---- original: {self.radarr.original}
-- Torrent: {self.torrent.name}
---- label: {self.torrent.label}
---- ratio: {self.torrent.ratio}
---- finished: {self.torrent.finished} ({days_old} days old)
"""
        else:
            return f"""Movie
-- Path: {self.radarr.fullpath}
---- original: {self.radarr.original}
"""

    def __repr__(self):
        return f"Movie({self.radarr.original})"


def finished_time_filter(
    torrent: rtorrent.Torrent, invert: bool = False, days: int = 30
) -> bool:
    """Filter function torrents finished older than `days`.

    Args:
        torrent:  the torrent object to filter upon
        invert:   invert the filter so its how many days young
        days:     the number of days the filter should be
                  (default 30)

    Returns:
        Boolean value to filter older torrents
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
        A list of movies that have satisfied the conditions.
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

    return movies_in_both + movies_in_radarr_only


def sizeof_fmt(num: float, suffix: str = "B") -> str:
    """Fomatter for num in bytes.

    Gotten from https://stackoverflow.com/questions/1094841/

    Returns:
        A string that contains the formatted size of bytes with the correct suffix
    """
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


if __name__ == "__main__":
    paths = get_deletable_movies()
    size = reduce(lambda a, b: a + b, [movie.radarr.size for movie in paths])
    for path in paths:
        print(path.pretty)
    print(len(paths))
    print(f"total size: {sizeof_fmt(size)}")
