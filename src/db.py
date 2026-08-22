# -*- coding: utf-8 -*-
"""SQLite 存储层（任务4/5/6/7 参考实现）

提供：connect / init_db / insert_ticket / query_tickets / export_csv
所有函数都接收 conn 参数，便于复用与测试。
"""
import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "tickets.db"
SCHEMA_PATH = ROOT /"data" / "schema.sql"


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    """打开数据库连接；row_factory=Row 让查询结果可以按列名取值。"""
    conn = sqlite3.connect(str(db_path or DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """执行 schema.sql 建表（IF NOT EXISTS，可重复执行）。"""
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()


def insert_ticket(conn: sqlite3.Connection, ticket: dict) -> int | None:
    """插入一条工单；单号重复返回 None，成功返回新记录 id。

    参数化（? 占位符）防 SQL 注入；先查再插实现防重复。
    """
    row = conn.execute(
        "SELECT id FROM tickets WHERE ticket_no = ?", (ticket["ticket_no"],)
    ).fetchone()
    if row:
        return None
    cur = conn.execute(
        "INSERT INTO tickets (ticket_no, customer, phone, device_type,"
        " device_sn, fault, report_date, priority, status, note)"
        " VALUES (?,?,?,?,?,?,?,?,?,?)",
        (ticket["ticket_no"], ticket["customer"], ticket["phone"],
         ticket["device_type"], ticket["device_sn"], ticket["fault"],
         ticket.get("report_date") or "", ticket.get("priority") or "普通",
         ticket.get("status") or "待处理", ticket.get("note") or ""),
    )
    conn.commit()
    return cur.lastrowid


def query_tickets(conn: sqlite3.Connection, device: str = "",
                  status: str = "") -> list[dict]:
    """查询工单：device 按设备编号模糊匹配（LIKE），status 精确筛选；
    都不传返回全部，按 id 倒序（最新在前）。"""
    sql = "SELECT * FROM tickets WHERE 1=1"
    params: list = []
    if device:
        sql += " AND device_sn LIKE ?"
        params.append(f"%{device}%")
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY id DESC"
    return [dict(row) for row in conn.execute(sql, params)]


def export_csv(conn: sqlite3.Connection, path: Path | str,
               status: str = "") -> int:
    """导出为 CSV；utf-8-sig 让 Excel 打开中文不乱码；返回导出行数。"""
    rows = query_tickets(conn, status=status)
    cols = ["id", "ticket_no", "customer", "phone", "device_type", "device_sn",
            "fault", "report_date", "priority", "status", "note", "created_at"]
    with open(str(path), "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        for row in rows:
            writer.writerow([row.get(c, "") for c in cols])
    return len(rows)
