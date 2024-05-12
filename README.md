# lastfm-scraper

Scripts to extract data from lastfm.

The scripts need a valid config file with your lastfm API keys (get them at last.fm/api.) in a `config.ini` file (see `config_sample.ini` for an example).

- `lastfm-artists_by_genre` : Export artists name from one or several genres to csv files (2 backends available, beautifulsoup4 and pylast).
- `lastfm-artists_infos` : Export data for one or several artists (Fields : Name, URL, Listeners, Playcount, Country, Tags, Top Tracks, Top Albums, Similar Artists). Slow (~10s/artist)
- `lastfm-complete_timeline` : Export all the scrobbles of one or several users in csv files (Fields : Artist, Album, Title, Date, Timestamp).
- `lastfm-all_favorite_tracks` : Export all favorite tracks of one or several users in csv files (Format : Artist - Track)

## Requirements

- bs4
- lxml
- numpy
- pandas
- requests
- pylast

## Usage

```
python lastfm-artists_by_genre_pylast.py -g "pop,rock,metal,jazz,indie rock"
python lastfm-artists_infos.py -a "daft punk,u2,radiohead"
python lastfm-complete_timeline.py -u USERNAME
python lastfm-all_favorite_tracks -u USERNAME
```

## Help

### lastfm-artists_by_genre_pylast

```
python lastfm-artists_by_genre_pylast.py -h
```

```
usage: lastfm-artists_by_genre_pylast.py [-h] [--debug] [-g GENRES]

Genre lastfm scraper

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -g GENRES, --genres GENRES
                        Genres to scrap (separated by comma)
```

### lastfm-artists_infos

```
python lastfm-artists_infos.py -h
```

```
usage: lastfm-artists_infos.py [-h] [--debug] [-f FILE] [-a ARTIST]

Extract infos from artists from a timeline or from a list

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -f FILE, --file FILE  File containing the timeline to extract the unique
                        artists from
  -a ARTIST, --artist ARTIST
                        Artists (separated by comma)
```

### lastfm-complete_timeline

```
python lastfm-complete_timeline.py -h
```

```
usage: lastfm-complete_timeline.py [-h] [--debug] [--file FILE]
                                   [--username USERNAME]

Extract complete or partial lastfm timeline from an user

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  --file FILE, -f FILE  File already containing a timeline
  --username USERNAME, -u USERNAME
                        Name of the user
```

### lastfm-artists_by_genre_bs4 (deprecated)

```
python lastfm-artists_by_genre_bs4.py -h
```

```
usage: lastfm-artists_by_genre_bs4.py [-h] [--debug] [-g GENRES]

Genre lastfm scraper

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information
  -g GENRES, --genres GENRES
                        Genres to scrap (separated by comma)
```

### lastfm-all_favorite_tracks

```
python lastfm-all_favorite_tracks.py -h
```

```
usage: lastfm-all_favorite_tracks.py [-h] [--debug] [--username USERNAME]

Extract all favorite tracks from one or several lastfm users.

optional arguments:
  -h, --help            show this help message and exit
  --debug               Display debugging information.
  --username USERNAME, -u USERNAME
                        Names of the users (separated by comma).
```
