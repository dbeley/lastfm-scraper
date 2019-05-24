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
    API_KEY = config["lastfm"]["API_KEY"]
    API_SECRET = config["lastfm"]["API_SECRET"]
    api_username = config["lastfm"]["username"]
    api_password = pylast.md5(config["lastfm"]["password"])

    network = pylast.LastFMNetwork(
        api_key=API_KEY,
        api_secret=API_SECRET,
        username=api_username,
        password_hash=api_password,
    )
    return network


def main():
    args = parse_args()
    network = lastfmconnect()
    if args.username:
        user = network.get_user(args.username)
    else:
        logger.error("Use the -u/--username flag to set an username.")
        exit()

    if args.file:
        df_initial = pd.read_csv(args.file, sep="\t")
        logger.debug("Columns : %s", list(df_initial))
        max_timestamp = df_initial["Timestamp"].astype(int).max()
        logger.debug("Maximum timestamp = %s", max_timestamp)
        # for small updates, limit=None works fine
        complete_tracks = user.get_recent_tracks(
            limit=None, time_from=max_timestamp
        )
        logger.debug("Length complete_tracks : %s", len(complete_tracks))
    else:
        complete_tracks = []
        # can't do limit=None here, it throws an error after some time
        new_tracks = user.get_recent_tracks(limit=100)
        complete_tracks = complete_tracks + new_tracks
        logger.debug("Length complete_tracks : %s", len(complete_tracks))
        while new_tracks:
            last_timestamp = new_tracks[-1].timestamp
            logger.debug("Last timestamp : %s", last_timestamp)
            try:
                new_tracks = user.get_recent_tracks(
                    limit=100, time_to=last_timestamp
                )
                complete_tracks = complete_tracks + new_tracks
                logger.debug(
                    "Length complete_tracks : %s", len(complete_tracks)
                )
            except Exception as e:
                logger.error(e)

    timeline = {}
    for index_timeline, new_track in enumerate(complete_tracks, 1):
        dict_track = {}
        dict_track["Artist"] = new_track.track.artist
        dict_track["Album"] = new_track.album
        dict_track["Title"] = new_track.track.title
        dict_track["Date"] = new_track.playback_date
        dict_track["Timestamp"] = new_track.timestamp
        timeline[index_timeline] = dict_track
        index_timeline += 1

    Path("Exports").mkdir(parents=True, exist_ok=True)

    logger.debug("Creating dataframe")
    df = pd.DataFrame.from_dict(timeline, orient="index")
    if args.file:
        df = pd.concat([df, df_initial], ignore_index=True, sort=True)

    max_timestamp = df["Timestamp"].astype(int).max()

    logger.debug("Exporting dataframe")
    df.to_csv(
        f"Exports/complete_timeline_{args.username}_{max_timestamp}.txt",
        sep="\t",
        index=False,
    )

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract complete or partial lastfm timeline from an user"
    )
    parser.add_argument(
        "--debug",
        help="Display debugging information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    parser.add_argument(
        "--file", "-f", help="File already containing a timeline", type=str
    )
    parser.add_argument("--username", "-u", help="Name of the user", type=str)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
