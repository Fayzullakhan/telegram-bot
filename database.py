# database.py
# Supabase (PostgreSQL) bilan ishlash uchun barcha funksiyalar

from datetime import datetime
from supabase import create_client, Client

# ── Supabase ulanish ──────────────────────────────────────────────────────────
SUPABASE_URL = "https://hizhdwjspecoytoqclvn.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhpemhkd2pzcGVjb3l0b3FjbHZuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIxODc3MTQsImV4cCI6MjA5Nzc2MzcxNH0"
    ".c0HeVMFq5fXLRwc21LVpYtyvX10FlnvqXyMsTuBdLs4"
)

_client: Client = None


def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


# ── Jadvallarni yaratish (birinchi ishga tushirishda) ─────────────────────────
def init_db():
    """
    Supabase'da jadvallar SQL orqali yaratiladi.
    Bu funksiya ulanishni tekshiradi.

    Agar jadvallar yo'q bo'lsa, Supabase Dashboard → SQL Editor da quyidagi SQL ni ishga tushiring:

    CREATE TABLE IF NOT EXISTS users (
        user_id       BIGINT PRIMARY KEY,
        full_name     TEXT,
        username      TEXT,
        lang          TEXT DEFAULT 'uz',
        phone         TEXT,
        latitude      DOUBLE PRECISION,
        longitude     DOUBLE PRECISION,
        is_subscribed BOOLEAN DEFAULT FALSE,
        is_banned     BOOLEAN DEFAULT FALSE,
        created_at    TIMESTAMPTZ DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS listings (
        id                 BIGSERIAL PRIMARY KEY,
        user_id            BIGINT,
        brand              TEXT,
        model              TEXT,
        year               TEXT,
        mileage            TEXT,
        battery_capacity   TEXT,
        range_km           TEXT,
        condition          TEXT,
        price              TEXT,
        region             TEXT,
        district           TEXT,
        extra_info         TEXT,
        photos             TEXT,
        status             TEXT DEFAULT 'pending',
        reject_reason      TEXT,
        is_vip             BOOLEAN DEFAULT FALSE,
        channel_message_id BIGINT,
        created_at         TIMESTAMPTZ DEFAULT NOW()
    );
    """
    sb = get_client()
    sb.table("users").select("user_id").limit(1).execute()
    sb.table("listings").select("id").limit(1).execute()


# ── Yordamchi ─────────────────────────────────────────────────────────────────
def _row(data):
    return data[0] if data else None


# ── USERS ─────────────────────────────────────────────────────────────────────

def add_or_update_user(user_id, full_name=None, username=None):
    sb = get_client()
    existing = sb.table("users").select("user_id").eq("user_id", user_id).execute().data
    if not existing:
        sb.table("users").insert({
            "user_id": user_id,
            "full_name": full_name,
            "username": username,
            "created_at": datetime.now().isoformat(),
        }).execute()
    else:
        sb.table("users").update({
            "full_name": full_name,
            "username": username,
        }).eq("user_id", user_id).execute()


def set_user_lang(user_id, lang):
    get_client().table("users").update({"lang": lang}).eq("user_id", user_id).execute()


def set_user_phone(user_id, phone):
    get_client().table("users").update({"phone": phone}).eq("user_id", user_id).execute()


def set_user_location(user_id, lat, lon):
    get_client().table("users").update({
        "latitude": lat,
        "longitude": lon,
    }).eq("user_id", user_id).execute()


def set_user_subscribed(user_id, status: bool):
    get_client().table("users").update({"is_subscribed": status}).eq("user_id", user_id).execute()


def set_user_banned(user_id, status: bool):
    get_client().table("users").update({"is_banned": status}).eq("user_id", user_id).execute()


def get_user(user_id):
    data = get_client().table("users").select("*").eq("user_id", user_id).execute().data
    return _row(data)


def is_user_banned(user_id):
    u = get_user(user_id)
    return bool(u.get("is_banned")) if u else False


def get_all_user_ids():
    data = get_client().table("users").select("user_id").eq("is_banned", False).execute().data
    return [r["user_id"] for r in data]


def get_users_stats():
    sb = get_client()
    total      = len(sb.table("users").select("user_id").execute().data)
    banned     = len(sb.table("users").select("user_id").eq("is_banned", True).execute().data)
    subscribed = len(sb.table("users").select("user_id").eq("is_subscribed", True).execute().data)
    today = datetime.now().strftime("%Y-%m-%d")
    new_today  = len(
        sb.table("users").select("user_id")
        .gte("created_at", f"{today}T00:00:00")
        .lte("created_at", f"{today}T23:59:59")
        .execute().data
    )
    return {"total": total, "banned": banned, "subscribed": subscribed, "new_today": new_today}


