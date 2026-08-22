import sqlite3
from pathlib import Path

# 自动定位数据库文件路径（和项目现有写法一致）
ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "tickets.db"

# 要插入的工单数据
ticket_data = (
    "T-20260819-001",          # 工单号
    "华源纺织厂",               # 客户名称
    "13800005678",             # 联系电话
    "工业缝纫机",               # 设备类型
    "SN-3X-0217",              # 设备编号
    "缝纫时线迹跳针机针区有异响", # 故障现象
    "2026-08-19",              # 报修日期
    "紧急",                    # 优先级
    "待处理",                  # 工单状态
    "客户要求周四上午上门"       # 备注
)

# INSERT SQL 语句，用 ? 占位符（安全防注入，和项目代码规范一致）
insert_sql = """
INSERT INTO tickets 
    (ticket_no, customer, phone, device_type, device_sn, fault, report_date, priority, status, note)
VALUES 
    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(insert_sql, ticket_data)
    conn.commit()
    print(f"✅ 插入成功！新增记录自增ID：{cursor.lastrowid}")

    # ========== 自动验证：查询刚插入的记录 ==========
    print("\n📋 已插入的工单详情：")
    row = conn.execute(
        "SELECT id, ticket_no, customer, device_type, fault, priority, status FROM tickets WHERE ticket_no = ?",
        ("T-20260819-001",)
    ).fetchone()
    print(f"  记录ID：{row[0]}")
    print(f"  工单号：{row[1]}")
    print(f"  客户名：{row[2]}")
    print(f"  设备类型：{row[3]}")
    print(f"  故障描述：{row[4]}")
    print(f"  优先级：{row[5]}")
    print(f"  当前状态：{row[6]}")

    conn.close()

except sqlite3.IntegrityError:
    print("⚠️  插入失败：工单号 T-20260819-001 已存在，不可重复录入（符合唯一约束设计）")
except Exception as e:
    print(f"❌ 执行出错：{e}")
