# -*- coding: utf-8 -*-
"""售后报修工单 CLI 录单工具（任务3/5 参考实现 v2）

用法：python src/cli.py

学习点：
- 任务3：逐字段 input() 采集 + 必填空值重输 + 日期/优先级校验
- 任务5：录入后写入 SQLite、单号重复拦截
"""
import datetime
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "tickets.db"

# 字段清单（中文名, 字典 key, 是否必填）——与 docs/字段设计表.md、schema.sql 保持一致
FIELDS = [
    ("工单号", "ticket_no", True),
    ("客户名称", "customer", True),
    ("联系电话", "phone", True),
    ("设备类型", "device_type", True),
    ("设备编号", "device_sn", True),
    ("故障现象", "fault", True),
]

PRIORITIES = ["普通", "紧急", "特急"]


def ask_text(label: str) -> str:
    """输入一段文本；必填项为空自动重输（任务3 的核心循环）。"""
    while True:
        value = input(f"{label}：").strip()
        if value:
            return value
        print(f"  [校验] {label}是必填项，不能为空，请重新输入。")

def ask_date() -> str:
    """输入报修日期，校验 YYYY-MM-DD 格式；直接回车默认今天。"""
    while True:
        value = input("报修日期（YYYY-MM-DD，直接回车=今天）：").strip()
        if not value:
            return datetime.date.today().isoformat()
        try:
            datetime.date.fromisoformat(value)
            return value
        except ValueError:
            print("  [校验] 日期格式不对，请按 YYYY-MM-DD 输入，例如 2026-08-19。")

def ask_priority() -> str:
    """选择优先级：1 普通 / 2 紧急 / 3 特急；直接回车默认普通。"""
    while True:
        value = input("优先级（1 普通 / 2 紧急 / 3 特急，直接回车=普通）：").strip()
        if not value:
            return "普通"
        if value in ("1", "2", "3"):
            return PRIORITIES[int(value) - 1]
        print("  [校验] 请输入 1/2/3 或直接回车。")

def collect_ticket() -> dict:
    """逐字段采集，返回工单字典。"""
    print("=" * 48)
    print("  售后报修工单录入（必填项不能为空）")
    print("=" * 48)
    ticket = {}
    for label, key, _required in FIELDS:
        ticket[key] = ask_text(label)
    ticket["report_date"] = ask_date()
    ticket["priority"] = ask_priority()
    ticket["status"] = "待处理"
    ticket["note"] = input("备注（可直接回车）：").strip()
    return ticket

def save_ticket(ticket: dict):
    """写入 SQLite（任务5）；单号重复返回 None；数据库未初始化返回 "no_db"。"""
    if not DB_PATH.exists():
        return "no_db"
    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            "SELECT id FROM tickets WHERE ticket_no = ?", (ticket["ticket_no"],)
        ).fetchone()
        if row:
            print(f"  [拦截] 工单号 {ticket['ticket_no']} 已存在，不重复录入。")
            return None
        cur = conn.execute(
            "INSERT INTO tickets (ticket_no, customer, phone, device_type,"
            " device_sn, fault, report_date, priority, status, note)"
            " VALUES (?,?,?,?,?,?,?,?,?,?)",
            (ticket["ticket_no"], ticket["customer"], ticket["phone"],
             ticket["device_type"], ticket["device_sn"], ticket["fault"],
             ticket["report_date"], ticket["priority"], ticket["status"],
             ticket["note"]),
        )
        conn.commit()
        print(f"  [落库] 已保存，记录 id={cur.lastrowid}")
        return cur.lastrowid
    finally:
        conn.close()

def main() -> int:
    ticket = collect_ticket()
    print()
    print("录入结果（字典）：")
    print(ticket)
    print()
    result = save_ticket(ticket)
    if result == "no_db":
        print("提示：数据库还没初始化（任务4 建库后这里会自动落库）。")
        print("本任务先验证采集与校验：上面字典已打印，字段齐全即达标。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