def get_top_active_users(limit=5):
    from collections import Counter
    sb = get_client()
    listings = sb.table("listings").select("user_id").execute().data
    counts = Counter(r["user_id"] for r in listings)
    top_ids = [uid for uid, _ in counts.most_common(limit)]
    result = []
    for uid in top_ids:
        u = get_user(uid)
        if u:
            result.append({
                "user_id": uid,
                "cnt": counts[uid],
                "username": u.get("username"),
                "full_name": u.get("full_name"),
                "phone": u.get("phone"),
            })
    return result


# ── LISTINGS ──────────────────────────────────────────────────────────────────

def create_listing(user_id, data: dict, photos: list):
    row = {
        "user_id":          user_id,
        "brand":            data.get("brand"),
        "model":            data.get("model"),
        "year":             data.get("year"),
        "mileage":          data.get("mileage"),
        "battery_capacity": data.get("battery_capacity"),
        "range_km":         data.get("range_km"),
        "condition":        data.get("condition"),
        "price":            data.get("price"),
        "region":           data.get("region"),
        "district":         data.get("district"),
        "extra_info":       data.get("extra_info"),
        "photos":           ",".join(photos),
        "status":           "pending",
        "created_at":       datetime.now().isoformat(),
    }
    resp = get_client().table("listings").insert(row).execute()
    return resp.data[0]["id"] if resp.data else None


def get_listing(listing_id):
    data = get_client().table("listings").select("*").eq("id", listing_id).execute().data
    return _row(data)


def get_pending_listings():
    return (
        get_client().table("listings").select("*")
        .eq("status", "pending").order("id").execute().data
    )


def get_user_listings(user_id):
    return (
        get_client().table("listings").select("*")
        .eq("user_id", user_id).order("id", desc=True).execute().data
    )


def delete_listing(listing_id):
    get_client().table("listings").delete().eq("id", listing_id).execute()


def update_listing_field(listing_id, field, value):
    allowed_fields = {
        "brand", "model", "year", "mileage", "battery_capacity", "range_km",
        "condition", "price", "region", "district", "extra_info", "photos",
    }
    if field not in allowed_fields:
        raise ValueError(f"Field '{field}' tahrirlash uchun ruxsat etilmagan")
    get_client().table("listings").update({field: value}).eq("id", listing_id).execute()


def set_listing_status(listing_id, status):
    get_client().table("listings").update({"status": status}).eq("id", listing_id).execute()


def reject_listing(listing_id, reason):
    get_client().table("listings").update({
        "status":        "rejected",
        "reject_reason": reason,
    }).eq("id", listing_id).execute()


def set_listing_vip(listing_id, is_vip: bool):
    get_client().table("listings").update({"is_vip": is_vip}).eq("id", listing_id).execute()


def set_listing_channel_msg(listing_id, message_id):
    get_client().table("listings").update({
        "channel_message_id": message_id,
    }).eq("id", listing_id).execute()


def get_approved_listings(filters: dict = None):
    sb = get_client()
    q = sb.table("listings").select("*").eq("status", "approved")
    if filters:
        if filters.get("brand"):
            q = q.ilike("brand", f"%{filters['brand']}%")
        if filters.get("region"):
            q = q.ilike("region", f"%{filters['region']}%")
        if filters.get("district"):
            q = q.ilike("district", f"%{filters['district']}%")
        if filters.get("vip_only"):
            q = q.eq("is_vip", True)
    return q.order("is_vip", desc=True).order("id", desc=True).execute().data


def get_listings_stats():
    sb = get_client()
    today = datetime.now().strftime("%Y-%m-%d")
    return {
        "total":    len(sb.table("listings").select("id").execute().data),
        "approved": len(sb.table("listings").select("id").eq("status", "approved").execute().data),
        "pending":  len(sb.table("listings").select("id").eq("status", "pending").execute().data),
        "rejected": len(sb.table("listings").select("id").eq("status", "rejected").execute().data),
        "vip":      len(sb.table("listings").select("id").eq("is_vip", True).execute().data),
        "today":    len(
            sb.table("listings").select("id")
            .gte("created_at", f"{today}T00:00:00")
            .lte("created_at", f"{today}T23:59:59")
            .execute().data
        ),
    }


def get_top_brands(limit=5, status="approved"):
    from collections import Counter
    data = get_client().table("listings").select("brand").eq("status", status).execute().data
    counts = Counter(r["brand"].lower() for r in data if r.get("brand"))
    return [{"brand": b, "cnt": c} for b, c in counts.most_common(limit)]


def get_top_regions(limit=5):
    from collections import Counter
    data = get_client().table("listings").select("region").execute().data
    counts = Counter(r["region"].lower() for r in data if r.get("region"))
    return [{"region": r, "cnt": c} for r, c in counts.most_common(limit)]
