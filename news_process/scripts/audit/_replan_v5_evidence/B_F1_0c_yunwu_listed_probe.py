"""F1-0c: 探针 yunwu /v1/models 实际返回清单中的全部 chat 模型，
    确定 B 方案下是否仍可保留真正的三家族三角验证。

候选清单（来自 /v1/models 端点）:
    - gemini-3.1-flash-lite-preview   (Google 候选)
    - gpt-5.4-nano                (已确认 200 OK)
    - deepseek-v4-flash          (DeepSeek 候选)

每个 model 测：
    1) 最小 chat 调用 (force_json=True)
    2) 最小 chat 调用 (force_json=False)
    3) 一次模拟 sentiment.yaml 真实场景的 prompt（含 JSON 输出要求）
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

CANDIDATES = [
    "gpt-5.4-nano",
    "gemini-3.1-flash-lite-preview",
    "deepseek-v4-flash",
]

REAL_PROMPT = """你是金融文本情感分析专家。请阅读以下文章片段，仅输出单行 JSON：
{"is_bank_fintech_news": true/false, "sentiment": "正面"/"中性"/"负面", "verification_confidence": 0.0-1.0, "sentiment_confidence": 0.0-1.0, "reason": "<<=30 字>"}

文章片段：工商银行近日发布数字人民币钱包升级公告，新增智能合约功能，进一步推动金融科技应用落地。"""


def call(model: str, mode: str, content: str = "hi", force_json: bool = True) -> dict:
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.0,
        "max_tokens": 200,
    }
    if force_json:
        payload["response_format"] = {"type": "json_object"}
    t0 = time.time()
    try:
        r = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, timeout=60)
        elapsed_ms = int((time.time() - t0) * 1000)
        try:
            body = r.json()
        except Exception:
            body = {"_raw": r.text[:500]}
        return {
            "model": model,
            "mode": mode,
            "force_json": force_json,
            "http_status": r.status_code,
            "elapsed_ms": elapsed_ms,
            "ok": r.status_code == 200 and "choices" in body,
            "model_field": body.get("model") if isinstance(body, dict) else None,
            "system_fingerprint": body.get("system_fingerprint") if isinstance(body, dict) else None,
            "usage": body.get("usage") if isinstance(body, dict) else None,
            "content_preview": (
                body["choices"][0]["message"].get("content", "")[:400]
                if isinstance(body, dict) and body.get("choices") and "message" in body["choices"][0]
                else None
            ),
            "error_msg": (body.get("error", {}) or {}).get("message")
            if isinstance(body, dict)
            else None,
        }
    except requests.RequestException as e:
        return {"model": model, "mode": mode, "force_json": force_json, "ok": False, "exception": str(e)}


def main():
    out = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "base_url": BASE_URL, "probes": []}
    for m in CANDIDATES:
        # mode 1: minimal hi (force_json on)
        r = call(m, "minimal_force_json", "hi", True)
        out["probes"].append(r)
        print(f"[{m}] minimal force_json=True -> {r.get('http_status')} {'OK' if r.get('ok') else r.get('error_msg')}")
        time.sleep(0.5)

        # mode 2: minimal hi (force_json off)
        r = call(m, "minimal_no_force_json", "hi", False)
        out["probes"].append(r)
        print(f"[{m}] minimal force_json=False -> {r.get('http_status')} {'OK' if r.get('ok') else r.get('error_msg')}")
        time.sleep(0.5)

        # mode 3: real-world prompt
        r = call(m, "real_world", REAL_PROMPT, True)
        out["probes"].append(r)
        print(f"[{m}] real_world force_json=True -> {r.get('http_status')} {'OK' if r.get('ok') else r.get('error_msg')}")
        if r.get("ok"):
            print(f"    content: {r.get('content_preview')!r}")
        time.sleep(0.5)

    succ_models = sorted({r["model"] for r in out["probes"] if r.get("ok")})
    full_succ_models = sorted({
        r["model"] for r in out["probes"]
        if r.get("ok") and any(p["model"] == r["model"] and p["mode"] == "real_world" and p.get("ok") for p in out["probes"])
    })
    out["summary"] = {
        "any_success": succ_models,
        "real_world_success": full_succ_models,
    }
    print(f"\n[summary] any-mode OK: {succ_models}")
    print(f"[summary] real-world OK: {full_succ_models}")

    out_path = Path(__file__).parent / "B_F1_0c_yunwu_listed_probe.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[OK] saved -> {out_path}")


if __name__ == "__main__":
    main()
