# 劳动力成本与劳动节约型技术创新 $ ^{*} $

——来自 AI 语言模型和专利文本的证据

刘青肖柏高

内容提要: 从替代体力的蒸汽机到替代脑力的 AI, 重大劳动节约型技术的创新和应用都深度改变了世界经济发展格局, 并成为学界研究焦点。然而梳理文献发现, 现有关于劳动节约型技术的研究主要聚焦于其应用或引进, 对其创新关注甚少。本文首次结合 AI 领域前沿的 BERT 语言模型和专利摘要较为精准地识别劳动节约型技术创新。在此基础上, 考虑到中国正处于老龄化加剧、劳动力成本快速上涨阶段且劳动节约型前沿技术引进日益受阻, 检验劳动力成本上升如何影响中国企业的劳动节约型技术自主创新。基于上市公司数据, 本文发现劳动力成本上升显著地促进了劳动节约型技术创新的概率、数量、占比以及质量。使用考虑中国省界特征的相邻城市样本来解决潜在内生性问题后结论依然成立。本文提出的特定技术创新的识别方法可复制推广, 在技术创新相关研究领域有较大应用前景。本文研究结论对于理解我国在人口红利消失、老龄化加剧、劳动力成本快速上升阶段的特定类型技术创新有重要启示。

关键词: 劳动节约型技术 BERT 模型 劳动力成本 最低工资

## 一、引言

劳动节约型技术(labor saving technology,又称劳动替代型技术)是指能代替或节约劳动力使用的技术。 $ ^{①} $自工业革命以来，技术换人一直都是备受关注的话题，其热度经久不衰的原因在于，一方面，劳动节约型技术的应用对于经济增长和劳动力市场有重大影响，如生产率、就业结构、劳动收入份额、劳动收入差距、老龄化等； $ ^{②} $另一方面，劳动节约型技术在不断创新，从替代体力的蒸汽机到替代脑力的人工智能(AI)，技术对劳动力的替代不断泛化和深化，从而推动劳动节约型技术持续地成为社会大众和学术研究的焦点。这两方面的因素都非常重要，缺一不可。

这两个因素中，第一个因素即劳动节约型技术的应用已经得到充分研究，但是第二个因素创新却较少受到关注，仅有 Acemoglu（2010）等从理论上进行了探讨。创新是技术进步的根源，是劳动节约型技术能不断影响经济发展和劳动力市场的背后力量。党的二十大报告再一次强调了创新在我国现代化中的核心地位，同时也指出创新要“面向世界科技前沿、面向经济主战场、面向国家重

大需求、面向人民生命健康，加快实现高水平科技自立自强”。然而至今为止，对于劳动节约型技术这种在我国经济增长、劳动力成本上升、老龄化加剧等重大问题中有重大影响的技术，我们对其创新的具体情况都不甚了解，例如最基本的也是本文所关注的问题，我国企业是否有进行劳动节约型技术创新？或者说企业的劳动节约型技术进步是否来源于创新？为了更好地掌握劳动节约型技术的前沿动态对我国经济的影响，以及更好、更安全地应用其来应对我国劳动力成本和数量优势消失、老龄化加剧等紧迫问题，我们有必要对劳动节约型技术自主创新（而不仅仅是其应用或引进）进行深入研究。

阻碍劳动节约型技术创新相关研究一个可能的重要原因是数据缺失。劳动节约型技术的应用指标已经不少，例如机器、电脑、机器人等的存量或安装指标(Krueger,1993; Acemoglu & Restrepo,2020; 王永钦和董雯,2020)。但是梳理文献可知，目前尚未有良好的劳动节约型技术创新的直接度量指标，这使得高质量的实证研究难以开展，而理论研究也可能会因为缺少典型事实或关键参数支持而难以持续深化。因此，只有构建劳动节约型技术创新指标，我们才能了解劳动节约型技术进步动态，才能把握分析其对于经济和社会的真实影响。

基于上述现实与学术背景，本文引入人工智能领域前沿的 BERT 语言模型（以下简称 BERT），基于专利摘要语义识别以节约劳动为目的或者客观上可以节约劳动力的专利技术，构建劳动节约型技术创新的直接度量指标，并在此基础上研究劳动力成本上升对我国劳动节约型技术创新的影响。BERT 是人工智能领域中具有突破性的前沿研究成果，它尝试将文本语义“翻译”为计算机可以处理的向量。BERT 在权威的阅读理解测试中超越了人类平均水平，在 AI 学术界和工业界得到了广泛认可和使用。 $ ^{①} $ 专利摘要描述了该专利技术的功能和用途，可以通过摘要语义判断出其是否属于劳动节约型技术。本文随机挑选了 5000 条专利进行人工分类，如果专利摘要指出本专利旨在替代劳动力，或者描述了能够（部分）替代劳动力的技术或设备，则将其归为劳动节约型专利。接着让 BERT 去学习这些人工分类案例所蕴含的分类规则，再让学习完的 BERT 去对所有专利进行分类。以人工识别结果为基准，BERT 在样本内的预测准确度接近 100%，样本外的预测准确度也高达 90%。进一步的回归检验结果也显示，劳动节约型专利可以显著减少企业的低技能劳动力数量，而非劳动节约型专利会显著增加企业各类别的劳动力数量，和理论预期相符，进一步确认了本文识别方法的总体可靠性。

在准确识别劳动节约型技术创新的基础上，本文基于2002—2016年间中国上市公司、专利和地级市最低工资匹配数据，发现最低工资政策导致的劳动力成本冲击显著、全面地促进了劳动节约型技术创新。具体而言，最低工资上升提高了企业劳动节约型技术创新的概率、数量、质量以及劳动节约型技术创新在总体创新活动中的比重。进一步分析发现，这一效应在劳动密集型、低技能员工占比高、工资水平相对较低的企业或行业中更加显著，说明最低工资的确会通过提升劳动力成本从而促使企业研发劳动节约型技术。本文使用（考虑中国省界特征的）相邻城市法、工具变量、双重差分法来解决可能的内生性问题，并检验了模型设定、关键变量等方面的稳健性，结论均成立。

本文的创新与贡献包括新数据、新发现和新方法三个方面。在数据方面，本文首次构建了劳动节约型技术创新指标，显著区别于电脑、机器人安装量等应用指标，为劳动节约型技术创新相关理论和实证研究奠定微观数据基础。在发现层面，本文首次证实了劳动要素层面的“引致创新假说”，即要素价格上升会引致能减少此要素使用的技术创新（Hicks，1932）。由于缺乏良好的劳动节约型技术创新指标，这一重要假设其实并未得到严格检验，已有的相关研究本质上是证明劳动力

成本上升引致劳动节约型技术应用，或者促进总体创新水平(以专利总量或研发投入等衡量)。更重要的是，这两类文献都有重要问题未能回答，分别是所应用的劳动节约型技术的来源是购买还是研发？劳动力成本具体以什么机制影响了什么创新？

劳动力成本上升引致劳动节约型技术应用这类文献， $ ^{①} $尤其是关于中国的文献，没有回答所应用技术是否来自于创新。以机器人这种当下最典型的劳动节约型技术为例，Fan et al.（2021）发现最低工资促进了我国企业进口机器人，国际机器人联盟的数据也表明，直到2020年中国安装的机器人仍有约四分之三来自于进口， $ ^{②} $说明我国目前有通过购买来实现劳动节约型技术进步。那么自主创新是否是我国劳动节约型技术的来源之一呢？回答这一问题不仅仅是填补文献空白，也具有重大现实意义。最近我国企业从外国购买先进的机器人或AI等技术的正常市场行为已经遇到了阻碍， $ ^{③} $而随着国家之间技术竞争加剧，可以预见这些障碍将会持续存在，甚至有加剧的可能。因此自主创新应当成为劳动节约型技术进步的主要动力，为我国应用劳动节约型技术解决劳动力成本上升、数量下降等问题提供安全保障。

劳动力成本影响总体创新水平（以专利总量等衡量）的这类文献， $ ^{④} $无法回答劳动力成本具体以什么机制影响什么创新。劳动力成本上升促进创新的机制非常多，除了本文的“引致创新假说”外，劳动力成本上升也可能通过促进过程创新来降低生产成本、通过产品创新来提升利润率等机制来提升总体创新水平（诸竹君等，2017；Bena et al., 2021），因此劳动力成本上升促进总体创新并不能说明“引致创新假说”必然成立。尽管劳动力成本与总体创新的这些文献也提出“引致创新假说”是可能的机制之一，但是由于缺乏劳动节约型技术创新指标，他们并未严格检验这一机制。本文则利用AI语言模型和专利摘要识别出与劳动力成本密切相关的劳动节约型技术创新，进而专注于验证“引致创新假说”在劳动要素上成立与否。

