from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import xmlrpc.client

server_url = (
    "***REMOVED***"
)
server = xmlrpc.client.Server(server_url)


@dataclass
class Torrent:
    """Torrent Data"""

    hash: str
    name: str
    ratio: float
    label: str
    added: datetime
    finished: Optional[datetime]
    trackers: List[str]


def get_all_torrents() -> List[Torrent]:
    """Returns all torrents in rTorrent

    Calls rTorrent XMLRPC with a multicall to get list of all torrents plus selected
    attributes

    Returns:
        A list of formatted torrents
    """
    torrents = []
    list = server.d.multicall2(
        "",
        "main",
        "d.hash=",
        "d.name=",
        "d.ratio=",
        "d.custom1=",
        "d.timestamp.started=",
        "d.timestamp.finished=",
        't.multicall=,"","t.url="',
    )

    for torrent in list:
        finished: Optional[datetime]

        if torrent[5]:
            finished = datetime.fromtimestamp(torrent[5])
        else:
            finished = None

        torrents.append(
            Torrent(
                hash=torrent[0],
                name=torrent[1],
                ratio=torrent[2] / 1000,
                label=torrent[3],
                added=datetime.fromtimestamp(torrent[4]),
                finished=finished,
                trackers=[group[1] for group in torrent[6]],
            )
        )

    return torrents


def get_finished_torrents() -> List[Torrent]:
    """Returns a filtered list of torrents that have been finished

    Calls `get_all_torrents()` and filters out torrents that have not finished
    downloading.

    Returns:
        A list of torrents that contain the finished attribute.
    """
    return list(filter(lambda torrent: torrent.finished, get_all_torrents()))
