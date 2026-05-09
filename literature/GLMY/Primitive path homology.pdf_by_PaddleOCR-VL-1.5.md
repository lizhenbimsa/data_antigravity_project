# Primitive path homology

Jingyan Li

Beijing Institute of

Mathematical Sciences and

Application, Beijing, China

Yuri Muranov

University of Warmia and

Mazury in Olsztyn, Olsztyn

Poland

Jie Wu

Beijing

Institute of Mathematical

Sciences and Application,

Beijing, China

Shing-Tung Yau

Tsinghua University,

Beijing, China

November, 2024

## Abstract

In this paper we introduce a primitive path homology theory on the category of simple digraphs. On the subcategory of asymmetric digraphs, this theory coincides with the path homology theory which was introduced by Grigor'yan, Lin, Muranov, and Yau, but these theories are different in general case. We study properties of the primitive path homology and describe relations between the primitive path homology and the path homology. Let a, b two different vertices of a digraph. Our approach gives a possibility to construct primitive homology theories of paths which have a given tail vertex a or (and) a given head vertex b. We study these theories and describe also relationships between them and the path homology theory.

Keywords: path homology theory, chain complex, path in digraph, paths with fixed tail vertex, paths with fixed head vertex, paths with fixed ends.

AMS Mathematics Subject Classification 2020: 55N35, 05C20, 05C38, 05C25, 55U15.

## Contents

1 Introduction 2    
2 The path homology 4    
3 Primitive path homology 8    
4 Cluster digraphs 18    
5 Primitive homology of cluster digraphs 22    
6 Primitive homology of paths with a fixed tail or a head vertex 30    
7 Functionality 36

## 1 Introduction

In this paper, we develop the path homology theory (GLMY theory) that was created by Grigor'yan, Lin, Muranov, and Yau in [5], [8], [9], [10]. The path homology theory closely relates to other homology theories on discrete objects. The simplicial homology of a simplicial complex is isomorphic to the path homology of a digraph which is functorially defined by the complex [12]. The deep relations between the path cohomology theory of digraphs, and Hochschild cohomology of algebras were obtained in [13]. The category of discrete spaces coincides with the category of transitive digraphs, and hence, Alexandroff homology [1] gives a homology of transitive digraphs which coincides with the path homology [17]. The singular cubic homology coincides with the path homology in the category of transitive digraphs and in the category of cubical digraphs [18], [11] but these homology theories are different in general [4, Pr. 13, Pr. 14].

Recently, a cell approach was developed to study path homology in [3], [6], [14], [19], [20], and the path homology of cycles, circuits and closed walk was constructed in [15] and [16]. In both approaches, paths with some restrictions on the tail and head vertex arise naturally.

In this paper, we introduce a primitive path homology theory on the category of simple digraphs. This theory coincides with the path homology theory on the subcategory of simple asymmetric digraphs and differs from the path homology theory in general. We study properties of the primitive path homology and describe relations between this homology and the path homology. Let a, b be two different vertices of a digraph. Our approach gives a possibility to construct primitive homology theories of paths that have a given tail vertex a or (and) a given head vertex b. We also describe relations between these theories, the path homology and the path homology of clusters which were defined in [6]. We give a number of examples that illustrate the results obtained. The paper is organized as follows.

In Section 2, we recall the basic definitions of the digraph theory and introduce the path homology theory of digraphs.

In Section 3, we define and study the primitive path homology theory of digraphs. We describe relations between primitive path homology and the path homology and provide several examples. In particular, we prove that the primitive path homology coincides with the path homology on the category of asymmetric digraphs and give an example which shows that these theories differ in general.

In Section 4, we define a cluster subgraph  $ G^{[a,b]} $ of a digraph G. The cluster digraph  $ G^{[a,b]} $ in G is a subgraph given by all vertices and all arrows of paths with a tail vertex a and a head vertex b in the digraph G. We describe relations between primitive homology of cluster digraphs and primitive homology of ambient digraphs. Similarly, we define tail fixed digraphs, and head fixed digraphs which are subgraphs of a digraph G and describe its relations to the primitive path homology of cluster digraphs and ambient digraphs.

In Section 5, for a digraph  $  G = (V, E)  $ and two vertices  $  a, b \in V  $, we define a primitive homology of paths which have the tail vertex  $  a  $ and the head vertex  $  b  $. We call this homology by primitive  $  (a, b)  $-cluster homology of the digraph  $  G  $. We describe basic properties of this homology and its relation to primitive homology of the cluster digraph in  $  G  $ and to primitive homology of  $  G  $. We provide also several examples.

In Section 6, we introduce the primitive homology of paths with a fixed tail vertex and the primitive homology of paths with a fixed head vertex. We describe relations between them and its relations to the various primitive homology which are considered in Section 5. We provide also several examples.

In Section 7, we prove functionality of primitive homology theories constructed in Sections 5 and 6 on the category  $ AD $ of asymmetric digraphs.

## Acknowledgments

This work is supported by the start-up research funds of the first author and the third author from BIMSA. The third author was supported by High-Level Scientific Research Foundation of Hebei Province.

## 2 The path homology

In this section, we recall the necessary notions of the graph theory and the path homology theory [2], [8], [9], [12], [13], [6].

In this paper, we only consider simple digraphs  $ G = (V_G, E_G) $ with a nonempty and finite set  $ V_G $ of vertices and with a set  $ E_G $ of ordered pairs  $ (v, w) \in E_G $ of different vertices  $ v, w \in V $. A pair  $ (v, w) \in E_G $ is called an arrow, denoted  $ v \to w $, where  $ v $ is the tail and  $ w $ is the head of the arrow. In this case we write  $ v = t(v \to w) $ and  $ w = h(v \to w) $. For two vertices  $ v, w \in V_G $ the arrows  $ v \to w, w \to v \in E_G $ are called symmetric. A digraph  $ G $ is called asymmetric if it doesn't contain symmetric arrows.

A digraph $G = (V_G, E_G)$ is a subgraph of a digraph $H = (V_H, E_H)$, and we write $G \sqsubset H$, if $V_G \subset V_H$ and $E_G \subset V_H$. A subgraph $G \sqsubset H$ is called the induced subgraph and is denoted $G \subset H$, if for any $v, w \in E_G \subset E_H$ and $(v \to w) \in E_H$ implies $(v \to w) \in E_G$. Any subgraph $G \sqsubset H$ uniquely defines an minimal induced subgraph $\overline{G} \subset H$ containing $G$.

Let $G$ and $H$ be two digraphs. A map $f: G \to H$ is given by a map $f: V_G \to V_H$ of vertices such that for every arrow $(v \to w) \in E_G$ we have either $(f(v) \to f(w)) \in E_H$ or $f(v) = f(w) \in V_H$. A map $f: G \to H$ is a homomorphism if $(f(v) \to f(w)) \in E_H$ for any $(v \to w) \in E_G$.

Thus we obtain the category $\mathcal{D}$ of digraphs and digraph maps. By a natural way, there are two subcategory of $\mathcal{D}$ defined. We have a subcategory $\mathcal{N}\mathcal{D} \subset \mathcal{D}$ with the same set of objects as in $\mathcal{D}$ and with the morphisms which are homomorphisms and a subcategory $\mathcal{A}\mathcal{D} \subset \mathcal{D}$ with the same set of morphisms as in $\mathcal{D}$ and with the set of objects consisting of asymmetric digraphs.

Recall the definition of path homology groups of a digraph G with coefficients in a unitary commutative ring R. Let V be a finite set whose elements we call vertices. For  $ n \geq 0 $, an elementary n-path in V is any sequence  $ i_0, \ldots, i_n $ of vertices. Let  $ \Lambda_n = \Lambda_n(V, R) $ be a free R-module generated by the elements  $ e_{i_0 \ldots i_n} $ where  $ i_0, \ldots, i_n $ is an elementary n-path in V. The elements of  $ \Lambda_n $ are called n-paths in V. We set also  $ \Lambda_{-1} = 0 $. For  $ n \geq 1 $, define the homomorphism (differential)  $ \partial: \Lambda_n \to \Lambda_{n-1} $ by setting on basic elements

 $$ \partial(e_{i_{0}\ldots i_{n}})=\begin{cases}\displaystyle\sum_{m=0}^{n}(-1)^{m}e_{i_{0}\ldots\widehat{i_{m}\ldots i_{n}}}&for n\geq1,\\0&for n=0.\end{cases} $$ 

where  $ \widehat{i_m} $ means omitting the vertex  $ i_m $. For  $ n \geq 0 $, we can write down the differential in the form

 $$ \partial(e_{i_{0}\ldots i_{n}})=\sum_{m=0}^{n}(-1)^{m}\partial^{m}(e_{i_{0}\ldots i_{n}}) $$ 

where  $ \partial^m\colon \Lambda_n \to \Lambda_{n-1} $ is a homomorphism given on the basic elements by

 $$ \partial^{m}(e_{i_{0}\ldots i_{n}})=\begin{cases}e_{i_{0}\ldots i_{m}\ldots i_{n}}&for n\geq1,0\leq m\leq n,\\0&for m=n=0.\end{cases} $$ 

The differential $\partial$ has the property $\partial \circ \partial = 0$ and the modules $\Lambda_n$ with the differential $\partial$ form a chain complex $\Lambda_* = \Lambda_*(V, R)$.

We call an elementary path  $ e_{i_0...i_n} $ irregular if the path  $ i_0, \ldots, i_n $ has two equal consecutive vertices and regular otherwise.

For  $ n \geq 1 $, let  $ I_n = I_n(V, R) $ be a submodule of  $ \Lambda_n(V, R) $ that is generated by all irregular elementary paths. Set  $ I_0 = I_{-1} = 0 $. For  $ n \geq -1 $, denote by  $ \mathcal{R}_n = \mathcal{R}_n(V, R) $ the quotient module  $ \Lambda_n/I_n = \Lambda_n(V, R)/I_n(V, R) $. The elements of modules  $ \mathcal{R}_n $ we will continue to call regular paths in the set  $ V $.

Since  $ \partial(I_n) \subset I_{n-1} $, the modules  $ \mathcal{R}_n $ with the induced differential  $ \partial $, which we continue to denote  $ \partial $, form a chain complex  $ \mathcal{R}_* $.

Let  $  G = (V_G, E_G)  $ be a digraph. For  $  n \geq 1  $, an elementary path  $  e_{i_0...i_n}  $ in  $  V_G  $ is called allowed if  $  (i_k \to i_{k+1}) \in E_G  $ for  $  0 \leq k \leq n-1  $. We note that every allowed path is regular since we consider only simple digraphs. The length of an allowed path  $  e_{i_0...i_n}  $ equals  $  n  $ and it is denoted by  $  |e_{i_0...i_n}|  $. Every path  $  e_{i_0}  $ is allowed and has the length 0. For an allowed path  $  e_{i_0...i_n}  $ we call the vertex  $  i_0 = t(e_{i_0...i_n})  $ by the tail of the path and the vertex  $  i_n = h(e_{i_0...i_n})  $

by the head of the path. The oriented distance  $ d(v,w) $ between two vertices  $ v,w \in E_G $ is the minimal length of an allowed path with the tail  $ v $ and the head  $ w $. If such a path doesn't exist then the distance equals  $ \infty $.

For  $ n \geq 0 $, let  $ \mathcal{A}_n = \mathcal{A}_n(G, R) $ be a module that is generated by all allowed elementary n-paths and let  $ \mathcal{A}_{-1} = 0 $. We set also  $ \mathcal{A}_n = 0 $ ( $ n \geq 1 $) if elementary allowed n-paths do not exist in  $ G $. We will continue to call elements of  $ \mathcal{A}_n(G) $ by allowed paths. This module can be naturally considered as a submodule of  $ \mathcal{R}_n(V_G, R) = \mathcal{R}_n(V_G) $. The inclusion  $ \eta: \mathcal{A}_n(G) \to \mathcal{R}_n(V_G) $ is given on the allowed elementary paths  $ e_{i_0\ldots i_n} $, which form the basis of  $ \mathcal{A}_n(G) $, by  $ \eta(e_{i_0\ldots i_n}) = [e_{i_0\ldots i_n}] $ where the classes  $ [e_{i_0\ldots i_n}] $ give a basis of  $ \eta(A_n(G)) \subset \mathcal{R}_n(G) $. For  $ n \geq 0 $, define a submodule  $ \Omega_n(G, R) \subset \mathcal{R}_n(V_G, R) $ by setting

 $$ \Omega_{n}=\Omega_{n}(G)=\Omega_{n}(G,R)=\left\{w\in\mathcal{A}_{n}(G)\mid\partial w\in\mathcal{A}_{n-1}(G)\right\}, $$ 

where $\partial$ is the differential $\partial\colon\mathcal{R}_n(V_G)\to\mathcal{R}_{n-1}(V_G)$. We set $\Omega_{-1}=0$. It follows from (2.3) that $\partial(\Omega_n)\subset\Omega_{n-1}$ for $n\geq0$. Hence, the modules $\Omega_n$ with the differential $\partial$ form a chain complex $\Omega_*$ which we call a path chain complex of the digraph $G$.

The homology groups  $ H_{*}(\Omega_{*}) $ are called path homology groups of the digraph G and are denoted by  $ H_{*}(G)=H_{*}(G,R) $.

A digraph map $f\colon G\to H$ induces a morphism of chain complexes $f_{*}\colon\Omega_{*}(G,R)\to\Omega_{*}(H,R)$ which on the set of allowed elementary paths is given by the condition

 $$ f_{*}(e_{i_{0}\ldots i_{n}})=\begin{cases}{e_{f(i_{0})\ldots f(i_{n})}}&{\mathrm{i f~}f(i_{j})\neq f(i_{j+1})\mathrm{~f o r~a n y~}0\leq i_{j}\leq n-1,}\\ {0}&{\mathrm{o t h e r w i s e.}}\\ \end{cases} $$ 

We obtain an induced homomorphism  $ f_*\colon H_*(G,R) \to H_*(H,R) $. Thus, the path homology is functorial on the categories  $ \mathcal{D} $,  $ \mathcal{N}\mathcal{D} $, and  $ \mathcal{A}\mathcal{D} $.

