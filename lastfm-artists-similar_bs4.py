import time
import argparse
import logging
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from pathlib import Path

logger = logging.getLogger()

temps_debut = time.time()


def get_artists(soup):
    artists = []
    for item in soup.findAll("h3", {"class": "similar-artists-item-name"}):
        artists.append(item.find("a").text)
    return artists


def main():
    args = parse_args()
    if not args.artists:
        raise Exception("Use the -a flag to input a artist to scrap.")
    artists = [x.strip() for x in args.artists.split(",")]

    Path("Exports").mkdir(parents=True, exist_ok=True)

    for artist in tqdm(artists, dynamic_ncols=True):
        try:
            url = f"https://www.last.fm/music/{artist}/+similar"
            soup = BeautifulSoup(requests.get(url).content, "lxml")
            artists = []

            while soup.find("li", {"class": "pagination-next"}):

                artists = artists + get_artists(soup)
                logger.debug("Total artists number : %s", len(artists))
                lien = soup.find("li", {"class": "pagination-next"}).find("a")[
                    "href"
                ]
                logger.debug("Next page : %s/{lien}", url)
                soup = BeautifulSoup(
                    requests.get(f"{url}/{lien}").content, "lxml"
                )
            with open(f"Exports/{artist}_similar-artists_bs4.csv", "w") as f:
                for artist in artists:
                    f.write(f"{artist}\n")
        except Exception as e:
            logger.error("%s", e)

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description="artist lastfm scraper.")
    parser.add_argument(
        "--debug",
        help="Display debugging information.",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-a",
        "--artists",
        type=str,
        help="artists to scrap (separated by comma).",
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
