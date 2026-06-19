# database.py
# SQLite bilan ishlash uchun barcha funksiyalar shu yerda joylashgan

import sqlite3
import threading
from datetime import datetime
from config import DB_PATH

_lock = threading.Lock()


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            username TEXT,
            lang TEXT DEFAULT 'uz',
            phone TEXT,
            latitude REAL,
            longitude REAL,
            is_subscribed INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            created_at TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            brand TEXT,
            model TEXT,
            year TEXT,
            mileage TEXT,
            battery_capacity TEXT,
            range_km TEXT,
            condition TEXT,
            price TEXT,
            region TEXT,
            district TEXT,
            extra_info TEXT,
            photos TEXT,
            status TEXT DEFAULT 'pending',
            reject_reason TEXT,
            is_vip INTEGER DEFAULT 0,
            channel_message_id INTEGER,
            created_at TEXT
        )
        """)
        # Eski bazalarda reject_reason ustuni bo'lmasligi mumkin — migratsiya
        cur.execute("PRAGMA table_info(listings)")
        existing_cols = {row[1] for row in cur.fetchall()}
        if "reject_reason" not in existing_cols:
            cur.execute("ALTER TABLE listings ADD COLUMN reject_reason TEXT")
        conn.commit()
        conn.close()


# ---------------- USERS ----------------

def add_or_update_user(user_id, full_name=None, username=None):
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        if row is None:
            cur.execute(
                "INSERT INTO users (user_id, full_name, username, created_at) VALUES (?,?,?,?)",
                (user_id, full_name, username, datetime.now().isoformat())
            )
        else:
            cur.execute(
                "UPDATE users SET full_name=?, username=? WHERE user_id=?",
                (full_name, username, user_id)
            )
        conn.commit()
        conn.close()


def set_user_lang(user_id, lang):
    _update_field(user_id, "lang", lang)


def set_user_phone(user_id, phone):
    _update_field(user_id, "phone", phone)


def set_user_location(user_id, lat, lon):
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("UPDATE users SET latitude=?, longitude=? WHERE user_id=?", (lat, lon, user_id))
        conn.commit()
        conn.close()


def set_user_subscribed(user_id, status: bool):
    _update_field(user_id, "is_subscribed", 1 if status else 0)


def set_user_banned(user_id, status: bool):
    _update_field(user_id, "is_banned", 1 if status else 0)


def _update_field(user_id, field, value):
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
        conn.commit()
        conn.close()


def get_user(user_id):
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return row


def is_user_banned(user_id):
    u = get_user(user_id)
    return bool(u["is_banned"]) if u else False


def get_all_user_ids():
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE is_banned=0")
        rows = [r["user_id"] for r in cur.fetchall()]
        conn.close()
        return rows


def get_users_stats():
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as c FROM users")
        total = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM users WHERE is_banned=1")
        banned = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM users WHERE is_subscribed=1")
        subscribed = cur.fetchone()["c"]
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute("SELECT COUNT(*) as c FROM users WHERE created_at LIKE ?", (f"{today}%",))
        new_today = cur.fetchone()["c"]
        conn.close()
        return {"total": total, "banned": banned, "subscribed": subscribed, "new_today": new_today}


def get_top_active_users(limit=5):
    """Eng ko'p e'lon joylagan foydalanuvchilar (faollik reytingi)"""
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT l.user_id, COUNT(*) as cnt, u.username, u.full_name, u.phone
            FROM listings l
            LEFT JOIN users u ON u.user_id = l.user_id
            GROUP BY l.user_id
            ORDER BY cnt DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        conn.close()
        return rows


# ---------------- LISTINGS ----------------

def create_listing(user_id, data: dict, photos: list):
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO listings
            (user_id, brand, model, year, mileage, battery_capacity, range_km,
             condition, price, region, district, extra_info, photos, status, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            user_id, data.get("brand"), data.get("model"), data.get("year"),
            data.get("mileage"), data.get("battery_capacity"), data.get("range_km"),
            data.get("condition"), data.get("price"), data.get("region"),
            data.get("district"), data.get("extra_info"),
            ",".join(photos), "pending", datetime.now().isoformat()
        ))
        conn.commit()
        listing_id = cur.lastrowid
        conn.close()
        return listing_id


def get_listing(listing_id):
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM listings WHERE id=?", (listing_id,))
        row = cur.fetchone()
        conn.close()
        return row


def get_pending_listings():
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM listings WHERE status='pending' ORDER BY id ASC")
        rows = cur.fetchall()
        conn.close()
        return rows


def get_user_listings(user_id):
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM listings WHERE user_id=? ORDER BY id DESC", (user_id,))
        rows = cur.fetchall()
        conn.close()
        return rows


def delete_listing(listing_id):
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM listings WHERE id=?", (listing_id,))
        conn.commit()
        conn.close()


def update_listing_field(listing_id, field, value):
    """E'lonning bitta maydonini yangilash (tahrirlash uchun)"""
    allowed_fields = {
        "brand", "model", "year", "mileage", "battery_capacity", "range_km",
        "condition", "price", "region", "district", "extra_info", "photos",
    }
    if field not in allowed_fields:
        raise ValueError(f"Field '{field}' tahrirlash uchun ruxsat etilmagan")
    _update_listing_field(listing_id, field, value)


