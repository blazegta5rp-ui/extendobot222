# -*- coding: utf-8 -*-
# ============================================================================
#  БОТ EXTENDO — ЗАЯВКИ (RP+VZP) + ЭКОНОМИКА + МАГАЗИН  —  discord.py
# ============================================================================

import os
import io
import json
import random
import asyncio
import datetime
import aiohttp
import discord
from discord import app_commands
from discord.ext import tasks

# ============================================================================
#  ОБЩИЕ НАСТРОЙКИ
# ============================================================================

TOKEN = os.getenv("TOKEN")
GUILD_ID = 1375220511209947257

BANNER_URL = "https://cdn.discordapp.com/attachments/1562900235313750248/1564779291412271234/21312312312.gif?ex=6ae281c7&is=6ae13047&hm=2c833bd3ef91384f439f9409a5ee49a8ea95f9b467800991a6ea15703751dd4f&"
THUMBNAIL_URL = "https://cdn.discordapp.com/attachments/1562900235313750248/1564779291412271234/21312312312.gif?ex=6ae281c7&is=6ae13047&hm=2c833bd3ef91384f439f9409a5ee49a8ea95f9b467800991a6ea15703751dd4f&"
EMBED_COLOR = 0xB11226

# ----------------------------------------------------------------------------
#  КОНФИГ СЕМЕЙ (ЗАЯВКИ) — как было
# ----------------------------------------------------------------------------
FAMILIES = {
    "extendo": {  # Chilliad RP
        "name": "EXTENDO CHILLIAD",
        "panel_title": "🩸 Вступление в семью EXTENDO CHILLIAD",
        "submit_channel_id": 1494355176260112394,
        "logs_channel_id": 1497713478314623077,
        "accepted_role_id": 1533198229158494360,       # Academy (общая)
        "family_role_id": 1524756881472622674,          # Extendo Family Chilliad
        "recruiter_role_ids": [1524757394955960511, 1513509436600090644,
                               1513294574007615518, 701066783498698813],
        "panel_role_ids": [1513294574007615518],        # Head Recruitment Chilliad
        "call_voice_channel_id": 1510082641762717696,
    },
    "vzp": {  # Chilliad VZP
        "name": "EXTENDO CHILLIAD VZP",
        "panel_title": "🩸 Вступление в семью EXTENDO CHILLIAD VZP",
        "submit_channel_id": 1513633675277897809,
        "logs_channel_id": 1513633996041355264,
        "accepted_role_id": 1512956758719467591,        # VZP (общая)
        "recruiter_role_ids": [1510102054696259654, 1513510003607212062,
                               701066783498698813],
        "panel_role_ids": [1513510003607212062],        # Head VZP Chilliad
        "call_voice_channel_id": 1510082641762717696,
    },
    "blaine": {  # Blaine RP
        "name": "EXTENDO BLAINE",
        "panel_title": "🩸 Вступление в семью EXTENDO BLAINE",
        "submit_channel_id": 1562894004712906823,
        "logs_channel_id": 0,                           # создаётся /setup_blaine -> cfg
        "logs_cfg_key": "blaine_rp_logs",
        "accepted_role_id": 1533198229158494360,        # Academy (общая)
        "family_role_id": 1562892249883345026,          # Extendo Family Blaine
        "recruiter_role_ids": [1562892139212439708, 1513509436600090644,
                               1562891847234359507, 1562892051866198177],
        "panel_role_ids": [1562891847234359507],        # Head Recruitment Blaine
        "call_voice_channel_id": 1510082641762717696,
    },
    "blaine_vzp": {  # Blaine VZP
        "name": "EXTENDO BLAINE VZP",
        "panel_title": "🩸 Вступление в семью EXTENDO BLAINE VZP",
        "submit_channel_id": 1562893949566193664,
        "logs_channel_id": 0,
        "logs_cfg_key": "blaine_vzp_logs",
        "accepted_role_id": 1512956758719467591,        # запасной (до /setup_vzp_blaine)
        "accepted_cfg_key": "vzp_blaine_role",          # роль VZP Blaine (создаётся командой)
        "recruiter_role_ids": [1510102054696259654, 1562891933561397258,
                               1562892051866198177],
        "panel_role_ids": [1562891933561397258],        # Head VZP Blaine
        "call_voice_channel_id": 1510082641762717696,
    },
}

# ============================================================================
#  КОНФИГ ЭКОНОМИКИ / МАГАЗИНА  — ⚠️ ЗАПОЛНИ 0 И [] СВОИМИ ID
# ============================================================================

CURRENCY_NAME = "Extendo Coins"   # игровая валюта
CURRENCY_EMOJI = "🪙"
FOOTER_TEXT = "EXTENDO FAMILY"
COINS_PER_ACCEPT = 10          # монет рекрутеру за принятого (базово)
COINS_PER_HOUR = 1             # монета за ПОЛНЫЙ час в войсе (базово)
NIGHT_MULTIPLIER = 1.3         # ночной бонус ×1.3
NIGHT_FROM = 0                 # ночь с 00:00 МСК
NIGHT_TO = 10                  # ночь до 10:00 МСК

# каналы/роли экономики (0 = не настроено)
TOP_CHANNEL_ID = 1560278779337900164   # топ-10 + розыгрыш
GIVE_LOG_CHANNEL_ID = 1560278970115686401  # лог выдачи монет
GIVE_COIN_ROLE_ID = 1560277765411045518    # Coin Manager

# --- Персонал (кто может варнить / смотреть историю) ---
STAFF_ROLE_IDS = [
    701066421240856626,    # Owner
    1560277765411045518,   # Coin Manager
    996791697193308302, 1562891371101032528,   # Dep.Owner Chilliad/Blaine
    1513294574007615518, 1562891847234359507,   # Head Recruitment Chilliad/Blaine
    1513510003607212062, 1562891933561397258,   # Head VZP Chilliad/Blaine
    701066783498698813, 1562892051866198177,    # Extendo Main Chilliad/Blaine
]
# --- Ник не по форме ---
NICKFORM_DAY = 0          # день недели проверки (0=пн)
NICKFORM_HOUR = 12        # час МСК
# роль/канал создаются автоматически, ID сохраняются в cfg
import re as _re
NICKFORM_REGEX = _re.compile(r"^[A-Za-zА-Яа-яЁё]{2,} [A-Za-zА-Яа-яЁё]{2,}")  # "Имя Фамилия"
GIVE_COIN_CHANNEL_ID = 1560279074142691449  # канал выдачи
SHOP_PANEL_ROLE_ID = 1560277765411045518    # Coin Manager

TICKET_CATEGORY_ID = 1560278599037358080    # категория тикетов
PURCHASE_NOTIFY_USER_IDS = [279177916686794752, 1096846888537432244]

# розыгрыш — когда проводить (МСК). day: 0=пн … 6=вс
WEEKLY_DAY = 6
WEEKLY_HOUR = 20
LOTTERY_PRIZE = 500            # приз победителю розыгрыша

AFK_CHANNEL_ID = 996802856948617326  # афк-войс (монеты не капают)

# ===== НОВЫЕ ФИЧИ — ⚠️ ЗАПОЛНИ 0 СВОИМИ ID =====
WELCOME_CHANNEL_ID = 0              # 🔴 канал приветствия новичков (welcome-картинка)

NICKFORM_ROLE_ID = 0               # 🔴 роль "Ник не по форме"
NICKFORM_REMIND_CHANNEL_ID = 0     # 🔴 канал, где раз в неделю тегать нарушителей
NICKFORM_REGEX = r"^[A-Za-zА-Яа-яЁё]+ [A-Za-zА-Яа-яЁё]+$"   # шаблон: Имя Фамилия
NICKFORM_DAY = 0                   # день недели проверки (0=пн … 6=вс)
NICKFORM_HOUR = 12                 # час проверки (МСК)

HONOR_CHANNEL_ID = 0               # 🔴 канал доски почёта (0 = топ-канал)
HONOR_HOUR = 12                    # час поста доски почёта (1-го числа месяца)

BACKUP_CHANNEL_ID = 1564974384446447767  # канал 🗄・логи-бэкап (вшит — авто-восстановление после пересборки)
WAR_STATS_CHILLIAD_ID = 0         # 🔴 канал статистики войн Chilliad
WAR_STATS_BLAINE_ID = 0           # 🔴 канал статистики войн Blaine
WAR_API_URL = "https://vzp-gta5rp.com/api/events?limit=50&offset=0"  # API войн
WAR_FAMILY_NAME = "extendo"        # как нас ищем в названиях (в нижнем регистре)

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
    "┣ 👥 1 принятый рекрутом — **10** монет\n"
    "┗ 🌙 Ночью **00:00–10:00 МСК** — бонус **×1.3** (13 за принятого, 1.3 за час)"
)

MSK = datetime.timezone(datetime.timedelta(hours=3))
_DATA_DIR = os.getenv("DATA_DIR", "")
DATA_FILE = os.path.join(_DATA_DIR, "data.json") if _DATA_DIR else "data.json"


def is_night():
    h = datetime.datetime.now(MSK).hour
    return NIGHT_FROM <= h < NIGHT_TO


def current_mult():
    return NIGHT_MULTIPLIER if is_night() else 1.0

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
    # миграция старого ./data.json в постоянную папку (чтобы не потерять монеты)
    if _DATA_DIR and not os.path.exists(DATA_FILE) and os.path.exists("data.json"):
        try:
            import shutil
            os.makedirs(_DATA_DIR, exist_ok=True)
            shutil.copy("data.json", DATA_FILE)
            print("[data] мигрировал data.json в постоянную папку", flush=True)
        except Exception as e:
            print(f"[data] миграция: {e}", flush=True)
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                _data = json.load(f)
        except Exception:
            pass
    _data.setdefault("users", {})
    _data.setdefault("last_weekly", "")
    _data.setdefault("stock", {})
    _data.setdefault("cfg", {})
    _data.setdefault("reac", {})
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
                "w_accepted": 0, "w_voice": 0,
                "d_voice": 0, "vbucket": 0, "d_day": ""}
        _data["users"][uid] = user
    for k in ("balance", "accepted", "voice_sec", "w_accepted", "w_voice",
              "d_voice", "vbucket"):
        user.setdefault(k, 0)
    user.setdefault("d_day", "")
    user.setdefault("warns", [])
    return user


def add_balance(uid, amount):
    u(uid)["balance"] += amount
    save_data()


def add_accept(uid):
    user = u(uid)
    user["accepted"] += 1
    user["w_accepted"] += 1
    earned = COINS_PER_ACCEPT * current_mult()
    user["balance"] += earned
    save_data()
    return earned


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
        self.add_dynamic_items(ApplyButton, AcceptButton, CallButton, DeclineButton, RelayButton)
        self.add_view(ShopView())
        self.add_view(GiveView())
        self.add_view(ReacView())


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


