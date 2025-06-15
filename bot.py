import discord
from discord.ext import commands
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Simple in-memory storage
ads_data = {}
guides = {}

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

@bot.command()
async def ads(ctx, amount: int):
    user = ctx.author.name
    ads_data[user] = ads_data.get(user, 0) + amount
    await ctx.send(f"{user} reported {amount} ads. Total: {ads_data[user]}")

@bot.command()
async def ads_leaderboard(ctx):
    leaderboard = sorted(ads_data.items(), key=lambda x: x[1], reverse=True)
    msg = "**📊 Ads Leaderboard:**\n"
    for i, (user, total) in enumerate(leaderboard, start=1):
        msg += f"{i}. {user}: {total}\n"
    await ctx.send(msg)

@bot.command()
@commands.has_permissions(administrator=True)
async def announce(ctx, channel: discord.TextChannel, *, message):
    await channel.send(f"📢 **Announcement:** {message}")
    await ctx.send("✅ Announcement sent.")

@bot.command()
@commands.has_permissions(administrator=True)
async def guide_add(ctx, title, *, content):
    guides[title.lower()] = content
    await ctx.send(f"✅ Guide '{title}' added.")

@bot.command()
async def guide(ctx, title):
    guide = guides.get(title.lower())
    if guide:
        await ctx.send(f"📘 **{title}**\n{guide}")
    else:
        await ctx.send("❌ Guide not found.")

@bot.command()
async def guide_list(ctx):
    if not guides:
        await ctx.send("No guides added yet.")
    else:
        await ctx.send("📘 Guides:\n" + "\n".join(guides.keys()))

bot.run(os.getenv("DISCORD_TOKEN"))