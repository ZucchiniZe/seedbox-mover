from datetime import datetime
from typing import List, Dict, Any
import xmlrpc.client

server_url = "***REMOVED***"
server = xmlrpc.client.Server(server_url)

Torrent = Dict[str, Any]


def get_torrents() -> List[Torrent]:
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
                               't.multicall=,"","t.url="')

    for torrent in list:
        torrents.append({
            'hash': torrent[0],
            'name': torrent[1],
            'ratio': torrent[2] / 1000,
            'label': torrent[3],
            'added': datetime.fromtimestamp(torrent[4]),
            'finished': datetime.fromtimestamp(torrent[5]),
            'trackers': [group[1] for group in torrent[6]]
        })

    return torrents
