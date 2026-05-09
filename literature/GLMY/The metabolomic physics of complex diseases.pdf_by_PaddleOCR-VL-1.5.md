# The metabolomic physics of complex diseases

Shuang Wu $ ^{a} $, Xiang Liu $ ^{b,c} $, Ang Dong $ ^{a} $, Claudia Gragnoli $ ^{d,e,f} $, Christopher Griffin $ ^{g} $ $ ^{ID} $, Jie Wu $ ^{c} $, Shing-Tung Yau $ ^{c,h,1} $ $ ^{ID} $, and Rongling Wu $ ^{c,h,1} $

Contributed by Shing-Tung Yau; received May 21, 2023; accepted August 15, 2023; reviewed by Yuehua Cui and Jun Tanimoto

Human diseases involve metabolic alterations. Metabolomic profiles have served as a vital biomarker for the early identification of high-risk individuals and disease prevention. However, current approaches can only characterize individual key metabolites, without taking into account the reality that complex diseases are multifactorial, dynamic, heterogeneous, and interdependent. Here, we leverage a statistical physics model to combine all metabolites into bidirectional, signed, and weighted interaction networks and trace how the flow of information from one metabolite to the next causes changes in health state. Viewing a disease outcome as the consequence of complex interactions among its interconnected components (metabolites), we integrate concepts from ecosystem theory and evolutionary game theory to model how the health state-dependent alteration of a metabolite is shaped by its intrinsic properties and through extrinsic influences from its conspecifics. We code intrinsic contributions as nodes and extrinsic contributions as edges into quantitative networks and implement GLMY homology theory to analyze and interpret the topological change of health state from symbiosis to dysbiosis and vice versa. The application of this model to real data allows us to identify several hub metabolites and their interaction webs, which play a part in the formation of inflammatory bowel diseases. The findings by our model could provide important information on drug design to treat these diseases and beyond.

metabolic interaction | evolutionary game theory | allometric scaling law | quasi-dynamic ordinary differential equations | idopNetwork

Human health and diseases are very complex, involving an extremely large number of known or unknown factors. While several previous studies have attempted to identify transcriptomic and proteomic predictors of complex diseases (1, 2), a growing body of evidence shows that the blood metabolome contains much-unexplored information that is associated with a broad array of disease phenotypes, including cardiovascular disease risk (3), risk of myocardial infarction and stroke (4), breast cancer (5), risk of incident dementia and Alzheimer's disease (6), and their ensuing comorbidities (7). The use of human metabolites as a clinical predictor of the physiological state in humans has been further stimulated by advanced high-throughput techniques that can identify a massive amount of metabolites in the blood simultaneously at comparatively low cost (8).

Current approaches mostly focus on the identification of individual significant metabolites associated with diseases through statistical testing, but given that most diseases are multifactorial, dynamic, and context-specific (9, 10), these approaches are not able to chart a comprehensive landscape of metabolic function. Because metabolites coexist and work together in cells, it is likely that they form a complex system to contribute to physiological and biochemical variation in human health and disease. Network models have proven to be powerful for characterizing the internal workings of complex systems by visualizing how different constituent components interact with each other to mediate system behavior (11–13).

There has been a rich wealth of literature on the application of biomedical networks to disease etiology (14–17), but these networks only characterize the cooccurrence of multiple entities rather than their bidirectional, signed, and weighted (bDSW) interactions. From these networks, one cannot distinguish whether the contribution of individual entities is due to their own intrinsic capacity or the influence of other entities on them. In addition, existing network models can only reconstruct an aggregated network from a large number of samples, failing to identify sample- and context-specific changes in the network architecture. All these issues can be overcome by cross-pollinating ecosystem theory and evolutionary game theory with graph theory under a statistical physics framework (13, 18–20). The use of evolutionary game theory and networks has been considered in the broader literature [see an excellent overview by Tanimoto (21–23)]. Our work is distinct in that the data we use is rich in volume, but not in sampling rate. Consequently, our framework is expressed as a quasidynamic Lokta–Volterra (predator–prey) ordinary differential equation (qdLVODE) that decomposes the abundance of an entity into its independent and

### Significance

Complex diseases are characterized by enormous metabolic alterations. Network-based approaches can systematically characterize the interconnections of different metabolites. While available approaches can only reconstruct aggregated cooccurrence networks from a number of samples, we formulate a statistical physics model that can capture bidirectional, signed, and weighted interactions into informative, dynamic, omnidirectional, and personalized networks. The model can capitalize on any metabolomic data from any level of organization. We implement GLMY homology theory to dissect the topological alterations of metabolic networks associated with health state changes from symbiosis to dysbiosis and vice versa. The utility of our model to analyze metabolic data on inflammatory bowel diseases demonstrates its biological and statistical value in disentangling a broader scope of disease scenarios.

dependent components (19). By coding the independent components of each entity as nodes and the dependent components of each entity-entity pair as edges into graphs, qdLVODE can fully capture the full set of emergent properties of interactions and reconstruct informative, dynamic, omnidirectional, and personalized networks (idopNetworks) inferred from any data domain. However, the application of idopNetworks to understanding the metabolic mechanisms of diseases has not yet been reported in the literature.

In this study, distinct from their previous applications, we leverage idopNetworks by implementing GLMY homology theory to analyze their topological architecture. Originally proposed by Grigor'yan, Lin, Muranov and Yau (24), GLMY homology is a mathematical approach for the topological analysis of directed networks. Recently, this approach has been extensively expanded for widespread applications by these and other authors (25–30). The GLMY-leveraged model can visualize and compare how the topological information of idopNetworks varies along spatio-temporal gradients. We test and validate this model by analyzing metabolic data for inflammatory bowel disease (IBD)—a chronic immune-mediated disease that affects the gastrointestinal tract (31–33). Despite its high prevalence, the etiology of IBD remains elusive. This disease includes two types, Crohn's disease (CD) and ulcerative colitis (UC). While CD is a segmental, transmural disease that can occur in any part of the gastrointestinal tract, UC infects the mucosal and submucosal layers of the rectum, moving up to the colon (34). As a recent focus of medical research, we still know little about the physiological mechanisms underlying the difference and commonality between CD and UC (33, 35). Since most diseases involve metabolic alternations, an increasing number of studies have begun to use individual metabolites as clinical predictors for disease (3–7). By extracting and analyzing systemic information from high-dimensional metabolomics profiles, our model gains unique insight into the metabolic physiology of CD and UC and can be generally used to dissect other diseases from any biological entities.

