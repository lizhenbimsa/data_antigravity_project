# COMPANY_TAX_BANK_COOC_PANEL 执行计划 (v6, 2026-07-08)

> **状态: 计划待批, 未获用户明确允许不得执行任何实现步骤。**
> 母本 = `company_listed_bank/` 三步流水线 (权威计划
> `scripts/audit/COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-03.md` v34, 已实施
> main=0e741da1 起、fail-closed 硬化至 3f2f410a)。本计划**完全参照其做法与目录结构**,
> 把公司名单从上市公司 (5,528 家) 换成税调企业 (44,771 家), 替代权重从七权源裁成
> **银行分支机构一权源、拆城市/县域两层级**, 与银企共现报道权合计 **3 个权重互为稳健性**。
> v2 = v1 经四路对抗评审 (事实核查/口径计量/工程耦合/完备性, §9 记录) 修订:
> 2 P0 + 12 P1 全部落判定, P2 择要采纳。
> v3 = v2 经第二轮双向评审 (收敛核验判 converged / 新鲜终审判 needs-fix) 收口:
> 终审 4 P1 (两处新口径可实施性落字/字面量清单/县权可区分性) + 4 P2 + 3 处勘误全修。
> v4 = v3 经第三轮双路评审 (v3 增量终验 + 实施者视角走查, 均 needs-fix 轻量收口):
> 4 P1 (dv2 自举顺序/T-D5c 施加位置/county_key_ok gate 方向/grep 白名单) + 9 P2 全修;
> T-P0 探针 1/2/4/5/6/7 已实测, 结果落 §9。**获用户完全授权执行 (2026-07-08)。**

---

## §1 目标

新增一条**独立于主管道 DAG** 的三步派生数据流水线 `news_process/company_tax_bank/`:
把新闻库里"税调企业与银行在同一篇报道中共现"的信息, 加工成
**税调企业 × 年份 (2007–2025) 的计量面板** (dta + parquet), 并用
**城市层级**与**县域层级**的银行分支机构数据构造两个替代权重, 与共现报道权重
互为交叉验证 (三权互为稳健性、不分主次)。面板与外部数据的 merge 键 =
**`usci × year`** (18 位统一社会信用代码, 全填全唯一 — 税调数据的核心接入优势;
`company_tax_name × year` 为等价备用键)。

产出 (数据全部落 `company_tax_bank/data/`, 不入库; registry yaml 落 `config/` 入库):

| # | 文件 | 生产者 |
|---|---|---|
| 1 | `config/company_tax_bank_cooc_registry.yaml` (SSOT) | 01 |
| 2 | `company_tax_bank_cooc_panel.{dta,parquet}` + `company_tax_bank_cooc_panel_codebook.md` | 02 |
| 3 | `_company_tax_bank_cooc_pairs.parquet` (pair 长表, 内嵌指纹) | 02 |
| 4 | `_company_tax_bank_altweights_branch_city.parquet` + `company_tax_bank_branch_cityw_panel.{dta,parquet}` | 03 |
| 5 | `_company_tax_bank_altweights_branch_county.parquet` + `company_tax_bank_branch_countyw_panel.{dta,parquet}` | 03 |
| 6 | `_company_tax_bank_weight_validation.md` (三权互验报告) + codebook「双权面板章」upsert | 03 |

**命名推导规则 (钉死, 防两拼并存)**: scheme 字符串 = `branch_city` / `branch_county`;
长表 = `_company_tax_bank_altweights_{scheme}.parquet`; 面板 =
`company_tax_bank_{scheme}w_panel.{dta,parquet}` (镜像 listed
`company_bank_{scheme}w_panel` 推导式, scheme 内下划线原样保留);
中文标签词 `SCHEME_LABEL_WORD = {"branch_city": "城市网点",
"branch_county": "县域网点"}` (驱动 dta rel_* 标签/互验报告/codebook 双权章文案,
禁自造第二拼法); codebook 双权章标记成对字面量 =
`<!-- BEGIN 双替代权面板章 (03 生成, 勿手改) -->` / `<!-- END 双替代权面板章 -->`。

## §2 事实基础 (2026-07-08 本机实测, 经事实核查评审员复核; 非估算)

**F1 税调名单** `config/company_tax_names.yaml` (v1.0.0, 2026-07-07, 生成器
`scripts/generate_company_tax_names.py`; **已入库**, 由 `tax_survey_frims_names.yaml`
更名全量替换的谱系 = main e39955d0→8448e5df — registry `meta.company_names_sha256`
锚的即此盘上态): **44,771 家**, 键 `company_tax_name / usci / province / city /
district / address / variants`。实测: usci 18 位全填且**全局唯一**; 企业名全局唯一;
四地理字段+address **零缺失**; variants 合计 **124,366** 条 (≤4 字 1,353 条,
其中 2 字 32 / 3 字 21 — 短名假阳性风险见 §7-L1)。

**F2 地理字段分布**: city 共 324 值, 非标准值仅 `省直辖县级行政区划` /
`自治区直辖县级行政区划` 两个占位 (对应 listed `DV2.city_placeholder` 既有语义);
district 尾字分布 区 24,547 / 市 9,749 / 县 9,451 / **`-` 922** / 旗 102。
`-` 的 922 家中 **918 家**在东莞 (492)/中山 (294)/嘉峪关 (132) 三个无县级区划的
直筒子市, 另有 **4 家**零星散布 (南宁/温州/大连/巴音郭楞 — 有真县级区划但源数据
district 缺失, 定性为零星缺失而非直筒子)。

**F3 分支机构权源** `config/银行业金融机构基本信息表.dta` (恒不入库, 父仓
`.gitignore:72` 覆盖): **603,907 行 × 21 列**, 含 `HeadofficeName / ProvinceName /
CityName / CountyName / Status / ApprovalDate / QuitDate / RunawayDate` 等。
实测: ProvinceName 36 值 / CityName 502 值 (零缺失) / CountyName 4,607 值,
缺失 3,168 行 ≈0.52% 且**缺失形态是字面字符串 `"None"`** (非 NaN — 实现须显式
映射, 照搬 isna 判空会漏)。Status {0(持有): 550,359, 2(退出): 51,185, 1(失控): 2,363}。
CountyName 尾字: 区 310,831 / 县 182,890 / 市 92,922 / 旗 7,150 / 镇 5,073 /
街道·路等少量 (镇/街道级值集中在直筒子市, F5)。
**⚠ 网点侧 CityName 亦有脏值** (计量评审实测, R2 勘误后数字): 占位串
`省直辖县级行政区划` / `海南省直辖(县级行政区)` 等剥括注后 **225 行**
(琼中 100/屯昌 95/定安 22), 另 **47 行**带全角 `（注：…）` 批注、剥净后可解析
归伊犁州/喀什地区等 (直辖族 225+47=272 为并集总数; 全表带括注 131 行) — 见 T-D5c。

**F4 地理对齐率 (税调 × 分支 dta 直匹, 预清洗前原值)**:
- 城市层: `city` 直匹 CityName = **44,681/44,771 = 99.80%**; 未匹配 = 自治区直辖
  占位 90 家。⚠ 其中省直辖占位 54 家的"名义命中"是**占位串对上 dta 占位串**的假
  匹配 (非地理对齐); 预清洗 + 双侧 placeholder 回退 (T-D5c) 后城市层预期逼近 100%。
- 县域层: `(city, district)` 直匹 `(CityName, CountyName)` = **43,664/44,771 =
  97.53%**; 未匹配分解 (恰合计 1,107): ① district=`-` 922 家 (F2); ② 省/自治区
  直辖县级 **143 家** (石河子 60/仙桃 27/潜江 15 等 — 分支侧把这些县级市直接记在
  CityName, 石河子市 477 行实证; 另 1 家文昌撞 dta 脏占位行名义命中, 占位企业
  实际共 **144 家**); ③ 开发区/高新区等非民政区划 **42 家** (宿迁经开 7 等)。

**F5 直筒子市县名语义**: 东莞 3,730 网点县名=虎门镇 303/长安镇 251/…(镇级);
中山 1,622=小榄镇/石岐区/…; 嘉峪关 209=None 104/新华南路…(街道路级)。
→ 县域层对直筒子市**不可能**做真县级匹配 (T-D5b(ii))。

**F6 银行系税调企业**: 名称含"银行"或"农商" (listed 同款两 token 子串判据) 的
税调企业 = **280 家**, 以国有大行/股份行的**分行/支行法人记录**为主, 另含农商行
总行。计量评审逐家模拟 AC 映射: **244 家单命中 (抽查无误) / 34 家零命中**
(农发行分支/包商/村镇/农合/港外资 — 不在 canonical 1,767 名单) / **2 家多命中**
(浙江长兴农商 → {长兴农商, 山西兴县农商} 假阳性, 因 bank_names.json 内部存在
**71 组跨行 variant 子串对**; 中信银行国际(中国) → {中信银行, 中信银行国际}) —
own-bank 机器映射的裁决规则见 T-D3。
备注: 含 信用社/农信/农村商业 的五词宽口径本批**恰同为 280 家** (计数巧合,
非口径同源 — token 终集判定见 T-D3①)。

