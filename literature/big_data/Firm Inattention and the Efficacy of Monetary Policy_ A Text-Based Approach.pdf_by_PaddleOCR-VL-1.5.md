Review of Economic Studies (2025) 92, 3438–3469 https://doi.org/10.1093/restud/rdae102

© The Author(s) 2024. Published by Oxford University Press on behalf of The Review of Economic Studies Limited. All rights reserved. For commercial re-use, please contact reprints@oup.com for reprints and translation rights for reprints. All other permissions can be obtained through our RightsLink service via the Permissions link on the article page on our site—for further information please contact journals.permissions@oup.com. Advance access publication 23 October 2024

# Firm Inattention and the Efficacy of Monetary Policy: A Text-Based Approach

Wenting Song

Bank of Canada, Canada

and

Samuel Stern

University of Michigan, USA

First version received November 2021; Editorial decision April 2024; Accepted October 2024 (Eds.)

This paper provides empirical evidence of the importance of firm attention to macroeconomic dynamics. We construct a text-based measure of attention to macroeconomic news and document that attention is polarized across firms and countercyclical. Differences in attention lead to asymmetric responses to monetary policy: expansionary monetary shocks raise the market values of attentive firms more than those of inattentive firms, and contractionary shocks lower the values of attentive firms by less. Attention also mitigates the effects of macroeconomic uncertainty on firm performance. In a quantitative rational inattention model that is calibrated with this new text-based measure, inattention drives monetary non-neutrality. As average attention varies over the business cycle, so does the efficacy of monetary policy.

Key words: Rational inattention, Monetary policy, Natural language processing

JEL codes: D83, E44, E52

## 1. INTRODUCTION

Public information often goes unused because attention is scarce. Rational inattention models pioneered by Sims (2003) and a broader set of incomplete-information models (Mankiw and Reis 2002; Woodford 2009) consider firm managers who gather information to maximize value while facing cognitive costs of processing information. Inattention provides an intuitive micro-foundation for monetary non-neutrality, yet empirically assessing the importance of attention is challenging because neither a firm’s allocation of attention nor information-processing costs are readily observable.

This paper provides some of the first empirical evidence of the importance of firm attention to macroeconomic dynamics using a novel text-based measure. We document countercyclical firm attention and uncover substantial heterogeneity in attention across firms. Moreover, our measure is consistent with the asymmetric prediction of inattention models that attentive firms exhibit higher profit semi-elasticities in response to expansionary monetary shocks and lower semi-elasticities following contractionary shocks. We then use this measure to study the macroeconomic implications of firm attention. Empirically, we find that attention mitigates the effects of macroeconomic uncertainty on firms' long-term performance. Quantitatively, we use this measure to calibrate information costs in a general equilibrium model with rationally inattentive firms. Firm inattention generates monetary non-neutrality and is a source of state dependence in monetary policy.

To construct our attention measure, we compile a corpus based on approximately 200,000 annual SEC filings of U.S. publicly traded firms and search each document for macroeconomic keywords. We define two measures of attention: “prevalence,” whether firm managers discuss macro conditions at all, and “intensity,” the frequency with which managers discuss macro conditions. Our text-based classification of firm attention passes a number of sense checks: topic-specific attention is concentrated by industry; firms in more attentive industries adjust prices faster in response to monetary shocks; and attentive firms predict macro and firm-specific variables better in surveys.

We document two stylized facts about firm attention. First, firm attention is polarized. The majority of firms in our sample either mention macroeconomic conditions in every filing or in none of their filings. Second, attention is countercyclical. Among the remaining firms with time-varying attention, the number of firms that referenced macroeconomic news rose notably during recessions. We also study potential drivers of firm attention, which include firm characteristics and macroeconomic uncertainty.

Our main empirical result validates our text-based measure by testing for asymmetry in firm performance that is predicted by inattention models: following a macroeconomic shock, the responses of firms with greater information-processing capacity should be closer to the optimal response regardless of the shock's direction. Therefore, attentive firms should exhibit higher profit elasticities in response to positive shocks and lower elasticities in response to negative shocks as they make decisions more accurately than inattentive competitors. We test for this asymmetry using an event-study design that exploits high-frequency variation in firms' market values around FOMC announcements. This test requires combining our prevalence attention measure with daily CRSP stock prices, quarterly Compustat firm financials (CCM 2020), and high-frequency monetary shocks (constructed as in Gürkaynak et al. 2005; Gorodnichenko and Weber 2016; Nakamura and Steinsson 2018).

Consistent with the theoretical prediction, expansionary monetary shocks raise stock returns of attentive firms by nearly 2% more than those of their inattentive peers, whereas contractionary shocks lower returns of attentive firms by 6% less. The suboptimal responses to monetary shocks by inattentive firms are direct evidence of the cost of inattentive behaviour. Moreover, the asymmetry is inconsistent with several common concerns about measuring firm attention with text analysis: concern that filings contain macroeconomic buzzwords as a form of cheap talk to appease investors would imply a zero effect; concern that firms mention keywords solely as a function of exposure to monetary policy would imply symmetric responses to monetary shocks; and concern that stock returns vary with investor attention rather than firm attention would also fail to produce an asymmetric response.

We then examine how attention affects firm performance under varying degrees of aggregate uncertainty. We construct an uncertainty index based on the Survey of Professional Forecasters and measure performance in three dimensions: profitability, financial performance, and survival.

The resulting estimates show that attentive firms outperform their inattentive competitors under increased uncertainty. Interestingly, attention appears to weakly reduce performance in low-uncertainty environments, which may hint at the cost of attention.

Finally, we present a quantitative rational inattention model calibrated using our new measure to study the aggregate implications of incomplete firm attention. In the model, firms with heterogeneous information costs optimally trade off between the precision of their signals of aggregate demand and the cost of acquiring and processing information. Consistent with our empirical findings, attentive firms have higher output semi-elasticities to expansionary monetary shocks and lower semi-elasticities to contractionary shocks. We incorporate observed countercyclicality of firm attention to show that the efficacy of monetary policy declines as the share of attentive firms rises and more firms set prices closer to the optimum. This new interpretation of attention-dependent monetary policy implies that central banks should expect policy interventions to be weaker when an aggregate shock has already drawn firm attention to macroeconomic policy.

Related Literature. Our paper contributes to four strands of literature. First, we contribute to the empirical literature on macroeconomic expectations by developing an ongoing, broad-based measure of firm attention that extends back to the mid-1990s. Recent literature has highlighted the importance of expectations for macroeconomic policy $ ^{1} $ and consequently the need for empirical measures. $ ^{2} $ Existing research has successfully measured attention in lab experiments (Reutskaja et al. 2011), field experiments (Bartoš et al. 2016; Fuster et al. 2022), and for individual consumers and banks (Macaulay 2020; Weitzner and Howes 2023). Our methodology complements those measures as well as survey-based evidence on firm expectations by Tanaka et al. (2020), Coibion et al. (2018), and Candia et al. (2024), and enables researchers to explore questions that lie outside the coverage of existing surveys.

Second, our findings lend empirical support to a broad body of theoretical work on incomplete information as a source of monetary non-neutrality (Mankiw and Reis 2002; Sims 2003; Woodford 2009). Microfoundations proposed in rational inattention and sticky information models are successful in explaining firm pricing (Maćkowiak and Wiederholt 2009; Afrouzi 2020; Yang 2022), asset prices (Van Nieuwerburgh and Veldkamp 2009), discrete choices (Matějka and McKay 2015; Caplin et al. 2019), aggregate dynamics (Maćkowiak and Wiederholt 2015; Afrouzi and Yang 2021a), and reconciling micro and macro evidence (Auclert et al. 2020). Our results estimate a substantial cost of information frictions in the U.S. data, providing empirical support for these theories.

Our findings on the relationship between countercyclical attention and monetary policy efficacy relates to existing literature on state dependencies of monetary policy. Tenreyro and Thwaites (2016) estimate non-linear responses in monetary policy that are weaker in recessions than in expansions. Vavra (2014), McKay and Wieland (2021), and Ottonello and Winberry (2020) consider volatility, durable consumption, and default risk as other channels through which state dependency arises. This paper suggests that attention may be an important source of state dependency of monetary policy.

Fourth, our paper relates to a broader and emerging literature that brings natural language processing techniques to economics. The seminal work of Loughran and McDonald (2011) applies the “bag of words” method to firm filings and develops word lists specific to economic and financial texts. Recent work has used textual analysis to study financial constraints

(Buehlmaier and Whited 2018), central bank communication (Hansen et al. 2018), firm-level political risk (Hassan et al. 2019), inflation expectation formation (Larsen et al. 2021), and uncertainty (Handley and Li 2020). We contribute to this literature by constructing a set of keyword dictionaries based on macroeconomic news releases that correspond to nine macroeconomic topics. While this paper focuses on attention to monetary policy, our method for measuring attention and its effects can be generalized to other macroeconomic topics.

In a related paper, Flynn and Sastry (2024) independently and contemporaneously develop a text-based measure of firm attention to macroeconomic topics. They show, like we do, that their measure is countercyclical. Whereas we show that the stock prices of more attentive firms rise relative to less attentive firms in response to both positive and negative monetary shocks, they compare firms' labour market choices to those of a neoclassical model with full information and show the gap between model and firm behaviour is negatively correlated with firm attention both over time and across firms. Together, our papers present compelling evidence that our text-based measures contain information that is useful in predicting economic outcomes and that these predictions are consistent with interpreting these measures as measures of attention.

Road map. The rest of the paper proceeds as follows: in Section 2, we describe our methodology for measuring attention and present evidence of the stylized facts listed above; in Section 3, we present a theoretical framework that incorporates attention and exposure to macro shocks and derive the predicted asymmetry; in Section 4, we outline an empirical strategy for testing the effects of attention on expected returns and present our results; in Section 5, we present the mitigating effects of attention on uncertainty; in Section 6 we construct a quantitative model of rational inattention and conduct policy counterfactuals; Section 7 concludes.

## 2. TEXTUAL MEASURE OF ATTENTION

This section presents our measure of firm attention, conducts preliminary validation exercises, and documents stylized facts about attention. We show that cross-industry patterns of our proposed measure and its correlation with price adjustment are consistent with predictions about attention behaviour. We then highlight two key stylized facts: aggregate attention moves countercyclically over the sample period, and the majority of firms remain polarized between never and always paying attention. The section concludes with some reflections on the limitations and promise of textual analysis as a tool for measuring attention.

### 2.1. Data and methodology

10-K filings. Our analysis uses all electronically available 10-K filings by publicly listed U.S. companies between 1994 and 2019. $ ^{3} $ Under Regulation S-K, the US Securities and Exchange Commission (SEC) requires all public companies to disclose audited financial statements and a description of business conditions in these filings each year. Companies were phased into mandatory electronic filing between 1993 and 1996, meaning that our sample covers the universe of filers since 1996. $ ^{4} $ The final sample contains 203,050 documents submitted by 35,765 unique firms. Table 1 summarizes the length of these documents and unique vocabulary used by filers.

<div style="text-align: center;"><div style="text-align: center;">TABLE 1</div> </div>


<div style="text-align: center;"><div style="text-align: center;">10-K filing length and vocabulary size</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>N</td><td style='text-align: center; word-wrap: break-word;'>Mean</td><td style='text-align: center; word-wrap: break-word;'>Median</td><td style='text-align: center; word-wrap: break-word;'>SD</td><td style='text-align: center; word-wrap: break-word;'>5th Pctl</td><td style='text-align: center; word-wrap: break-word;'>95th Pctl</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Total word count</td><td style='text-align: center; word-wrap: break-word;'>203,050</td><td style='text-align: center; word-wrap: break-word;'>30,580</td><td style='text-align: center; word-wrap: break-word;'>25,963</td><td style='text-align: center; word-wrap: break-word;'>24,013</td><td style='text-align: center; word-wrap: break-word;'>1,788</td><td style='text-align: center; word-wrap: break-word;'>73,042</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>excl. stopwords</td><td style='text-align: center; word-wrap: break-word;'>203,050</td><td style='text-align: center; word-wrap: break-word;'>18,879</td><td style='text-align: center; word-wrap: break-word;'>16,027</td><td style='text-align: center; word-wrap: break-word;'>15,108</td><td style='text-align: center; word-wrap: break-word;'>1,127</td><td style='text-align: center; word-wrap: break-word;'>44,927</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Unique word count</td><td style='text-align: center; word-wrap: break-word;'>203,050</td><td style='text-align: center; word-wrap: break-word;'>2,430</td><td style='text-align: center; word-wrap: break-word;'>2,488</td><td style='text-align: center; word-wrap: break-word;'>2,439</td><td style='text-align: center; word-wrap: break-word;'>417</td><td style='text-align: center; word-wrap: break-word;'>4,030</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>excl. stopwords</td><td style='text-align: center; word-wrap: break-word;'>203,050</td><td style='text-align: center; word-wrap: break-word;'>2,334</td><td style='text-align: center; word-wrap: break-word;'>2,387</td><td style='text-align: center; word-wrap: break-word;'>2,433</td><td style='text-align: center; word-wrap: break-word;'>363</td><td style='text-align: center; word-wrap: break-word;'>3,920</td></tr></table>

A discussion of economic conditions in an SEC filing typically appears in two contexts: (1) recent or future firm performance and (2) the risk factors that shareholders face by investing in the company. The former context usually appears in Item 7, which requires managers to discuss the firm's financial conditions and results of operations. This section is written as a narrative and its length varies widely across firms (for instance, Item 7 of Alphabet's 2020 10-K filing is 17 pages long). Economic conditions as a source of risk appear in Items 1A and 7A, which detail general firm risks and near-term market risks, respectively.

