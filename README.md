# auto (re)mover

a script that connects to rtorrent and radarr/sonarr to find torrents that can be safely offloaded onto google drive without any consequenses from not seeding.

goals:

- search through rtorrent and find files that are elliegible for moving to google drive and then remove them from the client
- ellegibility criteriea:
  - [x] has been finished for more than 30 days
  - [x] exists as a movie on radarr but was previously deleted in rtorrent
  - [ ] limit to a specific tracker (torrentleech)
