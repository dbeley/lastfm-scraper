import time
import argparse
import logging
import requests
import os
import errno
from tqdm import tqdm
from bs4 import BeautifulSoup

logger = logging.getLogger()

temps_debut = time.time()


def get_artists(soup):
    artists = []
    for item in soup.findAll('h3', {'class': 'big-artist-list-title'}):
        artists.append(item.find('a').text)
    return artists


def main():
    args = parse_args()
    genres = args.genres
    if not genres:
        logger.error("Use the -g flag to input a genre to scrap.")
        exit()
    genres = genres.split(',')
    for genre in tqdm(genres, dynamic_ncols=True):
        try:
            url = f"https://www.last.fm/fr/tag/{genre}/artists"
            soup = BeautifulSoup(requests.get(url).content, 'lxml')
            artists = []

            while soup.find('li', {'class': 'pagination-next'}):

                artists = artists + get_artists(soup)
                logger.debug(f"Total artists number : {len(artists)}")
                lien = soup.find('li', {'class': 'pagination-next'}).find('a')['href']
                logger.debug(f"Next page : {url}/{lien}")
                soup = BeautifulSoup(requests.get(f"{url}/{lien}").content, 'lxml')

            try:
                os.makedirs('Exports')
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            with open(f"Exports/{genre}.txt", 'w') as f:
                for artist in artists:
                    f.write(f"{artist}\n")
        except Exception as e:
            logger.error(f"{e}")

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Genre lastfm scraper')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING)
    parser.add_argument('-g', '--genres', type=str, help='Genres to scrap (separated by comma)')
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