Textual measure of firm attention. To measure firm attention, we employ dictionary-based frequency counts that identify when firms discuss any of the following nine macroeconomic topics: general economic conditions, output, inflation, labour market, consumption, investment, monetary policy, housing, and oil. Each topic is matched with a keyword dictionary that consists of names of major macroeconomic releases from Econoday (the data provider behind Bloomberg's economic calendar) as well as words and phrases that commonly appear in popular articles on each topic. Any words or phrases that might apply to both aggregate- and firm-specific conditions are removed to avoid misidentification. For example, the phrase “interest rates” is excluded from the monetary policy dictionary because firms may mention interest rates in the context of their own liabilities. The dictionary of topics and associated keywords appears in Appendix Table A.1.

We then construct two measures of attention based on these keywords. Attention prevalence,  $ d_{it}^{k} $, indicates whether firm i mentioned any keyword related to a given topic k in period t:

 $$ d_{i t}^{k}=\mathbb{1}(Total topic-k words_{i t}>0). $$ 

Attention intensity,  $ s_{it}^{k} $, records the rate at which keywords are mentioned as a share of total words in the filing. We interpret this measure as the average intensity with which firms pay attention to economic conditions:

 $$ s_{i t}^{k}=\frac{Total topic-k words_{i t}}{Total words_{i t}}. $$ 

The total word count is generated by following the parsing strategy in Loughran and McDonald (2011): each text is stripped of all numbers and “stop words,” such as articles, and then mapped onto a dictionary of all words that appear in our sample of 10-K filings.

We treat prevalence as our baseline measure of firm attention in the majority of the paper. Since both measures are closely related, this avoids presenting duplicate results. The prevalence measure is also less susceptible to contamination by changes unrelated to firm attention. For instance, intensity will decrease if a firm adds a new Appendix to its filing despite no change in its discussion of any topics listed above. Nonetheless, intensity is essential for understanding the intensive margin of attention and countercyclical variation documented below.

Table A.2, Appendix A reports summary statistics of the firms that are classified as attentive or inattentive according to our “general” topic. Firms that mention macro keywords tend to be

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//257f2f10-6b35-4f4e-b785-e6b291974422/markdown_0/imgs/img_in_chart_box_158_126_903_493.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A48Z%2F-1%2F%2F000740dbaa71f3d07075d7e542bf8c79b55777ec63c8c229e52bb1311e403c9b" alt="Image" width="69%" /></div>


Average industry attention by topic

Notes: Heat map of the fraction of firms in an industry that discuss each macroeconomic topic. Industry is defined according to SIC. Darker colour represents a higher fraction of firms that mention macro keywords.

larger—averaging $7.6 billion in assets compared with $2.9 billion among firms with no macro discussions—and older by just under four years on average. In contrast, average and median leverage appear fairly similar between the two groups of firms.

### 2.2. Sense check of the textual measure

This section uses cross-industry variation to test whether our prevalence measure is consistent with predictions of incomplete information models and then assesses how the measure relates to firms' forecast accuracy. We interpret the results as preliminary evidence that the prevalence measure may capture firm attention before presenting firm-level evidence in Section 4.

Cross-industry patterns of prevalence measure. We first check whether the prevalence measure for the nine topics listed above is concentrated among commonly associated industries. Figure 1 reports the share of firms in each industry that discuss each topic in their 10-K filings, where industry is defined using 2-digit SIC codes. Since each topic uses a different set of keywords, differences in the prevalence measure across topics may reflect the relative popularity of keywords. Therefore, results should be interpreted across industries rather than across topics.

By and large, the prevalence measure for each topic is highest within related industries: mining/extraction has the highest share of firms that discuss oil prices; retail trade has the highest share of firms that discuss consumption; and the financial sector has the highest prevalence on monetary policy (FOMC). While this cross-industry pattern is not unique to firm attention (for instance, a measure of profit exposure to each topic would produce the same pattern), it serves as a common sense check for our prevalence measure and suggests that textual analysis methods are capable of identifying firm attention.

Price adjustment following monetary shocks. We next test whether industries with higher average prevalence adjust prices faster following monetary policy shocks, as predicted for attention in models of incomplete information (Mankiw and Reis 2002; Maćkowiak and Wiederholt 2009; Woodford 2009). The association between prevalence and price response is estimated using the interaction between high-frequency monetary shocks—constructed as in

<div style="text-align: center;"><div style="text-align: center;">(a)</div> </div>


<div style="text-align: center;"><div style="text-align: center;">(b)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//257f2f10-6b35-4f4e-b785-e6b291974422/markdown_1/imgs/img_in_chart_box_168_159_517_412.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A49Z%2F-1%2F%2F4cc91448accc4236410211d132856e97c8083ff97b7f85e3dccf847696e6efbd" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Average responses to monetary policy</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//257f2f10-6b35-4f4e-b785-e6b291974422/markdown_1/imgs/img_in_chart_box_552_156_901_417.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A49Z%2F-1%2F%2F45e874a5ca89b8daf603bf08d8b22e8f16b10e20bbc8b66fa7be02122d58723e" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Marginal effects of attention</div> </div>


<div style="text-align: center;"><div style="text-align: center;">FIGURE 2</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Prevalence measure and price adjustment (a) Average responses to monetary policy and (b) marginal effects of attention Notes: Panels (a) and (b) report the average and marginal coefficients,  $ \beta_{v}^{h} $ and  $ \beta_{dv}^{h} $, respectively, from estimating equation (1) over months  $ h = 1, \ldots, 16 $. We exclude finance and utility industries. Standard errors are double clustered by industry and year. Confidence intervals of 65 and 90% are reported. We have normalized the sign of monetary shocks so that positive shocks are expansionary.</div> </div>


Gorodnichenko and Weber (2016) $ ^{5} $ —and average industry prevalence in a local projection model (Jordà 2005). Over an h-month horizon, our model takes the form

 $$ \log P_{s,t+h}-\log P_{s,t}=\alpha_{s}+\alpha_{t}+\beta_{v}^{h}\nu_{t}^{\mathrm{M}}+\beta_{d}^{h}d_{s t}+\beta_{d v}^{h}d_{s t}\nu_{t}^{\mathrm{M}}+\Gamma^{\prime}Z_{s t}+\varepsilon_{s t}, $$ 

where  $ P_{s,t} $ is the BLS producer price index (PPI 2022) for industry s (4-digit NAICS) in month  $ t $,  $ \nu_t^M $ denotes the monetary shock in month  $ t $,  $ d_{st} $ denotes average industry prevalence, and  $ Z_{st} $ is a vector of controls including industrial production, a recession indicator, and industry size. We include industry and time fixed effects,  $ \{\alpha_s, \alpha_t\} $, and cluster standard errors by both industry and year. For ease of interpretation, monetary shocks are normalized so that positive values correspond to expansionary shocks. We exclude finance and utility industries as is common for estimating firm responses to monetary shocks. $ ^6 $

Figure 2a plots the estimated average price response,  $ \beta_v^h $, and shows that prices rise in a hump-shaped manner following an expansionary monetary shock. At its peak, an unanticipated 25 basis point rate cut causes prices to rise by 1.8%. Figure 2b plots the marginal effect of average prevalence on an industry’s price response,  $ \beta_dv^h $. Industries with a higher fraction of firms mentioning macro keywords raise prices faster in the first 10 months after a monetary shock, though the effect begins to decline after about seven months as the other industries catch up. This result is consistent with imperfect information models that predict faster price adjustment by attentive firms (e.g. Maćkowiak and Wiederholt 2009).

Survey forecast accuracy. The most direct test of our prevalence measure is whether it can predict a firm's forecasting accuracy. This can be implemented for a very limited subset of our sample that overlaps with a quarterly survey conducted by the Bank of Canada. The Business Outlook Survey (BOS 2022) began in 1997 and interviews senior managers about macroeconomic and firm-specific conditions. It covers 100 firms every quarter based on quota sampling by industry, region, and size (Amirault et al. 2020).

<div style="text-align: center;"><div style="text-align: center;">TABLE 2</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Attention and survey forecast accuracy</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2"></td><td colspan="2">General</td><td colspan="2">Inflation</td><td colspan="2">Monetary</td><td rowspan="2">All</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Attn</td><td style='text-align: center; word-wrap: break-word;'>Inattn</td><td style='text-align: center; word-wrap: break-word;'>Attn</td><td style='text-align: center; word-wrap: break-word;'>Inattn</td><td style='text-align: center; word-wrap: break-word;'>Attn</td><td style='text-align: center; word-wrap: break-word;'>Inattn</td></tr><tr><td colspan="8">Panel A: Macro forecasts (2-year ahead inflation)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Avg accuracy</td><td style='text-align: center; word-wrap: break-word;'>41%</td><td style='text-align: center; word-wrap: break-word;'>31%</td><td style='text-align: center; word-wrap: break-word;'>45%</td><td style='text-align: center; word-wrap: break-word;'>32%</td><td style='text-align: center; word-wrap: break-word;'>43%</td><td style='text-align: center; word-wrap: break-word;'>40%</td><td style='text-align: center; word-wrap: break-word;'>40%</td></tr><tr><td rowspan="3">N</td><td style='text-align: center; word-wrap: break-word;'>131</td><td style='text-align: center; word-wrap: break-word;'>13</td><td style='text-align: center; word-wrap: break-word;'>92</td><td style='text-align: center; word-wrap: break-word;'>52</td><td style='text-align: center; word-wrap: break-word;'>14</td><td style='text-align: center; word-wrap: break-word;'>130</td><td style='text-align: center; word-wrap: break-word;'>144</td></tr><tr><td colspan="2">General</td><td colspan="2">Consumption</td><td colspan="2">Output</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Attn</td><td style='text-align: center; word-wrap: break-word;'>Inattn</td><td style='text-align: center; word-wrap: break-word;'>Attn</td><td style='text-align: center; word-wrap: break-word;'>Inattn</td><td style='text-align: center; word-wrap: break-word;'>Attn</td><td style='text-align: center; word-wrap: break-word;'>Inattn</td><td style='text-align: center; word-wrap: break-word;'>All</td></tr><tr><td colspan="8">Panel B: Micro forecasts (1-year ahead sales growth)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Avg accuracy</td><td style='text-align: center; word-wrap: break-word;'>29%</td><td style='text-align: center; word-wrap: break-word;'>12%</td><td style='text-align: center; word-wrap: break-word;'>31%</td><td style='text-align: center; word-wrap: break-word;'>26%</td><td style='text-align: center; word-wrap: break-word;'>28%</td><td style='text-align: center; word-wrap: break-word;'>27%</td><td style='text-align: center; word-wrap: break-word;'>28%</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>N</td><td style='text-align: center; word-wrap: break-word;'>121</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>49</td><td style='text-align: center; word-wrap: break-word;'>80</td><td style='text-align: center; word-wrap: break-word;'>39</td><td style='text-align: center; word-wrap: break-word;'>90</td><td style='text-align: center; word-wrap: break-word;'>129</td></tr></table>

Notes: This table reports average forecast accuracy by firm attention. Panel A reports the forecast accuracy of 2-year ahead inflation based on firm responses to BOS question 6.14. “General,” “inflation,” and “monetary” denote firm attention to the respective topics. Panel B reports the forecast accuracy of 1-year ahead sales growth based on firm responses to BOS question 2.6. “General,” “consumption,” and “output” denote firm attention to the respective topics.

Over the course of the survey, 137 firms in our sample have appeared in the BOS because they are either a U.S. multinational with a presence in Canada or a Canadian firm listed in the U.S. Although these firms skew larger and are more likely to mention macro keywords than those in our full sample, they exhibit substantial variation in the prevalence measure across relevant topics.

The BOS includes two questions that pertain to firm forecasts. Question 6.14 asks about inflation expectations over the next two years, and question 2.6 asks about a firm’s expected sales growth. The text for each is reproduced here:

Question 6.14: Over the next 2 years what do you expect the annual rate of inflation to be based on the Canadian Consumer Price Index? (a) between 1 and 2%, (b) between 2 and 3%, (c) above 3%, (d) below 1%, and (e) NA.

Question 2.6: Over the next 12 months, is your firm’s sales volume expected to increase (a) at a lesser rate, (b) the same rate, or (c) a greater rate, as over the past 12 months?

Since responses are multiple choice, we calculate the share of firms whose responses match the realized data and compare these shares between firms that are classified as attentive or inattentive using the prevalence measure. Responses to question 6.14 are compared with annual inflation over the next two years, from the OECD, and responses to question 2.6 are compared with sales volume in the next year, according to Compustat. We report forecast accuracy across all relevant economic topics: attention to general, inflation, and monetary news for forecasting inflation; and attention to general, output, and consumption news for forecasting sales.

Panel A in Table 2 shows that firms that are classified as attentive have more accurate inflation forecasts, and that the accuracy gap is highest for the inflation-specific prevalence measure: the accuracy rate of attentive firms was 13 percentage points higher than that of inattentive firms.

Panel B shows a similar pattern of accuracy when firms predict their own sales growth. Firms that are classified as attentive to aggregate demand (e.g. general, consumption, and output topics) forecast firm-specific demand better, which suggests that these firms translate macro information into better firm planning.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//257f2f10-6b35-4f4e-b785-e6b291974422/markdown_3/imgs/img_in_chart_box_167_124_526_472.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A51Z%2F-1%2F%2Fc5ce8456bc2eda4ed8d251f94a0a23372a607c25ac9c7b36540f7b9bc5bc6c30" alt="Image" width="33%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(b)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//257f2f10-6b35-4f4e-b785-e6b291974422/markdown_3/imgs/img_in_chart_box_542_126_902_462.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A51Z%2F-1%2F%2F48f86b1468405c4dff52c0502d8a51c778d4aee9443aecbb03bd29e7a4746cc8" alt="Image" width="33%" /></div>


<div style="text-align: center;"><div style="text-align: center;">FIGURE 3</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Time series of attention to “economic conditions” (a) Prevalence  $ (d_{it}) $ and (b) Intensity  $ (s_{it}) $</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Notes: Time series of firm attention to the keyword “economic conditions.” The left panel plots the prevalence measure and reports the share of firms that mention the keyword. The right panel plots the intensity measure and reports the average mentions of the keyword per 100,000 words. “Raw” refers to the unfiltered series, and “HP filtered” refers to the cyclical components of the HP-filtered series with smoothing factor  $ \lambda = 400 $. Shares are reported in percent.</div> </div>


### 2.3. Stylized facts about firm attention

This section builds upon preliminary evidence that our text-based measures capture firm attention by summarizing how these measures vary over time and between firms, and then exploring potential drivers of firm attention. We document two key stylized facts: aggregate attention moves countercyclically over the sample period and the majority of firms remain polarized between never and always paying attention.

Countercyclical attention to economic conditions. Both the share of firms that mention economic keywords and the intensity with which they are discussed vary countercyclically over our sample period. This is illustrated in Figure 3, which plots the annual average prevalence and intensity measures for the phrase “economic conditions,” as well as detrended versions using an HP-filter ( $ \lambda = 400 $).

Figure 3a shows that the share of firms mentioning “economic conditions” has steadily increased since 1994, with particularly rapid growth during the 2001 Recession and the Great Recession. Between 2008 and 2010, aggregate attention jumped by about 15 percentage points and remained elevated for the rest of the sample period. Average intensity in Figure 3b similarly spiked during the Great Recession but declined faster in subsequent years.

We point to these sharp dynamics around the 2001 Recession and the Great Recession as evidence of countercyclical attention, but we also acknowledge that our sample is limited and a longer time series is needed to confirm this pattern. In light of this, future sections use fluctuations in GDP growth and macroeconomic uncertainty—continuous measures related to business cycles—to provide further evidence of countercyclical attention and explore why attention increases in downturns.

Some models with endogenous firm attention predict the countercyclicality displayed in Figure 3. Mackowiak and Wiederholt (2009) consider imperfect information firms that allocate attention between aggregate and idiosyncratic state variables. Increased aggregate uncertainty (itself countercyclical) induces these firms to shift attention towards aggregate conditions. Chiang (2024) decomposes the impact of lower expected productivity on attention into income

<div style="text-align: center;"><div style="text-align: center;">(a)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//257f2f10-6b35-4f4e-b785-e6b291974422/markdown_4/imgs/img_in_chart_box_165_123_525_499.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A52Z%2F-1%2F%2F1e59c6307a8a688f4cacf885a84470deb3f4ada9e2f12ac604fd4fe9f5f47001" alt="Image" width="33%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(b)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//257f2f10-6b35-4f4e-b785-e6b291974422/markdown_4/imgs/img_in_chart_box_539_127_900_499.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A52Z%2F-1%2F%2F967adf5d11a470fc18300007f141245cb087997bc702c630b42a954fd9be552f" alt="Image" width="33%" /></div>


<div style="text-align: center;"><div style="text-align: center;">FIGURE 4</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Share of filings that mention “economic conditions” (a) All firms and (b) within industry</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Notes: Histograms of the share of filings by a firm that mention “economic conditions.” The left panel shows the histogram of the average fraction of filings that mention the keyword “economic conditions” over the sample period of 1994–2019. Dark blue bars correspond to the distribution of all firms, and light blue bars correspond to firms appearing for at least 5 years in the sample. The right panel shows the histogram of the time-series averages of the residuals of firm attention to “economic conditions” after regressing on industry fixed effects. Shares of firms on the vertical axes are reported in percentages.</div> </div>


and substitution effects. Countercyclical attention emerges among goods-producing agents when their marginal utility rises faster than the returns to attention falls under lower productivity.

Polarization in firm attention. Despite the countercyclical dynamics documented above, most firms in our sample are polarized between either always or never discussing economic conditions in their 10-K filings. Figure 4 illustrates this by plotting each firm’s share of filings that mention the same key phrase, “economic conditions.” $ ^{7} $ The resulting distribution in Figure 4a is heavily concentrated at each extreme, with about three-quarters of firms taking values of either 0 or 1. This suggests that most variation in attention occurs across firms rather than within firms and countercyclical variation is caused by a relatively small subset of filers.

To test whether polarized attention is driven by firms with few filings, we overlay a second histogram in Figure 4a that restricts to firms with at least 5 years of data. This adjustment greatly reduces the share of firms that never pay attention, yet over half remain polarization between always- and never-attentive firms.

We also test whether cross-industry differences in attention are responsible for polarization. Figure 4b demeans by industry, which explains approximately one-quarter of the attention variation. The distribution now contains a large mass of firms around their industry average (i.e. industries with little attention dispersion), while the remaining firms form a bimodal pattern consistent with polarization.

The presence of any inattentive firms may be surprising given that most U.S. macroeconomic data are readily available. However, this result is consistent with a broader interpretation of attention that includes information processing, communication, and optimal response in addition to

information acquisition. As highlighted in Reis (2006), firms likely require significant resources and expertise to process, summarize, and forecast macroeconomic series into sufficient statistics that inform firm decision-making. This is consistent with plant-level evidence from Zbaracki et al. (2004). To this end, Abis and Veldkamp (2023) estimate a data production function that uses labour and capital inputs to produce knowledge from unstructured data.

Potential drivers of firm attention. To understand what motivates attention and how attentive firms differ from their competitors, we turn to potentially related firm and macroeconomic factors. First, we estimate the relationship between attention and four firm variables—size, age, leverage, and productivity—both cross-sectionally and within-firm. We then examine how attention evolves alongside GDP growth and aggregate beliefs from the Survey of Professional Forecasters. Our findings suggest that size, age, productivity, economic growth, and aggregate uncertainty are important to understanding observed variation in attention.

The relationship between attention and firm characteristics is estimated with the following pair of regressions,

 $$  Cross-firm variation:y_{i(j)t}=\alpha_{j}+\delta_{t}+\mathbf{X}_{it}\beta+\varepsilon_{it} $$ 

 $$ \mathbf{W i t h i n-f i r m~v a r i a t i o n:}y_{i(j)t}=\nu_{i}+\delta_{t}+\mathbf{X}_{i t}\beta+\varepsilon_{i t}, $$ 

where  $ y_{i(j)t} \in \{d_{i(j)t}, \log(s_{i(j)t})\} $ represents attention by firm  $ i $ in industry  $ j $ and year  $ t $, and  $ \mathbf{X}_{it} $ is a vector of firm variables, including size, age, leverage, filing length, and productivity. $ ^8 $ Note that our intensity measure,  $ s_{it} $, is logged for ease of interpretation. Equation (2) includes time and industry (4-digit NAICS) fixed effects to highlight cross-sectional variation, while equation (3) uses firm fixed effects to isolate within-firm variation. The first model clusters standard errors by industry and year, and the second model clusters by firm and year.

Data on firm characteristics are from Compustat or firms’ 10-K filings. Size is measured as the log of total assets, age as the number of years that a firm has appeared in Compustat, and leverage as the debt-to-asset ratio. $ ^{9} $ Productivity is estimated using the control function approach from Olley and Pakes (1996) and implemented with GMM as in Wooldridge (2009). $ ^{10} $

Results for this analysis are displayed in Table 3. The first two columns report estimates for equation (2) and the second two columns do the same for equation (3). Columns using our prevalence measure,  $ d_{it} $, capture changes in attention along the extensive margin, while those using our intensity measure,  $ \log(s_{it}) $, restrict the sample to attentive firms and measure changes on the intensive margin. Both outcome variables are scaled by 100 so that units for  $ d_{it} $ are percentage points and those for  $ \log(s_{it}) $ are percents.

By and large, we find that larger, older, and more productive firms exhibit higher rates of attention. The association with size and productivity is strongest across firms, while the effect of age appears almost exclusively within-firm. Together, these results suggest that larger and more

<div style="text-align: center;"><div style="text-align: center;">TABLE 3</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Firm characteristics and attention</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td colspan="2">Cross-firm</td><td colspan="2">Within-firm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ d_{it} $</td><td style='text-align: center; word-wrap: break-word;'>$ \log(s_{it}) $</td><td style='text-align: center; word-wrap: break-word;'>$ d_{it} $</td><td style='text-align: center; word-wrap: break-word;'>$ \log(s_{it}) $</td></tr><tr><td rowspan="2">Size (log total assets)</td><td style='text-align: center; word-wrap: break-word;'>$ 1.25^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 4.25^{***} $</td><td style='text-align: center; word-wrap: break-word;'>0.80</td><td style='text-align: center; word-wrap: break-word;'>$ 3.47^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.22)</td><td style='text-align: center; word-wrap: break-word;'>(0.56)</td><td style='text-align: center; word-wrap: break-word;'>(0.48)</td><td style='text-align: center; word-wrap: break-word;'>(0.85)</td></tr><tr><td rowspan="2">Age</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>$ 0.42^{**} $</td><td style='text-align: center; word-wrap: break-word;'>$ 1.78^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 3.33^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.07)</td><td style='text-align: center; word-wrap: break-word;'>(0.18)</td><td style='text-align: center; word-wrap: break-word;'>(0.04)</td><td style='text-align: center; word-wrap: break-word;'>(0.17)</td></tr><tr><td rowspan="2">Leverage</td><td style='text-align: center; word-wrap: break-word;'>0.57</td><td style='text-align: center; word-wrap: break-word;'>$ 6.01^{*} $</td><td style='text-align: center; word-wrap: break-word;'>-1.14</td><td style='text-align: center; word-wrap: break-word;'>4.20</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(1.77)</td><td style='text-align: center; word-wrap: break-word;'>(3.31)</td><td style='text-align: center; word-wrap: break-word;'>(1.41)</td><td style='text-align: center; word-wrap: break-word;'>(3.32)</td></tr><tr><td rowspan="2">Productivity (TFPR)</td><td style='text-align: center; word-wrap: break-word;'>$ 1.27^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 2.89^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 1.20^{***} $</td><td style='text-align: center; word-wrap: break-word;'>0.78</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.34)</td><td style='text-align: center; word-wrap: break-word;'>(0.73)</td><td style='text-align: center; word-wrap: break-word;'>(0.32)</td><td style='text-align: center; word-wrap: break-word;'>(0.67)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Observations</td><td style='text-align: center; word-wrap: break-word;'>73101</td><td style='text-align: center; word-wrap: break-word;'>55276</td><td style='text-align: center; word-wrap: break-word;'>72283</td><td style='text-align: center; word-wrap: break-word;'>54365</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.313</td><td style='text-align: center; word-wrap: break-word;'>0.290</td><td style='text-align: center; word-wrap: break-word;'>0.635</td><td style='text-align: center; word-wrap: break-word;'>0.698</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Industry FE</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>no</td><td style='text-align: center; word-wrap: break-word;'>no</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Firm FE</td><td style='text-align: center; word-wrap: break-word;'>no</td><td style='text-align: center; word-wrap: break-word;'>no</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td></tr></table>

