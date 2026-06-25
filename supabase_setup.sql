-- Supabase Dashboard → SQL Editor da ushbu SQL ni ishga tushiring
-- (bir marta bajarsangiz yetarli)

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
    user_id            BIGINT REFERENCES users(user_id),
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

-- Tezkor qidirish uchun indekslar
CREATE INDEX IF NOT EXISTS idx_listings_status  ON listings(status);
CREATE INDEX IF NOT EXISTS idx_listings_user_id ON listings(user_id);
CREATE INDEX IF NOT EXISTS idx_listings_is_vip  ON listings(is_vip);
