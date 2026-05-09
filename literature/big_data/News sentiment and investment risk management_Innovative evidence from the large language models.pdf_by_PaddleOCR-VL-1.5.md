# News sentiment and investment risk management: Innovative evidence from the large language models

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//d597bd66-95bf-471d-ab0d-ed47f2602549/markdown_0/imgs/img_in_image_box_1001_297_1058_353.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-31T08%3A09%3A02Z%2F-1%2F%2F5e5089c747b3fe777f637f3077e926b2f669d264d0b5934acdadf862b6653535" alt="Image" width="4%" /></div>


Tong Liu $ ^{a} $, Yanlin Shi $ ^{b,*} $

 $ ^{a} $ Guizhou University of Commerce, Guiyang, Guizhou 550014, China

 $ ^{b} $ Department of Actuarial Studies and Business Analytics, Macquarie University, Sydney, NSW 2000, Australia

#### ARTICLE INFO

Keywords:

Asset volatility

News sentiment

Markov regime-switching

Discrete choice model

## ABSTRACT

This paper reexamines the significance of news sentiment in explaining stock return volatility persistence and its role in driving underlying volatility states. Our simulation study demonstrates that more accurately measured news sentiment has a greater impact on volatility dynamics. Using data from firms in the Dow Jones Composite Average index spanning 2019–2023, we compare news sentiment classified by GPT-4 with that classified by RavenPack. Our findings show that both negative and positive firm-specific and macroeconomic news significantly affect intraday stock return volatility. The classification accuracy achieved by employing GPT-4 potentially surpasses that of using RavenPack.

## 1. Introduction

Effective financial decision-making critically hinges on investment risk management, which directly impacts the stability and profitability of investment portfolios in today's increasingly volatile and complex market environment. Robust risk management strategies are vital for mitigating potential losses, particularly during periods of heightened market turbulence (Shi and Ho, 2021). Volatility is central to investment risk management, functioning as a primary indicator of market uncertainty and risk. It influences asset pricing, portfolio allocation, and the overall risk profile of investments. Consequently, a deep understanding of volatility dynamics is the foundational step toward successful investment risk management.

Among existing finance theories, the Mixture of Distributions Hypothesis (MDH) proposed by Clark (1973) provides an explanation for the mechanism underlying volatility. In essence, MDH posits that asset volatility is proportional to the rate of news arrival. Subsequent research has further contended that news sentiment plays a critical role in MDH (Ho et al., 2013), with its effects on volatility differing between low- and high-volatility states. Regarding the drivers of these volatility states, Shi and Ho (2021) demonstrated that both the volume and sentiment of news stories exert significant influence.

This paper revisits the influence of news sentiment on stock return volatility by leveraging modern large language models (LLMs), with a particular focus on the effectiveness of LLMs in measuring news sentiment. In the existing literature, sentiment is typically assessed using textual analysis tools that rely on pre-defined dictionaries. For example, the seminal work by Huang et al. (2014) employed the Linguistic Inquiry and Word Count (LIWC) tool to analyze the tone of earnings announcements and its impact on market reactions. LIWC categorizes words into various psychological and sentiment categories, with sentiment scores determined by the frequencies of relevant words. Similar techniques have been employed or discussed in seminal works of Buehlmaier and Whited (2018), Gentzkow et al. (2019), and Jeon et al. (2022), among others.

However, dictionary-based approaches often struggle with contextual understanding, irony, sarcasm, and nuanced language. For example, double negatives or negations can confuse these algorithms, leading to incorrect sentiment classification (e.g., “not unhappy” being misclassified as negative). To address these limitations, various advanced natural language processing (NLP) techniques have been developed. For instance, Google Cloud Natural Language and Stanford CoreNLP employ deep learning models for sentiment analysis. Despite these advancements, Verma et al. (2018) noted that these algorithms still exhibit weak performance in capturing negative polarity items within sentences. Consequently, there remains a significant demand for improved sentiment analysis tools.

With the advent of ChatGPT, modern LLMs, such as GPT-4, present significant advantages over traditional textual analysis tools. These models can accurately interpret phrases, idiomatic expressions, and subtle emotional tones that older tools often overlook. This capability makes LLMs particularly effective for analyzing complex and evolving texts, such as financial news stories. The effectiveness of LLMs has been explored in recent studies. For example, Schuettler et al. (2024)

compared the performance of LLMs with traditional human-annotated labeling methods in sentiment analysis for asset pricing. Their findings supported the superiority of LLMs in this context.

In this paper, we reexamine the research questions posed in the influential study by Shi and Ho (2021), with a particular emphasis on the potential improvements that LLMs offer in measuring news sentiment. Consistent with their approach, we utilize the Markov Regime-Switching Fractionally Integrated Exponential GARCH (MRS-FIEGARCH) model. This model effectively controls for the spurious long memory associated with structural changes, as highlighted by Diebold and Inoue (2001). Compared to standard FIGARCH models, the FIE-GARCH specification is better suited to capture the genuine long-memory persistence in the conditional volatility of stock returns (Davidson 2004), a phenomenon commonly observed in finance research (see, for example, Ho et al., 2013, among others). Moreover, the smoothed probabilities generated by the MRS-FIEGARCH model facilitate the identification of latent volatility states (i.e., low and high volatility states). We then employ discrete choice models to assess the influence of news sentiment on these volatility states.

