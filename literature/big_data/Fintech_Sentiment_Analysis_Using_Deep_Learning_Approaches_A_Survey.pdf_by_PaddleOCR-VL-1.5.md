# Fintech Sentiment Analysis using Deep Learning Approaches: a Survey

Sarah Anis

Faculty of Computer and Information Sciences

Ain-shams University

Cairo, Egypt

0000-0002-4337-4948

sarrahaniss@gmail.com

Mohamed Mabrouk Morsey

Faculty of Computer and Information Sciences

Ain-shams University

Cairo, Egypt

0009-0005-6181-9057

mohamed.mabrouk@cis.asu.edu.eg

Mostafa Aref

Faculty of Computer and Information Sciences

Ain-shams University

Cairo, Egypt

0000-0002-1278-0070

mostafa.aref@cis.asu.edu.eg

Abstract—The number of consumers who are eager to use mobile financial services for their daily financial activities has increased dramatically thanks to fintech (financial technology). The success of these applications is highly dependent on user feedback. Sentiment analysis is a powerful tool for learning about users' opinions towards various applications, including fintech services. Recent studies have shown that deep learning models offer a potential way to address the difficulties in sentiment analysis. This study provides a comprehensive study of the latest deep learning approaches applied for sentiment analysis in the financial sector. The aim of this study is to give scholars and academics a broad perspective on using deep learning approaches for fintech sentiment analysis. This paper additionally summarizes deep learning methods, their advantages and disadvantages, and recent challenges associated with sentiment analysis in fintech.

Keywords—Sentiment Analysis, Deep Learning, Fintech, Natural Language Processing.

## I. INTRODUCTION

Sentiment analysis is a technique used in natural language processing (NLP) to extract the emotions, opinions, and attitudes of customers from their texts, such as reviews, feedback, complaints, or social media posts. Sentiment analysis in fintech can help financial institutions understand how their customers feel about their services, features, or brand and use this information to improve customer experience, retention, loyalty, and satisfaction. Sentiment analysis can be performed at different levels of granularity, such as document, sentence, aspect, or entity level, and can use different methods and techniques, such as lexicon-based, machine learning-based, deep learning-based, or hybrid approaches. By analyzing customer emotions and opinions, fintech companies can gain valuable insights into their customer preferences, expectations, and satisfaction and take appropriate actions to meet their needs and expectations. Nowadays, the number of users of fintech and smart banking is growing exponentially [1]. Because of the competitive nature of this field, most fintech applications seek to provide the best experience to their users. To achieve this unique experience, automatic sentiment analysis is leveraged to classify user reviews of these services. The most accurate results can be obtained by using deep learning structures [2]. Deep learning has achieved state-of-the-art performance in many fields of research due to its ability to learn increasingly abstract data representations in a layer-wise manner [3].

In this paper, we attempt to provide a comparative analysis that covers the advantages and disadvantages of various deep learning methods applied for sentiment analysis in Section II. The rest of the paper is organized as follows: Section III presents the most recent work related to sentiment analysis in fintech and the challenges that are still going in this field. Lastly, the conclusion of the analysis and findings is covered in Section IV.

## II. BACKGROUND

### A. Deep Learning

Deep learning has been around since the 1940s [4]. It only seems new because, prior to its present popularity, deep learning was comparatively unpopular for several years. Deep learning is considered to be very effective for dealing with massive amounts of data. Through multi-level hierarchical learning, deep learning algorithms derive an abstract representation of big data [5]. Deep learning is also relevant for unsupervised feature learning, which means taking advantage of massive, unlabeled data for learning purposes.

Deep learning, which is simply a neural network with three or more layers, is a subset of machine learning. The main difference between deep learning and machine learning is the type of data it works on and the learning methods used. Deep neural networks consist of numerous layers of interconnected nodes, each of which enhances the classification or prediction provided by the layer that comes before it. The term "forward propagation" describes how computations propagate across a network. The input and output layers of a deep neural network are its visible layers. In the input layer, the deep learning model interprets the data, and in the output layer, the final prediction or classification is carried out [6]. Backpropagation is a different method that uses techniques such as gradient descent to calculate prediction errors before changing the function's weights and biases by iteratively going back through the layers in an effort to

