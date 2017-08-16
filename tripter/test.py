import tweepy
from instagram.client import InstagramAPI
from secrets import *
from utils import *

import urllib.request
import shutil
import logging, traceback, unicodedata, re, os, sys
logger = logging.getLogger("tripter.log")
handler = logging.FileHandler("tripter.log")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


filename = unicodedata.normalize('NFKD', 'tripter_read' + timestamp).encode('ascii', 'ignore').decode('ascii')
# readout_file = slugify('tripter_read' + timestamp) + '.txt'
readout_file = re.sub('[^\w\s-]', '', filename).strip().lower() + '.txt'



auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)

twitter_api = tweepy.API(auth)
ig_self_api = InstagramAPI(access_token=IG_A_TOKEN, client_secret=IG_SECRET)
ig_api = InstagramAPI(access_token=IG_A_TOKEN_3, client_secret=IG_SECRET)

#twitter_api.retweets_of_me(since_id, max_id, count, page)
#twitter_api.status_lookup(id, include_entities, trim_user, map)
#twitter_api.home_timeline(since_id, max_id, count, page)

# Generate tweet text
tweet_text = ''
tweet_text_output = os.path.join('txt', date + '__generated_tweet_text.txt') #TODO: append image name or id when dealing with multiple posts

#TODO: add countdown or "hours until" for tweet text (just cuz it'd be cool)
#TODO: make hashtag lookup, creator for generator --> this will also help with sorting pulled hashtags from IG by popularity!
#TODO: Add spell/grammar checker, twitter botting ettiqute rules

#TODO: look into getting triggered by live notification --> possibly using Nightbot or another bot?


# Get game info from file or prompt
info_file = "info.txt"
parsed_time = ''
try:
    if os.path.exists(info_file):
        read_file = open(info_file, 'r')
        for line in read_file:
            if line.lower().startswith('$game_tag='):
                game_tag = line.lower().replace('$game_tag=', '').strip()
                # game_tag = "darksouls3"
                # game_tag = "assassinscreedsyndicate"
                print("Found game tag: %s" % game_tag)####
            elif line.lower().startswith('$req_tags='):
                parsed_tags = line.lower().replace('$req_tags=', '').replace(', ', ',').split(',')
                req_tags += parsed_tags
                # req_tags = ['twitch', 'letsplay', 'darksouls', 'ds3', 'ps4']
                # req_tags = ['twitch', 'letsplay', 'syndicate', 'ps4']
                print("Found required tags. Full list is now: %s" % req_tags)  ####
            elif line.lower().startswith('$rem_tags='):
                parsed_tags = line.lower().replace('$rem_tags=', '').replace(', ', ',').split(',')
                rem_tags += parsed_tags
                print("Found tags to remove. Full list is now: %s" % rem_tags)  ####
            elif line.lower().startswith('$time='):
                parsed_time = line.lower().replace('$time=', '').strip()
                print("Found time: %s" % parsed_time)  ####
            else:
                print("No match for line: %s" % line)
        read_file.close()
except Exception as e:
    print("Error reading info file! Exception: %s" % e)

if game_tag == '':
    game_tag = input("Enter game tag: \n").lower().strip()

# Get content from IG through webscraper

# user_results, next_ = ig_api.user_search(q=ig_bot_user, count=1)
# print(user_results)


# Get content from IG
# https://www.instagram.com/developer/
recent_media, next_ = ig_api.user_recent_media(user_id=ig_src_id, count=5)
img_count = 1
ig_img_paths = []

