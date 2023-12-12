# Craigslist Discord Bot

This Discord bot scrapes Craigslist for free items and wanted posts, looking for matches based on title similarity. It then sends the results to a specified Discord channel.

## Configuration

1. Replace `YOUR_BOT_TOKEN_PLACEHOLDER` with your actual Discord bot token.
2. Replace `YOUR_CHANNEL_ID_PLACEHOLDER` with the ID of the Discord channel where you want to send the results.
3. Replace `YOUR_FREE_SECTION_URL_PLACEHOLDER` and `YOUR_WANTED_SECTION_URL_PLACEHOLDER` with the URLs of the Craigslist sections you want to scrape for free items and wanted posts, respectively.

## How to Run

1. Install the required Python packages:

   ```bash
   pip install requests beautifulsoup4 pandas discord.py
   python freebot.py
