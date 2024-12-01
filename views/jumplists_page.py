import flet as ft
from CustomLibs import config
from CustomLibs import jumplist_parsing
import os
import psutil

# functions
def clear_fields():
    dd_drives.value = None
    dd_users.value = None
    dd_users.options = []
    dd_applications.options = []

def get_page(page):
    global page_var
    page_var = page
    page_var.overlay.append(dlg_loading)
    page_var.overlay.append(dlg_message)

def drive_change(e):
    # clear application dropdown
    dd_applications.options = []

    # populate user list
    users = get_users(dd_drives.value)
    for user in users:
        dd_users.options.append(ft.dropdown.Option(user))

    # update values
    dd_users.update()
    dd_applications.update()

def user_change(e):
    # search jumplist applications
    dd_applications.options = []
    apps = jumplist_parsing.get_jumplist_apps(dd_drives.value, dd_users.value)
    for app in apps:
        dd_applications.options.append(ft.dropdown.Option(app))
    dd_applications.update()

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
    with open(output_path, 'w', encoding='utf-16') as file:
        file.write(data)

def open_text(file_path):
    if switch_open_file.value:
        os.startfile(file_path)

def parse(drive, user):
    if dd_applications.value is not None and dd_applications.value != "":
        open_dlg_loading()
        output = jumplist_parsing.parse_jumplist(drive, user, dd_applications.value)
        if output != 1:
            export_data(output, f"{user} {dd_applications.value} Jumplist.txt")
            dlg_loading.open = False
            open_text(os.path.join(config.output_path, f"{user} {dd_applications.value} Jumplist.txt"))
            open_message("Success", f"Jumplist data saved to {config.output_path}")
        else:
            dlg_loading.open = False
            open_message("Error", "Unable to parse jumplist file.")
    else:
        open_message("Error", "No application selected.")


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
dd_applications = ft.Dropdown(
    label="Applications",
    options=[]
)
# populate dd_drives
for drive in drives:
    dd_drives.options.append(ft.dropdown.Option(drive))

# buttons
b_parse = ft.ElevatedButton(
    "Parse Jumplists",
    height=50, width=250,
    on_click=lambda _: parse(dd_drives.value, dd_users.value)
)

# switches
switch_open_file = ft.Switch(label="Open data after parsing", value=False)

# dialogues
dlg_loading = ft.AlertDialog(
    title=ft.Text("Parsing Artifacts"),
    content=ft.ProgressRing(width=16, height=16, stroke_width=2)
)
dlg_message = ft.AlertDialog()


def jumplists_page(router):
    content = ft.Column([
        ft.Row([
            ft.Text("Jumplist Parsing", size=40)
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            dd_drives, dd_users, dd_applications
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            switch_open_file
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            b_parse
        ], alignment=ft.MainAxisAlignment.CENTER),
    ], alignment=ft.MainAxisAlignment.START)

    return content