Recall the notion of an augmentation of a chain complex  $ C_*(C_n, \partial)(n \geq 0) $ of  $ R $-modules with a differential  $ \partial: C_n \to C_{n-1} $. An augmentation of  $ C_* $ is given by a homomorphism

 $$ \varepsilon\colon C_{0}\longrightarrow R\mathrm{~s u c h~t h a t~}\varepsilon\partial=0. $$ 

Thus we obtain an augmented chain complex

 $$ \ldots\stackrel{\partial}{\longrightarrow}C_{2}\stackrel{\partial}{\longrightarrow}C_{1}\stackrel{\partial}{\longrightarrow}C_{0}\stackrel{\varepsilon}{\longrightarrow}R\longrightarrow0. $$ 

which we denote  $ \widetilde{C}_{*} $

Definition 2.1 The reduced homology  $ \tilde{H}(C_{*}) $ of a chain complex  $ C_{*} $ is the homology of the augmented chain complex  $ \tilde{C}_{*} $ in (2.5).

For every set V, the chain complex  $ \Lambda_{*}(V, R) $ has the natural augmentation

 $$ \varepsilon\colon\Lambda_{0}(G,R)\longrightarrow R,\ \varepsilon\left(\sum_{i}r^{i}e_{i}\right)=\sum_{i}r^{i}\ \mathrm{w h e r e}\ r^{i}\in R,\ i\in V. $$ 

For a digraph $G$, the augmentation of the chain complexes $\mathcal{R}_*(V_G, R)$ and $\Omega_*(G, R)$ is defined similarly (2.6). Hence, for every digraph $G$, the augmented path homology groups $\widetilde{H}_*(G) = \widetilde{H}_*(G, R)$ are defined.

Let $G$ be a digraph and $w \in \mathcal{A}_n(G, R)$ be an allowed path. For $n \geq 1$, we can write $w$ in the form

 $$ w=\sum_{a,b\in V}w^{[a,b]},\quad w^{[a,b]}=\sum_{i_{0}=a,i_{n}=b}r^{i_{0}i_{1}\ldots i_{n-1}i_{n}}e_{i_{0}i_{1}\ldots i_{n-1}i_{n}} $$ 

where  $ r^{i_{0}i_{1}\ldots i_{n-1}i_{n}} \in R $ and  $ e_{i_{0}i_{1}\ldots i_{n-1}i_{n}} $ is an elementary allowed path with

 $$ a=i_{0}=t\left(e_{i_{0}i_{1}\ldots i_{n-1}i_{n}}\right),\quad b=i_{n}=h\left(e_{i_{0}i_{1}\ldots i_{n-1}i_{n}}\right). $$ 

We set  $ w^{[a,b]}=0 $ if there are no elementary paths fitting into  $ w $ with the tail vertex  $ a $ and the head vertex  $ b $. For  $ n=0 $ and  $ a\neq b $ we have  $ w^{[a,b]}=0 $. For  $ a=b $ we have  $ w^{[a,a]}=0 $ for  $ n=1 $ and  $ w^{[a,a]}=r^a e_a $ ( $ a\in V $) for  $ n=0 $. Hence, for  $ a=b $ we can write every path  $ w\in\mathcal{A}_0(G) $ in the form similar to (2.7)

 $$ w=\sum_{a\in V}w^{[a,a]}=\sum_{a\in V}r^{a}e_{a},\ r^{a}\in R. $$ 

Definition 2.2 For  $ n \geq 1 $, a path  $ w^{[a,b]} \in \mathcal{A}_n(G) $ in (2.7) and for  $ n = 0 $ a path  $ w^{[a,a]} \in \mathcal{A}_0(G) $ in (2.8) is called a cluster path in dimension  $ n \geq 0 $ (see also [6, §2.2]). The cluster path is elementary if it is given by an elementary path.

Now we slightly reformulate the result from [6, Lemma 2.2].

Theorem 2.3 Let $G$ be a digraph and $w \in \mathcal{A}_n(G)$ ($n \geq 0$). Then $w \in \Omega_n(G)$ if and only if $w^{[a,b]} \in \Omega_n(G)$ for every $w^{[a,b]}$ fitting into the decomposition $w$ in (2.7) or in (2.8).

Proof. For $n=0$ it is nothing to prove. For $n\geq1$, if $w^{[a,b]}\in\Omega_{n}(G)$ then $\partial(w^{[a,b]})\in\mathcal{A}_{n-1}(G)$ and

 $$ \partial(w)=\partial\left(\sum_{a,b\in V}w^{[a,b]}\right)=\sum_{a,b\in V}\partial(w^{[a,b]})\in\mathcal{A}_{n-1}. $$ 

Hence  $ w \in \Omega_n(G) $. The inverse statement is proved in [6, Lemma 2.2] ■

By technical reasons, we set  $ \Omega_n^{[a,b]}(G) = 0 $ if there are no  $ (a,b) $-cluster paths in dimension  $ n $.

Corollary 2.4 For every digraph  $  G = (V, E)  $ and  $  n \geq 0  $, the module  $ \Omega_n(G) $ is a direct sum of submodules

 $$ \Omega_{n}(G)=\bigoplus_{a,b\in V}\Omega_{n}^{[a,b]}(G) $$ 

where

 $$ \Omega_{n}^{[a,b]}(G)=\langle w^{[a,b]}\in\Omega_{n}(G)\mid a,b\in V\rangle $$ 

is generated by  $ (a,b) $-cluster paths in dimension n.

## 3 Primitive path homology

In this Section we define a primitive path homology of digraphs and describe its relation to the path homology. We prove that these theories coincide on the category  $ \mathcal{A}\mathcal{D} $ of asymmetric digraphs. We describe algebraic properties of the primitive homology and provide an example which illustrate the difference between the primitive path homology and the path homology.

Let $G$ be a digraph and $R$ be a ring of coefficients. We note that for $n \geq -1$ the module $\mathcal{A}_n(G)$ is a submodule of $\Lambda_n(V_G)$. For $n \geq 0$, define a submodule

 $$ \Pi_{n}=\Pi_{n}(G)=\left\{w\in\mathcal{A}_{n}(G)\mid\partial w\in\mathcal{A}_{n-1}(G)\right\} $$ 

