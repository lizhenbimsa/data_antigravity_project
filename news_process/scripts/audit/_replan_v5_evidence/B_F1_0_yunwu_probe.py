"""F1-0 yunwu.ai/v1 透传探针（强制前置门）

[⚠ 2026-08-02 状态订正] 本探针针对 **yunwu.ai** 端点 (成文当时的聚合代理)。
2026-08-02 起全项目已迁移至 OpenLux (https://api.openlux.ai/v1, OPENLUX_API_KEY)。
本文件保留原样作历史取证 —— 其记录的是当时对 yunwu.ai 的真实实测结果, 不代表
当前生产端点; 如需对 OpenLux 做同类探测, 请另写新探针, 勿改本文件。

对 3 个候选 model_name 各发 1 条最小 prompt（探测期候选名，非 config 锁定名；
其中 gemini-3.1-flash-lite-preview 为带 -preview 后缀的候选，与 config 中
gemini-3.1-flash-lite 不同），记录：
- HTTP 状态
- 响应 JSON 结构（是否含 choices[0].message.content）
- model / system_fingerprint 等元数据
- response_format={"type":"json_object"} 是否被接受

任一 model 不返回 200 + OpenAI-compatible JSON → [E1] 不允许启动。
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

# 加载 .env
ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ.get("GPT5NANO_API_KEY") or os.environ.get("YUNWU_API_KEY")
assert API_KEY, "API key not found in .env"

BASE_URL = "https://yunwu.ai/v1"
MODELS = [
    "gpt-5.4-nano",
    "gemini-3.1-flash-lite-preview",
    "deepseek-v4-flash",
]


def probe(model: str, force_json: bool = True) -> dict:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "返回单行 JSON: {\"family\": <vendor>, \"version\": <full id>, \"cutoff\": <date>}"}],
        "temperature": 0.0,
        "max_tokens": 200,
    }
    if force_json:
        payload["response_format"] = {"type": "json_object"}

    t0 = time.time()
    try:
        r = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=60)
        elapsed_ms = int((time.time() - t0) * 1000)
        body_raw = r.text
        try:
            body = r.json()
        except Exception as e:
            body = {"_parse_error": str(e), "_raw": body_raw[:500]}
        return {
            "model": model,
            "http_status": r.status_code,
            "elapsed_ms": elapsed_ms,
            "force_json": force_json,
            "response_keys": list(body.keys()) if isinstance(body, dict) else None,
            "has_choices": "choices" in body if isinstance(body, dict) else False,
            "has_message_content": (
                isinstance(body, dict)
                and "choices" in body
                and len(body.get("choices", [])) > 0
                and "message" in body["choices"][0]
                and "content" in body["choices"][0]["message"]
            ),
            "model_field": body.get("model") if isinstance(body, dict) else None,
            "system_fingerprint": body.get("system_fingerprint") if isinstance(body, dict) else None,
            "usage": body.get("usage") if isinstance(body, dict) else None,
            "content_preview": (
                body["choices"][0]["message"].get("content", "")[:300]
                if isinstance(body, dict) and body.get("choices") and "message" in body["choices"][0]
                else None
            ),
            "error": body.get("error") if isinstance(body, dict) else None,
        }
    except requests.RequestException as e:
        elapsed_ms = int((time.time() - t0) * 1000)
        return {
            "model": model,
            "http_status": None,
            "elapsed_ms": elapsed_ms,
            "force_json": force_json,
            "exception": str(e),
        }


def main():
    out_path = Path(__file__).parent / "B_F1_0_yunwu_probe.json"
    results = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "base_url": BASE_URL, "probes": []}
    for m in MODELS:
        for fj in (True, False):
            r = probe(m, force_json=fj)
            results["probes"].append(r)
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print("---")
            time.sleep(1)

    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[OK] saved -> {out_path}")

    # 强制门：每个 model 至少有一种调用方式返回 200 + 含 choices[0].message.content
    pass_models = set()
    for r in results["probes"]:
        if r.get("http_status") == 200 and r.get("has_message_content"):
            pass_models.add(r["model"])
    fail = set(MODELS) - pass_models
    print(f"\n[F1-0 GATE] passed: {sorted(pass_models)}")
    if fail:
        print(f"[F1-0 GATE] FAILED for: {sorted(fail)}")
        sys.exit(1)
    print("[F1-0 GATE] PASS — all 3 models OK")


if __name__ == "__main__":
    main()
