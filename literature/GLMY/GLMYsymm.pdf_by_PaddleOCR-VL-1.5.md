# GLMYsymm: Inferring Symmetry Order of Protein Complexes from Single Sequences Using Persistent GLMY homology

Jiaqi Zhai $ ^{†1} $, Jingyan Li $ ^{†2} $, Shing-Tung Yau $ ^{3*} $, Xinqi Gong $ ^{1*} $

 $ ^{1} $School of Mathematics, Renmin University of China, Zhongguancun Street, Beijing, China.

 $ ^{2} $Institute of Mathematical Sciences and Application, Yanqi Lake, Beijing, China.

 $ ^{3} $Tsinghua University, Beijing, China.

*Corresponding author(s). E-mail(s): styau@tsinghua.edu.cn, xinqigong@ruc.edu.cn;

## Abstract

Proteins often perform essential biological functions in the form of complexes. The assembly of protein complexes typically exhibits symmetry, which contributes to a more stable structural organization. Therefore, investigating structural symmetry is of great importance for protein complex structure prediction. However, existing methods for predicting protein structural symmetry are limited in number and generally show unsatisfactory accuracy. To address this issue, we propose GLMYsymm, a single-sequence-based model for symmetry prediction of homologous protein complexes. The key innovation of this work lies in the use of persistent GLMY homology to extract topological information from protein sequences, which is further integrated with the ESM2 pretrained model to enable end-to-end symmetry prediction directly from sequence data. To the best of our knowledge, this is the first study to apply persistent GLMY homology to protein sequence feature extraction, without relying on structural information or multiple sequence alignment (MSA). Through extensive ablation and comparative experiments, we further demonstrate the effectiveness of GLMY homology-based topological sequence features for training deep learning models. On the same test dataset, GLMYsymm outperforms both Seq2symm and QUEEN by 0.32 in terms of the Macro AUC-PR metric. In the field of protein structure prediction, GLMYsymm can be used to assess the symmetry of predicted protein structures, thereby assisting in protein structure quality evaluation, and can also serve as an important reference for stoichiometry prediction. The code and datasets for GLMYsymm are available at http://mialab.ruc.edu.cn/GLMYsymmServer/.

Keywords: Homologous protein complexes, symmetry prediction, GLMY homology, single-sequence model, deep learning

## 1 Introduction

Symmetric quaternary structures of proteins are highly prevalent in nature [1]. Since protein structure determines function [2], structural symmetry enables the formation of more complex architectures through relatively simple assembly mechanisms, thereby facilitating more sophisticated biological functions [3]. In addition, protein symmetry contributes to enhanced structural stability [4], increased flexibility, conservation of genetic resources, and functional cooperativity [5]. Investigating protein symmetry is therefore essential for deepening our understanding of protein quaternary structure and function, and is particularly important for protein structure prediction—especially for large protein complexes—as well as for protein structure quality assessment.

At present, several methods have been developed to identify symmetry in protein quaternary structures [6], including SymD [7], CE-Symm [8], and DeepSymmetry [9]. These approaches can detect symmetric residue pairs and symmetry axes, enabling the analysis of symmetry and pseudosymmetry in multimeric protein structures. However, all of these methods require experimentally determined protein structures in order to perform geometric analysis. In practical applications, due to the high cost and labor demands of experimental structure determination [10], a large number of proteins still lack resolved structures. In contrast, protein sequence information is much easier to obtain and is far more abundant than experimentally determined structures [11, 12].

In recent years, deep learning-based computational methods for protein structure prediction have achieved remarkable progress. Methods such as AlphaFold2  $ [11] $ and AlphaFold3  $ [13] $ have reached accuracies exceeding 90% for monomeric protein structure prediction. However, there remains substantial room for improvement in the prediction of multimeric protein structures. Predicting protein structural symmetry using deep learning approaches has the potential to further enhance the accuracy of protein complex structure prediction.

Several deep learning-based methods have been proposed to predict the symmetry of homologous protein structures (e.g., Seq2Symm [14]) or to infer homologous protein assembly modes (e.g., QUEEN [15]). However, Seq2Symm relies on multiple sequence alignment (MSA) information, which increases computational cost, while QUEEN is unable to determine the intrinsic symmetry type of a protein complex.

To further improve the accuracy of symmetry prediction for homologous protein complexes, we propose GLMYsymm, a method that predicts the symmetry of homologous protein complex structures by extracting sequence topological features using Persistent GLMY Homology. The overall workflow is illustrated in Figure 1A and B. Given the strong correlation between protein homology and structural symmetry—namely, homologous proteins tend to exhibit symmetric structures, and most symmetric structures arise from homologous assemblies [16, 17]—this study focuses specifically on homologous protein complexes.

The main contributions of GLMYsymm are summarized as follows:

1. We use statistical features derived from persistent GLMY homology barcodes as topological features extracted from protein sequences to predict the symmetry of protein complex structures. To the best of our knowledge, this is the first application of persistent GLMY homology to protein sequence feature extraction.

2. GLMYsamm relies solely on sequence information, without requiring structural data or multiple sequence alignment (MSA), enabling end-to-end prediction from protein sequence to symmetry.

3. By analyzing features extracted via persistent GLMY homology, we observe clear separability of sequence topological features across different symmetry classes, further demonstrating the relevance of sequence topology for protein symmetry prediction.

4. Through comparisons among different persistent GLMY homology feature extraction strategies, ablation studies, and benchmarking against existing methods, we demonstrate the effectiveness of persistent GLMY homology-derived sequence topological information for training deep learning models, providing guidance for future research in related problems.

In this study, we systematically evaluated multiple strategies for extracting sequence features using persistent GLMY homology and ultimately selected a configuration that computes only 1-mer features with a maximum filtration value of 8 and homology dimension 2. Under this setting, the model achieved a Macro AUC-PR of 0.5921. Statistical analysis of the extracted persistent GLMY homology features revealed that the one-dimensional Betti number features of 1-mers exhibit clear separability among different symmetry classes, confirming that sequence topological features derived from persistent GLMY homology enable the model to distinguish between different symmetry types.

Furthermore, we compared GLMYsymm with two deep learning-based methods, Seq2Symm and QUEEN, for protein complex symmetry prediction. Using Macro AUC-PR as the evaluation metric, GLMYsymm outperformed both methods by 0.32. These results demonstrate that persistent GLMY homology features can more precisely capture sequence information, allowing GLMYsymm to achieve improved prediction performance for homologous protein symmetry without relying on structural data or MSA information.

In summary, GLMYsymm enables more accurate prediction of symmetry in homologous protein complexes. The sequence topological information extracted via persistent GLMY homology shows meaningful associations with protein symmetry, allowing the model to better learn symmetry-related features. GLMYsymm therefore provides a valuable methodological reference for future research in related areas.

## 2 Datasets

In this study, the data were obtained from the Protein Data Bank (PDB) [18]. The detailed data processing procedure is described as follows.

Based on the symmetry annotations provided in the PDB database, protein structures were retrieved using the advanced search function [1]. Specifically, protein complexes exhibiting  $ C_n $ symmetry ( $ n = 1-17 $),  $ D_n $ symmetry ( $ n = 2-8 $, where  $ D_1 $ is equivalent to  $ C_2 $ symmetry), as well as H, O, and T symmetries were collected. All selected structures were required to contain no more than 20 chains. This procedure yielded an initial set of 329,768 FASTA sequences.

Structures with  $ C_n $ ( $ n > 17 $),  $ D_n $ ( $ n > 8 $), I symmetry, or with more than 20 chains were excluded from this study. After applying the above filtering criteria, the number of structures belonging to these symmetry types was extremely limited (only a few or several dozen), and these structures are typically very large. Including them would introduce noise into the model and negatively affect learning efficiency.

To remove redundancy, MMseqs2[19] was employed to cluster protein sequences. All sequences were clustered with a minimum sequence identity of 30% and an alignment coverage of at least 80% of the sequence length. Representative protein structures from each cluster were then selected to construct the dataset. This procedure effectively prevents data leakage during model training. After redundancy removal, the dataset was split into training, validation, and test sets with a ratio of 8:1:1.

The number of samples varies substantially across different symmetry classes, resulting in severe class imbalance that significantly degrades model performance. To address this issue, sampling strategies were applied to the training dataset. Specifically, samples labeled as  $ C_1 $ were undersampled to 60% of their original size;  $ C_2 $ samples were left unchanged;  $ C_3 $ and  $ D_2 $ samples were oversampled by a factor of 5; and all remaining symmetry classes, which had very limited sample sizes, were oversampled by a factor of 20. This strategy was designed to increase the number of samples in extremely small classes to approximately 1,000, bringing them to the same order of magnitude as the larger classes. The data distributions before and after sampling are shown in Figure 1C and D.

