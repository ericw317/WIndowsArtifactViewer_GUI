import flet as ft
from CustomLibs import config
from CustomLibs import artifact_search as AS
from CustomLibs.InternetArtifacts import history_parsing
from CustomLibs.InternetArtifacts import downloads_parsing
from CustomLibs.InternetArtifacts import bookmarks_parsing
from CustomLibs.InternetArtifacts import logins_parsing
import os
import psutil

# functions
def clear_fields():
    dd_drives.value = None
    dd_users.value = None
    dd_browser.value = None
    dd_users.options = []
    dd_browser.options = []
    c_history.value = None
    c_downloads.value = None
    c_bookmarks.value = None
    c_logins.value = None
    grey_checkboxes(initial=True)

def get_page(page):
    global page_var
    page_var = page
    page_var.overlay.append(dlg_loading)
    page_var.overlay.append(dlg_message)

def drive_change(e):
    # populate user list
    users = get_users(dd_drives.value)
    for user in users:
        dd_users.options.append(ft.dropdown.Option(user))
    dd_users.update()

    # set browser option to none
    dd_browser.value = None

    # search artifacts
    search_artifacts(dd_drives.value, dd_users.value)

def user_change(e):
    # search artifacts
    search_artifacts(dd_drives.value, dd_users.value)

def browser_change(e):
    # search artifacts
    search_artifacts(dd_drives.value, dd_users.value)

def open_dlg_loading(e=None):
    page_var.dialogue = dlg_loading
    dlg_loading.open = True
    page_var.update()

def open_message(title, message, e=None):
    dlg_message.title = ft.Text(title)
    dlg_message.content = ft.Text(message)
    page_var.dialog = dlg_message
    dlg_message.open = True
    page_var.update()

def get_users(drive):
    dd_users.options = []
    user_list = []
    exclusion_list = ["All Users", "Default", "Default User", "Public"]
    try:
        if drive == "C:\\":
            users_path = f"{drive}Users"
        else:
            users_path = f"{drive}[root]\\Users"

        for user in os.listdir(users_path):
            full_path = os.path.join(users_path, user)
            if os.path.isdir(full_path) and user not in exclusion_list:
                user_list.append(user)
    except Exception:
        user_list = []

    return user_list

def list_drives():
    partitions = psutil.disk_partitions()
    drives = []

    # add each drive to a dictionary and enumerate each entry
    for partition in partitions:
        drives.append(partition.device)

    return drives

def export_data(data, filename):
    output_path = os.path.join(config.output_path, filename)
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(data)

def search_artifacts(drive, user=None):
    # find available browsers
    browser_list = AS.search_internet(drive, user)
    dd_browser.options = []
    for browser in browser_list:
        dd_browser.options.append(ft.dropdown.Option(browser))
    dd_browser.update()

    # make checkboxes available if browser is selected
    if dd_browser.value is None or dd_browser.value == "":
        grey_checkboxes()
    else:
        ungrey_checkboxes()

def grey_checkboxes(initial=False):
    # set all checkboxes to false and disabled
    checkboxes = [c_history, c_downloads, c_bookmarks, c_logins]
    for checkbox in checkboxes:
        checkbox.disabled = True
        checkbox.value = False
        if not initial:
            checkbox.update()

def ungrey_checkboxes(initial=False):
    # set all checkboxes to false and disabled
    checkboxes = [c_history, c_downloads, c_bookmarks, c_logins]
    for checkbox in checkboxes:
        checkbox.disabled = False
        checkbox.update()

def open_text(file_path):
    if switch_open_file.value:
        os.startfile(file_path)

def parse(drive, user):
    open_dlg_loading()
    success = False

    if c_history.value:
        output = history_parsing.collect_history(drive, user, dd_browser.value)
        export_data(output, f"{dd_users.value} {dd_browser.value} History.txt")
        open_text(os.path.join(config.output_path, f"{dd_users.value} {dd_browser.value} History.txt"))
        success = True
    if c_downloads.value:
        output = downloads_parsing.collect_downloads(drive, user, dd_browser.value)
        export_data(output, f"{user} {dd_browser.value} Downloads.txt")
        open_text(os.path.join(config.output_path, f"{user} {dd_browser.value} Downloads.txt"))
        success = True
    if c_bookmarks.value:
        output = bookmarks_parsing.collect_bookmarks(drive, user, dd_browser.value)
        export_data(output, f"{user} {dd_browser.value} Bookmarks.txt")
        open_text(os.path.join(config.output_path, f"{user} {dd_browser.value} Bookmarks.txt"))
        success = True
    if c_logins.value:
        output = logins_parsing.main(drive, user, dd_browser.value)
        export_data(output, f"{user} {dd_browser.value} Logins.txt")
        open_text(os.path.join(config.output_path, f"{user} {dd_browser.value} Logins.txt"))
        success = True

    dlg_loading.open = False

    if success:
        open_message("Success", f"Artifact data saved to {config.output_path}")
    else:
        open_message("Error", "No artifacts selected.")


# variables
drives = list_drives()

# dropdowns
dd_drives = ft.Dropdown(
    label="Drives",
    options=[],
    on_change=drive_change
)
dd_users = ft.Dropdown(
    label="Users",
    options=[],
    on_change=user_change
)
dd_browser = ft.Dropdown(
    label="Browser",
    options=[],
    on_change=browser_change
)
# populate dd_drives
for drive in drives:
    dd_drives.options.append(ft.dropdown.Option(drive))

# buttons
b_parse = ft.ElevatedButton(
    "Parse Artifacts",
    height=50, width=250,
    on_click=lambda _: parse(dd_drives.value, dd_users.value)
)

# checkboxes
c_history = ft.Checkbox(label="History")
c_downloads = ft.Checkbox(label="Downloads")
c_bookmarks = ft.Checkbox(label="Bookmarks")
c_logins = ft.Checkbox(label="Logins")

# switches
switch_open_file = ft.Switch(label="Open data after parsing", value=False)

# dialogues
dlg_loading = ft.AlertDialog(
    title=ft.Text("Parsing Artifacts"),
    content=ft.ProgressRing(width=16, height=16, stroke_width=2)
)
dlg_message = ft.AlertDialog()


def internet_artifacts_page(router):
    content = ft.Column([
        ft.Row([
            ft.Text("Internet Artifacts", size=40)
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            dd_drives, dd_users, dd_browser
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            c_history, c_downloads, c_bookmarks, c_logins
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            switch_open_file
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            b_parse
        ], alignment=ft.MainAxisAlignment.CENTER),
    ], alignment=ft.MainAxisAlignment.START)

    return content