Notes: Columns (1) and (2) report estimates for  $ y_{i(j)t} = \alpha_j + \delta_t + \mathbf{X}_{it} \beta + \varepsilon_{it} $, while columns (3) and (4) report estimates for  $ y_{i(j)t} = v_i + \delta_t + \mathbf{X}_{it} \beta + \varepsilon_{it} $. The outcome variable,  $ y_{i(j)t} \in \{d_i(j)t, \log(s_i(j)t)\} $, represents attention by firm  $ i $ in industry  $ j $ and year  $ t $, and  $ \mathbf{X}_{it} $ is a vector of firm variables including size, age, leverage, filing length, and productivity. The first two columns include industry fixed effects (4-digit NAICS), and the second two columns include firm fixed effects. All four columns include year fixed effects and control for filing length (log words), though not reported. Outcome variables are scaled by 100 so that units for  $ d_{it} $ are percentage points and those for  $ \log(s_{it}) $ are percents.

productive firms pay greater attention to aggregate conditions over time, while smaller and less productive competitors may never do so.

Next, we consider how attention varies with aggregate conditions and beliefs. We estimate the magnitude of countercyclical attention observed in Figure 3 by regressing our attention measures on annual real GDP growth and then see how attention comoves with three measures of aggregate uncertainty: the interquartile range of expectations, the consensus forecast error, and the absolute value of that error. $ ^{[1]} $ Each measure emphasizes a different dimension of uncertainty. The interquartile range captures disagreement among forecasters, the consensus forecast error considers how attention responds to positive or negative surprises differently, and the absolute forecast error isolates the accuracy of consensus beliefs regardless of error direction. $ ^{[12]} $

The relationship between attention and aggregate variables is estimated with the following model,

 $$ y_{i(j)t}=\nu_{i}+\delta z_{t}+\beta x_{it}+\varepsilon_{it}, $$ 

where  $ y_i(j)_t \in \{d_{i(j)_t}, \log(s_{i(j)_t})\} $ again represents attention,  $ z_t $ is our aggregate variable of interest,  $ x_{it} $ is the 10-K filing length, and  $ \nu_i $ represents a firm fixed effect. Standard errors are clustered by both firm and year.

11. Given a series,  $ x_t $, and a sample of one-period-ahead forecasts,  $ \hat{x}_{it} $, the interquartile range is defined as  $ \mathrm{IQR}(\hat{x}_{\mathrm{it}}) = \mathrm{P}_{75}(\hat{x}_{\mathrm{it}}) - \mathrm{P}_{25}(\hat{x}_{\mathrm{it}}) $, where  $ P_Y $ is the Yth percentile of the forecast sample. The consensus forecast error is defined as  $ \mathrm{FE}(\hat{x}_{\mathrm{it}}) = x_t - \mathrm{P}_{50}(\hat{x}_{\mathrm{it}}) $.

12. Data on macroeconomic expectations are from the Survey of Professional Forecasters, which has been administered on a quarterly basis since 1968. In each instalment, a panel of respondents forecast several economic indicators up to one year in the future. We focus on one-quarter-ahead forecasts for real GDP growth and the unemployment rate. Uncertainty is constructed for each series at a quarterly frequency, standardized over the sample period, and then averaged into an annual composite uncertainty index. Forecast errors for unemployment are inverted so that positive values correspond to positive economic surprises.

<div style="text-align: center;"><div style="text-align: center;">TABLE 4 Aggregate variables and attention</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2"></td><td colspan="4">Prevalence,  $ d_{it} $</td><td colspan="4">Intensity,  $ \log(s_{it}) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td><td style='text-align: center; word-wrap: break-word;'>(4)</td><td style='text-align: center; word-wrap: break-word;'>(5)</td><td style='text-align: center; word-wrap: break-word;'>(6)</td><td style='text-align: center; word-wrap: break-word;'>(7)</td><td style='text-align: center; word-wrap: break-word;'>(8)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>rGDP growth</td><td style='text-align: center; word-wrap: break-word;'>$ -0.59^{***}(0.17) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -5.14^{***}(1.23) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>IQR index</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ 3.29^{***}(0.71) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ 14.90^{**}(6.54) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Abs(FE) index</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1.15(0.81)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ 24.19^{***}(4.52) $</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>FE index</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -1.58^{***}(0.24) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-7.16(4.26)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Observations</td><td style='text-align: center; word-wrap: break-word;'>129416</td><td style='text-align: center; word-wrap: break-word;'>129416</td><td style='text-align: center; word-wrap: break-word;'>129416</td><td style='text-align: center; word-wrap: break-word;'>129416</td><td style='text-align: center; word-wrap: break-word;'>99041</td><td style='text-align: center; word-wrap: break-word;'>99041</td><td style='text-align: center; word-wrap: break-word;'>99041</td><td style='text-align: center; word-wrap: break-word;'>99041</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ R^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.651</td><td style='text-align: center; word-wrap: break-word;'>0.651</td><td style='text-align: center; word-wrap: break-word;'>0.651</td><td style='text-align: center; word-wrap: break-word;'>0.651</td><td style='text-align: center; word-wrap: break-word;'>0.749</td><td style='text-align: center; word-wrap: break-word;'>0.747</td><td style='text-align: center; word-wrap: break-word;'>0.752</td><td style='text-align: center; word-wrap: break-word;'>0.745</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Firm FE</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Quadratic Trend</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td></tr></table>

Notes: This table reports estimates of  $ \beta $ from the model in (4):  $ y_i(j)t = v_i + \delta z_t + \beta x_{it} + \varepsilon_{it} $, where  $ z_t $ represents either real GDP growth or one of three uncertainty indices: the IQR index, Abs(FE) index, or FE index. The outcome variable  $ y_i(j)t $ represents the attention of firm  $ i $ in year  $ t $,  $ x_{it} $ is the 10-K filing length, and  $ v_i $ represents a firm fixed effect. The first four columns use attention prevalence,  $ d_{it} $, as the outcome variable, and the last four columns use log intensity,  $ \log(s_{it}) $. Standard errors are clustered by both firm and year.

The resulting estimates are reported in Table 4. Columns 1 and 5 show a strong, countercyclical pattern of attention, while columns 2 and 6 show a strong positive association between forecaster disagreement and firm attention. Column 4 suggests that higher rates of attentive firms are associated with negative economic surprises, while column 7 suggests that firms pay greater attention when consensus forecasts are less accurate.

### 2.4. Limitations and promise of textual measures

Boilerplate language is a key concern when using regulatory filings to measure firm attention. Filings are often written collaboratively between managers and legal departments, and evidence suggests that firms include certain statements within 10-K filings to appease investors or lower liability (Cao et al. 2023). Moreover, firms likely save time and resources by revising previous filings rather than starting from scratch each year.

The methods used above cannot distinguish between authentic attention to macroeconomic conditions and cheap talk references or recycled language that does not reflect current management practices. We address this shortcoming in Appendix C.1 by measuring the diversity in filing language with a Jaccard score of lexical similarity and testing whether our main findings are robust in the most linguistically diverse 10-K sections. Table A.8 confirms that our key findings are not driven by the most repetitive and standardized sections.

Even greater measurement error may arise from misidentifying firms as inattentive because they do not mention a certain keyword or discuss economic conditions when such conditions pose a financial risk. $ ^{13} $ False negatives can result from methodological limitations or variation in the amount of information that firms choose to disclose. It is worth noting that firm managers