Some protein monomer sequences were associated with multiple symmetry labels, meaning that the same single-chain protein could assemble into complexes with different symmetry types. For example, protein 3MSR can form assemblies with  $ C_{1} $,  $ C_{2} $,  $ C_{3} $, and  $ D_{3} $ symmetries. Since such multi-label samples may adversely affect model

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//f3623cf1-90e9-44e1-a540-423bd2e1a6a4/markdown_3/imgs/img_in_image_box_288_148_914_830.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A13Z%2F-1%2F%2F5f40bbe478201167e8e7f882c45f7295b1f82df547ab67188f74d8dcc71cba9c" alt="Image" width="52%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//f3623cf1-90e9-44e1-a540-423bd2e1a6a4/markdown_3/imgs/img_in_chart_box_286_834_562_1132.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A13Z%2F-1%2F%2F5125fda9a93f38057079bf4f4df6e5d408138029ee967a7c6da9019cf77e8da5" alt="Image" width="23%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//f3623cf1-90e9-44e1-a540-423bd2e1a6a4/markdown_3/imgs/img_in_chart_box_570_835_924_1144.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A13Z%2F-1%2F%2F54788730f9cd7e1e6f423c4222bffa737a8338d606a7f0cd06dccbef68a87182" alt="Image" width="29%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 1 Overview of the GLMYsymm framework and data distribution. A Schematic illustration of persistent GLMY homology feature extraction. The protein sequence "PYFPDNIP-SPTIAYEGPASKNPLAFKFYPNPEPEKVPGDKTMTFTGDGSDPFGAGNMIRP" is used as an example. The positions of the residue "P" in the sequence are identified as (1, 4, 8, 10, 17, 22, 29, 31, 33, 37, 51, 60). Within the dashed box, the left panels show the undirected graphs  $ \mathbf{G}(d_i) $ constructed at relative distances  $ d = 0, 1, \cdots, 8 $, while the right panels present the barcodes corresponding to the birth and death of 0-dimensional, 1-dimensional, and 2-dimensional homology classes throughout the filtration process. Statistical features are extracted from the barcode diagram of each residue in the sequence, and these features are concatenated to form the persistent GLMY homology representation of the entire sequence. B Workflow of GLMYsymm. The model takes the sequence information of homologous proteins as input and consists of two parallel feature extraction branches. In the first branch, the ESM2 model is used to compute residue-level embeddings, which are then aggregated via average pooling to obtain a global protein representation and further compressed through a multilayer perceptron (MLP). In the second branch, persistent GLMY homology is applied to compute sequence topological features for all 1-mers of the protein, with a maximum filtration distance of 8; these features are subsequently reduced in dimensionality using an MLP to match the dimensionality of the ESM2 features. Finally, the features from both branches are concatenated and fed into subsequent MLP layers and a prediction head to predict the symmetry of protein complex structures. C Distribution of samples across different symmetry classes before sampling. D Distribution of samples across different symmetry classes after sampling. As shown in the figure, after oversampling and resampling, the data distribution becomes more balanced, which enables the model to better learn and attend to symmetry classes with limited sample sizes.</div> </div>


performance and account for only a small fraction of the dataset, all multi-label data were removed.

Because large protein complexes are underrepresented in current databases, further steps were taken to alleviate class imbalance. Symmetry classes with extremely small sample sizes were merged as follows:  $ C_{7}-C_{9} $,  $ C_{10}-C_{17} $, and  $ D_{6}-D_{8} $ were grouped into three composite labels. The final number of protein structures for each symmetry class used in this study is reported in Table 1 of the Appendix.

## 3 Results

### 3.1 GLMYsymm Overview

GLMYsymm is a deep learning model that predicts the symmetry of homologous protein complexes by extracting sequence topological features using persistent GLMY homology and integrating them with representations derived from the ESM2 large-scale pretrained language model. The input to the model is the single-chain amino acid sequence of a protein whose symmetry is to be predicted, and the output is the predicted symmetry class.

The overall workflow of GLMYsymm is as follows. First, for each input single-chain sequence, persistent GLMY homology is used to extract 360-dimensional sequence topological features, which are subsequently reduced to 256 dimensions using a multilayer perceptron (MLP). In parallel, the ESM2 pretrained language model is applied to compute sequence embeddings for the protein, and the resulting residue-level features are averaged across the residue dimension to obtain a global sequence representation for the single chain. This representation is also projected to 256 dimensions using an MLP. The two feature representations are then concatenated and fused through an MLP-based architecture. Finally, a prediction head is applied to output the symmetry class of the protein complex.

Further methodological details are provided in the Methods section, and a schematic illustration of the model architecture is shown in Figure 1B.

### 3.2 Exploration of GLMY homology–Based Feature Extraction Methods

GLMY homology is an algebraic topology-based framework specifically designed to characterize the topological structure of directed graphs. By defining boundary operators on directed paths, GLMY homology constructs chain complexes that capture higher-order connectivity patterns induced by directionality in directed networks. In GLMYsymm, GLMY homology is employed to extract topological features from protein sequences. The results of all feature extraction strategies explored in this study are summarized in Figure 1A, and the detailed methodologies and corresponding analyses are described as follows.

#### 3.2.1 Construction and Selection of Relative-Position-Based Persistent Homology Features

##### Modeling Method

For each type of residue or residue pair in a protein sequence, we denote it by the symbol  $ \pi $. All occurrences of  $ \pi $ in the sequence are identified and indexed as  $ \pi_{k_1}, \pi_{k_2}, \ldots, \pi_{k_n} $, where  $ k_i $ denotes the position index of  $ \pi $ in the sequence. We first construct a relative distance matrix  $ D $, whose entries are defined as

 $$ D_{i,j}=\left|k_{i}-k_{j}\right| $$ 

This matrix characterizes the absolute positional distances between different occurrences of  $ \pi $ along the sequence. Next, a nested sequence of undirected graphs is constructed. The vertex set is given by  $ \{\pi_{k_1}, \pi_{k_2}, \ldots, \pi_{k_n}\} $. Given a distance filtration

threshold d, an undirected edge is added between vertices  $ \pi_{k_i} $ and  $ \pi_{k_j} $ if

 $$ |k_{i}-k_{j}|\leq d. $$ 

The weight of the edge is set to  $ |k_i - k_j| $, yielding a weighted undirected graph denoted by  $ G(d) $. As the filtration value  $ d $ increases, a nested sequence of undirected graphs is obtained:

 $$ G(d_{0})\subset G(d_{1})\subset G(d_{2})\subset\cdots\subset G(d_{N}). $$ 

This approach not only characterizes the positional distribution of  $ \pi $ along the protein sequence, but also captures adjacency patterns and topological structures formed by  $ \pi $ at different locations, providing a novel topological perspective for protein sequence analysis.

##### Feature Extraction Implementation

We construct persistent GLMY homology features (GLMY features) from protein sequences by considering both individual residues (1-mer) and residue pairs (2-mer) to capture topological information. Specifically, we compute GLMY features for all 1-mer and the 20 most frequent 2-mer across the dataset. For each residue  $ \pi $, a nested undirected graph is constructed, and persistent GLMY homology is computed for the three homology dimensions  $ H_0 $,  $ H_1 $,  $ H_2 $ (or 2-dimensional cycles). From the corresponding barcodes, six statistical features are extracted for each homology dimension to form the model input.

Each graph  $ G(d_i) $ is then treated as a directed graph by assigning bidirectional arrows to each undirected edge. Persistent homology is computed over the resulting nested sequence of directed graphs. The extracted barcode information, including statistical features of the 0-dimensional, 1-dimensional, and 2-dimensional barcodes, is used as the topological representation of  $ \pi $ in the sequence.

For computational efficiency, although there are theoretically  $ 20 \times 20 = 400 $ possible 2-mer combinations, we only consider the 20 most frequent 2-mer, as including all combinations would significantly increase computational cost and produce many sparse features, which could hinder model training.

The maximum filtration distance  $ d_{\max} $ is determined by first estimating the average distances between identical residues using kernel density estimation, followed by a grid search to optimize  $ d_{\max} $. During graph construction, an edge between two identical k-mers is only added if  $ d(i,j) \leq d_{\max} $, where  $ d(i,j) $ denotes the sequence distance between the two mers.

The six statistics extracted from the barcode information are defined as follows. Let  $ \ell_{i} $ denote the lifetime of the i-th bar, N be the total number of bars, and  $ d_{\max} $ the maximum filtration distance:

1. Count of bars: N

2. Maximum lifetime:  $ \max_{i} \ell_{i} $

3. Mean lifetime:  $ \frac{1}{N} \sum_{i=1}^{N} \ell_{i} $

