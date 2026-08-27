# -*- coding: utf-8 -*-
"""任务 9 版本（v3）：v2 + GET /api/tickets（?status= ?device= 筛选）。

比 v2 多：一个 GET 路由，逻辑复用 db.query_tickets（与命令行查询同一套）。
录单表单（前端）任务 10 加。
"""
import datetime

from flask import Flask, jsonify, request

import db

app = Flask(__name__)

# 录单必填字段（与 docs/字段设计表.md、schema.sql 一致）
REQUIRED = ["ticket_no", "customer", "phone", "device_type", "device_sn", "fault"]


@app.get("/")
def index():
    return "售后报修工单系统已启动（v3：POST/GET 接口已就位，表单任务 10 加入）"


@app.post("/api/tickets")
def create_ticket():
    """任务 8：解析 JSON、校验必填、入库、返回新记录 id；缺字段返回 400。"""
    payload = request.get_json(silent=True) or {}
    missing = [f for f in REQUIRED if not str(payload.get(f) or "").strip()]
    if missing:
        return jsonify({"ok": False,
                        "error": "缺少必填字段：" + "、".join(missing)}), 400
    ticket = {f: str(payload.get(f) or "").strip() for f in REQUIRED}
    ticket["report_date"] = str(payload.get("report_date") or "").strip() or datetime.date.today().isoformat()
    ticket["priority"] = str(payload.get("priority") or "普通").strip()
    ticket["note"] = str(payload.get("note") or "").strip()
    conn = db.connect()
    try:
        new_id = db.insert_ticket(conn, ticket)
    finally:
        conn.close()
    if new_id is None:
        return jsonify({"ok": False, "error": "单号已存在，请勿重复录入"}), 409
    return jsonify({"ok": True, "id": new_id})


@app.get("/api/tickets")
def list_tickets():
    """任务 9：?status= 与 ?device= 筛选，无参数返回全部。"""
    device = str(request.args.get("device") or "").strip()
    status = str(request.args.get("status") or "").strip()
    conn = db.connect()
    try:
        rows = db.query_tickets(conn, device=device, status=status)
    finally:
        conn.close()
    return jsonify({"ok": True, "tickets": rows})


def main() -> None:
    conn = db.connect()
    try:
        db.init_db(conn)
    finally:
        conn.close()
    print("售后报修工单系统已启动：http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
