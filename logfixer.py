import os
import datetime
import tkinter as tk
from tkinter import filedialog


# Gotta clear the screen somehow...
def clear():
    command = "clear"
    if os.name == "nt":
        command = "cls"
    os.system(command)


def get_log_file(mode):
    file_flag = False
    message = ""
    while file_flag is False:
        clear()
        print("Log File Selection [" + mode + "]")
        print(message)
        print("Enter 0 to return to the main menu.")
        print("Press Enter to proceed to log file selection.")

        choice = input()
        if choice == "0":
            return False, False, False
        else:
            # File select dialog
            root = tk.Tk()
            root.withdraw()
            log_path = filedialog.askopenfilename()
            root.destroy()
            # Isolate log name without extension for naming purposes
            log_name = log_path.split('.', 1)[0]

        if os.path.exists(log_path):
            clear()
            print("Log '" + log_path + "' selected. Locating fights...")
            log_file = open(log_path, 'r', encoding="utf8")
            # Get and display the list of fights in the log
            fights = get_fights(log_file)
            return log_file, log_name, fights
        else:
            message = "\n\033[93mNo log file selected.\033[0m"


def get_fights(log_file):
    # Keywords for extracting fight durations
    combat_keywords = ['BEGIN_LOG', 'END_LOG', 'BEGIN_COMBAT', 'END_COMBAT']
    combat_dict = {}
    fight_counter = 1
    start_time = ""

    # Loop through each line in the log looking for timestamps and type of entry
    for i, line in enumerate(log_file):
        # Split each line into chunks based on comma delineation
        split = line.split(',')
        # Get epoch timestamp of the original start of the log - IN SECONDS
        if i == 0:
            start_time = int(split[2]) / 1000
        # Get timestamp and entry types
        time = int(split[0])
        entry_type = split[1].rstrip()
        # Extract all begin and end combats with their timestamps
        if entry_type in combat_keywords:
            combat_dict[fight_counter] = [time, entry_type, i]
            fight_counter += 1

    # Extract individual fights from the larger log for selection
    previous = None
    fight_list = {}
    counter = 1
    fight_list[0] = start_time
    for key, value in combat_dict.items():
        # Assign previous as current if first item in dictionary
        if key == 1:
            previous = value
        else:
            if previous[1] in ["BEGIN_COMBAT", "BEGIN_LOG"] and value[1] in ["END_COMBAT", "END_LOG"]:
                # Get start times and end times in readable time format
                begin_time = datetime.datetime.fromtimestamp(start_time + (previous[0] / 1000)).strftime("%I:%M %p")
                end_time = datetime.datetime.fromtimestamp(start_time + (value[0] / 1000)).strftime("%I:%M %p")
                # Get duration in raw ms, then convert to an easy-to-read string
                total = value[0] - previous[0]
                seconds = datetime.timedelta(milliseconds=total).seconds
                minutes = (seconds // 60)
                #  Get number of spaces to add for uniformity up to 3 minutes digits and 2 seconds digits
                minute_spaces = ""
                if minutes < 10:
                    minute_spaces = "  "
                elif minutes < 100:
                    minute_spaces = " "
                second_spaces = ""
                if (seconds % 60) < 10:
                    second_spaces = " "

                duration = minute_spaces + str(minutes) + " Minutes " + second_spaces + str(seconds % 60) + " Seconds"
                half = round(total / 2) + previous[0]
                # Package up the fight with start, end, duration, half point, start line #, end line #, begin, end, fight #
                fight_list[counter] = [previous[0], value[0], duration, half, previous[2], value[2], begin_time, end_time, counter]
                counter += 1
            # Set current to previous for next loop
            previous = value

    return fight_list


def display_fights(fights):
    clear()
    # Display all fights for choice
    start_time = fights[0]
    print("            " + datetime.datetime.fromtimestamp(start_time).strftime("%a %b %d %Y %I:%M %p"))
    print("                     Fights")
    print("-------------------------------------------------")
    for key, value in fights.items():
        if key != 0:
            spaces = ""
            if key < 10:
                spaces = " "
            print("[" + str(key) + "] " + spaces + value[2] + " | " + value[6] + " - " + value[7])
    print("[0] Back")
    print("-------------------------------------------------")


def simple_fight_selection(fights, prompt):
    fight_selection_flag = False
    message = ""
    while fight_selection_flag is False:
        print(message)
        choice = input("Select fight to " + prompt + ": ")
        if choice.isnumeric():
            choice = int(choice)
            if choice == 0:
                return False
            elif choice in fights.keys():
                return fights[choice]
        message = "\n\033[93mFight choice '" + choice + "' not valid.\033[0m"
        display_fights(fights)


def display_fights_double(fights, selection):
    clear()
    # Display all fights for choice
    start_time = fights[0]
    print("            " + datetime.datetime.fromtimestamp(start_time).strftime("%a %b %d %Y %I:%M %p"))
    print("                     Fights")
    print("-------------------------------------------------")
    for key, value in fights.items():
        if key != 0:
            spaces = ""
            if key < 10:
                spaces = " "
            if key == selection:
                print("\033[92m[" + str(key) + "] " + spaces + value[2] + " | " + value[6] + " - " + value[7] + "\033[0m")
            elif key < selection:
                print("\033[1;30m[" + str(key) + "] " + spaces + value[2] + " | " + value[6] + " - " + value[7] + "\033[0m")
            else:
                print("[" + str(key) + "] " + spaces + value[2] + " | " + value[6] + " - " + value[7])
    print("[0] Back")
    print("-------------------------------------------------")


def double_fight_selection(fights):
    first_fight_flag = False
    second_fight_flag = False
    fight1 = None
    fight2 = None
    message = ""
    while first_fight_flag is False:
        display_fights(fights)
        second_fight_flag = False
        print(message)
        choice = input("Select start fight: ")
        if choice.isnumeric():
            choice = int(choice)
            if choice == 0:
                return False, False
            elif choice in fights.keys():
                fight1 = fights[choice]
                message = ""
                first_fight_flag = True
                while second_fight_flag is False:
                    display_fights_double(fights, choice)
                    print(message)
                    second_choice = input("Select end fight: ")
                    if second_choice.isnumeric():
                        second_choice = int(second_choice)
                        if second_choice == 0:
                            first_fight_flag = False
                            second_fight_flag = True
                            message = "\n\033[93mStart fight choice cleared.\033[0m"
                        elif second_choice in fights.keys():
                            if second_choice <= choice:
                                message = "\n\033[93mFight choice '" + str(second_choice) + "' not valid. Choice cannot be less than/equal to first.\033[0m"
                            else:
                                fight2 = fights[second_choice]
                                return fight1, fight2
                        else:
                            message = "\n\033[93mFight choice '" + str(second_choice) + "' not valid.\033[0m"
                    else:
                        message = "\n\033[93mFight choice '" + second_choice + "' not valid.\033[0m"
            else:
                message = "\n\033[93mFight choice '" + str(choice) + "' not valid.\033[0m"
        else:
            message = "\n\033[93mFight choice '" + choice + "' not valid.\033[0m"


def extract_fight(log_file, log_name, chosen_fight):
    clear()
    print("Extracting fight...")

    # Start extracting the selected fight and creating the new file
    with open(log_name + "_extracted.log", 'w', encoding="utf8") as new_file:
        # Keywords: unit info map log zone
        # These keywords identify lines with pertinent info to save even outside of the chosen fight
        keywords = ['UNIT', 'INFO', 'MAP', 'LOG', 'ZONE']

        # Seek to reset cursor to beginning since it already looped through to find the fights
        log_file.seek(0)

        pertinent_info = []
        # Loop through each line in the original log to split it
        for i, line in enumerate(log_file):
            # Split each line into chunks based on comma delineation
            split = line.split(',')
            time = int(split[0])

            # Lines before the fight starts
            if i < chosen_fight[4]:
                if any(word in line for word in keywords):
                    # Add the pertinent line into storage for later
                    pertinent_info.append(line)
                    # Replace time with start of chosen fight to avoid empty space in front of log
                    line = str(line).replace(str(time) + ",", str(chosen_fight[0]) + ",", 1)
                    new_file.write(line)
            # Lines between the start and end of the fight
            elif chosen_fight[4] <= i <= chosen_fight[5]:
                # End the log if it's the last line, otherwise write actual fight data
                if i == chosen_fight[5]:
                    new_file.write(str(time) + ",END_LOG")
                else:
                    new_file.write(line)
    clear()
    print("Fight extraction complete.")
    print("Created extracted file: " + new_file.name)
    log_file.close()


def split_log(log_file, log_name, chosen_fight):
    clear()
    print("Splitting log...")

    # Start extracting the selected fight and creating the new file
    with open(log_name + "_split.log", 'w', encoding="utf8") as new_file:
        # If split_time is low enough, the parser will combine the fights even though it recognizes they are distinct
        # split_time of about a minute (in ms) will show 2 separate fights

        split_time = 0

        # Split time unnecessary with new log splitting technique -- saving only just in case
        # split_flag = input("Split fights with time gap (y)? ")
        # if split_flag == "y":
        #     split_time = 60000
        #     print("Added " + str(split_time) + "ms split time.")
        # else:
        #     print("No additional split time added.")

        # Keywords: unit info map log zone
        # These keywords identify lines with pertinent info to save even outside of the chosen fight
        keywords = ['UNIT', 'INFO', 'MAP', 'LOG', 'ZONE']

        # Seek to reset cursor to beginning since it already looped through to find the fights
        log_file.seek(0)

        found_flag = False
        pertinent_info = []
        split_line = chosen_fight[4] + round((chosen_fight[5] - chosen_fight[4]) / 2)
        # Loop through each line in the original log to split it
        for i, line in enumerate(log_file):
            # Split each line into chunks based on comma delineation
            split = line.split(',')
            time = int(split[0])

            # Lines before the fight starts
            if i < chosen_fight[4]:
                if any(word in line for word in keywords):
                    # Add the pertinent line into storage for later
                    pertinent_info.append(line)
                    # Replace time with start of chosen fight to avoid empty space in front of log
                    line = str(line).replace(str(time) + ",", str(chosen_fight[0]) + ",", 1)

                    new_file.write(line)
            # Lines between the start and end of the fight
            elif chosen_fight[4] <= i <= chosen_fight[5]:
                # The very first time after the halfway point of the fight - add a split
                # time > chosen_fight[3]
                if found_flag is False and i > split_line:
                    # Apply the halfway cut by ending the log and restarting it directly after
                    # Depending on what split_time is, will either combine or make 2 distinct fights with 1 min between
                    new_file.write(str(time) + ",END_LOG\n")

                    # Re-attach pertinent info after the cut so abilities/players are identified
                    # Includes the START_LOG from the original file start
                    for pert_line in pertinent_info:
                        split = pert_line.split(',')
                        pert_time = int(split[0])
                        pert_line = str(pert_line).replace(str(pert_time) + ",", str(time + split_time) + ",", 1)
                        new_file.write(pert_line)
                    found_flag = True
                # Any line after the halfway point, but still within the bounds
                # time > chosen_fight[3]
                # Should be irrelevant if using line split instead of time split
                elif i > split_line and found_flag is True:
                    # Apply split_time to everything after the halfway point (if 0 just stays normal time)
                    line = str(line).replace(str(time) + ",", str(time + split_time) + ",", 1)
                    # End the log if it's the last line, otherwise write actual fight data
                    if i == chosen_fight[5]:
                        new_file.write(str(time + split_time) + ",END_LOG")
                    else:
                        new_file.write(line)
                # Any time before the halfway point
                else:
                    # Get pert info after start of fight, but before the split time
                    if any(word in line for word in keywords):
                        # Add the pertinent line into storage for later
                        pertinent_info.append(line)
                    new_file.write(line)
    clear()
    print("Log splitting complete.")
    print("Created split file: " + new_file.name)
    log_file.close()


def combine_fights(log_file, log_name, fights, start_fight, end_fight):
    clear()
    print("Combining fights...")

    # Start extracting the selected fight and creating the new file
    with open(log_name + "_combined.log", 'w', encoding="utf8") as new_file:
        # Keywords: unit info map log zone
        # These keywords identify lines with pertinent info to save even outside of the chosen fight
        keywords = ['UNIT', 'INFO', 'MAP', 'ZONE']

        # Seek to reset cursor to beginning since it already looped through to find the fights
        log_file.seek(0)

        time_diff = 0
        next_fight = start_fight[8] + 1
        next_fight_start_time = 0
        next_fight_start_line = 0
        previous_fight_end_time = 0
        previous_fight_end_line = 0
        flag = False
        # Loop through each line in the original log to split it
        for i, line in enumerate(log_file):
            # Split each line into chunks based on comma delineation
            split = line.split(',')
            time = int(split[0])
            entry_type = split[1].rstrip()

            # Lines before the start fight begins (pertinent info)
            if i == 0:
                line = str(line).replace(str(time) + ",", str(start_fight[0]) + ",", 1)
                new_file.write(line)
            elif i < start_fight[4]:
                if any(word in line for word in keywords):
                    # Replace time with start of chosen fight to avoid empty space in front of log
                    line = str(line).replace(str(time) + ",", str(start_fight[0]) + ",", 1)
                    new_file.write(line)
            # Lines between the beginning of the start fight and end of the final fight
            elif start_fight[4] <= i <= end_fight[5]:
                # End the log if it's the last line, otherwise write actual fight data
                if i == end_fight[5]:
                    new_file.write(str(time - time_diff) + ",END_COMBAT\n")
                    new_file.write(str(time - time_diff) + ",END_LOG")
                elif i == start_fight[4]:
                    new_file.write(str(start_fight[0]) + ",BEGIN_COMBAT\n")
                else:
                    if entry_type != "BEGIN_COMBAT":
                        if entry_type == "END_COMBAT":
                            previous_fight_end_time = time - time_diff
                            previous_fight_end_line = i
                            next_fight_start_time = fights[next_fight][0]
                            next_fight_start_line = fights[next_fight][4]
                            next_fight += 1
                            time_diff = next_fight_start_time - previous_fight_end_time
                            flag = True
                        elif (previous_fight_end_line < i < next_fight_start_line) and flag:
                            if any(word in line for word in keywords):
                                line = str(line).replace(str(time) + ",", str(previous_fight_end_time) + ",", 1)
                                new_file.write(line)
                        elif i >= next_fight_start_line and flag:
                            line = str(line).replace(str(time) + ",", str(time - time_diff) + ",", 1)
                            new_file.write(line)
                        else:
                            new_file.write(line)
    clear()
    print("Fight combination complete.")
    print("Created combined file: " + new_file.name)
    log_file.close()


def batch_extract(log_file, log_name, start_fight, end_fight):
    clear()
    print("Batch extracting fights...")

    # Start extracting the selected fight and creating the new file
    with open(log_name + "_batch.log", 'w', encoding="utf8") as new_file:
        # Keywords: unit info map log zone
        # These keywords identify lines with pertinent info to save even outside of the chosen fight
        keywords = ['UNIT', 'INFO', 'MAP', 'ZONE', 'LOG']

        # Seek to reset cursor to beginning since it already looped through to find the fights
        log_file.seek(0)

        pertinent_info = []
        # Loop through each line in the original log to split it
        for i, line in enumerate(log_file):
            # Split each line into chunks based on comma delineation
            split = line.split(',')
            time = int(split[0])

            # Lines before the fight starts
            if i < start_fight[4]:
                if any(word in line for word in keywords):
                    # Add the pertinent line into storage for later
                    pertinent_info.append(line)
                    # Replace time with start of chosen fight to avoid empty space in front of log
                    line = str(line).replace(str(time) + ",", str(start_fight[0]) + ",", 1)
                    new_file.write(line)
            # Lines between the start and end of the fight
            elif start_fight[4] <= i <= end_fight[5]:
                # End the log if it's the last line, otherwise write actual fight data
                if i == end_fight[5]:
                    new_file.write(str(time) + ",END_LOG")
                else:
                    new_file.write(line)
    clear()
    print("Batch extract complete.")
    print("Created extracted file: " + new_file.name)
    log_file.close()


def startup():
    mode_flag = False
    message = ""
    while mode_flag is False:
        clear()
        file_flag = False
        # Options for the program
        print("\n           ESO Log Fixer")
        print("            \033[35m@Grimlock46\033[0m")
        print("----------------------------------")
        print("[1] Extract Single Fight and Split")
        print("[2] Extract Single Fight")
        print("[3] Combine Fights")
        print("[4] Batch Extract")
        print("[0] Exit")
        print("----------------------------------")
        print(message)
        message = ""
        mode_selection = input("Select the mode you want: ")
        clear()
        if mode_selection == "1":
            while file_flag is False:
                log_file, log_name, fights = get_log_file("Extract Single Fight and Split")
                if log_file is not False:
                    file_flag = True
                    display_fights(fights)
                    chosen_fight = simple_fight_selection(fights, "split")
                    if chosen_fight is not False:
                        split_log(log_file, log_name, chosen_fight)
                        mode_flag = True
                    else:
                        file_flag = False
                else:
                    file_flag = True
        elif mode_selection == "2":
            while file_flag is False:
                log_file, log_name, fights = get_log_file("Extract Single Fight")
                if log_file is not False:
                    file_flag = True
                    display_fights(fights)
                    chosen_fight = simple_fight_selection(fights, "extract")
                    if chosen_fight is not False:
                        extract_fight(log_file, log_name, chosen_fight)
                        mode_flag = True
                    else:
                        file_flag = False
                else:
                    file_flag = True
        elif mode_selection == "3":
            while file_flag is False:
                log_file, log_name, fights = get_log_file("Combine Fights")
                if log_file is not False:
                    file_flag = True
                    start_fight, end_fight = double_fight_selection(fights)
                    if start_fight is not False:
                        combine_fights(log_file, log_name, fights, start_fight, end_fight)
                        mode_flag = True
                    else:
                        file_flag = False
                else:
                    file_flag = True
        elif mode_selection == "4":
            while file_flag is False:
                log_file, log_name, fights = get_log_file("Batch Extract")
                if log_file is not False:
                    file_flag = True
                    start_fight, end_fight = double_fight_selection(fights)
                    if start_fight is not False:
                        batch_extract(log_file, log_name, start_fight, end_fight)
                        mode_flag = True
                    else:
                        file_flag = False
                else:
                    file_flag = True
        elif mode_selection == "0":
            mode_flag = True
        else:
            message = "\n\033[93mSelection not valid.\033[0m"


if __name__ == "__main__":
    startup()
    print("Happy logging!\n")
