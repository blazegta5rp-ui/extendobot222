# -*- coding: utf-8 -*-
# ============================================================================
#  БОТ EXTENDO — ЗАЯВКИ (RP+VZP) + ЭКОНОМИКА + МАГАЗИН  —  discord.py
# ============================================================================

import os
import json
import random
import asyncio
import datetime
import discord
from discord import app_commands
from discord.ext import tasks

# ============================================================================
#  ОБЩИЕ НАСТРОЙКИ
# ============================================================================

TOKEN = os.getenv("TOKEN")
GUILD_ID = 1375220511209947257

BANNER_URL = "https://cdn.discordapp.com/attachments/1495058968278728836/1560280937349120050/image.png?ex=6ad2245c&is=6ad0d2dc&hm=7d8e96c38e56aefb7c24c071717c66a10f2bf2aa3d3f546573a58f6be8fb2ad8&"
THUMBNAIL_URL = "https://cdn.discordapp.com/attachments/1495058968278728836/1560280996270575718/preview.png?ex=6ad2246a&is=6ad0d2ea&hm=4ee66000d92c902d3ec58ddec42c80d59d3b90a06b333b470d1f47839f63ece1&"
EMBED_COLOR = 0xB11226

# ----------------------------------------------------------------------------
#  КОНФИГ СЕМЕЙ (ЗАЯВКИ) — как было
# ----------------------------------------------------------------------------
FAMILIES = {
    "extendo": {
        "name": "EXTENDO",
        "panel_title": "🩸 Вступление в семью EXTENDO",
        "submit_channel_id": 1494355176260112394,
        "logs_channel_id": 1497713478314623077,
        "accepted_role_id": 1533198229158494360,   # academy
        "family_role_id": 1524756881472622674,      # family (выбор кнопкой)
        "recruiter_role_ids": [1524757394955960511, 1513509436600090644,
                               1513294574007615518, 701066783498698813],
        "panel_role_ids": [1513294574007615518],
        "call_voice_channel_id": 1510082641762717696,
    },
    "vzp": {
        "name": "EXTENDO VZP",
        "panel_title": "🩸 Вступление в семью EXTENDO VZP",
        "submit_channel_id": 1513633675277897809,
        "logs_channel_id": 1513633996041355264,
        "accepted_role_id": 1512956758719467591,
        "recruiter_role_ids": [1510102054696259654, 1513510003607212062,
                               701066783498698813],
        "panel_role_ids": [1513510003607212062],
        "call_voice_channel_id": 1510082641762717696,
    },
}

# ============================================================================
#  КОНФИГ ЭКОНОМИКИ / МАГАЗИНА  — ⚠️ ЗАПОЛНИ 0 И [] СВОИМИ ID
# ============================================================================

CURRENCY_NAME = "Extendo Coins"   # игровая валюта
CURRENCY_EMOJI = "🪙"
FOOTER_TEXT = "EXTENDO FAMILY"
COINS_PER_ACCEPT = 10          # коинов рекрутеру за каждого принятого в семью
COINS_PER_VOICE_MINUTE = 1     # коинов за каждую минуту в голосовом

# каналы/роли экономики (0 = не настроено)
TOP_CHANNEL_ID = 1560278779337900164   # топ-10 + розыгрыш
GIVE_LOG_CHANNEL_ID = 1560278970115686401  # лог выдачи монет
GIVE_COIN_ROLE_ID = 1560277765411045518    # Coin Manager
GIVE_COIN_CHANNEL_ID = 1560279074142691449  # канал выдачи
SHOP_PANEL_ROLE_ID = 1560277765411045518    # Coin Manager

TICKET_CATEGORY_ID = 1560278599037358080    # категория тикетов
PURCHASE_NOTIFY_USER_IDS = [279177916686794752, 1096846888537432244]

# розыгрыш — когда проводить (МСК). day: 0=пн … 6=вс
WEEKLY_DAY = 6
WEEKLY_HOUR = 20
LOTTERY_PRIZE = 500            # приз победителю розыгрыша

AFK_CHANNEL_ID = 996802856948617326  # афк-войс (монеты не капают)