**F7 母本管线锚点** (实读, 经复核): 01=942 行 / 02=1,532 行 / 03=1,444 行 /
run_pipeline=465 行; registry 五区段, `registry_content_sha256` 只锚
entries/bank_company_map/excluded/dv2_constants 四区段 (meta 刻意不入);
02: AC 扫描/pair 长表/`build_measure_library`+`compute_weighted_panel` 双 SSOT/
`_compute_weighted_panel_percol` 位级参照臂/`write_outputs` 单点注入/八组 gate;
03: BankCanon/七权 builder/DV2 双向锁+pair 指纹双锁/互验报告;
run_pipeline: 单实例锁 (路径=`logs/_run_pipeline.lock`) 先于日志接管/子进程串跑
fail-loud/跳步自检/锚三方对比。gate 129 项 = 12+58+54+5 (collect 实数复核一致),
五处计数字面量 (01:103/02:140/03:121/run_pipeline:196/README:52-54)。
listed 主面板 = **105,032 行 × 1,914 列 = 20 固定 (含 stock_code) + 1,894 加权**
≈1.6GB dta (盘上实读; v1 曾误记 1,913/19, 已更正)。

**F8 上游测度中立性**: 五上游 parquet (40/51/27/16/21) 全按 `target_bank×year`
组织, **与公司身份无关** — registry 的 entries/excluded 判定逻辑与 CUT 负清单
对税调版可复用 (核验: 01 的 resolve_cols/classify_excluded/parse_cut_list 全程
无公司名/stock_code 依赖); 公司身份只进 ① AC 名单 ② bank_company_map
③ 固定列/标签 ④ 03 的 geo。

## §3 口径判定 (T-D1 … T-D20; 实施前全部定死, 逐条为闸)

**T-D1 名单与主键**: 公司名单 SSOT = `config/company_tax_names.yaml`; 面板行键 =
`company_tax_name × year` 满骨架 (44,771 × 19 = **850,649 行**, 无缺格)。
标识符固定列 = **`usci`** (str18; 合法 Stata 变量名; 850,649×18B≈15MB 可忽略),
沿用 write_outputs **单点注入**范式: 税调 02 本地实现 `usci_map()` + `write_outputs`
(相对 listed 为本地件, 见 T-D10), **税调 03 经
`importlib.import_module("02_build_company_tax_bank_cooc_panel")` 复用税调 02 的
同一 `write_outputs`** — "禁第二份实现"的边界是**管道内** (税调 03 禁重抄税调 02),
跨管道则按 T-D10 分桶。dta 标签 "统一社会信用代码 (18 位)"。
满骨架显式披露: 99%+ 全零行在回归端属"无共现企业-年", 样本裁剪归分析端
(codebook Stata 示例给口径), 面板本体不裁 — 裁行会破坏计数列 fillna(0) 真零语义。

**T-D2 registry 独立而同构**: 新建 `config/company_tax_bank_cooc_registry.yaml`,
schema 与 listed registry 五区段完全同构 (meta/entries/bank_company_map/excluded/
dv2_constants)。entries/excluded 判定逻辑与 CUT 负清单
(`COMPANY_BANK_COOC_PANEL_CUT_LIST_v23.txt`) 复用; **CUT=410 硬闸保留;
KEEP==294 / domain==704 依 listed 明文禁令 (01:12/129) 不设锚** (v1 误标"硬闸",
已更正 — KEEP 段有 lazy 幽灵基名折叠等动态处理, 锚死即脆断言)。
差异仅 ① `meta.company_names_sha256` 锚税调 yaml ② `bank_company_map` 按 T-D3
重建 ③ `dv2_constants` 按 T-D9 裁剪。哈希锚函数 `registry_content_sha256` 经
importlib 复用 (01→02→run_pipeline→gate 四方同一实现)。
**两 registry 并存互不引用**: listed 管线零改动 (T-D18 边界铁律)。

**T-D3 D4 own-bank 剔除 (税调重设计; 采纳计量评审 P0-1/P1-1/P1-2)**:
语义不变 — 银行系企业与"自家银行"的共现不算银企关系。构造五通道:
① `name_flag_set` = 名称含"银行"或"农商"的税调企业 — **token 终集 = {银行, 农商}
   两 token 子串判据, 与 listed 01:547 逐字节同款, 作为税调版 SSOT 常量落 gate 锚**
   (F6 实测=280 家; 五词宽口径本批计数巧合相等的证据落 §9, 未来批次分叉时以
   两 token 为准并重审);
② 机器映射 = variant × 银行 AC 命中 → own-bank 候选集。**这是对 listed 精确相等
   查表 (01:529 起) 的显式口径改变** (分/支行法人名是银行名超集串, 精确相等必然
   零命中, 子串命中是必要的)。**三层口径钉死 (R2 终审 P1-2)**:
   - **扫描域 (haystack) = 该企业 `company_tax_name ∪ variants` 全集**
     (含曾用名 — F6 的 244/34/2 计数与长兴/兴县错例均按此口径实测; 兴县假命中
     恰来自曾用名 variant, 只扫全名会得出不同数字);
   - **施加域 = 仅 ① 的 name_flag_set 280 家** (禁对全部 44,771 家跑子串映射 —
     非银行系企业含 2 字银行短 variant 会批量产出假 own-bank 对);
   - **裁决规则**: `|hits|==1` → 自动接受 (F6: 244 家, 抽查无误);
     `|hits|>=2` → 先施**最长匹配支配规则** — 银行 X 被弃当且仅当 **X 的全部
     命中 variant** 均为某银行 Y 命中 variant 的真子串 (X 若另有非嵌套 variant
     独立命中则不弃 — 杀"长兴农商⊃兴县农商"型假阳性而不误杀真多关联);
     支配后仍多值 → **强制人工裁决** (T-P0-1 实测: 本批支配规则把仅有的 2 个
     多命中全部归一 — 中信国际保留自身剔母行、长兴保留自身剔兴县 — 该分支
     本批为空集; 中信型"母行是否并入"的构念裁量在 ④ 全量过目层复核,
     归一 ≠ 免检);
③ `|hits|==0` (F6: 34 家) → 人工核定后落 `MANUAL_TAX_BANK_COMPANY_MAP`,
   **每条附理由码** (`NOT_IN_CANON` 农发/村镇/港外资 · `VARIANT_GAP` 名单内但
   variant 未覆盖 · `NO_BANK` 真无对应); 无对应者**保留为 bank_company_map 的键、
   值 = `[]` 空列表** (02 scan 的 `bank in own_map.get(comp)` 与 03 `drop_own_bank`
   对空列表天然 no-op; `is_bank_company` 仍=1 语义正确)。v1 的
   `__NO_CANONICAL_BANK__` 字面哨兵与"并入 excluded 区段"两案**废弃**
   (excluded 区段语义=面板列负清单, 塞公司名属 schema 错位);
④ **280 家机器映射结果全量人工过目** (T-P0 探针产物), 核定后冻结为常量;
⑤ 覆盖 gate: **集合相等** `set(mapping) == name_flag_set` (恰 280, 无"+");
   人工键经 variant 解析归一到 `company_tax_name` 全称, 非唯一即 SystemExit;
   gate 加三负例: 长兴/兴县型支配规则夹具 · 空列表值 no-op · "空值键企业名确无
   任何 bank variant 子串命中" (bank_names.json 未来扩充时该断言翻红提示重审)。
listed 的 5 家人工表 (上市银行) **不迁移**。`is_bank_company` 标签
"银行系税调企业 (D4, 280 家)"。

**T-D4 共现口径零改动**: 同篇共现 = 21_full 行 (报道×target_bank) 的三轨文本被
公司 variant AC 命中; D4b 子串作废 (公司 variant 全部为该银行名真子串 → 作废,
牡丹江先例)、D5 重复 variant 多归属、跨年去重键 (company,track,docid) 不含 year、
docid→min(年) 归年、frac=1/k 分摊、n_docs_v/strict/longhit 全套 pair 口径、
两套缺失语义 (计数 fillna(0) 真零 / 加权无共现 NaN) — **构造口径逐条照搬,
零新口径**。绝对年域 2007–2025 与面板年窗同 listed。
D5/D4b 的**事实基础在税调侧须重建** (完备性 P1-6): 跨公司重复 variant 普查
(listed 30 个 → 税调规模未知, T-P0-4) 与 D4b 子串对全量普查 (listed 22 对;
命中主体不限银行系企业, 须对全部 124,366 variants × 1,767 银行 variants 普查,
T-P0-5) — 结果回填本节与 §7。

