import flet as ft
from CustomLibs import config
from CustomLibs import artifact_search as AS
from CustomLibs.FileArtifacts import recent_items_parsing
from CustomLibs.FileArtifacts import prefetch_parsing
from CustomLibs.FileArtifacts import recycle_bin_parsing
import os
import psutil

# functions
def clear_fields():
    dd_drives.value = None
    dd_users.value = None
    c_recent.value = None
    c_prefetch.value = None
    c_recycle_bin.value = None
    dd_users.options = []
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

    # search artifacts
    search_artifacts(dd_drives.value, dd_users.value)

def user_change(e):
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
    with open(output_path, 'w', encoding='utf-16') as file:
        file.write(data)

def grey_checkboxes(initial=False):
    # set all checkboxes to false and disabled
    checkboxes = [c_recent, c_prefetch, c_recycle_bin]
    for checkbox in checkboxes:
        checkbox.disabled = True
        checkbox.value = False
        if not initial:
            checkbox.update()

def search_artifacts(drive, user=None):
    grey_checkboxes()

    # search artifacts
    if AS.search_recent_items(drive, user):
        c_recent.disabled = False
        c_recent.update()
    if AS.search_prefetch(drive):
        c_prefetch.disabled = False
        c_prefetch.update()
    if AS.search_recycle_bin(drive):
        c_recycle_bin.disabled = False
        c_recycle_bin.update()

def open_text(file_path):
    if switch_open_file.value:
        os.startfile(file_path)

def parse(drive, user):
    open_dlg_loading()
    success = False
    if c_recent.value:
        output = recent_items_parsing.main(drive, user)
        export_data(output, f"({dd_drives.value[0]}) {dd_users.value} Recent Data.txt")
        open_text(os.path.join(config.output_path, f"({dd_drives.value[0]}) {dd_users.value} Recent Data.txt"))
        success = True
    if c_prefetch.value:
        output = prefetch_parsing.main(drive)
        export_data(output, f"({dd_drives.value[0]}) Prefetch Data.txt")
        open_text(os.path.join(config.output_path, f"({dd_drives.value[0]}) Prefetch Data.txt"))
        success = True
    if c_recycle_bin.value:
        output = recycle_bin_parsing.parse_recycle_bin(drive, dd_users.value)
        if dd_users.value is not None and dd_users.value != "":
            file_name = f"({dd_drives.value[0]}) {dd_users.value} $Recycle.Bin Data.txt"
            export_data(output, file_name)
            open_text(os.path.join(config.output_path, f"({dd_drives.value[0]}) {dd_users.value} $Recycle.Bin Data.txt"))
        else:
            file_name = f"({dd_drives.value[0]}) $Recycle.Bin Data.txt"
            export_data(output, file_name)
            open_text(os.path.join(config.output_path, f"({dd_drives.value[0]}) $Recycle.Bin Data.txt"))
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
# populate dd_drives
for drive in drives:
    dd_drives.options.append(ft.dropdown.Option(drive))

# buttons
b_parse = ft.ElevatedButton(
    "Parse Jumplists",
    height=50, width=250,
    on_click=lambda _: parse(dd_drives.value, dd_users.value)
)

# checkboxes
c_recent = ft.Checkbox(label="Recent Items", disabled=True)
c_prefetch = ft.Checkbox(label="Prefetch", disabled=True)
c_recycle_bin = ft.Checkbox(label="$Recycle.Bin", disabled=True)

# switches
switch_open_file = ft.Switch(label="Open data after parsing", value=False)

# dialogues
dlg_loading = ft.AlertDialog(
    title=ft.Text("Parsing Artifacts"),
    content=ft.ProgressRing(width=16, height=16, stroke_width=2)
)
dlg_message = ft.AlertDialog()


def file_artifacts_page(router):
    content = ft.Column([
        ft.Row([
            ft.Text("File Artifacts", size=40)
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            dd_drives, dd_users
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            c_recent, c_prefetch, c_recycle_bin
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            switch_open_file
        ], alignment=ft.MainAxisAlignment.CENTER),
        ft.Row([
            b_parse
        ], alignment=ft.MainAxisAlignment.CENTER),
    ], alignment=ft.MainAxisAlignment.START)

    return content
