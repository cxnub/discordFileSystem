"""Command line interface for the application."""
import os
import json
import asyncio

from discordfilesystem import core


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

    # print table like structure of files
    print("id\t| filename\t| size")
    print("-" * 40)
    for file_id, file in files_cache.items():
        print(
            f"{file_id}\t| {file['filename']}\t| {format_bytes(file['size'])}"
        )


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

    webhooks = read_config()["webhooks"]
    download_dir = read_config()["download_dir"]
    file_system = core.FileSystem(webhooks)

    while True:
        command = input("Enter command (help): ")

        if command == "exit":
            break

        if command == "upload":
            # get the file path
            file_path = input("Enter file path: ")

            # check if file exists
            if not os.path.isfile(file_path):
                print("Could not find file at " + file_path)

            file_path = os.path.abspath(file_path)

            # upload the file
            await file_system.upload_file(file_path)

        elif command == "download":
            file_id = str(input("Enter file id: "))
            await file_system.download_file(file_id, download_dir)

        # elif command == "delete":
        #     file_id = int(input("Enter file id: "))
        #     file_system.delete_file(file_id)

        elif command == "list":
            show_files(file_system)

        elif command == "help":
            print(
                "upload - Upload a file\n" +
                "download - Download a file\n" +
                "list - List all files\n" +
                "exit - Exit the program\n" +
                "help - Show this message\n" +
                "add_webhooks - Add webhooks"
            )

        elif command == "add_webhooks":
            add_webhooks()

        else:
            print("Invalid command")


if __name__ == "__main__":
    asyncio.run(main())
