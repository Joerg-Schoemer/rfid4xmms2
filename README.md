# rfid4xmms2

A project to control xmms2 on a Raspberry PI with an rc522 rfid reader

## hardware requirements

* raspberry PI
* rc522 reader
* rfid cards

## required installations on PI

* xmms2
* xmms2-client-medialib-updater

### configure xmms2 medialib updater

The medialib updater tracks directories to import media into the internal database of xmms2.

The following command line tells the medialib updater to track /home/pi/Music

```sh
xmms2 server config clients.mlibupdater.watch_dirs /home/pi/Music
```
