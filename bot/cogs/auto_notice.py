import discord
import re
from discord.ext import commands

# ⚙️ [설정] 일반 채팅을 임베드로 자동 변환할 채널 ID를 입력하세요!
NOTICE_CHANNEL_ID = 1540640158628716644  # 공지 채널 ID

class AutoNoticeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 1. 봇이 작성한 메시지이거나, 지정된 공지 채널이 아니면 무시
        if message.author.bot or message.channel.id != NOTICE_CHANNEL_ID:
            return

        # 2. 작성자가 관리자인지 확인
        if not message.author.guild_permissions.administrator:
            return

        # 3. 메시지 본문에서 멘션(@everyone, @here, @역할) 추출하기
        mentions = []
        
        if message.mention_everyone:
            if "@everyone" in message.content:
                mentions.append("@everyone")
            if "@here" in message.content:
                mentions.append("@here")

        if message.role_mentions:
            for role in message.role_mentions:
                mentions.append(role.mention)

        mention_text = " ".join(list(dict.fromkeys(mentions))) if mentions else None

        # 4. 첨부파일(이미지) 확인
        image_url = None
        if message.attachments:
            image_url = message.attachments[0].url

        # 5. 임베드 생성
        embed = discord.Embed(
            title="📢 공지사항",
            description=message.content,
            color=discord.Color(0xF705D2)
        )
        
        if message.guild.icon:
            embed.set_author(name=message.guild.name, icon_url=message.guild.icon.url)
        embed.set_footer(text=f"작성자: {message.author.display_name}", icon_url=message.author.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        if image_url:
            embed.set_image(url=image_url)

        # 6. 원본 채팅 삭제 후 멘션 + 임베드 전송
        try:
            await message.delete()  # 원본 삭제
            
            # 모든 멘션 허용 설정 (에러 방지 및 알림 보장)
            allowed = discord.AllowedMentions(everyone=True, roles=True, users=True)

            if mention_text:
                await message.channel.send(content=mention_text, embed=embed, allowed_mentions=allowed)
            else:
                await message.channel.send(embed=embed)

        except discord.Forbidden:
            print("⚠️ 봇에게 '메시지 관리' 또는 '메시지 전송' 권한이 없습니다.")
        except Exception as e:
            print(f"⚠️ 공지 변환 중 에러 발생: {e}")

async def setup(bot):
    await bot.add_cog(AutoNoticeCog(bot))