事实上，各种以专利总量等作为创新指标的文献都普遍无法回答具体什么创新受到了什么样的影响这一问题，这导致我们可能难以触及所探讨的经济现象的核心。例如，如果发现旨在促进芯片技术研发的政策促进了芯片企业专利总量增长，这个结果无法说明政策是否已经实现了目标，因为企业或许是用其他难度更小的非芯片技术来申请专利套取补助。再比如，如果发现新能源汽车补贴政策促进了汽车企业的专利总量，这也不能判断企业是否如政策所愿加强了新能源汽车技术研发，因为企业也有可能是加强燃油汽车技术的研发。所以说，为了更加深入地研究技术创新相关话题，我们有必要去识别和所研究问题密切相关的创新，这样才能得到更加深入和令人信服的结论。

在方法层面，本文发展了一个通用的技术创新识别方法，在技术创新这一核心议题中有较大应用前景。自从技术创新被视为经济长期增长的主要动力后（Romer，1986），它的重要性进一步加强，成为了经济学中最核心领域之一。我国也越发重视创新的作用，将创新列为新发展理念的首要要求和发展的第一动力。之所以要识别不同技术创新，是因为不同的技术创新有不同的作用和影响。例如蒸汽机、电力、AI等通用型基础技术对于经济增长意义重大，劳动节约型、资本增强型等技术在劳动和收入等议题中备受关注，数字技术是数字经济具有效率和质量优势的背后力量，能源

节约型或绿色技术在低碳发展中扮演重要角色，“卡脖子”技术则在保障我国安全发展方面不可或缺。因此，研发投入或专利总量等一般意义上的技术创新指标已经难以满足学术和实践的要求，迫切需要一种通用的方法来识别特定技术创新，为相关研究和政策制定提供便利。已有的较为成功的技术创新识别案例通常要求技术特征与IPC分类号契合，如绿色专利的识别就完全基于IPC分类号（李青原和肖泽华，2020），这个要求阻碍了此方法的广泛使用。本文利用BERT基于专利摘要语义成功识别了劳动节约型专利，这一方法不依赖于技术特征，而是基于语言最本质的特征语义，因而理论上说，只要遵循本文的方法，对于任意技术创新的识别都是可行的。

相对于本文直接识别特定技术创新的做法，也有部分文献采取间接或迂回的方式来测量技术进步或创新，这些方法存在过于依赖模型设定等问题，可能会导致重大偏误。例如，由于劳动节约型技术和技术进步偏向性难以测量，相关研究只能通过先假定技术和劳动力的关系，然后观察劳动力市场的动态来反推这些技术指标（Autor et al., 2003）。如果模型假定或劳动力市场数据等步骤出现问题，那么将可能给核心结论带来严重影响。为了得出更加准确的技术创新相关指标，最直接有效的方法可能就是直接识别特定技术创新。

本文的政策启示在于: 第一, 最低工资制度虽然能提高低收入或低技能劳动力的工资水平, 但是这会促使企业通过研发劳动节约型技术来替代这类劳动力, 有可能造成被动失业。因此, 政府在提高最低工资水平的同时, 应该考虑到引致的偏向型技术变化, 可以通过职业培训等措施提高低工资劳动力的技能水平, 防止他们因为 “高工资” 而被迫失业的问题。第二, 本文发现劳动力成本的上升将有助于我国劳动节约型技术的研发, 结合相关研究发现的廉价劳动力阻碍了英国自动化技术应用这一证据, 本文建议需辩证看待我国劳动成本上升的现象, 应该注意到其在引致我国劳动节约型技术创新方面的作用。

## 二、劳动节约型专利的定义和识别——基于 BERT

## (一)劳动节约型专利的定义和人工识别

本文的难点在于如何识别劳动节约型专利(labor saving patent, LSP)，现行的专利分类体系《国际专利分类表》(international patent classification, IPC) 是按技术主体(如物理、电学等)设立不同类目，而劳动节约型专利的分类是基于专利的功效或者目的，这与 IPC 的分类原则显然不同，所以无法基于 IPC 规则来判断哪些专利为劳动节约型。

专利的摘要中提供了专利功能和目的等相关信息，我们可以基于专利摘要识别劳动节约型专利。但前提是逐一阅读专利摘要文本，识别文本含义。由于专利数以千万计，逐一人工研读识别不具有可行性，这是本领域研究基础数据缺失的根本原因。本文利用最新的人工智能技术突破此困境：首先通过逐一阅读的方式去人工分类一定数量专利，接着利用AI领域先进的BERT语言模型去学习人工分类专利所蕴含的分类规则，最后用学习完分类规则的BERT语言模型去识别所有专利。

根据劳动节约型技术是替代劳动力的技术这一根本定义,我们从直接和间接两个方面对劳动节约型专利进行了定义:

定义 1。专利的目的或者功效是节约劳动力的使用。如果某专利摘要中有“节省或替代劳动力(人力、人工)”等词句，则说明此专利的功能和目的之一就是节约劳动力，这符合劳动节约型技术的直接定义，故将其判定为劳动节约型专利。

定义 2。专利摘要中描述了一种可以(部分)替代劳动力使用的自动化技术或设备。 $ ^{①} $ 假设某

专利的主体可以全自动完成某项任务，或者它可以部分替代人类任务，即便专利摘要中没有明确指出它可以减少劳动力使用，但是从实际效果而言，它还是会对劳动力产生替代效应。从间接意义上来说，它也符合劳动节约型技术的定义，因此我们也将这类判定为劳动节约型专利。事实上，自动化通常被认为是引起技术性失业的“元凶”，正如 Acemoglu & Restrepo（2020）在其论文中开篇所指出的，日益进步的自动化加剧了劳动力将变得多余的担心。

在表 1 中，我们以几个典型例子说明了劳动节约型专利的特征以及人工识别时的注意要点。对于 1 号专利，其虽然没有指出专利的目的在于节约劳动力，但是通过摘要语义，可以知道它描述了一个可以代替人力实现混揉功能的设备，因此符合定义 2。2 号和 3 号专利虽然都出现了“人力”这个词语，但是根据语义，3 号专利中的“人力车”是指用人力驱动的车，和“节约人力”的语义相差甚远，而 2 号专利的“节省人力”才和定义 1 相符，所以只有 2 号专利是劳动节约型专利。4 号专利既指出此专利可以节约劳动力，又表明这是一种可提高生产效率的制作帽子的机器，所以它符合定义 1 和定义 2，也是劳动节约型专利。5 号专利不符合定义 1，但是作为利用人工智能来自动完成计算任务的系统，符合定义 2，故也被认定为劳动节约型专利。6 号专利更是直接指出了本专利可以自动化排除故障，所以符合劳动节约型专利的定义 2。对于 7 号专利，虽然它不像 2 号或者 4 号专利直接表明“减少了人力”，但是它指出本专利解决了人工方式效率不高的问题，言外之意即这个系统更好地取代了人工，所以符合劳动节约型专利的定义 1。

从表 1 中的例子可以看出，1、2、4 号专利替代的主要是重复性的体力劳动，而 5、6、7 号专利则可以完成相对复杂的感知、决策等需要人类大脑功能的任务，这恰恰反映出劳动节约型技术的不断创新使得劳动节约型技术的应用范围越来越广，其对劳动的替代也越来越深化，再一次体现了研究劳动节约型技术创新的重要性。

<div style="text-align: center;"><div style="text-align: center;">表 1</div> </div>


