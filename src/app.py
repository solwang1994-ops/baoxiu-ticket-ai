# -*- coding: utf-8 -*-
"""售后报修工单 Web 应用（任务8/9/10/11/12/16 参考实现）

启动：python src/app.py  然后浏览器打开 http://127.0.0.1:5000

路由一览：
  GET  /                    录单页（任务8/11）
  GET  /list                台账页（任务12）
  POST /api/tickets         提交工单（任务9）
  GET  /api/tickets         查询工单，支持 ?status= ?device=（任务10）
  GET  /api/tickets/export  导出 CSV（任务12）
  POST /api/ai_classify     AI 故障分类（任务16）
"""
import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

import ai_classify
import db

ROOT = Path(__file__).resolve().parent.parent
app = Flask(__name__, template_folder=str(ROOT / "src" / "templates"))

# 录单必填字段（与 docs/字段设计表.md、schema.sql 一致）
REQUIRED = ["ticket_no", "customer", "phone", "device_type", "device_sn", "fault"]


@app.get("/")
def index():
    """任务8：最小可运行——GET / 返回录单页。"""
    return render_template("index.html")


@app.get("/list")
def list_page():
    """任务12：台账列表页。"""
    return render_template("list.html")


@app.post("/api/tickets")
def create_ticket():
    """任务9：解析 JSON、校验必填、入库、返回新记录 id；缺字段返回 400。"""
    payload = request.get_json(silent=True) or {}
    missing = [f for f in REQUIRED if not str(payload.get(f) or "").strip()]
    if missing:
        return jsonify({"ok": False,
                        "error": "缺少必填字段：" + "、".join(missing)}), 400
    ticket = {f: str(payload.get(f) or "").strip() for f in REQUIRED}
    ticket["report_date"] = str(payload.get("report_date") or "").strip()         or datetime.date.today().isoformat()
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
    """任务10：?status= 与 ?device= 筛选，无参数返回全部。"""
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
    """任务12：导出 CSV（utf-8-sig，Excel 打开中文不乱码）。"""
    from urllib.parse import quote  # ← 这行不能少
    status = str(request.args.get("status") or "").strip()
    stamp = datetime.date.today().isoformat()
    name = f"tickets_{status or 'all'}_{stamp}.csv"
    path = ROOT / "data" / name
    conn = db.connect()
    try:
        count = db.export_csv(conn, path, status=status)
    finally:
        conn.close()

    filename_encoded = quote(name)  # ← 这行不能少

    return Response(
        path.read_bytes(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename_encoded}"})


@app.post("/api/ai_classify")
def ai_classify_endpoint():
    """任务16：AI 分类（无 Key/失败自动降级规则分类）。"""
    payload = request.get_json(silent=True) or {}
    result = ai_classify.ai_classify(payload)
    return jsonify({"ok": True, **result})


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
