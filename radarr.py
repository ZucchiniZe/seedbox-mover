import requests

BASE_URL = '***REMOVED***'
API_KEY = '***REMOVED***'


def _url(path: str) -> str:
    return f'{BASE_URL}{path}?apiKey={API_KEY}'


def build_db():
    r = requests.get(_url('/movie'))
    movies = {}

    for movie in r.json():
        if 'movieFile' in movie.keys() and 'sceneName' in movie['movieFile'].keys():
            movies[movie['movieFile']['sceneName']] = {
                'filename': movie['movieFile']['relativePath'],
                'basepath': movie['path']
            }

    return movies
