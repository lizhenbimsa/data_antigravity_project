# Enhancing Investment Decisions with Sentiment Analysis: A Probabilistic Ranking Framework $ ^{*} $

Zheng Tracy Ke, Bryan Kelly & Dacheng Xiu

To cite this article: Zheng Tracy Ke, Bryan Kelly & Dacheng Xiu (20 Mar 2026): Enhancing Investment Decisions with Sentiment Analysis: A Probabilistic Ranking Framework*, Journal of the American Statistical Association, DOI:  $ \underline{\text{10.1080/01621459.2026.2643001}} $

To link to this article: https://doi.org/10.1080/01621459.2026.2643001

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//17cfdac2-770b-49d5-8ba1-2c25678a6464/markdown_0/imgs/img_in_image_box_212_740_245_779.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A36Z%2F-1%2F%2F36a1b336c6b02c6457451ac2d18588d79a018271b8b22d8fd45ddb775a648981" alt="Image" width="2%" /></div>


View supplementary material ☐

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//17cfdac2-770b-49d5-8ba1-2c25678a6464/markdown_0/imgs/img_in_image_box_210_824_249_866.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A36Z%2F-1%2F%2F8a5a1cf7992646d8e0cf35bcc626594587e594f6fd684270ef70b0644ad39ee3" alt="Image" width="3%" /></div>


Accepted author version posted online: 20 Mar 2026.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//17cfdac2-770b-49d5-8ba1-2c25678a6464/markdown_0/imgs/img_in_image_box_210_909_249_943.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A36Z%2F-1%2F%2Ff37132fcd8ebefccc24362523d21821b783a8485d21a48497170fdade82b6850" alt="Image" width="3%" /></div>


Submit your article to this journal ☐

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//17cfdac2-770b-49d5-8ba1-2c25678a6464/markdown_0/imgs/img_in_image_box_210_995_253_1031.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A37Z%2F-1%2F%2F51f3b1c1fd39c65cf2f95f7b22cb6eaa8e92f81a2bf6211d7f28e04f1649e51b" alt="Image" width="3%" /></div>


Article views: 320

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//17cfdac2-770b-49d5-8ba1-2c25678a6464/markdown_0/imgs/img_in_image_box_210_1081_247_1123.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A37Z%2F-1%2F%2F1a9556c4e69ae0082a4edd750a4955a4f5bafff9340827cd1d16427e36856b67" alt="Image" width="2%" /></div>


View related articles ☐

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//17cfdac2-770b-49d5-8ba1-2c25678a6464/markdown_0/imgs/img_in_image_box_211_1171_252_1215.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A37Z%2F-1%2F%2Fed86f9268a261fcca6a7fd8d85de631650edfa927ec04504f334d238dbdaa83f" alt="Image" width="3%" /></div>


View Crossmark data

# Enhancing Investment Decisions with Sentiment Analysis: A Probabilistic Ranking Framework $ ^{*} $

