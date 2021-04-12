"""Interface for rTorrent."""
from dataclasses import dataclass
from datetime import datetime
from pathlib import PurePath
from typing import List, Optional
import xmlrpc.client

from environs import Env

env = Env()
env.read_env()

server_url = env("RTORRENT_URL")
server = xmlrpc.client.Server(server_url)


@dataclass
class Torrent:
    """Torrent Data."""

    hash: str
    name: str
    ratio: float
    label: str
    added: datetime
    finished: Optional[datetime]
    trackers: List[str]
    path: PurePath

    def __repr__(self):
        return (
            f"Torrent(name={self.name}, label={self.label}, finished={self.finished})"
        )

    def delete(self, dry_run=False) -> PurePath:
        """Calls the delete method at rTorrent to remove the torrent from the client.

        Args:
            dry_run (bool, optional): When true, don't make any changes.
            Defaults to False.

        Returns:
            Path: the path of the directory or file that was removed.
        """
        if not dry_run:
            server.d.erase(self.hash)
        return self.path


def get_all_torrents() -> List[Torrent]:
    """Returns all torrents in rTorrent.

    Calls rTorrent XMLRPC with a multicall to get list of all torrents.

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
        "d.base_path=",
        "d.is_multi_file=",
    )

    for torrent in list:
        # if the torrent is just a single file, remove the extension from the name
        name = torrent[1] if torrent[8] else PurePath(torrent[1]).stem
        # handle the possibility of torrents not being finished
        finished = datetime.fromtimestamp(torrent[5]) if torrent[5] else None

        torrents.append(
            Torrent(
                hash=torrent[0],
                name=name,
                ratio=torrent[2] / 1000,
                label=torrent[3],
                added=datetime.fromtimestamp(torrent[4]),
                finished=finished,
                trackers=[group[1] for group in torrent[6]],
                path=PurePath(torrent[7]),
            )
        )

    return torrents
