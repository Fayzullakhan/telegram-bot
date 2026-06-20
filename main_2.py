# main.py
# Elektromobil oldi-sotdi Telegram bot - asosiy fayl
# Ishga tushirish: python main.py
# Talab qilinadigan kutubxona: pip install aiogram==3.4.1

import asyncio
import logging

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest

import database as db
from config import (
    BOT_TOKEN, ADMIN_IDS, CHANNEL_ID, CHANNEL_USERNAME, MAX_PHOTOS, MIN_PHOTOS,
    OWNER_PHONE, REGION_NAMES, REGIONS,
)
from texts import t
import keyboards as kb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# E'lon joylashtirish jarayonida vaqtinchalik rasm fayllari
TEMP_PHOTOS = {}     # {user_id: [file_id, ...]}


# ---------------- FSM HOLATLARI ----------------

class Reg(StatesGroup):
    choosing_lang = State()
    waiting_phone = State()


class AddListing(StatesGroup):
    brand = State()
    model = State()
    year = State()
    mileage = State()
    battery = State()
    range_km = State()
    condition = State()
    price = State()
    region = State()
    district = State()
    extra = State()
    photos = State()
    confirming = State()
    editing_value = State()


class SearchFlow(StatesGroup):
    waiting_brand = State()
    waiting_region = State()


class AdminFlow(StatesGroup):
    broadcasting = State()
    banning = State()
    unbanning = State()
    rejecting = State()


class MyListings(StatesGroup):
    editing_value = State()
    editing_photos = State()
    region = State()
    district = State()


# ---------------- YORDAMCHI FUNKSIYALAR ----------------

def is_admin(user_id):
    return user_id in ADMIN_IDS


async def is_subscribed(user_id) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status not in ("left", "kicked")
    except TelegramBadRequest:
        return False
    except Exception as e:
        logger.warning(f"Subscription check error: {e}")
        return False


def append_unit_if_missing(value: str, unit: str) -> str:
    """
    Agar foydalanuvchi faqat raqam kiritgan bo'lsa (masalan '2000'),
    oxiriga birlikni qo'shadi ('2000 km'). Agar allaqachon biror
    birlik/belgi yozilgan bo'lsa (masalan '2000 km' yoki '35000$'),
    qayta qo'shmaydi.
    """
    if not value:
        return value
    value = value.strip()
    # Agar qiymat faqat raqamlardan (va bo'sh joy/vergul/nuqtadan) iborat bo'lsa —
    # demak foydalanuvchi birlik yozmagan, shuni qo'shamiz.
    cleaned = value.replace(" ", "").replace(",", "").replace(".", "")
    if cleaned.isdigit():
        return f"{value} {unit}"
    return value


def normalize_listing_numeric_fields(data: dict, lang="uz") -> dict:
    """mileage, range_km, battery_capacity, price maydonlariga avtomatik birlik qo'shadi"""
    data = dict(data)
    data["mileage"] = append_unit_if_missing(data.get("mileage"), t(lang, "unit_km"))
    data["range_km"] = append_unit_if_missing(data.get("range_km"), t(lang, "unit_km"))
    data["battery_capacity"] = append_unit_if_missing(data.get("battery_capacity"), t(lang, "unit_kwt"))
    data["price"] = append_unit_if_missing(data.get("price"), t(lang, "unit_usd"))
    return data


def format_listing_caption(data: dict, lang="uz", vip=False, phone=None):
    star = "⭐ VIP ⭐\n" if vip else ""
    if lang == "ru":
        text = (
            f"{star}🚗 <b>{data.get('brand','')} {data.get('model','')}</b>\n\n"
            f"📅 Год: {data.get('year','-')}\n"
            f"🛣 Пробег: {data.get('mileage','-')}\n"
            f"🔋 Батарея: {data.get('battery_capacity','-')}\n"
            f"⚡️ Запас хода: {data.get('range_km','-')}\n"
            f"🛠 Состояние: {data.get('condition','-')}\n"
            f"💰 Цена: {data.get('price','-')}\n"
            f"📍 Регион: {data.get('region','-')}, {data.get('district','-')}\n"
        )
        if data.get("extra_info"):
            text += f"📝 Доп: {data.get('extra_info')}\n"
    else:
        text = (
            f"{star}🚗 <b>{data.get('brand','')} {data.get('model','')}</b>\n\n"
            f"📅 Yil: {data.get('year','-')}\n"
            f"🛣 Probeg: {data.get('mileage','-')}\n"
            f"🔋 Batareya: {data.get('battery_capacity','-')}\n"
            f"⚡️ Zapas hodi: {data.get('range_km','-')}\n"
            f"🛠 Holati: {data.get('condition','-')}\n"
            f"💰 Narxi: {data.get('price','-')}\n"
            f"📍 Hudud: {data.get('region','-')}, {data.get('district','-')}\n"
        )
        if data.get("extra_info"):
            text += f"📝 Qo'shimcha: {data.get('extra_info')}\n"

    if phone:
        text += f"\n📞 {phone}"
    return text


async def send_main_menu(message: Message, lang):
    await message.answer(t(lang, "main_menu"), reply_markup=kb.main_menu_keyboard(lang))


def listing_dict_from_row(row):
    return {
        "brand": row["brand"], "model": row["model"], "year": row["year"],
        "mileage": row["mileage"], "battery_capacity": row["battery_capacity"],
        "range_km": row["range_km"], "condition": row["condition"],
        "price": row["price"], "region": row["region"], "district": row["district"],
        "extra_info": row["extra_info"],
    }


def find_region_index(region_name):
    """Berilgan viloyat nomiga mos REGION_NAMES indeksini topadi (mos kelmasa None)"""
    if not region_name:
        return None
    region_name = region_name.strip().lower()
    for i, name in enumerate(REGION_NAMES):
        if name.lower() == region_name:
            return i
    return None


