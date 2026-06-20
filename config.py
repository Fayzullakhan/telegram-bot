# config.py
# Botni sozlash uchun barcha asosiy o'zgaruvchilar shu yerda

BOT_TOKEN = "8830330537:AAGUuYz-8smeTXqvKFTlnClVjQQIQIH7BuY"

# Admin(lar) Telegram ID raqamlari (bir nechta bo'lishi mumkin)
ADMIN_IDS = [8768742753,8469134615, 7443915351, 589336241]

# Majburiy obuna kanali (e'lonlar ham shu yerga chiqadi)
CHANNEL_ID = -1002366243994        # kanal ID (raqamli, -100 bilan boshlanadi)
CHANNEL_USERNAME = "@elecktrichka_xayda"  # kanal username (link yasash uchun)
OWNER_PHONE = "+998990007458"
# Moderatsiya / e'lonlar kelib tushadigan admin guruh yoki shaxsiy chat (ixtiyoriy)
ADMIN_REVIEW_CHAT_ID = ADMIN_IDS[0]

DB_PATH = "ev_market.db"

MAX_PHOTOS = 10
MIN_PHOTOS = 1

# O'zbekiston viloyatlari va ularning tumanlari
# (e'lon joylashtirishda / qidiruvda inline tugmalar orqali tanlash uchun)
REGIONS = {
    "Toshkent shahri": [
        "Bektemir", "Chilonzor", "Yashnobod", "Mirobod", "Mirzo Ulug'bek",
        "Sergeli", "Shayxontohur", "Olmazor", "Uchtepa", "Yakkasaroy",
        "Yunusobod", "Yangihayot",
    ],
    "Toshkent viloyati": [
        "Bekobod", "Bo'ka", "Bo'stonliq", "Chinoz", "Qibray", "Ohangaron",
        "Oqqo'rg'on", "Parkent", "Piskent", "Quyichirchiq", "Yuqorichirchiq",
        "Zangiota", "O'rtachirchiq", "Toshkent tumani", "Yangiyo'l", "Nurafshon",
    ],
    "Andijon viloyati": [
        "Andijon shahri", "Andijon tumani", "Asaka", "Baliqchi", "Buloqboshi",
        "Izboskan", "Jalaquduq", "Qo'rg'ontepa", "Marhamat", "Oltinko'l",
        "Paxtaobod", "Shahrixon", "Ulug'nor", "Xo'jaobod", "Bo'z",
    ],
    "Buxoro viloyati": [
        "Buxoro shahri", "Buxoro tumani", "Vobkent", "G'ijduvon", "Jondor",
        "Kogon", "Qorako'l", "Qorovulbozor", "Peshku", "Romitan",
        "Shofirkon", "Olot",
    ],
    "Farg'ona viloyati": [
        "Farg'ona shahri", "Marg'ilon", "Qo'qon", "Beshariq", "Bog'dod",
        "Buvayda", "Dang'ara", "Furqat", "Quva", "Quvasoy", "Rishton",
        "So'x", "Toshloq", "Uchko'prik", "O'zbekiston", "Yozyovon", "Oltiariq",
    ],
    "Jizzax viloyati": [
        "Jizzax shahri", "Arnasoy", "Baxmal", "Do'stlik", "Forish",
        "G'allaorol", "Mirzacho'l", "Paxtakor", "Sharof Rashidov",
        "Yangiobod", "Zafarobod", "Zarbdor", "Zomin",
    ],
    "Xorazm viloyati": [
        "Urganch shahri", "Urganch tumani", "Bog'ot", "Gurlan", "Hazorasp",
        "Xiva", "Xonqa", "Qo'shko'pir", "Shovot", "Yangiariq", "Yangibozor",
    ],
    "Namangan viloyati": [
        "Namangan shahri", "Namangan tumani", "Chortoq", "Chust", "Kosonsoy",
        "Mingbuloq", "Norin", "Pop", "To'raqo'rg'on", "Uchqo'rg'on",
        "Uychi", "Yangiqo'rg'on",
    ],
    "Navoiy viloyati": [
        "Navoiy shahri", "Konimex", "Karmana", "Navbahor", "Nurota",
        "Qiziltepa", "Tomdi", "Uchquduq", "Xatirchi",
    ],
    "Qashqadaryo viloyati": [
        "Qarshi shahri", "Shahrisabz", "Chiroqchi", "Dehqonobod", "G'uzor",
        "Kasbi", "Kitob", "Koson", "Mirishkor", "Muborak", "Nishon",
        "Qamashi", "Yakkabog'",
    ],
    "Samarqand viloyati": [
        "Samarqand shahri", "Samarqand tumani", "Bulung'ur", "Ishtixon",
        "Jomboy", "Kattaqo'rg'on", "Narpay", "Nurobod", "Oqdaryo",
        "Pastdarg'om", "Paxtachi", "Payariq", "Qo'shrabot", "Toyloq", "Urgut",
    ],
    "Sirdaryo viloyati": [
        "Guliston shahri", "Guliston tumani", "Boyovut", "Mirzaobod",
        "Oqoltin", "Sardoba", "Sayxunobod", "Sirdaryo", "Xovos",
        "Yangiyer", "Shirin",
    ],
    "Surxondaryo viloyati": [
        "Termiz shahri", "Termiz tumani", "Angor", "Bandixon", "Boysun",
        "Denov", "Jarqo'rg'on", "Muzrabot", "Oltinsoy", "Qiziriq",
        "Qumqo'rg'on", "Sariosiyo", "Sherobod", "Sho'rchi", "Uzun",
    ],
    "Qoraqalpog'iston Respublikasi": [
        "Nukus shahri", "Nukus tumani", "Amudaryo", "Beruniy", "Chimboy",
        "Ellikqal'a", "Kegeyli", "Qonliko'l", "Qorao'zak", "Qo'ng'irot",
        "Mo'ynoq", "Taxtako'pir", "To'rtko'l", "Xo'jayli", "Shumanay",
    ],
}

REGION_NAMES = list(REGIONS.keys())
