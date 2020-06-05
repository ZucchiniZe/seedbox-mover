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


def filter_old_torrents(
    torrents: List[rtorrent.Torrent], days_old: int = 30
) -> List[rtorrent.Torrent]:
    """Filters torrents finished older than `days_old`.

    Args:
        days_old: the cutoff for how long the torrents should be finished by
                  (default 30)

    Returns:
        List of filtered torrents.
    """

    def _finished_movies_filter(torrent: rtorrent.Torrent) -> bool:
        if torrent.finished is not None:
            return (datetime.today() - torrent.finished).days > days_old
        else:
            return False

    pruned = filter(_finished_movies_filter, torrents)

    return list(pruned)


def get_combined_paths() -> List[Movie]:
    """Combines the data from radarr and rTorrent

    Returns:
        A list of torrents matched between radarr and rTorrent
    """
    movie_paths = radarr.get_movie_filepaths()
    all_torrents = rtorrent.get_all_torrents()

    torrents = filter_old_torrents(all_torrents)

    combined = []

    # get the union of torrents that exist in rTorrent and Radarr
    # TODO: find the movies that exist in radarr but have already been deleted
    #       in rTorrent
    for torrent in torrents:
        path = movie_paths.get(torrent.name, None)

        if path:
            combined.append(Movie(path=path, torrent=torrent))

    return combined


if __name__ == "__main__":
    # torrents = get_torrents_to_delete()
    paths = get_combined_paths()
    print(paths)
    print(len(paths))