To support our empirical findings, we first provide simulation illustrations. These simulations demonstrate that more accurate measurement of sentiment allows the news variable to better explain the persistence of volatility in financial returns, with a greater marginal influence on the likelihood of entering a high-volatility state. Next, we extend the work of Shi and Ho (2021) by analyzing the influence of news on stocks traded on the Dow Jones Composite Average index (DJN65) over the period 2019–2023. As in Shi and Ho (2021), we collect relevant news stories from the RavenPack News Analytics - Dow Jones Edition. However, unlike their approach, which calculates sentiment using RavenPack's inherent scores, we employ GPT-4 to classify both firm-specific and macroeconomic news articles as negative vs. positive. Our results indicate that incorporating GPT-4 classified news variables leads to a more substantial reduction in volatility persistence compared to RavenPack variables. Additionally, both RavenPack and GPT-4 consistently show that all news variables exert significant marginal impacts on the volatility states. Specifically, macroeconomic news exerts a stronger influence than firm-specific news. Negative news increases the likelihood of higher volatility states, while positive news decreases it to a greater extent. More importantly, we find that the marginal impacts of GPT-4 classified news variables are uniformly larger than those of the RavenPack counterparts. Consistent with our simulation results, this suggests that GPT-4 is potentially more accurate in classifying negative and positive news articles than RavenPack scores.

To the best of our knowledge, this paper is the first to compare the effectiveness of LLMs with existing textual analyzer in studying the role of news sentiment in MDH and volatility states of stock returns. The observed asymmetric impacts of negative and positive news underscore the critical importance of accurately classifying news sentiment to understand volatility dynamics. The demonstrated effectiveness and superiority of LLMs, such as GPT-4, offer valuable insights into their potential applications in risk management practices and suggest promising directions for future research.

The remainder of the paper is organized as follows. Section 2 explains the models used in this study. Section 3 describes our stock and news data. Simulation results are presented in Section 4. Section 5 discusses the empirical findings. Finally, Section 6 concludes the paper.

## 2. Methodology

### 2.1. MRS-FIEGARCH model

Markov regime-switching (MRS) approaches, first proposed by Hamilton (1989), represent a significant advancement in the study of structural changes. Among the various extensions to GARCH-type models, the MRS-GARCH model developed by Haas et al. (2004) is widely recognized for its ability to address the path-dependence issue effectively.

To accurately measure the long-memory persistence, we employ the MRS-FIEGARCH model investigated in Shi and Ho (2021) as follows.

 $$ \begin{aligned}&r_{t}=\mu+\varepsilon_{t}\\&\varepsilon_{t}=\eta_{t}\sqrt{h_{s_{t},t}}\mathrm{w h e r e}\eta_{t}\stackrel{i i d}{\sim}t(0,1,v)\\ \end{aligned} $$ 

 $$ (1-\phi L)(1-L)^{d}\log h_{t}=\begin{cases}\omega_{1}+\beta|\eta_{t-1}|+\gamma\eta_{t-1}\text{when}s_{t}=1\\\omega_{2}+\beta|\eta_{t-1}|+\gamma\eta_{t-1}\text{when}s_{t}=2\end{cases} $$ 

where  $ r_t $ is the return at time  $ t $.  $ s_t $ is its latent state.  $ h_{s_t,t} $ is the conditional volatility in state  $ s_t $.  $ d \in (-0.5, 0.5) $ measures the long-memory persistence of  $ h_t $.  $ v $ is the degree of freedom of the Student-t distribution. $ ^1 $ The sequence  $ \{s_t\} $ is assumed to be a stationary, irreducible Markov process with a discrete state space  $ \{1, 2\} $ and transition matrix  $ P = [p_{jk}] $ where  $ p_{jk} = \mathrm{P}(s_{t+1} = k|s_t = j) $ is the transition probability of moving from state  $ j $ to state  $ k $ ( $ j, k \in \{1, 2\} $). We define states 1 and 2 as the low-volatility (calm) and high-volatility (turbulent) states, respectively. The parameters of the MRS-FIEGARCH model are estimated using the maximum likelihood estimation described in Haas et al. (2004).

To identify the state in which the stock return lies at time t, we extract the smoothed probability of the turbulent state, denoted as  $ P(s_t = 2|\theta, \Omega_T) $. Here,  $ \theta $ represents the parameter vector, and  $ \Omega_T $ is the information set available up to time T. For details on the calculation of these probabilities, see Shi and Ho (2021).

### 2.2. Discrete choice models

To study the news influence on the states of stock return volatility, we follow Shi and Ho (2021) and employ the following logit models.

Null model:  $ U_t = \lambda_0 + \varepsilon_t $

Full model:  $ U_t = \lambda_0 + \lambda N e w s_t + \varepsilon_t $

