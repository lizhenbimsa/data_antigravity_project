Full Length Article

# Topology structure optimization of reservoirs using GLMY homology

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//0e34657e-d358-4bbe-8d24-e0458e69c27d/markdown_0/imgs/img_in_image_box_1002_297_1057_353.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A38Z%2F-1%2F%2F92213291ff06134c59e1557c8a200a8521c3376d09b1a9740958833c71b67227" alt="Image" width="4%" /></div>


Yu Chen $ ^{a} $, Shengwei Wang $ ^{b} $, Hongwei Lin $ ^{a,*} $

 $ ^{a} $ School of Mathematical Sciences, Zhejiang University, Hangzhou, 310058, China

 $ ^{b} $ Polytechnic Institute of Zhejiang University, Hangzhou, 310015, China

#### ARTICLE INFO

Keywords:

Reservoir computing

Echo state network

GLMY homology

Computational topology

Structure optimization

## A B S T R A C T

Reservoirs are efficient networks for time-series processing. It is well known that the network structure is one of the determinants of their performance. However, the topological structure of reservoirs, as well as their performance, is hard to analyze due to the lack of suitable mathematical tools. In this paper, we study the topological structure of reservoirs using persistent GLMY homology theory and develop a method to improve their performance. Specifically, we find that reservoir performance is correlated with the one-dimensional GLMY homology groups. Then, we develop a reservoir structure optimization method by modifying the minimal representative cycles of one-dimensional GLMY homology groups. Finally, through experiments, we validate that the performance of reservoirs is jointly influenced by the reservoir structure and the periodicity of the dataset.

### 1. Introduction

Neural networks, inspired by biological brains, have become a cornerstone in artificial intelligence and machine learning, enabling solutions to complex tasks in image recognition, natural language processing, and predictive analytics (Goodfellow et al., 2016; LeCun et al., 2015). Their structure—including layer count, neuron connectivity, and activation function type—directly determines functional capabilities, with early studies establishing foundational concepts like weight roles and nonlinearity from activation functions (Hornik et al., 1989). Moreover, a recent study has proposed weight-agnostic neural networks (Gaier & Ha, 2019), which can perform learning tasks without weight training, relying only on structural optimization. This shows that the structure of neural networks plays an essential role. However, as real-world problem complexity grows, a deeper understanding of task-optimized neural network structure design is needed.

The continuous improvement and optimization of neural network structures hold profound and far-reaching significance in advancing the practical application and theoretical development of artificial intelligence. From a performance perspective, a well-optimized structure can significantly enhance the network's ability to extract features and learn patterns, enabling it to achieve higher accuracy and robustness in handling complex tasks. In terms of resource efficiency, optimizing the number of layers, neuron density, and connectivity patterns can effectively reduce the model's parameter scale and computational complexity. Additionally, structural optimization plays a crucial role in enhancing the adaptability and interpretability of neural networks. By adjusting the structure to match the characteristics of specific tasks, the network's generalization ability across different domains can be improved. Meanwhile, rational structural design can reduce the "black-box" nature of neural networks—for instance, through modular structural design, researchers can more clearly trace the flow of information and the contribution of each module to the final output, laying the foundation for interpreting the internal working mechanism of the network (Montavon et al., 2018). Moreover, recent studies indicate that the topology of a network's structure significantly impacts its performance, suggesting that understanding and designing network architectures from a topological perspective is a crucial and effective approach (Zhang et al., 2024).

Reservoir Computing (RC), as a distinctive paradigm within the machine learning landscape, has rapidly gained traction and widespread adoption owing to its inherent advantages that address key challenges in traditional neural network deployment. Specifically, RC exhibits a compact model architecture, which minimizes the demand for storage resources; enables rapid training processes by focusing optimization only on the readout layer rather than the entire network, significantly reducing computational overhead; delivers high prediction accuracy across various time-series and nonlinear tasks; and maintains excellent generalization performance when faced with unseen or noisy data—these attributes collectively make RC a preferred choice for applications ranging from real-time signal processing to complex system prediction (Jaeger, 2001a; Lukoševičius & Jaeger, 2009). Nevertheless, a critical limitation of RC lies in its "black-box" nature, primarily stemming from the lack of clear interpretability regarding the internal dynamics of the reservoir. The reservoir, typically composed of a large

number of randomly connected neurons, operates through complex non-linear interactions, making it difficult to establish a direct link between its structural characteristics (e.g., connectivity density, neuron type, and topological arrangement) and its prediction performance. Consequently, investigating how the internal structure of the reservoir influences its prediction ability has become an increasingly attractive and essential research direction, as resolving this issue could not only unlock the potential to further optimize RC performance but also enhance its reliability and applicability in critical domains where interpretability is essential (Pathak et al., 2018).

In practice, a reservoir is usually regarded as a digraph. In previous studies, the lack of mathematical tools to study the topology of digraphs made it difficult to topologically optimize the structure of the reservoir from an algebraic topological perspective. Now with the rapid development of GLMY homology theory, there are new effective tools for topology optimization of digraphs. The GLMY homology, also known as path homology and initially proposed by Grigor'yan et al. (2012), represents a significant development in computational topology. As complex systems—ranging from social networks and neural connections to transportation and biochemical pathways—are increasingly modeled using directed graphs (digraphs), traditional homology theories, which are designed for undirected topological spaces, prove inadequate. They fail to capture crucial directional information, such as information flow, influence propagation, or causal relationships. GLMY homology overcomes this fundamental limitation by constructing a chain complex specifically based on directed paths within digraphs. Its distinct sensitivity to edge directions allows it to capture the flow and hierarchical organization of these paths, revealing hidden structural features and topological properties that are otherwise invisible to standard methods. In real-world digraphs, edge orientation often conveys critical information, such as influence direction in a social network or material flow in a manufacturing process. The directional awareness of GLMY homology provides a more accurate and nuanced representation of the digraph's underlying topology. Persistent GLMY homology (Chowdhury & Mémoli, 2018), a further development of GLMY homology, enhances its analytical capabilities by tracking how directed path structures evolve as parameters, such as edge weights, change. Through persistent GLMY homology, researchers can effectively capture structural features encoded in both edge directions and weights, making it a powerful tool for analyzing dynamic and weighted complex systems. This framework provides a new lens through which to analyze the structural properties of complex networks, particularly those where directionality is a defining feature.

Therefore, in this study, since a reservoir can be represented as a digraph, we present a novel method for reservoir optimization using GLMY homology. Firstly, we show that adding rings $ ^{1} $ in the reservoir digraph can improve the orthogonality of the reservoir adjacency matrix, hence enhancing the reservoir's predictive capacity. Mathematically, a directed ring structure with uniform weights corresponds to a (scaled) permutation adjacent matrix. Permutation matrices are a fundamental subclass of orthogonal matrices. As highlighted in Gallicchio and Micheli (2019), structured reservoirs based on permutation matrices provide a particularly advantageous architectural setting by ensuring stable signal propagation and mitigating the vanishing gradient problem through their near-orthogonal nature. Moreover, Rodan and Tino (Rodan & Tino, 2010) introduced the Simple Cycle Reservoir (SCR), proving that a deterministic ring topology is sufficient to capture complex temporal features and can reach near-optimal memory capacity. And theoretical studies in Stockdill and Neshatian (2016) also confirm that rings are essential for replicating the memory-leaking and state-holding properties required for temporal processing. By increasing the number of rings, one can effectively increase the number of paths for information to recirculate, which provably maintains the “fading memory” property over longer time horizons compared to purely random connections. Hence, these studies serve as the fundamental motivation for our approach. Our strategy focuses on strategically modifying the edge directions within the digraph to deliberately increase the number of rings, thereby optimizing the reservoir's performance. Moreover, since these rings are a special type of representative cycle of one-dimensional GLMY homology, we can achieve our target by considering a subset of representative cycles of 1D GLMY homology, i.e., the subset consists of all rings. In other words, our optimization strategy, which focuses on increasing the number of rings, is theoretically motivated by the advantages of cyclic topologies. According to the SCR theory (Rodan & Tino, 2010), rings provide the necessary feedback loops for stable fading memory. By leveraging GLMY homology, we provide a systematic way to enhance these critical cyclic structures in an initially random reservoir, effectively moving its topology toward a more organized, high-memory-capacity state. We also validate through experiments that the prediction ability of a reservoir is related to both its structure and the topological features of the dataset.

In summary, the main contributions of our study are as follows:

• Adding rings inside the reservoir digraph can improve the orthogonality of the reservoir adjacency matrix, which is equivalent to increasing a certain type of representative cycle of GLMY homology.

• We optimize the structure of reservoirs by expanding a certain subset of representative cycles (rings) of 1D GLMY homology.

• It is validated by experiments that the performance of reservoirs is related to both their structure and the characteristics of the dataset.

The remainder of this paper is organized as follows: We provide an overview of reservoir computing, reservoir optimization and GLMY homology in Section 2. Then, we present the key tools and the proposed method in Sections 3 and 4. In Section 5, we show our experimental results and provide some discussions. Section 6 presents the conclusions of this study.

### 2. Related work

In this section, we provide some related work about optimizing reservoir structure, the GLMY homology, and some of its applications.

### 2.1. Reservoir computing and reservoir optimization

Reservoir computing (RC) has emerged as a powerful and widely adopted machine learning paradigm over the past few decades, gaining considerable attention for its effectiveness in handling complex time-dependent data. Its application has extended across various domains, including time series prediction, nonlinear system identification (Yao et al., 2019), and speech recognition (Skowronski & Harris, 2007). The core strength of RC lies in its architectural simplicity: a fixed, randomly generated recurrent neural network (the reservoir) projects the input into a high-dimensional feature space, while only a simple linear readout layer is trained. This separation of the nonlinear dynamics of the reservoir from the linear readout training process is a key reason for its exceptional computational efficiency and rapid training speed. This efficiency has led to remarkable results, such as those demonstrated by Jaeger and Haas (2004), who applied RC to chaotic time series prediction and achieved computational accuracy two orders of magnitude higher than traditional approaches. Beyond its core architecture, variations have further expanded its capabilities. For instance, Shougat et al. (2021) employed Hopf oscillators as an intermediate reservoir, successfully demonstrating robustness to noise and preservation of predictive accuracy even with reduced training costs. In the financial sector, Wang et al. (2021) utilized an RC network for forecasting stock market prices, where comparative experiments against several classical models—including long short-term memory (LSTM) networks—showed

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e738631c-5b98-42b7-bd0f-18d7277ece2c/markdown_0/imgs/img_in_image_box_201_143_992_534.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A38Z%2F-1%2F%2F8e03052156761b10a2033cf680131d00be52a8bb76b28e4e7b4031bf29cbd09d" alt="Image" width="66%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 1. Illustration of the flowchart of our method and experimental procedures.</div> </div>


the RC model consistently achieving lower mean-squared error (MSE) and mean absolute error (MAE), alongside higher  $ R^{2} $ scores. This work also provided insights into how distinct reservoir initialization strategies influence predictive accuracy, further highlighting the critical role of network dynamics in financial forecasting.

A reservoir is usually represented as a digraph (called the reservoir digraph). In most implementations, reservoir parameters and topological configurations are initialized stochastically. However, such stochastic initialization frequently produces unstable dynamical behavior, necessitating extensive empirical trial-and-error to obtain a well-conditioned network. Therefore, beyond investigating the deployment of reservoirs in prediction tasks, the design of high-quality reservoir architectures has emerged as both a major challenge and a focal point of contemporary research. Gallicchio and Micheli (2019) assessed the impact of constrained reservoir topologies—namely permutation, ring, and chain structures—within Deep Echo State Networks (DeepESNs) on time series forecasting performance. Through a systematic comparison against conventional sparsely random reservoirs and shallow ESNs, demonstrated that embedding structurally sparse topologies in deep reservoir computing constitutes a straightforward yet effective strategy for enhancing temporal modeling accuracy. Cui et al. (2012) investigated the interplay between reservoir topology and predictive performance by constructing reservoirs with small-world, scale-free, and hybrid small-world/scale-free structures. Experimental results demonstrate that manually designed reservoir networks deliver superior predictive accuracy and possess a broader spectral radius, while their short-term memory capacity remains comparable to that of traditional models. Roeschies and Igel (2010) proposed an evolutionary algorithm that optimizes reservoir-network architectures for specific problem classes, resulting in substantial gains in predictive performance. Sun et al. (2012) introduced a deterministic echo state network architecture featuring a loop reservoir with adjacent feedback connections. This simplified design builds upon the basic loop reservoir structure by incorporating regular adjacent feedback, requiring optimization of only a single parameter. The approach significantly reduces the complexity of ESN implementation while maintaining computational capabilities. These results, together with previous studies, confirm that the structure of a reservoir is pivotal in determining its functionality and overall effectiveness.

