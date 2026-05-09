# An explainable attention network for fraud detection in claims management☆

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//04d54618-4f38-483d-b2a8-90356a68b93d/markdown_0/imgs/img_in_image_box_895_329_953_386.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A21Z%2F-1%2F%2Fd3e0fb7ef4349a56ca8a1e170422adf8a08c4a31be33c7c6dd010250d279cbaa" alt="Image" width="5%" /></div>


Helmut Farbmacher $ ^{a} $, Leander Löw $ ^{b} $, Martin Spindler $ ^{b,*} $

 $ ^{a} $ Munich Center for the Economics of Aging, Max Planck Society, Germany  

 $ ^{b} $ Hamburg Business School, University of Hamburg, Germany

#### ARTICLE INFO

Article history:

Received 29 May 2019

Received in revised form 24 April 2020

Accepted 4 May 2020

Available online 30 September 2020

Keywords:

Claims management

Health insurance

Fraud detection

Machine learning

Deep learning

Categorical data

Embeddings

## A B S T R A C T

Insurance companies must manage millions of claims per year. While most of these are not fraudulent, those that are nevertheless cost insurance companies and those they insure vast amounts of money. The ultimate goal is to develop a predictive model that can single out fraudulent claims and pay out non-fraudulent ones automatically. Health care claims have a peculiar data structure, comprising inputs of varying length and variables with a large number of categories. Both issues are challenging for traditional econometric methods. We develop a deep learning model that can handle these challenges by adapting methods from text classification. Using a large dataset from a private health insurer in Germany, we show that the model we propose outperforms a conventional machine learning model. With the rise of digitalization, unstructured data with characteristics similar to ours will become increasingly common in applied research, and methods to deal with such data will be needed.

