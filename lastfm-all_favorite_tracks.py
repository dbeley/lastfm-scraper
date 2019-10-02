import pylast
import configparser
import logging
import time
import argparse
import pandas as pd
from pathlib import Path

logger = logging.getLogger()
temps_debut = time.time()


def lastfmconnect():
    config = configparser.ConfigParser()
    config.read("config.ini")
    api_key = config["lastfm"]["api_key"]
    api_secret = config["lastfm"]["api_secret"]
    api_username = config["lastfm"]["username"]
    api_password = pylast.md5(config["lastfm"]["password"])

    network = pylast.LastFMNetwork(
        api_key=api_key,
        api_secret=api_secret,
        username=api_username,
        password_hash=api_password,
    )
    return network


def main():
    args = parse_args()
    network = lastfmconnect()
    if args.username:
        users = [x.strip() for x in args.username.split(",")]
    else:
        logger.error("Use the -u/--username flag to set an username.")
        exit()

    Path("Exports").mkdir(parents=True, exist_ok=True)

    for user in users:
        logger.info("Extracting favorite tracks for %s.", user)
        user = network.get_user(user)

        loved_tracks = user.get_loved_tracks(limit=None)
        loved_tracks = [x.track for x in loved_tracks]
        logger.info("%s tracks extracted for %s.", len(loved_tracks), user)

        with open(f"Exports/{user}_favorite_tracks.csv", "w") as f:
            for track in loved_tracks:
                f.write(f"{track.artist} - {track.title}\n")

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract all favorite tracks from one or several lastfm users."
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
        "--username",
        "-u",
        help="Names of the users (separated by comma).",
        type=str,
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
