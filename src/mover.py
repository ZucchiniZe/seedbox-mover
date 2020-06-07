from dataclasses import dataclass
from datetime import datetime
from functools import partial
from typing import List

import radarr
import rtorrent


@dataclass
class Movie:
    path: radarr.MoviePath
    torrent: rtorrent.Torrent

    def delete(self):
        # TODO: figure out how to handle deleting of files
        pass

    @property
    def pretty(self) -> str:
        days_old = (datetime.today() - self.torrent.finished).days  # type: ignore
        return f"""Movie
-- Path: {self.path.fullpath} ({self.path.original})
-- Torrent: {self.torrent.name}
---- label: {self.torrent.label}
---- ratio: {self.torrent.ratio}
---- finished: {self.torrent.finished} ({days_old} days old)
"""


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


def get_combined_paths() -> List[Movie]:
    """Combines the data from radarr and rTorrent

    Returns:
        A list of torrents matched between radarr and rTorrent sorted by finished date.
    """
    movie_paths = radarr.get_movie_filepaths()
    all_torrents = rtorrent.get_all_torrents()

    old_torrents = filter(finished_time_filter, all_torrents)
    young_torrents = filter(partial(finished_time_filter, invert=True), all_torrents)

    combined = []

    # get the union of torrents that exist in rTorrent and Radarr
    for torrent in old_torrents:
        path = movie_paths.get(torrent.name, None)

        if path:
            combined.append(Movie(path=path, torrent=torrent))

    # TODO: find the movies that exist in radarr but have already been deleted
    #       in rTorrent

    return sorted(combined, key=lambda movie: movie.torrent.finished, reverse=True)


if __name__ == "__main__":
    paths = get_combined_paths()
    for path in paths:
        print(path.pretty)
    print(len(paths))
