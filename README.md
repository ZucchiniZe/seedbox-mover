# auto (re)mover

a script that connects to rtorrent and radarr/sonarr to find torrents that can be safely offloaded onto google drive without any consequenses from not seeding.

goals:

- search through rtorrent and find files that are elliegible for moving to google drive and then remove them from the client
- ellegibility criteriea:
  - older than one month
  - is a movie on radarr
  - is on a specific tracker (torrentleech)