Zheng Tracy Ke $ ^{a} $, Bryan Kelly $ ^{b} $, Dacheng Xiu $ ^{c,\#} $

 $ ^{a} $Department of Statistics, Harvard University

 $ ^{b} $Yale University, AQR Capital, Management, and NBER

 $ ^{c} $Booth School of Business, University of Chicago, and NBER

#Dacheng.Xiu@chicagobooth.edu

*An earlier version of this paper circulated under the title “Predicting Returns with Text Data.”

## Abstract

We develop a probabilistic framework to extract sentiment information from text by training a model to predict and rank sentiments in newly encountered documents. Our approach imposes a joint semi-parametric model on text and ordinal response variables, addressing the challenges of sparse sentiment signals and complex response distributions. Through a word screening procedure and the use of normalized ranks, our approach achieves consistent sentiment ranking without estimating the full model. Applying our method to the Dow Jones Newswires, we demonstrate its effectiveness in extracting return-predictive signals.

Keywords: Text Mining, Machine Learning, Return Predictability, Sentiment Analysis, Screening, Topic Modeling, Penalized Likelihood

## 1 Introduction

Sentiment analysis, a key task within Natural Language Processing (NLP), focuses on extracting emotional tones and subjective information from written text. It encompasses a range of techniques, including lexicon-based approaches, machine learning, and deep learning, and is widely applied across sectors such as customer feedback evaluation, survey data interpretation, social media monitoring, healthcare management, and financial market prediction [13].

One of the most prevalent techniques within the lexicon-based approach is the dictionary method. This strategy relies on a pre-established sentiment dictionary containing lists of both positive and negative words. A sentiment score is then calculated using a weighted combination of these sentiment-charged words, where the weights potentially reflect the strength of their emotional tone and are adjusted based on word frequency.

Sentiment analysis can also be approached from a machine learning perspective: treating it as either a regression task or a classification problem. These methodologies necessitate a collection of training documents already labeled with sentiment scores. Once a set of document-wise features has been established—such as the counts of dictionary words or embeddings generated by large language models—any prevalent machine learning algorithm can be utilized, like naive Bayes, random forest, or neural networks.

In this paper, we offer a unique statistical perspective on sentiment analysis by framing it as a ranking problem. The sentiment score assigned to a training document typically assumes the form of an ordinal variable, with scales that can vary arbitrarily, such as “0 to 1” or “-10 to 10.” The precise values of these scores are not inherently meaningful, as they depend on how the training labels are mapped to sentiment categories during data preprocessing. Instead of estimating exact sentiment scores for each document—which may have limited practical value—our primary focus is on ranking the sentiments of a set of test documents in accordance with their ordinal relationships. This approach only requires estimating sentiment scores up to a monotonic transformation. In many downstream tasks, sentiment ranks are more relevant than the exact values. In Section 5, we demonstrate an application in empirical finance where sentiment ranks derived from financial news articles are utilized for portfolio construction.

Our method is founded on a semi-parametric model that encompasses two interconnected components. Firstly, we employ a fully parametric sparse topic model [2, 7], customized specifically for sentiment analysis, to model the dependence of text documents on their sentiment scores. Secondly, we utilize a nonparametric model with minimal assumptions to capture the relationship between ordinal responses and sentiment scores. Therefore, the link between these two components is established through the sentiment score of the document. Our model offers extensive flexibility, allowing for the incorporation of various types of ordinal responses, ranging from discrete (e.g., star ratings) to continuous (e.g., stock returns).

However, estimating this model poses a significant challenge: learning the exact distribution of ordinal responses is often difficult, and at times even impossible. Fortunately, our primary objective is to rank sentiments rather than predict the specific ordinal responses. Recognizing that the distribution of ordinal responses is essentially a “nuisance,” we propose an algorithm

that circumvents the need for estimating this distribution while still achieving consistent sentiment ranking. The core idea of our algorithm is a strategic integration of rank statistics, correlation screening, and topic modeling techniques.

A key distinction of our structural approach, in contrast to reduced-form lexicon-based or machine learning methods, is the adoption of a joint data-generating model for text documents and ordinal responses. This allows for a rigorous examination of the estimator's asymptotic behavior, providing valuable theoretical insights into how sentiment analysis performs under varying data dimensions and signal-to-noise ratios—insights that cannot be gained from reduced-form approaches. We consider scenarios where the number of documents approaches infinity, and we accommodate settings in which the dictionary size and average document length may either remain bounded or grow with the number of documents. This flexibility ensures that our theory is applicable in high-dimensional settings.

When the dictionary size significantly exceeds the document lengths, we impose a sparsity assumption that only a small fraction of words carry sentiment information. This assumption holds true in practical scenarios and significantly enhances the signal-to-noise ratio. Consequently, we demonstrate that our algorithm produces a consistent estimator of the sentiment score, up to a linear transformation uniquely determined by the training data. This suffices to guarantee the consistent ranking of sentiments for any given set of testing documents. Notably, our theory unveils a somewhat unexpected finding: consistent sentiment ranking can be achieved without the need for consistent parameter estimation. The underlying reason behind this lies in the inherent ordinal nature shared by both our objective of sentiment ranking, which aims to order the true sentiment scores, and the training labels themselves, which also serve as ordinal variables.

We present an application of our methodology in which we address one of the most extensively researched text-based questions in finance: the extent to which business news can explain and predict observed variations in asset prices. To conduct our analysis, we utilize the machine text feed and archive database of the Dow Jones Newswires, a highly regarded information source widely subscribed to and closely monitored by sophisticated investors, serving as a central resource for market participants. This dataset spans over 30 years and contains time-stamped articles tagged with identifiers corresponding to the relevant firms. By leveraging these identifiers, we match the articles with stock return data from CRSP, which act as the ordinal responses in our study.

To demonstrate the economic significance of our model’s statistical performance, we highlight its predictive power through a simple trading strategy. This strategy involves purchasing assets with positive sentiment from recent news and selling those with negative sentiment. The portfolio constructed using our approach delivers exceptional risk-adjusted returns in out-of-sample testing, outperforming not only off-the-shelf sentiment scores from RavenPack, the industry-leading provider of financial news sentiment, but also black-box, reduced-form predictions from transformer-based large language models. Furthermore, we utilize our framework to investigate several economic questions. For example, we investigate the impact of “fresh” versus “stale” news on return behavior and examine how disparities in news assimilation are associated with a range of stock attributes.

#### Related literature

Traditional approaches to sentiment analysis, such as the dictionary methods, rely on pre-defined sentiment dictionaries. However, these dictionaries have limitations. For instance, general sentiment dictionaries like the Harvard IV dictionary primarily capture the psychological states of words and may not be suitable for applications where sentiment information is conveyed through psychologically neutral words. On the other hand, domain-specific dictionaries like the Loughran-McDonald dictionary [10] tailored for finance are not always readily accessible in practical situations. In contrast, our method leverages ordinal labels in the training data to guide the process of sentiment analysis and automatically learns a domain-specific sentiment dictionary. This data-driven approach ensures adaptability to the specific domain of interest without relying on pre-existing dictionaries.

Ordinal classification [6] has emerged as a valuable approach in sentiment analysis to handle ordinal responses. Unlike standard multi-class classification, which assumes unordered class categories, ordinal classification embraces the ordered nature of the classes and constructs classification boundaries accordingly. An interesting recent study on this problem is presented by [15]. The authors proposed an ordinal classifier specifically designed for unstructured predictors, where imprecise information regarding the strength of associations between predictors is available. One practical application of their method is predicting star ratings based on product reviews. However, it is important to note that classification methods are typically limited to discrete ordinal responses. In our financial application discussed in Section 5, the ordinal responses correspond to continuous stock returns. While it is possible to discretize these returns, doing so would result in a large number of classes, and traditional ordinal classification methods tend to perform well with a smaller number of classes. In contrast, our method offers flexibility in accommodating various types of ordinal responses, whether they are discrete or continuous in nature.

The multinomial inverse regression (MNIR) was introduced by [14] to study text-sentiment relationships. This fully parametric model employs logistic functions to map the ordinal response to the population word frequencies. Similarly, we also adopt multinomial distributions for word counts in our approach. However, our method diverges from MNIR in the way we handle the sentiment information. We create two separate models for the text and the ordinary response instead of linking them directly, and the two models are connected by the latent sentiment score. This allows us to create a flexible model for the conditional distribution of ordinal response given its sentiment score, making our approach semi-parametric and more versatile than MNIR. Additionally, our algorithm circumvents the need to estimate the exact distribution of the ordinal response, allowing for a higher degree of flexibility in the modeling process. Because of this, our method can adapt to a broader range of scenarios and better capture the complexities inherent in sentiment analysis.

Deep neural networks (DNNs) have recently garnered significant attention for their impressive achievements across various tasks. The application of DNNs in sentiment analysis has also been widely explored; see [13] for a comprehensive survey. More recently, large-language models (LLMs) have emerged as leading benchmarks in DNN-based methods, see, e.g., [4], [11]. These LLM-based approaches primarily focus on training a general-purpose model that can be applied

to downstream tasks, such as sentiment analysis. While our method can be integrated with LLMs by replacing word counts with DNN-learned features, such as embeddings, it is important to note that our current approach already offers several advantages over DNN approaches. Our method is a “white box,” making it easy to interpret and diagnose. It is also computationally more efficient and requires fewer training documents. This not only establishes it as a valuable benchmark for sentiment analysis but also as a theoretical reference that provides critical statistical insights. Moreover, it avoids issues such as look-ahead bias, which LLMs may encounter due to their opaque use of web-based datasets. Despite its simplicity, our approach delivers performance comparable to that of LLM-based methods.

The rest of the paper is organized as follows. In Section 2, we introduce the semi-parametric model and propose a sentiment ranking algorithm called SESTM. In Section 3, we present the theoretical properties of our method. Section 4 contains numerical experiments, and Section 5 reports an empirical analysis of the stock-level news and returns via SESTM and alternative methods. We conclude the paper with further discussions in Section 6. The mathematical proofs and additional details of empirical analysis are relegated to the supplementary material.

## 2 A Probabilistic Framework for Sentiment Analysis

Consider a collection of $n$ documents, each composed using a dictionary of $m$ words, where both $n$ and $m$ are large. We represent these documents in their bag-of-words form. Specifically, for any $1 \leq i \leq n$ and $1 \leq j \leq m$, let $d_{j,i}$ represent the frequency of word $j$ in document $i$. The data matrix, denoted as $D$, is an $m \times n$ matrix defined as $D = [d_1, d_2, \ldots, d_n]$, where each $d_i \in \mathbb{R}^m$ is a word count vector of document $i$. In addition to these documents, we have access to a response variable $y_i$ for each document. This variable captures ordinal values and can either be discrete or continuous. We assume that it contains sentiment-related information. In the case of customer reviews, $y_i$ represents the associated star rating and is discrete. When analyzing financial news articles (refer to Section 5), we identify the mentioned company and utilize its stock return (before and after the news release) as $y_i$, which is a continuous value.

We assume that each document has a sentiment score  $ p_i \in [0,1] $. A score of 1 indicates a maximally positive sentiment at the document level, while a score of 0 represents a maximally negative sentiment. In Section 2.1, we introduce a joint model for  $ d_i $ and  $ y_i $, where these two quantities are interconnected through  $ p_i $. Furthermore, in Section 2.2, we propose a sentiment extraction algorithm, and in Section 2.3, we delve into the theoretical insights of our method.

### 2.1 Data generating processes

We assume the training data  $ \{(d_i, y_i)\}_{1 \leq i \leq n} $ are independently generated. Fixing  $ i $, we describe the model for  $ d_i $ and  $ y_i $, respectively, starting with the model for  $ d_i $. Let  $ \{1, 2, \ldots, m\} = S \cup N $ represent a partition of the dictionary into two sets:  $ S $, containing sentiment-charged words, and

N, containing sentiment-neutral words. Define  $ d_{[S],i} $ as the sub-vector of  $ d_i $ restricted to the indices in S, and similarly define  $ d_{[N],i} $ for sentiment-neutral words.

We denote $s_i$ and $n_i$ as the total counts of sentiment-charged and sentiment-neutral words in document $i$, respectively. A vector is referred to as a probability mass function (PMF) if its entries are nonnegative and sum up to 1. For two PMFs $Q_i \in \mathbb{R}_{+}^{|S|}$ and $\Omega_i \in \mathbb{R}_{+}^{m-|S|}$, we assume the following multinomial distributions:

 $$ d_{[S],i}\sim\mathrm{Multinomial}(s_{i},Q_{i}),\qquad d_{[N],i}\sim\mathrm{Multinomial}(n_{i},\Omega_{i}).\mathrm{(1)} $$ 

According to this model, we have  $ Q_i = s_i^{-1} \mathbb{E} d_{[S],i} $ and  $ \Omega_i = n_i^{-1} \mathbb{E} d_{[N],i} $, which characterize the distributions of sentiment-charged and sentiment-neutral words, respectively.

To allow for greater flexibility in modeling the sentiment-neutral words, we make no structural assumptions on  $ \Omega_i $.  $ {}^{1} $ However, for the sentiment-charged words, we impose a two-topic structure on  $ Q_i $. Let  $ O_+ $ and  $ O_- $ be two PMFs in  $ \mathbb{R}_{+}^{|S|} $, refereed to as the positive sentiment topic and the negative sentiment topic, respectively. Recall that  $ p_i \in [0,1] $ represents the true sentiment score of document  $ i $. We make the assumption:

 $$ Q_{i}=p_{i}O_{+}+(1-p_{i})O_{-}.(2) $$ 

Here,  $ O_{+} $ and  $ O_{-} $ describe the distribution of sentiment-charged words in a maximally positive document and maximally negative document, respectively. For any document  $ i $, the vector  $ Q_{i} $ represents the population frequencies of sentiment-charged words and is a convex combination of  $ O_{+} $ and  $ O_{-} $. By combining this assumption with the model in (1), we effectively model  $ d_{[S],i} $ using Hofmann's topic model [7], with two topics representing positive and negative sentiment.

In this model, the value of $p_i$ representing the “neutral” sentiment is unspecified. $^2$ For convenience, we define the average $p_i$ of training documents, $\tau = n^{-1} \sum_{i=1}^{n} p_i$, as the neutral sentiment. By (2), for a neutral document, its word distribution is given by $\tau O_+ + (1 - \tau) O_-$ Motivated by this observation, we define a vector of frequency, $F$, and a vector of tone, $T$:

 $$ F=\tau O_{+}+(1-\tau)O_{-},\qquad T=(1-\tau)(O_{+}-O_{-}).\ (3) $$ 

If a word has a larger value in $F$, it indicates a higher overall frequency of occurrence. The sentiment strength conveyed by a word is captured by its corresponding entry in $T$. A positive $T_{j}$ indicates that word $j$ has a greater weight in the positive sentiment topic than in the negative one,

meaning that the word has a positive tone. Conversely, a negative  $ T_{j} $ indicates a negative tone for word j. The magnitude of  $ T_{j} $ reflects the strength of the tone.

Next, we proceed to model the ordinal response variable  $ y_{i} $. Without loss of generality, we assume that  $ y_{i} $ takes real values, where  $ y_{i}=0 $ signifies the absence of a sentiment signal. To illustrate this, let's consider the example of a 5-star customer rating. If we interpret a review with 3 stars as being “neutral,” we can assign values to  $ y_{i} $ from the set  $ \{-2,-1,0,1,2\} $, representing 1 star to 5 stars, respectively. In this particular example,  $ y_{i} $ assumes discrete values. In Section 5 where we analyze financial news articles, we identify the company mentioned in the news and utilize the stock return of this company (or its idiosyncratic component) as the corresponding  $ y_{i} $. A zero return, denoted by  $ y_{i}=0 $, indicates the absence of a sentiment signal. In this case,  $ y_{i} $ is continuous. To encompass both examples, we make the assumption:

 $$ \mathbb{P}(y_{i}>0)=g(p_{i}),for a monotone increasing function g(\cdot).(4) $$ 

This model has flexibility as it does not specify the complete distribution of  $ y_{i} $. The monotone increasing property of  $ g(\cdot) $ ensures that the sign of  $ y_{i} $ is positively associated with  $ p_{i} $.

Our model can be classified as semi-parametric. The parametric component includes Model (1)-(3), which deals with word counts and is a natural adaptation of the topic model for sentiment analysis. Meanwhile, Model (4) for ordinal responses is nonparametric.

It is important to note that our primary objective is to rank sentiments rather than predict the exact ordinal responses. Therefore, we consider the distribution of  $ y_i $ as a nuisance and refrain from estimating it within our sentiment analysis framework. It is also worth mentioning that Model (4) differs from a classification model that treats the sign of  $ y_i $ as a binary class label. In our framework, not only the sign of  $ y_i $ but also its relative rank holds significance. Specifically, the rank of  $ y_i $ among  $ y_1, y_2, \ldots, y_n $ contains information regarding the overall signal strength in the  $ i^{th} $ document. This rank information is employed to “re-weight” the contribution of each document in our estimation procedure.

### 2.2 SESTM: A sentiment extraction and ranking algorithm

We now present our Sentiment Extraction via Screening and Topic Modeling (SESTM) procedure, comprising three steps. Firstly, we conduct screening to identify the set of sentiment-charged words. Secondly, we estimate the positive and negative sentiment topics  $ O_{+} $ and  $ O_{-} $. Lastly, we employ penalized maximum likelihood to estimate the sentiment score for each test document, and use these scores to rank all test documents.

Although the dictionary size m can be large, the proportion of sentiment-charged words is often small (e.g., see [16]). In the first step of SESTM, we perform screening on the dictionary to

identify these sentiment-charged words. Our screening statistic measures the frequency at which word j co-occurs with a positive value of y:

 $$ f_{j}=\frac{count of word j in documents with sgn(y)=+1}{count of word j in all documents},\qquad1\leq j\leq m,(5) $$ 

where  $ \text{sgn}(x) $ denotes the sign function that returns 1 if  $ x > 0 $ and -1 otherwise. We solely rely on the sign of  $ y $ rather than its actual value. One reason for this choice is that an ordinal variable can be arbitrarily re-coded (e.g., transforming  $ y \in \{-1, 0, 1\} $ to  $ y \in \{-2, 0, 3\} $ while preserving the order of  $ y_i $'s). Hence, it is advisable to avoid utilizing the actual values of  $ y $.

According to Model (4), the occurrence of a sentiment-charged word is correlated with the sign of y. We denote  $ \hat{\pi} \in [0,1] $ as the fraction of documents with a positive value of y, and let  $ k_j $ represent the count of word  $ j $ in all documents (i.e., the denominator in (5)). Given tuning parameters  $ (\alpha_+, \alpha_-, \kappa) $, we estimate S by

 $$ \hat{S}=\{j\colon f_{j}\geq\hat{\pi}+\alpha_{+},\mathrm{~o r~}f_{j}\leq\hat{\pi}-\alpha_{-}\}\cap\{j\colon k_{j}\geq\kappa\}. $$ 

In equation (6), we utilize asymmetric thresholds (i.e.,  $ \alpha_{+} $ can have different values) to handle scenarios where the individual signal strengths in positive sentiment terms and negative sentiment terms differ. Furthermore, given that the variance of  $ f_{j} $ decreases as  $ k_{j} $ increases, we introduce an additional threshold  $ \kappa $ for  $ k_{j} $ to avoid excessively noisy  $ f_{j} $ values.

In Step 2 of SESTM, our attention is directed towards the words in the set  $ \hat{S} $, as we aim to estimate the two sentiment topic vectors, denoted as  $ O_{+} $ and  $ O_{-} $. We denote the combined matrix as  $ O = [O_{+}, O_{-}] \in \mathbb{R}_{+}^{|S| \times 2} $. For document i, we define  $ d_{|\hat{S}|,i} $ as the sub-vector of  $ d_i $ that is restricted to the indices found in  $ \hat{S} $. Additionally, we define

 $$ H=[\hat{h}_{1},\hat{h}_{2},...,\hat{h}_{n}],\quad\text{with}\quad\hat{h}_{i}=\hat{s}_{i}^{-1}d_{[\hat{S}],i},\quad\text{and}\quad\hat{s}_{i}=\sum_{j\in\hat{S}}d_{j,i}.(7) $$ 

If  $ \hat{S} = S $, then by Model (2),  $ \hat{h}_i \approx Q_i = p_i O_++ (1 - p_i) O_- $, or in the matrix form,

 $$ H\approx O W,\qquad\mathrm{w i t h}\quad W=\left[\begin{matrix}{p_{1}}&{p_{2}}&{\cdots,}&{p_{n}}\\ {1-p_{1}}&{1-p_{2}}&{\cdots,}&{1-p_{n}}\\ \end{matrix}\right].\mathrm{(8)} $$ 

It motivates an ideal estimator  $ \hat{O}^{*}=HW'(WW')^{-1} $; however, the values of  $ p_i $ are unknown. To address this, we utilize the ordinal responses to construct a proxy for  $ p_i $ as follows:

 $$ \hat{p}_{i}=\frac{\operatorname{r a n k~o f~y_{i}~\operatorname{i n}~\{y_{l}\}_{l=1}^{n}~}}{n},\qquad1\leq i\leq n.\;(9) $$ 

Here,  $ \hat{p}_{i} $ is a normalized rank, ranging from 0 to 1, representing the relative position of  $ y_{i} $ among all ordinal responses in the training documents. When  $ y_{i} $'s have ties, we can pick an arbitrary order among the equal-valued  $ y_{i} $'s. $ ^{3} $ Our proposed estimator of O is

 $$ \hat{O}=H\hat{W}^{\prime}(\hat{W}\hat{W}^{\prime})^{-1},\qquad\mathrm{w h e r e}\quad\hat{W}=\left[\begin{matrix}{\hat{p}_{1}}&{\hat{p}_{2}}&{\cdots}&{\hat{p}_{n}}\\ {1-\hat{p}_{1}}&{1-\hat{p}_{2}}&{\cdots}&{1-\hat{p}_{n}}\\ \end{matrix}\right].\mathrm{(10)} $$ 

While  $ \hat{p}_i $’s are not estimates of  $ p_i $, interestingly, the estimator in (10) remains meaningful (see Section 2.3 for a detailed explanation). We view  $ \hat{O} $ as a linear estimator, because each of  $ \hat{O}_\pm $ is a weighted linear combination of the empirical word frequency vectors  $ \hat{h}_1, \hat{h}_2, \ldots, \hat{h}_n $, and the normalized ranks in (9) are used to determine the weights in (10).

In Step 3 of SESTM, we use  $ \hat{S} $ and  $ \hat{O} $ to estimate the sentiment  $ p $ for any new test document. Let  $ d \in \mathbb{R}_+ $ be word count vector of the new document and  $ s $ be the total count of sentiment-charged words. According to Model (1)-(2),  $ d_{\{S\}} \sim \text{Multinomial}(s, pO_+) + (1-p)O_- $. We thus estimate  $ p $ by penalized maximum likelihood estimation (MLE):

 $$ \hat{p}=\arg\max_{p\in[0,1]}\{\hat{s}^{-1}\sum_{j\in\hat{S}}d_{j}\log\Big(p\hat{O}_{+,j}+(1-p)\hat{O}_{-,j}\Big)+2\lambda[\hat{\tau}\log(p)+(1-\hat{\tau})\log(1-p)]\}, $$ 

where $\hat{\tau}=n^{-1}\sum_{i=1}^{n}\hat{p}_{i}$ is the average of normalized ranks of training documents, $\hat{s}=\sum_{j\in\hat{S}}d_{j}$ is the total count of words from $\hat{S}$, and $(d_{j},\hat{O}_{+,j},\hat{O}_{-,j})$ are the $j$th entries of the corresponding vectors. The last term, $2\lambda[\hat{\tau}\log(p)+(1-\hat{\tau})\log(1-p)]$, serves as a penalty that encourages the estimate to move toward $\hat{\tau}$. This penalty can be interpreted as imposing a prior distribution of $\mathrm{Beta}\left(1+2\lambda\hat{\tau},1+2\lambda(1-\hat{\tau})\right)$ on $p$ and maximizing the posterior likelihood. In Section 2.3, we will show that $\hat{p}$ is an estimate of the rescaled sentiment score $p^{*}=\hat{\tau}+\hat{\rho}^{-1}(p-\tau)$, where $\tau=n^{-1}\sum_{i=1}^{n}p_{i}$ is the neutral sentiment; as a result, moving $\hat{p}$ toward $\hat{\tau}$ is motivated by the observation that the majority of documents exhibit a tone that is close to neutral.

In the previous step, an estimated sentiment score is generated for each test document. In Step 4 of SESTM, these estimated sentiment scores are utilized to rank the sentiments of all test documents. A larger value of  $ \hat{p} $ corresponds to a more positive sentiment.

A summary of SESTM is given in Algorithm 1. It has four tuning parameters  $ \left(\alpha_{+}, \alpha_{-}, \kappa, \lambda\right) $. The first three parameters,  $ \left(\alpha_{+}, \alpha_{-}, \kappa\right) $, are utilized during the training phase and selected via cross-validation. The last parameter,  $ \lambda $, does not significantly impact the sentiment ranking, as will be explained in Section 2.3. Consequently, we set it to a fixed value, say, 10, which suffices to ensure that all estimates remain within the interior of the interval  $ [0,1] $.

Algorithm 1 Sentiment Extraction via Screening and Topic Modeling (SESTM).

Training. Input is the word count matrix  $ D=[d_1,d_2,\ldots,d_n] $, ordinal responses  $ y_1,y_2,\ldots,y_n $, and tuning parameters  $ (\alpha_+,\alpha_-,\kappa,\lambda) $.

1. Word screening: Compute  $ f_{j} $ for each word j as in (5). Estimate S by  $ \hat{S} $ in (6).

2. Sentiment topic estimation: Construct  $ \hat{p}_1, \ldots, \hat{p}_n $ as in (9) and obtain  $ \hat{O} = [\hat{O}_+, \hat{O}_{-}] $ as in (10). Due to noise perturbation,  $ \hat{O} $ may have negative entries. We set negative entries of this matrix to zero and re-normalize each column to have a unit  $ \ell^1 $-norm. To simplify notations, we still denote the resulting matrix by  $ \hat{O} $.

Testing: Input is  $ \hat{O}_{\pm} $ (from training) and the word count vectors of a set of new documents.

3. Sentiment scoring: Estimate the sentiment score of each new document using (11).

4. Ranking: Rank new documents in the descending order of estimated sentiment scores.

### 2.3 Some theoretical insights for SESTM

We offer further insights into SESTM, with a specific focus on elucidating the rationale behind the formula (10). While the  $ \hat{p}_{i} $ values serve as normalized rank statistics rather than estimates of the  $ p_{i} $ values themselves, we explain why this approach remains meaningful.

Same as in (3), let $F$ and $T$ be the vector of frequency and the vector of tone, respectively. Given $\hat{O}_{\pm}$, we estimate these two vectors by $\hat{F} = \hat{\tau}\hat{O}_{+} + (1 - \hat{\tau})\hat{O}_{-}$ and $\hat{T} = (1 - \hat{\tau})(\hat{O}_{+} - \hat{O}_{-})$. In Section 2.2, we have seen $H \approx OW$. Plugging it into (10) gives $\hat{O} \approx OW\hat{W}'(\hat{W}\hat{W}')^{-1}$. In addition, it is implied by (3) that $O_{+} = F + T$ and $O_{-} = F + \frac{\tau}{\tau-1}T$. Combining them gives

 $$ [\hat{F},\hat{T}]=\hat{O}\begin{bmatrix}{{{\hat{\tau}}}}&{{{1-\hat{\tau}}}} \\{{{1-\hat{\tau}}}}&{{{\hat{\tau}-1}}}\end{bmatrix}\approx[F,T]\underbrace{\begin{bmatrix}{{{1}}}&{{{1}}} \\{{{1}}}&{{{\frac{\tau}{\tau-1}}}}\end{bmatrix}W\hat{W}^{\prime}(\hat{W}\hat{W}^{\prime})^{-1}\begin{bmatrix}{{{\hat{\tau}}}}&{{{1-\hat{\tau}}}} \\{{{1-\hat{\tau}}}}&{{{\hat{\tau}-1}}}\end{bmatrix}. $$ 

The next lemma is one of our key results, which indicates that M is a diagonal matrix:

Lemma 1.

 $$ M=\mathrm{diag}(1,\frac{1-\hat{\tau}}{1-\tau}\hat{\rho}),where\hat{\rho}=[\sum_{i=1}^{n}(p_{i}-\tau)(\hat{p}_{i}-\hat{\tau})]/[\sum_{i=1}^{n}(\hat{p}_{i}-\hat{\tau})^{2}]. $$ 

Combining Lemma 1 with (12) gives  $ \hat{F} \approx F $ and  $ \hat{T} \approx \frac{1 - \hat{\tau}}{1 - \tau} \hat{\rho} T $. It shows that the linear estimator in (10) can consistently estimate  $ F $; but for  $ T $ there is an unknown bias. This bias quantity  $ \frac{1 - \hat{\tau}}{1 - \tau} \hat{\rho} $ measures the association between true sentiment scores and normalized rank statistics. $ ^{4} $

We then proceed to examine the testing stage. Let $d$ represent the word count vector of a test document, and write $\hat{h} = \hat{s}^{-1} d_{[\hat{s}]}$. The optimization in (11) essentially targets to find $\hat{p}$ such that $\hat{h} \approx \hat{p} \hat{O}_+ + (1 - \hat{p}) \hat{O}_-$.$^{5}$ To further analyze this, we introduce a re-parametrization of $\hat{p}$ by $\hat{\eta} = \hat{p} - \hat{\tau}$. Consequently, we can express $\hat{p} \hat{O}_+ + (1 - \hat{p}) \hat{O}_- = \hat{F} + \frac{\hat{\eta}}{1 - \hat{\tau}} \hat{T}$. In addition, from the preceding analysis of the training stage, we observe that $\hat{F} \approx F$ and $\hat{T} \approx \frac{1 - \hat{\tau}}{1 - \tau} \hat{\rho} T$. By combining these findings, we can interpret (11) as finding $\hat{\eta}$ such that

 $$ \hat{h}\approx F+\frac{\hat{\eta}\hat{\rho}}{1-\tau}T.\ (13) $$ 

Meanwhile, if we re-parametrize p by  $ \eta = p - \tau $, it follows from Model (2) that

 $$ \hat{h}\approx p O_{+}+(1-p)O_{-}=F+\frac{\eta}{1-\tau}T.\left(14\right) $$ 

Comparing (14) with (13), we can immediately deduce that  $ \hat{\eta} \approx \hat{\rho}^{-1}\eta $, or equivalently speaking,  $ \hat{p} \approx \hat{\tau} + \hat{\rho}^{-1}(p - \tau) $. We shall refer to  $ p^* \equiv \hat{\tau} + \hat{\rho}^{-1}(p - \tau) $ as the re-scaled sentiment score of the test document. Based on the aforementioned analysis, it can be inferred that SESTM learns the re-scaled sentiment score during the testing stage.

In the ideal case where  $ n^{-1}\sum_{i=1}^{n}(\hat{p}_{i}-p_{i})^{2} $ converges to 0 in probability, it can be shown that  $ \hat{\tau}=\tau+o_{\mathbb{P}}(1) $ and  $ \hat{\rho}=1+o_{\mathbb{P}}(1) $, so that no bias is introduced (refer to Corollary 1). However, in most practical situations, the ordinal responses only carry weak sentiment signals, leading to  $ \hat{\rho} $ being a positive number distinct from 1. In such cases,  $ p^{*} $ retains the positivity/negativity of the tone but exhibits more (or less) “extremeness” compared to the original p when  $ \hat{\rho}<1(\hat{\rho}>1) $. If

there exists an additional set of “validation” documents with known true $p_{i}$ values, we can estimate $\hat{\rho}$ by performing regression of estimated sentiment scores on true sentiment scores in this validation dataset. Consequently, it becomes possible to eliminate the bias in $\hat{p}$.

On the other hand, learning the re-scaled sentiment score is sufficient for many downstream tasks. For example, Section 5 presents an application. The test documents consist of financial news articles from a trading day. The estimated sentiment scores are utilized to identify stocks mentioned in the 50 most positive articles and 50 most negative articles, forming a portfolio based on these stocks. In this application, since the rescaled sentiments and true sentiments yield the same ranks, learning the re-scaled sentiments is sufficient.

Our final observation pertains to the penalty term in (11) and the tuning parameter  $ \lambda $. The optimization process in (11) essentially seeks to determine  $ \hat{p} = \hat{\tau} + \hat{\eta} $ in such a way that  $ \hat{h} \approx \hat{F} + \frac{\hat{\eta}}{1 - \hat{\tau}} \hat{T} $ (see (13) and the paragraph above it). The penalty term aims to shrink the value of  $ \hat{p} $ toward  $ \hat{\tau} $, which is equivalent to shrinking  $ \hat{\eta} $ toward 0. The tuning parameter  $ \lambda $ governs the degree of shrinkage applied. Different levels of shrinkage will impact the estimated sentiment scores, but they will have minimal influence on the relative sentiment ranks, because all estimates are similarly shrunk toward  $ \hat{\tau} $. Hence, the choice of  $ \lambda $ is not critical.

## 3 Statistical Theory

Recall that $n$ is the number of training documents, and that $m$ is the size of full vocabulary. Additionally, $|S|$ denotes the size of the sentiment dictionary, and $s_1, s_2, \ldots, s_n$ represent the counts of sentiment-charged words in individual documents. We use $n$ as the driving asymptotic parameter and allow $(m, |S|, s_1, \ldots, s_n)$ to depend on $n$. The training data, denoted as $(d_i, y_i)_{i=1}^n$, is generated from the model specified in equations (1) through (4).

We begin by stating a few assumptions. Firstly, we introduce a measure of the association between the word count and the sign of  $ y $. For each  $ 1 \leq j \leq m $, we define  $ \delta_j $ as follows:

 $$ \delta_{j}=\mathbb{E}[n^{-1}\sum_{i=1}^{n}(\operatorname{sgn}(y_{i})-\overline{\operatorname{sgn}}_{y})d_{j,i}],\qquad\mathrm{w h e r e}\quad\overline{\operatorname{sgn}}_{y}=n^{-1}\sum_{i=1}^{n}\operatorname{sgn}(y_{i}). $$ 

In order for the notions of “sentiment-charged” and “sentiment-neutral” to be well-defined, we expect  $ \delta_j = 0 $ for  $ j \in N $ and  $ \delta_j \neq 0 $ for  $ j \in S $. For  $ j \in S $, it can be shown (e.g., see the proof of Theorem 2) that  $ \delta_j \neq 0 $ if and only if  $ O_{+,j} - O_{-,j} \neq 0 $. For  $ j \in N $, the quantities  $ O_{\pm,j} $ are not defined. Therefore, we directly impose the assumption  $ \delta_j = 0 $ as a means to distinguish words in  $ N $ from words in  $ S $.

Assumption 1 (Word Classification).

For any  $ j \in S $,  $ O_{+,j} - O_{-,j} \neq 0 $; for any  $ j \in N $,  $ \delta_{j} = 0 $.

Finally, we need some regularity conditions. Let $s_i$ and $n_i$ be the respective total count of sentiment-charged words and sentiment-neutral words in document $i$, for $1 \leq i \leq n$. Write $\overline{s} = n^{-1} \sum_{i=1}^n s_i$ and $\overline{n} = n^{-1} \sum_{i=1}^n n_i$. Let $\Omega_{j,i}$ denote the $j^{th}$ entry of the vector $\Omega_i$, for $j \in N$. Define $q_j := (n\overline{n})^{-1} \sum_{i=1}^n n_i \Omega_{j,i}$. Let $(\tau, F, T)$ be the same as in equation (3).

##### Assumption 2 (Regularity Conditions).

There exist constants  $ a_0 \in (0, 1/2) $ and  $ c_0 > 0 $ such that the following statements hold:

(a)  $ a_{0} \leq \tau \leq 1 - a_{0} $, and  $ a_{0} \leq \hat{\tau} \leq 1 - a_{0} $.

 $$ \omega_{n}/\log(m)\rightarrow\infty,\text{where}\omega_{n}:=\min\{n,n\overline{s}\min_{j\in S}F_{j},n\overline{n}\min_{j\in N}q_{j} $$ 

(c)  $ s_1, s_2, \ldots, s_n $ satisfy that  $ \sum_{i=1}^n s_i^2 \leq Cn\overline{s}^2 $,  $ \sum_{i=1}^n s_i^{-1} \leq Cn\overline{s}^{-1} $, and  $ s_{\min}^{-1}\overline{s} \leq C\omega_n $. For each  $ j \in N $,  $ \sum_{i=1}^n n_i^2 \Omega_{j,i}^2 \leq Cn\overline{n}^2 q_j^2 $.

(d)  $ \sum_{i=1}^{n}s_{i}[p_{i}O_{+,j}+(1-p_{i})O_{-,j}]\geq c_{0}\sum_{i=1}^{n}s_{i}F_{j} $, for any  $ j\in S $.

(e)  $ |\sum_{i=1}^{n}(g(p_i)-\overline{g})(s_i-\overline{s})|\leq C\overline{s}\sqrt{n\log(m)} $, where  $ g(\cdot) $ is as in (4) and  $ \overline{g}=n^{-1}\sum_{i=1}^{n}g(p_i) $.

Condition (a) says that the average of $p_i$’s cannot be too extreme, which prevents extreme imbalance of positive/negative sentiments in training and is necessary for efficient estimation of $O_\pm$. It also says that the average of $\hat{p}_i$’s cannot be too extreme. This is not hard to satisfy: When $y_i$’s have no ties, $\hat{\tau}=1/2$ always holds; when $y_i$’s have ties, the user has the freedom to choose $\hat{p}_i$ (see Section B of the supplementary material). In Condition (b), noting that the expected total count of a word in all training documents is of the order $n\overline{s}F_j$ for $j\in S$ and $n\overline{n}q_j$ for $j\in N$, we require these expected counts to dominate $\log(m)$. This assumption is reasonable because, in real data, $n$ is usually very large. Condition (c) imposes mild balance conditions on $\{s_i\}_{i=1}^n$ and on $\{n_i\Omega_{j,i}\}_{i=1}^n$ for each $j\in N$. For example, since $\omega_n\to\infty$ by Condition (b), the requirement $s_{\min^{-1}}\overline{s}\leq C\omega_n$ still allows $s_{\min}\ll\overline{s}$ to happen. Condition (d) and Condition (e) are high-level technical conditions. The former is satisfied when all $p_i$’s are bounded away from 0 and 1,

whereas the latter holds with probability approaching one if we assume that  $ s_{i} $'s are independently and identically distributed.

### 3.1 Accuracy of estimating sentiment topics

The screening step estimates the sentiment dictionary by $S$. We first establish the consistency of screening by showing that $\hat{S} = S$ with an overwhelming probability. Let $g(\cdot)$ be as in Model (4) and $\overline{g} = n^{-1}\sum_{i=1}^{n}g(p_i)$. We define a quantity to capture the association between ordinal responses and document sentiments:

 $$ \theta:=\frac{\sum_{i=1}^{n}s_{i}\big(p_{i}-1/2\big)\big[g(p_{i})-\overline{{g}}]}{\sum_{i=1}^{n}s_{i}}. $$ 

This quantity is increasing with steepness of g and extremeness of training documents' tones.

##### Lemma 2 (Screening Statistics).

Consider Models (1)-(2) and (4), where Assumptions 1-2 are satisfied. Let  $ \epsilon_n $ be a sequence such that  $ \epsilon_n = o(1) $ and  $ \log(\epsilon_n^{-1}) = o\left(n \min\{1, \overline{s} \min_{j \in S} (O_{+,j} + O_{-,j}), \overline{n} \min_{j \in N} q_j\}\right) $, where  $ (\overline{s}, \overline{n}, q_j) $ are the same as in Assumption 2. With probability  $ 1 - \epsilon_n $, simultaneously for all  $ 1 \leq j \leq m $, the following statements are true: For  $ j \in S $,

 $$ \mid f_{j}-\hat{\pi}\mid\geq\theta\cdot\frac{2\tau\mid O_{+,j}-O_{-,j}\mid}{(1+\tau)(O_{+,j}+O_{-,j})}-\frac{C\sqrt{\log(m/\epsilon_{n})}}{\sqrt{n\min\{1,\overline{s}(O_{+,j}+O_{-,j})\}}}\cdot For\ j\in N, $$ 

 $$ |f_{j}-\hat{\pi}|\leq\frac{C\sqrt{\log(m/\epsilon_{n})}}{\sqrt{n\min\{1,\overline{n}q_{j}\}}} $$ 

We recall that  $ \hat{S} $ is obtained by thresholding  $ |f_j - \hat{\pi}| $. Theorem 2 justifies that  $ |f_j - \hat{\pi}| $ is relatively large for sentiment-charged words and relatively small for sentiment-neutral words. For any choice of  $ \epsilon_n = o(1) $, the statement of this lemma holds with probability approaching 1. In what follows, we assume  $ m \to \infty $ as  $ n \to \infty $ and fix  $ \epsilon_n = m^{-1} $; item (c) in Assumption 2 ensures that  $ \epsilon_n = m^{-1} $ satisfies the requirement of Lemma 2. This choice of  $ \epsilon_n $ greatly simplifies the expressions. The next theorem establishes the consistency of screening:

##### Theorem 1 (Consistency of Screening).

In Models (1)-(2) and (4), suppose Assumptions 1-2 hold, and additionally,

 $$ n\theta^{2}\min_{j\in S}\frac{(O_{+,j}-O_{-,j})^{2}}{(O_{+,j}+O_{-,j})^{2}}\geq\frac{\log^{2}(m)}{\min\left\{1,\overline{s}\min_{j\in S}(O_{+,j}+O_{-,j}),\overline{n}\min_{j\in N}q_{j}\right\}}.(16) $$ 

In the SESTM algorithm, set  $ \kappa = \log(m) $ and  $ \alpha_{\pm} = \frac{\sqrt{\log(m)\log(\log(m))}}{\sqrt{n\min\{1,\overline{s}\min_{j\in S}(O_{+,j}+O_{-,j}),\overline{n}\min_{j\in N}q_j\}}} $.

As  $ n,m\to\infty $,  $ \mathbb{P}(\hat{S}=S)=1-o(1) $.

##### Remark 1.

To ensure consistency for screening, the required number of training documents, $n$, relies on three factors: 1) the association between ordinal responses and document sentiments, denoted as $\theta$ and defined in (15); 2) the minimum among frequency-adjusted sentiments of all words in S, expressed as $\min_{j \in S} \frac{|O_{+,j} - O_{-,j}|}{O_{+,j} + O_{-,j}}$; 3) $\min\{1, \overline{s} \min_{j \in S} (O_{+,j} + O_{-,j}), \overline{n} \min_{j \in N} q_j\}$, where the last two terms inside the minimum account for the per-document count of individual words. In essence, a larger sample size $n$ is required if the association between ordinal responses and document sentiments is insufficient, if the sentiment-charged words do not significantly differ from the neutral ones, or if there is an inadequate number of words per document (i.e., the documents are on average too short).