<div style="text-align: center;"><div style="text-align: center;">劳动节约型专利示例</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>编号</td><td style='text-align: center; word-wrap: break-word;'>公开号</td><td style='text-align: center; word-wrap: break-word;'>专利摘要</td><td style='text-align: center; word-wrap: break-word;'>定义1</td><td style='text-align: center; word-wrap: break-word;'>定义2</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>CN201332650Y</td><td style='text-align: center; word-wrap: break-word;'>本实用新型涉及食品机械领域，公开了一种混揉机，……。本实用新型的混揉机在混揉腔内通过两个Z字状的混揉浆以及卸料螺旋杆对经过纤维分离处理的动物皮进行混揉，……，达到尽可能大的混揉效果，……</td><td style='text-align: center; word-wrap: break-word;'>否</td><td style='text-align: center; word-wrap: break-word;'>是</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>CN111376381A</td><td style='text-align: center; word-wrap: break-word;'>一种永磁铁氧体湿式成型用料浆截止阀，旨在解决现有技术中……截止阀的频繁维护更换导致加工过程中装置成本和人力成本大幅增加的技术问题。</td><td style='text-align: center; word-wrap: break-word;'>是</td><td style='text-align: center; word-wrap: break-word;'>否</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>CN2157330Y</td><td style='text-align: center; word-wrap: break-word;'>本实用新型涉及一种兼具锁车功能的充气筒，它用于自行车等人力车的充气和锁车，……，而且使用方便，尤其适用于野外旅游。</td><td style='text-align: center; word-wrap: break-word;'>否</td><td style='text-align: center; word-wrap: break-word;'>否</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>CN201846866U</td><td style='text-align: center; word-wrap: break-word;'>本实用新型涉及一种皮棉帽高效扦衬帽机；……，用本实用新型……，生产效率有很大提高，节省劳动力，降低生产成本，采用本实用新型制作提高了工作效率，适于大批量生产的需要。</td><td style='text-align: center; word-wrap: break-word;'>是</td><td style='text-align: center; word-wrap: break-word;'>是</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>CN102679935A</td><td style='text-align: center; word-wrap: break-word;'>本发明公开了一种计算输电线路覆冰厚度的系统，包括设置于输电线路处的监测设备，……并引进人工智能原理进行学习和推理，实现计算模型不断优化，从而准确计算覆冰厚度。</td><td style='text-align: center; word-wrap: break-word;'>否</td><td style='text-align: center; word-wrap: break-word;'>是</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>CN101178598</td><td style='text-align: center; word-wrap: break-word;'>本发明公开了一种故障安全处理方法、装置及工业自动化控制设备，……。应用本发明提供的故障安全处理方法，能够在工业自动化控制系统故障恢复后向被控制设备输出相对……较小的调整控制值，以实现被控设备的安全正常运行。</td><td style='text-align: center; word-wrap: break-word;'>否</td><td style='text-align: center; word-wrap: break-word;'>是</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">续表 1</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>编号</td><td style='text-align: center; word-wrap: break-word;'>公开号</td><td style='text-align: center; word-wrap: break-word;'>专利摘要</td><td style='text-align: center; word-wrap: break-word;'>定义1</td><td style='text-align: center; word-wrap: break-word;'>定义2</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>CN101916406A</td><td style='text-align: center; word-wrap: break-word;'>本发明公开了一种用于项目资金预算信息管理的系统，……，有效地解决了目前依靠人工方式管理资金预算信息执行效率不高，执行成本较高，缺乏对资金预算信息的实时监控等问题。</td><td style='text-align: center; word-wrap: break-word;'>是</td><td style='text-align: center; word-wrap: break-word;'>是</td></tr></table>

注：省略号处主要是省略结构等方面的描述，不涉及功能和作用。

从上面的人工识别过程可以看出，识别劳动节约型专利时只要求分类者能理解分类规则和语言语义，无需专业知识。然而，对于计算机而言，这个要求却非常高。人工智能领域中自然语言处理（natural language processing，NLP）方向专门研究用计算机处理人类语言，因为自然语言处理难度之大，重要性之高，被公认为人工智能皇冠上的明珠。相较于人工智能中的其他子领域，自然语言处理技术的准确率、产业化发展都有较大落后，也使得经济学研究中文本数据处理的效率和准确度都有待提升（李春涛和冯旭南，2022）。 $ ^{①} $幸运的是，Google公司于2018年底推出的BERT语言模型为各项文本处理任务提供了一个相对完善的工具。

## (二) 基于 BERT 的分类方法

BERT 语言模型是一个将蕴含在语言中语义转化为计算机可以处理的数学向量的模型。计算机界称这一步为“文本表示”或者“文本表征”，这是用计算机处理自然语言的最基础性工作。当前，经济学界常用 word2vec 模型来完成文本表征任务（Imbert et al., 2022）。而后来者 BERT 在表征文本长度、准确度等方面有明显提升：第一，word2vec 只能对词语进行表征，而 BERT 则可以处理专利摘要等长文本。第二，BERT 对于自然语言的理解准确度更高，比如说，BERT 对于某个字词的数学表征会随这个字词在句子中语义的变化而变化，而 word2vec 的数学表征则是固定不变的。在检验语言模型阅读理解水平的权威测试中，BERT 的表现优于人类平均水平和当时的其他语言模型，在 AI 自然语言领域，BERT 已经成为了语言处理任务中的“新范式”（Li et al., 2020）。

BERT 的出现是包括文本分类在内的诸多语言任务的重要转折点。在 BERT 出现之前，基于关键词的统计学分类模型是主流，例如简单贝叶斯模型（naive Bayesian）、TF-IDF 模型等。基于关键词的分类方法的核心思想是同一类别的专利摘要会有相似的词语，并不会考虑文本语义信息。此类模型的优点在于简单、速度快、效果稳定。但是对于中文文本分类而言，其还存在对分词结果敏感、独立性假设不成立、不考虑词义句义这三个主要问题。分词结果敏感问题是指，基于词进行分类时，我们需要对专利摘要进行“分词”，即将一个句子切为一个个词语，但目前的中文分词工具（如 jieba 等）还难做到完全准确切分。比如说，如果将“本专利涉及苹果手机”这个句子切为“本专利”“涉及”“苹果”“手机”，那么有可能这个专利就会被误分类到“水果”类别而不是“手机”类别。独立性假设不成立问题是指这类模型通常需要假设词之间是独立的，但是自然语言的固定搭配和语境等因素决定了词语之间绝非独立。如果说“苹果”和“电磁炉”这两个词之间的独立性假设或许可以成立，但是“苹果”和“手机”这两个词之间肯定不成立，这就违背了简单贝叶斯的独立性假设。不考虑词义句义是这类模型最大的问题，语言的根本目的是为了表达语义，如果不利用语义而是基于统计手段进行分类会出现很大偏差。例如说“人工关节”和“节省人工”中的“人工”语义是截然不同的，如果基于“人工”这个关键词进行分类，那么这两个专利可能会被错误归为一类。

基于 BERT 的分类方法则不会有上述的问题。本文是基于 BERT 给出的专利摘要的整体语义向量进行分类，而不是关键词。因此这一方法无需分词，避免了分词错误和词语独立性假设。而且

基于语义的分类方法对于用词差异、语言变迁、一词多义等问题有更高的稳健性和准确性，和人类根据语言语义进行分类的模式是一致的。例如说“节约人工”和“节省人力”在语义上接近但关键词不同，而“人工关节”和“节省人工”则是关键词“人工”相同但语义不同。只有基于语义，才能解决上述问题。正是得益于上述改进，人工智能领域的众多研究发现，BERT在包含专利文本在内的文本分类任务中显著优于其他模型，准确度有飞跃式的提升（Jin et al., 2020；González-Carvajal & Garrido-Merchán, 2020）。本文方法不仅为如何从（专利）文本中识别特定技术创新提供了思路，也有可以适用于财务文本、新闻文本等文本分类任务。

## (三) 训练和识别——基于 BERT

一般来说, 使用 BERT 模型对专利进行分类的基本步骤可以分为以下三步:

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//412da4fc-a650-48f5-bb01-3a23b25be09d/markdown_1/imgs/img_in_image_box_245_501_943_798.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A56%3A35Z%2F-1%2F%2Fc918462354f94e002d4a711f9cb844dd294a1c744c3a4393601478a7f1837b06" alt="Image" width="58%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 1 使用 BERT 进行专利文本分类任务主要步骤</div> </div>


其中步骤一预训练已经由 Google 公司完成，本文使用 BERT 版本为 Google 发布的中文版本 bert-base-chinese，模型参数为 1.1 亿个。BERT 模型参数巨大的原因有两个，一方面是因为模型本身的深度网络结构使然，另一方面也是为了更好地捕捉和逼近语义。试想三千常用汉字就能带来几乎无穷的语义变化，只有巨额的参数才能尽量去逼近人类语言语义。BERT 在预训练阶段使用的数据为中文维基百科的全部内容，约 120 余万个条目，5.5 亿字。 $ ^{①} $ 中文维基百科包含了大量的工程、技术、自然科学和应用科学方面的内容，无论是在词汇还是句子结构等方面，都很接近专利摘要的语言，这能避免或减轻因为预训练和具体任务中的文本相差过大而可能导致的偏误。本文参考了 Sun et al. (2019) 等研究完成步骤二和步骤三。

步骤二主要包含微调和训练分类器两个任务。对于使用 BERT 进行文本分类的任务而言，微调的主要目的是通过特定语料的学习来提高 BERT 在特定任务上的准确率，但这一步并不是必须的。例如说，在维基百科通用语料上，一氧化碳和二氧化碳的区别可能并不会如化学语料中的大，如果是针对化学语料的文本分类任务，若用化学语料对 BERT 进行微调，增大这两个词之间的区分度，或许可以提高准确度。考虑到 BERT 预训练阶段所用的维基百科语言和专利摘要语言比较接近，加之本文训练集样本量相对于预训练阶段的非常小，本文没有进行微调。

