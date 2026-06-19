# keyboards.py
# Barcha reply va inline klaviaturalar shu yerda

from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from texts import t
from config import CHANNEL_USERNAME, REGIONS, REGION_NAMES


def lang_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek tili", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data="lang_ru"),
        ]
    ])
    return kb


def profile_lang_keyboard():
    """Profil bo'limidan tilni o'zgartirish uchun (ro'yxatdan o'tish bilan aralashmasligi uchun alohida prefix)"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbek tili", callback_data="plang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data="plang_ru"),
        ]
    ])
    return kb


def regions_keyboard():
    """Barcha viloyatlar ro'yxati (inline tugmalar)"""
    rows, row = [], []
    for i, name in enumerate(REGION_NAMES):
        row.append(InlineKeyboardButton(text=name, callback_data=f"selreg_{i}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def districts_keyboard(region_idx: int):
    """Tanlangan viloyat ichidagi tumanlar ro'yxati (inline tugmalar)"""
    region_name = REGION_NAMES[region_idx]
    districts = REGIONS[region_name]
    rows, row = [], []
    for j, d in enumerate(districts):
        row.append(InlineKeyboardButton(text=d, callback_data=f"seldist_{region_idx}_{j}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def phone_keyboard(lang):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "phone_button"), request_contact=True)]],
        resize_keyboard=True
    )
    return kb


def location_keyboard(lang):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "location_button"), request_location=True)]],
        resize_keyboard=True
    )
    return kb


def subscribe_keyboard(lang):
    channel_link = f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanal / Канал", url=channel_link)],
        [InlineKeyboardButton(text=t(lang, "check_sub"), callback_data="check_sub")]
    ])
    return kb


def main_menu_keyboard(lang):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "btn_add_listing"))],
            [KeyboardButton(text=t(lang, "btn_search")), KeyboardButton(text=t(lang, "btn_vip"))],
            [KeyboardButton(text=t(lang, "btn_my_region")), KeyboardButton(text=t(lang, "btn_profile"))],
            [KeyboardButton(text=t(lang, "btn_my_listings"))],
        ],
        resize_keyboard=True
    )
    return kb


def finish_photos_keyboard(lang):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "finish_photos"))]],
        resize_keyboard=True
    )
    return kb


def skip_keyboard(lang):
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "skip_btn"))]],
        resize_keyboard=True
    )
    return kb


def confirm_listing_keyboard(lang):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "send_for_review"), callback_data="ad_submit")],
        [InlineKeyboardButton(text=t(lang, "edit_btn"), callback_data="ad_edit")],
        [InlineKeyboardButton(text=t(lang, "cancel"), callback_data="ad_cancel")],
    ])
    return kb


# Tahrirlanadigan maydonlar va ularning state nomlari (ketma-ketlikda)
EDIT_FIELDS = [
    ("brand", "field_brand"),
    ("model", "field_model"),
    ("year", "field_year"),
    ("mileage", "field_mileage"),
    ("battery_capacity", "field_battery"),
    ("range_km", "field_range"),
    ("condition", "field_condition"),
    ("price", "field_price"),
    ("region", "field_region"),
    ("district", "field_district"),
    ("extra_info", "field_extra"),
    ("photos", "field_photos"),
]


def edit_fields_keyboard(lang, prefix="ad_edit_field"):
    rows = []
    row = []
    for field_key, text_key in EDIT_FIELDS:
        row.append(InlineKeyboardButton(text=t(lang, text_key), callback_data=f"{prefix}_{field_key}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text=t(lang, "back_to_preview"), callback_data=f"{prefix}_back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def admin_listing_keyboard(listing_id, lang="uz"):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(lang, "adm_approve_btn"), callback_data=f"adm_approve_{listing_id}"),
            InlineKeyboardButton(text=t(lang, "adm_reject_btn"), callback_data=f"adm_reject_{listing_id}"),
        ],
        [InlineKeyboardButton(text=t(lang, "adm_vip_btn"), callback_data=f"adm_vip_{listing_id}")]
    ])
    return kb


def admin_panel_keyboard(lang="uz"):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "adm_pending_btn"), callback_data="adm_pending")],
        [InlineKeyboardButton(text=t(lang, "adm_stats_btn"), callback_data="adm_stats")],
        [InlineKeyboardButton(text=t(lang, "adm_broadcast_btn"), callback_data="adm_broadcast")],
        [InlineKeyboardButton(text=t(lang, "adm_ban_btn"), callback_data="adm_ban"),
         InlineKeyboardButton(text=t(lang, "adm_unban_btn"), callback_data="adm_unban")],
    ])
    return kb


# ---------------- MENING E'LONLARIM ----------------

def my_listing_actions_keyboard(listing_id, lang, can_edit: bool):
    rows = []
    if can_edit:
        rows.append([InlineKeyboardButton(text=t(lang, "edit_listing_btn"), callback_data=f"my_edit_{listing_id}")])
    rows.append([InlineKeyboardButton(text=t(lang, "delete_btn"), callback_data=f"my_delete_{listing_id}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_delete_keyboard(listing_id, lang):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "confirm_delete_yes"), callback_data=f"my_delete_yes_{listing_id}")],
        [InlineKeyboardButton(text=t(lang, "confirm_delete_no"), callback_data=f"my_delete_no_{listing_id}")],
    ])
    return kb


def my_listing_edit_fields_keyboard(lang, listing_id):
    return edit_fields_keyboard(lang, prefix=f"my_field_{listing_id}")


# ---------------- PROFIL ----------------

def profile_keyboard(lang):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "change_lang_btn"), callback_data="profile_change_lang")],
        [InlineKeyboardButton(text=t(lang, "btn_my_listings"), callback_data="profile_my_listings")],
    ])
    return kb