train the model. A neural network can predict things thanks to forward propagation and backpropagation working together. This is how deep learning is described in its simplest form.

### B. Deep Learning Architectures

Convolutional neural networks (CNNs) use a deep learning network design that learns directly from input. Thus, it does not require human feature extraction. The three layers that make up CNNs are convolution, pooling, and fully linked layers, as shown in Fig. 1. They are quite good at identifying visual patterns that can be used to distinguish between items, people, and scenes. They are also useful for categorizing time series, sound, and signal data. The dense layer is connected directly. The commonly used optimization functions are "Adam" and "SoftMax."

CNNs, which are generally employed in computer vision and image classification applications, can find features and patterns in an image, making it possible to perform operations like object recognition or detection. While recurrent neural networks (RNNs), which make use of sequential or time series data, are frequently utilized in applications for speech and natural language recognition, RNNs take the input of the current phase as the output of the previous phase. Similarly, the input of the next phase is the output of the current phase, and so on. One advantage of RNNs is that the model size does not increase with the input size. Thus, RNNs can process inputs of any length.

Long Short-Term Memory (LSTM) has the capability to store information for long periods of time. The outputs from the LSTM can be fed as inputs to the current phase, thanks to RNNs' architecture. Due to its internal memory, the LSTM's output can remember prior inputs and use them as inputs in the current phase. On the other hand, a bidirectional LSTM (BiLSTM) is a type of model for sequence processing that consists of two LSTMs. One of which receives input going forward, while the other accepts input going backward. Using BiLSTM allows the network to access more data. The Bi-LSTM approach consists of two concurrent steps that communicate in simultaneously forward and backward segments to preserve dependability in two conditions, in contrast to the LSTM network. Reference [2] compared the performance of different deep learning techniques for sentiment classification from various Bangladesh mobile financial services. They used CNN, LSTM, and BiLSTM deep learning algorithms. Their results showed that BiLSTM generated better accuracy compared to CNN and LSTM since the input flows in both directions (backward and forward architectures).

Deep learning excels at unsupervised feature learning as well. The core principle of deep learning is what is known as greedy layer-wise unsupervised pre-training, which involves learning a hierarchy of characteristics one level at a time [7]. One of the unsupervised, pre-trained deep learning network architectures is autoencoders [8]. An autoencoder's initial layer is constructed as an encoding layer, which is then translated into a decoder. The unsupervised method is employed to train it to replicate the input. Autoencoders are mainly used in image processing, dimensionality reduction, and feature extraction.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//55443134-f008-40b3-9b20-f90db98ccac9/markdown_1/imgs/img_in_image_box_645_116_1125_351.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-31T08%3A09%3A01Z%2F-1%2F%2Fea65811a580106bbb6191ec326f7211e89fb3e9586d1e873ae96a43b3cd0ddd6" alt="Image" width="39%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 1. CNN's Model Architecture [9].</div> </div>


