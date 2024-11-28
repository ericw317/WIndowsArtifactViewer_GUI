import os
from CustomLibs import jumplist_IDs
from CustomLibs import time_conversion as TC
from CustomLibs import display_functions
from CustomLibs import config
from datetime import datetime
from zoneinfo import ZoneInfo
import shutil

# initialize appID dictionary
jump_list_dict = {}
# Read the file and process each line
for line in jumplist_IDs.ID_list.strip().split("\n"):
    # Split the line by the delimiter "|"
    parts = line.strip().split("|")
    if len(parts) == 2:  # Ensure the line has both key and value
        app_id = (parts[0].strip('"')).lower()  # Remove surrounding quotes
        program_name = parts[1].strip('"')
        jump_list_dict[app_id] = program_name


def convert_timezone(timestamp):
    utc_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    utc_time = utc_time.replace(tzinfo=ZoneInfo("UTC"))
    converted_time = utc_time.astimezone(ZoneInfo(config.timezone))

    return converted_time

def get_jumplist_apps(drive, user):
    if drive == "C:\\":
        jumplist_path = rf"{drive}Users\{user}\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations"
    else:
        jumplist_path = rf"{drive}[root]\Users\{user}\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations"

    # add found jumplists to list
    application_list = []
    for file in os.listdir(jumplist_path):
        ID = file.split(".")[0]
        if ID in jump_list_dict:
            application_list.append(jump_list_dict[ID])

    return sorted(application_list)

def parse_jumplist(drive, user, app):
    try:
        if drive == "C:\\":
            jumplist_path = rf"{drive}Users\{user}\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations"
        else:
            jumplist_path = rf"{drive}[root]\Users\{user}\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations"

        # get file name
        file_path = ""
        for key in jump_list_dict:
            if jump_list_dict[key] == app:
                file_path = os.path.join(jumplist_path, f"{key}.automaticDestinations-ms")
                break

        # copy file
        destination = os.path.join(os.getcwd(), "jumplist_copy")
        shutil.copy(file_path, destination)

        jumplist_path = destination

        entry_header = b'\x4C\x00\x00\x00\x01\x14\x02\x00\x00'
        entry_footer = b'\x43\x99\x8F\x77\x19\xFB\xC1\x0B\x58'
        path_header = b'\x0D\x1D\x1D\xA4\x10\x00\x00\x00\x00'
        path_footer = b'\x00\x60\x00\x00\x00\x03\x00\x00\xA0'
        buffer = bytearray()
        path_data = bytearray()
        timestamp_data = bytearray()
        path_string = ""
        record = False
        found_path = False
        time_collection = ""
        path_list = []
        header_counter = 0
        c_date = ""
        a_date = ""
        m_date = ""

        with open(jumplist_path, 'rb') as file:
            while byte := file.read(1):

                # initialize byte buffer
                buffer.append(byte[0])
                if len(buffer) > 9:
                    buffer.pop(0)

                # only search values inside a record
                if buffer == entry_header:
                    record = True
                elif buffer == entry_footer:
                    # wrap up data
                    if len(path_data) > 0:
                        path_list.append([path_string, str(c_date), str(a_date), str(m_date)])
                        path_data = bytearray()  # reset path_data

                    record = False
                    time_collection = ""
                    header_counter = 0
                    timestamp_data = bytearray()

                if record:
                    if time_collection != "done":
                        # collect timestamp bytes
                        if 20 <= header_counter <= 43:
                            timestamp_data.append(byte[0])
                        if header_counter <= 52:
                            header_counter += 1
                        else:
                            timestamp_data = timestamp_data.hex()
                            time_collection = "collected"

                        # split into chunks of 8 bytes
                        if time_collection == "collected":
                            time_chunks = []
                            for x in range(0, len(timestamp_data), 16):
                                chunk = timestamp_data[x:x + 16]
                                time_chunks.append(chunk)
                            time_collection = "chunked"

                        # convert each chunk via FILETIME
                        if time_collection == "chunked":
                            c_date = convert_timezone(str(TC.hex_filetime(time_chunks[0])))
                            a_date = convert_timezone(str(TC.hex_filetime(time_chunks[1])))
                            m_date = convert_timezone(str(TC.hex_filetime(time_chunks[2])))
                            # print(f"{c_date} {a_date} {m_date} {timestamp_data}")
                            time_collection = "done"

                    # check for file path
                    if not found_path and buffer == path_header:
                        found_path = True
                        continue
                    elif found_path and buffer == path_footer:
                        try:
                            path_string = path_data[:-9].decode('utf-8')  # convert to plaintext
                            # path_list.append(path_string)
                            # path_data = bytearray()  # reset path_data
                            found_path = False
                        except Exception:
                            path_data = bytearray()
                            found_path = False

                    # store bytes in path_data
                    if found_path:
                        path_data.append(byte[0])

                    # handle error for entries with no footers
                    if buffer == entry_header:
                        time_collection = ""
                        header_counter = 0
                        timestamp_data = bytearray()
                        timestamp_data.append(byte[0])

        os.remove(destination)

        # format data
        output = display_functions.four_values("File Path", "Creation Date", "Access Date",
                                               "Modification Date", path_list)
        formatted_output = "\n".join(output) + "\n"
        return formatted_output
    except Exception:
        return 1
