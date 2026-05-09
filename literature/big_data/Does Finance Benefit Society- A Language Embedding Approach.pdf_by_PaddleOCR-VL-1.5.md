# Does Finance Benefit Society? A Language Embedding Approach

Manish Jha

Georgia State University, USA

Hongyi Liu

Washington University in St. Louis, USA

#### Asaf Manela

Washington University in St. Louis, USA

We measure popular sentiment toward finance by applying a large language model to millions of books published in eight countries over hundreds of years. We extensively validate this measure both internally and externally. We document persistent differences in finance sentiment across countries despite ample time-series variation. Books written in the languages of more capitalist countries discuss finance in a more positive context. Finance sentiment is correlated with survey-based measures of financial market participation and income inequality. Finance sentiment declines one year before rather than after financial crises. Positive shocks to finance sentiment are followed by higher output and credit growth. (JEL G15, C82, E44, G52, N40)

Received: July 19, 2023; Editorial decision: November 5, 2024

Editor: Clemens Sialm

Authors have furnished an Internet Appendix, which is available on the Oxford University Press Web site next to the link to the final published paper online..

As finance academics, we should care deeply about the way the financial industry is perceived by society. Not so much because this affects our own reputation, but because there might be some

truth in all these criticisms, truths we cannot see because we are too embedded in our own world. And even if we thought there were no truth, we should care about the effects that this reputation has in shaping regulation and government intervention in the financial industry. Last but not least, we should care because the positive role that finance can play in society depends on the public's perception of our industry.

(Zingales 2015, AFA Presidential Address)

Positive popular sentiment toward finance can spread its benefits widely, while suspicion toward financial services can restrict credit, risk sharing, and competition (Zingales 2012, 2015). Survey evidence reveals that trust in finance fell following the 2008 financial crisis (Sapienza and Zingales 2012), that such public perceptions often diverge from those of economists (Sapienza and Zingales 2013; Goetzmann, Kim, and Shiller 2016), and that low trust can hinder insurance market efficiency (Gennaioli et al. 2022). The recency of survey data limits our understanding of how finance sentiment changes over time and differs across countries. Although we cannot survey people who lived during the 20th century, books allow us to travel through time and across borders and to study public perceptions about the benefits of finance to society.

We measure popular sentiment toward finance in an annual panel covering eight large economies from 1870 to 2009, using a computational linguistics approach applied to the text of millions of books. Our finance sentiment index relies on a recently developed large language model (BERT, Devlin et al. 2018) to measure whether references to finance are, on average, semantically closer to positive or negative sentences. BERT and its offspring have shattered records on multiple natural language processing tasks, surpassing human ability in many.

We use BERT to embed sentences into relatively low-dimensional numerical vectors. Following Kozlowski, Taddy, and Evans (2019), we measure the angle between the embedding of sentences mentioning “finance” and the “positive” minus “negative” dimension. This approach goes beyond the dictionary or bag-of-words approach to sentiment analysis (Zhou 2018) by capturing not only whether a book excerpt is positive or negative, but also the degree to which the context of the word “finance” is positive. By aggregating this positivity angle for all finance-mentioning sentences in each language and in each year, we construct a novel finance sentiment panel.

We extensively validate this measure both internally and externally. We find that the most negative and most positive sentences identified by our method indeed put finance in its expected context. Furthermore, the most salient changes in finance sentiment for the different languages coincide with major historical events such as civil wars and regime changes. Looking for external sources of validation, we find that finance sentiment correlates positively with direct measures of financial market participation based on survey and national

accounts data and negatively with indirect measures like income inequality. Finally, as a placebo, we replicate our measure for other industries with a long history. We find that sentiment toward the paper, coal, and tobacco industries shows no clear upward trend, rises and falls at different times, and exhibits a different ordering across languages.

We find highly persistent differences in finance sentiment across languages. Russian finance sentiment is lowest by far throughout our long sample, followed by German, Italian, Chinese, French, and Spanish, with British and American English at the top. Despite considerable within-country variation, this ordering persists throughout our sample, with the exception of British English finance sentiment, which is slightly higher than American English sentiment until 1912, and slightly lower thereafter.

Generally, books written in languages of more capitalist countries tend to discuss finance in a more positive context. We find that countries with a more right-leaning government, with citizens who prefer private rather than public ownership of business, and where registering a business is easier, all exhibit higher finance sentiment. These facts provide validation that text-based finance sentiment works as expected. But at the same time, these measures of capitalism explain only a modest share of the variation in finance sentiment, suggesting there is more to it than attitudes toward capitalism.

Interestingly, Chinese finance sentiment is about as positive as the French one, though more volatile. Chinese sentiment drops sharply in 1971 as uncertainty associated with the sociopolitical movements led by Mao Zedong rises. However, it rebounds substantially the following year after the United Nations recognizes the People's Republic of China as "the only legitimate representative of China" and following President Nixon's visit to China. Other significant changes in sentiment coincide with major historical events, like wars and revolutions.

Having described and validated our measure of finance sentiment, we relate it to financial crises and to macroeconomic fundamentals, and document two new empirical facts. The first is that finance sentiment drops one year before periods of banking distress, as defined by Baron, Verner, and Xiong (2021), but remains relatively flat in their aftermath. Consistent with the idea that a deterioration of sentiment toward finance can transform a mild recession into a severe financial crisis (Sapienza and Zingales 2012), we find that declines in finance sentiment predict a higher probability of banking distress in the following year, even after controlling for lags of credit growth, which has been shown to rise two years before such crises (Schularick and Taylor 2012). Note that delays in the publication of books would strengthen the finding that changes in financial sentiment precede periods of banking distress. However, as discussed in Section 5.1, these publication lags are likely modest, typically lasting less than a year.

The second fact is that shocks to finance sentiment lead to higher future output and credit growth. We estimate impulse responses to finance sentiment

shocks on GDP growth using local projections (Jordà 2005). We study GDP growth, an imperfect measure of economic well-being, simply because it is available for all countries in our panel. We find that a 1% improvement in finance sentiment leads to a gradual and persistent increase in GDP growth of about 20 basis points in each of the 10 years following the shock. For a subset of countries that excludes China and Russia, we can include credit growth in the local projections. We find that some, but not all, of the positive effects of finance sentiment on output growth can be attributed to its positive effect on credit growth.

To the extent that these impulse responses identify a causal effect of finance sentiment, they suggest that positive public perceptions of the financial sector indeed benefit society as Zingales (2015) postulates. But macroeconomic turning points could also affect finance sentiment or be jointly determined by other socioeconomic changes, as we discuss in Section 6. In subsequent work, we analyze how finance sentiment responds to plausibly exogenous natural disasters (Jha, Liu, and Manela 2021). We find that finance sentiment declines after epidemics and earthquakes, but rises following severe droughts, floods, and landslides. These heterogeneous effects of natural disasters suggest finance sentiment responds differently to the realization of insured versus uninsured risks.

Our paper relates to recent work on the measurement of public attitudes toward the financial sector. Stulz and Williamson (2003) finds that a country's language and religion predict its creditor rights. Guiso, Sapienza, and Zingales (2008) finds that a general lack of trust reduces stock market participation. Giannetti and Wang (2016) documents that after the revelation of corporate fraud in a state, household participation and trust in the stock market decrease. Gurun, Stoffman, and Yonker (2018) finds that communities indirectly exposed to a Ponzi scheme withdraw assets from investment advisers. D'Acunto, Prokopczuk, and Weber (2019) finds that present-day demand for finance is lower in German counties where historical antisemitism (and therefore distrust of finance) was higher. Levine, Lin, and Xie (2020) links the African slave trade to household demand and trust in financial services. We contribute to this work by providing a novel measure of sentiment toward finance that spans over a century and several large economies, and by documenting how finance sentiment relates to financial crises and economic and credit growth.

A broader related literature considers the measurement of culture and its effects on economic outcomes (Guiso, Sapienza, and Zingales 2006). Cultural differences can persist for generations (Spolaore and Wacziarg 2013). Changes in culture, ideas, and, in particular, language, have been tied to the dramatic enrichment the world experienced starting in the 19th century (Mokyr 2016; McCloskey 2016). Our finding that finance sentiment drops before financial distress supports the idea that changes in language and in sentiment toward productive parts of society have important effects on economic growth.

A recent increase in the availability of textual data has prompted great interest in its use for the analysis of culture (Michel et al. 2011), and of economics and finance (Gentzkow, Kelly, and Taddy 2019; Loughran and McDonald 2020). Although this literature has yet to study sentiment toward finance or any particular sector, textual analysis has been used to analyze partisanship (Gentzkow and Shapiro 2010; Luo, Manconi, and Massa 2023; Goldman, Gupta, and Israelsen 2024; Engelberg et al. 2023; Cookson, Engelberg, and Mullins 2022), product markets (Hoberg and Phillips 2016; Chen and Sarkar 2020), central bank communication (Hansen, McMahon, and Prat 2018; Cieslak and Vissing-Jorgensen 2020), corporate culture (Grennan 2019), asset market sentiment (Antweiler and Frank 2004; Tetlock 2007; García 2013; Soo 2018; Ke, Kelly, and Xiu 2019), employee expectations (Sheng 2019), financial constraints (Bodnaruk, Loughran, and McDonald 2015), media narratives (Dim, Sangiorgi, and Vilkov 2023; Goetzmann, Kim, and Shiller 2022), subjective well-being (Hills et al. 2019), uncertainty (Baker, Bloom, and Davis 2016; Manela and Moreira 2017; Goetzmann, Kim, and Shiller 2017; Hassan et al. 2019; Boudoukh et al. 2018), firm-identified risks (Hanley and Hoberg 2019; Lopez Lira 2023), emerging technologies (Chava, Du, and Paradkar 2021), and the link between business news and business cycles (Bybee et al. 2024).

While early work relied on simple word counts (the bag-of-words approach), recent work, starting with Mikolov et al. (2013) shows that using neural networks to embed words in vector spaces improves the performance of learning algorithms in natural language-processing tasks. Kozlowski, Taddy, and Evans (2019) demonstrate that such word embeddings produce richer insights into cultural associations and categories than prior methods. Our work builds and improves on their methodology by using a pre-trained large language model designed to capture context (BERT), both to embed sentences mentioning our object of interest (finance) and to define the dimension on which we project these embeddings (positive – negative). This “transfer learning” approach lowers both estimation error and computation costs. It can be broadly applied to measure sentiment toward other concepts (e.g., industries), and can leverage future language models that may produce more accurate embeddings (e.g., OpenAI 2024, GPT-4).

## 1. Text-Based Sentiment Toward Finance

In this section, we describe our text data and how we measure a language's sentiment toward finance across time. For each language and year, we start with a sample of finance-mentioning sentences published in the language and year. Next, we measure the degree to which each sentence places finance in a positive context. We then aggregate these scores to an average finance sentiment that reflects the mean sentiment toward finance of books written in the language in that year.

We assume throughout that the choice of words used by book authors, magazine publishers, and journalists whose work is archived in libraries reflects the sentiment of the average denizen of that language during the time, or at least that of an influential literary elite. For example, in our data set, the sentence “correcting corruption or financial malpractice” appears first in 1951, and then appears every year after 1959. The sentence was part of the 1959 U.S. labor-management reform legislation hearings, when correcting corruption or financial malpractice became an allowable purpose for establishing a trusteeship by labor unions. Hence, “financial malpractice” is used more frequently in subsequent legal documents and books. The context for the word “financial” here is clearly negative. In this particular case, we assume that the labor unions in particular, and the U.S. English-speaking public in general, are more likely to associate finance with malpractice around that time.

### 1.1 Textual data

Our text data includes five-word sentences (5-grams) containing the stem of the word "finance" in eight languages, between 1870 and 2009, extracted from the 2012 edition of the Google Books Ngram Corpus (Michel et al. 2011; Lin et al. 2012). The corpus consists of words and phrases and their annual usage frequency from 1500 to 2009. The data come from Google scans of over 8 million books or 6% of all books ever published in American English, British English, Simplified Chinese, French, German, Italian, Russian, and Spanish. $ ^{1} $ Jha, Liu, and Manela (2021) finds that the lag between severe disasters and their mention in the Google Books Ngram Corpus is less than a year. This is likely due to the inclusion of regular government reports and serial publications in the corpus.

Although the original data also provide lower complexity n-gram counts, we focus on 5-grams because for sentiment analysis, especially with BERT, a word's context is essential. We start our study in 1870 (Google Books corpora are available from 1500) because beginning in that year we have more confidence in the accuracy of our macro-data. Moreover, the number of sentences is relatively modest earlier in time, and features fewer mentions of finance before 1870, which would increase the measurement error of our sentiment index.

We preprocess the Book Corpus by stripping case, symbols, double spaces, part-of-speech tags, and positional tags. Next, we extract all sentences mentioning the stem of the word for finance. The finance stem word is different across languages, as listed in Table 1. We use the word stem “financ” for English to include sentences that contain either “finance” or “financial.” Similarly, for other languages, we use a word stem common to the different

