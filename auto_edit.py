import io, sys, os, re
import glob #https://docs.python.org/3/library/glob.html
from moviepy.editor import * # http://zulko.github.io/moviepy/
from datetime import datetime, timedelta
import shutil
import logging, traceback

# Globals #####
today = datetime.now().strftime('%Y_%m_%d')
today_v = today.replace('_', '')
script_start = datetime.now().strftime('%Y_%m_%d  %H:%M:%S.%f')
# current_hour = int(datetime.now().strftime('%H'))
yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y_%m_%d')
yesterday_v = yesterday.replace('_', '')

ideal_clip_len = 900.0 # duration in sec so 15min = 900sec
overlap = 600.0 # 10mins overlap (in sec)
# ideal_clip_len = 300.0 #testing
# overlap = 120.0 #testing

notes_file_pattern = "stream_notes__*.txt" # where * is date
# Video file naming convention: 20170215_122399776_Resident Evil 4.mp4
video_name_re = r'^(?P<date_year>\d\d\d\d)(?P<date_month>\d\d)(?P<date_day>\d\d)_(?P<id>\d+)_(?P<game_name>.+)\.mp4'

# Debug #####
# override = False
override = True
notes_file = 'OVERRIDE'
#video_file = '20170329_132139888_Dark Souls III.mp4'
#video_id = "132139888"
#game_name = "Dark Souls III"
#date_year = '2017'
#date_month = '03'
#date_day = '29'

video_file = '20170217_122861239_Resident Evil 4.mp4'
video_id = "122861239"
game_name = "Resident Evil 4"
date_year = '2017'
date_month = '02'
date_day = '17'
##############

# logger = logging.getLogger("timestamp_counter__%s.log" % date)
# handler = logging.FileHandler("timestamp_counter__%s.log" % date)
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)



def select_file(file_list, file_type_str, file_pattern_str):
    selected_file = ''

    if len(file_list) == 1:
        selected_file = file_list[0]
    elif len(file_list) == 0:
        print("! There are no %s files that match the file pattern '%s' in this directory.\n" % (file_type_str, file_pattern_str))
        selected_file = input("Please give me the full path to the %s file you'd like to use.\n" % file_type_str)
    else:
        # Try to narrow down by date by assuming either today or yesterday
        filtered_list = [f for f in file_list if ((today in f or today_v in f) or (yesterday in f or yesterday_v in f))]

        if len(filtered_list) == 1:
            selected_file = filtered_list[0]
            print("Using the most recent %s file: %s" % (file_type_str, selected_file))
        elif len(filtered_list) < 5:
            print("Multiple recent files found!")
            for found_file in filtered_list:
                select = input("\n%s\nWould you like to use this one? (y/n)  " % found_file)
                if select.lower().startswith('y'):
                    selected_file = found_file
                    break
            if not selected_file:
                if len(file_list) < 5:
                    select = input("Would you like to use an older file? (y/n)   ")
                    if select.lower().startswith('y'):
                        for found_file in file_list:
                            select = input("\n%s\nWould you like to use this one? (y/n)  " % found_file)
                            if select.lower().startswith('y'):
                                selected_file = found_file
                                break
                    else:
                        selected_file = input("Please give me the name of the %s file you'd like to use.\n" % file_type_str)

        elif len(filtered_list) == 0:
            print("No recent files found")
            if len(file_list) < 5:
                print("Multiple older files found!")
                for found_file in file_list:
                    select = input("\n%s\nWould you like to use this one? (y/n)  " % found_file)
                    if select.lower().startswith('y'):
                        selected_file = found_file
                        break
            else:
                selected_file = input("Please give me the name of the %s file you'd like to use.\n" % file_type_str)

        #Validate
        if os.path.exists(selected_file):
            print("Selected file path OK!\n")
        else:
            print("\t\t! Error: File with given path does not exist: %s\n\t\tThe script will close. Please move the files into this folder and try again." % selected_file)
            sys.exit()

    return selected_file

# Set up dict for report log
report_data = {'start_time': script_start}

if override:
    # Debug
    print("Running override!\n\n")

else:
    # Get number of stream_notes files
    dir_list = os.listdir()
    print("FILES IN DIR: %s\n\n------\n" % dir_list)####
    notes_count = [f for f in dir_list if f.startswith('stream_notes__')]

    # Select notes file
    notes_file = select_file(notes_count, 'notes', notes_file_pattern)

    # Get date from notes file
    video_date = notes_file.replace('stream_notes__', '').replace('.txt', '').replace('_', '')

    # Find matching video file
    video_matches = [f for f in dir_list if re.match(video_name_re, f) and f.startswith(video_date)]
    video_file = select_file(video_matches, 'video', video_name_re)

    #Parse name for data
    matchdict = re.match(video_name_re, video_file).groupdict()
    date_year = matchdict.get("date_year", None)
    date_month = matchdict.get("date_month", None)
    date_day = matchdict.get("date_day", None)
    video_id = matchdict.get("id", None)
    game_name = matchdict.get("game_name", None)

# report_data['total_video_files'] = len(video_matches)
# report_data['total_notes_files'] = len(notes_count)
report_data['date_year'] = date_year
report_data['date_month'] = date_month
report_data['date_day'] = date_day
report_data['video_id'] = video_id
report_data['game_name'] = game_name
report_data['video_file'] = video_file
report_data['notes_file'] = notes_file

