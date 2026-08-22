import discord
from discord.ext import commands
import os
import asyncio
from keep_alive import keep_alive

# 봇 인텐트 설정
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'✅ 로그인 성공: {bot.user.name} (ID: {bot.user.id})')
    
    # 슬래시 커맨드 즉시 동기화
    try:
        synced = await bot.tree.sync()
        print(f"✅ 슬래시 커맨드 {len(synced)}개 즉시 동기화 완료!")
    except Exception as e:
        print(f"❌ 슬래시 커맨드 동기화 실패: {e}")

async def load_extensions():
    # main.py가 위치한 폴더 기준으로 cogs 폴더 경로를 지정합니다.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cogs_dir = os.path.join(current_dir, 'cogs')
    
    # cogs 폴더가 존재할 때만 로드 진행
    if os.path.exists(cogs_dir):
        for filename in os.listdir(cogs_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"📦 Cog 로드 완료: {filename[:-3]}")

async def main():
    async with bot:
        # 1. cogs 명령어 파일 로드
        await load_extensions()
        
        # 2. Render 웹 포트 유지를 위한 Flask 서버 실행
        keep_alive()
        
        # 3. 디스코드 로그인 및 봇 시작
        token = os.environ.get('DISCORD_TOKEN')
        if not token:
            print("❌ 에러: DISCORD_TOKEN 환경 변수를 찾을 수 없습니다!")
            return
        await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())