<div style="text-align: center;"><div style="text-align: center;">Table 1 Finance mentions across languages</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Language</td><td style='text-align: center; word-wrap: break-word;'>Finance word stem</td><td style='text-align: center; word-wrap: break-word;'>Unique sentences</td><td style='text-align: center; word-wrap: break-word;'>Total sentences</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American English</td><td style='text-align: center; word-wrap: break-word;'>financ</td><td style='text-align: center; word-wrap: break-word;'>220k</td><td style='text-align: center; word-wrap: break-word;'>79m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>British English</td><td style='text-align: center; word-wrap: break-word;'>financ</td><td style='text-align: center; word-wrap: break-word;'>48k</td><td style='text-align: center; word-wrap: break-word;'>15m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Simplified Chinese</td><td style='text-align: center; word-wrap: break-word;'>金融, 金融, 金_融</td><td style='text-align: center; word-wrap: break-word;'>196k</td><td style='text-align: center; word-wrap: break-word;'>305m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>French</td><td style='text-align: center; word-wrap: break-word;'>financ</td><td style='text-align: center; word-wrap: break-word;'>100k</td><td style='text-align: center; word-wrap: break-word;'>43m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>German</td><td style='text-align: center; word-wrap: break-word;'>finanz</td><td style='text-align: center; word-wrap: break-word;'>28k</td><td style='text-align: center; word-wrap: break-word;'>7m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Italian</td><td style='text-align: center; word-wrap: break-word;'>finanz</td><td style='text-align: center; word-wrap: break-word;'>23k</td><td style='text-align: center; word-wrap: break-word;'>9m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Russian</td><td style='text-align: center; word-wrap: break-word;'>финаH</td><td style='text-align: center; word-wrap: break-word;'>187k</td><td style='text-align: center; word-wrap: break-word;'>250m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Spanish</td><td style='text-align: center; word-wrap: break-word;'>finan</td><td style='text-align: center; word-wrap: break-word;'>89k</td><td style='text-align: center; word-wrap: break-word;'>33m</td></tr></table>

We report the number of mentions of the word finance, translated, and stemmed, in a five-word sequence (5-gram) for each language in the Google Books Ngram Corpus. Our data set covers the period 1870–2009.

verb and noun forms of “finance.” For example, for (Simplified) Chinese we use “金融” (financial) but also include base words where there is a space or an underscore between 金 (gold) and 融 (melt). Filtering yields a set of unique sentences that mention finance for each language. In our data set, American English has the highest number of unique sentences that mention “financ,” followed by Simplified Chinese and Russian. Although Simplified Chinese has only been promoted since the 1950s, the Google ngram data for Chinese have been translated to the simplified version throughout the data set.

### 1.2 Macroeconomic data

The economic and credit data that we use are from the macro-history data set compiled by Jordà, Schularick, and Taylor (2017). The macro-history data set covers annual data for 17 advanced countries from 1870 to 2016, 6 of which are in the Google Books Corpus: France, Germany, Italy, Spain, the United Kingdom and the United States. Following Schularick and Taylor (2012), we use total loans to non-financial private sector as a proxy for the aggregate availability of credit. We measure credit growth as the annual change in real total loans to the non-financial private sector. Our credit data includes six countries and excludes China and Russia.

The macro-history data set lacks the GDP and population of China and Russia, which we supplement from the Barro-Ursua Macroeconomic Data (Barro and Ursua 2010). We measure GDP growth as the annual percentage increase in real per capita GDP.

### 1.3 Methods

We measure finance sentiment across languages at an annual frequency using a three-step process. First, we embed each sentence in the corpus into a 768-dimensional vector space. Second, we measure the cosine similarity of this sentence embedding with respect to a language specific positive minus negative embedding. Third, we average the cosine similarity of all finance-mentioning sentences in each year, weighted by their frequency.

We next describe how we calculate a sentence embedding, the positive minus negative embedding, and their cosine similarity.

1.3.1 BERT. Recent work in natural language processing (NLP) has been increasingly successful in capturing the complexity of language by considering words in sequence rather than in isolation. One of the ways this is accomplished is by representing words as embeddings. Word embeddings are high-dimensional vector space models of text in which each unique word in a corpus is represented as a vector in a shared vector space (Mikolov et al. 2013). The vector for each word is based on the context the word shares with other words in the sentence. The classic flavors of word embeddings, such as Word2Vec (Mikolov et al. 2015), GloVe (Pennington, Socher, and Manning 2014), and FastText (Bojanowski et al. 2017; Joulin et al. 2016) rely on the Distributional Hypothesis (Harris, 1954) to capture relationships in the embedding space. The hypothesis states that words that occur in the same contexts tend to have similar meanings, with the underlying idea that "a word is characterized by the company it keeps," popularized by Firth (1957). However, there are certain downsides to these flavors. First, traditional methods assign embeddings from the ground up; this is an issue for our data set in earlier years, when the number of words in the corpus is less than a million (Altszyler et al. 2017). Second, while these embedding methods work well for word-level embeddings, they are poor sentence encoders because they often misinterpret context (Perone, Silveira, and Paula 2018). We therefore move beyond shallow neural network methods.

We employ a deep neural network-based natural language processing method, BERT, developed by Devlin et al. (2018). BERT produces meaningful results even with smaller training data and can provide context for words in sentences. The key advantage of this method over classic word vector models is transfer learning, where a model developed for a task is reused as the starting point for a model on a second task. BERT's neural network is pre-trained on 800-million-word BooksCorpus and 2,500-million-word Wikipedia. Thus, the model knows which words have a similar meaning, based on pre-training.

While a full treatment of BERT is beyond our scope, we wish to provide an intuitive understanding of this method and the structure that it implicitly imposes on the data. BERT uses Transformers (Vaswani et al. 2017), a mechanism that learns contextual relations between words in a text. The model processes each word in relation to all other words in a sentence, rather than one-by-one in order. BERT is also bidirectional, which allows the model to learn the context of a word based on all its surroundings, as opposed to a unidirectional model, which reads the text sequentially. To train the model from unlabeled text from BooksCorpus and Wikipedia text, BERT employs two strategies: (i) Masked Language Modeling, where 15% of the input words are masked out and then predicted, and (ii) Next Sentence Prediction, which predicts whether Sentence B is the actual sentence that proceeds Sentence A. Solving the above two problems using its large corpora, BERT is able to place words in the embedding space. Google shares two versions of the pre-trained model: Base (12-layer, 768-hidden features) and Large (24-layer, 1,024-hidden features).

Both models are available in a cased and uncased variant. In a cased model, the text is preserved with its original casing. For example, the word "Apple" would be treated differently from "apple" or "APPLE." By maintaining the original case, the model can potentially learn to recognize and differentiate between proper nouns, acronyms, and other types of capitalized words. We use the base uncased model for English and Chinese because the extra efficiency we get from the large and cased model is not significant enough to spend more time and resources on them. For French, German, Italian, Russian, and Spanish, we use the cased multilingual model as recommended by Google Research. Thus, we use BERT Base for American and British English, BERT Base Chinese for Simplified Chinese, and BERT Base Multilingual Cased for French, German, Italian, Russian, and Spanish. $ ^{2} $

The following features of BERT make it especially useful for our purposes: First, BERT comes pre-trained, so it works well out of the box. A pre-trained model is important to us, especially in earlier years of our sample, where the Google Books Corpus is considerably smaller. Second, it offers contextualized embedding. For example, the word “bank” has a different meaning in the following two sentences: “In a crisis, we could bank on financing from the government,” and “Government’s financing for the bank is in crisis.” The context changes what the author conveys. BERT can distinguish the connotation difference between the two sentences, resulting in different embeddings. By contrast, in classical word vector models, each word has a unique embedding. Third, to reduce the number of unique words that feature in the model, BERT breaks each word into smaller subwords or tokens. For example, “wonderful” is tokenized to “won #der ##ful,” where # denotes subwords. The dimension reduction is especially important in the multilingual model. Finally, BERT is designed to encode entire sentences, up to 512 subwords. The tokenization process adds [CLS], which stands for “classification” at the beginning of each sentence. The embedding for [CLS] is used as the embedding for the entire sentence that follows it.

1.3.2 Cosine similarity. A major advantage of word embeddings is that they allow language features (such as words, sentences, etc.) to be treated as vector spaces with intuitive mathematical properties. A common example from Mikolov, Yih, and Zweig (2013) is king — man + woman ~ queen. That is, subtracting the male gender vector and adding the female gender vector to the king vector corresponds to a vector that is close to the queen vector. Thus, the word queen could be seen as starting at the word king and then moving in the feminine gender direction. Similarly, we could think of dictator + positive — negative ~ king. Here, positive minus negative represents a displacement in the positive direction. Thus, if we start from the dictator vector and move a step in

<div style="text-align: center;"><div style="text-align: center;">Table 2 Positive – negative defining sentences for English Positive sentences</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Financial services benefit society</td><td style='text-align: center; word-wrap: break-word;'>Financial services damage society</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Finance is good for society</td><td style='text-align: center; word-wrap: break-word;'>Finance is bad for society</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Finance professionals are mostly good people</td><td style='text-align: center; word-wrap: break-word;'>Finance professionals are mostly corrupt people</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Finance positively impacts our world</td><td style='text-align: center; word-wrap: break-word;'>Finance negatively impacts our world</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Financial system helps the economy</td><td style='text-align: center; word-wrap: break-word;'>Financial system hurts the economy</td></tr></table>

To define the positive minus negative dimension, we average the embeddings of positive sentences less than that of their negative counterparts.

the positive direction, we get the king vector. Other word pairs also correspond to the positive dimension, such as (benefit – damage), (good – bad), (good – corrupt), and (help – hurt).

To define our positive minus negative dimension, we average the sentence embedding differences across sentences containing “finance” or “financial” together with the above words, similar to Kozlowski, Taddy, and Evans (2019). The list of sentences for English (both American and British) is shown in Table 2. The corresponding sentence pairs for other languages are included in Internet Appendix A. We focus on the broader notion of “finance,” as opposed to more specific financial activities or players (e.g. “bank,” “lender,” etc.), because this sentiment measure speaks directly to our question of interest, attitude toward finance. More specific related words would be close in vector space to “finance” because they are frequently mentioned together, so we expect them to generate similar sentiment estimates, but each brings its own identification issues. For example, “bank turmoil” can often refer to the financial institution but also to contested territory of the West Bank. In Internet Appendix E, we verify that our main results are robust to using a broader definition of finance.

To measure sentiment toward finance, for each finance-mentioning sentence  $ j $ in language  $ i $ with embedding  $ s_{ji} $, we calculate the orthogonal projection of the sentence vector onto the language-specific positivity embedding  $ p_i $ using cosine similarity:

 $$ a_{ji}=\frac{s_{ji}\cdot p_{i}}{\left|s_{ji}\right|\left|p_{i}\right|}=\frac{\sum_{d}s_{jid}p_{id}}{\sqrt{\sum_{d}s_{jid}^{2}}\sqrt{\sum_{d}p_{id}^{2}}}, $$ 

where $d$ enumerates the elements of $s_{ji}$ and $p_{i}$, both 768-dimension vectors. By construction, the cosine similarity in Equation (1) of two positive vectors is bounded between $-1$ and $+1$, with zero indicating a neutral sentence. A more negative cosine similarity indicates that the sentence has a more negative sentiment, while a more positive cosine similarity indicates a more positive sentence.

Figure 1 illustrates this method in a two-dimensional space. The five positive (and negative) sentences, from Table 2 bunch together in the embedding space,

<div style="text-align: center;"><div style="text-align: center;">(a)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//78da4d66-fc47-4a54-ad47-576a98efe5bb/markdown_0/imgs/img_in_image_box_138_97_740_239.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A52Z%2F-1%2F%2Fb6988d129c6d8f959e1e6c4dc6743b3ea9c7a490629c8701a3ef23e08933eda3" alt="Image" width="69%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Defining the positive minus negative finance sentiment dimension</div> </div>


<div style="text-align: center;"><div style="text-align: center;">(b)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//78da4d66-fc47-4a54-ad47-576a98efe5bb/markdown_0/imgs/img_in_image_box_138_276_736_490.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A53Z%2F-1%2F%2Fb6abd301fac2a10fd6c3888df0596aa8e23e6f9ca403e06eb92e62e31976681d" alt="Image" width="69%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Projection of sentences onto positive minus negative sentiment dimension</div> </div>


## Figure 1 Conceptual diagram of finance sentiment measurement

Panel (a) shows a conceptual diagram of how similar sentences aggregate to a two-dimensional embedding space. We take the vector difference between positive and negative embeddings to define the finance sentiment dimension. Panel (b) illustrates the classification of three example sentences by projecting them onto this dimension. For one of the sentences, we illustrate cosine similarity, defined as the cosine of the angle between two vectors. Sentences that are close in terms of meaning have a smaller angle between them in this vector space, thus higher cosine similarity. Positive finance sentences have a smaller angle to the positive dimension and a larger positive projection on the finance sentiment dimension.

<div style="text-align: center;"><div style="text-align: center;">ALT TEXT: Conceptual diagram of finance sentiment measurement. Panel (a) shows positive and negative sentences in a two-dimensional embedding space, defining the finance sentiment dimension by vector differences. Panel (b) illustrates the projection of example sentences onto this dimension, with cosine similarity as the angle between vectors, indicating sentiment alignment.</div> </div>


as similar sentences keep similar company (Firth, 1957). We take the vector difference between positive and negative sentence embeddings to define our positivity dimension. Next, we project finance sentences onto the positive minus negative dimension. Sentences tend to be close to the dimension that is closer to their connotation. For example, a sentence such as “financial sector supports economic development” lies closer to the positive sentences, at a smaller angle with the positive dimension.

