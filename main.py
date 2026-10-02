import os
import asyncio
import discord
from discord.ext import commands
import requests
import edge_tts
from dotenv import load_dotenv
from googletrans import Translator

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================
# CUANDO EL BOT INICIA
# =========================

@bot.event
async def on_ready():

    print("================================")
    print("🤖 Bot conectado correctamente")
    print("👤 Usuario:", bot.user)
    print("================================")

    # Buscar un canal de texto donde pueda enviar el mensaje
    for servidor in bot.guilds:

        for canal in servidor.text_channels:

            if canal.permissions_for(servidor.me).send_messages:

                try:

                    await canal.send(
                        "🤖 **¡FunFactsBot está en línea!**\n\n"
                        "📋 **Comandos disponibles:**\n"
                        "🌦️ `!weather <ciudad>` — Consulta el clima.\n"
                        "🧠 `!fact` — Obtén un dato interesante y escúchalo en voz."
                    )

                    break

                except discord.Forbidden:
                    continue

        break


# =========================
# CLIMA
# =========================

def get_weather(city):

    url = f"https://wttr.in/{city}?format=%C+%t&lang=es"

    response = requests.get(url)

    if response.status_code == 200:
        return response.text.strip()

    return "No pude obtener el clima"


# =========================
# DATOS CURIOSOS
# =========================

def get_fact():

    url = "https://uselessfacts.jsph.pl/api/v2/facts/random"

    response = requests.get(url)

    print("Código de respuesta:", response.status_code)
    print("Respuesta:", response.json())

    if response.status_code == 200:

        data = response.json()

        hecho = data["text"]

        # Traducir al español
        translator = Translator()

        traduccion = translator.translate(
            hecho,
            src="en",
            dest="es"
        )

        return traduccion.text

    return "No pude obtener un dato interesante."


# =========================
# TEXTO A AUDIO
# =========================

async def text_to_audio(text, archivo):

    voz = edge_tts.Communicate(
        text,
        "es-MX-DaliaNeural"
    )

    await voz.save(archivo)


# =========================
# COMANDO WEATHER
# =========================

@bot.command()
async def weather(ctx, *, city):

    info = get_weather(city)

    texto = f"El clima en {city} es {info}"

    await text_to_audio(
        texto,
        "clima.mp3"
    )

    await ctx.send(
        f"🌦️ **Clima en {city}:** {info}",
        file=discord.File("clima.mp3")
    )


# =========================
# COMANDO FACT
# =========================

@bot.command()
async def fact(ctx):

    hecho = get_fact()

    await text_to_audio(
        hecho,
        "fact.mp3"
    )

    await ctx.send(
        f"🧠 **Dato interesante:** {hecho}",
        file=discord.File("fact.mp3")
    )

    if os.path.exists("fact.mp3"):
        os.remove("fact.mp3")


# =========================
# INICIAR BOT
# =========================

bot.run(os.getenv("DISCORD_TOKEN"))