where  $ U_t $ is the latent utility of  $ s_t $, the form of which will be determined by the logit models.  $ s_t $ is determined by the fitted probability  $ P(s_t = 2|\theta, \Omega_T) $. In a two-state scenario,  $ s_t = 2 $ if  $ P(s_t = 2|\theta, \Omega_T) > 0.5 $ and  $ s_t = 1 $ otherwise.  $ News_t $ is the corresponding news variable vector.  $ \lambda $ is the vector of associated slopes, which measures the marginal influence of news. In addition to the logit models, we employ the probit models to check the robustness.

## 3. Data and sample

Our stock price series consist of hourly data for all firms listed in the Dow Jones Composite Average index (DJN 65) from March 2019 to December 2023. We chose an hourly frequency to ensure a sufficient number of news events are captured during each interval. The data are sourced from the Thomson Reuters Tick History database. Hourly returns, expressed in percentages, are defined as  $ r_t = 100 \times \log(S_t / S_{t-1}) $, where  $ S_t $ is the hourly close price.

The RavenPack News Analytics database is used to proxy the news counts, capturing more than 1200 types of intraday news events starting from January 2000. Following Shi and Ho (2021), we utilize the composite sentiment score (CSS) and event sentiment score (ESS) $ ^{2} $ to derive the firm-specific and macroeconomic news variables, respectively. Specifically, at time t, the numbers of negative and positive

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//d597bd66-95bf-471d-ab0d-ed47f2602549/markdown_2/imgs/img_in_chart_box_191_107_584_296.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-31T08%3A09%3A04Z%2F-1%2F%2F1a81b6a2ef4f19068e6f92375874270996cd460ae0fa256693fe019cb215a5a2" alt="Image" width="32%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//d597bd66-95bf-471d-ab0d-ed47f2602549/markdown_2/imgs/img_in_chart_box_608_109_999_296.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-31T08%3A09%3A04Z%2F-1%2F%2F208b1c363604dc66abbbde30ddc6a7722e116efadc3ad8591989c378e033a43b" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(a) News counts</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//d597bd66-95bf-471d-ab0d-ed47f2602549/markdown_2/imgs/img_in_chart_box_400_415_790_604.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-31T08%3A09%3A05Z%2F-1%2F%2Ffed69928bd527514381d612a90e9f4890c3e7d5e1c96898e4923987e35201fae" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(b) Returns</div> </div>


<div style="text-align: center;"><div style="text-align: center;">(c) Smoothed probabilities</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 1. Simulated news counts, returns and smoothed probabilities of the turbulent state.</div> </div>


firm-specific, as well as negative and positive macroeconomic news stories, are:

 $$ NN_{f,t}=\sum_{all\tau}I(CSS_{f,\tau}<50) $$ 

 $$ NN_{m,t}=\sum_{all\tau}I(ESS_{m,\tau}<50) $$ 

 $$ NP_{f,t}=\sum_{all\tau}I(CSS_{f,\tau}>50) $$ 

 $$ NP_{m,t}=\sum_{all\tau}I(ESS_{m,\tau}>50) $$ 

where the subscripts  $ f $ and  $ m $ indicate that the corresponding variables refer to firm-specific and macroeconomic news, respectively.  $ NN $ represents negative news, and  $ NP $ represents positive news. The indicator function  $ I(\cdot) $ returns 1 when the condition inside the brackets is true and 0 otherwise.  $ \tau $ denotes the time at which the news story is received, with  $ \tau \in [t-1, t] $.

In addition to the RavenPack algorithm, we utilize GPT-4 to measure the textual sentiment of each news story. Specifically, we replace  $ I(CSS_{f,\tau}) $ and  $ I(ESS_{m,\tau}) $ in (3) with 0 or 1 according to the GPT-4 output. In this context, NN and NP represent negative and positive news, respectively, as classified by GPT-4. More detailed explanations of the RavenPack and GPT-4 algorithms can be found in online supplementary materials.

## 4. Simulation results

We demonstrate the impact of accuracy in news sentiment measurement through simulations. To simplify the illustration, we consider only one type of non-neutral news and define the latent flow as  $ n_t $ with a sample size of  $ T $. We simulate  $ log(n_t) $ with a known long-memory persistence parameter  $ d_n $. To depict structural changes, we set the unconditional mean of  $ log(n_t) $ to 0.1 for  $ t < T/2 $ and to 0.5 for  $ t \geq T/2 $. The series  $ n_t $ is then obtained by exponentiating the simulated values. The return series is simulated as  $ r_t = \sqrt{n_t} \eta_t $, where  $ \eta_t $ is an independent standard normal sequence. Finally, we fit the MRS-FIEGARCH model.

