from typing import Dict, List

import requests

BASE_URL = "***REMOVED***"
API_KEY = "***REMOVED***"


def _url(path: str) -> str:
    """Helper function to build url with apikey at the end"""
    return f"{BASE_URL}{path}?apiKey={API_KEY}"


def get_movie_filepaths() -> Dict[str, Dict[str, str]]:
    """
    Calls Radarr API to and builds a dict with the key being the original torrent name
    and the value being a dict to build the renamed file path
    """
    r = requests.get(_url("/movie"))
    movies = {}

    for movie in r.json():
        if "movieFile" in movie.keys() and "sceneName" in movie["movieFile"].keys():
            movies[movie["movieFile"]["sceneName"]] = {
                "filename": movie["movieFile"]["relativePath"],
                "basepath": movie["path"],
            }

    return movies
