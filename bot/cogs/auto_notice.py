import discord
from discord.ext import commands

# ⚙️ [설정] 일반 채팅을 임베드로 자동 변환할 채널 ID를 입력하세요!
NOTICE_CHANNEL_ID = 1540031700086693938  # 👈 공지 채널 ID로 수정 필수!

class AutoNoticeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 1. 봇이 작성한 메시지이거나, 지정된 공지 채널이 아니면 무시
        if message.author.bot or message.channel.id != NOTICE_CHANNEL_ID:
            return

        # 2. 작성자가 관리자인지 확인 (일반 유저의 도배 방지)
        if not message.author.guild_permissions.administrator:
            return

        # 3. 원본 작성자가 올린 첨부파일(이미지 등) 확인
        image_url = None
        if message.attachments:
            image_url = message.attachments[0].url  # 첫 번째 첨부파일 이미지 가져오기

        # 4. 임베드 생성
        embed = discord.Embed(
            title="📢 공지사항",
            description=message.content,  # 작성한 채팅 내용
            color=discord.Color(0xF705D2)     # 원하는 색상으로 변경 가능 (gold, red, green 등)
        )
        
        # 서버 프로필 & 작성자 정보 추가
        if message.guild.icon:
            embed.set_author(name=message.guild.name, icon_url=message.guild.icon.url)
        embed.set_footer(text=f"작성자: {message.author.display_name}", icon_url=message.author.display_avatar.url)
        embed.timestamp = discord.utils.utcnow()

        # 이미지가 첨부되어 있었다면 임베드에 포함
        if image_url:
            embed.set_image(url=image_url)

        # 5. 원본 채팅 메시지 삭제 후 임베드 공지 전송
        try:
            await message.delete()  # 관리자가 친 일반 채팅 삭제
            await message.channel.send(embed=embed)  # 변환된 임베드 전송
        except discord.Forbidden:
            print("⚠️ 봇에게 '메시지 관리' 권한이 없어 원본 메시지를 지우지 못했습니다.")

async def setup(bot):
    await bot.add_cog(AutoNoticeCog(bot))