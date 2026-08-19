# -*- coding: utf-8 -*-
# ============================================================================
#  БОТ ЗАЯВОК — СЕМЬЯ ПРОХОРОВЫ  —  discord.py
# ============================================================================

import os
import discord
from discord import app_commands

# ============================================================================
#  ОБЩИЕ НАСТРОЙКИ
# ============================================================================

TOKEN = os.getenv("TOKEN")

GUILD_ID = 1375220511209947257

BANNER_URL = "https://ссылка_на_баннер_прохоровы.png"      # большой баннер внизу
THUMBNAIL_URL = "https://ссылка_на_лого_прохоровы.png"     # герб справа

EMBED_COLOR = 0xC0C0C0  # серебристый под герб (можно 0xB11226 для красного)

# ----------------------------------------------------------------------------
#  КОНФИГ СЕМЬИ
# ----------------------------------------------------------------------------
FAMILIES = {
    "prohorovy": {
        "name": "Прохоровы",
        "panel_command": "панель",
        "panel_title": "👑 Вступление в семью Прохоровы 🇷🇺",
        "submit_channel_id": 1538665847059513471,     # где висит кнопка
        "logs_channel_id": 1538665847260708998,        # куда падают заявки
        "accepted_role_id": 1539721211418775582,       # роль принятому
        "recruiter_role_ids": [1539721362854252574, 1539720792974164038],  # рекрут + глава
        "panel_role_ids": [1539720792974164038],       # кто может выкладывать /панель (глава)
        "call_voice_channel_id": 1538665847059513473,  # войс-приёмная для обзвона
    },
}

# --- Вопросы анкеты (макс. 5) ---
Q1_LABEL = "Ваше имя & возраст в IRL & игровой ник"
Q1_HINT = "Дмитрий & 54 года & ник: Zhmyshe"
Q2_LABEL = "Список семей, в которых были"
Q2_HINT = "KILLA, TANK, SMUZI"
Q3_LABEL = "Ваш лвл в игре & онлайн & часовой пояс"
Q3_HINT = "10 LVL & 10 ч & (+-1 МСК)"
Q4_LABEL = "Откат стрельбы / если нету то прочерк"
Q4_HINT = "Full Open Special (10 человек)"

BUTTON_LABEL = "📝 Подать заявку"
MODAL_TITLE = "Заявка на вступление в семью"

WELCOME_DESC = (
    "👑 Добро пожаловать! Здесь начинается твой путь в семью **{name}** 🇷🇺\n\n"
    "📌 **Как это работает:**\n"
    "▸ Нажми кнопку ниже и честно заполни анкету.\n"
    "▸ Если заявка проходит первичный отбор — тебя вызовут на **обзвон** "
    "(голосовое собеседование).\n"
    "▸ После обзвона рекрутер принимает финальное решение.\n\n"
    "⏳ Заявки рассматриваются в течение 1 дня.\n"
    "🔒 Не указывай в анкете пароли и личные данные."
)

ACCEPT_DM = "🎉 Поздравляем! Твоя заявка в семью **{name}** одобрена. Тебе выдана роль. Добро пожаловать!"
DECLINE_DM = "😔 К сожалению, твоя заявка в семью **{name}** отклонена. Ты можешь попробовать снова позже."
CALL_DM = (
    "🎙 **Вы были вызваны на обзвон!**\n\n"
    "Твоя заявка в семью **{name}** прошла первичный отбор. Зайди в **приёмную** "
    "и ожидай, пока рекрутер заберёт тебя на обзвон:\n{link}\n\n"
    "Доступ к приёмной уже открыт для тебя."
)

# ============================================================================
#  КОД
# ============================================================================

intents = discord.Intents.default()
intents.members = True


class FamilyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_dynamic_items(ApplyButton, AcceptButton, CallButton, DeclineButton)
        try:
            synced = await self.tree.sync()
            print(f"Синхронизировано команд: {len(synced)}")
        except Exception as e:
            print(f"Ошибка синхронизации команд: {e}")


bot = FamilyBot()


def _has_any_role(member, role_ids):
    if not isinstance(member, discord.Member):
        return False
    if member.guild and member.id == member.guild.owner_id:
        return True
    try:
        if any(rid in member._roles for rid in role_ids):
            return True
    except Exception:
        pass
    have = {r.id for r in member.roles}
    return any(rid in have for rid in role_ids)