# товары магазина — добавляй/меняй как нужно
SHOP_ITEMS = [
    # 🎮 В ИГРЕ (дёшево → дорого)
    {"id": "bag100k",   "cat": "game", "name": "Большая сумка за 100.000$", "price": 40,  "stock": None, "desc": "Вместительная сумка"},
    {"id": "ch100k",    "cat": "game", "name": "100.000$ Chilliad",          "price": 50,  "stock": None, "desc": "Игровая валюта Chilliad"},
    {"id": "role",      "cat": "game", "name": "ЛЮБАЯ кастомная роль",       "price": 100, "stock": None, "desc": "Своя роль с цветом и названием"},
    {"id": "ch250k",    "cat": "game", "name": "250.000 Chilliad",           "price": 125, "stock": None, "desc": "Игровая валюта Chilliad"},
    {"id": "ch500k",    "cat": "game", "name": "500.000 Chilliad",           "price": 250, "stock": None, "desc": "Игровая валюта Chilliad"},
    {"id": "ch1kk",     "cat": "game", "name": "1.000.000$ Chilliad",        "price": 450, "stock": None, "desc": "Игровая валюта Chilliad"},
    # 💵 В ЖИЗНЬ (дёшево → дорого)
    {"id": "rub5000",   "cat": "irl",  "name": "5.000 рублей",               "price": 1000, "stock": None, "desc": "Перевод 5.000 ₽"},
    {"id": "mouse",     "cat": "irl",  "name": "Мышка Lunacy One",           "price": 1000, "stock": 1,    "desc": "Игровая мышь"},
    {"id": "keyboard",  "cat": "irl",  "name": "Клавиатура Aula F75",        "price": 1000, "stock": 1,    "desc": "Механическая клавиатура"},
    {"id": "headset",   "cat": "irl",  "name": "Наушники Logitech G435",     "price": 1000, "stock": 1,    "desc": "Игровая гарнитура"},
    {"id": "monitor",   "cat": "irl",  "name": "Монитор 240hz 2K",           "price": 2000, "stock": 1,    "desc": "Игровой монитор 240 Гц 2K"},
]

ECONOMY_INFO = (
    "💠 **Как заработать {cur}:**\n"
    "┣ 🎙 1 час в войсе (не в муте) — **1** монета\n"
    "┗ 👥 1 принятый рекрутом — **10** монет"
)

MSK = datetime.timezone(datetime.timedelta(hours=3))
DATA_FILE = "data.json"

# --- Вопросы анкеты ---
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
    "Добро пожаловать! Здесь начинается твой путь в семью **{name}**.\n\n"
    "📌 **Как это работает:**\n"
    "▸ Нажми кнопку ниже и честно заполни анкету.\n"
    "▸ Если заявка проходит первичный отбор — тебя вызовут на **обзвон**.\n"
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
#  ХРАНИЛИЩЕ ДАННЫХ (data.json)
#    user -> {balance, accepted, voice_sec, w_accepted, w_voice}
# ============================================================================
_data = {"users": {}, "last_weekly": ""}
_data_lock = asyncio.Lock()
voice_hour_earn = {}  # {uid: коинов за текущий час} — для дайджеста


def load_data():
    global _data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                _data = json.load(f)
        except Exception:
            pass
    _data.setdefault("users", {})
    _data.setdefault("last_weekly", "")
    _data.setdefault("stock", {})
    # инициализация остатков из SHOP_ITEMS (если ещё нет)
    for it in SHOP_ITEMS:
        if it.get("stock") is not None and it["id"] not in _data["stock"]:
            _data["stock"][it["id"]] = it["stock"]


def save_data():
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def u(uid):
    uid = str(uid)
    user = _data["users"].get(uid)
    if user is None:
        user = {"balance": 0, "accepted": 0, "voice_sec": 0,
                "w_accepted": 0, "w_voice": 0}
        _data["users"][uid] = user
    for k in ("balance", "accepted", "voice_sec", "w_accepted", "w_voice"):
        user.setdefault(k, 0)
    return user


def add_balance(uid, amount):
    u(uid)["balance"] += amount
    save_data()


def add_accept(uid):
    user = u(uid)
    user["accepted"] += 1
    user["w_accepted"] += 1
    user["balance"] += COINS_PER_ACCEPT
    save_data()


# ============================================================================
#  КОД БОТА
# ============================================================================
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True


class FamilyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.add_dynamic_items(ApplyButton, AcceptButton, CallButton, DeclineButton)
        self.add_view(ShopView())
        self.add_view(GiveView())
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


def member_can_review(member, family_key):
    return _has_any_role(member, FAMILIES[family_key]["recruiter_role_ids"])


def member_can_panel(member, family_key):
    return _has_any_role(member, FAMILIES[family_key]["panel_role_ids"])


