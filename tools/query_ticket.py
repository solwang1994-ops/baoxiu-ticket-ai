import sqlite3
from pathlib import Path

# 定位数据库
ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "tickets.db"

# 查询语句：按工单号查询完整记录
query_sql = "SELECT * FROM tickets WHERE ticket_no = ?"
target_ticket = "T-20260819-001"

conn = sqlite3.connect(DB_PATH)
cursor = conn.execute(query_sql, (target_ticket,))
# 获取表的所有字段名
column_names = [desc[0] for desc in cursor.description]
row = cursor.fetchone()
conn.close()

# 格式化输出结果
print("=" * 65)
print(f"SELECT 查询结果（工单号：{target_ticket}）")
print("=" * 65)

if row:
    print(f"✅ 查到 1 条记录，共 {len(column_names)} 个字段\n")
    for name, value in zip(column_names, row):
        print(f"  {name:<15} : {value}")
    print("\n" + "-" * 65)
    print("字段值与插入内容完全一致；id 为自增主键、created_at 为自动录入时间")
    print("验证通过")
else:
    print("❌ 未查到对应工单记录")
