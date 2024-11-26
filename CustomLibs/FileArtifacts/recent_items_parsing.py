from CustomLibs import list_functions
from CustomLibs import config
from CustomLibs import artifact_search as AS
from CustomLibs import display_functions
import os
import time
import shutil
from tempfile import mkdtemp
from datetime import datetime
import pytz

def convert_to_timezone(date_str, target_timezone):
    # Step 1: Parse the date string
    # The format includes a double space for single-digit days, so we use %d to handle it dynamically
    date_format = "%a %b %d %H:%M:%S %Y"
    date_obj = datetime.strptime(date_str, date_format)

    # Step 2: Assign the original timezone (e.g., UTC)
    # You can adjust this to the correct timezone if the input is not in UTC
    original_timezone = pytz.UTC
    date_obj = original_timezone.localize(date_obj)

    # Step 3: Convert to the target timezone
    target_tz = pytz.timezone(target_timezone)
    converted_date = date_obj.astimezone(target_tz)

    return str(converted_date)

def get_metadata(file_path):
    creation_time = time.ctime(os.path.getctime(file_path))
    mod_time = time.ctime(os.path.getmtime(file_path))
    return [creation_time, mod_time]

def parse_recent(drive, user):
    # set path to recent items and get number of files
    recent_items_path = AS.set_path(f"Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\Recent", drive)

    # put link files in a list and sort it by modification date
    lnk_list = []
    for file in os.listdir(recent_items_path):
        file_path = os.path.join(recent_items_path, file)
        lnk_list.append(file_path)
    lnk_list = list_functions.sort_files_by_modification(lnk_list)
    lnk_list.reverse()

    # set values into list
    lnk_value_list = []
    for file in lnk_list:
        file_name = os.path.basename(file)
        m_date = convert_to_timezone(str(get_metadata(file)[1]), config.timezone)
        c_date = convert_to_timezone(str(get_metadata(file)[0]), config.timezone)
        lnk_value_list.append([file_name, m_date, c_date])

    # display data
    output = display_functions.three_values("File Name", "Modification Date", "Creation Date",
                                            lnk_value_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output


def parse_recent_external(drive, user):
    # set path to recent items and get number of files
    recent_items_path = AS.set_path(f"Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\Recent", drive)

    # make temp directory for analysis
    current_directory = os.getcwd()
    temp_dir = mkdtemp(dir=current_directory)
    creation_dates = {}
    try:
        for file_name in os.listdir(recent_items_path):
            if file_name.endswith(".lnk"):
                full_file_name = os.path.join(recent_items_path, file_name)

                # Only copy if it's a file (skip directories or anything else)
                if os.path.isfile(full_file_name):
                    creation_dates[file_name] = get_metadata(full_file_name)[0]  # preserve creation date
                    shutil.copy2(full_file_name, temp_dir)  # copy2 preserves metadata (modification times, etc.)
    except Exception as e:
        print(f"Error copying files: {e}")

    # put link files in a list and sort it by modification date
    lnk_list = []
    for file in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, file)
        lnk_list.append(file_path)
    lnk_list = list_functions.sort_files_by_modification(lnk_list)
    lnk_list.reverse()

    # set values into list
    lnk_value_list = []
    for file in lnk_list:
        file_name = os.path.basename(file)
        m_date = convert_to_timezone(str(get_metadata(file)[1]), config.timezone)
        c_date = convert_to_timezone(str(creation_dates[file_name]), config.timezone)
        lnk_value_list.append([file_name, m_date, c_date])

    shutil.rmtree(temp_dir)

    # display data
    output = display_functions.three_values("File Name", "Modification Date", "Creation Date",
                                            lnk_value_list)

    formatted_output = "\n".join(output) + "\n"
    return formatted_output

def main(drive, user):
    if drive == "C:\\":
        return parse_recent(drive, user)
    else:
        return parse_recent_external(drive, user)