## Results

Model Construct. The metabolic basis of a complex disease involves not only the diversity and function of individual metabolites but also how different metabolites interact with each other in a linear manner. Each subject contains a multitude of metabolites, the change of whose interaction pattern causes his/her current health state to shift to a different state. We view each subject at a time point as an ecosystem and calculate and define the total abundance value of all metabolites as its ecosystem niche, a parameter reflecting the “production” of this ecosystem, similar to the concept of environmental index in ecoagriculture (36). Subjects are discrete, but they can be serialized by the ecosystem niche in order from small to large. The abundance level of each metabolite can be expressed as a function of ecosystem niche. This function obeys the allometric scaling law of the part-whole relationship, which can be described by a power equation. The notion of ecosystem niche helps to extract dynamic information from static points.

The process of metabolite–metabolite interactions can be interpreted through lens of game theory (37); i.e., every metabolite strives to maximize its fitness (payoff) by developing an optimal strategy based on its intrinsic capacity in response to the strategies of its coexisting metabolites. Such an attempt at fitness maximization proceeds until a Nash equilibrium is reached, where the fitness of a metabolite cannot be improved further by only changing its own strategy (38). By combining game theory and evolutionary theory, Maynard Smith and Price (39) proposed the notion of the evolutionarily stable strategies (ESS) as an equilibrium refinement to the Nash equilibrium. ESS assumes that the entities' strategies are biologically encoded and heritable, without needing to know the strategies of any metabolites (species), as required by a Nash equilibrium. The dynamic generalization of evolutionary game theory through predator–prey equations (40), guided by allometric scaling law (41, 42), allows us to derive a system of quasidynamic Lokta–Volterra ordinary differential equations (qdLVODEs) that decomposes the fitness of each metabolite into its independent component (due to its own capacity) and dependent component (due to the influence on this metabolite by other metabolites) (13, 18, 20, 43). We code the independent components of each metabolite as nodes and the dependent components of each metabolite pair as edges into idopNetworks (Methods).

Two-Layer Metabolic Networks as a Predictor of Disease Risk. In the ongoing Integrative Human Microbiome Project (31–33), stool metabolites were measured in diseased patients and healthy controls (HC) in a range of ages from childhood to late adulthood. By viewing all metabolites measured in a sample that constitute an ecosystem, we analyze and interpret how human metabolic networks are associated with two types of IBD—CD and UC. The abundance levels of individual metabolites against ecosystem niches can be well fitted by the power law, with the shape of the fitting curves depending on the metabolite and health state (SI Appendix, Fig. S1). This implies that the ecosystem niche-varying pattern of metabolites can roughly serve as a predictor of distinguishing healthy status from IBD status.

We implement a functional clustering algorithm to classify all metabolites into different modules (M1 to M9) over healthy, CD, and UC groups (SI Appendix, Fig. S2). We reconstruct coarse-grained networks using total abundance levels of all metabolites from each module and fine-grained networks using the abundance levels of each metabolite within the same module, forming a two-layer metabolic bDSW network for each group (Fig. 1A). We find that coarse-grained networks are similar in structure among the three groups (i.e., there is a hub module that links with other modules in a radiating manner), but they exhibit group-specific organizational patterns. In the healthy group, M8 is a hub that influences the eight other modules, although the strength, sign, and pattern of influence depend on the influenced modules. It is interesting to find that the hub in the IBD group is changed to M3, which acts like M8 in the healthy network. Although CD and UC networks share some commonality in network topology, e.g., M3 promoting M1, M4, and M5, they differ in many ways, including M3 to M9 amensalism in the CD network vs. M3 to M9 commensalism in the UC network and M3 to M7 predation in the CD network vs. M3 to M7 amensalism in the UC network. Fig. 1C illustrates the detailed picture of how the total abundance level of each module is influenced by (passive), or influences (active), the abundance of other modules for the three groups. It can be seen that the pattern of passive and active influences differ dramatically among modules, depending on the health state.

We find that the overall architecture of fine-grained networks displays a higher similarity between the CD and UC groups than between IBD and healthy groups, implying that the determinants of network differences can serve as a predictor of gastrointestinal health state. M8 is the hub module for the healthy coarse-grained network, composed of five metabolites, of which 3-hydroxyoctanoate is a hub of the M8 fine-grained healthy network that establishes a bidirectional link to all four other metabolites. However, the number of its incoming links reduces to two when the healthy status

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e06db948-229a-490a-8941-f79b03f25c57/markdown_2/imgs/img_in_image_box_96_70_1073_789.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-10T09%3A45%3A12Z%2F-1%2F%2Fc7e5777e809fc252e4f7926fd4233f400048d31f54cdeb89db6db1b9a0268c89" alt="Image" width="83%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e06db948-229a-490a-8941-f79b03f25c57/markdown_2/imgs/img_in_chart_box_629_72_1073_791.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-10T09%3A45%3A12Z%2F-1%2F%2F28a181c79339c430612e22e7799defd89cca33a2351f8c8b64d06de533ba17d7" alt="Image" width="37%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 1. Context-specific metabolic networks reconstructed from 185 metabolites. (A) All metabolites are coalesced into two-layer idopNetworks, at the top of which is the coarse-grained network at the module level (M1 to M9) and the bottom of which is the fine-grained network at the metabolite level (with the names of individual metabolites shown), for HC, CD, and UC groups. Red and blue lines represent promotion and inhibition, respectively, with the thickness of lines proportional to the strength of interaction. (B) Homological analysis of coarse-grained networks at different dimensions based on positive and negative links. (C) Net total metabolic abundance curves of each module (blue line) decomposed into independent component curves resulting from intrinsic capacity (red line) and dependent component curves due to regulation by other modules (green line).</div> </div>