def member_can_review(member, family_key) -> bool:
    return _has_any_role(member, FAMILIES[family_key]["recruiter_role_ids"])


def member_can_panel(member, family_key) -> bool:
    return _has_any_role(member, FAMILIES[family_key]["panel_role_ids"])


# ----------------------------------------------------------------------------
#  АНКЕТА (модалка кандидата)
# ----------------------------------------------------------------------------
class ApplicationModal(discord.ui.Modal):
    def __init__(self, family_key):
        self.family_key = family_key
        super().__init__(title=MODAL_TITLE)
        self.a1 = discord.ui.TextInput(label=Q1_LABEL, placeholder=Q1_HINT, max_length=200)
        self.a2 = discord.ui.TextInput(label=Q2_LABEL, placeholder=Q2_HINT,
                                       style=discord.TextStyle.paragraph, max_length=500)
        self.a3 = discord.ui.TextInput(label=Q3_LABEL, placeholder=Q3_HINT, max_length=200)
        self.a4 = discord.ui.TextInput(label=Q4_LABEL, placeholder=Q4_HINT, max_length=200)
        for item in (self.a1, self.a2, self.a3, self.a4):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        fam = FAMILIES[self.family_key]
        channel = interaction.client.get_channel(fam["logs_channel_id"])
        if channel is None:
            await interaction.response.send_message(
                "⚠️ Канал логов заявок не настроен. Сообщи администратору.", ephemeral=True)
            return

        embed = discord.Embed(title=f"📨 Новая заявка — {fam['name']}", color=EMBED_COLOR)
        embed.set_author(name=str(interaction.user),
                         icon_url=interaction.user.display_avatar.url)
        if THUMBNAIL_URL.startswith("http"):
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.add_field(name=f"👤 {Q1_LABEL}", value=self.a1.value, inline=False)
        embed.add_field(name=f"👪 {Q2_LABEL}", value=self.a2.value, inline=False)
        embed.add_field(name=f"🎮 {Q3_LABEL}", value=self.a3.value, inline=False)
        embed.add_field(name=f"🔫 {Q4_LABEL}", value=self.a4.value, inline=False)
        embed.add_field(name="\u200b", value=f"Кандидат: {interaction.user.mention}", inline=False)
        embed.set_footer(text=f"ID кандидата: {interaction.user.id}")

        view = discord.ui.View(timeout=None)
        view.add_item(AcceptButton(self.family_key, interaction.user.id))
        view.add_item(CallButton(self.family_key, interaction.user.id))
        view.add_item(DeclineButton(self.family_key, interaction.user.id))

        ping = " ".join(f"<@&{rid}>" for rid in fam["recruiter_role_ids"])
        await channel.send(content=ping, embed=embed, view=view,
                           allowed_mentions=discord.AllowedMentions(roles=True))
        await interaction.response.send_message(
            "✅ Заявка отправлена! Ожидай решения — оно придёт в личные сообщения.",
            ephemeral=True)


# ----------------------------------------------------------------------------
#  КНОПКА "Подать заявку"
# ----------------------------------------------------------------------------
class ApplyButton(discord.ui.DynamicItem[discord.ui.Button],
                  template=r"apply:(?P<fam>\w+)"):
    def __init__(self, family_key):
        self.family_key = family_key
        super().__init__(discord.ui.Button(label=BUTTON_LABEL,
                         style=discord.ButtonStyle.danger,
                         custom_id=f"apply:{family_key}"))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["fam"])

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ApplicationModal(self.family_key))