本文在步骤二的工作是利用训练集和测试集训练一个基于 BERT 输出结果进行分类的分类器（又称全连接层），分类器包含一个线性分类层和分类函数。将专利文本输入 BERT 后，BERT 会输出一个代表文本整体语义的向量 c，我们首先使用一个线性分类层来计算输出向量 c 在各类别上的得分 s。接着，利用 softmax 函数来计算专利文本属于某个类别的概率。softmax 函数是归一化指数

函数,它将各类别上的得分 s 转化为概率。对于 0-1 二分类问题,类别为 0 的概率为:

 $$ P\left[ 类别为 0\mid c\right]=softmax(s)=\frac{e^{s_{0}}}{e^{s_{0}}+e^{s_{1}}} $$ 

训练分类器需要人工分类的专利数据。我们从1998—2015年间900余万发明、新型实用专利中随机抽取了5000条。 $ ^{①} $基于前文中劳动节约型专利的定义和人工识别要点，我们将这5000条专利进行了分类。这5000条专利中，再随机抽4000条作为训练集，500条作为开发集，500条作为测试集。训练集的主要作用就是训练分类器的参数，开发集的主要作用是测试模型在不同数据上的正确率和防止过拟合等情况。测试集则用于分析模型在样本外的泛化能力和预测准确率。我们利用训练集和开发集共计4500条标注专利数据来训练上述步骤，就可以获得用于劳动节约型专利分类的分类器。 $ ^{②} $

BERT 模型在本专利分类任务中取得了较为出色的成绩。我们将上述训练和测试步骤重复了10次，得益于 BERT 的准确表征，在训练集中，预测结果达到了近100%的正确率。在开发集和测试集中，预测的正确率在约89%—91%之间波动，这表明 BERT 模型具有非常好稳健性和泛化能力。我们取预测成绩最好的一个训练模型用于后续的专利分类，它在测试集上的“一类错误”概率为8.2%，“二类错误”的概率为9.3%。 $ ^{③} $ 最后一步，用训练好的 BERT 模型对上市公司的所有发明和实用新型专利进行分类。

## (四) 识别效果再检验: 劳动节约型专利能节约劳动力吗?

本节进一步以计量回归的方式检验 BERT 模型识别结果的准确性，发现劳动节约型专利可以“节约”低技能劳动力的使用，而非劳动节约型专利不可以。在上一节我们从技术原理方面说明了为什么 BERT 在专利分类任务中会有较高的准确率，实际结果也表明 BERT 的分类结果和人类一致性高达 90%。但是还存在一个问题：本文所定义和识别的劳动节约型专利究竟有没有节约劳动力的作用？为了回答这一问题，我们使用的模型为：

 $$ \begin{array}{c} employ_{it}=\beta_{0}+\beta_{1}\ln LSP_{it}+\beta_{2}\ln NonLSP_{it}+\Gamma X+\delta_{t}+\gamma_{i}+\mu_{it}\end{array} $$ 

其中，i，t 分别代表企业和年份。employ 为企业所雇佣某类型员工的相关变量，包括低技能员工数量对数（lowlabor）、高技能员工数量对数（highlabor）、员工总量对数（labor）。低技能是指高中学历及以下，高技能是指高中以上学历。lnLSP 和 lnNonLSP 分别为劳动节约型专利（labor saving patent）和非劳动节约型专利数量的对数。TX 为一系列的企业特征和地级市特征，包括企业年龄、规模、杠杆率、资产收益率、营收、劳动力成本、地级市人均 GDP 和人口数量。 $ \delta_{t} $， $ \gamma_{i} $ 分别为时间和企业固定效应，样本为正常经营的非金融类上市公司 2002—2016 年的观察值，变量均来自于 CCER 经济金融数据库，回归结果见表 2。

<div style="text-align: center;"><div style="text-align: center;">表 2</div> </div>


<div style="text-align: center;"><div style="text-align: center;">劳动节约型技术创新与劳动力数量</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2"></td><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>lowlabor</td><td style='text-align: center; word-wrap: break-word;'>highlabor</td><td style='text-align: center; word-wrap: break-word;'>labor</td></tr><tr><td rowspan="2">$ \ln LSP $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.020^{**} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.012^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.004</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.009)</td><td style='text-align: center; word-wrap: break-word;'>(0.007)</td><td style='text-align: center; word-wrap: break-word;'>(0.005)</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">续表2</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2"></td><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>lowlabor</td><td style='text-align: center; word-wrap: break-word;'>highlabor</td><td style='text-align: center; word-wrap: break-word;'>labor</td></tr><tr><td rowspan="2">lnNonLSP</td><td style='text-align: center; word-wrap: break-word;'>0.022 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>0.022 $ ^{***} $</td><td style='text-align: center; word-wrap: break-word;'>0.014 $ ^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.009)</td><td style='text-align: center; word-wrap: break-word;'>(0.007)</td><td style='text-align: center; word-wrap: break-word;'>(0.005)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>企业控制变量</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>市级控制变量</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>企业固定效应</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>年份固定效应</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>观测值</td><td style='text-align: center; word-wrap: break-word;'>21206</td><td style='text-align: center; word-wrap: break-word;'>22340</td><td style='text-align: center; word-wrap: break-word;'>24989</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R $ ^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.364</td><td style='text-align: center; word-wrap: break-word;'>0.547</td><td style='text-align: center; word-wrap: break-word;'>0.580</td></tr></table>

注：括号内为聚类到个体的稳健标准误。 $ ^{***} $、 $ ^{**} $、 $ ^{*} $ 分别表示在 1%、5%、10% 的水平上显著，下表同。

表 2 的回归结果验证了 BERT 模型所识别劳动节约型专利的可靠性。表 2 第（1）列的结果表明，劳动节约型技术会显著减少低技能员工的数量，而非劳动节约型技术则显著增加低技能员工数量。前者显然是替代效应，替代弹性为 -0.02。而后者的原因可能是非劳动节约型技术创新中的产品创新、过程创新会带来产品数量、质量或者生产效率提升，提高企业的产出，进而提高对于低技能员工在内的劳动力需求（Harrison et al., 2014），即需求效应。劳动节约型和非节约型专利的结果表明，我们所识别的劳动节约型专利是基本准确的。

第(2) 列表明劳动节约型技术创新和高技能员工数量之间的正相关，这可能是因为新的劳动节约型技术的出现会刺激高技能员工的需求。例如自动驾驶技术的创新使得企业对于自动驾驶算法、硬件等高技能人才的需求增加。劳动节约型技术创新与高技能员工的正相关对冲了其对低技能员工的替代效应，所以在第(3) 列我们没有观察到劳动节约型技术创新和员工总量之间的显著关系。

上述检验的目的在于验证我们识别的劳动节约型创新度量指标的准确性，表明识别的劳动节约型创新的确与劳动使用具有高度相关性。对于上述结果中可能存在的内生性问题，由于篇幅和主题相关性，本文并未展开论述，在相关的研究中，学者们尝试利用创新的不确定性来尽量减轻内生性问题。原理在于创新的一大天然特性就是能否成功的不确定性，创新能否成功不能由企业完全决定，因此创新成果专利就具有一定偶然性和外生性。对于研发规模较小的企业或难度较大的技术，创新能否成功的不确定性更大，以小型研发企业或发明专利代表这两种情况进行检验，结果保持了稳健。

## 三、基准模型和数据

上文的回归分析表明劳动节约型技术显著减少了企业的低技能劳动力数量，那么我们有理由推测最低工资会影响劳动节约型技术创新。背后的影响机制是，最低工资会带来(低技能)劳动力成本冲击，而劳动节约型技术可以通过替代(低技能)劳动力来减少这一冲击，所以企业会研发劳动节约型技术来应对最低工资上升，这就是“引致创新假说”。

本文利用中国沪深上市公司及专利数据来识别最低工资上涨对于劳动节约型技术创新的影响。样本期限为2002—2016年，上市公司的专利数据、财务数据和员工学历信息等均来自于CCER经济金融数据库，地级市最低工资数据来自于中国研究数据服务平台（CNRDS）。其中员工学历数据经过作者手工整理，得到低技能和高技能员工数量和占比。参考倪骁然和朱玉杰（2016），本文剔除了金融企业和有退市风险警示的企业。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//412da4fc-a650-48f5-bb01-3a23b25be09d/markdown_4/imgs/img_in_chart_box_265_203_918_526.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A56%3A38Z%2F-1%2F%2F451861b221c25178c3d81ce570e20e9f21a308ce3450979921ffa1244fd66242" alt="Image" width="54%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 2 上市公司专利数据情况</div> </div>


