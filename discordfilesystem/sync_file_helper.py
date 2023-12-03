"""Helper functions to manage files."""
from typing import List
import os
from io import BytesIO
import discord
import requests
from tqdm import tqdm


def split_file(
    file_path: str, filename: str, chunk_size: int = 24_000_000
) -> List[discord.File]:
    """Split a file into chunks.

    Parameters
    ----------
    file_path : str
        The full path to the file to split into chunks.
    filename : str
        The name of the file to upload to discord.
    chunk_size: int
        The size per chunk. Defaults to 24000000.

    Returns
    -------
    List of `discord.File`
        _description_
    """

    files = []

    with open(file_path, "rb") as file:

        # index to keep track of chunks
        index = 0

        # read file by chunks of chunk size
        while (chunk := file.read(chunk_size)):

            # create a discord file object for each chunk
            discord_file = discord.File(
                BytesIO(chunk), filename=f"{filename}.{index}"
            )

            # append discord.File object to the list of files
            files.append(discord_file)

            # increment the index
            index += 1

    return files


def download_chunk(url: str, output_file: str, progress_bar: tqdm):
    """Download a chunk from a url.

    Parameters
    ----------
    url : str
        The url to download the chunk from.
    output_file : str
        The path to the file to save the chunk to.
    progress_bar : tqdm
        The progress bar to update.
    """

    # get the chunk
    response = requests.get(url, timeout=60)

    # check if chunk is downlaoded successfully
    if response.status_code == 200:

        # open the output file and append to it
        with open(output_file, 'ab') as f:
            content = response.content
            f.write(content)

            progress_bar.update(len(content))

    else:
        print(
            "Failed to download chunk from " +
            f"{url}, status code: {response.status_code}"
        )


def merge_chunks(chunk_urls: [], total_size: int, filepath: str):
    """Merge chunks into a single file.

    Parameters
    ----------
    chunk_urls : list
        The list of urls to download the chunks from.
    total_size : int
        The total size of the file to download.
    filepath : str
        The path to the file to save the merged chunks to.
    """

    with tqdm(
        total=total_size, unit='B', unit_scale=True, desc=filepath
    ) as progress_bar:
        for url in chunk_urls:
            download_chunk(url, os.path.abspath(filepath), progress_bar)

    print(f"File downloaded successfully at '{filepath}'")
