import discord
from discord.ext import commands

# ⚙️ [설정]
NOTICE_CHANNEL_ID = 1540640158628716644  # 공지 채널 ID

# 📌 공지를 쓸 수 있는 허용 역할 ID 목록 (여러 개 등록 가능!)
# 디스코드 설정 ➡️ 역할 ➡️ 원하는 역할 우클릭 ➡️ '역할 ID 복사'해서 넣으세요.
ALLOWED_ROLE_IDS = [
    1539945377724104755,  # 예: 스태프 역할 ID
    1539946285715427379   # 예: 공지 작성자 역할 ID (필요 없으면 1개만 남기세요)
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

        # 둘 다 해당하지 않으면 일반 채팅으로 취소(무시)
        if not (is_admin or has_allowed_role):
            return

        # 3. 멘션(@everyone, @here, @역할) 추출
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

        # 6. 원본 삭제 후 (임베드 ➡️ 아래 멘션) 전송
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