图 2 展示了上市公司拥有的劳动节约型专利数据， $ ^{①} $专利总数和劳动节约型专利数量都是随时间增加的。在 2000—2005 年期间因为专利数量较少，所以劳动节约型专利占比波动较大，之后劳动节约型专利占比逐步增加至约 40%。

本文提出以下基准模型来研究最低工资标准的提高对于劳动节约型专利的影响：

 $$ L S P_{_{i j t}}=\beta_{0}+\beta_{1}\ln M W_{_{j t}}+\varGamma X+\delta_{_{t}}+\gamma_{_{i}}+\mu_{_{i j t}} $$ 

其中，i,j,t 分别代表企业、地级市和时间。LSP 为劳动节约型专利的相关变量，包括是否有劳动节约型专利（LSPDummy）、劳动节约型专利数量对数（lnLSP）、劳动节约型专利的占比（LSPRate）、劳动节约型专利质量（LSPQuality）。 $ ^{②} $ 这四个指标分别衡量劳动力成本上升是否会影响具有劳动节约型专利的企业比例（广延边际）、劳动节约型专利的绝对数量（集约边际）、劳动节约型技术创新在企业创新中的占比和劳动节约型专利的价值。lnMW 为地级市最低工资的对数，TX， $ \delta_{t} $， $ \gamma_{t} $ 的含义和本文第二章第四节中模型保持一致，控制了企业、地级市特征和年份、企业固定效应。相关变量描述性统计量见表 3，回归结果见表 4。

<div style="text-align: center;"><div style="text-align: center;">表 3</div> </div>


<div style="text-align: center;"><div style="text-align: center;">主要变量描述性统计</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Variable</td><td style='text-align: center; word-wrap: break-word;'>Definition</td><td style='text-align: center; word-wrap: break-word;'>Obs</td><td style='text-align: center; word-wrap: break-word;'>Mean</td><td style='text-align: center; word-wrap: break-word;'>Std.</td><td style='text-align: center; word-wrap: break-word;'>Min</td><td style='text-align: center; word-wrap: break-word;'>Max</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>LSPDummy</td><td style='text-align: center; word-wrap: break-word;'>是否有劳动节约型专利</td><td style='text-align: center; word-wrap: break-word;'>26,109</td><td style='text-align: center; word-wrap: break-word;'>0.32</td><td style='text-align: center; word-wrap: break-word;'>0.47</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>1.00</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>lnLSP</td><td style='text-align: center; word-wrap: break-word;'>ln(劳动节约型专利 +1)</td><td style='text-align: center; word-wrap: break-word;'>26,109</td><td style='text-align: center; word-wrap: break-word;'>0.63</td><td style='text-align: center; word-wrap: break-word;'>1.13</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>8.52</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>LSPRate</td><td style='text-align: center; word-wrap: break-word;'>劳动节约型专利比例</td><td style='text-align: center; word-wrap: break-word;'>26,109</td><td style='text-align: center; word-wrap: break-word;'>0.18</td><td style='text-align: center; word-wrap: break-word;'>0.31</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>1.00</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>LSPQuality</td><td style='text-align: center; word-wrap: break-word;'>劳动节约型专利质量</td><td style='text-align: center; word-wrap: break-word;'>26,109</td><td style='text-align: center; word-wrap: break-word;'>0.48</td><td style='text-align: center; word-wrap: break-word;'>0.77</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>8.00</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>lnNonLSP</td><td style='text-align: center; word-wrap: break-word;'>ln(非劳动节约型专利 +1)</td><td style='text-align: center; word-wrap: break-word;'>26,109</td><td style='text-align: center; word-wrap: break-word;'>0.77</td><td style='text-align: center; word-wrap: break-word;'>1.20</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>8.39</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>lnMW</td><td style='text-align: center; word-wrap: break-word;'>地级市最低工资对数</td><td style='text-align: center; word-wrap: break-word;'>24,177</td><td style='text-align: center; word-wrap: break-word;'>6.91</td><td style='text-align: center; word-wrap: break-word;'>0.47</td><td style='text-align: center; word-wrap: break-word;'>5.33</td><td style='text-align: center; word-wrap: break-word;'>7.69</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>lowlabor</td><td style='text-align: center; word-wrap: break-word;'>低技能员工数量对数</td><td style='text-align: center; word-wrap: break-word;'>21,636</td><td style='text-align: center; word-wrap: break-word;'>6.84</td><td style='text-align: center; word-wrap: break-word;'>1.64</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>12.64</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>highlabor</td><td style='text-align: center; word-wrap: break-word;'>高技能员工数量对数</td><td style='text-align: center; word-wrap: break-word;'>22,792</td><td style='text-align: center; word-wrap: break-word;'>6.54</td><td style='text-align: center; word-wrap: break-word;'>1.28</td><td style='text-align: center; word-wrap: break-word;'>1.79</td><td style='text-align: center; word-wrap: break-word;'>12.59</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>labor</td><td style='text-align: center; word-wrap: break-word;'>员工数量对数</td><td style='text-align: center; word-wrap: break-word;'>25,484</td><td style='text-align: center; word-wrap: break-word;'>7.54</td><td style='text-align: center; word-wrap: break-word;'>1.32</td><td style='text-align: center; word-wrap: break-word;'>1.95</td><td style='text-align: center; word-wrap: break-word;'>13.22</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 4</div> </div>


<div style="text-align: center;"><div style="text-align: center;">基准模型回归结果</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2"></td><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td><td style='text-align: center; word-wrap: break-word;'>(4)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>LSPDummy</td><td style='text-align: center; word-wrap: break-word;'>lnLSP</td><td style='text-align: center; word-wrap: break-word;'>LSPRate</td><td style='text-align: center; word-wrap: break-word;'>LSPQuality</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>lnMW</td><td style='text-align: center; word-wrap: break-word;'>$ 0.100^{***}(0.035) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.205^{**}(0.089) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.073^{***}(0.023) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.096^{*}(0.058) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>企业控制变量</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>市级控制变量</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>企业固定效应</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>年份固定效应</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>观测值</td><td style='text-align: center; word-wrap: break-word;'>23222</td><td style='text-align: center; word-wrap: break-word;'>23222</td><td style='text-align: center; word-wrap: break-word;'>23222</td><td style='text-align: center; word-wrap: break-word;'>23222</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.049</td><td style='text-align: center; word-wrap: break-word;'>0.099</td><td style='text-align: center; word-wrap: break-word;'>0.024</td><td style='text-align: center; word-wrap: break-word;'>0.030</td></tr></table>

表 4 的结果表明，最低工资水平的上升对于劳动节约型专利的数量、质量和占比都有显著的正面影响。列（1）表明，最低工资促进更多的企业开始进行劳动节约型技术创新，最低工资每上升10%，则企业申请劳动节约型专利的概率会增加1%。列（2）表明，最低工资也会提升企业劳动节约型专利的绝对数量，最低工资每上升10%，则劳动节约型专利的数量会增加2.05%。此外，列（3）表明，最低工资上升还会略微影响企业研发结构：最低工资每上升10%，则劳动节约型专利的占比会增加约0.73%，这意味着劳动节约型研发在企业的研发中占据了更大的比重。列（4）表明，最低工资上升还显著提升了以知识宽度衡量的专利质量。综上可见，最低工资的提高促进了企业研发劳动节约型技术，主要体现在四方面：最低工资上升提高了企业劳动节约型技术创新的可能性、数量、质量以及在总体创新活动中的比重。

## 四、稳健性检验

本节从模型设定和控制变量方面检验了本文结论的稳健性。检验结果表明，使用泊松固定将就模型、Logit固定效应模型和Heckman两阶段模型进行回归可以得出相似的结果。增加研发投入、外商直接投资、进出口作为控制变量后，本文的结论也不受影响。

## (一) 其他估计方法

考虑到专利数量为计数变量，存在严重的偏态和大量的0值，基准模型使用的OLS方法可能存在问题。为了缓解这个问题，本文参考Liu & Qiu（2016），直接以劳动节约型专利数量为因变量，并相应地使用泊松固定效应模型作为回归方法，结果表明最低工资上升对于劳动节约型专利数量有显著正效应。在因变量为是否有劳动节约型专利这一哑变量的回归中，本文以Logit固定效应模型进行回归，结果还是显示最低工资上升提高了企业研发劳动节约型专利的可能性。