def set_listing_status(listing_id, status):
    _update_listing_field(listing_id, "status", status)


def reject_listing(listing_id, reason):
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE listings SET status=?, reject_reason=? WHERE id=?",
            ("rejected", reason, listing_id)
        )
        conn.commit()
        conn.close()


def set_listing_vip(listing_id, is_vip: bool):
    _update_listing_field(listing_id, "is_vip", 1 if is_vip else 0)


def set_listing_channel_msg(listing_id, message_id):
    _update_listing_field(listing_id, "channel_message_id", message_id)


def _update_listing_field(listing_id, field, value):
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(f"UPDATE listings SET {field}=? WHERE id=?", (value, listing_id))
        conn.commit()
        conn.close()


def get_approved_listings(filters: dict = None):
    """filters: brand, region, district, min_price, max_price, vip_only"""
    query = "SELECT * FROM listings WHERE status='approved'"
    params = []
    if filters:
        if filters.get("brand"):
            query += " AND brand LIKE ?"
            params.append(f"%{filters['brand']}%")
        if filters.get("region"):
            query += " AND region LIKE ?"
            params.append(f"%{filters['region']}%")
        if filters.get("district"):
            query += " AND district LIKE ?"
            params.append(f"%{filters['district']}%")
        if filters.get("vip_only"):
            query += " AND is_vip=1"
    query += " ORDER BY is_vip DESC, id DESC"
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return rows


def get_listings_stats():
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) as c FROM listings")
        total = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM listings WHERE status='approved'")
        approved = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM listings WHERE status='pending'")
        pending = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM listings WHERE status='rejected'")
        rejected = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM listings WHERE is_vip=1")
        vip = cur.fetchone()["c"]
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute("SELECT COUNT(*) as c FROM listings WHERE created_at LIKE ?", (f"{today}%",))
        today_count = cur.fetchone()["c"]
        conn.close()
        return {
            "total": total, "approved": approved,
            "pending": pending, "rejected": rejected, "vip": vip,
            "today": today_count,
        }


def get_top_brands(limit=5, status="approved"):
    """Eng ko'p joylangan / so'raladigan brendlar reytingi"""
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT brand, COUNT(*) as cnt FROM listings
            WHERE status=? AND brand IS NOT NULL AND brand != ''
            GROUP BY LOWER(brand)
            ORDER BY cnt DESC
            LIMIT ?
        """, (status, limit))
        rows = cur.fetchall()
        conn.close()
        return rows


def get_top_regions(limit=5):
    """Eng faol hududlar (qaysi viloyatdan ko'proq e'lon kelmoqda)"""
    with _lock:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT region, COUNT(*) as cnt FROM listings
            WHERE region IS NOT NULL AND region != ''
            GROUP BY LOWER(region)
            ORDER BY cnt DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        conn.close()
        return rows