"""Interface for radarr."""
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Dict

import dateutil.parser as dt
from environs import Env
import requests

env = Env()
env.read_env()

BASE_URL = env("RADARR_URL")
API_KEY = env("RADARR_KEY")


@dataclass
class RadarrMovie:
    """Dataclass for path information from radarr."""

    original: Path
    filename: Path
    basepath: Path
    date_added: datetime
    size: int

    @property
    def fullpath(self):
        """The full path combining the base path and filename."""
        return f"{self.basepath}/{self.filename}"

    def __repr__(self):
        return f"Path(filename={self.filename}, original={self.original}, date_added={self.date_added})"  # noqa: E501


def _url(path: str) -> str:
    """Helper function to build url with apikey at the end."""
    return f"{BASE_URL}{path}?apiKey={API_KEY}"


def get_movie_filepaths() -> Dict[str, RadarrMovie]:
    """Get a list of all the downloaded and their accompanying paths.

    Calls Radarr API to and builds a dict with the key being the original torrent name
    and the value being a dict to build the renamed file path

    Returns:
        Dict[str, RadarrMovie]: dict of movies optimized for searching.
    """
    r = requests.get(_url("/movie"))
    r.raise_for_status()
    movies = {}

    try:
        for movie in r.json():
            if (
                "movieFile" in movie.keys()
                and "sceneName" in movie["movieFile"].keys()
                and movie["downloaded"]
            ):
                movies[movie["movieFile"]["sceneName"]] = RadarrMovie(
                    original=Path(movie["movieFile"]["sceneName"]),
                    filename=Path(movie["movieFile"]["relativePath"]),
                    basepath=Path(movie["path"]),
                    size=movie["movieFile"]["size"],
                    date_added=dt.parse(movie["movieFile"]["dateAdded"]),
                )
    except json.JSONDecodeError:
        print("json is malformed")
        print("response", r.text)

    return movies