The sentiment topic estimation step produces  $ \hat{O}_{\pm} $. Let  $ \hat{F} = \hat{\tau}\hat{O}_{+} + (1 - \hat{\tau})\hat{O}_{-} $ and  $ \hat{T} = (1 - \hat{\tau})(\hat{O}_{+} - \hat{O}_{-}) $, where  $ \hat{\tau} = n^{-1} \sum_{i=1}^{n} \hat{p}_{i} $. They are the respective estimates of the vector of frequency,  $ F $, and the vector of tone,  $ T $. We quantify the estimation errors of  $ F $ and  $ T $, which can be easily translated to the estimation errors for  $ O_{\pm} $.

Theorem 2 (Estimation Errors for Sentiment Topic Vectors).

Suppose Assumptions 1-2 and (16) are satisfied. Let  $ \hat{\rho} $ be defined as in Lemma 1. As  $ n,m \to \infty $, with probability approaching 1,  $ \|\hat{F} - F\| \leq C\sqrt{\frac{|S|\log(m)}{n\overline{s}}} $, and  $ \|\hat{T} - \frac{1 - \hat{\tau}}{1 - \tau}\hat{\rho}T\| \leq C\sqrt{\frac{|S|\log(m)}{n\overline{s}}} $.

Theorem 2 states that our method in fact estimates  $ (F, \hat{\rho}T) $ rather than  $ (F,T) $. This is the price we pay by not imposing an exact model on the distribution of  $ y_i $. Suppose, instead of Model (4), we specify a parametric distribution of  $ y_i $, then we could construct more accurate estimates of  $ p_i $ such that  $ n^{-1} \sum_{i=1}^{n} (\hat{p}_i - p_i)^2 \to 0 $, which in turn results in the consistency for the estimation of T. This is confirmed by the next corollary: $ ^6 $

