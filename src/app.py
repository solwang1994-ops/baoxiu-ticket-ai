# -*- coding: utf-8 -*-
"""
售后报修工单 Web 应用
启动方法：python src/app.py
启动后浏览器打开：http://127.0.0.1:5000
"""

# ===== 第一步：导入要用的工具 =====
# Python 自带的工具
import datetime
from pathlib import Path

# Flask 网页框架提供的工具
from flask import Flask, Response, jsonify, render_template, request

# 我们自己写的数据库模块，复用所有增删查改逻辑
import db

# ===== 第二步：全局基础配置 =====
# 计算项目根目录路径，保证找文件不会出错
ROOT = Path(__file__).resolve().parent.parent

# 初始化 Flask 应用，指定 HTML 页面模板放在 src/templates 文件夹里
app = Flask(__name__, template_folder=str(ROOT / "src" / "templates"))

# 定义工单必填字段，和数据库表、命令行录入的字段完全一致
REQUIRED = ["ticket_no", "customer", "phone", "device_type", "device_sn", "fault"]

# ===== 第三步：路由功能（地址和业务的对应关系）=====

# 1. 首页：录单页面
# 装饰器：给下面的函数挂个牌子，牌子写着「有人访问网站根地址 / 时，就执行我」
@app.get("/")
def index():
    # 读取 index.html 页面文件，返回给浏览器显示
    return render_template("index.html")

# 2. 台账列表页面
@app.get("/list")
def list_page():
    # 读取 list.html 页面文件，返回给浏览器
    return render_template("list.html")

# 3. 提交工单接口：接收前端填的表单，写入数据库
# post 表示：用户是来提交数据的，不是来看页面的
@app.post("/api/tickets")
def create_ticket():
    # 第一步：接收前端传过来的 JSON 格式的工单数据
    payload = request.get_json(silent=True) or {}

    # 第二步：校验必填字段有没有漏填
    missing = [f for f in REQUIRED if not str(payload.get(f) or "").strip()]
    if missing:
        # 有缺字段，返回错误提示，状态码 400 = 参数错误
        return jsonify({"ok": False, "error": "缺少必填字段：" + "、".join(missing)}), 400

    # 第三步：整理工单数据
    ticket = {f: str(payload.get(f) or "").strip() for f in REQUIRED}
    # 报修日期没填就自动用今天的日期
    ticket["report_date"] = str(payload.get("report_date") or "").strip() or datetime.date.today().isoformat()
    # 优先级没填就默认是「普通」
    ticket["priority"] = str(payload.get("priority") or "普通").strip()
    # 备注没填空着就行
    ticket["note"] = str(payload.get("note") or "").strip()

    # 第四步：连接数据库，调用 db.py 里的插入函数写进去
    conn = db.connect()
    try:
        new_id = db.insert_ticket(conn, ticket)
    finally:
        # 用完一定要关闭数据库连接
        conn.close()

    # 第五步：返回结果给前端
    if new_id is None:
        # 工单号重复了，返回 409 = 数据冲突
        return jsonify({"ok": False, "error": "单号已存在，请勿重复录入"}), 409
    # 成功了，返回新工单的 id
    return jsonify({"ok": True, "id": new_id})

# 4. 查询工单接口：支持按设备、按状态筛选
@app.get("/api/tickets")
def list_tickets():
    # 从网址里拿到筛选参数，比如 ?status=待处理
    device = str(request.args.get("device") or "").strip()
    status = str(request.args.get("status") or "").strip()

    # 调用 db.py 里的查询函数，复用之前写好的逻辑
    conn = db.connect()
    try:
        rows = db.query_tickets(conn, device=device, status=status)
    finally:
        conn.close()

    # 把查询结果转成 JSON 返回给前端
    return jsonify({"ok": True, "tickets": rows})

# 5. 导出 CSV 接口：点击按钮下载台账
@app.get("/api/tickets/export")
def export_tickets():
    status = str(request.args.get("status") or "").strip()
    # 生成带日期的文件名
    stamp = datetime.date.today().isoformat()
    name = f"tickets_{status or 'all'}_{stamp}.csv"
    path = ROOT / "data" / name

    # 调用 db.py 里的导出函数，生成 CSV 文件
    conn = db.connect()
    try:
        count = db.export_csv(conn, path, status=status)
    finally:
        conn.close()

    # 让浏览器自动下载这个 CSV 文件
    return Response(
        path.read_bytes(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{name}"'})

# ===== 第四步：启动服务 =====
def main() -> None:
    # 启动前先自动建表，新环境第一次跑也不用手动建库，开箱即用
    conn = db.connect()
    try:
        db.init_db(conn)
    finally:
        conn.close()

    # 打印启动提示
    print("售后报修工单系统已启动：http://127.0.0.1:5000")
    # 启动服务，只允许本机访问，端口号 5000
    app.run(host="127.0.0.1", port=5000, debug=False)

# 程序入口：直接运行这个文件时，就执行 main() 启动服务
if __name__ == "__main__":
    main()