are obligated to disclose any material risk factors under SEC Regulation S-K. $ ^{14} $ Those who track inflation, unemployment, or any other topic because they are considered material risk factors are obligated to disclose this to their investors. For the purposes of this paper, underestimated attention would attenuate our results and imply that our current estimate for the cost of information frictions serves as a lower bound.

Text analysis methods also hold tremendous promise for uncovering a more refined depiction of firm attention and expectations formation. We illustrate these capabilities with two approaches for identifying the context in which firms discuss economic conditions. Appendix C.2 uses a Latent Dirichlet Allocation (LDA) unsupervised model to categorize words adjacent to each keyword and produces nine unlabelled “topics” in which keywords appear. Appendix C.3 uses the itemized structure of 10-K filings to identify sections that contain the most keywords. This analysis shows that keywords typically appear in sections that discuss firm risk factors (Item 1A) and business operations (Item 7A).

## 3. ILLUSTRATIVE FRAMEWORK

This section derives a testable implication of firm attention to address a key identification challenge for our text-based measure: whether it captures exposure rather than attention to macroeconomic conditions. We present a stylized model in which firms are heterogeneous in both attention and exposure to an aggregate state variable and then consider how firm outcomes vary with each source of heterogeneity. The model predicts contradictory responses to aggregate shocks under varying attention and exposure, which guides our empirical design in Section 4. The model environment is kept minimal to highlight key mechanisms before Section 6 incorporates more realistic assumptions.

Environment. The model is static. Consider a firm whose profits,  $ \pi(s, a) $, depend on an aggregate state variable, s, and a firm action, a. Assume that  $ \pi(s, a) $ is twice continuously differentiable, a single-peaked function of a and maximized at  $ a^* = s $. For concreteness, we think of a as the price that a monopolistically competitive firm sets and s as the exogenous optimal price determined by factors outside of that firm's control, as in Woodford (2009).

Firm profits can be approximated under a second-order log approximation around the non-stochastic steady state as $ ^{15} $

 $$ \hat{\pi}(\hat{s},\hat{a})=\pi_{s}(\bar{s},\bar{a})\bar{s}\hat{s}+\frac{1}{2}\left(\pi_{s s}(\bar{s},\bar{a})\bar{s}^{2}-\pi_{a a}(\bar{s},\bar{a})\bar{a}^{2}\right)\hat{s}^{2}+\frac{1}{2}\pi_{a a}(\bar{s},\bar{a})\bar{a}^{2}(\hat{a}-\hat{s})^{2}, $$ 

where  $ \bar{s} $ and  $ \bar{a} $ denote the steady-state values;  $ \hat{\pi} $,  $ \hat{s} $, and  $ \hat{a} $ denote the log deviations from the steady state; and  $ \pi_{s} \equiv \frac{\partial}{\partial s} \pi(s, a) $,  $ \pi_{aa} \equiv \frac{\partial^{2}}{\partial a^{2}} \pi(s, a) $, and  $ \pi_{ss} \equiv \frac{\partial^{2}}{\partial s^{2}} \pi(s, a) $.

Lastly, assume that firm profits are increasing in s,  $ \pi_{s} > 0 $, and that the profit function is concave in the own action,  $ \pi_{aa} < 0 $.

Attention and exposure. We can now define attention and exposure in the model. A firm is more exposed to aggregate conditions if its profits are more sensitive to aggregate shocks, while a firm is more attentive if its actions are more sensitive to shocks. Definitions 1 and 2 formalize these ideas.

Definition 1(attention). Let a firm’s action be a function of the state:  $ \hat{a} = f(\hat{s}) $, with  $ f(0) = 0 $ and  $ 0 < f'(\hat{s}) \leq 1 $. Firm i is attentive to macroeconomic conditions if  $ f_i'(\hat{s}) = 1 $, and firm j is inattentive to macroeconomic conditions if  $ 0 < f'(\hat{s}) < 1 $.

An attentive firm reacts one-for-one with innovations to the aggregate state, whereas an inattentive firm responds less than one-for-one. The simplified definition of inattention is consistent with that in rational inattention models such as Sims (2003), which yields a steady-state Kalman gain between 0 and 1. $ ^{16} $

Definition 2(exposure). Firm $i$ is more exposed to macroeconomic conditions than firm $j$ if $\pi_{s}^{i}(s,a) > \pi_{s}^{j}(s,a)$.

Differences in attention and exposure. We now derive model predictions for heterogeneity in attention and exposure that guide the empirical analysis to come.

We first construct the stock return, which is the dependent variable in our empirical analysis. As in Gorodnichenko and Weber (2016), a firm's stock price is equal to its firm value, which in the simple static setting equals its profits:

 $$ V=\pi(s,a). $$ 

Realized equity returns, measuring the log change in a firm’s value around an aggregate shock, are given by

 $$ r=\hat{v}-\hat{v}_{-1}. $$ 

where lowercase  $ \hat{v} \equiv \log V - \log V $ denotes the log deviation of firm value from the steady state, and  $ \hat{v}_{-1} \equiv \log \mathbb{E}_{-1} V - \log V $ denotes the log deviation of firm value before the shock is realized.

Proposition 1 highlights the asymmetric responses of stock returns to positive and negative aggregate shocks that result from the attention channel and the symmetric responses from the exposure channel.

Proposition 1. The return elasticity with respect to aggregate shocks for the exposure and the attention channels can be characterized as:

(i) Exposure: If firm i is more exposed to macroeconomic conditions than firm j, then, holding all else equal, the return elasticity of firm i with respect to the aggregate shock is higher than the return elasticity of firm j for all realizations of the shocks:

 $$ \frac{\partial r_{i}}{\partial\hat{s}}>\frac{\partial r_{j}}{\partial\hat{s}}\quad\forall\hat{s}. $$ 

(ii) Attention: Suppose firm i is attentive to macroeconomic conditions and firm j is inattentive. Then, holding all else equal, the return elasticity of a positive (expansionary) shock is higher for the attentive firm i than for the inattentive firm j. For negative (contractionary) shocks, the return elasticity for the attentive firm i is lower than for the inattentive firm j. For zero shocks, the return elasticities for attentive and inattentive

<div style="text-align: center;"><div style="text-align: center;">(a) Heterogeneity in exposure</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//9607f8df-2385-4100-8c81-91d39f569059/markdown_0/imgs/img_in_image_box_163_158_514_483.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A50Z%2F-1%2F%2Fe675a57d29c23f4a93ff78d6f46cf7bfb00d7ff2076c09c291fd4f7cdcf13a8f" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(b) Heterogeneity in attention</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//9607f8df-2385-4100-8c81-91d39f569059/markdown_0/imgs/img_in_image_box_551_161_905_483.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A50Z%2F-1%2F%2F43296ee159f77a1203ac765a14e2f0d38e5deab3b8fe79a9588b1825968faf62" alt="Image" width="33%" /></div>


<div style="text-align: center;"><div style="text-align: center;">FIGURE 5</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Model predictions for exposure versus attention (a) Heterogeneity in exposure and (b) heterogeneity in attention  Notes: Illustration of model predictions of return elasticity with respect to aggregate shocks. Vertical axes represent conditional realized return, and horizontal axes represent the magnitude of shocks. The left panel shows return elasticity for firms that are highly exposed to macro conditions (high) and firms that are unexposed (low). The right panel shows return elasticity for attentive firms (attn) and inattentive firms (inattn). Exposure and attention are as defined in the main text.</div> </div>


