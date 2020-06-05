from typing import Dict, TypedDict

import requests

BASE_URL = "***REMOVED***"
API_KEY = "***REMOVED***"


class MoviePath(TypedDict):
    original: str
    filename: str
    basepath: str


Movies = Dict[str, MoviePath]


def _url(path: str) -> str:
    """Helper function to build url with apikey at the end"""
    return f"{BASE_URL}{path}?apiKey={API_KEY}"


def get_movie_filepaths() -> Movies:
    """Get a list of all the downloaded and their accompanying paths

    Calls Radarr API to and builds a dict with the key being the original torrent name
    and the value being a dict to build the renamed file path

    Returns:
        A list of movies with their `filename` and `basepath`
    """
    r = requests.get(_url("/movie"))
    movies: Movies = {}

    for movie in r.json():
        if "movieFile" in movie.keys() and "sceneName" in movie["movieFile"].keys():
            movies[movie["movieFile"]["sceneName"]] = {
                "original": movie["movieFile"]["sceneName"],
                "filename": movie["movieFile"]["relativePath"],
                "basepath": movie["path"],
            }

    return movies