<div style="text-align: center;"><div style="text-align: center;">TABLE I. COMPARISON BETWEEN DIFFERENT DEEP LEARNING MODELS.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Model</td><td style='text-align: center; word-wrap: break-word;'>Applications</td><td style='text-align: center; word-wrap: break-word;'>Advantages</td><td style='text-align: center; word-wrap: break-word;'>Disadvantages</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CNN</td><td style='text-align: center; word-wrap: break-word;'>Semantic segmentation, Object detection, Image processing, Face recognition, Video analysis, Autonomous vehicles.</td><td style='text-align: center; word-wrap: break-word;'>Automatic feature extraction. Highly accurate for image processing. Minimizes computation. Efficient with large datasets.</td><td style='text-align: center; word-wrap: break-word;'>Needs large amount of labelled data. Interpretability challenges. Training takes longer time.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>RNN</td><td style='text-align: center; word-wrap: break-word;'>Time series prediction, Natural language processing, speech recognition, Machine translation.</td><td style='text-align: center; word-wrap: break-word;'>High accuracy. Sequential processing. Flexibility. Non-linear mapping. Ability to handle variable length sequences.</td><td style='text-align: center; word-wrap: break-word;'>Vanishing gradients. Difficulty in capturing long term dependencies. Computationally complex. Lack of parallelism.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>LSTM</td><td style='text-align: center; word-wrap: break-word;'>Language modelling, machine translation, handwriting recognition, question answering, video to text conversion.</td><td style='text-align: center; word-wrap: break-word;'>Handling long-term dependencies. Less risk to vanishing gradients. Efficient at modelling complex sequential data.</td><td style='text-align: center; word-wrap: break-word;'>Temporal dependencies. Needs large training dataset. Not suitable for online learning tasks. Does not perform well with noisy data.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>BiLSTM</td><td style='text-align: center; word-wrap: break-word;'>Speech recognition, text classification, text translation.</td><td style='text-align: center; word-wrap: break-word;'>Powerful tool for modeling the temporal dependencies in LSTM.</td><td style='text-align: center; word-wrap: break-word;'>Higher time complexity. Longer training time.</td></tr></table>

### C. Deep Learning Methods

This section discusses some of the potent methods that can be applied to deep learning algorithms to shorten training times

and optimize models. A comparison between these methods is conducted and summarized in Table II.

- Backpropagation is simply a method of returning the total loss to the neural network in order to determine how much of the loss each node is responsible for and then changing the weights to give lower weights to the nodes with higher error rates and vice versa in order to minimize the loss. Backpropagation can be used to calculate the gradient of the function for each iteration [10]. Backpropagation is a standard method that works well in most cases because of its high adaptability and efficiency.

- Stochastic Gradient Descent (SGD), due to the high cost of running backpropagation over the entire training set, can reduce this expense and yet result in rapid convergence. It is used to identify the model parameters that best match the correlation between expected and actual results. Depending upon the values of the function and learning rate, the convex function in gradient descent algorithms may find an optimal minimum [11].

- Learning rate decay is used to gradually slow down the learning process. This enables the network to take huge initial steps and then fine-tune as it gets closer to the optimal point, which can help the network converge faster and more precisely. This allows fine-tuning the weights in the later stages. Empirically, it is seen to support both generalization and optimization [12].

- The dropout method can be used to solve the overfitting issue in deep neural networks. This technique involves dropping units and their connections at random as they are being trained to ensure that there are no units that are codependent on one another [13]. Dropout provides a powerful regularization technique that can lower overfitting and enhance generalization error.

- Max pooling is a down-sampling method in which a specified filter is used, and this filter is then applied across the non-overlapping sub-regions of the input, taking the maximum of the values found in the region as the output. Consequently, the most relevant features are retained. It is used to reduce dimensionality as well as computational costs [14].

- Batch normalization is used to accelerate deep neural networks because it reduces the covariate shift. When the weights are changed during training, it normalizes the inputs to a layer for each mini-batch. Normalization decreases training epochs while stabilizing the learning process. A neural network's stability can be improved by normalizing the output from the preceding activation layer [15].

skipping one of them during training, and then using the model to predict the skipped term [16].

- Skip-gram is used for modeling word embeddings. Two vocabulary phrases that are similar in context and are then identical are described by the skip-gram model. It is trained using a significant amount of unstructured text data and is capable of capturing context and semantic similarity between words. Implementing a skip-gram can be done by using a context window with n terms,

- Transfer learning is based on the idea that a model that has been trained for one task can be used for another task that is related. The network that will be trained on a comparable topic can benefit from the knowledge gained while tackling a specific problem. This enables the second problem to be solved quickly and with improved performance [17].

