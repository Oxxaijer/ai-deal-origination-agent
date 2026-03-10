import sqlite3
from datetime import datetime

DB_NAME = "deals.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            other_companies_mentioned TEXT,
            industry TEXT,
            event_type TEXT,
            funding_detected INTEGER,
            funding_amount TEXT,
            country_or_region TEXT,
            summary TEXT,
            investment_signal TEXT,
            growth_score INTEGER,
            market_score INTEGER,
            strategic_fit INTEGER,
            risk_score INTEGER,
            overall_score REAL,
            reasoning TEXT,
            title TEXT,
            source TEXT,
            published_at TEXT,
            url TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_deal(deal: dict):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO deals (
            company_name, other_companies_mentioned, industry, event_type,
            funding_detected, funding_amount, country_or_region, summary,
            investment_signal, growth_score, market_score, strategic_fit,
            risk_score, overall_score, reasoning, title, source,
            published_at, url, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        deal.get("company_name"),
        ", ".join(deal.get("other_companies_mentioned", [])),
        deal.get("industry"),
        deal.get("event_type"),
        1 if deal.get("funding_detected") else 0,
        deal.get("funding_amount"),
        deal.get("country_or_region"),
        deal.get("summary"),
        deal.get("investment_signal"),
        deal.get("growth_score"),
        deal.get("market_score"),
        deal.get("strategic_fit"),
        deal.get("risk_score"),
        deal.get("overall_score"),
        deal.get("reasoning"),
        deal.get("title"),
        deal.get("source"),
        deal.get("published_at"),
        deal.get("url"),
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()


def fetch_saved_deals(limit: int = 50):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT company_name, industry, event_type, funding_detected, funding_amount,
               overall_score, investment_signal, source, published_at, url
        FROM deals
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows