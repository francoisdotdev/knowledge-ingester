import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import requests
import re

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")
DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.tree.command(name="add", description="Adds a new article/blog post to the knowledge base")
async def add_slash(interaction: discord.Interaction, url: str):
    """Adds a new article/blog post to the knowledge base."""
    if not re.match(r"https?://", url):
        await interaction.response.send_message("Please provide a valid URL (starting with http:// or https://)")
        return

    await interaction.response.defer()
    
    try:
        response = requests.post(f"{BACKEND_URL}/ingest/", json={"url": url, "source": "discord", "resource_type": "article"})
        response.raise_for_status()
        link = response.json()
        await interaction.followup.send(f"✅ Article saved!\nTitle: {link.get('title', 'N/A')}\nURL: {link['url']}")
    except requests.RequestException as e:
        await interaction.followup.send(f"❌ Error saving link: {str(e)[:100]}")

@bot.tree.command(name="tool", description="Adds a tool/resource to the knowledge base")
async def tool_slash(interaction: discord.Interaction, url: str, description: str = None):
    """Adds a tool (software, repo, resource, etc.) to the knowledge base."""
    if not re.match(r"https?://", url):
        await interaction.response.send_message("Please provide a valid URL (starting with http:// or https://)")
        return

    await interaction.response.defer()
    
    try:
        payload = {
            "url": url, 
            "source": "discord", 
            "resource_type": "resource"
        }
        if description:
            payload["description"] = description
            
        response = requests.post(f"{BACKEND_URL}/ingest/", json=payload)
        response.raise_for_status()
        link = response.json()
        await interaction.followup.send(f"✅ Tool saved!\nTitle: {link.get('title', 'N/A')}\nURL: {link['url']}")
    except requests.RequestException as e:
        await interaction.followup.send(f"❌ Error saving tool: {str(e)[:100]}")

@bot.tree.command(name="list", description="Lists the last 10 links from the knowledge base")
async def list_slash(interaction: discord.Interaction):
    """Lists the last 10 links from the knowledge base."""
    await interaction.response.defer()
    
    try:
        response = requests.get(f"{BACKEND_URL}/links/?limit=10")
        response.raise_for_status()
        links = response.json()
        if not links:
            await interaction.followup.send("No links found.")
            return

        embed = discord.Embed(title="Latest Links", color=discord.Color.blue())
        for link in links:
            embed.add_field(name=link.get('title', 'No Title'), value=link['url'], inline=False)
        await interaction.followup.send(embed=embed)
    except requests.RequestException as e:
        await interaction.followup.send(f"❌ Error fetching links: {str(e)[:100]}")

@bot.tree.command(name="rf", description="Force push a link to the database")
async def rf_slash(interaction: discord.Interaction, url: str, title: str = None):
    """Force push a link to the database (bypass errors). Optionally provide a custom title."""
    if not re.match(r"https?://", url):
        await interaction.response.send_message("Please provide a valid URL (starting with http:// or https://)")
        return

    await interaction.response.defer()
    
    try:
        payload = {
            "url": url,
            "source": "discord",
            "resource_type": "article"
        }
        
        if title:
            payload["title"] = title
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/ingest/",
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                link = response.json()
                await interaction.followup.send(f"✅ **Force inserted!**\nTitle: {link.get('title', 'N/A')}\nURL: {link['url']}")
                return
            except requests.RequestException as retry_error:
                if attempt < max_retries - 1:
                    await interaction.followup.send(f"⚠️ Attempt {attempt + 1} failed, retrying...")
                    continue
                else:
                    raise retry_error
                    
    except requests.RequestException as e:
        await interaction.followup.send(f"❌ Force push failed after 3 attempts: {str(e)[:100]}")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
