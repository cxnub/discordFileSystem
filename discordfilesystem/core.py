"""Core module for the Discord File System."""
from typing import List

import os
import json
import random
from tqdm import tqdm

import discord

from file_helper import split_file, merge_chunks
from webhook_helper import upload_files


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

    def __init__(self, directory: str, webhook_url: str):
        """Initialize the Core class."""
        self.directory = directory
        self.webhook_url = webhook_url

    def read_files_cache(self):
        """read the files cache.

        Returns
        -------
        dict
            The files cache.
        """
        # read the files cache
        with open("files_cache.json", "r", encoding="utf-8") as f:
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
        with open("files_cache.json", "w", encoding="utf-8") as f:
            json.dump(files_cache, f, indent=4)

    async def upload_file(self, file_path: str):
        """Upload a file to discord.

        Parameters
        ----------
        file_path : str
            The path to the file to upload.
        """
        file_path = os.path.abspath(file_path)
        filename = os.path.basename(file_path)
        temp_folder = os.path.abspath("./temp_upload_files/")

        # get file size
        file_size = os.path.getsize(file_path)

        file_chunks = split_file(file_path, temp_folder=temp_folder)

        # read files cache
        files_cache = self.read_files_cache()

        while True:
            # generate a unique id for the file upload
            file_id = random.randint(1, 9999)

            # check if the file id already exists
            if file_id not in files_cache.keys():
                break

        chunk_urls = []

        with tqdm(
            total=file_size,
            desc="Uploading file",
            unit="B",
            unit_scale=True
        ) as progress_bar:
            for index, chunk in enumerate(file_chunks):

                # create a discord file object
                discord_file = discord.File(
                    chunk, filename=f"{file_id}.{index}"
                )

                # upload the file
                attachments = await upload_files(
                    [discord_file], self.webhook_url
                )

                # add the url to the list of chunk urls
                chunk_urls.append(attachments[0].url)

                # update the progress bar
                progress_bar.update(os.path.getsize(chunk))

                # delete the temporary file
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
        await self.upload_file("valorant.mp4")

        # download a file
        download_dir = os.path.abspath("./downloaded_files/")
        await self.download_file("7691", download_dir=download_dir)


# if __name__ == "__main__":
#     core = FileSystem(
#         "./", "https://discord.com/api/webhooks/1179721340689842236/ZBJk8ZokbSuAMPYDB3clIZuYa7gnw95wsRgEOi5ZqwdVqupmt4N1I-1eovLAR8kFzr02")
#     asyncio.run(core.test())
