import pylast
import configparser
import logging
import time
import argparse
import pandas as pd
import requests
import time
from tqdm import tqdm
from pathlib import Path
from bs4 import BeautifulSoup

logger = logging.getLogger()
temps_debut = time.time()


def lastfmconnect():
    config = configparser.ConfigParser()
    config.read("config.ini")
    api_key = config["lastfm"]["api_key"]
    api_secret = config["lastfm"]["api_secret"]
    username = config["lastfm"]["username"]
    password = pylast.md5(config["lastfm"]["password"])

    network = pylast.LastFMNetwork(
        api_key=api_key,
        api_secret=api_secret,
        username=username,
        password_hash=password,
    )
    return network


def get_country(url_artist):
    soup = BeautifulSoup(requests.get(url_artist).content, "lxml")
    place = soup.find("dt", string="Founded In")
    if place:
        place = place.findNext().text
    else:
        place = soup.find("dt", string="Born In")
        if place:
            place = place.findNext().text
        else:
            place = None
    if place:
        return place.split(", ")[-1]
    return None


def main():
    args = parse_args()
    if not args.file and not args.artist:
        raise Exception(
            "Use the -f/--file or the -a/--artist flags to input one or several artists to search."
        )

    network = lastfmconnect()

    if args.artist:
        artists = [x.strip() for x in args.artist.split(",")]
    else:
        df = pd.read_csv(args.file, sep="\t", encoding="utf-8")
        logger.debug(df.columns)
        artists = df.Artist.unique()
    n_artists = len(artists)
    logger.debug("Number of artists : %s", n_artists)

    Path("Exports/Artists").mkdir(parents=True, exist_ok=True)

    list_dict = []
    for artist in tqdm(artists, total=n_artists, dynamic_ncols=True):
        dict = {}
        n_tries = 0
        while True:
            try:
                n_tries += 1
                a = network.get_artist(artist)
                dict["Name"] = a.get_name()
                dict["URL"] = a.get_url()
                dict["Listeners"] = int(a.get_listener_count())
                dict["Playcount"] = int(a.get_playcount())
                dict["Country"] = get_country(dict["URL"])
                break
            except Exception as e:
                logger.warning(f"{artist} try {n_tries}: {e}.")
                time.sleep(3)
                if n_tries > 4:
                    break
        logger.debug(dict)
        list_dict.append(dict)

        # tags = a.get_top_tags(20)
        # for i, t in enumerate(tags, 1):
        #     dict[f"Tag {i}"] = t.item.name
        #     dict[f"Tag {i} weight"] = t.weight

        # tracks = a.get_top_tracks(10)
        # for i, t in enumerate(tracks, 1):
        #     dict[f"Top track {i}"] = t.item.title
        #     dict[f"Top track {i} weight"] = t.weight

        # albums = a.get_top_albums(10)
        # for i, t in enumerate(albums, 1):
        #     dict[f"Top album {i}"] = t.item.title
        #     dict[f"Top album {i} weight"] = t.weight

        # similar = a.get_similar(50)
        # for i, t in enumerate(similar, 1):
        #     dict[f"Similar artist {i}"] = t.item.name
        #     dict[f"Similar artist {i} match"] = t.match

        # # Export csv containing data for the artist.
        # df_export = pd.DataFrame.from_dict(dict, orient="index")
        # df_export.to_csv(
        #     f"Exports/Artists/{artist.replace('/', '_')}_infos.csv",
        #     sep="\t",
        # )

    # Export csv containing data for all the artists.
    pd.DataFrame.from_records(list_dict).to_csv(
        f"Exports/complete_artists_infos.csv", sep="\t", index=False
    )

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract infos from artists from a timeline or from a list."
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information.",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "-f",
        "--file",
        help="File containing the timeline to extract the unique artists from.",
        type=str,
    )
    parser.add_argument(
        "-a", "--artist", help="Artists (separated by comma).", type=str
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
