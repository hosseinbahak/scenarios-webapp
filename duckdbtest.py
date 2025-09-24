import duckdb

con = duckdb.connect("torob.duckdb")

# attach parquet
con.execute("CREATE OR REPLACE TABLE base_products AS SELECT * FROM 'base_products.parquet'")
con.execute("CREATE OR REPLACE TABLE members AS SELECT * FROM 'members.parquet'")
con.execute("CREATE OR REPLACE TABLE shops AS SELECT * FROM 'shops.parquet'")

# نمونه کوئری: ارزان‌ترین فروشندگان برای یک base_random_key
base_key = "awsome-gooshi-rk"
q = """
SELECT m.random_key, m.price, s.score, s.has_warranty
FROM members m
JOIN shops s ON m.shop_id = s.id
WHERE m.base_random_key = ?
ORDER BY m.price ASC
LIMIT 10
"""
print(con.execute(q, [base_key]).fetchdf())