<div style="text-align: center;"><div style="text-align: center;">Table 1</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Simulation results: reduction in long-memory persistence and news influence.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2">$ d_{n} $</td><td colspan="4">Reduced persistence in percentage</td><td colspan="4">News influence</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Mean $ _{H} $</td><td style='text-align: center; word-wrap: break-word;'>Std $ _{H} $</td><td style='text-align: center; word-wrap: break-word;'>Mean $ _{L} $</td><td style='text-align: center; word-wrap: break-word;'>Std $ _{L} $</td><td style='text-align: center; word-wrap: break-word;'>Mean $ _{H} $</td><td style='text-align: center; word-wrap: break-word;'>Std $ _{H} $</td><td style='text-align: center; word-wrap: break-word;'>Mean $ _{L} $</td><td style='text-align: center; word-wrap: break-word;'>Std $ _{L} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0.25</td><td style='text-align: center; word-wrap: break-word;'>75%</td><td style='text-align: center; word-wrap: break-word;'>13%</td><td style='text-align: center; word-wrap: break-word;'>26%</td><td style='text-align: center; word-wrap: break-word;'>7%</td><td style='text-align: center; word-wrap: break-word;'>0.2352</td><td style='text-align: center; word-wrap: break-word;'>0.0145</td><td style='text-align: center; word-wrap: break-word;'>0.1401</td><td style='text-align: center; word-wrap: break-word;'>0.0181</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0.35</td><td style='text-align: center; word-wrap: break-word;'>72%</td><td style='text-align: center; word-wrap: break-word;'>13%</td><td style='text-align: center; word-wrap: break-word;'>24%</td><td style='text-align: center; word-wrap: break-word;'>6%</td><td style='text-align: center; word-wrap: break-word;'>0.2243</td><td style='text-align: center; word-wrap: break-word;'>0.0131</td><td style='text-align: center; word-wrap: break-word;'>0.1460</td><td style='text-align: center; word-wrap: break-word;'>0.0184</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0.45</td><td style='text-align: center; word-wrap: break-word;'>76%</td><td style='text-align: center; word-wrap: break-word;'>10%</td><td style='text-align: center; word-wrap: break-word;'>24%</td><td style='text-align: center; word-wrap: break-word;'>5%</td><td style='text-align: center; word-wrap: break-word;'>0.2217</td><td style='text-align: center; word-wrap: break-word;'>0.0139</td><td style='text-align: center; word-wrap: break-word;'>0.1409</td><td style='text-align: center; word-wrap: break-word;'>0.0200</td></tr></table>

Note:  $ Mean_{H} $ and  $ Std_{H} $ ( $ Mean_{L} $ and  $ Std_{L} $) are mean and standard deviation of the news variables with higher (lower) accuracy, respectively.

to  $ r_t $ and estimate the smoothed probability  $ P(s_t = 2|\theta, \Omega_T) $. Setting  $ T = 1000 $ and  $ d_n = 0.25 $, we plot one simulated instance in Fig. 1. It is evident that  $ n_t $ serves as the underlying driver of the conditional volatility of  $ r_t $, and the MRS-FIEGARCH model effectively captures the latent volatility states.

According to the MDH, the conditional volatility of  $ r_t $ and its persistence are driven by  $ n_t $. Therefore, if  $ n_t $ could be measured accurately, the estimated  $ d $ in (1) would be significantly reduced after incorporating news influence into the conditional variance equation. To illustrate the impact of accuracy on news sentiment measurement, we define two proxy news counts:  $ n_t^H $ (higher accuracy) and  $ n_t^L $ (lower accuracy). Specifically, at each time  $ t $, we set  $ n_t^H = n_t $ with a probability between 0.9 and 1, and  $ n_t^L = n_t $ with a probability between 0.7 and 0.8. In other words, there is over a 90% chance that  $ n_t^H $ accurately captures the true non-neutral news flow, while the probability for  $ n_t^L $ is between 70% and 80%. We first incorporate  $ n_t^H $ and  $ n_t^L $ individually into the conditional variance equation of the MRS-FIEGARCH model. According to the MDH, the reduction in  $ d $ caused by  $ n_t^H $ should be more substantial than that caused by  $ n_t^L $, compared to the original  $ d $ estimated without news influence. To further investigate the impact of news on the volatility states of  $ r_t $, we fit two-state logit models as described in (2), replacing  $ News_t $ with either  $ n_t^H $ or  $ n_t^L $.

The simulation results are summarized in Table 1. We examine three different levels of long-memory persistence, simulating 1000 replicates

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//d597bd66-95bf-471d-ab0d-ed47f2602549/markdown_3/imgs/img_in_chart_box_231_109_586_282.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-31T08%3A09%3A06Z%2F-1%2F%2F30308a2fa85100592dd9225449c6f58100a82353517b4c95cc84e67848539968" alt="Image" width="29%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//d597bd66-95bf-471d-ab0d-ed47f2602549/markdown_3/imgs/img_in_chart_box_606_111_960_281.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-31T08%3A09%3A06Z%2F-1%2F%2F261ddeff65be218469d7fdcd6c5b8995074ae3d13169f27d7a7d34cfcd33dc44" alt="Image" width="29%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(a) MSFT returns</div> </div>


