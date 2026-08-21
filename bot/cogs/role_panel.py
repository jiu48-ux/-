import discord
from discord.ext import commands

#⚙️ [설정] 역할 패널 채널 ID
ROLE_CHANNEL_ID = 1539988135847403661  # #역할-선택 채널 ID (숫자)

class RoleSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🤿 제작 알림", style=discord.ButtonStyle.primary, custom_id="role_btn_notice")
    async def notice_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, int(1540288313661857913))

    @discord.ui.button(label="🐬 이벤트 알림", style=discord.ButtonStyle.success, custom_id="role_btn_event")
    async def event_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.toggle_role(interaction, int(1540289160500215858))

    async def toggle_role(self, interaction: discord.Interaction, role_id: int):
        role = interaction.guild.get_role(role_id)
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
                title="🫧 𝒟𝒾𝓋𝑒𝓇'𝓈  𝒫𝒶𝓈𝓈𝓅𝑜𝓇𝓉",
                description=(
                    "# 🤿 Welcome to 𝓢𝓬𝓾𝓿𝓮𝓻 𝓭𝓲𝓿𝓮 Emoji Shop!\n\n"
                    "바닷속 숨겨진 이모지와 스티커 소식을 누구보다 빠르게 받아보세요!\n"
                    "아래 메뉴를 눌러 원하는 알림 역할을 선택할 수 있습니다. 🫧\n\n"
                    "------------------------------------------------\n\n"
                    "🪸 **`𝓓𝓮𝓮𝓹 𝓢𝓮𝓪`**\n"
                    "> 새로운 이모지 & 스티커가 등록되면 신상 알림 핑을 받습니다.\n\n"
                    "🐬 **`𝒟𝑜𝓁𝓅𝒽𝒾𝓃 𝒫𝒶𝓇𝓉𝓎`**\n"
                    "> 한정판 이모지 드롭, 이벤트, 할인 소식 핑을 받습니다.\n\n"
                    "⚓ **원하는 역할을 클릭해서 바닷속 보물을 찾아 떠나보세요!** 🌊"
                ),
                color=discord.Color(0x0077B6)
            )
            embed.set_footer(text="시스템 · 자동 역할 선택")
            await channel.send(embed=embed, view=RoleSelectView())

async def setup(bot):
    await bot.add_cog(RolePanelCog(bot))
