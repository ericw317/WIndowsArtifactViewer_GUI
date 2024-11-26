from CustomLibs import artifact_search as AS
from CustomLibs import InputValidation as IV
from CustomLibs import list_functions
from CustomLibs import config
import windowsprefetch
import os
import shutil
from tempfile import mkdtemp
from datetime import datetime
import pytz

def parse_prefetch(drive):
    prefetch_path = AS.set_path("Windows\\Prefetch", drive)  # set prefetch path
    prefetch_list = []

    # load prefetch files and sort them
    for file in os.listdir(prefetch_path):
        prefetch_list.append(os.path.join(prefetch_path, file))
    prefetch_list = list_functions.sort_files_by_modification(prefetch_list)
    prefetch_list.reverse()

    # get file name lengths for formatting
    file_name_list = []
    for file in prefetch_list:
        file_name_list.append(os.path.basename(file))

    # set spacing size for formatting
    longest_file_name = max(file_name_list, key=len)
    longest_length = len(longest_file_name)

    # set spacing size
    if longest_length <= 30:
        spacing = 30
    else:
        spacing = longest_length

    # Collect output into a list
    output_lines = []
    header = f"{'File Name':<{spacing}} | {'Executable Name':<{spacing}} | {'Run Count':<{spacing}} | {'Last Runtimes':<{spacing}}"
    output_lines.append(header)
    output_lines.append("-" * (spacing * 4))

    for file in prefetch_list:
        try:
            # load prefetch file and data
            pf = windowsprefetch.Prefetch(file)
            exe_name = pf.executableName
            run_count = pf.runCount
            last_runtimes = get_last_runtimes(pf, 8)

            # Construct the row
            row = f"{os.path.basename(file):<{spacing}} | {exe_name:<{spacing}} | {run_count:<{spacing}} | "
            output_lines.append(row)

            for x, runtime in enumerate(last_runtimes):
                try:
                    if x == 0:
                        output_lines[-1] += f"{runtime:<{spacing}}"
                    else:
                        runtime_line = f"{' ' * ((spacing * 3) + 9)}{runtime}"
                        output_lines.append(runtime_line)
                except IndexError:
                    continue

            output_lines.append("-" * (spacing * 4))
        except Exception:
            pass

    # Combine lines into a single string, or return the list
    return "\n".join(output_lines)  # Return as a single string

def parse_prefetch_external(drive):
    prefetch_path = AS.set_path("Windows\\Prefetch", drive)  # set prefetch path
    prefetch_list = []

    # make temp directory for analysis
    current_directory = os.getcwd()
    temp_dir = mkdtemp(dir=current_directory)
    try:
        for file_name in os.listdir(prefetch_path):
            if file_name.endswith(".pf"):
                full_file_name = os.path.join(prefetch_path, file_name)

                # Only copy if it's a file (skip directories or anything else)
                if os.path.isfile(full_file_name):
                    shutil.copy2(full_file_name, temp_dir)  # copy2 preserves metadata (modification times, etc.)
    except Exception as e:
        print(f"Error copying files: {e}")

    # load prefetch files and sort them
    for file in os.listdir(temp_dir):
        prefetch_list.append(os.path.join(temp_dir, file))
    prefetch_list = list_functions.sort_files_by_modification(prefetch_list)
    prefetch_list.reverse()

    # get file name lengths for formatting
    file_name_list = []
    for file in prefetch_list:
        file_name_list.append(os.path.basename(file))

    # set spacing size for formatting
    longest_file_name = max(file_name_list, key=len)
    longest_length = len(longest_file_name)

    # set spacing size
    if longest_length <= 30:
        spacing = 30
    else:
        spacing = longest_length

    # Collect output into a list
    output_lines = []
    header = f"{'File Name':<{spacing}} | {'Executable Name':<{spacing}} | {'Run Count':<{spacing}} | {'Last Runtimes':<{spacing}}"
    output_lines.append(header)
    output_lines.append("-" * (spacing * 4))

    for file in prefetch_list:
        try:
            # load prefetch file and data
            pf = windowsprefetch.Prefetch(file)
            exe_name = pf.executableName
            run_count = pf.runCount
            last_runtimes = get_last_runtimes(pf, 8)

            # Construct the row
            row = f"{os.path.basename(file):<{spacing}} | {exe_name:<{spacing}} | {run_count:<{spacing}} | "
            output_lines.append(row)

            for x, runtime in enumerate(last_runtimes):
                try:
                    if x == 0:
                        output_lines[-1] += f"{runtime:<{spacing}}"
                    else:
                        runtime_line = f"{' ' * ((spacing * 3) + 9)}{runtime}"
                        output_lines.append(runtime_line)
                except IndexError:
                    continue

            output_lines.append("-" * (spacing * 4))
        except Exception:
            pass

    shutil.rmtree(temp_dir)
    # Combine lines into a single string, or return the list
    return "\n".join(output_lines)  # Return as a single string

def get_last_runtimes(pf_file, num):
    runtime_list = []
    try:
        timezone = pytz.timezone(config.timezone)
        for x in range(num):
            runtime = datetime.strptime(pf_file.timestamps[x], "%Y-%m-%d %H:%M:%S.%f")
            runtime_utc = pytz.utc.localize(runtime)
            runtime_converted = runtime_utc.astimezone(timezone)
            runtime_list.append(f"{runtime_converted.strftime('%Y-%m-%d %H:%M:%S%z')}")
            # runtime = f"{(pf_file.timestamps[x])[:-7]} UTC"
            # runtime_list.append(runtime)
    except IndexError:
        pass
    return runtime_list

def main(drive):
    if drive == "C:\\":
        return parse_prefetch(drive)
    else:
        return parse_prefetch(drive)