<div style="text-align: center;"><div style="text-align: center;">TABLE II. COMPARISON BETWEEN DIFFERENT DEEP LEARNING METHODS.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Method</td><td style='text-align: center; word-wrap: break-word;'>Advantages</td><td style='text-align: center; word-wrap: break-word;'>Disadvantages</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Backpropagation</td><td style='text-align: center; word-wrap: break-word;'>Simple and Fast.Does not need parameter tuningFlexible.</td><td style='text-align: center; word-wrap: break-word;'>Performancedependson theinput data.Sensitive to noise.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>SGD</td><td style='text-align: center; word-wrap: break-word;'>Faster convergence.Computationallyefficient.Ease ofimplementation.</td><td style='text-align: center; word-wrap: break-word;'>Noisy updatesmaking theoptimizationprocess less stable.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Dropout</td><td style='text-align: center; word-wrap: break-word;'>Reduces overfitting.Faster convergence.Better performancein case of limited training data.</td><td style='text-align: center; word-wrap: break-word;'>Longer training time.Difficulty in tuning.Hyper-Parameters.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Learning Rate Decay</td><td style='text-align: center; word-wrap: break-word;'>Improves the learning forcomplex patterns.Helps both optimization and generalization.</td><td style='text-align: center; word-wrap: break-word;'>Highercomputational cost.Longer training time.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Max Pooling</td><td style='text-align: center; word-wrap: break-word;'>Helps in solvingoverfitting problem.Parameter reduction.Removinginvariances.</td><td style='text-align: center; word-wrap: break-word;'>Expensive training.More Hyper-Parameters.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>BatchNormalization</td><td style='text-align: center; word-wrap: break-word;'>Leads to Faster and more stableconvergence.Reduces training time.Tolerant to different learning rates andinitial weights.Helps in generalization and performance.</td><td style='text-align: center; word-wrap: break-word;'>Not suitable foronline learning.Unstable when on small batch sizes.Computationally expensive.Dependent on the batch size.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Skip-gram</td><td style='text-align: center; word-wrap: break-word;'>uses less memorycompared to other vectorrepresentations.Considers the surrounding words that appear with a certain word.Scalable.</td><td style='text-align: center; word-wrap: break-word;'>Higher training time.Requires huge number of training data.Computationally expensive.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Transfer Learning</td><td style='text-align: center; word-wrap: break-word;'>Does not require a lot of data.Saves time and resources.Better performance in most cases.</td><td style='text-align: center; word-wrap: break-word;'>Domain mismatch.Overfitting issueswhen trained on small datasetsLimited flexibility</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Negative transfer problem</td></tr></table>





## III. RELATED WORK

This section compares the most recent work on sentiment analysis in the field of fintech. The details are listed in Table III. We discovered that deep learning has the ability to achieve high classification accuracy and outperform other approaches. Recently, stock market prediction has gained popularity and attracted the interest of many researchers in this field [18]. Based on our study, CNN and LSTM were the most used approaches for sentiment classification in fintech. However, there are several challenges associated with the process of sentiment analysis in fintech, including data privacy and algorithmic transparency [19]. Lack of publicly available datasets [20], is one of the primary obstacles facing academics in the financial sector, forcing them to rely on their own collected data for analysis [2]. Some of the available datasets for sentiment analysis in the field of fintech are included in Table III. Generally, user-generated content used for sentiment analysis may contain a lot of noise and inconsistencies that can affect the performance of the model, especially when dealing with large amounts of data. Moreover, existing applications that are created for a particular market or time period might not be applicable to other financial markets or periods of time [21].

