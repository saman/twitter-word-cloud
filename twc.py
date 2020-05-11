from matplotlib.cbook import get_sample_data
import argparse
import twint
from string import punctuation
import pandas as pd
from hazm import *
from wordcloud import WordCloud
import re
import sys
from PIL import Image
import numpy as np
from os import path
import stopwords
from collections import Counter
import os
from random import randint
from arabic_reshaper import arabic_reshaper
from bidi.algorithm import get_display
import json


punctuation_list = list(punctuation)

parser = argparse.ArgumentParser(description='Twitter word cloud generator')
parser.add_argument("-u", "--username", help="twiter username", required=True)
parser.add_argument("-f", "--font", help="font name")
parser.add_argument(
    "-c", "--count", help="Number of words to show on word cloud image")
parser.add_argument("-l", "--limit", help="Number of tweets to pull")
parser.add_argument("-i", "--input", help="input twitter archive csv file")

username = ""
max_words = 200
tweets_file_path = ""
tweets_archive_file_path = ""
image_file_path = ""
limit = None
font_name = ""
output_dir = "output"
fonts_dir = "fonts"
image_file_extension = '.png'


def select_a_font():
    if font_name is not None and os.path.isfile(os.path.join(fonts_dir, font_name)):
        return os.path.join(fonts_dir, font_name)

    fonts = [file_name for file_name in os.listdir(
        fonts_dir) if os.path.isfile(os.path.join(fonts_dir, file_name)) and file_name.endswith(".ttf")]
    if len(fonts) > 0:
        font_index = randint(0, len(fonts)-1)
        return os.path.join(fonts_dir, fonts[font_index])
    return ""

def fix_date(x):
    return pd.to_datetime(x).strftime("%Y-%m-%d")

def export_archive_tweets():
    fo = open(tweets_archive_file_path, '+r')
    json_content = fo.read()
    fo.close()
    json_content = json_content.replace('window.YTD.tweet.part0 =', '')
    data_json = json.loads(json_content)
    data = pd.json_normalize(data_json)
    data.rename(columns = {'tweet.full_text':'tweet'}, inplace = True)

    data.insert(len(data.columns), 'date', '')
    data['date'] = data['tweet.created_at'].apply(lambda x: fix_date(x))
    data.to_csv(tweets_file_path, index=False, encoding='utf-8')

def export_tweets():
    if os.path.isfile(tweets_file_path):
        print(f"{tweets_file_path} is found and it will be processed.")
        print("If you want to get tweets from twitter, remove this file")
        return

    if os.path.isfile(tweets_archive_file_path):
        print(f"{tweets_archive_file_path} is found as archive and it will be processed.")
        print("If you want to get tweets from twitter archive file, remove the --input (-i) argument")
        return export_archive_tweets()

    c = twint.Config()

    if limit is not None:
        c.Limit = limit

    c.Username = username
    c.Store_csv = True
    c.Format = "Username: {username} |  Date: {date} {time}"
    c.Output = tweets_file_path
    twint.run.Search(c)

# remove links from tweet text


def remove_links(tweet):
    return re.sub(
        r'(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})\S*', '', tweet)


def remove_mentions(tweet):
    return re.sub(r'@\w*', '', tweet)


def remove_reserved_words(tweet):
    return re.sub(r'^(RT|FAV)', '', tweet)

# remove enoji and some unicode chars from tweet text


def remove_emoji(tweet):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u'\U00010000-\U0010ffff'
                               u"\u200d"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\u3030"
                               u"\ufe0f"
                               u"\u2069"
                               u"\u2066"
                               u"\u2068"
                               u"\u2067"
                               "]+", flags=re.UNICODE)

    return emoji_pattern.sub(r'', tweet)

def remove_punctuations(tweet):
    return re.sub(
        r'''[!()-\[\]{};:'"\,<>.\/?؟@#$%^&*_~=\\|`]''', '', tweet)

# preprocess tweet text (remove links, stopwords, images, mentions and numbers form tweets text )


