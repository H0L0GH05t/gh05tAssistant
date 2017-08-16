from datetime import datetime
import shutil
import logging, traceback, re, os, sys

date = datetime.now().strftime('%Y_%m_%d')

logger = logging.getLogger("timestamp_counter__%s.log" % date)
handler = logging.FileHandler("timestamp_counter__%s.log" % date)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

info_file_path = "stream_notes__%s.txt" % date

# Counters
kill_counter = 0
death_counter = 0
mark_time = 0
edit_note_count = 0

# Timestamps
kills = []
deaths = []

# Timestamps with Notes
mark_time_notes = {}
edit_notes = {}

# Start up
print("Open session!")

resp = input("Enter 's' to start counter and mark time!\n")
if resp.lower().startswith('s'):
    # Mark start time
    #logger.info("")
    start_time = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

    print("Start time marked!\n\n")
    while(resp != 'x'):
        resp = input("Enter 'x' to end counter and mark time!\n\t\tk = increment kill count\n\t\td = increment death count\n\t\tm = mark the time for notes\n\t\te = mark time for edit note\n\n")
        timestamp = datetime.now().strftime('%H:%M:%S')
        if resp.lower() == 'k':
            #Kill count
            kill_counter += 1
            kills.append(timestamp)
            #logger.info("")
        elif resp.lower() == 'd':
            #Death count
            death_counter += 1
            deaths.append(timestamp)
            #logger.info("")
        elif resp.lower() == 'm':
            #Mark Time
            mark_time += 1
            #logger.info("")
            note = input("Enter note for timestamp mark:\n")
            mark_time_notes[timestamp] = note
        elif resp.lower() == 'e':
            #Edit Note
            edit_note_count += 1
            #logger.info("")
            note = input("Enter edit note for timestamp:\n")
            edit_notes[timestamp] = note
        elif resp.lower() == 'x':
            #Mark end time
            end_time = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
            #logger.info("")
        elif resp.lower() == '?k':
            #Print kills till now
            print('\nCurrent kill count: %s\n' % kill_counter)
            #logger.info("")
        elif resp.lower() == '?d':
            #Print deaths till now
            print('\nCurrent death count: %s\n' % death_counter)
            #logger.info("")

    # TODO: Convert Live timestamps to Video timestamps

    # Format and write info file
    with open(info_file_path, 'a') as info_file:
        info_file.write("Start time: %s\n" % start_time)
        info_file.write("End time: %s\n\n----------" % end_time)
        if len(kills):
            info_file.write("Kills [Total: %s]:\n" % kill_counter)
            idx = 0
            for kill in kills:
                idx += 1
                spaces = '   '
                if idx > 9:
                    spaces = '  '
                info_file.write("%s.%s%s\n" % (idx, spaces, kill))
            info_file.write("----------------------------------------------------\n\n")
        if len(deaths):
            info_file.write("Deaths [Total: %s]:\n" % death_counter)
            idx = 0
            for death in deaths:
                idx += 1
                spaces = '   '
                if idx > 9:
                    spaces = '  '
                info_file.write("%s.%s%s\n" % (idx, spaces, death))
            info_file.write("----------------------------------------------------\n\n")
        else:
            info_file.write("0 Deaths!!\n")
        if len(mark_time_notes):
            info_file.write("Time Markers [Total: %s]:\n" % mark_time)
            idx = 0
            for mark in mark_time_notes:
                idx += 1
                spaces = '   '
                if idx > 9:
                    spaces = '  '
                info_file.write("%s.%s%s -- %s\n" % (idx, spaces, mark, mark_time_notes[mark]))
            info_file.write("----------------------------------------------------\n\n")
        if len(edit_notes):
            info_file.write("Edit Notes [Total: %s]:\n" % edit_note_count)
            idx = 0
            for note in edit_notes:
                idx += 1
                spaces = '   '
                if idx > 9:
                    spaces = '  '
                info_file.write("%s.%s%s -- %s\n" % (idx, spaces, note, edit_notes[note]))
            info_file.write("----------------------------------------------------\n\n")
        info_file.write("--- END OF SESSION ---")

# Purge old logs
for f in os.listdir():
    if '.log' in f:
        if os.stat(f).st_size == 0:
            print("Deleting empty log file: %s")
            os.remove(f)

print("K bai!")
