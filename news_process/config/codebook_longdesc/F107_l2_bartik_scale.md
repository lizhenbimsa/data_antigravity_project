---
family_id: F107
novelty_exempt_rationale: "该家族是 Bartik shift-share 工具变量在「银行规模」维度上的份额分量, 与 bartik_type (主维度) 共享同一 compute_bartik_iv 计算内核, 仅 group_prefix 与分组映射不同, 属规格稳健性并排的技术变体, 非独立新构念, 其测度定义的学术依据已在 GPSS(2020)/Adão et al.(2019)/Borusyak et al.(2022,2025)/Bartik(1991) 等母族 Bartik 工具变量文献中给出。"
columns:
- bartik_scale_share_L
- bartik_scale_share_M
- bartik_scale_share_S
- bartik_scale_share_XS
unit: 基期共现份额 (proportion, 无量纲, 定义域 [0,1]; 同一银行四组份额在非退化情形下横向求和为 1)
formula: "bartik_scale_share_g(i) = n_base(i,g) / Σ_{g'∈{L,M,S,XS}} n_base(i,g'); n_base(i,g)=基期年集合内目标银行 i 的同篇共现银行中规模组为 g 的计数; total==0 时 own-group one-hot 兜底 (own∈groups→该组=1 余=0, 否则整行 skip→NaN); 基期无文章或未映射→NaN"
producer: news_process/pipeline/panel/iv_did.py::compute_bartik_iv (group_prefix='scale'; runner 步骤 7e 调用, export.py 仅补 variable-label)
upstream:
- config/bank_addresses.json (enterprise_scale 字段 → 规模组映射 L/M/S/XS)
- 40_panel 银行×年面板 df_exploded (co_mentioned_banks 同篇共现银行串)
citations:
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: 39
  issue: 1
  pages_or_artno: 181-204
- doi: 10.48550/arXiv.2404.17049
  type: arxiv
  authors: Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W.
  year: 2024
  title: "Overidentification in shift-share designs"
  venue: arXiv
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: Review of Economic Studies
  vol: 89
  issue: 1
  pages_or_artno: 181-213
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: "Shift-share designs: Theory and inference"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 1949-2010
- doi: 10.17848/9780585223940
  type: book
  authors: Bartik, T. J.
  year: 1991
  title: "Who benefits from state and local economic development policies?"
  venue: W.E. Upjohn Institute for Employment Research
new_dois: []
---

## CORE

【构念与来源】
本家族四列 bartik_scale_share_L / _M / _S / _XS 是 Bartik (shift-share) 工具变量在「银行规模」维度上的基期暴露份额 (base-period exposure shares), 即 shift-share 结构中被冻结不变的 share 分量。构念上, 每一列刻画一家目标银行在样本基期与四类规模银行群体的「亲近度」: 目标银行 i 的份额 bartik_scale_share_g 等于基期年集合内 i 的同篇共现银行 (co_mentioned_banks) 中落入规模组 g 的计数, 除以 i 全部落入四类规模组的非兜底共现计数。规模组标签来自 config/bank_addresses.json 的 enterprise_scale 字段, 经映射表 SCALE_TO_SHORT 归一为四档: L 大型 / M 中型 / S 小型 / XS 微型; 落不进这四档的记为 other 并在分母前被剔除。该维度是 Bartik 工具的稳健性维度之二 (主维度为银行类型 nfra_type, 另两条稳健性维度为金融科技类别与媒体类型), 与主维度共享同一 compute_bartik_iv 计算内核, 仅 group_prefix 与分组映射不同。

【方法学与计算】
计算由 pipeline/panel/iv_did.py::compute_bartik_iv 承担 (runner 步骤 7e 调用, group_prefix='scale'), pipeline/panel/export.py 只负责补 .dta variable-label 不产数。流程分四步: 其一, 取面板中 year 落在基期年集合 (base_years, 单年时退回面板最早年) 的文章子集作为 base; 其二, 对 base 内每篇文章把 co_mentioned_banks 按分号切分并 explode, 映射到规模组, 丢弃 other; 其三, 对每家目标银行按组计数得 n_base(i,g), 除以其非 other 共现总数 total 得份额, 四组份额横向求和为 1 (退化情形除外); 其四, 份额被冻结, 与「组×年」的留一 (leave-one-out) shift 相乘并跨组求和, 合成 bartik_scale_iv_{full,ctx,ss} 三轨工具列 (本家族只落 share 分量, IV 列另属工具家族)。缺失与退化语义严格保留、绝不零插补: total==0 (基期无跨组共现) 时退化为 own-group one-hot (该行仅当银行自身规模组在 groups 内才置该组=1、余=0, 否则整行 skip 使 merge 后 share=NaN); 基期无文章或未映射到规模组的银行 share 保持 NaN, 以消除 Goldsmith-Pinkham et al. (2020) 所警示的 incomplete-shares 伪零暴露; 面板 year < max(基期年) 的行携带「未来」测得的 share, 其基期份额预定外生性论证结构性失效, 对应 IV 列被前视掩码置 NaN (share 列本身保留供诊断)。识别路径上, 本实现仅依赖 GPSS (2020) 的「基期份额外生性」视角, 不主张 shift 侧的准随机冲击外生性; Rotemberg 权重诊断走 Cov(share, BIV) 的近似而非 GPSS 精确 α_k。