# with open('IG_OUTPUT.TXT', 'a', encoding='utf-8') as fp:
for media in recent_media:

    #TODO: add 'if image posted today' condition here
    # if media.created_time.strftime('%Y_%m_%d') == date:

    #Image object - url, height, width
    std_res_img = media.get_standard_resolution_url()
    low_res_img = media.get_low_resolution_url()
    thumb_img = media.get_thumbnail_url()

    #media.images['standard_resolution']
    #media.images['low_resolution']
    #media.images['thumbnail']
    #For videos: media.videos['...']

    # Check tags for target
    tags = []
    found_tag = False
    for tag in media.tags:
        # Remove tags we're adding manually later and tags we want removed
        if (tag.name.lower() not in req_tags) and (tag.name.lower() not in rem_tags):
            tags.append(tag.name)
        if tag.name.lower() == target_tag.lower():
            print("Found image!")
            found_tag = True

    if found_tag:
        # Check image name
        if os.path.exists(image_file_path):
            print("\t\t\nExisting image for %s!" % image_file_path)
            # image_file_path = image_file_path.replace('.jpg', '__IG_' + img_count + '.jpg')

        # Download image from URL
        try:
            urllib.request.urlretrieve(std_res_img, image_file_path)
            # # Download the file from `url`, save it in a temporary directory and get the
            # # path to it (e.g. '/tmp/tmpb48zma.txt') in the `file_name` variable:
            # ig_img_file, headers = urllib.request.urlretrieve(url)

            # Download the file from `url` and save it locally under `ig_img_file`:
            # with urllib.request.urlopen(url) as response, open(ig_img_file, 'wb') as out_file:
            #     shutil.copyfileobj(response, out_file)

            ig_img_paths.append(image_file_path)
            img_count += 1
        except Exception as e:
            print("Failed to download image from IG! -- %s" % e)

        # Get caption text
        caption_text = media.caption.text

        ######
        # Parse caption text
        caption_text = parse_text_from_caption(caption_text, parsed_time)


        ### see utils.py for other fixes ###

        # TODO: trim function for different social medias
        if len(caption_text) > 140:
            print("\n\n\tCaption from IG is too long...\n\tLet's try to shorten it!\n")
            with open('IG_OUTPUT.TXT', 'a', encoding='utf-8') as fp:
                fp.write('full caption:%s\n\nShortened (%s): %s\n-------------\n' % (caption_text, len(caption_text[:140]),caption_text[:140]))
            fp.close()

        else:
            print("Caption length is OK! Let's add tags...")
            # First add game tag
            if (len(caption_text) + len(game_tag)) + 2 <= 140:
                caption_text = caption_text + ' #' + game_tag
            else:
                print("\n\t\t ! The tweet is a bit too long to add the tag for the game name... I suggest you change it a bit.")

            # Start by adding the necessary tags
            for tag in req_tags:
                if (len(caption_text) + len(tag)) + 2 <= 140: # +2 because space and hashtag
                    caption_text = caption_text + ' #' + tag

            # Sort tags by size
            tags = sorted(tags, key=lambda x: len(x))
            #TODO: sort tags by popularity???

            if len(caption_text) < 140:
                for tag in tags:
                    if (len(caption_text) + len(tag)) + 2 <= 140:
                        caption_text = caption_text + ' #' + tag
            else:
                print("Ran out of space for tags...")
            print('You can see the results in the output file! ^^ \n\n')

            with open(tweet_text_output, 'a', encoding='utf-8') as fp:
                fp.write('Original text: %s\n\n-----\nfull caption [%s chars]:%s\n-------------\n' % (media.caption.text, len(caption_text), caption_text))

            tweet_text = caption_text #TODO: move this to approval area?
        ############
        # Send Tweet
        if os.path.exists(image_file_path):
            print("Attaching image for tweet: %s\n" % image_file_path)

            tweet_ok = False
            if approval_required:
                resp = input("The tweet will be sent with text in '%s' and image '%s'.\nIs this ok? (y/n)\n" % (tweet_text_output, image_file_path))
                if resp.lower().startswith('y'):
                    tweet_ok = True
                    print("\nOK! Great :D")
            else:
                tweet_ok = True

            if tweet_ok:
                print("I will go ahead and send this!")
                imgfile = open(image_file_path, 'r')
                print("\nTweeting status...")
                twitter_api.update_with_media(image_file_path, tweet_text, imgfile)
                imgfile.close()
            else:
                #TODO: return function to do corrections, add manual/edit text for tweet (read from same file), add manual image for tweet
                print("\n\nI'm sorry... Let's fix it.")
        else:
            # TODO: update_status without media here
            # http://docs.tweepy.org/en/v3.5.0/api.html?highlight=update_status
            resp = ("The image '%s' for the tweet is missing.\nShould I send it without the image? (y/n)\n")
            if resp.lower().startswith('y'):
                print("OK! (but for now that's not working so i'll just... move on...)")
        ################
        # Break Loop
        break

#####################
# Forward Post to IG
# resp = ("Would you like me to repost this to another account? (y/n)\n")
# if resp.lower().startswith('y'):
#     print("OK! (but for now that's not working so i'll just... move on...)")
# ig_self_api
# ig_bot_api = InstagramAPI(access_token=IG_A_TOKEN_3, client_secret=IG_SECRET)


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

def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            time.sleep(15 * 60)

#TODO: add rate limiter
# http://docs.tweepy.org/en/v3.5.0/api.html?#tweepy-error-exceptions

print("\nDone!")
sys.exit()

# for follower in tweepy.Cursor(twitter_api.followers).items():
#     follower.follow()

#
# for follower in limit_handled(tweepy.Cursor(twitter_api.followers).items()):
#     if follower.friends_count < 300:
#         print(follower.screen_name)