In a broader optimization context, surrogate-based and response surface methodologies (RSM) have been extensively studied in engineering design and system optimization. These approaches typically construct an explicit or implicit approximation of a performance landscape over a continuous parameter space, and subsequently perform optimization on the learned surrogate model. Representative examples include (Ahmed et al., 2024, 2025), where response surfaces are employed to guide design optimization under computational or experimental constraints. While effective for continuous and parameterized systems, such approaches fundamentally differ from our concern: the reservoir structure considered in this work is discrete, graph-based, and non-differentiable. We will focus on topology-level structural modifications guided by algebraic-topological invariants, providing a complementary optimization paradigm that is particularly suitable for discrete dynamical networks.

### 2.2. GLMY homology and its applications

GLMY homology represents a significant extension of classical homology theory, specifically developed to analyze directed or asymmetric interactions in digraphs (Grigor'yan et al., 2012) and hypergraphs (Grigor'yan et al., 2019). This framework has spawned several theoretical developments, such as homotopy theory for digraphs (Grigor'yan et al., 2014), discrete Morse theory on digraphs (Lin et al., 2021), and path homology theory for multigraphs and quivers (Grigor'yan et al., 2018). Notable computational advances include the persistent path homology for networks proposed by Chowdhury and Mémoli (Chowdhury & Mémoli, 2018), which offers a novel approach to digraph analysis in topological data analysis, and an efficient algorithm for computing one-dimensional persistent path homology of digraph filtrations by Dey et al. (2022). In contrast to traditional simplicial complexes, GLMY homology offers a unique set of dimensional fingerprints. These fingerprints are instrumental in unearthing the intrinsic structural information hidden within networks, providing a more detailed view of network architecture. This theoretical framework has demonstrated its practical utility across a diverse range of applications, such as modeling intricate biological systems (Feng et al., 2024), analyzing material properties and structures (Liu et al., 2023), analyzing discrete planar vector fields (Chen & Lin, 2025), and understanding complex networks (Chowdhury et al., 2019, 2020). Persistent GLMY homology represents a further advancement in this area. By tracking how topological features change and evolve across various filtration processes, it allows us to identify and analyze topological patterns in networks (Chowdhury & Mémoli, 2018). This capability significantly enhances our understanding of network behavior and evolution.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//7ec9f4cc-7dda-4e2b-a357-5967f232066c/markdown_0/imgs/img_in_chart_box_245_134_589_412.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A38Z%2F-1%2F%2F478daee300cf187502455250ace63b89dbc5cc3d1c3ffebdb1882252713add8f" alt="Image" width="28%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(a)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//7ec9f4cc-7dda-4e2b-a357-5967f232066c/markdown_0/imgs/img_in_chart_box_604_134_945_412.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A38Z%2F-1%2F%2F568708ae97f273518e7cc04942e13fa123751b36b8bac6e775f95e5b7b60b678" alt="Image" width="28%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(b)</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 2. (a) Example of a one-dimensional persistence diagram. (b) An illustration of the confidence set (red area) of (a).</div> </div>


### 3. Preliminary

In this section, basic concepts of digraphs and persistent homology are introduced.

