import discord
from discord.ext import commands
import os
import asyncio
from keep_alive import keep_alive  # keep_alive를 쓰시는 경우

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

async def load_extensions():
    # cogs 폴더 안의 모든 파이썬 파일을 딱 한 번씩만 로드합니다.
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            # __init__.py 같은 파일은 제외하고 순수 cog만 불러옵니다.
            if not filename.startswith('__'):
                await bot.load_extension(f'cogs.{filename[:-3]}')

async def main():
    async with bot:
        await load_extensions()
        # keep_alive()  # 필요시 사용
        await bot.start(os.environ.get('DISCORD_TOKEN'))

if __name__ == '__main__':
    asyncio.run(main())
