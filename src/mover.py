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


def get_old_torrents(days_old: int = 30) -> List[rtorrent.Torrent]:
    """Pulls torrents from rTorrent and filters torrents older than `days_old`.

    Args:
        days_old: the cutoff for how old the torrents should be (default 30)

    Returns:
        List of filtered torrents.
    """
    torrents = rtorrent.get_finished_torrents()

    pruned = filter(
        lambda torrent: (datetime.today() - torrent.finished).days > days_old, torrents
    )

    return list(pruned)


def get_combined_paths():
    """Combines the data from radarr and rTorrent

    Returns:
        A list of torrents matched between radarr and rTorrent
    """
    movie_paths = radarr.get_movie_filepaths()
    torrents = get_old_torrents()
    combined = []

    for torrent in torrents:
        path = movie_paths.get(torrent.name, None)

        if path:
            combined.append(Movie(**{"path": path, "torrent": torrent}))

    return combined


if __name__ == "__main__":
    # torrents = get_torrents_to_delete()
    get_combined_paths()
