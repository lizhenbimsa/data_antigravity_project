"""F1-0b 备援探针：当主 3 个 model_name 全部 403 时，

[⚠ 2026-08-02 状态订正] 本探针针对 **yunwu.ai** 端点 (成文当时的聚合代理)。
2026-08-02 起全项目已迁移至 OpenLux (https://api.openlux.ai/v1, OPENLUX_API_KEY)。
本文件保留原样作历史取证 —— 其记录的是当时对 yunwu.ai 的真实实测结果, 不代表
当前生产端点; 如需对 OpenLux 做同类探测, 请另写新探针, 勿改本文件。
    检验 API key 整体是否还有效（vs 仅对这三个模型无权限）。

测试一组通用回退模型 + /models endpoint，确定根因：
    根因 A：API key 已失效或欠费 → 所有调用都会 401/403
    根因 B：仅特定模型权限缺失 → 通用 gpt-4o-mini / gpt-3.5-turbo 等可调
    根因 C：服务路由问题 → 个别可调，个别不行
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests

ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
if ENV_PATH.exists():
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ.get("GPT5NANO_API_KEY") or os.environ.get("YUNWU_API_KEY")
BASE_URL = "https://yunwu.ai/v1"

FALLBACK_MODELS = [
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-3.5-turbo",
    "deepseek-chat",
    "claude-3-5-haiku-20241022",
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gpt-5.4-nano",
    "glm-4.5-flash",
    "gpt-5-nano",
    "gpt-5",
]


def call(model: str) -> dict:
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "hi"}],
        "max_tokens": 5,
    }
    t0 = time.time()
    try:
        r = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=30)
        elapsed_ms = int((time.time() - t0) * 1000)
        try:
            body = r.json()
        except Exception:
            body = {"_raw": r.text[:300]}
        return {
            "model": model,
            "http_status": r.status_code,
            "elapsed_ms": elapsed_ms,
            "ok": r.status_code == 200 and "choices" in body,
            "error_msg": (body.get("error", {}) or {}).get("message")
            if isinstance(body, dict)
            else None,
            "model_field": body.get("model") if isinstance(body, dict) else None,
            "content_preview": (
                body["choices"][0]["message"].get("content", "")[:80]
                if isinstance(body, dict) and body.get("choices")
                else None
            ),
        }
    except requests.RequestException as e:
        return {"model": model, "http_status": None, "ok": False, "exception": str(e)}


def list_models() -> dict:
    headers = {"Authorization": f"Bearer {API_KEY}"}
    t0 = time.time()
    try:
        r = requests.get(f"{BASE_URL}/models", headers=headers, timeout=30)
        elapsed_ms = int((time.time() - t0) * 1000)
        try:
            body = r.json()
        except Exception:
            body = {"_raw": r.text[:500]}
        if isinstance(body, dict) and isinstance(body.get("data"), list):
            ids = [m.get("id") for m in body["data"][:80]]
            return {"http_status": r.status_code, "elapsed_ms": elapsed_ms, "count": len(body["data"]), "first_80_ids": ids}
        return {"http_status": r.status_code, "elapsed_ms": elapsed_ms, "body_preview": str(body)[:500]}
    except requests.RequestException as e:
        return {"exception": str(e)}


def main():
    out = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "base_url": BASE_URL, "key_prefix": API_KEY[:12] + "..."}
    out["models_endpoint"] = list_models()
    out["fallback_calls"] = []
    for m in FALLBACK_MODELS:
        r = call(m)
        out["fallback_calls"].append(r)
        print(f"{m:50s} -> {r.get('http_status')} {'OK' if r.get('ok') else (r.get('error_msg') or 'fail')}")
        time.sleep(0.5)

    succ = [r["model"] for r in out["fallback_calls"] if r.get("ok")]
    fail = [r["model"] for r in out["fallback_calls"] if not r.get("ok")]
    print(f"\n[summary] OK: {succ}")
    print(f"[summary] FAIL: {fail}")

    out_path = Path(__file__).parent / "B_F1_0b_yunwu_fallback_probe.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[OK] saved -> {out_path}")


if __name__ == "__main__":
    main()
