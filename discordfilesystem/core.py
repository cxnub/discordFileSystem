"""Core module for the Discord File System."""
from typing import List

import os
import json
import random
import asyncio
from tqdm import tqdm
import aiohttp

import discord

from file_helper import split_file, merge_chunks
from webhook_helper import upload_files


this_file_dir = os.path.dirname(os.path.abspath(__file__))
cache_file = this_file_dir + "./files_cache.json"
cache_file = os.path.abspath(cache_file)


class FileSystem:
    """Core class for the Discord File System.

    This class represents the core functionality of the Discord FileSystem.
    It initializes necessary variables and data structures and contains the
    main logic of the program.

    Attributes:
        None

    Methods:
        __init__(): Initializes the Core class.
        run(): Executes the main logic of the program.
    """

    def __init__(self, directory: str, webhook_urls: list[str]):
        """Initialize the Core class."""
        self.directory = directory
        self.webhook_urls = webhook_urls

    def read_files_cache(self):
        """read the files cache.

        Returns
        -------
        dict
            The files cache.
        """
        # read the files cache
        with open(cache_file, "r", encoding="utf-8") as f:
            return dict(json.load(f))

    def update_files_cache(
        self, file_id: int, urls: List[str], filename: str, size: int
    ):
        """Update the files cache.

        Parameters
        ----------
        file_id : int
            The id of the file.
        urls : list of str
            The urls of the file.
        filename : str
            The name of the file.
        size : int
            The size of the file.
        """
        # read the files cache
        files_cache = self.read_files_cache()

        # update the files cache
        files_cache[file_id] = {
            "filename": filename,
            "size": size,
            "urls": urls
        }

        # write the files cache
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(files_cache, f, indent=4)

    async def upload_file(
        self, file_path: str, chunks_per_upload: int = 4
    ):
        """Upload a file to discord.

        Parameters
        ----------
        file_path : str
            The path to the file to upload.
        chunks_per_upload : int
            The number of chunks to upload per upload. Defaults to 4.
        """
        file_path = os.path.abspath(file_path)
        filename = os.path.basename(file_path)
        temp_folder = os.path.abspath("./temp_upload_files/")

        # get file size
        file_size = os.path.getsize(file_path)

        file_chunks = await split_file(file_path, temp_folder=temp_folder)

        # read files cache
        files_cache = self.read_files_cache()

        while True:
            # generate a unique id for the file upload
            file_id = random.randint(1, 9999)

            # check if the file id already exists
            if file_id not in files_cache.keys():
                break

        # list of chunk files
        chunk_files = []

        # list of chunk urls
        chunk_urls = []

        # create an aiohttp session
        async with aiohttp.ClientSession() as session:

            # create a progress bar
            with tqdm(
                total=file_size,
                desc="Uploading file",
                unit="B",
                unit_scale=True
            ) as progress_bar:

                # iterate over the file chunks
                for index, chunk in enumerate(file_chunks):

                    # add the file to the list of chunk files
                    chunk_files.append(
                        discord.File(chunk, filename=f"{file_id}.{index}")
                    )

                    # check if the number of chunks per upload has been reached
                    if (index + 1) % chunks_per_upload == 0:

                        # upload the chunk
                        attachments = await upload_files(
                            session, chunk_files, self.webhook_urls
                        )

                        # add the urls to the list of chunk urls
                        chunk_urls.extend(
                            [attachment.url for attachment in attachments]
                        )

                        # reset the chunk files
                        chunk_files = []

                    # update the progress bar
                    progress_bar.update(os.path.getsize(chunk))

        # remove the temporary chunk files
        for chunk in file_chunks:
            os.remove(chunk)

        # update the files cache
        self.update_files_cache(file_id, chunk_urls, filename, file_size)

    async def download_file(self, file_id: int, download_dir: str):
        """Download a file from discord.

        Parameters
        ----------
        file_id : int
            The id of the file to download.
        download_dir : str
            The directory to download the file to.
        """
        # read the files cache
        files_cache = self.read_files_cache()

        # check if the file id exists
        if file_id not in files_cache.keys():
            print("File not found.")
            return

        # get the file data
        file_data = files_cache[file_id]

        # get the file name
        filename = file_data["filename"]

        # get te output file path
        output_path = os.path.join(download_dir, filename)

        # get the file size
        file_size = file_data["size"]

        # get the file urls
        file_urls = file_data["urls"]

        # temporary folder to store the chunks
        temp_folder = os.path.abspath("./temp_download_files/")

        # download the file
        await merge_chunks(
            file_urls, file_size, output_path, temp_folder=temp_folder
        )

    async def test(self):
        """Test the Discord File System."""

        # upload a file
        # await self.upload_file("C:\\Users\\broth\\Code\\Discord Bots\\discordFileSystem\\discordfilesystem\\downloaded_files\\valorant.mp4")

        # create the download directory
        if not os.path.exists("./downloaded_files/"):
            os.makedirs("./downloaded_files/")

        # download a file
        download_dir = os.path.abspath("./downloaded_files/")
        await self.download_file("3571", download_dir=download_dir)


if __name__ == "__main__":
    webhooks = [
        "https://discord.com/api/webhooks/1179721340689842236/ZBJk8ZokbSuAMPYDB3clIZuYa7gnw95wsRgEOi5ZqwdVqupmt4N1I-1eovLAR8kFzr02",
        "https://discord.com/api/webhooks/1180123961909051473/dRRzVJ93BL6E2x-r5sb3Rt45lPVGtkR9IpabCOABcWXIp_7Hyz0khTljuA6gzNALBJD7",
        "https://discord.com/api/webhooks/1179721808421867590/gQ77GS_in15R_Z5vOw10EK5XMgpc6jV8MkCZyDQGBU_0EEz487Vl9fOdjSjhnT5-j1yo",
        "https://discord.com/api/webhooks/1179721862863917056/dpRDWWW4ce8W3gI29NVvKsO9I8EOxvZbPLH3pv89bsSO9j9H42i0SZ2PViYXoP9oRrhA",
        "https://discord.com/api/webhooks/1179721901233418314/tULNftikKEuJFeJfkzMyGyUiZgzSfnUdA1JsOKHlzF5fsViY75EJqKCPBck18E3xXs9X"
    ]
    core = FileSystem(
        "./", webhooks)
    asyncio.run(core.test())
