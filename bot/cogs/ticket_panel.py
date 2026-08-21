import discord
import asyncio
from discord.ext import commands
import datetime

# ⚙️ [설정] 본인 서버 상황에 맞게 채널 ID를 넣어주세요!
TICKET_PANEL_CHANNEL_ID = 1539988031728128010  # 패널이 위치할 채널 ID

# 🔒 관리자만 볼 수 있는 로그 기록 채널 ID (분리 저장)
INQUIRY_LOG_CHANNEL_ID  = 1539989164303319080  # 문의 기록 저장용 로그 채널 ID
REPORT_LOG_CHANNEL_ID   = 1539989205676068884  # 신고 기록 저장용 로그 채널 ID

CATEGORY_NAME = "문의 및 신고"                 # 생성될 비공개 채널들의 카테고리 이름

# ==========================================
# 1. 패널 및 버튼 정의
# ==========================================
class UnifiedTicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="💙 문의하기 💙", style=discord.ButtonStyle.primary, custom_id="btn_unified_inquiry")
    async def create_inquiry(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket_channel(
            interaction, 
            prefix="문의", 
            title="1:1 문의", 
            description="**문의하실 내용**을 상세히 남겨주시면 관리자가 확인 후 답변해 드립니다."
        )

    @discord.ui.button(label="🚨 유저/채널 신고하기 🚨", style=discord.ButtonStyle.danger, custom_id="btn_unified_report")
    async def create_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket_channel(
            interaction, 
            prefix="신고", 
            title="신고 접수", 
            description="**신고 대상(유저/채널)과 사유, 증거 스크린샷**을 함께 남겨주시면 관리자가 확인 후 조치하겠습니다."
        )

# ==========================================
# 2. 비공개 채널 생성 로직
# ==========================================
# 📌 description으로 매개변수 이름을 일치시켰습니다!
async def create_ticket_channel(interaction: discord.Interaction, prefix: str, title: str, description: str):
    guild = interaction.guild
    user = interaction.user

    ticket_channel_name = f"{prefix}-{user.name.lower()}"
    existing_channel = discord.utils.get(guild.text_channels, name=ticket_channel_name)
    
    if existing_channel:
        await interaction.response.send_message(f"⚠️ 이미 진행 중인 {prefix} 채널이 있습니다: {existing_channel.mention}", ephemeral=True)
        return

    # 1. 기본 권한 설정 (일반 유저 비공개, 신청자 및 봇 허용)
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    # 2. 문의/신고 볼 수 있는 관리자 역할 권한 추가
    staff_role1 = guild.get_role(1539945377724104755)
    if staff_role1:
        overwrites[staff_role1] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    staff_role2 = guild.get_role(1539946285715427379)
    if staff_role2:
        overwrites[staff_role2] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
    if not category:
        category = await guild.create_category(CATEGORY_NAME)

    ticket_channel = await guild.create_text_channel(
        name=ticket_channel_name,
        category=category,
        overwrites=overwrites
    )

    await interaction.response.send_message(f"✅ {title} 채널이 생성되었습니다: {ticket_channel.mention}", ephemeral=True)

    color = discord.Color.blue() if prefix == "문의" else discord.Color.red()
    embed = discord.Embed(
        title=f"📋 {title} 채널",
        description=f"안녕하세요 {user.mention}님!\n\n{description}\n\n볼일이 끝나시면 아래 **`🔒 종료 및 채널 삭제`** 버튼을 누르세요.",
        color=color
    )
    await ticket_channel.send(content=f"{user.mention} 님", embed=embed, view=TicketCloseView(prefix=prefix, ticket_owner=user))

# ==========================================
# 3. 종료 버튼 및 대화 내역 로그 저장 로직
# ==========================================
class TicketCloseView(discord.ui.View):
    def __init__(self, prefix: str = "문의", ticket_owner: discord.User = None):
        super().__init__(timeout=None)
        self.prefix = prefix
        self.ticket_owner = ticket_owner

    @discord.ui.button(label="🔒 종료 및 채널 삭제", style=discord.ButtonStyle.secondary, custom_id="btn_unified_ticket_close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("5초 뒤 채널을 삭제합니다.")

        channel = interaction.channel
        guild = interaction.guild

        messages = []
        async for msg in channel.history(limit=100, oldest_first=True):
            if msg.author.bot and msg.embeds and "📋" in (msg.embeds[0].title or ""):
                continue
            
            time_str = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
            content = msg.content if msg.content else "(이미지/첨부파일 포함)"
            messages.append(f"[{time_str}] {msg.author.display_name}: {content}")

        log_text = "\n".join(messages) if messages else "작성된 메시지가 없습니다."

        if len(log_text) > 3800:
            log_text = log_text[-3800:] + "\n...(이전 대화 내용 생략)..."

        is_inquiry = "문의" in channel.name or self.prefix == "문의"
        log_channel_id = INQUIRY_LOG_CHANNEL_ID if is_inquiry else REPORT_LOG_CHANNEL_ID
        log_channel = guild.get_channel(log_channel_id)

        if log_channel:
            owner_mention = self.ticket_owner.mention if self.ticket_owner else "알 수 없음"
            color = discord.Color.blue() if is_inquiry else discord.Color.red()
            title_prefix = "📩 문의" if is_inquiry else "🚨 신고"

            log_embed = discord.Embed(
                title=f"{title_prefix} 기록 저장 완료",
                description=f"**종료된 채널:** `{channel.name}`\n**신청자:** {owner_mention}\n**종료 처리자:** {interaction.user.mention}\n\n```text\n{log_text}\n```",
                color=color,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            log_embed.set_footer(text=f"타입: {'문의' if is_inquiry else '신고'} 기록")
            await log_channel.send(embed=log_embed)

        await asyncio.sleep(5)
        await channel.delete()

# ==========================================
# 4. Cog 메인 및 자동 패널 삭제/생성
# ==========================================
class TicketPanelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(UnifiedTicketPanelView())
        self.bot.add_view(TicketCloseView())

        channel = self.bot.get_channel(TICKET_PANEL_CHANNEL_ID)
        if channel:
            # 기존 봇의 패널 메시지 깔끔하게 삭제 후 새로 생성
            async for message in channel.history(limit=10):
                if message.author == self.bot.user:
                    try:
                        await message.delete()
                    except:
                        pass

            embed = discord.Embed(
                title="🎫 고객지원 및 신고 센터",
                description=(
                    "도움이 필요하시거나 불편 사항이 있으신가요?\n"
                    "아래 원하시는 버튼을 누르시면 **1:1 비공개 채널**이 생성됩니다.\n\n"
                    "🔹 **💙 문의하기 💙** 제작문의, 건의사항 등\n"
                    "🔸 **🚨 유저/채널 신고하기 🚨** 규칙 위반, 비매너 유저 및 채널 신고"
                ),
                color=discord.Color.gold()
            )
            embed.set_footer(text="시스템 · 1:1 고객 지원")
            await channel.send(embed=embed, view=UnifiedTicketPanelView())

async def setup(bot):
    await bot.add_cog(TicketPanelCog(bot))