**T-D5 分支机构两层级权重 (本计划核心新口径)**:
公共部分: 权源同一 dta (F3); 银行名规范化同 `BankCanon` (境外闸/泛称闸/尾段黑名单
判定序零改动); 存续窗口口径零改动 (ApprovalDate≤t 且非 [Status=2 & QuitDate≤t]
且非 [Status=1 & RunawayDate≤t]; 端点解析失败按"未发生"保守处理)。
**端点失败率闸更正** (计量 P2-1): 分母 = Status∈{1,2} 行 (listed 03:609-610,
非 v1 所写"全表行"); 城/县两 builder 读同一 dta → **单点读表+规范化+闸一次**,
两 builder 接同一份 df 分臂 (v1 "各自独立计算"是恒等重复, 废弃)。

- **T-D5a 城市层 `branch_city`**: 复刻 listed `build_weight_branch` 主体:
  网点键 = CityName 剥括注→缺失归空→`市$` 去尾 (对称性已验: CityName 151 个
  非市尾值 [州/盟/地区] 正则 no-op, 税调 city 同为民政全称, 双侧对称);
  公司键 = city, 遇 `city_placeholder` 退 district, 同一去尾; 境外/缺失剔除。
  w = 公司城市内该行当年存续网点数, w>0 才落长表。
- **T-D5b 县域层 `branch_county`** (新 builder): 复合键 **(city_key, county_key)**
  精确匹配 (同名区县跨市实测 310 个 — 复合键消歧, province 不需):
  - 网点侧: county_key = CountyName 剥括注→**字面 `"None"`/空显式清洗** (F3),
    **清洗后空键行剔除** (`b = b[b.county != ""]`, 镜像 listed 03:636 城键先例 —
    封死空键假匹配通道, 计量 P1-4); **不做尾缀剥离** (直匹已 97.53%, 剥尾制造
    通州区↔通州市 歧义; 县改区错位留披露 §7-L4, 不建别名表 §8-N6)。
  - 公司侧: 键 = (city_key, district_norm); **district_norm = 剥括注 + 脏值集
    清洗 (镜像 city 键 03:605-606 两步), 去尾豁免**。**district=`-` 走显式 NaN
    通道, 禁清洗归空** (归空会与网点侧任何脏空键假匹配; 计量 P1-4)。
  - **三条例外 (全部机器规则, 无人工)**:
    (i) city ∈ `city_placeholder` (144 家, F4②): 分支侧把县级市记在 CityName
        (石河子 477 行实证)、CountyName 为镇/街道级 → **该 144 家绕过复合键
        通道, 走城市层同款 city-level 匹配**: 公司键 = district (即城权同款
        退化键), 网点计数对 county 维折叠 (`groupby(city_key, bank)` 求和,
        与 branch_city 同式) — 由构造保证城/县两权对这些企业**逐 (bank,year)
        数值恒等** (行政区划本身无更细层级, 非 bug; gate 用例锚死恒等;
        codebook 点名, 互验剔除见 T-D7); 其 B 锚命中判定 = district ∈ 网点
        CityName 键集 (非复合键);
    (ii) district == `-` (922 家 = 918 直筒子 + 4 零星缺失, F2): 县名不可对齐
        (直筒子分支侧为镇/街道级) → **县权全缺失 (NaN), 不回退城市层** —
        回退会让县权复制城权污染互稳独立性; 企业清单落审计日志;
    (iii) 复合键无匹配残差 (开发区 42 家 + 零星): 县权缺失, 落审计。
  - 长表 schema 同 branch: company/bank/year/w 四列, 无稳健臂
    (`ROBUST_ARM_COLS` 两 scheme 均 `[]`)。
  - **NaN 通道的实现语义 (消歧)**: (ii)/(iii) 企业在县权**长表中无行**即可 —
    引擎对 weights `dropna(w)` (listed 02:672)、`rel_n_banks` 对骨架缺格
    `fillna(0)` (03:815), 故"显式 NaN 行"与"长表无行"两种实现在面板端恰好
    等价, 实现取后者 (简单); "禁归空"约束针对的是**键清洗层** (防空键假匹配),
    非长表行层。
  - **县权面板新增机器可读固定列 `county_key_ok`** (int8; 1 = 有效复合键或
    (i) 退化键, 0 = (ii)/(iii)/境外缺键; R2 终审 P1-4): 县权缺失的 ~964 家
    (本批 = 922+42 精确下界; 境外/空键实测为**空集** — city 324 值全境内、
    四地理字段零缺失, 该条款是防御性空集; 终值随运行时实数回填, 禁写死硬锚)
    在面板端与"城里真无网点"同为 rel_n_banks=0 + cw/ce NaN 签名, 而税调名单
    (含 district) 不可再分发 → 复现包使用者无法自行重构 L3 子集, 必须随面板
    给机器可读标识。仅县权面板 +1 列 (城权面板/主面板不加), dta 标签 +1;
    gate 为**单向断言** `county_key_ok==0 ⇒ 该企业县权全缺失` + key_ok==0
    家数锚 (运行时实数) — **禁双向**: key_ok==1 且县权全缺失是合法真零形态
    (如全部网点 2007 前退出), 恰是该列要与缺键区分的情形, 归互验报告
    "真零企业 N 家"披露行 (补强 T-D7① 判读) 而非断言。
- **T-D5c 网点侧 CityName 占位回退 (对 listed 的净新增, 计量 P1-3)**: 网点侧
  CityName ∈ 占位值集 (T-P0-2 实测全集 = {海南省直辖 128, 海南省直辖县级行政区
  93, 省直辖县级行政区划 3, 省直辖县级行政区 1} 恰 225 行, 落 DV2 新键
  `city_placeholder_branch_side`) → **网点侧回退 CityName:=CountyName** (镜像
  公司侧 placeholder 逻辑的对偶), 否则琼中/屯昌/定安等县的 225 行网点权重死键
  漏计。同时验证 `PAREN_RE` 覆盖全角 `（…）` 批注串 (47 行伊犁/喀什批注值剥净
  后才可对齐, F3)。**施加位置 = 单点读表后的公共规范化段 (分臂之前), 城/县两
  builder 同受益** (R3 走查 P1-2: 预清洗从 listed builder 内嵌位置上提为共享
  prep 函数, 防只装进城权侧漏掉县权 (i) 退化键通道)。**覆盖锚要素改显式返回值**
  (tuple/dataclass, 县侧带 (ii)/(iii) 分类计数供 county_key_ok 与审计; 不沿用
  listed 的 `out.attrs` — 经 copy/merge 易丢, R3 走查 P2-4)。
  此条为**显式偏离 listed** 的两处之一 (另一处 = T-D3② 子串映射), 均落 §9 留痕。
- `SCHEMES = ("branch_city", "branch_county")`; `DTA_USECOLS` = listed branch
  六列 **+ CountyName** (ProvinceName 不读 — 复合键已消歧)。

**T-D6 覆盖锚 (fail-loud 阈值, 城县分设; 分母显式定义 — 计量 P1-5)**:
- **锚分母 (keyed 集; A/B 两锚共用同一分母, 镜像 listed 03:1130-1144)** =
  有有效键企业: 城市层剔境外/空键 (listed 同型); 县域层**剔 (ii)** (`-` 通道,
  无有效县键)、**(iii) 不剔** (开发区 42 家有键、只是匹不上 → 留在分母, 诚实
  计入 A/B 锚缺口), 即县域 keyed 集 = 44,771 − 922(ii) − 境外/空键;
  (i) placeholder 144 家有退化键, 进分母 (B 判定按 T-D5b(i) 的 city 层口径)。
- branch_city: A=非零权企业占比 ≥90% ∧ B=城市键命中率 **≥99.5%** (T-P0-2 实测
  B_city=100.0000%, 初值 95% 按探针铁律上修)。
- branch_county: A ≥85% ∧ B=(city,county) 复合键命中率 **≥99.5%** (T-P0-2 实测
  B_county=99.9042%, 初值 90% 上修; 缺口恰 42 家开发区 (iii) 通道)。
- 锚公式+分母家数+终值全部落 §9 与 gate; **铁律: 只许探针实证后上修,
  不许为过闸静默下修** (下修须回本计划记录理由)。

**T-D7 三权互验设计 (DV5 全五件继承 + 三权重构; 采纳完备性 P1-1)**:
主锚 = pair 长表 full 轨 canonical **n_docs (刻意不用 _v**, 与 listed 03:1229
一致 — verified 门控属测度层, 互验锚取存档全量口径)。
- **① 覆盖概览** (v1 漏, 补): 公司/银行/(c,b) 对数逐权 + **逐年关系对数表**
  (让 rel_n_banks=0 可判"真无关系 vs 权源覆盖假零")。
- **② 支撑重合段**: 两替代权皆稠密 → 整段替换为 city×county 支撑对比
  (Jaccard + 覆盖企业数), 标注稠密语义。
- **③ 份额 Spearman** (共同支撑, 禁 union 补零, ρ 未定义归 n/a): 三行 —
  media×city / media×county / **city×county** (跨粒度收敛效度; **(i) 类 144 家
  按企业整体剔除** — 其两权向量逐格恒等, 按对剔无意义; 剔除数点名披露)。
  **份额 = 先窗口求和再算份额, 禁逐年份额取均值** (v33 公式铁律落字)。