【文献定位】
方法学锚定 Bartik (1991) 提出的 share×shift 加权范式, 及其现代计量化: Goldsmith-Pinkham et al. (2020) 在 American Economic Review 系统阐明 Bartik 工具的两条识别路径 (份额外生 vs 冲击外生) 与 Rotemberg 权重诊断, 是本 share 分量识别论证的直接依据; Adão et al. (2019) 给出 shift-share 设计下的正确推断与标准误校正; Borusyak et al. (2022, 2025) 从冲击外生视角补全 quasi-experimental 解读与操作核对清单。须强调本项目对 Bartik 工具的多维度实现 (类型/规模/金融科技/媒体) 属规格稳健性并排: 各维度、各文本轨 (full/ctx/ss) 的 just-identified 工具各自并排、互为稳健性、不分主次, 严禁把不同维度或不同轨的份额混进同一 over-identified Hansen J 过度识别检验 (计量支撑见 Hahn et al. (2024) 对 shift-share 过度识别的处理)。留篇口径与全仓一致遵循 full-only 门控 (2026-06-29): 一篇报道是否计入基期共现由 full 轨留篇判定, ctx/ss 为 conditional-on-full 的稳健性轨。

## VAR: bartik_scale_share_L

【变体差分】
本列是「大型银行」(L, enterprise_scale='L(大型)') 维度的基期共现份额: 目标银行 i 基期同篇共现银行中被 SCALE_TO_SHORT 归为 L 组的计数, 占其全部非 other 规模组共现计数之比。它与同家族 _M/_S/_XS 是同一 compute_bartik_iv 单次调用 (group_prefix='scale') 内并列产出的四个分组份额, 区别仅在分子所计规模组不同, 分母 total 三列共享。语义上它衡量目标银行在基期与国有大型商业银行等大型机构的媒体共现亲近度, 冻结后作为 Bartik 规模维度工具 bartik_scale_iv 的一个 share 权重。退化情形 (total==0 且银行自身即 L 组) 会 one-hot 退化为该列=1、余三列=0; 基期无文章或未映射银行该列=NaN。⚠ 生产 T=2 试跑下基期跨规模组共现大面积为 0, 相当比例的 bank-year 因缺乏跨规模档共现而退化为 own-group (银行自身规模档) one-hot, 该列在 T=2 会出现大量 0/1 极化, 属结构退化非缺陷, 全量 T=18 恢复连续 (具体退化占比随规模映射与语料而变, 不套用其它维度的实测比率)。识别路径上本列沿 GPSS (2020) 基期份额外生性假设: 大型银行档份额在基期被视为预定, 不随目标银行当期结果 (情感、投资、绩效等) 内生变动, 从而使 bartik_scale_iv 满足工具的排他性论证。前视掩码只作用于下游 IV 列, 不改写本 share 列的历史行取值。留篇口径遵循 full-only 门控 (2026-06-29): 该列基期共现计数只统计 full 轨留篇判定为一篇银行金科报道的文章, ctx/ss 为 conditional-on-full 稳健性轨。铁律: 本 share 与 _M/_S/_XS 及 full/ctx/ss 三文本轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 过度识别处理的计量支撑见 Hahn et al. (2024)。

## VAR: bartik_scale_share_M

