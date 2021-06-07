"""Main entrypoint for mover utility."""
import operator
from functools import partial, reduce
from pathlib import PurePath
from typing import List

import click

import radarr
import rtorrent
import util
from movie import Movie


def get_radarr_deletable_movies() -> List[Movie]:
    """List of movies that only exist in radarr and not rtorrent.

    note: this returns a lot of false positives since movies exist in google
      drive and radarr but have been since deleted from rtorrent.

    Returns:
        List[Movie]: List of movies
    """
    movie_paths = radarr.get_movie_filepaths()
    all_torrents = rtorrent.get_all_torrents()

    # find the movies that exist in radarr but have already been deleted in rTorrent
    torrent_names = list(map(lambda torrent: torrent.name, all_torrents))
    movies_in_radarr_only = []
    for path in movie_paths.values():
        if path.original.name not in torrent_names:
            movies_in_radarr_only.append(Movie(radarr=path, torrent=None))

    return movies_in_radarr_only


def get_rtorrent_deletable_movies(days: int = 30) -> List[Movie]:
    """List of movies that exist in rtorrent and radarr that satisfy conditions of deletion.

    Conditions:
    - movie exists in rtorrent
    - movie exists in radarr
    - has finished downloading more than 30 days ago

    Args:
        days (int, optional): amount of days to search for within rtorrent

    Returns:
        List[Movie]: A list of movies that have satisfied the conditions.
    """
    movie_paths = radarr.get_movie_filepaths()
    all_torrents = rtorrent.get_all_torrents()

    partial_filter = partial(util.finished_time_filter, days=days)

    old_torrents = filter(partial_filter, all_torrents)

    # get the union of torrents that exist in rTorrent and Radarr
    # TODO: limit to specifc tracker? implement with another filter
    movies_in_both = []
    for torrent in old_torrents:
        if path := movie_paths.get(torrent.name, None):
            movies_in_both.append(Movie(radarr=path, torrent=torrent))

    return movies_in_both


def get_all_deletable_movies(days: int = 30) -> List[Movie]:
    """Combine both conditions to get a list of all movies that can be deleted.

    Args:
        days (int, optional): amount of days to search for within rtorrent

    Returns:
        List[Movie]: All movies that satisfy conditions for deletion
    """
    return get_radarr_deletable_movies() + get_rtorrent_deletable_movies(days)


@click.command()
@click.option(
    "-s",
    "--source",
    default="rtorrent",
    show_default=True,
    type=click.Choice(["both", "radarr", "rtorrent"], case_sensitive=False),
    help="type of source to get deletable movies from.",
)
@click.option(
    "--dry-run", is_flag=True, help="run a dry run and show how large deletion will be"
)
@click.option("-d", "--days", default=30, type=int)
@click.option("--show-media-path", is_flag=True, default=False)
def mover(source: str, dry_run: bool, days: int, show_media_path: bool):
    """Custom program to search through radarr and rtorrent and remove unneeded torrents.

    \b
    radarr:
        searches through for movies that only exist in radarr but not in rtorrent.
    rtorrent:
        searches through for movies in both radarr and rtorrent that has finished downloading more than 30 days ago.
    both:
        combines both sources.
    """
    click.echo(f"Dry-run: {dry_run}, Removing from {source} for the last {days} days")

    paths: List[Movie]
    if source == "radarr":
        paths = get_radarr_deletable_movies()
    elif source == "rtorrent":
        paths = get_rtorrent_deletable_movies(days)
    else:
        paths = get_all_deletable_movies(days)

    if len(paths) == 0:
        click.echo("0 torrents to delete")
        return

    size = reduce(operator.add, [movie.radarr.size for movie in paths])
    deleted_paths: List[PurePath] = []

    for movie in paths:
        if show_media_path:
            click.echo(util.transform_path(movie.radarr.basepath))
        if torrent := movie.torrent:
            path = torrent.delete(dry_run=dry_run)
            deleted_paths.append(path)

    with open("deletable.txt", "w") as file:
        for item in deleted_paths:
            file.write(f"{util.transform_path(item, torrent=True)}\n")

    click.echo(f"{len(paths)} torrents to delete")
    click.echo(f"total size: {util.human_readable_size(size)}")


if __name__ == "__main__":
    mover()