劳动节约型专利的研发或许是一个两阶段过程，企业首先考虑要不要研发劳动节约型技术，然后考虑研发的多少。换言之，两个步骤并不是独立的，第二步中劳动节约型专利的数量取决于第一步的概率密度函数，所以专利的正值数据并不是随机产生的。这种可能性会对OLS估计结果产生影响，为此我们使用Heckman两阶段模型来验证估计结果的稳健性。值得说明的是，在第一阶段以企业是否有劳动力节约型专利为因变量的回归中，参考Sanyal & Ghosh（2013）和Liu & Qiu（2016），使用企业前5年度专利累计数量作为排除条件（exclusion restriction）。结果表明企业前5年度的专利数量对于当年是否研发劳动节约型技术有显著促进作用，而且存在选择效应。总的来看，在两阶段模型中，最低工资的上升提高了企业研发劳动力节约型专利的可能性和数量，和基准

结果还是保持一致。 $ ^{①} $

## (二) 更多控制变量

根据已有研究成果，本文尝试加入了企业研发投入、地级市外商直接投资、进口、出口等可能和企业研发行为和最低工资相关的控制变量，结果同样稳健，限于篇幅，结果没有列出。

## 五、内生性检验

为了解决基准模型中潜在内生性问题，本文利用了文献中常用的相邻城市法、工具变量和双重差分等方法，结果基本稳健。其中，相邻城市法植根于美国随机划分州界的历史，而针对中国省界基于山川形便的特点，对相邻城市法进行了一定调整，将样本限定为华北平原的几个省份。本文结论通过了这几种主流方法的检验，确保了因果关系的可靠性。

## (一) 相邻城市法

相邻城市法其思想最早可以追溯到 Card & Krueger(1993)，他们利用美国新泽西州和宾夕法尼亚州这两个相邻州的餐饮企业的雇佣差异来解决最低工资影响的内生性问题，之后 Dube et al. (2008) 将这种做法规范化。这一做法背后的逻辑是，美国最低工资由州确定，州与州边界相邻县的最低工资存在差异，但是由于相邻且州界划分相对随机的缘故，它们在地理、经济等可观察和难以观察因素等方面都更加相似，因此它们互为对照组可以减轻内生性问题。针对我国最低工资的部分研究等也使用了这一策略来解决内生性问题(Fan et al., 2018; Fan et al., 2021; 熊瑞祥等, 2021)。

这种方法有合理之处，然而，将这种方法应用于中国时，不能直接照搬，而要考虑适用性问题，因为中国的省界问题远比美国复杂。美国的州界乃至县界大都为直线（见 Dube et al.（2008）文中的图2），这是因为殖民者给美国这块“新大陆”划分州界时大多简单地依据经纬线，这种方法意味着州界是随机外生的，并没有过于考虑地形、经济或者历史渊源。从整体上来说，州界两边的县具有良好的可比性，它们在各方面更容易相似，更适合作为对照组。

但是中国的省界则是在历史演化中慢慢形成的，尤其受到大山大河等地理条件的影响，省界两边的经济和地理条件等因素可能存在较大差异。例如河北省和山西省的省界是太行山，青海与西藏的分界是唐古拉山，甘肃与青海的界限是祁连山，山西和陕西以黄河为界，四川和西藏、四川和云南部分边界以金沙江为界，贵州和广西部分边界以南盘江为界，江西的省界更几乎全是由山脉和河流组成。可以说，以山川河流为界是中国省级区域划分的最重要特征之一（赵彪等，2021）。这些大山大河一方面往往是重要的地理划分线，例如太行山是黄土高原和华北平原的分界线，两边的地理条件、资源禀赋差异较大。另一方面它们也阻碍了两边的往来，两边也许走向了不同的发展方向。因此，这些边界两边的区域可能并不具备可比性。

为了解决这个问题，本文尝试将样本限制为华北平原的河北、山东、河南、安徽、江苏这些省之间的相邻市。这几个省份的边界主要为平原，没有大山大河的阻碍，因此省界相邻城市的可比性会更好。我们仿照 Dube et al.（2008），首先找出了这几个省份所有相邻城市对，并与基准模型中的面板数据进行合并。接着在基准模型中加入相邻城市对与年份的交互固定效应，用于控制城市对随时间不可观察效应，此时我们是利用城市对内部城市最低工资差异来估计最低工资的影响。由于城市对内部城市的条件更接近，所以内部城市在最低工资之外的难以观察效应趋同，内生性得到大大减轻。以这几个省份的相邻城市对中企业为样本的回归结果见表 5。表 5 显示，当以相邻城市对样本进行回归来减轻可能的内生性问题时，结果保持稳健。

 $$ 相邻城市对样本回归结果 $$ 



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2"></td><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td><td style='text-align: center; word-wrap: break-word;'>(4)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>LSPDummy</td><td style='text-align: center; word-wrap: break-word;'>lnLSP</td><td style='text-align: center; word-wrap: break-word;'>LSPRate</td><td style='text-align: center; word-wrap: break-word;'>LSPQuality</td></tr><tr><td rowspan="2">lnMW</td><td style='text-align: center; word-wrap: break-word;'>0.364 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>0.960 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>0.225 $ ^{***} $</td><td style='text-align: center; word-wrap: break-word;'>0.555 $ ^{**} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.169)</td><td style='text-align: center; word-wrap: break-word;'>(0.420)</td><td style='text-align: center; word-wrap: break-word;'>(0.078)</td><td style='text-align: center; word-wrap: break-word;'>(0.234)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>企业控制变量</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>市级控制变量</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>企业固定效应</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>城市对×年份固定效应</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>观测值</td><td style='text-align: center; word-wrap: break-word;'>3407</td><td style='text-align: center; word-wrap: break-word;'>3407</td><td style='text-align: center; word-wrap: break-word;'>3407</td><td style='text-align: center; word-wrap: break-word;'>3407</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.245</td><td style='text-align: center; word-wrap: break-word;'>0.253</td><td style='text-align: center; word-wrap: break-word;'>0.158</td><td style='text-align: center; word-wrap: break-word;'>0.207</td></tr></table>

注：其余控制变量的信息已省略。由于一个地级市可能和多个他省地级市交界，这会导致这个地级市在地级市对数据库中出现多次。为了控制这种影响，我们借鉴已有文献报告加权回归结果的做法，其中权重为此地级市在地级市对数据库中出现次数的倒数（Fan et al., 2018；熊瑞祥等，2021）。

## (二) 其他内生性检验

本文还采取了工具变量和双重差分等解决最低工资内生性的主流方法来验证因果关系。其中工具变量遵循 Mayneris et al. (2018) 的做法，基于我国最低工资不得低于当地平均工资 40% 的这一规定和巴蒂克法 (Bartik) 思路构造工具变量，这一工具变量的相关性和外生性在赵瑞丽等 (2018)、Du et al. (2022) 等研究中也得到了有效论证，本文使用这一工具变量来解决内生性问题时得到了和基准结果无异的结论。我们也参考 Gan et al. (2016)，利用福建省在 2007 年最低工资标准增加了 8%，而广东省 (除深圳) 不变的差异构建双重差分模型。福建省和广东省是相邻的省份，同为外向型经济，具有一定可比性。双重差分法同样得到了一致的结论。限于篇幅，本文没有列出上述步骤和具体回归结果。

## 六、机制检验

本文从三个角度来检验最低工资通过影响劳动力成本进而促进企业的劳动节约型创新，分别是劳动密集度、低技能员工占比和企业相对工资水平。最低工资的提高对于劳动密集型、低技能员工占比高、工资水平较低的企业或行业的劳动力成本应该有更大的影响。对于劳动密集型企业而言，劳动力成本在生产成本中占比更大。对于低技能员工占比高的企业，低技能员工的工资会更接近最低工资标准，而且低技能员工更容易被劳动节约型技术所替代。对于平均工资较低的企业，受最低工资影响的员工占比可能会更大。因此，最低工资的提高对于上述企业冲击会更大，或者说劳动节约型技术对于上述企业价值更大，它们有更大动力研发更多的劳动节约型技术。这三个机制检验的实证结果表明，劳动密集型、低技能员工占比高和工资水平相对低的企业或行业在最低工资提高后有更加显著的劳动节约型技术创新表现。这些结果验证了最低工资通过提高劳动力成本来促进劳动节约型技术创新的影响机制，提高了本文基准模型结论的可信度。

## (一)劳动密集度

为了识别最低工资上升是否对于劳动密集型企业影响更大，我们加入劳动密集度与最低工资的交互项，具体模型为：

 $$ L S P_{_{i j t}}=\beta_{0}+\beta_{1}\ln M W_{_{j t}}*l a b o r i n t_{_{i j t}}+\beta_{2}l a b o r i n t_{_{i j t}}+\beta_{3}\ln M W_{_{j t}}+\varGamma X+\delta_{_{t}}+\gamma_{_{i}}+\mu_{_{i j t}} $$ 