<div style="text-align: center;"><div style="text-align: center;">(b) MSFT smoothed probabilities</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//d597bd66-95bf-471d-ab0d-ed47f2602549/markdown_3/imgs/img_in_chart_box_232_390_586_561.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-31T08%3A09%3A06Z%2F-1%2F%2F48a0d4c8e00e98fa1a021715516381344b1ebf359ed574e794dc53b912c17959" alt="Image" width="29%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(c) JPM returns</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//d597bd66-95bf-471d-ab0d-ed47f2602549/markdown_3/imgs/img_in_chart_box_606_389_959_562.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-31T08%3A09%3A07Z%2F-1%2F%2F4a150e933e00764b4449f99000fcfe48642756bc0421e1a8f35fa7ac2aef9a39" alt="Image" width="29%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(d) JPM smoothed probabilities</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//d597bd66-95bf-471d-ab0d-ed47f2602549/markdown_3/imgs/img_in_chart_box_232_670_586_839.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-31T08%3A09%3A07Z%2F-1%2F%2F360d7f062b45aa8e546cb3a6665ded084b7a9e3a8ee2a0025921afc924320a44" alt="Image" width="29%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(e) KO returns</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//d597bd66-95bf-471d-ab0d-ed47f2602549/markdown_3/imgs/img_in_chart_box_607_669_959_838.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-31T08%3A09%3A07Z%2F-1%2F%2Fd46726af4f7925f9bf7704c6611e0ac29273bd60fbd702c305f6e189b9fda89b" alt="Image" width="29%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(f) KO smoothed probabilities</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Fig. 2. Returns and smoothed probabilities of the turbulent state for MSFT, JPM and KO over 2019–2023.</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Table 2</div> </div>


<div style="text-align: center;"><div style="text-align: center;">News influence on long-memory persistence.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Scenario</td><td style='text-align: center; word-wrap: break-word;'>Mean</td><td style='text-align: center; word-wrap: break-word;'>Reduction (%)</td><td style='text-align: center; word-wrap: break-word;'>Std</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>No news</td><td style='text-align: center; word-wrap: break-word;'>0.4069</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>0.1496</td></tr><tr><td colspan="4">Panel A: RavenPack</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Firm-specific</td><td style='text-align: center; word-wrap: break-word;'>0.1574</td><td style='text-align: center; word-wrap: break-word;'>61%</td><td style='text-align: center; word-wrap: break-word;'>0.0781</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Macroeconomic</td><td style='text-align: center; word-wrap: break-word;'>0.1981</td><td style='text-align: center; word-wrap: break-word;'>51%</td><td style='text-align: center; word-wrap: break-word;'>0.0871</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Both</td><td style='text-align: center; word-wrap: break-word;'>0.1391</td><td style='text-align: center; word-wrap: break-word;'>66%</td><td style='text-align: center; word-wrap: break-word;'>0.0686</td></tr><tr><td colspan="4">Panel B: GPT-4</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Firm-specific</td><td style='text-align: center; word-wrap: break-word;'>0.0968</td><td style='text-align: center; word-wrap: break-word;'>76%</td><td style='text-align: center; word-wrap: break-word;'>0.0852</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Macroeconomic</td><td style='text-align: center; word-wrap: break-word;'>0.1105</td><td style='text-align: center; word-wrap: break-word;'>73%</td><td style='text-align: center; word-wrap: break-word;'>0.0933</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Both</td><td style='text-align: center; word-wrap: break-word;'>0.0832</td><td style='text-align: center; word-wrap: break-word;'>80%</td><td style='text-align: center; word-wrap: break-word;'>0.0841</td></tr></table>

Note: Mean is the average of estimated d across all DJN65 firms. Std is the standard deviation. Reduction (%) is the long-memory persistence reduced in percentage after accounting for the corresponding news variable(s).

for each scenario. As expected,  $ n_t^H $ proves to be more effective in reducing persistence, achieving an average reduction of over 70%, compared to around 25% for  $ n_t^L $. Similarly, the influence of  $ n_t^H $ on the smoothed probability is approximately 0.22 on average, which is more than 50% greater than the 0.14 observed for  $ n_t^L $. These results are consistent across all three scenarios. Additionally, the standard deviations indicate that the uncertainty associated with  $ n_t^H $ is consistently lower than that of  $ n_t^L $. Consequently, our simulation results suggest that more accurate measurement of news sentiment may enhance the effectiveness of news influence while reducing estimation uncertainty.

## 5. Empirical findings

Consistent with Shi and Ho (2021), we use Microsoft (MSFT), JP Morgan (JPM), and Coca-Cola (KO) to illustrate our empirical dataset. The returns and fitted smoothed probabilities from the MRS-FIEGARCH model, without incorporating news, are plotted in Fig. 2. It is evident that all firms experienced significantly heightened turbulence in early 2020. The smoothed probabilities, despite variations in persistence, reflect this dynamic, confirming that the MRS-FIEGARCH model effectively identifies the underlying volatility states. These states align with the well-documented early impact of the COVID-19 pandemic.

We follow Ho et al. (2013) by considering three sets of news variables in the conditional variance equation of the MRS-FIEGARCH model: firm-specific news ( $ NN_{f,t} $ and  $ NP_{f,t} $), macroeconomic news ( $ NN_{m,t} $ and  $ NP_{m,t} $), or a combination of both. We then compare the performance of news sentiment classified using the original RavenPack scores against that classified by GPT-4. The results are summarized in Table 2. Overall, firm-specific news proves more effective than macroeconomic news in reducing long-memory persistence, with the most significant reduction observed when both types of news are incorporated. These findings are consistent with Ho et al. (2013). More