Corollary 1.

Suppose conditions of Theorem 2 hold. Let  $ \hat{p}_i $ be an arbitrary estimate of  $ p_i $. We obtain  $ \hat{O}_\pm $ similarly as in (10), with  $ \hat{W} $ constructed from these  $ \hat{p}_i $'s. Suppose  $ |S|\log(m)/(n\overline{s}) \to 0 $ and  $ n^{-1}\sum_{i=1}^n (\hat{p}_i - \hat{\tau})^2 \geq a_1 $, for a constant  $ a_1 > 0 $. As  $ n, m \to \infty $, with probability approaching 1,  $ \max\{\|\hat{F} - F\|_{1}, \|\hat{T} - T\|_{1}\} \leq C\sqrt{\frac{|S|\log(m)}{n\overline{s}}} + C\sqrt{\frac{1}{n}\sum_{i=1}^n (\hat{p}_i - p_i)^2} $. Consequently, if  $ n^{-1}\sum_{i=1}^n (\hat{p}_i - p_i)^2 $ converges to 0 in probability, then  $ \|\hat{F} - F\|_{1} $ and  $ \|\hat{T} - T\|_{1} $ also diminish with probability approaching 1.

##### Remark 2.

We compare our results with those for unsupervised topic modeling (e.g., [1, 9, 12]). These methods recover  $ \hat{O}_{\pm} $ solely from the text data, without using the ordinal responses. While the unsupervised approach can achieve consistency in terms of  $ \|\hat{T}-T\| $, this is inconsequential within our context. As explained in Section 2.3, obtaining an accurate estimate of  $ \hat{\rho}T $ is sufficient for sentiment ranking. However, the unsupervised approach suffers from a slower rate of convergence. According to Corollary 3.1 in [9], their error rate is at best  $ \sqrt{\frac{|S|\log(m)}{n\overline{s}}}(1+\frac{|S|}{\overline{s}}) $, where  $ |S| $ represents the size of the sentiment dictionary, and  $ \overline{s} $ denotes the average per-document count of sentiment-charged words. In many real-world applications,  $ |S|\gg\overline{s} $ (for instance, in the application discussed in Section 5,  $ |S| $ is several hundreds while  $ \overline{s} $ is typically below 10), so the supervised approach we propose here is preferable.

### 3.2 Accuracy of scoring and ranking new documents

Given the word count vector  $ d \in \mathbb{R}_+ $ of a new document, we use (11) to obtain an estimate of its true sentiment score  $ p $. Recall that  $ \hat{\rho} $, as defined in Lemma 1, is related to the bias of  $ \hat{T} $ in Theorem 2. As the estimation error propagates, a similar bias occurs to the estimator of  $ p $. We thereby define the rescaled sentiment score  $ p^* \in [0,1] $ as:

 $$ p^{*}=\min\{1,\max\{0,\hat{\tau}+(p-\tau)/\hat{\rho}\}\},\qquad where\tau=n^{-1}\sum_{i=1}^{n}p_{i}.(17) $$ 