firms equal

 $$ \left\{\begin{array}{l l}\frac{\partial r_{i}}{\partial\hat{s}}>\frac{\partial r_{j}}{\partial\hat{s}}&i f\hat{s}>0\end{array}\right. $$ 

 $$ \left\{\begin{array}{l}{\displaystyle\frac{\partial r_{i}}{\partial\hat{s}}=\frac{\partial r_{j}}{\partial\hat{s}}\quad{i f}\hat{s}=0.}\end{array}\right. $$ 

 $$ \left\lfloor\frac{\partial r_{i}}{\partial\hat{s}}<\frac{\partial r_{j}}{\partial\hat{s}}\quad if\hat{s}<0\right. $$ 

Proof: See Appendix D.2.

Figure 5 illustrates the predictions from Proposition 1. In Figure 5a, firms are heterogeneous in their exposure to aggregate shocks, and those with high exposure exhibit higher return elasticities to aggregate shocks regardless of the sign of the shock. Figure 5b illustrates the mechanism of attention. Attentive firms are better at tracking the state variable, so their stock returns outperform those of inattentive firms after any aggregate disturbance. In response to a positive shock, stock returns of both attentive and inattentive firms rise, but returns of attentive firms rise more. In response to a negative shock, returns of both types of firms decrease, but returns of attentive firms drop by less.

This asymmetry in return elasticities is a unique feature of the attention channel and allows us to distinguish between the effects of firm attention and exposure to macro news. In the next section, we use this predicted asymmetry to show that our text-based measure correctly identifies firm attention and then estimate the cost of inattention based on the difference in return elasticities for positive and negative shocks.

## 4. ASYMMETRIC RESPONSE TO MONETARY SHOCKS

We now test the hypothesis that attentive firms respond better to aggregate shocks using a high-frequency identification strategy. Shocks are constructed as plausibly exogenous monetary policy surprises following FOMC announcements, and resulting changes in firm value are measured using stock prices. We use our prevalence measure to estimate the relative performance of attentive firms and then test whether they fare better following both positive and negative shocks. $ ^{17} $ Results in this section serve the dual purpose of validating our text-based attention measure and quantifying the expected benefits of attention to economic conditions.

Stock prices are a particularly informative outcome variable because they are forward-looking and similarly high frequency as our monetary shocks. The cumulative effect of a rate surprise on expected future profits will be reflected quickly in a firm’s stock price. By restricting to a narrow window around the shock, we isolate this price effect while avoiding other confounding factors. In comparison, a firm’s investment and hiring decisions will be smoothed over a longer horizon and any low-frequency response is confounded by other factors that influence these choices. These limitations are exacerbated by the low statistical power of high-frequency monetary shocks, preventing precise estimates of investment and hiring responses. $ ^{18} $

To best isolate the effects of attention, our baseline specification controls for firm size, age, leverage, and industry measured by 4-digit NAICS. The underlying identifying assumption is that firms have similar exposure to monetary policy shocks within a narrowly defined industry after conditioning on firm characteristics and financial structure. Residual variation in stock prices can then be attributed to firm attention rather than cross-firm variation in the exposure to monetary policy.

### 4.1. Data

Monetary policy shocks are constructed using the high-frequency identification strategy developed by Cook and Hahn (1989) and Gürkaynak et al. (2005) and used more recently in Gorodnichenko and Weber (2016), Nakamura and Steinsson (2018), and Ottonello and Winberry (2020). These shocks are measured as the change in the fed funds futures rate within a one-hour window surrounding FOMC announcements. Any changes within such a narrow window can be attributed to unanticipated changes to monetary policy as it is unlikely that other shocks occurred within the same window.

Monthly fed funds futures contracts clear at the average daily effective fed funds rate over the delivery month, so rate changes are weighted by the number of days in the month that are affected by the monetary policy shock. Following notation in Gorodnichenko and Weber (2016), the final shock series is defined as

 $$ \nu_{t}=\frac{D}{D-\tau}(f f_{t+\Delta t^{+}}^{0}-f f_{t-\Delta t^{-}}^{0}), $$ 

where $t$ is the time of the FOMC announcement, $ff_{t+\Delta t^+}^0$ and $ff_{t-\Delta t^-}^0$ are the fed funds futures rates 15 min before and 45 min after the announcement, $D$ is the number of days in the month of the announcement, and $\tau$ is the date of the announcement. We use the series published by Gorodnichenko and Weber (2016) and Nakamura and Steinsson (2018) for monetary shocks

from 1994 to 2014. For easier interpretation of our empirical results, we normalize the sign of the monetary shock so that a positive shock is expansionary (corresponding to a decrease in interest rates).

Firm outcome and control variables are constructed using CRSP and Compustat data (CCM 2020). Daily stock returns are measured as the open-to-close change in stock prices on the day of an FOMC announcement. Firm size, age, and industry controls are constructed as described in Section 2.3.

Firm attention is measured using the prevalence measure  $ d_{it} $, described in Section 2. To better suit a high-frequency methodology, firm attention at the time of an FOMC announcement is identified using the firm's most recent annual filing rather than the filing in the same year as the FOMC announcement. This modification precludes the possibility that firms are identified as attentive to the FOMC announcement that inspired their attention.

### 4.2. Methodology

We separately estimate the slope of the interaction between monetary shocks and firm attention for positive and negative shocks and then test whether these two coefficients are statistically different.

For firm i in industry j on day t, our baseline model takes the form

 $$ \begin{align*}r_{it}&=\beta_{d} d_{it}+\beta_{1}\mathbb{1}_{\nu_{t}>0}+\beta_{\nu_{+}}\nu_{t}\mathbb{1}_{\nu_{t}>0}+\beta_{\nu_{-}}\nu_{t}\mathbb{1}_{\nu_{t}<0}\\&\quad+\beta_{d\nu_{+}}(d_{it}\nu_{t}\mathbb{1}_{\nu_{t}>0})+\beta_{d\nu_{-}}(d_{it}\nu_{t}\mathbb{1}_{\nu_{t}<0})+\delta_{j}+\delta_{j}\nu_{t}+\Gamma_{1}^{\prime}X_{t}+\Gamma_{2}^{\prime}X_{t}\nu_{t}+\varepsilon_{it},\end{align*} $$ 

where  $ d_{it} $ is the attention prevalence,  $ \nu_t $ is the monetary policy shock,  $ \mathbb{1}_{\nu_t > 0} $ indicates positive monetary policy shocks,  $ \mathbb{1}_{\nu_t < 0} $ indicates negative monetary policy shocks, and  $ X_t $ is a vector of controls including the indicator variable for positive shocks and quarterly firm controls for size, age, and leverage. We also control for the interaction of monetary shocks with industry dummies and firm controls to capture the average effects of industry and firm characteristics on differential responses to monetary shocks. Standard errors are clustered by FOMC announcement to allow for correlated errors across firms at each FOMC announcement.

The coefficients of interest are  $ \beta_{dv_{+}} $ and  $ \beta_{dv_{-}} $. The theoretical framework in Section 3 hypotheses  $ \beta_{dv_{+}} $ to be positive and  $ \beta_{dv_{-}} $ to be negative, implying attentive firms should outperform inattentive firms in response to both expansionary and contractionary monetary shocks. To formally test the hypothesis, we conduct a Wald test with the null hypothesis  $ H_{0}: \beta_{dv_{+}} = \beta_{dv_{-}} $.

### 4.3. Empirical results

Our baseline results are reported in Table 5. In the first column, we estimate the effect of high-frequency monetary shocks without our attention measures and find that a 25 basis point expansionary monetary shock is associated with about a 1.4% increase in stock prices. This result is consistent with existing estimates from Gorodnichenko and Weber (2016) and Nakamura and Steinsson (2018). The second column introduces the unconditional interaction between monetary shocks and firm attention. We find that attentive firms experience slightly higher stock returns than their inattentive counterparts, but our estimate is not statistically distinguishable from zero. This result is consistent with the framework outlined in Section 3, which remains agnostic as to the average interaction over the entire range of monetary shocks.

The main results from equation (8) are presented in the third column. We test whether attention leads to differential responses to positive and negative monetary shocks. Consistent with predictions from rational inattention models, attentive firms appear to experience larger increases

<div style="text-align: center;"><div style="text-align: center;">TABLE 5 Baseline results</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2"></td><td colspan="4">Baseline results</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(1) Average</td><td style='text-align: center; word-wrap: break-word;'>(2) Exposure</td><td style='text-align: center; word-wrap: break-word;'>(3) Attention</td><td style='text-align: center; word-wrap: break-word;'>(4) excl. ZLB</td></tr><tr><td rowspan="2">Shock</td><td style='text-align: center; word-wrap: break-word;'>5.55 $ ^{***} $</td><td style='text-align: center; word-wrap: break-word;'>3.58</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(1.16)</td><td style='text-align: center; word-wrap: break-word;'>(2.34)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td rowspan="2">Attention</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.02</td><td style='text-align: center; word-wrap: break-word;'>-0.07</td><td style='text-align: center; word-wrap: break-word;'>-0.04</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.05)</td><td style='text-align: center; word-wrap: break-word;'>(0.06)</td><td style='text-align: center; word-wrap: break-word;'>(0.06)</td></tr><tr><td rowspan="2">Shock  $ \times $ Attn</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.94</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.68)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td rowspan="2">Shock  $ \times $  $ \mathbb{1}_{v_t &gt; 0} $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>3.80</td><td style='text-align: center; word-wrap: break-word;'>5.40 $ ^{**} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(2.48)</td><td style='text-align: center; word-wrap: break-word;'>(2.53)</td></tr><tr><td rowspan="2">Shock  $ \times $  $ \mathbb{1}_{v_t &lt; 0} $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-4.04</td><td style='text-align: center; word-wrap: break-word;'>-1.42</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(3.64)</td><td style='text-align: center; word-wrap: break-word;'>(3.67)</td></tr><tr><td rowspan="2">Shock  $ \times $ Attn  $ \times $  $ \mathbb{1}_{v_t &gt; 0} $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1.87 $ ^{***} $</td><td style='text-align: center; word-wrap: break-word;'>1.47 $ ^{**} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.66)</td><td style='text-align: center; word-wrap: break-word;'>(0.68)</td></tr><tr><td rowspan="2">Shock  $ \times $ Attn  $ \times $  $ \mathbb{1}_{v_t &lt; 0} $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-6.16 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>-6.12 $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(3.02)</td><td style='text-align: center; word-wrap: break-word;'>(3.11)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Observations</td><td style='text-align: center; word-wrap: break-word;'>603940</td><td style='text-align: center; word-wrap: break-word;'>603940</td><td style='text-align: center; word-wrap: break-word;'>603940</td><td style='text-align: center; word-wrap: break-word;'>458794</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R $ ^2 $</td><td style='text-align: center; word-wrap: break-word;'>0.018</td><td style='text-align: center; word-wrap: break-word;'>0.022</td><td style='text-align: center; word-wrap: break-word;'>0.025</td><td style='text-align: center; word-wrap: break-word;'>0.027</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Clustered SE</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Firm controls</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4-digit NAICS FE</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>excl. ZLB</td><td style='text-align: center; word-wrap: break-word;'>no</td><td style='text-align: center; word-wrap: break-word;'>no</td><td style='text-align: center; word-wrap: break-word;'>no</td><td style='text-align: center; word-wrap: break-word;'>yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Wald Test  $ p $-value</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.017</td><td style='text-align: center; word-wrap: break-word;'>0.031</td></tr></table>

Notes: We have normalized the sign of the monetary shock  $ \nu_t $ so that a positive shock is expansionary (corresponding to a decrease in interest rates). Column (1) reports the average effect of monetary shocks from estimating  $ r_{it} = \delta_j + \beta_v \nu_t + \Gamma' X_t + \varepsilon_{it} $. Column (2) estimates the exposure model  $ r_{it} = \delta_j + \delta_i' \nu_t + \beta_v \nu_t + \beta_d d_{it} + \beta_d v_t \nu_t $  $ (1 + \Gamma' X_t + \Gamma' X_t \nu_t + \varepsilon_{it}) $. Column (3) estimates the baseline attention model equation (8):  $ r_{it} = \beta_d d_{it} + \beta_1 \nu_t \nu_0 + \beta_v + \nu_t \nu_t + \nu_0' \nu_t \nu_t + \nu_0'' \nu_t \nu_t < 0 + \beta_d v_t + (d_{it} \nu_t \nu_t > 0) + \beta_d v_t - (d_{it} \nu_t \nu_t < 0) + \delta_j + \delta_i \nu_t + \Gamma' X_t + \Gamma' X_t \nu_t + \varepsilon_{it} $, where  $ \nu_t $ is the monetary shock,  $ d_{it} $ is the prevalence attention measure,  $ \delta_j $ is an industry fixed effect,  $ \delta_i' \nu_t $ is its interaction with the shock, and  $ X_t $ contains firm-level controls of size, age and leverage. The vector  $ X_t \nu_t $ contains the interactions between firm controls and the shock. Column (4) re-estimates equation (8) on the sample ending in 2007 to exclude the zero lower bound period following the Great Recession. Standard errors are clustered at the shock level and reported in parentheses.  $ * $ ( $ p < 0.10 $),  $ ** $ ( $ p < 0.05 $),  $ *\*\* $ ( $ p < 0.01 $).

in stock returns following expansionary monetary shocks and smaller decreases in stock returns following contractionary monetary shocks. The coefficients are statistically different from zero, and the Wald test of whether these coefficients are equivalent is rejected at 5% significance. Column 4 shows that this result is not driven by outsized monetary surprises during the Great Recession nor unconventional monetary policy at the zero lower bound by ending the sample in 2007.

The asymmetric response to positive and negative shocks is inconsistent with alternative interpretations of the textual measure that predict a symmetric effect. The foremost alternative discussed in Section 3 is that the textual measure identifies exposure to monetary shocks rather than attention. Any such symmetric effect would also appear in the interaction coefficient  $ \beta_{dv} $ in Column 2, which is only weakly positive. Appendix B.2 further shows that directly estimating and controlling for exposure to monetary shocks leaves our main findings unchanged.

Suboptimal responses to monetary policy by inattentive firms reported in Table 5, together with the large fraction of inattentive firms documented in Figure 4, provide some of the first direct evidence of the empirical consequences of firm inattention in the U.S. We estimate that inattentive firm returns rise by nearly 2% less following positive shocks and drop by 6% more

following negative shocks compared with those of their attentive peers. These differences are substantial given the average stock return response of 5.6%.

Alternative sources of asymmetry. We now consider alternative explanations for the asymmetric price response documented above. Each explanation is tested by augmenting our baseline model to include interaction terms for a confounding variable,  $ c_{it} $, that match those for firm attention,  $ d_{it} $. The resulting “horse-race” model takes the form

 $$ \begin{aligned}r_{it}&=\delta_{j}+\delta_{j}\nu_{t}+\beta_{1}\mathbb{1}_{\nu_{t}>0}+\beta_{\nu_{+}}\nu_{t}\mathbb{1}_{\nu_{t}>0}+\beta_{\nu_{-}}\nu_{t}\mathbb{1}_{\nu_{t}<0}\\&+\left[\beta_{d}d_{it}+\beta_{d\nu_{+}}(d_{it}\nu_{t}\mathbb{1}_{\nu_{t}>0})+\beta_{d\nu_{-}}(d_{it}\nu_{t}\mathbb{1}_{\nu_{t}<0})\right]\\&+\left[\beta_{c}c_{it}+\beta_{c v_{+}}(c_{it}\nu_{t}\mathbb{1}_{\nu_{t}>0})+\beta_{c v_{-}}(c_{it}\nu_{t}\mathbb{1}_{\nu_{t}<0})\right]+\Gamma_{1}^{\prime}X_{t}+\Gamma_{2}^{\prime}X_{t}\nu_{t}+\varepsilon_{it},\\ \end{aligned} $$ 

where, as in the baseline specification, we control for industry fixed effects, industry-specific responses to monetary shocks, a vector of firm controls and their interaction with monetary shocks. If the main result,  $ \beta_{dv_{-}} < 0 < \beta_{dv_{+}} $, holds true, then we rule out  $ c_{it} $ as a confounding source of asymmetry.

The first factor considered is productivity. Van Nieuwerburgh and Veldkamp (2006) present a model in which higher productivity increases learning as well as production. If productivity determines both information acquisition and the response to aggregate shocks, it could explain the asymmetric result found above. Productivity is constructed as above in Section 2.3.

Management quality is another potential confounder that could explain both attention and firm performance. Effective managers who capitalize on opportunities during expansionary shocks and mitigate losses from contractionary shocks will generate the same asymmetric performance pattern documented in our main results. We approximate a firm’s management quality using the share of board members who hold a graduate degree since existing research documents a strong relationship between education and management quality (Bloom and Van Reenen 2010). $ ^{19} $ Data on the educational attainment is from BoardEx (BoardEX 2021), which covers publicly traded U.S. firms.

The third variable considered is a firm’s financial performance measured using return on assets (ROA). Managers may feel compelled to cite macroeconomic conditions when explaining recent performance, and a tendency for well-performing firms to cite such conditions could generate the asymmetry observed.

Finally, we control for the length of a firm's SEC filing as a measure of its preference for information provision. Longer filings—measured using log word count—offer more opportunities for managers to mention macro keywords and signal commitment to due diligence. If thorough due diligence engenders investor confidence, then stocks should perform better following either positive or negative monetary shocks.

Table 6 reports the estimates for equation (9) using each factor described above: productivity, management quality, profitability, and filing length. As in our baseline results, attentive firms experience a larger increase in market value following an expansionary shock and a smaller contraction following a contractionary shock. The estimates are statistically significant, with similar magnitudes as those in Table 5. While some of the control variables (e.g. filing length) also display an asymmetric effect on firms' responses to monetary shocks, the explanatory power of firm attention remains under all specifications. All four Wald tests for  $ H_0: \beta_{dv_+} = \beta_{dv_-} $ are rejected at 5% significance. In Appendix Table A.3, we show that these results are also robust to excluding zero-lower-bound periods.

19. Graduate degrees include MBA, MS, MSC, MA, JD, MD, MPA, MSE, PHD, and any degree names that include “master” or “doctor.”

<div style="text-align: center;"><div style="text-align: center;">TABLE 6</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Controlling for alternative explanations of asymmetry</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Productivity (LTFP)</td><td style='text-align: center; word-wrap: break-word;'>Mgmt quality</td><td style='text-align: center; word-wrap: break-word;'>Profit (ROA)</td><td style='text-align: center; word-wrap: break-word;'>Filing length</td></tr><tr><td rowspan="2">Shock  $ \times $  $ \mathbb{1}_{v_t}&gt;0 $</td><td style='text-align: center; word-wrap: break-word;'>6.24 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>-0.21</td><td style='text-align: center; word-wrap: break-word;'>3.38</td><td style='text-align: center; word-wrap: break-word;'>-2.38</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(2.55)</td><td style='text-align: center; word-wrap: break-word;'>(2.16)</td><td style='text-align: center; word-wrap: break-word;'>(2.43)</td><td style='text-align: center; word-wrap: break-word;'>(4.95)</td></tr><tr><td rowspan="2">Shock  $ \times $  $ \mathbb{1}_{v_t}&lt;0 $</td><td style='text-align: center; word-wrap: break-word;'>-1.39</td><td style='text-align: center; word-wrap: break-word;'>-10.34 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>-4.54</td><td style='text-align: center; word-wrap: break-word;'>21.52</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(3.78)</td><td style='text-align: center; word-wrap: break-word;'>(4.08)</td><td style='text-align: center; word-wrap: break-word;'>(3.58)</td><td style='text-align: center; word-wrap: break-word;'>(13.85)</td></tr><tr><td rowspan="2">Attention</td><td style='text-align: center; word-wrap: break-word;'>-0.12</td><td style='text-align: center; word-wrap: break-word;'>-0.09</td><td style='text-align: center; word-wrap: break-word;'>-0.07</td><td style='text-align: center; word-wrap: break-word;'>-0.08 $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.09)</td><td style='text-align: center; word-wrap: break-word;'>(0.06)</td><td style='text-align: center; word-wrap: break-word;'>(0.06)</td><td style='text-align: center; word-wrap: break-word;'>(0.05)</td></tr><tr><td rowspan="2">Shock  $ \times $ Attn  $ \times $  $ \mathbb{1}_{v_t}&gt;0 $</td><td style='text-align: center; word-wrap: break-word;'>2.46 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>2.29 $ ^{***} $</td><td style='text-align: center; word-wrap: break-word;'>1.85 $ ^{***} $</td><td style='text-align: center; word-wrap: break-word;'>1.68 $ ^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(1.20)</td><td style='text-align: center; word-wrap: break-word;'>(0.79)</td><td style='text-align: center; word-wrap: break-word;'>(0.66)</td><td style='text-align: center; word-wrap: break-word;'>(0.57)</td></tr><tr><td rowspan="2">Shock  $ \times $ Attn  $ \times $  $ \mathbb{1}_{v_t}&lt;0 $</td><td style='text-align: center; word-wrap: break-word;'>-6.82 $ ^{***} $</td><td style='text-align: center; word-wrap: break-word;'>-8.11 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>-6.09 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>-5.51 $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(1.90)</td><td style='text-align: center; word-wrap: break-word;'>(3.23)</td><td style='text-align: center; word-wrap: break-word;'>(3.00)</td><td style='text-align: center; word-wrap: break-word;'>(2.79)</td></tr><tr><td rowspan="2">Control Var</td><td style='text-align: center; word-wrap: break-word;'>0.04 $ ^{***} $</td><td style='text-align: center; word-wrap: break-word;'>-0.05</td><td style='text-align: center; word-wrap: break-word;'>0.04 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>-0.01</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.06)</td><td style='text-align: center; word-wrap: break-word;'>(0.02)</td><td style='text-align: center; word-wrap: break-word;'>(0.04)</td></tr><tr><td rowspan="2">Control  $ \times $ Shock  $ \times $  $ \mathbb{1}_{v_t}&gt;0 $</td><td style='text-align: center; word-wrap: break-word;'>-0.08</td><td style='text-align: center; word-wrap: break-word;'>1.80 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>-1.37</td><td style='text-align: center; word-wrap: break-word;'>0.66 $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.14)</td><td style='text-align: center; word-wrap: break-word;'>(0.75)</td><td style='text-align: center; word-wrap: break-word;'>(1.60)</td><td style='text-align: center; word-wrap: break-word;'>(0.38)</td></tr><tr><td rowspan="2">Control  $ \times $ Shock  $ \times $  $ \mathbb{1}_{v_t}&lt;0 $</td><td style='text-align: center; word-wrap: break-word;'>-0.18</td><td style='text-align: center; word-wrap: break-word;'>-3.56</td><td style='text-align: center; word-wrap: break-word;'>-9.02 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>-2.70 $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.22)</td><td style='text-align: center; word-wrap: break-word;'>(2.76)</td><td style='text-align: center; word-wrap: break-word;'>(4.22)</td><td style='text-align: center; word-wrap: break-word;'>(1.56)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Observations</td><td style='text-align: center; word-wrap: break-word;'>386094</td><td style='text-align: center; word-wrap: break-word;'>337927</td><td style='text-align: center; word-wrap: break-word;'>603065</td><td style='text-align: center; word-wrap: break-word;'>603940</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R $ ^2 $</td><td style='text-align: center; word-wrap: break-word;'>0.026</td><td style='text-align: center; word-wrap: break-word;'>0.039</td><td style='text-align: center; word-wrap: break-word;'>0.026</td><td style='text-align: center; word-wrap: break-word;'>0.026</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Clustered SE</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Firm controls</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4-digit NAICS FE</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>excl. ZLB</td><td style='text-align: center; word-wrap: break-word;'>no</td><td style='text-align: center; word-wrap: break-word;'>no</td><td style='text-align: center; word-wrap: break-word;'>no</td><td style='text-align: center; word-wrap: break-word;'>no</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Wald test p-value: Attention</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>0.003</td><td style='text-align: center; word-wrap: break-word;'>0.018</td><td style='text-align: center; word-wrap: break-word;'>0.022</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Wald test p-value: Control</td><td style='text-align: center; word-wrap: break-word;'>0.473</td><td style='text-align: center; word-wrap: break-word;'>0.071</td><td style='text-align: center; word-wrap: break-word;'>0.114</td><td style='text-align: center; word-wrap: break-word;'>0.042</td></tr></table>

 $$ r_{i t}=\delta_{j}+\delta_{j}\nu_{t}+\beta_{1}\mathbb{1}_{\nu_{t}>0}+\beta_{\nu_{+}}\nu_{t}\mathbb{1}_{\nu_{t}>0}+\beta_{\nu_{-}}\nu_{t}\mathbb{1}_{\nu_{t}<0}+\beta_{d}d_{i t}+\beta_{d\nu_{+}} $$ 

