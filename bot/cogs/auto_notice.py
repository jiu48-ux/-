import discord
from discord.ext import commands

# ⚙️ [설정]
NOTICE_CHANNEL_ID = 1540640158628716644  # 공지 채널 ID

# 📌 공지를 쓸 수 있는 허용 역할 ID 목록
ALLOWED_ROLE_IDS = [
    1539945377724104755,  # 예: 스태프 역할 ID
    1539946285715427379   # 예: 공지 작성자 역할 ID
]

class AutoNoticeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 1. 봇 메시지이거나 지정된 공지 채널이 아니면 무시
        if message.author.bot or message.channel.id != NOTICE_CHANNEL_ID:
            return

        # 2. 작성 권한 확인 (서버 관리자 OR 허용된 역할 보유자)
        is_admin = message.author.guild_permissions.administrator
        has_allowed_role = any(role.id in ALLOWED_ROLE_IDS for role in message.author.roles)

        # 둘 다 해당하지 않으면 무시
        if not (is_admin or has_allowed_role):
            return

        # 📌 3. 작성자의 역할 색상(Color) 결정
        # 기본 핑크색 (역할에 고유 색상이 설정되어 있지 않을 때 적용)
        embed_color = discord.Color(0xF705D2)

        # 작성자가 가진 역할 중 가장 높은 위치의 색상 가져오기
        for role in reversed(message.author.roles):
            if role.color != discord.Color.default():
                embed_color = role.color
                break

        # 4. 멘션(@everyone, @here, @역할) 추출
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

        # 5. 첨부파일(이미지) 확인
        image_url = None
        if message.attachments:
            image_url = message.attachments[0].url

        # 6. 임베드 생성 (자동 추출된 역할 색상 적용)
        embed = discord.Embed(
            title="📢 공지사항",
            description=message.content,
            color=embed_color
        )
        
        if message.guild.icon:
            embed.set_author(name=message.guild.name, icon_url=message.guild.icon.url)
        embed.set_footer(text=f"작성자: {message.author.display_name}", icon_url=message.author.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        if image_url:
            embed.set_image(url=image_url)

        # 7. 원본 삭제 후 (임베드 ➡️ 아래 멘션) 전송
        try:
            await message.delete()
            
            allowed = discord.AllowedMentions(everyone=True, roles=True, users=True)

            # 1단계: 임베드 전송
            await message.channel.send(embed=embed)

            # 2단계: 멘션이 있다면 임베드 바로 밑에 전송
            if mention_text:
                await message.channel.send(content=mention_text, allowed_mentions=allowed)

        except discord.Forbidden:
            print("⚠️ 봇에게 메시지 관리/전송 권한이 없습니다.")
        except Exception as e:
            print(f"⚠️ 공지 변환 실패: {e}")

async def setup(bot):
    await bot.add_cog(AutoNoticeCog(bot))