A digraph is an ordered pair  $  G = (V, E)  $, where  $  V  $ denotes the vertex set and  $  E \subseteq V \times V  $ represents the directed edges. A digraph without loops or multiple edges is called a simple digraph. The GLMY homology (or path homology) provides a topological framework for analyzing simple digraphs (Grigor'yan et al., 2012). For a finite nonempty vertex set  $  V  $, an elementary  $  n  $-path is defined as a sequence  $  e_{i_0 \ldots i_n}  $ of  $  n + 1  $ vertices, where  $  n \geq 0  $. By convention, the set of elementary  $  (-1)  $-paths is empty. The boundary operator acts on elementary  $  n  $-paths as:

 $$ \partial e_{i_{0}\cdots i_{n}}=\sum_{k=0}^{n}(-1)^{k}e_{i_{0}\cdots\hat{i}_{k}\cdots i_{n}}, $$ 

where  $ \hat{i}_k $ indicates the omission of vertex  $ i_k $ from the sequence. An elementary path  $ e_{i_0\ldots i_n} $ on a set  $ V $ is regular if  $ i_{k-1} \neq i_k $,  $ \forall k = 1, \ldots, n $. Otherwise, it is non-regular. Thus, using the vertex set of a simple digraph, we can obtain the set of elementary  $ n $-paths of  $ G $, where all elements are regular paths. In the following discussion, unless otherwise noted, simple digraphs are considered.

Let  $  G = (V, E)  $ be a simple digraph. For any integer  $ n \geq 0 $, we define the K-linear space of allowed n-paths as:

 $$ \mathcal{A}_{n}(G)=\operatorname{s p a n}\Big\{e_{i_{0}\ldots i_{n}}:i_{k}i_{k+1}\in E for k=0,\ldots,n-1\Big\}, $$ 

where  $ e_{i_0...i_n} $ denotes an elementary  $ n $-path. For  $ n \geq -1 $, the subspace of  $ \partial $-invariant  $ n $-paths is defined as:

 $$ \Omega_{n}(G)=\left\{v\in\mathcal{A}_{n}:\partial v\in\mathcal{A}_{n-1}\right\}, $$ 

with the boundary cases  $ \Omega_{-1} \cong \mathbb{K} $ and  $ \Omega_{-2} = \{0\} $. This gives rise to the chain complex:

 $$ \cdots\xrightarrow{\partial}\Omega_{3}\xrightarrow{\partial}\Omega_{2}\xrightarrow{\partial}\Omega_{1}\xrightarrow{\partial}\Omega_{0}\xrightarrow{\partial}\mathbb{K}\xrightarrow{\partial}0. $$ 

The n-dimensional GLMY homology group of G is then:

 $$ H_{n}(G)=\mathrm{Ker}(\partial|_{\Omega_{n}})/\mathrm{Im}(\partial|_{\Omega_{n+1}}). $$ 

Elements of  $ Z_n := \text{Ker}(\partial|_{\Omega_n}) $ are called  $ n $-cycles, while elements of  $ B_n := \text{Im}(\partial|_{\Omega_{n+1}}) $ are  $ n $-boundaries. A representative of a homology generator is any  $ n $-cycle that is not an  $ n $-boundary, though such representatives are generally non-unique.

Persistent homology is a tool from computational topology that captures the topological features of space at various scales (Edelsbrunner et al., 2008). It provides a way to quantify the persistence of topological features, capturing the birth and death of topological features in the considered space (such as point clouds, graphs, and digraphs) by constructing a filtration. The persistence diagram (PD) serves as a powerful visualization tool for persistent homology, where each point  $ (b_i, d_i) $ corresponds to a persistence pair representing the birth  $ (b_i) $ and death  $ (d_i) $ times of a homology generator (Fig. 2). Notice that all points in a PD are located above or on the diagonal. And the value  $ |d_i - b_i| $ is called the persistence of the point  $ (b_i, d_i) $, representing the significance of the corresponding topological features. The greater the persistence of a point in the persistence diagram, the more significant the corresponding topological feature is.

A statistical approach for identifying significant points in a persistence diagram is the confidence set (Fasy et al., 2014), which categorizes these points into two classes based on their persistence. As shown in Fig. 2 (b), the confidence set draws two areas on the persistence diagram: the red area and the white area, which contain points with less persistence and greater persistence, respectively. Points in the class that show greater persistence are called significant points, while the other points are called noise points.

The tool of persistence diagram is first employed to illustrate the persistent homology computed from some point clouds, and this framework can also naturally extend to persistent GLMY homology, where we denote the one-dimensional persistence diagram of  $ H_{1} $ as  $ PD_{1} $.

### 4. Methodology

In this section, we first introduce some basic concepts and methods of reservoir computing, as well as some theoretical analysis. In particular, we consider optimization by improving the orthogonality of the reservoir digraph matrix, which enhances its memory capacity. To achieve this goal, the GLMY theory will be used. Subsequently, we further introduce the persistent GLMY homology of a digraph and the proposed approach for optimizing the reservoirs.

#### 4.1. Reservoir computing and its theoretical analysis

Training the weight matrices in deep learning models is typically computationally expensive. In contrast to conventional neural networks, where the weights of all layers are trained, the reservoir computing (RC) architecture only requires the training of the readout layer's weights. This characteristic significantly reduces the computational complexity, offering a computational efficiency advantage in certain applications. The general structure of the reservoir computing model is illustrated in Fig. 3. It primarily consists of three components: the input layer, the reservoir, and the output layer. The input layer is responsible for encoding the incoming data and feeding it into the reservoir. The reservoir consists of a large, fixed, and recurrent network of neurons that project the input data into a high-dimensional dynamic space. The output layer, which is typically trained, maps the high-dimensional representations from the reservoir to the desired output. Generally, the input and output layers are fully connected layers, while the reservoir is represented by

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//5017f609-4ec4-462b-80d1-3e4b8fdd246a/markdown_0/imgs/img_in_image_box_118_118_533_390.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F3d63158d1fb779fbc83949a3c8a0925bfb93e4a1e4d623617e3d8d78b9975418" alt="Image" width="34%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 3. Structure of reservoir computing model.</div> </div>


a weight matrix  $ W_r \in \mathbb{R}^{N \times N} $, where  $ N $ denotes the size of the reservoir. The weight matrix defines the connections between the neurons within the reservoir, determining the structure and dynamics of the recurrent network. Similarly, the input layer  $ L_in $ and the output layer  $ L_{output} $ are also described by their respective weight matrices. Specifically, the input layer is represented by the weight matrix  $ W_in \in \mathbb{R}^{N \times L} $, where  $ L $ is the dimensionality of the input data. The output layer is represented by the weight matrix  $ W_{out} \in \mathbb{R}^{M \times N} $, where  $ M $ is the number of output neurons. These weight matrices govern the flow of information from the input to the reservoir and from the reservoir to the output layer, ensuring the appropriate transformations and mappings of data within the network. Typically, both  $ W_in $ and  $ W_r $ are randomly initialized and remain fixed throughout operation, whereas  $ W_{out} $ is optimized via gradient descent or ordinary least-squares methods to obtain the optimal parameters. This strategy substantially reduces the training time and computational resources.

At each discrete time step  $ t + 1 $, the new reservoir state is jointly determined by the external input arriving at that moment and the internal state carried over from the previous step. Concretely, the update rule is often written as

 $$ \mathbf{x}_{t+1}=(1-\alpha)\mathbf{x}_{t}+\alpha\phi\big(W_{\mathrm{i n}}\mathbf{u}_{t+1}+W_{\mathrm{r}}\mathbf{x}_{t}+\mathbf{b}\big), $$ 

where  $ \mathbf{u}_{t+1} \in \mathbb{R}^L $ is the input vector,  $ \mathbf{x}_t \in \mathbb{R}^N $ is the previous reservoir state,  $ W_{\text{in}} \in \mathbb{R}^{N \times L} $ and  $ W_r \in \mathbb{R}^{N \times N} $ are the fixed input and reservoir weight matrices,  $ \mathbf{b} $ is an optional bias, and  $ \phi(\cdot) $ is a point-wise non-linear activation (e.g.,  $ \tanh $). The leak rate  $ \alpha $ controls the trade-off between retaining historical information and incorporating new information.

More precisely, the activation of each neuron inside the reservoir at time step  $ t + 1 $ depends on (i) the subset of input-layer neurons projecting to it and (ii) the neighbouring reservoir neurons to which it is connected. Denoting the  $ i $th reservoir neuron by  $ x_{i,t} $, we have

 $$ x_{i,t+1}=(1-\alpha)x_{i,t}+\alpha\phi\Big(\sum_{j=1}^{L}W_{\mathrm{i n},i j}u_{j,t+1}+\sum_{k=1}^{N}W_{\mathrm{r},i k}x_{k,t}+b_{i}\Big), $$ 

where  $ u_{j,t+1} $ is the jth component of the input vector,  $ W_{\mathrm{in},ij} $ and  $ W_{\mathrm{r},ik} $ are the fixed weights onto neuron i, and  $ b_i $ is an optional bias term.

Inspection of the update rules in Eqs. (1)–(2) reveals that, much like a conventional recurrent neural network (RNN) (Rumelhart et al., 1986), the reservoir maintains a compact representation of both historical and instantaneous information within its state  $ \mathbf{x}_{t} $. This internal memory allows the model to integrate long-range temporal dependencies when predicting future outcomes. The output at time t is produced by the current reservoir state:

 $$ \mathbf{y}_{t}=W_{\mathrm{o u t}}\mathbf{x}_{t}+\mathbf{c}, $$ 

where  $ \mathbf{y}_t \in \mathbb{R}^M $ denotes the output vector,  $ W_{\text{out}} \in \mathbb{R}^{M \times N} $ is the trainable readout weight matrix, and  $ \mathbf{c} \in \mathbb{R}^M $ is an optional bias term. Unlike traditional Recurrent Neural Networks (RNNs) that often struggle with vanishing or exploding gradients when learning long-term dependencies, RC models sidestep this issue by training only a linear readout layer. This simplifies the training process, making RC more stable and efficient in learning the repeating structures characteristic of periodic data.

In our study, we focus on the Echo State Network (ESN), a widely used framework of reservoir computing. Here, an important index that is closely related to the properties of ESN is the (short-term) memory capacity (MC). The memory capacity quantifies the network's ability to reconstruct past information from its reservoir at the network's output by computing correlations (Barančok & Farkaš, 2014; Farkaš et al., 2016; Jaeger, 2001b). It is defined by the following equation:

 $$ \mathrm{MC}=\sum_{k=1}^{k_{\max}}\mathrm{MC}_{k}=\sum_{k=1}^{k_{\max}}\frac{\mathrm{cov}^{2}\left(\mathbf{u}(t-k),\mathbf{y}_{k}(t)\right)}{\mathrm{var}(\mathbf{u}(t))\cdot\mathrm{var}\left(\mathbf{y}_{k}(t)\right)} $$ 

Here, cov represents the covariance between the two time series, and var denotes the variance.  $ \mathbf{u}(t-k) $ refers to the input presented k steps before the current input, while  $ \mathbf{y}_k(t) = \tilde{\mathbf{u}}(t-k) $ is its reconstructed output from the network using a linear readout. Thus, memory in ESNs is conceptualized as the network's capacity to retrieve historical information (for various k values) from the reservoir through linear combinations of internal unit activations. The study (Barančok & Farkaš, 2014) shows that the memory capacity of ESNs depends on the properties of the structure and parameters of reservoirs, and may also be influenced by the data properties.

A key finding of our study is that introducing additional rings into the reservoir digraph enhances the orthogonality of its adjacency matrix, a property empirically demonstrated to correlate with improved reservoir performance. The orthogonality of reservoir adjacent matrices is closely related to the memory capability of reservoirs, which influences the prediction of reservoirs (Strauss et al., 2012). Mathematically, orthogonality is a special case of linear independence, which ensures that the matrix columns are not only linearly independent but also mutually orthogonal. Improving the orthogonality of a reservoir matrix reduces overlap and interference between dataset signals stored at different time steps, enabling the network to better distinguish and retrieve distinct inputs. Moreover, orthogonal matrix columns or rows increase the probability of the matrix being full-rank, which is crucial for maximizing memory capacity. Additionally, enhanced orthogonality improves numerical stability, ensuring that computational errors do not accumulate and allowing the network to store and recall information with greater accuracy. In summary, enhancing the orthogonality of reservoir matrices maximizes short-term memory capacity and improves the network's ability to distinguish and retrieve different input signals (Strauss et al., 2012). This provides a theoretical base for our optimization method, which focuses on improving the orthogonality of reservoir matrices.

Hence, we aim to increase the orthogonality of the reservoir adjacent matrices to improve their capabilities. We use the following measurement to measure the orthogonality of a matrix:

Definition 1. Suppose A is a matrix. Consider all its column vectors  $ \{a_1, a_2, \ldots, a_n\} $, here we define the orthogonality measurement of A is

 $$ O M(A)=\frac{1}{C_{n}^{2}}\sum_{i,j=1;i\neq j}^{n}|m(\mathbf{a}_{i},\mathbf{a}_{j})|, $$ 

where  $ C_n^2 = \frac{n(n-1)}{2} $ is the combinatorial number,  $ m(\mathbf{a}_i, \mathbf{a}_j) = 1 $ if  $ \mathbf{a}_i $ or  $ \mathbf{a}_j $ is zero vector, and  $ m(\mathbf{a}_i, \mathbf{a}_j) = \cos \langle \frac{\mathbf{a}_i}{\|\mathbf{a}_i\|}, \frac{\mathbf{a}_j}{\|\mathbf{a}_j\|} \rangle $ ( $ \|\cdot\| $ denotes the 2-norm) if both of them are nonzero vectors.

It is easy to see that  $ OM(A) $ ranges from  $ [0,1] $, and the closer to zero, the more vectors in  $ \{a_1, a_2, \ldots, a_n\} $ are orthogonal to each other, which implies that the orthogonality of this matrix is greater. We clarify that this metric is a normalized adaptation of Mutual Coherence (Donoho et al., 2001) and is closely related to the Frame Total Potential (Benedetto & Fickus, 2003). In high-dimensional dynamical systems

like reservoirs, the degree of linear independence between state dimensions is critical for information processing. Our OM metric quantifies the average “aliasing” between basis vectors. By defining OM, we provide a quantitative tool to track how our GLMY theory-based topological optimization systematically reduces redundancy and approaches the isometry property required for optimal fading memory.

Since a reservoir can be represented by a digraph, the problem of improving the orthogonality of its adjacency matrix can also be regarded from the perspective of the reservoir digraph corresponding to the adjacency matrix. To explain this, we first introduce ring, which is a special kind of digraph and is useful for analyzing the properties of reservoirs. A digraph  $ G = (V, E) $ is a ring if it is connected (as an undigraph), and the in-degree and out-degree of each vertex are 1. We say a digraph has rings if some of its subgraphs are rings. According to the matrix representation of a ring, modifying a reservoir to increase the number of rings in its digraph is equivalent to making its adjacency matrix possess more fundamental cyclic submatrices, such as:

 $$ \begin{pmatrix}1&&&\\&1&&\\&&\ddots&\\&&&1\\1&&&\end{pmatrix} $$ 

or its transpose. For example, in Fig. 4, when changing from (a) to (b),  $ \stackrel{A}{\downarrow} \longrightarrow \stackrel{D}{\uparrow} $  $ \stackrel{A}{\downarrow} \longrightarrow \stackrel{D}{\uparrow} $ the shape  $ B \longrightarrow C $ becomes  $ B \longrightarrow C $ and the corresponding matrix representation changes from  $ \left(\begin{array}{cc} 1 & 1 \\ 1 & 1 \end{array}\right) $ to  $ \left(\begin{array}{cc} 1 & 1 \\ 1 & 1 \end{array}\right) $. Notice that the orthogonality of the adjacency matrix increases from 3 to 4. In fact, for the more general case (Eq. (4)), since each row and column of this matrix is orthogonal to each other, the more submatrices of this type a matrix has, the greater its orthogonality will be. Combining the previous discussion of the relationship between the orthogonality of the reservoir matrix and the memory capacity of the reservoir, when we make the reservoir matrix (particularly sparse one) have more fundamental cyclic submatrices (which is equivalent to making the digraph of the reservoir have more rings), the greater the memory capacity of the reservoir is, and the more likely it is to exhibit greater predictive ability (Strauss et al., 2012).

Therefore, the core objective of this study is to enhance the orthogonality of the reservoir adjacency matrix. From a graph-theoretic perspective, this goal is equivalent to adding the number of rings in the reservoir digraph—an equivalence that forms the logical starting point for the subsequent methodological design. To achieve this objective, the GLMY homology theory is introduced in this paper as the core analytical tool and operational framework. It is crucial to emphasize that, within the algebraic topological characterization of digraphs, rings are essentially a proper subset of the set of representative cycles contained in the GLMY homology groups. This implies that the representative cycles described by GLMY homology groups include not only rings but also other non-cyclic loop structures.

Based on the above theoretical understanding, the core idea of this study is clarified as follows: to maximize the proportion of rings within the representative cycles of GLMY homology through targeted topological operations. Specifically, it involves implementing structural transformations on those representative cycles that do not currently belong to the ring subset (i.e., non-cyclic loops) to make them become rings, thereby incorporating them into the ring subset. The essence of this process lies in systematically increasing the number of rings in the digraph by optimizing the composition of the representative cycles of GLMY homology, ultimately serving the fundamental goal of improving the orthogonality of the adjacency matrix. The specific implementation method of this transformation process will be introduced in the next subsection.

#### 4.2. Optimizing reservoir structure by persistent GLMY homology

We first introduce persistent GLMY homology, which extends classical persistent homology theory to the context of weighted digraphs. Let  $  G = (V, E, w)  $ be a weighted digraph with vertex set  $  V  $, edge set  $  E  $, and weight function  $  w : E \to \mathbb{R}_+  $. For any threshold  $  \delta \in \mathbb{R}_+  $, define the subgraph:

 $$ G^{\delta}=(V,E^{\delta}=\{e\in E:w(e)\leq\delta\}). $$ 

This construction yields a digraph filtration $\{G^\delta \hookrightarrow G^\delta'\}_{\delta \leq \delta',}$ where the inclusion maps preserve the vertex set while gradually adding edges in order of increasing weight. The one-dimensional persistent GLMY homology of $G$ is then defined as the persistent vector space:

 $$ H_{1}=\{H_{1}(G^{\delta})\xrightarrow{i_{\delta,\delta^{\prime}}}H_{1}(G^{\delta^{\prime}})\}_{\delta\leq\delta^{\prime}}, $$ 

where  $ i_{\delta,\delta'}' $ denotes the induced homomorphism of the inclusion map. Here, each  $ G^{\delta} $ represents the state of the digraph at filtration parameter  $ \delta $. This framework provides a systematic way to track the evolution of homology classes as the filtration parameter increases, revealing persistent topological features of the weighted digraph across multiple scales.

In order to find the generators of one-dimensional GLMY homology of a digraph, we first introduce some special structures. A bigon is a sequence of two distinct vertices  $ a, b \in V $ such that  $ a \to b, b \to a $. A (boundary) triangle is a sequence of three distinct vertices  $ a, b, c \in V $ such that  $ a \to b, b \to c, a \to c $:

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//abd9cec8-d42a-474b-b674-1bd2fb28ebae/markdown_0/imgs/img_in_image_box_635_714_770_775.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A40Z%2F-1%2F%2Fa30ed15c2c1db3fc43a8b3e84f25e67d411ed58ac167c2b39f46ca66fe76ab18" alt="Image" width="11%" /></div>


A (boundary) square is a sequence of four distinct vertices  $ a, b, c, d \in V $ such that  $ a \to b, b \to c, a \to d, d \to c $:

 $$ \begin{array}{l} b \longrightarrow c \\ \uparrow \quad \uparrow \\ a \longrightarrow d \end{array} $$ 

Then, the one-dimensional GLMY homology of simple digraphs is clear because of the following Theorem (Dey et al., 2022). This theorem establishes the theoretical foundation for our operation to reservoirs.

Theorem. Let  $  G = (V, E)  $ be a simple digraph. Let  $  Z_1 = \text{Ker} \left( \partial|_{\Omega_1} \right)  $,  $  B_1 = \text{Im} \left( \partial|_{\Omega_2} \right)  $, and let  $  Q  $ denote the space generated by all bigons and boundary triangles and boundary squares in  $  G  $. Then, we have  $  B_1 = Q  $. Hence, the one-dimensional GLMY homology group satisfies that  $  H_1 = Z_1 / Q  $.

Consequently, any 1-cycle in a digraph that does not form a bigon, boundary triangle, or boundary square serves as a generator of the one-dimensional GLMY homology. In our study, we employ an algorithm that computes the one-dimensional persistent GLMY homology (Dey et al., 2022) to identify the minimal generators of  $ H_1(G) $ for a given digraph G. These minimal generators are called the minimal representative cycles(Dey et al., 2022; Grigor'yan et al., 2012) of the  $ H_1(G) $.

Now we introduce our approach for optimizing reservoir structures using GLMY homology to enhance their predictive capabilities. As we have mentioned above, a key distinguishing feature of reservoirs compared to feedforward neural networks is the presence of rings in their architecture, which have been shown to possibly influence their time series prediction performance. Therefore, we aim to increase the number of rings in a given reservoir to optimize its structure. Specifically, when a reservoir is given, we first compute the persistent GLMY homology of its digraph and get the minimal representative cycles of one-dimensional GLMY homology groups. Since a ring is a special type of minimal representative cycle, we can modify other representative cycles into rings by changing some edges' directions in a compatible way (this will be introduced later). In other words, these representative cycles are used to modify the structure of the reservoir to increase the number of rings.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//7e366c47-74f0-40c1-8365-a5d994f6f716/markdown_0/imgs/img_in_image_box_174_114_1012_257.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2Fd54509340f3d88ec4ed3b6b9bd9dc9357762dac36fda97fe9cba5e7e26a1b1b1" alt="Image" width="70%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 4. Illustration of compatibility modifying cycles into rings. (a) A digraph has two rings on the left and right. The middle cycle (red) is not a ring. (b) By changing the direction of AD, the middle cycle becomes a ring ABCD compatible with the other rings. (c) The case where the middle cycle cannot be changed into a ring without destroying the other two rings, since either AB or DC would need to have its direction changed.</div> </div>


in the reservoir digraph. In our experiments, the reservoir can get better prediction ability on three tested datasets after adding the rings in the reservoir digraph. The flowchart of our method and experimental procedures is shown in Fig. 1.

from a tneoretucai perspective, the 1-amensionai persistence diagram (1-PD) plays a crucial role in our methodology. Each point in the 1-PD corresponds to a minimal representative cycle in the digraph. Our first step is to check whether each minimal representative cycle forms a closed loop, where edges are connected end-to-end in a sequential and continuous manner, which we define as a "ring". This verification process is essential because only cycles with a proper ring structure can fully contribute to the reservoir's predictive capabilities. When a minimal representative cycle fails to meet the ring condition, we employ an edge direction modification process. The primary objective of this process is to transform the non-ring representative cycle into a ring while ensuring that all existing rings within the digraph are preserved. For each individual representative cycle, we begin by attempting to modify its edges to achieve the desired ring structure. However, during the edge direction modification, if there are common edges among the current cycle and existing rings, changing the direction of these shared edges may inadvertently destroy these existing rings (see Fig. 4 for an example). In such cases, where altering the current cycle would be incompatible with the preservation of existing rings, we adopt a conservative approach. Instead of forcing the modification and risking the disruption of the existing rings, we abandon the attempt to change the current cycle and proceed to the next representative cycle in the sequence.

To execute this optimization method comprehensively, we apply the above procedure sequentially to all representative cycles corresponding to the points in the 1-PD. Through this iterative process, we gradually and significantly increase the number of rings within the reservoir diagram. As the number of well-formed rings grows, the reservoir's ability to capture complex patterns improves, leading to enhanced predictive performance. This systematic approach not only leverages the theoretical insights from GLMY homology but also provides a practical and effective solution for reservoir optimization.

The above method can be summarized as the following Algorithm 1.

Now we analyze the complexity of Algorithm 1. According to the theoretical bounds provided by (Dey et al., 2022), computing 1-dimensional persistent GLMY homology and extracting the minimal representative cycles (the first step of our method) follows the complexity of  $ O(rm^{\omega-1} + m^{\omega} + nmg^{\omega-1}) $, here

 $$ r=\min\{a(G)m,\sum_{(u,v)\in E}(d_{i n}(u))+d_{o u t}(v))\}, $$ 

 $ a(G) = O(n) $ is the so-called arboricity of  $ G $,  $ \omega < 2.373 $ is the exponent for matrix multiplication, and  $ g = rank(H_1) $. Upon obtaining the set of  $ g $ minimal representative cycles, the algorithm performs a targeted structural refinement. This phase is characterized by its linear efficiency relative to the reservoir's sparsity: For each identified generator, the algorithm verifies its cyclic structure and performs a compatible weight adjustment. The complexity for each generator is  $ O(L_i) $, where  $ L_i $ is the length of the cycle. Summed over all  $ g $ generators, the total complexity for this stage is  $ O(\sum_{i=1}^{g} L_i) $. In practice, this is bounded by  $ O(m) $, the number of edges in the sparse reservoir. Consequently, the complexity

Algorithm 1 Reservoir optimization by GLMY homology.
Input: A digraph  $ G = (V, E) $ with n vertices and m edges representing a reservoir.
1: Computing the minimal representative cycles of the 1D GLMY homology of G. Denote these cycles by C.
2: For each cycle in C:
3: If the cycle is already a ring:
4: Turn to the next cycle.
5: Else
6: If the cycle is not a ring but can be modified as a ring without destroying existing rings:
7: Change some edge directions to make it a ring.
8: Else
9: Turn to the next cycle.
10: EndIf
11: EndFor
Return: The optimized digraph G of the reservoir.

of Algorithm 1 is  $ O(rm^{\omega-1} + m^{\omega} + nmg^{\omega-1}) $, concentrated in the initial topology computation.

### 5. Experiments and discussions

In this section, we introduce the datasets used and their topology analysis, and illustrate our experimental results. Our experiments aim to rigorously evaluate prediction performance before and after implementing the optimization process on reservoir digraphs. We will also give some discussions about the proposed method.

In the following subsections, we will use the following designs and parameter settings. In our experimental setup, we assumed that there is at most one edge between every two nodes, and all edges share identical weights for simplicity. The spectral radius² of the reservoir in our experiments is set as λ_target = 0.8 since empirical studies (Venayagamoorthy & Shishir, 2009) indicate that a spectral radius close to 0.8 realizes a favourable trade-off between fading memory and nonlinear amplification, thereby yielding best performance for the reservoir. The setting of the spectral radius can be achieved by the following steps: firstly, for a randomly generated reservoir, we assign each edge an identity weight, for example, one, to get the initial reservoir digraph W_initial. Then we can compute the maximum eigenvalue λ_max of the reservoir digraph, followed by adjusting the spectral radius of the reservoir to λ_target using the following formula:

 $$ W_{r}=\lambda_{target}\cdot\frac{W_{initial}}{\lambda_{max}}. $$ 

### 5.1. Reservoir size sensitivity and reservoir dynamics analysis

First, we examine the sensitivity of our method with respect to reservoir size. In particular, we focus on optimizing the orthogonality

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//f0be0e1f-54a1-4101-8401-b353673affc0/markdown_0/imgs/img_in_chart_box_174_111_451_329.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2Fbd7d6a7711a95f5f6b718236399e378c1184b3f2bc5a260981a2089c212bfa3c" alt="Image" width="23%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//f0be0e1f-54a1-4101-8401-b353673affc0/markdown_0/imgs/img_in_chart_box_451_112_733_328.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F8c4392aace8b38f308907126699dd676651fad7f4a62ca790cc1bf8b9e880ccc" alt="Image" width="23%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//f0be0e1f-54a1-4101-8401-b353673affc0/markdown_0/imgs/img_in_chart_box_734_112_1014_328.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F690115409eaea52b9c1b836cf5b94bebd56304b5fb763d3f310504c656820ad8" alt="Image" width="23%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 5. Reservoir size sensitivity analysis. Here we analyze reservoir sizes ranging from 100 to 500 and calculate the orthogonality measurement (OM) before and after optimization. The results presented from left to right correspond to Random, Small-world, and Scale-free initialization, respectively.</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//f0be0e1f-54a1-4101-8401-b353673affc0/markdown_0/imgs/img_in_chart_box_179_401_444_626.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F26a3147e3ab295dd129bfb30fb4e15a4c798da5f912310a172cf00d8f7f6994e" alt="Image" width="22%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//f0be0e1f-54a1-4101-8401-b353673affc0/markdown_0/imgs/img_in_chart_box_457_402_725_626.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2Ffc667b89c8fb2e953ca58c7dfd7cd5d195e31b85afcbc2a0c33c7cb6c9c38e6c" alt="Image" width="22%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//f0be0e1f-54a1-4101-8401-b353673affc0/markdown_0/imgs/img_in_chart_box_734_402_1010_625.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F47e2e680f03b7d27c884ae335ba63538697c88b7b0af91191ce5e09ca41d7dfa" alt="Image" width="23%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 6. Spectral analysis of a reservoir with 100 nodes, 0.99 sparsity, and a fixed spectral radius of 0.8 before and after optimization. Left: eigenvalue distribution before optimization. Middle: eigenvalue distribution after optimization. Right: singular values before (blue) and after (red) optimization.</div> </div>


measurement (OM) for varying reservoir sizes (ranging from 100 nodes to 500 nodes) and initialization strategies (Random, Small-world, and Scale-free). Fig. 5 demonstrates that the proposed optimization consistently reduces OM across reservoir sizes and initialization types, with the largest absolute improvements observed for initially less-orthogonal (random and scale-free) reservoirs, while preserving the spectral-radius constraint. It is noteworthy that these results are obtained while maintaining the same spectral radius constraint ( $ \lambda = 0.8 $), thus supporting our assertion that orthogonality can be improved without sacrificing stability by adjusting the structure of rings.

Then, we illustrate how our optimization method affects the reservoir dynamics. Thanks to the size sensitivity analysis, it suffices to analyze a specific reservoir size. Here we conducted a spectral analysis on a sparse reservoir with 100 nodes, 0.99 sparsity, and a fixed spectral radius of 0.8, to isolate the structural effects. Fig. 6 shows the eigenvalue distributions and singular value decay before and after optimization while keeping the spectral radius fixed at 0.8. After optimization, the eigenvalues did not exhibit the situation where a few extremely slow modes were pushed towards the spectral radius boundary; instead, the modulus distribution became more uniform. This indicates that the optimization does not rely solely on extremely slow modes but instead enhances the overall contribution of multiple moderately decaying modes, thereby giving the state space a higher effective representational capability in multiple directions and improving memory capacity. Moreover, the post-optimization singular value spectrum is noticeably flatter in its mid-range and exhibits fewer near-zero singular values, indicating a more uniform energy distribution across state directions. Dynamically, this corresponds to a redistribution of modal contributions: more moderate-decay modes rather than a few dominant very-slow modes, which yields a richer set of approximately orthogonal state components for the linear readout to exploit.

Additionally, in our spectral analysis, the eigenvalues of the reservoir weight matrix remain strictly within the target spectral radius both before and after optimization, which indicates that the optimization does not compromise this fundamental stability and hence preserves the fading memory property. Moreover, the post-optimization eigenvalue and singular value distributions suggest a redistribution of modal contributions without inducing a few excessively slow modes. Instead, a broader set of moderate-decay modes emerges, enriching the reservoir's state representation under stable dynamics. Such a shift enhances the reservoir's effective memory capacity while maintaining controlled fading of older inputs, consistent with the theoretical notion of fading memory.

### 5.2. Datasets and their topology

To validate our approach and compare results from different datasets on the same scale and for the convenience of comparing topological difference, we employ the following datasets with value normalized into the range  $ [-0.5, 0.5] $:

1. Mackey-glass system: This classical chaotic system evaluates time series prediction models through the discrete approximation:

 $$ y(t+1)=y(t)+\delta\Bigg(a\frac{y(t-\tau/\delta)}{1+y(t-\tau/\delta)^{n}}-b y(t)\Bigg), $$ 

with standard parameters  $ \delta = 0.1 $, a = 0.2, b = -0.1, n = 10, and chaotic regime  $ \tau = 17 $. The task involves k-step prediction using historical data  $ u(1, \ldots, t) $ to forecast  $ u(t + k) $. In our experiments, we use the first 5000 steps for training and the following 5000 steps for prediction.

2. Multiple superimposed oscillator series: The Multiple Superimposed Oscillator (MSO) series prediction is also an important problem. The core concept behind the MSO is to combine multiple oscillator signals into a single composite indicator by superimposing and normalizing them. It can be described by the following equation:

 $$ y(t)=\sum_{i=1}^{m}\sin(\alpha_{i}t), $$ 

where $m$ is the number of summed sine waves. To test ESN, a common way is to set $m = 5$ and $\alpha_1 = 0.2$, $\alpha_2 = 0.311$, $\alpha_3 = 0.42$, $\alpha_4 = 0.51$, $\alpha_5 = 0.63$.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_image_box_190_112_567_176.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A38Z%2F-1%2F%2F35d9fe457c623a9719b84559e7019999fabe2dc3df185e294d70483e424cde9a" alt="Image" width="31%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_image_box_181_184_363_346.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A38Z%2F-1%2F%2F37bf3824803a740eeb6475585aab1c35ddde72bcdb3453ca8ea2b6c79d764bfd" alt="Image" width="15%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_chart_box_366_185_577_339.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F8e30432f1bd85cd09c3fbe6a95e060f538d06818901bd931a813dfca72c32cad" alt="Image" width="17%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_image_box_625_113_1002_176.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2Fe61bfc836c2abb9823e312a50ac5f27d1f12511285afb212db604e62d9230c22" alt="Image" width="31%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_chart_box_609_183_794_346.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F3761ee0f4bdbd9812299bdb0115c77f3f7f69c757b348352208f2b2bf5c2a049" alt="Image" width="15%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(a)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_chart_box_798_182_1012_341.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2Fd2a0b2030a246957e884bbc5c725dcaeb3cb26bee1017d7276acbf4f182c45af" alt="Image" width="17%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(b)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_chart_box_192_371_570_439.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2Fdf284a759690cc5df091e4423869edaae42f633a4e4c1819c8377ab89ce37ccf" alt="Image" width="31%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_chart_box_625_371_1004_437.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F724141afdd8a99e1285a2b00b399a79e9b559aadd00091f53e4f31692867e59f" alt="Image" width="31%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_chart_box_181_443_369_611.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F7fdb8b9ae9e2b5d2f144332df2dc6ccdbfb17015a03751f822ac97912ee17ef6" alt="Image" width="15%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_chart_box_376_442_579_602.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2Fcbd2bfe288b572de6dbc8cddd080fad3f457c5e17c7f8d830268f36ad29557ae" alt="Image" width="17%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_chart_box_611_442_798_608.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F832779b84f4a1711d1f6d76b0c41a3946ae408facae3bc54fc58997ca2ea83e1" alt="Image" width="15%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(c)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_chart_box_801_442_1011_603.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2Fe87f129dc190fc355660a89c2910ff9013302a85959432353da363c2f011dc9a" alt="Image" width="17%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(d)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_chart_box_405_619_785_688.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F99846aa45d58397832ca236b33a085985e044eea7dbae8e92d7f3cc135c1dbc5" alt="Image" width="31%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_chart_box_408_685_575_854.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F60acdaa0775d2c94a8c043a76bddc52a8a1fc377a8fb718d73f530f44a58b1f8" alt="Image" width="14%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fc0ab8ce-716c-4708-bb43-46ec321905c5/markdown_0/imgs/img_in_chart_box_571_687_800_855.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F7acaa51ea8d614542cbc162b193335f55816864105efbd39de0aa99c69f7eaa1" alt="Image" width="19%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(e)</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 7. Illustration of five datasets, and their Time-delay embedding results in  $ \mathbb{R}^{3} $ and the one-dimensional persistence diagrams. (a) Result of Mackey-Glass Data. Max Persistence is 0.1696. (b) Result of MSO Data. Max Persistence is 0.0183. (c) Result of Lorenz System Data. Max Persistence is 0.0183. (d) Result of NARMA Data. Max Persistence is 0.0269. (e) Result of ETT Data. Max Persistence is 0.0135.</div> </div>


3. Lorenz system: A typical benchmark for chaotic systems:

 $$ \begin{cases}\dot{x}=-a x(t)+a y(t)\\\dot{y}=b x(t)-y(t)-x(t)z(t)\\\dot{z}=x(t)y(t)-c z(t)\end{cases} $$ 

with $a = 10/4$, $b = 28$, $c = 8/3$. The Runge-Kutta method can generate a sample of length $L$ from the initial conditions $(x_0, y_0, t_0)$ with a step size of 0.01. In our experiments, the $y$-axis is chosen for our prediction task, and we also use the first 5000 steps for training and the following 5000 steps for prediction. The first 1000 input samples were discarded after being fed into the network.

4. NARMA system: This nonlinear auto-regressive moving average system presents a challenging identification problem:

 $$ y(t+1)=0.3y(t)+0.05y(t)\sum_{i=0}^{9}y(t-i)+1.5u(t-9)u(t)+0.1, $$ 

where  $ u(t) \sim \mathcal{U}[0, 0.5] $ (uniform distribution). Initialized with  $ y(t) = 0 $ for  $ t = 1, \ldots, 10 $, it tests echo state networks through one-step prediction. In our experiments, we use the first 5000 steps for training and the following 5000 steps for prediction. The first 500 input samples were discarded after being fed into the network.

5. Electricity transformer dataset: The Electricity Transformer Dataset (ETT) dataset is one of the widely used standard public datasets in the field of long-series time series forecasting in recent years, published and systematically organized by Zhou et al. (2021). This dataset records various monitoring variables such as load power and oil temperature of transformers in power systems during long-term operation. It exhibits significant seasonal and periodic components, while also containing random fluctuations, making it suitable as a forecasting benchmark for real-world industrial scenarios. We use an hourly subset of the ETT dataset, selecting 10,000 h of monitoring data beginning on 2017/1/1. In the experiments, transformer oil temperature is used as the predicting target. We use the first 5000 steps for training and the following 5000 steps for prediction.

To analyze the periodic differences between datasets, we employ Time-Delay Embedding (TDE) (Takens, 2006) to embed the time series into higher-dimensional space, followed by computing their one-dimensional persistence diagrams (1-PDs) from constructing the alpha filtration (Edelsbrunner & Harer, 2010) of the embedded point clouds. Time-Delay Embedding is a powerful technique used in the analysis of time series data, which transforms a single observed time series into a point cloud in high-dimensional space. This method leverages the concept of phase space reconstruction, allowing for the visualization and analysis of complex time series from limited measurements (Takens, 2006).

Given a scalar time series $\{x_t\}_{t=1}^N$, where $N$ is the number of observations, the TDE process constructs a set of points in a higher-dimensional space (called the embedding space) using a specified embedding

dimension $d$ and a time delay parameter $\tau$. Each point in this new representation is formed as follows:

 $$ \mathbf{X}_{i}=[x_{i},x_{i+\tau},x_{i+2\tau},\ldots,x_{i+(d-1)\tau}]^{T}, $$ 

where  $ i = 1, 2, \ldots, N - (d - 1)\tau $, ensuring that all components of each  $ \mathbf{X}_i $ are within the bounds of the original time series.

The choice of the embedding dimension $d$ and the time delay $\tau$ plays a crucial role in the effectiveness of TDE. The embedding dimension determines the number of past values included in each vector, capturing the dynamics of the underlying system. Meanwhile, the time delay specifies how far apart these values are spaced in time, influencing the independence between the components of the embedded vectors. In our study, by testing a variety of parameter selections, we embed the aforementioned time series into $\mathbb{R}^{3}$ with a delay parameter of $\tau = 5$, which gives a clear and intuitive illustration of the topological characteristics of the embedded data. This transformation not only enhances the estimation precision of models but also reveals hidden structures and patterns in the data that are not apparent in the raw time series form. The one-dimensional persistence diagram captures the topological features of loops present in the point cloud. When a point in the 1-PD exhibits significantly greater persistence than others, this indicates both the existence of a prominent loop structure in the embedded point cloud and a strong periodic mode in the original time series (Perea & Harer, 2015). This correspondence between persistent homology features and time series periodicity provides valuable insight into the underlying dynamics of the system. Therefore, we can use the Max Persistence in a 1-PD as a Periodicity Index (PI) to detect the periodicity of a time series:

 $$ PI=\max\left\{d_{i}-b_{i}\mid(b_{i},d_{i})\in PD_{1}\right\}. $$ 

In this representation, the periodic or quasi-periodic dynamics of the signal manifest as cyclic attractors (Perea & Harer, 2015; Takens, 2006). A higher PI indicates a more robust cyclic attractor in the data's underlying dynamics, representing stronger periodicity. The results are illustrated in Fig. 7, where we illustrate the original time series, the embedded point clouds in  $ \mathbb{R}^3 $, and the 1D persistence diagram with confidence sets. The title of Fig. 8 records the Max Persistence (PI) of these datasets. These results reveal distinct topological characteristics: the Mackey-Glass data exhibits a significant 1-dimensional topological feature as its 1-PD has one point located above the red area, while others show no significant 1-dimensional topological structures. Hence, these five datasets differ in their prominence of periodicity.

It is widely observed that Reservoir Computing models may demonstrate superior performance when dealing with datasets exhibiting pronounced periodicity (Jaeger, 2001a). This enhanced capability stems from RC's unique architectural features, which are well-suited to capture and exploit the complex temporal dependencies inherent in periodic signals. The fixed, randomly connected "reservoir" acts as a dynamic, high-dimensional feature extractor, mapping input sequences into a rich, nonlinear state space. This intrinsic non-linearity and recurrent connectivity enable the reservoir to effectively represent intricate periodic patterns and their underlying dynamics, even when such patterns are embedded within noise or non-stationary components. Furthermore, the inherent memory capacity of the reservoir allows it to retain information about past inputs over extended periods, which is crucial for learning and predicting long-term periodic cycles. According to the operation of TDE, the topology of the embedded data relates to its periodicity, hence influencing the prediction results of the reservoir. This will be shown later in the experimental results.

### 5.3. Initial reservoir generation and its optimization

In our experiments, we tested three types of initial construction strategies for the reservoir. The first one is constructing the reservoir randomly, which typically results in a sparse reservoir digraph matrix. Additionally, we also test the small-world reservoir constructed with the Watts–Strogatz model (Watts & Strogatz, 1998) and the scale-free reservoir produced by the Barabási–Albert (BA) model (Barabási & Albert, 1999). These manually designed network structures have been shown in related studies to provide superior prediction accuracy and a wider spectral radius, which provide a diverse set of benchmarks for our optimization method to validate its effectiveness.

Here, we compute the orthogonality measurement (OM) defined in Section 4.1 of each initialization method, comparing their digraph matrices' OM before and after optimization. Additionally, the number of rings that are added to the digraph is also counted. This evaluation is crucial because research suggests that an increase in the orthogonality of the reservoir matrix can significantly enhance its short-term memory capacity and improve the network's ability to distinguish and retrieve different input signals. From a topological perspective, increasing the number of rings in the reservoir digraph is equivalent to its adjacency matrix having more fundamental cycle submatrices, which is the key to improving orthogonality.

In this computation, the node number of the reservoir digraph is 500, which means the digraph matrix has the size  $ 500 \times 500 $. Hence, the orthogonality of each digraph matrix will not be greater than 500. In the Random configuration, we set the sparsity of the reservoir to 0.99, which means that only 1% of the possible edges in the fully connected graph of all nodes, which are randomly selected, actually exist. Due to the presence of a large number of zero elements, the initial orthogonality of the matrix will not be too large. In the small-world configuration, each node was initially connected to its  $ k = 10 $ nearest neighbors on a ring lattice, after which every edge was rewired with probability  $ p = .3 $. In the scale-free configuration, each newly added node established  $ m = 8 $ directed links according to preferential attachment. In the following discussion, we perform 10 tests for each of the initialization methods and datasets and take the overall average of each test index, which illustrates the general applicability of our method. We compute the persistent GLMY homology and minimal representative cycles using the code provided by Dey et al. (2022). Again, we note that there is at most one edge between any two nodes, and all edges have identical weights for simplification.

Table 1 illustrates the comparison of the average orthogonality measurement (OM) and ring addition number of the three different initialization methods, as well as the average optimization running time. For the Random initialization approach, the reservoir's initial sparsity results in a significant number of zero columns. Our optimization method effectively addresses this by substantially improving the average level of orthogonality. Additionally, our approach introduces numerous cycles into the reservoir digraph, strongly demonstrating that the method, based on GLMY homology theory, can indeed optimize the reservoir's structure. Similar results were observed in the Small-world initialization cases; although the increase in cycles was less than in the Random cases, the average OM was still reduced by approximately half. In the Scale-free approach, our optimization also reduced its OM significantly. These results, while showing variations in the original orthogonality and the number of cycles that can be added across different initialization methods, collectively validate our approach's effectiveness in increasing the orthogonality of the matrices. We can also infer that the orthogonality enhancement will be more significant with larger reservoir matrices.

In the following subsections, we will compute the memory capacity to further validate this observation and provide a more comprehensive performance evaluation. Moreover, we will also provide some related discussions later.

### 5.4. Memory capacity analysis

In the subsequent experiments, the reservoir digraph's node number is still set as 500. For the Random initial method, the reservoir sparsity is set to 0.99 (i.e., 1 % connectivity), which is a typical setting in practice (Jaeger & Haas, 2004). This configuration results in a large and sparse

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//4e28f811-8fff-45e6-887b-97d2a5816414/markdown_0/imgs/img_in_chart_box_201_143_583_282.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F96e845461777d5feadd80aacc5e04aef6ac972e391463b8285a3002ae63610c1" alt="Image" width="32%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//4e28f811-8fff-45e6-887b-97d2a5816414/markdown_0/imgs/img_in_chart_box_201_287_585_374.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2Fad6a30be75b5d0e12c50531bcaba3954c11bcc6b9a623588acc4348905f7ab30" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(a)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//4e28f811-8fff-45e6-887b-97d2a5816414/markdown_0/imgs/img_in_chart_box_612_146_993_278.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A39Z%2F-1%2F%2F9188caaf9fe7b78e7aa9147e3f68c1101dcfa3f90dbff95fbb0796dbb95a6d6c" alt="Image" width="31%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//4e28f811-8fff-45e6-887b-97d2a5816414/markdown_0/imgs/img_in_chart_box_607_288_991_379.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A40Z%2F-1%2F%2Fe007b1573673bcb50dda37c5a3f8d0c7e87c380c8c43b628b31abf866c789b14" alt="Image" width="32%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//4e28f811-8fff-45e6-887b-97d2a5816414/markdown_0/imgs/img_in_chart_box_206_403_585_488.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A40Z%2F-1%2F%2Fdc66b018251a31ee01391b25ba67852e812cdb634a42e684a3c0facc6e11bb54" alt="Image" width="31%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//4e28f811-8fff-45e6-887b-97d2a5816414/markdown_0/imgs/img_in_chart_box_202_489_588_617.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A40Z%2F-1%2F%2Fbf4d7a41f2d7a06cfa50706db9921c9a14d86b045e143092428634605109e96c" alt="Image" width="32%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//4e28f811-8fff-45e6-887b-97d2a5816414/markdown_0/imgs/img_in_chart_box_609_395_991_489.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A40Z%2F-1%2F%2F7c2dc22884193d0593a5eb0c34f5228bc829a61ce462df37b12ca3e657ebc53b" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(c)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//4e28f811-8fff-45e6-887b-97d2a5816414/markdown_0/imgs/img_in_chart_box_604_491_992_620.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A40Z%2F-1%2F%2Fb590d035b42f668e52dc76d2b5f4a268c8c102436158054f663362065730c74a" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(d)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//4e28f811-8fff-45e6-887b-97d2a5816414/markdown_0/imgs/img_in_chart_box_406_629_810_860.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-04-26T11%3A54%3A40Z%2F-1%2F%2F2dbc1af1dc67d6a11c7e195a076ffef754b882491b662714dafa30b8d8686964" alt="Image" width="33%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 8. Illustration of the prediction results on five datasets. (a)–(e) are results of the Mackey-Glass, MSO, Lorenz system, NARMA, and ETT datasets, respectively. Figures on the top are prediction results of the initial randomly generated reservoir, with black being the real data and red being the predicted values. It can be seen that after a period of time, the reservoir loses its predictive ability; Figures on the bottom are the prediction results of the optimized reservoir, whose predictive ability has been significantly enhanced.</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Comparison of average orthogonality measurement (OM), ring addition, and optimization running time across different initialization methods for  $ 500 \times 500 $ reservoir digraph matrices.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Random</td><td style='text-align: center; word-wrap: break-word;'>Small-world</td><td style='text-align: center; word-wrap: break-word;'>Scale-free</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Original OM</td><td style='text-align: center; word-wrap: break-word;'>0.3227</td><td style='text-align: center; word-wrap: break-word;'>0.0134</td><td style='text-align: center; word-wrap: break-word;'>0.4795</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Optimized OM</td><td style='text-align: center; word-wrap: break-word;'>0.1397</td><td style='text-align: center; word-wrap: break-word;'>0.0074</td><td style='text-align: center; word-wrap: break-word;'>0.2909</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Added rings</td><td style='text-align: center; word-wrap: break-word;'>112</td><td style='text-align: center; word-wrap: break-word;'>97</td><td style='text-align: center; word-wrap: break-word;'>88</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Running time</td><td style='text-align: center; word-wrap: break-word;'>762.5s</td><td style='text-align: center; word-wrap: break-word;'>540.5s</td><td style='text-align: center; word-wrap: break-word;'>347.5s</td></tr></table>

reservoir, which effectively leverages the greater predictive power of reservoir computing.

Now we begin introducing the results of the average memory capacity (MC) of reservoirs initialized by the three aforementioned methods, both before and after optimization, which demonstrates the improvement achieved by our approach. Here, the  $ k_{max} $ in Eq. (3) was set to  $ 1.4n $ (where n denotes the reservoir size), following the experimental setup described in Farkaš et al. (2016). For illustrative purposes, here we test the three initialization methods on the five datasets mentioned before, and compute the average MC and standard deviation of each tested dataset. The results presented in Table 2 clearly indicate that our method enhances the MC of the reservoirs. Although the initial MC values vary across different initialization methods due to their distinct reservoir architectures, our optimization approach exhibits a consistent effect on each method, leading to improvements in MC across the board. Moreover, it can be concluded that the improvement of the MC is related to the type of dataset and the initialization approach.

The optimization method consistently and effectively enhances the MC across all tested datasets and initialization schemes. However, the magnitude of this improvement varies significantly. For datasets like Mackey-Glass and ETT, the optimized reservoir shows a dramatic increase in MC, suggesting that the optimization is highly effective for these specific types of time series data. In contrast, for the other datasets, the optimization provides a more modest boost to MC. Furthermore, the choice of initialization method plays a crucial role. These results are consistent with our earlier introduction in Section 4.1 that MC depends on the properties of the structure and parameters of reservoirs, and may also be influenced by the data properties.

To further visualize these improvements, we showcase some typical experimental results from our study, as depicted in Fig. 8. After optimization, the duration for which the prediction results remain close to the real dataset is significantly extended compared to the pre-optimization state. This extension not only confirms the observable improvement in prediction length but also quantifies its substantial nature,

<div style="text-align: center;"><div style="text-align: center;">Table 2 Memory Capacity (MC) (Mean±Std) tested on five datasets before and after GLMY theory-based optimization. Here we compared three initialization approaches (Random, Small-world, Scale-free).</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td colspan="4">Mackey-Glass dataset</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Random</td><td style='text-align: center; word-wrap: break-word;'>Small-world</td><td style='text-align: center; word-wrap: break-word;'>Scale-free</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Origin</td><td style='text-align: center; word-wrap: break-word;'>1.6497_{3.3122}</td><td style='text-align: center; word-wrap: break-word;'>4.6585_{6.4405}</td><td style='text-align: center; word-wrap: break-word;'>4.6907_{10.8505}</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GLMY Optimized</td><td style='text-align: center; word-wrap: break-word;'>13.0021_{13.9663}</td><td style='text-align: center; word-wrap: break-word;'>14.6279_{8.1599}</td><td style='text-align: center; word-wrap: break-word;'>14.5722_{11.8339}</td></tr><tr><td colspan="4">MSO dataset</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Random</td><td style='text-align: center; word-wrap: break-word;'>Small-world</td><td style='text-align: center; word-wrap: break-word;'>Scale-free</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Origin</td><td style='text-align: center; word-wrap: break-word;'>3.0975_{2.9030}</td><td style='text-align: center; word-wrap: break-word;'>2.4869_{1.0932}</td><td style='text-align: center; word-wrap: break-word;'>1.8996_{1.8761}</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GLMY Optimized</td><td style='text-align: center; word-wrap: break-word;'>3.4561_{2.2308}</td><td style='text-align: center; word-wrap: break-word;'>2.7297_{1.4397}</td><td style='text-align: center; word-wrap: break-word;'>2.7929_{1.2467}</td></tr><tr><td colspan="4">Lorenz system dataset</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Random</td><td style='text-align: center; word-wrap: break-word;'>Small-world</td><td style='text-align: center; word-wrap: break-word;'>Scale-free</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Origin</td><td style='text-align: center; word-wrap: break-word;'>2.7488_{2.2589}</td><td style='text-align: center; word-wrap: break-word;'>2.8108_{2.3106}</td><td style='text-align: center; word-wrap: break-word;'>2.0317_{0.8796}</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GLMY Optimized</td><td style='text-align: center; word-wrap: break-word;'>5.2335_{3.8498}</td><td style='text-align: center; word-wrap: break-word;'>3.7102_{2.0723}</td><td style='text-align: center; word-wrap: break-word;'>3.9387_{2.5507}</td></tr><tr><td colspan="4">NARMA dataset</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Random</td><td style='text-align: center; word-wrap: break-word;'>Small-world</td><td style='text-align: center; word-wrap: break-word;'>Scale-free</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Origin</td><td style='text-align: center; word-wrap: break-word;'>0.6518_{0.1461}</td><td style='text-align: center; word-wrap: break-word;'>0.5548_{0.2050}</td><td style='text-align: center; word-wrap: break-word;'>0.6869_{0.3268}</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GLMY Optimized</td><td style='text-align: center; word-wrap: break-word;'>0.6923_{0.2479}</td><td style='text-align: center; word-wrap: break-word;'>0.7996_{0.2332}</td><td style='text-align: center; word-wrap: break-word;'>0.7227_{0.2506}</td></tr><tr><td colspan="4">ETT dataset</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Random</td><td style='text-align: center; word-wrap: break-word;'>Small-world</td><td style='text-align: center; word-wrap: break-word;'>Scale-free</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Origin</td><td style='text-align: center; word-wrap: break-word;'>18.0664_{21.5056}</td><td style='text-align: center; word-wrap: break-word;'>7.8563_{9.2927}</td><td style='text-align: center; word-wrap: break-word;'>5.3869_{62.1683}</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GLMY Optimized</td><td style='text-align: center; word-wrap: break-word;'>51.0430_{79.0727}</td><td style='text-align: center; word-wrap: break-word;'>31.4610_{4.9896}</td><td style='text-align: center; word-wrap: break-word;'>21.7803_{18.5071}</td></tr></table>

which can be directly attributed to the enhanced memory capacity of the optimized reservoir. Importantly, this phenomenon was consistently observed across lots of the experimental cases, validating its generality.

Therefore, these results demonstrate that after optimization, the reservoirs exhibit enhanced MC, enabling them to better capture the intrinsic features of the datasets. This improvement in feature capture capability directly translates to a significant enhancement in prediction performance. These results illustrate the effectiveness of our optimization method in boosting reservoir computing performance through memory capacity enhancement.

### 5.5. Prediction performance analysis

Then we compute the average RMSE and standard deviation tested on five datasets before and after optimization using our approach, illustrating the improvement in the performance of reservoirs. The RMSE is computed as

 $$ RMSE=\sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_{i}-\hat{y}_{i})^{2}}, $$ 

