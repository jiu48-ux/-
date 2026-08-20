import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# --- 1. Render 포트 바인딩용 Flask 웹서버 ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    # Render가 자동으로 지정해 주는 PORT 환경변수를 읽어옵니다 (기본값 10000)
    port = int(os.environ.get("PORT", 10000))
    # 0.0.0.0 으로 바인딩해야 Render 외부 통신이 감지됩니다
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True  # 메인 프로세스 종료 시 함께 종료되도록 설정
    t.start()

# --- 2. 디스코드 봇 설정 ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ 로그인 성공: {bot.user}")

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

async def main():
    # 웹서버 먼저 확실하게 실행 (포트 바인딩)
    keep_alive()
    
    async with bot:
        await load_extensions()
        token = os.environ.get("DISCORD_TOKEN")
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
