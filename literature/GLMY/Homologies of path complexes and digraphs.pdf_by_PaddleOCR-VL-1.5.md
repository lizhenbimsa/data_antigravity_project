# Homologies of path complexes and digraphs

Alexander Grigor'yan *

Department of Mathematics

University of Bielefeld

33613 Bielefeld, Germany

Yuri Muranov $ ^{\dagger} $

Department of Mathematics

Grodno State University

Grodno 230023, Republic of Belarus

Yong Lin $ ^{\dagger} $

Department of Mathematics

Information School

Renmin University of China

Beijing 100872, China

Shing-Tung Yau

Department of Mathematics

Harvard University

Cambridge MA 02138, USA

May 2013

## Contents

1 Introduction 3    
    
2 Paths and forms a finite set 4    
2.1 Space of paths and the boundary operator 4    
2.2 Join of paths 6    
2.3 Regular paths 7    
2.4 Form and exterior differential 9    
2.5 Concatenation of forms 11    
2.6 Regular forms 12    
    
3 Path complexes 14    
3.1 Path complexes, simplicial complexes, digraphs 14    
3.2 Allowed paths 16    
3.3  $ \partial $-invariant paths 18    
3.4 d-invariant forms 23    
3.5 A condition for  $ \Omega^{p}=0 $ 26    
3.6 Connected components and  $ H^{0} $ 27    
3.7 Disjoint union and connected sum 28

4  $ \partial $-invariant paths on digraphs 28    
4.1 Semi-edges and  $ \partial $-invariant paths 28    
4.2 Triangles, squares and  $ \dim\Omega_{p} $ 29    
4.3 Snakes and simplexes 32    
4.4 Star-shaped digraphs and Poincaré lemma 33    
4.5 Cycle-graphs 33    
4.6 An example of direct computation of  $ \dim H_{p} $ 35    
4.7 Triangulation as a closed path 36    
4.8 Lemma of Sperner revisited 38    
5 Homologies of subgraphs 40    
5.1 Chain complex of a subgraph 40    
5.2 Removing a vertex of degree 1 40    
5.3 Removing a vertex of degree n 42    
5.4 Removing a vertex of degree  $ 1+1 $ 44    
6 Join of path complexes 49    
6.1 Definition and examples of a join 50    
6.2 Chain complex of a join 52    
6.3 Cones and simplexes 58    
6.4 Suspension and spheres 59    
7 Cartesian product of path complexes 62    
7.1 Cross product of regular paths 62    
7.2 The product rule 65    
7.3  $ \partial $-invariant paths on Cartesian product 68    
7.4 Cylinders and hypercubes 70    
7.5 Representation of  $ \partial $-invariant paths on product 72    
7.6 Proof of Künneth formula 76    
8 Minimal paths and hole detection 80    
9 Appendix: Elements of homological algebra 82    
9.1 Cochain complexes 82    
9.2 Chain complexes 83    
9.3 Tensor product of chain complexes 84    
9.4 Sub-complexes and quotient complexes 85    
9.5 Zigzag Lemma 86    
References 87

## 1 Introduction

In this paper we introduce a new notion – a path complex that can be regarded as a generalization of the notion of a simplicial complex. In short, a path complex P on a finite set V is a collection of paths (=sequences of points) on V such that if a path v belongs to P then a truncated path that is obtained from v by removing either the first or the last point, is also in P. Given a path complex P, all the paths in P are called allowed, while the paths outside P are called non-allowed.

Any simplicial complex S determines naturally a path complex by associating with any simplex from S the sequence of its vertices (see Section 3.1 for details).

However, the main motivation for considering path complexes comes from directed graphs (digraphs). A digraph $G$ is a pair $(V, E)$ where $V$ is a set as above and $E$ is a binary relation on $V$ that is, $E$ is a subset of $V \times V$. If $(a, b) \in E$ then the pair $(a, b)$ is called a directed edge; this fact is also denoted by $a \to b$. Any digraph naturally gives rise to a path complex where allowed paths go along the arrows of the digraph.

One of our key observations is that any path complex P gives rise to a chain complex with an appropriate boundary operator  $ \partial $ that leads to the notion of homology groups of P. We refer to this notion as a path homology.

In the case when P arises from a simplicial complex S, the path homology of P coincides with the simplicial homology of S. If P arises from a digraph G then we obtain a new notion: the path homology of a digraph. The path complexes of digraphs are the central objects of this paper. Although most of the results are presented for arbitrary path complexes, we always have in mind applications for digraphs. On the other hand, the notion of a path complex provides an alternative approach to the classical results about simplicial complexes.

There has been a number of attempts to define the notions of homology and cohomology for graphs. At a trivial level, any graph can be regarded as an one-dimensional simplicial complex, so that its simplicial homologies are defined. However, all homology groups of order 2 and higher are trivial, which makes this approach uninteresting.

Another way to make a graph into a simplicial complex is to consider all its cliques (=complete subgraphs) as simplexes of the corresponding dimensions (cf. [2], [10]). Then higher dimensional homologies may be non-trivial, but in this approach the notion of graph looses its identity and becomes a particular case of the notion of a simplicial complex. Besides, some desirable functional properties of homologies fail, for example, the Künneth formula is not true for Cartesian product of graphs.

Yet another approach to homologies of digraphs can be realized via Hochschild homology. Indeed, allowed paths on a digraph have a natural operation of product, which allows to define the notion of a path algebra of a digraph. The Hochschild homology of the path algebra is a natural object to consider. However, it was shown in [9] that Hochschild homologies of order  $ \geq $ 2 are trivial, which makes this approach not so attractive.

The path homologies of digraphs that we introduce in this paper have many advantages in comparison with the previously studied notions of graph homologies.

Firstly, the homologies of all dimensions could be non-trivial. Also, the chain complex associated with a path complex has a richer structure that simplicial chain complexes. It contains not only cliques but also binary hypercubes and many other subgraphs. By the way, the dimensions of the chain spaces are themselves non-trivial invariants of the digraphs.

Secondly, this notion is well linked to graph-theoretical operations. For example, the Künneth formula is true for join of two digraphs as well as for Cartesian product of two digraphs.

Thirdly, there is a dual cohomology theory with the coboundary operator d that arises

independently and naturally as an exterior derivative on the algebra of functions on the vertex set of the graph. The latter approach to the cohomology of digraphs, that is based on the classification of exterior derivations on algebras (cf. [1, III, §10.2]), was developed by Dimakis and Müller-Hoissen in [3] and [4]. In the present paper we introduce the notion of cohomology of path complexes independently, using the duality with homologies. The reader is referred to [8] where the equivalence of the two approaches is explained.

We feel that the notion of path homology of digraphs has a rich mathematical content and hope that it will become a useful tool in various areas of pure and applied mathematics. For example, this notion was employed in [7] to give a new elementary proof of a theorem of Gerstenhaber and Schack [5] that represents simplicial homology as a Hochschild homology. A link between path homologies of digraphs and cubical homologies was revealed in [6]. On the other hand, it is conceivable that the notion of path homology can be used in practical applications such as hole detection in graphs or coverage verification in sensor networks (cf. [12]).

Let us briefly describe the structure of the paper and the main results. In Section 2, we define the notions of p-paths and p-forms on a finite set V, as well as the dual operators  $ \partial $ and d. We also define the notions of join of paths and concatenation of forms and prove that they satisfy the product rule.

In Section 3 we define the notions of a path complex, a  $ \partial $-invariant path (element of a chain space), and a path homology. Then we define also the dual notions of  $ d $-invariant form and path cohomology.

In Section 4 we apply the aforementioned notions to digraphs and give numerous examples of  $ \partial $-invariant paths on digraphs. We prove some basic results about path homologies of digraphs. For example, we describe chain spaces and homologies of digraphs without squares (Theorem 4.3) and prove the Poincaré lemma for star-shaped digraphs (Theorem 4.6).

In Section in 5 we prove some relations between path homologies of a digraph and its sub-graphs (Theorems 5.1, 5.4, and 5.7).

In Section 6 we introduce the operation join of two path complexes and prove the Künneth formula for homologies of join (Theorem 6.5). Particular cases of join are operation of cone and suspension of a digraph that behave homologically in the same way as those in the classical algebraic topology.

In Section 7 we introduce the notions of cross product of paths and Cartesian product of path complexes. The latter matches the notion of Cartesian product of digraph. The main result of this section is the Künneth formula for Cartesian product (Theorem 7.6 that is based on Theorem 7.15).

In Section 8 we sketch an approach to hole detection on digraphs. In Section 9 (Appendix) we revise for the convenience of the reader some elementary results of homological algebra that are used in the main body of the paper.

## 2 Paths and forms a finite set

### 2.1 Space of paths and the boundary operator

Let V be an arbitrary non-empty finite set whose elements are called vertices. Fix a field K whose elements are called scalars.

Definition 2.1 For any non-negative integer $p$, an elementary $p$-path on a set $V$ is any sequence $\{i_k\}_{k=0}^p$ of $p+1$ vertices of $V$ (a priori the vertices in the path do not have to be distinct). For $p=-1$, an elementary $p$-path is the empty set $\emptyset$.

The $p$-path $\{i_k\}_{k=0}^p$ will also be denoted simply by $i_0...i_p$, without delimiters between the vertices.

Denote by  $ \Lambda_p = \Lambda_p(V, \mathbb{K}) $ the  $ \mathbb{K} $-linear space that consists of all formal linear combinations of all elementary p-paths with the coefficients from  $ \mathbb{K} $.

##### Definition 2.2 The elements of  $ \Lambda_{p} $ are called p-paths on V.

An elementary $p$-path $i_{0}...i_{p}$ as an element of $\Lambda_{p}$ will be denoted by $e_{i_{0}...i_{p}}$. The empty set as an element of $\Lambda_{-1}$ will be denoted by $e$.

By definition, the family  $ \{e_{i_0...i_p} : i_0, ..., i_p \in V\} $ is a basis in  $ \Lambda_p $. Each  $ p $-path  $ v $ has a unique representation in the form

 $$ v=\sum_{i_{0},\ldots,i_{p}\in V}v^{i_{0}\cdots i_{p}}e_{i_{0}\ldots i_{p}}, $$ 

where  $ v^i_0 \cdots i_p \in \mathbb{K} $. For example, the space  $ \Lambda_0 $ consists of all linear combinations of the elements  $ e_i $ that are just the vertices of  $ V $, the space  $ \Lambda_1 $ consists of all linear combinations of the elements  $ e_{ij} $ that are pairs of vertices, etc. Note that  $ \Lambda_{-1} $ consists of all multiples of  $ e $, so that  $ \Lambda_{-1} \cong \mathbb{K} $.

Definition 2.3 For any  $ p \geq 0 $, the boundary operator  $ \partial : \Lambda_p \to \Lambda_{p-1} $ is a linear operator that is defined on the elementary paths by

 $$ \partial e_{i_{0}\ldots i_{p}}=\sum_{q=0}^{p}(-1)^{q}e_{i_{0}\ldots\widehat{i_{q}\ldots i_{p}}}, $$ 

where the hat iq means omission of the index iq.

For example, we have

 $$ \partial e_{i}=e,\quad\partial e_{i j}=e_{j}-e_{i},\quad\partial e_{i j k}=e_{j k}-e_{i k}+e_{i j}. $$ 

For an arbitrary p-path  $ (2.1) $ with  $ p \geq 0 $, we have

 $$ \partial v=\sum_{i_{0},\ldots,i_{p}}v^{i_{0}\cdots i_{p}}\partial e_{i_{0}\cdots i_{p}}=\sum_{i_{0},\ldots,i_{p}}\sum_{q=0}^{p}(-1)^{q}v^{i_{0}\cdots i_{p}}e_{i_{0}\cdots\widehat{i_{q}\cdots i_{p}}} $$ 

whence

 $$ \begin{array}{r c l}{(\partial v)^{j_{0}\dots j_{p-1}}}&{=}&{\displaystyle\sum_{i_{0},\dots,i_{p}}\displaystyle\sum_{q=0}^{p}(-1)^{q}v^{i_{0}\dots i_{p}}(e_{i_{0}\dots\widehat{i_{q}}\dots i_{p}})^{j_{0}\dots j_{p-1}}}\\ {}&{=}&{\displaystyle\sum_{k\in V}\displaystyle\sum_{q=0}^{p}(-1)^{q}v^{j_{0}\dots j_{q-1}k}j_{q}\dots j_{p-1}}\\ \end{array} $$ 

where the index  $ k $ is inserted in the path  $ j_0\cdots j_{p-1} $ between  $ j_{q-1} $ and  $ j_q $ if  $ 1 \leq q < p $, before  $ j_0 $ if  $ q = 0 $, and after  $ j_{p-1} $ if  $ q = p $.

For example, or any  $ v \in \Lambda_0 $, we have

 $$ \partial v=\sum_{k\in V}v^{k}, $$ 

for  $ v \in \Lambda_1 $ we have

 $$ (\partial v)^{i}=\sum_{k}\left(v^{k i}-v^{i k}\right) $$ 

and for  $ v \in \Lambda_2 $ we have

 $$ \left(\partial v\right)^{i j}=\sum_{k}\left(v^{k i j}-v^{i k j}+v^{i j k}\right). $$ 

Set also  $ \Lambda_{-2} = \{0\} $ and define  $ \partial : \Lambda_{-1} \to \Lambda_{-2} $ to be zero.

Lemma 2.4 We have  $ \partial^{2}=0 $.

Proof. The operator $\partial^2$ acts from $\Lambda_p$ to $\Lambda_{p-2}$, so that the identity $\partial^2 = 0$ makes sense for all $p \geq 0$. In the case $p = 0$ the identity $\partial^2 = 0$ is trivial. For $p \geq 1$, we have by (2.2)

 $$ \begin{array}{r c l}{\partial^{2}e_{i_{0}...i_{p}}}&{=}&{\displaystyle\sum_{q=0}^{p}(-1)^{q}\partial e_{i_{0}...\widehat{i_{q}}...i_{p}}}\\ {}&{=}&{\displaystyle\sum_{q=0}^{p}(-1)^{q}\left(\displaystyle\sum_{r=0}^{q-1}(-1)^{r}e_{i_{0}...\widehat{i_{r}}...\widehat{i_{q}}...i_{p}}+\displaystyle\sum_{r=q+1}^{p}(-1)^{r-1}e_{i_{0}...\widehat{i_{q}}...\widehat{i_{r}}...i_{p}}\right)}\\ {}&{=}&{\displaystyle\sum_{0\leq r<q\leq p}(-1)^{q+r}e_{i_{0}...\widehat{i_{r}}...\widehat{i_{q}}...i_{p}}-\displaystyle\sum_{0\leq q<r\leq p}(-1)^{q+r}e_{i_{0}...\widehat{i_{q}}...\widehat{i_{r}}...i_{p}}.}\\ \end{array} $$ 

After switching $q$ and $r$ in the last sum we see that the two sums cancel out, whence $\partial^2 e_{i_0...i_p} = 0$. This implies $\partial^2 v = 0$ for all $v \in \Lambda_p$. ■

Consequently, we have the following chain complex of the set V:

 $$ 0\leftarrow\mathbb{K}\leftarrow\Lambda_{0}\leftarrow\ldots\leftarrow\Lambda_{p-1}\leftarrow\Lambda_{p}\leftarrow\ldots $$ 

where the arrows are given by the operator  $ \partial $.

### 2.2 Join of paths

Definition 2.5 For all  $ p, q \geq -1 $ and for any two paths  $ u \in \Lambda_p $ and  $ v \in \Lambda_q $ define their join  $ uv \in \Lambda_{p+q+1} $ as follows:

 $$ (u v)^{i_{0}\dots i_{p}j_{0}\dots j_{q}}=u^{i_{0}\dots i_{p}}v^{j_{0}\dots j_{q}}. $$ 

Clearly, join of paths is a bilinear operation that satisfies the associative law (but is not commutative). For  $ u = e_{i_0...i_p} $ and  $ v = e_{j_0...j_q} $, we obtain from (2.7)

 $$ e_{i_{0}\ldots i_{p}}e_{j_{0}\ldots j_{q}}=e_{i_{0}\ldots i_{p}j_{0}\ldots j_{q}}. $$ 

It $p = -2$ and $q \geq -1$ then set $uv = 0 \in \Lambda_{q-1}$. A similar rule applies it $q = -2$ and $p \geq -1$.

Now we can state and prove the product rule for the operation of joining the paths.

Lemma 2.6 (Product rule) For all p, q ≥ -1 and u ∈ Λp, v ∈ Λq we have

 $$ \partial\left(u v\right)=\left(\partial u\right)v+\left(-1\right)^{p+1}u\partial v. $$ 

Proof. It suffices to prove (2.9) for  $ u = e_{i_0...i_p} $ and  $ v = e_{j_0...j_q} $. We have

 $$ \begin{align*}\partial\left(uv\right)\ =\ &\partial e_{i_{0}\ldots i_{p}j_{0}\ldots j_{q}}=e_{i_{1}\ldots i_{p}j_{0}\ldots j_{q}}-e_{i_{0}i_{2}\ldots i_{p}j_{0}\ldots j_{q}}+\ldots\\&\quad+(-1)^{p+1}\left(e_{i_{0}\ldots i_{p}j_{1}\ldots j_{q}}-e_{i_{0}\ldots i_{p}j_{0}j_{2}\ldots j_{q}}+\ldots\right)\\\ =\ &\left(\partial e_{i_{0}\ldots i_{p}}\right)e_{j_{0}\ldots j_{q}}+(-1)^{p+1}e_{i_{0}\ldots i_{p}}\partial e_{j_{0}\ldots j_{q}},\end{align*} $$ 

whence (2.9) follows. ■

### 2.3 Regular paths

Definition 2.7 We say that an elementary path  $ i_0...i_p $ is non-regular if  $ i_{k-1} = i_k $ for some  $ k = 1, ..., p $, and regular otherwise.

For example, a 1-path ii is non-regular, while a 2-path iji is regular provided i ≠ j.

For any  $ p \geq -1 $, consider the following subspace of  $ \Lambda_p $ spanned by the regular elementary paths:

 $$ \mathcal{R}_{p}=\mathcal{R}_{p}\left(V\right):=\mathrm{s p a n}\left\{e_{i_{0}\ldots i_{p}}:i_{0}\ldots i_{p}\mathrm{~i s~r e g u l a r}\right\}. $$ 

Note that  $ \mathcal{R}_p = \Lambda_p $ for  $ p \leq 0 $, but  $ \mathcal{R}_p $ is strictly smaller than  $ \Lambda_p $ for  $ p \geq 1 $. Similarly, consider the subspace of  $ \Lambda_p $ spanned by non-regular elementary paths:

 $$ I_{p}=I_{p}\left(V\right)=\mathrm{s p a n}\left\{e_{i_{0}\ldots i_{p}}:i_{0}\ldots i_{p}\mathrm{~i s~n o n-r e g u l a r}\right\}. $$ 

For example, we have  $ I_{0} = \{0\} $ and  $ I_{1} = \text{span} \{e_{ii}\} $.

For $p = -2$ we set $\mathcal{R}_{-2} = I_{-2} = \{0\}$. Then we have $\Lambda_p = \mathcal{R}_p \oplus I_p$ for all $p \geq -2$, which implies that the quotient space

 $$ \widetilde{\mathcal{R}}_{p}=\widetilde{\mathcal{R}}_{p}\left(V\right):=\Lambda_{p}/I_{p} $$ 

is isomorphic to  $ \mathcal{R}_{p} $.

In what follows, the elements of a quotient space $U/W$ will be denoted by $u \bmod W$ where $u \in U$. Also, we write $u_1 = u_2 \bmod W$ if $u_1 - u_2 \in W$.

Definition 2.8 The elements of  $ \mathcal{R}_p $ are called regular  $ p $-paths. The elements of  $ \widetilde{\mathcal{R}}_p $, that is, the equivalence classes  $ v \bmod I_p $ (where  $ v \in \Lambda_p $), are called regularized  $ p $-paths.

Obviously, any regularized p-path has exactly one representative in regular p-paths.

We would like to consider the operator $\partial$ on the spaces $\mathcal{R}_p$. However, $\partial$ is not invariant on spaces of regular paths. For example, $e_{iji} \in \mathcal{R}_2$ for $i \neq j$ while its boundary $\partial e_{iji} = e_{ji} - e_{ii} + e_{ij}$ is not in $\mathcal{R}_1$ as it has a non-regular component $e_{ii}$. The same applies to the notion of join of paths: the join of two regular path does not have to be regular, for example, $e_i e_i = e_{ii}$.

Below we will modify the definitions of  $ \partial $ and join to make them invariant on the spaces  $ \mathcal{R}_p $. The basic idea is that when applying  $ \partial $ or join on regular paths, one should drop from the result all the non-regular components, so that it becomes regular. Technically it is easier (and cleaner) to define  $ \partial $ and join first on the quotient spaces  $ \widetilde{\mathcal{R}}_p $, and then pass to  $ \mathcal{R}_p $ by isomorphism.

Lemma 2.9 Let  $ p, q \geq -1 $.

(a) If  $ v_1, v_2 \in \Lambda_p $ and  $ v_1 = v_2 \bmod I_p $ then  $ \partial v_1 = \partial v_2 \bmod I_{p-1} $.

(b) Let  $ u_1, u_2 \in \Lambda_p $,  $ v_1, v_2 \in \Lambda_q $. If  $ u_1 = u_2 \bmod I_p $ and  $ v_1 = v_2 \bmod I_q $ then  $ u_1 v_1 = u_2 v_2 \bmod I_{p+q+1} $.

Proof. (a) If  $ p \leq 0 $ there is nothing to prove since  $ I_p = \{0\} $. In the case  $ p \geq 1 $, it suffices to prove that if  $ v = 0 \bmod I_p $ then  $ \partial v = 0 \bmod I_{p-1} $. Since  $ v $ is a linear combination of elementary non-regular paths  $ e_{i_0...i_p} $, it suffices to prove that if  $ e_{i_0...i_p} $ is non-regular then  $ \partial e_{i_0...i_p} $ is non-regular, too. Indeed, for a non-regular path  $ i_0...i_p $ there exists an index  $ k $ such that  $ i_k = i_{k+1} $. Then we have

 $$ \begin{array}{r c l}{\partial e_{i_{0}\ldots i_{p}}}&{=}&{e_{i_{1}\ldots i_{p}}-e_{i_{0}i_{2}\ldots i_{p}}+\ldots}\\ {}&{}&{+\left(-1\right)^{k}e_{i_{0}\ldots i_{k-1}i_{k+1}i_{k+2}\ldots i_{p}}+\left(-1\right)^{k+1}e_{i_{0}\ldots i_{k-1}i_{k}i_{k+2}\ldots i_{p}}}\\ {}&{}&{+\ldots+\left(-1\right)^{p}e_{i_{0}\ldots i_{p-1}}.}\\ \end{array} $$ 

By  $ i_k = i_{k+1} $ the two terms in the middle line of (2.10) cancel out, whereas all other terms are non-regular, whence  $ \partial e_{i_0...i_p} \in I_{p-1} $.

(b) Let us first verify that if  $ u = 0 \bmod I_p $ or  $ v = 0 \bmod I_q $ then  $ uv = 0 \bmod I_{p+q+1} $. Let, for example,  $ u = 0 \bmod I_p $. If  $ p \leq 0 $ then this implies  $ u = 0 $, and the claim is trivially satisfied. If  $ p \geq 1 $ then  $ u $ is a linear combination of non-regular paths  $ e_{i_0...i_p} $. Since the join of an non-regular path with any path is obviously non-regular, we obtain that  $ uv $ is non-regular, which proves the claim.

Since

 $$ u_{1}v_{1}-u_{2}v_{2}=\left(u_{1}-u_{2}\right)v_{1}+u_{2}\left(v_{1}-v_{2}\right) $$ 

and by hypothesis

 $$ u_{1}-u_{2}=0\bmod I_{p},\quad v_{1}-v_{2}=0\bmod I_{q}, $$ 

we conclude that

 $$ u_{1}v_{1}=u_{2}v_{2}\bmod I_{p+q+1}. $$ 

Lemma 2.9 shows that the boundary operator $\partial$ and the join are well-defined on the quotient spaces $\Lambda_p/I_p = \widetilde{\mathcal{R}}_p$ through the operations with the representatives of the classes. In particular, the identity $\partial^2 = 0$ and the product rule are satisfied in the spaces $\widetilde{\mathcal{R}}_p$.

Now we define the operations $\partial$ and join on the spaces $\mathcal{R}_p$ simply as pullbacks from $\widetilde{\mathcal{R}}_p$ using the natural linear isomorphism $\mathcal{R}_p \to \widetilde{\mathcal{R}}_p$.

Definition 2.10 The operator $\partial$ on $\mathcal{R}_p$ will be called a regular boundary operator, and the join on the spaces $\mathcal{R}_p$ will be called a regular join. To distinguish them from the operations $\partial$ and join on the spaces $\Lambda_p$, the latter operations will be referred to as non-regular.

When applying the formulas for the regular boundary operator  $ \partial $ and join, one should make the following adjustments:

(I) all the components  $ v^{i_0...i_p} $ of  $ v \in \mathcal{R}_p $ for non-regular paths  $ i_0...i_p $ are equal to 0 by definition;

(II) all non-regular paths  $ e_{i_{0}\ldots i_{p}} $, should they arise as a result of an operation, are treated as zeros (because after applying the operation on representatives, we should pass in the end to a regular representative).

'I'hus, the formula (2.4) for the component  $ (\partial v)^{j_0\cdots j_{p-1}} $ is valid only for regular paths  $ j_0\cdots j_{p-1} $, while for non-regular  $ j_0\cdots j_{p-1} $ we have by definition  $ (\partial v)^{j_0\cdots j_{p-1}} = 0 $. Similarly, the formula (2.7) for  $ (uv)^{i_0\cdots i_p j_0\cdots j_q} $ is valid only for regular paths  $ i_0\cdots i_p j_0\cdots j_q $.

On the other hand, the formula (2.2) for  $ \partial e_{i_0\ldots i_p} $ and the formula (2.8) for  $ e_{i_0\ldots i_p} e_{j_0\ldots j_q} $ remain valid for all sequences of indices as it follows from Lemma 2.9, provided one applies adjustment (II).

For example, we have for the non-regular operator  $ \partial $

 $$ \partial e_{i j i}=e_{j i}-e_{i i}+e_{i j}, $$ 

whereas for the regular operator  $ \partial $

 $$ \partial e_{i j i}=e_{j i}+e_{i j} $$ 

since  $ e_{ii} $ is non-regular and, hence, is replaced by 0. For non-regular join we have

 $$ e_{ij}e_{ji}=e_{ijji} $$ 

whereas for the regular join  $ e_{ij}e_{ji} = 0 $ since  $ e_{ijji} $ is non-regular.

Consequently, we obtain the regular chain complex of the set V:

 $$ 0\leftarrow\mathbb{K}\leftarrow\mathcal{R}_{0}\leftarrow\ldots\leftarrow\mathcal{R}_{p-1}\leftarrow\mathcal{R}_{p}\leftarrow\ldots $$ 

where all the arrows are given by regular operator  $ \partial $.

Let  $ V' $ be a subset of V. Clearly, every elementary regular p-path  $ e_{i_0\ldots i_p} $ on  $ V' $ is also a regular p-path on V, so that we have a natural inclusion

 $$ \mathcal{R}_{p}\left(V^{\prime}\right)\subset\mathcal{R}_{p}\left(V\right). $$ 