changes to the UC status (SI Appendix, Table S1), suggesting that the role of 3-hydroxyoctanoate as a hub declines in a diseased subject. If the healthy status of the subject changes to CD, the hub is shifted from 3-hydroxyoctanoate to indoleacetate. We can also find between-group topological similarities and differences in fine-grained networks of the other modules (SI Appendix, Table S1). Taken together, the fine-grained bDWS network can be used as not only a predictor of health risk but also a tool to understand the metabolic mechanisms mediating comorbidity.

Age Trends of Metabolic Networks. As a natural phenomenon, aging is a continuous decline in physical and metabolic functions, strongly associated with increased susceptibility to disease (44, 45). Using samples from different age intervals, we reconstruct the metabolic bDSW networks of subjects roughly aged <18, 20 to 40, 40 to 60, and >60 y for three groups (Fig. 2A). Interaction relationships in coarse-grained networks are stable over age for the HC group but display dramatic changes for the CD group. A few interactions change as a function of age for the UC group; e.g., promotion of M5 by M3 increases in strength from ages 18 to 60, but this promotion is shifted to inhibition of M5 by M3 when ages are greater than 60 y. These findings suggest that the response of metabolic networks to aging follows different mechanisms between healthy and IBD populations and between CD and UC populations.

We find that the independent component of M9 (reflecting its intrinsic capacity) increases substantially with age for both healthy and diseased populations, implying that increasing intrinsic expression of M9 is a signal of aging in metabolic function. Yet, the pattern with which M9 is influenced by other modules varies among the three groups. In the HC group, M9 is always promoted only by hub M8, whereas it is always inhibited by hub M3 and also promoted by M6 in the CD group. In the UC group, M9 is only promoted by M3 before 60 y of age, which changes to inhibition after age 60. Different from star-graph-like HC and UC networks, the CD networks have a secondary hub M6, in addition to the primary hub M3.

We further reconstruct age-specific fine-grained metabolic networks among individual metabolites from each module (SI Appendix, Figs. S3 and S4). We find that the interaction topology of these networks changes over age, with the pattern of change depending on health state. Taken together, the HC group appears to be different from the IBD group in terms of network organization, such as the type of hubs, and the two types of IBD can be distinguished from each other via the perspective of network structure. Network organization and structure are more stable over age for the healthy

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e06db948-229a-490a-8941-f79b03f25c57/markdown_3/imgs/img_in_image_box_247_74_927_1090.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-10T09%3A45%3A13Z%2F-1%2F%2Ff8193290cdaff715738af09170f00579dc18ad091b4e3249eecd70f53cc3086e" alt="Image" width="58%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 2. Age-varying change of metabolic networks by considering four age stages (<18, 18 to 40, 40 to 60, and >60 y). (A) Coarse-grained networks at the module level for HC, CD, and UC groups. Red and blue lines represent promotion and inhibition, respectively, with the thickness of lines proportional to the strength of interaction. (B) Homological analysis of coarse-grained networks at different dimensions based on positive and negative links.</div> </div>


group than for the diseased group. The hub modules identified from one health state change their network topology when this state is shifted to the other state, also displaying a remarkable age-specific alteration.

GLMY Homology of Metabolic Networks. We introduce GLMY homology theory to chart the flow of information initiated from a metabolite within each metabolic network at both module and metabolite levels. We estimate the rank of the GLMY homology at dimension zero, one, and two for a given directed network. For the coarse-grained networks, M2 and M8 contain a loop in dimension one (giving a first Bettin number  $ \beta_1 $ of 1) in the healthy group, whereas this topological feature disappears when the health state changes to an IBD state (Fig. 1B). In the CD group, (M3, M7) and (M6, M8) have two one-dimensional loops (giving a first Bettin number of 2). Although no nontrivial rank one-homology group is observed for the UC group, this group produces a nontrivial dimension two homology group, leading to nonzero second Bettin numbers  $ \beta_2 $ with M3, M6, M7, and M8. It can be seen that the topological change of the coarse-grained networks is numerical from the healthy to CD state but structural from the healthy to UC state. This difference shows topological variability between CD and UC groups.

We further dissect how the topology of the coarse-grained networks changes over age (Fig. 2B). The HC network is stable in

topological structure over age; nine subnetworks at dimension 0, one loop at dimension 1, and no void at dimension 2 are consistently observed. There is no difference in the zero-dimensional homology between the IBD and healthy groups, but they differ in their one- and two-dimensional homology groups. In the CD group, there are two loops at dimension 1 in age <18 y, and this number increases to three at 20 to 40 y, then decreases to two at 40 to 60 y, and again increases to three after 60 y, showing the susceptibility of network topology to aging. However, the UC group displays a different aging-specific pattern; while most ages have a nontrivial one-dimensional homology group (non-zero  $ \beta_1 $), a nontrivial two-dimensional homology group is observed at 20 to 40 y.

Fig. 3 illustrates health state-specific differences in the persistent GLMY homology derived from the descending order of positive and negative links for the fine-grained networks of hubs modules M3 (CD and UC) and M8 (HC). We find that the hub of the CD and UC networks exhibit many more topological features than that of the healthy network at dimensions one and two. For example, the healthy hub only has two one-dimensional loops derived from negative links, whereas there are four and three loops for the CD and UC hubs, respectively. Also, the two diseased hubs have two-dimensional voids, which do not occur for the HC hub. Generally speaking, increasing Betti numbers (homology group rank) are associated with increasing network complexity and, thereby, it can be inferred that the disease networks are more complex than the healthy network.

We do not identify differences in the homology of the M8 network at various dimensions for both healthy and IBD states, but pronounced state-specific variation is observed in the M3 network homology. There are one and three topological features (holes) at dimension 1 derived from positive edges for CD and UC networks, respectively, which is different from the HC network in which there are no such features. More striking differences are found in the homology at dimensions 1 and 2 among the negative edges of HC, CD, and UC groups. There are three holes at dimension 1 for both HC and UC networks, but this number becomes four for the CD network. The HC network has no voids at dimension 2, whereas there are four and one voids at dimension 2 for the two diseased networks.