(dᵢᵥᵣ₁ᵀ₁ᵃ₁₀ + βᵥᵣ₁₀(dᵢᵥᵣ₁₀₁₀ + βᵥᵣ₁₀ + βᵥᵣ₁₀ + βᵥᵣ₁

Additional robustness checks. Further robustness analysis pertaining to the identification of high-frequency monetary shocks can be found in Appendix B. Appendix B.3 controls for the information effect of FOMC announcements using Greenbook forecast revisions, and Appendix B.4 tests whether aggregate conditions confound the estimated effect of high-frequency shocks. In each case, our main results remain robust.

## 5. ATTENTION, PERFORMANCE, AND AGGREGATE UNCERTAINTY

This section explores how attention affects firm performance under varying levels of aggregate uncertainty. One implication of our illustrative model is that the performance gap between attentive and inattentive firms widens with the magnitude of nominal demand shocks. Returns to attention should therefore increase in periods of greater uncertainty and larger shocks. $ ^{20} $

We test this prediction by estimating the interaction effect between attention and uncertainty on firm performance. Aggregate uncertainty is measured using the interquartile range of quarterly forecasts for real GDP, inflation, and unemployment from the Survey of Professional Forecasters (SPF 2023). Each series is standardized over our sample period (1994–2019) and then averaged into a composite uncertainty index.

Firm performance is measured along three dimensions: profitability, financial performance, and survival. Profitability is measured as a firm's return on assets (ROA), which we construct using earnings before extraordinary items over total assets. Financial performance is measured as return on equity (ROE) using earnings before extraordinary items over market capitalization. Finally, survival is defined as whether a firm remains in operation in the next year. Each variable is constructed using annual Compustat data, and ROA and ROE are winsorized at 1%.

Our regression model takes the form

 $$ y_{i t}=\alpha_{j}+\beta d_{i t}+\delta\sigma_{t}+\gamma d_{i t}\cdot\sigma_{t}+\Gamma^{\prime}Z_{i t}+\varepsilon_{i t}, $$ 

where  $ y_{it} $ represents one of the three performance variables defined above,  $ d_{it} $ is our binary attention measure,  $ \sigma_{t} $ is aggregate uncertainty,  $ \alpha_{j} $ captures industry fixed effects with 4-digit NAICS, and  $ Z_{it} $ is a vector of firm controls including size, age, and 10-K filing length (as previously defined). Standard errors are clustered by both year and industry. We extend the model to future outcomes,  $ y_{i,t+h} $, to capture any lagged effects of attention on performance.

Results from this analysis are reported in Table 7. On average, aggregate uncertainty reduces profitability, financial performance, and the probability of survival, which is consistent with existing models of uncertainty (e.g. Bloom et al. 2007). $ ^{21} $ Attention to macroeconomic conditions, however, mitigates the negative effects of uncertainty: in periods of high uncertainty, attentive firms have higher profitability, better financial performance, and a higher probability of survival. Interestingly, the first row in Table 7 suggests that attention reduces firm performance under low uncertainty, consistent with models of imperfect information in which firms face a cost of attention and reap the benefit in states with large realized shocks (such as Reis 2006). $ ^{22} $ Appendix Table A.7 further interacts attention with recession indicators and shows that attention improves firm performance mainly by reducing uncertainty.

Section 4 showed that attentive firms respond better to monetary shocks. This section finds that these same firms outperform less attentive competitors under elevated aggregate uncertainty. Together, they paint a picture of attentive firms as more responsive to evolving macroeconomic conditions and highlight the benefits gained for their diligence.

## 6. QUANTITATIVE MODEL

Our attention measure can inform model-based analysis in addition to the new empirical findings above. This section presents a quantitative model in which inattention to aggregate conditions drives monetary non-neutrality. Both the rate of attentive firms and the cost of inattention are calibrated using the prevalence measure presented in Section 2. This model demonstrates the

<div style="text-align: center;"><div style="text-align: center;">TABLE 7</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Effects of attention on firm performance under uncertainty</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td colspan="2">ROE</td><td colspan="2">ROA</td><td colspan="2">Survival</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(1) Impact</td><td style='text-align: center; word-wrap: break-word;'>(2) Peak</td><td style='text-align: center; word-wrap: break-word;'>(3) Impact</td><td style='text-align: center; word-wrap: break-word;'>(4) Peak</td><td style='text-align: center; word-wrap: break-word;'>(5) Impact</td><td style='text-align: center; word-wrap: break-word;'>(6) Peak</td></tr><tr><td rowspan="2">Attention (general)</td><td style='text-align: center; word-wrap: break-word;'>$ -0.02^{*} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.02^{**} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.02^{*} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.03^{**} $</td><td style='text-align: center; word-wrap: break-word;'>-0.01</td><td style='text-align: center; word-wrap: break-word;'>$ -0.02^{**} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.01)</td></tr><tr><td rowspan="2">Uncertainty (SPF IQR)</td><td style='text-align: center; word-wrap: break-word;'>$ -0.03^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.02^{*} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.05^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.04^{*} $</td><td style='text-align: center; word-wrap: break-word;'>-0.01</td><td style='text-align: center; word-wrap: break-word;'>$ -0.03^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.02)</td><td style='text-align: center; word-wrap: break-word;'>(0.02)</td><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.01)</td></tr><tr><td rowspan="2">Attention  $ \times $ uncertainty</td><td style='text-align: center; word-wrap: break-word;'>0.03^{***}</td><td style='text-align: center; word-wrap: break-word;'>0.03^{***}</td><td style='text-align: center; word-wrap: break-word;'>0.05^{***}</td><td style='text-align: center; word-wrap: break-word;'>0.06^{***}</td><td style='text-align: center; word-wrap: break-word;'>0.01</td><td style='text-align: center; word-wrap: break-word;'>0.03^{**}</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.02)</td><td style='text-align: center; word-wrap: break-word;'>(0.02)</td><td style='text-align: center; word-wrap: break-word;'>(0.01)</td><td style='text-align: center; word-wrap: break-word;'>(0.01)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Observations</td><td style='text-align: center; word-wrap: break-word;'>104507</td><td style='text-align: center; word-wrap: break-word;'>92023</td><td style='text-align: center; word-wrap: break-word;'>110267</td><td style='text-align: center; word-wrap: break-word;'>97180</td><td style='text-align: center; word-wrap: break-word;'>111637</td><td style='text-align: center; word-wrap: break-word;'>66813</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R $ ^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.163</td><td style='text-align: center; word-wrap: break-word;'>0.156</td><td style='text-align: center; word-wrap: break-word;'>0.247</td><td style='text-align: center; word-wrap: break-word;'>0.236</td><td style='text-align: center; word-wrap: break-word;'>0.034</td><td style='text-align: center; word-wrap: break-word;'>0.028</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Clustered SE</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Firm controls</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4-digit NAICS FE</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td><td style='text-align: center; word-wrap: break-word;'>yes</td></tr></table>

Notes: The table reports results from estimating (10),  $ y_{it}^{h} = \alpha_{j} + \beta d_{it} + \delta \sigma_{t} + \gamma d_{it} \cdot \sigma_{t} + \Gamma' Z_{it} + \varepsilon_{it} $, for horizons  $ h = 1, \ldots, 5 $. The dependent variables  $ y_{t} $ include (i) profitability measured with ROA (i.e. net income over total assets), (ii) financial performance measured with ROE (i.e. net income over equity), and (iii) an indicator variable for firm survival. Independent variables include the prevalence attention to general economic conditions,  $ d_{it} $; macroeconomic uncertainty,  $ \sigma_{t}^{2} $; measured as the interquartile range of quarterly growth rate forecasts for real GDP and unemployment from the SPF; the interaction between attention and uncertainty; industry fixed effects  $ \delta_{j} $; and firm controls,  $ Z_{it} $. We standardize the interquartile range of each series over our observed sample period, take the absolute average deviation each quarter, and then average these quarterly values each year. The on-impact effect corresponds to the estimates for  $ h = 1 $. The peak effect corresponds to the largest estimated marginal effect over the 5-year horizon. Standard errors are clustered at the shock level and reported in parentheses.  $ * $ ( $ p < 0.10 $),  $ ** $ ( $ p < 0.05 $),  $ *\*\* $ ( $ p < 0.01 $).

importance of attention by showing that the efficacy of monetary policy depends on aggregate attention when firms face information frictions.

### 6.1. Model environment

We start with a canonical dynamic general-equilibrium model with rationally inattentive firms as in Maćkowiak and Wiederholt (2009) and Afrouzi and Yang (2021a). Time is discrete and infinite. The economy consists of a representative household, heterogeneous firms, and a central bank. Households and the central bank have full information about the economy, while firms pay a cost proportional to information obtained (measured using Shannon mutual information as in Sims 2003). Firms differ ex-ante in their marginal costs of information, which is motivated by the heterogeneity documented in Section 2.3.

Household. A representative household consumes a bundle of goods over the continuum of varieties  $ i \in [0, 1] $ and supplies labour,  $ N_t $, in a competitive labour market with wage,  $ W_t $. In addition to the wage income, the household has access to a one-period bond,  $ D_t $, with the interest rate  $ \iota_t $ and receives firms’ profits,  $ \Pi_t $. The household maximizes its life-time utility:

 $$ \begin{aligned}&\max_{\{C_{it},D_{t},N_{t}\}_{t=0}^{\infty}}\mathbb{E}_{0}\sum_{t=0}^{\infty}\beta^{t}(\log C_{t}-\psi N_{t}),\\&s.t.\int_{0}^{1}P_{it}C_{it}di+D_{t}\leq W_{t}N_{t}+(1+\iota_{t})D_{t-1}+\Pi_{t},\end{aligned} $$ 

where consumption, $C_t$, is aggregated over each good type $i$ with a CES aggregator, $C_t = \left(\int_0^1 C_{it}^{\frac{\varepsilon-1}{\varepsilon}} di\right)^{\frac{\varepsilon}{\varepsilon-1}}$, and $\varepsilon$ is the elasticity of substitution. Let $Q_t \equiv P_t C_t$ denote nominal aggregate demand. The household's optimal choices are given by the following three conditions

 $$ C_{it}=C_{t}(P_{it}/P_{t})^{-\varepsilon};1=\beta(1+\iota_{t})\mathbb{E}_{t}(Q_{t}/Q_{t+1});W_{t}=\psi Q_{t}. $$ 

Central bank. The central bank targets the aggregate money supply,  $ P_{t}C_{t} $, similar to Caplin and Spulber (1987) and Gertler and Leahy (2008). Nominal aggregate demand, therefore, follows

 $$ \Delta\log Q_{t}=\rho\Delta\log Q_{t-1}+\nu_{t},\nu_{t}\sim N(0,\sigma_{\nu}^{2}). $$ 

Firms. There is a unit measure of monopolistically competitive firms, indexed by  $ i \in [0, 1] $. Firms operate a decreasing-returns-to-scale production technology with labour as its only input:  $ Y_{it} = N_{it}^{\gamma} $. They take wage and demand as given and can flexibly set prices,  $ P_{it} $, based on their information set in period  $ t $. After setting prices, they hire labour from a competitive labour market to produce the realized level of demand induced by their prices.

Firms are assumed to be rationally inattentive, meaning that they do not observe shocks to aggregate demand and endogenously acquire information about  $ Q_t $. In each period, firm  $ i $ starts with their information set from the previous period,  $ S_i^{t-1} $, and selects the stochastic process for their new signal,  $ s_{it} $, from a set of available signals,  $ S^t $, that vary in cost and precision. These signals satisfy the properties outlined in Definition 3.

Definition 3 (set of available signals). The set of available signals,  $ S^{t} $, consists of all signal processes satisfying the following three properties:

(i)  $ S^t $ is rich: for any posterior distribution on  $ \{Q_t\}_{t\geq0} $, there is a set of signals  $ S^t \in S^t $ that generate that posterior;

(ii) Signals do not expire over time:  $ S^{t} \subset S^{t+h} $ fo

(iii) Signals contain no information about future shocks:  $ S_t \perp Q_{t+h} $ for  $ S_t \in S^t $ and  $ h \geq 1 $.

We assume that the cost of information is linear in the Shannon mutual information:

 $$ 2\omega_{i}\cdot\mathcal{I}(Q_{t};s_{i t}|S_{i}^{t-1}), $$ 

where the Shannon mutual information,  $ \mathcal{I}(Q_t; s_{it}|S_i^{t-1}) $, measures the expected reduction in uncertainty about aggregate demand from observing the signal. $ ^{23} $ A more precise signal requires a higher flow of mutual information and is therefore more expensive.

The information represented by  $ \mathcal{I}(\cdot) $ can be thought of as a firm’s attention to the economy: for each unit of mutual information (or nat), a firm pays a marginal cost,  $ \omega_i $, and reduces its expected uncertainty about aggregate demand. A firm’s information set evolves according to  $ S_i^t = S_i^{t-1} \cup s_{it} $.

Firms are ex-ante heterogeneous in their information-processing technology and face either high or low marginal costs of attention

 $$ \omega_{i}\in\{\omega_{H},\omega_{L}\}. $$ 

A fraction  $ \theta \in (0, 1) $ of firms are assumed to have low information-processing costs, while all remaining firms face high costs.