Cosine similarity measures the position between -1 and +1 where the shadow of a given sentence vector falls. If the sentence has a positive connotation, such as the one in our example, we will have a smaller angle between the sentence vector and the positive dimension. A smaller angle is associated with a higher cosine similarity. On the other hand, for a negative sentence such as “financial malpractices stunted our growth” would be closer to the negative dimension, or  $ \theta_{ij} > 90^\circ $. Thus, the cosine similarity for a sentence with negative connotation is negative. Similarly, a neutral sentence such as “finance lessons from the pandemic” would be roughly equidistant from both

<div style="text-align: center;"><div style="text-align: center;">Table 3 Sentences assigned the most positive and negative finance sentiment for American English Positive sentiment sentences Negative sentiment</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>the goal of financial management finance in the graduate school financial support of the center financial management of the organization business and financial experience financial support of the graduate financial support of the science financial support of the course financial support of the field knowledge of the financial structure</td><td style='text-align: center; word-wrap: break-word;'>turmoil in the financial markets finances become disordered the financial panic swept the country turmoil in financial markets financial panic swept the nation instability in the financial markets financial panic in the country severe financial setbacks a major financial panic world wide financial panic</td></tr></table>

A sentence is assigned positive or negative finance sentiment based on its projection onto the finance positivity dimension (cosine similarity). Sentences at the top are the most positive or negative in their respective column, and the absolute value of finance sentiment decreases down each list.

positive and negative dimensions ( $ \theta_{ij} \approx 90^\circ $), and thus have a cosine similarity close to zero.

Table 3 lists the sentences with the most positive and the most negative finance sentiment for American English. We can see that finance is placed in the most positive context when it is associated with funding for projects and businesses. The terms “financial management” and “financial support” are rated highly positive here because the context for “financial” in these is clearly closer to the idea that finance benefits rather than damages society. At the polar opposite, descriptions of financial distress and panics carry the most negative connotation. Internet Appendix B provides similar lists for all languages.

Finally, we calculate an annual finance sentiment for each language i based on the cosine similarity of all finance-mentioning sentences that occurs in that language in each year t, weighted by the number of times the sentence occurred that year,

 $$ f_{i t}=\sum_{j}a_{j i}\times\frac{c_{j i t}}{\sum_{k}c_{k i t}}. $$ 

The frequency weighted  $ f_{it} $ varies over time only due to changes in sentence occurrence  $ c_{jit} $, while the sentiment of particular sentences  $ a_{ji} $ in each language  $ i $ stays constant. This is an important distinction from the approach of Kozlowski, Taddy, and Evans (2019), who train a language model for each language in each year and then measure orthogonal projections based on these year-specific models. Although its approach may be more robust when very large amounts of data are available throughout the sample, our approach is more efficient and avoids issues with measurement error in small samples, which are particularly acute early in the Google Books Corpus. Computationally, our approach is considerably cheaper because training neural networks like the one behind BERT is still fairly expensive.

The cost of this reduction in measurement error and computation cost is that we implicitly assume that the language model is constant over time and that only the frequency of language use varies over time. This is obviously

not exactly right. Languages evolve. We lack the data to measure the extent to which such changes in the meaning of language matter for our conclusions. Encouragingly, evidence from U.S. newspapers over a similar period suggests that changes to American English do not greatly affect the ability to predict with text (Manela and Moreira 2017).

We calculate finance sentiment for every year from 1870 to 2009 for American English, British English, French, German, Italian, Russian, and Spanish. We have a shorter 95-year sample for Chinese because, prior to 1922, its corpus is highly sparse, and most years feature no mentions of finance. All of these languages can be traced to a major geographical area, centered around a distinct country, throughout most of our sample. For example, the concentration of Russian speakers is highest in Russia. Therefore, in what follows, we refer to the finance sentiment of these languages and countries interchangeably, but note that this requires a modest leap of faith. We expect it to introduce more error into our measure toward the end of our sample, when Spanish books, for example, may be published in Latin American countries whose economic condition is no longer highly correlated with that of Spain.

Another caveat to our finance sentiment index is that it is based on published books, which may not represent the average citizen, especially early in our sample, when large parts of the world were illiterate. As a result, we may miss marginalized and underrepresented groups of the population. Nonetheless, this “literary elite” has historically commanded a disproportionately large share of wealth and power and exerted considerable influence on the opinions of the rest of society. Its sentiment toward finance, therefore, can be even more economically important.

## 2. Finance Sentiment over Time and across Countries

Figure 2 plots our finance sentiment panel and reveals several salient features. American English has the most positive sentiment toward finance after 1912; before that, it was slightly below British English. We see a 5% drop in U.S. finance sentiment in 1874, a year after the Panic of 1873, which led to a prolonged depression, prompting policies like the adoption of the gold standard and the Special Payment Resumption Act to stabilize the economy. These measures, along with railroad expansion and good crop seasons, helped the economy recover by the late 1870s. The collapse of land and farm prices in 1887 led to renewed demands for silver coinage and intensified conflicts between gold and silver supporters. The spring of 1893 saw a severe banking panic and national depression due to a sharp drop in gold reserves. The trend across languages is of an improving finance sentiment across time, with a slight dip at the end in 2007–2008. A possible reason for that could be the great recession, the impact of which could be felt across the globe. $ ^{3} $

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//78da4d66-fc47-4a54-ad47-576a98efe5bb/markdown_3/imgs/img_in_chart_box_149_97_750_440.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A55Z%2F-1%2F%2F6f2a13ca9834c57eeff47a20c7865f168824571cf6429c14376b4ef3c5417f05" alt="Image" width="69%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 2</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Sentiment toward finance</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Finance sentiment is based on the annual average projection of finance-mentioning sentences' embeddings onto the positive minus negative finance sentiment dimension. Sentences are from the Google Books Ngram Corpus and embedded using BERT. Bands represent 95% confidence intervals produced by subsampling.</div> </div>


<div style="text-align: center;"><div style="text-align: center;">ALT TEXT: Historical finance sentiment across languages (1870–2009). The plot shows sentiment trends in various languages, highlighting shifts around significant events such as the Panic of 1873, the Great Depression, and the 2007–2008 financial crisis.</div> </div>


Languages do not seem to cross each other, apart from Chinese, which exhibits significant changes in finance sentiment over time. This volatility is in line with historical events. Chinese finance sentiment plunges in 1971 by 31% owing to uncertainty from socio-political movements led by Mao Zedong. It then rises by 28% in 1972, one year after the United Nations recognized the People's Republic of China as "the only legitimate representative of China," followed by a visit from U.S. President Nixon. Following Mao's death in 1976, Deng Xiaoping implemented significant economic reforms, including the "Open-door policy" and market-oriented development, resulting in an 18% increase. Finally, a 15% decline in 2009 underscores the significant impact of the global financial crisis on China's economy, highlighting its integration into the global financial system.

The three Romance languages in our sample, French, Italian, and Spanish, have similar attitudes toward finance. Spanish has the most favorable view, closely followed by French. At the start of 1873, we observe increased volatility and a surge in Spanish financial sentiments. This period saw the Spanish government resume gold coinage in 1876–1877 and contemplate the adoption of the gold standard. Furthermore, the restored monarchy under Alfonso XII successfully stabilized the government and ushered in a period of economic recovery, although the growth remained uneven. French finance sentiment is more volatile during World War II, with the most significant drop, 3%, in 1943 when France surrendered to Germany. The highest surge in French finance

sentiment is in 1944, the year Paris was liberated. Italian finance sentiment dips and then recovers during the 1911–1912 period, when Italy engaged in a war for the territories of Tripolitania and Cyrenaica in Libya. This conflict, which began in 1911, was part of Italy's broader imperial ambitions, but proved to be financially draining. However, this downturn was followed by a period of recovery and growth as the Fascist government established the Istituto per la Ricostruzione Industriale, aimed at stabilizing banks and large businesses by acquiring their shares, thereby bolstering their capital and mitigating losses incurred during the early 1930s crisis.

The two languages in which we find a negative finance sentiment are German and Russian. For Russian, we see high volatility in finance sentiment coinciding with the Russian revolution that occurred between 1917 and 1923. The newly formed Soviet state promoted Marx's communist doctrine and his academic stature (Magness and Makovi 2022). The largest percentage drop in Russian finance sentiment occurs in 1933 following the Soviet famine of 1932–1933. We also see a permanent increase at the beginning of the 1990s after the collapse of the USSR, as Russian-speaking countries adopt a more capitalist system.

For German, similar to Italian, we see finance sentiment falling in 1929 as Wall Street crashes and the Great Depression begins, and then increasing in 1930, the year Germany implemented the Young Plan. This plan was an effort to restructure Germany's reparations payments from World War I, significantly reducing the annual payments and extending the repayment period. However, the growth in financial sentiment reverses in the following years, as Chancellor Heinrich Brüning enacts austerity measures in an attempt to reduce Germany's public debt (Galofré-Vilà et al. 2021).

### 2.1 Summary statistics

Table 4 describes finance sentiment over our sample. We see that sentiment toward finance in languages spoken in more capitalist countries tends to be above that of communist countries. In our sample, American English, on average, is at the top, followed closely by British English. The next set of languages are Spanish, French, Chinese, and Italian. German and Russian are the two languages with an overall negative connotation for finance. Its volatility is highest for Russian, followed by Spanish and French.

Finance sentiment becomes more positive over time, growing 0.0001 a year across all languages. Within-language, average sentiment change is -0.0001 for China and +0.0001 for all other countries. France has the highest average change in finance sentiment at 0.00014, followed closely by Italy and Spain.

During the 1870–2009 period, both GDP and credit grow on average for countries in our sample. China experiences the highest GDP growth, averaging 4.3% a year. Germany, Spain, and the United States each saw average GDP growth of 2.1%. In terms of credit growth, Germany led with an annual average increase of 8.9%, followed by Spain at 7.4% and Italy at 6.1%.

<div style="text-align: center;"><div style="text-align: center;">Table 4 Finance sentiment and other summary statistics</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Country (language)</td><td style='text-align: center; word-wrap: break-word;'>Variable, %</td><td style='text-align: center; word-wrap: break-word;'>Mean</td><td style='text-align: center; word-wrap: break-word;'>Std. Dev.</td><td style='text-align: center; word-wrap: break-word;'>Obs.</td></tr><tr><td rowspan="3">China (Chinese)</td><td style='text-align: center; word-wrap: break-word;'>Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>7.4</td><td style='text-align: center; word-wrap: break-word;'>0.5</td><td style='text-align: center; word-wrap: break-word;'>88</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta $ Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>$ -0.01 $</td><td style='text-align: center; word-wrap: break-word;'>0.57</td><td style='text-align: center; word-wrap: break-word;'>87</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GDP growth</td><td style='text-align: center; word-wrap: break-word;'>4.3</td><td style='text-align: center; word-wrap: break-word;'>7.2</td><td style='text-align: center; word-wrap: break-word;'>87</td></tr><tr><td rowspan="4">France (French)</td><td style='text-align: center; word-wrap: break-word;'>Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>7.6</td><td style='text-align: center; word-wrap: break-word;'>0.7</td><td style='text-align: center; word-wrap: break-word;'>140</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta $ Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>0.01</td><td style='text-align: center; word-wrap: break-word;'>0.09</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GDP growth</td><td style='text-align: center; word-wrap: break-word;'>1.9</td><td style='text-align: center; word-wrap: break-word;'>6.4</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Credit growth</td><td style='text-align: center; word-wrap: break-word;'>4.9</td><td style='text-align: center; word-wrap: break-word;'>12.9</td><td style='text-align: center; word-wrap: break-word;'>101</td></tr><tr><td rowspan="4">Germany (German)</td><td style='text-align: center; word-wrap: break-word;'>Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>$ -4.9 $</td><td style='text-align: center; word-wrap: break-word;'>0.5</td><td style='text-align: center; word-wrap: break-word;'>140</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta $ Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>0.01</td><td style='text-align: center; word-wrap: break-word;'>0.22</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GDP growth</td><td style='text-align: center; word-wrap: break-word;'>2.1</td><td style='text-align: center; word-wrap: break-word;'>8.1</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Credit growth</td><td style='text-align: center; word-wrap: break-word;'>8.9</td><td style='text-align: center; word-wrap: break-word;'>17.8</td><td style='text-align: center; word-wrap: break-word;'>129</td></tr><tr><td rowspan="4">Italy (Italian)</td><td style='text-align: center; word-wrap: break-word;'>Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>4.4</td><td style='text-align: center; word-wrap: break-word;'>0.4</td><td style='text-align: center; word-wrap: break-word;'>140</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta $ Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>0.01</td><td style='text-align: center; word-wrap: break-word;'>0.21</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GDP growth</td><td style='text-align: center; word-wrap: break-word;'>2.0</td><td style='text-align: center; word-wrap: break-word;'>4.7</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Credit growth</td><td style='text-align: center; word-wrap: break-word;'>6.1</td><td style='text-align: center; word-wrap: break-word;'>13.9</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td rowspan="3">Russia (Russian)</td><td style='text-align: center; word-wrap: break-word;'>Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>$ -10.4 $</td><td style='text-align: center; word-wrap: break-word;'>0.3</td><td style='text-align: center; word-wrap: break-word;'>140</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta $ Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>0.01</td><td style='text-align: center; word-wrap: break-word;'>0.18</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GDP growth</td><td style='text-align: center; word-wrap: break-word;'>2.0</td><td style='text-align: center; word-wrap: break-word;'>8.5</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td rowspan="4">Spain (Spanish)</td><td style='text-align: center; word-wrap: break-word;'>Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>8.3</td><td style='text-align: center; word-wrap: break-word;'>0.7</td><td style='text-align: center; word-wrap: break-word;'>140</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta $ Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>0.01</td><td style='text-align: center; word-wrap: break-word;'>0.24</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GDP growth</td><td style='text-align: center; word-wrap: break-word;'>2.1</td><td style='text-align: center; word-wrap: break-word;'>5.0</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Credit growth</td><td style='text-align: center; word-wrap: break-word;'>7.4</td><td style='text-align: center; word-wrap: break-word;'>11.1</td><td style='text-align: center; word-wrap: break-word;'>98</td></tr><tr><td rowspan="4">UK (British English)</td><td style='text-align: center; word-wrap: break-word;'>Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>14.2</td><td style='text-align: center; word-wrap: break-word;'>0.3</td><td style='text-align: center; word-wrap: break-word;'>140</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta $ Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>0.002</td><td style='text-align: center; word-wrap: break-word;'>0.21</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GDP growth</td><td style='text-align: center; word-wrap: break-word;'>1.5</td><td style='text-align: center; word-wrap: break-word;'>2.9</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Credit growth</td><td style='text-align: center; word-wrap: break-word;'>4.0</td><td style='text-align: center; word-wrap: break-word;'>8.2</td><td style='text-align: center; word-wrap: break-word;'>129</td></tr><tr><td rowspan="4">US (American English)</td><td style='text-align: center; word-wrap: break-word;'>Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>14.5</td><td style='text-align: center; word-wrap: break-word;'>0.6</td><td style='text-align: center; word-wrap: break-word;'>140</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta $ Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>0.01</td><td style='text-align: center; word-wrap: break-word;'>0.18</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GDP growth</td><td style='text-align: center; word-wrap: break-word;'>2.1</td><td style='text-align: center; word-wrap: break-word;'>5.0</td><td style='text-align: center; word-wrap: break-word;'>139</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Credit growth</td><td style='text-align: center; word-wrap: break-word;'>4.5</td><td style='text-align: center; word-wrap: break-word;'>6.7</td><td style='text-align: center; word-wrap: break-word;'>129</td></tr><tr><td rowspan="4">Total</td><td style='text-align: center; word-wrap: break-word;'>Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>8.4</td><td style='text-align: center; word-wrap: break-word;'>1,068</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta $ Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>0.01</td><td style='text-align: center; word-wrap: break-word;'>0.25</td><td style='text-align: center; word-wrap: break-word;'>1,060</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GDP growth</td><td style='text-align: center; word-wrap: break-word;'>2.1</td><td style='text-align: center; word-wrap: break-word;'>6.2</td><td style='text-align: center; word-wrap: break-word;'>1,060</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Credit growth</td><td style='text-align: center; word-wrap: break-word;'>5.9</td><td style='text-align: center; word-wrap: break-word;'>12.5</td><td style='text-align: center; word-wrap: break-word;'>725</td></tr></table>