By dissecting the metabolic networks in terms of Betti numbers (rank of homology) at dimensions 0, 1, and 2, we identify the number of subnetworks that constitute the whole network, the number of cyclic origin–destination routes, and the number of tridimensional cyclic origin–destination routes, respectively. Consider the negative edge-derived subnetworks of module M3 for the three groups (Fig. 4). The HC and UC each have three holes (topological features) at dimension one, but these topological features are different between the two groups; for example, pentadecanoate forms a subnetwork with linoleate for the HC network but with palmitate for the UC network. Palmitate forms a subnetwork with phytosphingosine for the HC network, but this subnetwork does not exist for the UC network. Five metabolites, N6-acetyllysine, pentadecanoate, linoleate, methylinimidazole acetic acid, and 2-deoxyadenosine, form a subnetwork in the HC network, whereas three of them form a different subnetwork with butyrobetaine in the UC network. None of the four subnetworks for the CD network are the same as any subnetwork for HC and UC networks.

Homological features at dimension two can better distinguish between healthy and IBD states and between UC and CD states (Fig. 4). Two-dimensional topological features (voids) emerge when the health state of a subject changes from healthy to diseased. The CD network forms a two-dimensional void involving the majority

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e06db948-229a-490a-8941-f79b03f25c57/markdown_4/imgs/img_in_chart_box_176_816_983_1411.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-10T09%3A45%3A14Z%2F-1%2F%2F0fcd516006641b75b032ccbfacc8ea1e3dfa72faccace375bcb0e9331fcbb1f9" alt="Image" width="68%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 3. GLMY homology analysis of fine-grained networks for modules M3 served as a hub for CD and UC groups and M8 as a hub for the HC group. Y-axis represents the ranks of the homology groups (Betti numbers) at dimension zero, one, and two, and the x axis is the filtration, i.e., the change of thresholds for the strength of interaction, separately for positive interaction (promotion) and negative interaction (inhibition).</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//40b57f47-05d5-4bbe-8a06-befa45a2d953/markdown_0/imgs/img_in_image_box_183_97_462_265.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-10T09%3A45%3A11Z%2F-1%2F%2Fc1c2f48fb665d553416f1f88bd2bfa5365bb1afb3f5a08ef2f3b342ff3b3b027" alt="Image" width="23%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//40b57f47-05d5-4bbe-8a06-befa45a2d953/markdown_0/imgs/img_in_chart_box_487_67_662_262.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-10T09%3A45%3A11Z%2F-1%2F%2F76ae5b34bf3ba7f4b4deb516085ee2d77da4b562c53ad3729754aa7261f1a57c" alt="Image" width="14%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//40b57f47-05d5-4bbe-8a06-befa45a2d953/markdown_0/imgs/img_in_chart_box_674_66_980_256.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-10T09%3A45%3A11Z%2F-1%2F%2F31c5a42fed167554cee78423c426dd73e1c89b88589f5ad171deef1b68da1b29" alt="Image" width="26%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//40b57f47-05d5-4bbe-8a06-befa45a2d953/markdown_0/imgs/img_in_image_box_183_287_465_449.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-10T09%3A45%3A11Z%2F-1%2F%2Fac58e4ba3b648e1498c5cd4b8ad11b239cb71147810c5a058c6c4474b6d88587" alt="Image" width="24%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//40b57f47-05d5-4bbe-8a06-befa45a2d953/markdown_0/imgs/img_in_chart_box_488_284_657_445.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-10T09%3A45%3A11Z%2F-1%2F%2Febdf23748295b902000b02781f99c56c9826926010295e1411255e7fbc8c53de" alt="Image" width="14%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//40b57f47-05d5-4bbe-8a06-befa45a2d953/markdown_0/imgs/img_in_chart_box_673_282_986_438.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-10T09%3A45%3A11Z%2F-1%2F%2Fa8f332809930f3c6de5b32c11294351c3312bc5ab3c933828d40d0a81ba8675b" alt="Image" width="26%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//40b57f47-05d5-4bbe-8a06-befa45a2d953/markdown_0/imgs/img_in_image_box_181_468_467_627.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-10T09%3A45%3A11Z%2F-1%2F%2F952eb3f5bdbcb07bbd559c2c5d38adfc99833fecfc0c027c1fa08ce80ccf627a" alt="Image" width="24%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//40b57f47-05d5-4bbe-8a06-befa45a2d953/markdown_0/imgs/img_in_chart_box_488_462_654_620.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-10T09%3A45%3A11Z%2F-1%2F%2Fb5bf049074aac443da6304f6813af7a20301eb7d83ed2a1ced7004a851ec9022" alt="Image" width="14%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//40b57f47-05d5-4bbe-8a06-befa45a2d953/markdown_0/imgs/img_in_chart_box_672_458_985_611.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-10T09%3A45%3A12Z%2F-1%2F%2F234c0d5c5cd5c2f057627069ae201c2898108b2144c97a734e7c4d28a6d71de7" alt="Image" width="26%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 4. Detailed topological dissection of metabolic networks for healthy and diseased groups. As an example, the dissection is focused on M3's fine-grained network based on negative interactions. Betti numbers at dimensions one and two are shown, with the positions of each node corresponding to the original networks (at the Leftmost panel).</div> </div>


of metabolites as nodes, whereas the UC network dissolves such a complex homology into four different smaller two-dimensional voids. These four topological features share a circle of connectivity, a bidirectional N6-acetyllysine and methylinimidazole acetic acid edge linked to linoleate, in addition to the linkage of a bidirectional N6-acetyllysine and methylinimidazole acetic acid edge to 2-deoxyadenosine, phytosphingosine, butyrobetaine, and oleate, respectively.

