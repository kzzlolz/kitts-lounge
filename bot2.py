import os
import discord
from flask import Flask, jsonify
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

app = Flask('')

@app.route('/api/guild-data')
def guild_data():
    guild = bot.get_guild(int(GUILD_ID)) if GUILD_ID else None
    if not guild:
        return jsonify({"error": "Guild not found"}), 404
    
    members_data = []
    for member in guild.members:
        roles = [str(role.id) for role in member.roles]
        avatar_url = member.display_avatar.url if hasattr(member, 'display_avatar') else member.default_avatar.url
        members_data.append({
            "id": str(member.id),
            "username": member.name,
            "display_name": member.display_name,
            "avatar_url": str(avatar_url),
            "status": str(member.status),
            "bot": member.bot,
            "roles": roles
        })
        
    return jsonify({
        "total_members": guild.member_count,
        "members": members_data
    })

def run():
    app.run(host='0.0.0.0', port=8080)

intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = discord.Client(intents=intents)

GUILD_ID = os.getenv("GUILD_ID")
TOKEN = os.getenv("DISCORD_TOKEN")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

server_thread = Thread(target=run)
server_thread.start()

bot.run(TOKEN)