The sample spans from 1870 to 2009 for eight country-language pairs. The corpus of sentences for each language is gathered from the Google Books Ngram Corpus. The connotation for each finance-mentioning sentence is measured based on its cosine similarity with respect to the positive minus negative vector. Finance sentiment is the average cosine similarity of finance-mentioning sentences in each language and year. GDP and credit data are from Jordà, Schularick, and Taylor (2017) and Barro and Ursua (2010) when available.

Because finance sentiment trends positive, we use first differences when we relate finance sentiment to the macro economy in Section 5. For ease of interpretation, we standardize these first differences by dividing them by the full sample standard deviation (0.08). Our first difference in finance sentiment. or  $ \Delta f $, is defined as: $ ^{4} $

 $$ \Delta f_{it}=\frac{f_{it}-f_{it-1}}{\sigma\left(f_{it}\right)} $$ 

The full sample standard deviation change in finance sentiment (or 0.08) in the denominator is roughly the difference between China and the United States.

However, the within-country standard deviation (after absorbing country fixed effects) is 0.005 or 16 times smaller. Below, we use the within-county standard deviation to gauge economic magnitudes in regressions that include country fixed effects to focus on this more plausible variation in finance sentiment.

### 2.2 Capitalism and finance sentiment

Motivated by the turning points in Russian and German finance sentiment, we next investigate how finance sentiment relates to attitudes toward capitalism more broadly. In Table 5, we regress finance sentiment on 3 measures of attitudes toward capitalism that were previously used by Di Tella and Macculloch (2009). We gradually consider more saturated fixed effect specifications.

Given our narrow panel, we follow Baron and Muir (2022) who in a similar setting use Driscoll and Kraay (1998) standard errors to account for correlation in regression residuals over time within each country and between countries.

We find that, comparing across countries, higher finance sentiment is associated with more positive attitudes toward capitalism according to all 3 measures of capitalism. Countries with more right-leaning governments are more likely to exhibit positive sentiment toward finance. So do countries whose citizens say they prefer private over public ownership of businesses. Finally, countries where registering a business is difficult exhibit a lower sentiment toward finance.

While these results reassure us that our measure of finance sentiment works as intended, the low R-squares in the specifications without fixed effects imply that finance sentiment is quite different and far from being spanned by attitudes toward capitalism. Given the persistence of finance sentiment, the inclusion of country fixed effects captures essentially all its variation, as is evident from the R-squares being close to 1.

## 3. External Validation

In this section, we examine whether our measure of financial sentiment is associated with external indicators of demand for financial services. We analyze both direct measures of financial market participation and indirect measures, such as income inequality.

### 3.1 Credit and stock markets participation

We use several country-level variables that capture participation in the financial system to validate our measure of finance sentiment. Previous studies have shown that individuals are less inclined to participate in financial markets if they possess a general lack of trust in financial institutions (Guiso, Sapienza, and Zingales 2008; Giannetti and Wang 2016; Gurun, Stoffman, and Yonker 2018; D'Acunto, Prokopczuk, and Weber 2019). We therefore expect that

<div style="text-align: center;"><div style="text-align: center;">Finance sentiment and attitudes toward capitalism</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Finance sentiment</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td><td style='text-align: center; word-wrap: break-word;'>(4)</td><td style='text-align: center; word-wrap: break-word;'>(5)</td><td style='text-align: center; word-wrap: break-word;'>(6)</td><td style='text-align: center; word-wrap: break-word;'>(7)</td><td style='text-align: center; word-wrap: break-word;'>(8)</td><td style='text-align: center; word-wrap: break-word;'>(9)</td></tr><tr><td rowspan="2">Right-learning government</td><td style='text-align: center; word-wrap: break-word;'>$ 0.310^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.324^{***} $</td><td style='text-align: center; word-wrap: break-word;'>0.00338</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.100)</td><td style='text-align: center; word-wrap: break-word;'>(0.116)</td><td style='text-align: center; word-wrap: break-word;'>(0.00447)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Preference for private ownership of business</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ 0.489^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.515^{***} $</td><td style='text-align: center; word-wrap: break-word;'>0.00533</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Difficulty of registering a business</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.0327)</td><td style='text-align: center; word-wrap: break-word;'>(0.0333)</td><td style='text-align: center; word-wrap: break-word;'>(0.0252)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td rowspan="2">GDP growth</td><td style='text-align: center; word-wrap: break-word;'>0.0231</td><td style='text-align: center; word-wrap: break-word;'>0.0246</td><td style='text-align: center; word-wrap: break-word;'>$ -0.000342 $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.116^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.126^{***} $</td><td style='text-align: center; word-wrap: break-word;'>0.00394*</td><td style='text-align: center; word-wrap: break-word;'>$ -0.187^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.00261 $</td><td style='text-align: center; word-wrap: break-word;'>(0.00218)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.0243)</td><td style='text-align: center; word-wrap: break-word;'>(0.0311)</td><td style='text-align: center; word-wrap: break-word;'>(0.00109)</td><td style='text-align: center; word-wrap: break-word;'>(0.0147)</td><td style='text-align: center; word-wrap: break-word;'>(0.0194)</td><td style='text-align: center; word-wrap: break-word;'>(0.00187)</td><td style='text-align: center; word-wrap: break-word;'>(0.0036)</td><td style='text-align: center; word-wrap: break-word;'>(0.0109)</td><td style='text-align: center; word-wrap: break-word;'>(0.00218)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Country FE</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.0360 $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.00368 $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Year FE</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>(0.248)</td><td style='text-align: center; word-wrap: break-word;'>(0.00252)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Observations</td><td style='text-align: center; word-wrap: break-word;'>263</td><td style='text-align: center; word-wrap: break-word;'>263</td><td style='text-align: center; word-wrap: break-word;'>263</td><td style='text-align: center; word-wrap: break-word;'>67</td><td style='text-align: center; word-wrap: break-word;'>67</td><td style='text-align: center; word-wrap: break-word;'>67</td><td style='text-align: center; word-wrap: break-word;'>35</td><td style='text-align: center; word-wrap: break-word;'>35</td><td style='text-align: center; word-wrap: break-word;'>35</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.0293</td><td style='text-align: center; word-wrap: break-word;'>0.0518</td><td style='text-align: center; word-wrap: break-word;'>0.999</td><td style='text-align: center; word-wrap: break-word;'>0.522</td><td style='text-align: center; word-wrap: break-word;'>0.551</td><td style='text-align: center; word-wrap: break-word;'>1.000</td><td style='text-align: center; word-wrap: break-word;'>0.222</td><td style='text-align: center; word-wrap: break-word;'>0.231</td><td style='text-align: center; word-wrap: break-word;'>1.000</td></tr></table>

Right-leaning government is based on the ideology of the largest party in government, according to the classification scheme of the Database of Political Institutions, made available via the World Bank starting in 1975. Scale - Left: 0, Center: 0.5, Right: 1. Preference for business ownership is measured using the World Values Surveys, available after 1992. If survey data for a specific year is missing, we estimate the values by linearly extrapolating between the nearest available years. Scale - State: 1, Private: 10. Difficulty of registering a business measures the total number of procedures required for a startup to obtain legal status, obtained from World Development Indicators published by the World Bank starting in 2003. The scale ranges from 5 to 10. Finance sentiment is standardized to have a mean of zero and a standard deviation of one. Driscoll-Kraay standard errors are in parentheses. *p < 0.1; **p < 0.05; ***p < 0.01.

Downloaded from https://academic.oup.com/rfs/advance-article/doi/10.1093/rfs/hha012/8045328 by Zhejiang University user on 23 October 2025

finance sentiment would be positively correlated with national accounts and survey data on credit and stock market participation.

Our measures of credit are total loans to households and total loans to non-financial private sectors. Both are measured as a percent of GDP and derived from the macro-history data set, as compiled by Jordà, Schularick, and Taylor (2017). This data set includes annual data for 17 advanced countries that span the years 1870 to 2016. Notably, 6 of these countries, France, Germany, Italy, Spain, the United Kingdom and the United States, are included in the Google Books Corpus.

Our measure of stock market participation is equity as a percent of total assets for households. This aggregated survey data is from the Organisation for Economic Co-operation and Development (OECD). It is available for five countries in our text sample: France, Germany, Spain, the United Kingdom, and the United States.

Cross-country comparisons of demand for financial services and their correlation with finance sentiment can, of course, be driven by omitted factors. The same is true for comparisons over time. To limit the influence of such omitted variables on our inferences, we include year- and country-fixed effects in all our validation tests.

Table 6 shows that finance sentiment is positively correlated with credit and stock market participation. Specifically, we find that after absorbing country- and year- fixed effects, a single within-country standard deviation increase in finance sentiment, which is again 16 times smaller than the unconditional standard deviation, is associated with (1) a 4 percentage point increase in equity as a percent of total assets for households, (2) a 6 percentage point increase in loans to households as a percent of GDP, and (3) a 6 percentage point increase in loans to non-financial private sectors as a percent of GDP.

### 3.2 Income inequality

While credit and stock market participation directly measure demand for financial services, an indirect consequence of disparities in financial services demand is income and wealth inequality. Higher stock market participation, for example, could lead to lower equity premia and a decrease in wealth inequality if poorer households increasingly benefit from high average equity returns. Indeed, Favilukis (2013) finds that the stock market plays a major role in increasing wealth inequality. Moreover, in the presence of stock market participation costs, higher income inequality can result in lower participation in financial markets by the poor. In either case, we expect income and wealth inequality to be negatively correlated with sentiment toward finance.

To test this hypothesis, we use annual data on income inequality from the UNU-WIDER, World Income Inequality Database (WIID). Table 6 shows that a single within-country standard deviation increase in finance sentiment is associated with a 3 percentage point decrease in the Gini coefficient. That this

<div style="text-align: center;"><div style="text-align: center;">Table 6 Credit, stock market participation, and income inequality</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(1) Equity/Total for households (%)</td><td style='text-align: center; word-wrap: break-word;'>(2) Households loans / GDP</td><td style='text-align: center; word-wrap: break-word;'>(3) Non-financial private sector loans / GDP</td><td style='text-align: center; word-wrap: break-word;'>(4) Income inequality</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Finance sentiment</td><td style='text-align: center; word-wrap: break-word;'>57.77* (27.65)</td><td style='text-align: center; word-wrap: break-word;'>$ 0.9070^{***}(31.00) $</td><td style='text-align: center; word-wrap: break-word;'>$ 102.6^{***}(29.66) $</td><td style='text-align: center; word-wrap: break-word;'>$ -45.42^{***}(11.31) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GDP growth</td><td style='text-align: center; word-wrap: break-word;'>-0.377 (0.264)</td><td style='text-align: center; word-wrap: break-word;'>0.00873 (0.255)</td><td style='text-align: center; word-wrap: break-word;'>-0.311 (0.210)</td><td style='text-align: center; word-wrap: break-word;'>-0.0175 (0.0944)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Country FE</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Year FE</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Observations</td><td style='text-align: center; word-wrap: break-word;'>75</td><td style='text-align: center; word-wrap: break-word;'>431</td><td style='text-align: center; word-wrap: break-word;'>733</td><td style='text-align: center; word-wrap: break-word;'>216</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.952</td><td style='text-align: center; word-wrap: break-word;'>0.811</td><td style='text-align: center; word-wrap: break-word;'>0.718</td><td style='text-align: center; word-wrap: break-word;'>0.880</td></tr></table>

