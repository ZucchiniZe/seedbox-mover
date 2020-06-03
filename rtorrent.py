import xmlrpc.client
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

server_url = "***REMOVED***"
server = xmlrpc.client.Server(server_url)


@dataclass
class Torrent:
    '''Torrent Data'''
    hash: str
    name: str
    ratio: float
    label: str
    added: datetime
    finished: Optional[datetime]
    trackers: List[str]


def get_all_torrents() -> List[Torrent]:
    """
    Calls rTorrent XMLRPC endpoint with a multicall to get a list of torrrents

    returns a list of formatted torrents
    """
    torrents = []
    list = server.d.multicall2("",
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
        if torrent[5]:
            finished = datetime.fromtimestamp(torrent[5])
        else:
            finished = None

        torrents.append(Torrent(
            hash=torrent[0],
            name=torrent[1],
            ratio=torrent[2] / 1000,
            label=torrent[3],
            added=datetime.fromtimestamp(torrent[4]),
            finished=finished,
            trackers=[group[1] for group in torrent[6]]
        ))

    return torrents


def get_finished_torrents() -> List[Torrent]:
    return filter(lambda torrent: torrent.finished, get_all_torrents())
