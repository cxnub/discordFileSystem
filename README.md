# DiscordFileSystem

DiscordFileSystem is a proof of concept that demonstrates the use of Discord as a cloud file storage solution using Python.

## Overview

This project explores the feasibility of leveraging Discord for storing and retrieving files. By integrating Python with the Discord API, I aim to provide a basic cloud file storage system.

## Features

- **File Upload:** Upload files to Discord servers for storage.
- **File Download:** Retrieve files from Discord servers using Python.
- **Asynchronous Uploading/Downloading:** Uploading and downloading files are made asynchronously and run concurrently.
- **Filename Indexing:** Implement a mechanism to handle filename collisions and maintain uniqueness.
- **Proof of Concept:** Explore the potential of Discord as a cloud storage solution.

## Upcoming Features
- **Encryption:** Optional encryption for files uploaded to discord.
- **Graphical User Interface:** A user-friendly GUI for easier usage.
- **Folders:** Folders to organise files.
- **Export/Import of files cache:** Enables sharing of files just by importing files cache.

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

   
