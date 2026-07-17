---
family_id: F588
columns:
- tone_nonmkt_media_ctx
- tone_nonmkt_media_full
- tone_nonmkt_media_ss
unit: 语调得分 (连续, 理论区间约 [-1,1]; 文章级 LLM 投票分先算, 再按 bank-year 单元取子样本均值)
formula: 'tone_nonmkt_media{track} = mean(llm_vote_score{track} | _is_market==0), 分组键 (target_bank, year), 子样本 = 该 bank-year 单元中 _is_market==0 (非纯市场化媒体, 含官方/双判据/其余未标记来源) 的全部文章; _is_market 定义见【方法学与计算】'
producer: pipeline\panel\attention_media.py (维度⑥ market/nonmkt 情感均值双支路)
upstream:
- 21_tone_llms (llm_vote_score_full / _ctx / _ss)
- 13_cooccurrence_filter (行宇宙)
- 14_materialize_ctx (content_ctx / content_ss 三轨文本物化)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who Captures the Power of the Pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: Media Coverage and the Cross-Section of Stock Returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: 10.1111/jofi.12179
  type: journal
  authors: Peress, J.
  year: 2014
  title: 'The Media and the Diffusion of Information in Financial Markets: Evidence from Newspaper Strikes'
  venue: The Journal of Finance
  vol: '69'
  issue: '5'
  pages_or_artno: 2007-2043
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: 'Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  issue: ''
  pages_or_artno: 1150-1172
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: Media Bias in China
  venue: American Economic Review
  vol: '108'
  issue: '9'
  pages_or_artno: 2442-2476
- doi: "10.1016/j.enpol.2023.113917"
  title: "Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry"
  authors: "Xu, Z., Li, J., Hua, X., & Ren, P."
  year: 2024
  venue: "Energy Policy"
  type: "journal"
- doi: "10.1016/j.ememar.2024.101234"
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  authors: "Xu, Z., Hua, X., & Zhang, T."
  year: 2025
  venue: "Emerging Markets Review"
  type: "journal"
new_dois:
  - "10.1016/j.enpol.2023.113917"
  - "10.1016/j.ememar.2024.101234"
---

## CORE

【构念与来源】
`tone_nonmkt_media{full,ctx,ss}` 度量的是"非市场化媒体对目标银行报道语调"这一构念, 是家族维度⑥「媒体政治取向异质性」中 market/nonmkt 二分下的对照组测度。构念根植于 You, Zhang & Zhang (2018, RFS)「谁执笔杆子」的核心洞见: 中国媒体在所有权与治理逻辑上并非同质样本, 市场化媒体 (自负盈亏、依赖发行/广告收入) 与非市场化媒体 (党政机关报、行业系统报等) 在报道动机、独立性与议程设置上系统性分岔; 前者更接近 Tetlock (2007, JF) 经典"媒体语调 = 投资者情绪代理"框架下的信息中介角色, 后者则更多承担宣传/协调功能, 报道基调受行政意志与政治周期驱动而非纯粹的信息含量驱动。`tone_nonmkt_media` 正是这条分岔线上"非市场化"一侧的语调水平, 与其对照的 `tone_market_media` 及两者之差 `tone_gap_market_nonmkt{track}` 共同构成识别媒体所有权效应的三件套。

来源链路: 文章级情感底层是 stage 21 `21_tone_llms` 产出的 `llm_vote_score{track}` (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash 三家 LLM 多数投票共识分, 连续尺度), 三轨 (`_full`/`_ctx`/`_ss`) 分别对应全文、银行实体窗口上下文、银行∧金科同句窗口三种文本切片下独立跑的情感分。分组媒体来源判据 `_is_market` 由 `pipeline\panel\attention_media.py` 在维度⑥内构造: 依据「媒体(中文)」出版单位名称, 用 NPPA (国家新闻出版署) 主办单位登记信息比对两份预置名单 MARKET (以企业/商业集团为主办方) 与 OFFICIAL (以党政机关为主办方), `_is_market = isin(MARKET - OFFICIAL)` —— 即只把"纯市场化" (在 MARKET 名单内且不在 OFFICIAL 名单内) 的来源记为 1, 其余 (含双判据重叠来源、既不在 MARKET 也不在 OFFICIAL 的来源) 记为 0。`tone_nonmkt_media{track}` 即取 `_is_market==0` 子样本, 按 (target_bank, year) 分组对 `llm_vote_score{track}` 求均值。