Equity as a percent of total assets for households is from the OECD and covers five countries: France, Germany, Spain, the United Kingdom, and the United States. This metric ranges from 0 to 100 and is available from 1995 onward. Total loans to households and total loans to the non-financial private sector, expressed as a percentage of gross domestic product, are sourced from the Jordà-Schularick-Taylor Macrohistory Database. The available years for these metrics vary by country, with data for total loans to households typically starting from 1950 and for total loans to the non-financial private sector from 1900. Income inequality is measured using the Gini coefficient, reported by the World Income Inequality Database, with values ranging from 0 to 100. While the availability of data varies by country, it is generally accessible starting from 1970. Finance sentiment is standardized to have a mean of zero and a standard deviation of one. Driscoll-Knaay standard errors are in parentheses.  $ p<0.1 $;  $ p<0.05 $;  $ p<0.01 $.

Downloaded from https://academic.oup.com/rfs/advance-article/doi/10.1093/rfs/hha012/8045328 by Zhejiang University user on 23 October 2025

effect survives country and year fixed effects, suggests that a fundamental and robust link exists between finance sentiment and income inequality.

## 4. Sentiment Toward Other Industries

We next investigate attitudes towards more specific financial concepts. Then, as a placebo, we measure sentiment towards other sectors and toward a neutral term.

### 4.1 Sentiment toward more specific financial concepts

Finance is a somewhat broad concept. The English word originates from the French “finer,” which in the 14th century meant to reach an end or to settle a dispute or debt (Oxford English Dictionary 2022). Its meaning in contemporary use can vary. To some people, finance means specific financial contracts such as loans and stocks. To others, it means specific financial intermediaries such as banks and mutual funds.

We explore these additional meanings by applying our sentiment measurement approach to more specific financial concepts: banks, stock markets, mutual funds, and large corporations. These four concepts comprise the Financial Trust Index created by Paola Sapienza and Luigi Zingales. This analysis requires that we translate the phrases we use to define the positivity dimension in each language. $ ^{5} $

Comparing the results in Figure 3 to the finance sentiment panel in Figure 2, we see fairly similar ordering between languages in their positivity toward these more specific concepts. American and British English are always at the top, and Russian is always at the bottom except for large corporations. Chinese, French, German, Italian, and Spanish are usually lumped in the middle of the distribution.

In both Russia and China, large corporations have existed throughout their planned-economy periods, largely owned by the government. Perhaps for this reason, Russian sentiment toward large corporations is unusually positive, and Chinese sentiment is more positive than for the other three finance concepts. These results suggest that constructing a broad index like the Financial Trust Index requires country-specific adjustments due to cross-country variation in the meaning and history of the different financial institutions.

Historically, terms such as banks, savings banks, and credit unions have been synonymous with the financial sector and financial system. To create a more comprehensive measure, we consider another sentiment index, which we call "Broad Finance Sentiment," calculated by averaging finance sentiment (from Figure 2) and bank sentiment (from Figure 3a). Internet Appendix E, shows that our main results are robust to using this broader definition of finance.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//2df5911d-3acf-4db4-b7ad-71db60d06ccc/markdown_1/imgs/img_in_image_box_39_176_638_1073.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A10Z%2F-1%2F%2F5b34edaf162e05308790d195ba8a8b3096443157f669aa07f39910eacb06602b" alt="Image" width="69%" /></div>


We report sentiment toward banks, mutual funds, stock markets, and large corporations by redefining the positivity dimension accordingly and focusing on sentences mentioning these specific concepts. For example, sentiment for banks is based on the annual average projection of bank-mentioning sentence embeddings onto the positive minus negative bank sentiment dimension. To define the positivity dimension, we average the difference in embedding for the following tuples (and their translations to each language): [(“banks are good for society”, “banks are bad for society”) (“bank managers are mostly good people”, “bank managers are mostly corrupt people”), “banks positively impact our world”, “banks negatively impact our world”], (“banking for society”) (“bank managers are mostly poor people”, “bank managers are mostly corrupt people”), (“banking services damages society”)). For banks, we only report sentiment for languages where the economy is “banking industry hurts the economy” (“banking services benefits society”, “banking services damages society”)). For banks, we use a cutoff equal to the maximum number of sentences containing the word, in a year, exceeds 1,000. For the rest, because the number of sentences in a year is smaller, we use a cutoff equal to the maximum number of sentences for a country across decades divided by 10. The cutoff is bounded between 10 and 1,000.

