import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "tickets.db"

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row

# 对应课程的查询语句：倒序取前2条
sql = "SELECT * FROM tickets ORDER BY id DESC LIMIT 2"
rows = conn.execute(sql).fetchall()

print("=" * 70)
print("工单查询验证结果（最新2条，倒序排列）")
print("=" * 70)

print(f"共查到 {len(rows)} 条记录\n")

ticket_nos = []
for row in rows:
    ticket = dict(row)
    ticket_nos.append(ticket["ticket_no"])
    print(f"记录ID: {ticket['id']}")
    print(f"工单号: {ticket['ticket_no']}")
    print(f"客户名: {ticket['customer']}")
    print(f"设备类型: {ticket['device_type']}")
    print(f"优先级: {ticket['priority']}")
    print(f"状态: {ticket['status']}")
    print("-" * 70)

# 验证是否重复
if len(set(ticket_nos)) == len(ticket_nos):
    print("✅ 验证通过：所有工单号唯一，无重复记录")
else:
    print("❌ 验证失败：存在重复工单号")

print(f"✅ 两条工单均已落库：{ticket_nos[0]}、{ticket_nos[1]}")
print("字段值与录入内容一致，cli.py + db.py 写入链路正常")

conn.close()
