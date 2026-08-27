# -*- coding: utf-8 -*-
"""Tests for the filtered GET /api/tickets endpoint."""
import sys
import tempfile
import unittest
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC_DIR))

import app as app_module  # noqa: E402
import db as db_module  # noqa: E402


def make_ticket(ticket_no: str, device_sn: str, status: str) -> dict:
    """Build a minimal valid ticket for test setup."""
    return {
        "ticket_no": ticket_no,
        "customer": "测试客户",
        "phone": "13800000000",
        "device_type": "工业设备",
        "device_sn": device_sn,
        "fault": "接口筛选测试",
        "report_date": "2026-08-27",
        "priority": "普通",
        "status": status,
        "note": "",
    }


class GetTicketsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "tickets.db"
        self.old_db_path = db_module.DB_PATH
        db_module.DB_PATH = self.db_path

        conn = db_module.connect()
        try:
            db_module.init_db(conn)
            db_module.insert_ticket(conn, make_ticket("T-001", "SN-3X-001", "待处理"))
            db_module.insert_ticket(conn, make_ticket("T-002", "SN-3X-002", "处理中"))
            db_module.insert_ticket(conn, make_ticket("T-003", "CNC-001", "待处理"))
        finally:
            conn.close()

        self.client = app_module.app.test_client()

    def tearDown(self) -> None:
        db_module.DB_PATH = self.old_db_path
        self.temp_dir.cleanup()

    def test_status_filter_returns_matching_rows(self) -> None:
        response = self.client.get("/api/tickets?status=待处理")
        self.assertEqual(response.status_code, 200)
        rows = response.get_json()["tickets"]
        self.assertEqual({row["ticket_no"] for row in rows}, {"T-001", "T-003"})

    def test_device_filter_uses_partial_match(self) -> None:
        response = self.client.get("/api/tickets?device=SN-3X")
        self.assertEqual(response.status_code, 200)
        rows = response.get_json()["tickets"]
        self.assertEqual({row["ticket_no"] for row in rows}, {"T-001", "T-002"})

    def test_no_filter_returns_all_rows(self) -> None:
        response = self.client.get("/api/tickets")
        self.assertEqual(response.status_code, 200)
        rows = response.get_json()["tickets"]
        self.assertEqual(len(rows), 3)


if __name__ == "__main__":
    unittest.main()
