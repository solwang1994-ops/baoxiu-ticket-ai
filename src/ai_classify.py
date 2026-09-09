# -*- coding: utf-8 -*-
"""DeepSeek 故障分类 + 维修建议（任务15 参考实现）

流程：读 .env 的 DEEPSEEK_API_KEY → 组 prompt → 调 API 解析 JSON；
无 Key / 超时 / 网络失败 / 解析失败 → 自动降级 rules.json 规则分类。
"""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

import classify

ROOT = Path(__file__).resolve().parent.parent
API_URL = "https://api.deepseek.com/chat/completions"

# prompt 模板：让模型只输出 JSON，方便解析（任务15 的学习点）
PROMPT_TEMPLATE = (
    "你是工业设备售后专家。根据下面的报修工单，判断故障类别并给出一句话维修建议。\n"
    "故障类别尽量从这些类别里选：电气故障、机械卡死、异响、漏水、密封失效、传感器异常、程序问题、散热不良、结构松动、通讯故障、其他。\n只输出一个 JSON 对象，格式：{{\"category\": \"故障类别\", \"advice\": \"一句话维修建议\"}}\n"
    "工单：{ticket}\n"
)


def load_dotenv(path: Path | None = None) -> None:
    """从 .env 读 KEY=VALUE（不依赖第三方库；已存在的环境变量优先）。"""
    env_path = path or (ROOT / ".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"'))


def rule_fallback(ticket: dict, reason: str) -> dict:
    """降级：用故障描述走规则分类，并标注降级原因。"""
    text = " ".join(str(ticket.get(k) or "") for k in
                    ("fault", "note", "device_type"))
    result = classify.classify(text)
    result["engine"] = "rule"
    result["reason"] = reason
    return result


def ai_classify(ticket: dict, timeout: float = 15.0) -> dict:
    """AI 分类主入口：成功返回 engine=llm，任何失败都降级。"""
    load_dotenv()
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        return rule_fallback(ticket, "未配置 DEEPSEEK_API_KEY")

    prompt = PROMPT_TEMPLATE.format(ticket=json.dumps(ticket, ensure_ascii=False))
    payload = {
        "model": "deepseek-v4-flash",
        "temperature": 0.2,
        "max_tokens": 200,
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        req = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Authorization": "Bearer " + api_key},
            method="POST")

        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        content = str(((data.get("choices") or [{}])[0].get("message") or {})
                      .get("content") or "")
        obj = json.loads(content)
        result = {"category": str(obj.get("category") or "").strip(),
                  "advice": str(obj.get("advice") or "").strip(),
                  "engine": "llm"}
        if not result["category"] or not result["advice"]:
            raise ValueError("LLM 返回字段不完整")
        return result

    except (urllib.error.URLError, TimeoutError, OSError,
            ValueError, KeyError, IndexError, TypeError) as exc:
        return rule_fallback(ticket, f"API 调用失败：{exc!r}")


if __name__ == "__main__":
    demo = {"device_type": "工业缝纫机", "fault": "缝纫时设备异响，机针区有噪音",
            "note": ""}

    result = ai_classify(demo)

    print(f"分类：{result['category']}（引擎：{result['engine']}）")
    print(f"建议：{result['advice']}")
    
    if result.get("reason"):
        print(f"降级原因：{result['reason']}")