4. Total lifetime:  $ \sum_{i=1}^{N}\ell_{i} $

5. Long-lived bars:  $ \# \left\{ \ell_i \mid \ell_i > \frac{d_{\max}}{2} \right\} $

6. Minimum lifetime:  $ \min_{i} \ell_{i} $

Thus, each 1-mer or 2-mer is represented by an 18-dimensional vector (3 homology dimensions  $ \times $6 statistics). At the level of the full protein sequence, the total persistent homology feature dimension is  $ (20\ 1-\mathrm{mers} + 20\ 2-\mathrm{mers}) \times 18 = 720 $.

Finally, we systematically evaluated different strategies for selecting GLMY homology features and used the Macro AUC-PR as the performance metric, as described in Section 5.1 of the Methods.

#### 3.2.2 Selection of 1-mer and 2-mer Features

First, we trained the model using only 1-mer features, i.e., extracting topological information solely from individual residues. Subsequently, we incorporated the 20 most

frequent 2-mer features observed across all protein sequences. The selected 2-mers are: AA, AG, AL, AV, EA, EL, GL, GS, HH, LA, LE, LG, LK, LL, LS, LV, SG, SL, VA, VL.

In comparison, incorporating 2-mer features still outperforms the baseline model without GLMY features, suggesting that the topological information of residue pairs can partially complement local structural features of sequences. However, due to the high sparsity of 2-mer features in real sequences, many feature values are zero, which limits the model's ability to effectively learn their topological patterns. As a result, in most parameter settings, the model with 2-mer features does not surpass the performance obtained using only 1-mer features.

The experimental results are shown in Figure 2. Each column corresponds to a specific value of the maximum filtration distance parameter, and each row represents a different feature extraction strategy. Overall, across different maximum filtration distance settings, training with only 1-mer features achieved superior predictive performance in the majority of cases (approximately 75%).

These results indicate that 1-mer features possess strong expressive power in capturing the global topological structure and semantic information of protein sequences. The relative positional distribution of individual residues and their global traversal patterns are sufficient to largely represent the overall structural features of the sequence. Consequently, relying solely on 1-mer features yields a stable and discriminative representation.

<div style="text-align: center;"><div style="text-align: center;">Grid Search Results Heatmap</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//8ef06af9-455d-4e5e-8cfc-e8d4f690f010/markdown_1/imgs/img_in_chart_box_204_711_937_943.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A10Z%2F-1%2F%2Fce2ab879dee63830f89ed30305f2b8b307579b5838977e485a9247098ba87400" alt="Image" width="61%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 2 Grid search results for parameter selection of persistent GLMY homology features. Each row corresponds to a different feature extraction strategy, and each column corresponds to a specific value of the maximum filtration distance. The numbers shown indicate the Macro AUC-PR of the model on the training and test sets for the corresponding parameter combination. Higher values indicate better predictive performance.</div> </div>


#### 3.2.3 Exploration of Dimensionality for 2-mer Features

During the extraction of persistent GLMY homology features, the Betti numbers of the 2-dimensional homology are mostly zero under the given distance constraints. Therefore, using them directly as features is not ideal. Instead, we chose to use the dimension of the 2-dimensional cycle group as the feature.

In Figure 2, “1mer+2mer_Z2” refers to using all 1-mer and the 20 most frequent 2-mer features, calculating the 0-dimensional and 1-dimensional persistent GLMY homology as well as the 2-dimensional cycle information, extracting statistical features from the barcodes, and using these as input features to train the model. “1mer+2mer_H2” refers to calculating the 0-dimensional, 1-dimensional, and 2-dimensional persistent GLMY homology of the same 1-mer and 2-mer features, and using the corresponding barcode statistics as input for model training.

The model testing results show that in most cases (62.5%), the performance with “1mer+2mer_H2” is worse than that with “1mer+2mer_Z2”. This is primarily because, within the range of the maximum filtration value, the Betti numbers for 2-dimensional paths in the undirected graphs are mostly zero.

Based on the comparative analysis of these experiments, we ultimately selected using only all 1-mer features for constructing persistent GLMY homology sequence topological features. This feature configuration demonstrates more stable and generally superior predictive performance across different filtration parameter settings, while effectively capturing the global topological and semantic information of protein sequences and avoiding feature sparsity and excessive computational complexity.

#### 3.2.4 Selection of Maximum Filtration Distance Parameter

During the construction of persistent GLMY features, the choice of the maximum filtration distance parameter has a critical impact on the extracted topological features. When the maximum filtration distance is too large, as the filtration distance $d$ increases, the resulting graph gradually approaches a complete graph. In this case, the topological features degenerate: the 0-dimensional homology class has only one connected component, and the 1-dimensional and 2-dimensional homology classes vanish, i.e., $\beta_0 = 1$, $\beta_1 = 0$, $\beta_2 = 0$. Although this process captures the full evolution of residue (or residue-pair) topology with increasing distance, it significantly increases computational complexity, and the overly trivial topological representation is not conducive to effective model learning and prediction. Conversely, if the maximum filtration distance is too small, edges between different mers are difficult to form, and the 1-dimensional and 2-dimensional homology classes rarely change, failing to capture the topological relationships among mers in the sequence.

To address this, we first constructed a statistic that reflects the “average residue distance” in the sequence and used it as a reference for selecting the maximum filtration distance. Specifically, for each protein sequence, for each residue type, we calculated the distances between each residue and its nearest neighboring occurrence, then took the average, yielding 20 average distance values per sequence corresponding to the 20 residue types. These averages were then aggregated across all protein sequences, and a kernel density estimation (KDE) was performed to model the probability density distribution. The peak of this distribution, representing the main concentration of the data, was found to be approximately 11.8859, as shown in Figure 3a.

Based on this statistic, we conducted a finer grid search over maximum filtration distances ranging from 3 to 18 to systematically evaluate the impact of different parameter settings on model performance. The experiments covered multiple feature configurations, including: using only 1-mer features; incorporating 2-mer features in addition to 1-mer and considering 0 to 1-dimensional as well as 2-dimensional cycle group; and various combinations of 0 to 2-dimensional homology for 2-mer features. The corresponding model performance results are summarized in Figure 2. Experimental results indicate that a maximum filtration distance of 8 yields the best predictive performance. Accordingly, we selected this configuration as the final parameter for extracting persistent GLMY homology features.

These results demonstrate that the choice of maximum filtration distance has a significant influence on model performance. Setting the maximum filtration distance to 8 achieves optimal performance, indicating that local interactions among residues within approximately 8 positions are most relevant for functional prediction. Distances that are too large (> 12) lead to oversimplified topological features, while distances that are too small (< 5) fail to capture sufficient sequence topological information.

### 3.3 Correlation Analysis Between 1-mer Homology Features and Protein Symmetry

We performed a systematic statistical analysis of the 1-mer persistent GLMY features to investigate whether there exist stable and interpretable topological differences among different protein symmetry categories. A differential scoring function, score, was introduced for this purpose (for details, see Methods Section 5.2).

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//8ef06af9-455d-4e5e-8cfc-e8d4f690f010/markdown_3/imgs/img_in_chart_box_276_212_865_556.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A12Z%2F-1%2F%2Fc5aabe675ec689d8c6b98552696c9b9ad4754a99c13012a6ba7e258fce7ae072" alt="Image" width="49%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//8ef06af9-455d-4e5e-8cfc-e8d4f690f010/markdown_3/imgs/img_in_chart_box_275_564_866_850.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A12Z%2F-1%2F%2F18b29e2f50bc7c37ea535fac6ebf56f1cbeeb858573e4f34af850cbeab55b664" alt="Image" width="49%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//8ef06af9-455d-4e5e-8cfc-e8d4f690f010/markdown_3/imgs/img_in_chart_box_274_855_868_1102.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A12Z%2F-1%2F%2F72a5098eec8749b18de923cd73ed33f197e66b1625fb6b8301bf3e4452b1e54a" alt="Image" width="49%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 3 Kernel density estimation of average residue distances in protein sequences and distributions of score values. a For each amino acid type, the average distance from each residue to its two nearest identical residues was calculated. The blue bars represent the normalized distance distribution histogram, the red curve shows the Gaussian KDE, and the green dashed line indicates the peak of the probability density function at 11.89 residues. This peak reflects the most common spacing between identical residue pairs in protein sequences, revealing the periodicity of residue distribution. The x-axis denotes the average distance (in number of residues), and the y-axis represents the probability density. b Strip plot of score values across different symmetry categories. This plot shows the distribution of score values for 20 standard amino acids in various protein symmetry categories. Each point represents the score of a particular amino acid within the corresponding symmetry category, with different colors indicating different amino acid types (see legend). The x-axis denotes symmetry categories, and the y-axis represents the score value. c Violin plot of score distributions for each amino acid. Each violin illustrates the distribution of score values of that amino acid across all symmetry categories, where the width of the violin reflects the density, and the thick line indicates the interquartile range. The x-axis shows the single-letter codes of amino acids, and the y-axis represents the score value. Higher score values indicate greater topological differences of the residue in a specific symmetry category compared to others. These two plots reveal the differential distribution patterns of amino acids in proteins with different symmetry types.</div> </div>


