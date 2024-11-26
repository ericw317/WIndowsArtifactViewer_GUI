import os

def set_path(artifact_path, drive):
    if "[root]" in os.listdir(drive):
        path = drive + f"[root]\\{artifact_path}"
    else:
        path = drive + artifact_path

    return path

# return list of all user profiles
def get_user_list(drive):
    exclusion_list = ["All Users", "Default", "Default User", "Public"]
    user_list = []
    users_path = set_path("Users", drive)

    for user in os.listdir(users_path):
        if os.path.isdir(os.path.join(users_path, user)) and user not in exclusion_list:
            user_list.append(user)

    return user_list

# search Recent Items
def search_recent_items(drive, user):
    user_path = set_path(f"Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\Recent", drive)

    if os.path.exists(user_path):
        if bool(os.listdir(user_path)):
            return True

    return False

# search for prefetch files
def search_prefetch(drive):
    prefetch_path = set_path("Windows\\Prefetch", drive)  # set path to prefetch files
    return os.path.exists(prefetch_path) and bool(os.listdir(prefetch_path))  # check if path and files exist

def search_internet(drive, user):
    # initialize user list and internet locations
    try:
        internet_locations = {
            "chrome": f"{drive}Users\\{user}\\AppData\\Local\\Google\\Chrome",
            "edge": f"{drive}Users\\{user}\\AppData\\Local\\Microsoft\\Edge",
            "brave": f"{drive}Users\\{user}\\AppData\\Local\\BraveSoftware\\Brave-Browser",
            "firefox": f"{drive}Users\\{user}\\AppData\\Roaming\\Mozilla\\Firefox"
        }

        # change locations if mounted drive has been selected
        if "[root]" in os.listdir(drive):
            for key in internet_locations:
                internet_locations[key] = internet_locations[key].replace(f"{drive}Users\\", f"{drive}[root]\\Users\\")

        # get list of available browsers
        browser_list = []
        if os.path.exists(internet_locations["chrome"]):
            browser_list.append("Chrome")
        if os.path.exists(internet_locations["edge"]):
            browser_list.append("Edge")
        if os.path.exists(internet_locations["brave"]):
            browser_list.append("Brave")
        if os.path.exists(internet_locations["firefox"]):
            browser_list.append("Firefox")

        return browser_list
    except Exception:
        return False

# search for $Recycle.Bin contents
def search_recycle_bin(drive):
    try:
        recycle_path = set_path("$Recycle.Bin", drive)
        if os.path.exists(recycle_path):
            for folder in os.listdir(recycle_path):
                for file in os.listdir(os.path.join(recycle_path, folder)):
                    if file.startswith("$I"):
                        return True
        return False
    except Exception:
        return False