async def log_coins(member, amount, balance, reason):
    if not GIVE_LOG_CHANNEL_ID:
        return
    ch = bot.get_channel(GIVE_LOG_CHANNEL_ID)
    if not ch:
        return
    emb = discord.Embed(color=EMBED_COLOR, timestamp=datetime.datetime.now(MSK))
    emb.description = (f"{member.mention} получил **+{amount} {CURRENCY_EMOJI}**\n"
                      f"💰 Баланс: **{balance:,}".replace(",", " ") + f" {CURRENCY_EMOJI}**\n"
                      f"📌 {reason}")
    emb.set_footer(text=FOOTER_TEXT,
                   icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
    try:
        await ch.send(embed=emb)
    except Exception:
        pass


def fmt_coins(n):
    return f"{n:,}".replace(",", " ") + f" {CURRENCY_EMOJI}"


def item_stock(item):
    if item.get("stock") is None:
        return None  # безлимит
    return _data.get("stock", {}).get(item["id"], item["stock"])


def stock_label(item):
    s = item_stock(item)
    if s is None:
        return "∞"
    return f"{s} шт." if s > 0 else "нет в наличии"


def fmt_voice(sec):
    h = sec // 3600
    m = (sec % 3600) // 60
    return f"{h}ч {m}м"


# ============================================================================
#  ===== БЛОК ЗАЯВОК (как было) =====
# ============================================================================
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
        embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
        if THUMBNAIL_URL.startswith("http"):
            embed.set_thumbnail(url=THUMBNAIL_URL)
        embed.add_field(name=f"👤 {Q1_LABEL}", value=self.a1.value, inline=False)
        embed.add_field(name=f"👪 {Q2_LABEL}", value=self.a2.value, inline=False)
        embed.add_field(name=f"🎮 {Q3_LABEL}", value=self.a3.value, inline=False)
        embed.add_field(name=f"🔫 {Q4_LABEL}", value=self.a4.value, inline=False)
        embed.add_field(name="​", value=f"Кандидат: {interaction.user.mention}", inline=False)
        embed.set_footer(text=f"ID кандидата: {interaction.user.id}")
        view = discord.ui.View(timeout=None)
        view.add_item(AcceptButton(self.family_key, interaction.user.id))
        view.add_item(CallButton(self.family_key, interaction.user.id))
        view.add_item(DeclineButton(self.family_key, interaction.user.id))
        ping = " ".join(f"<@&{rid}>" for rid in fam["recruiter_role_ids"])
        await channel.send(content=ping, embed=embed, view=view,
                           allowed_mentions=discord.AllowedMentions(roles=True))
        await interaction.response.send_message(
            "✅ Заявка отправлена! Ожидай решения — оно придёт в личные сообщения.", ephemeral=True)


class ApplyButton(discord.ui.DynamicItem[discord.ui.Button], template=r"apply:(?P<fam>\w+)"):
    def __init__(self, family_key):
        self.family_key = family_key
        super().__init__(discord.ui.Button(label=BUTTON_LABEL,
                         style=discord.ButtonStyle.danger, custom_id=f"apply:{family_key}"))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["fam"])

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(ApplicationModal(self.family_key))


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
        if fam.get("family_role_id"):
            await interaction.response.send_message(
                "Какую роль выдать кандидату?",
                view=RoleChoiceView(self.family_key, self.applicant_id, self.source_message,
                                    self.discord_id.value, self.static_id.value,
                                    self.full_name.value, interaction.user.id),
                ephemeral=True)
            return
        await finalize_accept(interaction, self.family_key, self.applicant_id,
                              self.source_message, self.discord_id.value, self.static_id.value,
                              self.full_name.value, fam["accepted_role_id"], interaction.user)


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


async def finalize_accept(interaction, family_key, applicant_id, source_message,
                          discord_id, static_id, full_name, role_id, reviewer):
    fam = FAMILIES[family_key]
    guild = interaction.guild
    member = guild.get_member(applicant_id)
    role = guild.get_role(role_id)
    warns = []
    if member and role:
        try:
            await member.add_roles(role, reason=f"Принят в {fam['name']}")
        except discord.Forbidden:
            warns.append("не смог выдать роль (проверь иерархию ролей бота)")
    if member:
        try:
            await member.edit(nick=full_name, reason="Принят в семью")
        except discord.Forbidden:
            warns.append("не смог сменить ник (нужно право 'Управлять никнеймами')")
        try:
            await member.send(ACCEPT_DM.format(name=fam["name"]))
        except discord.Forbidden:
            pass

    # === ЭКОНОМИКА: рекрутер получает монеты + счётчик принятых ===
    add_accept(reviewer.id)
    await log_coins(reviewer, COINS_PER_ACCEPT, u(reviewer.id)["balance"],
                    f"Принят игрок в {fam['name']}")

    role_name = role.name if role else "—"
    try:
        embed = source_message.embeds[0]
        embed.title = f"✅ ОДОБРЕНА — {fam['name']}"
        embed.color = 0x2ECC71
        embed.add_field(name="✅ Рассмотрел", value=reviewer.mention, inline=False)
        embed.add_field(name="🎖 Выдана роль", value=role_name, inline=False)
        embed.add_field(name="🆔 Discord ID", value=discord_id, inline=True)
        embed.add_field(name="🎫 Static ID", value=static_id, inline=True)
        embed.add_field(name="📝 Имя Фамилия", value=full_name, inline=True)
        await source_message.edit(embed=embed, view=None)
    except Exception:
        pass

    note = ("\n⚠️ " + "; ".join(warns)) if warns else ""
    msg = (f"Кандидат принят в {fam['name']}, выдана роль **{role_name}**. "
           f"Тебе начислено {fmt_coins(COINS_PER_ACCEPT)}.{note}")
    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        pass


class RoleChoiceView(discord.ui.View):
    def __init__(self, family_key, applicant_id, source_message,
                 discord_id, static_id, full_name, reviewer_id):
        super().__init__(timeout=300)
        self.family_key = family_key
        self.applicant_id = applicant_id
        self.source_message = source_message
        self.discord_id = discord_id
        self.static_id = static_id
        self.full_name = full_name
        self.reviewer_id = reviewer_id

    async def _finish(self, interaction, role_id):
        await finalize_accept(interaction, self.family_key, self.applicant_id,
                              self.source_message, self.discord_id, self.static_id,
                              self.full_name, role_id, interaction.user)
        for child in self.children:
            child.disabled = True
        try:
            await interaction.edit_original_response(view=self)
        except Exception:
            pass

    @discord.ui.button(label="🎓 Academy", style=discord.ButtonStyle.primary)
    async def academy(self, interaction, button):
        await self._finish(interaction, FAMILIES[self.family_key]["accepted_role_id"])

    @discord.ui.button(label="👑 Family", style=discord.ButtonStyle.success)
    async def family(self, interaction, button):
        await self._finish(interaction, FAMILIES[self.family_key]["family_role_id"])


