# LLM 复现性归档 (decision A — Zenodo 交付)

本目录的归档实体（每日 `responses/*.jsonl`，LLM 原始响应；顶刊 V4 F-P2.1 复现硬约束）
**不进 git**（当前 ~332MB，将增至 ~25GB），改由 **Zenodo** 托管并凭 **DOI** 引用 —
避免 git LFS 的存储/带宽成本，数据永久可引用。

- git **仅追踪** `manifest.json` — 每文件 SHA-256 + 记录数 + 字节数的索引。
- 归档实体 `responses/*.jsonl` 被 repo 根 `.gitignore` 排除（manifest.json 不在
  `responses/` 下，故仍可被 git 追踪）。

## 复现者：取回 + 校验
1. clone 本仓库（自带 `manifest.json` 与取回脚本）。
2. 从 Zenodo 下载归档，解压到 `data/llm_archive/responses/`：
   - **DOI: `10.5281/zenodo.20453766`**（Zenodo record "Bank FinTech" v1）
   - ⚠ **该记录文件当前为受限访问（Restricted）**：若直接下载提示需权限，请在
     Zenodo 记录页点 **"Request access"** 向作者申请，审批后即可下载。
     （若作者已将文件改为 Open，可直接下载。）
3. 校验完整性（repo 根运行）：
   ```bash
   python news_process/scripts/data_acquisition/fetch_llm_archive.py
   ```
   返回 `[OK]` 即表示下载的归档与作者发布版 **byte-for-byte 一致**（SHA-256）。

## 作者：一次性发布步骤
1. 把 `data/llm_archive/responses/` 打包上传 Zenodo（单条记录免费 ≤ 50GB），取得 DOI。
2. 把 DOI 填进：本 README 第 16 行 + `scripts/data_acquisition/fetch_llm_archive.py::ZENODO_DOI`。
3. 提交 `manifest.json`（已在 git）+ DOI 更新；**实体 jsonl 不进 git**。

## 当前快照
- 文件：5 个每日 jsonl（2026-05-25 ~ 2026-05-29）
- 记录：25638；字节：~332MB
- prompt_version_anchor：`v8`；prompt_sha256：见 `manifest.json`
- 校验：`verify_manifest()` = PASS（生成于 2026-05-30 迁移后）
