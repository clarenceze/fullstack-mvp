import os, csv, psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "vgsales.csv")

DDL = """
DROP TABLE IF EXISTS games;
CREATE TABLE games (
    rank INTEGER,
    name TEXT,
    platform TEXT,
    year INTEGER,
    genre TEXT,
    publisher TEXT,
    na_sales NUMERIC,
    eu_sales NUMERIC,
    jp_sales NUMERIC,
    other_sales NUMERIC,
    global_sales NUMERIC
);
"""

VIEW = """
DROP VIEW IF EXISTS vgs_view;
CREATE VIEW vgs_view AS
SELECT rank, name, platform, year, genre, publisher,
       na_sales, eu_sales, jp_sales, other_sales, global_sales
FROM games
WHERE global_sales IS NOT NULL;
"""

def to_int(x):
    try:
        return int(float(x)) if x and x.upper() != "N/A" else None
    except: return None

def to_num(x):
    try:
        return float(x) if x and x.upper() != "N/A" else None
    except: return None

def main():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")
    conn = psycopg2.connect(DATABASE_URL); conn.autocommit = True
    cur = conn.cursor()
    cur.execute(DDL)
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f); rows = []
        for r in reader:
            rows.append((
                to_int(r.get("Rank")), r.get("Name"), r.get("Platform"),
                to_int(r.get("Year")), r.get("Genre"), r.get("Publisher"),
                to_num(r.get("NA_Sales")), to_num(r.get("EU_Sales")),
                to_num(r.get("JP_Sales")), to_num(r.get("Other_Sales")),
                to_num(r.get("Global_Sales")),
            ))
    cur.executemany("""
        INSERT INTO games (
          rank, name, platform, year, genre, publisher,
          na_sales, eu_sales, jp_sales, other_sales, global_sales
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
    """, rows)
    cur.execute(VIEW)
    cur.close(); conn.close()
    print("Database initialized with CSV data.")
if __name__ == "__main__": main()