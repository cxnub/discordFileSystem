"""Helper functions to manage files."""
from typing import List
import os
import asyncio
import aiohttp
import aiofiles
from tqdm import tqdm


CHUNK_SIZE = 24_000_000


async def split_file(
    file_path: str,
    chunk_size: int = CHUNK_SIZE,
    temp_folder: str = "./temp_upload_files/"
) -> List[str]:
    """Split a file into chunks and stores them in a temporary folder.

    Parameters
    ----------
    file_path : str
        The full path to the file to split into chunks.
    chunk_size: int
        The size per chunk. Defaults to 24000000.
    temp_folder : str
        The path to the temporary folder to store the chunks in.

    Returns
    -------
    list of str
    """

    filename = os.path.basename(file_path)
    chunk_files = []

    # create folder to store temporary files
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    # get file size
    async with aiofiles.open(file_path, "rb") as file:

        # index to keep track of chunks
        index = 0

        # read file by chunks of chunk size
        while (chunk := await file.read(chunk_size)):

            # create a temporary file object for each chunk
            full_file_path = f"{temp_folder}/{filename}.{index}"

            # write the chunk to the temporary file
            async with aiofiles.open(full_file_path, "wb") as temp_file:
                await temp_file.write(chunk)

            # add the temporary file path to the list of chunk files
            chunk_files.append(full_file_path)

            # increment the index
            index += 1

        return chunk_files


async def download_chunk(
    session: aiohttp.ClientSession,
    url: str,
    index: int,
    output_file: str,
    progress_bar: tqdm,
    temp_folder: str = "./temp_download_files/"
):
    """Download a chunk from a url.

    Parameters
    ----------
    session : aiohttp.ClientSession
        The aiohttp client session to use for the download.
    url : str
        The url to download the chunk from.
    index : int
        The index of the chunk.
    output_file : str
        The path to the file to save the chunk to.
    progress_bar : tqdm
        The progress bar to update with the download progress.
    temp_folder : str
        The path to the temporary folder to store the chunks in.
    """
    # download the chunk
    async with session.get(url) as response:

        # raise an exception if the status code is not 200
        response.raise_for_status()

        # create folder to store temporary files
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        # save the chunk to a temporary output file
        temp_file_path = f"{temp_folder}/" + \
            f"{output_file}.{index}"
        async with aiofiles.open(temp_file_path, 'ab') as f:

            # read the chunk
            chunk = await response.read()

            # get length of chunk
            chunk_length = len(chunk)

            # write the chunk to the file
            await f.write(chunk)

            # update the progress bar
            progress_bar.update(chunk_length)


async def merge_chunks(
    chunk_urls: [],
    total_size: int,
    output_path: str,
    temp_folder: str = "./temp_download_files/"
):
    """Merge chunks into a single file.

    Parameters
    ----------
    chunk_urls : list
        The list of urls to download the chunks from.
    total_size : int
        The total size of the file to download.
    output_path : str
        The path to the file to save the merged chunks to.
    temp_folder : str
        The path to the temporary folder to store the chunks in.
    """

    output_file = os.path.basename(output_path)

    async with aiohttp.ClientSession() as session:

        # use asyncio.gather to download chunks concurrently
        tasks = []

        # create a tqdm progress bar
        with tqdm(
            total=total_size, unit='B', unit_scale=True, desc='Downloading'
        ) as progress_bar:
            # create tasks for each download_chunk coroutine
            tasks = [
                asyncio.create_task(
                    download_chunk(
                        session, url, index, output_file, progress_bar,
                        temp_folder=temp_folder
                    )
                ) for index, url in enumerate(chunk_urls)
            ]

            # wait for all tasks to complete
            await asyncio.gather(*tasks)

        # merge the temporary files
        async with aiofiles.open(output_path, 'wb') as merged_file:

            # iterate through the temporary files
            for index in range(len(chunk_urls)):
                temp_file_path = f"./temp_download_files/{output_file}.{index}"

                # append the temporary file to the merged file
                async with aiofiles.open(temp_file_path, 'rb') as temp_file:

                    # read the temporary file and append to the merged file
                    await merged_file.write(await temp_file.read())

                # remove the temporary file
                os.remove(temp_file_path)
