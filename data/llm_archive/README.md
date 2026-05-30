# LLM 复现性归档 (decision A — Zenodo 交付)

本目录的归档实体（每日 `responses/*.jsonl`，LLM 原始响应；顶刊 V4 F-P2.1 复现硬约束）
**不进 git**（当前 ~332MB，将增至 ~25GB），改由 **Zenodo** 托管并凭 **DOI** 引用 —
避免 git LFS 的存储/带宽成本，数据永久可引用。

- git **仅追踪** `manifest.json` — 每文件 SHA-256 + 记录数 + 字节数的索引。
- 归档实体 `responses/*.jsonl` 被 repo 根 `.gitignore` 排除（manifest.json 不在
  `responses/` 下，故仍可被 git 追踪）。

## 复现者：取回 + 校验
1. clone 本仓库（自带 `manifest.json` 与取回脚本）。
2. 从 Zenodo 下载 `responses.zip`（record "Bank FinTech"，**Open access / CC-BY-4.0**，可直接下载），
   解压到 **`data/llm_archive/`**：
   - **DOI: `10.5281/zenodo.20453766`**
   - ⚠ zip 内已含 `responses/` 子目录 → 解压到 **`data/llm_archive/`**（**不是**
     `data/llm_archive/responses/`，否则会嵌套成 `responses/responses/`）。
     解压后即得 `data/llm_archive/responses/*.jsonl`（5 个文件，~332MB）。
3. 校验完整性（repo 根运行）：
   ```bash
   python news_process/scripts/data_acquisition/fetch_llm_archive.py
   ```
   返回 `[OK]` 即表示下载的归档与作者发布版 **byte-for-byte 一致**（SHA-256）。

## 作者：一次性发布步骤
1. 把 `data/llm_archive/responses/` 打包上传 Zenodo（单条记录免费 ≤ 50GB），取得 DOI。
2. 把 DOI 填进：本 README 顶部 DOI 行 + `scripts/data_acquisition/fetch_llm_archive.py::ZENODO_DOI`。
3. 提交 `manifest.json`（已在 git）+ DOI 更新；**实体 jsonl 不进 git**。

## 当前快照
- 文件：5 个每日 jsonl（2026-05-25 ~ 2026-05-29）
- 记录：25638；字节：348,009,536（~332MB）
- prompt_version_anchor：`v8`；prompt_sha256：见 `manifest.json`
- 本地校验：`verify_manifest()` = PASS（2026-05-30 迁移后生成）
- **Zenodo 端到端核验（2026-05-30）**：下载 DOI 的 `responses.zip` → 解压 → 5 个 jsonl
  与本 `manifest.json` **SHA-256 byte-for-byte 一致** ✓（复现性成立；zip 内为 `responses/` 嵌套结构）