For each residue type, score values were calculated across all symmetry categories. The results are visualized using strip plots and violin plots in Figure 3b and c, with detailed numerical values provided in Appendix Table 2.

From the strip plot, the following observations can be made:

1. Low or non-symmetric categories (e.g.,  $ C_{1}, C_{2} $) show almost no significant residue-specific  $ \beta_{1} $ signal, with topological structures being dispersed and lacking stable repetitive patterns.

2. Mid-to-low order rotational symmetries  $ (C_{3}-C_{6}) $ already exhibit certain heterogeneity at the sequence level.

3. High-order rotational symmetries  $ (C_{7}-C_{9}, C_{10}-C_{17}) $ are strongly dominated by a few residues (e.g., C, H, M, W), presenting highly concentrated and long-lived loops in 1-mer  $ \beta_{1} $ homology.

4. Compared with the same-order  $ C_n $ symmetries, the corresponding  $ D_n $ categories still retain strong  $ \beta_1 $ signals. However, due to the introduction of mirror symmetry, the residue combinations become more complex, and the topological features are more dispersed across scales. This phenomenon constitutes a key topological evidence distinguishing  $ C $ and  $ D $ symmetries.

5. Extremely high-symmetry categories such as H and T exhibit nearly "lattice-like" residue distance patterns, corresponding to extremely concentrated  $ \beta_{1} $ topological signals.

From the violin plot, it is evident that residues C, H, M, P, and W show large differences in their score values across different symmetry types, serving as sequence topological fingerprints that distinguish protein complexes with different symmetries. This indicates that the persistent GLMY homology features extracted from sequences are associated with protein structural symmetries; specifically, the 1-mer persistent GLMY homology  $ \beta_{1} $ features are significantly separable across different symmetry classes.

The persistent GLMY homology features enable the model architecture to better learn the topological differences induced by the relative positional distributions of identical residues in sequences across different symmetry types. These results demonstrate the meaningfulness and interpretability of extracting sequence topological features.

### 3.4 Ablation Study

To assess the importance of different features and module designs in the GLMYsymm model, we conducted ablation experiments by removing certain features, replacing the feature fusion module, and adjusting the feature concatenation strategies. These experiments systematically evaluated the impact of each modification on the model's performance on the test set, thereby validating the rationality and effectiveness of the overall model architecture. The results of these experiments are shown in Figure 6.

#### 3.4.1 Evaluation of Individual Feature Types: ESM2 and Persistent GLMY homology

To assess the contribution of GLMY homology-based sequence topology features to model performance, we first evaluated the model using single-feature inputs. Specifically, we constructed a model that only utilizes ESM2-derived sequence embeddings as input. Under this setting, with only a single feature type, the model employing an MLP classifier achieved a Macro AUC-PR of 0.5354 on the test set.

Subsequently, we constructed a model that uses only persistent GLMY features, also employing an MLP as the prediction network. This model achieved a Macro AUC-PR of 0.1647 on the test set.

Building upon these results, we further combined ESM2 features and persistent GLMY homology features as input, while keeping the prediction head architecture unchanged (still using an MLP). The feature-fusion model achieved a Macro AUC-PR of 0.5921 on the test set, demonstrating a clear improvement over models using either single feature alone.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//98ea6338-3e12-4e29-b584-42d767c4f25e/markdown_0/imgs/img_in_chart_box_229_152_608_405.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A11Z%2F-1%2F%2Fc2cbe1ae09da4552929a2f8262bf58abc2cc135a83d7edb1b1c86e79e9614588" alt="Image" width="31%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//98ea6338-3e12-4e29-b584-42d767c4f25e/markdown_0/imgs/img_in_image_box_618_152_942_404.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A11Z%2F-1%2F%2F12dcbce2f799ea27f8f9da30d22c94bf1fdec125a1df548518102f57f5e1b367" alt="Image" width="27%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 4 GLMYsymm test set results for different model variants and the corresponding confusion matrix. a In the bar chart, the x-axis represents different tested models: "GLMY_only" indicates the model using only GLMY features; "QUEEN" and "Seq2Symm" denote the baseline methods compared with GLMYsymm in this study; "Concatenate First" represents the model where persistent GLMY features and ESM2 features are first concatenated before prediction; "ESM2_only" indicates the model using only ESM2 features; "Transformer" denotes the variant where the MLP architecture in GLMYsymm is replaced with a Transformer; "GLMYsymm_test2" shows GLMYsymm performance on the test set after removing samples appearing in the QUEEN training set; "GLMYsymm" is the proposed model; "GLMYsymm_test1" shows GLMYsymm performance after removing samples appearing in the Seq2Symm training set. The models are ordered by Macro AUC-PR scores from lowest to highest. b The confusion matrix illustrates the classification performance of GLMYsymm on the test set. Each row represents the true label, and each column represents the predicted label. The color intensity indicates the percentage of samples of each true class predicted as each target class, ranging from dark blue (low percentage) to yellow (high percentage). Diagonal elements correspond to correctly classified samples, while off-diagonal elements show the distribution of misclassifications.</div> </div>


These results indicate that persistent GLMY homology features alone are insufficient to fully capture the semantic information of protein sequences. However, when used as a structured topological complement to ESM2 sequence embeddings, they effectively enhance the model's discriminative capability and further improve overall prediction performance. This finding validates the necessity and effectiveness of incorporating GLMY homology features as auxiliary information in the GLMYsymm model.

#### 3.4.2 Comparison between MLP and Transformer Architectures

In the previous experiments, we demonstrated that the combination of ESM2 features and persistent GLMY homology features yields the best predictive performance. Building upon this, we further compared two different feature fusion architectures, namely MLP and Transformer, to evaluate the impact of the fusion strategy on model performance.

In both comparative experiments, the input features consisted of the concatenation of GLMY features and ESM2 features, with a shared linear layer used as the prediction head. Under the MLP-based fusion architecture, the model achieved a Macro AUC-PR of 0.5921 on the test set.

Subsequently, we replaced the feature fusion module with a Transformer architecture to model potential interactions between the two feature modalities. Specifically, the concatenated fixed-length feature vector (512 dimensions) was reshaped into a sequence of 8 tokens, where 4 tokens originated from GLMY features and 4 tokens from ESM2 features. This tokenization was chosen to balance model expressivity and computational complexity: using too many tokens would significantly increase computational cost, while the main goal of introducing the Transformer in this study was to model potential interactions and limited relative positional information between the two feature types. In this setting, the Transformer module contained 8 attention heads and 2 encoder layers. The resulting model achieved a Macro AUC-PR of 0.5359 on the test set.

These results indicate that, for the current task, there are no significant higher-order interactions between ESM2 and GLMY features. In contrast, the MLP architecture is more effective in preserving and integrating the discriminative information from both feature types, thereby achieving superior predictive performance. This finding suggests that, given the current feature representations and task scale, a simple and stable MLP is more suitable as the feature fusion module.

#### 3.4.3 Comparison of Feature Concatenation Strategies

The previous experiments demonstrated that using both persistent GLMY features and ESM2 features can significantly improve model performance. However, the order of feature concatenation and dimensionality reduction during multi-source feature fusion remains an important consideration. To investigate this, we conducted comparative experiments evaluating different feature concatenation strategies.

We mainly considered two fusion strategies. The first strategy, “reduce-then-concatenate,” involves independently reducing the dimensionality of GLMY features and ESM2 features to 256 dimensions via separate linear layers or MLPs, followed by concatenation into a 512-dimensional representation. This representation is then fed into the MLP network and prediction head to perform symmetry classification. Under this setting, the model achieved a Macro AUC-PR of 0.5921 on the test set.

The second strategy, “concatenate-then-reduce,” involves first concatenating GLMY and ESM2 features directly and then compressing the high-dimensional combined features to 512 dimensions via an MLP before passing them through the prediction head. To ensure comparable network depth with the first strategy, the number of MLP layers in this scheme was doubled. However, the resulting model only achieved a Macro AUC-PR of 0.3410 on the test set, indicating a substantial performance drop.

These results indicate that for features originating from different sources with distinct statistical properties, the “reduce-then-concatenate” strategy more effectively preserves the discriminative information of each feature type, leading to superior predictive performance. Therefore, this feature concatenation approach was adopted as the final feature fusion scheme in the GLMYsymm model.

