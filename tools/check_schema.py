import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "tickets.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.execute("PRAGMA table_info(tickets)")
columns = cursor.fetchall()
conn.close()

print("=" * 60)
print("tickets 表结构（共 {} 个字段）".format(len(columns)))
print("=" * 60)
print(f"{'序号':<4} {'字段名':<18} {'类型':<10} {'非空':<6} {'主键':<6}")
print("-" * 60)
for col in columns:
    cid, name, ctype, notnull, dflt, pk = col
    print(f"{cid:<4} {name:<18} {ctype:<10} {'是' if notnull else '否':<6} {'是' if pk else '否':<6}")