其中，laborint 为衡量企业劳动密集度的指标，定义为  $ \log(\text{labor}/\text{asset}) $。labor 为企业的员工数

量，asset 为企业总资产。 $ ^{①} $ 显然，指标的数值越大，则代表劳动密集程度越高。表 6 的(1)—(4) 列显示，交互项的系数均显著为正，说明最低工资上升后，劳动密集型的企业申请劳动节约型专利的可能性、数量、质量和占比都要显著更高。

<div style="text-align: center;"><div style="text-align: center;">表 6</div> </div>


<div style="text-align: center;"><div style="text-align: center;">最低工资与劳动节约型技术创新：机制检验</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2"></td><td colspan="4">劳动密集度</td><td colspan="4">低技能占比</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td><td style='text-align: center; word-wrap: break-word;'>(4)</td><td style='text-align: center; word-wrap: break-word;'>(5)</td><td style='text-align: center; word-wrap: break-word;'>(6)</td><td style='text-align: center; word-wrap: break-word;'>(7)</td><td style='text-align: center; word-wrap: break-word;'>(8)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ LSPDummy $</td><td style='text-align: center; word-wrap: break-word;'>$ lnLSP $</td><td style='text-align: center; word-wrap: break-word;'>$ LSPRate $</td><td style='text-align: center; word-wrap: break-word;'>$ LSPQuality $</td><td style='text-align: center; word-wrap: break-word;'>$ LSPDummy $</td><td style='text-align: center; word-wrap: break-word;'>$ lnLSP $</td><td style='text-align: center; word-wrap: break-word;'>$ LSPRate $</td><td style='text-align: center; word-wrap: break-word;'>$ LSPQuality $</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ lnMW* laborint $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.045^{***}(0.008) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.121^{***}(0.023) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.025^{***}(0.005) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.065^{***}(0.013) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ lnMW* lowrate $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ 0.228^{***}(0.060) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.496^{***}(0.151) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.0550(0.050) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.496^{***}(0.098) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>企业控制变量</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>市级控制变量</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>企业固定效应</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>年份固定效应</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td><td style='text-align: center; word-wrap: break-word;'>✓</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>观测值</td><td style='text-align: center; word-wrap: break-word;'>23222</td><td style='text-align: center; word-wrap: break-word;'>23222</td><td style='text-align: center; word-wrap: break-word;'>23222</td><td style='text-align: center; word-wrap: break-word;'>23222</td><td style='text-align: center; word-wrap: break-word;'>23207</td><td style='text-align: center; word-wrap: break-word;'>23207</td><td style='text-align: center; word-wrap: break-word;'>23207</td><td style='text-align: center; word-wrap: break-word;'>23207</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.053</td><td style='text-align: center; word-wrap: break-word;'>0.105</td><td style='text-align: center; word-wrap: break-word;'>0.026</td><td style='text-align: center; word-wrap: break-word;'>0.032</td><td style='text-align: center; word-wrap: break-word;'>0.051</td><td style='text-align: center; word-wrap: break-word;'>0.101</td><td style='text-align: center; word-wrap: break-word;'>0.024</td><td style='text-align: center; word-wrap: break-word;'>0.032</td></tr></table>

注：其余控制变量的信息已省略。

## (二) 低技能劳动力占比

类似地，本文加入证监会二级行业的低技能员工占比与最低工资的交互项来验证最低工资是否对低技能员工占比高的行业有更大的促进作用。之所以使用行业层面的低技能员工占比，是因为在上文中发现劳动节约型技术创新会影响企业的低技能和高技能员工的数量，进而影响低技能员工占比，如果使用企业层面的低技能员工占比指标会引入内生性问题。而行业层面的指标反映的是行业特征，相对外生。其中行业的低技能员工占比是此行业中企业低技能员工占比的中值。回归结果为表6中的(5)—(8)列，除第(7)列之外交互项的系数都显著为正数，总体上说明了低技能劳动力占比高的行业中的企业在最低工资上升后同样有更明显的劳动节约型技术创新。

## (三) 最低工资与企业平均工资比率

本文使用最低工资和企业平均工资的比率(WageGap)替代最低工资变量，作为另一个衡量劳动力成本冲击的度量。根据WageGap的定义可知，WageGap越大，意味着最低工资和企业平均工资之间的差值越小，则最低工资带来的冲击可能越大，我们会预期WageGap对企业进行劳动节约型技术创新的概率、强度、占比和质量都有显著正面影响，回归结果支持了这一预期，囿于篇幅，具体结果没有列出。

## 七、结论与启示

本文结合 AI 领域前沿的 BERT 语言模型和专利摘要识别出劳动节约型专利。BERT 模型能较为准确地将语言语义转为数学向量，我们用它获得了专利摘要语义的数学表示用于识别劳动节约型专利。经过测试，BERT 模型的分类结果和人类的一致性高达 90%。我们还发现劳动节约型专利会显著减少低技能劳动力，而非劳动节约型专利则不会，这从另一角度说明了本文的识别是准确的。

基于 2002—2016 年间上市公司专利和地级市的匹配数据，本文发现最低工资上升显著提高了企业进行劳动节约型技术创新的概率、数量、质量和占比，此效应在劳动力密集型、低技能劳动力占比高和相对工资较低的企业或行业中更加显著。这些结果支持了劳动要素角度的“引致创新假说”，即生产要素价格的相对变化会影响技术创新的方向，某要素价格上升促进企业研发能降低此要素使用强度的创新。

本文的研究对于理解我国在人口红利消失、老龄化加剧、劳动力成本快速上升阶段的技术进步偏向性有重要启示。第一，来自上市公司企业层面的证据表明，劳动节约型技术在“节约”低技能劳动力的同时会伴随更多的高技能劳动力就业，所以劳动节约型技术对于总体就业没有显著影响。因此，我们不能只聚焦于劳动节约型技术创新减少就业的负面效应，更应该看到其在增加高技能就业和提升就业结构方面的作用。第二，本文发现最低工资代表的劳动力成本冲击会通过“引致创新”途径刺激劳动节约型技术的研发，而刘青和肖柏高（2022a）发现廉价劳动力会阻碍英国的自动化技术应用，综合这两个发现可以得出这样的结论：我国劳动力成本的日益上升或许并不是坏事，它反而会“引致”企业通过技术创新来实现生产的自动化、智能化。所以我国无需过度担忧，甚至人为干预我国劳动力成本的上升，应该将主要精力放于鼓励企业技术创新。第三，最低工资制度虽然能提高低收入或低技能劳动力的工资水平，但是企业会通过研发劳动节约型技术来替代这类劳动力，进而造成失业。因此，政府在提高最低工资水平的同时，应该考虑到引致的偏向性技术变化，可以通过职业培训等措施提高低工资劳动力的技能水平，防止他们因为“高工资”而被迫失业的问题。

## 参考文献

黄先海、徐圣，2009《中国劳动收入比重下降成因分析——基于劳动节约型技术进步的视角》，《经济研究》第7期。

李建强、高翔、赵西亮，2020《最低工资与企业创新》，《金融研究》第12期。

李青原、肖泽华，2020《异质性环境规制工具与企业绿色创新激励——来自上市企业绿色专利的证据》，《经济研究》第9期。

林炜，2013《企业创新激励：来自中国劳动力成本上升的解释》，《管理世界》第10期。

刘媛媛、刘斌，2014《劳动保护、成本粘性与企业应对》，《经济研究》第5期。

倪骁然、朱玉杰，2016《劳动保护、劳动密集度与企业创新——来自2008年《劳动合同法》实施的证据》，《管理世界》第7期。

王文春、殷华宫、汝凯，2022《最低工资标准提高对企业资本劳动比的影响研究》，《金融研究》第1期。

王永钦、董雯，2020《机器人的兴起如何影响中国劳动力市场？——来自制造业上市公司的证据》，《经济研究》第10期。

熊瑞祥、万倩、梁文泉，2021《外资企业的退出市场行为——经济发展还是劳动力市场价格管制》，《经济学(季刊)》第4期。张杰、郑文平，2018《创新追赶战略抑制了中国专利质量么》，《经济研究》第5期。

赵彪、王开泳、王甫园、刘海猛，2021《中国县级以上行政边界的特征及其变动趋势》，《地理研究》第9期。

赵瑞丽、孙楚仁、陈勇兵，2018《最低工资与企业价格加成》，《世界经济》第2期。

诸竹君、黄先海、宋学印、胡馨月、王煌，2017《劳动力成本上升、倒逼式创新与中国企业加成率动态》，《世界经济》第8期。

Acemoglu, D., 2010, "When Does Labor Scarcity Encourage Innovation?", Journal of Political Economy, 118(6), 1037—1078.