# ----------------------------------------------------------------------------
#  МОДАЛКА ОДОБРЕНИЯ
# ----------------------------------------------------------------------------
class ApprovalModal(discord.ui.Modal):
    def __init__(self, family_key, applicant_id, source_message):
        self.family_key = family_key
        self.applicant_id = applicant_id
        self.source_message = source_message
        super().__init__(title="Принятие кандидата")
        self.discord_id = discord.ui.TextInput(label="Discord ID", max_length=50)
        self.static_id = discord.ui.TextInput(label="Static ID", max_length=50)
        self.full_name = discord.ui.TextInput(label="Имя Фамилия", max_length=60)
        for item in (self.discord_id, self.static_id, self.full_name):
            self.add_item(item)

    async def on_submit(self, interaction: discord.Interaction):
        fam = FAMILIES[self.family_key]
        guild = interaction.guild
        member = guild.get_member(self.applicant_id)
        role = guild.get_role(fam["accepted_role_id"])
        warns = []

        if member and role:
            try:
                await member.add_roles(role, reason=f"Принят в {fam['name']}")
            except discord.Forbidden:
                warns.append("не смог выдать роль (проверь иерархию ролей бота)")
        if member:
            try:
                await member.edit(nick=self.full_name.value, reason="Принят в семью")
            except discord.Forbidden:
                warns.append("не смог сменить ник (нужно право 'Управлять никнеймами' и роль бота выше)")
            try:
                await member.send(ACCEPT_DM.format(name=fam["name"]))
            except discord.Forbidden:
                pass

        try:
            embed = self.source_message.embeds[0]
            embed.title = f"✅ ОДОБРЕНА — {fam['name']}"
            embed.color = 0x2ECC71
            embed.add_field(name="✅ Рассмотрел", value=interaction.user.mention, inline=False)
            embed.add_field(name="🆔 Discord ID", value=self.discord_id.value, inline=True)
            embed.add_field(name="🎫 Static ID", value=self.static_id.value, inline=True)
            embed.add_field(name="📝 Имя Фамилия", value=self.full_name.value, inline=True)
            await self.source_message.edit(embed=embed, view=None)
        except Exception:
            pass

        note = ("\n⚠️ " + "; ".join(warns)) if warns else ""
        await interaction.response.send_message(
            f"Кандидат принят в {fam['name']} ({interaction.user.mention}).{note}",
            ephemeral=True)


# ----------------------------------------------------------------------------
#  МОДАЛКА ОТКАЗА
# ----------------------------------------------------------------------------
class DeclineModal(discord.ui.Modal):
    def __init__(self, family_key, applicant_id, source_message):
        self.family_key = family_key
        self.applicant_id = applicant_id
        self.source_message = source_message
        super().__init__(title="Отказ кандидату")
        self.reason = discord.ui.TextInput(label="Причина отказа",
                                           style=discord.TextStyle.paragraph,
                                           required=False, max_length=300)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        fam = FAMILIES[self.family_key]
        member = interaction.guild.get_member(self.applicant_id)
        if member:
            try:
                await member.send(DECLINE_DM.format(name=fam["name"]))
            except discord.Forbidden:
                pass
        try:
            embed = self.source_message.embeds[0]
            embed.title = f"❌ ОТКЛОНЕНА — {fam['name']}"
            embed.color = 0xE74C3C
            embed.add_field(name="❌ Рассмотрел", value=interaction.user.mention, inline=False)
            embed.add_field(name="Причина", value=self.reason.value or "—", inline=False)
            await self.source_message.edit(embed=embed, view=None)
        except Exception:
            pass
        await interaction.response.send_message(
            f"Заявка отклонена ({interaction.user.mention}).", ephemeral=True)


# ----------------------------------------------------------------------------
#  КНОПКА "Принять"
# ----------------------------------------------------------------------------
class AcceptButton(discord.ui.DynamicItem[discord.ui.Button],
                   template=r"accept:(?P<fam>\w+):(?P<uid>\d+)"):
    def __init__(self, family_key, user_id):
        self.family_key = family_key
        self.user_id = user_id
        super().__init__(discord.ui.Button(label="✅ Принять",
                         style=discord.ButtonStyle.success,
                         custom_id=f"accept:{family_key}:{user_id}"))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["fam"], int(match["uid"]))

    async def callback(self, interaction: discord.Interaction):
        if not member_can_review(interaction.user, self.family_key):
            await interaction.response.send_message(
                "⛔ У тебя нет прав рассматривать эти заявки.", ephemeral=True)
            return
        await interaction.response.send_modal(
            ApprovalModal(self.family_key, self.user_id, interaction.message))


