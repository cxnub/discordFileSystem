# DiscordFileSystem

Discord File System is a proof of concept that demonstrates the use of Discord as a cloud file storage solution using Python.

## Overview

This project explores the feasibility of leveraging Discord for storing and retrieving files. By integrating Python with the Discord API, I aim to provide a basic cloud file storage system.

## How it Works
- Large files (>24MB) are split into 24MB chunks and uploaded to a Discord channel via webhooks.
- The program records attachment URLs for each file's chunks.
- Upon retrieval, the program downloads chunks from the stored URLs and merges them into the original file.

## Features

- **File Upload:** Upload files to Discord servers for storage.
- **File Download:** Retrieve files from Discord servers using Python.
- **Settings:** Modify various config settings. [See more here](#settings-list)
- **Asynchronous Uploading/Downloading:** Uploading and downloading files are made asynchronously and run concurrently.
- **Filename Indexing:** Implement a mechanism to handle filename collisions and maintain uniqueness.
- **Proof of Concept:** Explore the potential of Discord as a cloud storage solution.

## Upcoming Features
- **Encryption:** Optional encryption for files uploaded to discord.
- **Graphical User Interface:** A user-friendly GUI for easier usage.
- **Folders:** Folders to organise files.
- **More Customability:** Ability to change number of chunks to upload concurrently (default: 5), ability to change chunk size (default: 24MB)

## Limitations
- Discord attachment URLs now expire in 2 months and would require a user to regenerate a new URL.
- Max chunk size of 24MB due to Discord's  attachment upload limit.

## Prerequisites

- Python 3.12.0
- Discord's Webhook URL(s)

## Getting Started

1. **Set up a Discord Webhook:**
   - Create a few webhook urls. For better performance create 5 webhooks, with 1 webhook per text channel.
   - [How to create a Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).
   - Note down the webhook urls.

2. **Clone the Project:**
   - Clone this repository.

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt

4. **Run the project:**
   ```bash
   python cli.py

## Commands List
| Command                      | Description                                         |
|------------------------------|-----------------------------------------------------|
| 1. Show files                | Show all files.                                     |
| 2. Upload file               | Upload a file to Discord's server.                  |
| 3. Download file             | Download a file using the file id.                  |
| 4. Help                      | Shows the help message.                             |
| 5. Quit                      | Quit the program.                                   |

## Settings List
| Command                      | Description                                         |
|------------------------------|-----------------------------------------------------|
| 1. Import files cache        | Import files cache.                                 |
| 2. Export files cache        | Export files cache for sharing.                     |
| 3. Add webhooks              | Add webhooks to the config file.                    |
| 4. Change download directory | Change the directory where files are downloaded to. |
| 5. Back                      | Return to main page.                                |

