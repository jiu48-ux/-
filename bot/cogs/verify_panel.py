import discord
from discord.ext import commands

# ⚙️ [기본 설정]
VERIFY_CHANNEL_ID = 123456789012345678  # 인증 패널이 올 채널 ID
VERIFY_ROLE_ID = 1539966686386462852    # 지급할 역할 ID
EMOJI_PREFIX = "꒰ა🐚໒꒱"                 # 닉네임 앞 이모지

# 🎨 [디자인 설정 - 바다 콘셉트]
EMBED_COLOR = discord.Color.from_rgb(0, 119, 182) # 에메랄드 딥 블루 (바다색)


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # 봇 재부팅 후에도 버튼 유지

    @discord.ui.button(
        label="해저 입장 및 역할 받기", 
        style=discord.ButtonStyle.primary, # 바다 느낌의 파란색 버튼
        emoji="🪸", 
        custom_id="btn_verify_scuba_ocean_v2"
    )
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # ⚡ 3초 타임아웃 방지 (사용자 응답 대기 처리)
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        member = interaction.user

        # 1. 역할 존재 여부 확인
        role = guild.get_role(VERIFY_ROLE_ID)
        if not role:
            await interaction.followup.send(
                f"🌊 **[오류]** 서버에서 인증 역할(ID: `{VERIFY_ROLE_ID}`)을 찾을 수 없습니다. 관리자에게 문의해 주세요.",
                ephemeral=True
            )
            return

        # 2. 이미 역할이 있는지 확인
        if role in member.roles:
            await interaction.followup.send(
                "🌊 이미 입수(인증)가 완료된 다이버 계정입니다!", 
                ephemeral=True
            )
            return

        # 3. 닉네임 자동 설정 (32자 한계 처리)
        new_nickname = f"{EMOJI_PREFIX} {member.display_name}"
        if len(new_nickname) > 32:
            new_nickname = new_nickname[:32]

        # 4. 역할 부여 및 닉네임 변경 실행
        try:
            await member.edit(nick=new_nickname)
            await member.add_roles(role)
            
            await interaction.followup.send(
                f"🫧 **입수 성공!** 환영합니다, 다이버님!\n"
                f"• **변경된 닉네임:** `{new_nickname}`\n"
                f"• **지급된 역할:** {role.mention}\n\n"
                f"지금부터 모든 채널을 이용하실 수 있습니다. 즐거운 다이빙 되세요! 🥽",
                ephemeral=True
            )
        except discord.Forbidden:
            # 봇의 역할 순위가 낮아 닉네임을 못 바꾸는 경우에도 역할은 먼저 부여
            await member.add_roles(role)
            await interaction.followup.send(
                f"🫧 **입수 성공!** (닉네임 변경은 건너뜀)\n"
                f"• **지급된 역할:** {role.mention}\n\n"
                f"*(⚠️ 봇의 역할 순위 권한 문제로 닉네임 자동 변경은 적용되지 않았습니다.)*",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ 인증 처리 중 오류가 발생했습니다: `{e}`", 
                ephemeral=True
            )


class VerifyPanelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # 봇 재부팅 후에도 버튼이 정상 동작하도록 뷰 추가
        self.bot.add_view(VerifyView())

        channel = self.bot.get_channel(VERIFY_CHANNEL_ID)
        if not channel:
            return

        # 중복 메시지 전송 방지 (최근 10개 메시지 탐색)
        async for message in channel.history(limit=10):
            if message.author == self.bot.user and message.embeds:
                return

        role = channel.guild.get_role(VERIFY_ROLE_ID)
        role_mention = role.mention if role else "인증 회원"

        # 🌊 바다 테마 디자인 임베드
        embed = discord.Embed(
            title="🌊 Oceanic Scuba Server | 입장 인증",
            description=(
                "푸른 바닷속에 오신 것을 환영합니다! 🥽\n"
                "아래 버튼을 눌러 인증을 완료하시면 서버의 모든 채널이 열립니다.\n\n"
                "───── **안내 사항** ─────\n"
                f"🪸 **이름 변경:** 닉네임 앞에 **`{EMOJI_PREFIX}`** 이모지가 붙습니다.\n"
                f"🥽 **역할 지급:** {role_mention} 역할이 부여되어 자유롭게 입장 가능합니다."
            ),
            color=EMBED_COLOR
        )
        
        # 패널 구성 완성도 업
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/3143/3143460.png") # 스쿠버 다이빙 아이콘
        embed.set_footer(text="Oceanic Scuba System • 안전하고 즐거운 다이빙 생활", icon_url=self.bot.user.display_avatar.url)

        await channel.send(embed=embed, view=VerifyView())


async def setup(bot):
    await bot.add_cog(VerifyPanelCog(bot))
