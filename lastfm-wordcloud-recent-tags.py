import pylast
import configparser
import logging
import time
import math
import argparse
from pathlib import Path
import random
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from wordcloud import WordCloud
from tqdm import tqdm

logger = logging.getLogger()
logging.getLogger("pylast").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
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


def custom_color_func(
    word, font_size, position, orientation, random_state=None, **kwargs
):
    # Normalize the font size to get a value between 0 and 1
    normalized_font_size = (
        font_size / 250
    )  # Adjust this based on the expected max font size
    normalized_font_size = min(
        max(normalized_font_size, 0), 1
    )  # Ensure it's within [0, 1]

    # Get the color from a matplotlib colormap
    color = cm.Blues(1 - normalized_font_size)
    return f"rgb({int(color[0] * 255)}, {int(color[1] * 255)}, {int(color[2] * 255)})"


def main():
    args = parse_args()
    network = lastfmconnect()
    if not args.username:
        raise Exception("Use the -u/--username flag to set an username.")
    users = [x.strip() for x in args.username.split(",")]

    Path("Exports").mkdir(parents=True, exist_ok=True)

    # Load the forbidden tags list
    forbidden_tags = [line.strip() for line in open("forbidden_tags.txt")]

    dict_frequencies = {}
    for user in users:
        logger.info("Computing word cloud for %s.", user)
        user = network.get_user(user)

        top_artists = user.get_top_artists(
            period=args.timeframe, limit=args.artists_count
        )
        for top_item in tqdm(top_artists, dynamic_ncols=True):
            top_tags = top_item.item.get_top_tags()
            top_tags = [
                top_tag
                for top_tag in top_tags
                if top_tag.item.name.lower() not in forbidden_tags
            ]
            for top_tag in top_tags[0 : args.top_tags_count]:
                top_tag_name = top_tag.item.name.lower()
                if top_tag_name in dict_frequencies:
                    dict_frequencies[top_tag_name] += int(top_item.weight) * int(
                        top_tag.weight
                    )
                else:
                    dict_frequencies[top_tag_name] = int(top_item.weight) * int(
                        top_tag.weight
                    )

        wordcloud = WordCloud(
            background_color="black",
            colormap="binary",
            width=2560,
            height=1440,
            prefer_horizontal=1.0,
        ).generate_from_frequencies(dict_frequencies)

        plt.figure()
        plt.imshow(
            wordcloud.recolor(color_func=custom_color_func, random_state=3),
            interpolation="bilinear",
        )
        plt.axis("off")
        plt.savefig(
            f"Exports/{user}_{int(time.time())}_{args.timeframe}.png",
            dpi=300,
            bbox_inches="tight",
            pad_inches=0,
        )

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
    parser.add_argument(
        "--artists_count",
        "-a",
        help="Number of artists to extract (default 10).",
        type=int,
        default=50,
    )
    parser.add_argument(
        "--top_tags_count",
        "-g",
        help="Number of top tags to take into account by artist (default 4).",
        type=int,
        default=4,
    )
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