class AcceptButton(discord.ui.DynamicItem[discord.ui.Button],
                   template=r"accept:(?P<fam>\w+):(?P<uid>\d+)"):
    def __init__(self, family_key, user_id):
        self.family_key = family_key
        self.user_id = user_id
        super().__init__(discord.ui.Button(label="✅ Принять", style=discord.ButtonStyle.success,
                         custom_id=f"accept:{family_key}:{user_id}"))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["fam"], int(match["uid"]))

    async def callback(self, interaction: discord.Interaction):
        if not member_can_review(interaction.user, self.family_key):
            await interaction.response.send_message("⛔ У тебя нет прав рассматривать эти заявки.", ephemeral=True)
            return
        await interaction.response.send_modal(
            ApprovalModal(self.family_key, self.user_id, interaction.message))


class CallButton(discord.ui.DynamicItem[discord.ui.Button],
                 template=r"call:(?P<fam>\w+):(?P<uid>\d+)"):
    def __init__(self, family_key, user_id):
        self.family_key = family_key
        self.user_id = user_id
        super().__init__(discord.ui.Button(label="🎙 Позвать на обзвон", style=discord.ButtonStyle.primary,
                         custom_id=f"call:{family_key}:{user_id}"))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["fam"], int(match["uid"]))

    async def callback(self, interaction: discord.Interaction):
        if not member_can_review(interaction.user, self.family_key):
            await interaction.response.send_message("⛔ У тебя нет прав рассматривать эти заявки.", ephemeral=True)
            return
        fam = FAMILIES[self.family_key]
        guild = interaction.guild
        member = guild.get_member(self.user_id)
        voice = guild.get_channel(fam["call_voice_channel_id"])
        if not member:
            await interaction.response.send_message("⚠️ Кандидат не найден на сервере.", ephemeral=True)
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
            await interaction.response.send_message("⚠️ У кандидата закрыты ЛС.", ephemeral=True)
            return
        try:
            embed = interaction.message.embeds[0]
            if embed.color != discord.Color(0xF1C40F):
                embed.color = 0xF1C40F
                embed.title = f"🎙 Вызван на ОБЗВОН — {fam['name']}"
                embed.add_field(name="🎙 Вызвал на обзвон", value=interaction.user.mention, inline=False)
            await interaction.message.edit(embed=embed)
        except Exception:
            pass
        await interaction.response.send_message(
            f"Кандидат вызван на обзвон ({interaction.user.mention}).", ephemeral=True)


class DeclineButton(discord.ui.DynamicItem[discord.ui.Button],
                    template=r"decline:(?P<fam>\w+):(?P<uid>\d+)"):
    def __init__(self, family_key, user_id):
        self.family_key = family_key
        self.user_id = user_id
        super().__init__(discord.ui.Button(label="❌ Отказать", style=discord.ButtonStyle.danger,
                         custom_id=f"decline:{family_key}:{user_id}"))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["fam"], int(match["uid"]))

    async def callback(self, interaction: discord.Interaction):
        if not member_can_review(interaction.user, self.family_key):
            await interaction.response.send_message("⛔ У тебя нет прав рассматривать эти заявки.", ephemeral=True)
            return
        await interaction.response.send_modal(
            DeclineModal(self.family_key, self.user_id, interaction.message))


async def post_panel(interaction, family_key):
    if not member_can_panel(interaction.user, family_key):
        await interaction.response.send_message("⛔ У тебя нет прав выкладывать эту панель.", ephemeral=True)
        return
    fam = FAMILIES[family_key]
    embed = discord.Embed(title=fam["panel_title"],
                          description=WELCOME_DESC.format(name=fam["name"]), color=EMBED_COLOR)
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
            f"⚠️ Не смог отправить сообщение: {e}", ephemeral=True)


@bot.tree.command(name="панель", description="Выложить панель заявок EXTENDO")
async def panel_extendo(interaction):
    await post_panel(interaction, "extendo")


@bot.tree.command(name="панель_vzp", description="Выложить панель заявок EXTENDO VZP")
async def panel_vzp(interaction):
    await post_panel(interaction, "vzp")


# ============================================================================
#  ===== ЭКОНОМИКА: ВОЙСЫ =====
# ============================================================================
@tasks.loop(minutes=1)
async def voice_earn_loop():
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            if AFK_CHANNEL_ID and vc.id == AFK_CHANNEL_ID:
                continue
            for member in vc.members:
                if member.bot:
                    continue
                vs = member.voice
                if vs and (vs.self_mute or vs.mute) and (vs.self_deaf or vs.deaf):
                    continue  # полностью заглушен — не капает
                user = u(member.id)
                user["voice_sec"] += 60
                user["w_voice"] += 60
                user["balance"] += COINS_PER_VOICE_MINUTE
                voice_hour_earn[member.id] = voice_hour_earn.get(member.id, 0) + COINS_PER_VOICE_MINUTE
    save_data()