【变体差分】
本列是「中型银行」(M, enterprise_scale='M(中型)') 维度的基期共现份额: 分子改为目标银行 i 基期同篇共现银行中规模组为 M 的计数, 分母与 _L/_S/_XS 共享同一 total (i 的非 other 规模组共现总数)。它捕捉目标银行在基期与中型规模银行的媒体共现亲近度, 冻结后与「M 组×年」留一 shift 相乘, 构成 bartik_scale_iv 三轨工具的一个加权项。该列与家族其余三列唯一差异即所计规模档为 M; 缺失、one-hot 兜底 (total==0 且自身为 M 组时该列=1)、前视掩码等语义与家族口径完全一致。GPSS (2020) 份额外生性识别路径对本列同样适用: 基期份额被视为预定, 不随当期结果内生变动。T=2 退化下本列亦呈 0/1 极化, 全量语料下恢复为跨中型同业的连续暴露比例。需强调本列与银行类型维度的 bartik_type_share_* 属彼此正交的稳健性维度: 规模档 (L/M/S/XS) 依 enterprise_scale 切分, 类型档 (soe/joint/city/rural/private/foreign) 依 nfra_type 切分, 两套映射相互独立, 因此规模维度工具是类型维度工具的独立稳健性替代而非其变换。留篇口径遵循 full-only 门控 (2026-06-29), 基期共现计数只纳入 full 轨留篇文章。铁律照旧: 四规模档份额与 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J; 过度识别处理见 Hahn et al. (2024)。

## VAR: bartik_scale_share_S

【变体差分】
本列是「小型银行」(S, enterprise_scale='S(小型)') 维度的基期共现份额: 分子为目标银行 i 基期同篇共现银行中规模组归为 S 的计数, 分母沿用四列共享的非 other 规模组共现总数 total。它度量目标银行在基期与小型规模银行 (如部分城市/农村商业银行中的小体量机构) 的媒体共现亲近度, 冻结后作为 Bartik 规模维度工具的 S 组 share 权重, 与「S 组×年」留一 shift 组合进 bartik_scale_iv_{full,ctx,ss}。与家族其余三列的唯一区别在所计规模档为 S; total==0 且银行自身即 S 组时 one-hot 退化为该列=1、余=0, 基期无文章或未映射时=NaN, 前视掩码只作用于下游 IV 列不改本 share 列。识别仍走 GPSS (2020) 基期份额外生性单一路径, 不叠加 shift 侧外生主张; 小型银行档份额在基期冻结后被视为预定量, 不随目标银行当期结果内生变动。前视掩码机制下, 面板 year 早于基期末年的行其 bartik_scale_iv 被置 NaN 而本 share 列保留供 Rotemberg 权重诊断。留篇口径遵循 full-only 门控 (2026-06-29): 基期共现计数只统计 full 轨留篇文章, ctx/ss 为 conditional-on-full 稳健性轨。推断层面须注意 Adão et al. (2019) 指出的 shift-share 标准误须作专门校正, 本 share 分量的方差贡献不可按普通聚类简单处理。铁律: 本 S 份额与 _L/_M/_XS 及 full/ctx/ss 三文本轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 过度识别处理的计量支撑见 Hahn et al. (2024)。

## VAR: bartik_scale_share_XS

【变体差分】
本列是「微型银行」(XS, enterprise_scale='XS(微型)') 维度的基期共现份额, 为家族四档中最小规模档: 分子为目标银行 i 基期同篇共现银行中规模组归为 XS 的计数, 分母仍为四列共享的非 other 规模组共现总数 total。它刻画目标银行在基期与微型规模银行 (如部分民营/村镇微体量机构) 的媒体共现亲近度, 冻结后作为 bartik_scale_iv 三轨工具的 XS 组 share 权重。与家族其余三列的唯一差异是所计规模档为 XS; 因微型银行样本稀薄, 该列在多数银行取小值或 0, 且 total==0 且银行自身即 XS 组时 one-hot 退化为该列=1、余=0, 基期无文章或未映射=NaN。⚠ T=2 试跑下 XS 档常整列近零方差或极化, 属基期共现稀疏的结构退化, 全量 T=18 方具区分度。识别沿 GPSS (2020) 基期份额外生路径, 微型档份额在基期冻结后不随当期结果内生。因 XS 档暴露稀薄, 该列在 Rotemberg 权重诊断中通常贡献极小权重, 对应的 shift 若在某年因组内留一后无剩余同业而不可计算, 则该 bank-year 的 IV 传播 NaN 而非零插补。留篇口径遵循 full-only 门控 (2026-06-29): 基期共现计数只纳入 full 轨留篇文章, ctx/ss 为 conditional-on-full 稳健性轨。Borusyak et al. (2025) 的操作核对清单提示, incomplete-shares 情形下的重归一选择须谨慎披露, 本实现以保留 NaN 而非补零对齐该建议。铁律不变: XS 份额与 _L/_M/_S 及 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W. (2024). Overidentification in shift-share designs. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.17049
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Bartik, T. J. (1991). Who benefits from state and local economic development policies?. W.E. Upjohn Institute for Employment Research. https://doi.org/10.17848/9780585223940
<!-- rendered-citations:end -->