Overall, the ablation experiments demonstrate that GLMY features provide complementary information for sequence representation, that MLP-based fusion is more effective than Transformers for the current task in preserving discriminative information, and that reducing feature dimensions individually before concatenation yields better performance. The GLMYsymm architecture integrates the most effective and reasonable combination of feature types and model components.

### 3.5 Comparison with Other Methods

#### 3.5.1 Comparison with Seq2Symm

Seq2Symm, proposed by the David Baker group [14], is a deep learning method for predicting the symmetry of homomeric protein complexes based on protein sequence information. This method mainly leverages sequence embeddings extracted by ESM2 and multiple sequence alignment (MSA) features, followed by a classifier head to predict the symmetry type of protein complexes. In the original study, Seq2Symm achieved a Macro AUC-PR of 0.47 on its self-constructed test set.

To ensure a fair comparison, we evaluated Seq2Symm and GLMYsymm on a unified test set. Specifically, to avoid potential data leakage, we first removed any samples from the test set that appeared in the original Seq2Symm training set. Subsequently, predictions were performed on the reconstructed test set, and the Macro AUC-PR and Macro Precision metrics were calculated for both methods.

The results show that Seq2Symm achieved a Macro AUC-PR of 0.2950 and a Macro Precision of 0.4337 on this test set. In contrast, GLMYsymm achieved a Macro AUC-PR of 0.6179 and a Macro Precision of 0.6144, demonstrating a substantial improvement over Seq2Symm.

#### 3.5.2 Comparison with QUEEN

QUEEN [15] is a method designed to predict the quaternary assembly of homomeric protein complexes from single-chain sequences. Considering that homomeric complexes in practice mostly exhibit symmetry, the prediction task of QUEEN aligns closely with the symmetry prediction task addressed by GLMYsymm. Therefore, we conducted a comparative evaluation of QUEEN and GLMYsymm on the same unified test set.

Similarly, to prevent data leakage, we first removed any samples in the test set that appeared in the original QUEEN training set. As QUEEN predicts the copy number of chains in the complex rather than directly predicting symmetry types, we performed label mapping for the comparison. Specifically, we retained all  $ C_n $ (n = 1,2,3,4,5,6,7,8,10,12,14,24) and  $ D_n $ (n = 1,2,3,4,5,6,7) samples, mapping  $ C_n $ to a copy number of n and  $ D_n $ to 2n. Symmetry types that could not be uniquely mapped (e.g., helical H symmetry corresponding to multiple copy numbers, and tetrahedral T symmetry corresponding to 12 or 24 copies) were excluded from the test set.

After this preprocessing, predictions were made using both methods on the unified test set, and Macro AUC-PR and Macro Precision were computed. QUEEN achieved a Macro AUC-PR of 0.2372 and a Macro Precision of 0.6161, while GLMYsymm achieved 0.5591 and 0.6355, respectively.

Overall, these comparative experiments demonstrate that GLMYsymm outperforms both Seq2Symm and QUEEN on the unified test set, particularly in terms of the Macro AUC-PR metric, highlighting the effectiveness and robustness of the proposed method for homomeric complex symmetry prediction.

### 3.6 Performance Analysis of the Model

We analyzed the predictive performance of GLMYsymm on the model's test set. The results show substantial differences in performance across different symmetry orders. Overall, low-order symmetry types (C1–C5 and D2–D3) achieve better predictive performance than high-order symmetry types. Specifically, the average Macro AUC-PR for low-order symmetric proteins reaches 0.631, whereas the average Macro AUC-PR for high-order symmetric proteins is 0.557. These results indicate that GLMYsymm demonstrates more stable predictive capability in identifying low-order symmetric structures, while there remains room for improvement in predicting high-order symmetric structures.

In fact, within existing protein databases, low-order symmetric proteins are far more abundant than high-order symmetric proteins, and their structural types are also more diverse. A larger number of data samples provides the model with more learnable structural patterns, thereby enhancing its predictive performance for the corresponding categories. In addition, high-order symmetric structures often exhibit more complex spatial organizations and stricter geometric constraints, which further increases the difficulty of recognition. Therefore, differences in data scale and structural complexity may be important factors contributing to the imbalance in predictive performance across different symmetry orders.

### 3.7 Model Generalization

To validate the generalization capability of GLMYsymm, we conducted predictions on several proteins of different types that were not included in the dataset and obtained favorable results. The following presents representative examples.

##### Homologous Soluble Protein

The Crystal structure of an extracellular domain fragment of human BAFF is a homologous soluble protein (PDB ID: 1KD7). This protein was not included in the dataset used to train the model. The prediction result of GLMYsymm is consistent with the experimentally determined symmetry type recorded in the database, both indicating C3 symmetry. The structural visualization is shown in Fig. 5a.

Heterologous Insoluble Protein

The Crystal structure of BamB and BamA P3–5 complex from E. coli is a heterologous insoluble protein (PDB ID: 4XGA). As a heterologous complex, it was not considered during data selection. Since GLMYsymm is designed to predict symmetry types based on single-chain sequence information, the input consists of individual sequences. To evaluate the model's generalization ability, we treated protein 4XGA (Global Stoichiometry: A1B1) as two separate sequences for prediction. The predicted symmetry type for both chains was C1, indicating no symmetry-related assembly and a monomeric state in the structure. This result is consistent with the actual structure, demonstrating that GLMYsymm can not only predict symmetry types but also assist in stoichiometry-related analysis. The structure is shown in Fig. 5b.

##### Multi-Label Protein

In addition, we evaluated GLMYsymm on proteins capable of forming multiple symmetry types. For example, the Structure of CYP119 with T213A and C317H mutations (PDB ID: 5BV5) can naturally adopt C1, C2, and D2 symmetry states. Among the predicted results, the top three most probable symmetry types were C1, C2, and D2, which are consistent with the experimentally observed possibilities. This indicates that the multiple predicted symmetry types provided by GLMYsymm can all represent plausible structural states that the protein may adopt. The structure is shown in Fig. 5c.

In summary, the proposed GLMYsymm model not only performs well on the test dataset but also demonstrates strong performance on independent data outside the dataset. It shows accurate predictive capability across different protein types, including soluble and insoluble proteins, heterologous complexes, and proteins capable of forming multiple symmetry types, thereby indicating that GLMYsymm possesses strong generalization ability.

## 4 Discussion

In this study, we propose GLMYsymm, which, to the best of our knowledge, is the first model to apply persistent GLMY homology—a mathematical framework from topological data analysis—to the extraction of topological features from protein sequences. Through ablation studies and comparisons with Seq2Symm and QUEEN, we demonstrate that persistent GLMY homology-based sequence features capture richer information, enabling the model to more effectively learn sequence characteristics and predict protein symmetry. Nevertheless, several challenges remain to be addressed.

At present, homology-based approaches for sequence analysis have been successfully applied to small molecules such as DNA and RNA [20]. Because these sequences are relatively simple and consist of only four nucleotide types (A, T, C, and G), the number of possible symbol combinations is limited, making it feasible to compute higher-order k-mer features (i.e., combinations of multiple symbols). In contrast, protein sequences contain 20 different residue types, and the number of possible combinations grows exponentially, leading to a substantial increase in computational cost. How to efficiently compute higher-order mer features and systematically evaluate their impact on protein sequence representation remains an important direction for future research.

Severe class imbalance in the dataset negatively affects model performance. Although undersampling, oversampling, and label merging were employed during data preprocessing to mitigate the adverse effects of data imbalance, and Macro AUC-PR was adopted as an appropriate evaluation metric, the scarcity of structures for many symmetry classes remains an objective limitation. Additional data will be required in the future to further improve model robustness and predictive performance.

Despite these challenges, which are difficult to resolve in the short term, the feature extraction strategy based on persistent GLMY homology used in GLMYsymm provides valuable methodological insights for protein symmetry prediction and related research areas. The proposed approach demonstrates the potential of topological

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//98ea6338-3e12-4e29-b584-42d767c4f25e/markdown_4/imgs/img_in_image_box_230_197_898_737.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A16Z%2F-1%2F%2F49d18203e51967fe4513be00779848fe131bb9b6234b1c7aea390d9f76834489" alt="Image" width="56%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 5 Generalization performance of GLMYsymm. a Structural representation of the homologous soluble protein 1K7D. The symmetry type predicted by GLMYsymm is consistent with the experimentally determined symmetry, both being C3. b Structural representation of the heterologous insoluble protein 4XGA. The overall structure is asymmetric (C1). When each chain is predicted separately using GLMYsymm, the predicted symmetry type for both chains is C1, which is consistent with the actual structure. c The protein 5BV5 can form three symmetry states: C1, C2, and D2. The top three predicted symmetry types by GLMYsymm are C1, C2, and D2, which are consistent with the experimentally observed possibilities.</div> </div>


