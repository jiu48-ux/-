import discord
from discord.ext import commands

NOTICE_CHANNEL_ID = 1540640158628716644  # 공지 채널 ID

class AutoNoticeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 1. 봇이 작성한 메시지이거나 지정된 공지 채널이 아니면 무시
        if message.author.bot or message.channel.id != NOTICE_CHANNEL_ID:
            return

        # 2. 관리자 권한 확인
        if not message.author.guild_permissions.administrator:
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

        # 4. 이미지 첨부파일 확인
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

        # 6. 원본 채팅 삭제 후 전송 (임베드 ➡️ 멘션 순서)
        try:
            await message.delete()
            
            allowed = discord.AllowedMentions(everyone=True, roles=True, users=True)

            # 📌 1단계: 먼저 임베드 상자를 전송합니다.
            sent_embed = await message.channel.send(embed=embed)

            # 📌 2단계: 멘션이 있다면 임베드 바로 밑에 멘션 메시지를 따로 보냅니다!
            if mention_text:
                await message.channel.send(content=mention_text, allowed_mentions=allowed)

        except discord.Forbidden:
            print("⚠️ 봇에게 메시지 관리/전송 권한이 없습니다.")
        except Exception as e:
            print(f"⚠️ 에러 발생: {e}")

async def setup(bot):
    await bot.add_cog(AutoNoticeCog(bot))