Although the number of components (the topological feature of dimension 0) is health state-invariant (Fig. 3), the architecture of these homologies is completely different among the three groups. As compared to the diseased networks for module M3, the healthy network tends to include more independent positive subnetworks but fewer independent negative subnetworks in a wider range of filtration (SI Appendix, Fig. S5). We find that linoleate is a major metabolite, the pattern of whose links with other metabolites can well explain detailed topological differences between healthy and diseased networks (SI Appendix, Fig. S5). In the healthy network, we find that linoleate is inhibited three times by other metabolites, including twice by pentadecanoate through two loops, corresponding to the dimension 1 homology groups (representatives 1 and 2 in Fig. 4) and once by methylimidazole acetic acid through a loop (dimension one feature) shown as representative homology 2 in Fig. 4. Comparatively, in the CD network, linoleate is inhibited six times by other metabolites, including twice by pentadecanoate through loops (representative homologies 2 and 4), twice by methylimidazole acetic acid through distinct loops (representative homologies 1 and 3), and twice by phytosphingosine shown in representative homologies 2 and 3. In the UC network, linoleate is inhibited only by methylimidazole acetic acid in a full range of filtration (representative homology 2 in one dimension), but this metabolite is inhibited jointly by methylimidazole acetic acid and N6-cacetyllysine through all homologies at dimension 2 (Fig. 4). Also, in the CD network, linoleate is inhibited simultaneously by methylimidazole acetic acid, phytosphingosine, palmitate, and pentadecanoate identified through the dimensional two homology group. In summary, the topological differences between healthy and diseased states can be explained by the strength of inhibition for linoleate by other metabolites. The healthy network differs from the CD network mostly through the one-dimensional homology but from the UC network through the two-dimensional homology.

Linoleate plays a different topological role in the homology at dimension 0 between the healthy and IBD networks (SI Appendix, Fig. S5). It tends to actively promote methylimidazoleacetic acid and/or N6-acetyllysine in zero-dimensional homology derived from positive links for the healthy network, but this phenomenon does not occur for the UC network or rarely occurs for the CD network. Linoleate is inhibited through more complex topological structure (involving more metabolites) at dimension 0 in the healthy network than in the IBD network, suggesting that this inhibition is less stable in the former than in the latter.

## Discussion

We develop and apply a statistical physics model to reconstruct and dissect metabolic networks (idopNetworks) for healthy and IBD subjects and characterize the emergent topological properties that determine the change of health state from healthy to CD or UC and vice versa. We find that network homologies can well characterize differences between healthy networks and diseased networks as well as between UC networks and CD networks (Figs. 3 and 4 and SI Appendix, Fig. S5). Network differences can be detected in many topological aspects, but we find a general trend in health state-specific differences due to linoleate and its resulting topological features at different dimensions.

A linoleate is a salt or ester of linoleic acid, a polyunsaturated omega-6 fatty acid, whose consumption is vital to proper health. Conjugated linoleic acids (CLA) to vaccenic acid are the compounds that are considered to be beneficial for health (46, 47). Ample evidence shows that CLA have antiproliferative and anti-inflammatory effects on colonocytes (48, 49), so that provision of CLA in the intestinal lumen could be considered to prevent inflammatory CD and UC diseases (50). We find that linoleate is only slightly inhibited by pentadecanoate and methylimidazole acetic acid through a loop in dimension 1 in the healthy group, but it is heavily inhibited by these two metabolites as well as phytosphingosine through loops in dimension 1 for the CD group (Fig. 4). In homology at dimension 2, linoleate is inhibited by different types of tridimensional networks with M6-acetyllysine-methylimidazole acetic acid linkage as the main axis for the UC group. To shift the metabolite network of a UC individual to be topologically equivalent to the metabolite network of a healthy individual, one can design a therapeutic intervention that can strengthen the antagonism between N6-acetyllysine and methylimidazole, thus minimizing their inhibitive effect on linoleate. On the other hand, by designing preventive or control interventions to inhibit the abundance of pentadecanoate, phytosphingosine, and methylimidazole acetic acid, it is possible to shift a CD status to a healthy status by matching its (dimension 1) topological structure. Further investigation is needed to explore the strength of casual the relationships between GLMY homologies and disease phenotypes in order to alter metabolic function and interdependence by discovering optimal therapeutic interventions for IBD disease.

Our statistical physics model provides a starting point to implement sophisticated network theory to dissect the mechanistic basis of complex diseases. It is obvious that there is much room to improve the model, including its algorithmic efficiency, mathematical and biological justifications, and integration with many other disease-related factors. For example, one of the objectives of the Integrative Human Microbiome Project is to investigate how complex diseases are mediated by the microbiome and its interactions with omics entities, such as the transcriptome, proteome, metabolome, and phenome. Thus, reconstructing a tridimensional idopNetwork across multiple spaces is, despite its formidable challenge, sorely needed to chart a complete picture of the regulatory mechanisms underlying complex diseases (51). In any case, the fundamental idea of the model is predicated on a tremendous advance in profiling a massive amount of metabolomic data at a relatively low cost. The model may also find more promising applications in analyzing the common etiology of multiple diseases that occur in the same individual and the design of personalized prevention of many common diseases at once.

## Methods

Inferring Metabolic idopNetworks. By reviewing each subject measured at a time point as an ecosystem, we integrate an allometric scaling law and evolutionary game theory (via a generalized Lotka-Volterra dynamic) to derive a system of qdLVODEs. Ordinarily, population dynamics are expressed via generalized Lotka-Volterra equations in terms of species volume (count) as a function of time. These can be converted to the equivalent replicator equations in terms of population proportion as a function of time [see ref. 52-54 with Tanimoto (22, 23) providing complete coverage on the use of sociophysics in health systems with a focus on epidemics]. Work involving humans that requires frequent time sampling can be costly and painful for the patients. To circumvent this problem, quasidynamic differential equations are used. Here, the independent variable is population size (which may itself be time-varying). Griffin et al. (19) study these dynamics, showing that they are equivalent to the replicator with structure (surprisingly) equivalent to one variation of the discrete-time replicator.