#Create Output folder
output_folder = video_file.replace('.mp4', '__clips')
if os.path.exists(output_folder):
    print("\n ! Output folder already exists! [%s]" % output_folder)
    usr_input = input("\n\nRemove files and continue? (y/n) ")
    if usr_input.strip().lower() == 'y':
        for old_file in os.listdir(output_folder):
            print("Removing %s..." % old_file)
            os.remove(os.path.join(output_folder,old_file))
    else:
        print("\n\nQuitting!")
        sys.exit()
else:
    os.mkdir(output_folder)

report_file_path = '%s-%s__report.txt' % (today, game_name)

# Pull full audio for backup
usr_input = input("\n\nRip full audio? (y/n)  ")
if usr_input.strip().lower() == 'y':
    full_audio_filename = video_file.replace('.mp4', '-FULL_AUDIO.mp3')
    full_audio = AudioFileClip(video_file)
    full_audio.write_audiofile(os.path.join(output_folder, full_audio_filename))
else:
    print("Ok, cutting video...\n\n")

# Clip Video into increments for editing
full_video = VideoFileClip(video_file)
vid_len = full_video.duration # in sec
clip_blocks, remainder = divmod(vid_len, ideal_clip_len)
clip_blocks = int(clip_blocks) #cast to int

print("Making %s clips...\n\n" % clip_blocks)
clip_list = []

for clip_block in range(0, clip_blocks):
    clip_start = clip_block * ideal_clip_len
    clip_end = clip_start + (ideal_clip_len + overlap) #length plus overlap added to start time to get end time
    if clip_block == (clip_blocks - 1):
        # Last clip, so add overlap to the front and extend to end
        if clip_start - overlap > 0.0:
            clip_start = clip_start - overlap
        clip_end = vid_len
    clip = full_video.subclip(clip_start,clip_end) #seconds (15.35), in (min, sec), in (hour, min, sec), or as a string: ‘01:03:05.35’
    clip_name = video_file.replace(".mp4", "__clip_%s.mp4" % clip_block)
    clip.write_videofile(os.path.join(output_folder, clip_name))
    print("Created clip %s with duration %s starting at %s\n" % (clip_name, clip.duration, clip_start))
#TODO: Try to move source video and notes file into output folder when finished

#TODO: create output file with list describing start and end times for clips
# Generate Report File
script_end = datetime.now().strftime('%Y_%m_%d  %H:%M:%S.%f')


# audioclip = AudioFileClip(video_file)
# audioclip.write_audiofile("new_audio.mp3")

###################### VIDEO NOTES ######################
#Advanced tools: http://zulko.github.io/moviepy/ref/videotools.html#ref-videotools
#
# # Basics
# clip = VideoFileClip("myHolidays.mp4").subclip(50,60) # Load myHolidays.mp4 and select the subclip 00:00:50 - 00:00:60
# video.write_videofile("myHolidays_edited.webm") # Write the result to a file (many options available !)
#
# # Create text clip and overlay
# txt_clip = TextClip("My Holidays 2013",fontsize=70,color='white') # Generate a text clip. You can customize the font, color, etc.
# txt_clip = txt_clip.set_pos('center').set_duration(10) # Say that you want it to appear 10s at the center of the screen
# video = CompositeVideoClip([clip, txt_clip]) # Overlay the text clip on the first video clip
#
# # Make a gif from a video
# myclip = VideoFileClip("some_video.avi")
# print (myclip.fps) # prints for instance '30'
# myclip2 = myclip.subclip(10, 25)
# myclip2.write_gif("test.gif") # the gif will have 30 fps
#
# # Rendering new video
# my_clip.write_videofile("movie.mp4") # default codec: 'libx264', 24 fps
# my_clip.write_videofile("movie.mp4",fps=15)
# my_clip.write_videofile("movie.webm") # webm format
# my_clip.write_videofile("movie.webm",audio=False) # don't render audio.
#
# # Pull audio from video or set audio to a new video file
# audioclip = AudioFileClip("some_audiofile.mp3")
# audioclip = AudioFileClip("some_video.avi")
# audioclip = videoclip.audio # can also get audio from existing video clip
# audioclip.write_audiofile("new_audio.mp3")
#
# #Concat video clips
# final_clip = concatenate_videoclips([clip1,clip2,clip3])
#
# #Composition (multiple videos play at the same time) #http://zulko.github.io/moviepy/getting_started/compositing.html
# video = CompositeVideoClip([clip1,
#                             clip2.set_pos((45,150)),
#                             clip3.set_pos((90,100))])
# # clip.size(w,h) # where (0,0) is top left
#
# #Composition audio
# # ... make some audio clips aclip1, aclip2, aclip3
# concat = concatenate_audioclips([aclip1, aclip2, aclip3])
# compo = CompositeAudioClip([aclip1.volumex(1.2),
#                             aclip2.set_start(5), # start at t=5s
#                             aclip3.set_start(9)])
#
# # FX
# VideoFileClip("myvideo.avi").fx( vfx.resize, width=460) # resize (keep aspect ratio
#
##########################################################

print("End!")
