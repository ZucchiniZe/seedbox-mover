"""Interface for radarr."""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

import dateutil.parser as dt
import requests

BASE_URL = "***REMOVED***"
API_KEY = "***REMOVED***"


@dataclass
class RadarrMovie:
    """Dataclass for path information from radarr."""

    original: str
    filename: str
    basepath: str
    date_added: datetime
    size: int

    @property
    def fullpath(self):
        """The full path combining the base path and filename."""
        return f"{self.basepath}/{self.filename}"

    def __repr__(self):
        return f"Path(filename={self.filename}, original={self.original}, date_added={self.date_added})"  # noqa: E501


Movies = Dict[str, RadarrMovie]


def _url(path: str) -> str:
    """Helper function to build url with apikey at the end."""
    return f"{BASE_URL}{path}?apiKey={API_KEY}"


def get_movie_filepaths() -> Movies:
    """Get a list of all the downloaded and their accompanying paths.

    Calls Radarr API to and builds a dict with the key being the original torrent name
    and the value being a dict to build the renamed file path

    Returns:
        A list of movies with their `filename` and `basepath`
    """
    r = requests.get(_url("/movie"))
    movies: Movies = {}

    for movie in r.json():
        if (
            "movieFile" in movie.keys()
            and "sceneName" in movie["movieFile"].keys()
            and movie["downloaded"]
        ):
            movies[movie["movieFile"]["sceneName"]] = RadarrMovie(
                original=movie["movieFile"]["sceneName"],
                filename=movie["movieFile"]["relativePath"],
                size=movie["movieFile"]["size"],
                date_added=dt.parse(
                    movie["movieFile"]["dateAdded"].replace("Z", "+00:00")
                ),
                basepath=movie["path"],
            )

    return movies