Firms maximize expected profits by choosing the stochastic process of the set of signals to observe over time,  $ \{s_{it} \in \mathcal{S}_{it}\}_{t \geq 0} $, and a pricing strategy,  $ P_{it}(S_i^t) $, that depends on its information set at time  $ t $ containing realizations of current and past signals. The firm’s problem is given by

 $$ \begin{aligned}\max_{\{s_{i t}\in\mathcal{S}_{i t},P_{i t}(S_{i}^{t})\}_{t\geq0}}\mathbb{E}&\left[\sum_{t=0}^{\infty}\beta^{t}\frac{1}{P_{t}C_{t}}\Big(\underbrace{\big(P_{i t}Y_{i t}-W_{t}N_{i t}\big)}_{operational profits}-\underbrace{2\omega_{i}\mathcal{I}(Q_{i};s_{i t}|S_{i}^{t-1})}_{information costs}\Big)\Big|S_{i}^{-1}\right]\quad(16)\\ s.t.\quad Y_{i t}&=Y_{t}(P_{i t}/P_{t})^{-\varepsilon}\tag{demand for goods}\\Y_{i t}&=N_{i t}^{\gamma}\tag{production technology}\\S_{i}^{t}&=S_{i}^{t-1}\cup s_{i t},\tag{evolution of information}\end{aligned} $$ 

where  $ Y_{t} $ is the aggregate output,  $ P_{t} $ is the aggregate price index,  $ P_{it} $ is firm i's price,  $ Y_{it} $ is the demand for the firm's good,  $ N_{it} $ is the firm's labour demand.

Equilibrium. Given the exogenous process for aggregate demand,  $ \{\Delta \log Q_t\}_{t \geq 0} $, the equilibrium consists of an allocation for the household,  $ \Omega^H = \{C_t, D_t, N_t, (C_{it})_{i \in [0,1]}\}_{t \geq 0} $, allocations for every firm  $ i \in [0,1] $ given their initial information sets  $ S_i^{-1} $,  $ \Omega_i^F = \{s_{it} \in S_{it}, P_{it}, N_{it}, Y_{it}\}_{t \geq 0} $, a set of prices  $ \{t_t, P_t, W_t\}_{t \geq 0} $, and a stationary distribution over firms' states such that

(i) Given the set of prices and firms' allocations, the household's allocation solves the problem in equation (11);

(ii) Given the set of prices and the household’s allocation, firms’ allocations solve the problem in equation (16);

(iii) All markets clear, that is, for  $ t \geq 0 $ and  $ i \in [0, 1] $,  $ D_t = 0 $,  $ Y_{it} = C_{it} $,  $ Y_t = C_t $, and  $ N_t = \int_0^1 N_{it} \, dt $.

Solution. We approximate a firm’s flow profits with second-order log approximations around the full-information steady state. $ ^{24} $ A firm’s total value under log approximation, v, is decomposed into a full-information value,  $ \nu^* $, representing the firm’s value under optimal pricing with full information, and the imperfect information value,  $ \tilde{\nu} $, representing firm value under imperfect information.

Let lowercase letters denote log deviations from the steady state. The imperfect-information value is given by

 $$ \begin{align*}\tilde{v}&=\max_{\{s_{it}\in\mathcal{S}_{it},p_{it}(S_{i}^{t})\}_{t\geq0}}\mathbb{E}\left[\sum_{t=0}^{\infty}\beta^{t}\Big(-B(p_{it}-p_{t}^{*})^{2}-2\omega_{i}\mathcal{I}(q_{t};s_{it}|S_{i}^{t-1})\Big)\Big|S_{i}^{-1}\right]\\&s.t.\quad p_{t}^{*}=\alpha p_{t}+(1-\alpha)q_{t}\\&\quad S_{i}^{t}=S_{i}^{t-1}\cup s_{it},\end{align*} $$ 

where  $ \alpha \in (0, 1) $ and  $ B > 0 $ are constants that depend on non-information-friction parameters and relate to the degree of strategic complementarity and the curvature of the profit function, respectively. $ ^{25} $  $ p_t^* $ denotes the optimal price under perfect information. Since prices are fully flexible, price setting with perfect information is a static problem (see Appendix E.2).

The imperfect information problem in (17) is solved numerically based on the algorithm for dynamic rational inattention problems (DRIPs) developed in Afrouzi and Yang (2021a). Appendix E.3 provides detailed information on its implementation.

### 6.2. Calibration

Model parameters are divided into two sets: those that govern information frictions and all remaining parameters. In the first set, the share of attentive firms and relative cost of information between firms are calibrated to match two empirical moments using our text-based measure of attention. The cost of information among attentive firms,  $ \omega_{L} $, is set near zero so that attentive firms have nearly full information. The second set of non-information parameters are calibrated to external sources or estimates using quarterly data on U.S. output from the Bureau of Economic Analysis. A summary of all model parameters can be found in Appendix Table A.9.

For non-information parameters, we calibrate the model quarterly and set the discount rate to be  $ \beta = 0.96^{1/4} $. The stochastic process for aggregate demand,  $ \{\rho, \sigma_v\} $, is estimated using quarterly U.S. nominal manufacturing output between 1994 and 2019. Restricting to the manufacturing sector is consistent with the within-sector results presented in our empirical analysis. The elasticity of substitution is set to  $ \varepsilon = 10 $, implying a steady-state markup of 11%, and the disutility of labour is set to  $ \psi = 0.90 $. Finally, we set returns to scale  $ \gamma = 0.93 $ according to the estimate by Basu and Fernald (1997) for the U.S. manufacturing sector.

For information parameters, the share of firms with low information costs,  $ \theta $, is set to 65% to match the share of attentive firms in Figure 3. As in Mackowiak et al. (2009) and Afrouzi and Yang (2021b), attention depends inversely on the ratio between attention costs and the curvature of the profit function,  $ \omega_i/B $. A firm pays greater attention when the information cost is low or when its incentives to pay attention are high. We focus on calibrating information parameters and therefore fix the curvature of profit function, which depends on non-information parameters.

We set  $ \omega_L $ close to zero to reflect the assumption that firms with low information costs have nearly full information. The relative cost of information for high-cost firms,  $ \omega_H - \omega_L $, is calibrated to match the heterogeneous responses to monetary shocks estimated in Table 5. Stock returns in the model are defined as the log change in a firm's value,  $ r_{it} = \log V_{it} - \log \mathbb{E}_{t-1}(V_{it}) $ $ ^{26} $. To connect Shannon mutual information,  $ \mathcal{I}_{it} $, in the model with the text-based attention measure, we assume that the frequency of macro keywords in 10-K filings is strictly increasing in firm attention. This allows us to match the cross-sectional distribution of firm attention without explicitly modelling the writing process of 10-K filings. Since our main empirical analysis uses the prevalence attention measure, we define a corresponding indicator variable,  $ d_{it} = \mathbb{1}(\mathcal{I}_{it} > \bar{\mathcal{I}}_t) $, for firms whose attention is above the cross-sectional mean in a given period. Finally, we use  $ \nu_t $ as the monetary shocks.

25. See equations (24) and (25) in the Appendix.

26. A firm’s value function in (16) can be expressed in recursive form as

 $$ V(S_{i}^{t-1})=\max_{\{s_{i t}\in\mathcal{S}_{i t},P_{i t}(S_{i}^{t})\}_{t\geq0}}\mathbb{E}_{t}\Big[\frac{1}{P_{t}}\Big(\big(P_{i t}Y_{i t}-W_{t}N_{i t}\big)-2\omega_{i}\mathcal{I}(Q_{t};s_{i t}|S_{i}^{t-1})\Big)+\beta\Lambda_{t,t+1}V(S_{i}^{t})\Big|S_{i}^{t-1}\Big] $$ 

 $$ \begin{array}{r l}{\mathrm{s.t.}}&{Y_{i t}=Y_{t}(P_{i t}/P_{t})^{-\varepsilon},\quad Y_{i t}=N_{i t}^{\gamma},\quad S_{i}^{t}=S_{i}^{t-1}\cup s_{i t}.}\end{array} $$ 

We simulate the model for a panel of 100 firms and for 1000 quarters, discarding the first 100 quarters as burn-in. With the simulated data, we estimate

 $$ \begin{align*}r_{it}&=c+\beta_{1}\mathbb{1}_{\nu_{t}>0}+\beta_{\nu_{+}}\nu_{t}\mathbb{1}_{\nu_{t}>0}+\beta_{\nu_{-}}\nu_{t}\mathbb{1}_{\nu_{t}<0}+\beta_{d} d_{it}\\&\quad+\beta_{d\nu_{+}}d_{it}\nu_{it}\mathbb{1}_{\nu_{t}>0}+\beta_{d\nu_{-}}d_{it}\nu_{it}\mathbb{1}_{\nu_{t}<0}+\varepsilon_{it}.\end{align*} $$ 

We set  $ \omega_H - \omega_L $ to target the elasticity  $ \frac{1}{2} |\hat{\beta}_{dv_+}| + \frac{1}{2} |\hat{\beta}_{dv_-}| $ from Column 3 in Table 5, which measures the relative stock return losses of firms that do not pay attention. Appendix Figure A.7a shows how the parameter is identified. As  $ \omega_H $ increases and the gap between  $ \omega_L $ and  $ \omega_H $ widens, the simulated elasticity monotonically increases, implying greater heterogeneity between attentive and inattentive firms. The resulting calibration for  $ \omega_H - \omega_L $ is 1.13 per nat.

Discussion of the calibration strategy. One primary challenge to calibrating a rational inattention model is that information costs—which determine the degree of information frictions—are unobserved in the data. Existing studies have successfully calibrated rational inattention parameters by matching moments related to aggregate consumption dynamics and monetary policy responses, while other have calibrated these parameters using survey data (Luo 2008; Maćkowiak and Wiederholt 2015, 2023). Our calibration strategy differs in three main ways. First, we allow heterogeneity in information costs and therefore have two parameters for information costs,  $ \omega_L $ and  $ \omega_H $, instead of a single parameter. We focus on calibrating the heterogeneity in attention costs,  $ \omega_H - \omega_L $, to study its implication for monetary transmission. In doing so, we set  $ \omega_L $ close to zero, which implies that our calibrated model provides a lower bound on the degree of monetary non-neutrality arising from inattention.

Second, our calibration makes use of the text-based attention measure instead of macro data or survey data. The measure informs attention at the granular firm level, but the trade-off is that 10-K filings do not have a direct model counterpart. To connect the concept of Shannon mutual information with our text-based attention measure, we need to assume that the frequency of macro keywords in 10-K filings is strictly increasing in firm attention. This allows us to use the textual measure to discipline the cross-sectional distribution of firm attention.

Lastly, the relative cost of attention,  $ \omega_{H} - \omega_{L} $, is calibrated by targeting a micro elasticity (namely, the relative stock return losses of inattentive firms in response to monetary shocks) rather than macro moments. This is possible because our proposed attention measure is available for a large number of firms over a long sample period. It is well-known since Mehra and Prescott (1985) that standard macro models, including ours, are not designed to match the unconditional cross section of stock returns. However, our target moment in Table 5 is the conditional responses of firm values to monetary shocks, with stock returns,  $ r_{it} $, in equation (8) capturing log changes in a firm's value. Appendix Table A.10 shows that our model matches heterogeneous responses of firms' values to monetary shocks through relative information costs.

For further robustness, Appendix E.5 implements an alternative calibration strategy that targets industry-level price adjustment estimates from Figure 2. It finds that attention remains quantitatively important for the transmission of monetary policy.

### 6.3. Attention and the efficacy of monetary policy

Figure 6 plots the aggregate responses to a one standard deviation expansionary shock to nominal aggregate demand growth. Figure 6a shows that inattentive firms under-adjust prices, reflecting

<div style="text-align: center;"><div style="text-align: center;">(a)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//73b7d56b-c260-42d9-91e4-3854d240cfd4/markdown_2/imgs/img_in_chart_box_160_123_525_476.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A51Z%2F-1%2F%2Fea5f63dbe496c9a059961f5f6cac1203022652d2024fda68babfba7e0047f424" alt="Image" width="34%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(b)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//73b7d56b-c260-42d9-91e4-3854d240cfd4/markdown_2/imgs/img_in_chart_box_538_124_909_476.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-04T14%3A57%3A51Z%2F-1%2F%2Fe0c2eb3e888f638d9eb7664f06b03b63b5112af610f37e9e57389e8faa9f285f" alt="Image" width="34%" /></div>


<div style="text-align: center;"><div style="text-align: center;">FIGURE 6</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Aggregate responses to expansionary monetary shock (a) Inflation and (b) output</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Notes: The figures report impulse responses in percent deviations from the perfect-information steady state of inflation and output for the aggregate economy, attentive firms, and inattentive firms.</div> </div>


partial incorporation of noisy signals about demand. Attentive firms track aggregate demand better than inattentive firms and exhibit more responsive prices. $ ^{27} $

Figure 6b shows that inattentive firms are responsible for increased output following an expansionary shock. Firms set prices and commit to supply the quantity demanded. Since attentive firms raise prices by more in response to an expansionary shock, their output responds by less.

The grey solid lines represent aggregate inflation and output responses, driven by attention costs and the share of attentive firms. $ ^{28} $ Monetary non-neutrality increases with the degree of inattention in the economy. Since we assume attentive firms face near-zero attention costs ( $ \omega_{L} \approx 0 $), the impulse responses in Figure 6 provide a lower bound on the output responses to monetary shocks and an upper bound on the inflation responses.

A key implication of Figure 6b is that the aggregate output response to monetary policy increases with the share of inattentive firms. To illustrate the quantitative scope of the effect, we exogenously vary the fraction of attentive firms and compare output responses in our baseline calibration against two alternatives,  $ \check{\theta} = 56\% $ and  $ \hat{\theta} = 73\% $, which correspond to the minimum and maximum fraction of attentive firms over the sample period.

Table 8 reports the aggregate responses to monetary policy change as the fraction of attentive firms in the economy changes. The response of output growth to monetary policy is 5 basis points (or 42%) weaker in the most attentive calibration compared with the least attentive calibration. This suggests that expansionary policy in the depth of a recession when more firms are

<div style="text-align: center;"><div style="text-align: center;">TABLE 8</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Attention and monetary non-neutrality</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Least attentive</td><td style='text-align: center; word-wrap: break-word;'>Baseline</td><td style='text-align: center; word-wrap: break-word;'>Most attentive</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Fraction of attentive firms  $ \theta $</td><td style='text-align: center; word-wrap: break-word;'>56%</td><td style='text-align: center; word-wrap: break-word;'>65%</td><td style='text-align: center; word-wrap: break-word;'>73%</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Output response</td><td style='text-align: center; word-wrap: break-word;'>0.12%</td><td style='text-align: center; word-wrap: break-word;'>0.09%</td><td style='text-align: center; word-wrap: break-word;'>0.07%</td></tr></table>

Notes: Dependence of output responses on the fraction of attentive firms in the economy. Output responses are calculated as percent deviations from the steady state in response to a 25 basis point rate cut. Calibration for the least and most attentive economy is described in the main text.

paying attention will be weaker than a preemptive interest rate (i.e. leaning against the wind) when aggregate attention is lower. This pattern is consistent with existing studies on the state dependency of monetary policy (e.g. Tenreyro and Thwaites 2016). Similarly, monetary tightening imposes a smaller contractionary effect on output when more firms are attentive to monetary news, which highlights the importance of clear central-bank communication (highlighted, e.g. by Haldane et al. 2021).