<div style="text-align: center;"><div style="text-align: center;">Table 3</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Nonparametric tests of RavenPack news variables in logit and probit models.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2"></td><td colspan="3">Logit</td><td colspan="3">Probit</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Mean</td><td style='text-align: center; word-wrap: break-word;'>Std</td><td style='text-align: center; word-wrap: break-word;'>Boot. CI</td><td style='text-align: center; word-wrap: break-word;'>Mean</td><td style='text-align: center; word-wrap: break-word;'>Std</td><td style='text-align: center; word-wrap: break-word;'>Boot. CI</td></tr><tr><td colspan="7">Panel A: two-state results</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>N Nf</td><td style='text-align: center; word-wrap: break-word;'>0.0205 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0570</td><td style='text-align: center; word-wrap: break-word;'>[0.0151, 0.0355] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0173 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0449</td><td style='text-align: center; word-wrap: break-word;'>[0.0133, 0.0294] $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>NPf</td><td style='text-align: center; word-wrap: break-word;'>$ -0.1407 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0640</td><td style='text-align: center; word-wrap: break-word;'>[-0.1471,  $ -0.1232 $] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.1273 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0572</td><td style='text-align: center; word-wrap: break-word;'>[-0.1324,  $ -0.1124 $] $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>NNm</td><td style='text-align: center; word-wrap: break-word;'>0.0414 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0464</td><td style='text-align: center; word-wrap: break-word;'>[0.0371, 0.0536] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0390 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0367</td><td style='text-align: center; word-wrap: break-word;'>[0.0352, 0.0488] $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>NPm</td><td style='text-align: center; word-wrap: break-word;'>$ -0.1558 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0607</td><td style='text-align: center; word-wrap: break-word;'>[-0.1616,  $ -0.1392 $] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.1378 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0541</td><td style='text-align: center; word-wrap: break-word;'>[-0.1428,  $ -0.1229 $] $ ^{*} $</td></tr><tr><td colspan="7">Panel B: three-state results</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>NNf</td><td style='text-align: center; word-wrap: break-word;'>0.0114 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0300</td><td style='text-align: center; word-wrap: break-word;'>[0.0084, 0.0196] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0103 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0259</td><td style='text-align: center; word-wrap: break-word;'>[0.0078, 0.0170] $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>NPf</td><td style='text-align: center; word-wrap: break-word;'>$ -0.0748 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0499</td><td style='text-align: center; word-wrap: break-word;'>[-0.0776,  $ -0.0663 $] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.0711 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0487</td><td style='text-align: center; word-wrap: break-word;'>[-0.0736,  $ -0.0631 $] $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>NNm</td><td style='text-align: center; word-wrap: break-word;'>0.0228 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0248</td><td style='text-align: center; word-wrap: break-word;'>[0.0207, 0.0298] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0225 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0211</td><td style='text-align: center; word-wrap: break-word;'>[0.0206, 0.0281] $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>NPm</td><td style='text-align: center; word-wrap: break-word;'>$ -0.0814 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0372</td><td style='text-align: center; word-wrap: break-word;'>[-0.0838,  $ -0.0739 $] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.0765 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0456</td><td style='text-align: center; word-wrap: break-word;'>[-0.0790,  $ -0.0695 $] $ ^{*} $</td></tr></table>

Note: Mean is the average of estimated coefficient of news variable across all DJN65 firms. Std is the Std is standard deviation. Boot. CI is 95% bootstrap interval.

 $ ^{*} $ Means the null hypothesis of a zero influence of the news variable is rejected at the 5% level.

<div style="text-align: center;"><div style="text-align: center;">Table 4</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Nonparametric tests of GPT-4 news variables in logit and probit models.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2"></td><td colspan="3">Logit</td><td colspan="3">Probit</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Mean</td><td style='text-align: center; word-wrap: break-word;'>Std</td><td style='text-align: center; word-wrap: break-word;'>Boot. CI</td><td style='text-align: center; word-wrap: break-word;'>Mean</td><td style='text-align: center; word-wrap: break-word;'>Std</td><td style='text-align: center; word-wrap: break-word;'>Boot. CI</td></tr><tr><td colspan="7">Panel A: two-state results</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ N_{F} $</td><td style='text-align: center; word-wrap: break-word;'>0.0278 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0427</td><td style='text-align: center; word-wrap: break-word;'>[0.0210, 0.0346] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0251 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0319</td><td style='text-align: center; word-wrap: break-word;'>[0.0198, 0.0305] $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ N_{Pf} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.2094 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0440</td><td style='text-align: center; word-wrap: break-word;'>[0.2180,  $ -0.2009 $] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.1891 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0419</td><td style='text-align: center; word-wrap: break-word;'>[ $ -0.1962 $,  $ -0.1820 $] $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ N_{Nm} $</td><td style='text-align: center; word-wrap: break-word;'>0.0583 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0355</td><td style='text-align: center; word-wrap: break-word;'>[0.0522, 0.0644] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0571 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0275</td><td style='text-align: center; word-wrap: break-word;'>[0.0520, 0.0621] $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ N_{Pm} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.2250 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0421</td><td style='text-align: center; word-wrap: break-word;'>[ $ -0.2336 $,  $ -0.2164 $] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.1820 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0386</td><td style='text-align: center; word-wrap: break-word;'>[ $ -0.1896 $,  $ -0.1744 $] $ ^{*} $</td></tr><tr><td colspan="7">Panel B: three-state results</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ N_{F} $</td><td style='text-align: center; word-wrap: break-word;'>0.0158 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0220</td><td style='text-align: center; word-wrap: break-word;'>[0.0121, 0.0196] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0149 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0190</td><td style='text-align: center; word-wrap: break-word;'>[0.0118, 0.0180] $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ N_{Pf} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.1109 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0356</td><td style='text-align: center; word-wrap: break-word;'>[ $ -0.1149 $,  $ -0.1069 $] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.0999 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0353</td><td style='text-align: center; word-wrap: break-word;'>[ $ -0.1037 $,  $ -0.0961 $] $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ N_{Nm} $</td><td style='text-align: center; word-wrap: break-word;'>0.0305 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0179</td><td style='text-align: center; word-wrap: break-word;'>[0.0272, 0.0338] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0334 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0153</td><td style='text-align: center; word-wrap: break-word;'>[0.0306, 0.0362] $ ^{*} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ N_{Pm} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.1078 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0261</td><td style='text-align: center; word-wrap: break-word;'>[ $ -0.1116 $,  $ -0.1040 $] $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.1123 $ $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>0.0316</td><td style='text-align: center; word-wrap: break-word;'>[ $ -0.1159 $,  $ -0.1086 $] $ ^{*} $</td></tr></table>

