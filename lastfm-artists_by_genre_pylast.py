import pylast
import configparser
import logging
import time
import argparse
from pathlib import Path
from tqdm import tqdm

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
    if not args.genres:
        logger.error("Use the -g flag to input a genre to scrap.")
        exit()
    genres = args.genres.split(',')

    network = lastfmconnect()

    for genre in tqdm(genres, dynamic_ncols=True):
        try:
            artists = [x.item.name for x in network.get_tag(genre).get_top_artists(limit=1000)]

            Path("Exports").mkdir(parents=True, exist_ok=True)
            with open(f"Exports/{genre}_pylast.txt", 'w') as f:
                for artist in artists:
                    f.write(f"{artist}\n")
        except Exception as e:
            logger.error("%s", e)

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Python skeleton')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    parser.add_argument('-g', '--genres', type=str, help='Genres to scrap (separated by comma)')
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