Acemoglu, D., and P. Restrepo, 2018, "Artificial Intelligence, Automation and Work", National Bureau of Economic Research Working Paper Series, No. 24196.

Acemoglu, D., and P. Restrepo, 2020, "Robots and Jobs: Evidence from Us Labor Markets", Journal of Political Economy, 128(6), 2188–2244.

Acemoglu, D., and P. Restrepo, 2022, "Demographics and Automation", Review of Economic Studies, 89(1), 1–44.

Acharya, V. V., R. Baghai-Wadji, and K. V. Subramanian, 2009, "Labor Laws and Innovation", Journal of Law and Economics, 56(4).

Acharya, V. V., R. P. Baghai, and K. V. Subramanian, 2014, "Wrongful Discharge Laws and Innovation", Review of Financial Studies, 27(1), 301–346.

Autor, D. H., F. Levy, and R. J. Murnane, 2003, "The Skill Content of Recent Technological Change: An Empirical Exploration", Quarterly Journal of Economics, 118(4), 1279–1333.

Bena, J., H. Ortiz-Molina, and E. Simintzi, 2022, "Shielding Firm Value: Employment Protection and Process Innovation", Journal of Financial Economics, 146(2), 637–664.

Card, D., and A. Krueger, 1993, "Minimum Wages and Employment: A Case Study of the Fast Food Industry in New Jersey and Pennsylvania", American Economic Review, 84.

Du, P., Y. Zheng, and S. Wang, 2022, "The Minimum Wage and the Financialization of Firms: Evidence from China", China Economic Review, 76, 101870.

Dube, A., T. Lester, and M. Reich, 2008, “Minimum Wage Effects Across State Borders: Estimates Using Contiguous Counties”, Institute of Industrial Relations, Uc Berkeley, Institute for Research On Labor and Employment, Working Paper Series, 92.

Fan, H., F. Lin, and L. Tang, 2018, "Minimum Wage and Outward FDI from China", Journal of Development Economics, 135, 1—19.

Fan, H., Y. Hu, and L. Tang, 2021, "Labor Costs and the Adoption of Robots in China", Journal of Economic Behavior & Organization, 186, 608–631.

Gan, L., M. A. Hernandez, and S. Ma, 2016, "The Higher Costs of Doing Business in China: Minimum Wages and Firms' Export Behavior", Journal of International Economics, 100, 81–94.

González-Carvajal, S., and E. C. Garrido-Merchán, 2020, "Comparing BERT Against Traditional Machine Learning Text Classification", Arxiv E-Prints, 2005. 13012.

Harrison, R., J. Jaumandreu, J. Mairesse, and B. Peters, 2014, "Does Innovation Stimulate Employment? A Firm-Level Analysis Using Comparable Micro-Data from Four European Countries", International Journal of Industrial Organization, 35, 29–43.

Hicks, J. R., 1932, "The Theory of Wages", American Journal of Sociology, 32(125).

Imbert, C., M. Seror, Y. Zhang, and Y. Zylberberg, 2022, "Migrants and Firms: Evidence from China", American Economic Review, 112(6), 1885–1914.

Irmen, A., 2017, “Capital-And Labor-Saving Technical Change in an Ageing Economy”, International Economic Review, 58(1), 261–285.

Jin, D., Z. Jin, J. T. Zhou, and P. Szolovits, 2020, "Is Bert Really Robust? A Strong Baseline for Natural Language Attack on Text Classification and Entailment", Proceedings of the Aaai Conference On Artificial Intelligence, 34(05), 8018–8025.

Karabarbounis, L., and B. Neiman, 2014, “The Global Decline of the Labor Share”, Quarterly Journal of Economics, 129(1), 61–103.

Krueger, A., 1993, "How Computers Have Changed the Wage Structure: Evidence from Microdata, 1984—1989", Quarterly Journal of Economics, 108(1), 33—60.

Krusell, P., L. E. Ohanian, J. Ríos-Rull, and G. L. Violante, 2000, "Capital-Skill Complementarity and Inequality: A Macroeconomic Analysis", Econometrica, 68(5), 1029–1053.

Li, J., Y. Shan, G. Tian, and X. Hao, 2020, "Labor Cost, Government Intervention, and Corporate Innovation: Evidence from China", Journal of Corporate Finance, 64, 101668.

Li, Q., H. Peng, J. Li, C. Xia, R. Yang, L. Sun, P. S. Yu, and L. He, 2020, "A Survey on Text Classification: from Shallow to Deep Learning", Arxiv E-Prints, 2008. 2364.

Liu, Q., and L. D. Qiu, 2016, "Intermediate Input Imports and Innovations: Evidence from Chinese Firms' Patent Filings", Journal of International Economics, 103, 166–183.

Mayneris, F., S. Poncet, and T. Zhang, 2018, "Improving Or Disappearing: Firm-Level Adjustments to Minimum Wages in China", Journal of Development Economics, 135, 20—42.

Romer, P. M., 1986, "Increasing Returns and Long-Run Growth", Journal of Political Economy, 94(5), 1002–1037.

Sanyal, P., and S. Ghosh, 2013, "Product Market Competition and Upstream Innovation: Evidence from the U.S. Electricity Market Deregulation", Review of Economics and Statistics, 95(1), 237–254.

Sun, C., X. Qiu, Y. Xu, and X. Huang, 2019, "How to Fine-Tune Bert for Text Classification?", Arxiv E-Prints, 1905. 5583. Zeira, J., 1998, "Workers, Machines, and Economic Growth", Quarterly Journal of Economics, 113(4), 1091–1117.

# Labor Costs and Labor-saving innovation: Evidence from AI Language Model and Patent Texts

LIU Qing $ ^{a} $ and XIAO Baigao $ ^{a} $

(Renmin University of China)

Summary: From the steam engine that replaces physical strength to the AI that replaces brain power, the innovation and application of revolutionary labor-saving technologies have profoundly changed the world's economic development and become the focus of academic research. However, after reviewing previous literature, it is found that the existing research on labor-saving technology mainly focuses on its application or introduction, such as the adoption or installation of computer or robot, and pays little attention to its innovation.

The lack of good labor-saving technology innovation indicators may be one of the reasons. Given such situation, this paper for the first time identifies labor-saving technology innovation by combining the cutting-edge BERT language model in the AI field with patent abstracts. The out-of-sample classification results of the BERT model are 90% consistent with human results. The regression results also show that labor-saving technology innovations identified by BERT significantly reduce low-skilled employees, while non-labor-saving technology innovations do not. These results indicate that the classification results are accurate.

Considering that China is haunted by intensified population aging, a rapid rise in labor costs, and the hindered introduction of labor-saving cutting-edge technologies, this paper examines how rising labor costs affect the indigenous innovation of labor-saving technology in Chinese companies. Based on the data of listed companies, this paper finds that rising labor costs have significantly enhanced the probability, quantity, proportion, and quality of labor-saving technology innovation, which implies that rising labor costs disrupt the bias of technological progress and push enterprises to use technology to replace expensive labor. Further analysis shows that this effect is more significant in firms with higher labor intensity, higher proportion of low-skilled labor and lower average wages.

When addressing possible endogeneity problems, we employed the sample of contiguous city pairs across provincial borders following studies in the US, but we considered the characteristics of Chinese provincial borders. Most of the state borders in the United States were randomly delimitated. Many state borders are straight lines based on latitude and longitude, and economic and geographical differences on either sides of the border are not taken into account. China's provincial borders were formed over a long period of historical evolution, considering geographical or economic features. For example, quite a few provincial borders in China are bounded by mountains and rivers. To address this issue, we limit our sample to a few provincial-level regions in the North China Plain.

The method to identify specific technology innovation proposed in this paper is general, and has great application prospects in the research fields related to technological innovation. Technological innovation is regarded as the main driving force of long-term economic growth and is one of the core areas of economics research. The reason for identifying specific technological innovations is that different technological innovations have different effects and impacts on the economy. For example, general-purpose technologies such as steam engines, electricity, and AI are of great significance to economic growth. Labor-saving and capital-enhancing technologies have attracted much attention in issues such as labor and income. Energy-saving or green technologies play an important role in low-carbon development. General innovation indicators such as the total number of patents or R&D investment can hardly meet the requirements of in-depth research. This paper uses BERT to successfully identify labor-saving patents based on patent abstract semantics, the most essential feature of language, rather than on technical features. Therefore, following our method, it is possible to identify any technological innovation.

Keywords: Labor-saving Technology; BERT Model; Labor Costs; Minimum Wage

JEL Classification: J30, J21, O31

(责任编辑：冀木)(校对：王红梅)