sequence representations and offers meaningful guidance for future studies in this domain.

## 5 Methods

In this work, we propose GLMYsymm, a method that leverages GLMY homology to extract topological features from protein sequences and integrates these with ESM2-derived sequence features to predict the symmetry type of homologous protein complexes. The overall model workflow is illustrated in Figure 1B. Below, we provide a detailed description of the feature extraction methods and the components of each module in the model.

### 5.1 GLMY homology

GLMY homology (also known as path homology) was proposed by Professor Shing-Tung Yau and his collaborators in 2012[21]. Its core innovation is to construct path complexes directly from directed graph structures, forming chain complexes through  $ \partial $-invariant paths, and subsequently defining homology groups. This allows algebraic topology tools to be naturally applied to directed networks while preserving intrinsic directional information. Moreover, since undirected networks can be considered a special case of directed networks (e.g., by replacing each undirected edge with a pair of bidirectional edges), GLMY homology can also be used to extract structural and geometric features from such data. But in undirected graphs, the presence of numerous symmetric edges often causes standard GLMY homology to collapse cycles formed

by symmetric edge pairs. To address this issue, we employ primitive GLMY homology, which is better suited for GLMY-homological analysis of undirected graphs. This framework preserves cycle information that would otherwise be eliminated by symmetry, following the approach described in [22]. Below we provide the formal definition of this GLMY homology.

Let  $  G = (V, E)  $ be a directed graph. An elementary allowed  $  n  $-path is a vertex sequence  $  i_0 i_1 \ldots i_n  $ such that for each consecutive pair of vertices  $  i_k  $ and  $  i_{k+1}  $, there exists a directed edge  $  i_k \to i_{k+1}  $ in  $  G  $. Let  $  \mathbb{Z}  $ be the coefficient ring. The free Abelian group generated by all elementary allowed  $  n  $-paths in  $  G  $ is denoted as  $  \mathcal{A}_n(G)  $, i.e.,

 $$ \mathcal{A}_{n}(G)=\langle e_{i_{0}i_{1}\ldots i_{n}}\mid i_{0}i_{1}\ldots i_{n}\mathrm{~i s~a n~a l l o w e d~p a t h}\rangle. $$ 

An elementary allowed path  $ i_{0}i_{1}...i_{n} $ in  $ \mathcal{A}_{n}(G) $ is denoted by  $ e_{i_{0}i_{1}...i_{n}} $. Elementary allowed paths of length n form the generators of  $ \mathcal{A}_{n}(G) $.

For each elementary allowed path  $ e_{i_0i_1\ldots i_n} $ in  $ \mathcal{A}_n(G) $, define the boundary operator:

 $$ \partial_{n}e_{i_{0}\ldots i_{n}}=\sum_{q=0}^{n}(-1)^{q}e_{i_{0}\ldots\widehat{i_{q}\ldots i_{n}}}, $$ 

In general, applying the boundary operator to an elementary allowed path of length n does not necessarily yield an allowed path. Therefore, we introduce the subgroup of  $ \mathcal{A}_{n}(G) $ consisting of  $ \partial $-invariant paths.

and define  $ \partial_{0}(e_{i_{0}})=0 $ when n=0. The operator  $ \partial_{n} $ is called the n-dimensional boundary operator.

Define

 $$ \Omega_{n}(G)=\{\nu\in\mathcal{A}_{n}(G)\mid\partial_{n}\nu\in\mathcal{A}_{n-1}(G)\}, $$ 

For $\Omega_n(G)$, we have $\partial_n\Omega_n(G) \subseteq \Omega_{n-1}(G)$ and $\partial_{n-1} \circ \partial_n = 0$. This forms a chain complex:

called the  $ \partial $-invariant path space.

The n-th GLMY homology group of a directed graph G is defined as

 $$ 0\xleftarrow{\partial_{0}}\Omega_{0}(G)\xleftarrow{\partial_{1}}\Omega_{1}(G)\xleftarrow{\partial_{2}}\Omega_{2}(G)\xleftarrow{\partial}\cdots.\Omega_{n-1}(G)\xleftarrow{\partial_{n}}\Omega_{n}(G)\xleftarrow{\partial}\cdots $$ 

The dimension of the homology group $H_{n}(G)$ is denoted by $\beta_{n}$, called the $n$-th Betti number of $G$.

 $$ H_{n}(G)=\ker(\partial_{n}:\Omega_{n}\to\Omega_{n-1})/\mathrm{i m}(\partial_{n+1}:\Omega_{n+1}\to\Omega_{n}). $$ 

GLMY homology of a directed graph can detect structural information within the graph:

•  $ \beta_{0} $: the number of connected components in the directed graph;

•  $ \beta_{1} $: the number of linearly independent 1-dimensional cycles formed by 1-paths that cannot be contracted or decomposed into smaller directed paths;

-  $ \beta_{n} $: the number of linearly independent n-dimensional cycles that cannot be expressed as boundaries of  $ (n+1) $-paths, i.e., the number of n-dimensional cavities generated by n-paths in G.

For directed graphs with relatively simple structure, higher-dimensional homology groups often vanish, while the corresponding cycle groups  $ \ker(\partial_n) $ may remain non-trivial. In some cases, we may use the dimension  $ c_n $ of the cycle group  $ Z_n $ in place of the Betti number  $ \beta_n $ to characterize structural features of graphs. In particular,  $ c_2 $ represents the dimension of the space of two-dimensional cycles, i.e., the number of chains generated by 2-paths in the directed graph whose boundaries vanish under the boundary operator.

#### 5.1.1 Persistent Homology and Barcodes

Given a sequence of nested directed graphs

Persistent homology considers the evolution of homology classes or Betti numbers along a sequence of nested directed graphs obtained according to a certain filtration.

for each  $ n \geq 0 $, we obtain a sequence of GLMY homology groups

 $$ G_{0}\subset G_{1}\subset G_{2}\subset\cdots\subset G_{N}=G, $$ 

 $$ H_{n}(G_{0})\longrightarrow H_{n}(G_{1})\longrightarrow H_{n}(G_{2})\longrightarrow\cdots\longrightarrow H_{n}(G_{N}). $$ 

The homomorphisms between consecutive homology groups are induced by the inclusion maps. If a homology class is born at time p and dies at time q (due to the addition of higher-dimensional paths whose boundary exactly forms a homology class, causing the disappearance of an existing class), we call p and q the birth and death times of this homology class. Plotting a horizontal line from p to q on the coordinate plane gives an n-dimensional barcode, and q - p is called the persistence of the homology class. Naturally, a homology class may never die after its creation; in this case, the barcode is a ray  $ (p, \infty) $ with infinite persistence. Plotting all n-dimensional barcodes on the same plane yields the persistent barcode for the sequence of nested directed graphs. From the persistent barcode, one can observe how the structure of the directed graph changes as the filtration scale varies.

For each residue or residue pair in a protein sequence, denoted by the letter  $ \pi $, we extract the positions of  $ \pi $ in the sequence and label them as

 $$ \pi_{k_{1}},\pi_{k_{2}},\cdots,\pi_{k_{n}}, $$ 

643 constructing a pairwise distance matrix D where

 $$ D_{i,j}=|k_{i}-k_{j}|. $$ 

Using  $ \pi_{k_1}, \pi_{k_2}, \cdots, \pi_{k_n} $ as the vertex set, we add an undirected edge between  $ \pi_{k_i} $ and  $ \pi_{k_j} $ whenever their distance is less than or equal to a given distance filtration value  $ d $, and assign the edge a weight of  $ |k_i - k_j| $. This yields the weighted undirected graph  $ \mathbf{G}(d) $ at filtration  $ d $. As  $ d $ increases, we obtain a nested sequence of undirected graphs:

 $$ \mathbf{G}(d_{0})\subset\mathbf{G}(d_{1})\subset\mathbf{G}(d_{2})\subset\cdots\subset\mathbf{G}(d_{N}). $$ 

Treating each  $ \mathbf{G}(d_i) $ as a directed graph, we compute the persistent GLMY homology of the nested sequence of directed graphs. The extracted barcode information (e.g., 0-dimensional, 1-dimensional, and 2-dimensional barcodes: maximum lifetime, mean lifetime, total lifetime, number of long-lived bars, minimum lifetime) is used as features for  $ \pi $ in the sequence. These features not only capture the positional information of  $ \pi $ within the sequence but also reflect the adjacency patterns of  $ \pi $ at different positions.

In the dashed box of Figure 1A, as an example, we construct a nested sequence of persistent undirected graphs for the letter P in a segment of a protein sequence, and present its 0-2-dimensional persistent barcodes.

