"""把 STATA_INDICATORS_CATALOG.html 渲染为 PDF。

⚠ 暂不可用: 源 catalog docs/STATA_INDICATORS_CATALOG.md 已删 (commit af80749b/1698bda5),
且依赖的 convert_catalog_to_html.py 同样失效; refresh_html_if_needed() 会在 MD.exists() 检查处
SystemExit。待 catalog 源文件重建后方可启用。

依赖 Microsoft Edge headless（Windows 自带），不引入 LaTeX / weasyprint /
wkhtmltopdf 等额外重型依赖。如果 HTML 缺失或比 MD 旧，会先调用
`convert_catalog_to_html.py` 刷新。

输入：news_process/docs/STATA_INDICATORS_CATALOG.md  (+ .html)
输出：news_process/docs/STATA_INDICATORS_CATALOG.pdf

用法（仓库根目录）：
    F:/Anaconda3/python.exe news_process/scripts/convert_catalog_to_pdf.py
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Windows PowerShell 默认 cp936，避免中文进度输出乱码
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MD = ROOT / "docs" / "STATA_INDICATORS_CATALOG.md"
HTML = ROOT / "docs" / "STATA_INDICATORS_CATALOG.html"
PDF = ROOT / "docs" / "STATA_INDICATORS_CATALOG.pdf"
HTML_CONVERTER = HERE / "convert_catalog_to_html.py"

# Edge 安装路径候选（按 Windows 实际分布优先级排序）
EDGE_CANDIDATES = [
    Path(r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    Path(r"C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
]

# Edge headless 等待 MathJax CDN + 代码高亮渲染的上限（毫秒）
VIRTUAL_TIME_BUDGET_MS = 20000

# 轮询 PDF 写出的最大耗时；Edge 渲染本身通常 ~10s
RENDER_TIMEOUT_S = 90

# 轮询间隔；连续 STABLE_TICKS 次大小相同认为 PDF 写完
POLL_INTERVAL_S = 1.0
STABLE_TICKS = 2


def find_edge() -> Path:
    for p in EDGE_CANDIDATES:
        if p.exists():
            return p
    raise SystemExit(
        "未找到 msedge.exe；本脚本依赖 Microsoft Edge headless。"
        f"\n  已检查：{[str(p) for p in EDGE_CANDIDATES]}"
        "\n  请安装 Edge 或编辑 EDGE_CANDIDATES。"
    )


def refresh_html_if_needed() -> None:
    """若 HTML 不存在或比 MD 旧，重新调用 HTML converter 刷新。"""
    if not MD.exists():
        raise SystemExit(f"源 markdown 不存在：{MD}")

    if HTML.exists() and HTML.stat().st_mtime >= MD.stat().st_mtime:
        print(f"  HTML 已是最新（{HTML.name}），跳过 markdown→html。")
        return

    if not HTML_CONVERTER.exists():
        raise SystemExit(f"HTML converter 缺失：{HTML_CONVERTER}")

    print(f"  刷新 HTML（{HTML_CONVERTER.name}）...")
    subprocess.run([sys.executable, str(HTML_CONVERTER)], check=True)


def render_pdf(edge: Path) -> None:
    file_url = HTML.resolve().as_uri()

    # 先清掉旧 PDF，避免轮询误判旧文件已稳定
    if PDF.exists():
        PDF.unlink()

    # Edge headless 在 Windows 上经常被 sync / encryption_keys_fetcher /
    # qqbrowser_importer 等后台任务挂住不退出，即使 PDF 早已写完。
    # 对策：① 临时 user-data-dir 让它没有真实 profile 可同步；
    # ② 关掉所有 background networking / sync / extension；
    # ③ 用 Popen + 轮询 PDF 大小稳定，主动 terminate 进程。
    with tempfile.TemporaryDirectory(prefix="edge_pdf_") as user_data_dir:
        cmd = [
            str(edge),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--virtual-time-budget={VIRTUAL_TIME_BUDGET_MS}",
            "--run-all-compositor-stages-before-draw",
            f"--user-data-dir={user_data_dir}",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-default-apps",
            "--disable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
            f"--print-to-pdf={PDF}",
            file_url,
        ]
        print(f"  Edge headless 渲染 → {PDF.name} ...")
        proc = subprocess.Popen(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        try:
            _wait_for_pdf(proc)
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()


def _wait_for_pdf(proc: subprocess.Popen) -> None:
    """轮询 PDF 文件，连续 STABLE_TICKS 次大小相同视为写完。"""
    deadline = time.monotonic() + RENDER_TIMEOUT_S
    last_size = -1
    stable = 0
    while time.monotonic() < deadline:
        # Edge 自己退出 — 检查产物，不再继续等
        if proc.poll() is not None:
            if PDF.exists() and PDF.stat().st_size > 0:
                return
            raise SystemExit(
                f"Edge 退出 (code={proc.returncode}) 但未写出 PDF"
            )

        if PDF.exists():
            size = PDF.stat().st_size
            if size > 0 and size == last_size:
                stable += 1
                if stable >= STABLE_TICKS:
                    return
            else:
                stable = 0
                last_size = size
        time.sleep(POLL_INTERVAL_S)

    raise SystemExit(
        f"等待 PDF 渲染超时（{RENDER_TIMEOUT_S}s）；最后文件大小 {last_size}"
    )


def main() -> None:
    refresh_html_if_needed()
    edge = find_edge()
    render_pdf(edge)

    if not PDF.exists():
        # Edge returncode=0 但没写出文件 — 极少见，通常是 print-to-pdf
        # 路径有权限/磁盘问题。
        raise SystemExit("Edge 报成功但未写出 PDF；检查路径与磁盘权限。")
    size_mb = PDF.stat().st_size / (1024 * 1024)
    print(f"OK: 写出 {PDF}  ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()
