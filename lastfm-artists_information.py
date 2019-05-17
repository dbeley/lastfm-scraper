import pylast
import configparser
import logging
import time
import argparse
import pandas as pd
from tqdm import tqdm
from pathlib import Path

logger = logging.getLogger()
temps_debut = time.time()


def lastfmconnect():
    config = configparser.ConfigParser()
    config.read('config.ini')
    API_KEY = config['lastfm']['API_KEY']
    API_SECRET = config['lastfm']['API_SECRET']
    username = config['lastfm']['username']
    password = pylast.md5(config['lastfm']['password'])

    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                                   username=username, password_hash=password)
    return network


def main():
    args = parse_args()
    if not args.file and not args.artist:
        logger.error("Use the -f/--file or the -a/--artist flags to input one or several artists to search")
        exit()

    network = lastfmconnect()

    if args.artist:
        artists = args.artist.split(',')
    else:
        df = pd.read_csv(args.file, sep='\t', encoding='utf-8')
        df.columns = ['Artist', 'Album', 'Track', 'Date', 'Timestamp']
        logger.debug(df.columns)
        artists = df.Artist.unique()
    n_artists = len(artists)
    logger.debug("Number of artists : %s", n_artists)

    dict_artists = {}
    for index, artist in tqdm(enumerate(artists, 1), total=n_artists, dynamic_ncols=True):
        logger.debug("%s: {artist}", index)
        dict = {}
        a = network.get_artist(artist)
        dict['Name'] = a.get_name()
        dict['URL'] = a.get_url()
        dict['Listeners'] = a.get_listener_count()
        dict['Playcount'] = a.get_playcount()

        tags = a.get_top_tags(20)
        for i, t in enumerate(tags, 1):
            dict[f"Tag {i}"] = t.item.name
            dict[f"Tag {i} weight"] = t.weight

        tracks = a.get_top_tracks(10)
        for i, t in enumerate(tracks, 1):
            dict[f"Top track {i}"] = t.item.title
            dict[f"Top track {i} weight"] = t.weight

        albums = a.get_top_albums(10)
        for i, t in enumerate(albums, 1):
            dict[f"Top album {i}"] = t.item.title
            dict[f"Top album {i} weight"] = t.weight

        similar = a.get_similar(50)
        for i, t in enumerate(similar, 1):
            dict[f"Similar artist {i}"] = t.item.name
            dict[f"Similar artist {i} match"] = t.match

        Path("Exports/Artists").mkdir(parents=True, exist_ok=True)

        dict_artists[index] = dict

        df_export = pd.DataFrame.from_dict(dict, orient='index')
        df_export.to_csv(f"Exports/Artists/{artist.replace('/', '_')}_information.csv", sep='\t')

    df_export_all = pd.DataFrame.from_dict(dict_artists, orient='index')
    df_export_all.to_csv(f"Exports/artists_information.csv", sep='\t')

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Extract information from artists from a timeline or from a list')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-f', '--file', help='File containing the timeline to extract the unique artists from', type=str)
    parser.add_argument('-a', '--artist', help='Artists (separated by comma)', type=str)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