where n is the time steps to predict, y_i and \hat{y}_i represent the predict value and real value of the i-step respectively. Table 4 shows the train and test time on the five datasets, $ ^{3} $ and Table 3 summarizes our experimental results, which shows the tested results on five datasets using three different initial construction. Here, “origin” represents the original reservoirs initialized by different approaches. A degree-preserving random rewiring baseline (“Random Rewiring” in the Table) was implemented using repeated edge swaps, ensuring identical in-degree and out-degree distributions. The swapping time is set to 0.3 times the number of edges.

<div style="text-align: center;"><div style="text-align: center;">Table 3 RMSE (Mean±Std) tested on five datasets before and after GLMY theory-based optimization, including a Random Rewiring baseline. Here we compared three initialization approaches (Random, Small-world, Scale-free).</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Random</td><td style='text-align: center; word-wrap: break-word;'>Small-world</td><td style='text-align: center; word-wrap: break-word;'>Scale-free</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>origin</td><td style='text-align: center; word-wrap: break-word;'>$ 2.9505_{1.8449} $</td><td style='text-align: center; word-wrap: break-word;'>$ 1.4882_{1.3749} $</td><td style='text-align: center; word-wrap: break-word;'>$ 1.7773_{0.9896} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>random Rewiring</td><td style='text-align: center; word-wrap: break-word;'>$ 3.6186_{1.3559} $</td><td style='text-align: center; word-wrap: break-word;'>$ 2.3224_{1.8731} $</td><td style='text-align: center; word-wrap: break-word;'>$ 3.4308_{1.4233} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>LMY Optimized</td><td style='text-align: center; word-wrap: break-word;'>$ 0.3039_{0.0228} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.3216_{0.0292} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.3288_{0.0298} $</td></tr><tr><td colspan="4">MSO dataset</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Random</td><td style='text-align: center; word-wrap: break-word;'>Small-world</td><td style='text-align: center; word-wrap: break-word;'>Scale-free</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>origin</td><td style='text-align: center; word-wrap: break-word;'>$ 0.6433_{0.8226} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.7405_{1.0915} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.7579_{0.8848} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>random Rewiring</td><td style='text-align: center; word-wrap: break-word;'>$ 0.2611_{0.0855} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.3496_{0.3952} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.2323_{0.0119} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>iLMY Optimized</td><td style='text-align: center; word-wrap: break-word;'>$ 0.2248_{0.0102} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.2328_{0.0164} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.2216_{0.0081} $</td></tr><tr><td colspan="4">Lorenz system dataset</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Random</td><td style='text-align: center; word-wrap: break-word;'>Small-world</td><td style='text-align: center; word-wrap: break-word;'>Scale-free</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>origin</td><td style='text-align: center; word-wrap: break-word;'>$ 1.0598_{1.2836} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.9786_{1.0647} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.8555_{1.0417} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>random Rewiring</td><td style='text-align: center; word-wrap: break-word;'>$ 1.0706_{1.3901} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.4393_{0.6146} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.3919_{0.4582} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>iLMY Optimized</td><td style='text-align: center; word-wrap: break-word;'>$ 0.2474_{0.0075} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.2454_{0.0088} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.2489_{0.0088} $</td></tr><tr><td colspan="4">NARMA dataset</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Random</td><td style='text-align: center; word-wrap: break-word;'>Small-world</td><td style='text-align: center; word-wrap: break-word;'>Scale-free</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>origin</td><td style='text-align: center; word-wrap: break-word;'>$ 0.1515_{0.0082} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.1580_{0.0141} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.1560_{0.0178} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Random Rewiring</td><td style='text-align: center; word-wrap: break-word;'>$ 0.1539_{0.0056} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.1489_{0.0028} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.1530_{0.0060} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GLMY Optimized</td><td style='text-align: center; word-wrap: break-word;'>$ 0.1487_{0.0028} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.1475_{0.0024} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.1487_{0.0035} $</td></tr><tr><td colspan="4">ETT dataset</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Random</td><td style='text-align: center; word-wrap: break-word;'>Small-world</td><td style='text-align: center; word-wrap: break-word;'>Scale-</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>origin</td><td style='text-align: center; word-wrap: break-word;'>$ 0.4519_{0.0665} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.4438_{0.0358} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.4615_{0.036} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Random Rewiring</td><td style='text-align: center; word-wrap: break-word;'>$ 0.3071_{0.1019} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.1973_{0.0173} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.3465_{0.0849} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GLMY Optimized</td><td style='text-align: center; word-wrap: break-word;'>$ 0.1961_{0.0213} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.1927_{0.0165} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.201^{*} $</td></tr></table>

