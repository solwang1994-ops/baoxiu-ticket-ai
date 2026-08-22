import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "tickets.db"
SQL_PATH = ROOT / "data" / "schema.sql"

# 读取SQL文件
with open(SQL_PATH, encoding="utf-8") as f:
    sql_content = f.read()

# 连接数据库并执行建表
conn = sqlite3.connect(DB_PATH)
conn.executescript(sql_content)
conn.commit()
conn.close()

print("✅ 建表成功，数据库文件：", DB_PATH)
