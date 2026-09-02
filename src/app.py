# -*- coding: utf-8 -*-
"""任务 11 版本（v5）：v4 + GET /list 台账页 + GET /api/tickets/export 导出 CSV。

比 v4 多：/list 路由、导出接口（utf-8-sig，Excel 打开中文不乱码）。
AI 分类（终态 app.py 才有）任务 14 接入。
"""
import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

import db

ROOT = Path(__file__).resolve().parent.parent
app = Flask(__name__, template_folder=str(ROOT / "src" / "templates"))

# 录单必填字段（与 docs/字段设计表.md、schema.sql 一致）
REQUIRED = ["ticket_no", "customer", "phone", "device_type", "device_sn", "fault"]


@app.get("/")
def index():
    """任务 10：返回录单表单页。"""
    return render_template("index.html")


@app.get("/list")
def list_page():
    """任务 11：台账列表页。"""
    return render_template("list.html")


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


@app.get("/api/tickets/export")
def export_tickets():
    """任务 11：导出 CSV（utf-8-sig，Excel 打开中文不乱码）。"""
    status = str(request.args.get("status") or "").strip()
    stamp = datetime.date.today().isoformat()
    name = f"tickets_{status or 'all'}_{stamp}.csv"
    path = ROOT / "data" / name
    conn = db.connect()
    try:
        count = db.export_csv(conn, path, status=status)
    finally:
        conn.close()
    return Response(
        path.read_bytes(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{name}"'})


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
