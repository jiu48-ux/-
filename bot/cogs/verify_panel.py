import discord
from discord.ext import commands

# ⚙️ [설정]
VERIFY_CHANNEL_ID = 123456789012345678  # 인증 패널이 올라갈 채널 ID (숫자)
VERIFY_ROLE_ID = 1539966686386462852    # 지급할 역할 ID (숫자)
EMOJI_PREFIX = "꒰ა🐚໒꒱"                 # 닉네임 앞에 붙일 이모지

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # 봇 재부팅 후에도 버튼 지속 동작

    @discord.ui.button(label="인증하고 입장하기", style=discord.ButtonStyle.success, custom_id="btn_verify_user_by_id")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user  # 버튼을 누른 유저

        # 1. 역할 ID로 정확한 역할 찾기
        role = guild.get_role(VERIFY_ROLE_ID)
        if not role:
            await interaction.response.send_message(
                f"❌ 지정된 역할(ID: `{VERIFY_ROLE_ID}`)을 서버에서 찾을 수 없습니다. 역할 ID를 다시 확인해 주세요.", 
                ephemeral=True
            )
            return

        # 2. 이미 인증된 유저인지 체크
        if role in member.roles:
            await interaction.response.send_message("⚠️ 이미 인증이 완료된 계정입니다!", ephemeral=True)
            return

        # 3. 유저 본인의 디스코드 이름(display_name) 앞에 이모지 붙여서 닉네임 변경
        # 예: '홍길동' -> '꒰ა🐚໒꒱ 홍길동'
        new_nickname = f"{EMOJI_PREFIX} {member.display_name}"
        
        # 디스코드 닉네임 최대 길이는 32자 제한이 있으므로 짤림 방지 처리
        if len(new_nickname) > 32:
            new_nickname = new_nickname[:32]

        try:
            # 닉네임 변경 및 역할 부여
            await member.edit(nick=new_nickname)
            await member.add_roles(role)
            
            await interaction.response.send_message(
                f"✅ 인증이 완료되었습니다!\n닉네임이 **`{new_nickname}`**(으)로 변경되고 **{role.mention}** 역할이 지급되었습니다.", 
                ephemeral=True
            )
        except discord.Forbidden:
            # 봇의 권한이 서버 소유자/관리자보다 낮아서 닉네임을 못 바꾸는 경우
            await member.add_roles(role)
            await interaction.response.send_message(
                f"✅ 인증 및 역할({role.mention}) 지급이 완료되었습니다.\n(⚠️ 봇 역할 순위 권한 문제로 닉네임 변경은 건너뛰었습니다.)", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ 인증 처리 중 오류가 발생했습니다: {e}", ephemeral=True)

class VerifyPanelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # 버튼 영구 유지 등록
        self.bot.add_view(VerifyView())

        channel = self.bot.get_channel(VERIFY_CHANNEL_ID)
        if channel:
            # 이미 인증 패널 메시지가 올려져 있으면 중복 전송 방지
            async for message in channel.history(limit=10):
                if message.author == self.bot.user and message.embeds:
                    return

            role = channel.guild.get_role(VERIFY_ROLE_ID)
            role_name = role.name if role else "인증 회원"

            embed = discord.Embed(
                title="🐚 서버 입장 인증",
                description=(
                    "아래 **`인증하고 입장하기`** 버튼을 누르시면 인증이 완료됩니다.\n\n"
                    f"• 닉네임 앞에 **`{EMOJI_PREFIX}`** 이모지가 자동으로 붙습니다.\n"
                    f"• **{role_name}** 역할이 부여되어 모든 채널 이용이 가능해집니다."
                ),
                color=discord.Color.teal()
            )
            embed.set_footer(text="스쿠버다이빙 서버 입장 시스템")
            await channel.send(embed=embed, view=VerifyView())

async def setup(bot):
    await bot.add_cog(VerifyPanelCog(bot))
