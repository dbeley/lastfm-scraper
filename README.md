# lastfm-scraper

Scripts to extract data from lastfm.

## Requirements

- tqdm
- bs4
- lxml
- numpy
- pandas
- requests
- pylast

## Installation of the virtualenv (recommended)

```
pipenv install
```

## Usage

```
python lastfm-artists_by_genre_pylast.py -g "pop,rock,metal,jazz,indie rock"
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

### lastfm-artists_information

```
python lastfm-artists_information.py -h
```

```
usage: lastfm-artists_information.py [-h] [--debug] [-f FILE] [-a ARTIST]

Extract information from artists from a timeline or from a list

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