\(S_{10} = \frac{1}{2} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 10^{10} \times 

Specifically, the broader finance sentiment index displays the same ordering of languages: U.S. and U.K. English are at the top, followed by French, Spanish, Simplified Chinese, and Italian in the middle, with German and Russian at the bottom. This ordering persists throughout most of the long sample. We also observe similar patterns of volatility, such as fluctuations in China during the 1970s and a significant drop in sentiment around the 2007–2009 financial crisis. Finally, we find that this broader definition of finance is positively correlated with attitudes toward capitalism.

### 4.2 Industries unrelated to finance

One potential concern may be that it is not just finance-specific sentiment that is changing over time and across countries, but rather sentiment more generally. To explore this possibility, we construct similar text-based measures of sentiment for three other industries that existed throughout our sample period: coal, paper, and tobacco. Because this calculation is computationally expensive, we produce these sentiment indices only once per decade. This lower-frequency analysis suffices for our purposes because we are interested mostly in comparing the ordering and variation across languages to those of finance sentiment.

Figure 4 shows that sentiment more generally looks quite different from the one toward finance. Sentiment toward other industries shows no clear upward trend, rises and falls at different times, and the ordering across languages is different. The cross-language variation is also more modest, suggesting these alternative industries carry a more neutral sentiment. We do see, however, that Russian language books tend to be the most negative about all the industries we study, albeit not quite as negative as its finance sentiment.

In the last panel of Figure 4, we report another measure of general sentiment as the sentiment associated with the fairly generic word “January” across time, following Gentzkow, Glaeser, and Goldin (2006), who use it to deflate for changes in newspaper reporting volume over time. It is not a perfectly neutral word because its cultural association is quite different across languages and religions. But within language variation over time could still inform us about trends in sentiment more generally. We can see that January sentiment is quite flat across years and does not trend in any language. Its ordering across languages is quite different from that of finance sentiment. January is placed in the most positive context by Italian books and in the most negative context by Chinese ones. Overall, we find little evidence that variation in general sentiment is responsible for the variation we see in finance sentiment.

While we have no strong prior as to how the paper and coal industries would trend over time, sentiment toward the tobacco industry has shifted considerably. In the early 20th century, smoking was considered fashionable and socially acceptable, and the tobacco industry made a significant contribution to the economy. However, in the 1950s, studies linking smoking to various health problems, including lung cancer and heart disease, began to emerge. This led

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//2df5911d-3acf-4db4-b7ad-71db60d06ccc/markdown_3/imgs/img_in_image_box_47_187_321_1065.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A12Z%2F-1%2F%2F17e4cf857f5b157ea47fcdbe309a60ceae175c2375fea5b557fb04607a5bd76c" alt="Image" width="31%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//2df5911d-3acf-4db4-b7ad-71db60d06ccc/markdown_3/imgs/img_in_chart_box_327_184_615_624.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A12Z%2F-1%2F%2Ffd028f9a0bdbfb1e072914d8edb704da8c66d18cce9de7d3214d08a8d681e818" alt="Image" width="33%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//2df5911d-3acf-4db4-b7ad-71db60d06ccc/markdown_3/imgs/img_in_image_box_327_632_616_1064.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A12Z%2F-1%2F%2Ff36b00db85c38ca4e9df603f28ec7de766629e04b6deba2692e67a80996d0cda" alt="Image" width="33%" /></div>


We report sentiment toward the coal, paper and tobacco industries, as well as toward the fairly generic word "January," redefining the positivity dimension accordingly and focusing on sentences mentioning these alternatives instead of "finance." For example, sentiment for the coal industry is based on the annual average projection of coal-mentioning sentence embeddings onto the positive minus negative coal sentiment dimension. To define the positivity dimension, we average the difference in embedding for the following tuples (and their translations to each language): [( "coal is good for society," "coal is bad for society" ) ("coal miners are mostly good people," "coal miners are mostly corrupt people" ) ("coal positively impacts our world," "coal negatively impacts our world" ) ("coal industry helps the economy," "coal industry hurts the economy" ) ("coal industry benefits society," "coal industry damages society" )). Between similar ngrams such as "coal miners," ("coal producers," we select the ngram with a higher Google search volume. We only report sentiments for the language when the number of sentences containing the word, in a year, exceeds 1,000.

5 AUG 2023, Central Seminare (Stewardship of the United States) 2023 08

<div style="text-align: center;"><div style="text-align: center;">Table 7 Tobacco consumption and tobacco sentiment</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(1) Daily smoking prevalence (%)</td><td style='text-align: center; word-wrap: break-word;'>(2) Consumption per capita (# cig.)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Tobacco Sentiment</td><td style='text-align: center; word-wrap: break-word;'>5.143 $ ^{***} $ (1.619)</td><td style='text-align: center; word-wrap: break-word;'>873.5 $ ^{***} $ (132.5)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Country FE</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Year FE</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Observations</td><td style='text-align: center; word-wrap: break-word;'>240</td><td style='text-align: center; word-wrap: break-word;'>240</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R $ ^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.902</td><td style='text-align: center; word-wrap: break-word;'>0.682</td></tr></table>

Daily smoking prevalence and annual cigarette consumption are from Global Health Data Exchange made available by the Institute for Health Metrics and Evaluation, covering the 1980–2009 period. Annual cigarette consumption is normalized by population data from the World Bank. Tobacco sentiment is standardized to have a mean of zero and a standard deviation of one. Driscoll-Kraay standard errors are in parentheses.  $ ^{*}p<0.1 $;  $ ^{**}p<0.05 $;  $ ^{***}p<0.01 $.

to a public health campaign to reduce smoking, and in the following decades, public opinion about the tobacco industry began to change.

In the 1980s and 1990s, public awareness of the health risks associated with smoking increased, and the tobacco industry faced greater scrutiny and regulation. The industry was accused of deceptive marketing practices and concealing the health risks associated with smoking, leading to numerous lawsuits against tobacco companies and a decline in smoking rates in many countries. Table 7 analyzes whether sentiment toward the tobacco industry aligns with tobacco consumption.

We find a positive correlation between sentiment toward the tobacco industry and smoking rates. Specifically, sentiment is positively correlated with the percentage of the population above the age of 15 years who smoke, as well as with smoking prevalence and per capita cigarette consumption. In Table 7, one within-country standard deviation increase in tobacco sentiment, which is 10.5 times smaller than the sample standard deviation, is associated with (1) an additional 0.5% increase in daily smoking prevalence and (2) an increase of 83 cigarettes in annual per capita consumption in the country.

These findings suggest that attitudes toward the tobacco industry are closely related to tobacco consumption. More broadly, these results show that the method we use to calculate finance sentiment is reasonably accurate and potentially applicable to other industries.

## 5. Finance Sentiment and the Macroeconomy

How does finance sentiment relate to financial crises and to macroeconomic growth? Our analysis focuses on output growth and credit growth. As Zingales (2015) argues, the positive role that finance can play in society depends on public sentiment toward the financial sector. Societies that find finance beneficial would likely use financial services more, smooth their consumption over time and across states of nature, and fund more productive projects.

We would thus expect countries where finance sentiment increases to be more productive and to utilize more financial services.

### 5.1 Financial crises

We next examine the relationship between finance sentiment changes and historical banking crises. One might expect finance sentiment to decline following a financial crisis. But, because the financial system requires trust, a decline in finance sentiment can itself transform a mild recession into a full-blown financial crisis (Sapienza and Zingales 2012). To do so, we leverage the data set on banking distress and panics gathered by Baron, Verner, and Xiong (2021), who have shown that bank equity declines precede contractions in credit and output, even in the absence of panics.

Figure 5 plots the mean finance sentiment changes around such bank equity declines. To control for unobserved heterogeneity, we absorb country and year fixed effects. $ ^{6} $ We find that finance sentiment declines by about 0.8% of its full sample standard deviation in the year preceding bank equity declines, but stays relatively flat in the 5 years following these events. Interestingly, these declines in finance sentiment follow a finance sentiment boom 2 years before the distress period. This result is consistent with the finding of Schularick and Taylor (2012) that financial crises tend to follow credit booms about 2 years later.

The relatively tight confidence interval around the year 0 estimates allows us to reject the hypothesis that finance sentiment declines in the short run. While the confidence intervals widen farther away from the onset of banking distress, the point estimates show little sign of a significant decline in finance sentiment during the subsequent 5 years.

Panel (b) of Figure 5 shows that the empirical fact that finance sentiment declines prior to banking crises is robust to accounting for credit and GDP growth. As mentioned earlier, controlling for credit growth reduces our sample size by excluding China and Russia. In contrast, the rise 2 years before the crisis is largely subsumed by these controls.

In Internet Appendix E, we show that when using the broader but noisier definition of finance, the direction of change in finance sentiment is negative 1 year prior to the crises, consistent with our main finding, though this result is statistically no different from zero. Furthermore, in Internet Appendix D, we show that our results remain robust when using growth instead of changes in finance sentiment.

In Table 8, we investigate whether finance sentiment holds incremental predictive power for financial distress, over and above credit growth. The first three columns report logistic regressions of bank equity declines on lags of finance sentiment growth and credit growth. All three show that declines in

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//7af60055-9b20-424b-9fb9-3559bbc05c38/markdown_1/imgs/img_in_chart_box_136_97_739_434.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A56Z%2F-1%2F%2Faedb7647cdfcec61c2612b3005e0a59e0315b58b77499bd254a758adb5842240" alt="Image" width="69%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Baseline</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//7af60055-9b20-424b-9fb9-3559bbc05c38/markdown_1/imgs/img_in_chart_box_137_476_739_816.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A56Z%2F-1%2F%2F6d83b6282c5a6674f4dbe2e0a682d2c7e1ebf71bfa9af3bdc1edcf724326b1a2" alt="Image" width="69%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Controlling for credit growth and GDP growth</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Figure 5</div> </div>


##### Finance sentiment around financial crises

The figure shows how finance sentiment evolves around periods of banking distress, when bank equity declines by at least 30%. The light blue bars represent 90% confidence intervals adjusted for country-level clustering. Estimates are based on the following regression:  $ \Delta f_{it}=c+\beta_1 crisis_{it}^{-5}+\cdots+\beta_{10 crisis_{it}^{+5}}+country_i+yr_t+\epsilon_{i,t} $. Model specifications with credit growth exclude China and Russia as credit data for these two countries are unavailable. Finance sentiment is standardized to have a mean of zero and a standard deviation of one.

ALT TEXT: Finance sentiment around banking crises. Graph shows changes in finance sentiment in relation to banking distress events, with confidence intervals. Sentiment drops noticeably in the year before bank equity declines, following a sentiment boom 2 years prior.

finance sentiment indicates an increase in the probability of banking distress in the following year. The second lag of finance sentiment growth is statistically insignificant, though positive as in Figure 5. Consistent with the results of Schularick and Taylor (2012) and Krishnamurthy and Muir (Forthcoming),

credit growth is higher 2 years prior to banking distress. But even when we control for credit growth, the first lag of finance sentiment remains a significant predictor of bank equity declines.

Specification (4) shows that this result also manifests in a linear probability model. Because banking panics often involve more than one country, in the last specification we include year fixed effects. We find that finance sentiment growth can also predict idiosyncratic banking distress episodes.

Given the compelling evidence of Baron, Verner, and Xiong (2021) that panics are the result of earlier declines in bank equity, our evidence suggests that declines in finance sentiment could be a cause, rather than a consequence, of financial crises. Although timing evidence cannot rule out reverse causality, we find it unlikely that finance sentiment declines in anticipation of a subsequent financial crisis.

As Table 9 shows, this result is fairly robust to varying the definition of banking distress. Finance sentiment declines 1 year before banking panics, bank failures, bank equity crises, or the union of these indicators, as defined by Baron, Verner, and Xiong (2021). The one exception is that it does not forecast Jordà, Schularick, and Taylor (2017) crises, which are based on narrative accounts of bank runs, bank failures, and government interventions. This could be because such narrative accounts miss important but smaller episodes or because the episodes they classify as crises are fundamentally different. As Krishnamurthy and Muir (Forthcoming) explain, these chronologies sometimes date the same episodes in different years.

Finally, we note that if the shift in public sentiment toward finance appears in the Google Books Corpus with a lag, this would strengthen the result that finance sentiment changes lead banking distress periods. The evidence on publication lags of severe natural disasters we report in Jha, Liu, and Manela (2021) suggests modest lags of less than a year before such disasters are first mentioned in the corpus. This may be surprising if we consider the time it now takes to publish a bestseller, but the Google Books Corpus includes many serial publications, like government reports, that are often more timely.

### 5.2 Economic growth

We next analyze how shocks to finance sentiment relate to macroeconomic activity through the lens of local projection-estimated impulse responses, which separate these shocks from other macroeconomic shocks to output and credit. Specifically, we estimate cumulative impulse response functions via local projections (Jordà 2005):

 $$ \Delta_{h}y_{i,t+h}=\alpha_{i}^{h}+\sum_{k=1}^{3}\beta_{k}^{h}\Delta f_{i,t-k}+\sum_{k=0}^{3}\gamma_{k}^{h}X_{i,t-k}+\epsilon_{i,t+h},\quad h=0,\ldots,H, $$ 

where i represents the country and t represents the year.  $ \Delta_{h}y_{i,t+h}=y_{i,t+h}-y_{i,t-1} $ indicates the h-year cumulative growth of interest, for example, GDP growth

<div style="text-align: center;"><div style="text-align: center;">Finance sentiment declines before bank equity declines</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Bank equity 30% decline $ _{t+1} $</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2">Model</td><td colspan="2">Logistic regression</td><td colspan="3">Linear probability model</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td><td style='text-align: center; word-wrap: break-word;'>(4)</td><td style='text-align: center; word-wrap: break-word;'>(5)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta f_{t} $</td><td style='text-align: center; word-wrap: break-word;'>$ -8.518^{***}(3.031) $</td><td style='text-align: center; word-wrap: break-word;'>$ -6.853^{*}(3.700) $</td><td style='text-align: center; word-wrap: break-word;'>$ -15.62^{***}(3.019) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.967^{**}(0.382) $</td><td style='text-align: center; word-wrap: break-word;'>$ -1.135^{***}(0.432) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta f_{t-1} $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>5.788(4.394)</td><td style='text-align: center; word-wrap: break-word;'>5.419(8.601)</td><td style='text-align: center; word-wrap: break-word;'>0.168(0.329)</td><td style='text-align: center; word-wrap: break-word;'>-0.0549(0.325)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Credit growth $ _{t} $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.0114(0.00867)</td><td style='text-align: center; word-wrap: break-word;'>-0.000767(0.00613)</td><td style='text-align: center; word-wrap: break-word;'>-0.00113(0.000728)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Credit growth $ _{t-1} $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.0312^{***}(0.00925)</td><td style='text-align: center; word-wrap: break-word;'>0.00258^{**}(0.00115)</td><td style='text-align: center; word-wrap: break-word;'>0.00202^{*}(0.00119)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Country FE</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Year FE</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Observations</td><td style='text-align: center; word-wrap: break-word;'>1,052</td><td style='text-align: center; word-wrap: break-word;'>1,044</td><td style='text-align: center; word-wrap: break-word;'>709</td><td style='text-align: center; word-wrap: break-word;'>709</td><td style='text-align: center; word-wrap: break-word;'>709</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.00971</td><td style='text-align: center; word-wrap: break-word;'>0.0129</td><td style='text-align: center; word-wrap: break-word;'>0.0494</td><td style='text-align: center; word-wrap: break-word;'>0.03</td><td style='text-align: center; word-wrap: break-word;'>0.354</td></tr></table>

We report regressions of banking crisis indicators on lagged finance sentiment changes and credit growth. Banking crises defined in Baron, Verner, and Xiong (2021) represent banking equity declines a 30% for each country in a year. Credit growth is loan growth as defined in Schularick and Taylor (2012). Model specifications with credit growth exclude China and Russia as credit data of these two countries are unavailable. Finance sentiment is standardized to have a mean of zero and a standard deviation of one. Bootstrap robust standard errors are in parentheses for logistic regression models and Driscoll-Kraay standard errors for linear probability models. *p<0.1; **p<0.05; ***p<0.01.

<div style="text-align: center;"><div style="text-align: center;">Alternative definitions of banking crises</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Logistic regression</td><td style='text-align: center; word-wrap: break-word;'>Panic $ _{t+1} $ (1)</td><td style='text-align: center; word-wrap: break-word;'>Bank failure $ _{t+1} $ (2)</td><td style='text-align: center; word-wrap: break-word;'>Bank equity crisis $ _{t+1} $ (3)</td><td style='text-align: center; word-wrap: break-word;'>BVX crisis $ _{t+1} $ (4)</td><td style='text-align: center; word-wrap: break-word;'>JST crisis $ _{t+1} $ (5)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta f_{t} $</td><td style='text-align: center; word-wrap: break-word;'>$ -15.05^{**}(6.047) $</td><td style='text-align: center; word-wrap: break-word;'>$ -15.80^{*}(9.113) $</td><td style='text-align: center; word-wrap: break-word;'>$ -18.42^{*}(10.79) $</td><td style='text-align: center; word-wrap: break-word;'>$ -14.33^{**}(6.204) $</td><td style='text-align: center; word-wrap: break-word;'>0.770 (6.640)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta f_{t-1} $</td><td style='text-align: center; word-wrap: break-word;'>5.464 (22.23)</td><td style='text-align: center; word-wrap: break-word;'>7.724 (24.19)</td><td style='text-align: center; word-wrap: break-word;'>15.82 (16.46)</td><td style='text-align: center; word-wrap: break-word;'>6.307 (20.67)</td><td style='text-align: center; word-wrap: break-word;'>15.97 (9.923)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Credit growth $ _{t} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.0156(0.0190) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.0264(0.0175) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.0236(0.0183) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.0163(0.0174) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.0132(0.0151) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Credit growth $ _{t-1} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.0421^{**}(0.0212) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.0524^{**}(0.0213) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.0523^{**}(0.0136) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.0429^{**}(0.0203) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.0424^{*}(0.0249) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Country FE</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Observations</td><td style='text-align: center; word-wrap: break-word;'>709</td><td style='text-align: center; word-wrap: break-word;'>709</td><td style='text-align: center; word-wrap: break-word;'>709</td><td style='text-align: center; word-wrap: break-word;'>709</td><td style='text-align: center; word-wrap: break-word;'>709</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.0730</td><td style='text-align: center; word-wrap: break-word;'>0.106</td><td style='text-align: center; word-wrap: break-word;'>0.131</td><td style='text-align: center; word-wrap: break-word;'>0.0729</td><td style='text-align: center; word-wrap: break-word;'>0.0662</td></tr></table>

We report regressions of banking crisis indicators on lagged finance sentiment changes and credit growth. For robustness, we consider several definitions of banking crises defined in Baron, Verner, and Xiong (2021). Credit growth is a defined in Schulman and Taylor (2012). Model specifications with credit growth exclude China and Russia as credit data of these two countries are unavailable. Finance sentiment is standardized to have a mean of zero and a standard deviation of one. Bootstrap robust standard errors are in parentheses. *p < 0.1; **p < 0.05; ***p < 0.01

Downloaded from https://academic.oup.com/rfs/advance-article/doi/10.1093/rfs/hha012/8045328 by Zhejiang University user on 23 October 2025

and credit growth.  $ \alpha_{i}^{h} $ are country fixed effects.  $ \Delta f_{i,t} $ represents the percentage change of the first difference in finance sentiment, referred to as finance sentiment throughout this section.  $ X_{i,t} $ is a vector of control variables, and  $ \epsilon_{i,t+h} $ are disturbance terms.

We are mainly interested in estimating the response of output and credit  $ \Delta_{h}y_{i,t+h} $ to a shock to finance sentiment  $ \Delta f_{i,t} $. To capture the direct link of such shocks to economic growth, we control for the first three lags of credit growth and finance sentiment. Similarly, the first three lags of economic growth and finance sentiment are control variables when credit growth is our target variable.

The results in Figure 6 include all countries in the sample and therefore focus on GDP and finance sentiment alone because no credit data is available for China or Russia. The bottom left panel shows that a 1 percentage point increase in finance sentiment increases GDP growth by about 0.3 percentage points 4 years out, though it has no contemporaneous effect. This effect is quite large compared to the mean annual GDP growth of 2.1% in this sample.

The top right panel shows that increases in output tend to coincide with declines in finance sentiment growth. Although the latter effect is statistically different from zero, its economic magnitude is quite modest.

Interestingly, the bottom right panel reveals that finance sentiment tends to oscillate after shocks. This is somewhat surprising, as we expected it to gradually mean-revert like GDP growth does on the top left panel. These oscillations could be the result of book writers and publishers trying to continuously innovate with contrarian books.

It is likely, however, that finance sentiment affects economic growth not directly, but indirectly, by changing the demand for financial services. It may also affect the supply of financial services by changing the way the sector is regulated. Both mechanisms should manifest as changes in the amount of credit. To investigate this channel, we focus next on the sub-sample of advanced economies for which we have credit data.

Figure 7 depicts the response of economic growth, finance sentiment, and credit growth to shocks by the same 3 variables. Regardless of the oscillating impact of finance sentiment, the cumulative response to the shock in finance sentiment is positive for both economic growth and credit growth after a year. A 1 percentage point increase in finance sentiment is associated with a 0.4 percentage point increase in credit growth. The addition of credit growth also reduces somewhat the impulse response of GDP to finance sentiment. It therefore seems that some, but not all, of the effect of finance sentiment on GDP is through credit growth.

### 5.3 Prolonged sentiment and credit expansions

The result that shocks to finance sentiment relate positively to future output growth is potentially surprising given recent work finding that credit expansions are followed by severe economic and financial crises (e.g.,

<div style="text-align: center;"><div style="text-align: center;">(a)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//94b3d71b-e449-4ebb-89be-e256b0c9a035/markdown_1/imgs/img_in_chart_box_154_100_454_398.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A57Z%2F-1%2F%2F797565d71d642301597c52af995469bcde510359b04f798e9c0804ba87d5152f" alt="Image" width="34%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//94b3d71b-e449-4ebb-89be-e256b0c9a035/markdown_1/imgs/img_in_chart_box_456_101_751_394.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A57Z%2F-1%2F%2F5bec36afbc3c07f64f55147b6ef9eb79976cfce81c9fbd55ec3bbabf49a36723" alt="Image" width="34%" /></div>


<div style="text-align: center;"><div style="text-align: center;">GDP growth shock</div> </div>


<div style="text-align: center;"><div style="text-align: center;">(b)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//94b3d71b-e449-4ebb-89be-e256b0c9a035/markdown_1/imgs/img_in_chart_box_154_425_457_727.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A57Z%2F-1%2F%2F57a9a647de88427c064d3973b8b0f26dd6c0b90e41dca978ef1c678edcc4a919" alt="Image" width="35%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//94b3d71b-e449-4ebb-89be-e256b0c9a035/markdown_1/imgs/img_in_chart_box_456_426_751_719.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A57Z%2F-1%2F%2Fb182ef5607f294797e057e007971a8d1a800c31d9c31adfb21ffaf85d0f9c35c" alt="Image" width="34%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Finance sentiment shock</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Figure 6</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Impulse responses of output and finance sentiment</div> </div>


Impulse responses estimated via local projections indicate the change of the cumulative response to a one percentage point shock. Bands are 90% confidence intervals based on Driscoll and Kraay nonparametric robust standard errors.

ALT TEXT: Impulse responses of GDP and finance sentiment to shocks. Panels illustrate the cumulative responses in GDP growth and finance sentiment over 10 years following a one percentage point shock, with confidence bands representing estimated error margins.

Schularick and Taylor 2012). Part of the reason for this potential difference is the length of the expansion examined. As Figure 6(b) shows, finance sentiment tends to oscillate, so an increase in finance sentiment in 1 year tends to lead to a decline in the next. A prolonged expansion in finance sentiment therefore requires the initial shock to overcome the tendency to revert.

To study how longer expansion periods of finance sentiment relate to economic growth, we follow Mian, Sufi, and Verner (2017), who show that increases in household debt to GDP ratios predict lower GDP growth and higher unemployment using a panel of 30 countries from 1960 to 2012.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//94b3d71b-e449-4ebb-89be-e256b0c9a035/markdown_2/imgs/img_in_chart_box_139_99_346_298.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A59Z%2F-1%2F%2F4e625b505381d4b79acfc30a6881272efd16ed602e4a2caa2fe605770e6b6a47" alt="Image" width="24%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//94b3d71b-e449-4ebb-89be-e256b0c9a035/markdown_2/imgs/img_in_chart_box_348_101_544_296.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A59Z%2F-1%2F%2F590069bae65a6b276da35b688bf070d8039daffb7d296c8c335c5df03185fa34" alt="Image" width="22%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//94b3d71b-e449-4ebb-89be-e256b0c9a035/markdown_2/imgs/img_in_chart_box_543_100_739_296.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A59Z%2F-1%2F%2F179607d8bb6ce74c10c1f4ea2acce381fb1cc45214dd93967d5c746d6ecf3087" alt="Image" width="22%" /></div>


<div style="text-align: center;"><div style="text-align: center;">GDP growth shock</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//94b3d71b-e449-4ebb-89be-e256b0c9a035/markdown_2/imgs/img_in_chart_box_138_322_348_524.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A59Z%2F-1%2F%2F3d6a216a62c0b0f229a93dfd71014222f20713dab16db20b55d7c203257c756f" alt="Image" width="24%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//94b3d71b-e449-4ebb-89be-e256b0c9a035/markdown_2/imgs/img_in_chart_box_348_327_544_525.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A59Z%2F-1%2F%2F9d673b1fb6e385e64cc348a4b462145289a84e9d3cd7d2ab4fd49b1a925b873f" alt="Image" width="22%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//94b3d71b-e449-4ebb-89be-e256b0c9a035/markdown_2/imgs/img_in_chart_box_543_325_739_520.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A59Z%2F-1%2F%2F545c010468fce0b79ea7c7ffa1390d752c2ae875ec3c5288be51a212c6a53244" alt="Image" width="22%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(c)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//94b3d71b-e449-4ebb-89be-e256b0c9a035/markdown_2/imgs/img_in_chart_box_141_546_350_752.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A59Z%2F-1%2F%2Ff8dc5fb77e7c2abb5dc343f54bc9e2ec1f90f575dbc0f6d842304eb2934de7fd" alt="Image" width="24%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//94b3d71b-e449-4ebb-89be-e256b0c9a035/markdown_2/imgs/img_in_chart_box_348_548_546_769.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A00Z%2F-1%2F%2F1f6404da9e41e1daff4fb5df7d4465b6913da9e66ce0d39341404648c6dfc6c4" alt="Image" width="22%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//94b3d71b-e449-4ebb-89be-e256b0c9a035/markdown_2/imgs/img_in_chart_box_544_548_739_745.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A58%3A00Z%2F-1%2F%2Fa82ad9c7571ed4443decb5c16e2655a418f3a49ce4ed7b4be7d1d682f607345b" alt="Image" width="22%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 7</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Impulse responses of output, sentiment, and credit (without China and Russia)</div> </div>


Impulse responses estimated via local projections indicate the change of the cumulative response to a 1 percentage point shock. Bands are 90% confidence intervals based on Driscoll and Kraay nonparametric robust standard errors.

ALT TEXT: Impulse responses of output, finance sentiment, and credit growth, excluding China and Russia. Panels show responses in GDP, finance sentiment, and credit growth to various economic shocks over 10 years, with confidence intervals reflecting statistical robustness.

They further show that this negative relation is stronger for countries with less flexible exchange rate regimes.

We divide our sample into fixed exchange rate regimes and flexible regimes. Specifically, the classification of exchange rate regimes for China follows Das (2019) and Si (2014), while for Russia, it is based on Central Bank of the Russian Federation (2014). In order to capture the response of economic growth preceding the finance sentiment and credit expansion, we generate the cumulative finance sentiment differences  $ \Delta f_{t-3\to t} $ and, following

<div style="text-align: center;"><div style="text-align: center;">Table 10 Prolonged sentiment and credit expansions and exchange rate regimes</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2">Regime</td><td colspan="3">GDP growth $ _{t+1} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Full sample (1)</td><td style='text-align: center; word-wrap: break-word;'>Fixed (2)</td><td style='text-align: center; word-wrap: break-word;'>Flexible (3)</td></tr><tr><td rowspan="2">$ \Delta f_{t-3\rightarrow t} $</td><td style='text-align: center; word-wrap: break-word;'>$ -15.20^{**} $</td><td style='text-align: center; word-wrap: break-word;'>$ -18.84^{*} $</td><td style='text-align: center; word-wrap: break-word;'>$ -18.11^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(6.44)</td><td style='text-align: center; word-wrap: break-word;'>(9.77)</td><td style='text-align: center; word-wrap: break-word;'>(9.48)</td></tr><tr><td rowspan="2">$ \Delta d_{t-3\rightarrow t}^{HH} $</td><td style='text-align: center; word-wrap: break-word;'>0.03^{***}</td><td style='text-align: center; word-wrap: break-word;'>0.05^{**}</td><td style='text-align: center; word-wrap: break-word;'>0.02</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.02)</td><td style='text-align: center; word-wrap: break-word;'>(0.01)</td></tr><tr><td rowspan="2">$ \Delta d_{t-3\rightarrow t}^{F} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.02 $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.03 $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.02 $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.03)</td><td style='text-align: center; word-wrap: break-word;'>(0.01)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Country FE</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Obs</td><td style='text-align: center; word-wrap: break-word;'>407</td><td style='text-align: center; word-wrap: break-word;'>163</td><td style='text-align: center; word-wrap: break-word;'>188</td></tr></table>

This table reports regressions of future GDP growth on prolonged expansions of financial sentiment and credit. We consider both household and firm debt as proxy variables for credit expansions. Following Mian, Sufi, and Verner (2017), we define  $ \Delta d_{t-3 \to t}^{HH} $ as the cumulative growth of household debt over GDP over 3 years and  $ \Delta d_{t-3 \to t}^{F} $ as the cumulative growth of firm debt over GDP over 3 years, respectively. Column 1 reports the results for the full sample, while columns 2 and 3 report the results for the fixed exchange regime and the flexible regime (intermediate and freely floating), respectively. All regressions include country fixed effects. Driscoll and Kraay nonparametric robust standard errors, clustered by country, are reported in parentheses.

Mian, Sufi, and Verner (2017), we define  $ \Delta d_{t-3\to t}^{\mathrm{HH}} $ as the cumulative growth of household debt over GDP over 3 years and  $ \Delta d_{t-3\to t}^{\mathrm{F}} $ as the cumulative growth of firm debt over GDP over 3 years, respectively.

Column 1 of Table 10 shows that prolonged finance sentiment expansions are negatively correlated with GDP growth, consistent with the findings of Mian, Sufi, and Verner (2017, Table IX), even after controlling for the macroeconomic variables they study, namely household debt and private credit expansions. Columns 2 and 3 of Table 10 show that this relationship is similar in magnitude and significance regardless of the exchange rate regime that coincides with these expansions. Although it is possible that the narrower panel of countries that we study is different from Mian, Sufi, and Verner (2017), these findings suggest that finance sentiment expansions are distinct from household credit expansions in their ability to predict economic growth.

## 6. Discussion

Having described our main empirical results, we pause to clarify what these results mean and what they do not.

### 6.1 Limitations of cross-language and country comparisons

The most striking fact that we uncover in Figure 2 is the considerable variation in finance sentiment across languages and its strong persistence over time. No measure is perfect and neither is our language-based one. What else besides sentiment toward finance could be driving this cross-language variation?

One potential source of measurement error is our choice of language-specific stem words and the sentences we use to determine the positive dimension of finance sentiment. Our guiding principle is to choose the most natural

translations, but it is possible that several stems are in fact needed to capture attitude toward finance. For example, consider Germans and Italians, who live in bank-centric systems. If they have a more negative perception of banks compared to the stock market and use the term "finanz" primarily in reference to banks, then the consistently lower finance sentiment observed for these countries might be influenced by the exclusion of instances where finance is portrayed more positively, due to the preference for referring to it as banks rather than finance. This concern is valid and, in fact, cross-country comparisons are often problematic because many characteristics differ across borders and cultures.

We offer two pieces of evidence that such measurement error is unlikely to explain away our findings. First, in Internet Appendix E, we show that using a broader definition of finance that relies on "bank" mentions as well does not materially change our main results. Second, in our tests where finance sentiment is related to outcomes with sufficient sample coverage, and therefore statistical power, we include country fixed effects that would absorb such country-specific measurement error as long as it is stable over time. For example, our results relating finance sentiment to financial crises, economic output, and credit use, all focus on within-country variation. Thus, these results are unlikely to be driven by unobserved cross-country heterogeneity.

### 6.2 Does finance sentiment affect economic outcomes?

For policy analysis, the causal identification of the effects of finance sentiment is often the ultimate goal. Our paper, however, cannot claim to identify such causal effects because that requires exogenous variation in finance sentiment. Moreover, such variation would have to plausibly affect economic outcomes only through the finance sentiment channel. These requirements are hard to satisfy in most macroeconomic studies because in these complex systems, even if an exogenous shock is found, it often works through multiple competing channels that prevent identification.

Our more modest goal here is to provide an accurate and comprehensive measure of finance sentiment and to study its variation across languages and over time. Nonetheless, our evidence can alleviate some natural concerns about identification. For example, one concern when we relate finance sentiment to capitalism attitudes is that both are being driven by unobserved time-varying economic shocks like business cycles. Such shocks, however, are unlikely to explain the systematic cross-sectional variation of finance sentiment across countries (see Figure 2). The persistent variation across countries is unlikely to be driven by business cycle fluctuations, which we control for in our tests (see Table 5). Our results instead suggest that finance sentiment captures more deep-rooted and slow-moving cultural attitudes.

It is also possible that these cultural differences are in turn co-determined with other unobserved country characteristics like institutions (Mokyr 2016) and legal origins (La Porta et al., 1998). Such codetermination could explain the

correlation we document between finance sentiment and capitalism attitudes. We find these alternative drivers, however, just as plausible as finance sentiment as the ultimate driver of economic outcomes.

Consistent with finance sentiment affecting economic decision-making, D'Acunto (2020) shows in a controlled experiment that exposure to anti-finance rhetoric diminishes trust in and demand for financial instruments and institutions. Moreover, it finds that educated, experienced, and female subjects are affected more by anti-finance rhetoric, suggesting that finance sentiment is likely to affect investors.

D'Acunto's (2020) field experiment provides the cleanest evidence of causal effects of finance sentiment we are aware of and complements our observational analysis. While we believe that measuring finance sentiment over time and across languages is an important first step, teasing out the causal effects of finance sentiment on particular outcomes remains a promising avenue for future research.

## 7. Conclusion

We measure popular sentiment toward finance using a computational linguistics approach applied to millions of books published in eight countries over hundreds of years, and document several new facts.

Finance sentiment differences across countries mostly persist throughout our long sample, with the exception of China, which exhibits greater volatility and a level of finance sentiment about as positive as that of Italy and France. Books written in languages of more capitalist countries discuss finance in a more positive context. Finance sentiment declines 1 year before periods of banking distress. Using local projections, we find that shocks to finance sentiment are followed by greater long-term output and credit growth.

In follow-up work, we investigate the origins of finance sentiment fluctuations, and in particular, how finance sentiment responds to natural disasters (Jha, Liu, and Manela 2021). The long panel of finance sentiment that we provide could also be used in future work to understand other consequences of finance sentiment variation. For example, combining our methods and data with the fraud-based identification approach of Giannetti and Wang (2016) and Gurun, Stoffman, and Yonker (2018) would be interesting. Further analysis of sentiment toward other industries, such as the ones we explore in Figure 4, could be another promising avenue for future research. More generally, the language embedding-based approach we develop could prove useful for other text-based measures that are of interest to economists.

Code Availability: The replication code is available in the Harvard Dataverse at: https://doi.org/10.7910/DVN/ZRSGXQ

## References

Altszyler, E., M. Sigman, S. Ribeiro, and D. F. Slezak. 2017. Comparative study of lsa vs. word2vec embeddings in small corpora: A case study in dreams database. Consciousness and Cognition 56:178–87.

Antweiler, W., and M. Z. Frank. 2004. Is all that talk just noise? the information content of internet stock message boards. Journal of Finance 59:1259–93.

Baker, S. R., N. Bloom, and S. J. Davis. 2016. Measuring economic policy uncertainty. Quarterly Journal of Economics 131:1593–636.

Baron, M., and T. Muir. 2022. Intermediaries and asset prices: International evidence since 1870. Review of Financial Studies 35:2144–89.

Baron, M., E. Verner, and W. Xiong. 2021. Banking crises without panics*. Quarterly Journal of Economics 136:51–113.

Barro, R. J., and J. F. Ursua. 2010. Barro-ursua macroeconomic data. Working paper, Harvard University.

Bodnaruk, A., T. Loughran, and B. McDonald. 2015. Using 10-K text to gauge financial constraints. Journal of Financial and Quantitative Analysis 50:623–46.

Bojanowski, P., E. Grave, A. Joulin, and T. Mikolov. 2017. Enriching word vectors with subword information. Transactions of the Association for Computational Linguistics 5:135–46.

Boudoukh, J., R. Feldman, S. Kogan, and M. Richardson. 2018. Information, trading, and volatility: Evidence from firm-specific news, and volatility. Review of Financial Studies.

Bybee, L., B. Kelly, A. Manela, and D. Xiu. 2024. Business news and business cycles. Journal of Finance 79:3105–47.

Central Bank of the Russian Federation. 2014. The history of the bank of Russia's exchange rate policy. Working Paper 2474433, Social Science Research Network.

Chava, S., W. Du, and N. Paradkar. 2021. More than buzzwords? firms' discussions of emerging technologies in earnings conference calls. Working Paper 3862645, Social Science Research Network.

Chen, J., and S. Sarkar. 2020. A semantic approach to financial fundamentals. In Proceedings of the Second Workshop on Financial Technology and Natural Language Processing, 22–26, Kyoto, Japan.

Cieslak, A., and A. Vissing-Jorgensen. 2020. The economics of the Fed put. Review of Financial Studies 34:4045–89.

Cookson, J. A., J. E. Engelberg, and W. Mullins. 2022. Echo chambers. Review of Financial Studies 36:450–500.

D'Acunto, F. 2020. Tear down this Wall Street: Anti-finance rhetoric, subjective beliefs, and investment. Working Paper 3213904, Social Science Research Network.

D'Acunto, F., M. Prokopczuk, and M. Weber. 2019. Historical antisemitism, ethnic specialization, and financial development. Review of Economic Studies 86:1170–206.

Das, M. S. 2019. China’s evolving exchange rate regime. Working Paper 2019/050, International Monetary Fund.

Devlin, J., M.-W. Chang, K. Lee, and K. Toutanova. 2018. BERT: Pre-training of deep bidirectional transformers for language understanding. arXiv preprint, https://arxiv.org/abs/1810.04805.

Di Tella, R., and R. Macculloch. 2009. Why doesn't capitalism flow to poor countries? Brookings Papers on Economic Activity 2009:285–321.

Dim, C., F. Sangiorgi, and G. Vilkov. 2023. Media narratives and price informativeness. Working Paper 4323093, Social Science Research Network.

Driscoll, J. C., and A. C. Kraay. 1998. Consistent covariance matrix estimation with spatially dependent panel data. Review of Economics and Statistics 80:549–60.

Engelberg, J., M. Henriksson, A. Manela, and J. Williams. 2023. The partisanship of financial regulators. Review of Financial Studies 36:4373–416.

Favilukis, J. 2013. Inequality, stock market participation, and the equity premium. Journal of Financial Economics 107:740–59.

Firth, J. R. 1957. Applications of general linguistics. Transactions of the Philological Society 56:1–14.

Galofré-Vila, G., C. Meissner, M. McKee, and D. Stuckler. 2021. Austerity and the rise of the Nazi Party. Journal of Economic History 81:81–113.

García, D. 2013. Sentiment during recessions. Journal of Finance 68:1267–300.

Gennaioli, N., R. La Porta, F. Lopez-de-Silanes, and A. Shleifer. 2022. Trust and Insurance Contracts. Review of Financial Studies 35:5287–333.

Gentzkow, M., E. L. Glaeser, and C. Goldin. 2006. The rise of the fourth estate. how newspapers became informative and why it mattered. Working Paper, National Bureau of Economic Research.

Gentzkow, M., B. Kelly, and M. Taddy. 2019. Text as data. Journal of Economic Literature 57:535–74.

Gentzkow, M., and J. M. Shapiro. 2010. What drives media slant? evidence From U.S. daily newspapers. Econometrica 78:35–71.

Giannetti, M., and T. Y. Wang. 2016. Corporate scandals and household stock market participation. Journal of Finance 71:2591–636.

Goetzmann, W., D. Kim, and R. J. Shiller. 2017. Affect, media and earthquakes: Determinants of crash beliefs from investor surveys. Working Paper, Yale University.

Goetzmann, W. N., D. Kim, and R. J. Shiller. 2016. Crash beliefs from investor surveys. National Bureau of Economic Research Working Paper 22143. doi:10.3386/w22143.

___. 2022. Crash narratives. Working Paper 4153089, Social Science Research Network.

Goldman, E., N. Gupta, and R. Israelsen. 2024. Political polarization in financial news. Journal of Financial Economics 155:103816–.

Grennan, J. 2019. A corporate culture channel: How increased shareholder governance reduces firm value. Working Paper 2345384, Social Science Research Network.

Guiso, L., P. Sapienza, and L. Zingales. 2006. Does culture affect economic outcomes? Journal of Economic Perspectives 20:23–48.

___. 2008. Trusting the stock market. Journal of Finance 63:2557–600.

Gurun, U. G., N. Stoffman, and S. E. Yonker. 2018. Trust busting: The effect of fraud on investor behavior. Review of Financial Studies 31:1341–76.

Hanley, K. W., and G. Hoberg. 2019. Dynamic interpretation of emerging risks in the financial sector. Review of Financial Studies 32:4543–603.

Hansen, S., M. McMahon, and A. Prat. 2018. Transparency and deliberation within the fomc: A computational linguistics approach. Quarterly Journal of Economics 133:801–70.

Harris, Z. S. 1954. Distributional structure. WORD 10:146–62.

Hassan, T. A., S. Hollander, L. van Lent, and A. Tahoun. 2019. Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics 134:2135–202.

Hills, T. T., E. Proto, D. Sgroi, and C. I. Seresinhe. 2019. Historical analysis of national subjective wellbeing using millions of digitized books. Nature Human Behaviour 3:1271–75.

Hoberg, G., and G. Phillips. 2016. Text-based network industries and endogenous product differentiation. Journal of Political Economy 124:1423–65.

Jha, M., H. Liu, and A. Manela. 2021. Natural disaster effects on popular sentiment toward finance. Journal of Financial and Quantitative Analysis 56:2584–2604.

Jordà, Ô. 2005. Estimation and inference of impulse responses by local projections. American Economic Review 95:161–82.

Jordà, Ô., M. Schularick, and A. M. Taylor. 2017. Macrofinancial history and the new business cycle facts. NBER Macroeconomics Annual 31:213–63.

Joulin, A., E. Grave, P. Bojanowski, and T. Mikolov. 2016. Bag of tricks for efficient text classification. arXiv preprint, https://arxiv.org/abs/1607.01759 1607.

Ke, Z. T., B. T. Kelly, and D. Xiu. 2019. Predicting returns with text data. Working Paper 26186, National Bureau of Economic Research.

Kozlowski, A. C., M. Taddy, and J. A. Evans. 2019. The geometry of culture: Analyzing the meanings of class through word embeddings. American Sociological Review 84:905–49.

Krishnamurthy, A., and T. Muir. Forthcoming. How credit cycles across a financial crisis. Journal of Finance.

La Porta, R., F. Lopez-de-Silanes, A. Shleifer, and R. Vishny. 1998. Law and finance. Journal of Political Economy 106:1113–55.

Levine, R., C. Lin, and W. Xie. 2020. The african slave trade and modern household finance. Economic Journal 130:1817–41.

Lin, Y., J.-B. Michel, E. Aiden Lieberman, J. Orwant, W. Brockman, and S. Petrov. 2012. Syntactic annotations for the Google Books NGram Corpus. In Proceedings of the ACL 2012 System Demonstrations, 169–74. Jeju Island, Korea: Association for Computational Linguistics.

Lopez Lira, A. 2023. Risk factors that matter: Textual analysis of risk disclosures for the cross-section of returns. Working Paper 3313663, Social Science Research Network.

Loughran, T., and B. McDonald. 2020. Textual analysis in finance. Annual Review of Financial Economics 12:357–75.

Luo, M., A. Manconi, and M. Massa. 2023. Political affiliation and media distrust: Evidence from stock market investors. Working Paper 2879939, Social Science Research Network.

Magness, P., and M. Makovi. 2022. The mainstreaming of marx: Measuring the effect of the Russian revolution on Karl Marx's influence. Journal of Political Economy.

Manela, A., and A. Moreira. 2017. News implied volatility and disaster concerns. Journal of Financial Economics 123:137–62.

McCloskey, D. N. 2016. Bourgeois equality: How ideas, not capital or institutions, enriched the world. University of Chicago Press.

Mian, A., A. Sufi, and E. Verner. 2017. Household debt and business cycles worldwide. The Quarterly Journal of Economics 132:1755–817.

Michel, J.-B., Y. K. Shen, A. P. Aiden, A. Veres, M. K. Gray, J. P. Pickett, D. Hoiberg, and et al 2011. Quantitative analysis of culture using millions of digitized books. Science 331:176–82.

Mikolov, T., K. Chen, G. Corrado, and J. Dean. 2013. Efficient Estimation of Word Representations in Vector Space. arXiv preprint, https://arxiv.org/abs/1301.3781.

Mikolov, T., K. Chen, G. S. Corrado, and J. A. Dean. 2015. Computing numeric representations of words in a high-dimensional space. Patent US9037464B1, Google LLC.

Mikolov, T., W. Yih, and G. Zweig. 2013. Linguistic regularities in continuous space word representations. In Proceedings of the 2013 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, 746–51. Atlanta, Georgia: Association for Computational Linguistics.

Mokyr, J. 2016. A culture of growth: The origins of the modern economy. Princeton, NJ: Princeton University Press.

OpenAI. 2024. Gpt-4 technical report. Working Paper.

Oxford English Dictionary. 2022. Finance, n. $ ^{1} $ meanings, etymology and more. Oxford: Oxford University Press.

Pennington, J., R. Socher, and C. Manning. 2014. GloVe: Global vectors for word representation. In Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing (EMNLP), 1532–43. Doha, Qatar: Association for Computational Linguistics.

Perone, C. S., R. Silveira, and T. S. Paula. 2018. Evaluation of sentence embeddings in downstream and linguistic probing tasks. arXiv preprint, https://arxiv.org/abs/1806.06259.

Sapienza, P., and L. Zingales. 2012. A trust crisis. International Review of Finance 12:123–31.

___. 2013. Economic experts versus average americans. American Economic Review 103:636–42.

Schularick, M., and A. M. Taylor. 2012. Credit booms gone bust: Monetary policy, leverage cycles, and financial crises, 1870–2008. American Economic Review 102:1029–61.

Sheng, J. 2019. Asset pricing in the information age: Employee expectations and stock returns. Working Paper 3321275, Social Science Research Network.

Si, W. 2014. Evolution of rmb exchange rate regime. Working Paper 2543400, Social Science Research Network.

Soo, C. K. 2018. Quantifying sentiment with news media across local housing markets. Review of Financial Studies 31:3689–719.

Spolaore, E., and R. Wacziarg. 2013. How deep are the roots of economic development? Journal of Economic Literature 51:325–69.

Stulz, R. M., and R. Williamson. 2003. Culture, openness, and finance. Journal of Financial Economics 70:313–49.

Tetlock, P. C. 2007. Giving content to investor sentiment: The role of media in the stock market. Journal of Finance 62:1139–68.

Vaswani, A., N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser, and I. Polosukhin. 2017. Attention is all you need. arXiv preprint, https://arxiv.org/abs/1706.03762.

Zhou, G. 2018. Measuring investor sentiment. Annual Review of Financial Economics 10:239–59.

Zingales, L. 2012. A capitalism for the people: Recapturing the lost genius of american prosperity. Basic Books, New York.

—2015. Presidential address: Does finance benefit society? Journal of Finance 70:1327–63.