Let  $ y_i(E) $ denote the value of metabolite  $ j $ at a given ecosystem niche  $ E $ ( $ E = 1, \ldots, n $). The qdLVODEs decompose the overall abundance level of a metabolite into two components due to its endogenous capacity and its exogenous influence from other metabolites, expressed as

 $$ \frac{d y_{j}(E)}{d E}=Q_{j}\left(y_{j}(E)\colon\Theta_{j}\right)+\sum_{j^{\prime}=1,j^{\prime}\neq j}^{m}Q_{j\leftarrow j^{\prime}}\left(y_{j^{\prime}}(E)\colon\Theta_{j j^{\prime}}\right), $$ 

where  $ Q_j(y_j(E):\Theta_j) $ is the independent component of metabolite  $ j $, which occurs when it is assumed to be in isolation, expressed as an endogenous-regulation function of  $ y_j(E) $, specified by parameters  $ \Theta_j $, and  $ Q_{j\rightarrow j'}(y_j(E):\Theta_{jj'} $ is the dependent component, which reflects the influence of the metabolite by another metabolite  $ j' $, expressed as an exogenous-regulation function of  $ y_j(E) $, specified by parameters  $ \Theta_{jj'} $. Both the independent and dependent components may not have explicit forms, but they can be fitted by a nonparametric approach, such as the Legendre Orthogonal Polynomial (LOP). The LOP has proven to be a powerful tool for fitting the curves of arbitrary forms (13). The best order of LOP fitting curves can be determined according to information criteria.

To overcome model overfitting of Eq. 1 and reconstruct biologically robust and sparse networks, we implement variable selection to choose a subset of the most significant metabolites that link with a given metabolite. Thus, a full model of qdLVODE is reduced to its sparse form, but without reduction of dimension. The fourth-order Runge-Kutta algorithm is implemented to solve the qdLVODE of Eq. 1 subject to variable selection. Alternatively, neural networks can be used as a universal approximator for the solution of a given ODE (55, 56). The independent components (as nodes) and dependent components (as edges) estimated by Eq. 1 are coded into mathematical graphs, which are idopNetworks. The requirement of sample size for idopNetwork reconstruction has been discussed in Wang et al. (57).

GLMY Homology Theory of Metabolic Networks. As a mathematical approach for dissecting network topology, fruitful mathematical structures and techniques from GLMY homology theory have been discovered through the collective work of researchers worldwide (24-27). Intensive research on the subject has led to efficient characterizations on the asymmetric structures of networks (28, 29).

A mathematical definition of GLMY homology is briefly provided as follows. Given a directed network  $ G = (V, E) $ with node set  $ V = \{v_1, \cdots, v_n\} $ and edge set  $ E \subset V \times V $. An elementary  $ p $-path is any sequence of  $ p+1 $ nodes  $ \cdots \ldots v_p $ of  $ V $. Taking coefficients in a field  $ F $, let  $ \Lambda_p $ be the vector space spanned the elementary  $ p $-paths of  $ G $ over  $ F $ (in much the same way a vector space over a field is defined for a simplicial complex). Define the boundary operator  $ \partial_p: \Lambda_p \to \Lambda_{p-1} $ by the formula:

 $$ \partial_{p}\left(v_{\cdots\cdots}v_{i_{p}}\right)=\sum_{q=0}^{p}(-1)^{q}v_{i_{0}}\cdots v_{i_{q-1}}v_{i_{q+1}}\cdots v_{i_{p}}. $$ 

Moreover, one needs to introduce a concept of allowed path as follows. An allowed $p$-path$\cdots\cdots v_{i_{p}}$ is an elementary $p$-path such that $(v_{i_{j}}, v_{i_{j+1}}) \in E(0 \leq j < p)$ Now let $A_{p}$ be the subspace of $\Lambda_{p}$ spanned by the allowed $p$-paths of $G$, and consider the following subspace of

 $$ \mathsf{A}_{p}\colon $$ 

 $$ \begin{array}{r}{\mathbf{\Delta}^{\prime}\Omega^{p}\;=\;\left\{\sigma\in\mathsf{A}_{p}|\partial_{p}(\sigma)\in\mathsf{A}_{p-1}\right\}.}\end{array} $$ 

Restriction of the boundary operator  $ \partial_p $ of  $ \Lambda_p $ to  $ \Omega_p $ gives rise to a chain complex (of homology groups),

 $$ 0\longleftarrow\Omega_{0}\stackrel{\partial_{1}}{\longleftarrow}\cdots\stackrel{\partial_{p-1}}{\longleftarrow}\Omega_{p-1}\stackrel{\partial_{p}}{\longleftarrow}\Omega_{p}\stackrel{\partial_{p+1}}{\longleftarrow}\Omega_{p+1}\longleftarrow\cdots, $$ 

with  $ \partial_{p-1}\partial_p=0 $. The p-th GLMY homology of G is then defined by  $ \mathrm{H}_p(G)=\mathrm{Ker}\partial_p/\mathrm{Im}\partial_{p+1} $.

The $p$-th GLMY Betti number of $G$ is the rank of $H_p(G)$, denoted by $\beta_p$, which gives a sequence of topological features on directed network. Here, $\beta_0$ is the number of connected components of the underlying undirected network, $\beta_1$ detects the structure of directed cycles up to interactions between them, and $\beta_p(p \geq 2)$ detects certain higher-order interacting structures on $p$-pathways.

By combining a filtration process of the digraph with the GLMY homology, the persistent GLMY homology can be constructed. More specifically, assume we have a filtration of a digraph G, that is, a sequence of nested digraphs

 $$ \varnothing\varnothing\;=\;G_{1}\;\subset\;G_{2}\;\subset\;\ldots\;\subset\;G_{n-1}\;\subset\;G_{n}\;=\;G\;, $$ 