Note: Mean is the average of estimated coefficient of news variable across all DJN65 firms. Std is standard deviation. Boot. CI is 95% bootstrap interval.

 $ ^{*} $ Means the null hypothesis of a zero influence of the news variable is rejected at the 5% level.

notably, we find that the reductions achieved using GPT-4 classified news variables are more substantial than those obtained using RavenPack scores. For example, when both firm-specific and macroeconomic news stories are included, GPT-4 variables reduce d from 0.41 to 0.08, representing an approximately 80% reduction, compared to a 66% reduction (from 0.41 to 0.14) using RavenPack scores. Consistent with our simulation results, this suggests that GPT-4 is more accurate than RavenPack scores in measuring news sentiment.

We now examine the impact of news on the volatility states of DJN65 firms. Consistent with Shi and Ho (2021), we utilize two-state and three-state logit and probit models to assess robustness. For the three-state case,  $ s_t $ is set to 1 when  $ \mathrm{P}(s_t = 2|\theta, \Omega_T) \leq 0.2 $, to 3 when  $ \mathrm{P}(s_t = 2|\theta, \Omega_T) \geq 0.8 $, and to 2 otherwise. We analyze the influence of news by applying the model in (3), where  $ \mathrm{News}_t $ is replaced by  $ \mathrm{NN}_{f,t} $,  $ \mathrm{NP}_{f,t} $,  $ \mathrm{NN}_{m,t} $, and  $ \mathrm{NP}_{m,t} $. To test the statistical significance of the results, we employ the Wilcoxon signed rank test and the 95% Bootstrap percentile confidence interval (Boot. CI). The results for the RavenPack and GPT-4 variables are presented in Tables 3 and 4, respectively.

In general, most of our findings align with those of Shi and Ho (2021). Specifically, we find that both negative and positive news significantly affect the likelihood of volatility states in DJN65 returns, with negative news increasing and positive news reducing this likelihood. The impact of macroeconomic news is found to be greater than that of firm-specific news. For example, in the two-state logit model using RavenPack variables, the average coefficient for  $ NN_f $ is 0.02, approximately 50% smaller than the 0.04 coefficient for  $ NN_m $. Similarly, for positive news, the average coefficient for  $ NP_f $ is -0.14, slightly weaker than the -0.16 coefficient for  $ NP_m $. These results are consistent across probit models and in the three-state cases, indicating robustness.

More importantly, when comparing Tables 3 and 4, we observe that GPT-4 variables are consistently more influential than their RavenPack counterparts on average. For instance, in the baseline results of the two-state logit model, the mean coefficients for  $ NN_{f} $,  $ NN_{m} $,  $ NP_{f} $, and  $ NP_{m} $ classified by GPT-4 are 0.03, 0.06, -0.21, and -0.23, respectively. These values are approximately 40%–50% stronger than those for the RavenPack variables. Additionally, as indicated by the standard deviations and the width of the Bootstrap CIs, GPT-4 results in lower estimation uncertainty compared to RavenPack scores. Consistent with our simulation findings, these results suggest that GPT-4 provides a more accurate measurement of news sentiment than RavenPack scores.

To further check the robustness of our findings, we consider two alternative models to MRS-FIEGARCH: the Markov regime-switching long memory stochastic volatility (MRS-LMSV) model from Shi (2023) and the MRS autoregressive fractionally integrated moving average (MRS-ARFIMA) model from Shi and Ho (2015). Note that the MRS-ARFIMA model is a first-moment approach and requires pre-estimated volatility. For this, we use the Yang and Zhang (2000)'s method, which utilizes the open, high, low and close prices and allows for opening gaps. We reproduce Tables 2–4 with each model, yielding largely consistent estimates and confirming robustness across specifications. Full results are available in the supplementary materials.