#### 5.1.2 Feature Extraction

In GLMYsymm, we extract 1-mer GLMY homology features from protein sequences. The maximum filtration distance is set to  $ d_{max} = 8 $, and we compute the following:

661 • 0-dimensional and 1-dimensional persistent GLMY homology group;

662 • 2-dimensional persistent cycle group.

For each dimension, we compute the following barcode statistics: count, max_life, mean_life, total_life, long_count ( $ > d_{\text{max}}/2 $), min_life. Since there are 6 statistics per homology dimension and 3 dimensions (0D, 1D, 2D), this results in  $ 3 \times 6 = 18 $ features per 1-mer. With 20 amino acid types in a protein sequence, the total feature vector dimension for each sequence is  $ 18 \times 20 = 360 $.

For a fixed symmetry class c and a 1-mer (letter)  $ \pi $, we aggregate all 1-dimensional persistent diagrams of  $ \pi $ across sequences in this class, denoted as

### 5.2 Differential Scoring

We performed a systematic statistical analysis of 1-mer persistent GLMY features to investigate whether there exist stable and interpretable 1-mer topological differences among different protein symmetry classes.

First, protein sequences were categorized according to their structural symmetry. For each sequence, under the 1-mer setting, we constructed a nested sequence of undirected graphs based on the relative positional distances between residues, with the maximum filtration distance set to 8, and computed the persistent GLMY homology. For each symmetry class, we aggregated the 1-dimensional persistent diagrams ( $ \beta_{1} $) of all sequences in that class, which record the birth and death times of 1-dimensional homology classes induced by each 1-mer in the sequence.

To characterize the topological difference of a given 1-mer within a specific symmetry class relative to other classes, we introduce a scoring function based on persistent diagrams.

 $$ P D_{c,\pi}^{(\beta_{1})}=\{(b_{1},d_{1}),(b_{2},d_{2}),\ldots,(b_{N},d_{N})\}, $$ 

where  $ b_i \in \{0, 1, \ldots, 8\} $ indicates the birth time and  $ d_i \in \{1, \ldots, 9\} $ indicates the death time of the homology class. Note that, if a homology class does not disappear within the maximum filtration distance 8, its death time is set as  $ d_i = 9 $.

Based on this, we define a discrete birth-scale axis  $ b = 0, \ldots, 8 $, and define the 1-dimensional homology generation distribution vector of letter  $ \pi $ in symmetry class c as

 $$ \mathbf{v}_{c,\pi}^{(\beta_{1})}=\big(n_{c,\pi}(b=1),n_{c,\pi}(b=2),\ldots,n_{c,\pi}(b=8)\big), $$ 

where

 $$ n_{c,\pi}(b=k)=\#\{(b_{i},d_{i})\in P D_{c,\pi}^{(\beta_{1})}:b_{i}=k\}. $$ 

This vector characterizes the distribution of 1-dimensional homology classes induced by  $ \pi $ at different scales within the maximum filtration distance in symmetry class c.

Let C denote the set of all symmetry classes. For a fixed  $ \pi $, we define its mean generation distribution vector across all non-c classes as

 $$ \bar{\mathbf{v}}_{o t h e r s,\pi}^{(\beta_{1})}=\frac{1}{|\mathcal{C}|-1}\sum_{c^{\prime}\in\mathcal{C}\backslash\{c\}}\mathbf{v}_{c^{\prime},\pi}^{(\beta_{1})}. $$ 

In this work, we consider 15 symmetry classes, so  $ |\mathcal{C}| - 1 = 14 $. This mean vector can be interpreted as the “typical background” of the 1-dimensional homology distribution of letter  $ \pi $ across non-c symmetry classes.

Based on the above definitions, we introduce the following differential scoring function:

 $$ \mathrm{score}(c,\pi)=\left\|\mathbf{v}_{c,\pi}^{(\beta_{1})}-\bar{\mathbf{v}}_{o t h e r s,\pi}^{(\beta_{1})}\right\|, $$ 

where  $ \|\cdot\| $ denotes the Euclidean norm. This score measures the deviation of the 1-dimensional homology distribution induced by letter  $ \pi $ in symmetry class c relative to the average distribution in other classes. A larger score  $ (c,\pi) $ indicates that the 1-mer topology corresponding to this letter is more specific to the symmetry class c.

### 5.3 ESM2 Features

The protein language model ESM2 is currently a state-of-the-art pre-trained model for extracting protein sequence representations, capable of learning structural, functional, and evolutionary information directly from amino acid sequences. The core of the ESM2 approach is based on the Masked Language Modeling (MLM) task, which is a self-supervised learning objective built upon the Transformer architecture. Importantly, ESM2 does not require multiple sequence alignments (MSA) to capture evolutionary conservation information during training. At present, many studies  $ [23–25] $ leverage ESM2 embeddings for downstream tasks.

In this study, we used the esm2_t33_650M_UR50D model [26] to generate embeddings for each protein sequence. For a sequence of length L, the initial embedding is a matrix of dimension  $ L \times 1280 $, representing per-residue features. We then performed average pooling along the residue dimension to obtain a fixed-length vector of dimension  $ 1 \times 1280 $ for each sequence. Finally, this vector is passed through a multi-layer perceptron (MLP) to reduce its dimension to  $ 1 \times 256 $, which is subsequently concatenated with the GLMY homology features.

### 5.4 Macro AUC-PR

The Area Under the Precision-Recall Curve (Macro AUC-PR) is an important evaluation metric for multi-class tasks. It is computed by converting the multi-class problem into multiple binary classification problems. Specifically, for each class t, we treat it as the positive class and all other classes as negative, and then calculate the Precision and Recall values for that class:

 $$  Precision_{t}=\frac{TP_{t}}{TP_{t}+FP_{t}} $$ 

 $$ \mathrm{Recall}_{t}=\frac{TP_{t}}{TP_{t}+FN_{t}} $$ 

where $TP_{t}$, $FP_{t}$, and $FN_{t}$ denote true positives, false positives, and false negatives for class $t$, respectively. The Area Under the Precision-Recall Curve (AUC-PR) for class $t$ can be approximated using discrete points along the curve as:

 $$ \mathrm{AUC-PR}_{t}\approx\sum_{i=1}^{N-1}(\mathrm{Recall}_{t,i+1}-\mathrm{Recall}_{t,i})\cdot\mathrm{Precision}_{t,i+1} $$ 

where N is the number of threshold points and  $ (Recall_{t,i}, Precision_{t,i}) $ are the Precision-Recall values for class t at the i-th threshold. Finally, the Macro AUC-PR is obtained by averaging over all C classes:

 $$  Macro AUC-PR=\frac{1}{C}\sum_{t=1}^{C}AUC-PR_{t} $$ 

Since the dataset is highly imbalanced across different classes, Macro AUC-PR is chosen to evaluate the model's predictive capability. In cases where the model is biased towards predicting majority classes, overall accuracy might appear high, but the performance on minority classes can be poor. Macro AUC-PR treats all classes equally, taking both precision and recall into account, making it more suitable than single accuracy for imbalanced data.

Moreover, unlike Micro AUC-PR, Macro AUC-PR is not dominated by the majority classes. Therefore, it provides a fair and robust metric to evaluate and compare model performance across all classes.

### 5.5 Loss Function

The GLMYsymm model uses the Focal Loss (FL) as its loss function, which is computed as follows. For class t, its Effective Number weight  $ w_{t} $ is defined as:

 $$ w_{t}=\frac{1-\beta^{n_{t}}}{1-\beta} $$ 

where  $ n_t $ denotes the number of samples in class  $ t $, and  $ \beta \in (0,1) $ is a hyperparameter controlling the degree of weight disparity. A larger  $ \beta $ results in more pronounced weight differences, giving greater attention to minority classes. The weights are then normalized:

 $$ \alpha_{t}=\frac{w_{t}}{\sum_{i}w_{i}} $$ 

The Focal Loss is expressed as:

 $$ FL(p_{t})=-\alpha_{t}\left(1-p_{t}\right)^{\gamma}\log(p_{t}) $$ 

where  $ p_t $ is the predicted probability for the true class,  $ \alpha_t $ is the normalized class weight based on the effective number of samples for class  $ t $, and  $ \gamma $ is the focusing parameter. In this study, we set  $ \gamma = 3 $ to emphasize hard-to-classify samples.

In the extremely imbalanced scenarios considered in this work, Focal Loss demonstrates strong adaptability and effectively enhances the model’s discriminative ability on minority classes.

## 6 Conclusion

