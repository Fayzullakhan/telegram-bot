# texts.py
# Ikki tilli (O'zbek / Rus) matnlar shu yerda saqlanadi

TEXTS = {
    "uz": {
        "choose_lang": "Tilni tanlang / Выберите язык:",
        "send_phone": "📞 Iltimos, telefon raqamingizni yuboring (tugmani bosing):",
        "phone_button": "📞 Raqamni yuborish",
        "send_location": "📍 Endi joylashuvingizni yuboring:",
        "location_button": "📍 Lokatsiyani yuborish",
        "subscribe_required": (
            "❗️ Botdan foydalanish uchun avval kanalimizga a'zo bo'ling:\n{channel}\n\n"
            "A'zo bo'lgach, pastdagi «✅ Tekshirish» tugmasini bosing."
        ),
        "check_sub": "✅ Tekshirish",
        "sub_ok": "✅ Tabriklaymiz! Endi botdan to'liq foydalanishingiz mumkin.",
        "sub_fail": "❌ Siz hali kanalga a'zo bo'lmagansiz. Iltimos, avval a'zo bo'ling.",
        "main_menu": "🏠 Asosiy menyu. Kerakli bo'limni tanlang:",
        "btn_add_listing": "🚗 E'lon joylashtirish",
        "btn_search": "🔍 Qidiruv",
        "btn_vip": "⭐ VIP e'lonlar",
        "btn_my_region": "📍 Hudud bo'yicha",
        "btn_profile": "👤 Profil",
        "ad_template": "🚗 Yangi elektromobil e'loni joylashtiramiz. Savollarga birma-bir javob bering.",
        "ask_brand": "1️⃣ Avtomobil markasini kiriting (masalan: Tesla):",
        "ask_model": "2️⃣ Modelini kiriting (masalan: Model 3):",
        "ask_year": "3️⃣ Ishlab chiqarilgan yilini kiriting (masalan: 2022):",
        "ask_mileage": "4️⃣ Probegini kiriting, km da (masalan: 25000 km):",
        "ask_battery": "5️⃣ Batareya sig'imini kiriting, kWt da (masalan: 75 kWt):",
        "ask_range": "6️⃣ Bir marta zaryadlashdagi zapas hodini kiriting, km (masalan: 500 km):",
        "ask_condition": "7️⃣ Avtomobil holatini kiriting (masalan: Yangidek, O'rtacha, Yaxshi):",
        "ask_price": "8️⃣ Narxini kiriting (masalan: 35000 $):",
        "ask_region": "9️⃣ Qaysi viloyatda joylashgan? (masalan: Toshkent):",
        "ask_district": "🔟 Qaysi tumanda joylashgan? (masalan: Yunusobod):",
        "ask_extra": "✏️ Qo'shimcha ma'lumot kiriting (kafolat, paket va h.k.). O'tkazib yuborish uchun «➡️ O'tkazish» tugmasini bosing:",
        "skip_btn": "➡️ O'tkazish",
        "invalid_year": "❌ Yilni faqat raqamlarda kiriting (masalan: 2022).",
        "send_photos": (
            "📸 Endi avtomobil rasmlarini yuboring (1 tadan {max} tagacha).\n"
            "Rasmlarni yuborib bo'lgach, «✅ Tugatish» tugmasini bosing."
        ),
        "finish_photos": "✅ Tugatish",
        "photo_added": "✅ Rasm qabul qilindi ({count}/{max})",
        "photo_limit": "❗️ Maksimal {max} ta rasm yuklash mumkin.",
        "need_at_least_one_photo": "❗️ Kamida 1 ta rasm yuklashingiz kerak.",
        "ad_preview": "👀 E'loningiz ko'rinishi shunday bo'ladi:",
        "send_for_review": "📤 Tasdiqlashga yuborish",
        "cancel": "❌ Bekor qilish",
        "ad_sent_to_review": "✅ E'loningiz moderatsiyaga yuborildi. Tasdiqlangach xabar beramiz.",
        "ad_approved_user": "✅ Tabriklaymiz! E'loningiz tasdiqlandi va kanalga joylandi:\n{link}",
        "ad_rejected_user": "❌ Afsuski, e'loningiz rad etildi. Sabab: {reason}",
        "no_listings": "😔 Hozircha mos e'lonlar topilmadi.",
        "back": "⬅️ Orqaga",
        "profile_info": (
            "👤 Profil ma'lumotlari:\n\n"
            "🆔 ID: {id}\n"
            "📞 Tel: {phone}\n"
            "🌐 Til: {lang}\n"
        ),
        "enter_brand": "🔎 Qidirish uchun marka nomini kiriting (masalan: Tesla):",
        "enter_region": "📍 Hudud (viloyat) nomini kiriting:",
        "search_results": "🔎 Topilgan e'lonlar: {count} ta",
        "banned": "🚫 Siz botdan foydalanish huquqidan mahrum qilingansiz.",

        # ---- Tasdiqlash / tahrirlash (e'lon joylashda) ----
        "confirm_question": "✅ Ma'lumotlar to'g'rimi? Tasdiqlaysizmi yoki tahrirlashni xohlaysizmi?",
        "edit_btn": "✏️ Tahrirlash",
        "choose_field_to_edit": "✏️ Qaysi ma'lumotni tahrirlamoqchisiz?",
        "field_brand": "🚗 Marka",
        "field_model": "🚘 Model",
        "field_year": "📅 Yil",
        "field_mileage": "🛣 Probeg",
        "field_battery": "🔋 Batareya",
        "field_range": "⚡️ Zapas hodi",
        "field_condition": "🛠 Holati",
        "field_price": "💰 Narxi",
        "field_region": "📍 Viloyat",
        "field_district": "📍 Tuman",
        "field_extra": "📝 Qo'shimcha",
        "field_photos": "📸 Rasmlar",
        "enter_new_value": "✏️ Yangi qiymatni kiriting:",
        "field_updated": "✅ Yangilandi.",
        "back_to_preview": "⬅️ Ko'rib chiqishga qaytish",

        # ---- Reject sababi ----
        "ask_reject_reason": "✏️ Rad etish sababini yozing:",
        "reject_reason_saved": "❌ E'lon #{id} rad etildi.",

        # ---- Mening e'lonlarim ----
        "btn_my_listings": "📂 Mening e'lonlarim",
        "my_listings_empty": "📭 Sizda hali e'lonlar yo'q.",
        "my_listings_title": "📂 Sizning e'lonlaringiz: {count} ta",
        "status_pending": "⏳ Kutilmoqda",
        "status_approved": "✅ Tasdiqlangan",
        "status_rejected": "❌ Rad etilgan",
        "listing_status_line": "\n\nHolati: {status}",
        "delete_btn": "🗑 O'chirish",
        "edit_listing_btn": "✏️ Tahrirlash",
        "confirm_delete": "🗑 Haqiqatan ham bu e'lonni o'chirmoqchimisiz?",
        "confirm_delete_yes": "🗑 Ha, o'chirish",
        "confirm_delete_no": "⬅️ Yo'q, orqaga",
        "listing_deleted": "🗑 E'lon o'chirildi.",
        "cannot_edit_approved": "❗️ Tasdiqlangan e'lonni faqat o'chirish mumkin.",

        # ---- Profil: tilni o'zgartirish ----
        "change_lang_btn": "🌐 Tilni o'zgartirish",
        "choose_new_lang": "🌐 Yangi tilni tanlang:",
        "lang_changed": "✅ Til o'zgartirildi.",

        # ---- Birliklar (avtomatik qo'shiladigan) ----
        "unit_km": "km",
        "unit_kwt": "kWt",
        "unit_usd": "$",

        # ---- Admin panel (ikki tilli) ----
        "adm_pending_btn": "📋 Kutilayotgan e'lonlar",
        "adm_stats_btn": "📊 Statistika",
        "adm_broadcast_btn": "📢 Broadcast",
        "adm_ban_btn": "🚫 Ban",
        "adm_unban_btn": "✅ Unban",
        "adm_panel_title": "🛠 Admin panel",
        "adm_approve_btn": "✅ Tasdiqlash",
        "adm_reject_btn": "❌ Rad etish",
        "adm_vip_btn": "⭐ VIP qilish",
        "adm_no_pending": "📭 Kutilayotgan e'lonlar yo'q.",
        "adm_choose_action": "👇 Amalni tanlang:",
        "adm_enter_broadcast": "📢 Barcha foydalanuvchilarga yuboriladigan xabarni yozing:",
        "adm_enter_ban_id": "🚫 Ban qilish uchun foydalanuvchi ID raqamini yuboring:",
        "adm_enter_unban_id": "✅ Unban qilish uchun foydalanuvchi ID raqamini yuboring:",
        "adm_only_digits": "❌ Faqat ID raqamini yuboring.",
        "adm_user_banned": "🚫 Foydalanuvchi {id} banlandi.",
        "adm_user_unbanned": "✅ Foydalanuvchi {id} unban qilindi.",
        "adm_broadcasting": "📤 Yuborilmoqda...",
        "adm_broadcast_done": "✅ Yuborildi: {sent}\n❌ Yuborilmadi: {failed}",
        "adm_listing_approved": "✅ E'lon #{id} tasdiqlandi va kanalga joylandi.",
        "adm_listing_already_handled": "E'lon topilmadi yoki allaqachon ko'rib chiqilgan.",
        "adm_listing_vip_done": "⭐ E'lon #{id} VIP qilindi.",

        "stats_title": "📊 Umumiy statistika",
        "stats_total_users": "👥 Jami foydalanuvchilar",
        "stats_new_today": "🆕 Bugun qo'shilgan",
        "stats_subscribed": "✅ Obuna bo'lganlar",
        "stats_banned": "🚫 Banlanganlar",
        "stats_total_listings": "📋 Jami e'lonlar",
        "stats_today_listings": "🆕 Bugun joylangan",
        "stats_approved": "✅ Tasdiqlangan",
        "stats_pending": "⏳ Kutilmoqda",
        "stats_rejected": "❌ Rad etilgan",
        "stats_vip": "⭐ VIP",
        "stats_top_brands": "🏆 Eng ko'p sotilayotgan brendlar",
        "stats_top_regions": "📍 Eng faol hududlar",
        "stats_top_users": "🔥 Eng faol foydalanuvchilar",
        "stats_ta_suffix": "ta",
        "stats_listing_suffix": "ta e'lon",
    },
    "ru": {
        "choose_lang": "Tilni tanlang / Выберите язык:",
        "send_phone": "📞 Пожалуйста, отправьте свой номер телефона (нажмите кнопку):",
        "phone_button": "📞 Отправить номер",
        "send_location": "📍 Теперь отправьте вашу локацию:",
        "location_button": "📍 Отправить локацию",
        "subscribe_required": (
            "❗️ Чтобы пользоваться ботом, подпишитесь на наш канал:\n{channel}\n\n"
            "После подписки нажмите кнопку «✅ Проверить»."
        ),
        "check_sub": "✅ Проверить",
        "sub_ok": "✅ Отлично! Теперь вы можете полноценно пользоваться ботом.",
        "sub_fail": "❌ Вы ещё не подписались на канал. Пожалуйста, подпишитесь.",
        "main_menu": "🏠 Главное меню. Выберите раздел:",
        "btn_add_listing": "🚗 Разместить объявление",
        "btn_search": "🔍 Поиск",
        "btn_vip": "⭐ VIP объявления",
        "btn_my_region": "📍 По региону",
        "btn_profile": "👤 Профиль",
        "ad_template": "🚗 Разместим новое объявление об электромобиле. Отвечайте на вопросы по очереди.",
        "ask_brand": "1️⃣ Введите марку автомобиля (например: Tesla):",
        "ask_model": "2️⃣ Введите модель (например: Model 3):",
        "ask_year": "3️⃣ Введите год выпуска (например: 2022):",
        "ask_mileage": "4️⃣ Введите пробег, в км (например: 25000 km):",
        "ask_battery": "5️⃣ Введите ёмкость батареи, в кВт (например: 75 kWt):",
        "ask_range": "6️⃣ Введите запас хода на одной зарядке, км (например: 500 km):",
        "ask_condition": "7️⃣ Введите состояние авто (например: Как новый, Среднее, Хорошее):",
        "ask_price": "8️⃣ Введите цену (например: 35000 $):",
        "ask_region": "9️⃣ В какой области находится? (например: Ташкент):",
        "ask_district": "🔟 В каком районе находится? (например: Юнусабад):",
        "ask_extra": "✏️ Введите доп. информацию (гарантия, пакет и т.д.). Чтобы пропустить — нажмите «➡️ Пропустить»:",
        "skip_btn": "➡️ Пропустить",
        "invalid_year": "❌ Год вводите только цифрами (например: 2022).",
        "send_photos": (
            "📸 Теперь отправьте фото автомобиля (от 1 до {max} штук).\n"
            "После загрузки нажмите «✅ Завершить»."
        ),
        "finish_photos": "✅ Завершить",
        "photo_added": "✅ Фото принято ({count}/{max})",
        "photo_limit": "❗️ Максимум {max} фото.",
        "need_at_least_one_photo": "❗️ Нужно загрузить хотя бы 1 фото.",
        "ad_preview": "👀 Так будет выглядеть ваше объявление:",
        "send_for_review": "📤 Отправить на модерацию",
        "cancel": "❌ Отмена",
        "ad_sent_to_review": "✅ Объявление отправлено на модерацию. Сообщим после проверки.",
        "ad_approved_user": "✅ Поздравляем! Объявление одобрено и опубликовано:\n{link}",
        "ad_rejected_user": "❌ К сожалению, объявление отклонено. Причина: {reason}",
        "no_listings": "😔 Подходящих объявлений не найдено.",
        "back": "⬅️ Назад",
        "profile_info": (
            "👤 Информация профиля:\n\n"
            "🆔 ID: {id}\n"
            "📞 Тел: {phone}\n"
            "🌐 Язык: {lang}\n"
        ),
        "enter_brand": "🔎 Введите марку для поиска (например: Tesla):",
        "enter_region": "📍 Введите название региона:",
        "search_results": "🔎 Найдено объявлений: {count}",
        "banned": "🚫 Вы заблокированы и не можете пользоваться ботом.",

        # ---- Подтверждение / редактирование (при размещении) ----
        "confirm_question": "✅ Данные верны? Подтвердите или отредактируйте.",
        "edit_btn": "✏️ Редактировать",
        "choose_field_to_edit": "✏️ Какое поле хотите отредактировать?",
        "field_brand": "🚗 Марка",
        "field_model": "🚘 Модель",
        "field_year": "📅 Год",
        "field_mileage": "🛣 Пробег",
        "field_battery": "🔋 Батарея",
        "field_range": "⚡️ Запас хода",
        "field_condition": "🛠 Состояние",
        "field_price": "💰 Цена",
        "field_region": "📍 Область",
        "field_district": "📍 Район",
        "field_extra": "📝 Доп. информация",
        "field_photos": "📸 Фото",
        "enter_new_value": "✏️ Введите новое значение:",
        "field_updated": "✅ Обновлено.",
        "back_to_preview": "⬅️ Вернуться к просмотру",

        # ---- Причина отклонения ----
        "ask_reject_reason": "✏️ Напишите причину отклонения:",
        "reject_reason_saved": "❌ Объявление #{id} отклонено.",

        # ---- Мои объявления ----
        "btn_my_listings": "📂 Мои объявления",
        "my_listings_empty": "📭 У вас пока нет объявлений.",
        "my_listings_title": "📂 Ваши объявления: {count}",
        "status_pending": "⏳ На рассмотрении",
        "status_approved": "✅ Одобрено",
        "status_rejected": "❌ Отклонено",
        "listing_status_line": "\n\nСтатус: {status}",
        "delete_btn": "🗑 Удалить",
        "edit_listing_btn": "✏️ Редактировать",
        "confirm_delete": "🗑 Вы действительно хотите удалить это объявление?",
        "confirm_delete_yes": "🗑 Да, удалить",
        "confirm_delete_no": "⬅️ Нет, назад",
        "listing_deleted": "🗑 Объявление удалено.",
        "cannot_edit_approved": "❗️ Одобренное объявление можно только удалить.",

        # ---- Профиль: смена языка ----
        "change_lang_btn": "🌐 Изменить язык",
        "choose_new_lang": "🌐 Выберите новый язык:",
        "lang_changed": "✅ Язык изменён.",

        # ---- Единицы измерения (добавляются автоматически) ----
        "unit_km": "км",
        "unit_kwt": "кВт",
        "unit_usd": "$",

        # ---- Админ-панель (двуязычная) ----
        "adm_pending_btn": "📋 Объявления на рассмотрении",
        "adm_stats_btn": "📊 Статистика",
        "adm_broadcast_btn": "📢 Рассылка",
        "adm_ban_btn": "🚫 Бан",
        "adm_unban_btn": "✅ Разбан",
        "adm_panel_title": "🛠 Админ-панель",
        "adm_approve_btn": "✅ Одобрить",
        "adm_reject_btn": "❌ Отклонить",
        "adm_vip_btn": "⭐ Сделать VIP",
        "adm_no_pending": "📭 Нет объявлений на рассмотрении.",
        "adm_choose_action": "👇 Выберите действие:",
        "adm_enter_broadcast": "📢 Напишите сообщение для рассылки всем пользователям:",
        "adm_enter_ban_id": "🚫 Отправьте ID пользователя для бана:",
        "adm_enter_unban_id": "✅ Отправьте ID пользователя для разбана:",
        "adm_only_digits": "❌ Отправьте только ID (цифрами).",
        "adm_user_banned": "🚫 Пользователь {id} забанен.",
        "adm_user_unbanned": "✅ Пользователь {id} разбанен.",
        "adm_broadcasting": "📤 Отправка...",
        "adm_broadcast_done": "✅ Отправлено: {sent}\n❌ Не отправлено: {failed}",
        "adm_listing_approved": "✅ Объявление #{id} одобрено и опубликовано.",
        "adm_listing_already_handled": "Объявление не найдено или уже рассмотрено.",
        "adm_listing_vip_done": "⭐ Объявление #{id} стало VIP.",

        "stats_title": "📊 Общая статистика",
        "stats_total_users": "👥 Всего пользователей",
        "stats_new_today": "🆕 Добавлено сегодня",
        "stats_subscribed": "✅ Подписаны",
        "stats_banned": "🚫 Забанены",
        "stats_total_listings": "📋 Всего объявлений",
        "stats_today_listings": "🆕 Размещено сегодня",
        "stats_approved": "✅ Одобрено",
        "stats_pending": "⏳ На рассмотрении",
        "stats_rejected": "❌ Отклонено",
        "stats_vip": "⭐ VIP",
        "stats_top_brands": "🏆 Популярные марки",
        "stats_top_regions": "📍 Активные регионы",
        "stats_top_users": "🔥 Активные пользователи",
        "stats_ta_suffix": "шт.",
        "stats_listing_suffix": "объявл.",
    },
}


def t(language, key, **kwargs):
    language = language if language in TEXTS else "uz"
    text = TEXTS[language].get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text