def clean_tweet(tweet):
    tweet = str(tweet)
    tweet = tweet.lower()
    # remove # so we preserve hashtags for the cloud
    tweet = tweet.replace("#", "")
    # remove RT which is the sign of retweet
    tweet = tweet.lstrip("rt ")
    tweet = remove_links(tweet)
    tweet = remove_mentions(tweet)
    tweet = remove_emoji(tweet)
    tweet = remove_punctuations(tweet)
    tweet = remove_reserved_words(tweet)
    normalizer = Normalizer()
    tweet = normalizer.normalize(tweet)
    # removes verbs such as می‌شود or نمی‌گویند
    tweet = re.sub(r'ن?می[‌]\S+', '', tweet)
    tokens = word_tokenize(tweet)
    tokens = [token for token in tokens if not token.isdigit()]
    tokens = [token for token in tokens if token not in stopwords.persian]
    tokens = [token for token in tokens if token not in stopwords.english]
    return " ".join(tokens).strip()

# draw word cloud from tweets with persian word cloud
# persian word cloud repo: https://github.com/mehotkhan/persian-word-cloud


def draw_cloud(cleantweets, image_path, monthly=False ,show_image=False):
    text = " ".join(str(tweet) for tweet in cleantweets)
    text = get_display(arabic_reshaper.reshape(text))
    tokens = word_tokenize(text)
    dic = Counter(tokens)
    print(dic.most_common(max_words))
    twitter_mask = np.array(Image.open("twitter-logo.png"))
    font_path = select_a_font()
    words = max_words
    if monthly:
        words = max_words // 2
    wordcloud = WordCloud(
        font_path=font_path,
        max_words=words,
        margin=0,
        width=5000,
        height=5000,
        min_font_size=4,
        max_font_size=700,
        background_color="white",
        mask=twitter_mask
    )
    wordcloud.generate_from_frequencies(dic)

    image = wordcloud.to_image()
    wordcloud.to_file(image_path)
    if show_image:
        image.show()
    print(f"Generated image {image_path}")


def check_dir(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def generate_word_cloud():
    export_tweets()

    if not os.path.isfile(tweets_file_path):
        print("couldn't get tweets, please try again")
        return False
    data = pd.read_csv(tweets_file_path)

    tweet_col = 11

    if 'clean_tweet' not in data.columns:
        data.insert(len(data.columns), 'clean_tweet', '')
        data['clean_tweet'] = data['tweet'].apply(lambda x: clean_tweet(x))

    years = data['date'].str[0: 4].unique()
    global output_dir
    output_dir = os.path.join(output_dir, username)
    check_dir(output_dir)

    yearly_image_path = os.path.join(output_dir, "yearly")
    check_dir(yearly_image_path)

    monthly_image_path = os.path.join(output_dir, "monthly")
    check_dir(monthly_image_path)

    # genarate yearly word cloud
    for year in years:
        year_data = data[data['date'].str[0: 4] == year]
        image_path = os.path.join(yearly_image_path, year+image_file_extension)
        draw_cloud(year_data.clean_tweet.values, image_path)

        # genarate monthly word cloud
        months = year_data['date'].str[0: 7].unique()
        for month in months:
            month_data = year_data[year_data['date'].str[0: 7] == month]
            image_path = os.path.join(
                monthly_image_path, month+image_file_extension)
            draw_cloud(month_data.clean_tweet.values, image_path, True)

    image_path = os.path.join(output_dir, username+image_file_extension)
    draw_cloud(data.clean_tweet.values, image_path, False, True)


def main():
    global username
    global max_words
    global tweets_file_path
    global image_file_path
    global limit
    global font_name
    global tweets_archive_file_path

    args = parser.parse_args()
    username = args.username

    check_dir(output_dir)

    if args.count is not None and args.count.isnumeric():
        max_words = int(args.count)

    limit = args.limit
    font_name = args.font

    if (args.input is not None):
        tweets_archive_file_path = args.input

    tweets_file_path = os.path.join(output_dir, f"{username}.csv")

    generate_word_cloud()


if __name__ == "__main__":
    main()
