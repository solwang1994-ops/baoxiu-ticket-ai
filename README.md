以下是完整可直接复制的 `README.md` 内容，全选复制后粘贴到你本地的 `README.md` 文件保存即可，完全匹配你当前的项目结构与已实现功能，满足课程验收的四要素要求。

```markdown
# 售后报修工单管理系统

基于 Python + SQLite 的命令行工单管理工具，实现报修工单的结构化录入、持久化存储、条件筛选与台账导出。

## 一、项目作用
解决传统 Excel 登记售后工单的痛点：信息字段不统一、工单号易重复、历史工单查询不便。
通过命令行工具完成「采集校验 → 写入数据库 → 查询导出」的完整闭环，数据本地持久化保存，支持单号防重复、字段自动校验。

## 二、运行方法
### 1. 环境准备
1. 创建并激活虚拟环境
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. 安装依赖（当前仅使用 Python 标准库，无第三方依赖）
```powershell
pip install -r requirements.txt
```

### 2. 初始化数据库
```powershell
python tools/init_db.py
```

### 3. 常用操作
- 录入工单：
```powershell
python src/cli.py
```

- 查询全部工单：
```powershell
python src/query.py
```

- 按设备编号模糊查询：
```powershell
python src/query.py --device SN-3X
```

- 按工单状态筛选：
```powershell
python src/query.py --status 待处理
```

- 导出工单台账为 CSV：
```powershell
python src/query.py --export data/工单台账.csv
```

## 三、目录结构
```
baoxiu/
├── .venv/              # Python 虚拟环境（本地生成，不提交版本管理）
├── data/               # 数据目录
│   ├── schema.sql      # 数据库建表脚本
│   └── tickets.db      # SQLite 数据库文件（运行时生成）
├── src/                # 核心业务代码
│   ├── cli.py          # 命令行工单录入工具，含输入校验与落库
│   ├── db.py           # SQLite 存储层，封装增查与导出能力
│   └── query.py        # 工单查询与导出命令行工具
├── test_data/          # 测试数据与用例
│   └── cli_input_answers.txt
├── tools/              # 辅助工具脚本
│   ├── init_db.py
│   ├── check_schema.py
│   ├── insert_ticket.py
│   ├── query_ticket.py
│   └── verify_tickets.py
├── README.md           # 项目说明文档
└── requirements.txt    # 项目依赖清单
```

## 四、已实现功能
1.  工单逐字段录入，必填项非空校验、日期格式校验、优先级选项校验
2.  工单号防重复拦截，数据库唯一约束 + 代码先查再插双重保障
3.  工单数据持久化存储，基于 SQLite 本地数据库
4.  多条件查询：按设备编号模糊匹配、按状态精确筛选
5.  工单台账对齐打印，支持一键导出 CSV 格式文件
```