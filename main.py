import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True  # Habilita esto para que el bot pueda leer los mensajes y usar comandos con prefijo
bot = commands.Bot(command_prefix='!', intents=intents)


async def load_cogs():
    for i in os.listdir("./cogs"):
        if i.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{i[:-3]}")
                print(f"Loaded {i}")
            except Exception as e:
                print(f"Error loading {i}")
                print(e)


@bot.event
async def on_ready():
    print(f"{bot.user} is ready!")
    # await bot.tree.sync()


async def main():
    await load_cogs()
    await bot.login(os.getenv("TOKEN"))
    await bot.connect()


if __name__ == '__main__':
    asyncio.run(main())