【方法学与计算】
`_is_market` 的构造经历过一次口径修正 (代码注释 fix(omni-g-attention-02, 2026-06-11)): 早期版本对 `market_media_frac`/相关 dummy 直接取 `isin(MARKET)`, 结果 82% 的 MARKET 名单来源同时落在 OFFICIAL 名单内 (重叠 386 家), 使 You-Zhang-Zhang 意义上本应对立的"纯市场化 vs 纯官方"构念被双重身份来源的噪声稀释、甚至反向掩盖。修正后改为结构性互斥判据: `market := MKT − OFF` (纯市场化, 即维度⑥的处理组), `official := OFF − MKT` (纯官方, 维度⑤的处理组); 同时具备双重身份的媒体来源 (OFF∩MKT) 不计入任一处理组, 而是落入两个维度各自的对照组 (维度⑤的 `nonoff`、维度⑥的 `nonmkt`)。这意味着 `tone_nonmkt_media` 的对照组并非"官方媒体"的镜像补集, 而是"非纯市场化"的广义补集 —— 包含纯官方来源、双判据重叠来源, 以及既未登记为市场化企业主办也未登记为党政机关主办的其余来源。这一口径选择使 `tone_market_media` 与 `tone_nonmkt_media` 之差 (`tone_gap_market_nonmkt{track}`) 能够干净地识别"纯市场化身份"这一处理效应, 而不被重叠样本的混合信号稀释, 代价是 `tone_nonmkt_media` 本身是一个异质对照组均值, 不宜单独解读为"官方媒体语调"。

三轨并排是本列族的第二层结构。full 轨在标题+全文上跑情感, 是 stage 21 的留篇门控轨 (`llm_verified_full==True` 决定一篇文章是否计入"银行金科报道"); ctx 轨在标题+银行实体窗口上跑; ss 轨在标题+银行∧金科同句 (±N 句窗口, 默认 N=1) 上跑, 缺失同句共现时优雅回退为全文 body 并置 `ss_is_fallback=True`。三轨在 `attention_media.py` 内以完全相同的分组-子样本-求均值逻辑各自独立计算 (`for track in ['_full','_ctx','_ss']: src = f'llm_vote_score{track}'`), 任一轨源列缺失即跳过该轨 (`if src not in df.columns: continue`), 不借用其他轨的值填补。三轨互为稳健性、各自 just-identified 并排, 禁止混入同一 over-identified Hansen J 检验; full 轨是留篇门控口径下的主测度, ctx/ss 是 conditional-on-full 的测度稳健性轨, 行宇宙是 full 轨留篇集的子集。

聚合分母上须注意: `tone_nonmkt_media{track}` 是"文章级子样本均值", 分母是该 bank-year 单元中 `_is_market==0` 且该轨情感分非缺失的文章数, 与 `n_articles`/`fintech_share` 等篇数类指标的分母 (全篇或留篇门控集) 不是同一集合; 当某 bank-year 单元当年报道全部来自市场化媒体 (即 `_is_market==0` 子样本为空) 时, `tone_nonmkt_media{track}` 取值缺失 (NaN), 属预期行为而非数据缺陷, 使用者做回归前应检视缺失模式是否与银行规模/地域相关。

