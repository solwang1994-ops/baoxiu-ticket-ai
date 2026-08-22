-- 报修工单表（任务4 参考实现）
-- 用 sqlite3 执行：sqlite3 data/tickets.db < schema.sql
CREATE TABLE IF NOT EXISTS tickets (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,   -- 自增主键
  ticket_no   TEXT NOT NULL UNIQUE,                -- 工单号（唯一，防重复录入）
  customer    TEXT NOT NULL,                       -- 客户名称
  phone       TEXT NOT NULL,                       -- 联系电话
  device_type TEXT NOT NULL,                       -- 设备类型（如 工业缝纫机）
  device_sn   TEXT NOT NULL,                       -- 设备编号
  fault       TEXT NOT NULL,                       -- 故障现象描述
  report_date TEXT NOT NULL DEFAULT '',            -- 报修日期 YYYY-MM-DD
  priority    TEXT NOT NULL DEFAULT '普通',         -- 优先级：普通/紧急/特急
  status      TEXT NOT NULL DEFAULT '待处理',       -- 状态：待处理/已处理
  note        TEXT NOT NULL DEFAULT '',            -- 备注
  created_at  TEXT NOT NULL DEFAULT (datetime('now','localtime'))  -- 录入时间
);
