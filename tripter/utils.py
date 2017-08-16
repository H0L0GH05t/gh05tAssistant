import logging, traceback, unicodedata, re, os, sys
from datetime import datetime
logger = logging.getLogger("tripter.log")
handler = logging.FileHandler("tripter.log")
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Globals
# timestamp = str(datetime.now())
timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
date = datetime.now().strftime('%Y_%m_%d')

image_file_path = os.path.join('img', 'stream_' + date + '.jpg')
info_file_path = os.path.join('txt', 'stream_info.txt')
target_tag = "twitch"
game_tag = ""
# game_tag = "darksouls3"
# game_tag = "assassinscreedsyndicate"
# req_tags = ['twitch', 'letsplay', 'darksouls', 'ds3', 'ps4']
# req_tags = ['twitch', 'letsplay', 'syndicate', 'ps4']
req_tags = ['twitch', 'letsplay', 'ps4'] #TODO: get game name from other places (i.e. games list), compare to pulled post tags
rem_tags = ['cosplay', 'cosplaying', 'costume', 'costuming'] #TODO: get automatically or read from file
IG_user_name = 'shapeshiftercosplay'
USER_NAME = 'Shapeshifter'
ig_bot_user = 'h0l0gh05t_b0t'
approval_required = True
# ig_src_id = 'self'
ig_src_id = '50374654'



# Regex patterns
re_tagged_user = r'\s+@(?P<user>\S+)' # Looks for space before @ and non-space characters after until the next space
re_time = r'(?P<day>\S+)\s+(@\s+)(?P<time>\d+:\d+(pm|am)) PST' # <day> @ <time> PST
re_url = r'(?P<url>Twitch+\.tv/\S+)' #TODO: named group not needed, make more universal for other urls

def slugify(value):
    try:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
    except Exception:
        logger.error("Could not slugify value [%s]: %s" % (value, traceback.format_exc()))
    return value

def trim_text_for_post(caption_text):
    # Trim for different social media length constraints
    return caption_text

def clean_text(caption_text, tagged_users, parsed_time, cap_day, cap_time, cap_url):
    # Clean caption text
    # caption_text = caption_text.split('\n_')[0]
    caption_text = re.split(r'\s_+\s', caption_text)[0]  # split on 1 white space, 1 or more underscore, followed by 1 whitespace
    caption_text = caption_text.replace('\n', '')
    caption_text = re.sub(r'[^\x00-\x7F]+', '', caption_text)  # removed non-ascii characters

    if tagged_users:
        for tagged_user in tagged_users:
            if tagged_user == IG_user_name:
                caption_text = caption_text.replace('@' + tagged_user, USER_NAME)  # TODO: make not hardcoded
            else:
                caption_text = caption_text.replace('@' + tagged_user, '')

    # Change self-reference to third person
    if ' me ' in caption_text:
        caption_text = caption_text.replace(' me ', ' ' + USER_NAME + ' ')  # TODO: make not hardcoded
    if ' Me ' in caption_text:
        caption_text = caption_text.replace(' Me ', ' ' + USER_NAME + ' ')  # TODO: make not hardcoded
    if ' i ' in caption_text:
        caption_text = caption_text.replace(' i ', ' ' + USER_NAME + ' ')  # TODO: make not hardcoded
    if ' I ' in caption_text:
        caption_text = caption_text.replace(' I ', ' ' + USER_NAME + ' ')  # TODO: make not hardcoded
        #TODO: check for "___ and I" and swap names, then replace with username
    if ' we ' in caption_text:
        caption_text = caption_text.replace(' we ', ' they ')  # TODO: make not hardcoded
    if ' We ' in caption_text:
        caption_text = caption_text.replace(' We ', ' They ')  # TODO: make not hardcoded

    caption_text = caption_text.strip()  # strip outside whitespace

    # Hacky fixes :p
    if parsed_time:
        #TODO: Fix when there's no space between @ and time so it's still readable
        if cap_time and parsed_time:
            print("Replacing cap_time '%s' with parsed time '%s'" % (cap_time, parsed_time))
            caption_text = caption_text.replace(cap_time, parsed_time)
            # caption_text = caption_text.replace("Starting  PSTTwitch.", " Starting %s PST Twitch." % parsed_time)  ####
            # caption_text = caption_text.replace("!8pm PSTTwitch.", "! %s PST Twitch." % parsed_time)  ####
        elif cap_time:
            print("Checking cap_time: %s" % cap_time)  ####
            caption_text = caption_text.replace("Starting  PSTTwitch.", " Starting %s PST Twitch." % cap_time)  ####
            caption_text = caption_text.replace("!8pm PSTTwitch.", "! %s PST Twitch." % cap_time)  ####
        elif parsed_time:
            print("\n\t ! Couldn't parse time from caption, inserting time parsed from info file!\n")
            caption_text = caption_text.replace("Starting  PSTTwitch.", " Starting %s PST Twitch." % parsed_time)  ####
            caption_text = caption_text.replace("!8pm PSTTwitch.", "! %s PST Twitch." % parsed_time)  ####
        else:
            print("\n\t ! Couldn't parse time from caption, defaulting to 7PM!\n")
            caption_text = caption_text.replace("Starting  PSTTwitch.", " Starting 7PM PST Twitch.")####
            caption_text = caption_text.replace("!7pm PSTTwitch.", "! 7pm PST Twitch.")  ####
            # caption_text = caption_text.replace("Starting  PSTTwitch.", " Starting 8PM PST Twitch.")  ####
            # caption_text = caption_text.replace("!8pm PSTTwitch.", "! 8pm PST Twitch.")  ####


    ### More Hacky Fixes ###
    caption_text = caption_text.replace("PSTTwitch.", "PST Twitch.")  ####
    caption_text = caption_text.replace("!SPECIAL", "! SPECIAL")  ####
    caption_text = caption_text.replace("?SPECIAL", "? SPECIAL")  ####
    caption_text = caption_text.replace('  ', ' ')  ####
    ######

    return caption_text

def parse_text_from_caption(caption_text, parsed_time):
    # Parse caption
    # TODO: make gamelist txt file with tags for games, search for game name in tags
    cap_time = ''
    cap_day = ''
    tagged_users = []
    cap_url = ''

    tagged_users = re.findall(re_tagged_user, caption_text)  # TODO: if no tagged user, use self?
    mdate = re.match(re_time, caption_text)
    if mdate:
        matchdict = mdate.groupdict()
        cap_time = matchdict.get("time", '')
        cap_day = matchdict.get("day", '')
    murl = re.match(re_url, caption_text)
    if murl:
        matchdict = murl.groupdict()
        cap_url = matchdict.get("url", '')

    caption_text = clean_text(caption_text, tagged_users, parsed_time, cap_day, cap_time, cap_url)

    return caption_text

def generate_text_from_plan(info_file_path):
    tweet_text = ''
    if os.path.exists(info_file_path):
        # TODO: add RE substitution text, read in text file, etc for generator
        # TODO: collect base phrases from past tweets
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
    else:
        #TODO: ask for alternative file or info retrieval method
        print("\n\t\t !! Info file doesn't exist, so I can't generate tweet text that way. Let's try something else?\n")
    return tweet_text