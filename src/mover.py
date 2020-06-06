from dataclasses import dataclass
from datetime import datetime
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


def old_torrents_filter(torrent: rtorrent.Torrent, days_old: int = 30) -> bool:
    """Filter function torrents finished older than `days_old`.

    Args:
        torrent:  the torrent object to filter upon
        days_old: the cutoff for how long the torrents should be finished by
                  (default 30)

    Returns:
        Boolean value to filter older torrents
    """
    if torrent.finished is not None:
        return (datetime.today() - torrent.finished).days > days_old
    else:
        return False


def get_combined_paths() -> List[Movie]:
    """Combines the data from radarr and rTorrent

    Returns:
        A list of torrents matched between radarr and rTorrent sorted by finished date.
    """
    movie_paths = radarr.get_movie_filepaths()
    all_torrents = rtorrent.get_all_torrents()

    torrents = filter(old_torrents_filter, all_torrents)

    combined = []

    # get the union of torrents that exist in rTorrent and Radarr
    for torrent in torrents:
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
