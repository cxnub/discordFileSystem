"""Command line interface for the application."""
import os
import json
import asyncio
from functools import partial
from inspect import iscoroutinefunction

from discordfilesystem import core


this_file_dir = os.path.dirname(os.path.abspath(__file__))


# ------------------------------ Commands ------------------------------

def read_config():
    """Read the config file.

    Returns
    -------
    dict
        The config file.
    """
    # read the config file
    with open("./config.json", "r", encoding="utf-8") as f:
        return dict(json.load(f))


def format_bytes(size: int) -> str:
    """Format bytes to a human readable format.

    Parameters
    ----------
    size : int
        The size in bytes.

    Returns
    -------
    str
        The formatted size.
    """
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {power_labels[n]}B"


def show_files(file_system: core.FileSystem):
    """Show the files in the files cache.

    Parameters
    ----------
    file_system : `discordfilesystem.core.FileSystem`
        The file system to use.
    """

    files_cache = file_system.read_files_cache()

    # define the padding for each column
    padding = 6

    files_cache_keys = files_cache.keys()
    files_cache_values = files_cache.values()

    # get the largest strings for each column
    max_id_length = len(max(files_cache_keys, key=lambda x: len(str(x)))) + \
        padding
    max_filename_length = len(
        max(
            files_cache_values,
            key=lambda x: len(x["filename"]))["filename"]
    ) + padding
    max_size_length = max(
        len(format_bytes(file["size"])) for file in files_cache_values
    ) + padding

    # print the column headers
    print(
        f"{'id':^{max_id_length}}║ " +
        f"{'filename':^{max_filename_length}}║ " +
        f"{'size':^{max_size_length}}\n" +
        "═" * (max_id_length + max_filename_length + max_size_length + 3)
    )

    for file_id, file in files_cache.items():
        print(
            f"{file_id:^{max_id_length}}║ " +
            f"{file['filename']:^{max_filename_length}}║ " +
            f"{format_bytes(file['size']):^{max_size_length}}"
        )

    input("\nPress enter to continue...")


async def upload(file_system: core.FileSystem):
    """Upload a file to discord.

    Parameters
    ----------
    file_system : `discordfilesystem.core.FileSystem`
        The file system to use.
    """

    # get the file path
    file_path = input("Enter file path: ")

    # check if file exists
    if not os.path.isfile(file_path):
        print("Could not find file at " + file_path)

    file_path = os.path.abspath(file_path)

    # upload the file
    await file_system.upload_file(file_path)


async def download(file_system: core.FileSystem):
    """Download a file from discord.

    Parameters
    ----------
    file_system : `discordfilesystem.core.FileSystem`
        The file system to use.
    download_dir : str
        The directory to download the file to.
    """
    download_dir = read_config()["download_dir"]
    file_id = input("Enter file id: ")
    await file_system.download_file(file_id, download_dir)


def show_commands():
    """Show the help menu."""
    print("""
Commands
--------
1. Show files
2. Upload file
3. Download file
4. Settings
5. Help
6. Quit
          """)


def show_help():
    """Show the help menu."""
    print("""
Help Menu
---------
1. Show files - Show the files in the files cache.
2. Upload file - Upload a file to discord.
3. Download file - Download a file from discord.
4. Settings - Change config settings.
5. Help - Show the help menu.
6. Quit - Exit the program.
            """)

# ------------------------------ Settings ------------------------------


