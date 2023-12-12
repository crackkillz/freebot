import requests
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import csv
import discord
from discord.ext import commands
import pandas as pd
from datetime import datetime
import asyncio

# Define your Discord bot token (replace with your actual token)
bot_token = "YOUR_BOT_TOKEN_PLACEHOLDER"

# Create a Discord bot instance with intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# Define placeholders for sensitive information
CHANNEL_ID_PLACEHOLDER = "YOUR_CHANNEL_ID_PLACEHOLDER"
FREE_SECTION_URL_PLACEHOLDER = "YOUR_FREE_SECTION_URL_PLACEHOLDER"
WANTED_SECTION_URL_PLACEHOLDER = "YOUR_WANTED_SECTION_URL_PLACEHOLDER"

def retrieve_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad responses

        print(f"Successfully retrieved Craigslist page: {url}")
        return BeautifulSoup(response.content, "html.parser")

    except requests.RequestException as e:
        print(f"Failed to retrieve Craigslist page. Error: {e}")
        return None

def scrape_craigslist_section(base_url, section_name):
    url = f"{base_url}?s=0"
    soup = retrieve_page(url)

    if soup is not None:
        posts = []
        for post in soup.select('li.cl-static-search-result'):
            title = post.find("div", class_="title").text.strip()
            link_element = post.find("a")
            link = link_element['href'] if link_element and 'href' in link_element.attrs else None
            posts.append((title, link, section_name))

        print(f"Scraped Craigslist {section_name} Section")
        print(f"{section_name} Posts:", posts)

        return posts
    else:
        return []

def find_matches_with_links(free_items, wanted_posts):
    matches = []

    for free_title, free_link, free_section in free_items:
        for wanted_title, wanted_link, wanted_section in wanted_posts:
            similarity = SequenceMatcher(None, free_title.lower(), wanted_title.lower()).ratio()
            if similarity > 0.8:
                matches.append((free_title, free_link, wanted_title, wanted_link, free_section, wanted_section))
                print(f"Match found (Similarity: {similarity}):")
                print(f"Free Item: {free_title}\nFree Item Link: {free_link or 'N/A'}")
                print(f"Wanted Post: {wanted_title}\nWanted Post Link: {wanted_link or 'N/A'}\n")

    return matches

async def send_results_to_discord(channel_id, free_items, wanted_posts, num_pages_to_scrape):
    all_match_urls = find_matches_with_links(free_items, wanted_posts)

    # Log matches to CSV only if there are matches
    if all_match_urls:
        with open("matches.csv", mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Free Title', 'Free Link', 'Wanted Title', 'Wanted Link', 'Free Section', 'Wanted Section'])
            writer.writerows(all_match_urls)
        print("Matches Logged to CSV")

    # Read in the CSV
    df = pd.read_csv('matches.csv')

    # Send a summary message
    summary_message = (
        f"**Matches Found ({len(df.index)}):**\n"
        f"Number of Free Items: {len(free_items)}\n"
        f"Number of Wanted Posts: {len(wanted_posts)}\n"
        f"Number of Pages Scraped: {num_pages_to_scrape}"
    )

    # Send the summary message to the Discord channel
    channel = bot.get_channel(channel_id)
    await channel.send(summary_message)

    # Send each match as a separate message
    for _, row in df.iterrows():
        match_message = (
            f"**Match Found!**\n"
            f"Free Item: [{row['Free Title']}]({row['Free Link']})\n"
            f"Wanted Post: [{row['Wanted Title']}]({row['Wanted Link']})"
        )
        await channel.send(match_message)

    # Log the time the results were sent to Discord
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Results Sent to Discord at:", current_time)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

    # Set the Discord channel ID
    channel_id = CHANNEL_ID_PLACEHOLDER

    # Scrape Craigslist sections
    free_items = scrape_craigslist_section(FREE_SECTION_URL_PLACEHOLDER, "Free")
    wanted_posts = scrape_craigslist_section(WANTED_SECTION_URL_PLACEHOLDER, "Wanted")

    if free_items and wanted_posts:
        try:
            await send_results_to_discord(channel_id, free_items, wanted_posts, num_pages_to_scrape=3)
        except Exception as e:
            print(f"Error during Discord message sending: {e}")

# Run the Discord bot using asyncio
async def main():
    await bot.start(bot_token)

if __name__ == '__main__':
    asyncio.run(main())
