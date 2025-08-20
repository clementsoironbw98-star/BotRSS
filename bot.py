import os
import discord
from discord.ext import tasks
import feedparser
from dotenv import load_dotenv
load_dotenv()


# Récupération des variables d'environnement
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))  # ID du salon Discord
RSS_FEEDS = [
    "https://actucine.webnode.fr/rss/all.xml",
    "https://www.cnc.fr/rss/-/journal/rss/36995/942647"
]

# Vérification basique
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN non défini dans les variables d'environnement.")
if CHANNEL_ID == 0:
    raise ValueError("❌ CHANNEL_ID non défini ou incorrect dans les variables d'environnement.")

# Set pour éviter les doublons
seen_links = set()

# Intents
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")
    check_rss.start()

@tasks.loop(minutes=5)
async def check_rss():
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print("⚠️ Impossible de trouver le salon. Vérifie l'ID.")
        return

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:  # On prend les 3 derniers articles
            if entry.link not in seen_links:
                seen_links.add(entry.link)
                try:
                    await channel.send(f"📰 **{entry.title}**\n{entry.link}")
                    print(f"✅ Article envoyé: {entry.title}")
                except Exception as e:
                    print(f"❌ Erreur en envoyant l'article: {e}")

# Démarrage du bot
client.run(TOKEN)
