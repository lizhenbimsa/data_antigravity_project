# Exception Handling Policy

**适用范围**: `news_process/` 生产代码（不含 tests/）。

**Plan-r3 P2-14 落地（2026-05-09）** —— 二轮诊断曾把 100+ `except Exception` 列为反模式，
核验后纠正为：**裸 `except:` 0 处，`except Exception: pass/continue/...` 13 处**，全部为 deliberate 的
defensive / best-effort 模式。本文件作为这 13 处的 single source of truth，code review 时遇到
`except Exception: pass` 应先在此查阅，再决定是否要重新评估。

## 设计原则

1. **裸 `except:` 严禁** —— 会捕获 `KeyboardInterrupt` / `SystemExit`，破坏调试与 Ctrl-C。
   ruff 已默认报 `E722`，CI 会失败。
2. **`except Exception` 允许，但要求每处满足以下任一**：
   - (a) **best-effort cleanup** —— 异常处理路径上再做的清理动作（关流、kill 进程、删 lock），
         本身不应让外层异常被掩盖；
   - (b) **fallback try-multiple** —— `for cand in candidates: try ...; except: continue`
         模式，遍历多个候选直到成功，最后 fallback；
   - (c) **diagnostic-only** —— 读 sidecar / 元数据 / 缓存 hash 等"辅助信息"失败时不阻塞
         主流程；
   - (d) **subprocess 边界** —— 子进程超时/kill 二次失败时不让父进程崩溃。
3. **不允许的反模式**：吞 `KeyError` / `TypeError` / `ValueError` 等"上游 schema 不匹配"
   错误（应让它 propagate，让 N1/N2 schema 守护捕获）；吞 `FileNotFoundError`（应 raise 显式
   说明缺失文件）。

## 13 处现状清单（截至 HEAD `f856853`）

| # | 文件 | 行 | 原因分类 | 简述 |
|---|---|---|---|---|
| 1 | `core/locking.py` | 118 | (a) | `__enter__` 异常路径上 `lock_file.close()` 失败 best-effort |
| 2 | `core/locking.py` | 134 | (a) | `_handle_lock_failure` 内 close 失败 best-effort |
| 3 | `core/locking.py` | 178 | (a) | Windows `msvcrt.locking(LK_UNLCK)` 失败 best-effort（OS 在 process 死时自动释放） |
| 4 | `core/locking.py` | 184 | (a) | Unix `fcntl.flock(LOCK_UN)` 失败 best-effort（同上） |
| 5 | `core/stage.py` | 68 | (a) | reader thread 关闭 stream 失败 best-effort |
| 6 | `core/stage.py` | 172 | (d) | 子进程超时后 `proc.kill()` 失败 best-effort |
| 7 | `core/stage.py` | 188 | (d) | 等待子进程异常路径上 `proc.kill()` + `proc.wait()` 失败 best-effort |
| 8 | `pipeline/audit/stats_excel.py` | 31 | (a) | Windows GBK 控制台 `sys.stdout.reconfigure('utf-8')` 失败回退 |
| 9 | `pipeline/panel/export.py` | 274 | (a) | object→float64 转换失败留给下游 `to_stata` 处理（注释已说明） |
| 10 | `pipeline/panel/network_spillover.py` | 482 | (b) | eigenvector 三级 fallback 中间级失败继续 |
| 11 | `pipeline/preprocess/dedup.py` | 286 | (c) | `np.datetime64` 解析失败时跳过该日期对去重判定 |
| 12 | `pipeline/preprocess/runner.py` | 166 | (c) | 缓存配置 hash 比对异常时 fall-through 重处理 |
| 13 | `validation/prompt_sensitivity.py` | 826 | (b) | matplotlib 字体候选遍历，失败 continue |

## 不变量

- **任何新增 `except Exception: pass/continue` 必须在本文件登记**，PR 应当同时更新表格。
- 表格行数 ≥ 13。少于 13 表示有 fix 漏登记（grep `except Exception:` 与 grep `pass|continue|\\.\\.\\.` 配合复核）。
- ruff `BLE001` 当前未启用，但 v3.0 启用后所有 13 处需要加 `# noqa: BLE001  -- (a) best-effort cleanup` 之类注释。

## 复核命令

```bash
F:/Anaconda3/python.exe -c "
import re, pathlib
def excluded(p):
    s = str(p).replace('\\\\', '/')
    return any(x in s for x in ['__pycache__', '.egg-info', '/tests/', '.pytest_cache'])

hits = []
for p in pathlib.Path('news_process').rglob('*.py'):
    if excluded(p): continue
    text = p.read_text(encoding='utf-8', errors='ignore')
    for m in re.finditer(r'except\s+Exception[^:]*:\s*\n\s*(pass|continue|\.\.\.)', text):
        ln = text[:m.start()].count('\n') + 1
        hits.append((str(p), ln, m.group(1)))
print(f'共 {len(hits)} 处 (期望 13):')
for h in hits: print(f'  {h[0]}:{h[1]}  body={h[2]}')
"
```
