import discord
import datetime
from collections import defaultdict, deque
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


# --- CONFIGURATION ---
TRUSTED_STAFF = {807758543829598230}  # Add officer/admin IDs you trust
MOD_LOG_CHANNEL_ID = 123456789012345678  # Replace with your log channel ID


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


# --- BAN TRACKER ---
ban_tracker = defaultdict(lambda: deque(maxlen=3))

@bot.event
async def on_member_ban(guild, user):
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        if entry.target.id != user.id:
            continue

        banner = entry.user
        now = datetime.datetime.utcnow()

        if banner.id in TRUSTED_STAFF:
            return  # Skip trusted staff

        ban_tracker[banner.id].append(now)

        if len(ban_tracker[banner.id]) == 3:
            first_ban_time = ban_tracker[banner.id][0]
            if (now - first_ban_time) <= datetime.timedelta(hours=24):
                try:
                    await guild.ban(banner, reason="Anti-nuke: Banned 3 users in under 24 hours.")
                    print(f"[ANTI-NUKE] {banner} auto-banned for mass banning users.")

                    try:
                        await banner.send("You were banned for banning 3 users in less than 24 hours.")
                    except discord.Forbidden:
                        pass

                    mod_log = guild.get_channel(MOD_LOG_CHANNEL_ID)
                    if mod_log:
                        await mod_log.send(
                            f"🚨 **Anti-Nuke Triggered**\n"
                            f"👤 `{banner}` (`{banner.id}`) was auto-banned for banning 3 users within 24 hours."
                        )

                    del ban_tracker[banner.id]
                except Exception as e:
                    print(f"Failed to ban {banner}: {e}")
        break


bot.run(TOKEN)