## 7. CONCLUSION

The empirical evidence of information frictions that we document in this paper, along with growing evidence in the literature (Candia et al. 2024), highlights firms' deviations from full-information rational expectations (FIRE). To discipline models without FIRE, researchers require an understanding of firms' information sets and expectation-formation processes.

In that direction, this paper presents a new text-based measure of firm attention to macroeconomic news, which will be made available publicly and updated on an ongoing basis. We validate that the measure indeed captures firm attention by testing for an asymmetric prediction of rational inattention on monetary policy transmission. We show that firms that pay attention to the FOMC have larger increases in stock returns after positive monetary shocks and smaller decreases in stock returns after negative monetary shocks, providing direct empirical evidence for the consequences of firm inattention.

The empirical measure can be used in combination with imperfect-information models to ground those theories in data. We demonstrate the value of this measure in a quantitative rational inattention model by showing that time variation in firm attention has important implications for the state dependency of monetary policy. In the model, average inattention drives the degree of monetary non-neutrality. The countercyclical nature of firm attention to macroeconomic news implies that the efficacy of monetary policy is weaker during recessions and should be considered in policy design.

Acknowledgments. We are grateful to John Leahy, Pablo Ottonello, Linda Tesar, and Toni Whited for generous advice and guidance. We thank the Editor, four anonymous referees, Sushant Acharya, Hassan Afrouzi, Yoosoon Chang, Martin Eichenbaum, Xing Guo, Andrei Levchenko, Juan Herreño, Yulei Luo, Alistair Macauley, Albert Marcet, Michael McMahon, Oleksiy Kryvtsov, Laura Veldkamp, Jing Cynthia Wu, Choogryul Yang, and the participants of numerous seminars and conferences for useful comments and suggestions. We also thank Kevin MacLean and Joshua Slive for their generous help with the Canadian survey data and Landon Liu for excellent research assistance. The views expressed herein are those of the authors and not necessarily those of the Bank of Canada. First posted version: 9 November 2020.

#### Supplementary Data

Supplementary data are available at Review of Economic Studies online.

#### Funding

This research received no external funding.

##### Data Availability Statement

The data and code underlying this research are available on Zenodo at https://dx.doi.org/10.5281/zenodo.11529484.

## REFERENCES

ABIS, S. and VELDKAMP, L. (2023), “The Changing Economics of Knowledge Production”, The Review of Financial Studies, 37, 89–118.

ACHARYA, V. V., CROSIGNANI, M. and EISERT, T. (2020), “Zombie Credit and (Dis-) Inflation: Evidence from Europe”, The Journal of Finance, 79, 1883–1929.

AFROUZI, H. (2020), “Strategic Inattention, Inflation Dynamics, and the Non-Neutrality of Money”, Journal of Political Economy, 132, 3378–3420.

AFROUZI, H. and YANG, C. (2021a), "Dynamic Rational Inattention and the Phillips Curve".

—— (2021b), "Selection in Information Acquisition and Monetary Non-Neutrality".

AHNERT, T., DOERR, S., PIERRI, N., et al. (2021), “Does IT Help? Information Technology in Banking and Entrepreneurship” (Tech. Rep., International Monetary Fund).

AMIRAULT, D., RAI, N. and MARTIN, L. (2020), “A Reference Guide for the Business Outlook Survey” (Tech. Rep., Bank of Canada).

AUCLERT, A., ROGNLIE, M. and STRAUB, L. (2020), “Micro Jumps, Macro Humps: Monetary Policy and Business Cycles in an Estimated HANK Model” (Tech. Rep., National Bureau of Economic Research).

AUTOR, D., DORN, D., KATZ, L. F., et al. (2020), “The Fall of the Labor Share and the Rise of Superstar Firms”, Quarterly Journal of Economics, 135, 645–709.

BARTOŠ, V., BAUER, M., CHYTILOVÁ, J., et al. (2016), “Attention Discrimination: Theory and Field Experiments with Monitoring Information Acquisition”, American Economic Review, 106, 1437–75.

BASU, S. and FERNALD, J. G. (1997), “Returns to Scale in us Production: Estimates and Implications”, Journal of Political Economy, 105, 249–283.

BLOOM, N., BOND, S. and VAN REENEN, J. (2007), “Uncertainty and Investment Dynamics”, Review of Economic Studies, 74, 391–415.

BLOOM, N. and VAN REENEN, J. (2010), “Why do Management Practices Differ across Firms and Countries?” Journal of Economic Perspectives, 24, 203–24.

BoardEX (2021), “BoardEx [dataset]” Wharton Research Data Services. wrds-www.wharton.upenn.edu (accessed 23 January 2021).

BOS (2022), "Business Outlook Survey [dataset]" Bank of Canada, (accessed 9 October 2022).

BUEHLMAIER, M. and WHITED, T. (2018), "Are Financial Constraints Priced? Evidence from Textual Analysis", Review of Financial Studies, 31, 2693–2728.

CANDIA, B., COIBION, O. and GORODNICHENKO, Y. (2024), “The Inflation Expectations of US Firms: Evidence from a New Survey”, Journal of Monetary Economics, 145, 103569.

CAO, S., JIANG, W. and YANG, B. (2023), “How to Talk When a Machine is Listening: Corporate Disclosure in the Age of AI”, The Review of Financial Studies, 36, 3603–3642.

CAPLIN, A., DEAN, M. and LEAHY, J. (2019), “Rational Inattention, Optimal Consideration Sets, and Stochastic Choice”, Review of Economic Studies, 86, 1061–1094.

CAPLIN, A. and SPULBER, D. (1987), "Menu Costs and the Neutrality of Money", Quarterly Journal of Economics, 102, 703–725.

CCM (2020), "CRSP/Compustat Merged Database [dataset]" Wharton Research Data Services.

wrds-www.wharton.upenn.edu (accessed 6 October 2020).

CHIANG, Y.-T. (2024), "Attention and a Paradox of Uncertainty" Manuscript.

CHRISTIANO, L., EICHENBAUM, M. and EVANS, C. (2005), “Nominal Rigidities and the Dynamic Effects of a Shock to Monetary Policy”, Journal of Political Economy, 113, 1–45.

CLOYNE, J., FERREIRA, C. and FROEMEL, M. (2023), "Monetary Policy, Corporate Finance, and Investment", Journal of the European Economic Association, 21, 2586–2634.

COIBION, O. and GORODNICHENKO, Y. (2015), “Information Rigidity and the Expectations Formation Process: A Simple Framework and new Facts”, American Economic Review, 105, 2644–78.

COIBION, O., GORODNICHENKO, Y. and KUMAR, S. (2018), "How do Firms Form Their Expectations? new Survey Evidence", American Economic Review, 108, 2671–2713.

COIBION, O., GORODNICHENKO, Y. and ROPELE, T. (2020), “Inflation Expectations and Firm Decisions: New Causal Evidence”, Quarterly Journal of Economics, 135, 165–219.

COOK, T. and HAHN, T. (1989), “The Effect of Changes in the Federal Funds Rate Target on Market Interest Rates in the 1970s”, Journal of Monetary Economics, 24, 331–351.

COVER, T. and THOMAS, J. (1991), Elements of Information Theory (The United States of America: John Wiley & Sons).

FLYNN, J. P. and SASTRY, K. (2024), "Attention Cycles" Manuscript.

FUSTER, A., PEREZ-TRUGLIA, R. and WIEDERHOLT, M. (2022), "Expectations with Endogenous Information Acquisition: An Experimental Investigation", Review of Economics and Statistics, 104, 1059–1078.

GABAIX, X. (2019), “Behavioral inattention”, in Handbook of Behavioral Economics: Applications and Foundations 1 (Vol. 2) (The Netherlands: Elsevier) 261–343.

GERTLER, M. and GILCHRIST, S. (1994), “Monetary Policy, Business Cycles, and the Behavior of Small Manufacturing Firms”, Quarterly Journal of Economics, 109, 309–340.

GERTLER, M. and LEAHY, J. (2008), “A Phillips Curve with an ss Foundation”, Journal of Political Economy, 116, 533–572.

GORODNICHENKO, Y. and WEBER, M. (2016), “Are Sticky Prices Costly? Evidence from the Stock Market”, American Economic Review, 106, 165–99.

GÜRKAYNAK, R. S., SACK, B. and SWANSON, E. T. (2005), "Do Actions Speak Louder Than Words? the Response of Asset Prices to Monetary Policy Actions and Statements", International Journal of Central Banking, 1.

HALDANE, A., MACAULAY, A. and MCMAHON, M. (2021), “The Three E’s of Central-Bank Communication with the Public”, in E. Pastén. and R. Reis (eds.) Independence, Credibility, and Communication of Central Banking (Chile: Central Bank of Chile).

HANDLEY, K. and LI, J. F. (2020), “Measuring the Effects of Firm Uncertainty on Economic Activity: New Evidence from One Million Documents” (Tech. Rep., National Bureau of Economic Research).

HANSEN, S., MCMAHON, M. and PRAT, A. (2018), “Transparency and Deliberation Within the FOMC: A Computational Linguistics Approach”, Quarterly Journal of Economics, 133, 801–870.

HASSAN, T. A., HOLLANDER, S., VAN LENT, L., et al. (2019), “Firm-level Political Risk: Measurement and Effects”, Quarterly Journal of Economics, 134, 2135–2202.

JORDÀ, Ó. (2005), “Estimation and Inference of Impulse Responses by Local Projections”, American Economic Review, 95, 161–182.

KONCHITCHKI, Y. and XIE, J. (2023), “Undisclosed Material Inflation Risk”, Journal of Monetary Economics, 140, S82–S100.

KWON, S. Y., MA, Y. and ZIMMERMANN, K. (2024), “100 Years of Rising Corporate Concentration”, American Economic Review, 114, 2111–2140.

LARSEN, V. H., THORSRUD, L. A. and ZHULANOVA, J. (2021), “News-driven Inflation Expectations and Information Rigidities”, Journal of Monetary Economics, 117, 507–520.

LEAHY, J. V. and WHITED, T. M. (1996), “The Effect of Uncertainty on Investment: Some Stylized Facts”, Journal of Money, Credit, and Banking, 28, 64–83.

LOUGHRAN, T. and MCDONALD, B. (2011), “When is a Liability not a Liability? Textual Analysis, Dictionaries, and 10-Ks”, Journal of Finance, 66, 35–65.

LUO, Y. (2008), “Consumption Dynamics under Information Processing Constraints”, Review of Economic Dynamics, 11, 366–385.

MACAULAY, A. (2020), "Cyclical Attention to Saving", in UniCredit Foundation Working Papers Series 140.

MACKOWIAK, B., MATEJKA, F. and WIEDERHOLT, M. (2023), “Rational Inattention: A Review”, Journal of Economic Literature, 61, 226–273.

MACKOWIAK, B., MOENCH, E. and WIEDERHOLT, M. (2009), “Sectoral Price Data and Models of Price Setting”, Journal of Monetary Economics, 56, S78–S99.

MACKOWIAK, B. and WIEDERHOLT, M. (2009), “Optimal Sticky Prices under Rational Inattention”, American Economic Review, 99, 769–803.

(2015), “Business Cycle Dynamics under Rational Inattention”, Review of Economic Studies, 82, 1502–1532.

(2023), “Rational Inattention and the Business Cycle Effects of Productivity and News Shocks”.

MALMENDIER, U. and NAGEL, S. (2016), “Learning from Inflation Experiences”, Quarterly Journal of Economics, 131, 53–87.

MANKIW, G. and REIS, R. (2002), “Sticky Information versus Sticky Prices: A Proposal to Replace the new Keynesian Phillips Curve”, Quarterly Journal of Economics, 117, 1295–1328.

MATEJKA, F. and MCKAY, A. (2015), “Rational Inattention to Discrete Choices: A new Foundation for the Multinomial Logit Model”, American Economic Review, 105, 272–98.

MCKAY, A. and WIELAND, J. F. (2021), "Lumpy Durable Consumption Demand and the Limited Ammunition of Monetary Policy", Econometrica: Journal of the Econometric Society, 89, 2717–2749.

MEHRA, R. and PRESCOTT, E. C. (1985), “The Equity Premium: A Puzzle”, Journal of Monetary Economics, 15, 145–161.

NAKAMURA, E. and STEINSSON, J. (2018), "High Frequency Identification of Monetary Non-Neutrality: The Information Effect", Quarterly Journal of Economics, 133, 1283–1330.

OLLEY, G. S. and PAKES, A. (1996), “The Dynamics of Productivity in the Telecommunications Equipment Industry”, Econometrica: Journal of the Econometric Society, 64, 1263–1297.

OTTONELLO, P. and WINBERRY, T. (2020), “Financial Heterogeneity and the Investment Channel of Monetary Policy”, Econometrica: Journal of the Econometric Society, 88, 2473–2502.

RAMEY, V. (2016), “Macroeconomic Shocks and Their Propagation”, in Handbook of Macroeconomics (Vol. 2) (The Netherlands: Elsevier) 71–162.

REIS, R. (2006), "Inattentive Producers", Review of Economic Studies, 73, 793–821.

REUTSKAJA, E., NAGEL, R., CAMERER, C., et al. (2011), "Search Dynamics in Consumer Choice under Time Pressure: An Eye-Tracking Study", American Economic Review, 101, 900–926.

SIMS, C. (2003), "Implications of Rational Inattention", Journal of Monetary Economics, 50, 665–690.

SPF (2023), “Survey of Professional Forecasters [dataset]” Federal Reserve Bank of Philadelphia. www.philadelphiafed.org, (accessed 5 November 2023).

TANAKA, M., BLOOM, N. and DAVID, J. (2020), “Firm Performance and Macro Forecast Accuracy”, Journal of Monetary Economics, 114, 26–41.

TENREYRO, S. and THWAITES, G. (2016), “Pushing on a String: Us Monetary Policy is Less Powerful in Recessions”, American Economic Journal: Macroeconomics, 8, 43–74.

VAN NIEUWERBURGH, S. and VELDKAMP, L. (2006), “Learning Asymmetries in Real Business Cycles”, Journal of Monetary Economics, 53, 753–772.

——(2009). "Information Immobility and the Home Bias Puzzle", Journal of Finance, 64, 1187–1215.

VAVRA, J. (2014), “Inflation Dynamics and Time-Varying Volatility: New Evidence and an Ss Interpretation”, Quarterly Journal of Economics, 129, 215–258.

WEITZNER, G. and HOWES, C. (2023), "Bank Information Production Over the Business Cycle" Manuscript.

WOODFORD, M. (2009), “Information-constrained State-Dependent Pricing”, Journal of Monetary Economics, 56, S100–S124.

WOOLDRIDGE, J. M. (2009), “On Estimating Firm-Level Production Functions Using Proxy Variables to Control for Unobservables”, Economics Letters, 104, 112–114.

YANG, C. (2022), “Rational Inattention, Menu Costs, and Multi-Product Firms: Micro Evidence and Aggregate Implications”, Journal of Monetary Economics, 128, 105–123.

ZBARACKI, M., RITSON, M., LEVY, D., et al. (2004), “Managerial and Customer Costs of Price Adjustment: Direct Evidence from Industrial Markets”, Review of Economics and Statistics, 86, 514–533.