This definition slightly differs from the $p$ described in Section 2.3, as the $p$ mentioned here is a winsorization of $\tau + \hat{\rho}^{-1}(p - \tau)$ within the range of [0,1]. We utilize this winsorized version because the $\hat{p}$ in (11) is always constrained to take values in the interval [0,1]. When $p$ is bounded away from both 0 and 1, and $\hat{\rho}$ is not excessively small, the winsorization has no impact, and the two definitions coincide.

Theorem 3 (Sentiment Accuracy of a New Document).

In Models (1)-(2) and (4), suppose Assumptions 1-2 and (16) are satisfied. Suppose  $ \rho_{\min} \leq \hat{\rho} \leq \rho_{\max} $, for constants  $ 0 < \rho_{\min} < \rho_{\max} $, and  $ \rho_{\max} \mid T_j \mid \leq (1 - c_1)(1 - \tau)F_j $, for all  $ j \in S $, where  $ c_1 \in (0,1) $ is a constant. Let  $ d \in \mathbb{R}^m_+ $ contain the word counts in a new document with sentiment  $ p $, and let  $ s $ be the total count of sentiment-charged words in this document. Suppose  $ -\hat{\tau} + c_2 \leq \hat{\rho}^{-1} \mid p - \tau \mid \leq 1 - \hat{\tau} - c_2 $, where  $ c_2 > 0 $ is a properly small constant. Let  $ err_n = \frac{\sqrt{|S \mid \log(m)}}{\Theta \sqrt{nS}} + \frac{1}{\sqrt{s \Theta}} $, with  $ \Theta := \sum_{j \in S} \frac{(O_{+,j} - O_{-,j})^2}{O_{+,j} + O_{-,j}} $. Suppose  $ err_n \to 0 $. Let  $ \hat{p} $ be the penalized MLE in (11). As  $ n \to \infty $, for each fixed  $ \epsilon \in (0,1) $, there exists a constant  $ C > 0 $, such that, with probability  $ 1 - \epsilon $,

 $$ |\hat{p}-p^{*}|\leq C\min\left\{1,\frac{\Theta}{\lambda}\right\}\times e r r_{n}+C\min\left\{1,\frac{\lambda}{\Theta}\right\}\times|p-\tau|.(18) $$ 

Furthermore, when  $ \lambda = \Theta \mid p - \tau \mid^{-1} err_n $, (18) becomes  $ \mid \hat{p} - p^* \mid \leq C \min\{err_n, \mid p - \tau \mid\} \leq Cerr_n $.

The term  $ err_n $ has two components,  $ \frac{\sqrt{S \mid \log(m)}}{\Theta \sqrt{n s}} $ and  $ \frac{1}{\sqrt{s \Theta}} $, corresponding to the respective errors from training and testing. Since  $ n $ is large, it is the second term that will dominate in finite sample. The tuning parameter  $ \lambda $ reflects a bias-variance trade-off. In (18), the first term  $ \min\left\{1, \frac{\Theta}{\lambda}\right\} \times err_n $ is related to the “variance”, which decreases with  $ \lambda $; the second term  $ \min\left\{1, \frac{\lambda}{\Theta}\right\} \times \left|p - \tau\right| $ is the “bias”, which increases with  $ \lambda $. In practice, it is often the case that most documents have a neutral tone, so that the bias is negligible relative to the variance. Besides, text data are very noisy, so imposing a large penalty in MLE significantly reduces the variance. Our estimator shares the same spirit as the James-Stein estimator [8].

Finally, we study the ranking performance of SESTM.

Theorem 4 (Consistency of Rank Correlation).

Under conditions of Theorem 3, suppose we are given $L$ new documents whose $p_1, p_2, \ldots, p_L$ are $i.i.d.$ generated from a distribution on $[\tau + \rho_{\min}(-\hat{\tau} + c_2), \tau + \rho_{\min}(1 - \hat{\tau} - c_2)]$ with a continuous probability density. Let $s_i$ be the total count of sentiment-charged words in a new document $i$. Suppose $\min\{s_1, s_2, \ldots, s_L\} \geq c_3 s$, where $s \Theta / \sqrt{\log(L)} \to \infty$ and $c_3 > 0$ is a constant. We apply (11) with $\lambda \asymp \Theta err_n$ to estimate sentiments of new documents. Let $SR(\hat{p}, p)$ be the Spearman's rank correlation between $\{\hat{p}_i\}_{i=1}^L$ and $\{p_i\}_{i=1}^L$. As $n, m, L \to \infty$, $\mathbb{E}[SR(\hat{p}, p)] \to 1$.

##### Remark 3.

Besides Spearman’s rank correlation, there exist other performance metrics for ranking, including mean average precision, mean reciprocal rank, discounted cumulative gain (DCG), and precision/recall of the top-k ranks. They can be studied in a similar manner by applying Theorem 3 and assuming regularity conditions on the true sentiment scores of test documents. In fact, when ranks are obtained by ordering estimated “scores,” the analysis of any performance metric essentially involves quantifying the differences between these estimated scores and a monotone transformation of the true scores (e.g., see [3, 5]). Theorem 3 provides the necessary theoretical foundation for studying any ranking performance metric.

##### Remark 4.

Theorem 4 assumes that the sentiment scores of new documents belong to  $ [\tau + \rho_{\min}(-\hat{\tau} + c_2), \tau + \rho_{\min}(1-\hat{\tau} - c_2)] $. However, this assumption can be relaxed by modifying Equation (11) to remove the constraint  $ p \in [0,1] $ during optimization. While the estimates  $ \{\hat{p}_i\}_{i=1}^L $ may fall outside  $ [0,1] $, they can still be effectively used to rank the documents.

## 4 Simulations

In this section, we provide Monte Carlo evidence to illustrate the finite-sample performance of our proposed algorithm. In our simulations, the counts of sentiment-charged and sentiment-neutral words in each article are generated from Model (1)-(2), where  $ p_i \sim \text{Unif}(0,1) $,

$s_i \sim \text{Unif}(0, 2\overline{s}), n_i \sim \text{Unif}(0, 2\overline{n}),$ and for $j=1,2,\ldots,|S|$, $O_{+,j} = \frac{2}{|S|} \left(1 - \frac{j}{|S|} \right)^2 + \frac{2}{3|S|} \times 1_{\left\{j < \frac{|S|}{2}\right\}}$

$O_{-,j} = \frac{2}{|S|} \left(\frac{j}{|S|} \right)^2 + \frac{2}{3|S|} \times 1_{\left\{j \geq \frac{|S|}{2}\right\}}$, and $\Omega_j$ is drawn from $\frac{1}{m-|S|}$ Unif(0,2), for $j=|S|+1,\ldots,m$, then renormalized such that $\sum \Omega_j = 1$. As a result, the first $|S|/2$ words are positive, the next $|S|/2$ words are negative, and the remaining $(m-|S|)$ words are neutral with frequencies randomly drawn from a uniform distribution. As such, the difference between $O_{+,j}$ and $O_{-,j}$ reaches the minimum at $j=|S|/2$. This means among all words within the set $S$, those with $j$ around $|S|/2$ are close to neutral. Next, the sign of the ordinal response is such that $\mathbb{P}(y_i > 0) = p_i$, and its magnitude $|y_i|$ follows a folded Student $t$-distribution with the degree of freedom parameter set at 4. The standard deviation of the $t$-distribution has negligible effects on our simulations, since only the ranks of returns matter for our results. We fix the number of Monte Carlo repetitions at $M_c = 200$ and the number of testing articles at $L = 1,000$. In the benchmark case, we set $|S| = 200$, $m = 4,000$, $n = 40,000$, $\overline{s} = 15$, and $\overline{n} = 200$. We vary these choices to examine their effect on the performance of our procedure.

Experiment 1: Finite-sample performance of SESTM.

We first evaluate the screening step. Although tuning threshold parameters give better results, for convenience we choose the top  $ |S| $ words in terms of  $ |f_j - 0.5|1_{\{k_j > \kappa\}} $, where  $ \kappa $ is set at the 10% quantile of all  $ k_j $s. Figure 1 reports the frequency of each word selected in the screening step across all Monte Carlo repetitions. Remarkably, the probability of selecting any word outside  $ S $ is approximately 0.93% across all repetitions. As expected, the words within set  $ S $ that are occasionally missed are those associated with  $ j $ values around  $ |S|/2 $. This observation is not surprising since such words exhibit relatively weak sentiment strength, rendering them nearly neutral in nature.

Next, Figure 2 delineates the precision of our estimation process, taking into consideration potential inaccuracies arising from the screening step. The true values of $T$ and $F$ are represented in black. In this benchmark simulation setting, the scaling constant $\hat{\rho}$ approximates 0.5. The graph clearly shows that the estimators $\hat{F}$ and $\hat{T}$ are centered around their respective targets $F$ and $\hat{\rho}T$ across all words, consistent with our theoretical prediction. Further analysis involves varying the number of training articles $(n)$, the size of the vocabulary $(m)$, the average of the sentiment words per article $(\bar{s})$, and the size of the dictionary of the sentiment words $(|S|)$ to scrutinize their influence on the estimates of $F$ and $\hat{\rho}T$, as depicted in Figure 3. The simulation results align with the theoretical implications of Theorem 2. Specifically, the estimation error diminishes with an increase in $n$ or $\bar{s}$, and a decrease in $|S|$ or $m$.

Next, we evaluate the accuracy of the sentiment ranking step, taking into account any errors propagated from the preceding steps. Notably, data from the test sample are never used in the two previous steps. Figure 4 reports the boxplots of the Spearman’s rank correlation coefficients between the predicted  $ \hat{p} $ and the true p across 1,000 documents within the test sample in a variety of cases. The rank correlation appears to be most sensitive concerning  $ \bar{s} $. Elevating it from 5 to 25 results in an improvement in rank correlation from an average of 0.8 to over 0.9, attributable to the larger number of counts from words in S. A rise in n seems to induce a moderately small enhancement, while increasing m and  $ |S| $ slightly degrades the results. Overall, these observations are congruent with our intuition and the error bounds for estimating F and T, although we do not have any theoretical error bound for  $ (1-SR(\hat{p}, p)) $.

#### Experiment 2: Comparison with alternative methods.

Finally, we undertake a comparative evaluation of our estimator against alternate methodologies, focusing primarily on three categories: the Naive Bayes, MNIR, and Dictionary methods. The Naive Bayes method is a supervised classification technique that uses word count as input features for sentiment label classification. However, it relies on an assumption that the word count remains independent given the sentiment score, which clearly contradicts the data generating process in our study. Additionally, Naive Bayes focuses solely on classification, disregarding any information pertaining to the (ordered) values of ordinary responses. Similarly, MNIR is also a supervised classification approach, suffering from the same issues due to model misspecification caused by inconsistent assumptions with our data generating process. On the other hand, the Dictionary method involves pre-selecting a sentiment dictionary and determining

the sentiment of each test document by simply computing the difference between the respective total counts of positive and negative words. Despite being simple and intuitive, this estimator lacks justifiable asymptotic properties. To further scrutinize the impact of the dictionary, we randomly select a fixed quantity of words, say, 80%, 90%, and 100%, from the true set of sentiment words, and supplement them with remaining words from the sentiment-neutral list. Table 1 delineates the summary statistics of Spearman's correlation within the context of the benchmark scenario. Our approach, SESTM, as demonstrated by the results, produces a stronger correlation and exhibits smaller variation compared to alternative methods. When equipped with an accurate dictionary, the Dictionary method achieves second place in the ranking, followed by MNIR. Nevertheless, the effectiveness of the Dictionary method rapidly diminishes as the dictionary quality declines. The Naive Bayes approach begins to outperform the Dictionary method once the accuracy of the dictionary drops to 80%.

## 5 Empirical Analysis of the Dow Jones Newswire

We apply our text-mining framework to extract sentiment information from the Dow Jones Newswire, aiming to utilize sentiment analysis in constructing an investment portfolio. Our null hypothesis of market efficiency predicts that the expected return is dominated by unpredictable news, as this news is rapidly (in its starkest form, immediately) incorporated in prices. The maintained alternative hypothesis of our research is that information in news text is not fully absorbed by market prices instantaneously, for reasons such as limits-to-arbitrage and rationally limited attention. As a result, information contained in news text is predictive of future asset price paths. While this alternative hypothesis is by now uncontroversial, it is hard to overstate its importance, as we have much to learn about the mechanisms through which information enters prices and the frictions that impede these mechanisms.