# ---------------- /START VA RO'YXATDAN O'TISH ----------------

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    db.add_or_update_user(message.from_user.id, message.from_user.full_name, message.from_user.username)

    if db.is_user_banned(message.from_user.id):
        await message.answer(t("uz", "banned"))
        return

    await state.clear()
    user = db.get_user(message.from_user.id)

    # Til allaqachon tanlangan bo'lsa, qayta so'ramaymiz
    if not user or not user["lang"]:
        await state.set_state(Reg.choosing_lang)
        await message.answer(t("uz", "choose_lang"), reply_markup=kb.lang_keyboard())
        return

    lang = user["lang"]

    if not user["phone"]:
        await state.set_state(Reg.waiting_phone)
        await message.answer(t(lang, "send_phone"), reply_markup=kb.phone_keyboard(lang))
        return

    # Foydalanuvchi allaqachon to'liq ro'yxatdan o'tgan — obunani jim tekshiramiz,
    # har safar "Tabriklaymiz" xabarini qayta ko'rsatmaymiz
    if user["is_subscribed"]:
        await send_main_menu(message, lang)
        return

    subscribed = await is_subscribed(message.from_user.id)
    if subscribed:
        db.set_user_subscribed(message.from_user.id, True)
        await send_main_menu(message, lang)
    else:
        await message.answer(
            t(lang, "subscribe_required", channel=CHANNEL_USERNAME),
            reply_markup=kb.subscribe_keyboard(lang)
        )


