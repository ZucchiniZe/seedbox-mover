from datetime import datetime
from typing import List
from pprint import pprint

import rtorrent
import radarr


def get_torrents_to_delete(days_old: int = 30) -> List[rtorrent.Torrent]:
    torrents = rtorrent.get_finished_torrents()

    pruned = filter(lambda torrent: (datetime.today() -
                                     torrent.finished).days > days_old, torrents)

    return list(pruned)


if __name__ == "__main__":
    torrents = get_torrents_to_delete()
    pprint(torrents)
