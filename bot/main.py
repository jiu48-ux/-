import asyncio
import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # 닉네임 및 역할 관리를 위해 멤버 권한 필수

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 로그인 성공: {bot.user.name}")

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.environ.get("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())