where $G_{i}$ is a subgraph of $G_{i+1}(0 < < n)$. For each diagram $G_{i}$, considering its $p$-th GLMY homology $H_{p}(G_{i})$, then a sequence of homogies can be derived as

 $$ H_{p}\left(G_{1}\right)\stackrel{f}{\rightarrow}H_{p}(\cdots)\stackrel{f}{\rightarrow}\cdots\stackrel{f}{\rightarrow}H_{p}\left(G_{n-1}\right)\stackrel{f}{\rightarrow}H_{p}\left(G_{n}\right), $$ 

where f is induced from the inclusion between two adjacent digraphs. The evolution of homology through this sequence is called the p-th persistent GLMY homology of the filtration of G. The persistent GLMY homology over the field coefficient can be represented as a persistent barcode or persistent diagram, which naturally gives a multiscale topological characterization of the structure within the digraph G. In particular, the GLMY persistent homology allows an individual to study the topological features of a digraph at multiple scales of resolution.

Real-World Datasets. As the second phase of the NIH Human Microbiome Project, the Integrative Human Microbiome Project produced metabolomic data of subjects from a cross-sectional cohort study (31–33), which are publicly available at http://hmp2.org. This study measured 185 metabolites from stool samples for 411 IBD-diseased subjects and 135 HC from both pediatric and adult populations. All IBD patients are divided into 265 CD subjects and 146 UC subjects. Specifically, these data were collected from 50 CD-diseased subjects, aged from 8 to 76 y, 30 UC-diseased subjects, aged from 6 to 76 y, and 26 HC, aged from 6 to 69 y. Among the three groups, the metabolites of some subjects were measured multiple times. The descriptions of the cohort study design, sampling strategies, and metabolomic measurement are detailed in The Integrative HMP Research Network Consortium (31, 32).

Data, Materials, and Software Availability. All study data are included in the article and/or SI Appendix. All code developed and used throughout this study has been made open source and is available on GitHub. The code used to train the metabolomic network model can be found at https://github.com/bjfuws/MetabPhysics (58). The Integrative Human Microbiome Project data, including metabolomics, are publicly available to bona fide researchers upon applications at https://ibdmdb.org/ (31-33).

ACKNOWLEDGMENTS. This work is partially supported by Beijing Yanqi Lake Institute of Mathematical Sciences and Applications.

Author affiliations:  $ {}^{a} $Center for Computational Biology, College of Biological Sciences and Technology, Beijing Forestry University, Beijing 100083, China;  $ {}^{b} $Chern Institute of Mathematics, Nankai University, Tianjin 300071, China;  $ {}^{c} $Beijing Yanqi Lake Institute of Mathematical Sciences and Applications, Beijing 101408, China;  $ {}^{d} $Department of Public Health Sciences, Penn State College of Medicine, Hershey, PA 17033;  $ {}^{e} $Department of Medicine, Creighton University School of Medicine, Omaha, NE 68124;  $ {}^{f} $Molecular Biology Laboratory, Bios Biotech Multi-Diagnostic Health Center, Rome 00197, Italy;  $ {}^{g} $Applied Research Laboratory, The Pennsylvania State University, University Park, PA 16802; and  $ {}^{h} $Yau Mathematical Sciences Center, Tsinghua University, Beijing 100084, China

1. S. Ahadi et al., Personal aging markers and age-type revealed by deep longitudinal profiling. Nat Med. 26, 83–90 (2020).

2. S. M. Schüssler-Fiorenza Rose et al., A longitudinal big data approach for precision health. Nat. Med. 25, 792–804 (2019).

3. D. C. Goff Jr. et al., ACC/AHA Guideline on the assessment of cardiovascular risk. Circulation 129, S49–S73 (2014).

4. M. V. Holmes et al., Lipids, lipoproteins, and metabolites and risk of myocardial infarction and stroke. J. Am. Coll. Cardiol. 71, 620–632 (2018).

5. L. Lécuyer et al., NMR metabolomic signatures reveal predictive plasma metabolites associated with long-term risk of developing breast cancer. Int. J. Epidemiol. 47, 484-494 (2018).

6. J. Tynkkynen et al., Association of branched-chain amino acids and other circulating metabolites with risk of incident dementia and Alzheimer's disease: A prospective study in eight cohorts. Alzheimer's Dement. 14, 723-733 (2018).

7. T. Buergel et al., Metabolomic profiles predict individual multidisease outcomes. Nat Med. 28, 2309–2320 (2022).

8. J. L. Markley et al., The future of NMR-based metabolomics. Curr. Opin. Biotechnol. 43, 34–40 (2017).

9. A. De Lorenzo et al., Obesity: A preventable, treatable, but relapsing disease. Nutrition. 71, 110615 (2020).

10. J. V. S. Guerra et al., Multifactorial basis and therapeutic strategies in metabolism-related diseases. Nutrients. 8, 2830 (2021).

11. R. Lambiotte et al., From networks to optimal higher-order models of complex systems. Nat. Phys. 15, 313-320 (2019).

13. R. L. Wu, L. B. Jiang, Recovering dynamic networks in big static datasets. Phys. Rep. 912, 1–57 (2021).

12. C. Sergiou et al., Complex systems: A communication networks perspective towards 6G. IEEE Access. 8, 89007–89030 (2020).

14. D. S. Lee et al., The implications of human metabolic network topology for disease comorbidity. Proc. Natl. Acad. Sci. U.S.A. 29, 9880-9885 (2008).

15. A. L. Barabási et al., Network medicine: A network-based approach to human disease. Nat. Rev. Genet. 12, 56-68 (2011).

16. M. Caldera et al., Interactome-based approaches to human disease. Curr. Opin. Syst. Biol. 3, 88–94 (2017).

17. P. E. P. Burke et al., A biochemical network modeling of a whole-cell. Sci. Rep. 10, 13303 (2020).

18. C. Chen et al., An omnidirectional visualization model of personalized gene regulatory networks. npj Syst. Biol. Appl. 5, 38 (2019).

19. C. Griffin et al., Analysis of quasi-dynamic ordinary differential equations and the quasi-dynamic replicator. Phys. A Stat. Mech. App. 555, 124422 (2020).