spectral radius is re-normalized to 0.8 after rewiring, consistent with our optimization method. As reported in Table 3, the random rewiring fails in many cases, which may make the RMSE become larger, while ours can reduce RMSE in all three initialization methods and five datasets. As for our optimization method, for the Random initialization, the initial reservoir digraphs are sparse and hence show weak memory capacities and prediction abilities at first, even if the dataset has obvious topological features. However, our experimental results demonstrate that even highly sparse reservoirs can achieve substantially improved prediction performance through adding the number of rings within their digraph architecture. And for the small-world and scale-free methods, since in some studies they have been proven to be effective initialization ways of reservoirs (Cui et al., 2012; Deng & Zhang, 2006; Kawai et al., 2019), we find that they have already achieve relative good performance of prediction on some datasets. But for these cases, we have also observed that after adding the number of rings, if the original reservoir already possessed great prediction capability (such as the small-world and scale-free method on the NARMA datasets), the modified results can maintain such good capability, i.e., obtaining similar RMSE or lower RMSE. On the contrary, for reservoirs with initially poor prediction capabilities (such as the Mackey-Glass dataset), the optimization process proves to be even more useful, where the modified reservoirs experience a significant enhancement in their prediction power.

Moreover, our optimization method demonstrates varying predictive gains across the evaluated datasets, revealing a compelling Topological Resonance effect that scales with the quantitative Periodicity Index (PI) (Fig. 7). The Mackey-Glass dataset, possessing the highest PI

