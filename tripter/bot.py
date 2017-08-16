import tweepy
from instagram.client import InstagramAPI
from secrets import *
from datetime import datetime
import urllib.request
import shutil
import logging, traceback, unicodedata, re, os, sys
logger = logging.getLogger("tripter.log")
handler = logging.FileHandler("tripter.log")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# timestamp = str(datetime.now())
timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
date = datetime.now().strftime('%Y_%m_%d')
filename = unicodedata.normalize('NFKD', 'tripter_read' + timestamp).encode('ascii', 'ignore').decode('ascii')
# readout_file = slugify('tripter_read' + timestamp) + '.txt'
readout_file = re.sub('[^\w\s-]', '', filename).strip().lower() + '.txt'

image_file_path = os.path.join('img', 'stream_' + date + '.png')
info_file_path = os.path.join('txt', 'stream_info.txt')

auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)

twitter_api = tweepy.API(auth)
ig_api = InstagramAPI(access_token=IG_A_TOKEN, client_secret=IG_SECRET)

def get_post_from_ig():
    return post_img, post_text

def generate_text_from_plan(info_file_path):
    if os.path.exists(info_file_path):
        # TODO: add RE substitution text, read in text file, etc for generator
        stream_time = ''
        stream_game = ''
        stream_url = ''
        stream_hashtags = ''
        stream_extra_hashtags = []
        base_phrases = []
        stream_phrases = []
        with open(info_file_path) as fp:
            for line in fp:
                line = line.replace('\n', '')
                if line.startswith('$time='):
                    stream_time = line.replace('$time=','')
                    print('Stream time phrase set to: %s' % stream_time)####
                elif line.startswith('$game='):
                    stream_game = line.replace('$game=','')
                    print('Stream game phrase set to: %s' % stream_game)  ####
                elif line.startswith('$url='):
                    stream_url = line.replace('$url=','')
                    print('Stream url set to: %s' % stream_url)  ####
                elif line.startswith('$hashtags='):
                    stream_hashtags = line.replace('$hashtags=','')
                    print('Stream hasahtags set to: %s' % stream_hashtags)  ####
                elif line.startswith('$extra_hashtags='):
                    stream_extra_hashtags = line.replace('$extra_hashtags=','').split()
                    print('Stream extrahashtags found: %s' % stream_extra_hashtags)  ####
                elif line.strip() != '':
                    # If the line is not blank or whitespace only, save it as a phrase
                    base_phrases.append(line)
                    print('Base phrase found: %s' % line)  ####
        print("\nTotal base phrases found (%s)\n" % (len(base_phrases)))####

        # Set up phrases for RE testing
        output_file = open('generated_phrases_output.txt', "w", encoding='utf-8')####
        phrase_len = 140
        for phrase in base_phrases:
            tweet_text = phrase.replace('[time]', stream_time)
            tweet_text = tweet_text.replace('[game]', stream_game)
            tweet_text = tweet_text.replace('[url]', stream_url)
            tweet_text = tweet_text.replace('[hashtags]', stream_hashtags)

            # Check length before adding extra hashtags
            if len(tweet_text.replace('#', '')) < 140:
                for extra_hashtag in stream_extra_hashtags:
                    extra_hashtag = ' ' + extra_hashtag
                    if (len(tweet_text) + len(extra_hashtag)) < 140:
                        tweet_text += extra_hashtag
                    else:
                        print("\nSkipping tag '%s' as it cause the tweet to go over the text limit" % extra_hashtag)
            print("\n\nCompiled phrase [len: %s]: %s" % (len(tweet_text), tweet_text))####
            output_file.write('Phrase length %s \n%s\n----\n' % (len(tweet_text), tweet_text))####
            if len(tweet_text) < phrase_len:
                stream_phrases.append(tweet_text)
            else:
                print("Phrase is longer, so it won't be used: [len=%s] %s" % (len(tweet_text), tweet_text))
        output_file.close()####

        stream_phrases = sorted(stream_phrases, key=lambda x: len(x))
        tweet_text = stream_phrases[0] #select smallest
        # tweet_text = stream_phrases[len(stream_phrases-1)] #select largest

    print("\nGenerated text for tweet: %s\n" % tweet_text)

def send_tweet(image_file_path, tweet_text):
    # Send out tweet

    if os.path.exists(image_file_path):
        print("Found image for tweet: %s\n" % image_file_path)

        imgfile = open(image_file_path, 'r')
        print("\nTweeting status...")
        twitter_api.update_with_media(image_file_path, tweet_text, imgfile)
        imgfile.close()
    else:
        #TODO: update_status without media here
        # http://docs.tweepy.org/en/v3.5.0/api.html?highlight=update_status
        print("Send tweet without media")####


def get_all_tweets():
    public_tweets = twitter_api.home_timeline()
    if public_tweets:
        textfile = open(readout_file, "w", encoding='utf-8')
        for tweet in public_tweets:
            # print(tweet.text)
            print("Adding tweet to file")
            textfile.write(tweet.text)
            textfile.write("\n\n-------------------------------------------\n\n")
        textfile.close()
    else:
        print("No public tweets in timeline")


def slugify(value):
    try:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
    except Exception:
        logger.error("Could not slugify value [%s]: %s" % (value, traceback.format_exc()))
    return value

def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)

# --------------------------------------------------------- #

def main(argv):
    print("Hi! Let's see what you need me to do...\n")

    src_post = ''
    approval_required = True

    try:
        options, remainder = getopt.gnu_getopt(sys.argv[1:],'s:a:h',["src=","approval=", "help="])
    except getopt.GetoptError as e:
        print('Error getting args. Use -h or --help to see help.\nError: %s' % e)
        sys.exit(2)

    try:
        found_args = False
        for opt, arg in options:
            if opt in ("-h", "--help"):
                print('\n\nHere is the list of commands you can use on command line.\n'
                      'Example: python bot.py -s <instagram> -o <yes or true /no or false>\n'
                      'Options (None are mandatory):\n'
                      '-s, --src      - Source post (i.e. Download image and text from Instagram to post to Twitter). Values: twitter, facebook, instagram\n'
                      '-a, --approval    - Require approval before posting. Values: Yes/True or No/False\n'
                      '* Note: If no args, user will be prompted.\n\n')
                sys.exit()
            if opt in ("-s", "--src"):
                found_args = True
                print("Oh!")
                src_post = arg
            if opt in ("-a", "--approval"):
                print("Oh!")
                found_args = True
                if arg.lower().startswith('n') or arg.lower().startswith('f'):
                    approval_required = False

        if not found_args:
            print("There's no instructions in the commandline for me, so I will try to make a twitter post!")
    except Exception as e:
        print("Error loading presets: %s" % e)

if __name__ == "__main__":
    main(sys.argv[1:])

print("\n-----------------------------\n\nFinished!")
sys.exit()