- **④ 富集度双基准** media→{city,county}: 均匀基准 gate ≥1.5× (未达 loud
  WARNING 不判失败); **B_m = pair 当窗 distinct bank 全集 (不限共同公司集,
  listed P0-1 修正后口径, 03:836)**; **边际保持基准用解析式
  Σ_b m_b·a_b/(|C|·|pairs_m|), 禁随机置换** (公式落字防裁剪重抄走样)。
- ④b 篇数均值差、⑤ Top-1 同银行率/包含率: media×{city,county} 各一组。
- 反向证据披露三件套 (spearman_neg/marg_below/meandiff_below) 逐权保留;
  未映射银行 top-50 附录保留。
- **⑥ 顶刊披露包 (a)–(e) 继承** (v1 漏, 补): (a) 富集度措辞钉死 — 禁写
  "validated against credit relationships"、必并报 {均匀值, 边际保持值,
  precision 绝对水平} 三件、叙事以边际保持为准; (b) 推断地位钉死 — 三权
  spec-curve 属描述性, 假设检验以预声明 primary 单臂为准, 禁挑臂单报,
  三权免 FWER 的归类依据 (规格稳健性并排, 非同构念替代 headline) 落字;
  (c)❶ 媒体权共源反射通道 (cw 权重与被加权测度同源语料机械相关) 处方 =
  重叠占比分位披露 + leave-company-out 臂提示; (c)❷ 分支稠密权 + 公司 FE 后
  识别变异=网点进退披露; (d) 存量/流量构念差异; (e) 第三方获取路径 (§6 谱系)。
- **铁律**: 三权各自 just-identified 并排、互为稳健性不分主次, **禁混同一
  over-identified Hansen J**; 城/县两权是同一权源的粒度梯子, 论文端预声明
  primary 层级。

**T-D8 双锁 + 指纹 + 工程闸 checklist (fail-closed 逐条照搬)**:
03 启动 ① DV2 常量双向锁 (registry.dv2_constants 缺/空/不等 → SystemExit)
② pair 指纹锁 (缺文件/缺指纹/stale → SystemExit); 02 启动哈希锚复算 (importlib
复用 01) + n_entries≥600 闸 + 40 面板列漂移闸; run_pipeline 单实例锁 (锁先于
日志接管) + 跳步自检 + 锚三方对比。
**checklist (工程评审 P2-11, 逐项显式)**: `-O/PYTHONOPTIMIZE` 闸 ×3 脚本 /
`PYTEST_CURRENT_TEST` 守卫 + **`propagate=True` 恢复** ×4 脚本 (漏恢复 →
负例测试 caplog 静默失捕) / console 兜底 handler / 锁先于日志接管注释块 /
psutil 声明依赖。
**run_pipeline 四字面量联动** (工程 P1-3 + R2 终审 P1-3): ① `_expected_registry_anchor`
的正则常量名 → `EXPECTED_TAX_REGISTRY_SHA256`; ② 测试文件路径 →
`tests/test_company_tax_bank_cooc_registry.py`; ③ 锁路径 →
`company_tax_bank/logs/_run_pipeline.lock` (镜像 listed logs/ 下, 免 gitignore
覆盖外残留 — v1 目录根方案废弃); ④ **`_registry_sha()` 内硬编码的 registry
yaml 路径** (listed run_pipeline.py:359 → 改 `company_tax_bank_cooc_registry.yaml`;
漏改则锚三方对比静默读 listed registry, 恒告警且 bump 提示指错文件)。另
`_iter_artifacts`/`_log_step_context` 内的 registry/pair/面板路径字面量随
WP-orch 改。lock gate **+1 正例**: `_expected_registry_anchor() is not None`
(防锚对比静默降级为"不可读")。
**字面量清零总则 (兜住枚举漏项; R3 终验 P1-2 修订口径)**: 税调三脚本 +
run_pipeline + 四 gate 内, **case-sensitive 三小写 token**
`company_bank` / `company_listed_name` / `stock_code` 全域 grep 清零;
**白名单三条**: ① T-D10 的跨管道 importlib 目标串与 logger 名
(`02_build_company_bank_cooc_panel`); ② 紧邻 index 重命名位点、以 listed 引擎
输出名为断言/注释对象的至多 2 处 `company_listed_name` (02 run_gates / 03
fixed_cols_for 各一; index 重命名一律**位置式赋值**
`index.names = ["company_tax_name", "year"]`, 禁旧名字面量参与逻辑);
③ 大写文件名/母本计划名 (`COMPANY_BANK_COOC_PANEL_CUT_LIST_v23.txt` 等)
天然不在小写命中面 — 口径设计豁免, 非漏检。该 grep 作为 WP-gate 收口断言落
gate 测试。

