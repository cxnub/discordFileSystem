"""Webhook helper functions."""
from typing import List
import aiohttp
import discord
from discord import Webhook


async def upload_files(
    files: List[discord.File], webhook_url: str
) -> List[discord.Attachment]:
    """Upload files to channel using webhooks.

    Parameters
    ----------
    files : list of `discord.File`
        The files to upload.
    webhook_url : str
        The webhook URL.

    Returns
    -------
    List of `discord.Attachment`
    """
    # checks if files are empty
    if not files:
        return []

    # start a aiohttp client session
    async with aiohttp.ClientSession() as session:

        # create a partial webhook from its URL
        webhook = Webhook.from_url(webhook_url, session=session)

        # send the files
        webhook_message = await webhook.send(
            files=files,
            username="fs",
            wait=True
        )

        # close the session
        await session.close()

        # return the list of attachments
        return webhook_message.attachments


# if __name__ == "__main__":

#     # testing upload_files function
#     result = asyncio.run(
#         upload_files(
#             [discord.File("8912.0"), discord.File("8912.0"), discord.File("8912.0"), discord.File("8912.0")],
#             "https://discord.com/api/webhooks/1179721340689842236/ZBJk8ZokbSuAMPYDB3clIZuYa7gnw95wsRgEOi5ZqwdVqupmt4N1I-1eovLAR8kFzr02"
#         )
#     )
#     print(result)