【文献定位】
本列族的构念定位直接对接 You, Zhang & Zhang (2018, RFS) 关于中国媒体"谁执笔"的所有权异质性框架, 将其市场化/非市场化二分应用到银行金融科技报道的情感测度上; 语调本身的测量哲学承袭 Tetlock (2007, JF) 与 Fang & Peress (2009, JF) 确立的"媒体语调作为信息含量/投资者情绪代理"传统, 以及 Peress (2014, JF) 关于媒体信息扩散对定价效率因果作用的证据基础。Holzman, Miller & Twedt (2023, TAR) 提供了本家族「媒体权威性加权」姊妹列族 (`llm_vote_tone_mw{track}`) 的方法学锚点, 也间接印证媒体来源异质性 (权威度、所有权) 对语调测度解释力的调节作用, 支撑本处按来源属性拆分的必要性。中国情境下的经验证据参照 Qin, Strömberg & Wu (2018, AER) 关于中国媒体偏向的系统性证据, 以及同域的 Fang, Wang, Wang & Yuan (2024, IREF) 银行层面媒体情感与存款稳定性/系统性风险研究, 后者直接支撑本家族服务于银行研究场景的建模选择。Xu, Li, Hua & Ren (2024, Energy Policy) 用 BERT 量化中国政府控制媒体语调对新能源企业股价的影响, 为本家族按媒体所有权 (市场化/非市场化) 拆分语调测度的构念提供了同期中国情境下的方法学与实证支撑; Xu, Hua & Zhang (2025, Emerging Markets Review) 构造官方媒体情绪指数并考察其对中国股市收益反转与散户交易行为的预测力, 呼应本家族非市场化媒体语调测度所依托的"官方媒体语调具有独特信息/情绪功能"这一构念。

## VAR: tone_nonmkt_media_ctx

【变体差分】
本列是 ctx 轨: 情感底层为 `llm_vote_score_ctx`, 该分是在"标题 + 银行实体窗口上下文" (而非全文) 上跑三家 LLM 投票得到的文章级语调分。ctx 轨的文本切片在 stage 14 `ctx_materializer` 物化为 `content_ctx` (+ `ctx_is_fallback` 标记), 围绕目标银行实体名的邻近窗口截取, 目的是让情感判断聚焦在与目标银行直接相关的语境, 而非被同篇报道中涉及的其他主体/事件稀释。`_is_market` 分组判据与 full/ss 轨完全共用同一套 (target_bank, year) 分组键与媒体来源名单, 唯一差异是被求均值的源列换成 `llm_vote_score_ctx`; 若某 bank-year 单元的 `llm_vote_score_ctx` 存在但对应 `_is_market==0` 子样本恰好为空 (例如该年非市场化媒体报道恰好都因窗口截取失败而缺失该轨分), 则本列取 NaN, 与同一单元的 full 轨取值可能不同步缺失。2026-06-29 起 full 轨承担"是否计入一篇银行金科报道"的留篇门控职责, ctx 轨降级为 conditional-on-full 的测度稳健性轨: 行宇宙 = full 轨留篇集的子集, 本列与 `tone_nonmkt_media_full` 应被理解为对同一构念的两次独立测量, 互为稳健性、不设主次, 禁止在同一 over-identified 设定 (如单一 Hansen J 检验) 中把两轨系数同时作为过度识别的工具变量或矩条件混用。ctx 轨的价值在于剥离同篇报道中与目标银行无关的段落 (例如一篇同时报道多家银行或多个行业事件的综合性报道), 使语调测度更贴近"该银行本身在这篇报道里被如何评价", 代价是窗口截取可能在实体识别边界处引入噪声, 尤其当银行简称与其他机构名存在字面重叠时。研究者在解读本列与 full 轨的差异时, 应优先归因于语境聚焦效应而非数据质量问题, 除非 `ctx_is_fallback` 标记显示窗口物化失败率异常偏高。

## VAR: tone_nonmkt_media_full

