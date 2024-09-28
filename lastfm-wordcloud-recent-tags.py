import pylast
import configparser
import logging
import time
import math
import argparse
from pathlib import Path
import random
import matplotlib.pyplot as plt
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


# Custom color function to adjust brightness based on the word size
def bright_color_func(
    word, font_size, position, orientation, random_state=None, **kwargs
):
    # Generate a brighter color for larger words (higher font_size)
    brightness = int(255 * (font_size / 200))  # Adjust this range as needed
    r = random.randint(brightness, 255)  # Random but brighter
    g = random.randint(brightness, 255)
    b = random.randint(brightness, 255)
    return f"rgb({r}, {g}, {b})"


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
            # filter tags I don't want
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

        # wordcloud = WordCloud().generate_from_frequencies(dict_frequencies)
        # plt.imshow(wordcloud, interpolation='bilinear')

        # Create a word cloud with specified settings
        wordcloud = WordCloud(
            background_color="black",  # Set background color to black
            colormap="Greys",  # Use a vibrant colormap
            width=2560,  # Width of the image
            height=1440,  # Height of the image
            # max_words=50,              # Limit to 50 words
            # contour_color='white',     # Contour color for detail
            # contour_width=1,           # Width of the contour
            prefer_horizontal=1.0,  # Prefer horizontal words
        ).generate_from_frequencies(dict_frequencies)

        # Display the word cloud using matplotlib
        # plt.figure(figsize=(10, 5))
        plt.figure()
        # plt.imshow(wordcloud, interpolation="bilinear")
        plt.imshow(
            wordcloud.recolor(color_func=bright_color_func, random_state=3),
            interpolation="bilinear",
        )
        plt.axis("off")
        # plt.tight_layout()
        # plt.show()
        plt.savefig(
            f"Exports/{user}_{int(time.time())}_{args.timeframe}.png",
            dpi=300,
            bbox_inches="tight",
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