**T-D9 DV2_CONSTANTS 裁剪**: 删除仅服务已裁权源的键 — `custodian_*` 与
`sanchan_words` 的消费点在 **shareholder builder** (03:729-739; v1 误写"贷款侧",
已更正), 税调裁掉 loan+shareholder+董监高后可删; 保留 unnameable/overseas_words/
foreign_suffixes/generic_heads/affiliate_tail/head_exempt_note (BankCanon 消费,
含 03:292 最小集断言勿裁) + city_placeholder/city_overseas (分支权消费)
**+ 新增 `city_placeholder_branch_side`** (T-D5c 网点侧占位值集, T-P0-2 终集)。
T-P0-3 以实读消费点为准定终集。裁剪使税调 registry 哈希与 listed 永不混淆。
**dv2 自举顺序 (R3 走查 P1-1, 关键)**: listed 01 对 03 importlib 失败落空占位,
但 03 双向锁对空区段同样 SystemExit → 若按"01→02→写 03→重跑 01"级联, sha 换代
要二次回填、02 整轮重跑。**税调解法 = WP5-stub 前置**: T-P0-3 定出裁剪终集后、
WP0 之前, 先落税调 03 文件骨架 (模块级 `DV2_CONSTANTS` 终值常量 + 无副作用
import; pyreadstat 等重依赖全在 main 内), 01 首跑即得终值区段、**sha 一次定终**;
`EXPECTED_TAX_REGISTRY_SHA256` 在 WP-gate 期 (gate 文件成形时) 单次写入。
01 的 importlib except 分支 WARNING 文案照 listed 原文 ("此属异常, 须排查 03
import 期错误而非重跑 WP0") — stub 前置后该文案语义恰当。
**40 面板残差闸处置协议 (R3 走查 P2-2)**: 税调 01 首跑若残差翻红 (共享树 40
面板在 listed registry 定稿后新增列) → 先跑 listed 01 对照确认漂移同源, 处置
回评审; **禁就地加 EXCLUDE 正则**。

**T-D10 跨管道引擎复用 (禁第二份实现的边界; 经工程评审逐函数核验可行)**:
税调 02/03 通过 `importlib` + `sys.path` 注入 `company_listed_bank/`, **复用**
listed 02 的公司无关件 (核验: 纯函数, 无名单/registry 模块态, import 无日志
副作用, HERE/REPO 路径推导从 listed `__file__` 出发仍指 repo 正确):
`build_measure_library` / `compute_weighted_panel` (+`_align_weight_frame`/
`_take_measure_col`/`_budget_cells`) / `_compute_weighted_panel_percol` (位级
参照臂, gate 继续消费) / `default_paths` / **`load_input21` / `compute_wt_base` /
`_sparse_equivalence_check`** (v1 漏分桶, 补 — listed 03:1149 本就复用
load_input21)。
**税调本地实现** (公司相关): `load_name_assets` (读税调 yaml) / `usci_map` /
`scan_hits`·`build_pair_table`·`build_counts`·`add_hhi` / `write_outputs`+
`FIXED_LABELS` (usci 注入+税调文案) / `run_gates` (行数锚 850,649)。
**index 名硬编码位点清单** (工程 P2-5, 防漏改): listed 02:761/839 引擎输出
index 名 `company_listed_name` (merge 按位置对齐不受影响, 但税调本地
`run_gates` [listed 02:1139] 与 03 `fixed_cols_for` [03:813] 的 index.names
须同步改 `company_tax_name`)。
**引擎日志接管** (工程 P1-2): 税调 02/03 import 引擎后须
`logging.getLogger("02_build_company_bank_cooc_panel")` attach 本阶段文件
handler (镜像主仓 redirect_module_logger 先例) — 否则 budget 生效值与 chunk
收缩 WARNING 只上 console, 生产日志失载。
耦合披露: listed 02 引擎演进 → 税调 gate (手算锚+bitwise) 翻红 = 故意的漂移
探测器。03 的 BankCanon/互验统计在税调 03 本地持有裁剪版 (§8-N5);
**税调本地 `drop_own_bank` 矢量化** (own_map 仅 280 家 → 先 isin 预过滤/
(company,bank) 对集合 isin, 免 25M 行逐行 apply ~4min/scheme; 属 N5 授权的
本地裁剪范围, listed 版冻结不动)。**`load_name_assets` 的 D4b 子串索引构建
允许长度分桶/AC 索引化** (语义等价加速; 外层实为银行 variant 总数×公司 variant
总数, 纯 Python 双循环 124,366×数千可到十分钟级; 以 T-P0-5 普查清单 [92 对]
作参照臂断言等价; R3 走查 P2-3)。

**T-D11 固定列 (20 列, 与 listed 逐位对齐仅换标识符)**:
`company_tax_name, usci, year, is_bank_company, n_cooc_{full,ctx,ss},
n_cooc_{full,ctx,ss}_v, n_cooc_ss_strict, n_banks_{full,ctx,ss},
cooc_hhi_{full,ctx,ss}, cooc_wt_base_{full,ctx,ss}`; 加权测度列
`cw_{short}_{track}` / `ce_{short}_{track}` 列序=registry 条目序, 与 listed
同列集 (~1,894 列)。dta 变量名 ≤32 字节 + 标签 ≤80 字符双闸照搬。
双权面板固定列: `rel_n_banks / rel_hhi / rel_wt_base` + is_bank_company 照搬;
县权面板另 +`county_key_ok` (T-D5b, 仅该面板)。

**T-D12 目录与命名**:
```
news_process/company_tax_bank/
├── 01_build_company_tax_bank_cooc_registry.py
├── 02_build_company_tax_bank_cooc_panel.py
├── 03_build_company_tax_bank_weight_validation.py
├── run_pipeline.py        # 锁 = company_tax_bank/logs/_run_pipeline.lock
├── README.md
├── data/   (gitignore)
└── logs/   (gitignore)
```
gate 四件: `tests/test_company_tax_bank_{cooc_registry,cooc_panel,
weight_validation,run_pipeline_lock}.py`。父仓 `.gitignore` 增两条:
`news_process/company_tax_bank/logs/` + `news_process/company_tax_bank/data/`。
模块名与 listed 含 `_tax_` 区分, sys.path 双目录无遮蔽 (工程评审核验)。

**T-D13 规模与预算 (128GB/64core; 采纳工程 P1-1/P2-7 修正)**: 主面板 850,649 行
× 1,914 列 ≈ 1.63e9 cell ≈ 13GB float64 单帧; **峰值 ≈ 3–4× 单帧 (~40–55GB:
concat/merge/列序重排/rename/arrow 转换各持一份拷贝)**, 128GB 边际 ~2.5× 成立
但不裕 — 实现须在 merge/写盘间显式 `del` 释放, 03 双面板**串行**处理禁同持两面板。
三面板 dta+parquet 落盘 **~80GB 磁盘**, T-P0-6 探针核余量 ≥120GB (先决闸)。
**引擎 chunk 预算**: 02 媒体权稀疏长表 → 默认 60M cell 够用; **03 branch 长表
~25–34M 行 → chunk_eff=2 触发内存吃紧 WARNING、~945 轮 groupby** — 跑前设
`NEWS_PROCESS_COOC_BUDGET_CELLS≈500M` (25M 行×20 列×8B=4GB/帧, chunk_eff→20,
轮次降 10×), 该设定写进 run_pipeline 03 步骤与 README。
耗时预估修正: 02 全链 ~30–60 min; **03 双权 ~60–90 min** (引擎 8× + 2×13GB dta
写盘 15–25 min; v1 "20–40 min"偏乐观 2×, 已更正); D4b 全量子串普查 ~2.2e8 次
`in` 分钟级。**dev T=2 语料下测度列大面积 NaN、2019+ 年计数 0 属预期退化,
生产 T=18 才有全谱; dev 产物不可用于任何回归** (镜像母本 §6 禁令, 显式落字)。

**T-D14 gate 测试设计 (四文件, 计数以 `--collect-only -q` 实数为准)**:
- registry 件: 哈希锚 (**常量名 `EXPECTED_TAX_REGISTRY_SHA256` 禁与 listed 同名**
  — run_pipeline 锚正则以行首+全名匹配为前提) / 名单哈希锚 / CUT 对账 410
  (KEEP 不锚) / 40 面板穷尽划分 /
  短名 32 字节唯一 / **D4 集合相等 (恰 280) + 空列表值容忍 + 支配规则夹具 +
  空值键无子串命中断言** / schema 字段 / `registry_content_sha256` 函数级复算。
- panel 件: 镜像 listed 58 项全谱, 行数锚/固定列改税调; 新增: **usci 三联断言
  (str.len()==18 + 全唯一 + 非空) + dta 读回 dtype 仍字符串**。
- weight 件: 裁掉贷款/银团/董监高/股东族; 保留 canon 全族 + 分支存活边界/失控/
  端点失败/城名预清洗/placeholder; **新增 county 族**: 复合键消歧 (同名区县
  跨市不串) / 直筒子 NaN 不回退 / **空键互不匹配负例** / placeholder 键退化恒等 /
  字面 "None" 清洗 / **网点侧占位回退 (T-D5c)** / 城县双锚独立 SystemExit /
  city×county ρ 剔恒等企业 / **county_key_ok 单向断言 (==0 ⇒ 县权全缺失) +
  key_ok==0 家数锚** (禁双向, T-D5b) / **(i) 类两权长表逐 (bank,year) 恒等** /
  **branch dta 行锚 integration 测试** (603,907 行 / Status {0:550,359,
  2:51,185, 1:2,363} / CountyName 字面 "None" 3,168 — 税调唯一权源不可零锚,
  翻红即数据商改版信号; R3 走查 P2-6) / **城县两权手算身份锚各一** (从 dta
  手算已知 (company,bank,year) 格值, 镜像 listed test:527);
  富集度手算/Spearman 禁补零/codebook 幂等/双锁+指纹 SystemExit 族照搬。
  **D4b/D5 夹具为注入式合成夹具** (listed test:135-148 牡丹江用例不依赖盘上
  名单), 原样迁移改税调风味即可, 勿找真实例 (R3 走查 P2-5)。
- lock 件: 5 项镜像 **+1 锚可读正例** (T-D8) = 6 项。
- **测试→产物依赖序声明** (工程 P2-9): panel 件全 mock 无盘上依赖 (01/02 未跑
  也绿); registry 件 fixture 直读 registry yaml (**01 首跑前必红, 属预期**) 且
  穷尽划分测试读盘上 40 面板 (clean clone 红, 与 listed 同型既有口径); weight
  件读 config 权源 dta (在盘即绿), 读 03 长表的用例带 pytest.skip 守卫。
  **哈希锚回填时点 (R3 走查 P1-1 修订)** = WP5-stub 前置使 WP0 首跑 sha 即终值;
  `EXPECTED_TAX_REGISTRY_SHA256` 在 **WP-gate 期** (gate 文件成形时) 从 registry
  meta.registry_sha256 单次写入 (run_pipeline 锚告警兜底提醒)。
- 五处计数字面量 (README + run_pipeline banner + 三脚本 banner) 在测试收敛后
  以 collect 实数一次性回填。

**T-D15 日志与可观测性**: 复用 `core/logging.py::setup_logging`
(PYTEST_CURRENT_TEST 守卫 + propagate 恢复); 阶段头/参考文献/漏斗日志/规模锚
(850,649 行 = 44,771×19)/富集度双基准判读逐段移植改写; 全量数字 `%.4g`;
引文只取 audit_dois 白名单池零自造 (县域银行分支暴露构念的可用 DOI 由 T-P0-7
盘点, 池内无则该段引文从简, **不为凑引文自造**); **跨管道引擎 logger 文件
handler attach** (T-D10); GBK 控制台兜底已由 listed 验证 (文件 handler utf-8,
console 罕见字由 logging.handleError 吞, 可接受)。

**T-D16 确定性**: 全链 $0 纯离线 (无 LLM/嵌入调用); **确定性验收域**: parquet +
互验报告 md + codebook md **字节级 sha256 恒等** (同输入两跑; 报告/codebook
禁写生成时间戳 — v31 R3 P2/v33 J2 条款继承); **dta 改「列内容哈希恒等」而非字节
sha256** (R2 修正: pyreadstat.write_dta 在 dta 头强制嵌入分钟级墙钟时间戳 [17 字节
`<timestamp>…</timestamp>` 字段, 无参数可关], 跨分钟两跑字节必变但数据列完全确定 —
故 dta 验收 = pyreadstat 读回后逐列内容哈希恒等, 与 02:161-162 已用的「列内容哈希
一致」措辞对齐)。不涉 golden/BLAS — 主管道 OUTPUT_REGISTRY/STAGES_MAIN/schemas.py 零接触。

**T-D17 提交协议**: by-name add (三脚本 + run_pipeline + README + 四 gate +
registry yaml + 父仓 .gitignore + 本计划), 排除 `*constants.json`/eval_reports/
并发会话产物; data//logs/ 永不入库; 绝不 amend / 绝不 --no-verify;
**不改 CLAUDE.md** (listed 先例即未加段)。

**T-D18 与 listed 管线的边界铁律**: `company_listed_bank/` 目录、listed
registry、其 gate、其产物 — **零字节改动** (实施/验证 agent prompt 硬禁触碰
listed 目录与他人在制文件, 07-07 实弹教训)。唯一交集 = 税调 02/03 只读 import
listed 02 引擎 (T-D10)。

**T-D19 codebook 内容规格 (采纳完备性 P0-1; 与 dta 同级交付物)**:
镜像母本 §3b 全骨架, 税调化改写:
① 文件功能 + **数据谱系散文段** (链条: 原始新闻语料 → stage 00–21 → 21_full →
   AC 共现扫描 [税调名单 v1.0.0] → pair 长表 → 加权引擎 [registry SSOT] →
   面板; 权源侧: 银行业金融机构基本信息表 → BankCanon → 双层级网点权);
② 逐变量说明 (A) 固定 20 列 (含 usci/is_bank_company 税调语义) + (B) 覆盖率与
   加权测度列族 + pair 10 列字典;
③ **使用要点段全量继承**: exposure-robust SE (AKM 2019/BHJ 2022, shift-share 型
   暴露)、⚠ 企业级回归 cluster(bank) 无定义警示、ln(1+x)/PPML 建议、三轨无单调
   关系断言禁令、cooc_wt_base 上界语义、权重内生性提示 — cw_ 列族对税调面板
   逐字节同构, 逐条成立;
④ **D17 三义务段**: allv 单载体声明 / neu=1−pos−neg 恒等注记 / 被删臂地位声明
   + D12 重构公式可复制代码段 (CUT 负清单同一份, 义务原封适用);
⑤ **D9 逐年语料覆盖表** (2025 假零可查表化);
⑥ 排除列审计表附录 + 短名对照 + Stata 示例 (usci×year merge + 满骨架截断示例,
   L2 口径) + 精度分层抽样 + 已知局限 (§7 全量);
⑦ 03 侧 **「双权面板章」 section-upsert**: 成对标记字面量见 §1 命名规则
   (BEGIN/END 两条都要), 02 写 codebook 时预留区块、03 幂等 replace
   (镜像 listed 七替代权面板章机制 02:1096/03:900-916)。

**T-D20 数据谱系与许可披露 (采纳完备性 P1-5; data editor 一票否决项)**:
① `银行业金融机构基本信息表.dta` (603,907 行商业数据): 谱系七字段 (数据商·
   数据库名/表编号·版本·获取日期·提取过滤条件·许可条款·第三方获取路径) 落
   codebook/互验报告, 缺项按 DEFERRED 标注 (§6);
② **税调名单是政府调查数据, 保密性/再分发地位比商业名单更尖锐**: 已入库事实
   (F1) 与"派生聚合面板可分发、名单/行级长表按需申请"的降级路径写入 codebook
   披露段; 复现包附 pair 长表+双权长表 (外部不可得的税调名单与权源 dta 使
   完整重生不可复现, 须显式声明);
③ registry `meta.company_names_sha256` 锚死 F1 所记盘上态。

## §4 实现步骤 (T-P0 → **WP5-stub** → WP0 → WP1 → WP3 → WP5 → WP-orch → WP-gate → WP4, 严格顺序)

**WP5-stub (新增, R3 走查 P1-1)**: 先落税调 03 文件骨架 — 模块级
`DV2_CONSTANTS` (T-P0-3 裁剪终集 + `city_placeholder_branch_side`) + 顶层仅轻
import — 使 WP0 首跑 registry 即含终值 dv2 区段、sha 一次定终; 03 其余函数体
在 WP5 期补齐 (**补齐不得改动 DV2_CONSTANTS 字面量**, 否则 sha 换代须整链重跑,
gate 哈希锚兜底)。

**T-P0 侦察探针 (先于一切代码; 编号统一 T-P0-1…T-P0-7; 产物落 scratchpad,
精华回填本计划 §9)**
1. **T-P0-1 own-bank 裁决**: 280 家机器映射 (含最长匹配支配规则) 全量清单 →
   人工过目核定 → `MANUAL_TAX_BANK_COMPANY_MAP` (含理由码) 终稿。
2. **T-P0-2 地理键普查与命中率复测**: 网点侧 CityName 占位/批注值**全集**
   (T-D5c 回退集终值) + PAREN_RE 全角覆盖验证 + 预清洗后城/县两层命中率
   (placeholder/直筒子/开发区逐类计数) → 回填 T-D6 锚终值与分母家数。
3. **T-P0-3 DV2 消费点核对**: 实读 listed 03 各键消费点 → T-D9 裁剪终集。
4. **T-P0-4 D5 重复 variant 普查**: 44,771 家/124,366 变体的跨公司重复 variant
   规模与清单 (listed 30 个基线) → 多归属计数膨胀评估落 §7。
5. **T-P0-5 D4b 子串对全量普查**: 124,366 公司 variants × 1,767 银行 variants
   子串关系 (listed 22 对基线; 命中主体不限银行系企业)。
6. **T-P0-6 资源核查**: 磁盘余量 ≥120GB + BUDGET_CELLS=500M 试算 +
   **dev 21_full AC 干跑计数预检** (三轨 Σn_cooc 与 Σn_cooc_v 各报一行 —
   预判 gate④ 严格分化在 dev 的可满足性, Σ==0 给独立诊断文案)。
7. **T-P0-7 短 variant 精度抽样 + DOI 盘点**: 2 字 32 条全量人工过目 + 3–4 字
   分层抽样 (R3-2 范式) → §7-L1 实数; audit_dois 池内县域分支暴露构念可用锚点
   盘点 → T-D15。

**WP0 (01 脚本)**: 复刻 listed 01, 改动面 = 名单路径/字段名、
`build_bank_company_map` 重写 (T-D3 五通道)、importlib 目标改税调 03、
meta.company_names_sha256 锚税调 yaml。产出 registry → 人工抽查 5 条 entries
与 listed registry 逐字段一致 (F8 中立性验证) → 哈希锚回填 gate (T-D14 时点)。

**WP1 (02 脚本)**: 复刻 listed 02, 改动面 = T-D10 本地件 + T-D11 固定列/标签 +
行数锚 + 引擎 logger attach。跑 dev 全链 → 八组 gate 全绿 → 落盘三件
(面板 dta/parquet + codebook [T-D19 ①–⑥] + pair 长表含指纹)。

**WP3 (人工抽核 + Stata 冒烟; 采纳完备性 P1-2, v1 漏)**: ≥10 命中人工核
(docid→原文确有该 variant) + ≥3 own-bank 排除案例 + ≥3 同 docid 多银行案例 +
≥3 加权测度手算复现; **Stata `/b` 冒烟** (use/describe/xtset, `.do` 末尾
`exit, clear`) 确认 13GB dta、usci str18、44,771 家中文企业名与 labels 在
Stata 侧可读; 性能实测记录回填 §9。

**WP5 (03 脚本)**: 复刻 listed 03 裁至两 scheme, 新写
`build_weight_branch_county` (T-D5b) + 网点侧占位回退 (T-D5c) + 单点读表分臂
(T-D5), 城县双锚 (T-D6), 互验报告 DV5 ①–⑥ (T-D7), codebook 双权章 upsert
(T-D19⑦)。跑 dev → 双权长表 + 双权面板 + 互验报告落盘。

**WP-orch (run_pipeline + README)**: 镜像移植; 锁路径/banner/产物 glob
(`_company_tax_bank_altweights_*` / `company_tax_bank_*w_panel.*`)/锚四字面量
(T-D8) 改税调; 03 步骤注入 BUDGET_CELLS 设定; 收口跑 T-D8 字面量清零 grep。

**WP-gate**: 四 gate 文件成形 → `pytest tests/test_company_tax_bank_*.py` 全绿
→ 全量 `pytest -m fast` A/B 差分 (baseline-stash, churn 隔离) 证 **0 新增失败**
→ 五处计数字面量回填。

**WP4 (记账收口; 采纳完备性 P2-4)**: ruff 过 → §9 实施记录回填 (锚终值/
探针实数/性能实测/偏离清单) → T-D17 by-name 提交 → memory 落卡。

## §5 验收 gate 汇总

1. 四 gate 文件全绿 + `pytest -m fast` A/B 差分 0 新增失败 (flaky 跑两次仲裁)。
2. 02 八组面板 gate + usci 三联闸全过。
3. 03 双权覆盖锚 (T-D6 定义与终值) 全过; 富集度均匀基准 ≥1.5× (未达 loud
   WARNING 不判失败); 反向证据三件套零漏报。
4. **确定性: 同输入两跑, parquet/互验报告/codebook 字节 sha256 恒等 + dta 列内容
   哈希恒等** (T-D16: dta 头含 pyreadstat 墙钟时间戳不入字节验收, 数据列确定; 禁时间戳
   条款对报告/codebook 生效)。
5. registry 哈希锚三方一致 (gate 锚 ⇔ yaml meta ⇔ pair 指纹)。
6. WP3 人工抽核 + Stata 冒烟全过。
7. listed 管线零改动 (git status 对 listed 目录/registry/tests 零 diff) +
   主管道全量 fast 0 新增失败。

## §6 生产机 DEFERRED (镜像母本 §9.4)

dev T=2 只证管线正确性; 生产 T=18 全量 21_full 重跑得真面板 (2025 无语料整年 0
属预期)。DEFERRED: 富集度双基准生产值 / 城县覆盖锚生产复测 / precision 生产
第二轮 / 未映射银行 top-N 生产版 / **权源 dta 谱系七字段与许可条款核定 (T-D20①)**
/ 复现包 (附 pair 长表+双权长表, 声明税调名单与权源不可再分发的降级路径) /
提交哈希回填。

## §7 已知局限 (逐条进 codebook/互验报告披露)

**税调特有**:
- **L1 短简称假阳性**: variants 124,366 条中 ≤4 字 1,353 条 (listed precision
  ≤2 字 0.71/3 字 0.76/≥4 字 0.92); 44,771 家名录密度下命中密度上升; T-P0-7
  实数回填。不裁剪, 只披露。
- **L2 税调名单时点性**: 批次快照无逐年存续 → 满骨架铺 0 (与 listed "上市前
  年份"同型); codebook Stata 示例给按需截断口径, 提示以 usci 关联外部工商注册年。
- **L3 县权结构性缺失** (~2.2%): (ii) 922 家 [918 直筒子+4 零星] + (iii) 42 家
  开发区 — 县权回归样本 = "有真县级区划企业"子集; (i) 144 家城县恒等点名。
- **L4 县改区/区划变更错位**: 权源快照 vs 税调批次两时点间的更名造成少量错配,
  计入 B 锚缺口披露, 不建别名表。
- **L5 分支权构念**: 网点数≈本地银行供给暴露 (shift-share 型), 构念差异非质量
  差异; rel_hhi 城市层≈0.05–0.10 稠密披露照搬, 县域层预期更集中, 生产值回填。
- **L6 280 家银行系企业**: own-bank 剔除后面板行保留 (is_bank_company=1),
  剔样本归分析端。
- **L7 own-bank 子串映射残余风险**: T-D3② 支配规则+人工过目后仍属批次快照,
  bank_names.json 扩充须重审 (gate 翻红机制兜底)。

**继承母本 §7 的通用局限 (对税调面板同构成立, 显式声明继承而非默认)**:
公司侧名录/通稿灌水 · **variant 子串重叠双计 (T-P0-4/5 普查实数回填)** ·
拉丁大小写敏感 · full 轨联播稿权重放大 + D8b 联播稿 HHI=1/k 假分散 ·
D4b 残余第三方假阳性 · 企业侧覆盖自选择 (Heckman/扩展边际提示) · variant
快照无逐年生效 · 21_full 行宇宙 = stage13 共现硬过滤后口径声明 · 加权测度
银行覆盖缺口 (共现银行全集 vs 40 面板 110 家) · dev 缺源列基名 · 分类份额
小分母噪声 · 多重检验负担 ~1,900 列 · 共现关系类型异质 (Hilt & Schwenkler) ·
LLM lookahead bias。(母本 NW/BLAS 豁免条不适用 — 本管线无网络列。)

## §8 明确不做

- N1 不注册主管道 DAG / OUTPUT_REGISTRY / shim。
- N2 不做贷款/董监高/股东/银团权源 (税调无对应数据)。
- N3 不做分支权稳健臂 (listed branch ROBUST_ARM_COLS 本就 [])。
- N4 不做省级第三层级权重 (用户口径=城市+县域; 省级构念退化)。
- N5 不抽跨管道共享模块 (改 listed 冻结脚本风险 > 复制收益; 税调 03 本地持有
  裁剪版, 漂移由各自 gate 兜底; 本地版允许 T-D10 声明的矢量化改良)。
- N6 不建县名历史别名表 (工程量/出错面 > ~2% 覆盖收益, L4 披露代替)。
- N7 不做写盘重叠/并行优化 (listed WP-S6 同款 DEFERRED)。
- N8 不动税调 yaml 生成器与源 xlsx; 不造 usci 之外衍生标识符。
- N9 不做地址级 geocode 匹配 (行政区划三级键已足)。
- N10 不改 CLAUDE.md / 不动主管道 golden。

## §9 评审与实施记录

- **v1 (2026-07-08)**: 初稿, 基于四路结构探查 + 六组本机实测事实。
- **v2 (2026-07-08)**: 四路对抗评审 (事实核查 31 项核验 / 口径计量 / 工程耦合 /
  完备性) 裁决修订:
  - **P0×2 均修**: ① own-bank AC 子串多命中误并他行 (实测错例: 浙江长兴农商
    误并山西兴县农商; bank_names.json 内 71 组跨行子串对) → T-D3② 支配规则+
    强制人工+全量过目+gate 负例; ② codebook 内容规格空洞 → 新增 T-D19 全骨架。
  - **P1×12 均修**: 哨兵落位改空列表值 (T-D3③) / name_flag token 集 SSOT 化
    (T-D3①) / 网点侧 225 行占位城名回退 T-D5c (净新增, 显式偏离留痕) / 空键
    碰撞三条封死 (T-D5b) / 县锚分母定义 (T-D6) / KEEP=294 禁锚更正 (T-D2) /
    listed 面板 1,914 列=20 固定更正 (F7) / DV5 ①+⑥ 继承 (T-D7) / WP3 人工
    抽核+Stata 冒烟补步 / 确定性域扩报告+codebook+禁时间戳 (T-D16) / §7 通用
    局限继承声明 + T-P0-4/5 普查 / 谱系许可披露 T-D20 / BUDGET_CELLS=500M +
    03 耗时 60–90min 修正 (T-D13) / 引擎 logger attach (T-D10) / run_pipeline
    锚三字面量联动+lock gate +1 (T-D8)。
  - **P2 采纳**: 命名推导规则钉死 (§1) / write_outputs import 链消歧 (T-D1) /
    load_input21 等分桶+index 名位点 (T-D10) / drop_own_bank 矢量化 / 峰值内存
    系数与释放点 (T-D13) / 锁回 logs/ / 测试依赖序+锚回填时点 (T-D14) /
    sanchan/custodian 消费点更正 (T-D9) / 工程闸 checklist (T-D8) / 探针编号
    统一 / WP4 记账步 / dev 禁回归声明 / usci×year merge 句 (§1) / B_m+边际
    解析式+份额窗口公式落字 (T-D7) / gate④ Σ==0 诊断+干跑预检 (T-P0-6) /
    usci 三联断言 (T-D14) / "280+"→恰 280 / 端点闸分母更正+单点读表 (T-D5) /
    922=918+4 定性 (F2) / 144/143/42 数字更正 (F4) / "None" 字面串形态 (F3) /
    行数 off-by-one 更正 (F7)。
  - **对 listed 的显式偏离清单 (仅两处, 均有实测依据)**: ① T-D3② own-bank
    机器映射精确相等→子串+支配规则 (分/支行法人名结构使然); ② T-D5c 网点侧
    CityName 占位回退 (listed 只做公司侧; 225 行实测漏计证据)。
- **v3 (2026-07-08)**: 第二轮双向评审收口。收敛核验员对 v2 逐条核验 (P0×2 +
  P1×12 + P2 全清单) 判 **converged** (所有修订真实落正文且与仓库实测一致,
  71 组子串对/225 占位行/280 家/105,032×1,914 等关键数字独立复算全部复现);
  新鲜终审员判 needs-fix, v3 全修:
  - **P1×4**: ① T-D5b(i) 退化键机制落字到可实施 (绕过复合键、city-level
    折叠求和、B 锚判定=district∈CityName 键集、gate 锚死两权恒等); ② T-D3②
    三层口径钉死 (haystack=全名∪variants / 施加域=仅 280 家 / 支配规则=全命中
    嵌套才弃); ③ run_pipeline 字面量三→四 (+`_registry_sha` yaml 路径) +
    全域 grep 清零总则落 gate; ④ 县权面板 +`county_key_ok` int8 固定列
    (缺键与真零在面板端可区分, 复现包使用者无需税调名单即可重构 L3 子集)。
  - **P2×4**: §4 头部补 WP3 / SCHEME_LABEL_WORD 中文词 + END 标记字面量钉死
    (§1) / T-D6 语序重写 + A/B 共用分母点明 / T-D14 锚常量禁与 listed 同名。
  - **勘误×3** (收敛核验): F3/T-D5c 批注行数 272→47 (272 为并集) / T-D20①
    七字段枚举补"数据库名/表编号" / T-D3① 行号 01:545→01:547。
- **v4 (2026-07-08)**: 第三轮双路评审 (v3 增量终验 + 实施者视角走查, 各 needs-fix
  轻量收口) 修订, 并获用户完全授权执行。
  - **P1×4**: ① dv2 自举顺序 → 新增 WP5-stub 前置步 (03 常量壳先落, sha 一次
    定终, 锚在 WP-gate 期单次写入); ② T-D5c 施加位置落字"公共规范化段, 城县双
    受益" + 覆盖锚改显式返回值; ③ county_key_ok gate 改单向断言 + 家数锚 (双向
    在真零形态必翻车); ④ grep 清零白名单修订 (case-sensitive 三小写 token +
    三条白名单 + index 位置式赋值)。
  - **P2×9**: 中信例证更正 (支配规则已归一该分支本批空集) / ~964 定性 (境外空
    集, 精确下界 964, 禁硬锚) / district_norm 两步清洗定义 / 01 WARNING 文案 /
    40 面板残差处置协议 (禁就地加正则) / load_name_assets D4b 索引化授权 (92 对
    参照臂) / 牡丹江夹具=注入式合成原样迁移 / branch dta 行锚+城县身份锚 gate /
    §4 头部顺序补 WP5-stub。
  - **T-P0 探针实测结果 (2026-07-08 本机)**:
    - T-P0-1: 280 家 own-bank 机器映射 = **244 单命中 / 34 零命中 / 2 支配规则
      归一 (中信国际→自身剔母行·长兴→自身剔兴县) / 0 强制人工**; 34 家零命中
      全部核验为 NOT_IN_CANON (农发行/进出口行/村镇/农合/包商/港外资/象山·蓬安·
      盈江等小农商均不在 canonical 1,767; bank_names.json 实测无对应条目),
      值全 `[]`。280 家全量过目通过。
    - T-P0-2: 网点侧占位全集 = {海南省直辖 128, 海南省直辖县级行政区 93,
      省直辖县级行政区划 3, 省直辖县级行政区 1} 恰 225 行; 预清洗+T-D5c 回退后
      **B_city = 100.0000% (44,771/44,771)**, **B_county = 99.9042%
      (43,807/43,849, keyed 集=44,771−922)**, 未命中约 42 家开发区 ((iii) 通道)。
      ⚠ **探针估 (iii)=42 是下界; 生产 build_weight_branch_county 的归一化
      (city_key 去市尾 + district_norm 剥括注/脏值清洗) 与探针略异, 运行时实测
      (iii)=49、county_key_ok==0=971=922+49** (见 v5 记录; 代码/日志/codebook 一律
      以运行时实数为单一数字源, 探针 42/964 仅历史下界参照)。**锚终值: 城 A≥90% ∧
      B≥99.5%; 县 A≥85% ∧ B≥99.5%** (B 按实测上修; 运行时 A_city=100%/A_county=99.89%)。
    - T-P0-4: 跨公司重复 variant **67 个** (最大 8 归属), D5 多归属语义照搬。
    - T-P0-5: 公司 variant ⊂ 银行 variant 真子串对 **92 对** (listed 22 对基线;
      D4b 作废逻辑照搬, 92 对清单作运行时构建参照臂)。
    - T-P0-6: F 盘余量 2,275.6GB ≥120GB 先决闸 PASS。
    - T-P0-7: 2 字 variants 32 条全量过目 — 含 `科技`/`电脑`/`空中`/`商检` 等
      高泛用 token (源自简称列, 挂在建碁科技/纬创资通/北京阜通等个别企业) —
      **维持不裁剪口径** (与 listed 一致), §7-L1 披露升级: 点名高泛用 token
      清单, 提示分析端可按 usci 剔除受污企业行; 3 字 21 条无同级风险。
    - T-P0-3 (DV2 消费点): BankCanon 消费 unnameable/overseas_words/
      foreign_suffixes/affiliate_tail (03:292 最小集断言满足), generic_heads
      仅日志消费保留, city_placeholder/city_overseas 分支权消费保留;
      custodian_*/sanchan_words 确属 shareholder 侧 → 删。终集 = 8 保留键 +
      新增 city_placeholder_branch_side。
- **v5 (2026-07-08, 实施 + 结果评审 R1)**: 计划 v4 全链实施完成 (dev T=2):
  WP5-stub→WP0 (registry sha=**4f580e3fc458be0c6aac6636f4ed1c3e0936f839c9b815161150e048b6e4c034**,
  n_entries=730/emit=320/cut=410) → WP1 (主面板 850,649×1,914 = 20 固定 [含 usci] +
  1,894 加权; 八 gate 全绿) → WP3 (人工抽核 14/14 命中 + own-bank 6/6 剔除 + 加权手算
  5/5 + Stata /b 冒烟 usci str18/中文标签全过; L1 实证 2 例短名假阳性「电脑」「青岛港」)
  → WP5 (双权面板 branch_{city,county}w 各 13GB + 互验报告; **⚠ 首跑因 WP5 子 agent
  turn 结束致子进程孤儿化崩溃, 会话 shell 重跑 exit 0** — 非代码/内存问题) → run_pipeline+
  README → **WP-gate 124 gate 全绿** (registry 15 + panel 59 + weight 44 + lock 6; 五处
  计数字面量同步; grep-clean 断言; **fast A/B baseline-stash 差分 = IDENTICAL, 税调新增
  0 新失败** [8 个既存红灯 = dev T=2 盘上态, 与本次无关])。
  - **运行时实数 (权威, 覆盖探针估计)**: (iii) 开发区残差 = **49** (探针估 42);
    **county_key_ok==0 = 971 = 922 (ii) + 49 (iii) + 0 境外/空键**; 城市锚 A=B=100%;
    县域锚 A=99.89%/B=99.90%; BankCanon 映射 85.2% (未映射 7,647 种落审计附录);
    city×county Spearman ρ=**0.899** (n=945,447, 剔 144 恒等占位); 支配规则本批归一 2 例
    (中信国际/长兴), 强制人工 0 例; T-D5c 网点侧占位回退 = 已映射子集 138 行 (源 dta 占位
    225 行 − 未映射剔 87)。
  - **R1 结果评审** (Workflow 7 维度对抗 18 agents → 11 原始发现 → 9 存活, **全 P2, 0 P0/P1**):
    ① 数字同源化 (探针估 42/964 → 运行时 49/971): 修 02:766 codebook L3 prose 改定性引附录 /
    03 county_key_ok 日志改运行时分解 / 本 §9 与 §2·§3 探针估记为下界; ② 03:531 城权 (i)
    退化键补 PAREN_RE 剥离 (与 net_city/县权 deg_key 对称, 当前批 0 括注字节等价, 不再仅靠
    运行时 assert 兜底); ③ 03:475 T-D5c 回退日志补 225→138 和解项; ④ 互验报告 ④b 比值
    精度 .2f→.4g 与反向证据点名一致; ⑤ 补 usci 输出侧 str18 dtype integration gate
    (weight 件, 兑现 T-D14 'dta 读回 dtype 仍字符串'); ⑥ grep-clean token 补
    `company_listed_bank` + 白名单 02:32 LISTED_DIR (消覆盖不对称)。**均 P2 文档/日志/防御/
    覆盖层, 无一触及数据列/权重/gate 正确性; on-disk dev codebook/报告/日志预 R1 修复态,
    生产复跑 (§6 DEFERRED) 产一致文档**。
- **v6 (2026-07-08, 结果评审 R2)**: Workflow 6 维度新鲜对抗 + R1 修复复核 (13 agents →
  7 原始 → 5 存活: **1 P1 + 4 P2**)。
  - **P1 (提交面必修)**: 父仓 `.gitignore` 缺 company_tax_bank/{data,logs} 忽略行 →
    39GB 双权面板 dta + 陈旧 codebook/report 会被误提交。修: 加
    `news_process/company_tax_bank/logs/` (镜像 listed :89) 与
    `news_process/company_tax_bank/data/` (镜像 listed :99); git check-ignore 实证两者
    现已忽略 (logs 另受 news_process/.gitignore:48 通用 logs/ 覆盖)。
  - **P2×4 (防御完备/口径, 无 active bug)**: ① 03:573 县权 eligible 路径 city_key 补
    PAREN_RE+strip (与 net_comp.city/城权 key 538/deg_key 584 三方对称, 当前批 0 括注
    字节等价 — R1 fix② 完整化); ② 03 county_key_ok==0 运行时分解补第 4 桶「(i)placeholder
    退化键落空 = n_placeholder − n_placeholder_hit」+ **穷尽 5 桶 fail-loud assert** (当前批
    971=922+49+0+0 闭合; 生产权源 dta 刷新致某占位县失去全部分支时不再静默漏桶) +
    codebook 附录同步; ③ plan T-D16/§5-4 dta 确定性口径修正: pyreadstat.write_dta 头嵌
    分钟级墙钟时间戳 (17 字节, 无参可关) → dta 改「列内容哈希恒等」, 字节 sha256 仅锚
    parquet+md (数据列完全确定, 破的仅字节声明); ④ (R2 复核确认 R1 六修复均正确无回归)。
  - **验收**: compile+ruff 全过; 125 gate 全绿 (weight 45 含新 usci gate + 03 builder
    单元 + 13GB integration 锚; EXIT=0); listed 零改动; fast A/B 不变 (R2 改动 = gitignore
    + 03 源码防御项, 不触既有测试)。
- (后续评审轮次与实施记录在此追加)
