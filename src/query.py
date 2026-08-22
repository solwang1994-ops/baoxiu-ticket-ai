# -*- coding: utf-8 -*-
"""台账查询与 CSV 导出命令行（任务6/7 参考实现）

用法：
  python src/query.py                    打印全部工单（对齐表格）
  python src/query.py --device 3号线    按设备编号模糊查询
  python src/query.py --status 待处理   按状态筛选
  python src/query.py --export data/台账.csv [--status 待处理]  导出 CSV
"""
import argparse
import sys
from pathlib import Path

import db

COLS = [
    ("id", 4),
    ("ticket_no", 20),
    ("customer", 16),
    ("phone", 16),
    ("device_type", 16),
    ("device_sn", 18),
    ("fault", 40),
    ("report_date", 14),
    ("priority", 8),
    ("status", 10),
]


def print_table(rows: list[dict]) -> None:
    """对齐打印表格：表头 + 每列按预设宽度截断对齐。"""
    if not rows:
        print("（没有符合条件的工单，先用 python src/cli.py 录几条）")
        return
    header = "".join(name.ljust(width) for name, width in COLS)
    print(header)
    print("-" * len(header))
    for row in rows:
        line = "".join(
            str(row.get(name, ""))[:width].ljust(width) for name, width in COLS
        )
        print(line)
    print(f"共 {len(rows)} 条")


def main() -> int:
    parser = argparse.ArgumentParser(description="报修工单台账查询/导出")
    parser.add_argument("--device", default="", help="按设备编号模糊查询")
    parser.add_argument("--status", default="", help="按状态筛选（待处理/已处理）")
    parser.add_argument("--export", default="", help="导出 CSV 到指定路径")
    args = parser.parse_args()

    conn = db.connect()
    try:
        if args.export:
            count = db.export_csv(conn, args.export, status=args.status)
            print(f"已导出 {count} 条到 {args.export}（Excel 直接打开，中文不乱码）")
        else:
            rows = db.query_tickets(conn, device=args.device, status=args.status)
            print_table(rows)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
