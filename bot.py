import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from collections import defaultdict

# Load token and prefix from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"

intents = discord.Intents.default()
intents.message_content = True  # Required for reading messages

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Store ads per user (in-memory)
user_ads = defaultdict(int)

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

@bot.command(name='ads')
async def report_ads(ctx, number: int):
    if number < 0:
        await ctx.send("You can't report a negative number of ads.")
        return
    user_id = ctx.author.id
    user_ads[user_id] += number
    await ctx.send(f"{ctx.author.display_name} reported {number} ads. Total: {user_ads[user_id]}")

@bot.command(name='leaderboard')
async def leaderboard(ctx):
    if not user_ads:
        await ctx.send("No ads have been reported yet.")
        return

    # Sort users by most ads
    sorted_ads = sorted(user_ads.items(), key=lambda x: x[1], reverse=True)
    message = "**Ad Reporting Leaderboard**\n"
    for i, (user_id, total) in enumerate(sorted_ads[:10], start=1):
        user = await bot.fetch_user(user_id)
        message += f"{i}. {user.display_name} – {total} ads\n"
    await ctx.send(message)

@bot.command(name='resetads')
@commands.has_permissions(administrator=True)
async def reset_ads(ctx):
    user_ads.clear()
    await ctx.send("All ad reports have been reset.")

bot.run(TOKEN)
