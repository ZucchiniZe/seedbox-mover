from datetime import datetime
from typing import List
from pprint import pprint

import rtorrent
import radarr


def get_torrents_to_delete(days_old: int = 30) -> List[rtorrent.Torrent]:
    '''
    Get list of torrents from rtorrent that are more than `days_old` (default: 30)
    '''
    torrents = rtorrent.get_finished_torrents()

    pruned = filter(lambda torrent: (datetime.today() -
                                     torrent.finished).days > days_old, torrents)

    return list(pruned)


def get_combined_paths():
    movie_paths = radarr.get_movie_filepaths()
    torrents = get_torrents_to_delete()
    combined = []

    for torrent in torrents:
        path = movie_paths.get(torrent.name, None)

        if path:
            combined.append({
                'path': path,
                'torrent': torrent
            })

    return combined


if __name__ == "__main__":
    # torrents = get_torrents_to_delete()
    get_combined_paths()
