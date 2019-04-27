import pylast
import configparser
import logging
import time
import argparse
import os
import errno
from tqdm import tqdm

logger = logging.getLogger()
temps_debut = time.time()


def main():
    args = parse_args()

    config = configparser.ConfigParser()
    config.read('config.ini')
    API_KEY = config['lastfm']['API_KEY']
    API_SECRET = config['lastfm']['API_SECRET']
    username = config['lastfm']['username']
    password = pylast.md5(config['lastfm']['password'])

    network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                                   username=username, password_hash=password)

    user = network.get_user(username)
    new_tracks = user.get_recent_tracks(limit=100)
    tracks = new_tracks
    logger.debug(f"Length tracks : {len(tracks)}")
    while new_tracks:
        last_timestamp = new_tracks[-1].timestamp
        logger.debug(f"Last timestamp : {last_timestamp}")
        try:
            new_tracks = user.get_recent_tracks(limit=100, time_to=last_timestamp)
            tracks = tracks + new_tracks
        except Exception as e:
            logger.error(e)
        logger.debug(f"Length tracks : {len(tracks)}")

    try:
        os.makedirs('Exports')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    with open(f"Exports/complete_timeline_{username}.txt", 'w') as f:
        f.write(f"Artist\tAlbum\tTitle\tDate\tTimestamp\n")
        logger.debug("Exporting timeline")
        for title in tqdm(tracks, dynamic_ncols=True):
            title_line = f"{title.track.artist}\t{title.album}\t{title.track.title}\t{title.playback_date}\t{title.timestamp}\n"
            f.write(title_line)

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Python skeleton')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
