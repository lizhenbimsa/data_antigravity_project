# -*- coding: utf-8 -*-
"""
AutoPaper 生产基础设施 — 统一 LLM 客户端
==========================================
所有模型统一通过 yunwu.ai 代理调用（OpenAI 兼容格式）。
支持重试、速率限制、Token 追踪和结构化日志。
"""

import time
import json
import hashlib
from abc import ABC, abstractmethod
from typing import Optional, Generator
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from config import ModelConfig, setup_logging

logger = setup_logging("paper.llm")


# ============================================================
# 1. 调用结果数据类
# ============================================================

@dataclass
class LLMResponse:
    """LLM 调用结果的统一封装"""
    content: str                            # 生成的文本
    model: str                              # 实际使用的模型 ID
    provider: str                           # 提供商
    input_tokens: int = 0                   # 输入 tokens
    output_tokens: int = 0                  # 输出 tokens
    total_tokens: int = 0                   # 总 tokens
    latency_ms: float = 0.0                 # 延迟（毫秒）
    finish_reason: str = ""                 # 停止原因
    cost_usd: float = 0.0                   # 估算成本（美元）
    request_id: str = ""                    # 请求唯一标识


@dataclass
class TokenTracker:
    """Token 使用量追踪器"""
    total_input: int = 0
    total_output: int = 0
    total_cost: float = 0.0
    call_count: int = 0

    def record(self, resp: LLMResponse):
        self.total_input += resp.input_tokens
        self.total_output += resp.output_tokens
        self.total_cost += resp.cost_usd
        self.call_count += 1

    def summary(self) -> str:
        return (
            f"📊 Token 统计: {self.call_count} 次调用 | "
            f"输入 {self.total_input:,} | 输出 {self.total_output:,} | "
            f"估算成本 ${self.total_cost:.4f}"
        )


# 全局 Token 追踪器
_global_tracker = TokenTracker()


def get_global_tracker() -> TokenTracker:
    return _global_tracker


# ============================================================
# 2. 抽象基类
# ============================================================

class BaseLLMClient(ABC):
    """LLM 客户端抽象基类"""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.client = httpx.Client(
            timeout=httpx.Timeout(config.timeout, connect=30.0),
            follow_redirects=True,
        )

    @abstractmethod
    def _raw_generate(
        self,
        messages: list[dict],
        system: str = "",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """由子类实现的原始 API 调用"""
        ...

    def generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        json_mode: bool = False,
    ) -> LLMResponse:
        """
        统一生成接口（带重试）。

        Args:
            prompt: 用户消息
            system: 系统提示词
            max_tokens: 最大输出 tokens
            temperature: 采样温度
            json_mode: 是否强制 JSON 输出

        Returns:
            LLMResponse 对象
        """
        messages = [{"role": "user", "content": prompt}]
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature if temperature is not None else self.config.temperature

        last_error = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                t0 = time.time()
                resp = self._raw_generate(
                    messages=messages,
                    system=system,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    json_mode=json_mode,
                )
                resp.latency_ms = (time.time() - t0) * 1000
                resp.request_id = hashlib.md5(
                    f"{time.time()}{prompt[:50]}".encode()
                ).hexdigest()[:12]

                _global_tracker.record(resp)

                logger.info(
                    f"✅ [{self.config.name}] 生成成功 | "
                    f"{resp.output_tokens} tokens | "
                    f"{resp.latency_ms:.0f}ms | "
                    f"id={resp.request_id}"
                )
                return resp

            except httpx.HTTPStatusError as e:
                last_error = e
                status = e.response.status_code
                if status == 429:
                    wait = self.config.retry_delay * attempt * 2
                    logger.warning(
                        f"⏳ [{self.config.name}] 速率限制 (429)，"
                        f"等待 {wait:.1f}s 后重试... ({attempt}/{self.config.max_retries})"
                    )
                    time.sleep(wait)
                elif status >= 500:
                    wait = self.config.retry_delay * attempt
                    logger.warning(
                        f"🔄 [{self.config.name}] 服务器错误 ({status})，"
                        f"等待 {wait:.1f}s 后重试... ({attempt}/{self.config.max_retries})"
                    )
                    time.sleep(wait)
                else:
                    logger.error(f"❌ [{self.config.name}] HTTP {status}: {e}")
                    raise

            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_error = e
                wait = self.config.retry_delay * attempt
                logger.warning(
                    f"🔄 [{self.config.name}] 连接超时，"
                    f"等待 {wait:.1f}s 后重试... ({attempt}/{self.config.max_retries})"
                )
                time.sleep(wait)

        raise RuntimeError(
            f"[{self.config.name}] 在 {self.config.max_retries} 次重试后仍然失败: {last_error}"
        )

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ============================================================
# 3. Anthropic 客户端（Claude）
# ============================================================

