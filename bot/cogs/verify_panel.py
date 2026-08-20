import discord
from discord.ext import commands

# ⚙️ [설정] 본인 서버 설정에 맞게 수정
VERIFY_CHANNEL_ID = 1539964159314362409  # 인증 채널 ID (숫자)
VERIFY_ROLE_NAME = "유저"               # 인증 완료 시 줄 역할 이름
EMOJI_PREFIX = "꒰ა🐚໒꒱"                   # 닉네임 앞에 붙일 이모지

class VerifyPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ 서버 입장 인증하기", style=discord.ButtonStyle.green, custom_id="persistent_verify_button")
    async def verify_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        role = discord.utils.get(interaction.guild.roles, name=VERIFY_ROLE_NAME)

        if not role:
            await interaction.response.send_message(f"❌ `{VERIFY_ROLE_NAME}` 역할을 찾을 수 없습니다.", ephemeral=True)
            return

        if role in user.roles:
            await interaction.response.send_message("⚠️ 이미 인증이 완료된 계정입니다!", ephemeral=True)
            return

        await user.add_roles(role)

        nick_changed = True
        try:
            if not user.display_name.startswith(EMOJI_PREFIX):
                new_nick = f"{EMOJI_PREFIX}{user.display_name}"
                await user.edit(nick=new_nick)
        except discord.Forbidden:
            nick_changed = False

        if nick_changed:
            await interaction.response.send_message(f"🎉 인증 완료! **{role.name}** 역할이 부여되고 닉네임이 변경되었습니다.", ephemeral=True)
        else:
            await interaction.response.send_message(f"🎉 인증 완료! **{role.name}** 역할이 부여되었습니다. (관리자 계정은 닉네임 변경 제외)", ephemeral=True)

class VerifyPanelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(VerifyPanelView())
        channel = self.bot.get_channel(VERIFY_CHANNEL_ID)
        if channel:
            async for message in channel.history(limit=10):
                if message.author == self.bot.user and message.embeds:
                    return
            
            embed = discord.Embed(
                title="🪼₊˚⊹🫧・서버 입장하기・🫧⊹˚₊🪼",
                description=f"아래 버튼을 누르면 **{VERIFY_ROLE_NAME}** 역할이 부여되고 닉네임 앞에 **{EMOJI_PREFIX}**가 붙으며 모든 채널이 열립니다.",
                color=discord.Color.green()
            )
            embed.set_footer(text="시스템 · 입장 인증 보안 패널")
            await channel.send(embed=embed, view=VerifyPanelView())

async def setup(bot):
    await bot.add_cog(VerifyPanelCog(bot))