<div style="text-align: center;"><div style="text-align: center;">TABLE III. SUMMARY OF RECENT RELATED WORK.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Year</td><td style='text-align: center; word-wrap: break-word;'>Study</td><td style='text-align: center; word-wrap: break-word;'>Research Work</td><td style='text-align: center; word-wrap: break-word;'>Method</td><td style='text-align: center; word-wrap: break-word;'>Dataset</td><td style='text-align: center; word-wrap: break-word;'>Target</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2024</td><td style='text-align: center; word-wrap: break-word;'>Abdelfattah BA, Darwish SM, Elkaffas SM [18]</td><td style='text-align: center; word-wrap: break-word;'>Stock market movement prediction</td><td style='text-align: center; word-wrap: break-word;'>Neutrosophic-Logic-Rule-Based Classification &amp; LSTM</td><td style='text-align: center; word-wrap: break-word;'>StockNet</td><td style='text-align: center; word-wrap: break-word;'>To detect data uncertainty and ambiguous opinions and to improve prediction accuracy.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2024</td><td style='text-align: center; word-wrap: break-word;'>Meher BK, Singh M, Birau R, Anand A [21]</td><td style='text-align: center; word-wrap: break-word;'>Predicting the stock values of Indian fintech companies</td><td style='text-align: center; word-wrap: break-word;'>Random Forest model with high-frequency data.</td><td style='text-align: center; word-wrap: break-word;'>www.moneycontrol.com and www.kotaksecurities.com</td><td style='text-align: center; word-wrap: break-word;'>To formulate stock forecasting models for top three fintech Companies of India</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2024</td><td style='text-align: center; word-wrap: break-word;'>Rizinski M, Peshov H, Mishev K, Jovanovic M, Trajanov D [22]</td><td style='text-align: center; word-wrap: break-word;'>Sentiment analysis in finance</td><td style='text-align: center; word-wrap: break-word;'>eXplainable Lexicons (XLex)</td><td style='text-align: center; word-wrap: break-word;'>Sentfin Fiqa Sem_eval Financial PhraseBank NASDAQ</td><td style='text-align: center; word-wrap: break-word;'>Enhance word coverage and increase classification accuracy</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2023</td><td style='text-align: center; word-wrap: break-word;'>Eachempati P, Srivastava PR [23]</td><td style='text-align: center; word-wrap: break-word;'>Stock market prediction using linguistic phrases</td><td style='text-align: center; word-wrap: break-word;'>FINBERT based neural network</td><td style='text-align: center; word-wrap: break-word;'>India&#x27;s National Stock Exchange (NSENIFTY50 Index) and Emerging Markets Information System (EMIS) database</td><td style='text-align: center; word-wrap: break-word;'>Enhance the stock market prediction</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2023</td><td style='text-align: center; word-wrap: break-word;'>Al Ryan A, Mahmud MS, Mahi HH, Hossen MS, Shimul NI, Noori SR [2]</td><td style='text-align: center; word-wrap: break-word;'>Sentiment classification from Bangladeshi mobile financial services</td><td style='text-align: center; word-wrap: break-word;'>CNN, LSTM, and BiLSTM</td><td style='text-align: center; word-wrap: break-word;'>Data is collected from Google Play Store</td><td style='text-align: center; word-wrap: break-word;'>Sentiment classification of user reviews on different mobile fintech apps</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2022</td><td style='text-align: center; word-wrap: break-word;'>Palle RR, Yennapusa H, Kathala KC [24]</td><td style='text-align: center; word-wrap: break-word;'>Vulnerability Prediction in fintech</td><td style='text-align: center; word-wrap: break-word;'>modified barnacles mating optimization (MBMO) and general regressive artificial neural network (GR-ANN)</td><td style='text-align: center; word-wrap: break-word;'>ScrawlD-real Ethereum smart contract benchmark dataset</td><td style='text-align: center; word-wrap: break-word;'>enhance the accuracy of vulnerability detection in fintech applications</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2022</td><td style='text-align: center; word-wrap: break-word;'>Utami SH, Purnama AA, Hidayanto AN, Utami SH, Purnama AA, Hidayanto AN [25]</td><td style='text-align: center; word-wrap: break-word;'>Sentiment analysis for fintech lending using twitter data</td><td style='text-align: center; word-wrap: break-word;'>K Nearest Neighbor (KNN), Stochastic Gradient Descent (SGD), Neural Network (NN), Logistic Regression (LR), Naïve Bayes (NB), Random Forest (RF), and Adaptive Boosting (AdaBoost).</td><td style='text-align: center; word-wrap: break-word;'>twitter</td><td style='text-align: center; word-wrap: break-word;'>Finding the best model for sentiment analysis using machine learning algorithms</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2022</td><td style='text-align: center; word-wrap: break-word;'>Issam A, Mounir AK, El Mendili Saida EM [26]</td><td style='text-align: center; word-wrap: break-word;'>Financial sentiment analysis of tweets</td><td style='text-align: center; word-wrap: break-word;'>Convolutional Neural Network (CNN) and Latent Dirichlet Allocation (LDA)</td><td style='text-align: center; word-wrap: break-word;'>twitter</td><td style='text-align: center; word-wrap: break-word;'>Detection of financial and non-financial tweets</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2022</td><td style='text-align: center; word-wrap: break-word;'>Wang H, Chen X, Du J, Lai KK [27]</td><td style='text-align: center; word-wrap: break-word;'>classification of Chinese fintech patents</td><td style='text-align: center; word-wrap: break-word;'>Character-level CNN model and BERTmodel</td><td style='text-align: center; word-wrap: break-word;'>fintech data released by the China National Intellectual Property Administration</td><td style='text-align: center; word-wrap: break-word;'>Classify massive Chinese fintech patents data and categorize fintech innovations.</td></tr></table>