<div style="text-align: center;"><div style="text-align: center;">Table 4 Comparison of training and testing time (s) across datasets and initialization types.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Dataset</td><td colspan="2">Random</td><td colspan="2">Small-world</td><td colspan="2">Scale-free</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Train</td><td style='text-align: center; word-wrap: break-word;'>Test</td><td style='text-align: center; word-wrap: break-word;'>Train</td><td style='text-align: center; word-wrap: break-word;'>Test</td><td style='text-align: center; word-wrap: break-word;'>Train</td><td style='text-align: center; word-wrap: break-word;'>Test</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Mackey-Glass</td><td style='text-align: center; word-wrap: break-word;'>1.8</td><td style='text-align: center; word-wrap: break-word;'>0.6</td><td style='text-align: center; word-wrap: break-word;'>1.2</td><td style='text-align: center; word-wrap: break-word;'>0.6</td><td style='text-align: center; word-wrap: break-word;'>1.7</td><td style='text-align: center; word-wrap: break-word;'>0.8</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>MSO</td><td style='text-align: center; word-wrap: break-word;'>1.4</td><td style='text-align: center; word-wrap: break-word;'>0.5</td><td style='text-align: center; word-wrap: break-word;'>1.7</td><td style='text-align: center; word-wrap: break-word;'>0.5</td><td style='text-align: center; word-wrap: break-word;'>1.6</td><td style='text-align: center; word-wrap: break-word;'>0.6</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Lorenz System</td><td style='text-align: center; word-wrap: break-word;'>1.4</td><td style='text-align: center; word-wrap: break-word;'>0.7</td><td style='text-align: center; word-wrap: break-word;'>1.9</td><td style='text-align: center; word-wrap: break-word;'>0.7</td><td style='text-align: center; word-wrap: break-word;'>2.0</td><td style='text-align: center; word-wrap: break-word;'>0.5</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>NARMA</td><td style='text-align: center; word-wrap: break-word;'>1.4</td><td style='text-align: center; word-wrap: break-word;'>0.9</td><td style='text-align: center; word-wrap: break-word;'>1.8</td><td style='text-align: center; word-wrap: break-word;'>0.6</td><td style='text-align: center; word-wrap: break-word;'>1.9</td><td style='text-align: center; word-wrap: break-word;'>0.8</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>ETT</td><td style='text-align: center; word-wrap: break-word;'>1.2</td><td style='text-align: center; word-wrap: break-word;'>0.5</td><td style='text-align: center; word-wrap: break-word;'>1.9</td><td style='text-align: center; word-wrap: break-word;'>0.6</td><td style='text-align: center; word-wrap: break-word;'>1.8</td><td style='text-align: center; word-wrap: break-word;'>0.7</td></tr></table>

