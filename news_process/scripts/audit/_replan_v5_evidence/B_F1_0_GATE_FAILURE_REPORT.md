# F1-0 强制门失败报告 — 致命阻塞

**生成时间**：2026-05-05 ~01:11 (UTC+8)
**触发动作**：[E1] / 全量执行被强制中止（按 v5 计划 §F1-0 强制门规则）

---

## 1. 客观事实

### 1.1 当前 sentiment.yaml 锁定的 3 个 model_name

```
- gpt-5.4-nano                       (slot: gpt54nano)
- gemini-3.1-flash-lite-preview      (slot: gemini3111)
- deepseek-v4-flash                  (slot: claude4h → 计划重命名为 deepseek4f)
```

### 1.2 F1-0 主探针结果（每个 model 各 2 次：force_json on/off）

| Model | HTTP | 错误信息 |
|---|---|---|
| gpt-5.4-nano (force_json=true) | **403** | "无访问该模型权限 gpt-5.4-nano" |
| gpt-5.4-nano (force_json=false) | **403** | 同上 |
| gemini-3.1-flash-lite-preview (force_json=true) | **403** | "无访问该模型权限 gemini-3.1-flash-lite-preview" |
| gemini-3.1-flash-lite-preview (force_json=false) | **403** | 同上 |
| deepseek-v4-flash (force_json=true) | **403** | "无访问该模型权限 deepseek-v4-flash" |
| deepseek-v4-flash (force_json=false) | **403** | 同上 |

> 错误消息原文为中文 "无访问该模型权限 \<model\>"，工具显示为 GBK 编码乱码 `��������Ȩ����ģ��`，可在 `B_F1_0_yunwu_probe.json` 查看 raw 内容。

### 1.3 F1-0b 备援探针（12 个候选 model 的全谱测试）

| Model | HTTP | 状态 |
|---|---|---|
| gpt-4o-mini | 403 | 无权限 |
| gpt-4o | 403 | 无权限 |
| gpt-3.5-turbo | 403 | 无权限 |
| deepseek-chat | 403 | 无权限 |
| claude-3-5-haiku-20241022 | 403 | 无权限 |
| gemini-1.5-flash | 403 | 无权限 |
| gemini-2.0-flash | 403 | 无权限 |
| gemini-2.0-flash-exp | 403 | 无权限 |
| **gpt-5.4-nano** | **200** | **✅ 唯一可用** |
| glm-4.5-flash | 403 | 无权限 |
| gpt-5-nano | 403 | 无权限 |
| gpt-5 | 403 | 无权限 |

---

## 2. 根因诊断（多重交叉验证）

| 假设 | 排除/确认 |
|---|---|
| API key 已失效 / 欠费 | **排除**：`gpt-5.4-nano` 200 OK |
| API key 限速 | **排除**：12 个连续调用，单一 model 200，其他全 403，与速率无关 |
| 网络/路由问题 | **排除**：12 个调用全部到达 yunwu 服务并返回结构化 JSON 错误 |
| force_json 兼容性 | **排除**：force_json on/off 均 403 |
| Yunwu 账户**仅授权 gpt-5.4-nano 一个 model** | ✅ **唯一与全部观察一致的结论** |

**根本原因**：当前 `YUNWU_API_KEY` 对应的账户**仅授权访问 `gpt-5.4-nano` 一个模型**。`sentiment.yaml` 中的三个新模型（v5 计划假设可用）以及历史 `glm-4.5-flash`、所有常见 OpenAI / Anthropic / Google / DeepSeek 通用模型**全部无权限**。

---

## 3. 对 v5 计划的连锁影响

| 阶段 | 影响 |
|---|---|
| **Phase B 剩余诊断**（F1-1 ~ F1-4 / F2-1 ~ F2-4） | F1-1/F1-2 依赖 LLM 调用 → 立即失败；F1-3/F1-4/F2-* 是 read-only parquet/cache 分析，仍可执行 |
| **Phase C [E1] 重跑 Stage 21** | **必然全部 403**：3 个 model_name 中无一个可用 → 整个 21 阶段崩溃；进而 F1 / F2 / N8 元数据列全部无法实施 |
| Phase D [E2] | 不直接依赖 LLM；F3 (NaN 处理) + F4 (IV 修剪) 仍可独立实施。**但**：若 21 输出未刷新，新 panel 仍承袭旧 LLM 标签错位 → F2 修复失效 |
| Phase E [E3] | 受 F1/F2 是否修复决定 |

---

## 4. 决策选项（请用户选择后再行授权）

### 选项 A：恢复 yunwu 模型权限（推荐 — 修复源头）
- 联系 yunwu 客服或自助充值/续期，开通至少以下三个 model 中的所有：
  - `gpt-5.4-nano`（或回退 `gpt-5.4-nano`）
  - `gemini-3.1-flash-lite-preview`（或回退到任一可用 Gemini）
  - `deepseek-v4-flash`（或回退到 `deepseek-chat` / `deepseek-v3` 等）
- 恢复后重新运行 `news_process/scripts/audit/_replan_v5_evidence/B_F1_0_yunwu_probe.py`，强制门通过即可恢复 [E1]
- **学术影响**：v5 计划完整执行；三家族 inter-model agreement 叙述成立

### 选项 B：sentiment.yaml 回退至唯一可用模型
- 把 3 个 slot 全部指向 `gpt-5.4-nano`（或同一可用 model 的不同温度）
- **学术影响**：**严重**——三角验证退化为单模型重复采样；论文方法学需明确说明这一限制；F2 篇章级修复仍可实施；F1 修复部分失效（无法解决错位的根本问题，因为已无独立模型）

### 选项 C：切换 LLM 提供方（中等成本）
- 改用 OpenAI / Anthropic / Google 直连，或换其他聚合代理（aigcbest / openrouter）
- 需要：新 API key、可能需要更新 base_url / payload schema 兼容
- **学术影响**：与选项 A 相当，但 v5 计划需要二次微调（base_url 等）

### 选项 D：跳过 LLM 重跑，仅在面板层做事后近似
- 接受 Phase C [E1] 中的"轻量补丁"路径（v4 计划中的象限 ① 子选项）
- 不重跑 Stage 21，直接在 Phase D [E2] 跑 F3+F4 修复，并在 panel 层加 mask 缓解 F2
- **学术影响**：F2 篇章级问题无法源头修复；论文需明确声明这一缺陷；F1 错位仍存在（21 输出 column 名不动 = 历史 OpenAI/GLM 输出永远沿用 gemini3111/claude4h 标签）

---

## 5. 当前执行状态

- ✅ Phase A 数据状态盘点完成（report `A5_data_state_audit.md`）
- ⛔ **Phase B F1-0 强制门失败 → 全量执行中止**
- 文件系统状态：**仅追加了 `news_process/scripts/audit/_replan_v5_evidence/` 5 个证据文件**，**未修改**任何 `.py` / `.yaml` / `.json` / `.parquet` / `.dta` / `.do` / `.tmpl` / `.env` / `.sqlite`
- git 状态：`replan-v5-anchor-pre-audit` tag 已创建；尚无 commit

---

## 6. 待用户授权的下一步动作

> 在用户**显式选择 A/B/C/D 之一**前，本计划保持完全静默：
> - ⛔ 不再调用任何 LLM API
> - ⛔ 不修改 sentiment.yaml 或 .env
> - ⛔ 不启动 [E1] / [E2] / [E3]
> - ⛔ 不创建任何代码改动

请告知决策。
