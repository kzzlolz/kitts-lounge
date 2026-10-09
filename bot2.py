import os
import threading
from dotenv import load_dotenv
import discord
from flask import Flask, jsonify
from flask_cors import CORS

load_dotenv('/etc/secrets/.env')

app = Flask(__name__)
CORS(app)

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.presences = True

client = discord.Client(intents=intents)

guild_data = {
    "total_members": 0,
    "members": []
}

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    guild = None
    if GUILD_ID:
        guild = client.get_guild(int(GUILD_ID))
    if not guild and client.guilds:
        guild = client.guilds[0]

    if guild:
        guild_data["total_members"] = guild.member_count
        members_list = []
        async for member in guild.fetch_members(limit=None):
            members_list.append({
                "username": member.name,
                "display_name": member.display_name,
                "avatar_url": str(member.display_avatar.url),
                "status": str(member.status),
                "bot": member.bot,
                "roles": [str(role.id) for role in member.roles]
            })
        guild_data["members"] = members_list
        print(f"Successfully loaded {len(members_list)} members for {guild.name}")
    else:
        print("ERROR: Bot is not in any servers or GUILD_ID is invalid!")

@app.route("/")
def home():
    return "Kitt's Lounge is active!"

@app.route("/api/guild-data")
def get_guild_data():
    return jsonify(guild_data)

def run_discord():
    client.run(TOKEN)

if __name__ == "__main__":
    discord_thread = threading.Thread(target=run_discord)
    discord_thread.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