Our text data set is the Dow Jones Newswires Machine Text Feed and Archive database. It contains real-time news feeds from January 1, 1989 to April 30, 2020, amounting to 25,743,474 unique articles (after combining “chained” articles). Approximately 62.2% news articles are tagged with one or more firm identifiers. We restrict our sample to articles tagged with only one firm, reducing the dataset to 11,988,392 articles. Table E.1 in the appendix outlines the step-by-step details of our article filtering process. The appendix also provides a thorough description of the data cleaning procedure, which converts each article into its bag-of-words representation. We match each article with tagged firm’s market capitalization and adjusted daily close-to-close returns from CRSP. To ensure a strong association between text sentiment and returns in our training sample, we label the sentiment of each article published on day t (between 4pm of day t−1 and 4pm of day t) based on the sign of its tagged firm’s three-day return from t−1 to t+1 (from market close on day t−2 to close on day t+1).

#### Return prediction and portfolio construction.

We train the model using rolling window estimation. The rolling window consists of a 15-year interval, the first 10 years for training and the last 5 years for validation/tuning. We then use the subsequent 1-year window for out-of-sample testing. At the end of the testing year, we roll the entire analysis forward by a year and re-train. We iterate this procedure until we exhaust the full sample, which amounts to estimating and validating the model 17 times.

In each training sample, we estimate a collection of SESTM models corresponding to a grid of tuning parameters. There are four tuning parameters in total: $(\alpha_{+}, \alpha_{-}, \kappa, \lambda)$. The first two, $\alpha_{+}$ and $\alpha_{-}$, determine the size of the sentiment dictionary for positive and negative words, respectively, while $\kappa$ sets the threshold for excluding overly rare words. In practice, it is more convenient (and equivalent) to adjust the number of positive and negative words directly, rather than tuning $\alpha_{+}$ and $\alpha_{-}$. To reduce computational burden, we select either 50, 100, or 200 words, as the results are not sensitive to this choice. The parameter $\kappa$ is set to be proportional to the logarithm of the total number of words for articles in the training sample. For the constant term, we explore a grid of values from 50 to 1,000, in increments of 50. Finally, $\lambda$ is fixed at 10 throughout the analysis, as it does not affect the ranking of sentiment scores but ensures all scores fall within the 0 to 1 range.

For the validation sample, we use all the estimated models to score each news article and select the constellation of tuning parameter values that provides the most desirable model performance. One sensible criterion is the rank correlation with return-based sentiment scores in the validation sample. Alternatively, since the sentiment scores will ultimately be used for portfolio construction, we use the Sharpe ratio of the resulting portfolios as the selection criterion for tuning parameters. The exact portfolio formation procedure follows the one described in the out-of-sample analysis, which we will outline below.

In the out-of-sample test period, we estimate the sentiment scores of articles using the optimally tuned model determined from the validation sample. To evaluate out-of-sample predictive performance in economic terms, we design a trading strategy that leverages sentiment estimates for prediction. Our trading strategy is very simple (the news timeline and our trading activities are summarized in Figure E.3 of the appendix). It is a zero-net-investment portfolio that each day buys 50 stocks with the most positive sentiment scores and shorts 50 stocks with the most negative sentiment scores. Trading only 100 stocks per day is a reasonable choice in light of the summary statistics of the data, despite it being unfortunately small. On average, we only have 936.5 firms with at least one piece of news on each trading day, among which 181.7 contain sentiment-charged words, for which our algorithm can output non-neutral sentiment scores. In the early part of the sample, there are a handful of days for which fewer than 50 firms have non-neutral scores, in which case we have to trade fewer than 100 stocks but otherwise maintain the zero-cost nature of the portfolio. That said, we also provide results for portfolios with (up to) 200 stocks for robustness check in the appendix.

We consider both equal-weighted and value-weighted schemes when forming the long and short sides of the strategy. Equal weighting is a simple and robust way of assessing predictive power of sentiment over the firm size spectrum, and is anecdotally closer to how hedge funds use news text for portfolio construction. Value weighting heavily overweights large stocks, which may be justifiable for economic reasons (assigning more weight to more productive firms) and for practical trade implementation reasons (such as limiting transaction costs). Figure 5 reports the cumulative one-day trading strategy returns (calculated from open-to-open) based on out-of-sample SESTM sentiment forecasts. We report the long (denoted “L”) and short (“S”) sides separately, as well as the overall long-short (“L-S”) strategy performance. We also contrast

performance of equal-weighted (“EW”) and value-weighted (“VW”) versions of the strategy. Table 2 reports the corresponding performance statistics of these portfolios.

Three basic facts emerge from the one-day forecast results in Figure 5 and Table 2. First, equal-weighted portfolios substantially outperform their value-weighted counterparts. The long-short strategy with equal weights earns an annualized Sharpe ratio of 5.21, versus 1.56 in the value-weighted case. This indicates that news article sentiment is a stronger predictor of future returns to small stocks, all else equal. There are several potential economic explanations for this, including the facts that i) small stocks receive less investor attention and thus respond more slowly to news, ii) the underlying fundamentals of small stocks are more uncertain and opaque and thus it requires more effort to process news into actionable price assessments, and iii) small stocks are less liquid and thereby require a longer time for trading to occur to incorporate information into prices. Second, both the long and short sides are significantly profitable. The long side slightly outperforms the short side, with a Sharpe ratio of 2.15 versus 1.52 (in the equal-weighted case). This is due in part to the fact that the long side naturally earns the market equity risk premium while the short side pays it. A potential explanation is that investors face short sales constraints so that the negative news cannot be fully expressed in prices over short horizons. Third, SESTM sentiment trading strategies have little exposure to standard aggregate risk factors. The individual long and short legs of the trade have at most a 40% daily  $ R^{2} $ when regressed on Fama-French factors, while the long-short spread portfolio  $ R^{2} $ is at most 1.8%. In all cases, the average return of the strategy is almost entirely alpha. Note that, by construction, the daily turnover of the portfolio is large. If we completely liquidated the portfolio at the end of each day, we would have a turnover of 100% per day. Actual turnover is slightly lower, on the order of 96% for equal-weighted implementation and 94% for value-weighted, indicating a small amount of persistence in positions. Figure 5 shows that the long-short strategy avoids major drawdowns, and indeed appreciates during the financial crisis while SPY sells off.

#### Most impactful words:

Figure 6 reports the list of sentiment-charged words estimated from our model. These are the words that most strongly correlate with realized returns and thus surpass the correlation screening threshold. Because we re-estimate the model in each of our 17 training samples, the sentiment word lists can change throughout our analysis. The font size of a word in the cloud is proportional to the word's average sentiment tone  $ (O_{+} - O_{-}) $ over all 17 training samples. Table E.5 in Appendix E.7 provides additional details on selected words, reporting the top 50 positive and negative sentiment words throughout our training samples. It also shows if these words overlap with LM and Harvard-IV dictionaries.

The estimated wordlists are remarkably stable over time. Of the top 50 positive sentiment words over all periods, 24 are selected into the positively charged set in at least 12 of the 17 training samples. For the 50 most negative sentiment words, 23 are selected in at least 14 out of 17 samples. The following 14 negative words are selected in every training sample: downgrade, hurt, fell, warn, slowdown, lower, resign, soft, delay, weak, slow, cut, drop, decrease, and the following nine words are selected into the positive list in 15 or more training samples: repurchase, declare, upgrade, beat, boost, jump, exceed, raise, strong. There are interesting distinctions vis-a-vis extant sentiment dictionaries. For example, in comparison to our estimated

nine most impactful positive words listed above, only two (boost, strong) appear in the LM positive dictionary, and only two (upgrade, boost) appear in Harvard-IV. Likewise, five of our 14 most impactful negative words (fell, lower, soft, drop, decrease) do not appear in the LM negative dictionary and eight are absent from Harvard-IV. Thus, in addition to the fact that our word lists are accompanied by term-specific sentiment weights (contrasting with the implicit equal weights in extant dictionaries), many words that we find to be most important for understanding realized returns are entirely omitted from pre-existing dictionaries.

#### Comparison versus dictionary methods, RavenPack, and BERT:

We compare SESTM to alternative sentiment scoring methods in terms of return prediction accuracy. The first competitor is dictionary-based sentiment scoring. We construct the LM sentiment score of an article by aggregating counts of words listed in their positive sentiment dictionary (weighted by tf-idf, as recommended by [10]) and subtracting off weighted counts of words in their negative dictionary. As with SESTM, we average scores from multiple articles for the same firm on the same day. This produces a stock-day signal,  $ \hat{p}_{i}^{LM} $, which we use to construct trading strategies in the same manner as the SESTM-based signal,  $ \hat{p}_{i}^{SESTM} $, in preceding analyses.

