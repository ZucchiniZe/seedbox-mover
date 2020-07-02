# auto (re)mover

a script that connects to rtorrent and radarr/sonarr to find torrents that can
be safely offloaded onto google drive without any consequenses from not seeding.

goals:

- search through rtorrent and find files that are elliegible for moving to
  google drive and then remove them from the client
- ellegibility criteriea:
  - [x] has been finished for more than 30 days
  - [x] exists as a movie on radarr but was previously deleted in rtorrent
  - [ ] limit to a specific tracker (torrentleech)

## Usage

when run, `mover.py` outputs a list of movies that are separated by a newline,
this is meant to be taken to the server and then using
`cat <file.txt> | xargs rm -rf` with some modification on the text file.

modifications are renaming mount to media and putting back slashes infront of
spaces, parens and apostrophes.

same thing with removing the data from rtorrent, it outputs a `deletable.txt`
and you do the same text modifications and cat xargs rm rf to remove all files/folders
