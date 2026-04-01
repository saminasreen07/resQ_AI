-- ============================================================
-- ResQAI TN — Supabase Database Setup
-- Run this in your Supabase SQL Editor (supabase.com → SQL Editor)
-- ============================================================

-- 1. REPORTS TABLE
CREATE TABLE IF NOT EXISTS reports (
    id                 TEXT PRIMARY KEY,
    name               TEXT NOT NULL,
    phone              TEXT NOT NULL,
    district           TEXT NOT NULL,
    location           TEXT NOT NULL,
    disaster           TEXT NOT NULL,
    people             INTEGER DEFAULT 1,
    medical            TEXT DEFAULT 'No',
    food               TEXT DEFAULT 'No',
    shelter            TEXT DEFAULT 'No',
    specific_needs     TEXT DEFAULT '',
    description        TEXT DEFAULT '',
    priority           TEXT DEFAULT 'LOW',
    priority_score     INTEGER DEFAULT 0,
    status             TEXT DEFAULT 'REPORTED',
    assigned_team_id   TEXT,
    lat                FLOAT,
    lon                FLOAT,
    created_at         TIMESTAMP DEFAULT NOW(),
    status_updated_at  TIMESTAMP DEFAULT NOW()
);

-- 2. TEAMS TABLE
CREATE TABLE IF NOT EXISTS teams (
    id                 TEXT PRIMARY KEY,
    name               TEXT NOT NULL,
    type               TEXT NOT NULL,        -- Flood / Fire / Medical / General
    district           TEXT NOT NULL,
    lat                FLOAT,
    lon                FLOAT,
    is_available       BOOLEAN DEFAULT TRUE,
    current_assignment TEXT
);

-- 3. STATUS HISTORY TABLE
CREATE TABLE IF NOT EXISTS status_history (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id   TEXT NOT NULL REFERENCES reports(id),
    status      TEXT NOT NULL,
    updated_by  TEXT DEFAULT 'system',
    timestamp   TIMESTAMP DEFAULT NOW(),
    note        TEXT DEFAULT ''
);

-- ============================================================
-- SEED DATA: Sample rescue teams for Tamil Nadu
-- ============================================================
INSERT INTO teams (id, name, type, district, lat, lon, is_available) VALUES
('TEAM-CHN-F1', 'Chennai Flood Response Unit',      'Flood',   'Chennai',        13.0827, 80.2707, TRUE),
('TEAM-CHN-F2', 'Adyar Flood Rescue Squad',         'Flood',   'Chennai',        13.0012, 80.2565, TRUE),
('TEAM-CHN-FR', 'Chennai Fire & Rescue Services',   'Fire',    'Chennai',        13.0550, 80.2400, TRUE),
('TEAM-CHN-MD', 'Chennai Medical Response Unit',    'Medical', 'Chennai',        13.0850, 80.2100, TRUE),
('TEAM-MDU-G1', 'Madurai General Rescue Team',      'General', 'Madurai',        9.9252,  78.1198, TRUE),
('TEAM-MDU-F1', 'Madurai Flood Response Unit',      'Flood',   'Madurai',        9.9100,  78.1000, TRUE),
('TEAM-CBE-G1', 'Coimbatore General Rescue',        'General', 'Coimbatore',     11.0168, 76.9558, TRUE),
('TEAM-CBE-FR', 'Coimbatore Fire Response',         'Fire',    'Coimbatore',     11.0300, 76.9700, TRUE),
('TEAM-TRZ-G1', 'Trichy General Rescue Unit',       'General', 'Tiruchirappalli',10.7905, 78.7047, TRUE),
('TEAM-VLR-G1', 'Vellore Emergency Response',       'General', 'Vellore',        12.9165, 79.1325, TRUE),
('TEAM-NGP-F1', 'Nagapattinam Coastal Rescue',      'Flood',   'Nagapattinam',   10.7672, 79.8449, TRUE),
('TEAM-TNJ-G1', 'Thanjavur Flood & Relief Team',    'Flood',   'Thanjavur',      10.7870, 79.1378, TRUE),
('TEAM-CDL-F1', 'Cuddalore Flood Response',         'Flood',   'Cuddalore',      11.7447, 79.7680, TRUE),
('TEAM-SLM-G1', 'Salem General Response Unit',      'General', 'Salem',          11.6643, 78.1460, TRUE),
('TEAM-TNL-G1', 'Tirunelveli Emergency Team',       'General', 'Tirunelveli',    8.7139,  77.7567, TRUE)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- RLS (Row Level Security) — Enable for production
-- For hackathon demo, disable RLS for easier access:
-- ============================================================
ALTER TABLE reports        DISABLE ROW LEVEL SECURITY;
ALTER TABLE teams          DISABLE ROW LEVEL SECURITY;
ALTER TABLE status_history DISABLE ROW LEVEL SECURITY;

-- ============================================================
-- DONE! Now set up .streamlit/secrets.toml:
--
-- [supabase]
-- url = "https://YOUR_PROJECT_ID.supabase.co"
-- key = "YOUR_ANON_PUBLIC_KEY"
--
-- authority_password = "SDMA@TN2024"
-- ============================================================
