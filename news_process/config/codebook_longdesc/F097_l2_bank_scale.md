---
family_id: F097
columns:
- bank_scale
- bank_scale_ord
unit: bank_scale = 银行规模类别标签 (无量纲名义/有序类别); bank_scale_ord = 有序整数编码 (0-4)
formula: "bank_scale_ord = scale_map_ord.get(bank_scale, 0); scale_map_ord = {'XS': 1, 'S': 2, 'M': 3, 'L': 4}; 缺失/other → 0"
producer: news_process/pipeline/panel/runner.py::步骤7g-het ; news_process/pipeline/panel/export.py (variable-label)
upstream:
- enterprise_scale (上游实体注册/规模字段, 经银行实体匹配落到 bank-year 面板)
- 40_panel_yearly.parquet (bank_scale 列)
citations:
- doi: 10.1111/jofi.13400
  type: journal
  authors: Hoberg, G., & Phillips, G. M.
  year: 2025
  title: "Scope, scale, and concentration: The 21st-century firm"
  venue: Journal of Finance
  vol: 80
  issue: 1
  pages_or_artno: 415-466
- doi: 10.1086/726236
  type: journal
  authors: Berger, A. N., Bouwman, C. H. S., Norden, L., Roman, R. A., Udell, G. F., & Wang, T.
  year: 2024
  title: "Piercing through opacity: Relationships and credit card lending to consumers and small businesses during normal times and the COVID-19 crisis"
  venue: Journal of Political Economy
  vol: 132
  issue: 2
  pages_or_artno: 484-551
- doi: 10.1017/S0003055418000783
  type: journal
  authors: Enamorado, T., Fifield, B., & Imai, K.
  year: 2019
  title: "Using a probabilistic model to assist merging of large-scale administrative records"
  venue: American Political Science Review
  vol: 113
  issue: 2
  pages_or_artno: 353-371
- doi: 10.1037/h0026256
  type: journal
  authors: Cohen, J.
  year: 1968
  title: "Weighted kappa: Nominal scale agreement provision for scaled disagreement or partial credit"
  venue: Psychological Bulletin
  vol: 70
  issue: 4
  pages_or_artno: 213-220
new_dois: []
---

## CORE

【构念与来源】
本家族刻画每家银行在样本期内的规模层级 (bank scale tier), 是一个跨年基本固定的银行级 (bank-level) 属性, 用作异质性分析的调节变量 (moderator) 与 Bartik 移动份额工具变量的分组维度之一。构念上, 银行规模并非本流水线由新闻文本内生构造的测度, 而是从上游实体注册与规模字段 enterprise_scale 经银行实体匹配落到 bank-year 面板的外生标识符。它把连续、异质的机构体量压缩为少数几个可解释的层级: 大型 (L)、中型 (M)、小型 (S)、微型 (XS) 以及无法归类的其他 (other)。规模在银行与金融科技研究中是一阶重要的调节因子: 大型银行拥有更雄厚的技术投入能力、更强的合规与风控冗余、更分散的业务条线, 因而对同一则金融科技新闻冲击的敏感度、以及新闻语气到实际投资/绩效的传导斜率, 都可能系统性地不同于中小银行。Hoberg 与 Phillips (2025) 在对二十一世纪企业的范围、规模与集中度的刻画中指出, 规模维度与经营范围、市场集中度共同决定了企业面对外部冲击的调整弹性, 为在银行样本中按规模分层做异质性检验提供了平行参照 (须注意这是构念层面的平行参照而非对本银行分层口径的直接背书)。Berger 等 (2024) 则从关系型信贷与信息不透明的角度说明, 银行体量与客户规模高度耦合、并调节了银行获取与处理软信息的能力, 这为"规模 × 新闻语气"这类交互项承载真实机制信息、而非纯统计噪声, 提供了机制依据。

【方法学与计算】
落地上, 本家族含两列彼此对偶的表示。第一列 bank_scale 保留原始的名义/有序字符串标签 (取值集 L/M/S/XS/other), 直接进入 Bartik 规模维度工具变量的份额构造 (bartik_scale_share_L/M/S/XS 各按基期规模份额分解), 亦可作为回归中的分组因子做分层估计。第二列 bank_scale_ord 是对前者的单调有序整数编码, 由 runner.py 步骤 7g-het 用固定映射 scale_map_ord (XS→1、S→2、M→3、L→4) 生成, 任何未命中该映射的取值 (含 other 与缺失 NaN) 一律 fillna(0) 折为 0 并转 int。之所以另立有序编码列, 是因为交互项预计算需要一个可与情感/关注度等连续处理变量直接相乘、且沿规模方向单调递增的数值载体; 名义字符串本身无法进入乘积项, 而独热展开又会使交互项数目爆炸并牺牲单调性假设。选择整数序而非机构资产的连续对数, 是刻意的稳健性取舍: 有序编码对上游规模字段的测量误差与分箱边界不敏感, 只要层级排序正确即可, 契合 Brambor 等交互项建模传统中"调节变量应尽量预先决定、外生且低噪声"的要求。有序编码的另一层含义是把"规模层级差"当作等距近似处理; 这一等距假设的合理性可借鉴 Cohen (1968) 加权 kappa 对有序尺度分歧赋以按距离递增惩罚的思想来审视——相邻层级 (如 S↔M) 的一格之差与跨两格 (如 XS↔M) 之差在编码上被处理为线性可加, 使用者若担心该假设应改用分层虚拟变量做稳健性对照。上游 enterprise_scale 到银行实体的落库依赖实体匹配, Enamorado、Fifield 与 Imai (2019) 关于大规模行政记录概率化合并的框架说明了此类跨库匹配中命中率与误配对下游变量质量的影响, 因而 other/缺失折 0 的兜底既是安全降级也是对未匹配样本的显式标注。