(0.1696) and prominent loop features, achieves the most dramatic RMSE reduction (a ≈ 90% improvement for random initialization), suggesting that the GLMY optimization effectively aligns the reservoir's engineered cycles with the data's inherent cyclic dynamics. This sensitivity to topological persistence is further corroborated by the results on MSO, Lorenz, and NARMA. These datasets exhibit significantly lower PI values (ranging from 0.0183 to 0.0269) and, as expected, show more constrained performance enhancements. Notably, an interesting observation is found in the ETT dataset. Despite its low PI (0.0135), it exhibits a substantial performance gain (RMSE reduced by ≈ 56% for random initialization). This indicates that our method enhances reservoir performance through two distinct pathways: (1) Topological Resonance: For periodic data, the engineered cycles in the reservoir "resonate" with the data's cyclic attractor. (2) Memory Extension: As shown in Table 2, the GLMY optimization significantly boosts the Memory Capacity (MC) (from 18.06 to 51.04). Since the ETT task involves long-term forecasting, it benefits more from the extended fading memory provided by the ring-like structures, even in the absence of strong periodicity. This dual-pathway mechanism explains the versatility of our method across diverse datasets.

#### 5.6. Discussion

#### 5.6.1. Comparison with traditional topological and spectral approaches

While topological data analysis has been applied to analyze the complexity and decision boundaries of neural networks (Naitzat et al., 2020; Rieck et al., 2019), and spectral graph theory is widely used to ensure the stability of reservoir computing (e.g., the spectral radius condition) (Jaeger, 2001a; Lukoševičius, 2012), they exhibit fundamental limitations when applied to the structural optimization of Reservoir Computing (RC). First, traditional persistent homology typically treats networks as undirected graphs or metric spaces. The resulting topological invariants, such as standard Betti numbers ( $ \beta_{1} $), quantify the number of “holes” or cycles without regard to edge direction. In the context of RC, this is insufficient because an undirected cycle does not necessarily imply a feedback loop, which is the physical mechanism for memory retention. A “hole” in the undirected sense might simply be a feedforward structure, whereas only directed cycles contribute to the recurrent dynamics essential for fading memory. GLMY homology, by contrast, is intrinsically designed for digraphs. It rigorously distinguishes between non-cyclic structures and true directed cycles, ensuring that the optimized topology directly enhances the information recurrence capabilities of the reservoir. Second, spectral graph theory, which analyzes the eigenvalues (spectra) of the Laplacian or Adjacency matrices, provides valuable insights into global properties like network connectivity and stability (e.g., the spectral radius). However, spectral metrics are global statistics; they do not explicitly identify or locate specific local structures that can be surgically modified. For instance, two reservoirs with identical spectral radii can have vastly different cycle distributions and memory capacities. The approach grounded in our GLMY theory provides a perspective that is both local and structural, enabling the accurate identification and modification of particular minimal representative cycles (generators of  $ H_{1} $) to enhance orthogonality. This degree of detail is unattainable through spectral methods.

##### 5.6.2. Quantitative interplay between dataset topology and performance

The predictive performance of our GLMY theory-based optimization demonstrates a strong dependency on the intrinsic topological characteristics of the input stream, as quantified by the Periodicity Index (PI) in Fig. 7. By comparing the performance gains in Table 3 with these PI values, a clear Topological Resonance effect emerges. Specifically, the Mackey-Glass dataset, which possesses the highest PI (0.1696) and exhibits prominent one-dimensional loops in its embedding space, achieves the most dramatic improvement. In the context of reservoir computing, these  $ H_{1} $ loops represent recurrent structures essential for capturing temporal dependencies. Our method explicitly strengthens these minimal representative cycles, allowing the reservoir's optimized digraph to structurally "resonate" with the data's cyclic attractor. This alignment facilitates more accurate detection and storage of periodic patterns, maximizing the model's forecasting accuracy.

