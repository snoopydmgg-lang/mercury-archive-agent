"""
TFT Database Schema - SQLite 数据库定义与初始化
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "tft_na.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS players (
        puuid TEXT PRIMARY KEY,
        summoner_name TEXT,
        tier TEXT DEFAULT 'CHALLENGER',
        rank TEXT DEFAULT 'I',
        league_points INTEGER,
        wins INTEGER,
        losses INTEGER,
        hot_streak INTEGER DEFAULT 0,
        veteran INTEGER DEFAULT 0,
        last_updated TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        match_id TEXT PRIMARY KEY,
        game_version TEXT,
        game_datetime TEXT,
        game_length REAL,
        tft_set_number INTEGER,
        tft_game_type TEXT,
        queue_id INTEGER,
        fetched_at TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS participants (
        match_id TEXT,
        puuid TEXT,
        placement INTEGER,
        augments TEXT,
        companion TEXT,
        gold_left INTEGER,
        last_round INTEGER,
        level INTEGER,
        players_eliminated INTEGER,
        time_eliminated REAL,
        total_damage_to_players INTEGER,
        PRIMARY KEY (match_id, puuid),
        FOREIGN KEY (match_id) REFERENCES matches(match_id),
        FOREIGN KEY (puuid) REFERENCES players(puuid)
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS units (
        match_id TEXT,
        puuid TEXT,
        unit_index INTEGER,
        character_id TEXT,
        item_names TEXT,
        rarity INTEGER,
        tier INTEGER,
        PRIMARY KEY (match_id, puuid, unit_index),
        FOREIGN KEY (match_id) REFERENCES matches(match_id),
        FOREIGN KEY (puuid) REFERENCES players(puuid)
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS traits (
        match_id TEXT,
        puuid TEXT,
        trait_name TEXT,
        num_units INTEGER,
        style INTEGER,
        tier_current INTEGER,
        tier_total INTEGER,
        PRIMARY KEY (match_id, puuid, trait_name),
        FOREIGN KEY (match_id) REFERENCES matches(match_id),
        FOREIGN KEY (puuid) REFERENCES players(puuid)
    )""")

    # 索引
    c.execute("CREATE INDEX IF NOT EXISTS idx_participants_puuid ON participants(puuid)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_participants_placement ON participants(placement)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_units_character ON units(character_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_traits_name ON traits(trait_name)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_matches_datetime ON matches(game_datetime)")

    conn.commit()
    conn.close()
    print(f"Database initialized: {DB_PATH}")

if __name__ == "__main__":
    init_db()
