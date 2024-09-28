import pylast
import configparser
import logging
import time
import argparse
from pathlib import Path
from wordcloud import WordCloud

logger = logging.getLogger()
temps_debut = time.time()

NUM_ARTISTS = 50
NUM_TAGS = 10
FORBIDDEN_TAGS = ["seen live", "lo-fi", "british", "alternative", "rock", "indie", "pop", "80s", "70s", "90s", "60s", "piano", "kicksastic", "ecm", "french", "manchester", "female vocalists", "canadian", "swedish", "trumpet", "the beatles", "japanese", "spiritual", "american", "acoustic", "psychedelic", "shibuya-key", "usa", "pennsylvania", "oldies", "japanese city pop", "philadelphia", "france", "instrumental", "j-indie", "new york", "uk", "00s", "10s", "20s"]

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
    if not args.username:
        raise Exception("Use the -u/--username flag to set an username.")
    users = [x.strip() for x in args.username.split(",")]

    Path("Exports").mkdir(parents=True, exist_ok=True)

    dict_frequencies = {}
    for user in users:
        logger.info("Extracting favorite tracks for %s.", user)
        user = network.get_user(user)

        top_artists = user.get_top_artists(period=args.timeframe)
        for top_item in top_artists[0:NUM_ARTISTS]:
            logger.info("Getting top tags for %s.", top_item.item.name)
            top_tags = top_item.item.get_top_tags()
            top_tags = [top_tag for top_tag in top_tags if top_tag.item.name.lower() not in FORBIDDEN_TAGS]
            # filter word I don't want
            for top_tag in top_tags[0:NUM_TAGS]:
                if top_tag.item.name in dict_frequencies:
                    dict_frequencies[top_tag.item.name] += int(top_item.weight) * int(top_tag.weight)
                else:
                    dict_frequencies[top_tag.item.name] = int(top_item.weight) * int(top_tag.weight)

        wordcloud = WordCloud().generate_from_frequencies(dict_frequencies)
        import matplotlib.pyplot as plt
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.show()


    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Create a wordcloud of the genres listened by one or several lastfm users."
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
        help="Usernames, separated by comma.",
        type=str,
    )
    parser.add_argument(
        "--timeframe",
        "-t",
        help="Timeframe (Accepted values : 7day, 1month,\
                              3month, 6month, 12month, overall.\
                              Default : 7day).",
        type=str,
        default="1month",
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