class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API 客户端"""

    API_URL = "https://api.anthropic.com/v1/messages"

    def _raw_generate(self, messages, system="", max_tokens=None,
                      temperature=None, json_mode=False) -> LLMResponse:
        headers = {
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": self.config.model_id,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "messages": messages,
        }
        if system:
            body["system"] = system

        resp = self.client.post(self.API_URL, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()

        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block["text"]

        usage = data.get("usage", {})
        return LLMResponse(
            content=content,
            model=data.get("model", self.config.model_id),
            provider="anthropic",
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
            finish_reason=data.get("stop_reason", ""),
        )


# ============================================================
# 4. OpenAI 客户端（GPT / Codex）
# ============================================================

class OpenAIClient(BaseLLMClient):
    """OpenAI API 客户端"""

    API_URL = "https://api.openai.com/v1/chat/completions"

    def _raw_generate(self, messages, system="", max_tokens=None,
                      temperature=None, json_mode=False) -> LLMResponse:
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        body = {
            "model": self.config.model_id,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "messages": full_messages,
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}

        url = getattr(self.config, 'base_url', None) or self.config.api_base_url or self.API_URL
        if not url.endswith("/chat/completions"):
            url = url.rstrip("/") + "/chat/completions"

        resp = self.client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})
        return LLMResponse(
            content=choice["message"]["content"],
            model=data.get("model", self.config.model_id),
            provider="openai",
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            finish_reason=choice.get("finish_reason", ""),
        )


# ============================================================
# 5. xAI 客户端（Grok）— 兼容 OpenAI 格式
# ============================================================

class XAIClient(OpenAIClient):
    """xAI Grok API 客户端（兼容 OpenAI chat/completions 接口）"""

    def _raw_generate(self, messages, system="", max_tokens=None,
                      temperature=None, json_mode=False) -> LLMResponse:
        resp = super()._raw_generate(
            messages, system, max_tokens, temperature, json_mode
        )
        resp.provider = "xai"
        return resp


# ============================================================
# 6. Google 客户端（Gemini）
# ============================================================

class GoogleClient(BaseLLMClient):
    """Google Gemini API 客户端"""

    API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

    def _raw_generate(self, messages, system="", max_tokens=None,
                      temperature=None, json_mode=False) -> LLMResponse:
        url = (
            f"{self.API_BASE}/{self.config.model_id}:generateContent"
            f"?key={self.config.api_key}"
        )
        contents = []
        for msg in messages:
            contents.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [{"text": msg["content"]}],
            })

        body = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens or self.config.max_tokens,
                "temperature": temperature if temperature is not None else self.config.temperature,
            },
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        if json_mode:
            body["generationConfig"]["responseMimeType"] = "application/json"

        resp = self.client.post(url, json=body)
        resp.raise_for_status()
        data = resp.json()

        content = ""
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            content = "".join(p.get("text", "") for p in parts)

        usage = data.get("usageMetadata", {})
        return LLMResponse(
            content=content,
            model=self.config.model_id,
            provider="google",
            input_tokens=usage.get("promptTokenCount", 0),
            output_tokens=usage.get("candidatesTokenCount", 0),
            total_tokens=usage.get("totalTokenCount", 0),
            finish_reason=candidates[0].get("finishReason", "") if candidates else "",
        )


# ============================================================
# 7. 工厂函数
# ============================================================

_CLIENT_MAP = {
    "anthropic": AnthropicClient,
    "openai": OpenAIClient,
    "xai": XAIClient,
    "google": GoogleClient,
}


def create_client(config: ModelConfig) -> BaseLLMClient:
    """根据 ModelConfig 创建对应的 LLM 客户端"""
    cls = _CLIENT_MAP.get(config.provider)
    if cls is None:
        raise ValueError(
            f"不支持的提供商: {config.provider}。"
            f"支持: {list(_CLIENT_MAP.keys())}"
        )
    return cls(config)


def generate_with_model(
    model_key: str,
    prompt: str,
    system: str = "",
    model_registry: Optional[dict] = None,
    **kwargs,
) -> LLMResponse:
    """
    便捷函数：通过模型 key 直接生成内容。

    Args:
        model_key: 模型注册表中的 key
        prompt: 用户提示
        system: 系统提示
        model_registry: 模型注册表（默认合并所有注册表）
        **kwargs: 传递给 generate() 的额外参数

    Returns:
        LLMResponse
    """
    from config import AUTHORING_MODELS, REVIEW_MODELS, JUDGE_MODELS

    if model_registry is None:
        model_registry = {**AUTHORING_MODELS, **REVIEW_MODELS, **JUDGE_MODELS}

    if model_key not in model_registry:
        raise KeyError(
            f"未知模型 key: {model_key}。"
            f"可用: {list(model_registry.keys())}"
        )

    config = model_registry[model_key]
    with create_client(config) as client:
        return client.generate(prompt=prompt, system=system, **kwargs)


# ============================================================
# 8. 文件生成辅助
# ============================================================

def generate_to_file(
    model_key: str,
    prompt: str,
    output_path: Path | str,
    system: str = "",
    **kwargs,
) -> LLMResponse:
    """
    生成内容并直接写入文件。
    如果输出被 ``` 代码块包裹，自动剔除。

    Args:
        model_key: 模型 key
        prompt: 用户提示
        output_path: 输出文件路径
        system: 系统提示
        **kwargs: 传递给 generate()

    Returns:
        LLMResponse
    """
    resp = generate_with_model(model_key, prompt, system, **kwargs)
    content = resp.content.strip()
    import re
    # 匹配最外层的 ```...``` 代码块，允许前面有文字
    match = re.search(r"```[a-zA-Z0-9_-]*\s*\n(.*?)\n```", content, flags=re.IGNORECASE | re.DOTALL)
    if match:
        content = match.group(1).strip()
    elif content.startswith("```"):
        # 回退处理如果缺少闭合
        content = re.sub(r"^```[a-zA-Z0-9_-]*\s*\n", "", content, flags=re.IGNORECASE)
        content = re.sub(r"\n```.*", "", content, flags=re.DOTALL).strip()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    logger.info(f"📄 内容已写入: {output_path} ({len(content)} 字符)")
    return resp


# ============================================================
# 9. 自测
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AutoPaper LLM 客户端自测")
    print("=" * 60)
    print(f"\n支持的提供商: {list(_CLIENT_MAP.keys())}")
    print(f"Token 使用统计: {_global_tracker.summary()}")

    # 验证工厂函数
    from config import AUTHORING_MODELS, REVIEW_MODELS
    for key, cfg in {**AUTHORING_MODELS, **REVIEW_MODELS}.items():
        try:
            client = create_client(cfg)
            print(f"  ✅ {key}: {cfg.name} ({cfg.provider}/{cfg.model_id})")
            client.close()
        except EnvironmentError as e:
            print(f"  ⚠️  {key}: API Key 未配置 — {e}")
        except Exception as e:
            print(f"  ❌ {key}: {e}")