By (2.2),  $ \partial e_{i_0...i_p} $ has the same expression in the both spaces  $ \mathcal{R}_p(V') $,  $ \mathcal{R}_p(V) $ so that  $ \partial $ commutes with the inclusion (2.12).

### 2.4 Form and exterior differential

For any integer $p \geq -1$, denote by $\Lambda^p = \Lambda^p(V)$ the linear space of all $\mathbb{K}$-valued functions on $V^{p+1} = \underbrace{V \times \ldots \times V}_{p+1 \text{ terms}}$. In particular, $\Lambda^0$ is the linear space of all $\mathbb{K}$-valued functions on $V$, and

 $ \Lambda^{-1} $ is the space of all  $ \mathbb{K} $-values functions on  $ V^0 := \{0\} $, that is,  $ \Lambda^{-1} $ can (and will) be identified with  $ \mathbb{K} $. Set also  $ \Lambda^{-2} = \{0\} $.

##### Definition 2.11 The elements of  $ \Lambda^{p} $ are called p-forms on V.

The value of a p-form  $ \omega $ at a point  $ (i_0, i_1, ..., i_p) \in V^{p+1} $ will be denoted by  $ \omega_{i_0 i_1 \ldots i_p} $. In particular, the value of a function  $ \omega \in \Lambda^0(V) $ at  $ i \in V $ will be denoted by  $ \omega_i $. Each element  $ \omega \in \Lambda^{-1} $ is determined by its value at 0 that will be denoted by the same letter  $ \omega $.

Denote by  $ e^{j_0 \cdots j_p} $ a p-form that takes value  $ 1_K $ at the point  $ (j_0, j_1, ..., j_p) $ and 0 at all other points. For example,  $ e^j $ is a function on  $ V $ that is equal to 1 at  $ j $ and 0 away from  $ j $. Also,  $ e $ stands for the function on  $ \{0\} $ taking value  $ 1_K $. Let us refer to  $ e^{j_0 \cdots j_p} $ as an elementary p-form. Clearly, the family  $ \{e^{j_0 \cdots j_p}\} $ of all elementary p-forms is a basis in the linear space  $ \Lambda^p $ and, for any  $ \omega \in \Lambda^p $,

 $$ \omega=\sum_{j_{0},\ldots,j_{p}\in V}\omega_{j_{0}\ldots j_{p}}e^{j_{0}\ldots j_{p}}. $$ 

We have a natural pairing of p-forms and p-paths as follows:

 $$ (\omega,v):=\sum_{i_{0},\ldots,i_{p}\in V}\omega_{i_{0}\ldots i_{p}}v^{i_{0}\ldots i_{p}} $$ 

for all  $ \omega \in \Lambda^p $ and  $ v \in \Lambda_p $. Obviously, the spaces  $ \Lambda^p $ and  $ \Lambda_p $ are dual with respect to this pairing.

#### Definition 2.12 Define the exterior differential  $ d : \Lambda^p \to \Lambda^{p+1} $ by

 $$ (d\omega)_{i_{0}\ldots i_{p+1}}=\sum_{q=0}^{p+1}(-1)^{q}\omega_{i_{0}\ldots\widehat{i_{q}\ldots i_{p+1}}}, $$ 

for any  $ \omega \in \Lambda^p $.

For example, for any  $ \omega \in \Lambda^{-1} $ we have

 $$ (d\omega)_{i}=\omega, $$ 

for any function  $ \omega \in \Lambda^0 $ we have

 $$ (d\omega)_{i j}=\omega_{j}-\omega_{i}, $$ 

for a 1-form  $ \omega $

 $$ (d\omega)_{i j k}=\omega_{j k}-\omega_{i k}+\omega_{i j}. $$ 

It follows from (2.14) that

 $$ d e^{i_{0}\ldots i_{p}}=\sum_{k\in V}\sum_{q=0}^{p+1}(-1)^{q}e^{i_{0}\ldots i_{q-1}k i_{q}\ldots i_{p}} $$ 

(cf. (2.4)). For example, we have

 $$ de=\sum_{k}e^{k}=1 $$ 

where 1 stands for the function on V with constant value  $ 1_{K} $. Also, we have

 $$ d e^{i}=\sum_{k}\left(e^{k i}-e^{i k}\right) $$ 

and

 $$ d e^{i j}=\sum_{k}\left(e^{k i j}-e^{i k j}+e^{i j k}\right). $$ 

Lemma 2.13 Let  $ p \geq -2 $. For any p-form  $ \omega $ and any  $ (p+1) $-path v the following identity holds

 $$ \left(d\omega,v\right)=\left(\omega,\partial v\right). $$ 

Consequently, the operators  $ d : \Lambda^p \to \Lambda^{p+1} $ and  $ \partial : \Lambda_{p+1} \to \Lambda_p $ are dual.

Proof. For $p = -2$ the both sides are 0. For $p \geq -1$ it suffices to prove this identity for $v = e_{i_0...i_{p+1}}$. Using (2.14) and (2.2), we obtain

 $$ (d\omega,v)=(d\omega)_{i_{0}\ldots i_{p+1}}=\sum_{q=0}^{p+1}(-1)^{q}\omega_{i_{0}\ldots\widehat{i_{q}\ldots i_{p+1}} $$ 

and

 $$ (\omega,\partial v)=\left(\omega,\sum_{q=0}^{p+1}(-1)^{q}e_{i_{0}\ldots\widehat{i_{q}}\ldots i_{p+1}}\right)=\sum_{q=0}^{p+1}(-1)^{q}\omega_{i_{0}\ldots\widehat{i_{q}}\ldots i_{p+1}}, $$ 

whence the required identity follows. ■

Corollary 2.14 We have  $ d^{2}=0 $.

Hence, we obtain a cochain complex

 $$ 0\to\mathbb{K}\to\Lambda_{0}\to\dots\to\Lambda_{p}\to\Lambda_{p+1}\to\dots $$ 

where all arrows are given by d, and this cochain complex is dual to the chain complex (2.6).

### 2.5 Concatenation of forms

Definition 2.15 For  $ p, q \geq 0 $ and for any two forms  $ \varphi \in \Lambda^p $ and  $ \psi \in \Lambda^q $, define their concatenation  $ \varphi\psi \in \Lambda^{p+q} $ by

 $$ (\varphi\psi)_{i_{0}\ldots i_{p+q}}=\varphi_{i_{0}\ldots i_{p}}\psi_{i_{p}i_{p+1}\ldots i_{p+q}}. $$ 

Clearly, concatenation is a bilinear operation that satisfies the associative law. It is obviously non-commutative. For example, if  $ \varphi $ is a function, that is,  $ p = 0 $, then  $ \varphi\psi \in \Lambda^q $ and

 $$ (\varphi\psi)_{i_{0}\dots i_{q}}=\varphi_{i_{0}}\psi_{i_{0}\dots i_{q}}, $$ 

while

 $$ (\psi\varphi)_{i_{0}\dots i_{q}}=\psi_{i_{0}\dots i_{q}}\varphi_{i_{q}}. $$ 

For the elementary forms  $ e^{i_{0}\ldots i_{p}} $ and  $ e^{j_{0}\ldots j_{q}} $ we have

 $$ e^{i_{0}\cdots i_{p}}e^{j_{0}\cdots j_{q}}=\left\{\begin{array}{l l}0,&i_{p}\neq j_{0},\\ e^{i_{0}\cdots i_{p}j_{1}\cdots i_{q}},&i_{p}=j_{0}.\end{array}\right. $$ 

The operation of concatenation is reminiscent of the operation of cup product in algebraic topology. Let us emphasize that concatenation of forms is essentially different from join of paths, which can be seen from comparison of (2.7) and (2.17): in the former the index  $ i_p $ is used twice in the right hand side whereas in the latter – only once. Consequently, concatenation acts from  $ \Lambda^p \times \Lambda^q $ to  $ \Lambda^{p+q} $, whereas join acts from  $ \Lambda_p \times \Lambda_q $ to  $ \Lambda_{p+q+1} $. Despite the differences, the both operations do satisfy the product rules with respect to the operators  $ d $ and  $ \partial $, respectively.

Lemma 2.16 For all  $ p, q \geq 0 $ and  $ \varphi \in \Lambda^p $,  $ \psi \in \Lambda^q $, we have

 $$ d\left(\varphi\psi\right)=\left(d\varphi\right)\psi+\left(-1\right)^{p}\varphi d\psi. $$ 

Proof. Denoting  $ \omega = \varphi \psi $, we have

 $$ \begin{array}{r c l}{{(d\omega)_{i_{0}\dots i_{p+q+1}}}}&{{=}}&{{\displaystyle\sum_{r=0}^{p+q+1}(-1)^{r}\omega_{i_{0}\dots\widehat{i_{r}}\dots i_{p+q+1}}}}\\ {{}}&{{=}}&{{\displaystyle\sum_{r=0}^{p}(-1)^{r}\omega_{i_{0}\dots\widehat{i_{r}}\dots i_{p+1}\dots i_{p+q+1}}+\displaystyle\sum_{r=p+1}^{p+q+1}(-1)^{r}\omega_{i_{0}\dots i_{p}\dots\widehat{i_{r}}\dots i_{p+q+1}}}}\\ {{}}&{{=}}&{{\displaystyle\sum_{r=0}^{p}(-1)^{r}\varphi_{i_{0}\dots\widehat{i_{r}}\dots i_{p+1}}\psi_{i_{p+1}\dots i_{p+q+1}}+\displaystyle\sum_{r=p+1}^{p+q+1}(-1)^{r}\varphi_{i_{0}\dots i_{p}}\psi_{i_{p}\dots\widehat{i_{r}}\dots i_{p+q+1}}.}}\end{array} $$ 

Noticing that

 $$ (d\varphi)_{i_{0}\ldots i_{p+1}}=\sum_{r=0}^{p+1}(-1)^{r}\varphi_{i_{0}\ldots\widehat{i_{r}}\ldots i_{p+1}} $$ 

and

 $$ (d\psi)_{i_{p}\ldots i_{p+q+1}}=\sum_{r=p}^{p+q+1}(-1)^{r-p}\psi_{i_{p}\ldots\widehat{i_{r}}\ldots i_{p+q+1}}, $$ 

we obtain

 $$ \begin{align*}(d\omega)_{i_0\ldots i_{p+q+1}}\quad&=\quad\left[(d\varphi)_{i_0\ldots i_{p+1}}-(-1)^{p+1}\varphi_{i_0\ldots i_p}\right]\psi_{i_{p+1}\ldots i_{p+q+1}}\\&\quad+(-1)^{p}\varphi_{i_0\ldots i_p}\left[(d\psi)_{i_{p}\ldots i_{p+q+1}}-\psi_{i_{p+1}\ldots i_{p+q+1}}\right]\\&=\quad((d\varphi)\psi)_{i_0\ldots i_{p+q+1}}+(-1)^{p}\left(\varphi d\psi\right)_{i_0\ldots i_{p+q+1}}\end{align*} $$ 

which was to be proved.

Remark 2.17 The direct sum of vector spaces

 $$ \Lambda=\bigoplus_{p\geq0}\Lambda^{p} $$ 

with the additional operation concatenation is a graded algebra over field K. It is easy to see that the constant function 1 on V is a unity of this algebra. As it follows from Lemma 2.16, the couple $(\Lambda, d)$ is a differential graded algebra.

Note that $(\Lambda, d)$ does not satisfy the minimality condition. The latter condition says that the minimal left $\Lambda^0$-module generated by $d\Lambda^p$ must coincide with $\Lambda^{p+1}$, which is not the case here. Indeed, each element of the left $\Lambda^0$-module generated by $d\Lambda^0$ is a finite some of the terms like $fdg$ where $f, g \in \Lambda^0$. For each $i \in V$, we have

 $$ \left(fdg\right)_{ii}=f_{i}\left(dg\right)_{ii}=f_{i}\left(g_{i}-g_{i}\right)=0. $$ 

Hence, the sum of such terms cannot be equal to  $ e^{ii} \in \Lambda^1 $. In Section 2.6 we will consider the spaces of regularized forms that do satisfy the minimality condition.

### 2.6 Regular forms

For any integer  $ p \geq -2 $, consider the following subspace of  $ \Lambda^p $:

 $$ \begin{align*}\mathcal{R}^p\quad&=\quad\mathcal{R}^p\left(V\right)=\mathrm{span}\left\{e^{i_{0}\dots i_p}:i_{0}\dots i_p\mathrm{is regular}\right\}\\&=\quad\left\{\omega\in\Lambda^p:\omega_{i_{0}\dots i_p}=0\mathrm{if}i_{0}\dots i_p\mathrm{is non-regular}\right\}.\end{align*} $$ 

Definition 2.18 The elements of  $ R^{p} $ are called regular p-forms.

For example, a 1-form ω belongs to  $ R^1 $ if  $ \omega_{ii} \equiv 0 $, and a 2-form ω belongs to  $ R^2 $ if  $ \omega_{iij} \equiv \omega_{jii} \equiv 0 $. For  $ p \leq 0 $ the condition  $ f \in \mathcal{R}^p $ has no additional restriction so that  $ R^p = \Lambda^p $.

The next lemma shows that the operations of exterior differentiation, concatenation and pairing can be restricted to regular forms.

Lemma 2.19 (a) If  $ \omega \in \mathcal{R}^p $ then  $ d\omega \in \mathcal{R}^{p+1} $.

(b) If  $ \varphi \in \mathcal{R}^p $ and  $ \psi \in \mathcal{R}^q $ then  $ \varphi\psi \in \mathcal{R}^{p+q} $, assuming that  $ p,q \geq 0 $.

(c) If  $ \omega \in \mathcal{R}^p $,  $ v_1, v_2 \in \Lambda_p $ and  $ v_1 = v_2 \bmod I_p $ then  $ (\omega, v_1) = (\omega, v_2) $.

Proof. (a) To prove that  $ d\omega \in \mathcal{R}^{p+1} $, we must show that

 $$ (d\omega)_{i_{0}\ldots i_{p+1}}=0 $$ 

whenever  $ i_{0}...i_{p+1} $ is non-regular, say  $ i_{k}=i_{k+1} $. We have by (2.14)

 $$ (d\omega)_{i_{0}\ldots i_{p+1}}=\sum_{q=0}^{p+1}(-1)^{q}\omega_{i_{0}\ldots\widehat{i_{q}\ldots i_{p+1}}}. $$ 

If  $ q \neq k $,  $ k + 1 $ then both  $ i_k $,  $ i_{k+1} $ are present in  $ \omega_{i_0\ldots\widehat{i_q}\ldots i_{p+1}} $ which makes this term equal to 0 since  $ \omega $ is regular. In the remaining two cases  $ q = k $ and  $ q = k + 1 $ the term  $ \omega_{i_0\ldots\widehat{i_q}\ldots i_{p+1}} $ has the same values (because the sequences  $ i_0\ldots\widehat{i_q}\ldots i_{p+1} $ are the same) but the signs  $ (-1)^q $ are opposite. Hence, they cancel out, which proves (2.20).

(b) By  $ (2.17) $, we have

 $$ (\varphi\psi)_{i_{0}\ldots i_{p+q}}=\varphi_{i_{0}\ldots i_{p}}\psi_{i_{p}\ldots i_{p+q}}. $$ 

If the sequence $i_0...i_{p+q}$ is non-regular, say $i_k = i_{k+1}$ then the both indices $i_k, i_{k+1}$ are present either in the sequence $i_0...i_p$ or in $i_{p}...i_{p+q}$, which implies that one of the terms $\varphi_{i_0...i_p}, \psi_{i_p...i_{p+q}}$ vanishes. It follows that $(\varphi\psi)_{i_k} = 0$ and, hence, $\varphi\psi \in \mathcal{R}^{p+q}$.

(c) Indeed,  $ v_1 - v_2 \in I_p $ is a linear combination of non-regular paths  $ e_{i_0...i_p} $. Since  $ (\omega, e_{i_0...i_p}) = 0 $ for non-regular paths, it follows that  $ (\omega, v_1 - v_2) = 0 $ and  $ (\omega, v_1) = (\omega, v_2) $.

It follows from 2.19(c) that the pairing $(\omega, v)$ is well defined for $\omega \in \mathcal{R}^p$ and $v \in \mathcal{R}_p$. In particular, the spaces $\mathcal{R}^p$ and $\widetilde{\mathcal{R}}_p$ are dual. It follows from Lemmas 2.9 and 2.13 that, for all $\omega \in \mathcal{R}^p$ and $v \in \widetilde{\mathcal{R}}_{p+1}$,

 $$ (d\omega,v)=(\omega,\partial v). $$ 

In particular, the operators  $ d : \mathcal{R}^p \to \mathcal{R}^{p+1} $ and  $ \partial : \widetilde{\mathcal{R}}_{p+1} \to \widetilde{\mathcal{R}}_p $ are dual. Replacing the regularized paths by their regular representatives, we obtain that the spaces  $ \mathcal{R}^p $ and  $ \mathcal{R}_p $ are dual (which is obvious directly from their definitions, though) and that the operator  $ d : \mathcal{R}^p \to \mathcal{R}^{p+1} $ is dual to the regular operator  $ \partial : \mathcal{R}_{p+1} \to \mathcal{R}_p $. In particular, we obtain the regular cochain complex of  $ V $

 $$ 0\to\mathbb{K}\to\mathcal{R}^{0}\to\dots\to\mathcal{R}^{p}\to\mathcal{R}^{p+1}\to\dots $$ 

that is dual to the regular chain complex  $ (2.11) $.

Remark 2.20 Similarly to Remark 2.17, the direct sum of vector spaces

 $$ \mathcal{R}=\bigoplus_{p\geq0}\mathcal{R}^{p} $$ 

with the operations $d$ and concatenation is a graded differential algebra over $\mathbb{K}$. This algebra does satisfy the minimality condition: the minimal left $\mathcal{R}^0$-module generated by $d\mathcal{R}^p$ coincides with $\mathcal{R}^{p+1}$; that is, any element of $\mathcal{R}^{p+1}$ is a finite sum of the terms like $fd\omega$ with $f\in\mathcal{R}^0$ and $\omega\in\mathcal{R}^p$.

Recall that there is a standard procedure of construction of the universal differential graded algebra starting with any associative unital algebra. If one starts with the algebra of all K-valued functions on V (that is  $ \mathcal{R}^0 $), then one obtains in this way exactly  $ (\mathcal{R}, d) $. The universality of  $ (\mathcal{R}, d) $ means that any minimal differential graded algebra over  $ \mathcal{R}^0 $ is a certain quotient of  $ (\mathcal{R}, d) $. The details can be found in [4] and [8].

## 3 Path complexes

### 3.1 Path complexes, simplicial complexes, digraphs

Definition 3.1 A path complex over a set V is a non-empty collection P of elementary paths on V with the following property: for any  $ n \geq 0 $,

if  $ i_0...i_n \in P $ then also the truncated paths  $ i_0...i_{n-1} $ and  $ i_1...i_n $ belong to  $ P $.

The set of $n$-paths from $P$ is denoted by $P_n$. Then a path complex $P$ can be regarded as a collection $\{P_n\}_{n=-1}^{\infty}$ satisfying (3.1). When a path complex $P$ is fixed, all the paths from $P$ are called allowed, whereas all the elementary paths that are not in $P$ are called non-allowed.

1. the set  $ P_{-1} $ consists of a single empty path  $ e $. The elements of  $ P_0 $ (that is, allowed 0-paths) are called the vertices of  $ P $. Clearly,  $ P_0 $ is a subset of  $ V $. By the property (3.1), if  $ i_0...i_n \in P $ then all  $ i_k $ are vertices. Hence, we can (and will) remove from the set  $ V $ all non-vertices so that  $ V = P_0 $. The elements of  $ P_1 $ (that is, allowed 1-paths) are called (directed) edges of  $ P $. By (3.1), if  $ i_0...i_n \in P $ then all 1-paths  $ i_{k-1}i_k $ are edges.

Example 3.2 By definition, an abstract finite simplicial complex S is a collection of subsets of a finite vertex set V that satisfies the following property:

 $$  if\sigma\in S then any subset of\sigma is also in S. $$ 

Let us enumerate the elements of V by distinct reals and identify any subset s of V with the elementary path that consists of the elements of s put in the (strictly) increasing order. Hence, we can regard S as a collection of elementary paths on V. Then the defining property of a simplex can be restated the following:

if an elementary path belongs to S then its any subsequence also belongs to S.

Consequently, the family S satisfies the property (3.1) so that S is a path complex. The allowed n-paths in S are exactly the n-simplexes.

For example, a simplicial complex on Fig. 1 has the following allowed paths (=simplexes):

0-paths: 0,...,8

1-paths: 01, 02, 03, 04, 05, 06, 07, 08, 12, 34, 35, 45, 67, 68, 78

2-paths: 012, 678, 034, 035, 045, 678

3-paths: 0345

Example 3.3 Let  $  G = (V, E)  $ be a finite digraph, where  $  V  $ is a finite set of vertices and  $  E  $ is the set of directed edges, that is,  $  E \subset V \times V  $. Equivalently, one can say that a digraph is a set  $  V  $ endowed with a binary relation  $  E  $. The fact that  $  (i, j) \in E  $ will also be denoted by  $  i \to j  $.

An elementary $n$-path $i_{0}...i_{n}$ on $V$ is called allowed if $i_{k-1} \to i_{k}$ for any $k=1,...,n$. Denote by $P_{n}=P_{n}(G)$ the set of all allowed $n$-paths. In particular, we have $P_{0}=V$ and $P_{1}=E$. Clearly, the family $\{P_{n}\}$ of all allowed paths satisfies the condition (3.1) so that $\{P_{n}\}$ is a path complex. This path complex is naturally associated with the digraph $G$ and will be denoted by $P(G)$.

For example, a digraph on Fig. 2 has the following path complex:

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//3ef4a871-5f22-4d44-81b5-82c22e7917c9/markdown_4/imgs/img_in_image_box_397_167_792_443.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A10Z%2F-1%2F%2F0fc2cb9be1708d0acf50984190804165604e3cade2a9173335d80a96761cbf7e" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 1: A simplicial complex</div> </div>


0-paths: 0,...,8

1-paths: 01, 02, 03, 04, 05, 06, 07, 08, 12, 34, 35, 45, 67, 68, 78

2-paths: 012, 678, 034, 035, 045, 067, 068, 678

3-paths: 0345, 0678

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//3ef4a871-5f22-4d44-81b5-82c22e7917c9/markdown_4/imgs/img_in_image_box_396_759_792_1035.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A11Z%2F-1%2F%2Fecbdfdcb0c24a4b9c597a9b33565535b1a036872b1dbed2fb612555e707323e0" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 2: A digraph</div> </div>


The path complexes of digraphs are the central objects of this paper. Although most of the results are proved for arbitrary path complexes, we always have in mind possible applications to digraphs. On the other hand, the notion of a path complex provides an alternative approach to the classical results about simplicial complexes.

It is easy to see that a path complex arises from a digraph if and only if it satisfies the following additional condition: if in a path  $ i_0...i_n $ all pairs  $ i_{k-1}i_k $ are allowed then the whole path  $ i_0...i_n $ is allowed.

Let us describe explicitly those path complexes that arise from simplicial complexes.

Definition 3.4 We say that a path complex P is perfect, if any subsequence of any allowed elementary path of P is also an allowed path.

Definition 3.5 We say that a path complex P is monotone, if there is an injective real-valued function on the vertex set of P that is strictly monotone increasing along any path from P.

Proposition 3.6 A path complex P is the path complex of a simplicial complex if and only if it is perfect and monotone.

Proof. The path complex of a simplicial complex is both perfect and monotone by definition. Let us prove the converse. By the monotonicity condition, the vertices in any path  $ i_0...i_n \in P $ are all distinct. Hence, with any path  $ i_0...i_n \in P $ we can associate a simplex  $ [i_0, ..., i_n] $; denote by  $ S $ the collection of all such simplexes. Then the perfectness of  $ P $ implies that  $ S $ is a simplicial complex. Ordering the vertex set of  $ S $ using the monotone function from the monotonicity condition, we see that each simplex from  $ S $ gives back a path from  $ P $. ■

Observe that the path complex of a digraph  $  G = (V, E)  $ is perfect if and only if the edge relation  $ \rightarrow $ is transitive, that is, if

 $$ i\rightarrow j\rightarrow k\Rightarrow i\rightarrow k. $$ 

In particular, this condition holds for posets (=partially ordered sets). Indeed, by definition a poset is a digraph G where the edge relation ▣ is reflexive, antisymmetric and transitive. Hence, the path complex of a poset is perfect, but satisfies also the following additional properties: all 1-paths ii are allowed, while 2-paths iji with  $ i \neq j $ are non-allowed.

It is easy to see that the path complex of a digraph $G$ is monotone if there is a function $\Phi: V \to \mathbb{R}$ such that

 $$ i\to j\Rightarrow\Phi\left(i\right)<\Phi\left(j\right). $$ 

For example, the path complex of the digraph on Fig. 2 is both monotone and perfect.

The path complex of a poset is not monotone as it has allowed 1-paths ii. However, if we reduce the set of edges on a poset by removing all loops  $ i \to i $, then the resulting digraph is perfect and monotone.

### 3.2 Allowed paths

Given an arbitrary path complex  $ P = \{P_n\}_{n=0}^\infty $ with a finite vertex set  $ V $, consider for any integer  $ n \geq -1 $ the  $ \mathbb{K} $-linear space  $ \mathcal{A}_n $ that is spanned by all the elementary  $ n $-paths from  $ P $, that is

 $$ \mathcal{A}_{n}=\mathcal{A}_{n}\left(P\right)=\left\{\sum_{i_{0},\ldots,i_{n}\in V}v^{i_{0}\ldots i_{n}}e_{i_{0}\ldots i_{n}}:i_{0}\ldots i_{n}\in P_{n},v^{i_{0}\ldots i_{n}}\in\mathbb{K}\right\}. $$ 

By construction,  $ A_n $ is a subspace of the space  $ \Lambda_n $ defined in Section 2.1. For example,  $ A_0 $ is spanned by all vertexes of  $ P $ so that  $ A_0 = \Lambda_0 $. The space  $ A_1 $ is spanned by all edges of  $ P $ and can be smaller than  $ \Lambda_1 $. It is clear that  $ A_{-1} \cong \mathbb{K} $. Set also  $ A_{-2} = \{0\} $.

Definition 3.7 The elements of  $ A_{n} $ are called allowed n-paths.

We would like to restrict the boundary operator  $ \partial $ on the spaces  $ \Lambda_n $ to the spaces  $ \mathcal{A}_n $. For some path complexes it can happen that

 $$ \partial\mathcal{A}_{n}\subset\mathcal{A}_{n-1}, $$ 

so that the restriction is straightforward. If it is not the case then an additional construction is needed as will be explained below. Let us describe first the setting when the inclusion (3.4)

takes place. Namely, let us show that for a perfect path complex the inclusion (3.4) takes places. For  $ n \leq 1 $ this is obvious as  $ \mathcal{A}_{n-1} = \Lambda_{n-1} $. Assuming  $ n \geq 2 $, let us show that if  $ e_{i_0...i_n} $ is allowed then  $ \partial e_{i_0...i_n} $ is also allowed. Indeed, we have by (2.2)

 $$ \partial e_{i_{0}\ldots i_{n}}=\sum_{q=0}^{n}(-1)^{q}e_{i_{0}\ldots\widehat{i_{q}\ldots i_{n}}}, $$ 

where all the terms  $ e_{i_0\ldots i_q\ldots i_n} $ in the right hand side are allowed because of the perfectness. Hence, (3.4) follows. Consequently, we obtain a chain complex

 $$ 0\leftarrow\mathbb{K}\leftarrow\mathcal{A}_{0}\leftarrow\ldots\leftarrow\mathcal{A}_{n-1}\leftarrow\mathcal{A}_{n}\leftarrow\ldots $$ 

Its homology groups are denoted by  $ \tilde{H}_{\bullet}(P) $ are referred to as the reduced path homologies of P. Consider also the truncated complex

 $$ 0\leftarrow\mathcal{A}_{0}\leftarrow\ldots\leftarrow\mathcal{A}_{n-1}\leftarrow\mathcal{A}_{n}\leftarrow\ldots $$ 

whose homology groups are denoted by  $ H_{\bullet}(P) $ and are referred to as the path homologies of  $ P $ (in the latter case the operator  $ \partial $ on  $ A_0 $ is set to be zero).

If P is the path complex of a simplicial complex S, then the boundary operator (3.5) matches the classical boundary operator on simplexes:

 $$ \partial\left[i_{0},...,i_{n}\right]=\sum_{q=0}^{n}(-1)^{q}\left[i_{0},...,\widehat{i_{q}},...i_{n}\right]. $$ 

In this case, (3.7) coincides with the classical chain complex of a simplicial complex, and the path homologies $H_{\bullet}(P)$ are identical to the simplicial homologies $H_{\bullet}(S)$.

If $P$ is a path complex of a digraph $G$, satisfying the transitivity condition (3.3) then $P$ is perfect and, hence, its homology groups are defined as above. In this case we denote them also by $H_{\bullet}(G)$.

Example 3.8 Let S be a finite simplicial complex. Consider the digraph G whose set of vertices is S, while the edges are defined as follows: if s, t are simplexes from S, then

 $$ s\rightarrow t\Leftrightarrow s\supset t and s\neq t. $$ 

Clearly, the graph $G$ satisfies the transitivity condition (3.3) so that the path complex $P = P(G)$ of the digraph $G$ is perfect. Let us prove that $H_n(G) \cong H_n(S)$ for all $n \geq 0$.

Let us first show that the path complex $P$ is monotone. For that, enumerate the vertices of $S$ by numbers $1,2,2^2,2^3,\ldots$ and assign to each simplicial complex $s\in S$ (that is, to a vertex of $G$) the sum of the numbers of all its vertices. The resulting function on $G$ is injective and strictly monotone decreasing along each edge and, hence, along any allowed path. By Lemma 3.6 the path complex $P$ arises from a simplicial complex.

It is easy to see that the latter simplicial complex is nothing else but the barycentric subdivision  $ B(S) $ of  $ S $ (cf. Fig. 3).

Indeed, any allowed path  $ s_{0}...s_{n} $ on the digraph  $ G $ consists of a sequence of simplexes from  $ S $ such that  $ s_{k} $ is a face of  $ s_{k-1} $. If each simplex  $ s_{k} $ in this path is replaced by its barycenter  $ b(s_{k}) $ (assuming that the simplicial complex  $ S $ is geometrically realized in a higher dimensional space  $ \mathbb{R}^{N} $) then the sequence  $ \{b(s_{k})\}_{k=0}^{n} $ forms a  $ n $-simplex of the barycentric subdivision  $ B(S) $ of  $ S $. Converse is obviously also true. Hence, the path complex  $ P $ of the digraph  $ G $ coincides with the path complex of the simplicial complex  $ B(S) $. It follows that

 $$ H_{\bullet}\left(G\right)=H_{\bullet}\left(P\right)=H_{\bullet}\left(B\left(S\right)\right). $$ 

The proof is finished by citing a classical result that  $ H_{\bullet}(B(S)) \cong H_{\bullet}(S) $.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//15416160-1c91-4710-88e0-bec8591d990c/markdown_2/imgs/img_in_image_box_187_156_990_422.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A10Z%2F-1%2F%2F73dc19ec46e08a4af6e0475814f4f81bb9af1611a464a0476873cadbdcdef390" alt="Image" width="65%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 3: Simplicial complex S and the digraph G</div> </div>


### 3.3  $ \partial $-invariant paths

Now consider a general case when  $ \partial A_{n} $ does not have to be a subspace of  $ A_{n-1} $. Consider first a simple example.

Example 3.9 Consider the digraph  $  G = (V, E)  $ as on the diagram

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//15416160-1c91-4710-88e0-bec8591d990c/markdown_2/imgs/img_in_image_box_535_701_656_761.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A10Z%2F-1%2F%2F0b610ebf832117fd48bf23d01c4f2bef0850658424c337e6dedb42d1b59c0389" alt="Image" width="9%" /></div>


that is $V = \{0,1,2\}$ and $E = \{01,12\}$ . Then the 2-path $e_{012}$ is allowed, while

 $$ \partial e_{012}=e_{12}-e_{02}+e_{01} $$ 

is non-allowed because  $ e_{02} $ is non-allowed.

For any  $ n \geq -1 $ consider the following subspaces of  $ A_n $:

 $$ \Omega_{n}=\Omega_{n}\left(P\right)=\left\{v\in\mathcal{A}_{n}:\partial v\in\mathcal{A}_{n-1}\right\}. $$ 

For example, we have:

•  $ \Omega_{-1} = \mathcal{A}_{-1} = \mathbb{K}; $

•  $ \Omega_0 = \mathcal{A}_0 $ is the space of linear combinations of all the vertices of  $ P $;

-  $ \Omega_1 = \mathcal{A}_1 $ is the space of linear combinations of all the edges of  $ P $ (indeed,  $ \partial e_{ij} = e_j - e_i $ is always in  $ \mathcal{A}_0 $).

The spaces  $ \Omega_n $ with  $ n \geq 2 $ can actually be smaller than  $ \mathcal{A}_n $ as will be seen from many examples in the subsequent sections. We claim that always

 $$ \partial\Omega_{n}\subset\Omega_{n-1}. $$ 

Indeed, if  $ v \in \Omega_n $ then  $ \partial v \in \mathcal{A}_{n-1} $ and  $ \partial (\partial v) = 0 \in \mathcal{A}_{n-2} $ whence it follows that  $ \partial v \in \Omega_{n-1} $, which was to be proved.

Definition 3.10 The elements of  $ \Omega_{n} $ are called  $ \partial $-invariant n-paths.

Thus, we obtain the chain complex of  $ \partial $-invariant paths:

 $$ 0\leftarrow\mathbb{K}\leftarrow\Omega_{0}\leftarrow\ldots\leftarrow\Omega_{n-1}\leftarrow\Omega_{n}\leftarrow\Omega_{n+1}\leftarrow\ldots $$ 

where all arrows are given by  $ \partial $. We consider also its truncated version

 $$ 0\leftarrow\Omega_{0}\leftarrow\ldots\leftarrow\Omega_{n-1}\leftarrow\Omega_{n}\leftarrow\Omega_{n+1}\leftarrow\ldots $$ 

where the definition of the boundary operator $\partial$ on $\Omega_0$ is modified by setting $\partial \equiv 0$. We refer to this modification of $\partial$ as a truncated boundary operator. Note that this modification does not affect $\partial$ on $\Omega_n$ with $n \geq 1$.

There is a different kind of modification of the above procedure as follows.

Definition 3.11 A path complex P is called regular if it contains no 1-path of the form ii.

Equivalently, $P$ is regular if all the paths $i_0\ldots i_n \in P$ are regular$^1$. For example, the path complex of a simplicial complex is always regular as all the vertices in any allowed elementary path are distinct. The path complex of a digraph is regular if and only if the digraph is loopless, that is, if the 1-paths $ii$ are not edges.

for a regular path complex the above construction of the spaces  $ \Omega_n $ allows the following variation. As the space  $ \mathcal{A}_n $ of allowed  $ n $-path is in this case a subspace of the space  $ \mathcal{R}_n $ of regular  $ n $-paths, we can replace in (3.8) a non-regular boundary operator  $ \partial $ on  $ \Lambda_n $ by a regular boundary operator on  $ \mathcal{R}_n $ as described in Section 2.3. The resulting space  $ \Omega_n $ will be referred to as a regular space of  $ \partial $-invariant paths. Hence, if the path complex  $ P $ is regular then we can consider also regular versions of the chain complexes (3.9) and (3.10).

The both chain complexes (3.9) and (3.10) (regular and non-regular versions) are denoted shortly by  $ \Omega_{\bullet}(P) $ and are referred to as the chain complex of the path complex  $ P $. In order not to overload the notation, we do not reflect the variations in definition in the notation  $ \Omega_{\bullet}(P) $. However, whenever using it, one should specify which of four possible versions (regular versus non-regular and truncated versus full) is being considered.

Definition 3.12 The homology groups of the truncated complex (3.10) are referred to as the path homology groups of the path complex P and are denoted by  $ H_n(P), n \geq 0 $. The homology groups of the complex (3.9) are called the reduced path homology groups of P and are denoted by  $ \widetilde{H}_n(P), n \geq -1 $.

Note that for a regular path complex $P$ the both homologies $H_{\bullet}(P)$ and $\tilde{H}_{\bullet}(P)$ admit regular and non-regular versions.

Hence, by definition we have for any  $ n \geq 0 $

 $$ H_{n}\left(P\right)=H_{n}\left(\Omega_{\bullet}\left(P\right)\right)=\ker\partial|_{\Omega_{n}}\left/\mathrm{I m}\partial\right|_{\Omega_{n+1}}, $$ 

so that $H_n(P)$ are linear spaces over $\mathbb{K}$. Recall that the paths of ker $\partial_{\Omega_n}$ are called closed, and the paths from $\operatorname{Im}\partial_{\Omega_{n+1}} - \operatorname{exact}$.

The reduced homologies  $ \bar{H}_{n}(P) $ are defined similarly for all  $ n \geq -1 $. We clearly have

 $$ \tilde{H}_{n}\left(P\right)=H_{n}\left(P\right)\quad for all n\geq1 $$ 

and  $ \widetilde{H}_{-1}(P) = \{0\} $. To describe  $ \widetilde{H}_{0}(P) $ observe that the pairing  $ (1, v) $ between 0-form 1 (=the constant function on V that is equal to  $ 1_{K} $ at all vertices) and 0-path v is extended to  $ (1, h) $ for any homology class  $ h \in H_{0}(P) $ because for any exact path  $ v = \partial u $ we have  $ (1, v) = (1, \partial u) = (d1, u) = 0 $. Then we have

 $$ \tilde{H}_{0}\left(P\right)=\left\{h\in H_{0}\left(P\right):\left(1,h\right)=0\right\} $$ 

and, in particular,

 $$ \dim\widetilde{H}_{0}\left(P\right)=\dim H_{0}\left(P\right)-1. $$ 

If the path complex $P$ is perfect then we obtain $\Omega_n(P) = \mathcal{A}_n(P)$ for all $n$ (in this case there is no difference between regular and non-regular versions). Hence, in this case the chain complex (3.9) is identical to (3.6), and (3.10) is identical to (3.7).

If  $ P(G) $ is the path complex of a digraph G then we use the notation

 $$ \Omega_{n}\left(G\right):=\Omega_{n}\left(P\left(G\right)\right). $$ 

The corresponding homology groups will be denoted by  $ H_{n}(G) $,  $ H(G) $ and are referred to as the path homologies of the digraph G.

Since the chain complex (3.10) is finite dimensional, the following identity always takes places:

 $$ \dim H_{n}=\dim\Omega_{n}-\dim\partial\Omega_{n}-\dim\partial\Omega_{n+1} $$ 

as it follows from (3.11) and the rank-nullity theorem (a similar identity holds also for reduced homologies). The Euler characteristic of the path complex is defined by

 $$ \chi\left(P\right)=\sum_{p=0}^{n}\left(-1\right)^{p}\dim H_{p}\left(P\right) $$ 

provided n is so big that

 $$ \dim H_{p}\left(P\right)=0for all p>n. $$ 

There are examples showing that the condition (3.15) is not always fulfilled. In the latter case  $ \chi(P) $ is not defined. For a regular path complex P there is a regular and non-regular versions of  $ \chi(P) $ that do not have to match.

If  $ \dim\Omega_{p}=0 $ for  $ p>n $, then it follows from (3.13) that

 $$ \chi\left(P\right)=\sum_{p=0}^{n}\left(-1\right)^{p}\dim\Omega_{p}\left(P\right). $$ 

The definition (3.14) has an advantage that it may work even when dim Ωp > 0 for all p.

Sometimes it is useful to be able to determine the homology groups  $ H_n $ directly via the spaces  $ A_n $, without  $ \Omega_n $, as in the next statement.

Proposition 3.13 We have

 $$ H_{n}=\ker\partial|_{\mathcal{A}_{n}}/(\mathcal{A}_{n}\cap\partial\mathcal{A}_{n+1}) $$ 

and

 $$ \dim H_{n}=\dim\mathcal{A}_{n}-\dim\partial\mathcal{A}_{n}-\dim\left(\mathcal{A}_{n}\cap\partial\mathcal{A}_{n+1}\right). $$ 

Proof. Observe first that

 $$ \ker\partial|_{\mathcal{A}_{n}}=\ker\partial|_{\Omega_{n}} $$ 

because v ∈ A n and ∂v = 0 imply v ∈ Ω n. Next, it follows from the definition of Ω n+1 that

 $$ u\in\partial\Omega_{n+1}\Leftrightarrow u\in\mathcal{A}_{n}\mathrm{~a n d~}u=\partial v\mathrm{~f o r~s o m e~}v\in\mathcal{A}_{n+1}, $$ 

which is equivalent to

 $$ \partial\Omega_{n+1}=\mathcal{A}_{n}\cap\partial\mathcal{A}_{n+1}. $$ 

Then (3.17) follows from (3.11). Finally, (3.18) follows from (3.17) and the rank-nullity theorem.

Let us present a simple example showing a distinction between regular and non-regular versions of  $ \Omega_{\bullet}(P) $ and  $ H_{\bullet}(P) $. For the rest of this section we use the superscript  $ ^{reg} $ to refer to all regular notions. For example,  $ \partial^{reg} $ will denote the regular boundary operator on the spaces  $ R_n $, and  $ \Omega_n^{reg} $ will denote the space of regular  $ \partial $-invariant paths, that is,

 $$ \Omega_{n}^{r e g}=\left\{v\in\mathcal{A}_{n}:\partial^{r e g}v\in\mathcal{A}_{n-1}\right\}. $$ 

Example 3.14 Consider the digraph  $ 0 \bullet \longleftrightarrow \bullet^1 $ with  $ V = \{0,1\} $ and  $ E = \{01,10\} $, and let  $ P $ be its path complex, that is,

 $$ P=\left\{0,1,01,10,010,101,\ldots\right\}. $$ 

Clearly, P is regular. The spaces $\{A_n\}$ of allowed paths are as follows:

 $$ \begin{aligned}\mathcal{A}_{0}\quad&=\quad span\left\{e_{0},e_{1}\right\}\\\mathcal{A}_{1}\quad&=\quad span\left\{e_{01},e_{10}\right\}\\\mathcal{A}_{2}\quad&=\quad span\left\{e_{010},e_{101}\right\}\\\mathcal{A}_{3}\quad&=\quad span\left\{e_{0101},e_{1010}\right\}\end{aligned} $$ 

etc. Then we have  $ \Omega_0 = \mathcal{A}_0 $,  $ \Omega_1 = \mathcal{A}_1 $ whereas all non-regular spaces  $ \Omega_n $ with  $ n \geq 2 $ are trivial. Indeed, consider, for example,

 $$ \Omega_{2}=\left\{v\in\mathcal{A}_{2}:\partial v\in\mathcal{A}_{1}\right\}. $$ 

We have

 $$ \begin{aligned}\partial e_{010}&=e_{10}-e_{00}+e_{01},\\\partial e_{101}&=e_{01}-e_{11}+e_{10}.\end{aligned} $$ 

Since  $ e_{00} $ and  $ e_{11} $ are non-allowed, the only allowed linear combination of  $ e_{010} $ and  $ e_{101} $ is zero. Hence,  $ \Omega_2 = \{0\} $. In the same way also  $ \Omega_n = \{0\} $ for all  $ n \geq 2 $.

It is easy to see that

 $$ \partial\Omega_{1}=\mathrm{s p a n}\left\{e_{1}-e_{0}\right\}, $$ 

while  $ \partial\Omega_{n}=\{0\} $ for all  $ n\neq1 $. Hence, we obtain by (3.13)

 $$ \begin{aligned}\dim H_{0}\quad&=\quad\dim\Omega_{0}-\dim\partial\Omega_{0}-\dim\partial\Omega_{1}=2-0-1=1\\\dim H_{1}\quad&=\quad\dim\Omega_{1}-\dim\partial\Omega_{1}-\dim\partial\Omega_{2}=2-1-0=1\end{aligned} $$ 

and  $ \dim H_n = 0 $ for all  $ n \geq 2 $. Note that  $ \dim H_n $ can also be computed using (3.18). One can also show that

 $$ H_{0}\cong\operatorname{s p a n}\left\{e_{0}+e_{1}\right\}\quad\mathrm{a n d}\quad H_{1}\cong\operatorname{s p a n}\left\{e_{01}+e_{10}\right\}. $$ 

The spanning 1-path  $ e_{01} + e_{10} $ of  $ H_{1} $ can be regarded as a kind of “hole” in the digraph. The non-regular Euler characteristic is

 $$ \chi=\dim H_{0}-\dim H_{1}=0. $$ 

Consider now regular spaces  $ \Omega_n^{reg} $. The spaces  $ \Omega_0^{reg} $ and  $ \Omega_1^{reg} $ are the same as  $ \Omega_0 $ and  $ \Omega_1 $, respectively. However, the formulas (3.20) for the case of the regular operator  $ \partial^{reg} $ should be modified as follows:

 $$ \begin{aligned}\partial^{reg}e_{010}&=e_{10}+e_{01}\\\partial^{reg}e_{101}&=e_{01}+e_{10}\end{aligned} $$ 

where we have replaced the non-regular 1-paths  $ e_{00} $ and  $ e_{11} $ by 0. It follows that both  $ \partial e_{010} $ and  $ \partial e_{101} $ belong to  $ A_1 $ whence both  $ e_{010} $ and  $ e_{101} $ belong to  $ \Omega_2^{reg} $. Hence, in this case  $ \Omega_2^{reg} = A_2 $. Similarly, one can verify that  $ \Omega_n^{reg} = A_n $ for all  $ n \geq 2 $.

It is easy to see that  $ \partial\Omega_{1}^{reg} = \partial\Omega_{1} $, while

 $$ \begin{array}{r l r}{\partial\Omega_{2}^{r e g}}&{{}=}&{\mathrm{s p a n}\left\{e_{01}+e_{10}\right\}}\end{array} $$ 

 $$ \begin{array}{r l r}{\partial\Omega_{3}^{r e g}}&{{}=}&{\mathrm{s p a n}\left\{e_{010}-e_{101}\right\}}\end{array} $$ 

etc. We obtain  $ \dim H_{0}^{reg} = 1 $ as in non-regular case, while

 $$ \dim H_{1}^{r e g}=\dim\Omega_{1}^{r e g}-\dim\partial\Omega_{1}^{r e g}-\dim\partial\Omega_{2}^{r e g}=2-1-1=0 $$ 

and in the same way $\dim H_n^{reg} = 0$ for all $n \geq 1$. Hence, the regular homologies do not see the “hole” $e_{01} + e_{10}$. The regular Euler characteristic is $\chi^{reg} = 1$.

Of course, it is a matter of convention whether a two-way path  $ e_{01} + e_{10} $ should qualify as a “hole”. We are inclined to think that it should not. For this and for other reasons, in the subsequent sections of this paper we deal mostly with regular homologies unless otherwise mentioned.

To finish the discussion “regular versus non-regular”, let us provide a condition ensuring the identity  $ \Omega_n = \Omega_n^{reg} $.

Definition 3.15 We say that a path complex P is strictly regular if it is regular and contains no path of the form  $ ij\dot{i} $.

Note that the path complex of a simplicial complex is always strictly regular because the sequences of indices in allowed paths are strictly increasing. The path complex of a digraph is strictly regular if and only if the digraph is loopless (that is, ii is never an edge) and contains no two-way edges (that is,  $ i \rightarrow j $ implies  $ j \nrightarrow i $). Clearly, the path complex (3.19) is regular but not strictly regular.

Proposition 3.16 Let P be a regular path complex.

(a) For all  $ n \geq -1 $ we have  $ \Omega_n \subset \Omega_n^{reg} $.

(b) If P is strictly regular then  $ \Omega_{n} = \Omega_{n}^{reg} $ for all  $ n \geq -1 $.

(c) If  $ \Omega_2 = \Omega_2^{reg} $ then  $ P $ is strictly regular.

Proof. (a) By (3.8) if  $ v \in \Omega_n $ then  $ v \in \mathcal{A}_n $ and  $ \partial v \in \mathcal{A}_{n-1} $. Recall that  $ \partial^{reg} v $ is obtained from  $ \partial v $ by removing all the components  $ e_{i_0 \ldots i_{n-1}} $ with non-regular  $ i_0 \ldots i_{n-1} $. However, if  $ \partial v \in \mathcal{A}_{n-1} $ then  $ \partial v $ is allowed and, hence, has no non-regular component. Therefore,  $ \partial^{reg} v = \partial v $ whence  $ v \in \Omega_n^{reg} $, which proves the inclusion  $ \Omega_n \subset \Omega_n^{reg} $.

(b) Let us prove the opposite inclusion for the case of strictly regular $P$. It suffices to show that if $v \in \Omega_n^{reg}$ then $\partial^{reg}v = \partial v$. Suppose this is not the case, that is, $\partial v$ contains a non-regular component. All the components of $\partial v$ comes from differentiating of the components of $v$. If $e_{i_0\ldots i_n}$ is one of the components of $v$ then $\partial e_{i_0\ldots i_n}$ consists of the terms of the form $e_{i_0\ldots\widehat{i}_k\ldots i_n}$ with an omitted index $i_k$. Since $i_0\ldots i_n$ is allowed and, hence, regular, the only way $e_{i_0\ldots\widehat{i}_k\ldots i_n}$ can be non-regular if $i_{k-1} = i_{k+1}$. However, the path $i_{k-1}i_k i_{k+1}$ is allowed, and by the strict regularity the identity $i_{k-1} = i_{k+1}$ is not possible. Hence, $\partial v$ cannot contain non-regular terms, which proves that $\partial v = \partial^{reg}v$ and, hence, $\Omega_n = \Omega_n^{reg}$.

(c) Assume from the contrary that $P$ is not strictly regular, that is, $P$ contains a path $iji$ for some $i,j \in V$. Since

 $$ \begin{array}{r l r}{\partial e_{i j i}}&{{}=}&{e_{j i}-e_{i i}+e_{i j}}\end{array} $$ 

 $$ \begin{array}{r l r}{\partial^{r e g}e_{i j i}}&{{}=}&{e_{j i}+e_{i j}}\end{array} $$ 

we see that  $ \partial^{reg}e_{iji} \in \mathcal{A}_2 $ whereas  $ \partial e_{iji} \notin \mathcal{A}_2 $. It follows that  $ e_{iji} \in \Omega_2^{reg} \setminus \Omega_2 $, which contradicts the hypothesis. ■

### 3.4 d-invariant forms

Given a (regular or non-regular) chain complex  $ \Omega_{\bullet} $ of a path complex  $ P $, we define here the dual cochain complex  $ \Omega^{\bullet} $ of forms and the exterior differential  $ d $ on forms.

Denote by  $ \mathcal{N}^n $ the subspace of  $ \Lambda^n $, spanned by the non-allowed elementary n-forms, that is,

 $$ \begin{align*}\mathcal{N}^n\quad&=\quad\operatorname{span}\left\{e^{i_0\ldots i_n}:i_0\ldots i_n\ \mathrm{is\ non-allowed}\right\}\\&=\quad\left\{\omega\in\Lambda^n:\omega_{i_0\ldots i_n}=0\ \mathrm{for\ all\ allowed}\ i_0\ldots i_n\right\}.\end{align*} $$ 

The elements of  $ N^{n} $ are referred to as non-allowed n-forms. Then set

 $$ \mathcal{J}^{n}=\mathcal{N}^{n}+d\mathcal{N}^{n-1}, $$ 

and

 $$ \Omega^{n}=\Omega^{n}\left(P\right)=\Lambda^{n}/\mathcal{J}^{n}. $$ 

Denoting by  $ \mathcal{A}^n $ the subspace of  $ \Lambda^n $ spanned by allowed elementary  $ n $-forms and noticing that  $ \Lambda^n = \mathcal{A}^n \oplus \mathcal{N}^n $, we obtain that

 $$ \Omega^{n}\cong\mathcal{A}^{n}/(\mathcal{A}^{n}\cap\mathcal{J}^{n})\;. $$ 

Lemma 3.17 (a) If  $ \omega \in \mathcal{J}^n $ then  $ d\omega \in \mathcal{J}^{n+1} $. Consequently, d is well defined on spaces  $ \Omega^n $ (b) If  $ \omega \in \mathcal{J}^n $ then  $ (\omega, v) = 0 $ for all  $ v \in \Omega_n $.

Proof. (a) Since  $ d^{2}=0 $, it follows from (3.21) that

 $$ d\mathcal{J}^{n}\subset d\mathcal{N}^{n}+d^{2}\mathcal{N}^{n-1}=d\mathcal{N}^{n}\subset\mathcal{J}^{n+1}. $$ 

Hence, if  $ \omega_1 = \omega_2 \bmod \mathcal{J}^n $ then  $ d\omega_1 = d\omega_2 \bmod \mathcal{J}^n $ so that  $ d $ is well-defined on the cosets  $ \omega \bmod \mathcal{J}^n $ that are the elements of the quotient space  $ \Lambda^n / \mathcal{J}^n = \Omega^n $.

Proof. (b) By (3.21)  $ \omega = \varphi + d\psi $ where  $ \varphi \in \mathcal{N}^n $ and  $ \psi \in \mathcal{N}^{n-1} $. Note that  $ \varphi \in \mathcal{N}^n $ and  $ v \in \mathcal{A}_n $ imply that

 $$ (\varphi,v)=\sum\varphi_{i_{0}\ldots i_{n}}v^{i_{0}\ldots i_{n}}=0 $$ 

because if  $ i_{0}...i_{n} $ is allowed then  $ \varphi_{i_{0}...i_{n}} = 0 $ while for non-allowed  $ i_{0}...i_{n} $ we have  $ v^{i_{0}...i_{n}} = 0 $. Next, we have

 $$ (d\psi,v)=(\psi,d v)=0 $$ 

because  $ \psi \in \mathcal{N}^{n-1} $ and  $ \partial v \in \mathcal{A}_{n-1} $. Hence, combining these two lines, we conclude  $ (\omega, v) = 0 $.

Definition 3.18 The elements of the dual space  $ \Omega^n $ are called  $ d $-invariant  $ n $-forms of the path complex  $ P $, and the operator  $ d : \Omega^n \to \Omega^{n+1} $ is called the exterior differential.

By Lemma 3.17(b), any element ω mod J n of Ω n determines a linear functional on Ω n by

 $$ (\omega\bmod J^{n},v)=(\omega,v). $$ 

Hence, we obtain a mapping

 $$ \Omega^{n}\rightarrow(\Omega_{n})^{\prime} $$ 

where  $ \left(\Omega_{n}\right)^{\prime} $ is the dual space to  $ \Omega_{n} $.

Lemma 3.19 The mapping (3.24) is a linear isomorphism, that is,  $ \Omega^n $ can be identified as a dual space of  $ \Omega_n $.

Proof. Every linear functions on $\Omega_n$ can be extended to that on $\Lambda_n$ and, hence, is given by $v \mapsto (\omega, v)$ for some $\omega \in \Lambda^n$. Therefore, it is determined also by $\omega \bmod J^n \in \Omega^n$, which means that the mapping (3.24) is surjective. To prove the injectivity of (3.24) is suffices to show that $\dim \Omega^n = \dim \Omega_n$. For that, let us first show that

 $$ \Omega_{n}=(\mathcal{J}^{n})^{\perp}, $$ 

where  $ (\mathcal{J}^n)^\perp $ denotes the annihilator in  $ \Lambda_n $ of  $ \mathcal{J}^n $ as a subspace of  $ \Lambda^n $. Indeed, for  $ v \in \Lambda_n $ the condition  $ v \in (\mathcal{J}^n)^\perp $ means that

 $$ v\perp\mathcal{N}^{n}\quad\mathrm{a n d}\quad v\perp d\mathcal{N}^{n-1}. $$ 

The first condition here is equivalent to  $ v \in (\mathcal{N}^n)^\perp = \mathcal{A}_n $ while the second condition is equivalent to

 $$ \left(d\omega,v\right)=0\forall\omega\in\mathcal{N}^{n-1}\Leftrightarrow\left(\omega,\partial v\right)=0\forall\omega\in\mathcal{N}^{n-1}\Leftrightarrow\partial v\bot\mathcal{N}^{n-1}\Leftrightarrow\partial v\in\left(\mathcal{N}^{n-1}\right)^{\perp}, $$ 

that is, to  $ \partial v \in \mathcal{A}_{n-1} $. We are left to recall that  $ v \in \mathcal{A}_n $ and  $ \partial v \in \mathcal{A}_{n-1} $ is equivalent to  $ v \in \Omega_n $, which proves (3.25).

Finally, we obtain

 $$ \dim\Omega_{n}=\dim\left(\mathcal{J}^{n}\right)^{\perp}=\dim\Lambda^{n}-\dim\mathcal{J}^{n}=\dim\Lambda^{n}/\mathcal{J}^{n}=\dim\Omega^{n}, $$ 

which finishes the proof. ■

It follows that the operators $\partial : \Omega_{n+1} \to \Omega_n$ and $d : \Omega^n \to \Omega^{n+1}$ are dual, that is, for any $v \in \Omega_{n+1}$ and $\omega \in \Omega^n$

 $$ \left(d\omega,v\right)=\left(\omega,\partial v\right). $$ 

because this identity is true for any representative of ω in Λn.

We obtain a cochain complex  $ \Omega^{\bullet}(P) $ of P, that is,

 $$ 0\to\mathbb{K}\to\Omega^{0}\to\cdots\to\Omega^{n}\to\Omega^{n+1}\to\cdots $$ 

where all arrows are given by $d$. Its cohomologies are referred to as reduced path cohomologies of $P$ and are denoted by $\tilde{H}^{\bullet}(P)$, that is

 $$ \tilde{H}^{n}\left(P\right)=H^{n}\left(\Omega^{\bullet}\left(P\right)\right)=\ker d|_{\Omega^{n}}\left/\operatorname{I m}d\right|_{\Omega^{n-1}}, $$ 

for any  $ n \geq -1 $. It follows from the construction that  $ H_n(P) $ and  $ \bar{H}^n(P) $ are dual vector spaces over  $ \mathbb{K} $, in particular, their dimensions are the same.

The cohomologies of the truncated cochain complex

 $$ 0\to\Omega^{0}\to\cdots\to\Omega^{n}\to\Omega^{n+1}\to\cdots $$ 

are called path cohomologies of $P$ and are defined by $H^{n}(P), n \geq 0$. Clearly, $H^{n}(P)$ is a dual space to $H_{n}(P)$. Similarly to (3.13), we have

 $$ \dim H^{n}=\dim\Omega^{n}-\dim d\Omega^{n}-\dim d\Omega^{n-1}, $$ 

and an analogous identity holds for reduced cohomologies  $ \tilde{H}^{n} $.

Let now P be a regular path complex. Then a similar construction works using the regular spaces  $ \Omega_{n} $ that are subspaces of  $ R_{n} $. Setting

 $$ \begin{align*}\mathcal{N}^{n}\quad&=\quad\operatorname{span}\left\{e^{i_{0}\ldots i_{n}}:i_{0}\ldots i_{n}\text{is regular and non-allowed}\right\}\\&=\quad\{\omega\in\mathcal{R}^{n}:\omega_{i_{0}\ldots i_{n}}=0\text{for all allowed}i_{0}\ldots i_{n}\}\end{align*} $$ 

and defining  $ J^{n} $ as before by (3.21), we set

 $$ \Omega^{n}=\mathcal{R}^{n}/\mathcal{J}^{n} $$ 

and show as above that $d$ is well-defined on $\Omega^n$, that $\Omega^n$ can be identified with $(\Omega_n)'$ and that operators $d$ and $\partial$ are dual. Since $\mathcal{R}^n = \mathcal{A}^n \oplus \mathcal{N}^n$, the formula (3.23) holds in the regular case, too.

Let us prove that the concatenation is well-defined on the (regular and non-regular) spaces  $ \Omega^{n} $.

Lemma 3.20 Let $\varphi$ be a $p$-form and $\psi$ be a $q$-form. If $\varphi \in \mathcal{J}^p$ or $\psi \in \mathcal{J}^q$ then $\varphi\psi \in \mathcal{J}^{p+q}$, that is, $\{ \mathcal{J}^p \}$ is a graded ideal for the concatenation. Consequently, the concatenation of two forms is well-defined on the spaces $\mathcal{J}^p$ as well as on $\Omega^p$, and it satisfies the product rule (2.19).

Proof. Observe first that if  $ \varphi \in \mathcal{N}^p $ then  $ \varphi\psi \in \mathcal{N}^{p+q} $. Indeed, it suffices to prove this for elementary forms  $ \varphi = e^{i_0\cdots i_p} $ and  $ \psi = e^{j_0\cdots j_q} $ where the claim is obvious: if the p-path  $ i_0\ldots i_p $ is non-allowed then so is the concatenated  $ (p + q) $-path  $ i_0\ldots i_p j_1\ldots j_q $, by the definition of a path complex (in the regular case we use in addition the fact that concatenation of regular paths is regular).

If  $ \varphi \in \mathcal{J}^p $ then  $ \varphi = \varphi_0 + d\varphi_1 $ where  $ \varphi_0 \in \mathcal{N}^p $ and  $ \varphi_1 \in \mathcal{N}^{p-1} $. Then we have

 $$ \begin{align*}\begin{array}{rcl}\varphi\psi&=&\varphi_{0}\psi+(d\varphi_{1})\psi\\&=&\varphi_{0}\psi+d\left(\varphi_{1}\psi\right)-(-1)^{p-1}\varphi_{1}d\psi.\end{array}\end{align*} $$ 

By the above observation, all the forms  $ \varphi_0\psi $,  $ \varphi_1\psi $,  $ \varphi_1d\psi $ are in  $ \mathcal{N}^\bullet $. It follows that  $ d(\varphi_1\psi) \in \mathcal{J}^{p+q} $ and, hence,  $ \varphi\psi \in \mathcal{J}^{p+q} $. In the same way one handles the case  $ \psi \in \mathcal{J}^q $.

To prove that concatenation is well defined on  $ \Omega^p $, we need to verify that if  $ \varphi = \varphi' \bmod \mathcal{J}^p $ and  $ \psi = \psi' \bmod \mathcal{J}^q $ then  $ \varphi\psi = \varphi\psi \bmod \mathcal{J}^{p+q} $. Indeed, we have

 $$ \varphi\psi-\varphi^{\prime}\psi^{\prime}=\varphi\left(\psi-\psi^{\prime}\right)+\left(\varphi-\varphi^{\prime}\right)\psi^{\prime}, $$ 

and each of the terms in the right hand side belong to  $ J^{p+q} $ by the first part. Finally, the product rule for equivalence classes follows from that for their representatives. ■

Lemma 3.20 and the product rule allow to extend concatenation to an operation of homology classes.

Proposition 3.21 If $\varphi \in \Omega^p$ and $\psi \in \Omega^q$ are closed forms and one of the forms $\varphi, \psi$ is exact then $\varphi \psi$ is also exact. Consequently, concatenation is well defined as an operation from $H^p \times H^q$ to $H^{p+q}$.

Proof. If  $ \varphi = d\omega $ then

 $$ d\left(\omega\psi\right)=\left(d\omega\right)\psi+\left(-1\right)^{p}\omega d\psi=\varphi\psi, $$ 

so that  $ \varphi\psi $ is exact. Hence, if  $ \varphi_1, \varphi_2 $ and  $ \psi_1, \psi_2 $ are closed forms such that  $ \varphi_1 = \varphi_2 \bmod \text{Im} d $ and  $ \psi_1 = \psi_2 \bmod \text{Im} d $ then

 $$ \varphi_{1}\psi_{1}-\varphi_{2}\psi_{2}=\varphi_{1}\left(\psi_{1}-\psi_{2}\right)+\left(\varphi_{1}-\varphi_{2}\right)\psi_{2}=0\bmod\operatorname{Im}d, $$ 

that is,  $ \varphi_{1}\psi_{1} $ and  $ \varphi_{2}\psi_{2} $ represent the same homology class, which was to be proved. ■

Hence, concatenation is analogous to operations of cup product for simplicial complexes and wedge product for differential forms on manifolds.

Remark 3.22 We see that the direct sum

 $$ \Omega=\bigoplus_{n\geq0}\Omega^{n} $$ 

with the operations $d$ and concatenation is a graded differential algebra. Note that $\Omega^0$ coincides with the space $\mathcal{R}^0$ of all $\mathbb{K}$-valued functions on $V$. As it was mentioned in Remark 2.20, all minimal graded differential algebras over $\mathcal{R}^0$ are the quotients of $\mathcal{R}$. In particular, in the case of a regular path complex, $\Omega$ is explicitly given by (3.28) as a quotient of $\mathcal{R}$.

### 3.5 A condition for  $ \dim\Omega^{p}=0 $

Let us consider the following equivalence relation. For two $n$-forms $\varphi, \psi$ (from $\Lambda^n$ or $\mathcal{R}^n$) we write

 $$ \varphi\simeq\psi\mathrm{i f}\varphi=\psi\bmod\mathcal{T}^{n}, $$ 

where  $ J^{n} $ is defined by (3.21). Then we already know that

 $$ \varphi\simeq0\Rightarrow d\varphi\simeq0, $$ 

and

 $$ \varphi\simeq0\quad or\quad\psi\simeq0\Rightarrow\varphi\psi\simeq0 $$ 

(cf. 3.20). By (3.22) or (3.28), the equivalence classes of $\simeq$ can be identified with the elements of $\Omega^{n}$.

Proposition 3.23 (a) If  $ \dim \Omega^n = 0 $ then  $ \dim \Omega^p = 0 $ for all  $ p > n $.

(b) If the spaces  $ \Omega^\bullet $ are regular then  $ \dim\Omega^n \leq 1 $ implies that  $ \dim\Omega^p = 0 $ for all  $ p > n $.

Proof. In the both cases, we need to show that, for any p-path  $ i_{0}...i_{p} $ with p > n,

 $$ e^{i_{0}\dots i_{p}}\simeq0. $$ 

(a) By hypothesis  $ \Omega^n = \{0\} $ we have  $ e^{i_0\ldots i_n} \simeq 0 $. Since

 $$ e^{i_{0}\dots i_{p}}=e^{i_{0}\dots i_{n}}e^{i_{n}\dots i_{p}}, $$ 

it follows by Lemma 3.20 that also  $ e^{i_{0}\cdots i_{p}} \simeq 0 $.

(b) It suffices to treat the case  $ \dim \Omega^n = 1 $. Since for a non-allowed path  $ i_0...i_p $ the relation  $ e^{i_0...i_p} \simeq 0 $ holds by definition, we can assume that  $ i_0...i_p $ is allowed. We have

 $$ e^{i_{0}\ldots i_{p}}=e^{i_{0}\ldots i_{n}}e^{i_{n}\ldots i_{p}}=e^{i_{0}i_{1}}e^{i_{1}\ldots i_{n+1}}e^{i_{n+1}\ldots i_{p}} $$ 

If

 $$ \begin{array}{r l}{\mathrm{e i t h e r}}&{{}e^{i_{0}\dots i_{n}}\simeq0\mathrm{o r}e^{i_{1}\dots i_{n+1}}\simeq0,}\end{array} $$ 

then we obtain  $ e^{i_0 \cdots i_p} \simeq 0 $. If (3.30) fails then the both forms  $ e^{i_0 \cdots i_n} $ and  $ e^{i_1 \cdots i_{n+1}} $ represent nonzero elements of  $ \Omega^n $. Since the latter space has dimension 1, it follows that for some constant  $ \alpha \in \mathbb{K} $,

 $$ e^{i_{1}\dots i_{n+1}}\simeq\alpha e^{i_{0}\dots i_{n}}. $$ 

Substituting into (3.29), we obtain

 $$ e^{i_{0}\dots i_{p}}\simeq\alpha e^{i_{0}i_{1}}e^{i_{0}\dots i_{n}}e^{i_{n+1}\dots i_{p}}. $$ 

Since the path  $ i_0...i_p $ is allowed and the path complex in question is regular, this path is regular and, hence,  $ i_0 \neq i_1 $. It follows that  $ e^{i_0i_1}e^{i_0...i_n} = 0 $, whence  $ e^{i_0...i_p} \simeq 0 $, which finishes the proof.

### 3.6 Connected components and  $ H^{0} $

Given a path complex $P$ with a vertex set $V$, by a connected component of $P$ we mean any minimal$^2$ subset $U$ of $V$ that if $i \in U$ then $U$ contains any vertex $j \in V$ such that $ij$ or $ji$ is an allowed 1-path. Clearly, any two connected components are either disjoint or identical, and the vertex set $V$ is a disjoint union of the connected components. If $V$ itself is a connected component then the path complex $P$ is called connected.

For example, if P is the path complex of a digraph then the connected components of P coincide with those of the underlying undirected graph.

Proposition 3.24 For any path complex P we have

 $$ \dim H^{0}\left(P\right)=C, $$ 

where $C$ is the number of connected components of $P$. In particular, if $P$ is connected then $\dim H^0(P) = 1$ and, hence, $\dim \widetilde{H}^0(P) = 0$.

Proof. By definition, we have

 $$ H^{0}\left(\Omega\right)=\ker d|_{\Omega^{0}}=\left\{f\in\Omega^{0}:df\simeq0\right\}. $$ 

The condition  $ df \simeq 0 $ means that  $ df \in \mathcal{J}^0 = \mathcal{N}^0 $, that is,  $ (df)_{ij} = 0 $ for all allowed 1-paths  $ ij $. Therefore, we have  $ f_i = f_j $ for all allowed 1-paths  $ ij $. The latter is equivalent to the fact that  $ f = \text{const} $ on any connected component of  $ P $. Hence, the dimension of the space of such functions is equal to  $ C $. ■

### 3.7 Disjoint union and connected sum

For any two path complexes  $ P' $ and  $ P'' $ with the vertex sets  $ V' $ and  $ V'' $, respectively, their union  $ P' \cup P'' $ is obviously also a path complex with the vertex set  $ V' \cup V'' $. We say that  $ P' $ and  $ P'' $ are disjoint if their vertex sets are disjoint.

Proposition 3.25 If  $ P' $ and  $ P'' $ are disjoint path complexes then, for their union  $ P = P' \cup P'' $ we have

 $$ \Omega^{n}\left(P\right)=\Omega^{n}\left(P^{\prime}\right)\oplus\Omega^{n}\left(P^{\prime\prime}\right) $$ 

and, hence,

 $$ H^{n}\left(P\right)\cong H^{n}\left(P^{\prime}\right)\oplus H^{n}\left(P^{\prime\prime}\right) $$ 

for all  $ n \geq 0 $.

Proof. This follows from the obvious identities

 $$ S^{n}\left(P\right)=S^{n}\left(P^{\prime}\right)\oplus S^{n}\left(P^{\prime\prime}\right) $$ 

for each space $S = \Lambda, \mathcal{R}, \mathcal{N}$, $\mathcal{J}$, and the fact that $d$ on $\Lambda''(P)$ splits into the direct sum of the operators $d$ on $\Lambda^n(P')$ and $\Lambda^n(P'')$.

## 4  $ \partial $-invariant paths on digraphs

In this section, we fix a digraph  $  G = (V, E)  $ without loops. Then its path complex  $  P(G)  $ is regular. We study here the regular spaces  $  \Omega_n(G) = \Omega_n(P(G))  $ of  $ \partial $-invariant paths and the associated homology groups  $  H_n(G) = H_n(P(G))  $ and  $  \widetilde{H}_n(G) = \widetilde{H}_n(P(G))  $.

### 4.1 Semi-edges and  $ \partial $-invariant paths

Let us describe more explicitly the notion of  $ \partial $-invariant paths on a digraph  $ G $. Let us say that a pair ij of vertices is a semi-edge if it is not an edge but there is a vertex  $ k $ (not necessarily unique) such that ik and kj are edges. The 2-path ikj is called a bridge of the semi-edge ij. The semi-edge ij will be denoted by  $ i \rightharpoonup j $ as on the diagram:

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//a51da62c-37be-4447-b774-c2076c9027ad/markdown_2/imgs/img_in_image_box_548_1258_644_1317.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A09Z%2F-1%2F%2Fcb516165aba80011857e4e7b34fa9c69fcf29b3ff27d6c6d87efda652b97907a" alt="Image" width="7%" /></div>


Let us say that an elementary path  $ i_0...i_p $ is semi-allowed if among the pairs  $ i_{q-1}i_q $,  $ q = 1, ..., p $, there is exactly one semi-edge, while all others are edges, as on the diagram:

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//a51da62c-37be-4447-b774-c2076c9027ad/markdown_2/imgs/img_in_image_box_401_1410_792_1481.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A10Z%2F-1%2F%2F80ccc58d6c475524491e80c2e1c1a3ce3ae426ec6c80fe3599919b1ffa561e1d" alt="Image" width="31%" /></div>


A path  $ i_0...i_{q-1}ki_q...i_p $ that is obtained by replacing in  $ i_0...i_{q-1}i_q...i_p $ the semi-edge  $ i_{q-1}i_q $ by the bridge  $ i_{q-1}ki_q $, is obviously allowed and will be called an allowed extension of  $ i_0...i_p $.

Let us use the following notation: if  $ i_{0}...i_{p} $ is semi-allowed with the semi-edge  $ i_{q-1}i_{q} $ then, for any p-path v, define its deficiency  $ [v]^{i_{0}...i_{p}} $ along the path  $ i_{0}...i_{p} $ by

 $$ [v]^{i_{0}\dots i_{p}}:=\sum_{k\in V}v^{i_{0}\dots i_{q-1}k i_{q}\dots i_{p}}. $$ 

Clearly, it suffices to restrict the summation to those $k$ forming a bridge $i_{q-1}ki_{q}$. Alternatively, one can say that the summation in (4.1) is performed across all allowed extensions of the path $i_{0}...i_{p}$.

Lemma 4.1 Let  $ p \geq 1 $. A path  $ v \in \mathcal{A}_{p+1} $ belongs to  $ \Omega_{p+1} $ if and only if for all semi-allowed paths  $ i_0...i_p $,

 $$ [v]^{i_{0}\dots i_{p}}=0. $$ 

Proof. The condition  $ v \in \Omega_{p+1} $ is equivalent to  $ \partial v \in \mathcal{A}_p $, while the latter is equivalent to

 $$ (\partial v)^{i_{0}\dots i_{p}}=0 $$ 

for all non-allowed regular paths  $ i_{0}...i_{p-1} $. By (2.4) we have

 $$ (\partial v)^{i_{0}...i_{p}}=\sum_{q=0}^{p+1}\sum_{k}(-1)^{q}v^{i_{0}...i_{q-1}k i_{q}...i_{p}}. $$ 

If  $ i_{0}...i_{p} $ is not semi-allowed then all the paths  $ i_{0}...i_{q-1}ki_{q}...ip $ are not allowed, because by inserting k one can eliminate only one non-edge. Hence, for such  $ i_{0}...i_{p} $ the condition (4.2) is satisfied automatically, so that (4.2) is non-void only for semi-allowed paths. If the only semi-edge in  $ i_{0}...i_{p} $ is  $ i_{q-1}i_{q} $ then (4.2) amounts to

 $$ \sum_{k}v^{i_{0}\ldots i_{q-1}k i_{q}\ldots i_{p}}=0, $$ 

which was to be proved. ■

### 4.2 Triangles, squares and  $ \dim \Omega_{p} $

Recall that  $ \dim \Omega_0 = \dim \mathcal{A}_0 = |V| $ and  $ \dim \Omega_1 = \dim \mathcal{A}_1 = |E| $. Here we give an explicit formula for  $ \dim \Omega_2 $ using the set  $ P_2 $ of allowed 2-paths and the set  $ \mathcal{S} $ of semi-edges of the digraph  $ G $ (see Section 4.1 for the definition of a semi-edge).

##### Proposition 4.2 We have

 $$ \dim\Omega_{2}=\dim\mathcal{A}_{2}-|\mathcal{S}|=|P_{2}|-|\mathcal{S}|. $$ 

Proof. Recall that

 $$ \mathcal{A}_{2}=\mathrm{s p a n}\left\{e_{a b c}:a b c\mathrm{~i s~a l l o w e d}\right\},\quad\mathrm{d i m}\mathcal{A}_{2}=\left|P_{2}\right|, $$ 

and

 $$ \Omega_{2}=\left\{v\in\mathcal{A}_{2}:\partial v\in\mathcal{A}_{1}\right\}=\left\{v\in\mathcal{A}_{2}:\partial v=0\bmod\mathcal{A}_{1}\right\}. $$ 

If abc is allowed then ab and bc are edges, whence

 $$ \partial e_{a b c}=e_{b c}-e_{a c}+e_{a b}=-e_{a c}\bmod{\mathcal{A}_{1}}. $$ 

If ac is an edge then  $ e_{ac} = 0 \bmod A_{1} $. If ac is not an edge then ac is a semi-edge, and in this case

 $$ \partial e_{a b c}\neq0\bmod{\mathcal{A}_{1}}. $$ 

For any  $ v \in \Omega_2 $, we have

 $$ v=\sum_{\{a b c\mathrm{i s~a l l o w e d\}}}v^{a b c}e_{a b c} $$ 

hence it follows that

 $$ \partial v=-\sum_{\{a b c:~a c~\mathrm{i s~\mathrm{s e m i-e d g e}\}}}{v^{a b c}}{e_{a c}}~\mathrm{m o d}\mathcal{A}_{1}. $$ 

The condition  $ \partial v = 0 \bmod A_1 $ is equivalent to

 $$ \sum_{\{a b c:~a c~i s~s e m i-e d g e\}}v^{a b c}e_{a c}=0\bmod{\mathcal{A}_{1}}, $$ 

which is equivalent to  $ \sum_b v^{abc} = 0 $ for all semi-edges  $ ac $. The number of these conditions is exactly  $ |\mathcal{S}| $, and they all are independent for different semi-edges, because a triple  $ abc $ determines at most one semi-edge. Hence,  $ \Omega_2 $ is obtained from  $ \mathcal{A}_2 $ by imposing  $ |\mathcal{S}| $ linearly independent conditions, which implies (4.4).

Let us call by a triangle a sequence of three distinct vertices  $ a, b, c \in V $ such that  $ a \to b, b \to c, a \to c $.

 $$ \begin{array}{ccc} b & & \\ \bullet & & \\ \rightarrow & \rightarrow & \\ a \bullet \begin{array}{c} \bullet \\ c \end{array} \end{array} $$ 

Note that a triangle determines a 2-path  $ e_{abc} \in \Omega_2 $ as  $ e_{abc} \in \mathcal{A}_2 $ and

 $$ \partial e_{a b c}=e_{b c}-e_{a c}+e_{a b}\in\mathcal{A}_{1}. $$ 

Let us called by a square a sequence of four distinct vertices  $ a, b, b', c \in V $ such that  $ a \to b, b \to c, a \to b', b' \to c $:

 $$ \begin{array}{ccc} b^{\bullet} & \longrightarrow &  \bullet_{c} \\ \uparrow & & \uparrow \end{array} $$ 

 $$ a^{\bullet}\quad\longrightarrow\quad\bullet b^{\prime} $$ 

Note that a square determines a 2-path  $ v := e_{abc} - e_{ab'c} \in \Omega_2 $ as  $ v \in \mathcal{A}_2 $ and

 $$ \begin{align*}\partial v\quad&=\quad(e_{bc}-e_{ac}+e_{ab})-(e_{b^{\prime}c}-e_{ac}+e_{ab^{\prime}})\\&=\quad e_{ab}+e_{bc}-e_{ab^{\prime}}-e_{b^{\prime}c}\in\mathcal{A}_{1}.\end{align*} $$ 

Theorem 4.3 Assume that a digraph  $  G = (V, E)  $ contains no squares (as subgraphs). Then  $ \dim \Omega_2(G) $ is equal to the number of distinct triangles in  $ G $, and  $ \dim \Omega_p(G) = 0 $ for all  $ p > 2 $.

In particular, if $G$ contains neither triangle nor square then $\dim\Omega_p(G)=0$ for all $p\geq2$. Consequently, $\dim H_p(G)=0$ for all $p\geq2$.

Proof. Let us split the family  $ P_{2} $ of allowed 2-paths into two subsets: an allowed path  $ abc $ is of the first kind if  $ ac $ is an edge and of the second kind otherwise:

 $$ 1^{s t}\mathrm{~k i n d}\colon\begin{array}{c c c c c}{}&{\stackrel{b}{\bullet}}&{}&{}\\ {a^{\bullet}}&{\rightarrow}&{\stackrel{\searrow}{\bullet}_{c}}&{,}&{}\\ \end{array}\quad2^{n d}\mathrm{~k i n d}\colon\begin{array}{c c c c c}{}&{\stackrel{b}{\bullet}}&{}&{}\\ {a^{\bullet}}&{\rightarrow}&{}&{}\\ \end{array}\stackrel{\searrow}{\bullet}_{c} $$ 

Clearly, the paths of the first kind are in one-to-one correspondence with triangles. Each path abc of the second kind determines a semi-edge ac. The mapping of  $ abc \mapsto ac $ from the paths of second kind to semi-edges is also one-to-one: if  $ abc \mapsto ac $ and  $ ab'c \mapsto ac $ then we obtain a square  $ a, b, b', c $ which contradicts the hypotheses. Hence, the number of the path of the second kind is equal to  $ |\mathcal{S}| $, which implies that the number of the paths of the first kind is equal to  $ |P_2| - |\mathcal{S}| $, and so is the number of triangles. Comparing with (4.4) we obtain that  $ \dim \Omega_2 $ is equal to the number of triangles.

Let us prove that $\Omega_3 = \{0\}$, that is, any $v \in \Omega_3$ is identical 0. It suffices to prove that $v^{ijkl} = 0$ for any allowed path ijkl on $G$. Fix an allowed path ijkl and assume first $jl$ is a semi-edge. Then ijl is semi-allowed, and by Lemma 4.1 we obtain $[v]^{ijl} = 0$, that is,

 $$ \sum_{k^{\prime}}v^{i j k^{\prime}l}=0. $$ 

However, the only allowed path of the form  $ ijk^{\prime}l $ is  $ ijkl $ because of the absence of squares:

 $$ \begin{array}{ccc} \text{k} & \bullet& \\ \text{i} \bullet \rightarrow_{j} \bullet \begin{array}{c} \searrow \\ \searrow \end{array} & \text{●} & \\ \text{k}^{\prime} & \text{●} & \end{array} $$ 

We conclude that  $ v^{ijkl} = 0 $, provided jl is a semi-edge. In the same way  $ v^{ijkl} = 0 $ provided ik is a semi-edge.

Now we claim that, for any allowed path ijkl, either ik or jl is a semi-edge. Indeed, if neither of them is a semi-edge then both ik and jl must be edges, which implies that the sequence i, j, k, l forms a square:

 $$ i\bullet\stackrel{k}{\leftarrow}\quad\stackrel{\bullet}{\uparrow}\quad\stackrel{\bullet}{\rightarrow}\bullet_{l}\quad, $$ 

which contradicts the hypothesis. It follows that  $ v^{ijkl} = 0 $ for any allowed path  $ ijkl $, which proves that  $ \Omega_3 = \{0\} $. By Proposition 3.23 we conclude that  $ \Omega_p = \{0\} $ for all  $ p \geq 3 $. ■

In the presence of squares one cannot relate directly  $ \dim \Omega_{2} $ to the number of squares and triangles since there may be a linear dependence between them as in the next example.

Example 4.4 In the following digraph

 $$ 0\xrightarrow{}\stackrel{\stackrel{1}{\bullet}}{\searrow}\quad\stackrel{\stackrel{2}{\bullet}}{\searrow}\quad\stackrel{\searrow}{\rightarrow}\quad\stackrel{\searrow}{\searrow}\quad4 $$ 

there are three squares 0, 1, 2, 4, 0, 1, 3, 4, and 0, 2, 3, 4, which determine three  $ \partial $-invariant paths

 $$ e_{014}-e_{024},\quad e_{024}-e_{034},\quad e_{034}-e_{014}. $$ 

These paths are linearly dependent as their sum is equal to 0. It is easy to see that  $ \dim\Omega_2 = 2 $ as  $ |P_2| = 3 $ and  $ |\mathcal{S}| = 1 $ as  $ \mathcal{S} = \{04\} $. For this digraph all homologies are trivial.

Also, in the presence of squares one may have non-trivial  $ \Omega_{p} $ for arbitrary p as one can see from numerous examples in the subsequent sections.

### 4.3 Snakes and simplexes

A snake of length p is a digraph with  $ p+1 $ vertices, say 0,1,...,p, and with the edges  $ i(i+1) $ and  $ i(i+2) $ (see Fig. 4). In particular, any triple  $ i(i+1)(i+2) $ is a triangle.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//17f314f3-eb17-47d7-900f-c7c740cd9b2c/markdown_1/imgs/img_in_image_box_273_455_824_648.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A09Z%2F-1%2F%2F6617faa5754571181afe8a8147d21805fa68b3a70463d4cf346cc7bca6f0ffe5" alt="Image" width="45%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 4: A snake</div> </div>


A snake of length $p$ contains a $\partial$-invariant $p$-path $v = e_{01...p}$. Indeed, this path is obviously allowed, its boundary

 $$ \partial v=\sum_{k=0}^{p}\left(-1\right)^{k}e_{0\ldots\widehat{k}\ldots p} $$ 

is also allowed (because  $ (k-1)(k+1) $ is an edge), whence  $ v \in \Omega_p $.

Let us define for any  $ n \geq 0 $ a simplex-digraph  $ \text{Sm}_n $ as follows: its set of vertices is  $ \{0,1,...,n\} $ and the edges are  $ i \to j $ for all  $ i < j $. For example, we have

 $$ \mathrm{S m}_{1}=\mathbf{\Lambda}^{0}\bullet\mathbf{\Lambda}\rightarrow\mathbf{\Lambda}\bullet\mathbf{\Lambda}^{1},\quad\mathrm{S m}_{2}=\mathbf{\Lambda}_{0}\mathbf{\Lambda}\stackrel{\mathbf{\Lambda}^{2}}{\rightarrow}\mathbf{\Lambda}\stackrel{\bullet}{\rightarrow}\mathbf{\Lambda}\bullet\mathbf{\Lambda}^{1}, $$ 

and Sm₃ is shown on Fig. 5.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//17f314f3-eb17-47d7-900f-c7c740cd9b2c/markdown_1/imgs/img_in_image_box_472_1124_685_1327.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A09Z%2F-1%2F%2F0deaa8548b1d56b20fc778505fbf52d55b1a2afd791ad4e71d1835471c8dbc07" alt="Image" width="17%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 5: A 3-simplex digraph Sm $ _{3} $</div> </div>


Since a simplex contains a snake as a subgraph, the n-path  $ v = e_{01...n} $ is  $ \partial $-invariant on  $ Sm_n $

### 4.4 Star-shaped digraphs and Poincaré lemma

Definition 4.5 We say that a digraph $G$ is star-shaped if there is a vertex $a$ (called a star center) such that $a \to b$ for all $b \neq a$. Similarly, a digraph $G$ is called inverse star-shaped if there is a vertex $a$ (called a star center) such that $b \to a$ for all $b \neq a$

For example, a digraph  $ 0_{\bullet} \stackrel{1}{\leftrightarrow} \stackrel{1}{\leftrightarrow} \stackrel{2}{\leftrightarrow} $ is star-shaped with the star center 0.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//17f314f3-eb17-47d7-900f-c7c740cd9b2c/markdown_2/imgs/img_in_image_box_410_308_510_367.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A11Z%2F-1%2F%2F6d4824c3369357f571168384568da29c4edc00ccd68b3639f58a8ae158d8d23b" alt="Image" width="8%" /></div>


Theorem 4.6 (A Poincaré lemma) If $G$ is a (inverse) star-shaped digraph, then all reduced homologies $\widetilde{H}_{n}(G)$ are trivial.

Proof. To prove that  $ H_n(G) = \{0\} $, we need to show that if  $ v \in \Omega_n $ and  $ \partial v = 0 $ then  $ v = \partial u $ for some  $ u \in \Omega_{n+1} $. Set  $ u = e_a v $. We claim that  $ u \in \mathcal{A}_{n+1} $. Since  $ v $ is a linear combination of allowed paths  $ e_{i_0\ldots i_n} $, it suffices to show that  $ e_{a_{i_0\ldots i_n}} \in \mathcal{A}_{n+1} $ for any allowed path  $ e_{i_0\ldots i_n} $. Indeed, if  $ i_0 = a $ then  $ e_{a_{i_0\ldots i_n}} = 0 \in \mathcal{A}_{n+1} $. If  $ i_0 \neq a $ then  $ e_{a_{i_0\ldots i_n}} $ is allowed by the star condition. Hence, we have  $ u \in \mathcal{A}_{n+1} $.

By the product rule (2.9) we have

 $$ \partial u=\partial\left(e_{a}v\right)=v-e_{a}\partial v=v, $$ 

where we have used $\partial v = 0$. It follows that $\partial u \in \mathcal{A}_n$ and, hence, $u \in \Omega_{n+1}$, which finishes the proof.

In a similar manner one handles the inverse star-shaped graphs. ■

For example, the simplex-digraph  $ Sm_{n} $ is star-shaped (and inverse star-shaped), we obtain by Theorem 4.6 that all reduced homologies of  $ Sm_{n} $ are trivial.

### 4.5 Cycle-graphs

We say that a digraph  $  G = (V, E)  $ is a cycle-graph if it is connected (as an undirected graph) and every vertex had the degree 2 (see Fig. 6).

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//17f314f3-eb17-47d7-900f-c7c740cd9b2c/markdown_2/imgs/img_in_image_box_533_1004_718_1133.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A11Z%2F-1%2F%2F223f1035b513012adf297814ec4fdc2ea73e59c2688c8a94ba5feceb0866fc85" alt="Image" width="15%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 6: A cycle-graph (directions of edges are not shown)</div> </div>


For a cycle-graph we have  $ \dim H_{0}(G) = 1 $ and

 $$ \dim\Omega_{0}\left(G\right)=\left|V\right|=\left|E\right|=\dim\Omega_{1}\left(G\right). $$ 

Proposition 4.7 Let G be a cycle-graph. Then

 $$ \begin{array}{r c l}{\operatorname{d i m}\Omega_{p}\left(G\right)}&{=}&{0\quad{f o r~a l l~}p\geq3}\\ {\operatorname{d i m}H_{p}\left(G\right)}&{=}&{0{~f o r~a l l~}p\geq2.}\\ \end{array} $$ 

If G is a triangle or a square then

 $$ \dim\Omega_{2}\left(G\right)=1,\dim H_{1}\left(G\right)=0,\chi=1 $$ 

whereas otherwise

 $$ \dim\Omega_{2}\left(G\right)=0,\quad\dim H_{1}\left(G\right)=1,\quad\chi=0. $$ 

Proof. Observe first that  $ \dim\Omega_2 \leq 1 $ will imply  $ \dim\Omega_p = 0 $ for all  $ p \geq 3 $ by Proposition 3.23, whence  $ \dim H_p = 0 $ for  $ p \geq 3 $. Hence, we need only to handle the cases  $ p = 1, 2 $.

Using two equivalent definition of the Euler characteristic, we have

 $$ \begin{aligned}\chi\ &=\dim H_{0}-\dim H_{1}+\dim H_{2}\\&=\dim\Omega_{0}-\dim\Omega_{1}+\dim\Omega_{2}\end{aligned} $$ 

whence

 $$ \chi=\dim\Omega_{2}=1-\dim H_{1}+\dim H_{2}. $$ 

Assume first that $G$ is neither triangle nor square. Then $G$ contains neither triangle nor square. By Theorem 4.3 $\dim\Omega_{2}=0$ whence $\dim H_{2}=0$ and by (4.6) $\chi=0$ and $\dim H_{1}=1$.

Let us construct an 1-path spanning  $ H_1 $. For that let us identify  $ G $ with  $ \mathbb{Z}_N $ where  $ N = |V| $ so that in the undirected graph based on  $ G $ the edges are  $ i(i+1) $. Hence, in the digraph  $ G $ either  $ i(i+1) $ or  $ (i+1)i $ is an edge. Consider an allowed 1-path  $ \sigma $ with components

 $$ \sigma^{i(i+1)}=\left\{\begin{array}{ll}1,&if i\left(i+1\right)is an edge\\ -1,&if\left(i+1\right)is an edge,\end{array}\right. $$ 

and all other components of  $ \sigma $ vanish (see Fig. 7).

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//17f314f3-eb17-47d7-900f-c7c740cd9b2c/markdown_3/imgs/img_in_image_box_485_873_716_1040.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A12Z%2F-1%2F%2Fc141125caad6da68a9e77e394feeed2ac004a6de08cc66d734b4733a652671d6" alt="Image" width="18%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 7: The 1-path  $ \sigma = -e_{01} - e_{12} + e_{23} + e_{34} - e_{45} + e_{50} $ spans  $ H_{1} $.</div> </div>


Since  $ \sigma \neq 0 $,  $ \sigma $ is not in  $ \mathrm{Im} \partial|_{\Omega_2} $. However,  $ \sigma \in \ker \partial_{\Omega_1} $ because by construction  $ \sigma^{i(i+1)} - \sigma^{(i+1)i} \equiv 1 $ whence for any  $ i $

 $$ \left(\partial\sigma\right)^{i}=\sum_{j\in V}\left(\sigma^{j i}-\sigma^{i j}\right)=\sigma^{(i-1)i}+\sigma^{(i+1)i}-\sigma^{i(i-1)}-\sigma^{i(i+1)}=1-1=0. $$ 

Let G be a triangle

 $$ \begin{array}{ccc} b & & \\ \bullet & & \\ \rightarrow & \rightarrow & \\ a \bullet \begin{array}{c} \bullet \\ c \end{array} \end{array} $$ 

Then  $ \dim\mathcal{A}_2 = 1 $,  $ \mathcal{S} = \emptyset $ whence  $ \dim\Omega_2 = 1 $ and  $ \chi = 1 $. Clearly, we have  $ \Omega_2 = \text{span}\{e_{abc}\} $. Since  $ \partial e_{abc} \neq 0 $, we see that  $ \ker \partial|_{\Omega_2} = 0 $ and, hence,  $ \dim H_2 = 0 $. Then by (4.6)  $ \dim H_1 = 0 $.

Let G be a square, say a, b,  $ b', c $:

 $$ \begin{array}{ccc} b^{\bullet} & \longrightarrow &  \bullet_{c} \\ \uparrow & & \uparrow \end{array} $$ 

 $$ a^{\bullet}\quad\longrightarrow\quad\bullet_{b^{\prime}} $$ 

Then

 $$ \mathcal{A}_{2}=\mathrm{s p a n}\left\{e_{a b c},e_{a b^{\prime}c}\right\},\quad\mathcal{S}=\left\{a c\right\} $$ 

whence  $ \dim\Omega_{2}=2-1=1 $ and  $ \chi=1 $. Note that in this case

 $$ \Omega_{2}=\mathrm{s p a n}\left\{e_{a b c}-e_{a b^{\prime}c}\right\}. $$ 

As in the case of a triangle, we obtain  $ \ker \partial|_{\Omega_2} = 0 $,  $ \dim H_2 = 0 $ and  $ \dim H_1 = 0 $. ■

### 4.6 An example of direct computation of  $ \dim H_{p} $

Consider the digraph  $  G = (V, E)  $ with  $  V = \{0, 1, 2, 3, 5\}  $ and  $  E = \{01, 02, 13, 14, 23, 24, 53, 54\}  $, see Fig. 8.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//17f314f3-eb17-47d7-900f-c7c740cd9b2c/markdown_4/imgs/img_in_image_box_467_625_653_906.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A14Z%2F-1%2F%2F61a2c7ad86690d4dcfdcdabadd2c355e33243bd4b3f17ab656fd32afd86f9b53" alt="Image" width="15%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 8: A digraph with 6 vertices and 8 edges</div> </div>


Let us compute the (regular) spaces Ωp and their homologies Hp. We have

 $$ \begin{array}{r l r}{\Omega_{0}}&{{}=}&{\mathcal{A}_{0}=\mathrm{s p a n}\left\{e_{0},e_{1},e_{2},e_{3},e_{4},e_{5}\right\},\quad\mathrm{d i m}\Omega_{0}=6}\end{array} $$ 

 $$ \Omega_{1}\quad=\quad\mathcal{A}_{1}=\mathrm{s p a n}\left\{e_{01},e_{02},e_{13},e_{14},e_{23},e_{24},e_{53},e_{54}\right\},\quad\mathrm{d i m}\Omega_{1}=8 $$ 

 $$ \mathcal{A}_{2}=\mathrm{s p a n}\left\{e_{013},e_{014},e_{023},e_{024}\right\},\mathrm{d i m}\mathcal{A}_{2}=4. $$ 

The set of semi-edges is  $ \mathcal{S} = \{e_{03}, e_{04}\} $ so that  $ \dim \Omega_2 = \dim \mathcal{A}_2 - |S| = 2 $. The basis in  $ \Omega_2 $ can be easily spotted as each of two squares 0, 1, 2, 3 and 0, 1, 2, 4 determine a  $ \partial $-invariant 2-paths, whence

 $$ \Omega_{2}=\mathrm{s p a n}\left\{e_{013}-e_{023},e_{014}-e_{024}\right\}. $$ 

Since there are no allowed 3-paths, we see that  $ A_3 = \Omega_3 = \{0\} $. It follows that

 $$ \chi=\dim\Omega_{0}-\dim\Omega_{1}+\dim\Omega_{2}=6-8+2=0. $$ 

By (3.13) we obtain

 $$ \dim H_{2}=\dim\Omega_{2}-\dim\partial\Omega_{2}-\dim\partial\Omega_{3}=2-\dim\partial\Omega_{2}. $$ 

The image  $ \partial\Omega_{2} $ is spanned by two 1-paths

 $$ \begin{array}{r l r}{\partial\left(e_{013}-e_{023}\right)}&{=}&{e_{13}-e_{03}+e_{01}-\left(e_{23}-e_{03}+e_{02}\right)=e_{13}+e_{01}-e_{23}-e_{02}}\end{array} $$ 

 $$ \begin{array}{r l r}{\partial\left(e_{014}-e_{024}\right)}&{=}&{e_{14}-e_{04}+e_{01}-\left(e_{24}-e_{04}+e_{02}\right)=e_{14}+e_{01}-e_{24}-e_{02}}\end{array} $$ 

that are clearly linearly independent. Hence,  $ \dim \partial\Omega_2 = 2 $ whence  $ \dim H_2 = 0 $. The dimension of  $ H_1 $ can be computed similarly, but we can do easier using the Euler characteristic: since

 $$ \dim H_{0}-\dim H_{1}+\dim H_{2}=\chi=0, $$ 

it follows that  $ \dim H_{1}=1 $.

In fact,  $ H_{1} $ is spanned by 1-path

 $$ v=e_{13}-e_{14}-e_{53}+e_{54}. $$ 

Indeed, by a direct computation $\partial v = 0$, so that $v \in \ker \partial|_{\Omega_1}$, while $v \notin \operatorname{Im} \partial|_{\Omega_2}$ because any element of $\operatorname{Im} \partial|_{\Omega_2}$ is a linear combination of $\partial(e_{013} - e_{023})$ and $\partial(e_{014} - e_{024})$ that does not contain the term $e_{54}$.

### 4.7 Triangulation as a closed path

Given a closed oriented $n$-dimensional manifold $M$, let $T$ be its triangulation, that is, a partition into $n$-dimensional simplexes. Denote by $V$ the set of all vertices of the simplexes from $T$ and by $E$ – the set of all edges, so that $(V,E)$ is a graph embedded on $M$. We would like to make $(V,E)$ into a digraph and define on that digraph a closed $n$-path as a certain alternating sum of elementary $n$-paths arising from the simplexes from $T$.

Let us enumerate the set of vertices V by distinct integers. For any simplex from T with the vertices  $ i_0...i_n $ define the quantity  $ \sigma^{i_0...i_n} $ to be equal to 1 if the orientation of the simplex  $ i_0...i_n $ matches the orientation of the manifold M, and -1 otherwise. Note that each simplex gives rise to  $ n! $ different ordered sequences of its vertices, each of them defining the quantity  $ \sigma^{i_0...i_n} $.

Let us introduce the orientation on the set of edges $E$ by choosing on each edge the direction from the vertex with a smaller number to the vertex with a larger number. Then each simplex from $T$ becomes a simplex-digraph as defined in Section 4.3. Denote by $\overrightarrow{T}$ the set of all digraph simplexes constructed in this way. That is, $i_0...i_n \in \overrightarrow{T}$ if $i_0...i_n$ is a monotone increasing sequence that determines a simplex from $T$.

Then consider the following n-path on the digraph G = (V, E):

 $$ \sigma=\sum_{i_{0}\dots i_{n}\in\overrightarrow{T}}\sigma^{i_{0}\dots i_{n}}e_{i_{0}\dots i_{n}}. $$ 

This path is allowed on G by the definition of the orientation of the edges.

We claim that the path $\sigma$ is closed, that is, $\partial\sigma = 0$, which, in particular, implies that $\sigma$ is $\partial$-invariant. Observe that $\partial\sigma$ is the a linear combination with coefficients $\pm 1$ of the terms $e_{j_0\cdots j_{n-1}}$ where the sequence $j_0,\ldots,j_{n-1}$ is monotone increasing and forms an $(n-1)$-dimensional face of one of the $n$-simplexes from $T$. In fact, every $(n-1)$-face arises from two $n$-simplexes, say $A = j_0\cdots j_{k-1}a_{j_k}\cdots j_{n-1}$ and $B = j_0\cdots j_{l-1}b_{j_l}\cdots j_{n-1}$ (cf. Fig. 9).

We have by  $ (2.2) $

 $$ \partial e_{j_{0}\cdots j_{k-1}a j_{k}\cdots j_{n-1}}=\cdots+(-1)^{k}e_{j_{0}\cdots j_{k-1}j_{k}\cdots j_{n-1}}+\cdots. $$ 

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e5d67364-6d3a-4a3d-af1e-67681318d208/markdown_1/imgs/img_in_image_box_256_158_930_529.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A07Z%2F-1%2F%2Fe31632ce94c6e1c234f8b355c918f1f52503822a5f93c7f6cbe8e40886f83f57" alt="Image" width="55%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 9: Two n-simplexes A, B having a common  $ (n-1) $-dimensional face  $ j_{0}...j_{n-1} $</div> </div>


Since interchanging the order of two neighboring vertices in an n-simplex changes its orientation, we have

 $$ \sigma^{j_{0}\cdots j_{k-1}a j_{k}\cdots j_{n-1}}=(-1)^{k}\sigma^{a j_{0}\cdots j_{k-1}j_{k}\cdots j_{n-1}}. $$ 

Multiplying the above lines, we obtain

 $$ \partial\left(\sigma^{A}e_{A}\right)=\ldots+\sigma^{a j_{0}\ldots j_{n-1}}e_{j_{0}\ldots j_{n-1}}+\ldots, $$ 

and in the same way

 $$ \partial\left(\sigma^{B}e_{B}\right)=\ldots+\sigma^{b j_{0}\ldots j_{n-1}}e_{j_{0}\ldots j_{n-1}}+\ldots $$ 

However, the vertices $a$ and $b$ are located on the opposite sides of the face $j_0\ldots j_{n-1}$, which implies that the simplexes $a j_0\ldots j_{n-1}$ and $b j_0\ldots j_{n-1}$ have the opposite orientations relative to that of $M$. Hence,

 $$ \sigma^{a j_{0}\cdots j_{n-1}}+\sigma^{b j_{0}\cdots j_{n-1}}=0, $$ 

which means that the term  $ e_{j_0\ldots j_{n-1}} $ cancels out in the sum  $ \partial\left(\sigma^A e_A + \sigma^B e_B\right) $ and, hence, in  $ \partial\sigma $. This proves that  $ \partial\sigma = 0 $.

The closed paths σ defined by (4.8) is called a surface path of M (or T).

There is a number of triangulations when a surface path  $ \sigma $ happens to be exact, that is,  $ \sigma = \partial v $ for some  $ (n+1) $-path  $ v $. If this is the case then  $ v $ is called a solid path as in this case  $ v $ represents a “solid” shape whose boundary is given by  $ M $ (or  $ T $).

Example 4.8 If  $ M = \mathbb{S}^1 $ then  $ T $ is a cycle graph, and a surface path  $ \sigma $ in this case was constructed in the proof of Proposition 4.7. We have seen there that  $ \sigma $ is exact if the digraph  $ G $ is a triangle or square, and non-exact otherwise. In the former case a solid paths  $ v $ represents a triangle or a square, respectively, in the latter case a solid path does not exist.

Example 4.9 Let  $ M = \mathbb{S}^n $ and let the faces of a triangulation  $ T $ of  $ M $ form a  $ (n+1) $-simplex, so that the digraph  $ G $ is a  $ (n+1) $-simplex digraph. Denoting the vertices by  $ 0,1,\ldots,n+1 $, we obtain  $ \partial e_{0\ldots n+1} = \sigma $ so that  $ e_{i_0\ldots i_{n+1}} $ is a solid path representing a solid  $ (n+1) $-simplex.

There are also higher dimensional examples when a surface path is not exact, see Example 6.17 below. Further examples of surface and solid paths will be given in Section 7.

### 4.8 Lemma of Sperner revisited

Consider a triangle  $ ABC $ on the plane  $ R^2 $ and its triangulation  $ T $. The set of vertices of  $ T $ is colored with three colors  $ 1, 2, 3 $ in such a way that

• the vertices A, B, C are colored with 1, 2, 3 respectively;

- each vertex on any edge of ABC is colored with one of the two colors of the endpoints of the edge (see Fig. 10).

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e5d67364-6d3a-4a3d-af1e-67681318d208/markdown_2/imgs/img_in_image_box_425_432_788_744.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A09Z%2F-1%2F%2F6a22050a4eccedf93ac07201a751235a844a44306bb313fc0e8963ffe94caf4b" alt="Image" width="29%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 10: A Sperner coloring</div> </div>


The classical lemma of Sperner says that then there exists in T a 3-color triangle, that is, a triangle, whose vertices are colored with the three different colors. Moreover, the number of such triangles is odd.

We give here a new proof using the boundary operator  $ \partial $ for 1-paths. Although this proof is no shorter than the classical proof based on a double counting argument, it still provides a new insight into the subject, that 3-color triangles appear as sources and sinks of some “vector field” on a digraph.

Let us first do some reauction. Firstly, let us moaity the trianguation 1 so that there are no vertices on the edges AB, AC, BC except for A, B, C. Indeed, if X is a vertex on AB then we move X a bit inside the triangle ABC. This gives rise to a new triangle in the triangulation T that is formed by X and its former neighbors, say Y and Z, on the edge AB (while keeping all old triangles). However, since all X, Y, Z are colored with two colors, no 3-color triangle emerges after that move. By induction, we remove all the vertices from the edges of ABC.

Secondly, we project the triangle  $ ABC $ and the triangulation  $ T $ onto the sphere  $ \mathbb{S}^2 $ and add to the set  $ T $ the triangle  $ ABC $ itself from the other side of the sphere. Then we obtain a triangulation of  $ \mathbb{S}^2 $, denote it again by  $ T $, and we need to prove that the number of 3-color triangles is even. Indeed, since we know that one of the triangles, namely,  $ ABC $ is 3-color, this would imply that the number of 3-color triangles in the original triangulation is odd.

Let us regard T as a graph on  $ S^{2} $ and construct a dual graph V. Chose at each face of T a point and regard them as vertices of the dual graph V. The vertices in V are connected if the corresponding triangles in T have a common edge (see Fig. 11). Then the faces of V are in one-to-one correspondence to the vertices of T.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e5d67364-6d3a-4a3d-af1e-67681318d208/markdown_3/imgs/img_in_image_box_473_162_731_405.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A11Z%2F-1%2F%2F8a88f29f1297645b6f78da8a2c575ac554ec18081420459dee1e07ff5beae65c" alt="Image" width="21%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 11: Construction of a dual graph</div> </div>


Hence, given a graph V on  $ S^{2} $ such that each vertex has degree 3 and each face is colored with one of the colors 1, 2, 3, we need to prove that the number of 3-color vertices (that is, the vertices, whose adjacent faces have all three colors) is even.

Let us make V into a digraph as follows. Each edge  $ \xi $ in V has two adjacent faces. Choose the orientation on  $ \xi $ so that the color from the left hand side and that from the right hand side of  $ \xi $ form one of the following pairs:  $ (1,2) $,  $ (2,3) $,  $ (3,1) $ (see Fig. 12), while if the colors are the same then allow both orientations of  $ \xi $.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e5d67364-6d3a-4a3d-af1e-67681318d208/markdown_3/imgs/img_in_image_box_320_731_880_812.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A11Z%2F-1%2F%2Fb6d0cd998231dd74fba89c452caf8db16696952e86726bcd008825dd385de4d1" alt="Image" width="45%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 12: The orientation of an edge depends on the colors of adjacent faces</div> </div>


Examples of such orientations are shown on Fig. 13.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e5d67364-6d3a-4a3d-af1e-67681318d208/markdown_3/imgs/img_in_image_box_292_969_883_1213.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A11Z%2F-1%2F%2Fd93b8733a01df8114f3e0ad6023778089426ab45c92c4268e6b2dde6601b9a36" alt="Image" width="48%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 13: Oriented edges in the dual graph  $ (V, E) $</div> </div>


Denote by E the set of the oriented edges and set  $ v = \sum_{\{ab \in E\}} e_{ab} $. We have for any  $ a \in V $

 $$ (\partial v)_{a}=\sum_{b}v^{ba}-\sum_{c}v^{ac}=\#\{incoming edges\}-\#\{outcoming edges\}, $$ 

where #A denotes the number of elements in the set A. If a is 3-color, then either all three edges at a are incoming or all are outcoming, whence  $ (\partial v)_{a} = 3 $ or -3, respectively. If a is not

3-color then  $ (\partial v)_a = 0 $ (cf. Fig. 13). Denoting by  $ n_1 $ the number of 3-color edges with incoming orientation and by  $ n_2 $ that with outcome orientation, we obtain that  $ (\partial v, 1) = 3(n_1 - n_2) $. On the other hand,  $ (\partial v, 1) = (v, d1) = 0 $ whence we conclude that  $ n_1 = n_2 $. In particular, the total number of 3-color vertices is  $ 2n_1 $, that is, even, which was to be proved. In fact, we have proved a bit more: in a triangulation of a sphere, the numbers of 3-color triangles of the opposite orientations are the same.

## 5 Homologies of subgraphs

### 5.1 Chain complex of a subgraph

Let  $ G' = (V', E') $ and  $ G = (V, E) $ be two digraph. We say that  $ G' $ is a subgraph of  $ G $ if  $ V' \subset V $ and  $ E' \subset E $. Let us mark by the dash "'\" all the notation related to the graph  $ G' $ rather than to  $ G $, for example,  $ \mathcal{R}_p' \equiv \mathcal{R}_p(G') $ while  $ \mathcal{R}_p \equiv \mathcal{R}_p(G) $.

As it was already observed (cf. (2.12)),  $ \mathcal{R}_p' \subset \mathcal{R}_p $ and  $ \partial $ commutes with this inclusion. It is also obvious that if  $ e_{i_0\ldots i_p} $ is an allowed path in  $ G' $ then it is also allowed in  $ G $, whence  $ \mathcal{A}_p' \subset \mathcal{A}_p $. Moreover, this argument shows that

 $$ \mathcal{A}_{p}^{\prime}=\mathcal{A}_{p}\cap\mathcal{R}_{p}^{\prime}. $$ 

By the definition (3.8) of  $ \Omega_p $, we obtain that  $ \Omega_p' \subset \Omega_p $ and  $ \partial $ commutes with this inclusion. Consequently, the chain complex

 $$ 0\quad\leftarrow\quad\Omega_{0}^{\prime}\quad\stackrel{\partial}{\leftarrow}\quad\Omega_{1}^{\prime}\quad\stackrel{\partial}{\leftarrow}\quad\Omega_{2}^{\prime}\quad\stackrel{\partial}{\leftarrow}\quad\Omega_{3}^{\prime}\quad\stackrel{\partial}{\leftarrow}\dots. $$ 

is a sub-complex of

 $$ 0~\leftarrow~\Omega_{0}~\stackrel{\partial}{\leftarrow}~\Omega_{1}~\stackrel{\partial}{\leftarrow}~\Omega_{2}~\stackrel{\partial}{\leftarrow}~\Omega_{3}~\stackrel{\partial}{\leftarrow}~\ldots $$ 

By Proposition 9.7 (cf. (9.22)) we obtain that the following long sequence is exact:

 $$ 0\leftarrow H_{0}(\Omega/\Omega^{\prime})\leftarrow H_{0}(\Omega)\leftarrow H_{0}(\Omega^{\prime})\leftarrow\cdots\leftarrow H_{p}(\Omega/\Omega^{\prime})\leftarrow H_{p}(\Omega)\leftarrow H_{p}(\Omega^{\prime})\leftarrow H_{p+1}(\Omega/\Omega^{\prime})\leftarrow\cdots $$ 

It is also worth mentioning that

 $$ \Omega_{p}^{\prime}=\Omega_{p}\cap\mathcal{A}_{p}^{\prime}=\Omega_{p}\cap\mathcal{R}_{p}^{\prime}. $$ 

Indeed, the inclusions  $ \Omega_p' \subset \Omega_p \cap \mathcal{A}_p' \subset \Omega_p \cap \mathcal{R}_p' $ are obvious. To prove the opposite inclusions, observe that  $ v \in \Omega_p \cap \mathcal{R}_p' $ implies by (3.8) and (5.1)

 $$ v\in\mathcal{A}_{p}\cap\mathcal{R}_{p}^{\prime}=\mathcal{A}_{p}^{\prime}\quad and\quad\partial v\in\mathcal{A}_{p-1}\cap\mathcal{R}_{p-1}^{\prime}=\mathcal{A}_{p-1}^{\prime}, $$ 

whence v ∈ Ω′p.

### 5.2 Removing a vertex of degree 1

Theorem 5.1 Suppose that a graph  $ G $ has a vertex  $ a $ such that there is only one outcoming edge  $ a \to b $ from  $ a $ and no incoming edges to  $ a $. Let  $ G' = (V', E') $ be the digraph with  $ V' = V \setminus \{a\} $ and  $ E' = E \setminus \{ab\} $.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e5d67364-6d3a-4a3d-af1e-67681318d208/markdown_4/imgs/img_in_image_box_449_1356_743_1435.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A12Z%2F-1%2F%2Fff92741cb8737846061bd9ef002d89fcb05f1284d86162564513def98b890ffb" alt="Image" width="24%" /></div>


Then  $ H_p(G) \cong H_p(G') $ for all  $ p \geq 0 $.

Remark 5.2 The same is true if the vertex a has one incoming edge  $ b \rightarrow a $ and no outcoming edges.

Theorem 5.1 is a particular case of a more general Theorem 5.4 from the next section. We give here an independent proof based on the identity (5.4) below that may be interesting on its own right.

Proof. Let us first prove that

 $$ \Omega_{p}=\Omega_{p}^{\prime}for all p\geq2, $$ 

which will imply that, for all p ≥ 2,

 $$ \dim H_{p}\left(\Omega^{\prime}\right)=\dim H_{p}\left(\Omega\right). $$ 

In the view of (5.3), to prove (5.4) it suffices to show that, for all p ≥ 2,

 $$ \Omega_{p}\subset\mathcal{A}_{p}^{\prime}, $$ 

that is

 $$ v\in\mathcal{A}_{p}\mathrm{a n d}\partial v\in\mathcal{A}_{p-1}\Rightarrow v\in\mathcal{A}_{p}^{\prime}. $$ 

Every elementary allowed p-path on G either is allowed on  $ G' $ or starts with ab, which implies that v can be represented in the form

 $$ v=e_{a b}u+v^{\prime}, $$ 

where  $ v' \in \mathcal{A}_p' $, while  $ u \in \mathcal{A}_{p-2}' $ is a linear combination of the paths  $ e_{i_0...i_{p-2}} \in \mathcal{A}_{p-2}' $ with  $ i_0 \neq b $. It follows that

 $$ \partial v=\left(e_{b}-e_{a}\right)u+e_{a b}\partial u+\partial v^{\prime}. $$ 

Note that $e_a u$ is a linear combination of the elementary paths $e_{ai_0...i_{p-2}}$ where $i_0, ..., i_{p-2} \in V'$ and $i_0 \neq b$. Since $ai_0$ is not an edge, those elementary paths are not allowed in $G$. No other terms in the right hand side of (5.7) has $e_{ai_0...i_{p-2}}$-component. Since $\partial v$ is allows in $G$, its $e_{ai_0...i_{p-2}}$-component is 0, which is only possible if $e_a u = 0$, that is, $u = 0$. It follows that $v = v' \in \mathcal{A}_p$, which finishes the proof of (5.6).

Hence, we have the identity (5.5) for  $ p \geq 2 $. For p = 0 this identity also true as the number of connected components of G and  $ G' $ is the same.

We are left to treat the case p = 1. Observe that

 $$ \Omega_{0}=\Omega_{0}^{\prime}+\mathrm{s p a n}\left\{e_{a}\right\}\quad\mathrm{a n d}\quad\Omega_{1}=\Omega_{1}^{\prime}+\mathrm{s p a n}\left\{e_{a b}\right\}. $$ 

By (5.4) and (5.8) the cochain complex  $ \Omega/\Omega' $ has the form

 $$ 0\longleftarrow\operatorname{s p a n}\left\{e_{a}\right\}\stackrel{\partial}{\longleftarrow}\operatorname{s p a n}\left\{e_{a b}\right\}\longleftarrow0=\Omega_{2}/\Omega_{2}^{\prime}. $$ 

Since

 $$ \partial e_{a b}=e_{b}-e_{a}=-e_{a}\bmod\Omega_{0}^{\prime}, $$ 

it follows that  $ \mathrm{Im} \partial_{|\Omega_{1}/\Omega_{1}^{\prime}} = \mathrm{span} \{e_{a}\} $, while  $ \ker \partial_{|\Omega_{1}/\Omega_{1}^{\prime}} = 0 $, whence

 $$ \dim H_{0}\left(\Omega/\Omega^{\prime}\right)=\dim H_{1}\left(\Omega/\Omega^{\prime}\right)=0. $$ 

By (5.2) we have a long exact sequence

 $$ H_{0}\left(\Omega/\Omega^{\prime}\right)=0\xleftarrow{\quad}H_{1}\left(\Omega\right)\xleftarrow{\quad}H_{1}\left(\Omega^{\prime}\right)\xleftarrow{\quad}0=H_{1}\left(\Omega/\Omega^{\prime}\right) $$ 

which implies that

 $$ \dim H_{1}\left(\Omega\right)=\dim H_{1}\left(\Omega^{\prime}\right), $$ 

thus finishing the proof. ■

Corollary 5.3 Let a digraph G be a tree (that is, the underlying undirected graph is a tree). Then  $ H_p(G) = 0 $ for all  $ p \geq 1 $.

Proof. Induction in the number of edges  $ |E| $. If  $ |E| = 0 $ then the claim is obvious. If  $ |E| > 0 $ then there is a vertex  $ a \in V $ of degree 1 (indeed, if this is not the case then moving along undirected edges allows to produce a cycle). Removing this vertex and the adjacent edge, we obtain a tree  $ G' $ with  $ |E'| < |E| $. By the inductive hypothesis  $ H_p(G') = 0 $ for  $ p \geq 1 $, whence by Theorem 5.1 also  $ H_p(G) = 0 $.

That  $ H_p(G) = 0 $ for  $ p \geq 2 $ follows also from Theorem 4.3.

### 5.3 Removing a vertex of degree n

Theorem 5.4 Suppose that a digraph  $  G = (V, E)  $ has a vertex  $  a  $ with  $  n  $ outcoming edges  $  a \to b_0  $,  $  a \to b_1  $, ...,  $  a \to b_{n-1}  $ and no incoming edges. Assume also that  $  b_0 \to b_i  $ for all  $  i \geq 1  $:

 $$ \begin{aligned}&a\bullet\stackrel{\rightarrow}{\searrow}\begin{bmatrix}b_{1}&&\\ \uparrow&b_{0}&\cdots&G^{\prime}\\ \downarrow&&\\ \bullet b_{2}&&\end{bmatrix}\quad G\end{aligned} $$ 

Denote by  $ G' = (V', E') $ the digraph that is obtained from G by removing a vertex a with all adjacent edges, that is,  $ V' = V \setminus \{a\} $ and  $ E' = E \setminus \{ab_i\}_{i=0}^{n-1} $. Then, for any  $ p \geq 0 $,

 $$ \dim H_{p}\left(G\right)=\dim H_{p}\left(G^{\prime}\right). $$ 

Remark 5.5 The same is true if a vertex $a$ has $n$ incoming edges $b_0 \to a, b_1 \to a, ..., b_{n-1} \to a$ and no outcoming edges, while $b_i \to b_0$ for all $i \geq 1$:

 $$ \begin{aligned}&\begin{vmatrix} \\{{{\bulletb_{1}}}} \\{{{\downarrow}}} \\{{{\bulletb_{0}}}}&{{{\cdots}}}&{{{G^{\prime}}}} \\{{{\uparrow}}} \\{{{\bulletb_{2}}}} \\\end{vmatrix}\quad G\\ \end{aligned} $$ 

Theorem 5.4 can be regarded as a discrete analogous of the classical result of homotopy invariance of homologies on manifolds.

Example 5.6 Consider a digraph G as shown in Fig. 14.

Each of the vertices  $ a_k $ satisfies the hypotheses of Theorem 5.4 with  $ n = 2 $ (either with incoming or outcoming edges). Removing successively the vertices  $ a_k $, we see that all the homologies of  $ G $ are the same as those of the remaining graph  $ b \bullet \rightarrow \bullet^c $. Since it is a star-shaped graph, we obtain  $ \dim H_0 = 1 $ and  $ \dim H_p = 0 $ for all  $ p \geq 1 $. In particular,  $ \chi = 1 $.

Note that for this digraph

 $$ \dim\Omega_{0}=m+n+2,\ \dim\Omega_{1}=2m+2n+1. $$ 

Using Proposition 4.2 and observing that the number of semi-edges is mn, we obtain

 $$ \dim\Omega_{2}=m+n+m n, $$ 

where the basis in $\Omega_{2}$ is given by the triangles $e_{a_{-k}bc}$, $e_{bca_{l}}$ and squares $e_{a_{-k}ba_{l}} - e_{a_{-k}ca_{l}}$. Finally, we have

 $$ \dim\Omega_{3}=\dim\mathcal{A}_{3}=mn $$ 

where the basis in Ω3 is determined by the snakes e a−k bcal, and dim Ωp = 0 for all p > 3.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e3f4392e-9b63-4427-a2f9-040d001411bb/markdown_2/imgs/img_in_image_box_310_174_905_384.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A12Z%2F-1%2F%2Fcb4f6ae72e95ec84b3f0c7ba0f19578ca66547b8f08cc50ea8f1782b54e5cf4c" alt="Image" width="48%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 14: A digraph with many triangles and squares</div> </div>


Proof of Theorem 5.4. Since the number of connected components of the graphs G and  $ G' $ is obviously the same, the identity (5.9) for p = 0 follows from Proposition 3.24.

For  $ p \geq 1 $ consider the long exact sequence (5.2), that is,

 $$ \begin{array}{r}{\dots\leftarrow H_{p}\left(\Omega/\Omega^{\prime}\right)\leftarrow H_{p}\left(\Omega\right)\leftarrow H_{p}\left(\Omega^{\prime}\right)\leftarrow H_{p+1}\left(\Omega/\Omega^{\prime}\right)\leftarrow\dots,}\end{array} $$ 

that implies the identity

 $$ \dim H_{p}\left(\Omega\right)=\dim H_{p}\left(\Omega^{\prime}\right)\quad for p\geq1, $$ 

if we prove that

 $$ \dim H_{p}\left(\Omega/\Omega^{\prime}\right)=0\text{for}p\geq1. $$ 

The condition  $ (5.10) $ means that

 $$ \ker\partial|_{\Omega_{p}/\Omega_{p}^{\prime}}\subset\operatorname{Im}\partial|_{\Omega_{p+1}/\Omega_{p+1}^{\prime}} $$ 

that is, if

 $$ v\in\Omega_{p}\mathrm{a n d}\partial v=0\bmod\Omega_{p-1}^{\prime} $$ 

then there exists  $ \omega \in \Omega_{p+1} $ such that

 $$ \partial\omega=v\bmod\Omega_{p}^{\prime}. $$ 

In fact, it suffices to prove the existence of  $ \omega \in \mathcal{A}_{p+1} $ such that

 $$ \partial\omega=v\bmod{\mathcal{A}_{p}^{\prime}}. $$ 

Indeed, (5.13) implies  $ \partial\omega \in \mathcal{A}_p $ and, hence,  $ \omega \in \Omega_{p+1} $. Since  $ \partial\omega - v \in \mathcal{A}_p' $ and

 $$ \partial\left(\partial\omega-v\right)=-\partial v\in\mathcal{A}_{p-1}^{\prime}, $$ 

it follows that  $ \partial\omega - v \in \Omega_v' $ which proves (5.12).

To prove the existence of  $ \omega $ as above, observe that  $ \nu $ can be represented in the form

 $$ v=e_{a}u\bmod{\mathcal{A}_{p}^{\prime}}, $$ 

where  $ u \in \mathcal{A}'_{p-1} $ and  $ e_a u \in \mathcal{A}_p $. We have then

 $$ \partial v=u-e_{a}\partial u\bmod\mathcal{R}_{p-1}^{\prime}. $$ 

Since  $ \partial v, u \in \mathcal{A}_{p-1}' $, it follows that

 $$ e_{a}\partial u=0\bmod{\mathcal{R}_{p-1}^{\prime}}. $$ 

However, all components of the path  $ e_a \partial u $ start with  $ e_{a...} $, whereas the condition (5.15) means that the path  $ e_a \partial u $ has no such component. Hence, (5.15) is only possible if  $ \partial u = 0 $.

Since  $ e_a u \in \mathcal{A}_p $, any component of  $ u $ has the form  $ e_{b_i} \ldots $, which, together with the hypothesis that  $ b_0 b_i $ is an edge, implies that  $ e_{b_0} u \in \mathcal{A}_p' $ and  $ e_{ab_0} u \in \mathcal{A}_{p+1} $. Using  $ \partial u = 0 $ and (5.14), we obtain

 $$ \partial\left(e_{a b_{0}}u\right)=\left(e_{b_{0}}-e_{a}\right)u+e_{a b_{0}}\partial u=e_{b_{0}}u-e_{a}u=-v\bmod\mathcal{A}_{p}^{\prime}, $$ 

so that (5.13) holds with  $ \omega = -e_{ab_0}u $. ■

### 5.4 Removing a vertex of degree  $ 1+1 $

Recall that a pair  $ c_b $ of distinct vertices on a graph is a semi-edge if  $ c_b $ is not an edge but there is a vertex  $ j $ such that  $ c_j $ and  $ j_b $ are edges:

 $$ \begin{array}{l}\bullet b\\ 1 \quad \stackrel{<}{\rightarrow} \bullet j\\ \bullet c \end{array} $$ 

In the next theorem the field K has characteristic 0.

Theorem 5.7 Suppose that a graph  $  G = (V, E)  $ has a vertex a such that there is only one outcoming edge  $  a \to b  $ from a and only one incoming edge  $  c \to a  $, where  $  b \neq c  $. Consider the digraph  $  G' = (V', E')  $ where  $  V' = V \setminus \{a\}  $ and  $  E' = E \setminus \{ab, ca\}  $.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e3f4392e-9b63-4427-a2f9-040d001411bb/markdown_3/imgs/img_in_image_box_457_865_735_984.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A14Z%2F-1%2F%2F839293b25f8992b25d299593254ca0919d7ce5a5e140fca06de56a6a83972dc9" alt="Image" width="22%" /></div>


Then the following is true.

(a) For any  $ p \geq 2 $,

 $$ \dim H_{p}\left(G\right)=\dim H_{p}(G^{\prime}). $$ 

(b) If cb is an edge or a semi-edge in  $ G' $ then (5.16) is satisfied also for p = 0,1, that is, for all  $ p \geq 0 $.

(c) If cb is neither edge nor semi-edge in  $ G' $, but b,c belong to the same connected component of  $ G' $ then

 $$ \dim H_{1}\left(G\right)=\dim H_{1}(G^{\prime})+1 $$ 

and  $ \dim H_{0}(G)=\dim H_{0}(G^{\prime}) $.

(d) If b, c belong to different connected components of  $ G' $ then

 $$ \dim H_{1}\left(G\right)=\dim H_{1}(G^{\prime}) $$ 

and  $ \dim H_{0}(G)=\dim H_{0}(G^{\prime})-1. $

Consequently, in the case  $ (b) $,  $ \chi(G) = \chi(G') $, whereas in the cases  $ (c) $ and  $ (d) $,  $ \chi(G) = \chi(G') - 1 $.

Example 5.8 Consider the graphs

 $$ G=\stackrel{a}{\underset{}{\bullet}{\stackrel{\nearrow}{\leftarrow}}}\stackrel{b}{\downarrow}\stackrel{\nearrow}{\underset{}{\bullet}{\stackrel{\nearrow}{\leftarrow}}}\stackrel{d}{\quad}and\quad G^{\prime}=\stackrel{b}{\downarrow}\stackrel{\nearrow}{\underset{}{\bullet}{\stackrel{\nearrow}{\leftarrow}}}\stackrel{d}{\quad}\begin{array}{c}\bullet\\ \bullet\\ \bullet\\ \bullet\\ \end{array} $$ 

Since  $ c_b $ is semi-edge in  $ G' $ we have case (b) so that all homologies of  $ G $ and  $ G' $ are the same. Removing further vertex  $ d $ we obtain a digraph

 $$ G^{\prime\prime}={}^{b}\bullet\rightarrow\bullet^{c} $$ 

It is a star-shaped graph whence  $ \dim H_p(G'') = 0 $ for  $ p \geq 1 $. Since  $ c_b $ is neither edge nor semi-edge in  $ G'' $, but the graph  $ G'' $ is connected, we conclude by case (c) that

 $$ \dim H_{1}\left(G^{\prime}\right)=\dim H_{1}\left(G^{\prime \prime}\right)+1=1. $$ 

and Hp (G′) = Hp (G′′) for p ≥ 2. It follows that dim Hp (G) = 0 for p ≥ 2 and dim H1 (G) = 1.

Example 5.9 Consider a digraph as on Fig. 15 (a kind of anti-snake).

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e3f4392e-9b63-4427-a2f9-040d001411bb/markdown_4/imgs/img_in_image_box_335_768_909_945.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A15Z%2F-1%2F%2Fa4630366b0c6218d7bb9ee85544266caedc345ced1f3f242cca84df2d0ea3b59" alt="Image" width="46%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 15: An anti-snake</div> </div>


We start building this graph with  $ 1 \rightarrow 2 $. Since 21 is neither edge nor semi-edge, adding a path  $ 2 \rightarrow 3 \rightarrow 1 $ increases  $ \dim H_1 $ by 1 and preserves other homologies. Since 23 is an edge, adding a path  $ 2 \rightarrow 4 \rightarrow 3 $ preserves all homologies. Since 34 is neither edge nor semi-edge, adding a path  $ 3 \rightarrow 5 \rightarrow 4 $ increases  $ \dim H_1 $ by 1 and preserves other homologies. Similarly, adding a path  $ 5 \rightarrow 6 \rightarrow 4 $ preserves all homologies.

One can repeat this pattern arbitrarily many times. By doing so we construct a digraph with a prescribed positive value of  $ \dim H_1 $ while keeping  $ \dim H_p = 0 $ for all  $ p \geq 2 $. Consequently, the Euler characteristic  $ \chi $ can take arbitrary negative values.

Example 5.10 Consider a digraph on Fig. 2. By Theorem 5.4, we can remove the vertices 5 and 8 (and their adjacent edges) without change of homologies. Then by the same theorem we can remove 4 and 7. By Theorem 5.7 we can remove the vertex 1. The resulting graph with the vertices 0, 2, 3, 6 is star-shaped, so that by Theorem 4.6 the homology groups  $ H_p $ are trivial for all  $ p \geq 1 $, while  $ \dim H_0 = 1 $.

Proof of Theorem 5.7. Proof of (a). The identity (5.16) for  $ p \geq 2 $ will follow if if prove that

 $$ \dim H_{p}\left(\Omega/\Omega^{\prime}\right)=0 for p\geq2. $$ 

In order to prove  $ (5.17) $ it suffices to show that

 $$ \ker\partial|_{\Omega_{p}/\Omega_{p}^{\prime}}=0, $$ 

which is equivalent to

 $$ v\in\Omega_{p},\quad\partial v=0\bmod\Omega_{p-1}^{\prime}\Rightarrow v=0\bmod\Omega_{p}^{\prime}. $$ 

By the definition (3.8) of  $ \Omega_{p} $, (5.18) is equivalent to

 $$ v\in\mathcal{A}_{p}\mathrm{~a n d~}\partial v\in\mathcal{A}_{p-1}^{\prime}\Rightarrow v\in\mathcal{A}_{p}^{\prime}. $$ 

Hence, let us prove (5.19) for all  $ p \geq 2 $.

Every elementary allowed $p$-path on $G$ either contains one of the edges $ab$, $ca$ or is allowed in $G'$. Let us show that, for any $v$ as in (5.19), its components $v^{...ab...}$ and $v^{...ca...}$ vanish, which will imply that $v \in \mathcal{A}_p$. Any such component can be written in the form $v^{\alpha ab\beta}$ or $v^{\gamma ca\beta}$ where $\alpha, \beta, \gamma$ are some paths. Consider the following cases. For further applications, in the Cases 1,2 we assume only that $v \in \Omega_p$ (whereas in the Case 3 $v$ is as in (5.19)).

Case 1. Let us consider first the component  $ v^{\alpha ab\beta} $ where  $ \beta $ is non-empty. If  $ \alpha ab\beta $ is not allowed in  $ G $ then  $ v^{\alpha ab\beta} = 0 $ by definition. Let  $ \alpha ab\beta $ be allowed in  $ G $. The path  $ \alpha a\beta $ is not allowed because the only outcoming edge from  $ a $ is  $ ab $. Since  $ \partial v \in \mathcal{A}_{p-1} $, we have

 $$ (\partial v)^{\alpha a\beta}=0. $$ 

Let us show that

 $$ (\partial v)^{\alpha a\beta}=\pm v^{\alpha a b\beta}, $$ 

which will imply  $ v^{\alpha ab\beta} = 0 $. Indeed, by (2.4)  $ \left(\partial v\right)^{\alpha a\beta} $ is the sum of the terms  $ \pm v^\omega $ where  $ \omega $ is a p-path that is obtained from  $ \alpha a\beta $ by inserting one vertex. Since there is no edge from a to  $ \beta $, the only way  $ \omega $ can be allowed is when  $ \omega = \alpha ab\beta $. Since for any other  $ \omega $ we have  $ v^\omega = 0 $, we obtain (5.20), which implies that  $ v^{\alpha ab\beta} = 0 $.

Case 2. In the same way one proves that  $ v^{\gamma ca\beta} = 0 $ provided  $ \gamma $ is non-empty, using the fact that the only incoming edge in a is ca.

Case 3. Consider now an arbitrary component  $ v^{\alpha ab\beta} $. If  $ \beta $ is non-empty then  $ v^{\alpha ab\beta} = 0 $ by Case 1. Let  $ \beta $ be empty. Then  $ \alpha $ must have the form  $ \alpha = \gamma c $ so that  $ v^{\alpha ab\beta} = v^{\gamma cab} $. If  $ \gamma $ is non-empty then  $ v^{\gamma cab} = 0 $ by Case 2. Finally, let  $ \gamma $ be also empty so that  $ v^{\alpha ab\beta} = v^{\gamma cab} $ (which is only possible if  $ p = 2 $). Since  $ \partial v \in \mathcal{A}_1' $, we have

 $$ (\partial v)^{a b}=0. $$ 

On the other hand,

 $$ (\partial v)^{a b}=\sum_{i\in V}v^{i a b}-v^{a i b}+v^{a b i}. $$ 

Here all the terms of the form  $ v^{iab} $ vanish, except possibly for  $ v^{cab} $, because ia is not an edge unless i = c. All the terms  $ v^{aib} $ vanish because ai is not an edge. All the terms  $ v^{abi} $ vanish by Case 1. Hence, we obtain

 $$ (\partial v)^{a b}=v^{c a b} $$ 

whence  $ v^{cab}=0 $ follows, thus finishing the proof of the part (a).

Proof of  $ (b) $,  $ (c) $,  $ (d) $. If b, c belong to the same connected component of  $ G' $ then the number of connected components of G and that of  $ G' $ are the same, so that

 $$ \dim H_{0}\left(\Omega\right)=\dim H_{0}\left(\Omega^{\prime}\right), $$ 

whereas if b, c belong to different connected components of  $ G' $ then after joining them by a the number of connected components reduces by 1, so that

 $$ \dim H_{0}\left(\Omega\right)=\dim H_{0}\left(\Omega^{\prime}\right)-1. $$ 

To handle  $ H_{1} $ we use the long exact sequence (5.2) that by (5.17) has the form

 $$ 0\leftarrow H_{0}\left(\Omega/\Omega^{\prime}\right)\leftarrow H_{0}\left(\Omega\right)\leftarrow H_{0}\left(\Omega^{\prime}\right)\leftarrow H_{1}\left(\Omega/\Omega^{\prime}\right)\leftarrow H_{1}\left(\Omega\right)\leftarrow H_{1}\left(\Omega^{\prime}\right)\leftarrow0. $$ 

Since we know already the relation between  $ H_0(\Omega') $ and  $ H_0(\Omega) $, to obtain the relation between  $ H_1(\Omega') $ and  $ H_1(\Omega) $ we need to compute  $ \dim H_0(\Omega/\Omega') $ and  $ \dim H_1(\Omega/\Omega') $ from the quotient complex  $ \Omega/\Omega' $. Observe that

 $$ \Omega_{0}=\Omega_{0}^{\prime}+\mathrm{s p a n}\left\{e_{a}\right\},\quad\Omega_{1}=\Omega_{1}^{\prime}+\mathrm{s p a n}\left\{e_{a b},e_{c a}\right\} $$ 

so that the quotient complex  $ \Omega/\Omega' $ has the form

 $$ 0\longleftarrow\mathrm{s p a n}\left\{e_{a}\right\}\stackrel{\partial}{\longleftarrow}\mathrm{s p a n}\left\{e_{a b},e_{c a}\right\}\stackrel{\partial}{\longleftarrow}\Omega_{2}/\Omega_{2}^{\prime}\stackrel{\partial}{\longleftarrow}\ldots $$ 

We need to determine  $ \mathrm{Im} \partial_{|\Omega_{1}/\Omega_{1}^{\prime}} $,  $ \mathrm{ker} \partial_{|\Omega_{1}/\Omega_{1}^{\prime}} $,  $ \mathrm{Im} \partial_{|\Omega_{2}/\Omega_{2}^{\prime}} $. Since

 $$ \begin{array}{r}{\partial e_{a b}=e_{b}-e_{a}=-e_{a}\bmod\Omega_{0}^{\prime},}\end{array} $$ 

it follows that

 $$ \begin{aligned}&\mathrm{I m}\partial|_{\Omega_{1}/\Omega_{1}^{\prime}}=\Omega_{0}/\Omega_{0}^{\prime},\\ &\\&\dim H_{0}\left(\Omega/\Omega^{\prime}\right)=0.\\ \end{aligned} $$ 

whence

For any scalars  $ k, l \in \mathbb{K} $, we have

 $$ \partial(k e_{a b}+l e_{c a})=(l-k)e_{a}\bmod\Omega_{0}^{\prime}, $$ 

so that  $ \partial(ke_{ab} + le_{ca}) = 0 $ if and only if  $ k = l $, that is

 $$ \ker\partial|_{\Omega_{1}/\Omega_{1}^{\prime}}=\operatorname{s p a n}(e_{a b}+e_{c a})\bmod\Omega_{1}^{\prime}. $$ 

Let us now compute  $ \mathrm{Im}\partial|_{\Omega_2/\Omega_2'}  $. For any  $ v \in \Omega_2 $ we have by the above Cases 1,2 that  $ v^{abi} = v^{jca} = 0 $, which implies that  $ v $ has the form

 $$ v=v^{\prime}+v^{c a b}e_{c a b}, $$ 

where  $ v' \in \mathcal{A}_2' $. It follows that

 $$ \partial v=\partial v^{\prime}+v^{c a b}\left(e_{a b}-e_{c b}+e_{c a}\right). $$ 

Since all 1-paths $\partial v$, $e_{ab}$ and $e_{ca}$ belong to $\mathcal{A}_1$, it follows that $\partial v' - v^{cab}e_{cb} \in \mathcal{A}_1$ whence also $\partial v' - v^{cab}e_{cb} \in \mathcal{A}_1$. Therefore,

 $$ \partial v=v^{c a b}\left(e_{a b}+e_{c a}\right)\bmod\Omega_{1}^{\prime}. $$ 

Next consider two cases.

(i) Let  $ \Omega_{2} $ contain an element v with  $ v^{cab} \neq 0 $. Then by (5.29)

 $$ \mathrm{I m}\partial|_{\Omega_{2}/\Omega_{2}^{\prime}}=\mathrm{s p a n}\left(e_{a b}+e_{c a}\right)\mathrm{m o d}\Omega_{1}^{\prime}, $$ 

which together with  $ (5.26) $ implies

 $$ \dim H_{1}\left(\Omega/\Omega^{\prime}\right)=0. $$ 

Substituting (5.25) and (5.31) into the exact sequence (5.23), we obtain that the identity

 $$ \dim H_{p}\left(\Omega^{\prime}\right)=\dim H_{p}\left(\Omega\right) $$ 

holds for all  $ p \geq 0 $.

(ii) Assume that  $ v^{cab} = 0 $ for all  $ v \in \Omega_{2} $. Then by (5.29)

 $$ \mathrm{I m}\partial|_{\Omega_{2}/\Omega_{2}^{\prime}}=0, $$ 

which together with  $ (5.26) $ implies

 $$ \dim H_{1}\left(\Omega/\Omega^{\prime}\right)=1. $$ 

Using again the exact sequence  $ (5.23) $, that is,

 $$ 0\leftarrow H_{0}\left(\Omega\right)\leftarrow H_{0}\left(\Omega^{\prime}\right)\leftarrow H_{1}\left(\Omega/\Omega^{\prime}\right)\leftarrow H_{1}\left(\Omega\right)\leftarrow H_{1}\left(\Omega^{\prime}\right)\leftarrow0, $$ 

we obtain by  $ (9.7) $ and  $ (5.32) $

 $$ \dim H_{1}\left(\Omega^{\prime}\right)-\dim H_{1}(\Omega)+1-\dim H^{0}\left(\Omega^{\prime}\right)+\dim H^{0}(\Omega)=0 $$ 

Let us now specify when (i) or (ii) occur. Assume first that cb is an edge:

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//058cacb2-e40b-43b7-a8ff-05d3d30c9536/markdown_2/imgs/img_in_image_box_456_1012_738_1119.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A11Z%2F-1%2F%2Fae3ab5ce8c5cb6efb57a6168b51a0bd1e8903333ecf18d0d21ce0d131a0cea6e" alt="Image" width="23%" /></div>


Then

 $$ \partial e_{c a b}=e_{a b}-e_{c b}+e_{c a}\in\mathcal{A}_{1}, $$ 

whence it follows that  $ e_{cab} \in \Omega_2 $. Hence, we have the case (i) with  $ v = e_{cab} $.

Assume now that  $ cb $ is not an edge. Denote by  $ J $ the set of vertices  $ j \in V' $ such that the 2-path  $ cjb $ is allowed in  $ G' $:

 $$ \begin{array}{l}a\begin{array}{l}\bullet\stackrel{\bullet}{\leftarrow}\\ \bullet c\end{array}\stackrel{\bullet}{\rightarrow}\boxed{\bullet j\ldots J}\end{array} $$ 

Assume first that J is non-empty, that is, cb is a semi-edge, and set

 $$ v=e_{c a b}-\frac{1}{|J|}\sum_{j\in J}e_{c j b}, $$ 

where  $ |J| $ is the number of elements in  $ J $. It is clear that  $ v \in \mathcal{A}_2 $. We have

 $$ \begin{align*}\partial v\ &=\left(e_{ab}-e_{cb}+e_{ca}\right)-\frac{1}{|J|}\sum_{j\in J}\left(e_{jb}-e_{cb}+e_{cj}\right)\\&=\left(e_{ab}+e_{ca}\right)-\frac{1}{|J|}\sum_{i\in J}\left(e_{jb}+e_{cj}\right),\end{align*} $$ 

where the term  $ e_{cb} $ has cancelled out. It follows from (5.34) that  $ \partial v \in \mathcal{A}_1 $ whence  $ v \in \Omega_2 $, and we obtain again the case (i). This finishes the proof of (b).

Let us show that if  $ J = \emptyset $ (that is, when  $ c_b $ is neither edge nor semi-edge) then we have the case  $ (ii) $. Any 2-path  $ v \in \Omega_2 $ has the form (5.27) and  $ \partial_v $ is given by (5.28). It follows that

 $$ (\partial v)^{c b}=\left(\partial v^{\prime}\right)^{c b}-v^{c a b}. $$ 

Since  $ \partial v \in \mathcal{A}_1 $ and  $ cb $ is not an edge, we have  $ (\partial v)^{cb} = 0 $. We have by (2.4)

 $$ \left(\partial v^{\prime}\right)^{c b}=\sum_{j\in V^{\prime}}\left(v^{\prime}\right)^{j c b}-\left(v^{\prime}\right)^{c j b}+\left(v^{\prime}\right)^{c b j}, $$ 

which implies that  $ (\partial v')^{cb} = 0 $ as no elementary 2-path of the form  $ jcb, cjb, cbj $ is allowed in  $ G' $, whereas  $ v' \in \mathcal{A}_2' $. It follows that  $ v^{cab} = 0 $ so that we have the case (ii).

If in addition b, c belong to the same connected component of  $ G' $ then we have (5.21), that is,

 $$ \dim H^{0}(\Omega)=\dim H^{0}(\Omega^{\prime}). $$ 

Substituting into  $ (5.33) $, we obtain

 $$ \dim H_{1}\left(\Omega\right)=\dim H_{1}(\Omega^{\prime})+1. $$ 

which proves part (c).

If b, c belong to different components of  $ G' $ then we have by (5.22)

 $$ \dim H^{0}\left(\Omega\right)=\dim H^{0}(\Omega^{\prime})-1, $$ 

whence by  $ (5.33) $

 $$ \dim H_{1}\left(\Omega\right)=\dim H_{1}(\Omega^{\prime}), $$ 

which finishes the proof of part (d).

Finally, the identities for the Euler characteristic follow easily from the relations between  $ \dim H_{p}(\Omega) $ and  $ \dim H_{p}(\Omega') $. ■

## 6 Join of path complexes

In this and next sections we use slightly different way of denoting the path/form spaces associated with a given path complex as we will have to consider path complexes on more than one set. Given a finite set X, denote by  $ P(X) $ a path complex on X. The space  $ \mathcal{A}_p(P(X)) $ of all allowed p-paths (= finite K-linear combinations of elements from  $ P_p(X) $) will be denoted shortly by  $ \mathcal{A}_p(X) $. Similarly, the space  $ \Omega_p(P(X)) $ of all  $ \partial $-invariant p-paths will be denoted by  $ \Omega_p(X) $. Similar notation will apply to all other relevant notions including homologies  $ H_p(X) $, etc.

### 6.1 Definition and examples of a join

Definition 6.1 Given two disjoint finite sets X, Y and their path complexes  $ P(X) $,  $ P(Y) $, set  $ Z = X \sqcup Y $ and define a path complex  $ P(Z) $ as follows:  $ P(Z) $ consists of all paths of the form uv where  $ u \in P(X) $ and  $ v \in P(Y) $. The path complex  $ P(Z) $ is called a join of  $ P(X) $,  $ P(Y) $ and is denoted by  $ P(Z) = P(X) * P(Z) $.

An example of the path  $ uv \in P(Z) $ is given on Fig. 16. Note that each of  $ u, v $ can be empty so that all allowed paths on  $ X $ and  $ Y $ will also be allowed on  $ Z $.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//058cacb2-e40b-43b7-a8ff-05d3d30c9536/markdown_4/imgs/img_in_image_box_432_404_734_694.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A15Z%2F-1%2F%2Fa8579189a8e8ce68c2e15fe53527763f76a33022467990550964a333a28d30c4" alt="Image" width="24%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 16: A path uv</div> </div>


The operation  $ * $ on the path complexes is obviously non-commutative but associative.

Example 6.2 Let X, Y be digraphs and  $ P(X) $ and  $ P(Y) $ with the path complexes arising from their digraph structures. Consider the digraph Z whose set of vertices is  $ X \sqcup Y $, while the set of edges of Z consists of all the edges of X and Y, as well as of all the edges  $ x \to y $ for all  $ x \in X $ and  $ y \in Y $. The digraph Z is called a join of X and Y and is denoted by  $ X * Y $.

An example of a join of two digraphs is shown on Fig. 17.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//058cacb2-e40b-43b7-a8ff-05d3d30c9536/markdown_4/imgs/img_in_image_box_434_992_734_1276.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A15Z%2F-1%2F%2F034aefbd69dd407525c92c8ec350d8850042b6a269491d1e20492ccaa0828271" alt="Image" width="24%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 17: A digraph  $ Z = X \times Y $</div> </div>


Let  $ P(Z) $ be the path complex arising from the digraph structure of Z. Then it is obvious from the definition that  $ P(Z) $ is the join of  $ P(X) $ and  $ P(Y) $ so that

 $$ P\left(X*Y\right)=P\left(X\right)*P\left(Y\right). $$ 

Hence, the operation of joining of digraphs is a particular case of the operation of joining path complexes.

If Y consists of a single vertex a then  $ Z = X * Y $ is called a cone over X, and if Y consists of two vertices a, b and no edges then  $ Z = X * Y $ is called a suspension over X (see Sections 6.3 and 6.4 for more details).

Example 6.3 Let $X$ and $Y$ be the vertex sets of finite simplicial complexes $S(X)$ and $S(Y)$. Let us construct a simplicial complex $S(Z)$ with the vertex set $Z = X \sqcup Y$ as follows. Assuming that $|X| = n$ and $|Y| = m$, embed the set $X$ (together with all simplexes from $S(X)$) into a hyperplane $h^{n-1} \subset \mathbb{R}^{n+m-1}$ and $Y - \text{into a hyperplane } h^{m-1} \subset R^{n+m-1}$, where the hyperplanes $h^{n-1}, h^{m-1}$ are orthogonal and non-intersecting. For any two simplexes $\sigma_1 \in S(X)$ and $\sigma_2 \in S(Y)$, define their join $\sigma_1 * \sigma_2$ as the convex hull of $\sigma_1$ and $\sigma_2$ embedded in $\mathbb{R}^{n+m-1}$ as above (see Fig. 18).

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//4c48b8c4-4f55-4bfc-8fc8-99e975ae36a8/markdown_0/imgs/img_in_image_box_399_554_791_832.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A07Z%2F-1%2F%2F3970bf83b7f2366b4198efb4571cb9da7201179a9761aed59f133b7116467007" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 18: A join  $ \sigma_{1}*\sigma_{2} $ of two one-dimensional simplexes  $ \sigma_{1},\sigma_{2} $ (case n=m=2)</div> </div>


Due to a general position of  $ \sigma_1 $ and  $ \sigma_2 $, the join  $ \sigma_1 * \sigma_2 $ is also a simplex. Then  $ S(Z) $ is a collection of all simplexes  $ \sigma_1 * \sigma_2 $ with  $ \sigma_1 \in S(X) $ and  $ \sigma_2 \in S(Y) $. We refer to  $ S(Z) $ as a join of simplicial complexes  $ S(X) $,  $ S(Y) $ and denote it by  $ S(X) * S(Y) $.

Equivalently, one can define $S(Z)$ in an abstract way without embedding into a Euclidean space. Indeed, considering simplexes as sequences of vertices, we can say that $S(Z)$ consists of all simplexes of the form $[x_0, \ldots, x_p, y_0, \ldots, y_q]$ where $[x_0, \ldots, x_p] \in S(X)$ and $[y_0, \ldots, y_q] \in S(Y)$. It is clear that $S(Z)$ satisfies the defining property (3.2) of a simplicial complex, so that $S(Z)$ is a simplicial complex. It is also obvious that the path complexes $P(X), P(Y), P(Z)$ of the simplicial complexes $S(X), S(Y), S(Z)$, respectively, satisfy $P(Z) = P(X) * P(Y)$. Hence, the operation of joining of simplicial complexes is a particular case of the operation of joining path complexes.

Alternatively one can see the latter using Proposition 3.6: if both path complexes  $ P(X) $ and  $ P(Y) $ arise from simplicial complexes, that is, if they are monotone and perfect, then the path complex  $ P(X) \times P(Y) $ is also monotone and perfect. Hence, it arises from a simplicial complex with the vertex set Z.

Proposition 6.4 Let $P(X)$ and $P(Y)$ be two path complexes and let $P(Z) = P(X) * P(Y)$. If $u \in \Omega_p(X)$ and $v \in \Omega_q(Y)$ then $uv \in \Omega_{p+q+1}(Z)$. Moreover, the operation $u, v \mapsto uv$ of join extends to that for the homology classes $u \in \widetilde{H}_p(X)$ and $v \in \widetilde{H}_q(Y)$ so that $uv \in \widetilde{H}_{p+q+1}(Z)$.

Proof. If $u$ and $v$ are allowed then $uv$ is allowed on $Z$ by definition. In particular, if $u \in \Omega_p(X)$ and $v \in \Omega_q(Y)$ then $uv \in \mathcal{A}_{p+q+1}(Z)$. Let us show that $\partial(uv) \in \mathcal{A}_{p+q}(Z)$, which would imply $uv \in \Omega_{p+q+1}(Z)$. Indeed, we have

 $$ \partial\left(u v\right)=\left(\partial u\right)v+\left(-1\right)^{p+1}u\left(\partial v\right). $$ 

Since  $ \partial u $ and  $ \partial v $ are also allowed, we obtain that the right hand side here is allowed, whence the claim follows.

If  $ u, v $ are representatives of homology classes, that is, closed paths, then by (6.1) the join  $ uv $ is also closed, so that  $ uv $ represents a homology class of  $ Z $. We are left to verify that the class of  $ uv $ depends only on the classes of  $ u $ and  $ v $. For that it suffices to prove that if either  $ u $ or  $ v $ is exact then so is  $ uv $. Indeed, if  $ u = dw $ then

 $$ \partial\left(w v\right)=\left(\partial w\right)v+\left(-1\right)^{p}w\left(\partial v\right)=u v $$ 

so that uv is exact. ■

### 6.2 Chain complex of a join

Given a regular path complex $P(X)$ on a finite set $X$, we consider as before the paths spaces $\mathcal{R}_n(X), \mathcal{A}_n(X)$ and $\Omega_n(X)$, where $n \geq -1$. If $W_n(X)$ is one of these space then set

 $$ W_{n}^{\prime}\left(X\right)\equiv W_{n-1}\left(X\right). $$ 

The graded linear space  $ W' $ and  $ W_\bullet $ coincide as linear spaces but have slightly different graded structure. Recall that  $ \mathcal{R}_\bullet(X) $,  $ \mathcal{R}_\bullet'(X) $,  $ \Omega_\bullet(X) $,  $ \Omega_\bullet'(X) $ carry in addition the structure of chain complexes with respect to the regular boundary operator  $ \partial $.

In the next statement we use the notion of the tensor product of chain complexes (see Section 9.3 for definition).

Theorem 6.5 Let X,Y be two finite non-empty sets and  $ P(X) $ and  $ P(Y) $ be regular path complexes on X and Y respectively. Set  $ Z = X \sqcup Y $ and consider the join path complex

 $$ P\left(Z\right)=P\left(X\right)*P\left(Y\right). $$ 

We have the following isomorphism of the chain complexes:

 $$ \Omega_{\bullet}\left(Z\right)\cong\Omega_{\bullet}^{\prime}\left(X\right)\otimes\Omega_{\bullet}\left(Y\right), $$ 

where the mapping  $ \Omega_{\bullet}^{\prime}(X)\otimes\Omega_{\bullet}(Y)\to\Omega_{\bullet}(Z) $ is given by  $ u\otimes v\mapsto uv $.

In particular, for any r ≥ −1,

 $$ \Omega_{r}\left(Z\right)\cong\bigoplus_{\left\{p,q\geq-1:p+q=r-1\right\}}\left(\Omega_{p}\left(X\right)\otimes\Omega_{q}\left(Y\right)\right) $$ 

and, for any  $ r \geq 0 $,

 $$ \tilde{H}_{r}\left(Z\right)\cong\bigoplus_{\left\{p,q\geq0:p+q=r-1\right\}}\left(\tilde{H}_{p}\left(X\right)\otimes\tilde{H}_{q}\left(Y\right)\right) $$ 

(the Künneth formula for join).

It follows from (6.4) that

 $$ \dim\widetilde{H}_{r}\left(Z\right)=\sum_{\left\{p,q\geq0:p+q=r-1\right\}}\dim\widetilde{H}_{p}\left(X\right)\dim\widetilde{H}_{q}\left(Y\right). $$ 

If the both path complexes  $ P(X) $ and  $ P(Y) $ are connected then  $ \tilde{H}_0 = \{0\} $ for the both complexes (cf. Proposition 3.24), and (6.4) can be restated as follows: for any  $ r \geq 1 $

 $$ H_{r}\left(Z\right)\cong\bigoplus_{\left\{p,q\geq1:p+q=r-1\right\}}\left(H_{p}\left(X\right)\otimes H_{q}\left(Y\right)\right). $$ 

Proof. Let us first show how (6.3) and (6.4) follow from (6.2). By definition (6.2) means that

 $$ \Omega_{r}\left(Z\right)\cong\bigoplus_{\left\{p\geq0,q\geq-1:p+q=r\right\}}\left(\Omega_{p}^{\prime}\left(X\right)\otimes\Omega_{q}\left(Y\right)\right), $$ 

whence (6.3) follows by changing $p - 1$ to $p$. The isomorphism (6.2) of the chain complexes $\Omega_\bullet(Z)$ and $\Omega_\bullet'(X) \otimes \Omega_\bullet(Y)$ implies that their homologies are also isomorphic. On the other hand, by the Künneth theorem (9.12), we have

 $$ H_{\bullet}\left(\Omega_{\bullet}^{\prime}\left(X\right)\otimes\Omega_{\bullet}\left(Y\right)\right)\cong H_{\bullet}\left(\Omega_{\bullet}^{\prime}\left(X\right)\right)\otimes H_{\bullet}\left(\Omega_{\bullet}\left(Y\right)\right) $$ 

whence

 $$ H_{\bullet}\left(\Omega_{\bullet}\left(Z\right)\right)\cong H_{\bullet}\left(\Omega_{\bullet}^{\prime}\left(X\right)\right)\otimes H_{\bullet}\left(\Omega_{\bullet}\left(Y\right)\right). $$ 

More explicitly this means that, for any  $ r \geq -1 $,

 $$ \begin{array}{r l r}{H_{r}\left(\Omega_{\bullet}\left(Z\right)\right)}&{\cong}&{\bigoplus_{\left\{p^{\prime}\geq0,q\geq-1:p^{\prime}+q=r\right\}}\left(H_{p^{\prime}}\left(\Omega_{\bullet}^{\prime}\left(X\right)\right)\otimes H_{q}\left(\Omega_{\bullet}\left(Y\right)\right)\right)}\\ &{=}&{\bigoplus_{\left\{p,q\geq-1:p+q=r-1\right\}}\left(H_{p}\left(\Omega_{\bullet}\left(X\right)\right)\otimes H_{q}\left(\Omega_{\bullet}\left(Y\right)\right)\right).}\end{array} $$ 

Since the homology group  $ H_{-1}(\Omega_\bullet) $ is always trivial, the condition  $ p, q \geq -1 $ can be replaced here by  $ p, q \geq 0 $. Finally, observing that  $ H_p(\Omega_\bullet(X)) = \widetilde{H}_p(X) $ and  $ H_q(\Omega_\bullet(Y)) = \widetilde{H}_q(Y) $ are the reduced homologies, we obtain (6.4).

Now we concentrate on the proof of (6.2). We will consider here the path spaces  $ \{\mathcal{R}_p\}, \{\mathcal{A}_p\}, \{\Omega_p\} $ associated with the path complexes  $ P(X) $,  $ P(Y) $ and  $ P(Z) $. If  $ \{W_p\} $ is one of these families then set

 $$ W_{\bullet}\left(X,Y\right)=W_{\bullet}^{\prime}\left(X\right)\otimes W_{\bullet}\left(Y\right). $$ 

Then (6.2) can be restated as follows:

 $$ \Omega_{\bullet}\left(Z\right)\cong\Omega_{\bullet}\left(X,Y\right). $$ 

To prove this, we will construct explicitly a mapping

 $$ \Phi:\Omega_{r}\left(X,Y\right)\rightarrow\Omega_{r}\left(Z\right) $$ 

that will be isomorphism of linear spaces and will commute with the boundary operator  $ \partial $.

Consider first a larger the chain complex

 $$ \mathcal{R}_{\bullet}\left(X,Y\right)=\mathcal{R}_{\bullet}^{\prime}\left(X\right)\otimes\mathcal{R}_{\bullet}\left(Y\right) $$ 

and define for any  $ r \geq -1 $ the linear mapping

 $$ \Phi:\mathcal{R}_{r}\left(X,Y\right)\rightarrow\mathcal{R}_{r}\left(Z\right) $$ 

as follows: for all  $ u \in \mathcal{R}_p'(X) $ and  $ v \in \mathcal{R}_q(Y) $ with  $ p + q = r $, set

 $$ \Phi\left(u\otimes v\right)=u v, $$ 

where uv is the join of u and v on Z (note that X and Y are subsets of Z).

It follows from Lemma 2.6 that, for u, v as above,

 $$ \partial\left(u v\right)=\left(\partial u\right)v+(-1)^{p}u\partial v. $$ 

Here the operator $\partial$ is the boundary operator on $\mathcal{R}_{\bullet}(Z)$, but in the expressions $\partial u$ and $\partial v$ it coincides with the boundary operators on $\mathcal{R}_{\bullet}(X)$ and $\mathcal{R}_{\bullet}(Y)$, respectively. By (9.11) we have for the operator $\partial$ on $\mathcal{R}_{\bullet}(X,Y)$

 $$ \partial\left(u\otimes v\right)=\left(\partial u\right)\otimes v+(-1)^{p}u\otimes\partial v. $$ 

The comparison with (6.7) shows that the following diagram is commutative:

 $$ \begin{array}{ccc}\mathcal{R}_{r-1}\left(X,Y\right)&\xleftarrow{\partial}&\mathcal{R}_{r}\left(X,Y\right)\\\downarrow^{\Phi}&&\downarrow^{\Phi}\\\mathcal{R}_{r-1}\left(Z\right)&\xleftarrow{\partial}&\mathcal{R}_{r}\left(Z\right)\end{array} $$ 

Hence, the mapping  $ \Phi $ is a homomorphism of chain complexes  $ \mathcal{R}_{\bullet}(X,Y) $ and  $ \mathcal{R}_{\bullet}(Z) $.

Let us verify that $\Phi$ is in fact a monomorphism. Indeed, the basis in $\mathcal{R}_r(X,Y)$ consists of all elements of the form $e_x \otimes e_y$ where $x \in R_p(X), y \in R_q(Y)$ with $p+q = r$. Since $\Phi(e_x \otimes e_y) = e_{xy}$ and all such paths $e_{xy}$ are linearly independent in $\mathcal{R}_r(Z)$, we see that $\Phi$ is injective.

Next observe that

 $$ \Phi\left(\mathcal{A}_{r}\left(X,Y\right)\right)=\mathcal{A}_{r}\left(Z\right). $$ 

Indeed, the basis in  $ \mathcal{A}_r(X,Y) $ consists of all elements of the form  $ e_x \otimes e_y $ where  $ x \in R_p(X) $,  $ y \in R_q(Y) $ with  $ p+q = r $, while the basis in  $ \mathcal{A}_r(Z) $ consists of the paths  $ e_{xy} $ with the same set of  $ x,y $, whence the claim follows. In particular, the linear spaces  $ \mathcal{A}_r(X,Y) $ and  $ \mathcal{A}_r(Z) $ are isomorphic.

Now we aim at restricting  $ \Phi $ to  $ \Omega_{\bullet}(X,Y) $. In fact, we will prove that

 $$ \Phi\left(\Omega_{r}\left(X,Y\right)\right)=\Omega_{r}\left(Z\right), $$ 

for all  $ r \geq -1 $, which will finish the proof of (6.2). The inclusion

 $$ \Phi\left(\Omega_{r}\left(X,Y\right)\right)\subset\Omega_{r}\left(Z\right) $$ 

is trivial because by Proposition 6.4 $u \in \Omega_p'(X)$ and $v \in \Omega_q(Y)$ with $p+q = r$ imply $uv \in \Omega_r(Z)$. Since $\Phi$ is injective, in order to prove the opposite inclusion in (6.10), it suffices to show that

 $$ \dim\left(\Omega_{r}\left(X,Y\right)\right)\geq\dim\Omega_{r}\left(Z\right). $$ 

To that end, we consider the dual spaces  $ \{\mathcal{R}^p\}, \{\mathcal{A}^p\}, \{\Omega^p\} $ of forms on  $ X, Y, Z $. We use the same notation as in the case of path spaces:  $ W'p = W^{p-1} $ and

 $$ W^{\bullet}\left(X,Y\right)=W^{\prime\bullet}\left(X\right)\otimes W^{\bullet}\left(Y\right). $$ 

In particular,  $ \Omega^{r}(X,Y) $ is dual to  $ \Omega_{r}(X,Y) $. We will prove that

 $$ \dim\left(\Omega^{r}\left(X,Y\right)\right)\geq\dim\Omega^{r}\left(Z\right), $$ 

which will settle (6.11) and, hence, (6.9).

Recall that

 $$ \Omega^{r}=\mathcal{A}^{r}/\mathcal{K}^{r} $$ 

where

 $$ \mathcal{K}^{r}=\left(\mathcal{N}^{r}+d\mathcal{N}^{r-1}\right)\cap\mathcal{A}^{r}. $$ 

Therefore, we have

 $$ \begin{array}{rcl}\Omega^{r}\left(X,Y\right)&=&\displaystyle\bigoplus_{\left\{p\geq0,q\geq-1:p+q=r\right\}}\Omega^{p}\left(X\right)\otimes\Omega^{q}\left(Y\right)\\&&\displaystyle\bigoplus_{\left\{p\geq0,q\geq-1:p+q=r\right\}}\left(\mathcal{A}^{\prime p}\left(X\right)\big/\mathcal{K}^{\prime p}\left(X\right)\right)\otimes\left(\mathcal{A}^{q}\left(Y\right)/\mathcal{K}^{q}\left(Y\right)\right)\\&\cong&\displaystyle\bigoplus_{\left\{p\geq0,q\geq-1:p+q=r\right\}}\left(\mathcal{A}^{\prime p}\left(X\right)\otimes\mathcal{A}^{q}\left(Y\right)\right)\big/\left(\mathcal{K}^{\prime p}\left(X\right)\otimes\mathcal{A}^{q}\left(Y\right)+\mathcal{A}^{\prime p}\left(X\right)\otimes\mathcal{K}^{q}\left(Y\right)\right),\end{array} $$ 

which implies that

 $$ \begin{array}{rcl}\dim\Omega^{r}\left(X,Y\right)&=&\displaystyle\sum_{\left\{p\geq0,q\geq-1:p+q=r\right\}}\dim\left(\mathcal{A}^{\prime p}\left(X\right)\otimes\mathcal{A}^{q}\left(Y\right)\right)\\&&-\displaystyle\sum_{\left\{p\geq0,q\geq-1:p+q=r\right\}}\dim\left(\mathcal{K}^{\prime p}\left(X\right)\otimes\mathcal{A}^{q}\left(Y\right)+\mathcal{A}^{\prime p}\left(X\right)\otimes\mathcal{K}^{q}\left(Y\right)\right)\end{array} $$ 

It follows from (6.8) that

 $$ \sum_{\left\{p\geq0,q\geq-1:p+q=r\right\}}\dim\left(\mathcal{A}^{\prime p}\left(X\right)\otimes\mathcal{A}^{q}\left(Y\right)\right)=\dim\mathcal{A}^{r}\left(Z\right). $$ 

Since

 $$ \dim\Omega^{r}\left(Z\right)=\dim\mathcal{A}^{r}\left(Z\right)-\dim\mathcal{K}^{r}\left(Z\right), $$ 

the inequality (6.12) will follow if we prove that

 $$ \sum_{\left\{p\geq0,q\geq-1:p+q=r\right\}}\dim\left(\mathcal{K}^{\prime p}\left(X\right)\otimes\mathcal{A}^{q}\left(Y\right)+\mathcal{A}^{\prime p}\left(X\right)\otimes\mathcal{K}^{q}\left(Y\right)\right)\leq\dim\mathcal{K}^{r}\left(Z\right). $$ 

In the next part of the proof we need an operation of joining of the forms on $X$ and $Y$. For any forms $\varphi \in \mathcal{A}^\bullet(X)$ and $\psi \in \mathcal{A}^\bullet(Y)$, define the form $\varphi \ast \psi \in \mathcal{A}^\bullet(Z)$ first for the elementary forms by

 $$ e^{i_{0}\cdots i_{p}}*e^{j_{0}\cdots j_{q}}=e^{i_{0}\cdots i_{p}j_{0}\cdots j_{q}} $$ 

(clearly, if the paths  $ i_0...i_p $ and  $ j_0...j_q $ are allowed on X and Y respectively, then their join path is also allowed on Z), and then extend to all  $ \varphi $ and  $ \psi $ by bilinearity.

The operation * allows us to define a linear mapping

 $$ \begin{aligned}&\Psi:\mathcal{A}^{r}\left(X,Y\right)\rightarrow\mathcal{A}^{r}\left(Z\right)\\ &\\ &\quad\Psi\left(\varphi\otimes\psi\right)=\varphi*\psi.\\ \end{aligned} $$ 

by

The mapping  $ \Psi $ is obviously bijective as all allowed paths on Z are obtained by joining the allowed paths on X and Y in a unique way.

Let us show that the operation * satisfies the following version of the product rule: for all  $ \varphi \in \mathcal{A}^p(X) $,  $ \psi \in \mathcal{A}^q(Y) $

 $$ d\left(\varphi*\psi\right)=\left(d\varphi\right)*\psi+\left(-1\right)^{p+1}\varphi*d\psi\bmod{\mathcal{N}^{p+q+2}}\left(Z\right). $$ 

It suffices to prove (6.15) for  $ \varphi = e^{i_0\cdots i_p} $ and  $ \psi = e^{j_0\cdots j_q} = e^{i_{p+1}\cdots i_{p+q+1}} $. We have by (2.15)

 $$ \begin{array}{r c l}{d\left(\varphi*\psi\right)}&{=}&{d e^{i_{0}\ldots i_{p+q+1}}=\displaystyle\sum_{k\in Z}\displaystyle\sum_{r=0}^{p+q+2}(-1)^{r}e^{i_{0}\ldots i_{r-1}k i_{r}\ldots i_{p+q+1}}}\\ {}&{=}&{\displaystyle\sum_{k\in Z}\displaystyle\sum_{r=0}^{p}(-1)^{r}e^{i_{0}\ldots i_{r-1}k i_{r}\ldots i_{p}i_{p+1}\ldots i_{p+q+1}}}\\ {}&{}&{+\displaystyle\sum_{k\in X\sqcup Y}(-1)^{p+1}e^{i_{0}\ldots i_{p}k i_{p+1}\ldots i_{p+q+1}}}\\ {}&{}&{+\displaystyle\sum_{k\in Z}\displaystyle\sum_{r=p+2}^{p+q+2}(-1)^{r}e^{i_{0}\ldots i_{p}i_{p+1}\ldots i_{r-1}k i_{r}\ldots i_{p+q+1}}.}\\ \end{array} $$ 

Observe that the form  $ e\cdots i_{r-1}ki_{r}\cdots i_{p}\cdots $ in the first sum is non-allowed if  $ k \in Y $, so that the range in the first sum can be restricted to  $ k \in X $. Similarly, the form  $ e\cdots i_{p+1}\cdots i_{r-1}ki_{r}\cdots $ in the third sum is non-allowed if  $ k \in X $, so that its range can be restricted to  $ k \in Y $. Splitting the range of the second sum into two parts  $ k \in X $ and  $ k \in Y $ and combining them with the first and third sums, respectively, we obtain the following identity  $ \text{mod} \mathcal{N}^{\bullet}(Z) $:

 $$ \begin{align*}d\left(\varphi*\psi\right)&=\sum_{k\in X}\sum_{r=0}^{p+1}(-1)^{r}e^{i_{0}\ldots i_{r-1}ki_{r}\ldots i_{p}}*e^{i_{p+1}\ldots i_{p+q+1}}\\&\quad+\sum_{k\in Y}\sum_{r=p+1}^{p+q+2}(-1)^{r}e^{i_{0}\ldots i_{p}}*e^{i_{p+1}\ldots i_{r-1}ki_{r}\ldots i_{p+q+1}}\\&=\left(d\varphi\right)*\psi+(-1)^{p+1}\varphi*d\psi,\end{align*} $$ 

which proves (6.15).

Let us now verify that

 $$ \Psi\left(\mathcal{K}^{\prime p}\left(X\right)\otimes\mathcal{A}^{q}\left(Y\right)+\mathcal{A}^{\prime p}\left(X\right)\otimes\mathcal{K}^{q}\left(Y\right)\right)\subset\mathcal{K}^{r}\left(Z\right), $$ 

provided  $ p + q = r $. We first prove that

 $$ \Psi\left(\mathcal{K}^{\prime p}\left(X\right)\otimes\mathcal{A}^{q}\left(Y\right)\right)\subset\mathcal{K}^{r}\left(Z\right). $$ 

For that we need to verify that

 $$ u\in\mathcal{K}^{\prime p}\left(X\right)\mathrm{a n d}v\in\mathcal{A}^{q}\left(Y\right)\Rightarrow u*v\in\mathcal{K}^{r}\left(Z\right). $$ 

Since  $ u \in \mathcal{A}'^p(X) $, we have  $ u * v \in \mathcal{A}^r(Z) $. By definition of  $ \mathcal{K}'^p(X) $, we have  $ u = d\varphi + \psi $ where  $ \varphi \in \mathcal{N}^{p-2}(X) $ and  $ \psi \in \mathcal{N}^{p-1}(X) $. Using (6.15), we obtain

 $$ u*v=(d\varphi+\psi)*v=d\left(\varphi*v\right)-(-1)^{p-1}\varphi*d v+\psi*v\bmod{\mathcal{N}^{\bullet}}\left(Z\right). $$ 

Clearly, all terms starting with  $ \varphi^* $ and  $ \psi^* $ belong to  $ \mathcal{N}^\bullet(Z) $, which implies that the right hand side belongs to  $ d\mathcal{N}^\bullet(Z) + \mathcal{N}^\bullet(Z) $, whence

 $$ u*v\in d\mathcal{N}^{\bullet}\left(Z\right)+\mathcal{N}^{\bullet}\left(Z\right). $$ 

It follows that  $ u * v \in \mathcal{K}^\bullet(Z) $, which proves (6.17). In the same way one proves that

 $$ \Psi\left(\mathcal{A}^{\prime p}\left(X\right)\otimes\mathcal{K}^{q}\left(Y\right)\right)\subset\mathcal{K}^{r}\left(Z\right), $$ 

whence (6.16) follows.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//a8c0ee7f-efdb-4fbc-82a9-a118d2b350c2/markdown_1/imgs/img_in_image_box_262_393_933_665.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A07Z%2F-1%2F%2F9f3e38c6d6a3d1463834321e50be68df7023c82571e1b4efb04a890a82c28e3e" alt="Image" width="54%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 19: The  $ \Psi $-images of the spaces  $ \mathcal{K}^{\prime p}(X)\otimes\mathcal{A}^{q}(Y)+\mathcal{A}^{\prime p}(X)\otimes\mathcal{K}^{q}(Y) $</div> </div>


Observe that the spaces  $ \mathcal{K}^p(X) \otimes \mathcal{A}^q(Y) + \mathcal{A}^p(X) \otimes \mathcal{K}^q(Y) $ have trivial intersections across different pairs  $ p, q $ as they are subspaces of  $ \mathcal{A}^p(X) \otimes \mathcal{A}^q(Y) $ (cf. Fig. 19). Since  $ \Psi $ is a monomorphism, the same applies to the  $ \Psi $-images of those spaces. Since by (6.16) all the  $ \Psi $-images lie in  $ \mathcal{K}^r(Z) $, we obtain (6.13).

Remark 6.6 It follows from (6.9) that  $ \Omega_{r}(Z) $ has a basis

 $$ \bigsqcup_{\left\{p,q\geq-1:p+q=r-1\right\}}\left\{u_{i}^{(p)}v_{j}^{(q)}\right\}, $$ 

where  $ \left\{u_{i}^{(p)}\right\} $ is a basis in  $ \Omega_{p}(X) $ and  $ \left\{v_{j}^{(q)}\right\} $ is a basis in  $ \Omega_{q}(Y) $. In the same way one expresses a basis in  $ \widetilde{H}_{r}(Z) $ via the basis in  $ \widetilde{H}_{p}(X) $ and  $ \widetilde{H}_{q}(Y) $.

Example 6.7 Consider the graph  $ Z = X * Y $ as on Fig. 17. We have

 $$ \Omega_{0}\left(X\right)=\mathrm{span}\left\{e_{0},e_{1},e_{2}\right\}\qquad\Omega_{0}\left(Y\right)=\mathrm{span}\left\{e_{3},e_{4},e_{5},e_{6}\right\} $$ 

 $$ \Omega_{1}\left(X\right)=\mathrm{span}\left\{e_{01},e_{02},e_{12}\right\}\quad\Omega_{1}\left(Y\right)=\mathrm{span}\left\{e_{34},e_{35},e_{46},e_{56}\right\} $$ 

 $$ \Omega_{2}\left(X\right)=\mathrm{span}\left\{e_{012}\right\}\quad\Omega_{2}\left(Y\right)=\mathrm{span}\left\{e_{346}-e_{356}\right\} $$ 

 $$ \Omega_{p}\left(X\right)=\left\{0\right\}\mathrm{~f o r~}p\geq3\qquad\quad\Omega_{q}\left(Y\right)=\left\{0\right\}\mathrm{~f o r~}q\geq3. $$ 

Using Remark 6.6, we can obtain explicitly the basis in all Ωr (Z). For example,

 $ \dim \Omega_1(Z) = 19 $

 $ \dim \Omega_2(Z) = 25 $

 $ \dim \Omega_3(Z) = 19 $

 $$ \begin{array}{r l r}{\Omega_{4}\left(Z\right)}&{=}&{\mathrm{s p a n}\left\{e_{01346}-e_{01356},e_{02346}-e_{02356},e_{12346}-e_{12356},e_{01234},e_{01235},e_{01246},e_{01256}\right\}}\end{array} $$ 

 $$ \begin{array}{r l r}{\Omega_{5}\left(Z\right)}&{{}=}&{\mathrm{s p a n}\left\{e_{012346}-e_{012356}\right\}}\end{array} $$ 

 $$ \begin{array}{r c l}{\operatorname{d i m}\Omega_{r}\left(Z\right)}&{=}&{0\mathrm{~f o r~}r\geq6.}\end{array} $$ 

Since by Proposition 4.7 all homologies  $ \widetilde{H}_{p}(X) $ and  $ \widetilde{H}_{q}(Y) $ are trivial, and so are  $ \widetilde{H}_{r}(Z) $

Example 6.8 Consider a slight modification of the previous example – the digraph  $ Z = X * Y $ as on Fig. 20

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//a8c0ee7f-efdb-4fbc-82a9-a118d2b350c2/markdown_2/imgs/img_in_image_box_434_293_733_579.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A08Z%2F-1%2F%2Fed162e1d2246382db36f7ef098ddedf54ba16b91baa5709760640fe9754328d1" alt="Image" width="24%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 20: A digraph  $ Z = X \times Y $</div> </div>


In this case we have by Proposition 4.7 that all homologies  $ \widetilde{H}_{p}(X) $ and  $ \widetilde{H}_{q}(Y) $ are trivial except for

 $$ \begin{array}{r l r}{H_{1}\left(X\right)}&{{}=}&{\mathrm{s p a n}\left\{e_{01}+e_{12}+e_{20}\right\},}\end{array} $$ 

 $$ \begin{array}{r l r}{H_{1}\left(Y\right)}&{=}&{\mathrm{s p a n}\left\{e_{35}-e_{65}+e_{64}-e_{34}\right\}.}\end{array} $$ 

Therefore, all  $ \widetilde{H}_{r}(Z) $ are trivial except for  $ H_{3}(Z) $ that is generated by a single element

 $$ e_{0135}-e_{0165}+e_{0164}-e_{0134}+e_{1235}-e_{1265}+e_{1264}-e_{1234}+e_{2035}-e_{2065}+e_{2064}-e_{2034}. $$ 

### 6.3 Cones and simplexes

Definition 6.9 A cone over a digraph X is a digraph Cone X that is obtained from X by adding one more vertex a and all the edges of the form  $ b \to a $ for all  $ b \in X $. The vertex a is called the cone vertex.

Clearly, we have Cone X = X * Y where Y consists of a single vertex a.

Proposition 6.10 For any digraph X, we have for any  $ r \geq 0 $

 $$ \Omega_{r}\left(\mathrm{Cone}X\right)\cong\Omega_{r-1}\left(X\right), $$ 

where the isomorphism is given by the mapping  $ u \mapsto ue_a $ from  $ \Omega_{r-1}(X) $ to  $ \Omega_r $ (Cone  $ X $) where  $ a $ is the cone vertex. Furthermore, all the reduced homologies of Cone  $ X $ are trivial.

Proof. Since Cone $X = X * Y$ with $Y = \{a\}$, (6.19) follows from (6.3) and $\Omega_0(Y) = \mathrm{span}\{e_a\}$. Since all the homologies $\widetilde{H}_q(Y)$ are trivial, it follows from (6.4) that all homologies $\widetilde{H}_r(Z)$ are also trivial. The latter follows from Theorem 4.6 since Cone $X$ is inverse star-shaped.

Example 6.11 Clearly, a simplex-digraph  $ Sm_n $ can be regarded as a cone over  $ Sm_{n-1} $ (cf. Section 4.3). Since  $ \Omega_0(\mathrm{Sm}_0) $ is spanned by a 0-path  $ e_0 $, we obtain by induction from (6.19) that  $ \Omega_n(\mathrm{Sm}_n) $ is spanned by a path  $ e_{01...n} $.

Example 6.12 Let G be a square digraph

 $$ \begin{array}{ccc} 1^{\bullet}&\longrightarrow&\bullet_{3}\\ \uparrow&&\uparrow\end{array} $$ 

 $$ \begin{array}{ccc} 0^\bullet & \longrightarrow & \bullet 2 \end{array} $$ 

Then ConeG is a pyramid shown on Fig. 21. Ω2 (G) is spanned by a 2-path e013 − e023, we

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//a8c0ee7f-efdb-4fbc-82a9-a118d2b350c2/markdown_3/imgs/img_in_image_box_431_476_757_702.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A10Z%2F-1%2F%2F9494b29929da0cac30f0aee4864de4c3f7ba63a5a646ebd6099a80e1d6bfccb5" alt="Image" width="26%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 21: A pyramid graph</div> </div>


obtain that  $ \Omega_{3} $ (Cone G) is spanned by a 3-path  $ e_{0134} - e_{0234} $.

### 6.4 Suspension and spheres

Definition 6.13 A suspension over a digraph $X$ is a digraph Sus $X$ that is obtained from $X$ by adding two vertices $a, b$ and all the edges $c \to a$ and $c \to b$ for all $c \in X$. The vertices $a, b$ are called the suspension vertices.

Clearly, we have Sus X = X * Y where Y is a digraph that consists of two vertices a, b and no edges. An example of a suspension digraph is shown on Fig. 22.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//a8c0ee7f-efdb-4fbc-82a9-a118d2b350c2/markdown_3/imgs/img_in_image_box_523_1103_706_1331.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A10Z%2F-1%2F%2F9848f0d6be287d6407891944825b83c31ba6b9ad7cf28fd46c36d9083449497f" alt="Image" width="14%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 22: A suspension digraph</div> </div>


Proposition 6.14 For any digraph X we have, for any  $ r \geq 0 $,

 $$ \Omega_{r}\left(\mathrm{S u s}X\right)\cong\Omega_{r-1}\left(X\right)\otimes\mathrm{s p a n}\left\{e_{a},e_{b}\right\}, $$ 

where $a,b$ are the suspension vertices and the isomorphism is given by the mappings $u\otimes e_a \mapsto u e_a$ and $u\otimes e_b \mapsto u e_b$. Furthermore, we have

 $$ \widetilde{H}_{r}\left(\mathrm{S u s}X\right)\cong\widetilde{H}_{r-1}\left(X\right), $$ 

where the isomorphism is given by the mapping  $ u \mapsto u(e_a - e_b) $.

Proof. Let Y as above. Since $\Omega_0(Y) = \text{span}\{e_a, e_b\}$ and all other $\Omega_q(Y)$ are trivial, (6.20) follows from (6.3). Since $\widetilde{H}_q(Y) = \{0\}$ for all $q \neq 0$ and $\widetilde{H}_0(Y) = \text{span}\{e_a - e_b\}$, (6.21) follows from (6.4).

Corollary 6.15 We have  $ \chi(\text{Sus}X)=2-\chi(X) $.

Proof. Denoting  $ Z = \text{Sus} X $ we obtain

 $$ \begin{align*}\chi\left(Z\right)&=1+\sum_{p\geq1}\left(-1\right)^{p}\dim H_{p}\left(Z\right)\\&=1+\sum_{p\geq1}\left(-1\right)^{p}\dim\widetilde{H}_{p-1}\left(X\right)\\&=1-\sum_{q\geq0}\left(-1\right)^{q}\dim\widetilde{H}_{q}\left(X\right)\\&=2-\sum_{q\geq0}\left(-1\right)^{q}\dim H_{q}\left(X\right)=2-\chi\left(X\right).\end{align*} $$ 

In particular, having examples of digraphs X with arbitrary negative values of  $ \chi $ (cf. Example 5.9), we obtain examples of digraphs Sus X with arbitrary positive values of  $ \chi $.

Example 6.16 Let $S$ be any cycle-graph that is neither triangle nor square. We regards $S$ as an analog of a circle. Define $S_n$ inductively by $S_1 = S$ and $S_{n+1} = \text{Sus} S_n$. Then $S_n$ can be regarded as $n$-dimensional sphere-graph. An example of $S_2$ is shown on Fig. 23.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//a8c0ee7f-efdb-4fbc-82a9-a118d2b350c2/markdown_4/imgs/img_in_image_box_489_1126_719_1366.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A12Z%2F-1%2F%2F0fc590812fe01988ba13aafc721227108f8694dd6829f42a7eae24828cbc49fc" alt="Image" width="18%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 23: A graph  $ S_{2} $ based on a 3-vertex cycle S</div> </div>


Since  $ \chi(S) = 0 $ by Proposition 4.7, it follows that  $ \chi(S_n) = 0 $ if  $ n $ is odd and  $ \chi(S_n) = 2 $ if  $ n $ is even. Proposition 6.14 also implies that  $ \dim H_n(S_n) = \dim H_1(S) = 1 $, which gives an example of a non-trivial  $ H_n $ with an arbitrary  $ n $.

Let v be an 1-path on S that spans  $ H_{1}(S) $ (see Section 4.5). If  $ S_{n+1} $ is a suspension of  $ S_{n} $ on the vertices  $ a_{n}, b_{n} $ then we obtain by induction that the spanning element of  $ H_{n}(S_{n}) $ is

 $$ v\left(e_{a_{1}}-e_{b_{1}}\right)\left(e_{a_{2}}-e_{b_{2}}\right)\ldots\left(e_{a_{n-1}}-e_{b_{n-1}}\right). $$ 

For example, if $S$ is a cycle-graph on Fig. 23 with $V = \{1, 2, 3\}$ and $E = \{12, 23, 31\}$, then $v = e_{12} + e_{23} + e_{31}$, whence the spanning element of $H_2(S_2)$ is

 $$ v\left(e_{a}-e_{b}\right)=\left(e_{12a}+e_{23a}+e_{31a}\right)-\left(e_{12b}+e_{23b}+e_{31b}\right). $$ 

Example 6.17 Another example of a 2-dimensional sphere-graph G is shown on Fig. 24.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//11e14db2-dc27-4966-8dd6-ee103f2f5b5b/markdown_0/imgs/img_in_image_box_239_548_950_830.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A06Z%2F-1%2F%2Fdda5afb897f143d9d740fa755f64b25d92a4f1e4e142df553af2e76c0693bfc3" alt="Image" width="58%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 24: An octahedron G</div> </div>


Indeed, we have  $ G = \text{Sus} G' $ where  $ G' $ is the subgraph with vertices  $ \{0,1,2,3\} $ that is a cycle-graph. By Proposition 4.7 we have

 $$ \dim H_{0}\left(G^{\prime}\right)=1,\ \dim H_{1}\left(G^{\prime}\right)=1,\ \dim H_{p}\left(G^{\prime}\right)=0for p\geq2. $$ 

The same follows from the fact that  $ G' = \text{Sus} G'' $ where  $ G''' $ is a subgraph with vertices  $ \{0,1\} $. By Proposition 6.14 we obtain

 $$ \dim H_{0}\left(G\right)=1,\dim H_{1}\left(G\right)=0,\dim H_{2}\left(G\right)=1,\dim H_{p}\left(G\right)=0\text{for}p\geq3. $$ 

Consequently,  $ \chi(G)=2 $.

In the digraph G we have

 $$ \dim\Omega_{0}=|V|=6\quad and\quad\dim\Omega_{1}=|E|=12 $$ 

and

 $$ \mathcal{A}_{2}=\mathrm{s p a n}\left\{e_{024},e_{025},e_{034},e_{035},e_{124},e_{125},e_{134},e_{135}\right\}. $$ 

The set of semi-edges is empty, whence by Proposition 4.2 dim $\Omega_2 = \dim \mathcal{A}_2 = 8$ and, hence, $\Omega_2 = \mathcal{A}_2$. Alternatively, one can see that because all the 2-paths spanning $\mathcal{A}_2$ are triangles and there are no squares. Also, there are no allowed 3-paths, so that $\mathcal{A}_3 = \{0\}$ whence $\dim \Omega_p = 0$ for all $p \geq 3$.

Let us determine a spanning element of $H_{2}(G)$. Clearly, $H_{0}(G'') = \text{span}\{e_{0}, e_{1}\}$ whence by (3.12)

 $$ \tilde{H}_{0}\left(G^{\prime\prime}\right)=\mathrm{s p a n}\left\{e_{0}-e_{1}\right\}. $$ 

By the second claim of Proposition 6.14, we have

 $$ \begin{align*}H_{1}\left(G^{\prime}\right)\quad&=\quad\operatorname{span}\left\{\tau\left(e_{0}-e_{1}\right)\right\}=\operatorname{span}\left\{\left(e_{0}-e_{1}\right)\left(e_{2}-e_{3}\right)\right\}\\&=\quad\operatorname{span}\left\{e_{02}-e_{03}-e_{12}+e_{13}\right\}.\end{align*} $$ 

Alternatively, the same spanning element can be obtained by (4.7).

Applying Proposition 6.14 again, we obtain

 $$ \begin{align*}H_{2}\left(G\right)&=\mathrm{span}\left\{\tau\left(e_{02}-e_{03}-e_{12}+e_{13}\right)\right\}\\&=\mathrm{span}\left\{\left(e_{02}-e_{03}-e_{12}+e_{13}\right)\left(e_{4}-e_{5}\right)\right\}\\&=\mathrm{span}\left\{e_{024}-e_{025}-e_{034}+e_{035}-e_{124}+e_{125}+e_{134}-e_{135}\right\}.\end{align*} $$ 

Note that the spanning element of  $ H_{2}(G) $ is exactly a surface path of a triangulation of  $ S^{2} $ into an octahedron (cf. Section 4.7). In this case the surface path is not exact so that there is no solid path representing an octahedron.

## 7 Cartesian product of path complexes

Let us fix some notation to be used in this section. For a finite set V, denote by  $ R(V) $ the path complex on V that consists of all regular elementary paths on V. Then  $ R_p(V) $ denotes the set of all regular elementary p-paths on V, for any non-negative integer p.

As before, the space  $ \mathcal{R}_{p}(V) $ of regular p-paths is the set of all formal finite linear combinations of paths from  $ R_{p}(V) $ with the coefficients from the field K.

In this Section all path complexes are regular and their chain complexes are always truncated and regular. In particular, we set  $ \mathcal{R}_{-1} = \{0\} $. Notation  $ W_{\bullet} $ means here  $ \{W_n\}_{n>0} $.

When considering more than one path complex we use the notation introduced in Section 6.

### 7.1 Cross product of regular paths

Given two finite sets X, Y, consider their Cartesian product

 $$ Z=X\times Y=\left\{(x,y):x\in X and y\in Y\right\}. $$ 

Let  $ z = z_0 z_1 \ldots z_r $ be a regular elementary  $ r $-path on  $ Z $, where  $ z_k = (x_k, y_k) $ with  $ x_k \in X $ and  $ y_k \in Y $. We say that the path  $ z $ is step-like if, for any  $ k = 1, \ldots, r $, either  $ x_{k-1} = x_k $ or  $ y_{k-1} = y_k $ is satisfied (in fact, exactly one of these conditions holds as  $ z $ is regular); in other words, any couple  $ z_{k-1} z_k $ of consecutive vertices is either vertical (when  $ x_{k-1} = x_k $) or horizontal (when  $ y_{k-1} = y_k $):

 $$ \begin{array}{c c c c c}{{}}&{{z_{k}}}&{{}}&{{}}&{{}}\\ {{}}&{{\bullet}}&{{}}&{{}}&{{}}\\ {{}}&{{}}&{{}}&{{}}&{{}}\\ {{v e r t i c a l~c o u p l e}}&{{\uparrow}}&{{}}&{{a n d~h o r i z o n t a l~c o u p l e}}&{{z_{k-1}}}&{{\longrightarrow}}&{{z_{k}}}\\ {{}}&{{z_{k-1}}}&{{}}&{{}}&{{\bullet}}&{{}}&{{.}}\end{array} $$ 

Any step-like path z on Z determines regular elementary paths x on X and y on Y by projection. More precisely, x is obtained from z by taking the sequence of all X-components of the vertices of z and then by collapsing in it any subsequence of repeated vertices to one vertex.

The same rule applies to y. By construction, the projections x and y are regular elementary paths on X and Y, respectively. Let the projections of z be  $ x = x_0...x_p $ and  $ y = y_0...y_q $. Then  $ p + q = r $ where r is the length of z, and every vertex  $ z_k $ of the path z has a form  $ (x_i, y_j) $, whereas the previous vertex  $ z_{k-1} $ is either  $ (x_i, y_{i-1}) $ or  $ (x_{i-1}, y_i) $ as on the diagram:

 $$ \begin{array}{ccc}z_{k}=&\underset{\bullet}{}(x_{i},y_{j})\\\uparrow&&\text{or}\quad\underset{\bullet}{}z_{k-1}=&\underset{\bullet}{}(x_{i-1},y_{j})\quad\longrightarrow\quad\underset{\bullet}{}z_{k}=&\underset{\bullet}{}(x_{i},y_{j})\quad.\\z_{k-1}=&\underset{\bullet}{}(x_{i},y_{j-1})\\\end{array} $$ 

An example of a step-like path z with its projections is shown on Fig. 25.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//11e14db2-dc27-4966-8dd6-ee103f2f5b5b/markdown_2/imgs/img_in_chart_box_355_459_856_781.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A09Z%2F-1%2F%2F6a322e48342ec2dc06cf74a270dd50fe154cd123fb0e7856d729e7bccfebb148" alt="Image" width="40%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 25: A step-like path z and its projections x and y</div> </div>


Every vertex $(x_i, y_j)$ of a step-like path $z$ can be represented as a point $(i, j)$ of $\mathbb{Z}^2$ so that the whole path $z$ is represented by a staircase $S(z)$ in $\mathbb{Z}^2$ connecting the points $(0,0)$ and $(p,q)$. Define the elevation $L(z)$ of the path $z$ as the number of cells in $\mathbb{Z}_+^2$ below the staircase $S(z)$ (the shaded area on Fig. 26).

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//11e14db2-dc27-4966-8dd6-ee103f2f5b5b/markdown_2/imgs/img_in_chart_box_369_1026_815_1342.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A09Z%2F-1%2F%2F93655e50db2960a0be0d65f41aa131873fc8a168118f13f47b0a375232b1c994" alt="Image" width="36%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 26: A staircase S (z) and its elevation L (z). On this picture L (z) = 30.</div> </div>


With any step-like path  $ z = z_0...z_r $ let us associate a sequence  $ \{d_k\}_{k=1}^r $ where  $ d_k = 1 $ if the

couple  $ z_{k-1}z_{k} $ is vertical, and  $ d_{k}=0 $ if this couple is horizontal. If the total number of horizontal couples is p and of the vertical ones - q, then the sequence  $ \{d_{k}\} $ is a permutation of the sequence

 $$ \{\underbrace{0,\ldots,0}_{p},\underbrace{1,\ldots,1}_{q}\}. $$ 

It is easy to see that $L(z)$ is equal to the minimal number of transposition in $\{d_k\}$ that brings it to the form (7.1). In the sequel we will need only the parity of the elevation $L(z)$ that is determined by the parity of the permutation $\{d_k\}$.

\textbf{Dennition 7.1} Given paths  $ u \in \mathcal{R}_p(X) $ and  $ v \in \mathcal{R}_q(Y) $ with some  $ p, q \geq 0 $, define a path  $ u \times v $ on  $ Z $ by the following rule: for any step-like elementary  $ (p + q) $-path  $ z $ on  $ Z $, the component  $ (u \times v)^z $ is defined by

 $$ (u\times v)^{z}=(-1)^{L(z)}u^{x}v^{y}, $$ 

where $x$ and $y$ are the projections of $z$ onto $X$ and $Y$, respectively, and $u^x$ and $v^y$ are the corresponding components of $u$ and $v$. For non-step-like paths $z$ set $(u \times v)^z = 0$.

The path  $ u \times v $ is called the (Cartesian) cross product of u and v. It follows that  $ u \times v \in \mathcal{R}_{p+q}(Z) $.

Given a step-like  $ (p + q) $-path  $ z $ on  $ Z $, the projection of  $ z $ onto  $ X $ could be a  $ p' $-path  $ x $ with  $ p' \neq p $; in this case we set by definition  $ u^x \equiv 0 $. The same rule applies to  $ v^y $. In other words,  $ (u \times v)^z $ may be non-zero only when the projections of  $ z $ onto  $ X $ and  $ Y $ are  $ p $-path  $ x $ and  $ q $-path  $ y $ respectively, with non-zero  $ u^x $ and  $ v^y $.

For given paths  $ x \in R_p(X) $ and  $ y \in R_q(Y) $ with non-negative integers  $ p, q $, denote by  $ \Pi_{x,y} $ the set of all step-like paths  $ z $ on  $ Z $ whose projections on  $ X $ and  $ Y $ are respectively  $ x $ and  $ y $. It follows from (7.2) that

 $$ e_{x}\times e_{y}=\sum_{z\in\Pi_{x,y}}(-1)^{L(z)}e_{z}. $$ 

It is not difficult to see that the cross product is associative.

Example 7.2 Let us denote the vertices of X by letters a, b, c etc and the vertices of Y by integers 0, 1, 2, etc so that the vertices of Z can be denoted as the fields on the chessboard, for example, a0, b1 etc. Then we have

 $$ e_{a}\times e_{01}=e_{a0a1} $$ 

 $$ e_{ab}\times e_{0}=e_{a0b0} $$ 

 $$ e_{ab}\times e_{01}=e_{a0b0b1}-e_{a0a1b1} $$ 

 $$ e_{abc}\times e_{01}=e_{a0b0c0c1}-e_{a0b0b1c1}+e_{a0a1b1c1} $$ 

 $$ \begin{array}{r c l}{e_{a b c}\times e_{012}}&{=}&{e_{a0b0c0c1c2}-e_{a0b0b1c1c2}+e_{a0b0b1b2c2}}\\ {}&{}&{}\\ {}&{}&{+e_{a0a1b1c1c2}-e_{a0a1b1b2c2}+e_{a0a1a2b2c2}}\\ \end{array} $$ 

etc (cf. Fig. 27).

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//11e14db2-dc27-4966-8dd6-ee103f2f5b5b/markdown_4/imgs/img_in_image_box_470_165_723_411.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A12Z%2F-1%2F%2F1c595e286c26e378c047741277b78563299e5f5624e3aac25ab0b17b6453f392" alt="Image" width="20%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 27: The staircase  $ a_{0}b_{0}b_{1}c_{1}c_{2} $ has elevation 1. Hence,  $ e_{a0b0b1c1c2} $ enters the product  $ e_{abc} \times e_{012} $ with the negative sign.</div> </div>


### 7.2 The product rule

In this and next sections we use the regular truncated version of the boundary operator  $ \partial $.

Proposition 7.3 If  $ u \in \mathcal{R}_p(X) $ and  $ v \in \mathcal{R}_q(Y) $ where  $ p, q \geq 0 $, then

 $$ \partial\left(u\times v\right)=\left(\partial u\right)\times v+\left(-1\right)^{p}u\times\left(\partial v\right). $$ 

Proof. It suffices to prove (7.4) for the case  $ u = e_x $ and  $ v = e_y $ where  $ x $ and  $ y $ are regular elementary  $ p $-path on  $ X $ and  $ q $-path on  $ Y $, respectively. Set  $ r = p + q $ so that  $ e_x \times e_y \in \mathcal{R}_r(Z) $. We have by (7.3) and (2.2)

 $$ \partial\left(e_{x}\times e_{y}\right)=\sum_{z\in\Pi_{x,y}}\left(-1\right)^{L(z)}\partial e_{z}=\sum_{z\in\Pi_{x,y}}\sum_{k=0}^{r}\left(-1\right)^{L(z)+k}e_{z_{(k)}}, $$ 

where we use a shortcut

 $$ z_{(k)}=z_{0}...\widehat{z_{k}}...z_{r}=z_{0}...z_{k-1}z_{k+1}...z_{r}. $$ 

Switching the order of the sums, rewrite  $ (7.5) $ in the form

 $$ \partial\left(e_{x}\times e_{y}\right)=\sum_{k=0}^{r}\sum_{z\in\Pi_{x,y}}\left(-1\right)^{L(z)+k}e_{z_{(k)}}. $$ 

Given an index  $ k = 0, \ldots, r $ and a path  $ z \in \Pi_{x,y} $, consider the following four logically possible cases how horizontal and vertical couples combine around  $ z_k $:

 $$ (V):\begin{array}{c}z_{k+1}\\ \bullet\\ \uparrow\\ z_{k}\\ \bullet\\ \uparrow\\ z_{k-1}\\ \bullet\end{array} $$ 

 $$ \begin{array}{ccc}(R):&\begin{array}{c}z_{k+1}\\\bullet\end{array}&(L):&\begin{array}{ccc}z_{k}&\longrightarrow&\bullet\\&\uparrow&\\z_{k-1}&\longrightarrow&\begin{array}{c}z_{k}\\\bullet\end{array}\end{array}\end{array} $$ 

Here  $ (H) $ stands for a horizontal position,  $ (V) $ for vertical,  $ (R) $ for right and  $ (L) $ for left. If k = 0 or k = r then  $ z_{k-1} $ or  $ z_{k+1} $ should be ignored, so that one has only two distinct positions  $ (H) $ and  $ (V) $.

If  $ z \in \Pi_{x,y} $ and  $ z_k $ stands in  $ (R) $ or  $ (L) $ then consider a path  $ z' \in \Pi_{x,y} $ such that  $ z_i' = z_i $ for all  $ i \neq k $, whereas  $ z'_k $ stands in the opposite position  $ (L) $ or  $ (R) $, respectively, as on the diagrams:

 $$ \begin{array}{ccc} z_{k}^{\prime} & \longrightarrow &  z_{k+1} \\ \bullet & & \bullet \\ \uparrow & & \uparrow \\ z_{k-1} & \longrightarrow &  z_{k} \\ \bullet & & \bullet \end{array} \quad \begin{array}{ccc} z_{k} & \longrightarrow &  z_{k+1} \\ \downarrow & & \uparrow \\ z_{k-1} & & z_{k}^{\prime} \\ \downarrow & & \bullet \end{array} $$ 

Clearly, we have $L\left(z^{\prime}\right)=L\left(z\right)\pm1$ which implies that the terms $e_{z_{(k)}}$ and $e_{z_{(k)}^{\prime}}$ out.

Denote by  $ \Pi_{x,y}^k $ the set of paths  $ z \in \Pi_{x,y} $ such that  $ z_k $ stands in position  $ (V) $ and by  $ \Pi_{x,y}^k $ the set of paths  $ z \in \Pi_{x,y} $ such that  $ z_k $ stands in position  $ (H) $. By the above observation, we can restrict the summation in (7.6) to those pairs  $ k, z $ where  $ z_k $ is either in vertical or horizontal position, that is,

 $$ \partial\left(e_{x}\times e_{y}\right)=\sum_{k=0}^{r}\sum_{z\in\Pi_{x,y}^{k}\cup\Pi_{x,y}^{k}}\left(-1\right)^{L(z)+k}e_{z_{(k)}}. $$ 

Let us now compute the first term in the right hand side of (7.4):

 $$ \left(\partial e_{x}\right)\times e_{y}=\sum_{l=0}^{p}\left(-1\right)^{l}e_{x}\times e_{y}=\sum_{l=0}^{p}\sum_{w\in\Pi_{x_{(l)}},y}\left(-1\right)^{L(w)+l}e_{w}. $$ 

Fix some  $ l = 0, \ldots, p $ and  $ w \in \Pi_{x_{(l)}, y} $. Since the projection of w on X is  $ x_{(l)} = x_0...x_{l-1} x_{l+1}...x_p $, there exists a unique index k such that  $ w_{k-1} $ projects onto  $ x_{l-1} $ and  $ w_k $ projects onto  $ x_{l+1} $. Then  $ w_{k-1} $ and  $ w_k $ have a common projection onto Y, say  $ y_m $.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//3f567a68-fa43-4a4b-b8ff-cc57424a9535/markdown_0/imgs/img_in_chart_box_375_915_794_1242.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A09Z%2F-1%2F%2F362fc25805ad35a761c3ae43c660e873c93d530d64212ee21389178818ebc25b" alt="Image" width="34%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 28: Step-like paths w and z. The shaded area represents the difference L(z) − L(w).</div> </div>


Define a path  $ z \in \Pi_{x,y}^{k} $ by setting

 $$ \begin{array}{ll}z_{i}=w_{i}&\text{for}i\leq k-1,\\z_{k}=(x_{l},y_{m})&\text{for}i=k,\\z_{i}=w_{i-1}&\text{for}i\geq k+1\end{array} $$ 

By construction we have  $ z_{(k)} = w $. It also follows from the construction that

 $$ L\left(z\right)=L\left(w\right)+m. $$ 

Since  $ k = l + m $, we obtain that

 $$ L\left(z\right)+k=L\left(w\right)+l+2m. $$ 

We see that each pair $l,w$ where $l=0,\ldots,p$ and $w\in\Pi_{x_{(l)},y}$ gives rise to a pair $k,z$ where $k=0,\ldots,r$, $z\in\Pi_{x,y}^{k}$, and

 $$ (-1)^{L(z)+k}e_{z_{(k)}}=(-1)^{L(w)+l}e_{w}. $$ 

By reversing this argument, we obtain that each such pair k,z gives back l,w so that this correspondence between k,z and l,w is bijective. Hence, we conclude that

 $$ \left(\partial e_{x}\right)\times e_{y}=\sum_{l=0}^{p}\sum_{w\in\Pi_{x_{(l)}},y}\left(-1\right)^{L(w)+l}e_{w}=\sum_{k=0}^{r}\sum_{z\in\Pi_{x,y}^{k}}\left(-1\right)^{L(z)+k}e_{z_{(k)}}. $$ 

The second term in the right hand side of  $ (7.4) $ is computed similarly:

 $$ (-1)^{p}e_{x}\times\partial e_{y}=\sum_{m=0}^{q}(-1)^{m+p}e_{x}\times e_{y_{(m)}}=\sum_{m=0}^{q}\sum_{w\in\Pi_{x,y_{(m)}}}(-1)^{L(w)+m+p}e_{w}. $$ 

Each pair $m$, $w$ here gives rise to a pair $k$, $z$ where $k = 0, \ldots, r$ and $z \in \Pi_{x,y}^k$ in the following way: choose $k$ such that $w_{k-1}$ projects onto $y_{m-1}$ and $w_k$ projects onto $y_{m+1}$. Then $w_{k-1}$ and $w_k$ have a common projection onto $X$, say $x_l$.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//3f567a68-fa43-4a4b-b8ff-cc57424a9535/markdown_1/imgs/img_in_chart_box_362_885_796_1212.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A11Z%2F-1%2F%2F07a22ef7549300f64e1cb627c3f2bf66d3a6f0cd8ffd84c6772814170848c73c" alt="Image" width="35%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 29: Paths w and z. The shaded area represents L (z) − L (w).</div> </div>


Define the path  $ z \in \Pi_{x,y}^k $ as in (7.9) (cf. Fig. 29). Then we have  $ w = z_{(k)} $ and

 $$ L\left(z\right)=L\left(w\right)+p-l. $$ 

Since  $ k = l + m $, we obtain

 $$ L\left(z\right)+k=L\left(w\right)+p+m $$ 

and

 $$ (-1)^{p}e_{x}\times\partial e_{y}=\sum_{m=0}^{q}\sum_{w\in\Pi_{x,y_{(m)}}}(-1)^{L(w)+m+p}e_{w}=\sum_{k=0}^{\tau}\sum_{z\in\Pi_{x,y}^{k}}(-1)^{L(z)+k}e_{z_{(k)}}. $$ 

Combining this with (7.7) and (7.10), we obtain (7.4). ■

### 7.3  $ \partial $-invariant paths on Cartesian product

Definition 7.4 Given two finite sets X and Y with path complexes  $ P(X) $ and  $ P(Y) $ respectively, define on the set  $ Z = X \times Y $ a path complex  $ P(Z) $ as follows: the elements of  $ P(Z) $ are step-like paths on Z whose projections on X and Y belong to  $ P(X) $ and  $ P(Y) $, respectively. The path complex  $ P(Z) $ is called the Cartesian product of the path complexes  $ P(X) $ and  $ P(Y) $ and is denoted by  $ P(X) \oplus P(Y) $.

In particular, if $x$ and $y$ are elementary allowed paths on $X$ and $Y$, respectively, then all the paths $z \in \Pi_{x,y}$ are allowed on $Z$. It clearly follows from (7.3) that

 $$ u\in\mathcal{A}_{p}\left(X\right)\mathrm{~a n d~}v\in\mathcal{A}_{q}\left(Y\right)\Rightarrow u\times v\in\mathcal{A}_{p+q}\left(Z\right). $$ 

Furthermore, the following is true.

Proposition 7.5 If  $ u \in \Omega_p(X) $ and  $ v \in \Omega_q(Y) $ then  $ u \times v \in \Omega_{p+q}(Z) $.

Proof. Indeed, $\partial u$ and $\partial v$ are allowed, whence also $\partial u \times v$ and $u \times \partial v$ are allowed, whence $\partial (u \times v)$ is allowed by the product rule (7.4). It follows that $u \times v \in \Omega_{p+q}(Z)$.

It follows easily from the product rule that the cross product of closed paths is closed, and of exact and closed paths – exact.

The next theorem gives a complete description of  $ \partial $-invariant paths on Z.

Theorem 7.6 Let $P(X)$ and $P(Y)$ be two regular path complexes. Then for their Cartesian product $P(Z)=P(X)\oplus P(Y)$ the following isomorphism of chain complexes holds:

 $$ \Omega_{\bullet}\left(Z\right)\cong\Omega_{\bullet}\left(X\right)\otimes\Omega_{\bullet}\left(Y\right), $$ 

where the mapping Ω⋄ (X) ⊗ Ω⋄ (Y) → Ω⋄ (Z) is given by u ⊗ v ↔ u × v.

Consequently we have

 $$ H_{\bullet}\left(Z\right)\cong H_{\bullet}\left(X\right)\otimes H_{\bullet}\left(Y\right) $$ 

(the Künneth formula for Cartesian product).

The relation (7.12) means that, for any  $ r \geq 0 $,

 $$ H_{r}\left(Z\right)\cong\bigoplus_{\left\{p,q\geq0:p+q=r\right\}}\left(H_{p}\left(X\right)\otimes H_{q}\left(Y\right)\right). $$ 

For example, if the path complex $P(X)$ is connected and all homologies $H_p(X)$, $p \geq 1$, are trivial then $H_r(Z) \cong H_r(Y)$.

The proof of Theorem 7.6 will be given in Section 7.6 after a necessary preparation. Here we consider some examples of Cartesian products.

Let  $ (X, E_X) $ and  $ (Y, E_Y) $ be two digraphs. Their Cartesian product is the digraph  $ (Z, E_Z) $ where  $ Z = X \times Y $ and the set  $ E_Z $ of edges is defined as follows:  $ (x, y) \to (x', y') $ if and only if either  $ x \to x' $ and  $ y = y' $ (a horizontal edge) and  $ y \to y' $ and  $ x = x' $ (a vertical edge):

 $$ \begin{array}{cccc}y^{\prime}\bullet&\cdots&(x,y^{\prime})&\longrightarrow&(x^{\prime},y^{\prime})\\ \uparrow&&\uparrow&\uparrow\\ y\bullet&\cdots&(x,y)&\longrightarrow&(x^{\prime},y)\\ \end{array}\quad\begin{array}{cccc}y^{\prime}\bullet&\cdots&(x,y^{\prime})&\longrightarrow&(x^{\prime},y^{\prime})\\ \uparrow&&\uparrow&\uparrow\\ y\bullet&\cdots&(x,y)&\longrightarrow&(x^{\prime},y)\\ \end{array} $$ 

 $$ ^{Y}\nearrow_{X}\quad\cdots\quad\bullet\quad\longrightarrow\quad\bullet\quad\cdots $$ 

Clearly, any allowed path on  $ (Z, E_Z) $ is step-like, and its projections onto X and Y are also allowed. Hence, the path complex of the digraph  $ (Z, E_Z) $ is the Cartesian product of the path complexes of the digraphs  $ (X, E_X) $ and  $ (Y, E_Y) $.

Let us give some explicit examples of product digraphs and  $ \partial $-invariant paths there.

Example 7.7 Consider the Cartesian product  $ Z = X \oplus Y $ of the digraphs

 $$ X=^{a}\bullet\leftrightarrow\bullet^{b}\mathrm{~a n d~}Y=^{0}\bullet\leftrightarrow\bullet^{1} $$ 

that is shown on Fig. 30. paths eaba and e010 are ∂-invariant, so that their cross product

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//3f567a68-fa43-4a4b-b8ff-cc57424a9535/markdown_3/imgs/img_in_image_box_457_722_628_895.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A13Z%2F-1%2F%2F15703f5924e44d6f961f3ec92546ee5fe81a02fc47c85a4e2529654d14c19bb7" alt="Image" width="13%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 30: Cartesian product of  $ ^a\bullet \leftrightarrow \bullet^b $ and  $ ^0\bullet \leftrightarrow \bullet^1 $</div> </div>


 $$ e_{a0b0a0a1a0}-e_{a0b0b1a1a0}+e_{a0b0b1b0a0}+e_{a0a1b1a1a0}-e_{a0a1b1b0a0}+e_{a0a1a0b0a0} $$ 

is  $ \partial $-invariant on Z. The paths  $ e_{ab} + e_{ba} $ and  $ e_{01} + e_{10} $ are exact, so that their cross product

 $$ e_{a0b0b1}-e_{a0a1b1}+e_{a1b1b0}-e_{a1a0b0}+e_{b0a0a1}-e_{b0b1a1}+e_{b1a1a0}-e_{b1b0a0} $$ 

is an exact path on Z.

Example 7.8 Let  $ Z = X \oplus Y $ where

 $$ X=\underset{a_{\bullet}}{\overset{b}{\rightarrow}}\underset{}{\overset{\bullet}{\rightarrow}}{\overset{b}{\bullet}}c\quad and\quad Y=\underset{0}{\overset{0}{\bullet}}\underset{}{\leftrightarrow}{\overset{\bullet}{\bullet}}^{1} $$ 

(see Fig. 31). paths  $ e_{abc} $ is  $ \partial $-invariant on X and  $ e_{01} + e_{10} $ is  $ \partial $-invariant on Y. Hence, their cross product

 $$ e_{a0b0c0c1}-e_{a0b0b1c1}+e_{a0a1b1c1}+e_{a1b1c1c0}-e_{a1b1b0c0}+e_{a1a0b0c0} $$ 

is  $ \partial $-invariant on Z.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//3f567a68-fa43-4a4b-b8ff-cc57424a9535/markdown_4/imgs/img_in_image_box_424_170_700_396.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A14Z%2F-1%2F%2F3be4cbbac9295ef9c134c53556b705b06734cd54b9f01fb624505f63fe3b3731" alt="Image" width="22%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 31: Cartesian product of a triangle and and  $ 0 \bullet \leftrightarrow \bullet^{1} $</div> </div>


Example 7.9 Let  $ Z = X \oplus Y $ where

 $$ X=\begin{array}{c}b\\ a_{\bullet}\end{array}\stackrel{\bullet}{\rightarrow}\stackrel{\bullet}{\bullet}^{c}\quad and\quad Y=\begin{array}{c}2^{\bullet}\quad\longrightarrow\quad\bullet_{3}\\ \uparrow\\ 0^{\bullet}\quad\longrightarrow\quad\bullet_{1}\end{array}. $$ 

(see Fig. 32). the cross product of  $ \partial $-invariant paths  $ e_{abc} $ and  $ e_{013} - e_{023} $, we obtain the following

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//3f567a68-fa43-4a4b-b8ff-cc57424a9535/markdown_4/imgs/img_in_image_box_368_740_797_1043.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A14Z%2F-1%2F%2Fd9f425bef164a9ad0d453d19ee53c61ca8a1e57b7071f54ff0f0de6c6e2dfa18" alt="Image" width="35%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 32: Cartesian product of a triangle and a square</div> </div>


 $ \partial $-invariant path on Z:

 $$ \begin{aligned}&e_{a0b0c0c1c3}-e_{a0b0b1c1c3}+e_{a0b0b1b3c3}\\&+e_{a0a1b1c1c3}-e_{a0a1b1b3c3}+e_{a0a1a3b3c3}\\&-e_{a0b0c0c2c3}+e_{a0b0b2c2c3}-e_{a0b0b2b3c3}\\&-e_{a0a2b2c2c3}+e_{a0a2b2b3c3}-e_{a0a2a3b3c3}\\ \end{aligned} $$ 

### 7.4 Cylinders and hypercubes

For any digraph X, the cylinder over X is the digraph

 $$ \mathrm{Cyl}X:=X\boxplus\mathbf{\Theta}^{0}\bullet\rightarrow\bullet^{1}. $$ 

Assuming that the vertices of X are enumerated by 0, 1, ..., n-1, we can enumerate the vertices of Cyl X by 0, 1, ..., 2n-1 using the following rule:  $ (x,0) $ is assigned the number x, while  $ (x,1) $ is assigned  $ x+n $.

Define the operation of lifting paths from X to Cyl X as follows: for any regular path v on X, the lifted path is denoted by  $ \hat{v} $ and is defined by

 $$ \widehat{v}=v\times e_{01}. $$ 

Since  $ e_{01} $ is  $ \partial $-invariant on Y, we obtain that if  $ v \in \mathcal{A}_p(X) $ then  $ \widehat{v} \in \mathcal{A}_{p+1}(\text{Cyl}X) $, and if  $ v \in \Omega_p(X) $ then  $ \widehat{v} \in \Omega_{p+1}(\text{Cyl}X) $.

For example, if  $ v = e_{i_0...i_p} $ then

 $$ \widehat{v}=e_{i_{0}\ldots i_{p}}\times e_{01}=\sum_{k=0}^{p}(-1)^{p-k}e_{i_{0}\ldots i_{k}(i_{k}+n)\ldots(i_{p}+n)}, $$ 

since the path  $ i_{0}...i_{k}\left(i_{k}+n\right)...\left(i_{p}+n\right) $ has the elevation p - k as can be seen on the diagram:

 $$ \begin{array}{c c c c c c c c c c}{\cdots}&{i_{k}+n}&{\longrightarrow}&{i_{k+1}+n}&{\longrightarrow}&{\cdots}&{\longrightarrow}&{i_{p}+n}\\ {}&{\bullet}&{\uparrow}&{\uparrow}&{}&{}&{}&{}\\ {}&{i_{k}}&{\longrightarrow}&{i_{k+1}}&{\cdots}&{}&{}&{}\\ {\bullet}&{\longrightarrow}&{\cdots}&{\bullet}&{\bullet}&{\cdots}&{}&{}\\ \end{array}, $$ 

Example 7.10 The cylinder over a triangle  $ X = \begin{array}{c} 0 \\ \bullet \end{array} \xrightarrow{\bullet} \begin{array}{c} 2 \\ \bullet \end{array} $ is shown on Fig. 33.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//727247f9-cdf6-4ae9-a7b0-c7a6957c522c/markdown_0/imgs/img_in_image_box_480_827_670_1068.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A10Z%2F-1%2F%2F4db5cc59e7d17c6c0771153cd066dfca47da982cf363a86de081c25da1447cb0" alt="Image" width="15%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 33: A cylinder over a triangle</div> </div>


Since 2-path  $ e_{012} $ is  $ \partial $-invariant on X, lifting it to the cylinder, we obtain the following  $ \partial $-invariant 3-path on Cyl X:

 $$ e_{0345}-e_{0145}+e_{0125}. $$ 

Example 7.11 The cylinder over the graph  $ X = ^{0}\bullet \rightarrow \bullet^{1} $ is a square:

 $$ \begin{array}{ccc} 2\bullet & \longrightarrow & \bullet^{3} \\ \uparrow & & \uparrow \\ 0\bullet & \longrightarrow & \bullet^{1} \end{array} $$ 

Lifting a  $ \partial $-invariant 1-path  $ e_{01} $ on X we obtain the following  $ \partial $-invariant 2-path on the square:  $ e_{013} - e_{023} $.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//727247f9-cdf6-4ae9-a7b0-c7a6957c522c/markdown_1/imgs/img_in_image_box_438_166_739_441.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A11Z%2F-1%2F%2F05c620fba884073b089061f4d43836e320b949d5d0203f21d925450d08a1dbe6" alt="Image" width="24%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 34: A 3-cube</div> </div>


The cylinder over a square is a 3-cube that is shown in Fig. 34.

Lifting the 2-path  $ e_{013} - e_{023} $ we obtain the following  $ \partial $-invariant 3-path on the 3-cube:

 $$ e_{0457}-e_{0157}+e_{0137}-e_{0467}+e_{0267}-e_{0237}. $$ 

Defining further n-cube for any positive integer n by

 $$ \mathrm{C u b e}_{n}=\mathrm{C y l}\mathrm{C u b e}_{n-1}, $$ 

we see that  $ \text{Cube}_n $ determines a  $ \partial $-invariant  $ n $-path that is a lifting of a  $ \partial $-invariant  $ (n-1) $-path from  $ \text{Cube}_{n-1} $ and that is an alternating sum of  $ n! $ elementary terms. It is easy to show that these terms correspond to partitioning of a solid  $ n $-cube into  $ n! $ simplexes.

By (7.13) all homology groups of  $ Cub_{n} $ are trivial except for  $ H_{0} $.

### 7.5 Representation of  $ \partial $-invariant paths on product

As in Section 7.3, we work with two paths complexes $P(X)$, $P(Y)$ and their Cartesian product $P(Z) = P(X) \boxplus P(Y)$ where $Z = X \times Y$. The following statement is a partial converse of Proposition 7.5.

Proposition 7.12 Any path  $ w \in \Omega_{\bullet}(Z) $ admits a representation

 $$ w=\sum_{x\in P(X),y\in P(Y)}c^{xy}\left(e_{x}\times e_{y}\right) $$ 

with some scalar coefficients  $ c^{xy} $ (only finitely many coefficients are non-vanishing). Furthermore, the coefficients  $ c^{xy} $ are uniquely determined by w.

Proof. Let us first show the uniqueness of  $ c^{xy} $, which is equivalent to the linear independence of the family  $ \{e_x \times e_y\} $ across all  $ x \in P(X) $ and  $ y \in P(Y) $. Indeed, assume that, for some scalars  $ c^{xy} $,

 $$ \sum_{x\in P(X),y\in P(Y)}c^{xy}e_{x}\times e_{y}=0, $$ 

and prove that  $ c^{xy} = 0 $ for any couple  $ x, y $ as in the summation. Fix such a couple  $ x, y $ and choose one  $ z \in \Pi_{x,y} $. Then by (7.2)

 $$ \left(e_{x^{\prime}}\times e_{y^{\prime}}\right)^{z}=\left\{\begin{array}{l l}\left(-1\right)^{L(z)},&x^{\prime}=x and y^{\prime}=y,\\ 0,&o t h e r w i s e,\end{array}\right. $$ 

which implies that

 $$ \left(\sum_{x^{\prime}\in P(X),y^{\prime}\in P(Y)}c^{x^{\prime}y^{\prime}}e_{x^{\prime}}\times e_{y^{\prime}}\right)^{z}=(-1)^{L(z)}c^{x y} $$ 

and, hence,  $ c^{xy}=0. $

Let us show existence of the representation (7.15) for any  $ w \in \Omega_r(Z) $ and any  $ r \geq 0 $. As before, for any elementary  $ r $-path  $ z $ on  $ Z $,  $ w^z $ denotes the  $ e_z $-coordinate of  $ w $. If  $ z $ is an elementary  $ r' $-path with  $ r' \neq r $ then set  $ w^z = 0 $. For any  $ x \in P(X) $ and  $ y \in P(Y) $ choose some  $ z \in \Pi_{x,y} $ and set

 $$ c^{x y}=(-1)^{L(z)}w^{z}. $$ 

Let us first show that the value of  $ c^{xy} $ in (7.16) is independent of the choice of  $ z \in \Pi_{x,y} $. Set  $ z = i_0...i_r $. Let  $ k $ be an index such that one of the couples  $ i_{k-1}i_k $,  $ i_k i_{k+1} $ is vertical and the other is horizontal. If  $ i_{k-1} = (a, b) $ and  $ i_{k+1} = (a', b') $ where  $ a, a' \in X $ and  $ b, b' \in Y $, then  $ i_k $ is either  $ (a', b) $ or  $ (a, b') $. Denote the other of these two vertices by  $ i'_k $, as, for example, on the diagram:

 $$ \begin{array}{ccccccc} \vdots & & & & \vdots & & \\ b^{\prime} & & i_{k}^{\prime} & & \longrightarrow &  i_{k+1} & & \cdots\\ \uparrow & & \uparrow & & \uparrow & & \\ b & & \cdots &  i_{k-1} & \longrightarrow &  i_{k} & & \\ \vdots & & \vdots & & & \\ \Downarrow & & & & & \\ y & & & & & \end{array} $$ 

 $$ x=\cdots\qquad\bullet\qquad\longrightarrow\qquad\bullet\qquad\cdots $$ 

Replacing in the path  $ z = i_0...i_r $ the vertex  $ i_k $ by  $ i'_k $, we obtain the path  $ z' = i_0...i_{k-1}i'_k i_{k+1}...i_r $ that clearly belongs to  $ \Pi_{x,y} $ and, hence, is allowed. Since the  $ (r-1) $-path  $ i_0...i_{k-1}i_{k+1}...i_r $ is regular but non-allowed (as it is not step-like), while  $ \partial w $ is allowed, we have

 $$ (\partial w)^{i_{0}\ldots i_{k-1}i_{k+1}\ldots i_{r}}=0. $$ 

On the other hand, we have by  $ (2.4) $

 $$ \begin{array}{r c l}{(\partial w)^{i_{0}\dots i_{k-1}i_{k+1}\dots i_{r}}}&{=}&{\displaystyle\sum_{i\in Z}\left(\displaystyle\sum_{m=0}^{k-1}\left(-1\right)^{m}w^{i_{0}\dots i_{m-1}j i_{m}\dots i_{k-1}i_{k+1}\dots i_{r}}\right.}\end{array} $$ 

 $$ +(-1)^{k}w^{i_{0}\ldots i_{k-1}j i_{k+1}\ldots i_{r}} $$ 

 $$ +\sum_{m=k+2}^{r+1}(-1)^{m-1}w^{i_{0}\ldots i_{k-1}i_{k+1}\ldots i_{m-1}j i_{m}\ldots i_{r}}\Big). $$ 

All the components of $w$ in the sums (7.18) and (7.20) vanish since they correspond to non-allowed paths, while $w$ is allowed. The path $i_0...i_{k-1}ji_{k+1}...i_r$ in the term (7.19) is also non-allowed the unless $j = i_k$ or $j = i_k'$ (note that $i_k$ and $i_k'$ are uniquely determined by $i_{k-1}$).

and  $ i_{k+1} $). Hence, the only non-zero terms in (7.18)-(7.20) are  $ w^{i_{0}\ldots i_{k-1}i_{k}i_{k+1}\ldots i_{r}} = w^{z} $ and  $ w^{i_{0}\ldots i_{k-1}i_{k}^{\prime}i_{k+1}\ldots i_{r}} = w^{z^{\prime}} $. Combining (7.17) and (7.18)-(7.20), we obtain

 $$ \begin{align*}0=w^z+w^{z^{\prime}}.\end{align*} $$ 

Since  $ L(z') = L(z) \pm 1 $, it follows that

 $$ (-1)^{L(z^{\prime})}w^{z^{\prime}}=(-1)^{L(z)}w^{z}. $$ 

The transformation  $ z \mapsto z' $ described above, allows us to obtain from a given  $ z \in \Pi_{x,y} $ in a finite number of steps any other path in  $ \Pi_{x,y} $. Since the quantity  $ (-1)^{L(z)} w^z $ does not change under this transformation, it follows that it does not depend on a particular choice of  $ z \in \Pi_{x,y} $, which was claimed. Hence, the coefficients  $ c^{xy} $ are well-defined by (7.16).

Finally, let us show that the identity (7.15) holds with the coefficients  $ c^{xy} $ from (7.16). By (7.3) we have

 $$ e_{x}\times e_{y}=\sum_{z\in\Pi_{x,y}}(-1)^{L(z)}e_{z}. $$ 

Using (7.16) we obtain

 $$ \begin{array}{r l r}{\displaystyle\sum_{x\in P(X),~y\in P(Y)}c^{x y}\left(e_{x}\times e_{y}\right)}&{=}&{\displaystyle\sum_{x\in P(X),~y\in P(Y)}c^{x y}\displaystyle\sum_{z\in\Pi_{x,y}}(-1)^{L(z)}e_{z}}\\ &{=}&{\displaystyle\sum_{x\in P(X),~y\in P(Y)}\displaystyle\sum_{z\in\Pi_{x,y}}w^{z}e_{z}}\\ &{=}&{\displaystyle\sum_{z\in P(Z)}w^{z}e_{z}=w,}\end{array} $$ 

which finishes the proof. ■

Corollary 7.13 Any path  $ w \in \Omega_{\bullet}(Z) $ admits representations

 $$ w=\sum_{x\in P(X)}e_{x}\times u^{x}=\sum_{y\in P(Y)}v^{y}\times e_{y} $$ 

where  $ u^x \in \Omega_\bullet(X) $ and  $ v^y \in \Omega_\bullet(Y) $ are uniquely determined.

Proof. It follows from (7.15) that

 $$ w=\sum_{x\in P(X)}e_{x}\times u^{x} $$ 

where

 $$ u^{x}=\sum_{y\in P(Y)}c^{x y}e_{y}\in\mathcal{A}_{\bullet}\left(X\right). $$ 

It is obvious that  $ u^x $ are uniquely determined as so are the coefficients  $ c^{xy} $. Let us show that, in fact,  $ u^x \in \Omega_\bullet(X) $. Let us define the coefficients  $ \delta_x', \in \{0,1,-1\} $ by

 $$ \partial e_{x}=\sum_{x^{\prime}\in R(X)}\delta_{x}^{x^{\prime}}e_{x^{\prime}}. $$ 

We have by the product rule

 $$ \begin{array}{r l}{\partial w}&{=\displaystyle\sum_{x\in P(X)}\partial e_{x}\times u^{x}+\displaystyle\sum_{x\in P(X)}e_{x}\times\partial u^{x}}\\ &{=\displaystyle\sum_{x\in P(X)}\displaystyle\sum_{x^{\prime}\in R(X)}\delta_{x^{\prime}}^{x^{\prime}}e_{x^{\prime}}\times u^{x}+\displaystyle\sum_{x\in P(X)}e_{x}\times\partial u^{x}}\\ &{=\displaystyle\sum_{x\in R(X)}\displaystyle\sum_{x^{\prime}\in P(X)}\delta_{x^{\prime}}^{x}e_{x}\times u^{x^{\prime}}+\displaystyle\sum_{x\in P(X)}e_{x}\times\partial u^{x}}\\ &{=\displaystyle\sum_{x\in P(X)}e_{x}\times\left(\displaystyle\sum_{x^{\prime}\in P(X)}\delta_{x^{\prime}}^{x}u^{x^{\prime}}+\partial u^{x}\right)}\\ &{\quad+\displaystyle\sum_{x\in R(X)\setminus P(X)}e_{x}\times\left(\displaystyle\sum_{x^{\prime}\in P(X)}\delta_{x^{\prime}}^{x}u^{x^{\prime}}\right).}\end{array} $$ 

Since  $ \partial w $ is allowed on Z, it follows that

 $$ \sum_{x\in R(X)\backslash P(X)}e_{x}\times\left(\sum_{x^{\prime}\in P(X)}\delta_{x^{\prime}}^{x}u^{x^{\prime}}\right)=0. $$ 

On the other hand, since  $ \partial w \in \Omega_{\bullet}(Z) $, we have a representation

 $$ \partial w=\sum_{x\in P(X)}e_{x}\times\widetilde{u}^{x} $$ 

where  $ \widetilde{u}^x \in \mathcal{A}_\bullet(X) $. Comparison with the previous computation of  $ \partial w $ yields

 $$ \widetilde{u}^{x}=\sum_{x^{\prime}\in P(X)}\delta_{x^{\prime}}^{x}u^{x^{\prime}}+\partial u^{x}. $$ 

Since  $ u^x' \in \mathcal{A}_\bullet(X) $, it follows that  $ \partial u^x \in \mathcal{A}_\bullet(X) $, which proves that  $ u^x \in \Omega_\bullet(X) $. The second identity in (7.22) is proved similarly.

Let us introduce in  $ \mathcal{A}_p(X) $ the  $ \mathbb{K} $-scalar product as follows: for all  $ u, v \in \mathcal{A}_p(X) $

 $$ [u,v]:=\sum_{x\in P(X)}u^{x}v^{x}. $$ 

If K = R then this is a proper scalar product, but for a general field K there is no positivity property (in fact, it can happen that  $ [u, u] = 0 $). Set also

 $$ \Omega_{p}^{\perp}\left(X\right)=\left\{u\in\mathcal{A}_{p}\left(X\right):\left[u,v\right]=0for all v\in\Omega_{p}\left(X\right)\right\}. $$ 

If $\mathbb{K} = \mathbb{R}$ then $\Omega_p^\perp$ is a proper orthogonal complement of $\Omega_p$ in $\mathcal{A}_p$ and $\mathcal{A}_p = \Omega_p \oplus \Omega_p^\perp$. For a general $\mathbb{K}$, this is not true, as $\Omega_p$ and $\Omega_p^\perp$ may have a non-trivial intersection, but for any field $\mathbb{K}$ it is still true that

 $$ \dim\Omega_{p}+\dim\Omega_{p}^{\perp}=\dim\mathcal{A}_{p}. $$ 

Lemma 7.14 If  $ u \in \Omega_p^\perp(X) $ and  $ v \in \mathcal{A}_q(Y) $ then  $ u \times v \in \Omega_r^\perp(Z) $ where  $ r = p + q $. Also, if  $ u \in \mathcal{A}_p(X) $ and  $ v \in \Omega_q^\perp(Y) $ then  $ u \times v \in \Omega_r^\perp(Z) $.

Proof. We need to prove that, for any  $ w \in \Omega_r(Z) $,

 $$ [u\times v,w]=0, $$ 

assuming that  $ u \in \Omega_p^\perp(X) $ (the second claim is proved similarly). We have

 $$ \begin{align*}[u\times v,w]&\ =\ \sum_{z\in P_{r}(Z)}(u\times v)^{z}w^{z}\\&=\ \sum_{z\in P_{r}(Z)}(-1)^{L(z)}u^{x}v^{y}w^{z}\ (x,y are projections of z)\\&=\ \sum_{x\in P_{p}(X)}\sum_{u\in P_{q}(Y)}\sum_{z\in\Pi_{x,y}}(-1)^{L(z)}u^{x}v^{y}w^{z}.\end{align*} $$ 

By Corollary 7.13, $w$ is a sum of the terms $\varphi \times \psi$ where $\varphi \in \Omega_\bullet(X)$ and $\psi \in \mathcal{A}_\bullet(Y)$, so that it suffices to prove (7.23) for $w = \varphi \times \psi$. Let $\varphi \in \Omega_p(X)$ and, hence, $\psi \in \mathcal{A}_q(Y)$. Then we have

 $$ w^{z}=(-1)^{L(z)}\varphi^{x}\psi^{y} $$ 

and

 $$ [u\times v,w]=\sum_{x\in P_{p}(X)}\sum_{y\in P_{q}(Y)}\sum_{z\in\Pi_{x,y}}u^{x}\varphi^{x}v^{y}\psi^{y}. $$ 

Since

 $$ \sum_{x\in P_{p}(X)}u^{x}\varphi^{x}=[u,\varphi]=0, $$ 

we obtain (7.23). If  $ \varphi \in \Omega_p' $ with  $ p' \neq p $, then  $ w^z = 0 $ for any  $ z \in \Pi_{x,y} $ with  $ x \in P_p(X) $, and (7.23) is trivially satisfied.

### 7.6 Proof of Künneth formula

The main part of the proof of Theorem 7.6 is contained in the following theorem.

Theorem 7.15 Let $P(X)$ and $P(Y)$ be two regular path complexes and let $P(Z) = P(X) \oplus P(Y)$ be their Cartesian product. Then any $\partial$-invariant path $w$ on $Z$ admits a representation in the form

 $$ w=\sum_{i=1}^{k}u_{i}\times v_{i} $$ 

for some finite k, where uᵢ and vᵢ are ∂-invariant paths on X and Y, respectively.

Proof. The representation (7.24) is simple in a special case when the path complexes  $ P(X) $ and  $ P(Y) $ are perfect, that is, when all allowed paths are  $ \partial $-invariant. Indeed, by Proposition 7.12, any  $ w \in \Omega_r(Z) $ admits a representation in the form (7.15), where  $ e_x $ and  $ e_y $ are allowed paths on  $ X $ and  $ Y $ respectively. By the assumption of the perfectness of  $ P(X) $ and  $ P(Y) $, the paths  $ e_x $ and  $ e_y $ are  $ \partial $-invariant, so that (7.15) implies (7.24).

For arbitrary path complexes $P(X)$ and $P(Y)$, the previous argument does not work since $e_x \times e_y$ does not have to be $\partial$-invariant. Hence, we need a more elaborated strategy. Given two subspaces $U \subset \mathcal{A}_p(X)$ and $V \subset \mathcal{A}_q(Y)$, denote by $U \times V$ the subspace of $\mathcal{A}_r(Z)$ that is spanned by all products $u \times v$ with $u \in U$ and $v \in V$. For any $r \geq 0$ set

 $$ \widetilde{\Omega}_{r}\left(Z\right)=\sum_{p+q=r}\Omega_{p}\left(X\right)\times\Omega_{q}\left(Y\right), $$ 

that is, $\Omega_r(Z)$ is the space of paths on $Z$ that is spanned by all paths of the form $u \times v$ where $u \in \Omega_p(X)$ and $v \in \Omega_q(Y)$ with some $p, q \geq 0$ such that $p + q = r$. By Proposition 7.5, we have $u \times v \in \Omega_r(Z)$ whence it follows that

 $$ \widetilde{\Omega}_{r}\left(Z\right)\subset\Omega_{r}\left(Z\right). $$ 

The existence of the representation (7.24) is equivalent to the opposite inclusion, that is, to the identity

 $$ \widetilde{\Omega}_{r}\left(Z\right)=\Omega_{r}\left(Z\right). $$ 

In fact, it suffices to show that

 $$ \dim\Omega_{r}\left(Z\right)\leq\dim\widetilde{\Omega}_{r}\left(Z\right). $$ 

Consider also the space

 $$ \widetilde{\mathcal{A}}_{r}\left(Z\right)=\sum_{p+q=r}\mathcal{A}_{p}\left(X\right)\times\mathcal{A}_{q}\left(Y\right). $$ 

By definition of the cross product, all paths in  $ \widetilde{A}_{r}(Z) $ are allowed, that is,

 $$ \widetilde{\mathcal{A}}_{r}\left(Z\right)\subset\mathcal{A}_{r}\left(Z\right). $$ 

By Proposition 7.12, any path from $\Omega_{r}(Z)$ is a linear combination of paths $e_{x} \times e_{y}$ with allowed $x, y$, which means that

 $$ \Omega_{r}\left(Z\right)\subset\widetilde{\mathcal{A}}_{r}\left(Z\right). $$ 

In particular, we have also

 $$ \widetilde{\Omega}_{r}\left(Z\right)\subset\widetilde{\mathcal{A}}_{r}\left(Z\right). $$ 

Fix some triple p, q, r with  $ p + q = r $ and consider the spaces (cf. Section 7.5):

•  $ \Omega_{p}^{\perp}(X) $-an orthogonal complement of  $ \Omega_{p}(X) $ in  $ \mathcal{A}_{p}(X) $;

•  $ \Omega_{q}^{\perp}(Y) $ – an orthogonal complement of  $ \Omega_{q}(Y) $ in  $ \mathcal{A}_{q}(Y) $;

•  $ \Omega_{r}^{\perp}(Z) $ – an orthogonal complement of  $ \Omega_{r}(Z) $ in  $ \widetilde{\mathcal{A}}_{r}(Z) $.

Consider first the case when the field K is  $ \mathbb{R} $ or  $ \mathbb{Q} $. In this case, a linear space with a K-scalar product is represented as a direct sum of a subspace with its orthogonal complement. For each  $ u \in \mathcal{A}_p(X) $ consider a decomposition

 $$ u=u_{\Omega}+u_{\perp} $$ 

where  $ u_\Omega \in \Omega_p(X) $ and  $ u_\perp \in \Omega_p^\perp(X) $, and a similar decomposition  $ v = v_\Omega + v_\perp $ for  $ v \in \mathcal{A}_q(Y) $. Then we have

 $$ u\times v=u_{\Omega}\times v_{\Omega}+u_{\Omega}\times v_{\perp}+u_{\Omega}\times v_{\perp}+u_{\perp}\times v_{\perp}. $$ 

Here we have  $ u_\Omega \times v_\Omega \in \tilde{\Omega}_r(Z) $, while by Lemma 7.14 all other terms in the right hand side belong to  $ \Omega_r^\perp(Z) $, whence it follows that

 $$ u\times v\in\widetilde{\Omega}_{r}\left(Z\right)+\Omega_{r}^{\perp}\left(Z\right). $$ 

Since  $ \widetilde{A}_{r}(Z) $ is spanned by the products  $ u \times v $ where  $ u, v $ are allowed, we obtain that

 $$ \widetilde{\mathcal{A}}_{r}\left(Z\right)=\widetilde{\Omega}_{r}\left(Z\right)+\Omega_{r}^{\perp}\left(Z\right). $$ 

Comparing with the decomposition

 $$ \widetilde{\mathcal{A}}_{r}\left(Z\right)=\Omega_{r}\left(Z\right)\oplus\Omega_{r}^{\perp}\left(Z\right), $$ 

we obtain  $ (7.25) $.

Consider now the most general case of an arbitrary field K. Let us introduce the following notation:

 $$ \begin{array}{r c l}{a_{p}}&{=}&{\dim\mathcal{A}_{p}\left(X\right),~a_{q}=\dim\mathcal{A}_{q}\left(Y\right),~a_{r}=\dim\widetilde{\mathcal{A}}_{r}\left(Z\right),}\\ {\omega_{p}}&{=}&{\dim\Omega_{p}\left(X\right),~\omega_{q}=\dim\Omega_{q}\left(Y\right),~\omega_{r}=\dim\Omega_{r}\left(Z\right),}\\ \end{array} $$ 

and observe that

 $$ \dim\Omega_{p}^{\perp}\left(X\right)=a_{p}-\omega_{p},\dim\Omega_{q}^{\perp}\left(Y\right)=a_{q}-\omega_{q},\dim\Omega_{r}^{\perp}\left(Z\right)=a_{r}-\omega_{r}. $$ 

Let us prove that

 $$ a_{r}=\sum_{p+q=r}a_{p}a_{q}. $$ 

Indeed,  $ \mathcal{A}_p(X) $ is spanned by all elementary paths  $ e_x $ with  $ x \in P_p(X) $ and  $ \mathcal{A}_q(Y) $ is spanned by all elementary paths  $ e_y $ with  $ y \in P_q(Y) $. Therefore,  $ \widetilde{\mathcal{A}}_r(Z) $ is spanned by all products  $ e_x \times e_y $ for  $ x, y $ as above over all possible  $ p, q $ such that  $ p + q = r $. The number of such products  $ e_x \times e_y $ is equal to the right hand side of (7.27), so that the identity (7.27) follows from the linear independence of the family  $ \{e_x \times e_y\} $ (cf. Proposition 7.12).

It follows from the above argument that

 $$ \dim\left(\mathcal{A}_{p}\left(X\right)\times\mathcal{A}_{q}\left(Y\right)\right)=a_{p}a_{q} $$ 

and that

 $$ \widetilde{\mathcal{A}}_{r}\left(Z\right)=\bigoplus_{p+q=r}\left(\mathcal{A}_{p}\left(X\right)\times\mathcal{A}_{q}\left(Y\right)\right). $$ 

Let us show that, for any subspaces  $ U \subset \mathcal{A}_p(X) $ and  $ V \subset \mathcal{A}_q(Y) $,

 $$ \dim\left(U\times V\right)=\dim U\dim V. $$ 

Indeed, let  $ u_1, u_2, \ldots u_k $ be a basis in  $ U $ and  $ v_1, \ldots v_l $ be a basis in  $ V $. Then  $ U \times V $ is spanned by all products  $ u_i \times v_j $, so that

 $$ \dim\left(U\times V\right)\leq kl. $$ 

Let us complement the basis $\{u_i\}$ to a basis in $\mathcal{A}_p(X)$ by adding additional paths $u_1',...,u_k',$ and the similarly complement $\{v_j\}$ to a basis in $\mathcal{A}_q(Y)$ by adding $v_1',...,v_l'$. Set $U' = \text{span}\{u_i\}$ and $V' = \text{span}\{v_j\}$. Then

 $$ \mathcal{A}_{p}\left(X\right)\times\mathcal{A}_{q}\left(Y\right)=\left(U+U^{\prime}\right)\times\left(V+V^{\prime}\right)=U\times V+U\times V^{\prime}+U^{\prime}\times V+U^{\prime}\times V^{\prime} $$ 

whence by  $ (7.28) $ and  $ (7.31) $

 $$ \begin{align*}a_{p}a_{q}\quad&\leq\quad\dim\left(U\times V\right)+\dim\left(U\times V^{\prime}\right)+\dim\left(U^{\prime}\times V\right)+\dim\left(U^{\prime}\times V^{\prime}\right)\\&\leq\quad kl+kl^{\prime}+k^{\prime}l+k^{\prime}l^{\prime}.\end{align*} $$ 

However, the right hand side here is equal to  $ (k + k')(l + l') = a_p a_q $, which implies that we must have the equality case in (7.32), in particular,  $ \dim(U \times V) = kl $, which proves (7.30).

By Lemma 7.14, we have

 $$ \Omega_{p}^{\perp}\left(X\right)\times\mathcal{A}_{q}\left(Y\right)\subset\Omega_{r}^{\perp}\left(Z\right) $$ 

and

 $$ \mathcal{A}_{p}\left(X\right)\times\Omega_{q}^{\perp}\left(Y\right)\subset\Omega_{r}^{\perp}\left(Z\right) $$ 

so that

 $$ \sum_{p+q=r}\left(\left(\Omega_{p}^{\perp}\left(X\right)\times\mathcal{A}_{q}\left(Y\right)\right)+\left(\mathcal{A}_{p}\left(X\right)\times\Omega_{q}^{\perp}\left(Y\right)\right)\right)\subset\Omega_{r}^{\perp}\left(Z\right). $$ 

It follows from (7.29) and (7.33) that

 $$ \sum_{p+q=r}\dim\left(\left(\Omega_{p}^{\perp}\left(X\right)\times\mathcal{A}_{q}\left(Y\right)\right)+\left(\mathcal{A}_{p}\left(X\right)\times\Omega_{q}^{\perp}\left(Y\right)\right)\right)\leq\dim\Omega_{r}^{\perp}\left(Z\right). $$ 

Note that the subspaces  $ \Omega_p^\perp(X) \times \mathcal{A}_q(Y) $ and  $ \mathcal{A}_p(X) \times \Omega_q^\perp(Y) $ have intersection  $ \Omega_p^\perp(X) \times \Omega_q^\perp(Y) $, which implies that

 $$ \begin{align*}&\dim\left(\left(\Omega_{p}^{\perp}\left(X\right)\times\mathcal{A}_{q}\left(Y\right)\right)+\left(\mathcal{A}_{p}\left(X\right)\times\Omega_{q}^{\perp}\left(Y\right)\right)\right)\\=&\dim\left(\Omega_{p}^{\perp}\left(X\right)\times\mathcal{A}_{q}\left(Y\right)\right)+\dim\left(\mathcal{A}_{p}\left(X\right)\times\Omega_{q}^{\perp}\left(Y\right)\right)\\&-\dim\left(\Omega_{p}^{\perp}\left(X\right)\times\Omega_{q}^{\perp}\left(Y\right)\right)\\=&\left(a_{p}-\omega_{p}\right)a_{q}+a_{p}\left(a_{q}-\omega_{q}\right)-\left(a_{p}-\omega_{p}\right)\left(a_{q}-\omega_{q}\right)\\=&\ a_{p}a_{q}-\omega_{p}\omega_{q}.\end{align*} $$ 

Hence,

 $$ \sum_{p+q=r}\left(a_{p}a_{q}-\omega_{p}\omega_{q}\right)\leq a_{r}-\omega_{r}. $$ 

 $$ \omega_{r}\leq\sum_{p+q=r}\omega_{p}\omega_{q}. $$ 

Combining with  $ (7.27) $ we obtain

Finally, we are left to observe that

 $$ \sum_{p+q=r}\omega_{p}\omega_{q}=\dim\widetilde{\Omega}_{r}\left(Z\right), $$ 

whence (7.25) follows. ■

Proof of Theorem 7.6. The isomorphism (7.12) follows from (7.11) and the Künneth theorem (9.12), so we only need to prove (7.11). Define the tensor product of graded linear spaces

 $$ \mathcal{A}_{\bullet}\left(X,Y\right)=\mathcal{A}_{\bullet}\left(X\right)\otimes\mathcal{A}_{\bullet}\left(Y\right) $$ 

and a linear mapping

 $$ \Phi:\mathcal{A}_{r}\left(X,Y\right)\rightarrow\mathcal{A}_{r}\left(Z\right) $$ 

that is defined by

 $$ \Phi\left(e_{x}\otimes e_{y}\right)=e_{x}\times e_{y} $$ 

for all  $ x \in P_p(X) $ and  $ y \in P_q(Y) $ with  $ p + q = r $. In fact, we have

 $$ \Phi\left(\mathcal{A}_{r}\left(X,Y\right)\right)=\widetilde{\mathcal{A}}_{r}\left(Z\right) $$ 

where  $ \widetilde{\mathcal{A}}_{r}(Z) $ is defined by (7.29). It follows from the argument in the proof of Theorem 7.15 that the mapping  $ \Phi $ is injective.

Consider now the tensor product of the chain complexes

 $$ \Omega_{\bullet}\left(X,Y\right)=\Omega_{\bullet}\left(X\right)\otimes\Omega_{\bullet}\left(Y\right) $$ 

and observe that

 $$ \Phi\left(\Omega_{r}\left(X,Y\right)\right)=\widetilde{\Omega}_{r}\left(Z\right). $$ 

Since by Theorem 7.15

 $$ \widetilde{\Omega}_{r}\left(Z\right)=\Omega_{r}\left(Z\right), $$ 

we obtain that the mapping  $ \Phi $ provides a linear isomorphism of the spaces  $ \Omega_\bullet(X,Y) $ and  $ \Omega_\bullet(Z) $. Moreover, since  $ \Phi $ commutes with  $ \partial $ by (9.11) and the product rule of Proposition 7.3,  $ \Phi $ provides an isomorphism of the chain complexes  $ \Omega_\bullet(X,Y) $ and  $ \Omega_\bullet(Z) $, which finishes the proof.

## 8 Minimal paths and hole detection

1he elements of  $ H_{p}(G) $ can be regarded as p-dimensional holes in the digraph G. To make this notion more geometric, we can work with representatives of the homologies classes, that are closed p-paths. Recall that two closed p-paths u and v are homological, that is, represent the same homology class, if u - v is exact. We write in this case  $ u \sim v $.

For any p-path v define its length by

 $$ \ell\left(v\right)=\sum_{i_{0},\ldots,i_{p}\in V}\left|v^{i_{0}\ldots i_{p}}\right|. $$ 

Given a closed p-paths  $ v_{0} $, consider the minimization problem

 $$ \ell\left(v\right)\mapsto\min\quad for v\sim v_{0}. $$ 

This problem has always a solution, although not necessarily unique. Any solution of  $ (8.1) $ is called a minimal p-path. It is hoped that minimal p-paths (in a given homology class) match our geometric intuition of what holes in a graph should be. In this section we give some examples of minimal paths to support this claim.

Example 8.1 Consider the digraph  $  G = (V, E)  $ as on Fig. 35.

By Theorem 5.4, we can remove successively the vertices 9, B, C, A, D (and their adjacent edges) without changing the homologies. Then by Theorem 5.7 we can remove the vertices 7, 6, 8 equally without changing the homologies. We are left with the graph  $ G' = (V', E') $ where  $ V' = \{0, 1, 2, 3, 4, 5\} $ and  $ E' = \{01, 12, 23, 34, 45, 50\} $. By Proposition 4.7 we obtain  $ \dim H_1(G) = 1 $, while  $ H_p(G) = \{0\} $ for all  $ p \geq 2 $.

The following closed 1-path is a minimal path in the non-trivial homology class of H1(G):

 $$ v=e_{01}+e_{12}+e_{23}+e_{34}+e_{45}+e_{50}, $$ 

that is obviously associated with a hexagonal hole on Fig. 35.

Example 8.2 Consider a digraph  $  G = (V, E)  $ on Fig. 36.

Removing successively the vertices A, B, 8, 9, 6, 7 by Theorem 5.4, we obtain a digraph  $ G' = (V', E') $ with  $ V' = \{0, 1, 2, 3, 4, 5\} $ and  $ E' = \{02, 03, 04, 05, 12, 13, 14, 15, 24, 25, 34, 35\} $ that has

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//dc096c31-544b-4ea1-a983-941989f11f9c/markdown_0/imgs/img_in_image_box_396_186_771_498.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A09Z%2F-1%2F%2F4ec9280a3e63e0f9a6d4ee524e5ba1ec8c0b710f683672ebe8280a76e7ff8e2e" alt="Image" width="30%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 35: A digraph with 14 vertices and 23 edges</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//dc096c31-544b-4ea1-a983-941989f11f9c/markdown_0/imgs/img_in_image_box_436_642_761_962.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A09Z%2F-1%2F%2Fb375ae068cdfa249dc0c61d18895b2339b22e61ac15cbb8ae16541f04c4f09eb" alt="Image" width="26%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 36: A digraph G with 12 vertices and 32 edges.</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//dc096c31-544b-4ea1-a983-941989f11f9c/markdown_0/imgs/img_in_image_box_266_1095_925_1367.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-13T05%3A53%3A09Z%2F-1%2F%2F729817981ecf68663d3d3958d72bf1fdbf564e225fd8d9bc60d8930c1c1967fa" alt="Image" width="53%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 37: Two representations of the digraph  $ G' $</div> </div>


the same homologies as G. The digraph  $ G' $ is shown in two ways on Fig. 37. Clearly, the second representation of this graph is reminiscent of an octahedron.

The digraph  $ G' $ is the same as the 2-dimensional sphere-graph of Example 6.17 (cf. Fig. 24). Hence, we obtain by (6.22) that  $ \dim H_{2}(G) = 1 $ while  $ H_{p}(G) = \{0\} $ for p = 1 and p > 2.

The following closed 2-path is a minimal path in the non-trivial homology class of H2(G):

 $$ v=e_{024}-e_{025}-e_{034}+e_{035}-e_{124}+e_{125}+e_{134}-e_{135}, $$ 

that is a 2-path that determines a 2-dimensional hole in G given by the octahedron. Note that on Fig. 36 this octahedron is hardly visible, but it can be computed purely algebraically as shown above.

## 9 Appendix: Elements of homological algebra

### 9.1 Cochain complexes

A cochain complex X is a sequence

 $$ 0\quad\rightarrow\quad X^{0}\quad\stackrel{d}{\rightarrow}\quad X^{1}\quad\stackrel{d}{\rightarrow}\quad\ldots\quad\stackrel{d}{\rightarrow}\quad X^{p-1}\quad\stackrel{d}{\rightarrow}\quad X^{p}\quad\stackrel{d}{\rightarrow}\ldots $$ 

of vector spaces $\{X^p\}_{p=0}^\infty$ over a field $\mathbb{K}$ and linear mappings $d:X^p \to X^{p+1}$ with the property that $d^2 = 0$ at each level. To distinguish the operators $d$ on different spaces, we will denote by $d|_{X^p}$ the operator $d:X^p \to X^{p+1}$. The condition $d^2 = 0$ means that

 $$ \operatorname{Im}d|_{X^{p}-1}\subset\ker d|_{X^{p}}. $$ 

This allows to define the de Rham cohomologies of the complex X by

 $$ H^{p}\left(X\right)=\ker d|_{X^{p}}\left/Im d\right|_{X^{p-1}} $$ 

where  $ X^{-1} := \{0\} $. The sequence (9.1) is called exact if  $ H^{p}(X) = \{0\} $ for all  $ p \geq 0 $.

We always assume that the spaces  $ X^{p} $ are finitely dimensional.

Lemma 9.1 We have for any  $ p \geq 0 $

 $$ \begin{array}{r l r}{\dim H^{p}\left(X\right)}&{=}&{\dim X^{p}-\dim d X^{p}-\dim d X^{p-1}}\end{array} $$ 

 $$ \begin{array}{r l}{=}&{{}\operatorname{d i m}\ker d|_{X^{p}}+\operatorname{d i m}\ker d|_{X^{p-1}}-\operatorname{d i m}X^{p-1}.}\end{array} $$ 

Proof. By definition, we have

 $$ \dim H^{p}\left(X\right)=\dim\ker d|_{X^{p}}-\dim\operatorname{Im}d|_{X^{p-1}}. $$ 

Applying the nullity-rank theorem to the mapping d : Xp → Xp+1, we obtain

 $$ \dim\ker d|_{X^{p}}=\dim X^{p}-\dim\operatorname{Im}d|_{X^{p}}. $$ 

Substituting into (9.4), we obtain (9.2).

In the same way, substituting into (9.4) the identity

 $$ \dim\operatorname{Im}d|_{X^{p-1}}=\dim X^{p-1}-\dim\ker d|_{X^{p-1}}, $$ 

we obtain (9.3). ■

Lemma 9.2 For a finite cochain complex

 $$ 0\quad\rightarrow\quad X^{0}\quad\stackrel{d}{\rightarrow}\quad X^{1}\quad\stackrel{d}{\rightarrow}\quad\ldots\quad\stackrel{d}{\rightarrow}\quad X^{n-1}\quad\stackrel{d}{\rightarrow}\quad X^{n}\quad\stackrel{d}{\rightarrow}0, $$ 

the following identity is satisfied

 $$ \sum_{k=0}^{n}\left(-1\right)^{k}\dim H^{k}\left(X\right)=\sum_{k=0}^{n}\left(-1\right)^{k}\dim X^{k}. $$ 

In particular, if the sequence  $ (9.5) $ is exact, then

 $$ \sum_{k=0}^{n}\left(-1\right)^{k}\dim X^{k}=0. $$ 

Proof. We have by (9.2)

 $$ \begin{array}{r c l}{\displaystyle\sum_{k=0}^{n}\left(-1\right)^{k}\dim H^{k}\left(X\right)}&{=}&{\displaystyle\sum_{k=0}^{n}\left(-1\right)^{k}\dim X^{k}-\displaystyle\sum_{k=0}^{n}\left(-1\right)^{k}\dim d X^{k}-\displaystyle\sum_{k=0}^{n}\left(-1\right)^{k}\dim d X^{k-1}}\\ {}&{=}&{\displaystyle\sum_{k=0}^{n}\left(-1\right)^{k}\dim X^{k}-\displaystyle\sum_{k=0}^{n-1}\left(-1\right)^{k}\dim d X^{k}-\displaystyle\sum_{j=0}^{n-1}\left(-1\right)^{j+1}\dim d X^{j}}\\ {}&{=}&{\displaystyle\sum_{k=0}^{n}\left(-1\right)^{k}\dim X^{k},}\\ \end{array} $$ 

whence (9.6) follows. If in addition the sequence (9.5) is exact then the left hand side of (9.6) vanishes, whence (9.7) follows. ■

For any finite cochain complex (9.5), define its Euler characteristic by

 $$ \chi\left(X\right)=\sum_{p=0}^{n}\left(-1\right)^{p}\dim X^{p}. $$ 

Then (9.6) implies

 $$ \chi\left(X\right)=\sum_{k=0}^{n}\left(-1\right)^{k}\dim H^{k}\left(X\right). $$ 

### 9.2 Chain complexes

Given a cochain complex (9.1) with finite-dimensional spaces  $ X^p $, denote by  $ X_p $ the dual space to  $ X^p $ and by  $ \partial $ the dual operator to  $ d $. Then we obtain a chain complex

 $$ 0\ \leftarrow\ X_{0}\ \stackrel{\partial}{\leftarrow}\ X_{1}\ \stackrel{\partial}{\leftarrow}\ \ldots\ \stackrel{\partial}{\leftarrow}\ X_{p-1}\ \stackrel{\partial}{\leftarrow}\ X_{p}\ \stackrel{\partial}{\leftarrow}\ \ldots $$ 

Denoting by  $ \left(\cdot,\cdot\right) $ the natural pairing of dual spaces.

For  $ \omega \in X^p $ and  $ v \in X_p $ we write  $ \omega \perp v $ if  $ (\omega, v) = 0 $. If  $ S $ is a subset of  $ X^p $ then  $ S^\perp $ denotes the annihilator in the dual space  $ X_p $, that is,

 $$ S^{\perp}=\{v\in X_{p}:\omega\perp v\quad\forall\omega\in S\}. $$ 

Clearly,  $ S^{\perp} $ is a linear subspace of  $ X_{p} $. In the same way one defines the annihilator of subsets of  $ X_{p} $.

By definition we have

 $$ (d\omega,v)=(\omega,\partial v) $$ 

for all  $ \omega \in X^p $ and  $ v \in X_{p+1} $. Since  $ d^2 = 0 $, it follows that also  $ \partial^2 = 0 $. Hence, one can define the homologies of the chain complex (9.8) by

 $$ H_{p}\left(X\right)=\ker\partial|_{X_{p}}\left/\mathrm{Im}\partial\right|_{X_{p+1}}. $$ 

By duality we have

 $$ \ker\partial|_{X_{p}}=(\operatorname{I m}d|_{X^{p-1}})^{\perp},\qquad\ker d|_{X^{p}}=\left(\operatorname{I m}\partial|_{X_{p+1}}\right)^{\perp}. $$ 

Lemma 9.3 The spaces  $ H^{p}(X) $ and  $ H_{p}(X) $ are dual. In particular,  $ \dim H^{p}(X) = \dim H_{p}(X) $.

Proof. Let $\omega \in X^p$ be a representative of an element of $H^p(X)$ and $v \in X_p$ be a representative of an element of $H(X_p)$. Let us show that the pairing $(\omega, v)$ of $\omega$ and $v$ in the dual spaces $X^p$ and $X_p$ is also well-defined for the elements of $H^p(X)$ and $H_p(X)$. Indeed, $v$ is defined $\bmod \mathrm{Im} \partial|_{X_{p+1}}$, that is, $v$ and $v + \partial u$ represent the same element of $H_p(X)$ for any $u \in X_{p+1}$. Since $\omega \in \ker d|_{X^p}$, we obtain

 $$ (\omega,v)=(\omega,v+\partial u)=(\omega,v)+(d\omega,u)=(\omega,v). $$ 

In the same way,  $ (ω, v) $ does not change when adding  $ dφ $ to  $ ω $.

If $(\omega, v) = 0$ for all $v \in \ker \partial|_{X_p}$ then $\omega \perp \ker \partial|_{X_p}$ whence by (9.9) $\omega \in \operatorname{Im} d|_{X^{p}-1}$, that is, $\omega$ represent the zero element of $H^p(X)$. In the same way, if $(\omega, v) = 0$ for all $\omega \in \ker d|_{X^p}$ then $v$ represents the zero element of $H_p(X)$. Hence, $(\omega, v)$ is a pairing between $H^p(X)$ and $H_p(X)$, whence the duality of these spaces follows.

Lemma 9.4 We have for any  $ p \geq 0 $

 $$ \begin{align*}\dim H_{p}\left(X\right)\quad&=\quad\dim X_{p}-\dim\partial X_{p}-\dim\partial X_{p+1}\\&=\quad\dim\ker\partial|_{X_{p}}+\dim\ker\partial|_{X_{p+1}}-\dim X_{p+1}.\end{align*} $$ 

The proof is similar to Lemma 9.1.

### 9.3 Tensor product of chain complexes

Let $\{A_n\}$ be a sequence of finite dimensional linear spaces over $\mathbb{K}$ enumerated by an integer parameter $n$. We denote usually by $A_\bullet$ the whole sequence. Now it will be convenient to denote by $A_\bullet$ the direct sum of all $A_n$, that is

 $$ A_{\bullet}=\bigoplus_{n}A_{n} $$ 

so that $A_\bullet$ is a graded linear space. If $\{A_n\}$ is a chain complex with the boundary operator $\partial_A$ then $\partial_A$ extends linearly to an operator in $A_\bullet$ that respect a graded structure. In this case we will denote the chain complex also by $A_\bullet$. The homologies $H_n(A_\bullet)$ of the chain complex $A_\bullet$ form also a graded linear space $H_\bullet(A_\bullet)$.

Given two graded linear spaces  $ A_{\bullet} $ and  $ B_{\bullet} $ as above, define their tensor product by

 $$ A_{\bullet}\otimes B_{\bullet}=\bigoplus_{p,q}\left(A_{p}\otimes B_{q}\right), $$ 

where  $ A_p \otimes B_q $ is the tensor product over  $ \mathbb{K} $ of the linear spaces  $ A_p $ and  $ B_q $. In other words,  $ A_\bullet \otimes B_\bullet = C_\bullet $ where

 $$ C_{r}=\bigoplus_{\{p,q:p+q=r\}}\left(A_{p}\otimes B_{q}\right). $$ 

If  $ A_{\bullet} $ and  $ B_{\bullet} $ are chain complexes with the boundary operators  $ \partial_{A} $ and  $ \partial_{B} $, respectively, then define the boundary operator  $ \partial_{C} $ in  $ C_{\bullet} $ by

 $$ \partial_{C}\left(u\otimes v\right)=\left(\partial_{A}u\right)\otimes v+\left(-1\right)^{p}u\otimes\left(\partial_{B}v\right), $$ 

for all  $ u \in A_p $ and  $ v \in B_q $. It is well-known that  $ \partial_C^2 = 0 $ so that  $ C_\bullet $ with  $ \partial_C $ is a chain complex. Furthermore, by a theorem of Künneth, we have the following identity for homologies:

 $$ H_{\bullet}\left(C_{\bullet}\right)\cong H_{\bullet}\left(A_{\bullet}\right)\otimes H_{\bullet}\left(B_{\bullet}\right) $$ 

that is,

 $$ H_{r}\left(C_{\bullet}\right)\cong\bigoplus_{\left\{p,q:p+q=r\right\}}H_{p}\left(A_{\bullet}\right)\otimes H_{q}\left(B_{\bullet}\right) $$ 

(see [11]).

Let  $ A^{n} $ be a dual space to  $ A_{n} $. Then the graded linear space

 $$ A^{\bullet}=\bigoplus_{n}A^{n} $$ 

is dual to  $ A_\bullet $. Indeed, it follows from the following definition of the pairing  $ (\omega, v) $ between elements  $ \omega \in A^\bullet $ and  $ v \in A_\bullet $. If  $ \omega \in A^n $ and  $ v \in A_m $ then in the case  $ n = m $ then  $ (\omega, v) $ coincides the pairing between  $ A^n $ and  $ A_n $, whereas in the case  $ n \neq m $ set  $ (\omega, v) = 0 $. Then extend this definition by bilinearity to all  $ \omega \in A^\bullet $ and  $ v \in A_\bullet $.

Finally, observe that if  $ A_\bullet $ and  $ B_\bullet $ are two graded linear spaces then  $ A^\bullet \otimes B^\bullet $ is dual to  $ A_\bullet \otimes B_\bullet $ using the following pairing:

 $$ \left(\varphi\otimes\psi,u\otimes v\right)=\left(\varphi,u\right)\left(\psi,v\right) $$ 

for  $ \varphi \in A^\bullet $,  $ \psi \in B^\bullet $,  $ u \in A_\bullet $,  $ v \in B_\bullet $.

#### xes

Let $X$ be a cochain complex as in (9.1), and assume that each $X^p$ has a subspace $J^p$ so that $d$ is invariant on $\{J^p\}$, that is, $dJ^p \subset J^{p+1}$. Then we have a cochain sub-complex $J$ as follows:

 $$ \begin{array}{l} 0 \quad \rightarrow \quad J^{0} \quad \xrightarrow{d} \quad J^{1} \quad \xrightarrow{d} \quad \cdots \quad \xrightarrow{d} \quad J^{p-1} \quad \xrightarrow{d} \quad J^{p} \quad \xrightarrow{d} \quad \cdots \end{array} $$ 

Since the operator $d$ is well defined also on the quotient spaces $X^p/J^p$, we obtain also a cochain quotient complex $X/J$:

 $$ 0\quad\rightarrow\quad X^{0}/J^{0}\quad\stackrel{d}{\rightarrow}\quad X^{1}/J^{1}\quad\stackrel{d}{\rightarrow}\quad\ldots\quad\stackrel{d}{\rightarrow}\quad X^{p-1}/J^{p-1}\quad\stackrel{d}{\rightarrow}\quad X^{p}/J^{p}\quad\stackrel{d}{\rightarrow}\quad\ldots $$ 

Consider the annihilator of  $ J^{p} $, that is the space

 $$ (J^{p})^{\perp}=\left\{v\in X_{p}:v\perp J^{p}\right\}. $$ 

Lemma 9.5 The dual operator ∂ of d is invariant on  $ \left\{(J^{p})^{\perp}\right\} $, and the chain sub-complex

 $$ 0\quad\leftarrow\quad\left(J^{0}\right)^{\perp}\quad\stackrel{\partial}{\leftarrow}\quad\left(J^{1}\right)^{\perp}\quad\stackrel{\partial}{\leftarrow}\quad\ldots\quad\stackrel{\partial}{\leftarrow}\quad\left(J^{p-1}\right)^{\perp}\quad\stackrel{\partial}{\leftarrow}\quad\left(J^{p}\right)^{\perp}\quad\stackrel{\partial}{\leftarrow}\quad\ldots $$ 

is dual to the cochain quotient complex (9.14).

Proof. If  $ v \in (J^p)^\perp $ then, for any  $ \omega \in J^{p-1} $, we have  $ d\omega \in J^p $ and, hence,

 $$ (\omega,\partial v)=(d\omega,v)=0, $$ 

which implies  $ \partial v \in (J^{p-1})^{\perp} $. Hence,  $ \partial \text{ maps } (J^{p})^{\perp} \text{ to } (J^{p-1})^{\perp} $, so that the complex (9.15) is well-defined.

To prove the duality of (9.14) and (9.15), observe that  $ (J^p)^\perp $ is naturally isomorphic to the dual space  $ (X^p/J^p)' $. Indeed, each  $ v \in (J^p)^\perp $ defines a linear functional on  $ X^p/J^p $ simply by  $ \omega \mapsto (\omega, v) $ where  $ \omega \in X^p $ is a representative of an element of  $ X^p/J^p $. If  $ \omega_1 = \omega_2 \bmod J^p $ then  $ \omega_1 - \omega_2 \in J^p $ whence  $ (\omega_1 - \omega_2, v) = 0 $ and  $ (\omega_1, v) = (\omega_2, v) $. Clearly, the mapping  $ (J^p)^\perp \to (X^p/J^p)' $ is injective and, hence, surjective because of the identity of the dimensions of the two spaces. Finally, the duality of the operators  $ d $ and  $ \partial $ on the complexes (9.14) and (9.15) is a trivial consequence of their duality on the complexes  $ X^\bullet $ and  $ X_\bullet $.

Let us describe a specific method of constructing of d-invariant subspaces.

Lemma 9.6 Given any subspace  $ N^{p} $ of  $ X^{p} $, set

 $$ J^{p}=N^{p}+d N^{p-1}. $$ 

Then d is invariant on  $ \{J^{p}\} $. Besides, we have the following identity

 $$ (J^{p})^{\perp}=\left\{v\in(N^{p})^{\perp}:\partial v\in\left(N^{p-1}\right)^{\perp}\right\}. $$ 

Proof. The first claim follows from  $ d^{2}=0 $ since

 $$ d J^{p}\subset d N^{p}+d^{2}N^{p-1}=d N^{p}\subset J^{p+1}. $$ 

The condition  $  v \in (J^p)^{\perp}  $ means that

 $$ v\perp N^{p}\mathrm{a n d}v\perp d N^{p-1}. $$ 

Clearly, the first condition here is equivalent to  $ v \in (N^p)^\perp $, while the second condition is equivalent to

 $$ \left(d\omega,v\right)=0\forall\omega\in N^{p-1}\Leftrightarrow\left(\omega,\partial v\right)=0\forall\omega\in N^{p-1}\Leftrightarrow\partial v\bot N^{p-1}\Leftrightarrow\partial v\in\left(N^{p-1}\right)^{\perp}, $$ 

which proves (9.17). ■

### 9.5 Zigzag Lemma

Consider now three cochain complexes X, Y, Z connected by vertical linear mappings as on the diagram:

 $$ \begin{array}{ccccccc} 0 & & 0 & & 0 \\ \downarrow & & \downarrow & & \downarrow \\ 0 \quad \rightarrow & Y^{0} & \xrightarrow{d} & Y^{1} & \xrightarrow{d} Y^{2} & \rightarrow\cdots \\ & \downarrow^{\alpha} & & \downarrow^{\alpha} & & \downarrow^{\alpha} \\ 0 \quad \rightarrow & X^{0} & \xrightarrow{d} & X^{1} & \xrightarrow{d} X^{2} & \rightarrow\cdots \\ & \downarrow^{\alpha} & & \downarrow^{\alpha} & & \downarrow^{\alpha} \\ 0 \quad \rightarrow & Z^{0} & \xrightarrow{d} & Z^{1} & \xrightarrow{d} Z^{2} & \rightarrow\cdots \\ & \downarrow & & \downarrow & & \downarrow \\ & 0 & & 0 & & 0 \end{array} $$ 

Each horizontal mapping is denoted by $d$ and each vertical mapping is denoted by $\alpha$. We assume that the diagram is commutative. Let us also assume that each column in (9.19) is an exact sequence, that is, the mapping $\alpha: Y^p \to X^p$ is an injection, and $\alpha: X^p \to Z^p$ a surjection with the kernel $Y^p$. In this case we can identify $Y^p$ with a subspace of $X^p$ and $Z^p$ with the quotient $X^p/Y^p$.

Proposition 9.7 (Zigzag Lemma) Under the above conditions the sequence

 $$ 0\to H^{0}\left(Y\right)\to H^{0}\left(X\right)\to H^{0}\left(Z\right)\to\cdots\to H^{p}\left(Y\right)\to H^{p}\left(X\right)\to H^{p}\left(Z\right)\to H^{p+1}\left(Y\right)\to\cdots $$ 

is exact.

The sequence  $ (9.20) $ is called a long exact sequence in cohomology. A similar result holds for homologies of chain complexes.

The meaning of the statement is that the mappings denoted in  $ (9.20) $ by arrows, can be defined so that this sequence is exact. For example, the mappings

 $$ H^{p}\left(Y\right)\rightarrow H^{p}\left(X\right)\rightarrow H^{p}\left(Z\right) $$ 

are obvious extensions of the mapping  $ \alpha $ in (9.19), whereas the mapping  $ H^{p}(Z) \to H^{p+1}(Y) $ is defined in a more tricky way. The details of the proof can be found in [11].

One normally applies Proposition 9.7 in the following form: if X is a cochain complex (9.1) and J is its sub-complex (9.13), then the following long sequence is exact:

 $$ 0\rightarrow\cdots\rightarrow H^{p}(J)\rightarrow H^{p}(X)\rightarrow H^{p}(X/J)\rightarrow H^{p+1}(J)\rightarrow\cdots $$ 

Similarly, if X is a chain complex (9.8) and J its sub-complex, then the following long sequence is exact:

 $$ 0\leftarrow\cdots\leftarrow H_{p}(X/J)\leftarrow H_{p}(X)\leftarrow H_{p}(J)\leftarrow H_{p+1}(X/J)\leftarrow\cdots $$ 

## References

[1] Bourbaki, N., “Elements of mathematics. Algebra I. Chapters 1-3.”, 1989.

[2] Chen, Beifang, Yau, Shing-Tung, and Yeh, Yeong-Nan, Graph homotopy and Graham homotopy, Discrete Math., 241 (2001) 153-170.

[3] Dimakis A., Müller-Hoissen F., Differential calculus and gauge theory on finite sets, J. Phys. A, Math. Gen., 27 no.9, (1994) 3159-3178.

[4] Dimakis A., Müller-Hoissen F., Discrete differential calculus: Graphs, topologies, and gauge theory, J. Math. Phys., 35 no.12, (1994) 6703-6735.

[5] Gerstenhaber M., Schack S.D., Simplicial cohomology is Hochschild cohomology, J. Pure Appl. Algebra, 30 (1983) 143-156.

[6] Grigor'yan A., Muranov Yu., Yau S.-T., Graphs associated with simplicial complexes, preprint 2012.

[7] Grigor'yan A., Muranov Yu., Yau S.-T., Cohomology theories of simplicial complexes, algebras, and digraphs, preprint 2012.

[8] Grigor'yan A., Muranov Yu., Yau S.-T., Differential calculus on algebras and graphs, preprint 2012.

[9] Happel D., Hochschild cohomology of finite dimensional algebras, in: “Lecture Notes in Math. Springer-Verlag, 1404”, 1989. 108–126.

[10] Ivashchenko A. V., Contractible transformations do not change the homology groups of graphs, Discrete Math., 126 (1994) 159-170.

[11] MacLane S., "Homology", Die Grundlagen der mathematischen Wissenschaften 114, Springer, 1963.

[12] Tahbaz-Salehi, A., Jadbabaie, A., Distributed coverage verification in sensor networks without location information, IEEE Transactions on Automatic Control, 55 (2010) 1837-1849.