def fam_accepted_role(fam):
    key = fam.get("accepted_cfg_key")
    if key:
        rid = _data.get("cfg", {}).get(key)
        if rid:
            return rid
    return fam.get("accepted_role_id", 0)


def fam_logs_channel(fam):
    key = fam.get("logs_cfg_key")
    if key:
        cid = _data.get("cfg", {}).get(key)
        if cid:
            return cid
    return fam.get("logs_channel_id", 0)


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
    n = round(float(n), 1)
    if n.is_integer():
        txt = f"{int(n):,}".replace(",", " ")
    else:
        txt = f"{n:,.1f}".replace(",", " ")
    return txt + f" {CURRENCY_EMOJI}"


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
        channel = interaction.client.get_channel(fam_logs_channel(fam))
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
                              self.full_name.value, fam_accepted_role(fam), interaction.user)


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
    earned = add_accept(reviewer.id)
    await log_coins(reviewer, earned, u(reviewer.id)["balance"],
                    f"Принят игрок в {fam['name']}" + (" 🌙×1.3" if is_night() else ""))

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
           f"Тебе начислено {fmt_coins(earned)}" + (" 🌙 (ночной ×1.3)" if is_night() else "") + f".{note}")
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


class RelayModal(discord.ui.Modal, title="Сообщение кандидату"):
    def __init__(self, family_key, candidate_id):
        super().__init__()
        self.family_key = family_key
        self.candidate_id = candidate_id
        self.msg = discord.ui.TextInput(label="Текст сообщения",
                                        style=discord.TextStyle.paragraph, max_length=1500)
        self.add_item(self.msg)

    async def on_submit(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(self.candidate_id)
        if not member:
            await interaction.response.send_message("⚠️ Кандидат не найден на сервере.", ephemeral=True)
            return
        # запоминаем куда слать ответы кандидата
        _data.setdefault("cfg", {}).setdefault("dm_relay", {})[str(self.candidate_id)] = interaction.channel_id
        save_data()
        try:
            await member.send(f"📨 **Рекрутёр EXTENDO пишет тебе:**\n{self.msg.value}\n\n"
                              f"_Ответь прямо здесь, в личных сообщениях — я передам рекрутёру._")
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ У кандидата закрыты ЛС — не доставить.", ephemeral=True)
            return
        emb = discord.Embed(color=0x3498DB,
                            description=f"📤 {interaction.user.mention} → **{member}**:\n{self.msg.value}")
        await interaction.channel.send(embed=emb)
        await interaction.response.send_message("✅ Отправлено кандидату.", ephemeral=True)


class RelayButton(discord.ui.DynamicItem[discord.ui.Button],
                  template=r"relaymsg:(?P<fam>\w+):(?P<uid>\d+)"):
    def __init__(self, family_key, user_id):
        self.family_key = family_key
        self.user_id = user_id
        super().__init__(discord.ui.Button(label="💬 Написать кандидату",
                         style=discord.ButtonStyle.secondary,
                         custom_id=f"relaymsg:{family_key}:{user_id}"))

    @classmethod
    async def from_custom_id(cls, interaction, item, match):
        return cls(match["fam"], int(match["uid"]))

    async def callback(self, interaction: discord.Interaction):
        if not member_can_review(interaction.user, self.family_key):
            await interaction.response.send_message("⛔ Нет прав.", ephemeral=True)
            return
        await interaction.response.send_modal(RelayModal(self.family_key, self.user_id))


@bot.event
async def on_message(message):
    # ответы кандидата в ЛС -> в канал заявок
    if message.author.bot or message.guild is not None:
        return
    relay = _data.get("cfg", {}).get("dm_relay", {})
    ch_id = relay.get(str(message.author.id))
    if not ch_id:
        return
    ch = bot.get_channel(ch_id)
    if not ch:
        return
    emb = discord.Embed(color=0x2ECC71,
                        description=f"💬 **{message.author}** (кандидат) ответил:\n{message.content or '—'}")
    if message.attachments:
        emb.add_field(name="Вложения", value="\n".join(a.url for a in message.attachments), inline=False)
    emb.set_footer(text=f"ID: {message.author.id}")
    try:
        await ch.send(embed=emb)
        await message.add_reaction("✅")
    except Exception:
        pass


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


@bot.tree.command(name="панель", description="Выложить панель заявок EXTENDO CHILLIAD")
async def panel_extendo(interaction):
    await post_panel(interaction, "extendo")


@bot.tree.command(name="панель_vzp", description="Выложить панель заявок EXTENDO CHILLIAD VZP")
async def panel_vzp(interaction):
    await post_panel(interaction, "vzp")


@bot.tree.command(name="панель_blaine", description="Выложить панель заявок EXTENDO BLAINE")
async def panel_blaine(interaction):
    await post_panel(interaction, "blaine")


@bot.tree.command(name="панель_blaine_vzp", description="Выложить панель заявок EXTENDO BLAINE VZP")
async def panel_blaine_vzp(interaction):
    await post_panel(interaction, "blaine_vzp")


# ============================================================================
#  ===== ЭКОНОМИКА: ВОЙСЫ =====
# ============================================================================
@tasks.loop(minutes=1)
async def voice_earn_loop():
    today = datetime.datetime.now(MSK).strftime("%Y-%m-%d")
    mult = current_mult()
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            if AFK_CHANNEL_ID and vc.id == AFK_CHANNEL_ID:
                continue
            for member in vc.members:
                if member.bot:
                    continue
                vs = member.voice
                if vs and (vs.self_mute or vs.mute):
                    continue  # в муте — монеты НЕ капают
                user = u(member.id)
                # дневной сброс статистики
                if user.get("d_day") != today:
                    user["d_day"] = today
                    user["d_voice"] = 0
                # +1 минута времени
                user["voice_sec"] += 60
                user["w_voice"] += 60
                user["d_voice"] += 60
                user["vbucket"] += 60
                # монета ТОЛЬКО за каждый полный час (3600 сек)
                while user["vbucket"] >= 3600:
                    user["vbucket"] -= 3600
                    coins = COINS_PER_HOUR * mult
                    user["balance"] += coins
                    voice_hour_earn[member.id] = voice_hour_earn.get(member.id, 0) + coins
    save_data()


@voice_earn_loop.before_loop
async def _before_voice():
    await bot.wait_until_ready()


# ============================================================================
#  ===== ЭКОНОМИКА: БАЛАНС / ВЫДАЧА =====
# ============================================================================
def is_staff(member):
    if not isinstance(member, discord.Member):
        return False
    if member.guild and member.id == member.guild.owner_id:
        return True
    if member.guild_permissions.administrator:
        return True
    return _has_any_role(member, STAFF_ROLE_IDS)


# ----------------------------------------------------------------------------
#  /профиль — личный кабинет
# ----------------------------------------------------------------------------
@bot.tree.command(name="профиль", description="Личный кабинет участника")
@app_commands.describe(участник="Чей профиль (по умолчанию — свой)")
async def profile_cmd(interaction: discord.Interaction, участник: discord.Member = None):
    m = участник or interaction.user
    data = u(m.id)
    top_role = m.top_role.name if m.top_role and m.top_role.name != "@everyone" else "—"
    joined = m.joined_at.strftime("%d.%m.%Y") if m.joined_at else "—"
    warns = data.get("warns", [])
    embed = discord.Embed(title=f"📇  ПРОФИЛЬ · {m.display_name}", color=EMBED_COLOR)
    embed.set_thumbnail(url=m.display_avatar.url)
    embed.add_field(name="👤 Роль", value=top_role, inline=True)
    embed.add_field(name="📅 С нами с", value=joined, inline=True)
    embed.add_field(name="🪙 Монеты", value=fmt_coins(data["balance"]), inline=True)
    embed.add_field(name="👥 Принято", value=str(data["accepted"]), inline=True)
    embed.add_field(name="🎙 В войсах", value=fmt_voice(data["voice_sec"]), inline=True)
    embed.add_field(name="⚠️ Варнов", value=str(len(warns)), inline=True)
    embed.set_footer(text=FOOTER_TEXT,
                     icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
    await interaction.response.send_message(embed=embed)


# ----------------------------------------------------------------------------
#  Варны / история
# ----------------------------------------------------------------------------
@bot.tree.command(name="варн", description="Выдать предупреждение участнику")
@app_commands.describe(участник="Кому", причина="За что")
async def warn_cmd(interaction: discord.Interaction, участник: discord.Member, причина: str):
    if not is_staff(interaction.user):
        await interaction.response.send_message("⛔ Нет прав.", ephemeral=True)
        return
    data = u(участник.id)
    data.setdefault("warns", []).append({
        "by": interaction.user.id,
        "reason": причина,
        "date": datetime.datetime.now(MSK).strftime("%d.%m.%Y %H:%M"),
    })
    save_data()
    n = len(data["warns"])
    try:
        await участник.send(f"⚠️ Тебе выдан **варн** в EXTENDO.\nПричина: {причина}\nВсего варнов: {n}")
    except discord.Forbidden:
        pass
    await interaction.response.send_message(
        f"⚠️ Варн выдан {участник.mention} (всего: {n}).\nПричина: {причина}", ephemeral=True)


@bot.tree.command(name="снятьварн", description="Снять последний варн")
@app_commands.describe(участник="С кого снять")
async def unwarn_cmd(interaction: discord.Interaction, участник: discord.Member):
    if not is_staff(interaction.user):
        await interaction.response.send_message("⛔ Нет прав.", ephemeral=True)
        return
    data = u(участник.id)
    warns = data.setdefault("warns", [])
    if not warns:
        await interaction.response.send_message("У участника нет варнов.", ephemeral=True)
        return
    removed = warns.pop()
    save_data()
    await interaction.response.send_message(
        f"✅ Снят варн с {участник.mention} (осталось: {len(warns)}).\n"
        f"Был: {removed['reason']}", ephemeral=True)


@bot.tree.command(name="история", description="История варнов участника")
@app_commands.describe(участник="Чья история")
async def history_cmd(interaction: discord.Interaction, участник: discord.Member):
    if not is_staff(interaction.user) and участник.id != interaction.user.id:
        await interaction.response.send_message("⛔ Нет прав.", ephemeral=True)
        return
    data = u(участник.id)
    warns = data.get("warns", [])
    embed = discord.Embed(title=f"📋 История · {участник.display_name}", color=EMBED_COLOR)
    embed.set_thumbnail(url=участник.display_avatar.url)
    if warns:
        lines = [f"**{i+1}.** {w['date']} — {w['reason']} (от <@{w['by']}>)"
                 for i, w in enumerate(warns)]
        embed.add_field(name=f"⚠️ Варны ({len(warns)})", value="\n".join(lines)[:1024], inline=False)
    else:
        embed.add_field(name="⚠️ Варны", value="нет", inline=False)
    embed.set_footer(text=FOOTER_TEXT,
                     icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ----------------------------------------------------------------------------
#  НИК НЕ ПО ФОРМЕ — авто-создание роли/канала + проверка
# ----------------------------------------------------------------------------
async def ensure_nickform(guild):
    cfg = _data.setdefault("cfg", {})
    role = guild.get_role(cfg.get("nickform_role", 0))
    if role is None:
        role = discord.utils.get(guild.roles, name="Ник не по форме")
        if role is None:
            try:
                role = await guild.create_role(name="Ник не по форме", colour=discord.Colour(0xE67E22),
                                               reason="Система ник-формы")
            except Exception:
                role = None
        if role:
            cfg["nickform_role"] = role.id
    ch = guild.get_channel(cfg.get("nickform_channel", 0))
    if ch is None:
        ch = discord.utils.get(guild.text_channels, name="ник-не-по-форме")
        if ch is None:
            try:
                ch = await guild.create_text_channel("📝・ник-не-по-форме", reason="Система ник-формы")
            except Exception:
                ch = None
        if ch:
            cfg["nickform_channel"] = ch.id
    save_data()
    return role, ch


async def do_nickform_check(guild):
    role, ch = await ensure_nickform(guild)
    if not role or not ch:
        return 0
    violators = []
    for m in guild.members:
        if m.bot:
            continue
        name = m.nick or m.name
        if not NICKFORM_REGEX.match(name):
            violators.append(m)
            if role not in m.roles:
                try:
                    await m.add_roles(role, reason="Ник не по форме")
                except Exception:
                    pass
    if violators:
        mentions = " ".join(v.mention for v in violators[:50])
        emb = discord.Embed(
            title="⚠️ НИК НЕ ПО ФОРМЕ",
            description=("У вас ник **не по форме** (нужно: `Имя Фамилия`).\n"
                         "У вас есть **24 часа**, чтобы исправить ник, иначе — меры.\n\n"
                         f"Нарушителей: **{len(violators)}**"),
            color=0xE67E22, timestamp=datetime.datetime.now(MSK))
        emb.set_footer(text=FOOTER_TEXT,
                       icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
        try:
            await ch.send(content=mentions, embed=emb,
                          allowed_mentions=discord.AllowedMentions(users=True))
        except Exception:
            pass
    return len(violators)


@bot.tree.command(name="проверка_ников", description="Проверить ники по форме сейчас")
async def nickcheck_cmd(interaction: discord.Interaction):
    if not is_staff(interaction.user):
        await interaction.response.send_message("⛔ Нет прав.", ephemeral=True)
        return
    await interaction.response.send_message("⏳ Проверяю ники…", ephemeral=True)
    n = await do_nickform_check(interaction.guild)
    await interaction.followup.send(f"✅ Проверка завершена. Нарушителей: **{n}**", ephemeral=True)


@tasks.loop(hours=24)
async def nickform_loop():
    now = datetime.datetime.now(MSK)
    if now.weekday() != NICKFORM_DAY or now.hour != NICKFORM_HOUR:
        return
    stamp = now.strftime("%Y-%W-nick")
    if _data.get("cfg", {}).get("last_nick") == stamp:
        return
    _data.setdefault("cfg", {})["last_nick"] = stamp
    save_data()
    for g in bot.guilds:
        await do_nickform_check(g)


@nickform_loop.before_loop
async def _before_nickform():
    await bot.wait_until_ready()


def build_honor_embed():
    users = _data["users"]
    top_acc = sorted(users.items(), key=lambda kv: kv[1].get("accepted", 0), reverse=True)
    top_voice = sorted(users.items(), key=lambda kv: kv[1].get("voice_sec", 0), reverse=True)
    embed = discord.Embed(title="🏅  ДОСКА ПОЧЁТА  ·  EXTENDO FAMILY",
                          color=0xF1C40F, timestamp=datetime.datetime.now(MSK),
                          description="Лучшие за всё время. Спасибо за вклад! 🫡")
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    acc = [f"{medals[i]} <@{uid}> — **{d.get('accepted',0)}** принятых"
           for i, (uid, d) in enumerate(top_acc[:10]) if d.get("accepted", 0) > 0]
    voi = [f"{medals[i]} <@{uid}> — **{fmt_voice(d.get('voice_sec',0))}**"
           for i, (uid, d) in enumerate(top_voice[:10]) if d.get("voice_sec", 0) > 0]
    embed.add_field(name="👥  Лучшие рекрутёры", value="\n".join(acc) or "—", inline=False)
    embed.add_field(name="🎙  Больше всех в войсе", value="\n".join(voi) or "—", inline=False)
    if THUMBNAIL_URL.startswith("http"):
        embed.set_thumbnail(url=THUMBNAIL_URL)
    if BANNER_URL.startswith("http"):
        embed.set_image(url=BANNER_URL)
    embed.set_footer(text=FOOTER_TEXT,
                     icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
    return embed


@tasks.loop(hours=1)
async def honor_loop():
    now = datetime.datetime.now(MSK)
    if now.day != 1 or now.hour != HONOR_HOUR:
        return
    stamp = now.strftime("%Y-%m")
    if _data.get("cfg", {}).get("last_honor") == stamp:
        return
    _data.setdefault("cfg", {})["last_honor"] = stamp
    save_data()
    ch = bot.get_channel(HONOR_CHANNEL_ID or _data.get("cfg", {}).get("honor", 0) or TOP_CHANNEL_ID)
    if ch:
        try:
            await ch.send(content="@everyone 🏅 **Доска почёта месяца!**",
                          embed=build_honor_embed(),
                          allowed_mentions=discord.AllowedMentions(everyone=True))
        except Exception:
            pass


@honor_loop.before_loop
async def _before_honor():
    await bot.wait_until_ready()


@bot.tree.command(name="доска_почёта", description="Показать доску почёта сейчас")
async def honor_cmd(interaction):
    await interaction.response.send_message(embed=build_honor_embed())


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


@tasks.loop(hours=1)
async def hourly_stats_loop():
    if not TOP_CHANNEL_ID:
        return
    ch = bot.get_channel(TOP_CHANNEL_ID)
    if not ch:
        return
    # топ недели
    try:
        await ch.send(embed=build_top_embed(weekly=True))
    except Exception:
        pass
    # стата «кто сколько насидел за сегодня»
    users = _data["users"]
    rows = sorted(users.items(), key=lambda kv: kv[1].get("d_voice", 0), reverse=True)
    medals = ["🥇", "🥈", "🥉"] + ["▫️"] * 7
    lines = []
    for i, (uid, d) in enumerate(rows[:10]):
        if d.get("d_voice", 0) <= 0:
            break
        lines.append(f"{medals[i]} <@{uid}> — **{fmt_voice(d['d_voice'])}**")
    emb = discord.Embed(title="📊  НАСИЖЕНО ЗА СЕГОДНЯ (войсы)", color=EMBED_COLOR,
                        description="\n".join(lines) or "—",
                        timestamp=datetime.datetime.now(MSK))
    if THUMBNAIL_URL.startswith("http"):
        emb.set_thumbnail(url=THUMBNAIL_URL)
    emb.set_footer(text=FOOTER_TEXT,
                   icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
    try:
        await ch.send(embed=emb)
    except Exception:
        pass


@hourly_stats_loop.before_loop
async def _before_hourly_stats():
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
class ResetConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)

    @discord.ui.button(label="✅ ДА, обнулить всем", style=discord.ButtonStyle.danger)
    async def yes(self, interaction, button):
        count = 0
        for d in _data["users"].values():
            d["balance"] = 0
            count += 1
        save_data()
        for c in self.children:
            c.disabled = True
        await interaction.response.edit_message(
            content=f"✅ Баланс обнулён у **{count}** участников.", view=self)

    @discord.ui.button(label="Отмена", style=discord.ButtonStyle.secondary)
    async def no(self, interaction, button):
        for c in self.children:
            c.disabled = True
        await interaction.response.edit_message(content="Отменено.", view=self)


@bot.tree.command(name="обнулить_монеты", description="Обнулить монеты ВСЕМ участникам")
async def reset_coins_cmd(interaction: discord.Interaction):
    try:
        owner_id = interaction.guild.owner_id if interaction.guild else None
        can = (interaction.user.id == owner_id
               or (GIVE_COIN_ROLE_ID and _has_any_role(interaction.user, [GIVE_COIN_ROLE_ID])))
        if not can:
            await interaction.response.send_message("⛔ Нет прав.", ephemeral=True)
            return
        await interaction.response.send_message(
            "⚠️ **Обнулить монеты ВСЕМ?** Это нельзя отменить.",
            view=ResetConfirmView(), ephemeral=True)
    except Exception as e:
        print(f"[reset] {e}", flush=True)
        try:
            await interaction.response.send_message(f"⚠️ Ошибка: {e}", ephemeral=True)
        except Exception:
            pass


@bot.tree.command(name="closeticket", description="Закрыть тикет покупки (в канале тикета)")
async def close_ticket_cmd(interaction: discord.Interaction):
    ch = interaction.channel
    # только в каналах-тикетах покупок
    if not ch or not ch.name.startswith("покупка-"):
        await interaction.response.send_message(
            "⛔ Команду можно использовать только внутри тикета покупки.", ephemeral=True)
        return
    # права: владелец, Coin Manager или персонал уведомлений
    allowed = (interaction.user.id == interaction.guild.owner_id
               or (GIVE_COIN_ROLE_ID and _has_any_role(interaction.user, [GIVE_COIN_ROLE_ID]))
               or interaction.user.id in PURCHASE_NOTIFY_USER_IDS)
    if not allowed:
        await interaction.response.send_message("⛔ Нет прав закрывать тикеты.", ephemeral=True)
        return
    await interaction.response.send_message("🔒 Тикет закрывается через 5 секунд…", ephemeral=True)
    import asyncio as _a
    await _a.sleep(5)
    try:
        await ch.delete(reason=f"Тикет закрыл {interaction.user}")
    except Exception:
        pass


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    print(f"[CMD ERROR] {type(error).__name__}: {error}", flush=True)
    try:
        if interaction.response.is_done():
            await interaction.followup.send(f"⚠️ Ошибка команды: {error}", ephemeral=True)
        else:
            await interaction.response.send_message(f"⚠️ Ошибка команды: {error}", ephemeral=True)
    except Exception:
        pass


# ============================================================================
#  ===== ПРАВИЛА =====
# ============================================================================
RULES_BLOCKS = [
    ("💬  1. КОММУНИКАЦИЯ", [
        "1.1 Оскорбления в сторону софама запрещены.",
        "1.2 Упоминания родни в сторону софама запрещены.",
        "1.3 Оскорбление нации — **2 варна сразу!**",
        "1.4 Обман софама — **ЧС фамы**.",
        "1.5 Игнор старшего состава (OWNER, Dep.Owner, Recruitment).",
        "1.6 Залив жалобы на софама запрещён — конфликты решает СС (п.1.5), "
        "нужен откат/доказательства.",
    ]),
    ("🚗  2. АВТОПАРК", [
        "2.1 Перед ресом авто семьи — спроси в чат (нет ответа минуту — ресай).",
        "2.2 Действия с водителем запрещены (тайзер, отбор обманом). "
        "Можно, если сам отдаёт руль.",
        "2.3 Нельзя оставлять авто с бензином <40% — **15к на банк орги**.",
        "2.4 Нельзя ресать занятое авто (можно, если игрок вышел/не отвечает 5+ мин).",
    ]),
    ("🏛  3. ТИТУЛ (ОСОБНЯК)", [
        "3.1 Запрещено открывать титул (стрельба с территории).",
        "3.2 Запрещена стрельба за титулом и уход в него.",
        "3.3 Фан-гейм запрещён, если сторона не согласна.",
    ]),
    ("⚔️  4. ОРГАНИЗАЦИЯ / ВЗП", [
        "4.1 Прыгать в метку «Войны семей» запрещено (можно, если вписан в терру).",
        "4.2 Опоздание в терру — **ранг/варн**.",
        "4.3 Реакция на атаку/дефф без прыжка (будучи вписанным) — **ранг/варн**.",
        "4.4 Слив склада — **ЧС фамы**.",
        "4.5 Обход систем семьи запрещён.",
        "4.6 Крики/мешание коллеру — **ранг/варн**.",
    ]),
    ("📑  5. КОНТРАКТЫ", [
        "5.1 Минимум людей для пика — **от 3** (меньше — варн).",
        "5.2 Перед контрактом собери людей / будь уверен, что выполнишь.",
    ]),
    ("🧾  СНЯТИЕ ВАРНА", [
        "Снять варн — **30к на счёт орги** (через банк).",
        "При 3 варнах — **3 дня** на снятие всех (**100к на банк**). "
        "Не снял — **кик с фамы**.",
    ]),
]


@bot.tree.command(name="правила", description="Выложить правила семьи в этот канал")
async def rules_cmd(interaction: discord.Interaction):
    if (interaction.user.id != interaction.guild.owner_id
            and not interaction.user.guild_permissions.administrator):
        await interaction.response.send_message("⛔ Только для админов.", ephemeral=True)
        return
    head = discord.Embed(
        title="📜  ПРАВИЛА СЕМЬИ  ·  EXTENDO FAMILY",
        color=EMBED_COLOR,
        description=("Соблюдение правил обязательно для каждого участника.\n"
                     "Все наказания — на усмотрение СС (п. 1.5).\n"
                     "Правила дополняются по мере необходимости."))
    if BANNER_URL.startswith("http"):
        head.set_image(url=BANNER_URL)
    if THUMBNAIL_URL.startswith("http"):
        head.set_thumbnail(url=THUMBNAIL_URL)
    await interaction.channel.send(embed=head)
    for title, lines in RULES_BLOCKS:
        emb = discord.Embed(title=title, color=EMBED_COLOR,
                            description="\n".join(lines))
        emb.set_footer(text=FOOTER_TEXT,
                       icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
        await interaction.channel.send(embed=emb)
    await interaction.response.send_message("✅ Правила выложены.", ephemeral=True)


# ============================================================================
#  ===== АВТО-БЭКАП ДАННЫХ В КАНАЛ (замена БД) =====
# ============================================================================
@tasks.loop(hours=6)
async def backup_loop():
    bid = BACKUP_CHANNEL_ID or _data.get("cfg", {}).get("backup", 0)
    if not bid:
        return
    ch = bot.get_channel(bid)
    if not ch:
        return
    # ЗАЩИТА: не отправляем ПУСТОЙ бэкап — чтобы он не затёр хороший
    if len(_data.get("users", {})) == 0:
        print("[backup] пропуск — данные пустые, не затираем хороший бэкап", flush=True)
        return
    try:
        if os.path.exists(DATA_FILE):
            n = len(_data.get("users", {}))
            await ch.send(content=f"🗄 Бэкап {datetime.datetime.now(MSK).strftime('%d.%m.%Y %H:%M')} · 👥 {n}",
                          file=discord.File(DATA_FILE))
    except Exception as e:
        print(f"[backup] {e}", flush=True)


@backup_loop.before_loop
async def _before_backup():
    await bot.wait_until_ready()


async def restore_from_backup():
    """Если data.json пуст/отсутствует — тянем ЛУЧШИЙ (непустой) бэкап из канала."""
    bid = BACKUP_CHANNEL_ID or _data.get("cfg", {}).get("backup", 0)
    if not bid:
        return
    if os.path.exists(DATA_FILE) and len(_data.get("users", {})) > 0:
        return
    ch = bot.get_channel(bid)
    if not ch:
        return
    try:
        import json as _j
        best = None
        best_n = 0
        async for msg in ch.history(limit=50):          # ищем среди 50 последних
            for att in msg.attachments:
                if att.filename.endswith(".json"):
                    try:
                        data = _j.loads((await att.read()).decode("utf-8"))
                        n = len(data.get("users", {}))
                        if n > best_n:                   # берём бэкап с БОЛЬШИМ числом людей
                            best, best_n = data, n
                    except Exception:
                        continue
        if best and best_n > 0:
            cur_cfg = _data.get("cfg", {})
            _data.clear()
            _data.update(best)
            _data["cfg"] = {**best.get("cfg", {}), **cur_cfg}  # сохраняем текущие ID каналов
            save_data()
            print(f"[backup] восстановлено {best_n} участников из лучшего бэкапа ✅", flush=True)
    except Exception as e:
        print(f"[backup] restore: {e}", flush=True)


@bot.tree.command(name="восстановить", description="Восстановить монеты из файла data.json")
@app_commands.describe(файл="Прикрепи файл data.json (из канала бэкапа)")
async def restore_cmd(interaction: discord.Interaction, файл: discord.Attachment):
    if interaction.user.id != interaction.guild.owner_id and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Только для админов.", ephemeral=True)
        return
    if not файл.filename.endswith(".json"):
        await interaction.response.send_message("⚠️ Нужен файл **.json** (data.json).", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    try:
        import json as _j
        data = _j.loads((await файл.read()).decode("utf-8"))
    except Exception as e:
        await interaction.followup.send(f"⚠️ Файл не читается как data.json: {e}", ephemeral=True)
        return
    if not isinstance(data, dict) or "users" not in data:
        await interaction.followup.send("⚠️ Это не похоже на бэкап бота (нет users).", ephemeral=True)
        return
    n = len(data.get("users", {}))
    summ = round(sum(u.get("balance", 0) for u in data.get("users", {}).values()), 1)
    cur_cfg = _data.get("cfg", {})
    _data.clear()
    _data.update(data)
    _data["cfg"] = {**data.get("cfg", {}), **cur_cfg}   # сохраняем текущие ID каналов
    save_data()
    await interaction.followup.send(
        f"✅ Восстановлено **{n}** участников, всего **{summ}** {CURRENCY_NAME} {CURRENCY_EMOJI}.\n"
        f"Монеты вернулись. Сделай на всякий `/бэкап`.", ephemeral=True)
    print(f"[restore] вручную восстановлено {n} участников ({summ} монет)", flush=True)


@bot.tree.command(name="бэкап", description="Сделать бэкап данных сейчас")
async def backup_cmd(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Только для админов.", ephemeral=True)
        return
    bid = BACKUP_CHANNEL_ID or _data.get("cfg", {}).get("backup", 0)
    if not bid:
        await interaction.response.send_message("⚠️ Бэкап-канал не настроен (запусти /setup_all).", ephemeral=True)
        return
    ch = bot.get_channel(bid)
    try:
        await ch.send(content=f"🗄 Ручной бэкап {datetime.datetime.now(MSK).strftime('%d.%m.%Y %H:%M')}",
                      file=discord.File(DATA_FILE))
        await interaction.response.send_message("✅ Бэкап сделан.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ {e}", ephemeral=True)


# ============================================================================
#  ===== ИКОНКИ РОЛЕЙ (эмодзи) — требует буст 2 уровня =====
# ============================================================================
LOGO_ICON_URL = THUMBNAIL_URL   # логотип фамы для иконок ролей

ICON_ROLE_NAMES = [
    "Owner", "Coin Manager", "Dep.Owner Chilliad", "Dep.Owner Blaine",
    "Head Recruitment Chilliad", "Head Recruitment Blaine",
    "Head VZP Chilliad", "Head VZP Blaine", "High Recruitment", "High VZP",
    "Extendo Main Chilliad", "Extendo Main Blaine",
    "Recruitment Chilliad", "Recruitment Blaine",
    "Extendo Family Chilliad", "Extendo Family Blaine",
    "VZP Chilliad", "VZP Blaine", "VZP", "Extendo Academy",
]


LOGO_B64 = "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"


async def _logo_icon_bytes():
    """Иконка роли: берём ВШИТОЕ в код лого (base64) -> PNG 128x128.
    Работает всегда, даже если ссылка на лого протухла."""
    try:
        import base64 as _b64
        return _b64.b64decode(LOGO_B64)
    except Exception as e:
        print(f"[icons] b64 decode: {e}", flush=True)
    # запасной вариант — скачать по ссылке
    try:
        from PIL import Image
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as s:
            async with s.get(LOGO_ICON_URL) as r:
                if r.status != 200:
                    return None
                raw = await r.read()
        img = Image.open(io.BytesIO(raw))
        try: img.seek(0)
        except Exception: pass
        img = img.convert("RGBA").resize((128, 128))
        b = io.BytesIO(); img.save(b, "PNG")
        return b.getvalue()
    except Exception as e:
        print(f"[icons] {e}", flush=True)
        return None


@bot.tree.command(name="иконки_ролей", description="Поставить логотип фамы иконкой всем ролям (буст 2 ур.)")
async def role_icons_cmd(interaction: discord.Interaction):
    if interaction.user.id != interaction.guild.owner_id and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("⛔ Только для админов.", ephemeral=True)
        return
    await interaction.response.send_message("⏳ Ставлю логотип иконкой ролям…", ephemeral=True)
    icon = await _logo_icon_bytes()
    if not icon:
        await interaction.followup.send("⚠️ Не смог загрузить логотип (ссылка протухла?). Пришли новый PNG.", ephemeral=True)
        return
    g = interaction.guild
    done, fail = 0, []
    for name in ICON_ROLE_NAMES:
        role = discord.utils.get(g.roles, name=name)
        if not role:
            continue
        try:
            await role.edit(display_icon=icon, reason="Логотип-иконка")
            done += 1
        except Exception as e:
            fail.append(f"{name}: {e}")
    msg = f"✅ Иконок проставлено: {done}"
    if fail:
        msg += "\n⚠️ Нужен буст 2 ур. / права:\n- " + "\n- ".join(fail[:5])
    try:
        await interaction.followup.send(msg, ephemeral=True)
    except Exception:
        pass


async def make_welcome_image(member):
    """Генерит приветственную картинку. Возвращает BytesIO или None."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return None
    try:
        W, H = 1000, 350
        img = Image.new("RGB", (W, H), (18, 18, 20))
        draw = ImageDraw.Draw(img)
        # красная рамка
        draw.rectangle([6, 6, W - 7, H - 7], outline=(177, 18, 38), width=5)
        # аватар по центру слева, кругом
        try:
            avatar_bytes = await member.display_avatar.replace(size=256).read()
            av = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((200, 200))
            mask = Image.new("L", (200, 200), 0)
            ImageDraw.Draw(mask).ellipse([0, 0, 200, 200], fill=255)
            img.paste(av, (60, 75), mask)
            draw.ellipse([60, 75, 260, 275], outline=(177, 18, 38), width=5)
        except Exception:
            pass
        # шрифты (дефолтные, чтобы не зависеть от файлов)
        try:
            big = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
            mid = ImageFont.truetype("DejaVuSans-Bold.ttf", 34)
            small = ImageFont.truetype("DejaVuSans.ttf", 26)
        except Exception:
            big = mid = small = ImageFont.load_default()
        draw.text((300, 100), "ДОБРО ПОЖАЛОВАТЬ", font=big, fill=(255, 255, 255))
        name = member.display_name[:22]
        draw.text((300, 160), name, font=mid, fill=(230, 60, 80))
        draw.text((300, 215), "EXTENDO FAMILY", font=small, fill=(150, 150, 150))
        buf = io.BytesIO()
        img.save(buf, "PNG")
        buf.seek(0)
        return buf
    except Exception:
        return None


@bot.event
async def on_member_join(member):
    wid = WELCOME_CHANNEL_ID or _data.get("cfg", {}).get("welcome", 0)
    if not wid or member.bot:
        return
    ch = member.guild.get_channel(wid)
    if not ch:
        return
    count = member.guild.member_count
    emb = discord.Embed(
        title="Д О Б Р О   П О Ж А Л О В А Т Ь",
        color=EMBED_COLOR,
        description=(f"# {member.mention}\n\n"
                    f"Рады видеть тебя в **EXTENDO FAMILY** 🩸\n"
                    f"Ты — наш **{count}-й** участник.\n\n"
                    f"▸ Загляни в **правила**\n"
                    f"▸ Поставь ник **по форме**\n"
                    f"▸ Залетай в войс — погнали 🔥"))
    emb.set_thumbnail(url=member.display_avatar.url)   # аватар новичка
    if BANNER_URL.startswith("http"):
        emb.set_image(url=BANNER_URL)                  # логотип фамы крупно
    emb.set_footer(text=FOOTER_TEXT,
                   icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
    try:
        await ch.send(content=f"🎉 {member.mention}", embed=emb,
                      allowed_mentions=discord.AllowedMentions(users=True))
    except Exception:
        pass


@bot.tree.command(name="айди", description="Показать ID всех ролей и каналов сервера")
async def ids_cmd(interaction: discord.Interaction):
    # только владелец или Coin Manager / head-роли — чтобы не светить всем
    can = (interaction.user.id == interaction.guild.owner_id
           or interaction.user.guild_permissions.administrator)
    if not can:
        await interaction.response.send_message("⛔ Только для админов.", ephemeral=True)
        return
    g = interaction.guild
    # РОЛИ
    role_lines = [f"{r.name} = {r.id}" for r in reversed(g.roles) if r.name != "@everyone"]
    # КАНАЛЫ
    chan_lines = []
    for cat, chans in g.by_category():
        if cat:
            chan_lines.append(f"\n[КАТЕГОРИЯ] {cat.name} = {cat.id}")
        for ch in chans:
            t = "голос" if isinstance(ch, discord.VoiceChannel) else "текст"
            chan_lines.append(f"  ({t}) {ch.name} = {ch.id}")

    import io
    text = "=== РОЛИ ===\n" + "\n".join(role_lines) + "\n\n=== КАНАЛЫ ===\n" + "\n".join(chan_lines)
    buf = io.BytesIO(text.encode("utf-8"))
    await interaction.response.send_message(
        "📋 Все ID ролей и каналов во вложении:",
        file=discord.File(buf, filename="ids.txt"), ephemeral=True)


# ============================================================================
#  ===== SETUP BLAINE: создать структуру Blaine зеркально Chilliad =====
# ============================================================================
# карта Chilliad-роль -> Blaine-роль (права/цвет копируются, overwrites переназначаются)
BLAINE_ROLE_MAP = {
    996791697193308302: 1562891371101032528,   # Dep.Owner
    1513294574007615518: 1562891847234359507,   # Head Recruitment
    1513510003607212062: 1562891933561397258,   # Head VZP
    701066783498698813: 1562892051866198177,    # Extendo Main
    1524757394955960511: 1562892139212439708,   # Recruitment
    1524756881472622674: 1562892249883345026,   # Extendo Family
}
SRC_RECRUIT_CAT = 1513305674791256228   # Recruitment Chilliad (источник)
SRC_MEMBERS_CAT = 1494369677248561174   # Extendo (источник)
SHOP_CHANNEL_ID = 1560278688107470998   # магазин
EXTENDO_FAMILY_BLAINE = 1562892249883345026


async def _mirror_category(guild, src_cat_id, new_name):
    # не дублировать, если уже есть
    for c in guild.categories:
        if c.name == new_name:
            return c, list(c.channels)
    src = guild.get_channel(src_cat_id)
    if not src:
        return None, []
    # переназначаем overwrites: Chilliad-роли -> Blaine-роли, остальное как есть
    ow = {}
    for target, perm in src.overwrites.items():
        if isinstance(target, discord.Role) and target.id in BLAINE_ROLE_MAP:
            nt = guild.get_role(BLAINE_ROLE_MAP[target.id])
            if nt:
                ow[nt] = perm
        else:
            ow[target] = perm
    newcat = await guild.create_category(new_name, overwrites=ow)
    created = []
    for ch in src.channels:
        try:
            if isinstance(ch, discord.VoiceChannel):
                nc = await guild.create_voice_channel(ch.name, category=newcat)
            else:
                nc = await guild.create_text_channel(ch.name, category=newcat)
            created.append(nc)
        except Exception as e:
            print(f"[setup] канал {ch.name}: {e}", flush=True)
    return newcat, created


VZP_ROLE_CHILLIAD = 1512956758719467591   # роль VZP (станет "VZP Chilliad")
SRC_VZP_CAT = 1512868053409599669         # категория VZP (источник)


@bot.tree.command(name="setup_vzp_blaine", description="Создать VZP Blaine (роль + категория)")
async def setup_vzp_blaine_cmd(interaction: discord.Interaction):
    if (interaction.user.id != interaction.guild.owner_id
            and not interaction.user.guild_permissions.administrator):
        await interaction.response.send_message("⛔ Только для админов/владельца.", ephemeral=True)
        return
    await interaction.response.send_message("⏳ Создаю VZP Blaine…", ephemeral=True)
    g = interaction.guild
    report = []

    # 1) переименовать VZP -> VZP Chilliad
    vzp = g.get_role(VZP_ROLE_CHILLIAD)
    if vzp and vzp.name != "VZP Chilliad":
        try:
            await vzp.edit(name="VZP Chilliad", reason="Разделение на Chilliad/Blaine")
        except Exception as e:
            report.append(f"переименование VZP: {e}")

    # 2) создать роль VZP Blaine (копия VZP) — если ещё нет
    vzp_blaine_id = _data.get("cfg", {}).get("vzp_blaine_role")
    vzp_blaine = g.get_role(vzp_blaine_id) if vzp_blaine_id else None
    if not vzp_blaine:
        vzp_blaine = discord.utils.get(g.roles, name="VZP Blaine")
    if not vzp_blaine and vzp:
        try:
            vzp_blaine = await g.create_role(
                name="VZP Blaine", colour=vzp.colour,
                permissions=vzp.permissions, hoist=vzp.hoist,
                mentionable=vzp.mentionable, reason="VZP Blaine")
        except Exception as e:
            report.append(f"создание роли: {e}")
    if vzp_blaine:
        _data.setdefault("cfg", {})["vzp_blaine_role"] = vzp_blaine.id

    # 3) зеркалим категорию VZP -> VZP Blaine (роли remap + VZP->VZP Blaine)
    role_map = dict(BLAINE_ROLE_MAP)
    if vzp_blaine:
        role_map[VZP_ROLE_CHILLIAD] = vzp_blaine.id
    # не дублировать
    if not discord.utils.get(g.categories, name="VZP Blaine"):
        src_cat = g.get_channel(SRC_VZP_CAT)
        if src_cat:
            ow = {}
            for target, perm in src_cat.overwrites.items():
                if isinstance(target, discord.Role) and target.id in role_map:
                    nt = g.get_role(role_map[target.id])
                    if nt:
                        ow[nt] = perm
                else:
                    ow[target] = perm
            try:
                newcat = await g.create_category("VZP Blaine", overwrites=ow)
                for ch in src_cat.channels:
                    try:
                        if isinstance(ch, discord.VoiceChannel):
                            await g.create_voice_channel(ch.name, category=newcat)
                        else:
                            await g.create_text_channel(ch.name, category=newcat)
                    except Exception as e:
                        report.append(f"канал {ch.name}: {e}")
            except Exception as e:
                report.append(f"категория: {e}")

    save_data()
    msg = (f"✅ **VZP Blaine готов!**\n"
           f"Роль VZP Blaine: {vzp_blaine.mention if vzp_blaine else '—'}\n"
           "Роль VZP переименована в VZP Chilliad. Категория VZP Blaine создана.")
    if report:
        msg += "\n⚠️ " + "; ".join(report[:6])
    try:
        await interaction.followup.send(msg, ephemeral=True)
    except Exception:
        pass


@bot.tree.command(name="setup_blaine", description="Создать структуру Extendo Blaine (роли, каналы, права)")
async def setup_blaine_cmd(interaction: discord.Interaction):
    if (interaction.user.id != interaction.guild.owner_id
            and not interaction.user.guild_permissions.administrator):
        await interaction.response.send_message("⛔ Только для админов/владельца.", ephemeral=True)
        return
    await interaction.response.send_message("⏳ Создаю структуру Blaine… это займёт ~10-20 сек.", ephemeral=True)
    g = interaction.guild
    report = []

    # 1) копируем права + цвет ролей Chilliad -> Blaine
    for cid, bid in BLAINE_ROLE_MAP.items():
        cr = g.get_role(cid)
        br = g.get_role(bid)
        if cr and br:
            try:
                await br.edit(permissions=cr.permissions, colour=cr.colour,
                              hoist=cr.hoist, mentionable=cr.mentionable,
                              reason="Копия прав с Chilliad")
            except Exception as e:
                report.append(f"роль {br.name}: {e}")

    # 2) Recruitment Blaine
    rec_cat, rec_ch = await _mirror_category(g, SRC_RECRUIT_CAT, "Recruitment Blaine")
    for ch in rec_ch:
        if "логи-заявок" in ch.name and "vzp" not in ch.name.lower():
            _data.setdefault("cfg", {})["blaine_rp_logs"] = ch.id
    # отдельный канал логов VZP для Blaine
    if rec_cat:
        existing_vzp = discord.utils.get(rec_cat.channels, name="📥・логи-заявок-vzp")
        if existing_vzp:
            _data.setdefault("cfg", {})["blaine_vzp_logs"] = existing_vzp.id
        else:
            try:
                vlog = await g.create_text_channel("📥・логи-заявок-vzp", category=rec_cat)
                _data.setdefault("cfg", {})["blaine_vzp_logs"] = vlog.id
            except Exception as e:
                report.append(f"vzp-логи: {e}")

    # 3) Extendo Blaine (члены)
    await _mirror_category(g, SRC_MEMBERS_CAT, "Extendo Blaine")

    # 4) доступ в магазин для Extendo Family Blaine
    shop = g.get_channel(SHOP_CHANNEL_ID)
    fam_b = g.get_role(EXTENDO_FAMILY_BLAINE)
    if shop and fam_b:
        try:
            await shop.set_permissions(fam_b, view_channel=True, reason="Доступ Blaine в магазин")
        except Exception as e:
            report.append(f"магазин: {e}")

    save_data()
    cfg = _data.get("cfg", {})
    msg = ("✅ **Blaine создан!**\n"
           f"📥 Логи RP: <#{cfg.get('blaine_rp_logs', 0)}>\n"
           f"📥 Логи VZP: <#{cfg.get('blaine_vzp_logs', 0)}>\n"
           "Панели: `/панель_blaine` и `/панель_blaine_vzp`")
    if report:
        msg += "\n⚠️ Предупреждения:\n- " + "\n- ".join(report[:8])
    try:
        await interaction.followup.send(msg, ephemeral=True)
    except Exception:
        pass


# ============================================================================
#  ===== СТАТИСТИКА ВОЙН (ВС) — парсер + карточка в стиле Extendo =====
# ============================================================================
def _norm(s):
    return str(s or "").lower().replace(" ", "").replace("x", "")


def _wfont(sz, bold=True):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(f"DejaVuSans{'-Bold' if bold else ''}.ttf", sz)
    except Exception:
        return ImageFont.load_default()


def make_war_image(enemy, location, server, our_side, win, time_str):
    """Простая карточка (запасная, без ростера)."""
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return None
    try:
        W, H = 1000, 420
        img = Image.new("RGB", (W, H), (14, 14, 16))
        d = ImageDraw.Draw(img)
        accent = (46, 204, 113) if win else (231, 76, 60)
        d.rectangle([5, 5, W - 6, H - 6], outline=accent, width=6)
        d.rectangle([0, 0, W, 70], fill=(177, 18, 38))
        d.text((30, 14), "РЕЗУЛЬТАТ ВОЙНЫ СЕМЕЙ", font=_wfont(46), fill=(255, 255, 255))
        d.text((40, 120), "EXTENDO", font=_wfont(38), fill=(230, 60, 80))
        d.text((320, 128), "VS", font=_wfont(28, False), fill=(150, 150, 150))
        d.text((400, 120), str(enemy)[:20], font=_wfont(38), fill=(255, 255, 255))
        side_txt = "АТАКА" if our_side == "atk" else "ДЕФ"
        d.text((40, 210), f"Локация:  {location}", font=_wfont(28, False), fill=(180, 180, 180))
        d.text((40, 250), f"Сервер:  {server}     Время:  {time_str}", font=_wfont(28, False), fill=(180, 180, 180))
        d.text((40, 290), f"Наша сторона:  {side_txt}", font=_wfont(28, False), fill=(180, 180, 180))
        d.text((40, 335), "ПОБЕДА" if win else "ПОРАЖЕНИЕ", font=_wfont(60), fill=accent)
        buf = io.BytesIO(); img.save(buf, "PNG"); buf.seek(0)
        return buf
    except Exception:
        return None


def make_war_card(p):
    """Детальная карточка войны (ростер + урон) в стиле Extendo."""
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return None
    try:
        our, enemy, win = p["our"], p["enemy"], p["win"]
        rows = max(len(our["players"]), len(enemy["players"]), 1)
        W, H = 1500, 300 + rows * 34 + 40
        img = Image.new("RGB", (W, H), (13, 13, 15))
        d = ImageDraw.Draw(img)
        green, red, grey, white = (46, 204, 113), (231, 76, 60), (150, 150, 150), (240, 240, 240)
        accent = green if win else red
        d.rectangle([0, 0, W, 78], fill=(177, 18, 38))
        d.text((34, 16), "РЕЗУЛЬТАТ ВОЙНЫ СЕМЕЙ", font=_wfont(44), fill=(255, 255, 255))
        res = "ПОБЕДА" if win else "ПОРАЖЕНИЕ"
        rw = d.textlength(res, font=_wfont(40))
        d.text((W - rw - 34, 18), res, font=_wfont(40), fill=(255, 255, 255))
        d.text((34, 96), str(p["location"])[:48], font=_wfont(30), fill=white)
        d.text((34, 140), f"Сервер: {p['server']}        Время: {p['time']}", font=_wfont(26, False), fill=grey)
        d.rectangle([5, 5, W - 6, H - 6], outline=accent, width=5)

        def panel(x0, team, is_win, color):
            pw = 700
            d.rectangle([x0, 190, x0 + pw, 240], fill=(26, 26, 30))
            d.text((x0 + 18, 198), str(team["name"])[:24], font=_wfont(32), fill=color)
            if is_win:
                bw = d.textlength("WINNER", font=_wfont(22))
                d.rectangle([x0 + pw - bw - 40, 200, x0 + pw - 14, 232], fill=green)
                d.text((x0 + pw - bw - 27, 204), "WINNER", font=_wfont(22), fill=(0, 0, 0))
            d.text((x0 + 18, 250), f"Киллы: {team['kills']}    Урон: {team['damage']}    ХС: {team['hs']}",
                   font=_wfont(24), fill=white)
            cols = [("ИГРОК", x0 + 18), ("K", x0 + 330), ("SHOTS", x0 + 390),
                    ("DMG", x0 + 480), ("HIT%", x0 + 570), ("HS%", x0 + 650)]
            for name, cx in cols:
                d.text((cx, 292), name, font=_wfont(18, False), fill=grey)
            y = 322
            for pl in team["players"][:10]:
                d.text((x0 + 18, y), str(pl["name"])[:20], font=_wfont(20, False), fill=white)
                d.text((x0 + 330, y), str(pl["k"]), font=_wfont(20, False), fill=accent if pl["k"] else grey)
                d.text((x0 + 390, y), str(pl["shots"]), font=_wfont(20, False), fill=grey)
                d.text((x0 + 480, y), str(pl["dmg"]), font=_wfont(20, False), fill=white)
                d.text((x0 + 570, y), f"{pl['hit']}%", font=_wfont(20, False), fill=grey)
                d.text((x0 + 650, y), f"{pl['hs']}%", font=_wfont(20, False), fill=grey)
                y += 34

        panel(30, our, win, green if win else red)
        panel(770, enemy, not win, red if win else green)
        buf = io.BytesIO(); img.save(buf, "PNG"); buf.seek(0)
        return buf
    except Exception as e:
        print(f"[war] card: {e}", flush=True)
        return None


def _players_of(obj):
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in ("players", "members", "roster", "stats", "list"):
            if isinstance(obj.get(k), list):
                return obj[k]
    return []


def _pget(pl, *keys, default=0):
    for k in keys:
        if isinstance(pl, dict) and pl.get(k) is not None:
            return pl[k]
    return default


def _team_from(event, side_prefix, name):
    arr = None
    for key in (f"{side_prefix}Players", f"{side_prefix}_players", side_prefix,
                f"{side_prefix}Team", f"{side_prefix}_team", f"{side_prefix}Stats"):
        pl = _players_of(event.get(key))
        if pl:
            arr = pl
            break
    arr = arr or []
    players = []
    for pl in arr:
        players.append({
            "name": _pget(pl, "name", "nickname", "charName", "playerName", "nick", default="—"),
            "k": _pget(pl, "kills", "k", "killCount", default=0),
            "shots": _pget(pl, "shots", "shotCount", "shot", default=0),
            "dmg": _pget(pl, "damage", "dmg", "damageDealt", default=0),
            "hit": _pget(pl, "hitPercent", "hit", "accuracy", "hitPct", default=0),
            "hs": _pget(pl, "hsPercent", "hs", "headshotPercent", "hsPct", default=0),
        })
    totK = sum(int(x["k"] or 0) for x in players)
    totD = sum(int(x["dmg"] or 0) for x in players)
    return {"name": name, "kills": totK, "damage": f"{totD:,}".replace(",", " "),
            "hs": event.get(f"{side_prefix}Hs") or "-", "players": players}


@tasks.loop(minutes=3)
async def war_loop():
    cfg = _data.setdefault("cfg", {})
    chil_id = WAR_STATS_CHILLIAD_ID or cfg.get("war_chilliad", 0)
    blaine_id = WAR_STATS_BLAINE_ID or cfg.get("war_blaine", 0)
    if not (chil_id or blaine_id):
        return
    seen = cfg.setdefault("war_seen", [])
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout, headers={"User-Agent": "Mozilla/5.0"}) as s:
            async with s.get(WAR_API_URL) as r:
                if r.status != 200:
                    return
                raw = await r.json(content_type=None)
    except Exception as e:
        print(f"[war] fetch: {e}", flush=True)
        return
    events = raw if isinstance(raw, list) else raw.get("data", raw.get("events", []))
    if not isinstance(events, list):
        return
    for e in events:
        if not isinstance(e, dict):
            continue
        if e.get("endedAt") is None:
            continue
        eid = str(e.get("eventId") or e.get("id") or "")
        if not eid or eid in seen:
            continue
        atk = e.get("attackerName") or ""
        dfn = e.get("defenderName") or ""
        if WAR_FAMILY_NAME not in _norm(atk) and WAR_FAMILY_NAME not in _norm(dfn):
            continue
        if not cfg.get("war_logged"):
            print("[war] RAW EVENT >>> " + json.dumps(e, ensure_ascii=False)[:1800], flush=True)
            cfg["war_logged"] = True
            save_data()
        we_atk = WAR_FAMILY_NAME in _norm(atk)
        server = str(e.get("serverName") or "")
        location = e.get("pointName") or e.get("point") or "—"
        winner = str(e.get("winner") or e.get("winnerSide") or e.get("result") or "")
        wl = winner.lower()
        if "atk" in wl or "attack" in wl:
            win = we_atk
        elif "def" in wl:
            win = not we_atk
        else:
            wname = _norm(e.get("winnerName") or "")
            win = ((wname == _norm(atk) and we_atk) or (wname == _norm(dfn) and not we_atk)) if wname else False
        try:
            dt = datetime.datetime.fromisoformat(str(e.get("startedAt")).replace("Z", "+00:00"))
            time_str = dt.astimezone(MSK).strftime("%d.%m %H:%M")
        except Exception:
            time_str = "—"
        our = _team_from(e, "attacker" if we_atk else "defender", atk if we_atk else dfn)
        enemy = _team_from(e, "defender" if we_atk else "attacker", dfn if we_atk else atk)
        payload = {"win": win, "location": location, "server": server, "time": time_str,
                   "our": our, "enemy": enemy}
        ch_id = blaine_id if "blaine" in server.lower() else chil_id
        ch = bot.get_channel(ch_id) if ch_id else None
        if ch:
            buf = make_war_card(payload) if our["players"] else None
            if not buf:
                buf = make_war_image(enemy["name"], location, server, "atk" if we_atk else "def", win, time_str)
            try:
                if buf:
                    await ch.send(file=discord.File(buf, filename="war.png"))
                else:
                    rr = "ПОБЕДА" if win else "ПОРАЖЕНИЕ"
                    await ch.send(f"**EXTENDO vs {enemy['name']}** · {location} · {server} — {rr}")
            except Exception as ex:
                print(f"[war] send: {ex}", flush=True)
        seen.append(eid)
    if len(seen) > 200:
        cfg["war_seen"] = seen[-200:]
    save_data()


@war_loop.before_loop
async def _before_war():
    await bot.wait_until_ready()


@bot.tree.command(name="setup_war", description="Создать каналы статы войн + переименовать старые категории")
async def setup_war_cmd(interaction: discord.Interaction):
    if (interaction.user.id != interaction.guild.owner_id
            and not interaction.user.guild_permissions.administrator):
        await interaction.response.send_message("⛔ Только для админов.", ephemeral=True)
        return
    await interaction.response.send_message("⏳ Настраиваю статистику войн…", ephemeral=True)
    g = interaction.guild
    report = []

    # переименовать старые категории в Chilliad
    renames = {1494369677248561174: "Extendo Chilliad", 1512868053409599669: "VZP Chilliad"}
    for cid, newname in renames.items():
        cat = g.get_channel(cid)
        if cat and cat.name != newname:
            try:
                await cat.edit(name=newname)
            except Exception as e:
                report.append(f"{newname}: {e}")

    # канал статы войн Chilliad — в категории VZP Chilliad (бывш. VZP)
    vzp_cat = g.get_channel(1512868053409599669)
    if vzp_cat:
        ch = discord.utils.get(vzp_cat.channels, name="⚔️・статистика-войн")
        if not ch:
            try:
                ch = await g.create_text_channel("⚔️・статистика-войн", category=vzp_cat)
            except Exception as e:
                report.append(f"война-chilliad: {e}")
                ch = None
        if ch:
            _data.setdefault("cfg", {})["war_chilliad"] = ch.id

    # канал статы войн Blaine — в категории VZP Blaine
    blaine_cat = discord.utils.get(g.categories, name="VZP Blaine")
    if blaine_cat:
        ch = discord.utils.get(blaine_cat.channels, name="⚔️・статистика-войн")
        if not ch:
            try:
                ch = await g.create_text_channel("⚔️・статистика-войн", category=blaine_cat)
            except Exception as e:
                report.append(f"война-blaine: {e}")
                ch = None
        if ch:
            _data.setdefault("cfg", {})["war_blaine"] = ch.id
    else:
        report.append("Категория VZP Blaine не найдена — сначала /setup_vzp_blaine")

    save_data()
    cfg = _data.get("cfg", {})
    msg = (f"✅ Готово!\nСтата Chilliad: <#{cfg.get('war_chilliad', 0)}>\n"
           f"Стата Blaine: <#{cfg.get('war_blaine', 0)}>\n"
           "Старые категории переименованы в Chilliad.")
    if report:
        msg += "\n⚠️ " + "; ".join(report[:6])
    try:
        await interaction.followup.send(msg, ephemeral=True)
    except Exception:
        pass


@bot.tree.command(name="war_test", description="Показать пример карточки войны (дизайн)")
async def war_test_cmd(interaction: discord.Interaction):
    sample = {"win": True, "location": "Рынок Текстайл-сити — Мясо", "server": "Chiliad",
              "time": "27.10 22:28",
              "our": {"name": "X EXTENDO X", "kills": 10, "damage": "1 595", "hs": 19, "players": [
                  {"name": "Matteo_Violencean", "k": 3, "shots": 82, "dmg": 211, "hit": 37.8, "hs": 2.4},
                  {"name": "Icepeak_Extendo", "k": 2, "shots": 138, "dmg": 321, "hit": 34.8, "hs": 0.7},
                  {"name": "Kayseri_Extendo", "k": 2, "shots": 98, "dmg": 131, "hit": 20.4, "hs": 4.1},
                  {"name": "Ben_Ten", "k": 1, "shots": 131, "dmg": 281, "hit": 34.4, "hs": 0},
                  {"name": "Gazik_Extendo", "k": 1, "shots": 86, "dmg": 103, "hit": 17.4, "hs": 4.7},
                  {"name": "New_Era", "k": 0, "shots": 43, "dmg": 90, "hit": 18.6, "hs": 4.7}]},
              "enemy": {"name": "HARRIGAN", "kills": 1, "damage": "1 334", "hs": 9, "players": [
                  {"name": "Ye_Harriganov", "k": 1, "shots": 39, "dmg": 113, "hit": 46.2, "hs": 0},
                  {"name": "Lord_Harriganov", "k": 0, "shots": 212, "dmg": 348, "hit": 25.5, "hs": 1.4},
                  {"name": "Foxes_Harriganov", "k": 0, "shots": 40, "dmg": 150, "hit": 40, "hs": 2.5}]}}
    buf = make_war_card(sample)
    if buf:
        await interaction.response.send_message(file=discord.File(buf, filename="war_test.png"), ephemeral=True)
    else:
        await interaction.response.send_message("Не удалось сгенерить (нет Pillow).", ephemeral=True)


# ============================================================================
#  ===== ЗАПИСЬ НА ВС (/reac) =====
# ============================================================================
REAC_POSITIONS = ["Вход", "Опора", "Фраг", "Разгон", "Коллер", "Хил", "Снайпер", "Любая"]


def reac_embed(state):
    slots = state["slots"]
    main = state["main"]       # {uid: position}
    subs = state["subs"]       # [uid]
    embed = discord.Embed(title=f"📋  ЗАПИСЬ НА ВС  ·  {state['format']}",
                          color=EMBED_COLOR,
                          description=(f"🕒 {state.get('time','—')}\n"
                                       "Выбери позицию в меню ниже — запишешься в основу.\n"
                                       "Кол кидай в ветке. Нет места — жми **Замена**."))
    if THUMBNAIL_URL.startswith("http"):
        embed.set_thumbnail(url=THUMBNAIL_URL)
    main_lines = []
    for i, (uid, pos) in enumerate(main.items(), 1):
        main_lines.append(f"`{i}.` <@{uid}> — **{pos}**")
    embed.add_field(name=f"✅ Основа ({len(main)}/{slots})",
                    value="\n".join(main_lines) or "—", inline=False)
    sub_lines = [f"<@{u}>" for u in subs]
    embed.add_field(name=f"🔄 Замена ({len(subs)})",
                    value=", ".join(sub_lines) or "—", inline=False)
    embed.set_footer(text=FOOTER_TEXT,
                     icon_url=THUMBNAIL_URL if THUMBNAIL_URL.startswith("http") else None)
    return embed


async def reac_update(interaction, state):
    try:
        await interaction.message.edit(embed=reac_embed(state))
    except Exception:
        pass
    save_data()


async def reac_ensure_thread(interaction, state):
    if state.get("thread_id"):
        return interaction.guild.get_channel(state["thread_id"])
    try:
        th = await interaction.message.create_thread(name=f"ВС {state['format']} — колы/позиции")
        state["thread_id"] = th.id
        save_data()
        return th
    except Exception:
        return None


class ReacPositionSelect(discord.ui.Select):
    def __init__(self):
        opts = [discord.SelectOption(label=p, value=p) for p in REAC_POSITIONS]
        super().__init__(placeholder="Выбери позицию и запишись…", options=opts,
                         custom_id="reac_pos")

    async def callback(self, interaction: discord.Interaction):
        mid = str(interaction.message.id)
        state = _data.setdefault("reac", {}).get(mid)
        if not state:
            await interaction.response.send_message("Эта запись уже неактивна.", ephemeral=True)
            return
        uid = str(interaction.user.id)
        pos = self.values[0]
        if uid in state["main"]:
            state["main"][uid] = pos  # смена позиции
        else:
            if len(state["main"]) >= state["slots"]:
                await interaction.response.send_message(
                    "❌ Основа заполнена — жми **🔄 Замена**.", ephemeral=True)
                return
            if uid in state["subs"]:
                state["subs"].remove(uid)
            state["main"][uid] = pos
        await interaction.response.send_message(f"✅ Ты записан: **{pos}**. Кидай кол в ветке.", ephemeral=True)
        th = await reac_ensure_thread(interaction, state)
        if th:
            try:
                await th.add_user(interaction.user)
                await th.send(f"{interaction.user.mention} записался на **{pos}** — кидай кол 📸")
            except Exception:
                pass
        await reac_update(interaction, state)


class ReacView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ReacPositionSelect())

    @discord.ui.button(label="🔄 Замена", style=discord.ButtonStyle.secondary, custom_id="reac_sub")
    async def sub(self, interaction, button):
        mid = str(interaction.message.id)
        state = _data.setdefault("reac", {}).get(mid)
        if not state:
            await interaction.response.send_message("Запись неактивна.", ephemeral=True); return
        uid = str(interaction.user.id)
        state["main"].pop(uid, None)
        if uid not in state["subs"]:
            state["subs"].append(uid)
        await interaction.response.send_message("🔄 Ты в замене.", ephemeral=True)
        await reac_update(interaction, state)

    @discord.ui.button(label="❌ Выписаться", style=discord.ButtonStyle.danger, custom_id="reac_leave")
    async def leave(self, interaction, button):
        mid = str(interaction.message.id)
        state = _data.setdefault("reac", {}).get(mid)
        if not state:
            await interaction.response.send_message("Запись неактивна.", ephemeral=True); return
        uid = str(interaction.user.id)
        state["main"].pop(uid, None)
        if uid in state["subs"]:
            state["subs"].remove(uid)
        await interaction.response.send_message("❌ Ты выписан.", ephemeral=True)
        await reac_update(interaction, state)

    @discord.ui.button(label="🧵 Ветка", style=discord.ButtonStyle.primary, custom_id="reac_thread")
    async def thread(self, interaction, button):
        mid = str(interaction.message.id)
        state = _data.setdefault("reac", {}).get(mid)
        if not state:
            await interaction.response.send_message("Запись неактивна.", ephemeral=True); return
        th = await reac_ensure_thread(interaction, state)
        if th:
            await interaction.response.send_message(f"🧵 Ветка: {th.mention}", ephemeral=True)
        else:
            await interaction.response.send_message("Не смог открыть ветку.", ephemeral=True)


@bot.tree.command(name="reac", description="Создать запись на ВС")
@app_commands.describe(формат="Например 6x6", время="Когда (напр. 21:00 МСК)")
async def reac_cmd(interaction: discord.Interaction, формат: str, время: str = "—"):
    # slots = число слева
    import re as _re
    m = _re.match(r"\s*(\d+)", формат)
    slots = int(m.group(1)) if m else 6
    state = {"format": формат, "time": время, "slots": slots,
             "main": {}, "subs": [], "thread_id": None,
             "channel_id": interaction.channel_id}
    await interaction.response.send_message("Создаю запись…", ephemeral=True)
    msg = await interaction.channel.send(content="@here 📋 **Запись на ВС!**",
                                         embed=reac_embed(state), view=ReacView(),
                                         allowed_mentions=discord.AllowedMentions(everyone=True))
    _data.setdefault("reac", {})[str(msg.id)] = state
    save_data()


@bot.tree.command(name="setup_all", description="Создать ВСЕ системные каналы автоматически")
async def setup_all_cmd(interaction: discord.Interaction):
    if (interaction.user.id != interaction.guild.owner_id
            and not interaction.user.guild_permissions.administrator):
        await interaction.response.send_message("⛔ Только для админов/владельца.", ephemeral=True)
        return
    await interaction.response.send_message("⏳ Создаю систему… 20-40 сек.", ephemeral=True)
    g = interaction.guild
    cfg = _data.setdefault("cfg", {})
    report = []

    async def ensure_text(name, category=None, private=False, save_key=None):
        ch = discord.utils.get(g.text_channels, name=name)
        if not ch:
            ow = None
            if private:
                ow = {g.default_role: discord.PermissionOverwrite(view_channel=False),
                      g.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
            try:
                ch = await g.create_text_channel(name, category=category, overwrites=ow or {})
            except Exception as e:
                report.append(f"{name}: {e}")
                return None
        if save_key:
            cfg[save_key] = ch.id
        return ch

    # системная категория (скрытая)
    sys_cat = discord.utils.get(g.categories, name="⚙ Extendo Система")
    if not sys_cat:
        try:
            sys_cat = await g.create_category("⚙ Extendo Система", overwrites={
                g.default_role: discord.PermissionOverwrite(view_channel=False),
                g.me: discord.PermissionOverwrite(view_channel=True)})
        except Exception as e:
            report.append(f"категория: {e}")

    await ensure_text("🗄・логи-бэкап", sys_cat, private=True, save_key="backup")
    await ensure_text("📝・ник-напоминание", None, private=False, save_key="nickform_channel")

    # публичные каналы
    welcome = await ensure_text("👋・добро-пожаловать", save_key="welcome")
    honor = await ensure_text("🏅・доска-почёта", save_key="honor")
    rules_ch = await ensure_text("📜・правила")

    # роль "Ник не по форме"
    nf_role = discord.utils.get(g.roles, name="Ник не по форме")
    if not nf_role:
        try:
            nf_role = await g.create_role(name="Ник не по форме", colour=discord.Colour(0xE67E22),
                                          reason="Контроль ников")
        except Exception as e:
            report.append(f"роль ника: {e}")
    if nf_role:
        cfg["nickform_role"] = nf_role.id

    # выложить правила
    if rules_ch:
        try:
            await rules_ch.purge(limit=20)
        except Exception:
            pass
        try:
            head = discord.Embed(title="📜  ПРАВИЛА СЕМЬИ  ·  EXTENDO FAMILY", color=EMBED_COLOR,
                                 description="Соблюдение правил обязательно. Наказания — на усмотрение СС (п.1.5).")
            if BANNER_URL.startswith("http"):
                head.set_image(url=BANNER_URL)
            await rules_ch.send(embed=head)
            for title, lines in RULES_BLOCKS:
                emb = discord.Embed(title=title, color=EMBED_COLOR, description="\n".join(lines))
                emb.set_footer(text=FOOTER_TEXT)
                await rules_ch.send(embed=emb)
        except Exception as e:
            report.append(f"правила: {e}")

    # первый бэкап сразу (чтобы монеты были в безопасности)
    bch = g.get_channel(cfg.get("backup", 0))
    if bch and os.path.exists(DATA_FILE):
        try:
            await bch.send(content="🗄 Первый бэкап", file=discord.File(DATA_FILE))
        except Exception:
            pass

    save_data()
    msg = ("✅ **Система создана!**\n"
           f"📜 Правила: {rules_ch.mention if rules_ch else '—'}\n"
           f"👋 Приветствия: {welcome.mention if welcome else '—'}\n"
           f"🏅 Доска почёта: {honor.mention if honor else '—'}\n"
           f"🗄 Бэкап: <#{cfg.get('backup',0)}> (монеты теперь в безопасности)\n"
           "Дальше: `/setup_vzp_blaine` и `/setup_war` для войн.")
    if report:
        msg += "\n⚠️ " + "; ".join(report[:6])
    try:
        await interaction.followup.send(msg, ephemeral=True)
    except Exception:
        pass


# ============================================================================
#  ===== ПРАВА КАТЕГОРИЙ (закрыть приватные нормально) =====
# ============================================================================
CATEGORY_ACCESS = {
    "Recruitment Blaine": ["Owner", "Coin Manager", "Dep.Owner Blaine",
                           "Head Recruitment Blaine", "High Recruitment",
                           "Extendo Main Blaine", "Recruitment Blaine"],
    "Extendo Blaine": ["Owner", "Dep.Owner Blaine", "Head Recruitment Blaine",
                       "High Recruitment", "Extendo Main Blaine",
                       "Recruitment Blaine", "Extendo Family Blaine"],
    "VZP Blaine": ["Owner", "Dep.Owner Blaine", "Head VZP Blaine", "High VZP",
                   "Extendo Main Blaine", "VZP Blaine"],
}


@bot.tree.command(name="fix_perms", description="Закрыть приватные категории (VZP/Blaine) нормально")
async def fix_perms_cmd(interaction: discord.Interaction):
    if (interaction.user.id != interaction.guild.owner_id
            and not interaction.user.guild_permissions.administrator):
        await interaction.response.send_message("⛔ Только для админов.", ephemeral=True)
        return
    await interaction.response.send_message("⏳ Настраиваю права категорий…", ephemeral=True)
    g = interaction.guild
    report = []
    for cat_name, role_names in CATEGORY_ACCESS.items():
        cat = discord.utils.get(g.categories, name=cat_name)
        if not cat:
            report.append(f"нет категории {cat_name}")
            continue
        ow = {g.default_role: discord.PermissionOverwrite(view_channel=False),
              g.me: discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                manage_channels=True)}
        for rn in role_names:
            role = discord.utils.get(g.roles, name=rn)
            if role:
                ow[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                       connect=True, speak=True)
        try:
            await cat.edit(overwrites=ow, reason="Фикс прав")
            # синкаем все каналы категории под категорию
            for ch in cat.channels:
                try:
                    await ch.edit(overwrites=ow)
                except Exception:
                    pass
        except Exception as e:
            report.append(f"{cat_name}: {e}")
    msg = "✅ Права категорий закрыты (видят только нужные роли)."
    if report:
        msg += "\n⚠️ " + "; ".join(report[:6])
    try:
        await interaction.followup.send(msg, ephemeral=True)
    except Exception:
        pass


@bot.event
async def on_ready():
    if not voice_earn_loop.is_running():
        voice_earn_loop.start()
    if not weekly_loop.is_running():
        weekly_loop.start()
    if not voice_digest_loop.is_running():
        voice_digest_loop.start()
    # hourly_stats_loop отключён — топ теперь только раз в неделю (weekly_loop)
    if not backup_loop.is_running():
        backup_loop.start()
    if not war_loop.is_running():
        war_loop.start()
    await restore_from_backup()
    if not nickform_loop.is_running():
        nickform_loop.start()
    if not honor_loop.is_running():
        honor_loop.start()
    # МГНОВЕННАЯ регистрация команд во все серверы, где есть бот
    try:
        for g in bot.guilds:
            bot.tree.copy_global_to(guild=g)
            synced = await bot.tree.sync(guild=g)
            print(f"[SYNC] сервер {g.name}: {len(synced)} команд", flush=True)
        # чистим старые глобальные команды (чтобы не было дублей)
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
    except Exception as e:
        print(f"[SYNC] ошибка: {e}", flush=True)
    print(f"=== EXTENDO BOT v28 (лого вшито в код + бэкап-канал захардкожен) === запущен как {bot.user}", flush=True)


load_data()

if not TOKEN:
    raise RuntimeError("Не задан TOKEN. Добавь переменную окружения TOKEN на хостинге.")

bot.run(TOKEN)
