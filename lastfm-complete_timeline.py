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


def fetch_new_tracks(user, min_timestamp=None, max_timestamp=None):
    complete_tracks = []
    # Can't do limit=None here, it throws an error after some time.
    new_tracks = user.get_recent_tracks(
        limit=100, time_from=min_timestamp, time_to=max_timestamp
    )
    complete_tracks = complete_tracks + new_tracks
    logger.info("%s tracks extracted.", len(complete_tracks))
    while new_tracks:
        last_timestamp = new_tracks[-1].timestamp
        logger.debug("Last timestamp : %s", last_timestamp)
        try:
            new_tracks = user.get_recent_tracks(
                limit=100, time_to=last_timestamp, time_from=min_timestamp
            )
            complete_tracks = complete_tracks + new_tracks
            logger.info("%s tracks extracted.", len(complete_tracks))
        except Exception as e:
            logger.error(e)
    return complete_tracks


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
        logger.info("Extracting complete timeline for %s.", user)
        user = network.get_user(user)
        if args.file:
            logger.info("Reading %s.", args.file)
            df_initial = pd.read_csv(args.file, sep="\t")
            df_initial = df_initial.astype({"Timestamp": int})
            logger.debug("Columns : %s", list(df_initial))
            # Getting the timestamp of the most recent scrobble
            max_timestamp = df_initial["Timestamp"].max()
            logger.info("Extracting scrobbles since %s.", max_timestamp)

            complete_tracks = fetch_new_tracks(
                user, min_timestamp=max_timestamp
            )
            logger.debug("Length complete_tracks : %s", len(complete_tracks))
        else:
            complete_tracks = fetch_new_tracks(user)

        timeline = []
        for new_track in complete_tracks:
            dict_track = {
                "Artist": new_track.track.artist,
                "Album": new_track.album,
                "Title": new_track.track.title,
                "Date": new_track.playback_date,
                "Timestamp": new_track.timestamp,
            }
            timeline.append(dict_track)

        logger.debug("Creating final dataframe")
        df = pd.DataFrame.from_records(timeline)
        df = df.astype({"Timestamp": int})
        if args.file:
            df = pd.concat([df, df_initial], ignore_index=True, sort=True)

        df = df.sort_values(by=["Timestamp"])
        max_timestamp = df["Timestamp"].max()

        export_filename = (
            f"Exports/complete_timeline_{user}_{max_timestamp}.csv"
        )
        logger.info("Exporting timeline to %s.", export_filename)
        df.to_csv(
            export_filename,
            sep="\t",
            index=False,
            columns=["Title", "Artist", "Album", "Date", "Timestamp"],
        )

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract complete or partial lastfm timeline from one or several lastfm users."
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
        "--file",
        "-f",
        help="File already containing a timeline (to be used with only one user).",
        type=str,
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