## IV. Conclusion

This paper explored the foundations of deep learning models and related techniques that have been applied to fintech sentiment analysis. We have compared several deep learning architectures, outlining their advantages and disadvantages. The commonly used algorithms that are deployed for deep learning model optimization were discussed and compared. We've additionally addressed current research in this area. With the aid of this data and our comparative analysis, scholars can gain a general knowledge of sentiment analysis's application in fintech. It also offers an in-depth perspective on sentiment analysis using deep learning techniques. Finally, the major pitfalls and challenges that arise when utilizing financial data for sentiment analysis were covered.

In future work, we will focus on investigating and evaluating combined different deep learning approaches and methodologies for financial sentiment analysis. In addition, we aim to address the challenges discussed and extend the comparative analysis to incorporate additional techniques and data types.

## REFERENCES

[1] Poromatikul C, De Maeyer P, Leelapanyalert K, Zaby S, "Drivers of continuance intention with mobile banking apps," International Journal of Bank Marketing, vol. 38, no. 1, pp. 242-262, 2020.

[2] Al Ryan A, Mahmud MS, Mahi HH, Hossen MS, Shimul NI, Noori SR, "FinTech: Deep Learning-Based Sentiment Classification of User Reviews from Various Bangladeshi Mobile Financial Services," in International Conference on Computational Intelligence in Data Science (pp. 126-140), Cham: Springer Nature Switzerland, 2023.

[3] Li B, Xu Z, "Insights into financial technology (FinTech): a bibliometric and visual study," Financial innovation, no. 7, pp. 1-28, 2021.

[4] Hohman F, Kahng M, Pienta R, Chau DH. , "Visual analytics in deep learning: An interrogative survey for the next frontiers," IEEE transactions on visualization and computer graphics, vol. 25, no. 8, pp. 2674-2693, 2018.

[5] W. D. P. A. K. T. Sohangir S., "Big Data: Deep Learning for financial sentiment analysis," Journal of Big Data, vol. 5, no. 1, pp. 1-25, 2018.

[6] [Online]. Available: https://www.ibm.com/topics/deep-learning..

[7] Huang SC, Wu CF, Chiou CC, Lin MC, "Intelligent FinTech data mining by advanced deep learning approaches," Computational economics, pp. 1-6, 2021.

[8] Mathew A, Amudha P, Sivakumari S, "Deep learning techniques: an overview," in Advanced Machine Learning Technologies and Applications: Proceedings of AMLTA 2020. (599-608), 2021.

[9] B. S., "Binary Image classifier CNN using TensorFlow–Techiepedia–Medium," 29 Aug 2020. [Online]. Available: Techiepedia. [Accessed 2024].

