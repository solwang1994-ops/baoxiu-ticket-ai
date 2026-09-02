# -*- coding: utf-8 -*-
"""规则分类单元测试（任务14 参考实现）——unittest 三件套：用例、断言、运行。"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import classify  # noqa: E402

SAMPLE_RULES = [
    {"category": "电气故障", "keywords": ["不通电", "跳闸"], "advice": "先断电验电。"},
    {"category": "异响", "keywords": ["异响", "噪音"], "advice": "定位声源部件。"},
]


class ClassifyTests(unittest.TestCase):
    """覆盖：命中返回类别、关键词区分度、默认兜底。"""

    def test_hit_returns_category_and_advice(self):
        result = classify.classify("设备不通电，开机无反应", SAMPLE_RULES)
        self.assertEqual(result["category"], "电气故障")
        self.assertIn("断电", result["advice"])

    def test_keyword_hit_distinguishes_categories(self):
        result = classify.classify("运转时有异响", SAMPLE_RULES)
        self.assertEqual(result["category"], "异响")
        self.assertEqual(result["keyword"], "异响")

    def test_no_match_falls_back_to_default(self):
        result = classify.classify("暂时看不出问题", SAMPLE_RULES)
        self.assertEqual(result["category"], "其他")
        self.assertTrue(result["advice"])

    def test_real_rules_json_loads(self):
        rules = classify.load_rules()
        self.assertGreaterEqual(len(rules), 10)
        for rule in rules:
            self.assertTrue(rule["category"] and rule["keywords"] and rule["advice"])


if __name__ == "__main__":
    unittest.main()
