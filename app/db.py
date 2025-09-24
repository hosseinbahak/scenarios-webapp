# app/db.py
import os
import duckdb
from pathlib import Path

DATA_DIR = Path("/data")
DB_PATH = Path("/data/torob.duckdb")

TABLES = {
    "base_products": "base_products.parquet",
    "members": "members.parquet",
    "shops": "shops.parquet",
    "brands": "brands.parquet",
    "categories": "categories.parquet",
    "cities": "cities.parquet",
    "searches": "searches.parquet",
    "base_views": "base_views.parquet",
    "final_clicks": "final_clicks.parquet",
}

_con = None

def get_con():
    global _con
    if _con is None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        # اگر DB وجود ندارد، از پارکت‌ها بساز
        fresh_build = not DB_PATH.exists()
        _con = duckdb.connect(str(DB_PATH))
        if fresh_build:
            for tbl, fname in TABLES.items():
                fpath = DATA_DIR / fname
                if fpath.exists():
                    _con.execute(f"CREATE OR REPLACE TABLE {tbl} AS SELECT * FROM '{fpath.as_posix()}'")
            # ایندکس‌های مفید (DuckDB از zone map/ordering سود می‌بره؛ ایندکس hash آزمایشی):
            _con.execute("PRAGMA threads=4")
        return _con
    return _con

# ----- Query helpers -----

def search_base_products_by_text(q: str, limit: int = 10):
    con = get_con()
    # جستجوی ساده روی نام فارسی/انگلیسی (ILIKE → case-insensitive)
    return con.execute(
        """
        SELECT random_key, persian_name, english_name, brand_id, category_id
        FROM base_products
        WHERE persian_name ILIKE '%' || ? || '%'
           OR english_name ILIKE '%' || ? || '%'
        LIMIT ?
        """,
        [q, q, limit],
    ).fetchall()

def top_sellers_for_base(base_key: str, limit: int = 10):
    con = get_con()
    return con.execute(
        """
        SELECT m.random_key as member_random_key,
               m.price,
               s.id as shop_id,
               s.score,
               s.has_warranty
        FROM members m
        JOIN shops s ON m.shop_id = s.id
        WHERE m.base_random_key = ?
        ORDER BY m.price ASC, s.score DESC
        LIMIT ?
        """,
        [base_key, limit],
    ).fetchall()