[10] Panigrahi A, Chen Y, Kuo CC, "Analysis on gradient propagation in batch normalized residual networks," arXiv preprint arXiv:1812.00342., 2018.

[11] P. Netrapalli, "Stochastic Gradient Descent and Its Variants in Machine Learning," Journal of the Indian Institute of Science, vol. 99, p. 201–213, 2019, https://doi.org/10.1007/s41745-019-0098-4.

[12] "HOW DOES LEARNING RATE DECAY HELP MODERN NEURAL NETWORKS?", 2020. [Online]. Available: https://openreview.net/. [Accessed 2023].

[13] P. Marimuthu, "Dropout Regularization in Deep Learning," 2022. [Online]. Available: https://www.analyticsvidhya.com/.

[14] Hossein Gholamalinezhad, Hossein Khosravi, "Pooling Methods in Deep Neural Networks, a Review," in arXiv:2009.07485 Search..., 2020.

[15] Szegedy, Sergey Ioffe and Christian, "Batch normalization: Accelerating deep network training by reducing internal covariate shift.", in arXiv preprint arXiv:1502.03167, 2015.

[16] Samar AlSaqqa, Arafat Awajan, "The Use of Word2vec Model in Sentiment Analysis: A Survey," in AIRC '19: Proceedings of the 2019 International Conference on Artificial Intelligence, Robotics and Control, 2019.

[17] Yang., Sinno Jialin Pan and Qiang, "A survey on transfer learning," IEEE Transactions on knowledge and data engineering, vol. 22, no. 10, p. 1345–1359, 2009.

[18] Abdelfattah BA, Darwish SM, Elkaffas SM, "Enhancing the Prediction of Stock Market Movement Using Neutrosophic-Logic-Based Sentiment Analysis," Journal of Theoretical and Applied Electronic Commerce Research, vol. 19, no. 1, pp. 116-134, 2024.

[19] S. Ahmadi, "A Comprehensive Study on Integration of Big Data and AI in Financial Industry and its Effect on Present and Future Opportunities," International Journal of Current Science Research and Review, vol. 7, no. 1, 2024.

[20] Chung Chi Chen, Hen-Hsen Huang, Hsin-Hsi Chen, "NLP in FinTech Applications: Past, Present and Future," arXiv preprint arXiv:2005.01320, 2020.

[21] Meher BK, Singh M, Birau R, Anand A, "Forecasting stock prices of fintech companies of India using random forest with high-frequency data," Journal of Open Innovation: Technology, Market, and Complexity, vol. 10, no. 1, pp. 100-180, 2024.

[22] Rizinski M, Peshov H, Mishev K, Jovanovik M, Trajanov D, "Sentiment Analysis in Finance: From Transformers Back to eXplainable Lexicons (XLex)," IEEE Access, 2024.

[23] Eachempati P, Srivastava PR, "Prediction of the Stock Market From Linguistic Phrases: A Deep Neural Network Approach," Journal of Database Management (JDM), vol. 34, no. 1, pp. 1-22, 2023.

[24] Palle RR, Yennapusa H, Kathala KC, "Enhancing Cloud-Based Smart Contract Security: A Hybrid AI and Optimization Approach for Vulnerability Prediction in FinTech.", 2022.

[25] Utami SH, Purnama AA, Hidayanto AN, Utami SH, Purnama AA, Hidayanto AN, "Fintech Lending in Indonesia: A Sentiment Analysis, Topic Modelling, and Social Network Analysis using Twitter Data," International Journal of Applied Engineering & Technology, vol. 4, no. 1, pp. 50-56, 2022.

[26] Issam A, Mounir AK, El Mendili Saida EM, " Financial sentiment analysis of tweets based on deep learning approach," Indonesian Journal of Electrical Engineering and Computer Science, vol. 25, no. 3, pp. 1759-1770, 2022.

[27] Wang H, Chen X, Du J, Lai KK, "Classification of FinTech Patents by Machine Learning and Deep Learning Reveals Trends of FinTech Development in China," Mathematical Problems in Engineering, 2022.

