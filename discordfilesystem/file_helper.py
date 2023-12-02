"""Helper functions to manage files."""
from typing import List
import os
import asyncio
import aiohttp
import aiofiles
from tqdm import tqdm


CHUNK_SIZE = 24_000_000


def split_file(
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

    with open(file_path, "rb") as file:

        # index to keep track of chunks
        index = 0

        # read file by chunks of chunk size
        while (chunk := file.read(chunk_size)):

            # create folder to store temporary files
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)

            # create a temporary file object for each chunk
            full_file_path = f"{temp_folder}/{filename}.{index}"
            with open(full_file_path, "wb") as temp_file:
                temp_file.write(chunk)

            # add the temporary file path to the list of chunk files
            chunk_files.append(full_file_path)

            # increment the index
            index += 1

        file.close()

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
    try:
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

    # catch any exceptions
    except Exception as e:
        print(f"Failed to download chunk from {url}: {e}")


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
        with open(output_path, 'wb') as merged_file:

            # iterate through the temporary files
            for index in range(len(chunk_urls)):
                temp_file_path = f"./temp_download_files/{output_file}.{index}"

                # append the temporary file to the merged file
                with open(temp_file_path, 'rb') as temp_file:

                    # read the temporary file and append to the merged file
                    merged_file.write(temp_file.read())

                # remove the temporary file
                os.remove(temp_file_path)


# if __name__ == "__main__":

#     import time
#     start_time = time.time()
#     # split_file("valorant.mp4", "valorant")

#     asyncio.run(merge_chunks([
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070350084649010/292.0?ex=657c1528&is=6569a028&hm=2b93d19c5121e7163976a7e13314c7bafdab7b02b1f9c85f7d78b59ce54d42de&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070392233213962/292.1?ex=657c1532&is=6569a032&hm=8032c0c81bd0f44c5373709c20af4f8a5de3e67420e2d2cc76573e6753136b91&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070433668726825/292.2?ex=657c153c&is=6569a03c&hm=9438ff88f4e529cab1f50a4a0f2e3760e8097a32a824708dfcb0535d7f61aa31&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070478702981150/292.3?ex=657c1546&is=6569a046&hm=ecfc4d96611bafed5fac9416f4d40a4b9ccae4c25fca57ca431b9c33168599d7&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070520750866432/292.4?ex=657c1550&is=6569a050&hm=52d1cde83533e031170cd7b6e8071eb4d2e418179f251f3559321b9dbdb7c7a7&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070561955713044/292.5?ex=657c155a&is=6569a05a&hm=4cfd5b097c89f99a4e87b7bfa3f4ed4e4f1708b8d1928551dafef8d4f027b293&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070600962752512/292.6?ex=657c1563&is=6569a063&hm=c18059e77c7d59ab498a6b15479146a3aea49976bd33565eef9ed55b1c99f649&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070641978847262/292.7?ex=657c156d&is=6569a06d&hm=ffdbf86e1d01903c5e48890b24909503a7f19ffa112275ec2c75189be2972fc1&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070683930267709/292.8?ex=657c1577&is=6569a077&hm=9bd4558fb88eb47c4cb4f517491fb6fee077f56f4da0dbb2d2002ff9e446a669&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070725965590629/292.9?ex=657c1581&is=6569a081&hm=407c71a3b3d185de8d2f6e2f8814c9d332c667793c5cf6034a9aad2a5166bb57&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070762607038534/292.10?ex=657c158a&is=6569a08a&hm=db1a6b46d2b76b6fba2bb626db87a8bee681aae65021450232b24fc964cbacb7&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070805367955597/292.11?ex=657c1594&is=6569a094&hm=78f841b60c94438a0c47038bd911838e42686c0712cc69881cf57b79282df4a0&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070867032616970/292.12?ex=657c15a3&is=6569a0a3&hm=48d9baf491f915108a074b71b254aba7a7fb692f59c4d111a8d351416c15eec1&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070905074958446/292.13?ex=657c15ac&is=6569a0ac&hm=08ff0f89832f1a68b7192a7b0fb027609965b5521bfd0a721ad6f471dbb6d690&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070942098083890/292.14?ex=657c15b5&is=6569a0b5&hm=55018869d69d677acb640fc0c1e9c18650076dbb196db747bf78cdd5d04c807e&",
#         "https://cdn.discordapp.com/attachments/1179721213124296727/1180070965644890213/292.15?ex=657c15ba&is=6569a0ba&hm=8e84c428db70f6efe2a1880eadc6dd21d0984f71fcd73af23f9d3496402551d1&",
#     ], 364889000, "valorant.mp4"))

#     print("--- %s seconds ---" % (time.time() - start_time))
