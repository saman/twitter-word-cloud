# Twitter Word Cloud

A tool to generate word cloud images from twitter user timeline and twitter archive data.

# Requirements :

- <a href="https://github.com/twintproject/twint">TWINT - Twitter Intelligence Tool</a>
- <a href="https://github.com/sobhe/hazm">Hazm</a>
- <a href="https://github.com/amueller/word_cloud">Word Cloud generator</a>
- <a href="https://github.com/pandas-dev/pandas">Pandas</a>

# how to run :
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install --upgrade pip`
- `pip install -r requirements.txt` (Install dependencies)
- `python twc.py -u twitter_username` - Scrape all the Tweets from user's timeline and genarate word cloud images. You can find images in this path `output/twitter_username/`.
- `python twc.py -u twitter_username -c 100` - Scrape all the Tweets from user's timeline and genarate word cloud images with 100 words.
- `python twc.py -u twitter_username -f "XB Zar.ttf"` - Scrape all the Tweets from user's timeline and use "XB Zar.ttf" font on the image. Yon can find fonts in the `fonts` folder.

# Using Twitter Archive Data
You can use this feature if you have a private account or you need to compute all of your tweets from twitter archive data.
- First download your [Twitter data](https://twitter.com/settings/your_twitter_data).
- Pass the path of `tweet.js` file as --input or -i argument
- `python twc.py -u twitter_username -i /Users/saman/Downloads/twitter-2020-05-11/data/tweet.js`

# Sample Output:

![Sample Result](irLinja.png?raw=true)
