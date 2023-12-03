# DiscordFileSystem

DiscordFileSystem is a proof of concept that demonstrates the use of Discord as a cloud file storage solution using Python.

## Overview

This project explores the feasibility of leveraging Discord, a popular communication platform, for storing and retrieving files. By integrating Python with the Discord API, we aim to provide a rudimentary cloud file storage system.

## Features

- **File Upload:** Upload files to Discord servers for storage.
- **File Download:** Retrieve files from Discord servers using Python.
- **Filename Indexing:** Implement a mechanism to handle filename collisions and maintain uniqueness.
- **Proof of Concept:** Explore the potential of Discord as a cloud storage solution.

## Prerequisites

- Python 3.12.0
- Discord's Webhook URL(s)

## Getting Started

1. **Set up a Discord Webhook:**
   - Create a few webhook urls. For better performance create 5 webhooks, with 1 webhook per text channel.
   - [How to create a Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).
   - Note down the webhook urls.

2. **Configure the Project:**
   - Clone this repository.
   - Update config.json, it should look like this:
     ```json
     {"webhooks": ["YOUR_WEBHOOK_URL"]}

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt

4. **Run the project:**
   ```bash
   python cli.py

   
