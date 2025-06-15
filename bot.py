import os
import json
from dotenv import load_dotenv
import discord
from discord.ext import commands

# Load token from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "ads_data.json"

# Ensure data file exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

@bot.command()
async def ads(ctx, number: int):
    """Report the number of ads you've sent."""
    username = str(ctx.author)

    # Load existing data
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # Update user's ad count
    data[username] = data.get(username, 0) + number

    # Save updated data
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

    await ctx.send(f"{username} reported {number} ads. Total: {data[username]}")

@bot.command()
async def leaderboard(ctx):
    """Show leaderboard of users who sent the most ads."""
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        await ctx.send("No ad data available yet.")
        return

    if not data:
        await ctx.send("No ads have been reported yet.")
        return

    # Sort data by total ads sent
    sorted_data = sorted(data.items(), key=lambda item: item[1], reverse=True)

    leaderboard_text = "**📊 Ads Leaderboard:**\n"
    for i, (user, count) in enumerate(sorted_data[:10], start=1):
        leaderboard_text += f"{i}. {user}: {count} ads\n"

    await ctx.send(leaderboard_text)

# Run the bot
bot.run(TOKEN)
