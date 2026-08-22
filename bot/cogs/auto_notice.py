import discord
import re
from discord.ext import commands

# ⚙️ [설정] 일반 채팅을 임베드로 자동 변환할 채널 ID를 입력하세요!
NOTICE_CHANNEL_ID = 1540640158628716644  # 👈 공지 채널 ID로 수정 필수!

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
        
        # @everyone 이나 @here 가 포함되어 있다면 추가
        if message.mention_everyone:
            if "@everyone" in message.content:
                mentions.append("@everyone")
            if "@here" in message.content:
                mentions.append("@here")

        # 특정 역할(@Role) 태그 추출
        if message.role_mentions:
            for role in message.role_mentions:
                mentions.append(role.mention)

        # 중복 멘션 제거 및 한 줄로 합치기
        mention_text = " ".join(list(dict.fromkeys(mentions))) if mentions else None

        # 4. 첨부파일(이미지) 확인
        image_url = None
        if message.attachments:
            image_url = message.attachments[0].url

        # 5. 임베드 생성
        embed = discord.Embed(
            title="📢 공지사항",
            description=message.content,  # 작성한 원본 내용 그대로 복사
            color=discord.Color(0xF705D2)
        )
        
        if message.guild.icon:
            embed.set_author(name=message.guild.name, icon_url=message.guild.icon.url)
        embed.set_footer(text=f"작성자: {message.author.display_name}", icon_url=message.author.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        if image_url:
            embed.set_image(url=image_url)

        # 6. 원본 채팅 삭제 후 멘션 + 임베드 같이 전송
        try:
            await message.delete()  # 입력한 일반 채팅 삭제
            
            # 멘션이 있으면 멘션 문구와 임베드를 함께 전송 (알림 정상 작동!)
            if mention_text:
                await message.channel.send(content=mention_text, embed=embed)
            else:
                await message.channel.send(embed=embed)

        except discord.Forbidden:
            print("⚠️ 봇에게 '메시지 관리' 권한이 없어 원본 메시지를 지우지 못했습니다.")

async def setup(bot):
    await bot.add_cog(AutoNoticeCog(bot))