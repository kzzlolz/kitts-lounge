import os
import threading
import discord
from flask import Flask, render_template_string

app = Flask(__name__)

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

server_stats = {
    "member_count": 0
}

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    if GUILD_ID:
        guild = client.get_guild(int(GUILD_ID))
        if guild:
            server_stats["member_count"] = guild.member_count

@app.route("/")
def home():
    return f"Kitt's Lounge | Online members: {server_stats['member_count']}"

def run_discord():
    client.run(TOKEN)

if __name__ == "__main__":
    discord_thread = threading.Thread(target=run_discord)
    discord_thread.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