def add_webhooks():
    """Add webhooks to the config file."""

    config = read_config()
    while True:
        webhook_url = input("Enter webhook url (leave blank to stop): ")
        if webhook_url.isspace() or webhook_url == "":
            break
        config["webhooks"].append(webhook_url)
    with open("./config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def add_download_dir():
    """Add a download directory to the config file."""

    config = read_config()
    download_dir = input("Enter download directory: ")

    if not os.path.isdir(download_dir):
        print("Directoy not found")
        exit()

    download_dir = os.path.abspath(download_dir)
    config["download_dir"] = download_dir

    with open("./config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def import_files_cache(file_system: core.FileSystem):
    """Import the files cache from a json file.

    Parameters
    ----------
    file_system : `discordfilesystem.core.FileSystem`
        The file system to use.
    """
    # get the file path
    file_path = input("Enter file path: ")

    # check if file exists
    if not os.path.isfile(file_path):
        print("Could not find file at " + file_path)
        return

    file_path = os.path.abspath(file_path)

    # import the files cache
    file_system.import_files_cache(file_path)

    print(f"{file_path} imported successfully.")


def export_files_cache(file_system: core.FileSystem):
    """Export the files cache to a json file.

    Parameters
    ----------
    file_system : `discordfilesystem.core.FileSystem`
        The file system to use.
    """
    os.system("cls" if os.name == "nt" else "clear")

    show_files(file_system)

    # get all the file ids
    file_ids = list(file_system.read_files_cache().keys())

    # get file ids to export
    file_ids_to_export = []
    while True:
        user_input = input(
            "Enter file id (leave blank to stop, input 'all' to export all):\n"
        )

        if user_input == "all":
            file_ids_to_export = file_ids
            break

        if user_input in file_ids:
            file_ids_to_export.append(user_input)

        elif user_input == "":
            break

        else:
            print("Invalid file id...")

    # get the output directory
    output_dir = this_file_dir + "/exports"

    # create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # export the files cache
    file_system.export_files_cache(output_dir, file_ids_to_export)

    print(f"Files exported successfully to {output_dir}.")


async def settings(file_system: core.FileSystem):
    """Show the settings menu.

    Parameters
    ----------
    file_system : `discordfilesystem.core.FileSystem`
        The file system to use.
    """
    settings_list = [
        partial(import_files_cache, file_system),
        partial(export_files_cache, file_system),
        add_webhooks,
        add_download_dir
    ]

    while True:

        print("""
Settings
--------
1. Import Files Cache
2. Export Files Cache
3. Add webhooks
4. Change download directory
5. Back
    """)

        user_input = input("Enter command (back): ")

        if not user_input.isdigit() or \
                (int(user_input)) - 1 not in range(len(settings_list) + 1):
            print("Invalid command...")
            continue

        user_input = int(user_input) - 1

        if user_input == len(settings_list):
            break

        # get the command index
        command_index = user_input

        # get the command
        command = settings_list[command_index]

        # check if command is coroutine
        if iscoroutinefunction(command):

            # run the command
            await command()

        else:
            # run the command
            command()


# ------------------------------ Main ------------------------------


async def main():
    """The main function."""
    print(r"""
  ____  _                       _ _____ _ _      
 |  _ \(_)___  ___ ___  _ __ __| |  ___(_) | ___ 
 | | | | / __|/ __/ _ \| '__/ _` | |_  | | |/ _ \
 | |_| | \__ \ (_| (_) | | | (_| |  _| | | |  __/
 |____/|_|___/\___\___/|_|  \__,_|_|   |_|_|\___|
 / ___| _   _ ___| |_ ___ _ __ ___               
 \___ \| | | / __| __/ _ \ '_ ` _ \              
  ___) | |_| \__ \ ||  __/ | | | | |             
 |____/ \__, |___/\__\___|_| |_| |_|             
        |___/

Made by: cxnub
Github: https://github.com/cxnub/discordFileSystem
__________________________________________________                              
          """
          )

    webhooks = read_config()["webhooks"]
    download_dir = read_config()["download_dir"]

    if not webhooks:
        print("Error: No webhooks found in config.json")
        if input("Would you like to add some now? (y/n): ") == "y":
            add_webhooks()
        else:
            print("Exiting...")
            exit()

    if not download_dir:
        print("Error: No download directory found in config.json")
        if input("Would you like to add one now? (y/n): ") == "y":
            add_download_dir()
        else:
            print("Exiting...")
            exit()

    file_system = core.FileSystem(webhooks)

    commands_list = [
        partial(show_files, file_system),
        partial(upload, file_system),
        partial(download, file_system),
        partial(settings, file_system),
        show_help,
        exit
    ]

    while True:
        # show the commands
        show_commands()
        user_input = input("Enter command (help): ")

        # check if user input is a digit and is in range of commands list
        if not user_input.isdigit() or \
                (int(user_input)) - 1 not in range(len(commands_list)):

            print("Invalid command... Type help for a list of commands")
            continue

        # get the command index
        command_index = int(user_input) - 1

        # get the command
        command = commands_list[command_index]

        # check if command is coroutine
        if iscoroutinefunction(command):

            # run the command
            await command()

        else:
            # run the command
            command()


if __name__ == "__main__":
    asyncio.run(main())