where $\partial: \Lambda_n(V_G) \to \Lambda_{n-1}(V_G)$ is the differential in (2.1). We set $\Pi_{-1}(G) = 0$. It follows immediately from (3.1) that $\partial(\Pi_n) \subset \Pi_{n-1}$ for $n \geq 0$ and, hence, the modules $\Pi_n(G)$ with the restriction of the differential $\partial$ form a chain complex $\Pi_* = \Pi_*(G)$. By (3.1) and (2.3, for any digraph $G = (V, E)$ we have

 $$ \Pi_{0}(G)=\Omega_{0}(G)=\langle e_{i}\mid i\in V\rangle,\Pi_{1}(G)=\Omega_{1}(G)=\langle e_{i j}\mid(i\to j)\in E\rangle. $$ 

Definition 3.1 The homology groups of the chain complex  $ \Pi_*(G) $ are called primitive path homology groups with the coefficients  $ R $ of a digraph  $ G $ and are denoted by  $ \mathcal{H}_n(G) = \mathcal{H}_n(G, R) \, (n \geq 0) $.

Example 3.2 Consider the complete digraph  $  G = (V, E)  $ with the set of vertices  $  V = \{0, 1\}  $ and the set of arrows  $  E = \{0 \to 1, 1 \to 0\}  $. Let  $  R = \mathbb{Z}  $. The digraph  $  G  $ is homotopy equivalent to the one-vertex digraph and, hence,

 $$ H_{n}(G)=\begin{cases}\mathbb{Z}&for n=0,\\0&otherwise\end{cases} $$ 

since the path homology is homotopy invariant [9]. Now we compute primitive path homology groups of $G$. By (3.2) we have $\Pi_0(G) = \mathcal{A}_0(G) = \langle e_0, e_1 \rangle$ and $\Pi_1(G) = \mathcal{A}_1(G) = \langle e_{01}, e_{10} \rangle$. For $n \geq 2$, we have

 $$ \mathcal{A}_{n}(G)=\begin{cases}\langle e_{\underbrace{01\cdots10}_{n+1}},\ e_{\underbrace{10\cdots01}_{n+1}}\rangle&for n=2k,\\\langle e_{\underbrace{01\cdots01}_{n+1}},\ e_{\underbrace{10\cdots10}_{n+1}}\rangle&for n=2k+1.\end{cases} $$ 

Now we define the groups $\Pi_n(G)$ for $n \geq 2$. For $n = 2k \geq 2$, the differential $\partial: \Lambda_n(G) \to \Lambda_{n-1}(G)$ on the basic element $e_{\underbrace{n+1}_{n+1} \cdots \underbrace{n}_{n-1}} \in \mathcal{A}_n(G)$ contains the non-canceled summand $\partial^1(e_{\underbrace{n+1}_{n+1} \cdots \underbrace{n}_{n-1}}) = (-1)e_{\underbrace{n+1}_{n-1} \cdots \underbrace{n}_{n-1}} \notin \mathcal{A}_{n-1}(G)$. Similarly, for $n = 2k + 1$ the differential on the basic element $e_{\underbrace{n+1}_{n+1} \cdots \underbrace{n}_{n-1}} \text{ contains the non-canceled summand } \partial^1(e_{\underbrace{n+1}_{n+1} \cdots \underbrace{n}_{n-1}}) = (-1)e_{\underbrace{n+1}_{n-1} \cdots \underbrace{n}_{n-1}} \notin \mathcal{A}_{n-1}(G)$. Hence, the image of the differential on every linear combination of the basic elements of $\mathcal{A}_n(G)$ doesn't belong to $\mathcal{A}_{n-1}(G)$ for $n \geq 2$ and $\Pi_n(G) = 0$ in these cases. The differential $\partial: \Pi_0(G) \to \Pi_{-1}(G) = 0$ is trivial and the differential $\partial: \Pi_1(G) \to \Pi_0(G)$ is given on the basic elements by equalities $\partial(e_{01}) = e_1 - e_0$, $\partial(e_{10}) = e_0 - e_1$. Hence

 $$ \mathcal{H}_{n}(G)=\begin{cases}\mathbb{Z}&for\ n=0,1,\\0&otherwise.\end{cases} $$ 

Thus, the groups  $ H_{n}(G) $ and  $ \mathcal{H}_{n}(G) $ are not isomorphic in general case.

Fix a ring of coefficients $R$. Consider a digraph map $f: G \to H$. Recall that for any arrow $(v \to w) \in E_G$ we have $f(v) = f(w) \in V_H$ or $(f(v) \to f(w)) \in E_H$. For $n \geq 0$, define a homomorphism of modules

 $$ f_{\sharp}\colon\Lambda_{n}(V_{G})\to\Lambda_{n}(V_{H}) $$ 

setting on basic elementary paths

 $$ f_{\sharp}\left(e_{i_{0}\ldots i_{n}}\right)=\begin{cases}e_{f(i_{0})\ldots f(i_{n})},&if e_{f(i_{0})\ldots f(i_{n})}is regular,\\0,&otherwise.\end{cases} $$ 

We set also  $ f_{\sharp} = 0 $ for  $ n = -1 $. We note that the restriction of  $ f_{\sharp} $ defines a homomorphism  $ \mathcal{A}_n(G) \to \mathcal{A}_n(H) $ which we continue to denote  $ f_{\sharp} $.

Lemma 3.3 Let  $ f: G \to H $ be a digraph map and digraph  $ H $ is asymmetric. Then for every  $ n \geq 0 $, the following diagram is commutative

 $$ \begin{aligned}&\mathcal{A}_{n}\left(G\right)&\xrightarrow{f_{\sharp}}&\mathcal{A}_{n}\left(H\right)\\&\partial\downarrow&&\downarrow\partial\\ \end{aligned} $$ 

 $$ \begin{array}{r l}{\Lambda_{n-1}\left(V_{G}\right)}&{{}\stackrel{f_{\sharp}}{\rightarrow}\quad\Lambda_{n-1}\left(V_{H}\right).}\end{array} $$ 

Proof. For $n=0$ it is nothing to prove since both maps $\partial$ are trivial. Let $n\geq1$ and $e_{i_0\ldots i_n}\in\mathcal{A}_n(G)$. We consider the following cases:

(i) the path  $ e_{f(i_{0})\ldots f(i_{n})} $ is not allowed,

(ii) the path  $ e_{f(i_0)\ldots f(i_n)} $ is allowed.

Consider the case (i). Let the path  $ e_{f(i_0)\ldots f(i_n)} $ is not allowed. Then there is at least one pair of consequent vertices  $ i_k, i_{k+1} $ in the path  $ e_{i_0\ldots i_n} $ such that  $ f(i_k) = f(i_{k+1}) \in V_H $. Thus, the path  $ e_{f(i_0)\ldots f(i_n)} $ is not regular and, by (3.4),

 $$ \partial f_{\sharp}(e_{i_{0}\ldots i_{n}})=\partial(0)=0. $$ 

Furthermore, we have

 $$ \begin{aligned}f_{\sharp}\partial(e_{i_{0}...i_{n}})&=f_{\sharp}\left(\sum_{m=0}^{n}(-1)^{m}e_{i_{0}...\widehat{i_{m}}...i_{n}}\right)\\&=f_{\sharp}\left(\sum_{\substack{m=0\\ m\neq k,k+1}}^{n}(-1)^{m}e_{i_{0}...\widehat{i_{m}}...i_{n}}\right)\\&+(-1)^{k}e_{f(i_{0})...\widehat{f(i_{k})}...f(i_{n})}\\&+(-1)^{k+1}e_{f(i_{0})...\widehat{f(i_{k+1})}...f(i_{n})}.\\ \end{aligned} $$ 

Every elementary path in the sum of the second row in (3.7) has two consequent vertices  $ i_k $,  $ i_{k+1} $ such that  $ f(i_k) = f(i_{k+1}) \in V_H $. Hence, by the definition  $ f_{\sharp} $, the second row in (3.7) is zero. The paths of the two bottom rows in (3.7) differ only by sign, since  $ f(i_k) = f(i_{k+1}) $, and the sum of these two paths is zero. Hence  $ f_{\sharp}\partial(e_{i_0\ldots i_n}) = 0 $, and by (3.6) diagram (3.5) is commutative in the case (i).

Consider the case (ii). Only in this case we are forced to use the asymmetry of  $ H $. For an allowed path  $ e_{i_0...i_n} \in \mathcal{A}_n(G) $, there are no fragments in the form  $ iji(i \neq j) $ in  $ e_{f(i_0)...f(i_n)} $ since the digraph  $ H $ is asymmetric. Hence

 $$ \partial f_{\sharp}(e_{i_{0}\ldots i_{n}})=\partial(e_{f(i_{0})\ldots f(i_{n})})=\sum_{m=0}^{n}(-1)^{m}e_{f(i_{0})\ldots\widehat{f(i_{m})\ldots f(i_{n})}}, $$ 

where all elementary paths in (3.8) are regular. Now we prove that there are no fragments  $ ij_i (i \neq j) $ in the allowed path  $ e_{i_0...i_n} \in \mathcal{A}_n(G) $ in the considered case. If such a fragment exists then its image in the allowed path  $ e_{f(i_0)...f(i_n)} $ has the form  $ f(i)f(j)f(i)(f(i) \neq f(j)) $ or  $ f(i)f(i)f(i)(f(i) = f(j)) $. The first case is impossible since digraph  $ H $ is asymmetric and the second case is impossible since in the case (ii) the path  $ e_{f(i_0)...f(i_n)} $ is allowed. Hence,

 $$ f_{\sharp}\partial(e_{i_{0}\ldots i_{n}})=f_{\sharp}\left(\sum_{m=0}^{n}(-1)^{m}e_{i_{0}\ldots\widehat{i_{m}}\ldots i_{n}}\right), $$ 

where all elementary paths  $ e_{i_0\ldots i_m\ldots i_n} \in \Lambda_n(V_G) $ are regular. Moreover, the image  $ f_\sharp(e_{i_0\ldots i_m\ldots i_n}) \in \Lambda_n(V_H) $ of every such path is also regular since there

are no fragments in the form  $ iji(i \neq j) $ in  $ e_{f(i_0)\ldots f(i_n)} $ as was proved above. Thus we obtain

 $$ f_{\sharp}\partial(e_{i_{0}\ldots i_{n}})=f_{\sharp}\left(\sum_{m=0}^{n}(-1)^{m}e_{i_{0}\ldots\widehat{i_{m}}\ldots i_{n}}\right)=\sum_{m=0}^{n}(-1)^{m}e_{f(i_{0})\ldots\widehat{f(i_{m})\ldots f(i_{n})}}. $$ 

It follows now from (3.9) and (3.10) that diagram (3.5) is commutative in the case (ii). ■

Example 3.4 Consider the digraph  $ G = (0 \rightarrow 1 \rightarrow 2) $ and the digraph  $ H = (0 \rightleftharpoons 1) $. Define the map  $ f: G \rightarrow H $ by setting  $ f(0) = f(2) = 0 $,  $ f(1) = 1 $. Let  $ e_{012} \in \mathcal{A}_2(G) $. We compute homomorphisms in (3.5) using (2.1) and (3.4):

 $$ f_{\sharp}\partial(e_{012})=f_{\sharp}(e_{12}-e_{02}+e_{01})=f_{\sharp}(e_{12})-f_{\sharp}(e_{02})+f_{\sharp}(e_{01})=e_{10}+e_{01} $$ 

since  $  f_{\sharp}(e_{02}) = 0  $ by (3.4). Furthermore,

 $$ \partial f_{\sharp}(e_{012})=\partial(e_{010})=e_{10}-e_{00}+e_{01}. $$ 

Hence diagram  $ (3.5) $ is not commutative in general case.

Proposition 3.5 Let  $ f: G \to H $ be a map of asymmetric digraphs. Then the restriction of the map  $ f_\sharp: \mathcal{A}_n(G) \to \mathcal{A}_n(H) $ to  $ \Pi_n(G) $ satisfies the condition

 $$ f_{\sharp}\left(\Pi_{n}(G)\right)\subset\Pi_{n}(H). $$ 

Moreover, this map commutes with the differential $\partial$ and hence, defines a morphism of chain complexes $\Pi_*(G) \to \Pi_*(H)$.

Proof. Follows from Lemma 3.3 and [7, Lemma 2.3]. For  $ n \geq 0 $, consider a diagram

 $$ \begin{array}{ccc}\Pi_{n}(G)&\quad&\Pi_{n}(H)\\\tau_{G}\downarrow&&\downarrow\tau_{H}\\\mathcal{A}_{n}(G)&\xrightarrow{f_{\sharp}}&\mathcal{A}_{n}(H)\\\partial\downarrow&&\downarrow\partial\\\Lambda_{n-1}(V_{G})&\xrightarrow{f_{\sharp}}&\Lambda_{n-1}(V_{H})\\\nu_{G}\uparrow&&\uparrow\nu_{H}\\\mathcal{A}_{n-1}(G)&\xrightarrow{f_{\sharp}}&\mathcal{A}_{n-1}(H)\end{array} $$ 

where  $ \nu_G $,  $ \nu_H $,  $ \tau_G $, and  $ \tau_H $ are natural inclusions. The diagram (3.12) is commutative by Lemma 3.3 and by the definition of  $ f_\sharp $. Let  $ w \in \Pi_n(G) $. To prove the relation (3.11) it is necessary to check that in (3.12)

 $$ \partial\left[f_{\sharp}\tau_{G}(w)\right]\in\operatorname{I m}\nu_{H}. $$ 

Since  $ w \in \Pi_n(G) $ we have

 $$ \partial\left(\tau_{G}(w)\right)=\nu_{G}(v)where v\in\mathcal{A}_{n-1}(G). $$ 

Furthermore, using relation  $ (3.13) $ and commutativity of diagram  $ (3.12) $ we obtain

 $$ \partial f_{\sharp}[\tau_{G}(w)]=f_{\sharp}\partial[\tau_{G}(w)]=f_{\sharp}\nu_{G}(v)=\nu_{H}f_{\sharp}(v) $$ 

and relation (3.11) is proved. Now consideration of commutative upper square of (3.12) finishes the proof. ■

Corollary 3.6 The primitive path homology is functorial on the subcategory AD of the category D.

Theorem 3.7 Let G be an asymmetric digraph. Then the chain complexes  $ \Pi_{*}(G) $ and  $ \Omega_{*}(G) $ are naturally isomorphic.

Proof. For  $ n \geq 0 $, the basis of the module  $ \mathcal{A}_n(G) $ is given by the allowed elementary paths  $ e_{i_0\ldots i_n} $ in  $ G $. Consider the following commutative diagram

 $$ \begin{array}{ccc}\mathcal{A}_{n}(G)&\stackrel{=}{\longrightarrow}&\mathcal{A}_{n}(G)\\\downarrow&\downarrow\eta_{n}\\\Lambda_{n}(V_{G})&\stackrel{p_{n}}{\longrightarrow}&\mathcal{R}_{n}(V_{G})\\\partial\downarrow&\downarrow\partial\\\Lambda_{n-1}(V_{G})&\stackrel{p_{n-1}}{\longrightarrow}&\mathcal{R}_{n-1}(V_{G})\\\uparrow&\uparrow\eta_{n-1}\\\mathcal{A}_{n-1}(G)&\stackrel{=}{\longrightarrow}&\mathcal{A}_{n-1}(G)\\\end{array}=\Lambda_{n}(V_{G})/I_{n}(V_{G}) $$ 

in which horizontal homomorphisms $p_n, p_{n-1}$ are natural projections, the right differential is induced by the left differential, the upper and bottom left vertical maps are natural inclusions, and the map $\eta_n$ is given on basic elements $e_{i_0...i_n} \in \mathcal{A}_n(G)$ by $\eta_n(e_{i_0...i_n}) = [e_{i_0...i_n}]$ where $[e_{i_0...i_n}] \in \mathcal{R}_n(V_G)$ is the equivalence class defined in Section 2. We have $p_n(e_{i_0...i_n}) = [e_{i_0...i_n}]$ for $n \geq 0$ and $p_{-1} = 0$. The homomorphism $\eta_n$ is an inclusion since $\mathcal{A}_n(G) \cap$

 $ I_n(G) = 0 $. Thus we can naturally identify  $ \mathcal{A}_n(G) $ with the submodule of  $ \mathcal{R}_n(V_G) $ which is generated by classes  $ [e_{i_0\ldots i_n}] $ for elementary allowed paths  $ e_{i_0\ldots i_n} $. The inclusion  $ \eta_{n-1} $ has the similar properties as  $ \eta_n $.

For every elementary allowed path  $ e_{i_0} \in \mathcal{A}_0(G) $ we have  $ \partial(e_{i_0}) = 0 \in \mathcal{A}_{-1}(G) = 0 $ and  $ \partial([e_{i_0}]) = 0 \in \mathcal{R}_{-1}(V_G) = 0 $. Hence

 $$ \Pi_{0}(G)=\Omega_{0}(G)=\mathcal{A}_{0}(G) $$ 

and  $ p_{0} $ gives an isomorphism  $ p_{0}: \Pi_{0}(G) \to \Omega_{0}(G) $.

For every elementary allowed path  $ e_{i_0i_1} \in \mathcal{A}_1(G) $ we have  $ \partial(e_{i_0i_1}) = e_{i_1} - e_{i_0} \in \mathcal{A}_0(G) $ and  $ \partial([e_{i_0i_1}]) = [e_{i_1}] - [e_{i_0}] \in \eta_0(\mathcal{A}_0(G)) $. Hence

 $$ \Pi_{1}(G)=\Omega_{1}(G)=\mathcal{A}_{1}(G) $$ 

and  $ p_{1} $ gives an isomorphism  $ p_{1}\colon\Pi_{1}(G)\to\Omega_{1}(G) $.

For  $ n \geq 2 $, consider an elementary allowed path  $ e_{i_0...i_n} \in \mathcal{A}_n(G) $. The sequence of vertices  $ i_0 \ldots i_n $ doesn't contain fragments in the form  $ iji (i,j \in V_G) $ since there are no symmetric arrows in  $ G $. Hence, each summand in (3.17) below

 $$ \partial(e_{i_{0}\ldots i_{n}})=\sum_{m=0}^{n}(-1)^{m}e_{i_{0}\ldots\widehat{i_{m}\ldots i_{n}}} $$ 

doesn't belong to  $ I_{n-1}(V_{G}) $. Hence

 $$ p_{n-1}\partial(e_{i_{0}\ldots i_{n}})=\sum_{m=0}^{n}(-1)^{m}[e_{i_{0}\ldots i_{m}\ldots i_{n}}] $$ 

Consider an element

 $$ w=\sum r^{\alpha}e_{\alpha}\in\mathcal{A}_{n}(G)\subset\Lambda_{n}(V_{G}),\ \partial(w)=\sum r^{\beta}e_{\beta}\in\Lambda_{n-1}(V_{G}) $$ 

where  $ r^\alpha, r^\beta \in R $,  $ e_\alpha $ are elementary allowed  $ n $-paths, and  $ e_\beta $ are elementary  $ (n-1) $-paths obtained by the application of  $ \partial $. It follows from diagram (3.14), (3.17), and (3.18) that the diagram

 $$ \begin{array}{ccc}\sum r^{\alpha}e_{\alpha}&\xrightarrow{p_{n}}&\sum r^{\alpha}[e_{\alpha}]\\\partial\downarrow&&\downarrow\partial\\\sum r^{\beta}e_{\beta}&\xrightarrow{p_{n-1}}&\sum r^{\beta}[e_{\beta}]\end{array} $$ 

is commutative. Similarly to the inclusion  $ \eta_n $, the inclusion  $ \eta_{n-1} $ is given on basic elements  $ e_{i_0...i_{n-1}} \in \mathcal{A}_{n-1}(G) $ by  $ \eta_{n-1}(e_{i_0...i_{n-1}}) = [e_{i_0...i_{n-1}}] $. Hence the commutativity of the bottom square in (3.14) and (3.20) imply that

 $$ \sum r^{\beta}e_{\beta}\in\mathcal{A}_{n-1}(G) $$ 

if and only if

 $$ \sum r^{\beta}[e_{\beta}]\in\eta_{n-1}\left(\mathcal{A}_{n-1}(G)\right) $$ 

Hence, for  $ n \geq -1 $, the restriction of the homomorphism  $ p_n $ to the submodule  $ \Pi_n(G) \subset \Lambda_n(V_G) $ gives the natural isomorphism of modules  $ \Pi_n(G) \to \Omega_n(G) $ which agrees with the differential as follows from diagram (3.14).

Corollary 3.8 Let $G$ be an asymmetric digraph. Then we have a natural isomorphism $\mathcal{H}_*(G) \cong H_*(G)$ between primitive path homology groups and path homology groups.

Proposition 3.9 Let $G$ be a digraph and $w \in \mathcal{A}_n(G)$ ($n \geq 0$). Then $w \in \Pi_n(G)$ if and only if

 $$ \partial^{m}(w)\in\mathcal{A}_{n-1}(G)\quad{f o r\quad}0\leq m\leq n $$ 

where  $ \partial^{m} $ is defined in (2.2).

Proof. Let  $ w \in \mathcal{A}_n(G) $. For  $ n = 0 $ it is nothing to prove. Consider the case  $ n \geq 1 $. By (2.1) and (2.2), we have

 $$ \partial(w)=\partial^{0}(w)+(-1)\partial^{1}(w)+\cdots+(-1)^{n}\partial^{n}(w). $$ 

If the condition 3.21 is satisfied then every summand in the sum (3.22) lays in  $ \mathcal{A}_{n-1}(G) $ and, hence,  $ \partial(w) \in \mathcal{A}_{n-1}(G) $. By (3.1) this means that  $ w \in \Pi_n(G) $.

Now we prove the inverse statement. Let  $ w \in \Pi_n(G) $ that is  $ w \in \mathcal{A}_n(G) $ and the sum in (3.22) lays in  $ \mathcal{A}_{n-1}(G) $. It is necessary to prove that each element  $ \partial^m(w) $ in (3.22) lays in  $ \mathcal{A}_{n-1}(G) $. We can write down  $ w $ in the form

 $$ w=\sum_{j=1}^{k}r^{j}p_{j}=\sum_{j=1}^{k}r^{j}e_{i_{0}^{j}\cdots i_{m-1}^{j}i_{m}^{j}i_{m+1}^{j}\cdots i_{n}^{j}} $$ 

where  $ p_j = e_{i_0^{j} \ldots i_{m-1}^{j} i_m^{j} i_{m+1}^{j} \ldots i_n^{j}} $ are pairwise distinct allowed elementary paths in  $ G $ and  $ r^j \in R $. By (2.1), for  $ m = 0 $ and  $ m = n $ we have

 $$ \partial^{0}(w)=\sum_{j=1}^{k}r^{j}e_{\widehat{i_{0}^{j}i_{1}^{j}\ldots i_{n}^{j}}}=\sum_{j=1}^{k}r^{j}e_{i_{1}^{j}\ldots i_{n}^{j}}\in\mathcal{A}_{n-1}(G) $$ 

and

 $$ \partial^{n}(w)=\sum_{j=1}^{k}r^{j}e_{i_{0}^{j}\cdots i_{n-1}^{j}}\widehat{i_{n}^{j}}=\sum_{j=1}^{k}r^{j}e_{i_{0}^{j}\cdots i_{n-1}^{j}}\in\mathcal{A}_{n-1}(G) $$ 

since each path  $ e_{i_{0},i_{n}}^{j} $ is an allowed path in G.

Now consider $m$ such that $1 \leq m \leq n - 1$. Let $P_m = \{(i, i')\}$ be a set of pairs of vertices $i, i' \in V_G$ such that there exists an elementary path $p_j (1 \leq j \leq k)$ in (3.23) which has the form

 $$ p_{j}=e_{i_{0}^{j}\cdots i_{m-1}^{j}i_{m}^{j}i_{m+1}^{j}\cdots i_{n}^{j}}\mathrm{w h e r e}(i_{m-1}^{j},i_{m+1}^{j})=(i,i^{\prime}). $$ 

Then

 $$ \partial^{m}(w)=\sum_{(i_{m-1}^{j},i_{m+1}^{j})\in P_{m}}r^{j}e_{i_{0}^{j}\cdots i_{m-1}^{j}i_{m+1}^{j}\cdots i_{n}^{j}}\in\Lambda_{n-1}(V_{G}). $$ 

We note the following. If  $ (i_{m-1}^j \to i_{m+1}^j) \in E_G $ then path  $ e_{i_0^j \cdots i_{m-1}^j i_{m+1}^j \cdots i_n^j} $ in (3.26) is allowed and lays in  $ \mathcal{A}_{n-1}(G) $. If  $ (i_{m-1} \to i_{m+1}) \notin E_G $ then  $ e_{i_0^j \cdots i_{m-1}^j i_{m+1}^j \cdots i_n^j} \notin \mathcal{A}_{n-1}(G) $. Let

 $$ T_{m}=\left\{\left(i,i^{\prime}\right)\in P_{m}\mid\left(i\rightarrow i^{\prime}\right)\in E_{G}\right\} $$ 

and

 $$ S_{m}=\{(i,i^{\prime})\in P_{m}\mid(i\to i^{\prime})\notin E_{G}]\}. $$ 

Thus we can write down  $ P_{m} $ in the form

 $$ P_{m}=T_{m}\cup S_{m}\mathrm{~w h e r e~}T_{m}\cap S_{m}=\varnothing. $$ 

Hence, we can write down (3.26) in the form

 $$ \partial^{m}(w)=\sum_{(i_{m-1}^{j},i_{m+1}^{j})\in T_{m}}r^{j}\partial^{m}(p_{j})+\sum_{(i_{m-1}^{j},i_{m+1}^{j})\in S_{m}}r^{j}\partial^{m}(p_{j}). $$ 

where the first summand lays in  $ \mathcal{A}_{n-1}(G) $.

Since  $ \partial(w) \in \mathcal{A}_{n-1}(G) $ we obtain using (3.24), (3.25), and (3.28)

 $$ \sum_{1\leq m\leq n-1}\left(\sum_{(i_{m-1}^{j},i_{m+1}^{j})\in T_{m}}r^{j}\partial^{m}(p_{j})+\sum_{(i_{m-1}^{j},i_{m+1}^{j})\in S_{m}}r^{j}\partial^{m}(p_{j})\right)\in\mathcal{A}_{n-1}(G). $$ 

Since all summands by  $ T_{m} $ lays in  $ \mathcal{A}_{n-1}(G) $ we conclude that

 $$ \sum_{1\leq m\leq n-1}\left(\sum_{(i_{m-1}^{j},i_{m+1}^{j})\in S_{m}}r^{j}\partial^{m}(p_{j})\right)\in\mathcal{A}_{n-1}(G). $$ 

Denote by

 $$ \mathcal{S}_{n-1}^{m}(G)=\langle\partial^{m}(p_{j})\mid(i_{m-1}^{j},i_{m+1}^{j})\in S_{m}\rangle\subset\Lambda_{n-1}(V_{G}) $$ 

a submodule generated by the elements  $ \partial^m(p_j) $ such that  $ (i_{m-1}^j, i_{m+1}^j) \in S_m $. We state now, that

 $$ \mathcal{S}_{n-1}^{m}(G)\cap\mathcal{S}_{n-1}^{l}(G)=0\in\Lambda_{n-1}(V_{G})\mathrm{f o r}m\neq l. $$ 

For every basic element

 $$ \partial^{m}(p^{j})=e_{i_{0}^{j}\cdots i_{m-1}^{j}i_{m+1}^{j}\cdots i_{n}^{j}}\in\mathcal{S}_{n-1}^{m}(G)\left(1\leq m\leq n-1\right), $$ 

there is an arrow  $ i_{t}^{j} \rightarrow i_{t+1}^{j} $ for all t except t = m - 1. Similarly, for every basic element

 $$ \partial^{l}(p^{j})=e_{i_{0}^{j}\cdots i_{l-1}^{j}i_{l+1}^{j}\cdots i_{n}^{j}}\in\mathcal{S}_{n-1}^{l}(G)\left(1\leq l\leq n-1\right), $$ 

there is an arrow  $ i_t^j \to i_{t+1}^j $ for all  $ t $ except  $ t = l - 1 $. Hence, the condition (3.31) is satisfied. Recall that by the definition of the set  $ \mathcal{S}_{n-1}^m $, for every element  $ \partial^m(p^j) = e_{i_0^j \ldots i_n^j} \in \mathcal{S}_{n-1}(G) \subset \Lambda_{n-1}(V_G) $ we have

 $$ \partial^{m}(p^{j})=e_{i_{0}^{j}\dots i_{n}^{j}}\notin\mathcal{A}_{n-1}(G). $$ 

Hence, by (3.29), (3.31), and (3.32) we obtain that for  $ 1 \leq m \leq n - 1 $

 $$ \sum_{(i_{m-1}^{j},i_{m+1}^{j})\in S_{m}}\partial^{m}(p_{j})=0\in\mathcal{A}_{n-1}(G). $$ 

By the consideration above, the first summand in (3.28) lays in  $ \mathcal{A}_{n-1}(G) $ and by (3.33) the second summand in (3.28) is zero. Hence  $ \partial_n^m(w) \in \mathcal{A}_{n-1}(G) $ and the proposition is proved.

Definition 3.10 Let  $  G = (V, E)  $ be a digraph. We denote by  $  \overline{G} = (\overline{V}, \overline{E})  $ a digraph with

 $$ \overline{V}=V\ \mathrm{and}\ \overline{E}=\{v\rightarrow w\mid v,w\in V,(w\rightarrow v)\in E\}. $$ 

We call the digraph  $ \overline{G} $ by inverse directed digraph of the digraph G.

Thus, the digraph  $ \overline{G} $ is obtained from G by changing directions of all arrows. It easy to see that the operation  $ G \rightarrow \overline{G} $ is an involution on the set of digraphs.

Theorem 3.11 For every digraph  $  G = (V, E)  $, we have an isomorphism of chain complexes

 $$ \Pi_{*}(G)\to\Pi_{*}(\overline{G}) $$ 

which induces an isomorphism of primitive path homology groups

 $$ \mathcal{H}_{n}(G)\to\mathcal{H}_{n}(\overline{{G}})\quad{f o r\quad}n\geq0. $$ 

Proof. For the convenience of readers we give the proof which is similar to [10, Theorem 4.14]. For  $ n \geq 0 $, define an isomorphism of  $ R $-modules

 $$ \tau\colon\Lambda_{n}(V)\to\Lambda_{n}(V)\textup{by}\tau(e_{i_{0}\ldots i_{n}})=\begin{cases}e_{i_{n}\ldots i_{0}}&\textup{for}n=0,3\bmod4,\\e_{i_{n}\ldots i_{0}}&\textup{for}n=1,2\bmod4.\end{cases} $$ 

For $n = -1$, we set $\tau = 0: 0 = \Lambda_{-1}(V) \to \Lambda_{-1}(V) = 0$. The isomorphism $\tau$ commutes with the differential $\partial$ in (2.1) and, hence, defines an isomorphism of chain complexes $\tau_*: \Lambda_*(V) \to \Lambda_*(V)$. For $n \geq -1$, let $\mathcal{A}_n(G) \subset \Lambda_n(V)$ be a submodule generated by allowed elementary paths. By Definition 3.10 the restriction of the isomorphism $\tau$ defines an isomorphism $\tau: \mathcal{A}_n(G) \to \mathcal{A}_n(\overline{G})$. Let $w \in \Pi_n(G)$, that is $w \in \mathcal{A}_n(G)$ and $\partial w \in \mathcal{A}_{n-1}(G)$. Then $\tau(w) \in \mathcal{A}_n(\overline{G})$, $\partial\tau(w) = \tau\partial(w) \in \mathcal{A}_{n-1}(\overline{G})$ and, hence, $\tau(w) \in \Pi_n(\overline{G})$. The inverse conclusion is similar since $\tau_*:$ and the restriction of $\tau$ are isomorphisms.

## 4 Cluster digraphs

In this Section we define a cluster subgraph, a tail subgraph, and a head subgraph of a digraph G and study primitive path homology of these digraphs.

We describe relations between these homology and their relation to primitive path homology of the ambient digraph. We fix an unitary and commutative ring R of coefficients. All modules are R-modules and we don’t mention R in notations.

Definition 4.1 For  $ a, b \in V_G $, define  $ (a, b) $-cluster digraph  $ G^{[a,b]} = (V^{[a,b]}, E^{[a,b]}) $ of a digraph  $ G $ as a minimal subgraph which contains all vertices and all arrows of every  $ (a, b) $-cluster path  $ w^{[a,b]} \in \mathcal{A}_n(G) $ for  $ n = 0, 1, \ldots $.

Suppose a cluster digraph  $ G^{[a,b]} $ exists. Then  $ \mathcal{A}_n(G^{[a,b]}) \subset \mathcal{A}_n(G) $ for  $ n \geq -1 $ by Definition 4.1. For every vertex  $ a \in V_G $ the cluster digraph  $ G^{[a,a]} $ exists and contains the vertex  $ a $.

We note also that a cluster digraph  $ G^{[a,b]} $ may be not defined for some pairs  $ (a,b) $ of vertices. For example, for the digraph  $ G = (0 \rightarrow 1) $ the cluster digraph  $ G^{[1,0]} $ is not defined.

Proposition 4.2 Let  $ G^{[a,b]} $ be a cluster digraph in G. Then it is an induced subgraph.

Proof. Let $k$ be a vertex of an allowed path $e_{a\ldots sk\ldots b} \in \mathcal{A}_n\left(G^{[a,b]}\right)$ and $l \neq k$ be a vertex of an allowed path $e_{a\ldots lm\ldots b} \in \mathcal{A}_n\left(G^{[a,b]}\right)$ such that $(k \to l) \in E_G$. Then the allowed path $e_{a\ldots sklm\ldots b}$ from $a$ to $b$ contains the arrow $k \to l$ and, hence, $(k \to l) \in E^{[a,b]}$.

Let $G$ be a digraph and $w \in \mathcal{A}_n(G)$ be an allowed path. For $n \geq 0$, we can write $w$ in the form

 $$ w=\sum_{a\in V}w^{[a,\cdot]}\text{where}w^{[a,\cdot]}=\sum_{a i_{1}\cdots i_{n}}r^{a i_{1}\cdots i_{n}}e_{a i_{1}\cdots i_{n}},\quad r^{a i_{1}\cdots i_{n}}\in R $$ 

and  $ e_{ai_{1}\ldots i_{n}} $ are elementary allowed paths and  $ a = t\left(e_{ai_{1}\ldots i_{n-1}i_{n}}\right) $. We call the path  $ w^{[a,\cdot]} $ by a-tail path. Similarly, for  $ n \geq 0 $, we can write  $ w $ in the form

 $$ w=\sum_{b\in V}w^{[\cdot,b]},\quad w^{[\cdot,b]}=\sum_{i_{0}\cdots i_{n-1}b}r^{i_{0}\cdots i_{n-1}b}e_{i_{0}\cdots i_{n-1}b},\quad r^{i_{0}\cdots i_{n-1}b}\in R $$ 

and  $ e_{i_0\ldots i_{n-1}b} $ are elementary allowed paths and  $ b = h\left(e_{i_0i_1\ldots i_{n-1}b}\right) $. We call the path  $ w^{[\cdot,b]} $ by b-head path.

Theorem 4.3 Let G be a digraph and Πn(G) (n ≥ 0) be a module in (3.1).

(i) A path  $ w \in \mathcal{A}_n(G) $ lays in  $ \Pi_n(G) $ if and only if  $ w^{[a,\cdot]} \in \Pi_n(\dot{G}) $ for every tail fixed path  $ w^{[a,\cdot]} $ in  $ (4.1) $.

(ii)  $ A \text{ path } w \in \mathcal{A}_n(G) \text{ lays in } \Pi_n(G) \text{ if and only if } w^{[\cdot,b]} \in \Pi_n(G) \text{ for every head fixed path } w^{[\cdot,b]} \text{ in } (4.2). $

(iii)  $ A \text{ path } w \in \mathcal{A}_n(G) \text{ lays in } \Pi_n(G) \text{ if and only if } w^{[a,b]} \in \Pi_n(G) \text{ for every cluster path } w^{[a,b]} \text{ in } (2.7). $

Proof. For $n=0$ it is nothing to prove. For $n\geq1$, consider the case (i). If $w^{[a\cdot]}\in\Pi_n(G)$ for all tail paths in (4.1) then $\partial(w^{[a\cdot]})\in\mathcal{A}_{n-1}(G)$ and

 $$ \partial(w)=\partial\left(\sum_{a\in V}w^{[a,\cdot]}\right)=\sum_{a\in V}\partial\left(w^{[a,\cdot]}\right)\in\mathcal{A}_{n-1}. $$ 

Hence w ∈ ∏n (G).

Now we prove the inverse statement. Let  $ w \in \Pi_n(G) $ and, hence,  $ \partial w \in \mathcal{A}_{n-1}(G) $. The paths  $ w^{[a,\cdot]} $ in (4.1) are allowed and it is necessary to prove that  $ \partial\left(w^{[a,\cdot]}\right) \in \mathcal{A}_{n-1}(G) $ for every  $ w^{[a,\cdot]} $. Every path  $ w^{[a,\cdot]} $ in the decomposition (4.1) is a linear combination of allowed paths with the tail vertex  $ a $:

 $$ w^{[a.\cdot]}=\sum_{k}r^{k}e_{a i_{1}^{k}\ldots i_{n}^{k}},\quad r^{k}\in R. $$ 

We have

 $$ \partial\left(w^{[a,\cdot]}\right)=\sum_{k}r^{k}e_{i_{1}^{k}i_{2}^{k}\ldots i_{n}^{k}}+\sum_{k}\left(\sum_{j=1}^{n}r^{k}e_{a i_{1}^{k}\ldots\widehat{i_{j}^{k}}\ldots i_{n}^{k}}\right). $$ 

For every  $ a \in V $, the first sum in (4.3) is an allowed path. The second sum can contains allowed and non-allowed elementary paths. An non-allowed elementary path in the second sum can not be cancel with a similar non-allowed elementary fitting into  $ w^{[c,\cdot]} $ with  $ c \neq a $. Since there are no non-allowed paths in  $ \partial w $ we conclude that they have to cancel in the second sum in (3.4). Hence  $ \partial\left(w^{[a,\cdot]}\right) \in \mathcal{A}_{n-1}(G) $ and  $ w^{[a,\cdot]} \in \Pi_n(G) $. The proof in the cases (ii) and (iii) is similar. ■

Corollary 4.4 (i) Let  $ G = (V, E) $ be a digraph and  $ n \geq 0 $. The module  $ \Pi_n(G) $ is a direct sum of submodules

 $$ \Pi_{n}(G)=\bigoplus_{a\in V}\Pi_{n}^{[a,\cdot]}(G) $$ 

where  $ \Pi_n^{[a,\cdot]}(G) = \langle w^{[a,\cdot]} \in \Pi_n(G) \rangle $ is generated by a-tail paths in  $ \Pi_n(G) $. If there are no a-tail paths in dimension  $ n $ we set  $ \Pi_n^{[a,\cdot]}(G) = 0 $.

(ii) The module  $ \Pi_{n}(G) $ is a direct sum of submodules

 $$ \Pi_{n}(G)=\bigoplus_{b\in V}\Pi_{n}^{[\cdot,b]}(G) $$ 

where  $ \Pi_n^{[\cdot,b]}(G) = \langle w^{[\cdot,b]} \in \Pi_n(G) \rangle $ is generated by b-head paths in  $ \Pi_n(G) $. If there are no b-head paths in dimension  $ n $ we set  $ \Pi_n^{[\cdot,b]}(G) = 0 $.

(iii) The module  $ \Pi_{n}(G) $ is a direct sum of submodules

 $$ \Pi_{n}(G)=\bigoplus_{a,b\in V}\Pi_{n}^{[a,b]}(G) $$ 

where  $ \Pi_n^{[a,b]}(G) = \big\langle w^{[a,b]} \in \Pi_n(G) \big\rangle $ is generated by  $ (a,b) $-cluster paths in  $ \Pi_n(G) $. If there are no  $ (a,b) $-cluster paths in dimension  $ n $ we set  $ \Pi_n^{[a,b]}(G) = 0 $.

Definition 4.5 (i) For  $ a \in V $, we define an a-tail digraph  $ G^{[a,\cdot]} = (V^{[a,\cdot]}, E^{[a,\cdot]}) $ of a digraph  $ G $ as a minimal subgraph which contains all vertices and all arrows of every a-tail path  $ w^{[a,\cdot]} \in \mathcal{A}_n(G) $ for  $ n = 0, 1, \ldots $.

(ii) For  $ b \in V $, we define an b-head digraph  $ G^{[\cdot,b]} = (V^{[\cdot,b]}, E^{[\cdot,b]}) $ of a digraph  $ G $ as a minimal subgraph which contains all vertices and all arrows of every b-head path  $ w^{[\cdot,b]} \in \mathcal{A}_n(G) $ for  $ n = 0, 1, \ldots $.

Proposition 4.6 Every a-tail and every b-head digraph of a digraph G is an induced subgraph.

Proof. Similar to the proof of Proposition 4.2.

Proposition 4.7 Let  $  G = (V, E)  $ be a digraph and  $  n \geq 0  $. For  $  a, b \in V  $ we have the following equalities of modules

 $$ \begin{align*}\Pi_{n}^{[a,\cdot]}(G)&=\Pi_{n}^{[a,\cdot]}\left(G^{[a,\cdot]}\right),\quad\Pi_{n}^{[\cdot,b]}(G)=\Pi_{n}^{[\cdot,b]}\left(G^{[\cdot,b]}\right),\\\Pi_{n}^{[a,b]}(G)&=\Pi_{n}^{[a,b]}\left(G^{[a,b]}\right),\text{and}\Pi_{n}^{[a,b]}(G)=\Pi_{n}^{[a,\cdot]}(G)\cap\Pi_{n}^{[\cdot,b]}(G).\end{align*} $$ 

Proof. The equalities in (4.4) follow from Definitions 4.1 and 4.5, Theorem 4.3 and Corollary 4.4. ■

Remark 4.8 We note that the image of the restriction

 $$ \partial\colon\Pi_{n}^{[a,b]}(G)\to\Pi_{n-1}(G) $$ 

of the differential $\partial: \Pi_n(G) \to \Pi_{n-1}(G)$ doesn't belong to the submodule $\Pi_{n-1}^{[a,b]}(G) \subset \Pi_n(G)$ and, hence, the modules $\Pi_n^{[a,b]}(G)$ with the differential $\partial$ doesn't form a chain complex. The similar statement is true for the modules $\Pi_n^{[a,:]}(G)$ and $\Pi_n^{[\cdot,b]}(G)$ in (4.4).

## 5 Primitive homology of cluster digraphs

In this Section, for a digraph G, we construct a primitive path homology theory for a set of  $ (a,b) $-cluster paths, that is the set of paths which have the fixed tail vertex a and the fixed head vertex b. The construction of the chain complex is similar to the construction of the chain complex in the primitive path homology theory in Section 3. We note that the homology theory of cyclic paths  $ e_{i_{0}\ldots i_{n-1}i_{n}} $ with  $ i_{0}=i_{n} $ was constructed and studied in [16] and [15]. We describe relations between introduced homology and the primitive path homology and present several examples.

Fix a unitary and commutative ring R of coefficients. The next definition is a natural generalization of Definition 2.2 in which a cluster path is defined for a digraph G.

Definition 5.1 Let $V$ be a finite set of vertices, $a, b \in V$ be two vertices, and $n \geq 0$. A path in $\Lambda_n(G)$ is an $(a, b)$-cluster path if it is a linear combination of paths with the tail vertex $a$ and with the head vertex $b$. The cluster path is denoted $w^{[a,b]}$. The elementary paths fitting into $w^{[a,b]}$ are called elementary $(a, b)$-cluster paths.

Let  $ n \geq 1 $. Denote by  $ \Lambda_n^{[a,b]} = \Lambda_n^{[a,b]}(V) \subset \Lambda_n(V) $ a free submodule generated by elementary  $ (a,b) $-cluster path. The module  $ \Lambda_n^{[a,b]} $ is called  $ (a,b) $-cluster module and the elements of  $ \Lambda_n^{[a,b]} $ are called  $ (a,b) $-cluster paths in dimension  $ n $. We set also  $ \Lambda_0^{[a,b]} = 0 $.

For  $ n \geq 1 $, define a differential

 $$ d\colon\Lambda_{n}^{[a,b]}\to\Lambda_{n-1}^{[a,b]} $$ 

by setting on basic elements

 $$ d(e_{a i_{0}\ldots i_{n-2}b})=\begin{cases}{\displaystyle\sum_{m=0}^{n-2}(-1)^{m}e_{a i_{0}\ldots\widehat{i_{m}}\ldots i_{n-2}b}}&{\mathrm{f o r~}n\geq2,}\\ {0}&{\mathrm{f o r~}n=1.}\\ \end{cases} $$ 

For  $ n \geq 2 $, we can write down the differential d in the form

 $$ d(e_{a i_{0}\ldots i_{n-2}b})=\sum_{m=0}^{n-2}(-1)^{m}d^{m}(e_{a i_{0}\ldots i_{n-2}b}). $$ 

where  $ d^m: \Lambda_n^{[a,b]} \to \Lambda_{n-1}^{[a,b]} $ is a homomorphism given on the basic elements by

 $$ d^{m}(e_{a i_{0}...i_{n-2}b})=e_{a i_{0}...\widehat{i_{m}}...i_{n-2}b}. $$ 

Consider the augmented chain complex  $ \Lambda_*(V) $ defined in Section 2. We have  $ \widetilde{\Lambda}_n(V) = \Lambda_n(V) $ for  $ n \geq 0 $,  $ \widetilde{\Lambda}_{-1}(V) = R $, and  $ \widetilde{\Lambda}_{-2}(V) = 0 $.

For  $ n \geq 0 $, define an isomorphism of modules

 $$ \pi^{[a,b]}\colon\Lambda_{n}^{[a,b]}(V)\to\widetilde{\Lambda}_{n-2}(V), $$ 

by setting:  $ \pi^{[a,b]}(e_{ai_{0}\ldots i_{n-2}b})=e_{i_{0}\ldots i_{n-2}} $ for  $ n\geq2 $,  $ \pi^{[a,b]}(e_{ab})=1\in R $ for  $ n=1 $, and  $ \pi^{[a,b]}=0 $ for  $ n=0 $.

Proposition 5.2 For  $ n \geq 0 $, the following diagram

 $$ \begin{array}{ccc}\Lambda_{n}^{[a,b]}(V)&\xrightarrow{\pi^{[a,b]}}&\widetilde{\Lambda}_{n-2}(V)\\&&\\d&\downarrow&&\downarrow\partial\\\end{array} $$ 

is commutative.

Proof. Follows from the definition of the isomorphism  $ \pi^{[a,b]} $ and definitions of differential  $ \partial $ in (2.1) and differential  $ d $ in (5.2).

Corollary 5.3 For  $ n \geq 0 $, the modules  $ \Lambda_n^{[a,b]} $ with the differential d form a chain complex.

Proof. In diagram (5.4) the modules  $ \tilde{\Lambda}_n(V)(n \geq -2) $ with the differential  $ \partial $ form a chain complex. The horizontal maps are isomorphisms. Now the statement follows from commutativity of (5.4).

Definition 5.4 Consider a digraph  $ G = (V, E) $ and two vertices  $ a, b \in V $. For  $ n \geq 0 $, let  $ \mathcal{A}_n^{[a,b]} = \mathcal{A}_n^{[a,b]} $ ( $ G $) be a module generated by elementary  $ (a, b) $-cluster paths in  $ G $. If there are no such paths we set  $ \mathcal{A}_n^{[a,b]} = 0 $. We call the module  $ \mathcal{A}_n^{[a,b]} $ by an allowed  $ (a, b) $-cluster module.

It follows from Definition 5.4 that for every digraph G we have

 $$ \begin{array}{c}{\mathcal{A}_{0}^{[a,b]}(G)=0\mathrm{~f o r~a l l~}a,b\in V,}\\ {\mathcal{A}_{1}^{[a,b]}(G)=\begin{cases}{\langle e_{a b}\rangle,}&{\mathrm{i f~}a\to b\in E,}\\ {0,}&{\mathrm{o t h e r w i s e.}}\\ \end{cases}}\\ \end{array} $$ 

For  $ n \geq 0 $, the module  $ \mathcal{A}_n^{[a,b]}(G) $ is a submodule of  $ \Lambda_n(V) $. For  $ n \geq 1 $, define a submodule

 $$ \Theta_{n}^{[a,b]}=\Theta_{n}^{[a,b]}(G)=\{w\in\mathcal{A}_{n}^{[a,b]}(G)\mid d(w)\in\mathcal{A}_{n-1}^{[a,b]}(G)\}, $$ 

where d:  $ \Lambda_{n}^{[a,b]}(V) \to \Lambda_{n-1}^{[a,b]}(V) $ is the differential in (5.2). We set  $ \Theta_{0}^{[a,b]} = 0 $.

Proposition 5.5 The modules  $ \Theta_n^{[a,b]}(G) $ with the restriction of the differential  $ d $ form a chain complex  $ \Theta_* $^{[a,b]} = \Theta_*\^{[a,b]}(G) $.

Proof. Similarly to the case of modules  $ \Pi_n(G) $ defined in (3.1), we obtain that  $ d(\Theta_n^{[a,b]}) \subset \Theta_{n-1}^{[a,b]} $ for  $ n \geq 1 $ and the result follows. ■

By (5.5) and (5.6, for any digraph  $ G = (V, E) $ we have

 $$ \Theta_{1}^{[a,b]}(G)=\begin{cases}\langle e_{a b}\rangle,&if a\rightarrow b\in E,\\ 0,&otherwise.\end{cases} $$ 

Definition 5.6 The homology groups of the chain complex  $ \Theta_{*}^{[a,b]}(G) $ are called primitive  $ (a,b) $-cluster homology groups of the digraph  $ G $ and are denoted by  $ \mathcal{H}_{n}^{[a,b]}(G) = \mathcal{H}_{n}^{[a,b]}(G, R) (n \geq 0) $.

Let  $ I = (0 \to 1) $ be the digraph. For  $ n \geq 0 $, we define  $ n\text{-}cube\ \text{digraph}\ I^n $ by setting  $ I^0 = \{0\} $ and

 $$ I^{n}=\underbrace{I\Box I\Box I\Box\ldots\Box I}_{n\mathrm{~t i m e s}}\mathrm{~f o r~}n\geq1. $$ 

Example 5.7 Let Z be the ring of coefficients.

(i) Consider a 2-cube digraph  $ I^{2} $ below

 $$ \begin{array}{ccc}{{{1}}}&{{{\rightarrow}}}&{{{3}}} \\{{{\uparrow}}}&{{{\uparrow}}} \\{{{0}}}&{{{\rightarrow}}}&{{{2.}}}\end{array} $$ 

We have  $ \mathcal{A}_0^{[0,3]} = \mathcal{A}_1^{[0,3]} = 0 $,  $ \mathcal{A}_2^{[0,3]} = \langle e_{013}, e_{023} \rangle \cong \mathbb{Z}^2 $,  $ \mathcal{A}_n^{[0,3]} = 0 $ for  $ n \geq 2 $. By the definition of  $ d $ in (5.2), we obtain that  $ d(e_{013} - e_{023}) = e_{03} - e_{03} = 0 $. Hence,  $ \Theta_2^{[0,3]} = \langle e_{013} - e_{023} \rangle \cong \mathbb{Z} $ and  $ \Theta_n^{[0,3]} = 0 $ for  $ n \neq 2 $. Thus we conclude that  $ \mathcal{H}_5^{[0,3]}(I^2) = \mathbb{Z} $ for  $ n = 2 $ and  $ \mathcal{H}_n^{[0,3]}(I^2) = 0 $ otherwise.

(ii) Let  $ I^{3} $ be a digraph cube in Figure 1.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//6db1f8f7-1146-4820-b36b-a928565eb536/markdown_4/imgs/img_in_image_box_517_633_703_807.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A13Z%2F-1%2F%2F3357776487786936cbd0c82b7c348b55b889127b36a476424517fba261cadccf" alt="Image" width="15%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 1: Digraph cube  $ I^{3} $</div> </div>


We have  $ \mathcal{A}_i^{[0,7]} = 0 $ for  $ i \neq 3 $ and  $ \mathcal{A}_3^{[0,3]} = \langle e_{0137}, e_{0237}, e_{0157}, e_{0457}, e_{0467}, e_{0267} \rangle $. We have the following differential  $ d: \mathcal{A}_3^{[0,7]} \to \Lambda_2^{[0,7]} $:

 $$ \begin{array}{rcl}d(e_{0137})&=&e_{037}-e_{017},\quad d(e_{0237})&=&e_{037}-e_{027},\\d(e_{0157})&=&e_{057}-e_{017},\quad d(e_{0457})&=&e_{057}-e_{047},\\d(e_{0467})&=&e_{067}-e_{047},\quad d(e_{0267})&=&e_{067}-e_{027}.\end{array} $$ 

We can check directly that the kernel of d is generated by the element

 $$ w=e_{0137}-e_{0237}-e_{0157}+e_{0457}-e_{0467}+e_{0267}. $$ 

Hence,  $ \Theta_3^{[0,7]} = \langle w \rangle \cong \mathbb{Z} $ and  $ \Theta_n^{[0,7]} = 0 $ for  $ n \neq 3 $. Thus  $ \mathcal{H}_3^{[0,7]}(I^3) = \mathbb{Z} $ and  $ \mathcal{H}_n^{[0,7]}(I^3) = 0 $ otherwise.

(iii) Now we consider a digraph G in Figure 2 below.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//f8e2314f-29a3-440c-abae-8a33e34dff2a/markdown_0/imgs/img_in_image_box_486_241_852_611.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A06Z%2F-1%2F%2Fc1afca8248224dee19313bf23becd3f0d768adf735e59f9e590f8ed13146c81a" alt="Image" width="29%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 2: The planar digraph G from Example 5.7 (iii).</div> </div>


We have

 $$ \mathcal{A}_{n}^{[0,8]}=\begin{cases}{0}&{\mathrm{f o r~}n=0,}\\ {\langle e_{08}\rangle\cong\mathbb{Z}}&{\mathrm{f o r~}n=1,}\\ {\langle e_{028},e_{038}\rangle\cong\mathbb{Z}^{2}}&{\mathrm{f o r~}n=2,}\\ {\langle e_{0178},e_{0158},e_{0258},e_{0368},e_{0468},e_{0478}\rangle\cong\mathbb{Z}^{6}}&{\mathrm{f o r~}n=3,}\\ {0}&{\mathrm{f o r~}n\geq4.}\\ \end{cases} $$ 

We have the following differential in dimensions 1 and 2:

 $$ d(e_{08})=0,\;d(e_{028})=d(e_{038})=e_{08}. $$ 

In dimension 3, we have the following differential  $ d\colon \mathcal{A}_3^{[0,8]}\to\Lambda_2^{[0,7]} $:

 $$ \begin{array}{rclclclcl}d(e_{0178})&=&e_{078}-e_{018},&d(e_{0158})&=&e_{058}-e_{018},\\d(e_{0258})&=&e_{058}-e_{028},&d(e_{0368})&=&e_{068}-e_{038},\\d(e_{0468})&=&e_{068}-e_{048},&d(e_{0478})&=&e_{078}-e_{048}.\end{array} $$ 

Any nontrivial linear combination of elements of the right part of equalities in (5.11) doesn’t belong to  $ \mathcal{A}_{2}^{[0,8]} $ and, hence, by (5.9) and (5.10) we obtain

 $$ \mathcal{H}_{n}^{[0,8]}(G)=\begin{cases}\mathbb{Z}&for n=2,\\0&otherwise.\end{cases} $$ 

It is interesting to note, the path homology group of the digraph G is trivial in dimension two and the singular cubical homology group is non-trivial in dimension two [4, Propositions 13,14].

Theorem 5.8 Let  $  G = (V, E)  $ be a digraph and  $  a, b \in V  $ be two vertices.

(i) If  $ (a \to b) \notin E $ then there is a morphism of chain complexes

 $$ \Theta_{n}^{[a,b]}(G)\quad\stackrel{\pi^{[a,b]}}{\longrightarrow}\quad\Pi_{n-2}(G)\quad(n\geq1), $$ 

where  $ \Pi_n(G) $ is the chain complex in (3.1) for primitive path homology groups and  $ \pi^{[a,b]} $ is the restriction of the homomorphism  $ \pi^{[a,b]} $ defined in (5.3).

(ii) If  $ (a \rightarrow b) \in E $ then there is a morphism of chain complexes

 $$ \Theta_{n}^{[a,b]}(G)\quad\stackrel{\pi^{[a,b]}}{\longrightarrow}\quad\widetilde{\Pi}_{n-2}(G)\quad(n\geq1), $$ 

where  $ \widetilde{\Pi}_*(G) $ is the reduced chain complex and  $ \pi^{[a,b]} $ is the restriction of the homomorphism  $ \pi^{[a,b]} $ defined in (5.3).

Proof. (i) In this case, we have  $ \mathcal{A}_{1}^{[a,b]}(G) = \mathcal{A}_{-1}(G) = 0 $ and the restriction of the homomorphism  $ \pi^{[a,b]} $ to

 $$ \pi^{[a,b]}\colon\mathcal{A}_{2}^{[a,b]}(G)\to\mathcal{A}_{0}(G) $$ 

is given by $\pi^{[a,b]}(e_{ai_{0}b}) = e_{i_{0}} \in V$. Hence $\Theta_{2}^{[a,b]} = \mathcal{A}_{2}^{[a,b]}$, $\Pi_{0} = \mathcal{A}_{0}$, and the homomorphism in (5.16) is the homomorphism $\Theta_{2}^{[a,b]}(G) \to \Pi_{0}(G)$. Now consider the case $n \geq 3$. For every elementary $(a,b)$-cluster path $e_{ai_{0}\ldots i_{n-2}b} \in \mathcal{A}_{n}^{[a,b]}(G)$, we have $\pi^{[a,b]}(e_{ai_{0}\ldots i_{n-2}b}) = e_{i_{0}\ldots i_{n-2}} \in \mathcal{A}_{n-2}(G)$. Consider a diagram

 $$ \begin{array}{ccc} \mathcal{A}_{n}^{[a,b]}(G) & \longrightarrow &  \mathcal{A}_{n-2}(G) \\ d \downarrow & & \downarrow \partial \end{array} $$ 

 $$ \begin{array}{r l r l r l}{\mathcal{A}_{n-1}^{[a,b]}(G)}&{{}\xrightarrow{\subset}}&{\Lambda_{n-1}^{[a,b]}(V)}&{{}\xrightarrow{\pi^{[a,b]}}}}&{\Lambda_{n-3}(V)}&{{}\xleftarrow{\supset}}&{\mathcal{A}_{n-3}(G)}\end{array} $$ 

in which left and right bottom horizontal maps are the natural inclusions. Diagram (5.17) is commutative by the definition of the homomorphism  $ \pi^{a,b} $ in (5.3) and definitions of differentials in (5.2) and (2.1). Let  $ w \in \Theta_n^{[a,b]} $, then  $ w \in \mathcal{A}_n^{[a,b]}(G) $ and  $ d(w) \in \mathcal{A}_{n-1}^{[a,b]}(G) $. By the above, we have

 $$ \pi^{[a,b]}(w)\in\mathcal{A}_{n-2}(G)\quad\mathrm{a n d}\quad\pi^{[a,b]}(d(w))\in\mathcal{A}_{n-3}(G). $$ 

Furthermore, by commutativity of diagram  $ (5.17) $, we have

 $$ \partial\left(\pi^{[a,b]}\left(w\right)\right)=\pi^{[a,b]}\left(d(w)\right)\in\mathcal{A}_{n-3}(G). $$ 

Hence  $ \pi^{[a,b]}(w) \in \Pi_{n-2}(G) $ and the statement of the theorem follows in the case (i). The proof in the case (ii) is similar.

Corollary 5.9 Under assumptions of Theorem 5.8 we have the following homomorphisms. In the case (i), the morphism of chain complexes in (5.12) induces a homomorphism  $ \mathcal{H}_n^{[a,b]}(G) \to \mathcal{H}_{n-2}(G) $ of primitive path homology groups. In the case (ii) the morphism of chain complexes in (5.13) induces a homomorphism  $ \mathcal{H}_n^{[a,b]}(G) \to \widetilde{\mathcal{H}}_{n-2}(G) $ of primitive path homology groups.

Now we illustrate the relations of cluster homology theory to geometric properties of digraphs.

Theorem 5.10 Let  $  G = (V, E)  $ be a digraph and  $  \overline{G}  $ be the inverse directed digraph (see Definition 3.10). For any two vertices  $  v, w \in V  $ and  $  n \geq 0  $, there is an isomorphism of chain complex

 $$ \Theta_{*}^{[a,b]}(G)\cong\Theta_{*}^{[b,a]}(\overline{G}) $$ 

___ , ___ , ___ , ___ , ___

 $$ \mathcal{H}_{n}^{[a,b]}(G)\cong\mathcal{H}_{n}^{[b,a]}(\overline{{G}}). $$ 

Proof. Similar to the proof of Theorem 3.11.

Definition 5.11 Let  $  G = (V, E)  $ be a digraph. The directed suspension  $  S^d G  $ of the digraph  $  G  $ is a digraph obtained from  $  G  $ by adding two new vertices  $  a  $ and  $  b  $ and new arrows  $  (a \to v)  $,  $  (v \to b)  $ for all vertices  $  v \in V  $.

Theorem 5.12 Let  $  G = (V, E)  $ be a digraph and  $  S^d G  $ be the directed suspension defined by the vertices  $ a, b \notin V $. Then we have a natural isomorphism of chain complexes

 $$ \Theta_{*}^{[a,b]}(S^{d}G)\cong\Pi_{*}(G) $$ 

and, hence,

 $$ \mathcal{H}_{n}^{[a,b]}(S^{d}G)=\mathcal{H}_{n-2}(G). $$ 

Proof. For  $ n \geq 2 $, we define a homomorphism

 $$ \pi\colon\Lambda_{n}^{[a,b]}\left(V_{S^{d}(G)}\right)\to\Lambda_{n-2}(V)\mathrm{~\textbf{b y}}~\pi(e_{a i_{0}\dots i_{n-2}b})=e_{i_{0}\dots i_{n-2}}, $$ 

and we set  $ \pi = 0: 0 \to 0 $ for  $ n = 1 $. It follows from Definition 5.11 that  $ \pi $ is an isomorphism and its restriction to  $ \mathcal{A}_n^{[a,b]}(S^d G) $ is an isomorphism

 $$ \mathcal{A}_{n}^{[a,b]}(S^{d}G)\to\mathcal{A}_{n}(G). $$ 

By definitions of differentials $d$ in (5.2) and $\partial$ in (2.1) we obtain that the diagram

 $$ \begin{array}{ccc} \Lambda_{n}^{[a,b]}\left(V_{S^{d}G}\right) & \longrightarrow &  \Lambda_{n-2}(V) \\ {d}\downarrow& &  \downarrow  \mathcal{O} \\ \Lambda_{n-1}^{[a,b]}\left(V_{S^{d}G}\right) & \longrightarrow &  \Lambda_{n-3}(V) \end{array} $$ 

is commutative, and the result follows. ■

Example 5.13 Consider a cyclic digraph  $  G = (V, E)  $ below

 $$ \begin{array}{ccc}2&\\ \swarrow&\uparrow\\ 0&\rightarrow&1.\end{array} $$ 

Let  $ S^dG $ be the directed suspension defined by  $ a,b \notin V $ and  $ \mathbb{Z} $ be the ring of coefficients. By Corollary 3.8 and [9, Example 2.7],  $ \mathcal{H}_i(G) = H_i(G) = \mathbb{Z} $ for  $ i = 0,1 $. Hence, by Theorem 5.12,

 $$ \mathcal{H}_{3}^{[a,b]}(S^{d}G)=\mathcal{H}_{2}^{[a,b]}(S^{d}G)=\mathbb{Z}. $$ 

Now consider a digraph  $ H = (V_H, E_H) $ which has the same set of vertices as  $ S^d G $, and the set of arrows  $ E_H $ is obtained from  $ E_{S^d G} $ by deleting two arrows  $ (a \to 2) $ and  $ 2 \to b $. For  $ i \leq 4 $, we have

 $$ \mathcal{A}_{i}^{[a,b]}(H)=\begin{cases}{0}&{\mathrm{~f o r~}\;i=0,1,}\\ {\langle e_{a0b},e_{a1b}\rangle}&{\mathrm{~f o r~}\;i=2,}\\ {\langle e_{a01b}\rangle}&{\mathrm{~f o r~}\;i=3,}\\ {\langle e_{a120b}\rangle}&{\mathrm{~f o r~}\;i=4.}\\ \end{cases} $$ 

The further calculation of the groups  $ \mathcal{A}_i^{[a,b]}(H) $ is similar. To find the groups  $ \Theta_*\^{[a,b]}(H) $ we need to compute differentials

 $$ d\colon\mathcal{A}_{i}^{[a,b]}(H)\to\Lambda_{i}^{[a,b]}(H). $$ 

It follows from (5.17 that $d=0$ for $i=1,2$ and for $i=3,4$ we have:

 $$ \begin{array}{l}for i=3:\quad d(e_{a01b})=e_{a1b}-e_{a0b},\\ for i=4:\quad d(e_{a120b})=e_{a20b}-e_{a10b}+e_{a12b}.\end{array} $$ 

It follows from (5.17) and (5.18) that in dimensions  $ 1 \leq i \leq 4 $ there is only one nontrivial homology group  $ \mathcal{H}_2^{[a,b]}(H) = \mathbb{Z} $. It is an easy exercise for readers to check similarly above that  $ \mathcal{H}_2^{[a,b]}(H) = 0 $ for  $ i \geq 5 $.

## 6 Primitive homology of paths with a fixed tail or a head vertex

In this section, for a digraph G, we construct primitive path homology theories of paths with a fixed tail or a fixed head vertex. The construction in both cases is similar to the previous section. We describe relations between introduced primitive path homology and the path homology which was introduced in Sections 3 and 5. We present several examples. In this section we fix a unitary and commutative ring R of coefficients.

Definition 6.1 Let $V$ be a finite set of vertices, $a \in V$ be a vertex, and $n \geq 0$.

(i) A path in  $ \Lambda_n(V) $ is an a-tail path if it is a linear combination of n-paths with the tail vertex  $ a $. Such path is denoted  $ w^{[a,\cdot]} $. An elementary path fitting into the path  $ w^{[a,\cdot]} $ is called an elementary a-tail path.

(ii) A path in  $ \Lambda_n(V) $ is an a-head path if it is a linear combination of paths with the head vertex  $ a $. Such path is denoted  $ w^{[\cdot,a]} $. An elementary path fitting into the path  $ w^{[\cdot,a]} $ is called an elementary a-head path.

This definition is a natural generalization of the definitions of paths in a digraph G which are given by relations (4.1) and (4.2).

Let  $ n \geq 0 $ and  $ a \in V $. Denote by  $ \Lambda_n^{[a,\cdot]} = \Lambda_n^{[a,\cdot]}(V) $ a free module generated by elementary a-tail n-paths. The elements of  $ \Lambda_n^{[a,\cdot]} $ are called a-tail n-paths.

in V. Denote by  $ \Lambda_n^{[\cdot,a]} = \Lambda_n^{[\cdot,a]}(V) $ a free module generated by elementary a-head n-paths. The elements of  $ \Lambda_n^{[\cdot,a]} $ are called a-head n-paths in V. We set  $ \Lambda_{-1}^{[a,\cdot]} = \Lambda_{-1}^{[\cdot,a]} = 0 $.

For  $ n \geq 0 $, define differentials

 $$ d^{t}\colon\Lambda_{n}^{[a,\cdot]}\to\Lambda_{n-1}^{[a,\cdot]}\mathrm{~a n d~}d^{h}\colon\Lambda_{n}^{[\cdot,a]}\to\Lambda_{n-1}^{[\cdot,a]} $$ 

by setting on basic elements

 $$ d^{t}(e_{a i_{0}\ldots i_{n-1}})=\begin{cases}\displaystyle\sum_{m=0}^{n-1}(-1)^{m}e_{a i_{0}\ldots\widehat{i_{m}\ldots i_{n-1}}}&for n\geq1,\\0&for n=0,\end{cases} $$ 

 $$ d^{h}(e_{i_{0}\ldots i_{n-1}a})=\begin{cases}\displaystyle\sum_{m=0}^{n-1}(-1)^{m}e_{i_{0}\ldots\widehat{i_{m}\ldots i_{n-1}a}}&for n\geq1,\\0&for n=0.\end{cases} $$ 

Let  $ \widetilde{\Lambda}_*(V) $ be the augmented chain complex defined in Section 2. Recall that  $ \widetilde{\Lambda}_n(V) = \Lambda_n(V) $ for  $ n \geq 0 $,  $ \widetilde{\Lambda}_{-1}(V) = R $, and  $ \widetilde{\Lambda}_{-2}(V) = 0 $.

For  $ n \geq 0 $, define isomorphisms of modules

 $$ \begin{aligned}&\pi^{[a,\cdot]}:{\Lambda}_{n}^{[a,\cdot]}(V)\rightarrow\widetilde{\Lambda}_{n-1}(V),\\&\pi^{[\cdot,a]}:{\Lambda}_{n}^{[\cdot,a]}(V)\rightarrow\widetilde{\Lambda}_{n-1}(V),\\ \end{aligned} $$ 

by setting for  $ \pi^{[a,\cdot]}: \pi^{[a,\cdot]}(e_{ai_{0}\ldots i_{n-1}})=e_{i_{0}\ldots i_{n-1}} $ for  $ n\geq1 $,  $ \pi^{[a,\cdot]}(e_{a})=1\in R $ for  $ n=0 $, and  $ \pi^{[a,\cdot]}=0 $ for  $ n=-1 $. For  $ \pi^{[a]} $ we set similarly:  $ \pi^{[a,\cdot]}(e_{i_{0}\ldots i_{n-1}a})=e_{i_{0}\ldots i_{n-1}} $ for  $ n\geq1 $,  $ \pi^{[a,a]}(e_{a})=1\in R $ for  $ n=0 $, and  $ \pi^{[a,a]}=0 $ for  $ n=-1 $.

Proposition 6.2 For  $ n \geq 0 $, the following diagrams

 $$ \begin{array}{ccc}\Lambda_{n}^{[a,\cdot]}(V)&\xrightarrow{\pi^{[a,\cdot]}}&\widetilde{\Lambda}_{n-1}(V)\\&\\d^{t}\downarrow&&\downarrow\partial\\\\\Lambda_{n-1}^{[a,\cdot]}(V)&\xrightarrow{\pi^{[a,\cdot]}}&\widetilde{\Lambda}_{n-2}(V)\\\end{array} $$ 

and

 $$ \begin{array}{ccc}\Lambda_{n}^{[\cdot,a]}(V)&\xrightarrow{\pi^{[\cdot,a]}}&\widetilde{\Lambda}_{n-1}(V)\\&\\d^{h}\downarrow&&\downarrow\partial\\\end{array} $$ 

are commutative.

Proof. Follows from the definition of isomorphisms  $ \pi^{[a,\cdot]},\pi^{[\cdot,a]} $, the definition of differential  $ \partial $ in (2.1), and definitions of differentials  $ d^{t},d^{h} $ in (6.2).  $ \blacksquare $

Corollary 6.3 For  $ n \geq 0 $, the modules  $ \Lambda_n^{[a,:]} $ and  $ \Lambda_n^{[\cdot,a]} $ with differentials  $ d^t $ and  $ d^h $, respectively, form chain complexes.

Proof. In digrams (6.4) and (6.5) the modules  $ \tilde{\Lambda}_*(V) $ with the differential  $ \partial $ form chain complexes. The horizontal maps are isomorphisms. Now the statement follows from commutativity of these diagrams.

Definition 6.4 Let  $ G = (V, E) $ be a digraph,  $ a \in V $ be a vertex, and  $ n \geq 0 $.

(i) Let  $ \mathcal{A}_{n}^{[a,\cdot]} = \mathcal{A}_{n}^{[a,\cdot]}(G) $ be a module generated by elementary allowed a-tail n-paths in G. We set  $ \mathcal{A}_{-1}^{[a,\cdot]} = 0 $ and  $ \mathcal{A}_{n}^{[a,\cdot]} = 0 $ if there are no such paths.

(ii) Let  $ \mathcal{A}_{n}^{[:,a]} = \mathcal{A}_{n}^{[:,a]}(G) $ be a module generated by elementary allowed a-head n-paths in G. We set  $ \mathcal{A}_{-1}^{[:,a]} = 0 $ and  $ \mathcal{A}_{n}^{[:,a]} = 0 $ if there are no such paths.

It follows from Definition 6.4 that for every digraph G we have

 $$ \mathcal{A}_{0}^{[a,\cdot]}(G)=\mathcal{A}_{0}^{[\cdot,a]}(G)=\langle e_{a}\rangle for all a\in V, $$ 

 $$ \begin{align*}\mathcal{A}_{1}^{[a,:]}(G)&=\begin{cases}\langle e_{ab}\mid(a\to b)\in E\rangle,&if arrows(a\to b)\in E exist,\\0,&otherwise,\end{cases}\\\mathcal{A}_{1}^{[\cdot,a]}(G)&=\begin{cases}\langle e_{ba}\mid(b\to a)\in E\rangle,&if arrows(b\to a)\in E exist,\\0,&otherwise.\end{cases}\end{align*} $$ 

For  $ n \geq -1 $, the modules  $ \mathcal{A}_n^{[a,:]}(G) $ and  $ \mathcal{A}_n^{[:,a]}(G) $ are submodules of  $ \Lambda_n(V) $. For  $ n \geq 0 $, we define submodules

 $$ \begin{aligned}&\Theta_{n}^{[a,\cdot]}=\Theta_{n}^{[a,\cdot]}(G)=\{w\in\mathcal{A}_{n}^{[a,\cdot]}(G)\mid d^{t}(w)\in\mathcal{A}_{n-1}^{[a,\cdot]}(G)\}\\ &\\ &\Theta_{n}^{[\cdot,a]}=\Theta_{n}^{[\cdot,a]}(G)=\{w\in\mathcal{A}_{n}^{[\cdot,a]}(G)\mid d^{h}(w)\in\mathcal{A}_{n-1}^{[\cdot,a]}(G)\}\\ \end{aligned} $$ 

where d t and d h are differentials defined in (6.2). We set  $ \Theta_{-1}^{[a,\cdot]}=\Theta_{-1}^{[\cdot,a]}=0 $.

Proposition 6.5 The modules  $ \Theta_n^{[a,\cdot]}(G) $ ( $ n \geq 1 $) with the restriction of the differential  $ d^t $ and the modules  $ \Theta_n^{[:,a]}(G) $, ( $ n \geq -1 $) with the restriction of the differential  $ d^h $ form chain complexes  $ \Theta_*\^{[a,\cdot]} = \Theta_*\^{[a,\cdot]}(G) $ and  $ \Theta_*\^{[:,a]} = \Theta_*\^{[:,a]}(G) $, respectively

Proof. Similar to Proposition 5.5.

By (6.8) and (6.7), and by the definition of differentials  $ d^{h} $ and  $ d^{t} $, we obtain that for any digraph  $ G = (V, E) $

 $$ \Theta_{i}^{[a,\cdot]}(G)=\mathcal{A}_{i}^{[a,\cdot]},\ \Theta_{i}^{[\cdot\cdot a]}(G)=\mathcal{A}_{i}^{[\cdot,a]}\ \mathrm{f o r}\ -1\leq i\leq1. $$ 

Definition 6.6 (i) The homology groups of the chain complex  $ \Theta_{*}^{[a,:]}(G) $ are called primitive a-tail homology groups of the digraph  $ G $ and are denoted by  $ \mathcal{H}_{n}^{[a,:]}(G) = \mathcal{H}_{n}^{[a,:]}(G, R) (n \geq 0) $.

(ii) The homology groups of the chain complex  $ \Theta_{*}^{[:,a]}(G) $ are called primitive a-head homology groups of the digraph G and are denoted by  $ \mathcal{H}_{n}^{[:,a]}(G) = \mathcal{H}_{n}^{[:,a]}(G, R) (n \geq 0) $.

Theorem 6.7 Let $G$ be a digraph and $\overline{G}$ be the digraph which is obtained by changing directions of all arrows. Then, for $n \geq 0$, there is an isomorphism $\mathcal{H}_n^{[\cdot,a]}(G) \cong \mathcal{H}_n^{[a,\cdot]}(G)$.

Proof. Similar to the proof of Theorem 3.11.

Example 6.8 Let Z be the ring of coefficients.

(i) Consider a digraph G below

 $$ \begin{array}{ccc}3&2&\\ \uparrow&\nearrow&\searrow\\ 0&\rightarrow&1\rightarrow4.\end{array} $$ 

We have  $ \mathcal{A}_{-1}^{[0,:]}=0 $,  $ \mathcal{A}_{0}^{[0,\cdot]}=\langle e_{0}\rangle $,  $ \mathcal{A}_{1}^{[0,\cdot]}=\langle e_{01},e_{02},e_{03}\rangle $,  $ \mathcal{A}_{2}^{[0,\cdot]}=\langle e_{014},e_{024}\rangle $, and  $ \mathcal{A}_{n}^{[0,\cdot]}=0 $ for  $ n\geq3 $. In dimensions one and two, the differential  $ d^{t} $ is given as follows

 $$ d^{t}(e_{01})=d^{t}(e_{02})=d^{t}(e_{03})=e_{0}, $$ 

 $$ d^{t}(e_{014})=e_{04}-e_{01},\ d^{t}(e_{024})=e_{04}-e_{02}. $$ 

Hence,

 $$ \Theta_{0}^{[0,\cdot]}(G)=\langle e_{0}\rangle,\Theta_{1}^{[0,\cdot]}(G)=\langle e_{01},e_{02},e_{03}\rangle,\Theta_{2}^{[0,\cdot]}(G)=\langle e_{014}-e_{024}\rangle, $$ 

and  $ \Theta_n^{[0,\cdot]}(G) = 0 $ for  $ n \geq 3 $. Now the direct computation gives  $ \mathcal{H}_1^{[0,\cdot]}(G) = \mathbb{Z} $ and  $ \mathcal{H}_n^{[0,\cdot]}(G) = 0 $ for all  $ n \neq 1 $.

(ii) Consider a digraph G below

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//2e1b301d-6476-498e-aac2-ea8986b91817/markdown_3/imgs/img_in_image_box_504_649_717_819.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A13Z%2F-1%2F%2F91b8958c26c1d7868b58b19c34eb1db30d226c47b2c8c75bc91deebb8d0f562b" alt="Image" width="17%" /></div>


We have

 $$ \mathcal{A}_{-1}^{[0,\cdot]}=0,\ \mathcal{A}_{0}^{[0,\cdot]}=\langle e_{0}\rangle,\ \mathcal{A}_{1}^{[0,\cdot]}=\langle e_{01},e_{02}\rangle,\ \mathcal{A}_{2}^{[0,\cdot]}=\langle e_{013},e_{014},e_{023},e_{024}\rangle, $$ 

 $$ \mathcal{A}_{3}^{[0,\cdot]}=\langle e_{0134},e_{0234}\rangle,\quad\mathcal{A}_{n}^{[0,\cdot]}=0\mathrm{~f o r~}n\geq4. $$ 

In dimensions  $ 1 \leq n \leq 3 $, the differential  $ d^t $ is given as follows

 $$ d^{t}(e_{01})=d^{t}(e_{02})=e_{0}, $$ 

 $$ d^{t}(e_{013})=e_{03}-e_{01},\;d^{t}(e_{014})=e_{04}-e_{01},\;d^{t}(e_{023})=e_{03}-e_{02},\;d^{t}(e_{024})=e_{04}-e_{02}, $$ 

 $$ d^{t}(e_{0134})=e_{034}-e_{014}+e_{013}, $$ 

 $$ d^{t}(e_{0234})=e_{034}-e_{024}+e_{023}. $$ 

Hence,

 $$ \Theta_{0}^{[0,\cdot]}(G)=\langle e_{0}\rangle,\Theta_{1}^{[0,\cdot]}(G)=\langle e_{01},e_{02}\rangle,\Theta_{2}^{[0,\cdot]}(G)=\langle e_{013}-e_{023},e_{014}-e_{024}\rangle, $$ 

 $$ \Theta_{3}^{[0,:]}(G)=\langle e_{0134}-e_{0234}\rangle,\mathrm{a n d}\Theta_{n}^{[0,\cdot]}(G)=0\mathrm{f o r}n\geq4. $$ 

Now the direct computation gives  $ \mathcal{H}_{n}^{[0,\cdot]}(G)=0 $ for all n.

(iii) Consider a digraph G below

 $$ \begin{array}{ccc}{{{3}}}&{{{\rightarrow}}}&{{{4}}} \\{{{\nearrow}}}&{{{\uparrow}}}&{{{\uparrow}}} \\{{{1}}}&{{{\leftarrow}}}&{{{0}}}&{{{\rightarrow}}}&{{{2}}} \\\end{array} $$ 

We have

 $$ \mathcal{A}_{-1}^{[0,\cdot]}=0,\mathcal{A}_{0}^{[0,\cdot]}=\langle e_{0}\rangle\cong\mathbb{Z},\mathcal{A}_{1}^{[0,\cdot]}=\langle e_{01},e_{02},e_{03}\rangle\cong\mathbb{Z}^{3}, $$ 

 $$ \mathcal{A}_{2}^{[0,\cdot]}=\langle e_{013},e_{024},e_{034}\rangle\cong\mathbb{Z}^{3},\;\mathcal{A}_{3}^{[0,\cdot]}=\langle e_{0134}\rangle\cong\mathbb{Z},\;\mathcal{A}_{n}^{[0,\cdot]}=0\mathrm{~f o r~}n\geq4. $$ 

Now we can compute the differential d:  $ \mathcal{A}_n^{[0,\cdot]} \to \Lambda_{n-1}^{0,\cdot} $. We have  $ d^t(e_0) = 0 $,

 $$ d^{t}(e_{013})=e_{03}-e_{01}, $$ 

 $$ d^{t}(e_{024})=e_{04}-e_{02}, $$ 

 $$ d^{t}(e_{034})=e_{04}-e_{03}, $$ 

 $$ d^{t}(e_{0134})=e_{034}-e_{014}+e_{013}. $$ 

Hence $\Theta_n^{[0,\cdot]}=0$ for $n\geq3$, $\Theta_2^{[0,\cdot]}\langle e_{013},e_{024}-e_{034}\rangle\cong\mathbb{Z}^2$, $\Theta_1^{[0,\cdot]}=\langle e_{01},e_{02},e_{03}\rangle\cong\mathbb{Z}^3$, $\Theta_0^{[0,\cdot]}=\langle e_0\rangle=\mathbb{Z}$, and $\Theta_n^{[0,\cdot]}=0$ for $n=-1$. Thus we obtain $\mathcal{H}_n^{[0,\cdot]}=0$ for all $n$.

The notions of a cone and of a suspension of a digraph were introduced in [8], [10, Definition 4.20]. We use these digraph constructions to describe geometric properties of primitive a-head and a-tail homology. At first we recall these definitions.

Definition 6.9 Let G = (V, E) be a digraph.

(i) The cone  $ CG $ is obtained from the digraph  $ G $ by adding a new vertex  $ a $ and new arrows  $ (v \to a) $ for all vertices  $ v \in V $.

(ii) The inverse cone $C^{-}G$ is obtained from the digraph $G$ by adding a new vertex $a$ and new arrows $(a \to v)$, $(b \to v)$ for all vertices $v \in V$.

(iii) The suspension SG is obtained from the digraph G by adding two new vertices a and b and new arrows  $ (v \to a) $,  $ (v \to b) $ for all vertices  $ v \in V $.

(iv) The inverse suspension $S^{-}G$ is obtained from the digraph $G$ by adding two new vertices $a$ and $b$ and new arrows $(a \to v), (b \to v)$ for all vertices $v \in V$.

Theorem 6.10 Let  $  G = (V, E)  $ be a digraph and  $  CG  $,  $  C^{-}G  $ be direct and inverse cones which are defined by the vertex  $  a \notin V  $. Then there are the following relations between primitive path homology groups:

 $$ \mathcal{H}_{n}^{[v,a]}(C G)=\mathcal{H}_{n-1}^{[v,\cdot]}(G)\quad{f o r~e v e r y}\quad v\in V, $$ 

 $$ \mathcal{H}_{n}^{[a,v]}(C^{-}G)=\mathcal{H}_{n-1}^{[\cdot,v]}(G)\quad{f o r~e v e r y}\quad v\in V. $$ 

Let SG,  $ S^{-}G $ be direct and inverse suspensions which are defined by the vertices  $ a, b \notin V $. Then there are the following relations between primitive path homology groups:

 $$ \mathcal{H}_{n}^{[v,a]}(S G)=\mathcal{H}_{n}^{[v,b]}(S G)=\mathcal{H}_{n}^{[v,a]}(C G)=\mathcal{H}_{n-1}^{[v,\cdot]}(G)\quad{f o r~e v e r y}\quad v\in V, $$ 

 $$ \mathcal{H}_{n}^{[a,v]}(S^{-}G)=\mathcal{H}_{n}^{[b,v]}(S^{-}G)=\mathcal{H}_{n}^{[a,v]}(C^{-}G)=\mathcal{H}_{n-1}^{[\cdot,v]}(G)\quad{f o r~e v e r y}\quad v\in V. $$ 

Proof. Similar to the proof of Theorem 5.12.

## 7 Functionality

In this section, we prove functionality of primitive homology theories constructed in Sections 5 and 6 on the category  $ A D $ of asymmetric digraphs.

Theorem 7.1 Let $f: G \to H$ be a map of asymmetric digraphs. For two vertices $a, b \in V_G$ the homomorphism $f_\sharp: \Lambda_n(V_G) \to \Lambda_n(V_H) (n \geq -1)$ defined in (3.4) provides morphisms of chain complexes:

 $$ \begin{aligned}&f_{*}\colon\Theta_{*}^{[a,b]}(G)\to\Theta_{*}^{[f(a),f(b)]}(H),\\ &\\ &f_{*}\colon\Theta_{*}^{[a,\cdot]}(G)\to\Theta_{*}^{[f(a),\cdot]}(H),\\ &\\ &f_{*}\colon\Theta_{*}^{[\cdot,b]}(G)\to\Theta_{*}^{[\cdot,f(b)]}(H)\\ \end{aligned} $$ 

which induce homomorphisms of primitive homology groups:

 $$ \begin{aligned}&f_{*}\colon\mathcal{H}_{*}^{[a,b]}(G)\to\mathcal{H}_{*}^{[f(a),f(b)]}(H),\\ &\\ &\quad f_{*}\colon\mathcal{H}_{*}^{[a,\cdot]}(G)\to\mathcal{H}_{*}^{[f(a),\cdot]}(H),\\ &\\ &\quad f_{*}\colon\mathcal{H}_{*}^{[\cdot,b]}(G)\to\mathcal{H}_{*}^{[\cdot,f(b)]}(H).\\ \end{aligned} $$ 

Proof. Similar to the proof of Proposition 3.5.

## References

[1] P. Alexandroff, Discrete raume, Matem. Sb. 2(44) (1937), 501--519.

[2] Gary Chartrand, Linda Lesniak, and Ping Zhang, Graphs and digraphs, CRC Press: Boca Raton, Publadd, Florida, United States, 2011.

[3] Xin Fu and Sergei O. Ivanov, Path homology of digraphs without multi-squares and its comparison with homology of spaces, arXiv:2407.17001v1 (24 Jul 2024), 1–18.

[4] A. A. Grigor'yan, R. Jimenez, and Yu. V. Muranov, Homology of Di-graphs, Mathematical Notes 109 (2021), 712–726.

[5] A. A. Grigor'yan, Yong Lin, Yu. V. Muranov, and Shing-Tung Yau, Path complexes and their homologies, Journal of Mathematical Sciences 248 (2020), 564–599.

[6] Alexander Grigor'yan, Advances in path homology theory of digraphs, Notices of the International Consortium of Chinese Mathematicians 10 (2022), 61–124.

[7] Alexander Grigor’yan, Rolando Jimenez, Yuri Muranov, and Shing-Tung Yau, Homology of path complexes and hypergraphs, Topology and its Applications 269 (2019), 1–25.

[8] Alexander Grigor’yan, Yong Lin, Yuri Muranov, and Shing-Tung Yau, Homologies of path complexes and digraphs, Math arXiv: 1207.2834v4 (2013), 1–88.

[9] ___ , Homotopy theory for digraphs, Pure and Applied Mathematics Quarterly 10 (2014), 619–674.

[10] ___ , Cohomology of digraphs and (undirected) graphs, Asian Journal of Mathematics 19 (2015), 887–932.

[11] Alexander Grigor’yan and Yuri Muranov, On homology theories of cubical digraphs, Pacific Journal of Math. 322 (2023), 39–58.

[12] Alexander Grigor’yan, Yuri Muranov, and Shing-Tung Yau, Graphs associated with simplicial complexes, Homology, Homotopy, and Applications 16 (2014), 295–311.

[13] ___，On a cohomology of digraphs and hochschild cohomology, J. Homotopy Relat. Struct. 11 (2016), 209–230.

[14] An Huang and Shing-Tung Yau, On cohomology theory of (di)graphs, Homology Homotopy Appl. 17 (2015), 383–398.

[15] Rolando Jimenez and Yuri Muranov, Cyclic path homology of (di)graphs, Moscow Mathematical Journal 24 (2024), 373–390.

[16] Jingyan Li, Yuri Muranov, Jie Wu, and Shing-Tung Yau, On homology of circuits, BJPAM (2024), to appear.

[17] Yu. V. Muranov, Alexandroff homology and path homology, Mathematical Notes 112 (2022), 159–162.

[18] Yu. V. Muranov and R. Jimenez, Homology of transitive digraphs and discrete spaces, Sbornik: Mathematics 214 (2023), 1121–1139.

[19] XinXing Tang and Shing-Tung Yau, Minimal path and acyclic models, arXiv:2208.14063v1 (30 Aug 2022), 1–48.

[20]  $ \underline{\text{}} $, The cellular homology of digraphs, arXiv:2402.05682v1 (8 Feb2024), 1–51.

Jingyan Li: Beijing Institute of Mathematical Sciences and Application,

No. 544 Hefangkou Village, Huairou, Beijing China.

e-mail: jingyanli@bimsa.cn

Yuri Muranov: Faculty of Mathematics and Computer Science, University

uranov: Faculty of Mathematics and Computer Science, University of Warmia and Mazury in Olsztyn, Sloneczna 54 Street, 10-710 Olsztyn, Poland.

e-mail: muranov@matman.uwm.edu.pl

Jie Wu: Beijing Institute of Mathematical Sciences and Application, No. 'Hofanqkou Village, Huairou, Beijing China.

544 Hefangkou Village, Huairou, Beijing China.

e-mail: wujie@bimsa.cn

Shing-Tung Yau: Room 215, Yau Mathematical Sciences Center, Jing

- 1986 1au: Room 215, Yau Mathematical Sciences Center, Jing Zhai, Tsinghua University, Hai District, Beijing, China.

e-mail: styau@tsinghua.edu.cn

