import discord
from discord.ext import commands

# ⚙️ [설정] 역할 패널 채널 ID
ROLE_CHANNEL_ID = 1539988135847403661  # #역할-선택 채널 ID (숫자)

class RoleSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔔 공지 알림 받기", style=discord.ButtonStyle.primary, custom_id="role_btn_notice")
    async def notice_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "알림수신")

    @discord.ui.button(label="🎉 이벤트 알림 받기", style=discord.ButtonStyle.success, custom_id="role_btn_event")
    async def event_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, "이벤트알림")

    async def toggle_role(self, interaction: discord.Interaction, role_name: str):
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if not role:
            await interaction.response.send_message(f"❌ `{role_name}` 역할을 찾을 수 없습니다.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"❌ **{role.name}** 역할을 해제했습니다.", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ **{role.name}** 역할을 부여받았습니다!", ephemeral=True)

class RolePanelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(RoleSelectView())
        channel = self.bot.get_channel(ROLE_CHANNEL_ID)
        if channel:
            async for message in channel.history(limit=10):
                if message.author == self.bot.user and message.embeds:
                    return
            
            embed = discord.Embed(
                title="🎭 역할 선택 패널",
                description="아래 버튼을 눌러 원하시는 역할을 자유롭게 부여받거나 해제하세요!",
                color=discord.Color.blue()
            )
            embed.set_footer(text="시스템 · 자동 역할 선택")
            await channel.send(embed=embed, view=RoleSelectView())

async def setup(bot):
    await bot.add_cog(RolePanelCog(bot))