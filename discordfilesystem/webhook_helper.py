"""Webhook helper functions."""
from typing import List
import aiohttp
import discord
from discord import Webhook
import asyncio


async def upload_files(
    session: aiohttp.ClientSession,
    files: List[discord.File],
    webhook_urls: List[str]
) -> List[discord.Attachment]:
    """Upload files to channel using webhooks.

    Parameters
    ----------
    session : `aiohttp.ClientSession`
        The aiohttp session to use.
    files : list of `discord.File`
        The files to upload.
    webhook_urls : list of str
        The webhook urls to use.

    Returns
    -------
    List of `discord.Attachment`
    """
    # checks if files are empty
    if not files:
        return []

    # create a partial webhook for each webhook url
    webhooks = [
        Webhook.from_url(url, session=session) for url in webhook_urls
    ]

    # list of webhook messages
    webhook_messages = []

    # create a coroutine for sending each file
    async def send_file(file, webhook):
        return await webhook.send(file=file, wait=True)

    # gather all the coroutines and send files concurrently
    tasks = []
    for file in files:

        # get the webhook to use
        webhook = webhooks[len(tasks) % len(webhooks)]

        # create a task for sending the file
        tasks.append(send_file(file, webhook))

    # wait for all tasks to complete
    webhook_messages = await asyncio.gather(*tasks)

    # return the list of attachments
    return [
        message.attachments[0] for message in webhook_messages
    ]


# if __name__ == "__main__":

#     # testing upload_files function
#     result = asyncio.run(
#         upload_files(
#             [discord.File("8912.0"), discord.File("8912.0"), discord.File("8912.0"), discord.File("8912.0")],
#             "https://discord.com/api/webhooks/1179721340689842236/ZBJk8ZokbSuAMPYDB3clIZuYa7gnw95wsRgEOi5ZqwdVqupmt4N1I-1eovLAR8kFzr02"
#         )
#     )
#     print(result)