@router.callback_query(Reg.choosing_lang, F.data.startswith("lang_"))
async def process_lang(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    db.set_user_lang(callback.from_user.id, lang)
    await callback.message.delete()

    user = db.get_user(callback.from_user.id)
    if user and user["phone"]:
        await ensure_subscription_or_ask(callback.message, callback.from_user.id, lang, state)
        return

    await state.set_state(Reg.waiting_phone)
    await callback.message.answer(t(lang, "send_phone"), reply_markup=kb.phone_keyboard(lang))


@router.message(Reg.waiting_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    lang = db.get_user(message.from_user.id)["lang"]
    db.set_user_phone(message.from_user.id, message.contact.phone_number)
    # Lokatsiya so'ralmaydi — to'g'ridan-to'g'ri obuna tekshiruviga o'tamiz
    await ensure_subscription_or_ask(message, message.from_user.id, lang, state)


async def ensure_subscription_or_ask(message: Message, user_id, lang, state: FSMContext):
    subscribed = await is_subscribed(user_id)
    if subscribed:
        db.set_user_subscribed(user_id, True)
        await state.clear()
        await message.answer(t(lang, "sub_ok"))
        await send_main_menu(message, lang)
    else:
        await message.answer(
            t(lang, "subscribe_required", channel=CHANNEL_USERNAME),
            reply_markup=kb.subscribe_keyboard(lang)
        )


@router.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery, state: FSMContext):
    lang = db.get_user(callback.from_user.id)["lang"]
    subscribed = await is_subscribed(callback.from_user.id)
    if subscribed:
        db.set_user_subscribed(callback.from_user.id, True)
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(t(lang, "sub_ok"))
        await send_main_menu(callback.message, lang)
    else:
        await callback.answer(t(lang, "sub_fail"), show_alert=True)


# ---------------- UMUMIY BAN VA OBUNA TEKSHIRUVI ----------------

async def guard(message: Message) -> bool:
    user_id = message.from_user.id
    user = db.get_user(user_id)
    if not user:
        await message.answer("Iltimos /start buyrug'ini bosing.")
        return False
    if user["is_banned"]:
        await message.answer(t(user["lang"], "banned"))
        return False
    if not user["is_subscribed"]:
        subscribed = await is_subscribed(user_id)
        if not subscribed:
            await message.answer(
                t(user["lang"], "subscribe_required", channel=CHANNEL_USERNAME),
                reply_markup=kb.subscribe_keyboard(user["lang"])
            )
            return False
        db.set_user_subscribed(user_id, True)
    return True


# ============================================================
#                E'LON JOYLASHTIRISH (BOSQICHMA-BOSQICH)
# ============================================================

@router.message(F.text.in_([t("uz", "btn_add_listing"), t("ru", "btn_add_listing")]))
async def add_listing_start(message: Message, state: FSMContext):
    if not await guard(message):
        return
    lang = db.get_user(message.from_user.id)["lang"]
    await state.clear()
    await state.update_data(lang=lang)
    TEMP_PHOTOS[message.from_user.id] = []
    await message.answer(t(lang, "ad_template"), reply_markup=kb.main_menu_keyboard(lang))
    await state.set_state(AddListing.brand)
    await message.answer(t(lang, "ask_brand"))


@router.message(AddListing.brand, F.text)
async def listing_brand(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(brand=message.text.strip())
    await state.set_state(AddListing.model)
    await message.answer(t(lang, "ask_model"))


@router.message(AddListing.model, F.text)
async def listing_model(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(model=message.text.strip())
    await state.set_state(AddListing.year)
    await message.answer(t(lang, "ask_year"))


@router.message(AddListing.year, F.text)
async def listing_year(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    year_text = message.text.strip()
    digits = "".join(ch for ch in year_text if ch.isdigit())
    if len(digits) != 4:
        await message.answer(t(lang, "invalid_year"))
        return
    await state.update_data(year=digits)
    await state.set_state(AddListing.mileage)
    await message.answer(t(lang, "ask_mileage"))


@router.message(AddListing.mileage, F.text)
async def listing_mileage(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(mileage=message.text.strip())
    await state.set_state(AddListing.battery)
    await message.answer(t(lang, "ask_battery"))


@router.message(AddListing.battery, F.text)
async def listing_battery(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(battery_capacity=message.text.strip())
    await state.set_state(AddListing.range_km)
    await message.answer(t(lang, "ask_range"))


@router.message(AddListing.range_km, F.text)
async def listing_range(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(range_km=message.text.strip())
    await state.set_state(AddListing.condition)
    await message.answer(t(lang, "ask_condition"))


@router.message(AddListing.condition, F.text)
async def listing_condition(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(condition=message.text.strip())
    await state.set_state(AddListing.price)
    await message.answer(t(lang, "ask_price"))


@router.message(AddListing.price, F.text)
async def listing_price(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    await state.update_data(price=message.text.strip())
    await state.set_state(AddListing.region)
    await message.answer(t(lang, "ask_region"), reply_markup=kb.regions_keyboard())


@router.callback_query(AddListing.region, F.data.startswith("selreg_"))
async def listing_region_selected(callback: CallbackQuery, state: FSMContext):
    region_idx = int(callback.data.split("_")[1])
    region_name = REGION_NAMES[region_idx]
    await state.update_data(region=region_name, region_idx=region_idx)
    fsm_data = await state.get_data()
    lang = fsm_data.get("lang", "uz")
    await state.set_state(AddListing.district)
    await callback.message.answer(t(lang, "ask_district"), reply_markup=kb.districts_keyboard(region_idx))
    await callback.answer()


@router.callback_query(AddListing.district, F.data.startswith("seldist_"))
async def listing_district_selected(callback: CallbackQuery, state: FSMContext):
    _, region_idx_s, dist_idx_s = callback.data.split("_")
    region_idx, dist_idx = int(region_idx_s), int(dist_idx_s)
    region_name = REGION_NAMES[region_idx]
    district_name = REGIONS[region_name][dist_idx]
    await state.update_data(district=district_name)
    fsm_data = await state.get_data()
    lang = fsm_data.get("lang", "uz")

    if fsm_data.get("in_edit_mode"):
        await state.update_data(in_edit_mode=False)
        await callback.message.answer(t(lang, "field_updated"))
        await show_add_listing_preview(callback.message, state, callback.from_user.id)
    else:
        await state.set_state(AddListing.extra)
        await callback.message.answer(t(lang, "ask_extra"), reply_markup=kb.skip_keyboard(lang))
    await callback.answer()


@router.message(AddListing.extra, F.text)
async def listing_extra(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    extra = "" if message.text.strip() == t(lang, "skip_btn") else message.text.strip()
    await state.update_data(extra_info=extra)
    await state.set_state(AddListing.photos)
    await message.answer(t(lang, "send_photos", max=MAX_PHOTOS), reply_markup=kb.finish_photos_keyboard(lang))


@router.message(AddListing.photos, F.photo)
async def listing_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    photos = TEMP_PHOTOS.setdefault(message.from_user.id, [])
    if len(photos) >= MAX_PHOTOS:
        await message.answer(t(lang, "photo_limit", max=MAX_PHOTOS))
        return
    photos.append(message.photo[-1].file_id)
    await message.answer(t(lang, "photo_added", count=len(photos), max=MAX_PHOTOS))


async def show_add_listing_preview(message: Message, state: FSMContext, user_id: int):
    """E'lonni oldindan ko'rish (tasdiqlash/tahrirlash bosqichida qayta-qayta chaqiriladi)"""
    fsm_data = await state.get_data()
    lang = fsm_data.get("lang", "uz")

    # Raqamli maydonlarga avtomatik birlik qo'shamiz va state'ni yangilaymiz
    normalized = normalize_listing_numeric_fields(fsm_data, lang)
    await state.update_data(**{
        k: normalized[k] for k in ("mileage", "range_km", "battery_capacity", "price")
    })

    photos = TEMP_PHOTOS.get(user_id, [])
    user = db.get_user(user_id)
    caption = format_listing_caption(normalized, lang, phone=user["phone"] if user else None)

    await state.set_state(AddListing.confirming)
    await message.answer(t(lang, "ad_preview"))

    media = [InputMediaPhoto(media=p) for p in photos]
    media[0] = InputMediaPhoto(
    media=media[0].media,
    caption=caption,
    parse_mode="HTML"
)
    media[0].parse_mode = "HTML"
    await bot.send_media_group(message.chat.id, media)

    await message.answer(t(lang, "confirm_question"), reply_markup=kb.confirm_listing_keyboard(lang))


@router.message(AddListing.photos, F.text.in_([t("uz", "finish_photos"), t("ru", "finish_photos")]))
async def listing_photos_done(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    photos = TEMP_PHOTOS.get(message.from_user.id, [])
    if len(photos) < MIN_PHOTOS:
        await message.answer(t(lang, "need_at_least_one_photo"))
        return
    await show_add_listing_preview(message, state, message.from_user.id)


@router.callback_query(AddListing.confirming, F.data == "ad_cancel")
async def add_listing_cancel(callback: CallbackQuery, state: FSMContext):
    fsm_data = await state.get_data()
    lang = fsm_data.get("lang", "uz")
    TEMP_PHOTOS.pop(callback.from_user.id, None)
    await state.clear()
    await callback.message.answer(t(lang, "cancel"))
    await send_main_menu(callback.message, lang)


# ---- Tahrirlash (e'lon joylashtirish bosqichida, hali yuborilmasdan oldin) ----

@router.callback_query(AddListing.confirming, F.data == "ad_edit")
async def add_listing_edit_start(callback: CallbackQuery, state: FSMContext):
    fsm_data = await state.get_data()
    lang = fsm_data.get("lang", "uz")
    await callback.message.answer(
        t(lang, "choose_field_to_edit"),
        reply_markup=kb.edit_fields_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(AddListing.confirming, F.data == "ad_edit_field_back")
async def add_listing_edit_back(callback: CallbackQuery, state: FSMContext):
    await show_add_listing_preview(callback.message, state, callback.from_user.id)
    await callback.answer()


@router.callback_query(AddListing.confirming, F.data.startswith("ad_edit_field_"))
async def add_listing_edit_field_chosen(callback: CallbackQuery, state: FSMContext):
    field = callback.data[len("ad_edit_field_"):]
    fsm_data = await state.get_data()
    lang = fsm_data.get("lang", "uz")

    if field == "photos":
        TEMP_PHOTOS[callback.from_user.id] = []
        await state.set_state(AddListing.photos)
        await callback.message.answer(
            t(lang, "send_photos", max=MAX_PHOTOS),
            reply_markup=kb.finish_photos_keyboard(lang)
        )
        await callback.answer()
        return

    if field == "region":
        await state.update_data(in_edit_mode=True)
        await state.set_state(AddListing.region)
        await callback.message.answer(t(lang, "ask_region"), reply_markup=kb.regions_keyboard())
        await callback.answer()
        return

    if field == "district":
        region_idx = fsm_data.get("region_idx", 0)
        await state.update_data(in_edit_mode=True)
        await state.set_state(AddListing.district)
        await callback.message.answer(t(lang, "ask_district"), reply_markup=kb.districts_keyboard(region_idx))
        await callback.answer()
        return

    await state.update_data(editing_field=field)
    await state.set_state(AddListing.editing_value)
    await callback.message.answer(t(lang, "enter_new_value"))
    await callback.answer()


@router.message(AddListing.editing_value, F.text)
async def add_listing_edit_value_received(message: Message, state: FSMContext):
    fsm_data = await state.get_data()
    lang = fsm_data.get("lang", "uz")
    field = fsm_data.get("editing_field")

    value = message.text.strip()
    if field == "year":
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) != 4:
            await message.answer(t(lang, "invalid_year"))
            return
        value = digits

    await state.update_data(**{field: value})
    await message.answer(t(lang, "field_updated"))
    await show_add_listing_preview(message, state, message.from_user.id)


@router.callback_query(AddListing.confirming, F.data == "ad_submit")
async def add_listing_submit(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    fsm_data = await state.get_data()
    lang = fsm_data.get("lang", "uz")
    photos = TEMP_PHOTOS.get(user_id, [])

    if len(photos) < MIN_PHOTOS:
        await callback.message.answer(t(lang, "need_at_least_one_photo"))
        await callback.answer()
        return

    listing_data = {
        "brand": fsm_data.get("brand"), "model": fsm_data.get("model"),
        "year": fsm_data.get("year"), "mileage": fsm_data.get("mileage"),
        "battery_capacity": fsm_data.get("battery_capacity"),
        "range_km": fsm_data.get("range_km"), "condition": fsm_data.get("condition"),
        "price": fsm_data.get("price"), "region": fsm_data.get("region"),
        "district": fsm_data.get("district"), "extra_info": fsm_data.get("extra_info"),
    }
    listing_id = db.create_listing(user_id, listing_data, photos)

    await state.clear()
    await callback.message.answer(t(lang, "ad_sent_to_review"))
    await send_main_menu(callback.message, lang)

    # Adminga yuborish - ADMINGA FOYDALANUVCHINING HAQIQIY RAQAMI ko'rinadi
    user = db.get_user(user_id)

    for admin_id in ADMIN_IDS:
        try:
            admin_user = db.get_user(admin_id)
            admin_lang = admin_user["lang"] if admin_user else "uz"
            caption = format_listing_caption(listing_data, admin_lang, phone=user["phone"])
            caption += f"\n\n🆔 ID: {listing_id}\n👤 User: {user_id} (@{callback.from_user.username or '-'})"
            media = [InputMediaPhoto(media=p) for p in photos]
            media[0].caption = caption
            media[0].parse_mode = "HTML"
            await bot.send_media_group(admin_id, media)
            await bot.send_message(
                admin_id, t(admin_lang, "adm_choose_action"),
                reply_markup=kb.admin_listing_keyboard(listing_id, admin_lang)
            )
        except Exception as e:
            logger.warning(f"Could not send to admin {admin_id}: {e}")

    TEMP_PHOTOS.pop(user_id, None)


# ============================================================
#                ADMIN: E'LONLARNI BOSHQARISH
# ============================================================

@router.callback_query(F.data.startswith("adm_approve_"))
async def admin_approve(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    admin_user = db.get_user(callback.from_user.id)
    admin_lang = admin_user["lang"] if admin_user else "uz"

    listing_id = int(callback.data.split("_")[-1])
    listing = db.get_listing(listing_id)
    if not listing or listing["status"] != "pending":
        await callback.answer(t(admin_lang, "adm_listing_already_handled"), show_alert=True)
        return

    db.set_listing_status(listing_id, "approved")
    user = db.get_user(listing["user_id"])
    lang = user["lang"] if user else "uz"

    data = listing_dict_from_row(listing)
    # KANALGA — kanal egasining (umumiy) raqami chiqadi, userniki emas
    caption = format_listing_caption(data, lang, vip=bool(listing["is_vip"]), phone=OWNER_PHONE)
    photos = listing["photos"].split(",")

    media = [InputMediaPhoto(media=p) for p in photos]
    media[0].caption = caption
    media[0].parse_mode = "HTML"
    sent = await bot.send_media_group(CHANNEL_ID, media)
    channel_msg_id = sent[0].message_id
    db.set_listing_channel_msg(listing_id, channel_msg_id)

    if listing["is_vip"]:
        try:
            await bot.pin_chat_message(CHANNEL_ID, channel_msg_id, disable_notification=True)
        except Exception as e:
            logger.warning(f"Could not pin channel message: {e}")

    channel_uname = CHANNEL_USERNAME.replace("@", "")
    link = f"https://t.me/{channel_uname}/{channel_msg_id}"

    try:
        await bot.send_message(listing["user_id"], t(lang, "ad_approved_user", link=link))
    except Exception as e:
        logger.warning(f"Cannot notify user: {e}")

    await callback.message.answer(t(admin_lang, "adm_listing_approved", id=listing_id))
    await callback.answer()


@router.callback_query(F.data.startswith("adm_reject_"))
async def admin_reject_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    admin_user = db.get_user(callback.from_user.id)
    admin_lang = admin_user["lang"] if admin_user else "uz"

    listing_id = int(callback.data.split("_")[-1])
    listing = db.get_listing(listing_id)
    if not listing or listing["status"] != "pending":
        await callback.answer(t(admin_lang, "adm_listing_already_handled"), show_alert=True)
        return

    await state.set_state(AdminFlow.rejecting)
    await state.update_data(rejecting_listing_id=listing_id)
    await callback.message.answer(t(admin_lang, "ask_reject_reason"))
    await callback.answer()


@router.message(AdminFlow.rejecting, F.text)
async def admin_reject_reason_received(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    admin_user = db.get_user(message.from_user.id)
    admin_lang = admin_user["lang"] if admin_user else "uz"

    fsm_data = await state.get_data()
    listing_id = fsm_data.get("rejecting_listing_id")
    listing = db.get_listing(listing_id)
    await state.clear()

    if not listing or listing["status"] != "pending":
        await message.answer(t(admin_lang, "adm_listing_already_handled"))
        return

    reason = message.text.strip()
    db.reject_listing(listing_id, reason)

    user = db.get_user(listing["user_id"])
    lang = user["lang"] if user else "uz"
    try:
        await bot.send_message(listing["user_id"], t(lang, "ad_rejected_user", reason=reason))
    except Exception:
        pass

    await message.answer(t(admin_lang, "reject_reason_saved", id=listing_id))


@router.callback_query(F.data.startswith("adm_vip_"))
async def admin_vip(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    admin_user = db.get_user(callback.from_user.id)
    admin_lang = admin_user["lang"] if admin_user else "uz"

    listing_id = int(callback.data.split("_")[-1])
    db.set_listing_vip(listing_id, True)

    listing = db.get_listing(listing_id)
    if listing and listing["status"] == "approved" and listing["channel_message_id"]:
        try:
            await bot.pin_chat_message(CHANNEL_ID, listing["channel_message_id"], disable_notification=True)
        except Exception as e:
            logger.warning(f"Could not pin channel message: {e}")

    await callback.message.answer(t(admin_lang, "adm_listing_vip_done", id=listing_id))
    await callback.answer()


# ============================================================
#                       ADMIN PANEL
# ============================================================

@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    admin_user = db.get_user(message.from_user.id)
    admin_lang = admin_user["lang"] if admin_user else "uz"
    await state.clear()
    await message.answer(t(admin_lang, "adm_panel_title"), reply_markup=kb.admin_panel_keyboard(admin_lang))


@router.callback_query(F.data == "adm_pending")
async def admin_pending(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    admin_user = db.get_user(callback.from_user.id)
    admin_lang = admin_user["lang"] if admin_user else "uz"

    listings = db.get_pending_listings()
    if not listings:
        await callback.message.answer(t(admin_lang, "adm_no_pending"))
        await callback.answer()
        return
    for listing in listings:
        data = listing_dict_from_row(listing)
        user = db.get_user(listing["user_id"])
        caption = format_listing_caption(data, admin_lang, phone=user["phone"] if user else None)
        caption += f"\n\n🆔 ID: {listing['id']}\n👤 User: {listing['user_id']}"
        photos = listing["photos"].split(",")
        media = [InputMediaPhoto(media=p) for p in photos]
        media[0].caption = caption
        media[0].parse_mode = "HTML"
        await bot.send_media_group(callback.message.chat.id, media)
        await callback.message.answer(
            t(admin_lang, "adm_choose_action"),
            reply_markup=kb.admin_listing_keyboard(listing["id"], admin_lang)
        )
    await callback.answer()


@router.callback_query(F.data == "adm_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    admin_user = db.get_user(callback.from_user.id)
    admin_lang = admin_user["lang"] if admin_user else "uz"

    users = db.get_users_stats()
    listings = db.get_listings_stats()
    top_brands = db.get_top_brands(limit=5)
    top_regions = db.get_top_regions(limit=5)
    top_users = db.get_top_active_users(limit=5)
    ta = t(admin_lang, "stats_ta_suffix")

    text = (
        f"{t(admin_lang, 'stats_title')}\n\n"
        f"{t(admin_lang, 'stats_total_users')}: <b>{users['total']}</b>\n"
        f"{t(admin_lang, 'stats_new_today')}: <b>{users['new_today']}</b>\n"
        f"{t(admin_lang, 'stats_subscribed')}: <b>{users['subscribed']}</b>\n"
        f"{t(admin_lang, 'stats_banned')}: <b>{users['banned']}</b>\n\n"
        f"{t(admin_lang, 'stats_total_listings')}: <b>{listings['total']}</b>\n"
        f"{t(admin_lang, 'stats_today_listings')}: <b>{listings['today']}</b>\n"
        f"{t(admin_lang, 'stats_approved')}: <b>{listings['approved']}</b>\n"
        f"{t(admin_lang, 'stats_pending')}: <b>{listings['pending']}</b>\n"
        f"{t(admin_lang, 'stats_rejected')}: <b>{listings['rejected']}</b>\n"
        f"{t(admin_lang, 'stats_vip')}: <b>{listings['vip']}</b>\n"
    )

    if top_brands:
        text += f"\n{t(admin_lang, 'stats_top_brands')}:\n"
        for i, row in enumerate(top_brands, 1):
            text += f"{i}. {row['brand']} — {row['cnt']} {ta}\n"

    if top_regions:
        text += f"\n{t(admin_lang, 'stats_top_regions')}:\n"
        for i, row in enumerate(top_regions, 1):
            text += f"{i}. {row['region']} — {row['cnt']} {ta}\n"

    if top_users:
        listing_suffix = t(admin_lang, "stats_listing_suffix")
        text += f"\n{t(admin_lang, 'stats_top_users')}:\n"
        for i, row in enumerate(top_users, 1):
            uname = f"@{row['username']}" if row["username"] else (row["full_name"] or str(row["user_id"]))
            text += f"{i}. {uname} — {row['cnt']} {listing_suffix}\n"

    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data == "adm_broadcast")
async def admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    admin_user = db.get_user(callback.from_user.id)
    admin_lang = admin_user["lang"] if admin_user else "uz"
    await state.set_state(AdminFlow.broadcasting)
    await callback.message.answer(t(admin_lang, "adm_enter_broadcast"))
    await callback.answer()


@router.callback_query(F.data == "adm_ban")
async def admin_ban_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    admin_user = db.get_user(callback.from_user.id)
    admin_lang = admin_user["lang"] if admin_user else "uz"
    await state.set_state(AdminFlow.banning)
    await callback.message.answer(t(admin_lang, "adm_enter_ban_id"))
    await callback.answer()


@router.callback_query(F.data == "adm_unban")
async def admin_unban_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    admin_user = db.get_user(callback.from_user.id)
    admin_lang = admin_user["lang"] if admin_user else "uz"
    await state.set_state(AdminFlow.unbanning)
    await callback.message.answer(t(admin_lang, "adm_enter_unban_id"))
    await callback.answer()


@router.message(AdminFlow.banning, F.text)
async def admin_ban_id(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    admin_user = db.get_user(message.from_user.id)
    admin_lang = admin_user["lang"] if admin_user else "uz"
    if not message.text.strip().isdigit():
        await message.answer(t(admin_lang, "adm_only_digits"))
        return
    target_id = int(message.text.strip())
    db.set_user_banned(target_id, True)
    await message.answer(t(admin_lang, "adm_user_banned", id=target_id))
    await state.clear()


@router.message(AdminFlow.unbanning, F.text)
async def admin_unban_id(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    admin_user = db.get_user(message.from_user.id)
    admin_lang = admin_user["lang"] if admin_user else "uz"
    if not message.text.strip().isdigit():
        await message.answer(t(admin_lang, "adm_only_digits"))
        return
    target_id = int(message.text.strip())
    db.set_user_banned(target_id, False)
    await message.answer(t(admin_lang, "adm_user_unbanned", id=target_id))
    await state.clear()


@router.message(AdminFlow.broadcasting)
async def admin_broadcast_send(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    admin_user = db.get_user(message.from_user.id)
    admin_lang = admin_user["lang"] if admin_user else "uz"
    await state.clear()
    user_ids = db.get_all_user_ids()
    sent, failed = 0, 0
    status_msg = await message.answer(t(admin_lang, "adm_broadcasting"))
    for uid in user_ids:
        try:
            await bot.copy_message(uid, message.chat.id, message.message_id)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    await status_msg.edit_text(t(admin_lang, "adm_broadcast_done", sent=sent, failed=failed))


# ============================================================
#        QIDIRUV / VIP E'LONLAR / HUDUD BO'YICHA / PROFIL
# ============================================================

@router.message(F.text.in_([t("uz", "btn_search"), t("ru", "btn_search")]))
async def search_start(message: Message, state: FSMContext):
    if not await guard(message):
        return
    lang = db.get_user(message.from_user.id)["lang"]
    await state.clear()
    await state.set_state(SearchFlow.waiting_brand)
    await message.answer(t(lang, "enter_brand"))


@router.message(SearchFlow.waiting_brand, F.text)
async def search_by_brand(message: Message, state: FSMContext):
    lang = db.get_user(message.from_user.id)["lang"]
    listings = db.get_approved_listings({"brand": message.text.strip()})
    await state.clear()
    await show_listings(message, listings, lang)
    await send_main_menu(message, lang)


@router.message(F.text.in_([t("uz", "btn_vip"), t("ru", "btn_vip")]))
async def vip_listings(message: Message, state: FSMContext):
    if not await guard(message):
        return
    await state.clear()
    lang = db.get_user(message.from_user.id)["lang"]
    listings = db.get_approved_listings({"vip_only": True})
    await show_listings(message, listings, lang)
    await send_main_menu(message, lang)


@router.message(F.text.in_([t("uz", "btn_my_region"), t("ru", "btn_my_region")]))
async def region_search_start(message: Message, state: FSMContext):
    if not await guard(message):
        return
    lang = db.get_user(message.from_user.id)["lang"]
    await state.clear()
    await state.set_state(SearchFlow.waiting_region)
    await message.answer(t(lang, "enter_region"), reply_markup=kb.regions_keyboard())


@router.callback_query(SearchFlow.waiting_region, F.data.startswith("selreg_"))
async def search_by_region(callback: CallbackQuery, state: FSMContext):
    lang = db.get_user(callback.from_user.id)["lang"]
    region_idx = int(callback.data.split("_")[1])
    region_name = REGION_NAMES[region_idx]
    listings = db.get_approved_listings({"region": region_name})
    await state.clear()
    await show_listings(callback.message, listings, lang)
    await send_main_menu(callback.message, lang)
    await callback.answer()


async def show_listings(message: Message, listings, lang):
    await message.answer(t(lang, "search_results", count=len(listings)))
    if not listings:
        await message.answer(t(lang, "no_listings"))
        return
    for listing in listings[:10]:
        data = listing_dict_from_row(listing)
        caption = format_listing_caption(data, lang, vip=bool(listing["is_vip"]), phone=OWNER_PHONE)
        photos = listing["photos"].split(",")
        media = [InputMediaPhoto(media=p) for p in photos[:10]]
        media[0].caption = caption
        media[0].parse_mode = "HTML"
        try:
            await bot.send_media_group(message.chat.id, media)
        except Exception as e:
            logger.warning(f"Error sending listing: {e}")


# ---------------- PROFIL ----------------

@router.message(F.text.in_([t("uz", "btn_profile"), t("ru", "btn_profile")]))
async def profile(message: Message, state: FSMContext):
    if not await guard(message):
        return
    await state.clear()
    user = db.get_user(message.from_user.id)
    lang = user["lang"]
    await message.answer(
        t(lang, "profile_info", id=user["user_id"], phone=user["phone"], lang=user["lang"]),
        reply_markup=kb.profile_keyboard(lang)
    )
    await send_main_menu(message, lang)


@router.callback_query(F.data == "profile_change_lang")
async def profile_change_lang_start(callback: CallbackQuery):
    lang = db.get_user(callback.from_user.id)["lang"]
    await callback.message.answer(t(lang, "choose_new_lang"), reply_markup=kb.profile_lang_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("plang_"))
async def profile_change_lang_done(callback: CallbackQuery):
    new_lang = callback.data.split("_")[1]
    db.set_user_lang(callback.from_user.id, new_lang)
    await callback.message.delete()
    await callback.message.answer(t(new_lang, "lang_changed"))
    await send_main_menu(callback.message, new_lang)
    await callback.answer()


@router.callback_query(F.data == "profile_my_listings")
async def profile_my_listings(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = db.get_user(callback.from_user.id)["lang"]
    await show_my_listings(callback.message, callback.from_user.id, lang)
    await callback.answer()


# ============================================================
#                     MENING E'LONLARIM
# ============================================================

def listing_status_text(lang, status):
    return {
        "pending": t(lang, "status_pending"),
        "approved": t(lang, "status_approved"),
        "rejected": t(lang, "status_rejected"),
    }.get(status, status)


@router.message(F.text.in_([t("uz", "btn_my_listings"), t("ru", "btn_my_listings")]))
async def my_listings(message: Message, state: FSMContext):
    if not await guard(message):
        return
    await state.clear()
    lang = db.get_user(message.from_user.id)["lang"]
    await show_my_listings(message, message.from_user.id, lang)


async def show_my_listings(message: Message, user_id: int, lang: str):
    listings = db.get_user_listings(user_id)

    if not listings:
        await message.answer(t(lang, "my_listings_empty"))
        await send_main_menu(message, lang)
        return

    await message.answer(t(lang, "my_listings_title", count=len(listings)))
    for listing in listings:
        data = listing_dict_from_row(listing)
        caption = format_listing_caption(data, lang, vip=bool(listing["is_vip"]))
        caption += t(lang, "listing_status_line", status=listing_status_text(lang, listing["status"]))
        photos = listing["photos"].split(",")
        media = [InputMediaPhoto(media=p) for p in photos[:10]]
        media[0].caption = caption
        media[0].parse_mode = "HTML"
        try:
            await bot.send_media_group(message.chat.id, media)
        except Exception as e:
            logger.warning(f"Error sending own listing: {e}")
        can_edit = listing["status"] != "approved"
        await message.answer(
            "·",
            reply_markup=kb.my_listing_actions_keyboard(listing["id"], lang, can_edit)
        )
    await send_main_menu(message, lang)


@router.callback_query(F.data.startswith("my_delete_yes_"))
async def my_listing_delete_confirmed(callback: CallbackQuery):
    lang = db.get_user(callback.from_user.id)["lang"]
    listing_id = int(callback.data[len("my_delete_yes_"):])
    listing = db.get_listing(listing_id)
    if listing and listing["user_id"] == callback.from_user.id:
        db.delete_listing(listing_id)
        await callback.message.answer(t(lang, "listing_deleted"))
    await callback.answer()


@router.callback_query(F.data.startswith("my_delete_no_"))
async def my_listing_delete_cancelled(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data.startswith("my_delete_"))
async def my_listing_delete_start(callback: CallbackQuery):
    lang = db.get_user(callback.from_user.id)["lang"]
    listing_id = int(callback.data[len("my_delete_"):])
    listing = db.get_listing(listing_id)
    if not listing or listing["user_id"] != callback.from_user.id:
        await callback.answer()
        return
    await callback.message.answer(
        t(lang, "confirm_delete"),
        reply_markup=kb.confirm_delete_keyboard(listing_id, lang)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("my_edit_"))
async def my_listing_edit_start(callback: CallbackQuery):
    lang = db.get_user(callback.from_user.id)["lang"]
    listing_id = int(callback.data[len("my_edit_"):])
    listing = db.get_listing(listing_id)
    if not listing or listing["user_id"] != callback.from_user.id:
        await callback.answer()
        return
    if listing["status"] == "approved":
        await callback.answer(t(lang, "cannot_edit_approved"), show_alert=True)
        return
    await callback.message.answer(
        t(lang, "choose_field_to_edit"),
        reply_markup=kb.my_listing_edit_fields_keyboard(lang, listing_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("my_field_"))
async def my_listing_edit_field_chosen(callback: CallbackQuery, state: FSMContext):
    # callback_data format: my_field_{listing_id}_{field_or_back}
    rest = callback.data[len("my_field_"):]
    listing_id_str, _, field = rest.partition("_")
    listing_id = int(listing_id_str)
    lang = db.get_user(callback.from_user.id)["lang"]

    listing = db.get_listing(listing_id)
    if not listing or listing["user_id"] != callback.from_user.id:
        await callback.answer()
        return

    if field == "back":
        await callback.answer()
        return

    if field == "photos":
        TEMP_PHOTOS[callback.from_user.id] = []
        await state.set_state(MyListings.editing_photos)
        await state.update_data(my_editing_listing_id=listing_id)
        await callback.message.answer(
            t(lang, "send_photos", max=MAX_PHOTOS),
            reply_markup=kb.finish_photos_keyboard(lang)
        )
        await callback.answer()
        return

    if field == "region":
        await state.update_data(my_editing_listing_id=listing_id)
        await state.set_state(MyListings.region)
        await callback.message.answer(t(lang, "ask_region"), reply_markup=kb.regions_keyboard())
        await callback.answer()
        return

    if field == "district":
        region_idx = find_region_index(listing["region"])
        await state.update_data(my_editing_listing_id=listing_id)
        if region_idx is None:
            # Eski e'londa viloyat ro'yxatdagilarga mos kelmasa, avval viloyatni so'raymiz
            await state.set_state(MyListings.region)
            await callback.message.answer(t(lang, "ask_region"), reply_markup=kb.regions_keyboard())
        else:
            await state.set_state(MyListings.district)
            await callback.message.answer(t(lang, "ask_district"), reply_markup=kb.districts_keyboard(region_idx))
        await callback.answer()
        return

    await state.set_state(MyListings.editing_value)
    await state.update_data(my_editing_listing_id=listing_id, my_editing_field=field)
    await callback.message.answer(t(lang, "enter_new_value"))
    await callback.answer()


@router.callback_query(MyListings.region, F.data.startswith("selreg_"))
async def my_listing_region_selected(callback: CallbackQuery, state: FSMContext):
    region_idx = int(callback.data.split("_")[1])
    lang = db.get_user(callback.from_user.id)["lang"]
    await state.set_state(MyListings.district)
    await callback.message.answer(t(lang, "ask_district"), reply_markup=kb.districts_keyboard(region_idx))
    await callback.answer()


@router.callback_query(MyListings.district, F.data.startswith("seldist_"))
async def my_listing_district_selected(callback: CallbackQuery, state: FSMContext):
    _, region_idx_s, dist_idx_s = callback.data.split("_")
    region_idx, dist_idx = int(region_idx_s), int(dist_idx_s)
    region_name = REGION_NAMES[region_idx]
    district_name = REGIONS[region_name][dist_idx]
    lang = db.get_user(callback.from_user.id)["lang"]

    fsm_data = await state.get_data()
    listing_id = fsm_data.get("my_editing_listing_id")
    await state.clear()

    listing = db.get_listing(listing_id)
    if not listing or listing["user_id"] != callback.from_user.id:
        await callback.answer()
        return

    db.update_listing_field(listing_id, "region", region_name)
    db.update_listing_field(listing_id, "district", district_name)
    if listing["status"] == "rejected":
        db.set_listing_status(listing_id, "pending")

    await callback.message.answer(t(lang, "field_updated"))
    await send_main_menu(callback.message, lang)
    await callback.answer()


@router.message(MyListings.editing_value, F.text)
async def my_listing_edit_value_received(message: Message, state: FSMContext):
    lang = db.get_user(message.from_user.id)["lang"]
    fsm_data = await state.get_data()
    listing_id = fsm_data.get("my_editing_listing_id")
    field = fsm_data.get("my_editing_field")
    await state.clear()

    listing = db.get_listing(listing_id)
    if not listing or listing["user_id"] != message.from_user.id:
        return

    value = message.text.strip()
    if field == "year":
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) != 4:
            await message.answer(t(lang, "invalid_year"))
            return
        value = digits
    elif field == "mileage":
        value = append_unit_if_missing(value, t(lang, "unit_km"))
    elif field == "range_km":
        value = append_unit_if_missing(value, t(lang, "unit_km"))
    elif field == "battery_capacity":
        value = append_unit_if_missing(value, t(lang, "unit_kwt"))
    elif field == "price":
        value = append_unit_if_missing(value, t(lang, "unit_usd"))

    db.update_listing_field(listing_id, field, value)
    # Tahrirlangach e'lon yana moderatsiyaga qaytadi (allaqachon rad etilgan bo'lsa)
    if listing["status"] == "rejected":
        db.set_listing_status(listing_id, "pending")
    await message.answer(t(lang, "field_updated"))
    await send_main_menu(message, lang)


@router.message(MyListings.editing_photos, F.photo)
async def my_listing_edit_photo_received(message: Message, state: FSMContext):
    lang = db.get_user(message.from_user.id)["lang"]
    photos = TEMP_PHOTOS.setdefault(message.from_user.id, [])
    if len(photos) >= MAX_PHOTOS:
        await message.answer(t(lang, "photo_limit", max=MAX_PHOTOS))
        return
    photos.append(message.photo[-1].file_id)
    await message.answer(t(lang, "photo_added", count=len(photos), max=MAX_PHOTOS))


@router.message(MyListings.editing_photos, F.text.in_([t("uz", "finish_photos"), t("ru", "finish_photos")]))
async def my_listing_edit_photos_done(message: Message, state: FSMContext):
    lang = db.get_user(message.from_user.id)["lang"]
    fsm_data = await state.get_data()
    listing_id = fsm_data.get("my_editing_listing_id")
    photos = TEMP_PHOTOS.get(message.from_user.id, [])

    if len(photos) < MIN_PHOTOS:
        await message.answer(t(lang, "need_at_least_one_photo"))
        return

    listing = db.get_listing(listing_id)
    if not listing or listing["user_id"] != message.from_user.id:
        await state.clear()
        TEMP_PHOTOS.pop(message.from_user.id, None)
        return

    db.update_listing_field(listing_id, "photos", ",".join(photos))
    if listing["status"] == "rejected":
        db.set_listing_status(listing_id, "pending")

    TEMP_PHOTOS.pop(message.from_user.id, None)
    await state.clear()
    await message.answer(t(lang, "field_updated"))
    await send_main_menu(message, lang)


# ---------------- ISHGA TUSHIRISH ----------------

async def main():
    db.init_db()
    logger.info("Bot ishga tushdi...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
