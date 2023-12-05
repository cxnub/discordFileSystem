"""Core module for the Discord File System."""
from typing import List

import os
import json
import random
from tqdm import tqdm
import aiohttp

import discord

from discordfilesystem.file_helper import split_file, merge_chunks
from discordfilesystem.webhook_helper import upload_files


CHUNKS_PER_UPLOAD = 5
this_file_dir = os.path.dirname(os.path.abspath(__file__))
cache_file = this_file_dir + "./files_cache.json"
cache_file = os.path.abspath(cache_file)


class FileSystem:
    """Core class for the Discord File System.

    This class represents the core functionality of the Discord FileSystem.
    It initializes necessary variables and data structures and contains the
    main logic of the program.

    Attributes
    ----------
        webhook_urls: The webhook urls to use for uploading files.

    Methods
    -------
        read_files_cache(self):
            Read the files cache.
        update_files_cache(self, file_id, urls, filename, size):
            Update the files cache.
        import_files_cache(self, files_cache_path):
            Import the files cache.
        export_files_cache(self, output_path, file_ids=None):
            Export the files cache.
        upload_chunks(self, session, file_chunks):
            Upload chunks to discord.
        upload_file(self, file_path, chunks_per_upload=5):
            Upload a file to discord.
        download_file(self, file_id, download_dir):
            Download a file from discord.
    """

    def __init__(self, webhook_urls: list[str]):
        """Initialize the Core class."""
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

    def import_files_cache(self, files_cache_path: str):
        """Import the files cache.

        Parameters
        ----------
        files_cache_path : str
            The path to the files cache.
        """
        # read the imported files cache
        with open(files_cache_path, "r", encoding="utf-8") as f:
            imported_files_cache = dict(json.load(f))

        # read the files cache
        files_cache = self.read_files_cache()

        # update the files cache
        files_cache.update(imported_files_cache)

        # write the files cache
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(files_cache, f, indent=4)

    def export_files_cache(
        self, output_dir: str,
        file_ids: List[int] = None,
        output_file_name: str = "files_cache.json"
    ):
        """Export the files cache.

        Parameters
        ----------
        output_dir : str
            The directory to export the files cache to.
        file_ids : list of int
            The ids of the files to export. Defaults to None.
        output_file_name : str
            The name of the output file. Defaults to "files_cache.json".
        """
        # get the directory to export the files cache to
        output_dir = os.path.abspath(output_dir)

        # read the files cache
        files_cache = self.read_files_cache()

        # filter the files cache
        files_cache = {
            file_id: files_cache[file_id] for file_id in file_ids
        }

        # generate a unique file name
        output_file = os.path.join(output_dir, output_file_name)
        output_file = self.generate_file_name(output_file)

        # write the files cache
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(files_cache, f, indent=4)

    def generate_file_name(self, file_path: str):
        """Generate a file name for a file.

        Parameters
        ----------
        file_path : str
            The path to the file.
        """

        # get the output file path
        output_path = os.path.abspath(file_path)

        index = 1
        while os.path.exists(output_path):
            name, extension = os.path.splitext(output_path)
            new_file_path = f"{name} ({index}){extension}"
            output_path = os.path.abspath(new_file_path)

            index += 1

        return output_path

    async def upload_chunks(
        self,
        session: aiohttp.ClientSession,
        file_chunks: List[str]
    ):
        """Upload chunks to discord.

        Parameters
        ----------
        session : aiohttp.ClientSession
            The aiohttp session to use.
        file_chunks : list of str
            The chunks to upload.
        Returns
        -------
        list of str
            The urls of the uploaded chunks.
        """
        # upload the chunks
        attachments = await upload_files(
            session, file_chunks, self.webhook_urls
        )

        # return the urls of the uploaded chunks
        return [attachment.url for attachment in attachments]

    async def upload_file(
        self, file_path: str, chunks_per_upload: int = CHUNKS_PER_UPLOAD
    ):
        """Upload a file to discord.

        Parameters
        ----------
        file_path : str
            The path to the file to upload.
        chunks_per_upload : int
            The number of chunks to upload per upload. Defaults to 5.
        """
        file_path = os.path.abspath(file_path)
        filename = os.path.basename(file_path)

        # get file size
        file_size = os.path.getsize(file_path)

        file_chunks = await split_file(file_path)

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
                    if index % chunks_per_upload == 0 or \
                            index == len(file_chunks) - 1:

                        # upload the chunk and store the urls
                        chunk_urls.extend(
                            await self.upload_chunks(session, chunk_files)
                        )

                        # reset the chunk files
                        chunk_files = []

                    # update the progress bar
                    progress_bar.update(os.path.getsize(chunk))

        # update the files cache
        self.update_files_cache(file_id, chunk_urls, filename, file_size)

        # remove the temporary chunk files
        for chunk in file_chunks:
            os.remove(chunk)

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
        filename = str(file_data["filename"])

        # get the output file path
        output_path = os.path.join(download_dir, filename)

        # generate a unique file name
        output_path = self.generate_file_name(output_path)

        # get the file size
        file_size = file_data["size"]

        # get the file urls
        file_urls = file_data["urls"]

        # download the file
        await merge_chunks(file_urls, file_size, output_path)