© 2020 The Authors. Published by Elsevier B.V. This is an open access article under the CC BY license (http://creativecommons.org/licenses/by/4.0/).

### 1. Introduction

Health insurers receive millions of claims per year. Given that information asymmetries between the principal (insurer) and the agents (health care providers and the insured) can lead to moral hazard, insurance companies face the choice of either paying out insurance claims immediately without any adjustments or reviewing claims that are suspicious. The most common method for undertaking the latter involves manually auditing claims data, which is a time-consuming and expensive process (see, for instance, Townsend, 1979; Bond and Crocker, 1997). Machine learning models can greatly cut auditing costs by automatically screening incoming claims and flagging up those that are deemed to be suspicious – i.e. potentially incorrect – for subsequent manual auditing.

Health care claims have an unusual input data structure. During each doctor consultation or hospital visit, several tasks are performed and may be billed as separate items. Medical coders identify all services, prescriptions, and supplies received by the insured during his or her appointment and create an insurance claim. Each claim consists of multiple items, including the dates of treatment, a short description of the task or tasks performed, and the associated costs. The number of items varies from patient to patient, resulting in claims of variable length. Because ordinary machine learning methods, such as gradient boosting or random forests, require a vector of fixed size as input, the standard approach so far has been

to find a fixed-size vector by manually engineering features based on domain knowledge. Doing so, however, requires costly domain experts and does not scale well to other problems, even if they are similar. Moreover, good features can be difficult to build with manual feature engineering. In search of a better solution and, in particular, a way to automate this process, we exploit the similarities between the data structure of a claim and the data structure of a text.

Our main contribution is to describe deep learning architectures that can be used to handle datasets with a varying number of variables per observation and/or variables with very many categories. Datasets like these share some similarities with text data because sentences in a text can be of varying length, and words in a sentence can be interpreted as a variable with a large number of categories (each word in a dictionary is a category). One difference to text data is that the order of words in a text is crucial to understanding the meaning of a sentence, whereas it is uninformative in the applications we consider here. There are many other applications in which the deep learning architectures we describe might play an important role. For instance, incorporating occupational classifications in labor economics, industry codes in industrial organization, or International Classification of Diseases (ICD) codes in health economics, entails dealing with variables with very many categories. Researchers in these and other fields will increasingly have to grapple with unstructured and massive datasets as these become more readily available due to the rise of digitalization.

In recent years, deep learning models based on artificial neural networks have begun to show human-level performance in text processing (see, for example, Kim, 2014; Lai et al., 2015; Vaswani et al., 2017; Devlin et al., 2019). Because methods like these can directly handle unusual data structures and perform feature engineering as part of the learning process, they may represent an automated alternative to manual feature engineering. We pursue this approach for an important step in the claims management process: auditing and managing the risk of fraud and error. Additionally, we investigate the extent to which such models deliver meaningful explanations for their predictions. These explanations can be used to shed light on suspicious claim items, greatly simplifying the subsequent auditing process and thus transforming the model from a tool that is merely predictive to one that is prescriptive.

In our empirical application, we train standard and non-standard machine learning models on real data containing past claims and their associated labels, which classify each claim as either correct or suspicious. The latter may refer to any kind of error, ranging from typographical errors and unintentional upcoding to fraud. For a comprehensive overview of various fraud behaviors, see Li et al. (2008). For the sake of simplicity, we refer in the following to the detection of suspicious errors as (insurance) fraud detection. For each claim, we want to predict the probability of fraud and pay out all non-fraudulent claims automatically without any further manual auditing. Fraudulent or suspicious claims, however, should be flagged up so that they can be audited. Supervised machine learning models are tailored to this task. Like all supervised models, they should be updated regularly to capture new types of fraud and changes in regulations.

There is a vast literature on the economics of auditing and optimal auditing (see, for instance, Townsend, 1979; Mookherjee and Png, 1989; Picard, 1996; Schiller, 2006; Dionne et al., 2009, and, for an overview, Picard 2013). Schiller (2006) provided evidence that auditing becomes more effective when insurers condition their audits on the information provided by fraud detection systems. Dionne et al. (2009) showed that an optimal auditing strategy takes the form of a red-flags approach, which entails referring a claim to the auditing unit once certain fraud signals have been observed. We, in turn, demonstrate that our deep learning model is a particularly useful tool in the claims management process because it not only adds another red flag but gives further insights into the fraud mechanisms themselves.

Detecting fraud or systemic abuse is a major challenge for health insurers (see, for instance, Becker et al., 2005; Heese, 2018; Bastani et al., 2019), and there is also a vast literature on data-driven methods for fraud detection. For instance, Liou et al. (2008) compared the accuracy of logistic regression, neural networks, and classification trees in identifying fraud and claim abuse in diabetic outpatient services. Viaene et al. (2002) compared the performance of several classification techniques in detecting car insurance fraud. Van Vlasselaer et al. (2017) proposed a model that employs information about firm networks to detect social security fraud. Classification methods have also been used in other settings, for example to detect management fraud (Cecchini et al., 2010) or identify high-risk disability claims (Urbanovich et al., 2003). An overview of data-driven methods for fraud assessment is given by Bolton and Hand (2002) and Ekin et al. (2018), the latter of whom focus on the assessment of medical fraud.

In Section 2, we discuss an important trade-off that a cost-minimizing insurer faces in the claims management process. Our economic evaluation criterion, which we use to assess the performance of our machine learning model, reflects this trade-off. In Section 3, we describe the unusual data structure of our health care claims in detail. Section 4 gives a brief introduction to neural networks and deep learning. In Sections 5 and 6, we describe how deep learning can handle categorical variables with high cardinality, flexibly model nonlinearities, and aggregate the claims with variable length in a data-driven fashion—both generally and with regard to our specific application. Section 7 discusses the results of the models when applied to claims data from a private health insurer in Germany. Section 8 concludes.

### 2. The economics of auditing

A cost-minimizing insurance company faces a trade-off between the expected benefits of auditing (above all, the expected value of the adjustments to upcoded or fraudulent claims) and the auditing costs. This trade-off is an important component in models of optimal auditing (see, e.g., Mookherjee and Png, 1989). Our economic evaluation criterion, which we use to evaluate our machine learning model, reflects this trade-off. The main goal of our machine learning model is to identify suspicious claims automatically. A crucial aspect in this regard is its ability to predict the probability of fraud.

(P) for new, unseen claims. In doing so, two types of error may occur: the model may classify a non-fraudulent claim as suspicious, which would be a false positive, or it might fail to identify a fraudulent claim, which would be a false negative. Our evaluation criterion takes both errors into account.

Let N denote the number of claims (both fraudulent and non-fraudulent), c the fixed costs of manual auditing, and  $ a_{i} $ the adjustment associated with a particular claim. The last of these represents the cash benefit for that claim if correctly identified as suspicious. We assume that manual auditing of the suspicious claims detected by our models correctly identifies truly fraudulent claims with a probability equal to one. In this manner, the auditing process conditional on any machine learning model achieves a cost reduction of  $ \pi $ as follows:

 $$ \pi=\sum_{i=1}^{N}I(P_{i}>\tau)\cdot(a_{i}-c). $$ 

I() is the indicator function, which equals 1 if the statement in parentheses is true.  $ \tau $ is a threshold chosen by the insurer. It can be any value between 0 and 1 depending on free capacities in the auditing unit, risk preferences of the principal, or (fraud) signals from agents. Such a signal could, for instance, be based on the total number of claims a health care provider submits to the insurer (Li et al., 2008) or on hours worked by the provider (Fang and Gong, 2017). Splitting the claims into fraudulent and non-fraudulent cases, we have

 $$ \pi=\sum_{i\in fraud}I(P_{i}>\tau)\cdot(a_{i}-c)-\sum_{i\in no fraud}I(P_{i}>\tau)\cdot c. $$ 

The first term captures the net benefit of the true positives, and the second term the costs of the false positives. Any false positive causes a monetary loss  $ c $ due to the manual auditing costs. Let  $ FP_\tau = \sum_{i \in \text{no fraud}} I(P_i > \tau) $ denote the number of false positives and  $ FN_\tau = \sum_{i \in \text{fraud}} I(P_i \leq \tau) $ the number of false negatives. Generally, a lower value of  $ \tau $ increases the number of suspicious claims at the cost of a (potentially) larger  $ FP_\tau $, while a higher value of  $ \tau $ increases  $ FN_\tau $.

To incorporate the cost reductions missed due to false negatives, we compare  $ \pi $ with the maximum reduction in cost that can be achieved in the auditing process. This maximum is defined as

 $$ \pi^{\max}=\sum_{i\in fraud}\left(a_{i}-c\right). $$ 

Note that the missing indicator function implies that there are no false negatives. Moreover, there are also no false positives in  $ \pi^{\text{max}} $. That is, it reflects the maximum cost reduction that can be achieved if we know the fraudulent claims a priori from an oracle model. Finally, our evaluation criterion is defined as

 $$ \gamma=\pi^{\max}-\pi, $$ 

which measures the foregone cost savings of any screening model. A cost-minimizing insurer aims to set π = πmax.

For simplification, our evaluation criterion abstracts from several issues. First, we assume that the cost of manual auditing is a fixed amount per suspicious claim. However, one can imagine that these costs do not scale to all sizes of auditing unit. A unit that processes only pre-selected claims, for example, may be less expensive per claim than a larger auditing unit that has to verify all of the claims an insurer receives. As a result, our evaluation criterion may underestimate the potential benefits of a fraud detection system. Second, the benefits of auditing claims are not limited to identifying and adjusting fraudulent claims but rather extend to the deterrent effect that auditing can have on potential defrauders. Tennyson and Salsas-Forn (2002) and Dionne et al. (2009) are two of many authors who discuss the importance of claims auditing as a deterrent. Effective machine learning models could strengthen this effect. Third, meaningful explanations of suspicious claims may considerably shorten the subsequent (manual) auditing process. In summary, our evaluation criterion does not represent a general measure of the benefits of auditing but rather focuses on the direct net gains of our machine learning model.

### 3. Data structure and descriptives

Generally, items in health care claims consist of several variables that indicate the quantity and type of medical treatment provided, potential complications, and the price of the treatment. Depending on the type of health insurance and the country in question, prices vary for the same service and may thus contain additional information about the potential for settling suspicious claims. This is, for instance, the case for private health insurance in the US. Alternatively, there may be a physician fee schedule, which determines a fixed price for any medical service (as, for instance, in Medicare in the US or generally in private and public health insurance in Germany). In our empirical application, we employ health care claims from a private health insurer in Germany. These contain three variables for every claim item: a procedure code specifying which medical service was provided, a multiplier, which measures the patient-specific severity of the task, and the price of the medical service in question (as a numerical value). Each procedure code is assigned a base price, which, after the multiplier has been applied, yields the price of this medical service.

The dataset we use is a copy of all claims submitted to the private health insurer during a certain period. The structure of the dataset is representative of the German private health insurance market as a whole. It contains 381,013 claims.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//04d54618-4f38-483d-b2a8-90356a68b93d/markdown_3/imgs/img_in_chart_box_89_111_497_404.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A24Z%2F-1%2F%2Ff60c46af9b1a625436799051d653a2b30da2f3a6a5e4ffa8fc3804a215a8eddd" alt="Image" width="37%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(a) Fraud Probability</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//04d54618-4f38-483d-b2a8-90356a68b93d/markdown_3/imgs/img_in_chart_box_590_114_998_403.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A24Z%2F-1%2F%2Fe836c25b88b063e2173a7851edf8c2ee66d1f0e32862e38743e995ed4db2a693" alt="Image" width="37%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(b) Average Adjustments (cond. on fraud)</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 1. Heterogeneity over Most Frequent Categories of Procedure Code.</div> </div>


comprising more than three million claim items. On average, a claim in our dataset contains 8.6 items (range: 1–100), and 50% of the claims contain no more than 5 items. Each claim item consists of three variables: (1) the procedure code, which is a categorical variable with 2,205 categories; (2) the multiplier with six categories; and (3) the price, which we scale between zero and one after log transformation. The input vectors of a claim can be set up as a two-dimensional matrix, where each row is one claim item consisting of these three variables. Every claim has an associated label indicating whether an adjustment was made to it. For example, when the original charges in a claim were 100€ but ultimately only 80€ were paid, then we define the difference as the adjustment and label the claim as fraudulent. 1.5% of the claims in our data are fraudulent. The labels, which originate from manual auditing, refer to any kind of error, ranging from typos and unintentional upcoding to fraud. They might miss truly fraudulent claims and hence mislabeling might be prevalent among the non-fraud labels. This is a typical challenge of supervised learning.

Of course, insurance companies have additional variables at their disposal to detect fraud, such as characteristics of providers and the insured. While these can easily be included in our deep learning model, we refrain from doing so for confidentiality reasons and to focus on the peculiar data structure of the claims, which was the scope of our cooperation with the insurer.

We briefly examine the descriptive relationship between a claim being fraudulent and some of the important information in our data. $ ^{1} $ Fig. 1 shows the probability of fraud and the average adjustments conditional on fraudulent claims separately for the most frequent categories of the procedure code. The considerable heterogeneity that we can observe across these suggests that there is also considerable heterogeneity across the many other categories that we will use later in the model. Fig. 2 relates the fraud probability and the average adjustments to the length of the claims, i.e. the number of claim items. Claims with more than 50 items are aggregated to a single scatter dot. The probability of fraud tends to increase with the claim length, particularly for relatively short claims. The average adjustments show a highly nonlinear relationship with claim length.

### 4. A short introduction to neural networks

In this section, we give a brief introduction to neural networks. We focus on the basic concepts required to understand how our deep learning model can automatically classify claims, and we connect these concepts to the econometric terminology. Machine learning methods like deep learning or boosted trees can be applied to both regression problems (continuous outcome variables) or classification problems (discrete outcome variables). In the regression case, we want to approximate the unknown relation  $ f(x) $ between a dependent variable y and a p-dimensional set of input variables  $ x = (x_1, \ldots, x_p)' $:

 $$ y=f(x)+\epsilon $$ 

with  $ \epsilon $ denoting the error term. In the classification task, we model the probability of belonging to a certain class instead.

Deep learning, which in essence is an approach that uses neural networks with many layers, is a powerful way to estimate complex nonlinear relationships. All standard feedforward neural networks have a very similar structure, which consists of an input layer and an output layer, as well as several hidden layers. Each layer can consist of many units, also called neurons, which can be interpreted as constructed regressors. Every layer can have a different number of units.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//04d54618-4f38-483d-b2a8-90356a68b93d/markdown_4/imgs/img_in_chart_box_89_112_497_405.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A25Z%2F-1%2F%2Faea76463f4a07f6798b0cb735d13d8f92d39d9a9f35e78e4de952611957aa253" alt="Image" width="37%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(a) Fraud Probability</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//04d54618-4f38-483d-b2a8-90356a68b93d/markdown_4/imgs/img_in_chart_box_590_113_999_404.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A25Z%2F-1%2F%2Fafa59b3bb331a84cbb819b24dda3abb3d9413c22519da6008f4df18d3a978f72" alt="Image" width="37%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(b) Average Adjustments (cond. on fraud)</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 2. Descriptive Relationship with Claim Length.</div> </div>


The input layer contains the input variables (also called features) in our model. The units within a hidden layer receive inputs from the previous layer, execute a sequence of calculations, and then pass the result on to the subsequent layer. Finally, the output layer combines all results to predict the outcome variable. In the binary classification task considered here, the output layer has just one unit, i.e. it predicts only a single value, which can be interpreted as the (classification) probability.

Every unit  $ k(=1,\ldots,K_j) $ in layer  $ j(=1,\ldots,J) $ applies a series of calculations. First, every unit  $ k $ computes a linear index  $ (z_k^{[j]}) $ of the weights  $ (w_k^{[j]}) $ and the inputs from the previous layer  $ (a^{[j-1]}) $, and adds an intercept term  $ (b_k^{[j]}) $,

 $$ z_{k}^{[j]}=a^{[j-1]^{\prime}}w_{k}^{[j]}+b_{k}^{[j]} $$ 

where  $ a^{[j-1]} $ and  $ w_{k}^{[j]} $ are vectors and  $ b_{k}^{[j]} $ is a scalar. The output of the initial (input) layer can be interpreted as  $ a^{[0]} = x $. In the neural network literature, the coefficients are usually called weights and the intercept is called bias. The biases and weights are usually allowed to be different for each unit. Second, the linear index is passed through a so-called activation function. To achieve non-linearity, the activation functions are key. Each unit calculates

 $$ a_{k}^{[j]}=g(z_{k}^{[j]}) $$ 

with  $ g(\cdot) $ being a non-linear activation function and  $ a^{[j]} = (a_{j}^{[j]}, \ldots, a_{k_{j}^{[j]}}^{[j]}) $ forming the inputs of the subsequent layer. Usually, the activation function is the same for all units within a layer. The non-linearity of the activation functions enables the neural net to approximate a potentially complex relation between outcome and predictors. There are several activation functions in the literature. The most common ones are illustrated in Fig. 3: rectified linear units,  $ \text{relu}(x) = \max(0, x) $; the logistic sigmoid,  $ \sigma(x) = (1 + \exp(-x))^{-1} $; and the hyperbolic tangent,  $ \tanh(x) = 2\sigma(2x) - 1 $. The default choice is usually the rectified linear units (ReLU). Glorot et al. (2011) identify sparsity as a key element of the success of ReLU activations. The exact zeros that can arise from this function allow a sparse representation, which is appealing from a computational point of view despite its non-differentiability at zero.

Finally, in the output layer, the features are then used to construct an estimator  $ \widehat{y} $ for the outcome variable y. In the case of a regression, the continuous output is directly constructed by a linear combination of the previous units

 $$ a^{[J]}=a^{[J-1]^{\prime}}w_{k}^{[J]}+b_{k}^{[J]} $$ 

 $$ y=id(a^{[j]}) $$ 

with id denoting the identity function. In the case of a binary classification  $ (0/1) $, instead of the identity, a logistic transformation is applied

 $$ P(y=1|x)=\sigma\left(a^{[J]}\right). $$ 

This can easily be generalized to cases with more than two classes, say  $ K_j $ classes. The output-layer then consists of  $ K_j $ units, each describing the probability that the outcome falls into this category. This type of output layer is usually modeled by a multinomial distribution. $ ^2 $ To simplify notation, we will switch to matrix notation when we describe our model in

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//8bb583fd-d1fb-4666-ba5b-d8626519d25f/markdown_0/imgs/img_in_chart_box_313_114_776_446.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A18Z%2F-1%2F%2F5953560773053ebb1c74037ff523305fb0edcb02ecdc8006b544311118b23950" alt="Image" width="42%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 3. Common Activation Functions in Neural Networks.</div> </div>


the following sections. For every layer j, we then have

 $$ W_{j}=\begin{pmatrix}w_{1}^{[j]^{\prime}}\\ \vdots\\ w_{k}^{[j]^{\prime}}\\ \vdots\\ w_{K_{j}}^{[j]^{\prime}}\end{pmatrix},\quad b_{j}=\begin{pmatrix}b_{1}^{[j]}\\ \vdots\\ b_{k}^{[j]}\\ \vdots\\ b_{K_{j}}^{[j]}\end{pmatrix} $$ 

with  $ W_j \in \mathbb{R}^{K_j \times K_{j-1}} $ and  $ b_j \in \mathbb{R}^{K_j} $.

A standard neural network consists of a series of layers. For illustration, Fig. 4a depicts a shallow (as opposed to deep) neural network. The units are connected to each other across layers but not within a layer. Early applications of such single hidden layer networks in econometrics are Kuan and White (1994), Giacomini et al. (2008), McAleer et al. (2008) and Medeiros et al. (2008). By using additional hidden layers and more units, the network can approximate more complex functional relationships (Hornik et al., 1989; Hornik, 1991; Montúfar et al., 2014; Eldan and Shamir, 2016; Telgarsky, 2016). The additional hidden layers are created in the same way: each unit in a given layer is a nonlinear transformation of a linear combination of the units from the preceding layer. The depth of a neural network refers to the number of hidden layers. Fig. 4b illustrates the structure of a logistic regression, which can be interpreted as a neural network without hidden layers. The unit in the output layer calculates a single linear index  $ (z = x'w + b) $ and uses a sigmoid activation function,  $ \sigma(z) = \widehat{y} $.

Here we would like to mention briefly several general issues related to implementing deep neural networks. First, a neural network partly depends on a priori decisions of the researcher, which often cannot be theoretically motivated. For instance, prior to optimization, we have to choose the number of hidden layers, the number of units within a hidden layer, and the type of activation functions. $ ^{3} $ These decisions are the hyperparameters of a neural net. Usually, we consider a grid of values for the hyperparameters and pick the model that performs best. Second, a neural network often contains many parameters relative to the available sample size. As one can easily see, the number of parameters grows quickly as the number of units per layer and the number of layers increase. While a neural network with more units and more layers allows a better approximation of the unknown functional form, it is prone to overfit unique characteristics of the data that are not present in an additional, independent dataset. To avoid overfitting, we randomly split the data into three parts: a training sample, a validation sample for tuning hyperparameters, and a hold-out dataset for the final testing of our model. The hold-out sample should not be used to train the parameters or tune the hyperparameters. The latter could lead to indirect overfitting. Third, a challenge is how to estimate the parameters of a neural network. Measuring the discrepancy between observed values y and predicted values  $ \widehat{y} $ with a loss function, we must find the parameter vectors that minimize this loss function. The standard optimization algorithm is stochastic gradient descent (Goodfellow et al., 2016), which involves calculating the gradient of the loss function using only a subset of observations randomly chosen from the sample at each step. For this purpose, the training set is usually divided into mini-batches of 128 observations. The gradient is calculated via the backpropagation algorithm (Rumelhart et al., 1986). Additional hyperparameters, such

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//8bb583fd-d1fb-4666-ba5b-d8626519d25f/markdown_1/imgs/img_in_image_box_122_108_539_479.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A19Z%2F-1%2F%2Facdf804b8d77314fe5a2ef63610e62c3972e42c8ea813555df96198eb5fff868" alt="Image" width="38%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(a) 2-layer neural network</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//8bb583fd-d1fb-4666-ba5b-d8626519d25f/markdown_1/imgs/img_in_image_box_652_106_959_467.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A19Z%2F-1%2F%2Fec176481d994eda2277970d9b7f74c2e8ade2a15fa285757ba4346608a91e145" alt="Image" width="28%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(b) 1-layer NN ((Logit) regression)</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 4. Graphical Illustration of Neural Networks.</div> </div>


as the learning rate, have to be set in the optimization. The learning rate determines how much the optimization adjusts the parameters in each iteration. The standard loss function for regressions or classifications is the mean squared error or the likelihood function, respectively. For a broader discussion of deep learning and neural networks, see Goodfellow et al. (2016).

### 5. Deep learning for categorical data, sequences and highly unbalanced data

In the previous section, we discussed a standard feedforward neural network architecture. Our dataset has three characteristics that make it difficult to implement such networks: namely variables with very many categories, varying input length and highly unbalanced data. The methods we present in this section to address these challenges may be of independent interest because these characteristics are common for many datasets in applied research.

#### 5.1. Methods for categorical data

Generally, categorical variables cannot be used directly in neural networks. In this section, we describe methods for encoding variables that have a large number of categories. Many of these methods have been developed for text analysis because a word can be seen as a realization from a dictionary with very many entries. There are, however, many other applications in applied economics that must deal with high cardinality. The method we present here can, for instance, be used to embed ICD codes in health economics, occupational classifications in labor economics, or industry codes in industrial organization. $ ^{4} $

The most common way to handle categorical variables is to expand them into dummy variables, an approach known as one-hot encoding in machine learning and as dummy encoding in the econometrics literature. If there are m categories (size of the dictionary), a unique integer index i is associated with every category and subsequently turned into a binary vector of length m. This vector has zero entries except for the ith entry, which is 1. Using the Kronecker delta, we can formalize one-hot encoding as a function u, which maps a categorical input variable x that has values  $ \{\alpha_1, \ldots, \alpha_m\} $ into a m-dimensional vector  $ \delta_\infty $ with entries  $ (\delta_\infty, \ldots, \delta_m) $.

 $$ u:x\mapsto\delta_{\alpha}, $$ 

The Kronecker delta is defined as 1 if  $ x = \alpha_k $ and zero otherwise. One-hot encoding provides a sparse representation. If there are many categories, one-hot vectors are high-dimensional and storing them requires a lot of memory. Moreover, the encoded vectors for different categories are orthogonal and hence cannot reflect similarities or other relations between them.

One-hot encoding can already be considered the first layer in a deep learning architecture. We, however, refrain from doing so because there are no weights in this “layer” so far. The idea of categorical embeddings is, essentially, to incorporate such weights, making it a complete layer that has a linear activation function.

Categorical embeddings are an alternative method to incorporate categorical variables in deep learning models (Guo and Berkahn, 2016). They take the concept behind word embeddings, which is to learn a real-valued representation in which words with similar meaning have a similar representation, and adapt this to general types of categorical variables. The embedding layer maps each category of a discrete variable (or each one-hot encoded vector) to a real-valued vector. Each categorical variable  $ x_i $ is given its own embedding layer, which, in our application, is applied to every item of a claim to transform the categorical variable into numerical variables. Denote the number of categories of  $ x_i $ by  $ m_i $ and the size of the embedding space by  $ d_m $. The dimension of the embedding space is usually smaller than the number of categories (or the length of the one-hot encoded vector), leading to a dimension reduction. The weights are tabulated in the embedding matrix  $ (W_E \in \mathbb{R}^{d_m \times m_i}) $, which can be interpreted as a lookup table that maps every category  $ k $ into a  $ d_m $-dimensional space. Starting with the one-hot encoded categorical vector  $ \delta_\alpha $ of length  $ m_i $, the embedding function is given by

 $$ e:x_{j}\mapsto W_{E}\delta_{\alpha}, $$ 

which picks the kth column of  $ W_E $. One can either use pre-trained embedding matrices (Mikolov et al., 2013, for word embeddings) or learn the weights during the training process of the deep learning model. There are no task-specific embeddings available in our application and we, therefore, have to learn the  $ (d_m \cdot m_j) $ parameters of the embedding matrix as part of our task-specific model. This representation tends to put similar categories in the fraud process close to each other in the embedding space. Once the weights are learned, they can also be used as pre-trained embedding matrices with other datasets.

Categorical embeddings are especially useful for variables with high cardinality. When we one-hot encode such variables, the high cardinality leads to a huge set of parameters, which in turn can result in overfitting. Using an embedding layer rather than one-hot encoding reduces the number of parameters substantially and generally leads to better predictions, albeit at the expense of increased training time. If we suppose a variable has 1000 categories and the subsequent layer has 128 units, then one-hot encoding needs  $ 1000 \times 128 = 128,000 $ parameters. In contrast, an embedding first maps the categories in a lower-dimensional space, say 30 dimensions. For this we need  $ 30 \times 1000 $ parameters and then just  $ 128 \times 30 $ parameters in the subsequent layer, i.e. overall 33,840 parameters.

#### 5.2. Methods for sequences

Generally, machine learning methods require input data with fixed length. In this section, we describe methods to handle data with variable length. A very simple approach to make machine learning methods, such as boosted trees or random forests, work in situations with variable length is to fill up the shorter sequences with zeros so that all samples have the same length. This, however, may lead to suboptimal results. Another simple but widely used approach is the so-called bag-of-words. Let us assume we have a categorical variable and the number of times we observe this variable varies from observation to observation. Using a bag-of-words approach, one would determine which categories exist ("dictionary"), one-hot encode the input variables, and then aggregate the vectors by summing them up (i.e. counting how often a category/word is present in an observation), for example, or taking the maximum over all entries (i.e. indicating whether a category or word is present at all). The result of this procedure is a fixed size vector (with length of the size of the dictionary) for each observation. Far more powerful procedures are available in the deep learning literature. $ ^{5} $

Bahdanau et al. (2015) recently proposed the attention mechanism to find fixed-length and context-dependent representations. This approach allows dependencies between elements in a sequence to be taken into account independently of their distance. It has been successfully used to model context in machine translation (Bahdanau et al., 2015) or image captioning (Xu et al., 2015). The idea of the attention mechanism is to create a context vector that contains the most relevant information from a set of vectors by taking a weighted average, which is then used as input in the subsequent layer. The weights are determined in a data-driven way as described next.

The attention model has three ingredients (vectors): query and a key-value pair. The output is a weighted average of the value vectors, where the weights are determined by a similarity function (also called a compatibility or alignment function) between the query and the keys. Keys and values can be different vectors, but in many situations they are identical. More formally, we start with a query $q$, values $v = (v_1, \ldots, v_T)$ and keys $k = (k_1, \ldots, k_T)$. The output $c$ is computed as

 $$ c=\sum_{t=1}^{T}\alpha_{t}v_{t}. $$ 

c is the context vector (also called an attention vector) and has a fixed size that is independent of the length of the input sequence. The weights are calculated using the softmax-function applied to a similarity function f between query and keys

 $$ \alpha_{t}=\frac{\exp f(k_{t},q)}{\sum_{j=1}^{T}\exp f(k_{j},q)}. $$ 

In the literature, different similarity functions have been proposed, such as the (scaled) dot-product attention or additive attention (see, for instance, Bahdanau et al., 2015; Luong et al., 2015; Vaswani et al., 2017). The (scaled) dot-product attention is given by

 $$ f(k_{t},q)=\frac{k_{t}^{\prime}q}{\sqrt{d_{k}}}, $$ 

where  $ d_k $ denotes the length of the key vectors. The scaling by the factor  $ \sqrt{d_k} $ is mainly done to achieve numerical stability, which is challenging for both attention and self-attention mechanisms and remains an important focus of ongoing research. $ ^6 $

In our application, we use the attention mechanism to aggregate the varying claim length to a fixed-length vector by taking a weighted average over the items (see also Fig. 5 in Section 6). For this, the keys and values are the features of the claim items and the query is a learned parameter vector. The output is a weighted average that represents all items of a claim, and the attention weights indicate the relevance of a particular claim item. They could potentially be used to understand and substantiate the predictions, which in turn would reveal valuable information for the subsequent claims management process.

#### 5.3. Methods for highly unbalanced data

A third characteristic of our fraud data is that they are highly unbalanced. This means that the number of fraudulent cases is usually much smaller than that of the non-fraudulent ones. In addition, there are a couple of large frauds, which are particularly worthwhile to catch. This poses problems for learning the fraud process. Undersampling and oversampling are typical approaches to working with highly unbalanced data, leading either to a decrease in the number of non-fraudulent cases or an increase in the number of fraudulent cases, respectively—and in this way to a more balanced proportion of fraudulent to non-fraudulent observations. An alternative approach to handling this problem is cost-sensitive training. The idea behind cost-sensitive training is to use tailor-made loss functions that incorporate the savings of detecting a fraudulent case and the costs of inspecting a non-fraudulent one. In our empirical application, we observe that cost-sensitive training considerably improves performance and leads to better out-of-sample decisions. A short introduction to cost-sensitive learning is given in Ling and Sheng (2010).

For a binary classification model, a logistic regression is usually used to estimate the probabilities. This leads to the following loss function, which is also called the binary cross entropy loss in machine learning:

 $$ -\frac{1}{N}\sum_{i=1}^{N}\left[y_{i}\log(p(y_{i}))+(1-y_{i})\log(1-p(y_{i}))\right]. $$ 

 $ y_{i} $ denotes the binary outcome in  $ \{0, 1\} $, and  $ p(y_{i}) $ the estimated probability of the neural network for observation i given the learned parameters. In cost-sensitive learning, the loss function is scaled by the associated costs leading to:

 $$ -\frac{1}{N}\sum_{i=1}^{N}\left[(a_{i}-c)y_{i}\log(p(y_{i}))+c(1-y_{i})\log(1-p(y_{i}))\right]. $$ 

Here,  $ (a_{i} - c) $ measures the net benefits from identifying fraudulent claims, and c denotes the fixed costs of inspecting a claim. Using this weighted loss function leads to better results overall when dealing with unbalanced data because the fraudulent cases are weighted by their severity.

### 6. Deep learning model for fraud detection

In this section, we describe our model, which uses deep learning to process health care claims and identify suspicious claims automatically. We discuss the three main issues our deep learning model can address: the high cardinality of the categorical variables, the unknown patterns of the fraud process, and the relation between different items on a claim. Fig. 5 depicts the general structure of our deep learning model for fraud detection.

In the embedding layer, we use the technique described in Section 5.1 to find a real-valued representation of the categorical variables. The output of the embeddings is then concatenated with the continuous variables. Let X denote the resulting  $ d_e \times T $ matrix, where T denotes the number of items of a particular claim (analogous to the number of words in a sentence) and  $ d_e $ denotes the sum of the number of the continuous variables and the sizes of all embedding layers. X is now passed forward to the first feature extraction layer, which due to the real-valued representation of the categorical variables now allows us to model similarities flexibly between the different categories. This is the main strength of categorical embeddings.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//8bb583fd-d1fb-4666-ba5b-d8626519d25f/markdown_4/imgs/img_in_image_box_159_121_927_583.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A22Z%2F-1%2F%2Fd671dc233e7c850652c51c4fa5c1d5b45d9067fc66d0af2476418c7b1ca4d952" alt="Image" width="70%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 5. Illustration of the Distinct Layers in our Deep Learning Model. Note: For better visibility, the matrix dimensions are transposed in this illustration.</div> </div>


The first feature extraction layer (FEL) is responsible for capturing nonlinearities and interactions between parts of the inputs at the claim item level. We use a standard feedforward network here as described in Section 4. Every variable in the matrix X is turned into a set of features  $ H_{j_{1}} $ by using  $ J_{1} $ sublayers with  $ d_{f} $ units each and ReLU activation functions:

 $$ H_{j}=\mathrm{relu}(W_{Hj}H_{j-1}+b_{Hj})\quad\mathrm{with}j=1,\ldots,J_{1}\mathrm{and}H_{0}=X, $$ 

 $$ H_{j}\in\mathbb{R}^{d_{f}\times T},\;b_{H j}\in\mathbb{R}^{d_{f}}\;\forall j;\;W_{H1}\in\mathbb{R}^{d_{f}\times d_{e}};W_{H j}\in\mathbb{R}^{d_{f}\times d_{f}}\;with j=2,\ldots,J_{1} $$ 

It is important to observe that all weights of the feature extraction layer are independent of the varying claim length. This is a requisite for incorporating variable sequence lengths, and it even enables the model to handle claims of unseen lengths. However, to predict fraud probabilities, we must find one fixed-size vector for each claim.

This is the task of the aggregation layer, which takes as its input  $ H $ the output of the feature extraction layer ( $ H = H_{J_1} $). It aims to combine the information contained in each item of a claim into a single (fixed-size) vector. Sum, mean, and max pooling for each feature are simple methods that either sum, take the average, or identify the maximum value over all items of a claim. These methods connect the claim items in a rather crude and inflexible way. However, the contribution of an item to identifying potential upcoding or fraud probably varies within a claim. The claim therefore represents a context that we aim to exploit in the aggregation. Many approaches have been proposed recently to find context-dependent representations in natural language interpretation. We use the attention mechanism described in Section 5.2 in the aggregation layer. Query, values and keys are derived as linear combinations of the input variables  $ H $, and  $ c = \sum_{t=1}^T \alpha_t v_t $ is the resulting context vector of a particular claim. It has a fixed size ( $ d_f \times 1 $) that is independent of the length of this claim. In our application, we use sigmoid attention because we observe that it works better than softmax attention. In sigmoid attention, the weights need not sum up to one, which gives a slight nudge towards classifying longer sequences as suspicious cases. In the descriptive results, we have already seen that more comprehensive claims are fraudulent more often than less comprehensive ones (see Fig. 2).

After collapsing the claim items into a single observation, we have one context vector of fixed dimension per claim and can link it to the corresponding label for this claim. This leaves us with what is essentially a “standard” machine learning problem. In this step, we could, for instance, use random forests (Breiman, 2001), boosted trees (Breiman et al., 1984), or a feedforward network. We decide to set up a feedforward network in this last step to train the whole architecture, end to end. In this second feature extraction layer we capture nonlinearities and interactions at the claim level using  $ J_{2} $ sublayers with  $ d_{p} $ units each and ReLU activations, and finally obtain the scalar predictions P from a sigmoid activation in the output layer:

 $$ \begin{aligned}&c_{j}=\mathrm{relu}(W_{cj}c_{j-1}+b_{cj})\quad\mathrm{with}j=1,\ldots,J_{2}\mathrm{and}c_{0}=c,\\&P=\sigma(w^{\prime}c_{J_{2}}+b),\\ \end{aligned} $$ 

 $$ c_{j}\in\mathbb{R}^{d_{p}},b_{cj}\in\mathbb{R}^{d_{p}}\forall j;W_{c1}\in\mathbb{R}^{d_{p}\times d_{f}};W_{cj}\in\mathbb{R}^{d_{p}\times d_{p}}with j=2,\cdots,J_{2};w\in\mathbb{R}^{d_{p}};b\in\mathbb{R}. $$ 

<div style="text-align: center;"><div style="text-align: center;">Table 1</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Hyperparameter selection.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Batch size</td><td style='text-align: center; word-wrap: break-word;'>32</td><td style='text-align: center; word-wrap: break-word;'>64</td><td style='text-align: center; word-wrap: break-word;'>128</td><td style='text-align: center; word-wrap: break-word;'>128</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Hidden units ( $ d_{f} $ &amp;  $ d_{p} $)</td><td style='text-align: center; word-wrap: break-word;'>64</td><td style='text-align: center; word-wrap: break-word;'>128</td><td style='text-align: center; word-wrap: break-word;'>256</td><td style='text-align: center; word-wrap: break-word;'>128</td></tr><tr><td style='text-align: center; word-wrap: break-word;'># of sublayers (1st FEL)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1-5</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'># of sublayers (2nd FEL)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1-5</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>4</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Weight decay</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1e-04-1e-05</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>3e-05</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Dropouts</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0-0.5</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.164</td></tr></table>

Note: Bold values are the chosen hyperparameters, which performed best in the validation sample. FEL stands for Feature Extraction Layer.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//bc4b40b7-272a-4586-96b1-2a4f2bd69cd2/markdown_0/imgs/img_in_chart_box_318_327_773_637.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A20Z%2F-1%2F%2F24ccffb31f4ad80bfd5387316a7aa705e54a3b169abbcfe4f6138b55393657d7" alt="Image" width="41%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Note: Red vertical lines indicate top 1%, 5% and 10% claims.</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 6. Lorenz Curve of Adjustments.</div> </div>


We apply this model to the claims data described in Section 3. We use a validation dataset for model selection and an independent dataset for testing, each containing 20% of the claims. To train our deep learning model, we use the remaining 60% of the sample. We use dropout, which artificially corrupts the training data, to control for overfitting (Wager et al., 2013). Additionally, weight decay prevents overfitting by adding an  $ L_2 $-regularization to the training criterion. We select the dropouts and the weight decay parameters by random search. The number of hidden units, batch sizes and the number of sublayers for the nonlinearities are chosen from a grid of values. The grid values and the hyperparameters ultimately chosen are displayed in Table 1. The size of the embedding space for the categorical variable is set to the square root of the number of categories (rounded integer), i.e.  $ d_m = r(\sqrt{m}) $. We implement the model in PyTorch and use the Adam optimizer (Kingma and Ba, 2014) with learning rate  $ 1e-04 $ and early stopping.

### 7. Empirical evaluation

The success of automatically screening incoming claims crucially depends on how well our model can handle new claims. Based on the  $ N $ unseen claims in the test dataset, we determine the extent to which our screening,  $ I(P_i > \tau) $, aligns with the true fraud labels. We compare three methods to model  $ P_i $. First, we consider a random assignment of claims to manual auditing as a weak benchmark. $ ^7 $ Second, we use boosted trees (BT) with one-hot encoded categorical variables as a competing machine learning method. Finally, we use a classification derived from our deep learning model.

To make all three methods comparable, a constant number of claims are flagged up by each method and assigned to manual auditing. This analysis can be motivated with capacity constraints in the auditing unit. Let the number of claims, which the auditing unit can handle, be denoted by  $ N_r $. Every model  $ m $ then needs a specific threshold  $ \tau_m $ such that a constant number  $ N_\tau = \sum_{i=1}^N I(P_i^m > \tau_m) $ of suspicious claims are assigned to manual auditing. This way we interpret  $ P_i $ as a ranking and assign the claims that are most suspicious according to the respective screening model first. The quality of the automatic screening at any  $ N_\tau $ depends on how well the model can classify the claims (i.e. separate fraudulent ones from non-fraudulent ones), and on how well it can prioritize or rank the suspicious claims (i.e. finding claims with high adjustments first). Fig. 6 shows the Lorenz curve for the cumulative adjustments of the fraudulent claims. Detecting the top 1% of fraud claims would already yield more than 20% of the total adjustments, which underscores that prioritization is of crucial importance in our application.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//bc4b40b7-272a-4586-96b1-2a4f2bd69cd2/markdown_1/imgs/img_in_chart_box_336_114_753_406.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A21Z%2F-1%2F%2F0adfc5b188c12d91aaaf8e33dc8121315b58e8988daf64daea71308212c55792" alt="Image" width="38%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(a) Top 1%, i.e. 11 fraudulent claims</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//bc4b40b7-272a-4586-96b1-2a4f2bd69cd2/markdown_1/imgs/img_in_chart_box_95_468_514_764.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A21Z%2F-1%2F%2Fdf2700b41fd4d5fb50ca8f6e2e289512d8ea0ad4f48e6df0f44f9e35e6cb0aba" alt="Image" width="38%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(b) Top 5%, i.e. 57 fraudulent claims</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//bc4b40b7-272a-4586-96b1-2a4f2bd69cd2/markdown_1/imgs/img_in_chart_box_573_469_992_762.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A21Z%2F-1%2F%2F990cf540d7b84b7a58565bb18086586abf2e858f5e1a03a9c898385fc095fa17" alt="Image" width="38%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(c) Top 10%, i.e. 113 fraudulent claims</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 7. Fraction of Top Adjustments in Selected Set.</div> </div>


Fig. 7 shows how often we detect the top 1, 5, or 10% of fraudulent claims for different values of  $ N_{r} $. Prioritization based on our deep learning model performs better for all of these metrics. Fig. 7 also shows that the identification of fraudulent claims levels out after  $ N_{r} \approx 300 $. While this may indicate that we are missing some systematic frauds with our models, it could also be caused in part by random errors, such as unintentional upcoding, which we cannot separately identify in our labeled data and are generally hard to model due to their random nature. Randomly assigning claims to manual auditing is unable to detect a non-negligible fraction of the top frauds due to the low probability of fraudulent claims in our data in combination with the small set of top frauds we are looking for.

Suppose now that the claims are ranked based on their adjustment value such that i = 1 refers to the claim with the largest adjustment. The foregone cost savings of model m at every  $ N_{\tau} $ are then defined as

 $$ \begin{align*}\gamma_{N_{\tau}}=\pi_{N_{\tau}}^{\max}-\pi_{N_{\tau}}^{m}=&\sum_{i=1}^{N_{\tau}}a_{i}-\sum_{i=1}^{N}I(P_{i}^{m}>\tau_{m})a_{i}\\=&\sum_{i=1}^{N_{\tau}}I(P_{i}^{m}\leq\tau_{m})a_{i}+\sum_{i=1}^{N_{\tau}}I(P_{i}^{m}>\tau_{m})a_{i}-\sum_{i=1}^{N_{\tau}}I(P_{i}^{m}>\tau_{m})a_{i}-\sum_{i=N_{\tau}+1}^{N}I(P_{i}^{m}>\tau_{m})a_{i}\\=&\sum_{i=1}^{N_{\tau}}I(P_{i}^{m}\leq\tau_{m})a_{i}-\sum_{i=N_{\tau}+1}^{N}I(P_{i}^{m}>\tau_{m})a_{i},\end{align*} $$ 

where we used the fact that constant auditing costs per claim cancel out. The foregone cost savings comprise the losses from missing some of the top  $ N_\tau $ frauds and the cost reductions we yield by auditing less attractive claims instead, which includes auditing false positives ( $ a_i = 0 $). Fig. 8 depicts the cost savings ( $ \pi_N_\tau^m $) if we use deep learning (green line) or boosted trees (red line) to identify suspicious claims automatically. In Fig. 8(a), we use a constant cost parameter of  $ \tilde{c} $. Only 0.4% of the fraudulent claims offer an adjustment below  $ \tilde{c} $. Fig. 8(b) shows the results for a cost parameter that is twice

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//bc4b40b7-272a-4586-96b1-2a4f2bd69cd2/markdown_2/imgs/img_in_chart_box_89_114_542_430.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A22Z%2F-1%2F%2F81e12105943e9d2708408a543c28723034cc9095d951b5e76a88626635e3f187" alt="Image" width="41%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(a) Auditing costs  $ c = \bar{c} $</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//bc4b40b7-272a-4586-96b1-2a4f2bd69cd2/markdown_2/imgs/img_in_chart_box_553_114_1001_428.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A22Z%2F-1%2F%2Feeffdf677baf28cd7f795992ec9bb053844b869b8d60d55aa1cdaa5739109396" alt="Image" width="41%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(b) Auditing costs  $ c = 2\bar{c} $</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 8. Cost Savings for Boosted Trees and Deep Learning.</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//bc4b40b7-272a-4586-96b1-2a4f2bd69cd2/markdown_2/imgs/img_in_chart_box_316_534_777_870.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T15%3A00%3A23Z%2F-1%2F%2F9e0bac1f9a0327d0428cb6fa52ae206e1c5307b5dd70838e729925d04e2d612f" alt="Image" width="42%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 9. Claim Length Reduction using Attention Weights (fraudulent claims only).</div> </div>


as large. 17.8% of the fraudulent claims have an adjustment below 2€. The expected cost savings from randomly assigning claims to manual auditing are always negative because doing so leads to many costly false positives. We therefore do not illustrate them in Fig. 8. Instead we show the expected gains from an oracle that randomly draws from the subset of fraudulent claims (blue line). Assignments based on this oracle (C) benefit only from perfect classification of the fraudulent claims but completely fail with respect to the prioritization task. When we use the cost-sensitive loss, then both model-based assignments perform better than this oracle at the beginning of the path, which suggests that both models pay attention to the prioritization task. As reference we also add the results of boosted trees without cost-sensitive loss, which clearly fails in the prioritization. Oracle (C&P) benefits from both perfect classification and perfect prioritization of the fraudulent claims, which leads to  $ \pi_{N_r}^{max} $ depicted as black line in Fig. 8. The forgone savings are the differences in  $ \pi $ between this oracle and the model-based assignments. Our deep learning model clearly reduces the foregone savings compared to boosted trees for any value of  $ N_r $.

Neural attention has been a cornerstone in the development of many modern deep learning models. In our application, it not only increases the quality of predictions but also adds, with the estimation of the attention distribution, a potentially informative tool to the decision-support system. The attention weights shed light on the relevant claim items and may, additionally, provide meaningful explanations for the predictions. On average, a selection based on the attention weights being larger than 0.5 reduces the number of relevant claim items roughly by half. Fig. 9 shows a scatter plot of the original claim length and the length after screening.

The auditing unit will particularly benefit from the attention weights if these provide meaningful explanations, because then the weights can help elucidate which claim items are especially relevant for classifying a claim as being suspicious. Clearly, such information would speed up the subsequent (manual) auditing process. Therefore, meaningful explanations

would transform our model from a tool that is merely predictive to one that is prescriptive. An open research question, however, is the extent to which the obtained attention weights deliver meaningful insights into the relative importance of the inputs. Recent studies document mixed evidence on the reliability of the explanations provided by attention weights (Jain and Wallace, 2019; Jain et al., 2019; Vig and Belinkov, 2019; Vashishth et al., 2019). In a Monte Carlo simulation, we show that the attention weights can indeed recover the invalid claim items in a stylized setting (see Appendix B). Future research could explore whether it would be possible to use item-based labels in a real application to verify the selection based on the learned attention weights.

### 8. Conclusion

We outline basic similarities between the way that texts and health insurance claims are structured, and how these similarities allow deep learning techniques from text classification to be extended to the task of classifying claims. Claims management is a promising application for these methods outside of natural language processing or image analysis, and has real and quantifiable economic value. Methods based on neural networks can improve upon or even replace hand-designed features.

We develop a deep neural network that can be used to detect fraudulent claims automatically. It not only classifies claims but also delivers potentially meaningful explanations. Our model can handle data with inputs of varying length and variables with a large number of categories. As the digitalization of many aspects of our lives continues, very large amounts of unstructured data with characteristics similar to ours will become available, and it is therefore important for applied researchers to have such methods at their disposal.

Our proposed architecture can be used to mitigate informational asymmetries and accelerate subsequent auditing decisions. It outperforms default models on a large dataset from a private insurance company in Germany. A more comprehensive model can be built in a straightforward manner by incorporating additional input variables, such as information about health care providers or patients' medical histories. The empirical results substantiate the performance of deep learning as a data-driven tool in predictive analytics in claims management. Moreover, we demonstrate that our deep learning model not only adds another red flag but also gives additional insights into the fraud mechanisms themselves. We conduct a simulation study to assess their utility as a tool in prescriptive analytics. The simulations provide preliminary evidence that an attention model is able to deliver meaningful explanations of its predictions in claims management.

### Appendix A. Supplementary material

Supplementary material related to this article can be found online at https://doi.org/10.1016/j.jeconom.2020.05.021.

## References

Bahdanau, D., Cho, K., Bengio, Y., 2015. Neural machine translation by jointly learning to align and translate. In: 3rd International Conference on Learning Representations, ICLR 2015.

Bastani, H., Goh, J., Bayati, M., 2019. Evidence of upcoding in pay-for-performance programs. Manage. Sci. 65 (3), 1042–1060.

Becker, D., Kessler, D., McClellan, M., 2005. Detecting medicare abuse. J. Health Econ. 24 (1), 189–210.

Bolton, R.J., Hand, D.J., 2002. Statistical fraud detection: A review. Statist. Sci. 17 (3), 235–249.

Bond, E.W., Crocker, K.J., 1997. Hardball and the soft touch: the economics of optimal insurance contracts with costly state verification and endogenous monitoring costs. J. Public Econ. 63 (2), 239–264.

Breiman, L., 2001. Random forests. Mach. Learn. 45 (1), 5–32.

Breiman, L., Friedman, J.H., Olshen, R.A., Stone, C.J., 1984. Classification and Regression Trees. Wadsworth.

Cecchini M Avtu H Koehler G.I. Pathak P. 2010. Detecting management fraud in public companies. Manage. Sci. 56 (7), 1146–1160.

Cho, K., van Merriënboer, B., Bahdanau, D., Bengio, Y., 2014. On the properties of neural machine translation: Encoder-decoder approaches. In: Proceedings of SSST-8, Eighth Workshop on Syntax, Semantics and Structure in Statistical Translation, pp. 103–111.

Devlin, J., Chang, M.-W., Lee, K., Toutanova, K., 2019. Bert: Pre-training of deep bidirectional transformers for language understanding. Proc. NAACL-HLT 4171–4186.

Dionne, G., Giuliano, F., Picard, P., 2009. Optimal auditing with scoring: Theory and application to insurance fraud. Manage. Sci. 55 (1), 58–70.

Ekin, T., Ieva, F., Ruggeri, F., Soyer, R., 2018. Statistical medical fraud assessment: Exposition to an emerging field. Internat. Statist. Rev. 86 (3), 379–402.

Eldan, R., Shamir, O., 2016. The power of depth for feedforward neural networks. In: 29th Annual Conference on Learning Theory, pp. 901–940.

Fang, H., Gong, Q., 2017. Detecting potential overbilling in Medicare reimbursement via hours worked. Amer. Econ. Rev. 107 (2), 562–591.

Giacomini, R., Gottschling, A., Haefke, C., White, H., 2008. Mixtures of t-distributions for finance and forecasting. J. Econometrics 144 (1), 175–192.

Giorot, X., Bordes, A., Bengio, Y., 2011. Deep sparse rectifier neural networks. In: Proceedings of the 14th International Conference on Artificial Intelligence and Statistics, pp. 315–323.

Goodfellow, I., Bengio, Y., Courville, A., 2016. Deep Learning. MIT press.

Guo, C., Berkhahn, F., 2016. Entity embeddings of categorical variables. ArXiv preprint arXiv:1604.06737.

Heese, J., 2018. The role of overbilling in hospitals' earnings management decisions. Eur. Account. Rev. 27 (5), 875–900.

Hochreiter, S., Schmidhuber, J., 1997. Long short-term memory. Neural Comput. 9 (8), 1735–1780.

Hornik, K., Stinchcombe, M., White, H., 1989. Multilayer feedforward networks are universal approximators. Neural Netw. 2 (5), 359–366.

Jain, S., Mohammadi, R., Wallace, B.C., 2019. An analysis of attention over clinical notes for predictive tasks. In: Proceedings of the 2nd Clinical Natural Language Processing Workshop, pp. 15–21.

Jain, S., Wallace, B.C., 2019. Attention is not explanation. ArXiv preprint arXiv:1902.10186.

Kim, Y., 2014. Convolutional neural networks for sentence classification. In: Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing, EMNLP, pp. 1746–1751.

Kingma, D.P., Ba, J., 2014. Adam: A method for stochastic optimization. ArXiv preprint arXiv:1412.6980.

Kuan, C.-M., White, H., 1994. Artificial neural networks: An econometric perspective. Econometric Rev. 13 (1), 1–91.

Lai, S., Xu, L., Liu, K., Zhao, J., 2015. Recurrent convolutional neural networks for text classification. In: Twenty-Ninth AAAI Conference on Artificial Intelligence.

LeCun, Y., 1989. Generalization and network design strategies. In: Pfeifer, R., Schreter, Z., Fogelman-Soulié, F., Steels, L. (Eds.), Connectionism in Perspective. Elsevier Amsterdam, pp. 143–155.

Li, J., Huang, K.-Y., Jin, J., Shi, J., 2008. A survey on statistical methods for health care fraud detection. Health Care Manag. Sci. 11 (3), 275–287.

Ling, C.X., Sheng, V.S., 2010. Cost-sensitive learning. In: Sammut, C., Webb, G.I. (Eds.), Encyclopedia of Machine Learning. Springer US, Boston, MA, pp. 231–235.

Liou, F.-M., Tang, Y.-C., Chen, J.-Y., 2008. Detecting hospital fraud and claim abuse through diabetic outpatient services. Health Care Manag. Sci. 11(4), 353–358.

Luong, T., Pham, H., Manning, C.D., 2015. Effective approaches to attention-based neural machine translation. In: Proceedings of the 2015 Conference on Empirical Methods in Natural Language Processing, pp. 1412–1421.

McAleer, M., Medeiros, M.C., Slottje, D., 2008. A neural network demand system with heteroskedastic errors. J. Econometrics 147 (2), 359–371.

Medeiros, M.C., McAleer, M., Slottje, D., Ramos, V., Rey-Maquieira, J., 2008. An alternative approach to estimating demand: Neural network regression with conditional volatility for high frequency air passenger arrivals. J. Econometrics 147 (2), 372–383.

Mikolov, T., Chen, K., Corrado, G.S., Dean, J., 2013. Efficient estimation of word representations in vector space. ArXiv preprint arXiv:1301.3781.

Montúfar, G.F., Pascanu, R., Cho, K., Bengio, Y., 2014. On the number of linear regions of deep neural networks. In: Advances in Neural Information Processing Systems, vol. 27. pp. 2924–2932.

Mookherjee, D., Png, I., 1989. Optimal auditing, insurance, and redistribution. Q. J. Econ. 104 (2), 399–415.

Picard, P., 1996. Auditing claims in the insurance market with fraud: The credibility issue. J. Public Econ. 63 (1), 27–56.

Picard, P., 2013. Economic analysis of insurance fraud. In: Handbook of Insurance, Springer, pp. 349–395.

Rumelhart, D.E., Hinton, G.E., Williams, R.J., 1986. Learning representations by back-propagating errors. Nature 323 (6088), 533–536.

Schiller, I., 2006. The impact of insurance fraud detection systems. I. Risk Insurance 73 (3), 421–438.

Telgarsky, M., 2016. Benefits of depth in neural networks. In: 29th Annual Conference on Learning Theory, pp. 1517–1539.

Tennyson, S., Salsas-Forn, P., 2002. Claims auditing in automobile insurance: Fraud detection and deterrence objectives. J. Risk Insurance 69 (3), 289–308.

Townsend, R.M., 1979. Optimal contracts and competitive markets with costly state verification. J. Econom. Theory 21 (2), 265–293.

Urbanovich, E., Young, E.E., Puterman, M.L., Fattedad, S.O., 2003. Early detection of high-risk claims at the workers' compensation board of british columbia. Interfaces 33 (4), 15–26.

Van Vlasselaer, V., Eliassi-Rad, T., Akoglu, L., Snoeck, M., Baesens, B., 2017. Gotcha! Network-based fraud detection for social security fraud. Manage. Sci. 63 (9), 3090–3110.

Vashishth, S., Upadhyay, S., Tomar, G.S., Faruqui, M., 2019. Attention interpretability across NLP tasks. ArXiv preprint arXiv:1909.11218.

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, L., Polosukhin, I., 2017. Attention is all you need. In: Advances in Neural Information Processing Systems, vol. 30. pp. 5998–6008.

Viaene, S., Derrig, R.A., Baesens, B., Dedene, G., 2002. A comparison of state-of-the-art classification techniques for expert automobile insurance claim fraud detection. J. Risk Insurance 69 (3), 373–421.

Vig, J., Belinkov, Y., 2019. Analyzing the structure of attention in a transformer language model. In: Proceedings of the 2019 ACL Workshop BlackboxNLP: Analyzing and Interpreting Neural Networks for NLP, pp. 63–76.

Wager, S., Wang, S., Liang, P.S., 2013. Dropout training as adaptive regularization. In: Advances in Neural Information Processing Systems, vol. 26. pp. 351–359.

Xu, K., Ba, J., Kiros, R., Cho, K., Courville, A., Salakhudinov, R., Zemel, R., Bengio, Y., 2015. Show, attend and tell: Neural image caption generation with visual attention. In: Proceedings of the 32nd International Conference on Machine Learning, pp. 2048–2057.

