import discord
import os
import requests
import json
import feedparser
import time
from discord.ext import tasks
from replit import db
from keep_alive import keep_alive

client = discord.Client()

# List of banned words and corresponding responses
sad_words = ['amirkhan', 'sanzhar', 'dias', 'zhanibek', '', 'O m e g a ', 'o m e g a', 'OOOOOMEGA', 'OmEgA']
starter_encouragements = ["Сосать писю не харам", "Zhanibek lox", "Sanzhar lox", "шампунь жумайсынба", "Erik lox"]

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote

def update_encouragements(encouraging_message):
    encouragements = db.get('encouragements', [])
    encouragements.append(encouraging_message)
    db['encouragements'] = encouragements

def delete_encouragement(index):
    encouragements = db.get('encouragements', [])
    if len(encouragements) > index:
        del encouragements[index]
        db['encouragements'] = encouragements

def get_top_posts(subreddit, limit=5):
    url = f"https://www.reddit.com/r/{subreddit}/top.rss"
    feed = feedparser.parse(url)
    return feed.entries[:limit]

last_fetch_time = 0
cached_posts = []

@tasks.loop(hours=5)  # adjust to set the interval between posts
async def post_reddit_content():
    global cached_posts
    if cached_posts:  # if there are any cached posts left
        post = cached_posts.pop(0)  # get and remove the first post
        channel = client.get_channel(907575858150129696)  # Replace with your channel ID
        await channel.send(f"{post.title}\n{post.link}")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

    global last_fetch_time, cached_posts
    current_time = time.time()

    # Only fetch posts if it's been more than a day since the last fetch
    if current_time - last_fetch_time > 86400:  # 86400 seconds = 1 day
        # Get the top 5 posts from r/shitposting
        cached_posts = get_top_posts("shitposting")
        last_fetch_time = current_time

    # Start the background task
    post_reddit_content.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if any(word in msg for word in sad_words):
        await message.channel.send(random.choice(starter_encouragements))
    
    if msg.startswith('$omega-inspire'):
        quote = get_quote()
        await message.channel.send(quote)
    
    if msg.startswith("$help"):
        await message.channel.send("Here are the all list commands for now: \n - omega-inspire \n - Amirkhan \n - Zhanibek \n - sanzhar")

@client.event
async def on_message_edit(before, after):
    await before.channel.send(
        f'{before.author} edited a message.\n'
        f'Before: {before.content}\n'
        f'After: {after.content}'
    )

@client.event
async def on_message_delete(message):
    msg = f'{message.author} deleted message in {message.channel}: {message.content}'
    print(msg)
    await message.channel.send(msg)

# Don't forget to stop the task if the bot logs out
@client.event
async def on_disconnect():
    post_reddit_content.cancel()

# Running the keep_alive.py so my bot will be 24/7
keep_alive()
my_secret = os.environ['TOKEN']
client.run(my_secret)
