import sqlite3
from CustomLibs import display_functions
from CustomLibs import time_conversion
import os
import shutil
import json

# get bookmarks parsing
def get_history_path(drive, user, browser):
    if browser == "Chrome":
        if drive == "C:\\":
            return f"{drive}Users\\{user}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Bookmarks"
        else:
            return f"{drive}[root]\\Users\\{user}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Bookmarks"
    elif browser == "Edge":
        if drive == "C:\\":
            return f"{drive}Users\\{user}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Bookmarks"
        else:
            return f"{drive}[root]\\Users\\{user}\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Bookmarks"
    elif browser == "Brave":
        if drive == "C:\\":
            return f"{drive}Users\\{user}\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Bookmarks"
        else:
            return f"{drive}[root]\\Users\\{user}\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Bookmarks"
    elif browser == "Firefox":
        if drive == "C:\\":
            firefox_profiles_path = f"{drive}Users\\{user}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"
        else:
            firefox_profiles_path = f"{drive}[root]\\Users\\{user}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"

        if os.path.exists(firefox_profiles_path):
            for folder in os.listdir(firefox_profiles_path):
                if folder.endswith(".default-release"):
                    full_firefox_path = f"{firefox_profiles_path}\\{folder}\\places.sqlite"
                    return full_firefox_path

# collect bookmark data
def collect_bookmarks(drive, user, browser):
    try:
        # copy downloads file
        bookmarks_path = get_history_path(drive, user, browser)
        destination = os.path.join(os.getcwd(), "bookmarks_copy")
        shutil.copy(bookmarks_path, destination)

        if "Mozilla" not in bookmarks_path:
            with open(destination, 'r') as json_file:
                data = json.load(json_file)

            roots = data['roots']
            other_bookmarks = roots['other']['children']
            bookmarks_data = []

            # remove file copies
            if os.path.exists(destination):
                os.remove(destination)

            # add data to list
            for bookmark in other_bookmarks:
                name = bookmark['name']
                date_added = str(time_conversion.convert_windows_epoch(int(bookmark['date_added'])))
                URL = bookmark['url']
                bookmarks_data.append([name, date_added, URL])

            # format output
            output = display_functions.three_values("Bookmark", "Date Added", "URL", bookmarks_data)
            formatted_output = "\n".join(output) + "\n"
            return formatted_output
        else:
            # connect to sqlite3 database
            conn = sqlite3.connect(destination)
            cursor = conn.cursor()

            # query bookmarks data
            cursor.execute("SELECT title, dateAdded FROM moz_bookmarks")

            firefox_bookmarks = cursor.fetchall()

            # close connection
            conn.close()

            # remove file copies
            if os.path.exists(destination):
                os.remove(destination)

            # add data to list
            bookmark_list = []
            for bookmark in firefox_bookmarks:
                name = bookmark[0]
                date_added = str(time_conversion.convert_unix_epoch_microseconds(bookmark[1]))

                bookmark_list.append([name, date_added])

            # format output
            output = display_functions.two_values("Bookmark", "Date Added", bookmark_list)
            formatted_output = "\n".join(output) + "\n"
            return formatted_output
    except Exception:
        destination = os.path.join(os.getcwd(), "bookmarks_copy")
        if os.path.exists(destination):
            os.remove(destination)
        return 0
