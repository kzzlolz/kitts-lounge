import os
import threading
from dotenv import load_dotenv
import discord
from flask import Flask, jsonify
from flask_cors import CORS

load_dotenv("/etc/secrets/.env")

app = Flask(__name__)
CORS(app)

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.guilds = True

client = discord.Client(intents=intents)

guild_data = {
    "total_members": 0,
    "online_members": 0,
    "members": []
}

data_lock = threading.Lock()


def get_guild():
    if GUILD_ID:
        return client.get_guild(int(GUILD_ID))
    return client.guilds[0] if client.guilds else None


def refresh_member_data(guild):
    members = list(guild.members)
    member_list = []

    online_count = sum(
        1 for member in members
        if not member.bot and member.status != discord.Status.offline
    )

    for member in members:
        if member.bot:
            continue

        member_list.append({
            "id": str(member.id),
            "username": member.name,
            "display_name": member.display_name,
            "avatar_url": str(member.display_avatar.url),
            "status": str(member.status),
            "bot": False,
            "roles": [
                str(role.id)
                for role in member.roles
                if role != guild.default_role
            ]
        })

    with data_lock:
        guild_data["total_members"] = guild.member_count or len(members)
        guild_data["online_members"] = online_count
        guild_data["members"] = member_list


async def update_guild_data():
    guild = get_guild()

    if guild is None:
        print("ERROR: Could not find the configured Discord server.")
        return

    try:
        await guild.chunk(cache=True)
        refresh_member_data(guild)
        print(
            f"Loaded {len(guild_data['members'])} human members "
            f"from {guild.name}"
        )
    except Exception as error:
        print(f"Failed to update members: {error}")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await update_guild_data()


@client.event
async def on_member_join(member):
    guild = get_guild()
    if guild and member.guild.id == guild.id:
        refresh_member_data(guild)


@client.event
async def on_member_remove(member):
    guild = get_guild()
    if guild and member.guild.id == guild.id:
        refresh_member_data(guild)


@client.event
async def on_member_update(before, after):
    guild = get_guild()
    if guild and after.guild.id == guild.id:
        refresh_member_data(guild)


@client.event
async def on_presence_update(before, after):
    guild = get_guild()
    if guild and after.guild.id == guild.id:
        refresh_member_data(guild)


@app.route("/")
def home():
    return "Kitt's Lounge is active!"


@app.route("/api/guild-data")
def get_guild_data():
    with data_lock:
        return jsonify({
            "total_members": guild_data["total_members"],
            "online_members": guild_data["online_members"],
            "members": guild_data["members"]
        })


def run_discord():
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN is missing.")

    client.run(TOKEN)


if __name__ == "__main__":
    discord_thread = threading.Thread(
        target=run_discord,
        daemon=True
    )
    discord_thread.start()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        use_reloader=False
    )