Accurate prediction of protein complex symmetry is of great importance for understanding the assembly mechanisms of multimeric protein structures, functional analysis, and structure quality assessment. Given the strong correlation between protein homology and structural symmetry, this study focuses on homologous protein complexes and systematically investigates the problem of symmetry prediction for homologous protein assemblies. We propose GLMYsymm, a single-sequence model that predicts the symmetry of homologous protein complexes by extracting sequence topological features using persistent GLMY homology and integrating them with ESM2-derived sequence features.

In terms of feature construction, we systematically evaluated multiple parameter configurations and feature extraction strategies for persistent GLMY homology. The best performance was achieved using 1-mer-based sequence topological features with a maximum filtration distance of 8, incorporating homological information in dimensions 0 and 1 together with the dimension of the 2-cycle group  $ c_2 = \text{dim} \text{ker}(\partial_2) $. Furthermore, we analyzed the distribution of 1-mer persistent GLMY homology  $ \beta_1 $ features corresponding to different residue types across symmetry classes. The statistical results demonstrate clear separability of these features among different symmetry categories, revealing an intrinsic relationship between sequence topology and complex symmetry from a topological perspective. This observation provides further insight into the effectiveness of persistent GLMY homology features in protein sequence analysis.

Through a series of ablation studies, we determined the final architecture of GLMYsamm. Specifically, persistent GLMY homology features and ESM2 features are first reduced in dimensionality independently, then concatenated and fused through an MLP-based architecture, followed by a prediction head to determine the symmetry of protein complexes. Experimental results indicate that this design effectively integrates semantic sequence information with topological structural information while maintaining model stability.

Under a unified test set and strict prevention of data leakage, we compared GLMYsymm with two representative methods, Seq2Symm and QUEEN. The results show that GLMYsymm achieves an improvement of approximately 0.32 in Macro AUC-PR, demonstrating its superior performance and strong generalization ability in predicting the symmetry of homologous protein complexes.

The main innovations of GLMYsymm lie in two aspects. First, this work is the first to introduce persistent GLMY homology from mathematical topology into protein

sequence analysis, enabling the extraction of sequence information from a topological perspective and its successful application to protein symmetry prediction. Second, GLMYsymm operates entirely on single-sequence input, without relying on protein three-dimensional structural information or multiple sequence alignment (MSA), thereby substantially reducing data requirements and computational cost while maintaining strong predictive performance. These characteristics endow GLMYsymm with significant extensibility and practical applicability, and provide new perspectives and methodologies for future research on topological sequence modeling and structure–function prediction in bioinformatics.

All data used in this study, including symmetry labels and dataset splits, are available for download from the “Source Code” section of the website at http://mialab.ruc.edu.cn/GLMYsymmServer/.

## 7 Data availability

## 803 8 Code availability

The source code for the model architecture and the corresponding configuration files are available in the “Source Code” section of the website at http://mialab.ruc.edu.cn/GLMYsymmServer/. Detailed instructions for model usage are provided in the README file.

## 9 Acknowledgements

The authors thank the anonymous reviewers for their valuable suggestions. This review was supported by Public Computing Cloud, Renmin University of China.

## References

[1] Duarte, J.M., Dutta, S., Goodsell, D.S., Burley, S.K.: Exploring protein symmetry at the rcsb protein data bank. Emerging topics in life sciences 6(3), 231–243 (2022)

[2] Anfinsen, C.B.: Principles that govern the folding of protein chains. Science 181(4096), 223–230 (1973)

[3] Monod, J., Wyman, J., Changeux, J.-P.: On the nature of allosteric transitions: a plausible model. Journal of molecular biology 12(1), 88–118 (1965)

[4] Goodsell, D.S., Olson, A.J.: Structural symmetry and protein function. Annual review of biophysics and biomolecular structure 29(1), 105–153 (2000)

[5] Marianayagam, N.J., Sunde, M., Matthews, J.M.: The power of two: protein dimerization in biology. Trends in biochemical sciences 29(11), 618–625 (2004)

[6] Balaji, S.: Internal symmetry in protein structures: prevalence, functional relevance and evolution. Current opinion in structural biology 32, 156–166 (2015)

[7] Kim, C., Basner, J., Lee, B.: Detecting internally symmetric protein structures. BMC bioinformatics 11(1), 303 (2010)

[8] Myers-Turnbull, D., Bliven, S.E., Rose, P.W., Aziz, Z.K., Youkharibache, P., Bourne, P.E., Prlić, A.: Systematic detection of internal symmetry in proteins using ce-symm. Journal of molecular biology 426(11), 2255–2268 (2014)

[9] Pagès, G., Grudinin, S.: Deepsymmetry: using 3d convolutional networks for identification of tandem repeats and internal symmetries in protein structures. Bioinformatics 35(24), 5113–5120 (2019)

[10] Jacobson, M., Sali, A.: Comparative protein structure modeling and its applications to drug discovery. Annu. Rep. Med. Chem 39(85), 259–274 (2004)

[11] Jumper, J., Evans, R., Pritzel, A., Green, T., Figurnov, M., Ronneberger, O., Tunyasuvunakool, K., Bates, R., Žídek, A., Potapenko, A., et al.: Highly accurate protein structure prediction with alphafold. Nature 596(7873), 583–589 (2021)

[12] Ovchinnikov, S., Park, H., Varghese, N., Huang, P.-S., Pavlopoulos, G.A., Kim, D.E., Kamisetty, H., Kyrpides, N.C., Baker, D.: Protein structure determination using metagenome sequence data. Science 355(6322), 294–298 (2017)

[13] Liu, L., Zhang, S., Xue, Y., Ye, X., Zhu, K., Li, Y., Liu, Y., Gao, J., Zhao, W., Yu, H., et al.: Technical report of helixfold3 for biomolecular structure prediction. arXiv preprint arXiv:2408.16975 (2024)

[14] Kshirsagar, M., Meller, A., Humphreys, I.R., Sledzieski, S., Xu, Y., Dodhia, R., Horvitz, E., Berger, B., Bowman, G.R., Ferres, J.L., et al.: Rapid and accurate prediction of protein homo-oligomer symmetry using seq2symm. Nature Communications 16(1), 2017 (2025)

[15] Avraham, O., Tsaban, T., Ben-Aharon, Z., Tsaban, L., Schueler-Furman, O.: Protein language models can capture protein quaternary state. BMC bioinformatics 24(1), 433 (2023)

[16] André, I., Strauss, C.E., Kaplan, D.B., Bradley, P., Baker, D.: Emergence of symmetry in homooligomeric biological assemblies. Proceedings of the National Academy of Sciences 105(42), 16148–16152 (2008)

[17] Matsunaga, Y., Koike, R., Ota, M., Tame, J.R., Kidera, A.: Influence of structural symmetry on protein dynamics. PLoS One 7(11), 50011 (2012)

[18] Berman, H.M., Westbrook, J., Feng, Z., Gilliland, G., Bhat, T.N., Weissig, H., Shindyalov, I.N., Bourne, P.E.: The protein data bank. Nucleic acids research 28(1), 235–242 (2000)

[19] Steinegger, M., Söding, J.: Mmseqs2 enables sensitive protein sequence searching for the analysis of massive data sets. Nature biotechnology 35(11), 1026–1028 (2017)

[20] Hozumi, Y., Wei, G.-W.: Revealing the shape of genome space via k-mer topology. arXiv preprint arXiv:2412.20202 (2024)

[21] Grigor'yan, A., Lin, Y., Muranov, Y., Yau, S.-T.: Homologies of path complexes and digraphs. arXiv preprint arXiv:1207.2834 (2012)

[22] Li, J., Muranov, Y., Wu, J., Yau, S.-T.: Primitive path homology. Data Analytics and Topology 1(1), 1–15 (2025)

[23] Hou, L., Qin, H., Zhang, X., Zhang, Y.: Protein function prediction based on the pretrained language model esm2 and graph convolutional networks. In: 2024 IEEE International Symposium on Parallel and Distributed Processing with Applications (ISPA), pp. 1776–1781 (2024). IEEE

[24] Zhang, H.-Q., Liu, S.-H., Yu, J.-W., Li, R., Ye, D.-X., Jin, Y.-T., Huang, C.-B., Deng, K.-J.: Drugpred: An ensemble learning model based on esm2 for predicting

potential druggable proteins. Future Generation Computer Systems 170, 107801 (2025)

[25] Luo, Z., Wang, R., Sun, Y., Liu, J., Chen, Z., Zhang, Y.-J.: Interpretable feature extraction and dimensionality reduction in esm2 for protein localization prediction. Briefings in Bioinformatics 25(2), 534 (2024)

[26] Lin, Z., Akin, H., Rao, R., Hie, B., Zhu, Z., Lu, W., Smetanin, N., Santos Costa, A., Fazel-Zarandi, M., Sercu, T., Candido, S., et al.: Language models of protein sequences at the scale of evolution enable accurate structure prediction. bioRxiv (2022)

