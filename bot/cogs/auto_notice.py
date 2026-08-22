import discord
from discord.ext import commands

NOTICE_CHANNEL_ID = 1540752618387935383  # 공지 채널 ID

ALLOWED_ROLE_IDS = [
    1539945377724104755,
    1539946285715427379
]

class AutoNoticeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 1. 봇 메시지이거나 지정된 공지 채널이 아니면 무시
        if message.author.bot or message.channel.id != NOTICE_CHANNEL_ID:
            return

        # 2. 작성 권한 확인
        is_admin = message.author.guild_permissions.administrator
        has_allowed_role = any(role.id in ALLOWED_ROLE_IDS for role in message.author.roles)

        if not (is_admin or has_allowed_role):
            return

        # ⚡ 3. [핵심] 메시지를 받자마자 "무조건 최우선으로 원본 삭제"!
        try:
            await message.delete()
        except discord.Forbidden:
            print("❌ 오류: 봇에게 '메시지 관리' 권한이 없어서 원본 메시지를 못 지웁니다!")
            print("👉 디스코드 채널 설정에서 봇에게 '메시지 관리' 권한을 켜주세요.")
            return
        except Exception as e:
            print(f"❌ 삭제 실패: {e}")

        # 4. 작성자의 역할 색상 가져오기
        embed_color = discord.Color(0xF705D2)
        for role in reversed(message.author.roles):
            if role.color != discord.Color.default():
                embed_color = role.color
                break

        # 5. 멘션 추출
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

        # 6. 첨부파일(이미지) 확인
        image_url = message.attachments[0].url if message.attachments else None

        # 7. 임베드 생성
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

        # 8. 공지 전송
        try:
            allowed = discord.AllowedMentions(everyone=True, roles=True, users=True)
            await message.channel.send(embed=embed)

            if mention_text:
                await message.channel.send(content=mention_text, allowed_mentions=allowed)

        except Exception as e:
            print(f"❌ 공지 전송 실패: {e}")

async def setup(bot):
    await bot.add_cog(AutoNoticeCog(bot))