20. L. D. Sun et al., Statistical mechanics of clock gene networks underlying circadian rhythms. Appl. Phys. Rev. 8, 021313 (2021).

21. J. Tanimoto, Fundamentals of Evolutionary Game Theory and its Application (Springer, 2015).

22. J. Tanimoto, Sociophysics Approach to Epidemics (Springer, 2021).

23. J. Tanimoto, Evolutionary Games with Sociophysics: Analysis of Traffic Flow and Epidemics (Springer, 2018).

25. A. Grigor'yan et al., Homotopy theory of digraphs. Pure Appl. Math. Q. 10, 619–674 (2014).

24. A. Grigor'yan et al., Homologies of path complexes and digraphs. arXiv [Preprint] (2012). https://doi.org/10.48550/arXiv.1207.2834. Accessed 10 April 2022.

26. A. Grigor'yan et al., Homologies of digraphs and Künneth formulas. Comm. Anal. Geom. 25, 969-1018 (2017).

27. A. Grigor'yan et al., Path complexes and their homologies. J. Math. Sci. 248, 564–599 (2020).

28. S. Chowdhury, F. Memoli, "Persistent path homology of directed networks" in SODA '18: Proceedings of the Twenty-Ninth Annual ACM-SIAM Symposium on Discrete Algorithms, A. Czumaj, Eds. (SIAM, 2018), pp. 1152–1169.

29. S. Chowdhury et al., "Path homologies of deep feedforward networks" in International Conference on Machine Learning and Applications (ICMLA), M.A. Wani, T.M. Khoshgoftaar, D. Wang, H. Wang, N. Seliya, Eds. (IEEE, 2019), pp. 1077–1082.

30. D. Chen et al., Path topology in molecular and materials sciences. J. Phys. Chem. Lett. 14, 954–964 (2023).

31. The Integrative HMP (iHMP) Research Network Consortium, The Integrative Human Microbiome Project: Dynamic analysis of microbiome-host omics profiles during periods of human health and disease. Cell Host Microb. 16, 276–289 (2014).

32. The Integrative HMP (iHMP) Research Network Consortium, The integrative human microbiome project. Nature 569, 641–648 (2019).

33. J. Lloyd-Price et al., Multi-omics of the gut microbial ecosystem in inflammatory bowel diseases. Nature 569, 655-662 (2019).

34. C. Abraham et al., Inflammatory bowel disease. N. Engl. J. Med. 361, 2066–2078 (2009).

35. J.T. Chang, Pathophysiology of inflammatory bowel diseases. N. Engl. J. Med. 27, 2652–2664 (2020).

36. E. J. Millet et al., Genomic prediction of maize yield across European environmental conditions. Nat. Genet. 51, 952–956 (2019).

37. J. von Neumann et al., Theory of Games and Economic Behavior (Princeton University Press, Princeton, New Jersey, 1944).

38. J. F. Nash et al., Equilibrium points in n-person games. Proc. Natl. Acad. Sci. U.S.A. 36, 48–49 (1950).

39. J. M. Maynard Smith et al., The logic of animal conflict. Nature 246, 15–18 (1973).

40. K. Grunert et al., Evolutionarily stable strategies in stable and periodically fluctuating populations: The Rosenzweig-MacArthur predator-prey model. Proc. Natl. Acad. Sci. U.S.A. 4, e2017463118 (2021).

41. G. B. West et al., A general model for the origin of allometric scaling laws in biology. Science 122, 6 (1997).

42. M. Nosonovsky et al., Allometric scaling law and ergodicity breaking in the vascular system. Microfluid Nanofluid 24, 53 (2020).

43. D. Yang et al., Inferring multilayer interactome networks shaping phenotypic plasticity and evolution. Nat Commun. 12, 5304 (2021).

44. C. Lopez-Otin et al., The hallmarks of aging. Cell. 153, 1194-1217 (2013).

45. J. R. Aunan et al., The biology of aging and cancer: A brief overview of shared and divergent molecular hallmarks. Aging Dis. 8, 628-642 (2017).

46. E. Devillard et al., Metabolism of linoleic acid by human gut bacteria: Different routes for biosynthesis of conjugated linoleic acid. J. Bacteriol. 189, 2566–2570 (2007).

47. M. W. Pariza, Perspective on the safety and effectiveness of conjugated linoleic acid. Am. J. Clin. Nutr. 79, 1132S-1136S (2004).

48. J. Bassaganya-Riera et al., Activation of PPAR gamma and delta by conjugated linoleic acid mediates protection from experimental inflammatory bowel disease. Gastroenterology. 127, 777-791 (2004).

49. M. Q. Kemp et al., Conjugated linoleic acid inhibits cell proliferation through a p53-dependent mechanism: Effects on the expression of G1-restriction points in breast and colon cancer cells. J. Nutr. 133, 3670-3677 (2003).

50. A. Greicius et al., CLA's act: Feeding away inflammation. Gastroenterology 127, 994–996 (2004).

51. R. L. Wu, Quantitative Methods for Precision Medicine (CRC Press, 2022).

52. J. Hofbauer, K. Sigmund, Evolutionary Games and Population Dynamics (Cambridge University Press, 1998).

53. J. Weibull, Evolutionary Game Theory (MIT Press, 1997).

54. E. Paulson, C. Griffin, Cooperation can emerge in prisoner's dilemma from a multi-species predator prey replicator dynamic. Math. Bio. Sci. 278, 56–62 (2016).

55. I. E. Lagaris et al., Artificial neural networks for solving ordinary and partial differential equations. IEEE Trans. Neural Networks 9, 987–1000 (1998).

56. T.T. Dufera, Deep neural network for system of ordinary differential equations: Vectorized algorithm and simulation. Mach. Learn. Appl. 5, 100058 (2021).

57. H. Wang, Modeling genome-wide by environment interactions through omnigenic interactome networks. Cell Rep. 35, 109114 (2021).

58. S. Wu, et al., The metabolomic physics of complex diseases. GitHub. https://github.com/bjfuws/MetabPhysics. Deposited 1 March 2023.