# ----------------------------------------------------------------------------
#  КНОПКА "Позвать на обзвон"
# ----------------------------------------------------------------------------
class CallButton(discord.ui.DynamicItem[discord.ui.Button],
                 template=r"call:(?P<fam>\w+):(?P<uid>\d+)"):
    def __init__(self, family_key, user_id):
        self.family_key = family_key
        self.user_id = user_id
        super().__init__(discord.ui.Button(label="🎙 Позвать на обзвон",
                         style=discord.ButtonStyle.primary,
                         custom_id=f"call:{family_key}:{user_id}"))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["fam"], int(match["uid"]))

    async def callback(self, interaction: discord.Interaction):
        if not member_can_review(interaction.user, self.family_key):
            await interaction.response.send_message(
                "⛔ У тебя нет прав рассматривать эти заявки.", ephemeral=True)
            return

        fam = FAMILIES[self.family_key]
        guild = interaction.guild
        member = guild.get_member(self.user_id)
        voice = guild.get_channel(fam["call_voice_channel_id"])

        if not member:
            await interaction.response.send_message(
                "⚠️ Кандидат не найден на сервере.", ephemeral=True)
            return

        if voice:
            try:
                ow = voice.overwrites_for(member)
                ow.view_channel = True
                ow.connect = True
                await voice.set_permissions(member, overwrite=ow, reason="Вызван на обзвон")
            except discord.Forbidden:
                pass

        link = (f"https://discord.com/channels/{guild.id}/{fam['call_voice_channel_id']}"
                if fam["call_voice_channel_id"] else "(войс не настроен)")
        try:
            await member.send(CALL_DM.format(name=fam["name"], link=link))
        except discord.Forbidden:
            await interaction.response.send_message(
                "⚠️ У кандидата закрыты ЛС — не смог отправить приглашение.", ephemeral=True)
            return

        try:
            embed = interaction.message.embeds[0]
            if embed.color != discord.Color(0xF1C40F):
                embed.color = 0xF1C40F
                embed.title = f"🎙 Вызван на ОБЗВОН — {fam['name']}"
                embed.add_field(name="🎙 Вызвал на обзвон",
                                value=interaction.user.mention, inline=False)
            await interaction.message.edit(embed=embed)
        except Exception:
            pass
        await interaction.response.send_message(
            f"Кандидат вызван на обзвон ({interaction.user.mention}).", ephemeral=True)


# ----------------------------------------------------------------------------
#  КНОПКА "Отказать"
# ----------------------------------------------------------------------------
class DeclineButton(discord.ui.DynamicItem[discord.ui.Button],
                    template=r"decline:(?P<fam>\w+):(?P<uid>\d+)"):
    def __init__(self, family_key, user_id):
        self.family_key = family_key
        self.user_id = user_id
        super().__init__(discord.ui.Button(label="❌ Отказать",
                         style=discord.ButtonStyle.danger,
                         custom_id=f"decline:{family_key}:{user_id}"))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["fam"], int(match["uid"]))

    async def callback(self, interaction: discord.Interaction):
        if not member_can_review(interaction.user, self.family_key):
            await interaction.response.send_message(
                "⛔ У тебя нет прав рассматривать эти заявки.", ephemeral=True)
            return
        await interaction.response.send_modal(
            DeclineModal(self.family_key, self.user_id, interaction.message))


# ----------------------------------------------------------------------------
#  КОМАНДА ПАНЕЛИ
# ----------------------------------------------------------------------------
@bot.tree.command(name="панель", description="Выложить панель заявок (Прохоровы)")
async def panel(interaction: discord.Interaction):
    family_key = "prohorovy"
    if not member_can_panel(interaction.user, family_key):
        await interaction.response.send_message(
            "⛔ У тебя нет прав выкладывать панель (нужна роль главы семьи).", ephemeral=True)
        return
    fam = FAMILIES[family_key]
    embed = discord.Embed(title=fam["panel_title"],
                          description=WELCOME_DESC.format(name=fam["name"]),
                          color=EMBED_COLOR)
    if THUMBNAIL_URL.startswith("http"):
        embed.set_thumbnail(url=THUMBNAIL_URL)
    if BANNER_URL.startswith("http"):
        embed.set_image(url=BANNER_URL)
    view = discord.ui.View(timeout=None)
    view.add_item(ApplyButton(family_key))
    try:
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("Готово ✅", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(
            f"⚠️ Не смог отправить сообщение: {e}\n"
            f"Проверь права бота 'Отправлять сообщения' и 'Встраивать ссылки' в этом канале.",
            ephemeral=True)


@bot.event
async def on_ready():
    print(f"=== ПРОХОРОВЫ BOT v1 === запущен как {bot.user}")


if not TOKEN:
    raise RuntimeError("Не задан TOKEN. Добавь переменную окружения TOKEN на хостинге.")

bot.run(TOKEN)