The second competitor is the news sentiment scores from RavenPack News Analytics 4 (RPNA4) (https://www.ravenpack.com/about/). RavenPack is a leading provider of big data analytics for financial services, with clients including many of the world's most prominent hedge funds, banks, and asset managers. We use data from the RPNA4 DJ Edition Equities, released in September 2014, which constructs company-level sentiment scores based on the same Dow Jones sources we use to build SESTM (Dow Jones Newswires, Wall Street Journal, Barron's and MarketWatch). Thus, the underlying news collection available to us is presumably identical to that used by RavenPack. However, the observation count we see in RavenPack is larger than the number of observations we can construct from the underlying Dow Jones news (we discuss this point, along with additional details of the RavenPack data, in Appendix E.6). Following the same procedure, we construct RavenPack daily stock-level sentiment scores ( $ \hat{p}_{i}^{RP} $) by averaging all article sentiment scores pertaining to a given firm on a given day (we use RavenPack's flagship measure, CSS). To avoid any forward-looking bias, we restrict the use of RavenPack sentiment scores in our portfolio analysis to the post-September 2014 period. This ensures that the scores were produced after the release of RPNA4, rather than reflecting earlier data that may have been used to train the model, which could contaminate backfilled sentiment with information not available in real time.

The third alternative we consider is the BERT model, one of the first and most widely used large language models, developed by [4]. For each article, we generate article-level embeddings using the first 512 tokens. While the 512-token limit constrains the length of the text that the BERT model can process, most news articles provide sufficient information within these first 512 tokens. In practice, including more tokens has not been shown to improve performance. These embeddings act as sufficient statistics, effectively capturing the context of the text. We then use these embeddings to train a logistic regression model with the same labels used in the SESTM approach. Given the high dimensionality of the BERT embeddings 1,024 dimensions we apply a

ridge penalty to mitigate overfitting. $ ^{10} $ The ridge parameter is selected using the same training and validation design as in the previous models. The resulting model outputs sentiment scores  $ \hat{p}_{i}^{BERT} $.

We build trading strategies using each of the sentiment scores,  $ \hat{p}_{i}^{SESTM} $,  $ \hat{p}_{i}^{LM} $,  $ \hat{p}_{i}^{RP} $, and  $ \hat{p}_{i}^{BERT} $. These strategies follow the same approach as before, where we buy the 50 most positive and short the 50 most negative sentiments. We also evaluate both equal-weighted and value-weighted strategies. Figure 7 focuses on a one-day trading strategy and separately analyzes equal- and value-weighted portfolios. It reports out-of-sample cumulative daily returns to compare average performance and drawdowns across SESTM, LM, and BERT. Table 3 complements this figure by reporting a broader set of performance statistics, including annualized Sharpe ratios, daily turnover, and average returns. Unlike the figure, the table also includes RP in the comparison and restricts the sample to the post-September 2014 period.

The SESTM strategy exhibits clear dominance under equal-weighting, outperforming alternatives in both average returns and Sharpe ratio, while maintaining comparable turnover. In equal-weighted terms, SESTM achieves an annualized Sharpe ratio of 4.85, compared to 3.14 for LM, 4.20 for RavenPack, and 1.89 for BERT. Under value-weighting, however, the performance gap narrows and even reverses: SESTM's Sharpe ratio drops to 1.43, trailing both RavenPack (1.77) and LM (1.71), though remaining above BERT (0.56).

To more carefully assess the differences in performance across methods, Table 3 also reports a series of portfolio spanning tests. For each trading strategy, we regress its returns on the returns of each of the competing strategies, while also controlling for daily returns to the five Fama-French factors plus the UMD momentum factor (denoted FF6 in the table). We evaluate  $ R^2 $ and regression intercept ( $ \alpha $). If a trading strategy has a significant  $ \alpha $ after controlling for an alternative, it indicates that the underlying sentiment measure isolates predictive information not fully subsumed by the alternative. Likewise, the  $ R^2 $ measures the extent to which trading strategies duplicate each other. An interesting result of the spanning tests is the overall low correlation among strategies and with Fama-French factors. The highest  $ R^2 $ is 8.30% for SESTM regressed on FF6 and LM. The SESTM  $ \alpha $’s are in each case almost as large as its raw return. At most, 7.10% of the SESTM strategy performance is explained by the controls (i.e., an equal-weighted  $ \alpha $ of 29 basis points versus the raw average return of 37 basis points). We also see significant positive alphas for the alternative strategies after controlling for SESTM, indicating not only that they achieve significant positive returns, but also that a component of those excess returns are uncorrelated with SESTM and FF6. In short, SESTM, RavenPack, LM, and BERT capture different varieties of information content in news.

## 6 Conclusion

We introduce a new framework for extracting sentiment information from text that offers several key advantages over existing methods. Unlike pre-defined sentiment dictionaries, our method learns a domain-specific dictionary directly from the data, allowing it to adapt to various domains and capture nuanced sentiment expressions. It is also highly versatile, handling both discrete and continuous ordinal responses, unlike many existing methods limited to discrete data.

Furthermore, our approach operates as a “white box” model, offering clear interpretability of all parameters while being computationally efficient and requiring only basic statistical tools.

Compared to DNN approaches, our framework is easier to train, interpret, and diagnose. Additionally, it is backed by theoretical guarantees that provide valuable insights into how sentiment estimation and ranking accuracy depend on factors such as the number of documents and the size of the sentiment dictionary, a feature lacking in many alternative methods.

While our current model relies solely on word counts and functions as a uni-gram topic model, there are important avenues for future research that could enhance its explanatory power. Extending the model to incorporate multi-gram topic models or word-embedding techniques would allow it to capture additional information from word order and context. Moreover, sentiment analysis likely involves multiple dimensions that drive market behavior in distinct ways. For example, distinguishing between long-term and short-term sentiment, or differentiating between macroeconomic and company-specific sentiment, could provide deeper insights into market reactions. These extensions would move beyond a one-dimensional sentiment model and offer a richer understanding of the relationship between sentiment and financial outcomes.

Additionally, we observed in Section 5, that the most influential sentiment words varied across different time windows, suggesting the potential benefits of allowing sentiment topic vectors to vary over time. Re-estimating sentiment dictionaries periodically or modeling sentiment topics as smooth functions of time—potentially using change-point detection and kernel smoothing techniques—could improve the model's ability to capture these temporal dynamics. Document-level covariates, such as author attributes, could also be incorporated to further refine how sentiment is expressed in the text.

Finally, while we demonstrate the practical application of our methodology in enhancing sentiment-guided portfolio construction and compare it favorably with other sentiment analysis methods, the potential extensions discussed provide exciting directions for future research. These refinements could lead to more nuanced and accurate insights, contributing to a better understanding of how sentiment influences price formation in financial markets.

7 Conflict of Interest Statement

The authors report there are no competing interests to declare.

## References

[1] Bing, X., F. Bunea, S. Strimas-Mackey, and M. Wegkamp (2022). Likelihood estimation of sparse topic distributions in topic models and its applications to wasserstein document distance calculations. The Annals of Statistics 50(6), 3307–3333.

[2] Blei, D. M., A. Y. Ng, and M. I. Jordan (2003). Latent Dirichlet Allocation. Journal of Machine Learning Research 3(Jan), 993–1022.

[3] Chen, Y., J. Fan, C. Ma, and K. Wang (2019). Spectral method and regularized MLE are both optimal for top-k ranking. Annals of Statistics 47(4), 2204.

[4] Devlin, J., M.-W. Chang, K. Lee, and K. Toutanova (2018). Bert: Pre-training of deep bidirectional transformers for language understanding. arXiv preprint arXiv:1810.04805.

[5] Fan, J., Z. Lou, W. Wang, and M. Yu (2024). Ranking inferences based on the top choice of multiway comparisons. Journal of the American Statistical Association, 1–14.

[6] Frank, E. and M. Hall (2001). A simple approach to ordinal classification. In Machine Learning: ECML 2001: 12th European Conference on Machine Learning Freiburg, Germany, September 5–7, 2001 Proceedings 12, pp. 145–156. Springer.

[7] Hofmann, T. (1999). Probabilistic latent semantic analysis. In Proceedings of the Fifteenth conference on Uncertainty in artificial intelligence, pp. 289–296. Morgan Kaufmann Publishers Inc.

[8] James, W. and C. Stein (1961). Estimation with quadratic loss. In Proceedings of the fourth Berkeley symposium on mathematical statistics and probability, Volume 1, pp. 361–379.

[9] Ke, Z. T. and M. Wang (2024). Using SVD for topic modeling. Journal of the American Statistical Association 119(545), 434–449.

[10] Loughran, T. and B. McDonald (2011). When is a liability not a liability? textual analysis, dictionaries, and 10-ks. The Journal of Finance 66(1), 35–65.

[11] Radford, A., K. Narasimhan, T. Salimans, I. Sutskever, et al. (2018). Improving language understanding by generative pre-training.

[12] Recht, B., C. Re, J. Tropp, and V. Bittorf (2012). Factoring nonnegative matrices with linear programs. Advances in neural information processing systems 25.

[13] Stine, R. A. (2019). Sentiment analysis. Annual review of Statistics and Its Application 6, 287–308.

[14] Taddy, M. (2013). Multinomial inverse regression for text analysis. Journal of the American Statistical Association 108(503), 755–770.

[15] Wang, J., X. Shen, Y. Sun, and A. Qu (2016). Classification with unstructured predictors and an application to sentiment analysis. Journal of the American Statistical Association 111(515), 1242–1253.

[16] Yan, X. and J. Bien (2021). Rare feature selection in high dimensions. Journal of the American Statistical Association 116(534), 887–900.

##### Notes

 $ ^{1} $ Using the financial application in Section 5 as an example,  $ \Omega_{i} $ may include industry-specific information. Our framework permits the sentiment score  $ p_{i} $ to depend on  $ \Omega_{i} $ in a flexible manner, allowing the frequencies of sentiment words to vary across different industries. As long as industry topics are diversified in the news corpus, our screening step in Section 2.2 will be able to separate words in S from those in N.

 $ ^{2} $ This is related to model identification. Readers are referred to Appendix for a detailed discussion.

 $ ^{3} $ For example, let’s consider  $ y_i $ as the star rating associated with a customer review. We denote  $ \epsilon_k $ as the fraction of k-star reviews (where we set  $ \epsilon_0 = 0 $ by default). For each  $ 1 \leq k \leq 5 $, we require that the normalized ranks of all k-star reviews are within the interval  $ [\sum_{j=0}^{k-1} \epsilon_j, \sum_{j=0}^{k} \epsilon_j] $ (e.g., we can either set all these  $ \hat{p}_i $ to be equal to the midpoint of this interval or let them uniformly distributed in this interval; see Section of the supplementary material for a detailed discussion). These normalized ranks are invariant under any re-coding of  $ y $ (e.g., if  $ y \in \{1, 2, 3, 4, 5\} $ is re-coded to  $ y \in \{-1, -2, 0, 1, 2\} $, the  $ \hat{p}_i $ values remain the same).

 $ ^{4} $ For example, when  $ \tau = \frac{1}{2} $ and  $ \hat{p}_i $'s are uniformly distributed in  $ [0,1] $,  $ \hat{\rho} = \frac{12}{n} \sum_{i=1}^{n} (p_i - \frac{1}{2}) (\hat{p}_i - \frac{1}{2}) + O(n^{-1}) $.

 $ ^{5} $ To see this, consider maximizing  $ \sum_{j} \hat{h}_{j} \log(x_{j}) $, subject to  $ x_{j} \geq 0 $ and  $ \sum_{j} x_{j} = 1 $. The solution is  $ x_{j} = \hat{h}_{j} $.

 $ ^{6} $ This corollary applies to any estimate  $ \hat{p}_{i} $. For the particular  $ \hat{p}_{i} $ in (9), due to its special structure, the rate of convergence for  $ \|\hat{F}-F\|_{1} $ is faster without the additional term on the right-hand side; see Theorem 2.

not introduce forward-looking bias, as this labeling procedure applies only to articles in the training sample. Furthermore, since sentiment-driven news events may either cause or be caused by large returns, using a three-day window around the news event may provide a more accurate label for the sentiment in the news text.

 $ ^{8} $ In total, we tune 60 sets of tuning parameter values, constrained by the available computational resources. In general, increasing the number of tuning parameter sets explored would likely improve model performance. Therefore, the results presented should be considered as conservative estimates, as greater computational resources would allow for a more extensive tuning process and potentially stronger outcomes.

 $ ^{9} $ In the case a stock is mentioned in multiple news articles on the same day, we use the average sentiment score over the coincident articles.

 $ ^{10} $ Due to space constraints, we only report results from the BERT-large model, which has 340 million parameters. The BERT-base model, with 110 million parameters and 768-dimensional embeddings, performs worse empirically.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e37f82f6-3af4-4fe9-b419-7dc85fc55e0a/markdown_4/imgs/img_in_chart_box_169_168_1027_613.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A26Z%2F-1%2F%2F8300f39492d7116f5babd35c490d29c24664bb83321cf48c2305ad6a8ad6e9f3" alt="Image" width="70%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 1: The frequency of each sentiment-charged word selected into  $ \hat{S} $ in Monte Carlo simulations. The red bars correspond to those words with frequencies less than 100%.</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e37f82f6-3af4-4fe9-b419-7dc85fc55e0a/markdown_4/imgs/img_in_chart_box_173_754_926_1210.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A26Z%2F-1%2F%2F55a4d56341e9f2e1affb707007fce956919bfa00e68adb5ee537ad4685338f51" alt="Image" width="61%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 2: Comparison of the averages of  $ \hat{F} $ (blue, solid) and  $ \hat{T} $ (red, solid) across Monte Carlo repetitions with  $ F $ (black, dotted),  $ T $ (thin, black, dashed), and  $ \hat{\rho}T $ (thick, black, dashed), respectively, using the benchmark parameters. The blue and red dotted lines plot the 2.5% and 97.5% quantiles of the Monte Carlo estimates. For each word in  $ S $, the averages and percentiles are calculated based on those Monte Carlo samples where this word appears in  $ \hat{S} $.</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//0a292c52-535d-47a8-9146-6ab0c9e433c9/markdown_0/imgs/img_in_chart_box_161_151_1053_607.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A24Z%2F-1%2F%2Ff56602f419ff041155ee3ea922e06c31b7dce3afa375eaa8e341fa0a4611fc96" alt="Image" width="72%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 3: Comparison of $F$ and $T$ estimates across different scenarios. The figure shows the boxplots of $\|\hat{F}-F\|_{1}$ and $\|\hat{T}-\hat{\rho}T\|_{1}$ across Monte Carlo repetitions for different values of $(m,n,|S|,\overline{s})$.</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//0a292c52-535d-47a8-9146-6ab0c9e433c9/markdown_0/imgs/img_in_chart_box_157_760_1060_999.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A24Z%2F-1%2F%2Fe166c24a6cea9c7d2a254303755ff529281ad24ed903548fad61489d90336d4a" alt="Image" width="73%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 4: Comparison of ranking performance across different scenarios. The figure shows the boxplots of the Spearman's correlation across Monte Carlo repetitions for various values of  $ (m, n, |S|, \overline{s}) $.</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//0a292c52-535d-47a8-9146-6ab0c9e433c9/markdown_1/imgs/img_in_chart_box_172_161_1028_597.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A25Z%2F-1%2F%2Ff3c73adaa0fb66f910b297e6e82f2ad24b536d6c47cebcd9162c9aefc2d6a9dc" alt="Image" width="69%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 5: One-day-ahead performance comparison of SESTM (the out-of-sample cumulative log returns). The black, blue, and red colors represent the long-short (L-S), long (L), and short (S) portfolios, respectively. The solid and dashed lines represent equal-weighted (EW) and value-weighted (VW) portfolios, respectively. The yellow solid line is the S&P 500 return (SPY).</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//0a292c52-535d-47a8-9146-6ab0c9e433c9/markdown_1/imgs/img_in_seal_box_172_781_604_1133.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A25Z%2F-1%2F%2Fedbc15af7466c3f3aae5080318312c00558ba8538af0cad3a6332611889caf34" alt="Image" width="35%" />  <div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//0a292c52-535d-47a8-9146-6ab0c9e433c9/markdown_1/imgs/img_in_seal_box_172_781_604_1133.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A25Z%2F-1%2F%2Fedbc15af7466c3f3aae5080318312c00558ba8538af0cad3a6332611889caf34" alt="Image" width="35%" />  preliminary drop fell parentheses weak delay hurt face miss bad reduce decrease soft downgrade compliance resigns lowdown warn slow negative goodwill unadjusted lower  </div>   </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//0a292c52-535d-47a8-9146-6ab0c9e433c9/markdown_1/imgs/img_in_image_box_165_775_1051_1140.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A25Z%2F-1%2F%2F6adaa35c4d3d043e27732575f1dfbce2a520bff82581e8cf1fe7163a40112097" alt="Image" width="72%" /></div>


excellent

beat split

raise solid board

repurchase

definitive

strong declare

exceed boost

attract upgrade

double

complement

square

momentum

<div style="text-align: center;"><div style="text-align: center;">Figure 6: Sentiment-charged words. This figure reports the list of words in the sentiment-charged set  $ \hat{S} $. Font size of a word is proportional to its average sentiment tone over all 17 training samples.</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//0a292c52-535d-47a8-9146-6ab0c9e433c9/markdown_2/imgs/img_in_chart_box_198_173_1046_524.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A26Z%2F-1%2F%2F58c0c3654783af114a68bc853e5b8986dce582ce2365d3dde1217a5231fa75eb" alt="Image" width="69%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 7: SESTM versus LM, and BERT. This figure compares the daily cumulative returns of long-short portfolios constructed from SESTM, LM, and BERT sentiment scores, separated into equal-weighted (EW, solid lines) and value-weighted (VW, dashed lines) portfolios, respectively. The yellow solid line is the S&P 500 return (SPY).</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Table 1: Comparison of Spearman’s correlation. This table presents the mean and standard deviation of Spearman’s correlation, gathered across multiple Monte Carlo repetitions in the benchmark scenario using various methodologies, including Naive Bayes, MNIR, and dictionary methods. For the dictionary method, 80%, 90%, and 100% represent the proportion of words in S that are part of the pre-established dictionary utilized for sentiment measurement. The remaining 20% and 10% in the first two cases are randomly selected from the list of sentiment-neutral words.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>SESTM</td><td style='text-align: center; word-wrap: break-word;'>Naive Bayes</td><td style='text-align: center; word-wrap: break-word;'>MNIR</td><td style='text-align: center; word-wrap: break-word;'>Dictionary (80%)</td><td style='text-align: center; word-wrap: break-word;'>Dictionary (90%)</td><td style='text-align: center; word-wrap: break-word;'>Dictionary (100%)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Avg SR</td><td style='text-align: center; word-wrap: break-word;'>0.878</td><td style='text-align: center; word-wrap: break-word;'>0.833</td><td style='text-align: center; word-wrap: break-word;'>0.845</td><td style='text-align: center; word-wrap: break-word;'>0.816</td><td style='text-align: center; word-wrap: break-word;'>0.837</td><td style='text-align: center; word-wrap: break-word;'>0.853</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Std Dev</td><td style='text-align: center; word-wrap: break-word;'>0.007</td><td style='text-align: center; word-wrap: break-word;'>0.010</td><td style='text-align: center; word-wrap: break-word;'>0.008</td><td style='text-align: center; word-wrap: break-word;'>0.011</td><td style='text-align: center; word-wrap: break-word;'>0.009</td><td style='text-align: center; word-wrap: break-word;'>0.008</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">Table 2: Performance of daily news sentiment portfolios, including equal-weighted (EW) and value-weighted (VW) long-short (L-S) portfolios and their long (L) and short (S) legs. The performance measures include (annualized) annual Sharpe ratio, annualized expected returns, risk-adjusted alphas, and  $ R^2 $s (in percentage) with respect to the Fama-French three-factor model (“FF3”), the Fama-French five-factor model (“FF5”), and the Fama-French five-factor model augmented to include the momentum factor (“FF5+MOM”). We also report the strategy’s daily turnover, defined as  $ \frac{1}{2T}\sum_{t=1}^{T}\left(\sum_{i}|w_{i,t+1}-\frac{w_{i,t}(1+y_{i,t+1})}{1+\sum_{j}w_{j,t}y_{j,t+1}}|\right) $, where  $ w_{i,t} $ is the weight of stock  $ i $ in the portfolio at time  $ t $, as well as max drawdown, defined as the peak-to-trough decline relative to the value at peak.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Sharpe</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Average</td><td style='text-align: center; word-wrap: break-word;'>Max</td><td colspan="2">FF3</td><td colspan="2">FF5</td><td colspan="2">FF5+MOM</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Formation</td><td style='text-align: center; word-wrap: break-word;'>Ratio</td><td style='text-align: center; word-wrap: break-word;'>Turnover</td><td style='text-align: center; word-wrap: break-word;'>Return</td><td style='text-align: center; word-wrap: break-word;'>Drawdown</td><td style='text-align: center; word-wrap: break-word;'>$ \alpha $</td><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>$ \alpha $</td><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>$ \alpha $</td><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>EW L-S</td><td style='text-align: center; word-wrap: break-word;'>5.21</td><td style='text-align: center; word-wrap: break-word;'>95.55%</td><td style='text-align: center; word-wrap: break-word;'>36</td><td style='text-align: center; word-wrap: break-word;'>15.91%</td><td style='text-align: center; word-wrap: break-word;'>36</td><td style='text-align: center; word-wrap: break-word;'>1.26</td><td style='text-align: center; word-wrap: break-word;'>36</td><td style='text-align: center; word-wrap: break-word;'>1.48</td><td style='text-align: center; word-wrap: break-word;'>36</td><td style='text-align: center; word-wrap: break-word;'>1.79</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>EW L</td><td style='text-align: center; word-wrap: break-word;'>2.15</td><td style='text-align: center; word-wrap: break-word;'>95.93%</td><td style='text-align: center; word-wrap: break-word;'>19</td><td style='text-align: center; word-wrap: break-word;'>42.21%</td><td style='text-align: center; word-wrap: break-word;'>18</td><td style='text-align: center; word-wrap: break-word;'>38.88</td><td style='text-align: center; word-wrap: break-word;'>18</td><td style='text-align: center; word-wrap: break-word;'>39.49</td><td style='text-align: center; word-wrap: break-word;'>18</td><td style='text-align: center; word-wrap: break-word;'>40.33</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>EWS</td><td style='text-align: center; word-wrap: break-word;'>1.52</td><td style='text-align: center; word-wrap: break-word;'>95.17%</td><td style='text-align: center; word-wrap: break-word;'>16</td><td style='text-align: center; word-wrap: break-word;'>71.91%</td><td style='text-align: center; word-wrap: break-word;'>18</td><td style='text-align: center; word-wrap: break-word;'>34.50</td><td style='text-align: center; word-wrap: break-word;'>18</td><td style='text-align: center; word-wrap: break-word;'>35.43</td><td style='text-align: center; word-wrap: break-word;'>18</td><td style='text-align: center; word-wrap: break-word;'>36.73</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>VW L-S</td><td style='text-align: center; word-wrap: break-word;'>1.56</td><td style='text-align: center; word-wrap: break-word;'>93.75%</td><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>24.38%</td><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>0.99</td><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>1.67</td><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>1.69</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>VW L</td><td style='text-align: center; word-wrap: break-word;'>1.04</td><td style='text-align: center; word-wrap: break-word;'>93.85%</td><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>35.99%</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>30.96</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>31.02</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>31.50</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>VW S</td><td style='text-align: center; word-wrap: break-word;'>0.09</td><td style='text-align: center; word-wrap: break-word;'>93.66%</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>74.18%</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>25.47</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>25.88</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>26.09</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">Table 3: Comparison of SESTM with LM, RavenPack, and BERT. This table replicates the analysis from Table 2 for equal-weighted and value-weighted long-short portfolios shown in Figure 7, but focuses only on the out-of-sample period beginning in October 2014. It also incorporates additional covariates in a series of portfolio spanning tests. Sharpe ratios are annualized; returns and alphas are reported in basis points per day.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Sharpe</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Average</td><td colspan="4">FF6+SESTM</td><td colspan="4">FF6+LM</td><td colspan="4">FF6+RP</td><td colspan="4">FF6+BERT</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Ratio</td><td style='text-align: center; word-wrap: break-word;'>Turnover</td><td style='text-align: center; word-wrap: break-word;'>Return</td><td style='text-align: center; word-wrap: break-word;'>$ \alpha $</td><td style='text-align: center; word-wrap: break-word;'>t( $ \alpha $)</td><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>$ \alpha $</td><td style='text-align: center; word-wrap: break-word;'>t( $ \alpha $)</td><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>$ \alpha $</td><td style='text-align: center; word-wrap: break-word;'>t( $ \alpha $)</td><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>$ \alpha $</td><td style='text-align: center; word-wrap: break-word;'>t( $ \alpha $)</td><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>$ \alpha $</td><td style='text-align: center; word-wrap: break-word;'>t( $ \alpha $)</td><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td colspan="20">SESTM</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>EW</td><td style='text-align: center; word-wrap: break-word;'>4.85</td><td style='text-align: center; word-wrap: break-word;'>95.10%</td><td style='text-align: center; word-wrap: break-word;'>37</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>33</td><td style='text-align: center; word-wrap: break-word;'>10.27</td><td style='text-align: center; word-wrap: break-word;'>4.50</td><td style='text-align: center; word-wrap: break-word;'>29</td><td style='text-align: center; word-wrap: break-word;'>9.16</td><td style='text-align: center; word-wrap: break-word;'>7.10</td><td style='text-align: center; word-wrap: break-word;'>35</td><td style='text-align: center; word-wrap: break-word;'>10.97</td><td style='text-align: center; word-wrap: break-word;'>3.00</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>VW</td><td style='text-align: center; word-wrap: break-word;'>1.43</td><td style='text-align: center; word-wrap: break-word;'>91.60%</td><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>2.32</td><td style='text-align: center; word-wrap: break-word;'>8.30</td><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>2.49</td><td style='text-align: center; word-wrap: break-word;'>6.70</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>2.93</td><td style='text-align: center; word-wrap: break-word;'>5.30</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td colspan="20">LM</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>EW</td><td style='text-align: center; word-wrap: break-word;'>3.14</td><td style='text-align: center; word-wrap: break-word;'>95.40%</td><td style='text-align: center; word-wrap: break-word;'>23</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>5.05</td><td style='text-align: center; word-wrap: break-word;'>5.10</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>18</td><td style='text-align: center; word-wrap: break-word;'>5.84</td><td style='text-align: center; word-wrap: break-word;'>3.60</td><td style='text-align: center; word-wrap: break-word;'>21</td><td style='text-align: center; word-wrap: break-word;'>6.94</td><td style='text-align: center; word-wrap: break-word;'>2.40</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>VW</td><td style='text-align: center; word-wrap: break-word;'>1.71</td><td style='text-align: center; word-wrap: break-word;'>93.40%</td><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>3.36</td><td style='text-align: center; word-wrap: break-word;'>5.90</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>3.78</td><td style='text-align: center; word-wrap: break-word;'>1.90</td><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>3.79</td><td style='text-align: center; word-wrap: break-word;'>2.80</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td colspan="20">RavenPack</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>EW</td><td style='text-align: center; word-wrap: break-word;'>4.20</td><td style='text-align: center; word-wrap: break-word;'>97.00%</td><td style='text-align: center; word-wrap: break-word;'>30</td><td style='text-align: center; word-wrap: break-word;'>21</td><td style='text-align: center; word-wrap: break-word;'>7.02</td><td style='text-align: center; word-wrap: break-word;'>7.00</td><td style='text-align: center; word-wrap: break-word;'>27</td><td style='text-align: center; word-wrap: break-word;'>8.91</td><td style='text-align: center; word-wrap: break-word;'>2.90</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>28</td><td style='text-align: center; word-wrap: break-word;'>9.45</td><td style='text-align: center; word-wrap: break-word;'>2.10</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>VW</td><td style='text-align: center; word-wrap: break-word;'>1.77</td><td style='text-align: center; word-wrap: break-word;'>97.20%</td><td style='text-align: center; word-wrap: break-word;'>11</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>3.47</td><td style='text-align: center; word-wrap: break-word;'>6.70</td><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>3.77</td><td style='text-align: center; word-wrap: break-word;'>4.40</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>3.85</td><td style='text-align: center; word-wrap: break-word;'>4.50</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td colspan="20">BERT</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>EW</td><td style='text-align: center; word-wrap: break-word;'>1.89</td><td style='text-align: center; word-wrap: break-word;'>93.70%</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>11</td><td style='text-align: center; word-wrap: break-word;'>3.17</td><td style='text-align: center; word-wrap: break-word;'>2.70</td><td style='text-align: center; word-wrap: break-word;'>14</td><td style='text-align: center; word-wrap: break-word;'>4.31</td><td style='text-align: center; word-wrap: break-word;'>1.50</td><td style='text-align: center; word-wrap: break-word;'>13</td><td style='text-align: center; word-wrap: break-word;'>3.78</td><td style='text-align: center; word-wrap: break-word;'>1.90</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>VW</td><td style='text-align: center; word-wrap: break-word;'>0.56</td><td style='text-align: center; word-wrap: break-word;'>90.70%</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>1.29</td><td style='text-align: center; word-wrap: break-word;'>3.50</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>1.23</td><td style='text-align: center; word-wrap: break-word;'>3.40</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>1.44</td><td style='text-align: center; word-wrap: break-word;'>2.60</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr></table>

