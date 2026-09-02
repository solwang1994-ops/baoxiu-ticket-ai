# -*- coding: utf-8 -*-
"""规则故障分类（任务14 参考实现）

读取 rules.json，按关键词命中返回 {category, advice, keyword}；
匹配不到时返回默认兜底。任何情况下都返回可用结果，业务不中断。
"""
import json
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parent.parent / "docs" / "rules.json"

DEFAULT = {"category": "其他", "advice": "联系资深师傅现场诊断，记录故障现象以便后续补充规则。"}


def load_rules(path: Path | str | None = None) -> list[dict]:
    """加载规则表。"""
    with open(str(path or RULES_PATH), encoding="utf-8") as f:
        return json.load(f)


def classify(text: str, rules: list[dict] | None = None) -> dict:
    """在故障描述里找关键词，命中即返回该类别（顺序匹配，先命中的优先）。"""
    rules = rules if rules is not None else load_rules()
    for rule in rules:
        for keyword in rule.get("keywords", []):
            if keyword in text:
                return {"category": rule["category"],
                        "advice": rule["advice"],
                        "keyword": keyword}
    return dict(DEFAULT)


if __name__ == "__main__":
    import sys
    text = sys.argv[1] if len(sys.argv) > 1 else input("输入故障描述：")
    result = classify(text)
    print(f"分类：{result['category']}")
    print(f"建议：{result['advice']}")