## 6. Conclusions and implications

Using the modern LLMs, this paper reinvestigates the role of news sentiment in the MDH and the potential drivers of volatility states in stock returns. Through simulation illustrations, we first demonstrate that more accurate measurement of news sentiment can lead to a more substantial reduction in the persistence of stock return volatility. This also results in a larger marginal impact of news on the likelihood of entering a high-volatility state. Analyzing stocks from the Dow Jones Composite Average index over the period 2019–2023, we compare the influence of negative and positive news counts as classified by

RavenPack scores and the GPT-4 model. Our findings indicate that GPT-4 outperforms RavenPack algorithms in accurately measuring news sentiments.

Our findings offer valuable insights for professional traders in managing their investment risks. Specifically, the non-parametric tests reveal significant asymmetric impacts of negative and positive news flows on the likelihood of entering higher volatility states. This underscores the importance of accurately classifying the sentiment of real-time news stories for effective investment risk mitigation strategies. By utilizing modern LLMs such as GPT-4, our results suggest that traders can gain greater confidence in the correct classification of news sentiment. This enhanced accuracy enables traders to better anticipate the potential effects on asset volatility when new stories are released. By accurately incorporating the asymmetric effects of negative and positive news, traders can improve their dynamic hedging strategies, thereby mitigating the uncertainty in their investment portfolios.

It is worth noting that this paper is limited to the scope of binary news classifications. In Shi and Ho (2021) the analysis was extended by constructing weighted news counts using RavenPack scores, which account for varying degrees of negativeness and positiveness. Future research could explore the use of LLMs to design more nuanced news sentiment scores (e.g., ranging from 0 for maximum negativeness to 100 for maximum positiveness) to more comprehensively capture news sentiment. This would likely involve fine-tuning and applying tailored Low-Rank Adaptation (LoRA) techniques to LLMs to enhance the accuracy of sentiment scoring. Such developments are avenues for future work.

The authors would also like to thank the Macquarie University for the research support. We particularly thank the Editor (Max Croce) and the anonymous referee for providing valuable and insightful comments on earlier drafts. The usual disclaimer applies.

## Acknowledgments

Supplementary material related to this article can be found online at https://doi.org/10.1016/j.econlet.2024.112124.

## Appendix A. Supplementary data

#### Data availability

The authors do not have permission to share data.

## References

Buehlmaier, M.M., Whited, T.M., 2018. Are financial constraints priced? Evidence from textual analysis. Rev. Financ. Stud. 31 (7), 2693–2728.

Clark, P.K., 1973. A subordinated stochastic process model with finite variance for speculative prices. Econometrica 41 (1), 135–155.

Davidson, J., 2004. Moment and memory properties of linear conditional heteroscedasticity models, and a new model. J. Bus. Econom. Statist. 22 (1), 16–29.

Diebold, F.X., Inoue, A., 2001. Long memory and regime switching. J. Econom. 105, 131–159.

Gentzkow, M., Kelly, B., Taddy, M., 2019. Text as data. J. Econ. Lit. 57 (3), 535–574.

Haas, M., 2009. Value-at-risk via mixture distributions reconsidered. Appl. Math. Comput. 215 (6), 2103–2119.

Haas, M., Mittnik, S., Paolella, M.S., 2004. A new approach to Markov-switching GARCH models. J. Financ. Econom. 2 (4), 493–530.

Hamilton, J.D., 1989. A new approach to the economic analysis of nonstationary time series and the business cycle. Econometrica 57, 357–384.

Ho, K.-Y., Shi, Y., Zhang, Z., 2013. How does news sentiment impact asset volatility? Evidence from long memory and regime-switching approaches. N. Am. J. Econ. Financ. 26, 436–456.

Huang, X., Teoh, S.H., Zhang, Y., 2014. Tone management. Account. Rev. 89 (3), 1083–1113.

Jeon, Y., McCurdy, T.H., Zhao, X., 2022. News as sources of jumps in stock returns: Evidence from 21 million news articles for 9000 companies. J. Financ. Econ. 145(2), 1–17.

Schuettler, J., Audrino, F., Sigrist, F., 2024. Does sentiment help in asset pricing? A novel approach using large language models and market-based labels. Available at SSRN: https://ssrn.com/abstract=4905533.

Shi, Y., 2023. Long memory and regime switching in the stochastic volatility modelling. Ann. Oper. Res. 320 (2), 999–1020.

Shi, Y., Ho, K.-Y., 2015. Long memory and regime switching: A simulation study on the Markov regime-switching ARFIMA model. J. Bank. Finance 61, S189–S204.

Shi, Y., Ho, K.-Y., 2021. News sentiment and states of stock return volatility: Evidence from long memory and discrete choice models. Finance Res. Lett. 38, 101446.

Verma, R., Kim, S., Walter, D., 2018. Syntactical analysis of the weaknesses of sentiment analyzers. In: Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing. pp. 1122–1127.

Yang, D., Zhang, Q., 2000. Drift-independent volatility estimation based on high, low, open, and close prices. J. Bus. 73 (3), 477–492.