@voice_earn_loop.before_loop
async def _before_voice():
    await bot.wait_until_ready()


# ============================================================================
#  ===== ЭКОНОМИКА: БАЛАНС / ВЫДАЧА =====
# ============================================================================
@bot.tree.command(name="баланс", description="Показать свой баланс и статистику")
async def balance_cmd(interaction):
    user = u(interaction.user.id)
    embed = discord.Embed(title="🪙  ТВОЙ БАЛАНС", color=EMBED_COLOR)
    if THUMBNAIL_URL.startswith("http"):
        embed.set_thumbnail(url=THUMBNAIL_URL)
    embed.add_field(name="💰 Монеты", value=f"**{fmt_coins(user['balance'])}**", inline=False)
    embed.add_field(name="👥 Принято людей", value=f"**{user['accepted']}**", inline=True)
    embed.add_field(name="🎙 Время в войсах", value=f"**{fmt_voice(user['voice_sec'])}**", inline=True)
    embed.set_footer(text=FOOTER_TEXT,
                     icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="выдать", description="Выдать монеты участнику (с причиной)")
@app_commands.describe(участник="Кому выдать", сумма="Сколько монет", причина="Обязательная причина")
async def give_cmd(interaction: discord.Interaction, участник: discord.Member,
                   сумма: int, причина: str):
    # право
    if GIVE_COIN_ROLE_ID and not _has_any_role(interaction.user, [GIVE_COIN_ROLE_ID]):
        await interaction.response.send_message("⛔ У тебя нет прав выдавать монеты.", ephemeral=True)
        return
    # канал
    if GIVE_COIN_CHANNEL_ID and interaction.channel_id != GIVE_COIN_CHANNEL_ID:
        await interaction.response.send_message(
            f"⛔ Эта команда работает только в <#{GIVE_COIN_CHANNEL_ID}>.", ephemeral=True)
        return
    if сумма == 0:
        await interaction.response.send_message("Сумма не может быть 0.", ephemeral=True)
        return
    add_balance(участник.id, сумма)
    await interaction.response.send_message(
        f"✅ Выдано {fmt_coins(сумма)} → {участник.mention}\nПричина: {причина}", ephemeral=True)
    # лог
    if GIVE_LOG_CHANNEL_ID:
        ch = bot.get_channel(GIVE_LOG_CHANNEL_ID)
        if ch:
            emb = discord.Embed(title="🪙 Выдача монет", color=EMBED_COLOR,
                                timestamp=datetime.datetime.now(MSK))
            emb.add_field(name="Кому", value=участник.mention, inline=True)
            emb.add_field(name="Сумма", value=fmt_coins(сумма), inline=True)
            emb.add_field(name="Выдал", value=interaction.user.mention, inline=True)
            emb.add_field(name="Причина", value=причина, inline=False)
            emb.add_field(name="Баланс теперь", value=fmt_coins(u(участник.id)["balance"]), inline=False)
            try:
                await ch.send(embed=emb)
            except Exception:
                pass


