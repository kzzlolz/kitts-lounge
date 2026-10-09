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

client = discord.Client(intents=intents)

guild_data = {
    "member_count": 0,
    "owners": [],
    "admins": [],
    "mods": [],
    "bots": [],
    "online_members": []
}

@client.event
async def on_ready():
    if GUILD_ID:
        guild = client.get_guild(int(GUILD_ID))
        if guild:
            guild_data["member_count"] = guild.member_count
            
            owners = []
            admins = []
            mods = []
            bots = []
            online = []
            
            for member in guild.members:
                if member.bot:
                    bots.append(member.name)
                elif member.status != discord.Status.offline:
                    online.append(member.name)
                
                for role in member.roles:
                    role_name = role.name.lower()
                    if "owner" in role_name:
                        owners.append(member.name)
                    elif "admin" in role_name:
                        admins.append(member.name)
                    elif "mod" in role_name:
                        mods.append(member.name)
            
            guild_data["owners"] = list(set(owners))
            guild_data["admins"] = list(set(admins))
            guild_data["mods"] = list(set(mods))
            guild_data["bots"] = list(set(bots))
            guild_data["online_members"] = list(set(online))

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
