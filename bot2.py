import os
import threading
from dotenv import load_dotenv
import discord
from flask import Flask, jsonify

load_dotenv('/etc/secrets/.env')

app = Flask(__name__)

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.presences = True  # Required to read online/offline member statuses

client = discord.Client(intents=intents)

guild_data = {
    "total_members": 0,
    "members": []
}

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    if GUILD_ID:
        guild = client.get_guild(int(GUILD_ID))
        if guild:
            guild_data["total_members"] = guild.member_count
            members_list = []
            
            for member in guild.members:
                members_list.append({
                    "username": member.name,
                    "display_name": member.display_name,
                    "avatar_url": str(member.display_avatar.url),
                    "status": str(member.status),
                    "bot": member.bot,
                    "roles": [str(role.id) for role in member.roles]
                })
            
            guild_data["members"] = members_list

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