【变体差分】
本列是 full 轨, 也是家族口径下的主测度轨: 情感底层为 `llm_vote_score_full`, 在"标题 + 全文"上跑三家 LLM (gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash) 投票得到的文章级语调分。留篇门控 (2026-06-29 起) 以 `llm_verified_full==True` 判定一篇文章是否属于"银行金科报道", 这一门控只在 full 轨上执行, 因此本列所依赖的行宇宙即为该银行金科报道全集 (未经实体窗口或同句窗口二次裁剪), 是三轨中信息保留最完整、覆盖面最广的一支。分组子样本仍是 `_is_market==0` (非纯市场化媒体) 的文章, 按 (target_bank, year) 求 `llm_vote_score_full` 均值。P1 主线论文 (`bank_fintech_tone`) 的处理变量 `llm_vote_tone_full` 即建立在同一 full 轨情感底层上, 本列可理解为该主处理变量在"非市场化媒体来源"这一子样本上的条件均值, 用于检验媒体所有权异质性是否驱动整体语调结果、或反过来为整体语调结果提供来源层面的稳健性佐证。与 ctx/ss 两轨的关系遵循三轨并排铁律: 各自 just-identified, 互为稳健性不分主次, 不得混入同一 over-identified Hansen J。使用者若要检验"媒体所有权异质性是否驱动 P1 主线结论", 建议以本列 (full 轨非市场化子样本均值) 与 `tone_market_media_full`、`tone_gap_market_nonmkt_full` 三者并看, 而非孤立解读单一列; 三者共享同一 full 轨情感底层与同一年份分组键, 差异只在被平均的子样本, 因而彼此的比较在同一测量尺度下是有意义的, 但不构成可叠加的分解式 (子样本均值之差不等于整体样本的所有权效应估计量, 需在回归框架下控制银行-年份规模等混杂后再解读)。

## VAR: tone_nonmkt_media_ss

【变体差分】
本列是 ss 轨: 情感底层为 `llm_vote_score_ss`, 在"标题 + 银行∧金科科技词同句 (±N 句窗口, 默认 N=1, 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制) "文本切片上跑得到, 是三轨中语境最窄、判据最严格的一支, 判定原语要求银行实体与金科词汇在同一句 (或邻近句窗口) 内共现, 银行侧判据含否定+短名过滤、金科侧判据为裸 AC 自动机 1506 词表匹配, 两侧口径刻意不对称。当某篇报道不存在银行∧金科同句共现时, ss 轨回退语义镜像 ctx 轨: `content_ss` 取全文 body、`ss_is_fallback=True`, 该篇文章仍参与情感打分与本列的均值计算, 只是其 `llm_vote_score_ss` 实质上等价于全文轨的信息量, 使用者若需剔除回退样本应结合 `ss_is_fallback` 列自行过滤 (本列本身不做该项过滤)。分组逻辑与另两轨完全一致: `_is_market==0` 子样本按 (target_bank, year) 对 `llm_vote_score_ss` 求均值; 若源列 `llm_vote_score_ss` 在某次运行中整体缺失 (如 `FINTECH_AC=None` 导致的优雅降级链路上游), 本列在 `attention_media.py` 内的循环会直接跳过该轨, 全列置缺失, 不会静默退化为借用 full 轨的值填充。ss 轨与 full/ctx 轨同为 conditional-on-full 的稳健性并排轨, 互为稳健性不分主次, 禁止混入同一 over-identified Hansen J。由于同句共现判据比 ctx 轨的实体窗口更严苛, ss 轨在实践中对回退样本的依赖程度通常高于 ctx 轨 (更多文章找不到严格同句共现而触发全文回退), 因此本列的信息增量集中在那些确实存在银行∧金科紧密语境关联的报道子集上; 对这部分非回退样本, 语调判断最贴近"金融科技相关叙事本身对银行的评价", 是识别银行-金科关联语调 (而非泛化银行报道语调) 最严格的一支测度, 适合作为家族内其余两轨的上限约束式稳健性检验。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Fang, L., & Peress, J. (2009). Media Coverage and the Cross-Section of Stock Returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Peress, J. (2014). The Media and the Diffusion of Information in Financial Markets: Evidence from Newspaper Strikes. The Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Qin, B., Strömberg, D., & Wu, Y. (2018). Media Bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Xu, Z., Li, J., Hua, X., & Ren, P. (2024). Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry. Energy Policy. https://doi.org/10.1016/j.enpol.2023.113917
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2024.101234
<!-- rendered-citations:end -->