【文献定位】
在文献坐标系中, 本家族服务于两条相互独立的用途。其一是异质性识别: 与 runner.py 同段生成的 is_soe (产权性质哑变量) 及 high_coverage (基年中位数固定切分的覆盖强度分组) 并列, bank_scale_ord 构成规模维度的调节轴, 三者刻画的是不同的银行结构性异质性来源, 彼此正交、不互为替代。其二是工具变量: bank_scale 是 Bartik 移动份额 IV 四个并列维度 (银行类型 type / 规模 scale / 媒体类型 media / 金融科技类别 fintech) 中的"稳健性 1"维度, 各维度各自基于不同的基期份额向量构造独立的 just-identified 工具, 互为稳健性、不分主次, 禁止把不同维度的 Bartik 工具混进同一 over-identified Hansen J 过度识别统计量。需要强调, 本家族与文本三轨 (full/ctx/ss)、co-primary 双轨嵌入、以及各类消融/权重/阈值/判据梯子完全无关: bank_scale 是 track-agnostic 的银行级元数据, 不随文本轨道变化、无 _lg 孪生, 也不参与留篇门控 (full-only 口径下 n_articles 的界定与本家族无涉)。因此本家族不承载"三轨禁混 Hansen J"之类的文本轨铁律, 唯一适用的并列铁律是上述 Bartik 维度层面的工具分离。

## VAR: bank_scale

【变体差分】
本列是家族的规范 (canonical) 载体, 保留银行规模的原始类别标签而不做数值化。取值域为 {L, M, S, XS, other}, 分别对应大型、中型、小型、微型与无法归类的其他银行; 其中 other 是显式的兜底类, 收纳上游 enterprise_scale 字段缺失或不属于四个标准层级的银行, 而非某个中间规模。与有序编码列 bank_scale_ord 的关键区别在于: 本列保留名义/有序字符串的全部信息, 不把 other 与真正的规模层级混同, 因而是 Bartik 规模维度工具变量份额构造 (bartik_scale_share_L / _M / _S / _XS) 的直接输入——份额分解须按标签逐类聚合基期占比, 只能在字符串标签上进行, 无法在折 0 后的整数序上进行 (折 0 会把 other 与真实的层级混淆并污染份额基)。本列亦可作为分层估计的分组因子, 在按规模切分的子样本回归中直接使用。数据来源为上游实体注册的 enterprise_scale, 经银行实体匹配落到 bank-year 面板, 跨年基本固定 (银行规模层级在样本窗内极少迁移), 属外生于新闻文本的银行级标识符, 不随 full/ctx/ss 文本轨道变化、无嵌入 _lg 孪生。在 export.py 中该列的 Stata 变量标签为 Bank Scale (enterprise_scale), 明确标注其上游字段出处。使用时需注意 other 类在异质性或份额估计中通常应单列或剔除, 不宜与四个标准层级作等距外推。

## VAR: bank_scale_ord

【变体差分】
本列是 bank_scale 的单调有序整数编码, 由 runner.py 步骤 7g-het 用固定映射 scale_map_ord (XS→1、S→2、M→3、L→4) 生成, 沿规模递增方向赋值 1→4; 任何未命中该映射的取值——包括 other 类与缺失 NaN——一律经 fillna(0).astype(int) 折为哨兵值 0。与规范列 bank_scale 的本质差异在于载体形态与用途: 本列牺牲了 other 与缺失的可区分性 (二者在此皆折为 0), 换取一个可直接进入交互项乘积、且沿规模方向单调的数值。它的唯一设计目的是异质性分析的交互项预计算: 名义字符串无法与情感/关注度等连续处理变量相乘, 而独热展开会使交互项数目膨胀并放弃单调性假设, 有序整数序则以最少的自由度保留了"规模越大传导越强/越弱"这一可检验的单调方向。选用整数序而非机构资产对数, 是对上游规模字段测量误差与分箱边界的稳健性取舍——只要层级排序正确, 编码即有效。需警惕的是本列隐含等距假设: 相邻一格 (如 S=2↔M=3) 与跨两格 (如 XS=1↔M=3) 之差被当作线性可加, 若研究关心非线性规模效应, 应改用分层虚拟变量做稳健性对照 (Cohen (1968) 加权 kappa 按距离递增赋权的思想可用于审视该等距近似的松紧)。哨兵 0 同时承担未匹配/未归类样本的显式标注功能, 使用者在回归中应决定是否将 0 类单列或剔除, 避免把"信息缺失"误当作"最小规模"。本列与文本三轨、嵌入双轨、各类梯子均无关, 是 track-agnostic 银行级元数据, 无 _lg 孪生。

<!-- rendered-citations:begin -->
Hoberg, G., & Phillips, G. M. (2025). Scope, scale, and concentration: The 21st-century firm. Journal of Finance, 80(1), 415-466. https://doi.org/10.1111/jofi.13400
Berger, A. N., Bouwman, C. H. S., Norden, L., Roman, R. A., Udell, G. F., & Wang, T. (2024). Piercing through opacity: Relationships and credit card lending to consumers and small businesses during normal times and the COVID-19 crisis. Journal of Political Economy, 132(2), 484-551. https://doi.org/10.1086/726236
Enamorado, T., Fifield, B., & Imai, K. (2019). Using a probabilistic model to assist merging of large-scale administrative records. American Political Science Review, 113(2), 353-371. https://doi.org/10.1017/S0003055418000783
Cohen, J. (1968). Weighted kappa: Nominal scale agreement provision for scaled disagreement or partial credit. Psychological Bulletin, 70(4), 213-220. https://doi.org/10.1037/h0026256
<!-- rendered-citations:end -->
