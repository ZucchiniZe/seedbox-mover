"""Movie dataclass"""
from dataclasses import dataclass
from typing import Optional

import radarr
import rtorrent
from util import human_readable_size


@dataclass
class Movie:
    """Movie with path and torrent information."""

    radarr: radarr.RadarrMovie
    torrent: Optional[rtorrent.Torrent]

    def delete(self):  # noqa: D102
        # TODO: figure out how to handle deleting of files
        pass

    @property
    def pretty(self) -> str:
        """Nice nested text representation of a movie and its objects."""
        if self.torrent:
            days_old = (datetime.today() - self.torrent.finished).days  # type: ignore
            return f"""Movie
└─ Path: {self.radarr.fullpath}
  └─ size: {human_readable_size(self.radarr.size, decimal_places=1)}
  └─ original: {self.radarr.original}
└─ Torrent: {self.torrent.name}
  └─ label: {self.torrent.label}
  └─ ratio: {self.torrent.ratio}
  └─ finished: {self.torrent.finished} ({days_old} days old)"""
        else:
            return f"""Movie
└─ Path: {self.radarr.fullpath}
  └─ size: {human_readable_size(self.radarr.size, decimal_places=1)}
  └─ original: {self.radarr.original}"""

    def __repr__(self):
        return f"Movie({self.radarr.original})"