However, our study further reveals that the method's effectiveness is not solely restricted to high-PI datasets. A crucial observation is the dual-pathway mechanism of the GLMY theory-based optimization. While datasets like MSO, Lorenz, and NARMA (which have lower PI values (0.0183–0.0269)) show more constrained improvements, the ETT dataset presents a compelling case. Despite having the lowest PI (0.0135), ETT achieves a substantial performance gain. This phenomenon can be comprehensively understood by incorporating the Memory Capacity (MC) analysis from Table 2. Even when the "Topological Resonance" is weak due to indistinct loop features, the GLMY theory-based modification significantly expands the reservoir's fading memory (increasing ETT's MC from 18.06 to 51.04). Hence, the effectiveness of our method is the result of a joint influence: (1) Explicit Structural Alignment: directly matching 1-dimensional topological features for periodic data; (2) Functional Memory Extension: universally enhancing the network's information retention capacity via ring-structured optimization. Only when the method can effectively identify and utilize the topological foundation of the dataset, or significantly boost the requisite memory for the task, can it achieve significant improvements. This provides a generalized framework for understanding how structural optimization interacts with the complex dynamics of time-series data, offering valuable insights for integrating topological analysis with complex system modeling.

##### 5.6.3. Limitations

There are some limitations of our method. First, in this study, we exclude consideration of bidirectional edges (referred to as bigons in the context of GLMY homology), and also, our approach neither captures nor modifies boundary triangles and boundary squares, as they do not constitute generators of GLMY homology, despite being cycles. In dense reservoir digraphs, as the connection density is large, boundary triangles can be numerical, making the number of representative cycles small. But for a sparse reservoir digraph, the boundary cycles are significantly less than the representative cycles; the majority of cycles can still be transformed into rings, thereby enhancing the reservoir's prediction capability. Hence, our method is more suitable for optimizing sparse reservoirs. And since many rings can share common edges (which means their corresponding fundamental cycle submatrices will share common columns), the increased number of rings is not proportional to improved orthogonality. It is still worthwhile studying more efficient and reasonable methods for improving orthogonality.

Additionally, providing a rigorous theoretical explanation for our method's efficacy on large-scale random sparse reservoirs remains challenging. This absence of strict theoretical bounds introduces the potential for performance variance. Given the intricate dynamics of reservoirs, certain pathological initializations may exist where modifying representative cycles inadvertently disrupts advantageous hidden substructures, resulting in marginal gains or localized performance degradation. In our future work, we will continue to study relevant theoretical

explanations. Moreover, the computational efficiency also becomes a concern for dense reservoirs or large reservoirs, as our method computes GLMY homology and modifies edge directions iteratively, which can be time-intensive. Our future research directions will focus on investigating the theoretical relationship between reservoir topology and computational capability, and developing accelerated algorithms for GLMY homology computation and our algorithm.

### 6. Conclusions

In this study, we proposed a novel approach to optimize the structure of the reservoirs using GLMY homology theory. We begin by computing the one-dimensional GLMY homology of the reservoir digraph to obtain the corresponding minimal representative cycles. These cycles are then utilized to strategically modify the digraph structure in a compatible way, specifically increasing the number of rings within the reservoir. Experimental results demonstrate that this topological optimization leads to improved predictive performance across our tested datasets, and the proposed method performs better on datasets with significant 1-dimensional topological features.

### CRediT authorship contribution statement

Yu Chen: Conceptualization, Investigation, Formal analysis, Methodology, Software, Validation, Visualization, Writing – original draft, Writing – review & editing. Shengwei Wang: Methodology, Investigation, Software, Validation, Writing – original draft, Writing – review & editing. Hongwei Lin: Conceptualization, Methodology, Supervision, Funding acquisition, Writing – original draft, Writing – review & editing.

### Data availability

The raw Electricity Transformer Dataset (ETT) is available at https://github.com/zhouhaoyi/ETDataset/tree/main.

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Declaration of competing interest

#### Acknowledgment

This work was partially supported by National Natural Science Foundation of China under Grant No. 62272406 and Leading Goose R&D Program of Zhejiang under Grant No. 2024C01103.

## References

Ahmed, F., Aziz, M. S. A., Shaik, F., & Khor, C. Y. (2024). Experimental and numerical investigation of an innovative desalination unit under laminar, transient, and turbulent flow conditions. Chemical Engineering Research and Design, 208, 683–694.

Ahmed, F., Mohammed, N., Mewada, H., Aziz, M. S. A., & Khor, C. Y. (2025). An experimental evaluation, performance analysis, and improvement of water desalination system using optimized machine learning. Process Integration and Optimization for Sustainability. https://doi.org/10.1007/s41660-025-00595-8

Barabási, A.-L., & Albert, R. (1999). Emergence of scaling in random networks. Science, 286(5439), 509–512.

Barančok, P., & Farkaš, I. (2014). Memory capacity of input-driven echo state networks at the edge of chaos. In Artificial neural networks and machine learning—ICANN 2014: 24th international conference on artificial neural networks, hamburg, germany, september 15–19, 2014. proceedings 24 (pp. 41–48). Springer.

Benedetto, J. J., & Fickus, M. (2003). Finite normalized tight frames. Advances in Computational Mathematics, 18(2), 357–385.

Chen, Y., & Lin, H. (2025). Analyzing singular patterns in discrete planar vector fields via persistent path homology. Computers & Graphics, 132, (p. 104354).

Chowdhury, S., Gebhart, T., Huntsman, S., & Yutin, M. (2019). Path homologies of deep feedforward networks. In 2019 18th IEEE international conference on machine learning and applications (ICMLA) (pp. 1077–1082). IEEE.

Chowdhury, S., Huntsman, S., & Yutin, M. (2020). Path homology and temporal networks. In International conference on complex networks and their applications (pp. 639–650). Springer.

Chowdhury, S., & Mémoli, F. (2018). Persistent path homology of directed networks. In Proceedings of the twenty-ninth annual ACM-SIAM symposium on discrete algorithms (pp. 1152–1169). SIAM.

Cui, H., Liu, X., & Li, L. (2012). The architecture of dynamic reservoir in the echo state network. Chaos: An Interdisciplinary Journal of Nonlinear Science, 22(3), (pp. 033127).

Deng, Z., & Zhang, Y. (2006). Complex systems modeling using scale-free highly-clustered echo state network. In The 2006 IEEE international joint conference on neural network proceedings (pp. 3128–3135). IEEE.

Dey, T. K., Li, T., & Wang, Y. (2022). An efficient algorithm for 1-dimensional (persistent) path homology. Discrete & Computational Geometry, 68(4), 1102–1132.

Donoho, D. L., Huo, X. et al. (2001). Uncertainty principles and ideal atomic decomposition. IEEE Transactions on Information Theory, 47(7), 2845–2862.

Edelsbrunner, H., & Harer, J. (2010). Computational topology: An introduction. American Mathematical Soc.

Edelsbrunner, H., Harer, J. et al. (2008). Persistent homology-a survey. Contemporary Mathematics, 453(26), 257–282.

Farkaš, I., Bosák, R., & Gergel', P. (2016). Computational analysis of memory capacity in echo state networks. Neural Networks, 83, 109–120.

Fasy, B. T., Lecci, F., Rinaldo, A., Wasserman, L., Balakrishnan, S., & Singh, A. (2014). Confidence sets for persistence diagrams. The Annals of Statistics, 42(6), 2301.

Feng, L., Gong, H., Zhang, S., Liu, X., Wang, Y., Che, J., Dong, A., Griffin, C. H., Gragnoli, C., Wu, J. et al. (2024). Hypernetwork modeling and topology of high-order interactions for complex systems. Proceedings of the National Academy of Sciences, 121(40), e2412220121.

Gaier, A., & Ha, D. (2019). Weight agnostic neural networks. Advances in neural information processing systems, 32. https://proceedings.neurips.cc/paper/2019/hash/e98741479a7b998f88b8f8c9f0b6b6f1-Abstract.html

Gallicchio, C., & Micheli, A. (2019). Reservoir topology in deep echo state networks. In Artificial neural networks and machine learning—ICANN 2019: Workshop and special sessions: 28th international conference on artificial neural networks, munich, germany, september 17–19, 2019, proceedings 28 (pp. 62–75). Springer.

Goodfellow, I., Bengio, Y., Courville, A., & Bengio, Y. (2016). Deep learning (vol. 1). MIT press Cambridge.

Grigor'yan, A., Jimenez, R., Muranov, Y., & Yau, S.-T. (2019). Homology of path complexes and hypergraphs. Topology and its Applications, 267, 106877.

Grigor'yan, A., Lin, Y., Muranov, Y., & Yau, S.-T. (2012). Homologies of path complexes and digraphs. arXiv:1207.2834.

Grigor'yan, A., Lin, Y., Muranov, Y., & Yau, S.-T. (2014). Homotopy theory for digraphs. arXiv:1407.0234.

Grigor'yan, A., Muranov, Y., Vershinin, V., & Yau, S.-T. (2018). Path homology theory of multigraphs and quivers. In Forum mathematicum (pp. 1319–1337). De Gruyter (vol. 30).

Hornik, K., Stinchcombe, M., & White, H. (1989). Multilayer feedforward networks are universal approximators. Neural Networks, 2(5), 359–366.

Jaeger, H. (2001a). The "echo state" approach to analysing and training recurrent neural networks-with an erratum note. Bonn, Germany: German National Research Center for Information Technology GMD Technical Report, 148(34), 13.

Jaeger, H. (2001b). Short term memory in echo state networks. Technical Report 152, GMD

Forschungszentrum Informationstechnik. https://publica.fraunhofer.de/handle/publica/291107

Jaeger, H., & Haas, H. (2004). Harnessing nonlinearity: Predicting chaotic systems and saving energy in wireless communication. Science, 304(5667), 78–80.

Kawai, Y., Park, J., & Asada, M. (2019). A small-world topology enhances the echo state property and signal propagation in reservoir computing. Neural Networks, 112, 15–23. LeCun, Y., Bengio, Y., & Hinton, G. (2015). Deep learning, Nature, 521(7553), 436–444.

Lin, Y., Wang, C., & Yau, S.-T. (2021). Discrete morse theory on digraphs. arXiv:2102.10518.

Liu, J., Chen, D., Pan, F., & Wu, J. (2023). Neighborhood path complex for the quantitative analysis of the structure and stability of carboranes. Journal of Computational Biophysics and Chemistry, 22(04), 503–511.

Lukoševičius, M. (2012). A practical guide to applying echo state networks. In Neural networks: Tricks of the trade: Second edition (pp. 659–686). Springer.

Lukoševičius, M., & Jaeger, H. (2009). Reservoir computing approaches to recurrent neural network training. Computer Science Review, 3(3), 127–149.

Montavon, G., Samek, W., & Müller, K.-R. (2018). Methods for interpreting and understanding deep neural networks. Digital Signal Processing, 73, 1–15.

Naitzat, G., Zhitnikov, A., & Lim, L.-H. (2020). Topology of deep neural networks. Journal of Machine Learning Research, 21(184), 1–40.

Pathak, J., Hunt, B., Girvan, M., Lu, Z., & Ott, E. (2018). Model-free prediction of large spatiotemporally chaotic systems from data: A reservoir computing approach. Physical review letters, 120(2), 024102.

Perea, J. A., & Harer, J. (2015). Sliding windows and persistence: An application of topological methods to signal analysis. Foundations of Computational Mathematics, 15(3), 799–838.

Rieck, B. A., Togninalli, M., Bock, C., Moor, M., Horn, M., Gumbsch, T., & Borgwardt, K. (2019). Neural persistence: A complexity measure for deep neural networks using algebraic topology. In International conference on learning representations (ICLR) 2019.

Rodan, A., & Tino, P. (2010). Minimum complexity echo state network. IEEE Transactions on Neural Networks, 22(1), 131–144.

Roeschies, B., & Igel, C. (2010). Structure optimization of reservoir networks. Logic Journal of IGPL, 18(5), 635–669.

Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). Learning representations by back-propagating errors. Nature, 323(6088), 533–536.

Shougat, M. R. E. U., Li, X., Mollik, T., & Perkins, E. (2021). A Hopf physical reservoir computer. Scientific Reports, 11(1), 19465.

Skowronski, M. D., & Harris, J. G. (2007). Noise-robust automatic speech recognition using a predictive echo state network. IEEE Transactions on Audio, Speech, and Language Processing, 15(5), 1724–1730.

Stockdill, A., & Neshatian, K. (2016). Restricted echo state networks. In Ai 2016: Advances in artificial intelligence: 29th australasian joint conference, hobart, tas, australia, december 5–8, 2016, proceedings 29 (pp. 555–560). Springer.

Strauss, T., Wustlich, W., & Labahn, R. (2012). Design strategies for weight matrices of echo state networks. Neural Computation, 24(12), 3246–3276.

Sun, X.-c., Cui, H.-y., Liu, R.-p., Chen, J.-y., & Liu, Y.-j. (2012). Modeling deterministic echo state network with loop reservoir. Journal of Zhejiang University SCIENCE C, 13(9), 689-701.

Takens, F. (2006). Detecting strange attractors in turbulence. In Dynamical systems and turbulence, warwick 1980: Proceedings of a symposium held at the university of warwick 1979/80 (pp. 366–381). Springer.

Venayagamoorthy, G. K., & Shishir, B. (2009). Effects of spectral radius and settling time in the performance of echo state networks. Neural Networks, 22(7), 861–863.

Wang, W.-J., Tang, Y., Xiong, J., & Zhang, Y.-C. (2021). Stock market index prediction based on reservoir computing models. Expert Systems with Applications, 178, 115022.

Watts, D. J., & Strogatz, S. H. (1998). Collective dynamics of 'small-world' networks. Nature, 393(6684), 440–442.

Yao, X., Wang, Z., & Zhang, H. (2019). Prediction and identification of discrete-time dynamic nonlinear systems based on adaptive echo state network. Neural Networks, 113, 11–19.

Zhang, B., He, Z., & Lin, H. (2024). A comprehensive review of deep neural network interpretation using topological data analysis. Neurocomputing, 609, 128513.

Zhou, H., Zhang, S., Peng, J., Zhang, S., Li, J., Xiong, H., & Zhang, W. (2021). Informer: Beyond efficient transformer for long sequence time-series forecasting. In The thirty-fifth AAAI conference on artificial intelligence, AAAI 2021, virtual conference (pp. 11106–11115). AAAI Press (vol. 35).