# ============================================================================
#  ===== ТОП-10 =====
# ============================================================================
def build_top_embed(weekly=False):
    users = _data["users"]
    acc_key = "w_accepted" if weekly else "accepted"
    voice_key = "w_voice" if weekly else "voice_sec"
    top_acc = sorted(users.items(), key=lambda kv: kv[1].get(acc_key, 0), reverse=True)
    top_voice = sorted(users.items(), key=lambda kv: kv[1].get(voice_key, 0), reverse=True)
    title = "🏆 ТОП НЕДЕЛИ" if weekly else "🏆 ТОП ВСЁ ВРЕМЯ"
    embed = discord.Embed(title=title, color=EMBED_COLOR, timestamp=datetime.datetime.now(MSK))
    medals = ["🥇", "🥈", "🥉"] + ["🔹"] * 7
    acc_lines = []
    for i, (uid, d) in enumerate(top_acc[:10]):
        v = d.get(acc_key, 0)
        if v <= 0:
            break
        acc_lines.append(f"{medals[i]} <@{uid}> — **{v}**")
    voice_lines = []
    for i, (uid, d) in enumerate(top_voice[:10]):
        v = d.get(voice_key, 0)
        if v <= 0:
            break
        voice_lines.append(f"{medals[i]} <@{uid}> — **{fmt_voice(v)}**")
    embed.add_field(name="👥  ТОП ПО ПРИНЯТЫМ ЗАЯВКАМ", value="\n".join(acc_lines) or "—", inline=False)
    embed.add_field(name="\u200b", value="\u200b", inline=False)
    embed.add_field(name="🎙  ТОП ПО ВРЕМЕНИ В ВОЙСАХ", value="\n".join(voice_lines) or "—", inline=False)
    if THUMBNAIL_URL.startswith("http"):
        embed.set_thumbnail(url=THUMBNAIL_URL)
    if BANNER_URL.startswith("http"):
        embed.set_image(url=BANNER_URL)
    embed.set_footer(text=FOOTER_TEXT,
                     icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
    return embed


@bot.tree.command(name="топ", description="Показать топ-10 (всё время)")
async def top_cmd(interaction):
    await interaction.response.send_message(embed=build_top_embed(weekly=False))


# ============================================================================
#  ===== ЕЖЕНЕДЕЛЬНЫЙ РОЗЫГРЫШ + ТОП =====
# ============================================================================
@tasks.loop(minutes=30)
async def weekly_loop():
    now = datetime.datetime.now(MSK)
    if now.weekday() != WEEKLY_DAY or now.hour != WEEKLY_HOUR:
        return
    stamp = now.strftime("%Y-%W")
    if _data.get("last_weekly") == stamp:
        return  # уже проводили на этой неделе
    _data["last_weekly"] = stamp

    ch = bot.get_channel(TOP_CHANNEL_ID) if TOP_CHANNEL_ID else None
    if ch:
        try:
            await ch.send(embed=build_top_embed(weekly=True))
        except Exception:
            pass
        # розыгрыш среди активных за неделю
        pool = [uid for uid, d in _data["users"].items()
                if d.get("w_voice", 0) > 0 or d.get("w_accepted", 0) > 0]
        if pool:
            winner = random.choice(pool)
            add_balance(winner, LOTTERY_PRIZE)
            emb = discord.Embed(title="🎰 Еженедельный розыгрыш",
                                description=f"Победитель: <@{winner}>\nПриз: {fmt_coins(LOTTERY_PRIZE)}",
                                color=0xF1C40F)
            try:
                await ch.send(content=f"<@{winner}>", embed=emb,
                              allowed_mentions=discord.AllowedMentions(users=True))
            except Exception:
                pass
    # сброс недельных счётчиков
    for d in _data["users"].values():
        d["w_accepted"] = 0
        d["w_voice"] = 0
    save_data()


@weekly_loop.before_loop
async def _before_weekly():
    await bot.wait_until_ready()


@tasks.loop(hours=24)
async def voice_digest_loop():
    if not GIVE_LOG_CHANNEL_ID or not voice_hour_earn:
        return
    ch = bot.get_channel(GIVE_LOG_CHANNEL_ID)
    if not ch:
        voice_hour_earn.clear()
        return
    rows = sorted(voice_hour_earn.items(), key=lambda kv: kv[1], reverse=True)
    lines = [f"<@{uid}> — +{fmt_coins(c)} · баланс {fmt_coins(u(uid)['balance'])}" for uid, c in rows[:25]]
    emb = discord.Embed(title="🎙 Начисления за войсы (за сутки)", color=EMBED_COLOR,
                        description="\n".join(lines),
                        timestamp=datetime.datetime.now(MSK))
    emb.set_footer(text=FOOTER_TEXT, icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
    try:
        await ch.send(embed=emb)
    except Exception:
        pass
    voice_hour_earn.clear()


@voice_digest_loop.before_loop
async def _before_digest():
    await bot.wait_until_ready()


# ============================================================================
#  ===== МАГАЗИН =====
# ============================================================================
def shop_embed():
    embed = discord.Embed(
        title="🛒  МАГАЗИН  ·  EXTENDO FAMILY",
        color=EMBED_COLOR,
        description=(
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Валюта: **{CURRENCY_NAME}** {CURRENCY_EMOJI}  ·  Нажми **🛒 Купить**\n"
            + ECONOMY_INFO.format(cur=CURRENCY_NAME) + "\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        ))
    if THUMBNAIL_URL.startswith("http"):
        embed.set_thumbnail(url=THUMBNAIL_URL)
    if BANNER_URL.startswith("http"):
        embed.set_image(url=BANNER_URL)

    cats = [("game", "🎮  В ИГРЕ"), ("irl", "💵  В ЖИЗНЬ")]
    for cat_key, cat_title in cats:
        lines = []
        for it in SHOP_ITEMS:
            if it["cat"] != cat_key:
                continue
            lines.append(f"**{it['name']}**\n╰ 💰 `{it['price']} {CURRENCY_NAME}`  ·  📦 {stock_label(it)}")
        if lines:
            embed.add_field(name=f"▰▰▰  {cat_title}  ▰▰▰",
                            value="\n\n".join(lines), inline=False)
    embed.set_footer(text=FOOTER_TEXT,
                     icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
    return embed


class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🛒 Купить", style=discord.ButtonStyle.success, custom_id="shop_buy")
    async def buy(self, interaction, button):
        await interaction.response.send_message(
            "Выбери товар:", view=BuySelectView(), ephemeral=True)

    @discord.ui.button(label="🪙 Мой баланс", style=discord.ButtonStyle.secondary, custom_id="shop_balance")
    async def balance(self, interaction, button):
        user = u(interaction.user.id)
        await interaction.response.send_message(
            f"🪙 Твой баланс: **{fmt_coins(user['balance'])}**", ephemeral=True)


class BuySelect(discord.ui.Select):
    def __init__(self):
        options = []
        for it in SHOP_ITEMS:
            emoji = "🎮" if it["cat"] == "game" else "💵"
            options.append(discord.SelectOption(
                label=f"{it['name']} — {it['price']} {CURRENCY_NAME}"[:100],
                description=f"📦 {stock_label(it)}",
                value=it["id"], emoji=emoji))
        super().__init__(placeholder="Выбери товар…", options=options[:25])

    async def callback(self, interaction: discord.Interaction):
        item = next((i for i in SHOP_ITEMS if i["id"] == self.values[0]), None)
        if not item:
            await interaction.response.send_message("Товар не найден.", ephemeral=True)
            return
        # проверка остатка
        stock = item_stock(item)
        if stock is not None and stock <= 0:
            await interaction.response.send_message(
                f"❌ **{item['name']}** закончился (нет в наличии).", ephemeral=True)
            return
        user = u(interaction.user.id)
        if user["balance"] < item["price"]:
            await interaction.response.send_message(
                f"❌ Недостаточно монет.\nНужно {fmt_coins(item['price'])}, "
                f"у тебя {fmt_coins(user['balance'])}.", ephemeral=True)
            return
        # списываем баланс + склад
        user["balance"] -= item["price"]
        if stock is not None:
            _data["stock"][item["id"]] = stock - 1
        save_data()
        # создаём тикет
        ticket = await create_purchase_ticket(interaction, item)
        link = ticket.mention if ticket else "(тикет не создан — проверь категорию)"
        await interaction.response.send_message(
            f"✅ Покупка оформлена!\n"
            f"🛒 **{item['name']}** за {fmt_coins(item['price'])}\n"
            f"💰 Остаток баланса: {fmt_coins(user['balance'])}\n"
            f"🧾 Тикет: {link}", ephemeral=True)
        await notify_purchase(interaction, item, ticket)


class BuySelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(BuySelect())


async def create_purchase_ticket(interaction, item):
    guild = interaction.guild
    category = guild.get_channel(TICKET_CATEGORY_ID) if TICKET_CATEGORY_ID else None
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
    }
    for uid in PURCHASE_NOTIFY_USER_IDS:
        m = guild.get_member(uid)
        if m:
            overwrites[m] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
    try:
        ch = await guild.create_text_channel(
            name=f"покупка-{interaction.user.name}"[:90],
            category=category, overwrites=overwrites,
            reason=f"Покупка {item['name']}")
    except Exception:
        return None
    emb = discord.Embed(title="🧾 Новая покупка", color=EMBED_COLOR,
                        timestamp=datetime.datetime.now(MSK))
    emb.add_field(name="Покупатель", value=interaction.user.mention, inline=True)
    emb.add_field(name="Товар", value=item["name"], inline=True)
    emb.add_field(name="Цена", value=fmt_coins(item["price"]), inline=True)
    emb.set_footer(text=f"ID: {interaction.user.id}")
    ping = " ".join(f"<@{uid}>" for uid in PURCHASE_NOTIFY_USER_IDS)
    try:
        await ch.send(content=f"{interaction.user.mention} {ping}", embed=emb,
                      allowed_mentions=discord.AllowedMentions(users=True))
    except Exception:
        pass
    return ch


async def notify_purchase(interaction, item, ticket):
    link = (f"https://discord.com/channels/{interaction.guild.id}/{ticket.id}"
            if ticket else "тикет не создан")
    for uid in PURCHASE_NOTIFY_USER_IDS:
        m = interaction.guild.get_member(uid)
        if not m:
            continue
        try:
            await m.send(
                f"🧾 **Новая покупка!**\n"
                f"Покупатель: {interaction.user.mention} (`{interaction.user.id}`)\n"
                f"Товар: **{item['name']}** — {fmt_coins(item['price'])}\n"
                f"Тикет: {link}")
        except discord.Forbidden:
            pass


# ============================================================================
#  ===== ПАНЕЛЬ ВЫДАЧИ МОНЕТ (кнопки) =====
# ============================================================================
def resolve_member(guild, raw):
    raw = raw.strip().replace("<@", "").replace("!", "").replace(">", "")
    if raw.isdigit():
        return guild.get_member(int(raw))
    return None


class GiveModal(discord.ui.Modal):
    def __init__(self, mode):
        self.mode = mode  # "add" / "take"
        title = "Выдать монеты" if mode == "add" else "Забрать монеты"
        super().__init__(title=title)
        self.target = discord.ui.TextInput(
            label="Кому (ID или @упоминание)", placeholder="например: 123456789 или @ник",
            max_length=60)
        self.amount = discord.ui.TextInput(label="Сколько монет", placeholder="например: 500", max_length=12)
        self.reason = discord.ui.TextInput(label="Причина", style=discord.TextStyle.paragraph, max_length=300)
        for it in (self.target, self.amount, self.reason):
            self.add_item(it)

    async def on_submit(self, interaction: discord.Interaction):
        member = resolve_member(interaction.guild, self.target.value)
        if not member:
            await interaction.response.send_message(
                "⚠️ Участник не найден. Укажи ID или @упоминание.", ephemeral=True)
            return
        try:
            amount = int(self.amount.value.strip().replace(" ", ""))
        except ValueError:
            await interaction.response.send_message("⚠️ Сумма должна быть числом.", ephemeral=True)
            return
        if amount <= 0:
            await interaction.response.send_message("⚠️ Сумма должна быть больше 0.", ephemeral=True)
            return

        delta = amount if self.mode == "add" else -amount
        add_balance(member.id, delta)
        new_bal = u(member.id)["balance"]
        sign = "➕ Выдано" if self.mode == "add" else "➖ Забрано"

        await interaction.response.send_message(
            f"✅ {sign} **{fmt_coins(amount)}** → {member.mention}\n"
            f"💰 Баланс теперь: {fmt_coins(new_bal)}\n📌 {self.reason.value}", ephemeral=True)

        # лог
        if GIVE_LOG_CHANNEL_ID:
            ch = bot.get_channel(GIVE_LOG_CHANNEL_ID)
            if ch:
                color = 0x2ECC71 if self.mode == "add" else 0xE74C3C
                emb = discord.Embed(title=f"{sign} монеты", color=color,
                                    timestamp=datetime.datetime.now(MSK))
                if THUMBNAIL_URL.startswith("http"):
                    emb.set_thumbnail(url=THUMBNAIL_URL)
                emb.add_field(name="Кому", value=member.mention, inline=True)
                emb.add_field(name="Сумма", value=fmt_coins(amount), inline=True)
                emb.add_field(name="Кто", value=interaction.user.mention, inline=True)
                emb.add_field(name="Причина", value=self.reason.value, inline=False)
                emb.add_field(name="Баланс теперь", value=fmt_coins(new_bal), inline=False)
                emb.set_footer(text=FOOTER_TEXT,
                               icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
                try:
                    await ch.send(embed=emb)
                except Exception:
                    pass


class GiveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    def _can(self, member):
        return (member.id == member.guild.owner_id
                or (GIVE_COIN_ROLE_ID and _has_any_role(member, [GIVE_COIN_ROLE_ID])))

    @discord.ui.button(label="➕ Выдать монеты", style=discord.ButtonStyle.success, custom_id="give_add")
    async def add(self, interaction, button):
        if not self._can(interaction.user):
            await interaction.response.send_message("⛔ Нет прав.", ephemeral=True)
            return
        await interaction.response.send_modal(GiveModal("add"))

    @discord.ui.button(label="➖ Забрать монеты", style=discord.ButtonStyle.danger, custom_id="give_take")
    async def take(self, interaction, button):
        if not self._can(interaction.user):
            await interaction.response.send_message("⛔ Нет прав.", ephemeral=True)
            return
        await interaction.response.send_modal(GiveModal("take"))


def give_embed():
    embed = discord.Embed(
        title="💸  ВЫДАЧА МОНЕТ  ·  EXTENDO FAMILY",
        color=EMBED_COLOR,
        description=(
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Панель управления балансами игроков.\n\n"
            "➕ **Выдать монеты** — начислить участнику\n"
            "➖ **Забрать монеты** — снять с участника\n\n"
            "⚠️ Причина указывается **обязательно** — всё пишется в логи.\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        ))
    if THUMBNAIL_URL.startswith("http"):
        embed.set_thumbnail(url=THUMBNAIL_URL)
    if BANNER_URL.startswith("http"):
        embed.set_image(url=BANNER_URL)
    embed.set_footer(text=FOOTER_TEXT,
                     icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
    return embed


@bot.tree.command(name="панель_выдача", description="Выложить панель выдачи монет")
async def give_panel_cmd(interaction: discord.Interaction):
    can = (interaction.user.id == interaction.guild.owner_id
           or (GIVE_COIN_ROLE_ID and _has_any_role(interaction.user, [GIVE_COIN_ROLE_ID])))
    if not can:
        await interaction.response.send_message("⛔ Нет прав выкладывать панель выдачи.", ephemeral=True)
        return
    try:
        await interaction.channel.send(embed=give_embed(), view=GiveView())
        await interaction.response.send_message("Готово ✅", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Ошибка: {e}", ephemeral=True)


@bot.tree.command(name="магазин", description="Выложить магазин в этот канал")
async def shop_cmd(interaction: discord.Interaction):
    can = (interaction.user.id == interaction.guild.owner_id
           or (SHOP_PANEL_ROLE_ID and _has_any_role(interaction.user, [SHOP_PANEL_ROLE_ID])))
    if not can:
        await interaction.response.send_message("⛔ Нет прав выкладывать магазин.", ephemeral=True)
        return
    try:
        await interaction.channel.send(embed=shop_embed(), view=ShopView())
        await interaction.response.send_message("Готово ✅", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Ошибка: {e}", ephemeral=True)


# ============================================================================
#  ЗАПУСК
# ============================================================================
@bot.event
async def on_ready():
    if not voice_earn_loop.is_running():
        voice_earn_loop.start()
    if not weekly_loop.is_running():
        weekly_loop.start()
    if not voice_digest_loop.is_running():
        voice_digest_loop.start()
    print(f"=== EXTENDO BOT v14 (панель выдачи) === запущен как {bot.user}")


load_data()

if not TOKEN:
    raise RuntimeError("Не задан TOKEN. Добавь переменную окружения TOKEN на хостинге.")

bot.run(TOKEN)
