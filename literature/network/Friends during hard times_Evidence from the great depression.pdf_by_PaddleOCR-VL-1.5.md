JOURNAL OF FINANCIAL AND QUANTITATIVE ANALYSIS Vol. 59, No. 6, Sep. 2024, pp. 2647–2694 © The Author(s), 2023. Published by Cambridge University Press on behalf of the Michael G. Foster School of Business, University of Washington. This is an Open Access article, distributed under the terms of the Creative Commons Attribution licence (http://creativecommons.org/licenses/by/4.0), which permits unrestricted re-use, distribution and reproduction, provided the original article is properly cited. doi:10.1017/S0022109023000765

# Friends During Hard Times: Evidence from the Great Depression

Tania Babina

Columbia University Graduate School of Business

tania.babina@gsb.columbia.edu

Diego García

University of Colorado Leeds School of Business

diego.garcia@colorado.edu

Geoffrey Tate  $ \textcircled{D} $

University of Maryland Robert H. Smith School of Business and NBER

gtate@umd.edu (corresponding author)

## Abstract

Using a novel data set of over 3,500 public and private firms, we construct the network of executive and director connections prior to the 1929 financial market crash. We find that more connected firms have 17% higher 10-year survival rates. Consistent with a working capital channel, the results are strongest for small, private, cash-poor firms, and firms located in counties with high bank suspension rates. Moreover, connections to cash-rich firms that increase accounts receivable matter the most. Our results suggest that network connections can play a stabilizing role during a financial crisis by easing the flow of capital to constrained firms.

## 1. Introduction

How do connections between firms’ executives and directors affect the response to large negative macroeconomic shocks? Information flow through the connections of top decision-makers could exacerbate a crisis by facilitating herding (Banerjee (1992), Bikhchandani, Hirshleifer, and Welch (1992), and Goel and Thakor (2010)). Alternatively, connections could improve outcomes by reducing the frictions that impede the flow of information necessary to make optimal choices.

(Ellison and Fudenberg (1993), (1995)). In the context of a financial crisis, firms use trade credit and other forms of financial assistance from industrial peers to substitute for external finance (Love, Preve, and Sarria-Allende (2007), Garcia-Appendini and Montoriol-Garriga (2013), Almeida, Kim, and Kim (2015), Buchuk, Larrain, Prem, and Urzua (2020), Santioni, Schiantarelli, and Strahan (2020), Gao (2021), and Gofman and Wu (2022)). Information flow through network connections could allow executives to evaluate the costs and benefits of undertaking an intermediation role normally performed by the financial sector.

We use a novel panel data set with financial data for over 3,500 firms during the Great Depression to study the effect of executive and director network connections on firm fragility. Focusing on firm failure as a fragility measure, we document that connections are associated with larger 10-year survival rates: A firm with more connections than the median has a probability of failure that is roughly 3.4 percentage points lower than a firm with fewer connections than the median (a 17% decrease from the mean failure rate of 20%). The effect is 2 to 3 times larger for small, private, cash-poor, and rural firms. Moreover, the effects are the most pronounced in counties that experienced the highest rates of bank failure between 1928 and 1933. Links to cash-rich firms that increase accounts receivable have the largest association with survival, suggesting that information flow through networks facilitates the flow of trade credit.

We focus on the Great Depression for several reasons. The Depression is the largest negative economic shock to U.S. markets during the time period for which we can collect comprehensive data on industrial firms from Moody's manuals. $ ^{1} $ Unlike other downturns, the Depression was accompanied by high rates of firm failure, implying that many firms were unable to weather the shock by spending out of their cash reserves or reducing expenditures. Moreover, the severity of financial disruptions during the Depression varied significantly at the local level because of segmentation in the banking industry (Calomiris and Mason (2003a), (2003b), Nanda and Nicholas (2014)), providing a source of variation in the cross section that we can use to identify responses to the shock. Similarly, we can exploit the local nature of the director markets of the era to provide plausibly exogenous variation in director network connections.

In addition, we observe large subsamples of publicly traded and privately held firms for which the outcome of interest (firm failure) is directly comparable. Private firms, which comprise roughly 60% of our sample, appear to be more similar in size to publicly traded firms than we typically observe in recent data. $ ^{2} $ Thus, it is more credible to make cross-group comparisons to determine the effect of additional sources of finance. Moreover, public listing does not imply the same regulatory requirements as it does today. For example, the independence requirements in

regulations such as the Sarbanes Oxley Act of 2002 could constrain the ability of firms to construct optimal networks. If this is the case, historical data can allow us to study the stabilizing effects of network connections in a setting in which firms are not bound by these constraints. $ ^{3} $ By contrast, we cannot observe the appropriate counterfactual in modern data without making cross-country comparisons. Thus, our analysis provides unique evidence on the attractiveness of alternative policy regimes in the context of a major financial shock.

A challenge for all analyses of network effects is that network ties are not randomly assigned. Our analysis of differential outcomes following the 1929 financial shock addresses some sources of concern. In particular, it is unlikely that firms create the connections we observe in 1928 in anticipation of the coming Depression. Thus, to the extent that highly connected and less connected firms are otherwise similar, conditional on a set of controls that includes state and industry fixed effects, we can interpret the ex ante differences in connections as exogenous for the purposes of identifying the effect of connections on responses to the shock.

The remaining concern is that there is an omitted, unobservable factor that positively correlates with network connections and also predicts heightened survival odds during the Depression. We use the greater segmentation of markets during the Depression era as a source of plausibly exogenous local variation that we can exploit for identification. First, we build on the approach from Nanda and Nicholas (2014) by exploiting county-level variation in bank distress rates. Because of restrictions on interstate branching, local banks were an important source of working capital financing in the 1920s and 1930s, even for large firms. Thus, we can use variation in the distress rate of local banks to measure the intensity of the financial shock faced by firms. We find a much stronger positive effect of network ties on firm survival among firms located in areas with more local bank distress between 1930 and 1933. This result addresses the omitted variable concern under the plausible assumption that counties with more bank distress are not also counties that are home to firms of (unobservable) ex ante higher quality.

Second, we exploit the local nature of director markets in the 1920s and 1930s. We construct an instrument for network ties that isolates variation in the demand for directors' services in other local firms due to variation in the average sizes of the boards of in-state firms in their industry, conditional on the total number of in-state, in-industry firms (and other measures of local market activity). We find a positive relation between the instrumented number of network connections to other firms and a firm's likelihood of survival. The results provide a causal interpretation under the assumption that small average board sizes in a state–industry pair, conditional on a wide set of controls including the firm's own board size, affect firm survival only through their positive correlation with network connections.

As a third way to address the endogeneity concern, we measure heterogeneity in the effect of connections in the cross section. Under a causal interpretation,

connections should help firms that would otherwise be more prone to fail the most, such as financially constrained firms or firms with poor access to information about changing fundamentals. We indeed find that the effect of connections is concentrated among small, private, cash-poor, and rural firms, characteristics that generally predict higher failure rates during the Depression. For these firms, the magnitude of the effect is two to three times our baseline estimate. Thus, to explain our results, an omitted factor must not only positively correlate with connections and survival probabilities, but also have its primary influence among the most constrained firms.

As a final step, we provide evidence to distinguish among several economic channels through which network connections could aid firms during the crisis. First, we test whether firms use their network links to access credit from connected firms. Consistent with this channel, we find that the effect of network connections on survival derives primarily from connections of financially constrained to cash-rich firms. Moreover, we find that it is connections to cash-rich firms that increase their accounts receivable during the credit crunch from 1929 to 1933 that matter the most, suggesting that firms use trade credit as a mechanism to extend finance to connected trading partners. At the same time, we find no evidence that connections correlate with a higher use of trade credit as a source of financing in 1928, prior to the crisis. Thus, our results are consistent with information flow through director networks facilitating the expansion of trade credit in a crisis (when risk is high). Moreover, network connections are not likely to proxy for greater financial strength among a firm's trading partners.

Second, we consider the possibility that connections soften product market competition. Consistent with this channel, we find that connections to within-industry peers matter more for survival than out-of-industry links. However, we also find that within-industry links matter more when they are to out-of-state firms than to in-state firms, even though such firms are less likely to compete in the same product markets. Third, we test whether connections between firms are due to the presence of commercial bankers who sit on multiple boards and ease access to credit during the crisis. We find that the effect of connections remains when we purge all potential bankers from our sample of connected directors. More generally, we find that our results exist even among firms that did not have outstanding bank debt at the outset of the crisis. Thus, while connections to banks likely do assist troubled firms (Frydman and Hilt (2017)), our analysis uncovers a distinct mechanism. We also do not find any evidence that network connections proxy for the benefits of connections to major financial centers (i.e., cities with local stock markets). Finally, we test whether connected firms attract more equity investments from other industrial firms, finding that they are more likely to become acquisition targets. Though the mechanisms we consider are not mutually exclusive, our results suggest that a key channel through which networks lower firm failure rates is by facilitating access to capital from less constrained industrial firms. Moreover, our results suggest an externality from policies to support the financial health of large, connected firms during a crisis: Those firms are likely to have an information advantage in transferring needed capital to constrained trading partners.

Our analysis makes several contributions to the literature. First, we provide novel evidence on the role of economic networks during financial crises. The banking

literature largely identifies network connections as an amplification mechanism for shocks to the credit market (Das, Mitchener, and Vossmeyer (2018), Calomiris, Jaremski, and Wheelock (2019), and Mitchener and Richardson (2019)). Evidence on the effects of ownership and product market links among industrial firms is mixed: Some studies find evidence of a similar amplification mechanism (Ahem (2013), Giroud and Mueller (2019), and Loualiche, Vickers, and Ziebarth (2019)), while others find evidence that firms use such links to access financing when credit markets freeze (Garcia-Appendini and Montoriol-Garriga (2013), Almeida, Kim, and Kim (2015), Buchuk, Larrain, Prem, and Urzua (2020), Santioni, Schiantarelli, and Strahan (2020), and Gao (2021)). Adelino, Ferreira, Giannetti, and Pires (2023) find that product market links can facilitate the transmission of unconventional monetary policy from firms whose bonds are purchased to constrained trading partners. We study a different kind of link: connections through shared directors and executives. We find that these links are a stabilizing force during a financial crisis. Our results suggest that connections lower the information costs associated with providing funding to distressed firms, allowing industrial firms to substitute for banks as providers of working capital. The benefits of providing such assistance are likely to be largest when the recipient firm is a customer or supplier that might otherwise fail (Gofman and Wu (2022)). Thus, our evidence provides novel insight into the conditions under which product market connections are likely to provide a stabilization rather than an amplification mechanism. Literature from the Depression era noted the steep decline in bank lending as a source of corporate financing: Business loans declined from around 40% of bank earning assets in 1929 to less than 20% by 1936 (Reifer, Friday, Lichtenstein, and Riddle (1937)), suggesting that industrial firms might have partially displaced banks in providing working capital to the system. Our results support this conjecture and point to the economic conditions under which industrial firms are willing to play this role.

Our analysis also contributes to the existing literature on executive and director networks. Many existing articles focus on either the implications of network ties for corporate governance (Hwang and Kim (2009), Fracassi and Tate (2012), Nguyen (2012), and Schmidt (2015)) or the correlation of corporate policies across firms (Shue (2013), Fracassi (2017)). Work that links networks with access to financial capital typically focuses on connections to financial institutions (Guner, Malmendier, and Tate (2008), Engelberg, Gao, and Parsons (2012), and Frydman and Hilt (2017)). A partial exception is Huang, Jiang, and Lie (2012), who find evidence that connected S&P 1500 firms have stronger operating performance around the 2008 financial crisis. However, they also emphasize the role of personal ties to lenders, finding that firms in financial distress between 1998 and 2009 have a lower probability of filing for bankruptcy when they have such linkages. Our sole focus, instead, is on network links among industrial firms and the channels through which they promote stability in times of crisis. Internationally, Xia, Zhang, Cao, and Xu (2019) find an association between connections and trade credit in a Chinese sample and Amore, Caselli, Colla, and Corbetta (2019) find a similar link among family firms in Italy.

Finally, we provide new insight into how disruptions to the financial system affected business outcomes during the Great Depression. Existing work debates the relative importance of a number of financial factors for outcomes during the

Depression. $ ^{4} $ Most relevant to our analysis is the literature focusing on the effects of bank failures. Existing work finds that bank failures had large negative effects on state-level income growth (Calomiris and Mason (2003b)). Recent work also links bank failures to business outcomes including revenue growth (Ziebarth (2013)), innovation (Nanda and Nicholas (2014)), and employment growth (Ziebarth (2013), Lee and Mezzanotti (2017), and Benmelech, Frydman, and Papanikolaou (2019)). In our analysis, we likewise observe a significant effect of local bank failure on the probability of firm failure. We build on this literature by analyzing the interaction of banking shocks with firm-level network effects, using a novel data set of executive and director connections. $ ^{5} $ Given the documented effects of links among banks, we might expect firm networks to propagate shocks from firms that are directly affected by the failure of a lending bank to connected firms that are not. However, we instead find that they are a mitigating force: Information flow between connected executives and directors facilitates the flow of finance from cash-rich to distressed industrial firms.

### II. Data

To conduct our analysis of the effect of network ties on firm survival, we use the 1928 volume of the Moody’s Industrial manual to construct a novel mapping of the links between directors and executives of industrial firms. We collect information on the executives and directors of all firms in the manual using OCR and natural language processing techniques, including public and private firms, but excluding foreign firms and subsidiaries. $ ^{6} $ For a detailed description of the collection process and variable construction, see the Appendix. Our final data set has 3,753 firms between which we measure network links based on the presence of a common director or an executive in one company who is a director another. $ ^{7} $ To the best of our knowledge, our sample provides the broadest coverage of firms from the era in the existing literature.

We also collect a variety of financial information for each company from the 1928 manual. The manual contains fairly detailed accountings of firms' financial liabilities as of the end of the fiscal year prior to the manual's publication. We record the total value of each firm's outstanding debt and the identity of the stock exchanges on which it is listed. We also record the value of firms' cash holdings.

and total assets. Compared to balance sheet information, the information on income statement items in the manuals, such as sales or net income, tends to be less standardized across firms and is also less often available. Where available, we record the bottom line of firms' income statements and refer to it as "net income."⁸ We also obtain rich information on firm geography: For each firm, we record the locations of all the firms' offices. Finally, though we do not observe standardized industry codes such as SIC or NAICS codes, we use information on the nation's "basic industries" contained in the manual to construct an industry classification. Our approach to measuring industries is similar in spirit to that of Hoberg and Phillips (2016). We retrieve key words from the description of each industry in the manual and then search for the key words in the description of each firm. We use the relative frequencies of the key words from each industry to assign sample firms to industries, allowing the possibility that firms match to multiple industries.⁹ In the Appendix, we provide additional details. We also validate the classification by showing that our industry groups have significant explanatory power for the cross section of leverage beyond standard controls.¹⁰

We use information from the 1938 manual to construct our main dependent variables: i) an indicator variable that is equal to 1 if a firm fails by 1937 and ii) an indicator variable that is equal to 1 if a firm is acquired or merges with another firm by 1937. $ ^{11} $ The manual contains a list of companies that were included in the 1928 to 1937 manuals, but that are not included in the 1938 manual, and the reason for their exclusion. We use this list to construct the dependent variables. We do not count name changes as failures. Nor do we count firms that are acquired, because our economic hypothesis makes the opposite prediction for the relation with connections.

An advantage of using firm survival as our main outcome measure is that it is consistently measured and directly comparable across firms, both public and private. However, using firm survival as our outcome measure means that we must be cautious about making general welfare claims. Survival is in the private interests of the firm's claimholders, but could be socially inefficient. Nevertheless, in the context of network ties, such an outcome would require inefficient investment

choices by outsiders to whom the firm’s executives and directors share connections. An alternative approach could be to study differences in accounting variables such as asset or sales growth. However, our interest is in the effect of network connections around a major negative shock. If there are significant differences in firm survival rates across treated and untreated firms, then differences in growth rates are difficult to interpret. For example, if firms with slower growth rates are at greater risk of failure and connections increase the odds of survival, then network connections might predict lower growth rates conditional on firm survival (particularly if the primary effect of connected firms is to function as “financiers of last resort”). It would be incorrect to conclude that connections harm connected firms.

As our main measure of network connections, we compute each firm's degree centrality: the total number of connections it has through its executives and directors to other firms in the sample (TOTAL_CONNECTONS). To help tease out the mechanism through which connections matter for firm survival, we also consider several partitions of the network. We consider separately the subsets of connections to cash-rich firms and connections to cash-poor firms. We define a firm as cash-rich (cash-poor) if its cash holdings scaled by total assets are larger (smaller) than the sample median. Similarly, we consider separately connections to firms that increase and decrease accounts receivable during the peak Depression period of 1928 to 1933. We also consider two other partitions to distinguish between "local" and "distant" connections: connections within and outside the firm's industry and connections within and outside the states in which the firm has offices. All connections measures are likely to have a mechanical positive correlation with board size. Thus, we include board size as a control in all of our analysis.

Our degree centrality measures capture direct connections between pairs of companies, or the number of paths of length one that include each firm. Another way to characterize the director network is by calculating each firm's eigenvector centrality. This measure instead counts the number of paths of all lengths that include the firm. In our sample, the two measures are strongly positively correlated (0.67). Nevertheless, they could capture different economic channels through which networks affect firm survival. Direct firm-to-firm assistance (e.g., through the provision of trade credit) could be better captured by degree centrality, while general access to economic information could be better captured by the eigenvector measure. Though the two measures generally relate to firm survival in a similar way, we find stronger relations between degree centrality and firm survival and thus focus our analysis on that measure. $ ^{12} $

In Table 1, we report summary statistics of the data. The mean (median) firm in our sample has total assets of $16.029 M ($4.259 M) in 1927 dollars. These numbers translate into roughly $240 M ($64.5 M) in 2017 dollars. Among small firms with total assets less than the sample median, mean (median) total assets are $2.158 M ($2.050 M). Thus, our larger sample size compared to other studies of

Depression era firms does not appear to come from filling the sample with large numbers of tiny firms. The mean (median) firm has cash holdings equal to 8.6% (4.9%) of total assets. The mean (median) firm has 8.2 (7) directors on the board, which roughly equals the mean of TOTAL_CONNECTIONS (7.5). Connections to cash-rich firms are more common than connections to cash-poor firms, consistent with those connections having greater value to the firm. Connections to firms that increased receivables between 1928 and 1933 could be similarly valuable during the crisis. However, we find that they are far less common than connections to firms that decrease receivables, consistent with the unanticipated nature of the shock. We observe a rich distribution of firms across industries. Geographically, we observe

<div style="text-align: center;"><div style="text-align: center;">TABLE 1</div> </div>


#### Summary Statistics

The sample in Table 1 consists of firms from the 1928 volume of the Moody's Industrial manual, excluding foreign firms and subsidiaries. All variables are measured as of 1928, except where indicated. RURAL is an indicator variable equal to 1 for firms that have offices only in counties in which the rural population in 1930 is greater than 60%. TOTAL_CONNECTIONS is the sum of connections to other firms in the sample via shared directors or managers. In measuring CONNECTIONS_TO_HIGH(LOW)_CASH_FIRMS, high-cash firms are firms with CASH/ASSETS above the sample median value. Low-cash firms are the complementary set of firms with values below the sample median. Connections to firms for which CASH/ASSETS is unavailable are not included in either group. TOTAL_ASSETS are reported in $1,000.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td colspan="2">No. of Obs.</td><td style='text-align: center; word-wrap: break-word;'>Mean</td><td style='text-align: center; word-wrap: break-word;'>Median</td><td style='text-align: center; word-wrap: break-word;'>Std. Dev.</td></tr><tr><td colspan="6">Panel A. Main Control Variables</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL_ASSETS</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>16,029</td><td style='text-align: center; word-wrap: break-word;'>4,259</td><td style='text-align: center; word-wrap: break-word;'>68,924</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>0.086</td><td style='text-align: center; word-wrap: break-word;'>0.049</td><td style='text-align: center; word-wrap: break-word;'>0.1</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>0.106</td><td style='text-align: center; word-wrap: break-word;'>0.001</td><td style='text-align: center; word-wrap: break-word;'>0.145</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>NET_INCOME/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>2,158</td><td style='text-align: center; word-wrap: break-word;'>0.065</td><td style='text-align: center; word-wrap: break-word;'>0.054</td><td style='text-align: center; word-wrap: break-word;'>0.078</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>ACCTS_RECEIVABLE/ACCTS_PAYABLE</td><td style='text-align: center; word-wrap: break-word;'>2,321</td><td style='text-align: center; word-wrap: break-word;'>7.566</td><td style='text-align: center; word-wrap: break-word;'>2.488</td><td style='text-align: center; word-wrap: break-word;'>52.312</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>0.573</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>0.495</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>RURAL</td><td style='text-align: center; word-wrap: break-word;'>2,820</td><td style='text-align: center; word-wrap: break-word;'>0.061</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>0.240</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>NUMBER_OF_DIRECTORS</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>8.248</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>3.433</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td colspan="6">Panel B. Network Connection Measures</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL_CONNECTIONS</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>7.522</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>10.13</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CONNECTIONS_TO_HIGH_CASH_FIRM</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>3.465</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>5.392</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CONNECTIONS_TO_LOW_CASH_FIRM</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>2.953</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>4.193</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CONNECTIONS_TO_INC_ACCTS_REC_FIRM</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>0.871</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1.562</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CONNECTIONS_TO_DEC_ACCTS_REC_FIRM</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>2.616</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>4.262</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CONNECTIONS_TO_OUT_OF_STATE_FIRM</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>3.078</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>4.921</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CONNECTIONS_TO_IN_STATE_FIRM</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>2.671</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>4.838</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CONNECTIONS_TO_IN_INDUSTRY_FIRM</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>3.299</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>5.514</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CONNECTIONS_TO_OUT_OF_INDUSTRY_FIRM</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>3.549</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>6.194</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td colspan="6">Panel C. Key Outcome Variables</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DISAPPEARED_BY_1937</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>0.197</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>0.398</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>ACQUIRED_BY_1937</td><td style='text-align: center; word-wrap: break-word;'>3,024</td><td style='text-align: center; word-wrap: break-word;'>0.108</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>0.310</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \Delta $ln(ACCTS_RECEIVABLE/ACCTS_PAYABLE)</td><td style='text-align: center; word-wrap: break-word;'>1,567</td><td style='text-align: center; word-wrap: break-word;'>-0.068</td><td style='text-align: center; word-wrap: break-word;'>-0.029</td><td style='text-align: center; word-wrap: break-word;'>1.293</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td colspan="6">Panel D. Industry Distribution (N = 2,774)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Freq</td><td style='text-align: center; word-wrap: break-word;'>Failure Rate</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Freq</td><td style='text-align: center; word-wrap: break-word;'>Failure Rate</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>STEEL_AND_IRON</td><td style='text-align: center; word-wrap: break-word;'>0.052</td><td style='text-align: center; word-wrap: break-word;'>0.119</td><td style='text-align: center; word-wrap: break-word;'>0.023</td><td style='text-align: center; word-wrap: break-word;'>0.108</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>COAL</td><td style='text-align: center; word-wrap: break-word;'>0.038</td><td style='text-align: center; word-wrap: break-word;'>0.219</td><td style='text-align: center; word-wrap: break-word;'>0.042</td><td style='text-align: center; word-wrap: break-word;'>0.181</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TEXTILES</td><td style='text-align: center; word-wrap: break-word;'>0.070</td><td style='text-align: center; word-wrap: break-word;'>0.292</td><td style='text-align: center; word-wrap: break-word;'>0.159</td><td style='text-align: center; word-wrap: break-word;'>0.233</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>MOTOR</td><td style='text-align: center; word-wrap: break-word;'>0.031</td><td style='text-align: center; word-wrap: break-word;'>0.172</td><td style='text-align: center; word-wrap: break-word;'>0.113</td><td style='text-align: center; word-wrap: break-word;'>0.201</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>RUBBER</td><td style='text-align: center; word-wrap: break-word;'>0.014</td><td style='text-align: center; word-wrap: break-word;'>0.375</td><td style='text-align: center; word-wrap: break-word;'>0.127</td><td style='text-align: center; word-wrap: break-word;'>0.177</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PETROLEUM</td><td style='text-align: center; word-wrap: break-word;'>0.074</td><td style='text-align: center; word-wrap: break-word;'>0.175</td><td style='text-align: center; word-wrap: break-word;'>0.129</td><td style='text-align: center; word-wrap: break-word;'>0.204</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>COPPER</td><td style='text-align: center; word-wrap: break-word;'>0.021</td><td style='text-align: center; word-wrap: break-word;'>0.228</td><td style='text-align: center; word-wrap: break-word;'>0.018</td><td style='text-align: center; word-wrap: break-word;'>0.120</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>EQUIPMENT</td><td style='text-align: center; word-wrap: break-word;'>0.099</td><td style='text-align: center; word-wrap: break-word;'>0.197</td><td style='text-align: center; word-wrap: break-word;'>0.055</td><td style='text-align: center; word-wrap: break-word;'>0.301</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>SUGAR</td><td style='text-align: center; word-wrap: break-word;'>0.031</td><td style='text-align: center; word-wrap: break-word;'>0.174</td><td style='text-align: center; word-wrap: break-word;'>0.051</td><td style='text-align: center; word-wrap: break-word;'>0.176</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOBACCO</td><td style='text-align: center; word-wrap: break-word;'>0.009</td><td style='text-align: center; word-wrap: break-word;'>0.160</td><td style='text-align: center; word-wrap: break-word;'>0.112</td><td style='text-align: center; word-wrap: break-word;'>0.224</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PACKING</td><td style='text-align: center; word-wrap: break-word;'>0.013</td><td style='text-align: center; word-wrap: break-word;'>0.162</td><td style='text-align: center; word-wrap: break-word;'>0.020</td><td style='text-align: center; word-wrap: break-word;'>0.196</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>SHOE_AND_LEATHER</td><td style='text-align: center; word-wrap: break-word;'>0.021</td><td style='text-align: center; word-wrap: break-word;'>0.237</td><td style='text-align: center; word-wrap: break-word;'>0.006</td><td style='text-align: center; word-wrap: break-word;'>0.063</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>RETAIL_TRADING</td><td style='text-align: center; word-wrap: break-word;'>0.081</td><td style='text-align: center; word-wrap: break-word;'>0.196</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr></table>



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2"></td><td colspan="3">TABLE 1 (continued)</td></tr><tr><td colspan="3">Summary Statistics</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Panel E. State Distribution (N = 3,009)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>ALABAMA</td><td style='text-align: center; word-wrap: break-word;'>0.004</td><td style='text-align: center; word-wrap: break-word;'>MONTANA</td><td style='text-align: center; word-wrap: break-word;'>0.003</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>ARKANSAS</td><td style='text-align: center; word-wrap: break-word;'>0.001</td><td style='text-align: center; word-wrap: break-word;'>NORTH_CAROLINA</td><td style='text-align: center; word-wrap: break-word;'>0.005</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>ARIZONA</td><td style='text-align: center; word-wrap: break-word;'>0.003</td><td style='text-align: center; word-wrap: break-word;'>NORTH_DAKOTA</td><td style='text-align: center; word-wrap: break-word;'>0.001</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CALIFORNIA</td><td style='text-align: center; word-wrap: break-word;'>0.046</td><td style='text-align: center; word-wrap: break-word;'>NEBRASKA</td><td style='text-align: center; word-wrap: break-word;'>0.004</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>COLORADO</td><td style='text-align: center; word-wrap: break-word;'>0.010</td><td style='text-align: center; word-wrap: break-word;'>NEW_HAMPSHIRE</td><td style='text-align: center; word-wrap: break-word;'>0.002</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CONNECTICUT</td><td style='text-align: center; word-wrap: break-word;'>0.026</td><td style='text-align: center; word-wrap: break-word;'>NEW_JERSY</td><td style='text-align: center; word-wrap: break-word;'>0.037</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DISTRICT_OF_COLUMBIA</td><td style='text-align: center; word-wrap: break-word;'>0.002</td><td style='text-align: center; word-wrap: break-word;'>NEW_MEXICO</td><td style='text-align: center; word-wrap: break-word;'>0.001</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DELAWARE</td><td style='text-align: center; word-wrap: break-word;'>0.025</td><td style='text-align: center; word-wrap: break-word;'>NEVADA</td><td style='text-align: center; word-wrap: break-word;'>0.004</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>FLORIDA</td><td style='text-align: center; word-wrap: break-word;'>0.003</td><td style='text-align: center; word-wrap: break-word;'>NEW_YORK</td><td style='text-align: center; word-wrap: break-word;'>0.281</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GEORGIA</td><td style='text-align: center; word-wrap: break-word;'>0.012</td><td style='text-align: center; word-wrap: break-word;'>OHIO</td><td style='text-align: center; word-wrap: break-word;'>0.083</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>HAWAII</td><td style='text-align: center; word-wrap: break-word;'>0.005</td><td style='text-align: center; word-wrap: break-word;'>OKLAHOMA</td><td style='text-align: center; word-wrap: break-word;'>0.008</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>IOWA</td><td style='text-align: center; word-wrap: break-word;'>0.003</td><td style='text-align: center; word-wrap: break-word;'>OREGON</td><td style='text-align: center; word-wrap: break-word;'>0.005</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>IDAHO</td><td style='text-align: center; word-wrap: break-word;'>0.002</td><td style='text-align: center; word-wrap: break-word;'>PENNSYLVANIA</td><td style='text-align: center; word-wrap: break-word;'>0.084</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>ILLINOIS</td><td style='text-align: center; word-wrap: break-word;'>0.094</td><td style='text-align: center; word-wrap: break-word;'>RHODE_ISLAND</td><td style='text-align: center; word-wrap: break-word;'>0.006</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>INDIANA</td><td style='text-align: center; word-wrap: break-word;'>0.013</td><td style='text-align: center; word-wrap: break-word;'>SOUTH_CAROLINA</td><td style='text-align: center; word-wrap: break-word;'>0.008</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>KANSAS</td><td style='text-align: center; word-wrap: break-word;'>0.003</td><td style='text-align: center; word-wrap: break-word;'>SOUTH_DAKOTA</td><td style='text-align: center; word-wrap: break-word;'>0.000</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>KENTUCKY</td><td style='text-align: center; word-wrap: break-word;'>0.006</td><td style='text-align: center; word-wrap: break-word;'>TENNESSEE</td><td style='text-align: center; word-wrap: break-word;'>0.009</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>LOUISIANA</td><td style='text-align: center; word-wrap: break-word;'>0.011</td><td style='text-align: center; word-wrap: break-word;'>TEXAS</td><td style='text-align: center; word-wrap: break-word;'>0.011</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>MASSACHUSETTS</td><td style='text-align: center; word-wrap: break-word;'>0.138</td><td style='text-align: center; word-wrap: break-word;'>UTAH</td><td style='text-align: center; word-wrap: break-word;'>0.008</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>MARYLAND</td><td style='text-align: center; word-wrap: break-word;'>0.017</td><td style='text-align: center; word-wrap: break-word;'>VIRGINIA</td><td style='text-align: center; word-wrap: break-word;'>0.011</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>MAINE</td><td style='text-align: center; word-wrap: break-word;'>0.007</td><td style='text-align: center; word-wrap: break-word;'>VERMONT</td><td style='text-align: center; word-wrap: break-word;'>0.002</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>MICHIGAN</td><td style='text-align: center; word-wrap: break-word;'>0.046</td><td style='text-align: center; word-wrap: break-word;'>WASHINGTON</td><td style='text-align: center; word-wrap: break-word;'>0.010</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>MINNESOTA</td><td style='text-align: center; word-wrap: break-word;'>0.013</td><td style='text-align: center; word-wrap: break-word;'>WISCONSIN</td><td style='text-align: center; word-wrap: break-word;'>0.022</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>MISSOURI</td><td style='text-align: center; word-wrap: break-word;'>0.034</td><td style='text-align: center; word-wrap: break-word;'>WEST_VIRGINIA</td><td style='text-align: center; word-wrap: break-word;'>0.009</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>MISSISSIPPI</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>WYOMING</td><td style='text-align: center; word-wrap: break-word;'>0.001</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>OUTSIDE_US</td><td style='text-align: center; word-wrap: break-word;'>0.007</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Panel F. Failure Rates by Firm Characteristics</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>AGE ≤ 5</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.215</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5 &lt; AGE ≤ 15</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.203</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>15 &lt; AGE ≤ 25</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.192</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>AGE &gt; 25</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.177</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.266</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PUBLIC</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.104</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL_ASSETS_QUARTILE_1</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.341</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL_ASSETS_QUARTILE_2</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.234</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL_ASSETS_QUARTILE_3</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.147</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL_ASSETS_QUARTILE_4</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.065</td></tr></table>

firms operating in 49 states (we do not observe any firms in Alaska, which was not a U.S. state at the time), though there are noticeable clusters of firms in New York and Massachusetts.

Turning to our key dependent variables, the full-sample frequency of firm failure by 1937 is 19.7%. In addition, another 10.8% of firms were acquired. We also report variation in firm failure rates by industry (Panel D of Table 1) and by firm characteristics (Panel F of Table 1). We observe large differences in failure rates between public and private firms (private firms fail at higher rates) as well as for small and large firms (the quartile of smallest firms fails at a rate that is five times the rate in the top quartile). Interestingly, differences in failure rates by firm age are not very pronounced, though young firms are somewhat more likely to fail than older firms.

In Table 2, we report pairwise correlations of several of our key dependent and independent variables. Notably, we observe a strong and statistically significant negative correlation between the TOTAL_CONNECTIONS measure and the indicator for firm exit by 1937. We also observe that network ties are less frequent among private firms and among firms in rural areas. These correlations are consistent with geographic segmentation in the director labor market, a feature we exploit.

<div style="text-align: center;"><div style="text-align: center;">TABLE 2 Pairwise Correlations</div> </div>


The sample in Table 2 consists of firms from the 1928 volume of the Moody's Industrial manual, excluding foreign firms and subsidiaries. All variables are measured as of 1928, except where indicated. RURAL is an indicator variable equal to 1 for firms that have offices only in counties in which the rural population in 1930 is greater than 60%. TOTAL_CONNECTIONS is the sum of connections to other firms in the sample via shared directors or managers. The p-value and number of observations are reported in parentheses below each correlation.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>TOT_CONN</td><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>RURAL</td><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>TOTAL_ASSETS</td><td style='text-align: center; word-wrap: break-word;'>NI/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>REC/PAY</td><td style='text-align: center; word-wrap: break-word;'>DISAPPEARED</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL_CONNECTIONS</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>-0.2137 (0.00, 3.024)</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>RURAL</td><td style='text-align: center; word-wrap: break-word;'>-0.0637 (0.00, 2.820)</td><td style='text-align: center; word-wrap: break-word;'>0.0811 (0.00, 2.820)</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>0.0064 (0.63, 3.024)</td><td style='text-align: center; word-wrap: break-word;'>0.0868 (0.00, 3.024)</td><td style='text-align: center; word-wrap: break-word;'>0.0179 (0.34, 2.820)</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>0.0348 (0.06, 2.992)</td><td style='text-align: center; word-wrap: break-word;'>-0.0897 (0.00, 2.992)</td><td style='text-align: center; word-wrap: break-word;'>-0.0372 (0.05, 2.820)</td><td style='text-align: center; word-wrap: break-word;'>-0.2369 (0.00, 2.992)</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL_ASSETS</td><td style='text-align: center; word-wrap: break-word;'>0.1910 (0.00, 3.024)</td><td style='text-align: center; word-wrap: break-word;'>-0.1667 (0.00, 3.024)</td><td style='text-align: center; word-wrap: break-word;'>-0.0442 (0.02, 2.820)</td><td style='text-align: center; word-wrap: break-word;'>0.0208 (0.25, 3.024)</td><td style='text-align: center; word-wrap: break-word;'>0.0266 (0.15, 2.992)</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>NET_INCOME/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>-0.0353 (0.10, 2.158)</td><td style='text-align: center; word-wrap: break-word;'>-0.1257 (0.00, 2.158)</td><td style='text-align: center; word-wrap: break-word;'>-0.0378 (0.09, 1.997)</td><td style='text-align: center; word-wrap: break-word;'>-0.2467 (0.00, 2.158)</td><td style='text-align: center; word-wrap: break-word;'>0.4429 (0.00, 2.144)</td><td style='text-align: center; word-wrap: break-word;'>-0.0042 (0.84, 2.158)</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>ACCTS_REC/ACCTS_PAY</td><td style='text-align: center; word-wrap: break-word;'>-0.007 (0.74, 2.321)</td><td style='text-align: center; word-wrap: break-word;'>0.0382 (0.07, 2.321)</td><td style='text-align: center; word-wrap: break-word;'>-0.0024 (0.90, 2.185)</td><td style='text-align: center; word-wrap: break-word;'>-0.0206 (0.32, 2.321)</td><td style='text-align: center; word-wrap: break-word;'>0.0207 (0.32, 2.313)</td><td style='text-align: center; word-wrap: break-word;'>-0.0147 (0.48, 2.321)</td><td style='text-align: center; word-wrap: break-word;'>0.0264 (0.27, 1.718)</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DISAPPEARED_BY_1937</td><td style='text-align: center; word-wrap: break-word;'>-0.1282 (0.00, 2.024)</td><td style='text-align: center; word-wrap: break-word;'>0.2005 (0.00, 3.024)</td><td style='text-align: center; word-wrap: break-word;'>0.0266 (0.16, 2.820)</td><td style='text-align: center; word-wrap: break-word;'>0.0353 (0.05, 3.024)</td><td style='text-align: center; word-wrap: break-word;'>-0.0918 (0.00, 2.992)</td><td style='text-align: center; word-wrap: break-word;'>-0.0822 (0.00, 3.024)</td><td style='text-align: center; word-wrap: break-word;'>-0.1501 (0.00, 2.158)</td><td style='text-align: center; word-wrap: break-word;'>-0.0224 (0.28, 2.321)</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr></table>

for identification later in the article. We do not observe a significant correlation between connections and 1928 financial leverage and observe only a weak correlation with cash holdings, suggesting that network measures do not proxy for better precrisis access to capital markets.

### III. Network Connections and Firm Survival

The null hypothesis of our tests is that director and executive network ties to other firms do not affect the likelihood of firm failure during the Depression. Alternatively, the value of information that is available through network ties could be high at the time of a negative economic shock, when uncertainty is high. If so, network ties could increase survival odds, for example, by easing access to finance among (unexpectedly) financially constrained firms.

#### A. Baseline Regressions

Our initial approach to identifying the effect of network connections on firm survival is to employ a strategy similar in spirit to Opler and Titman (1994). We exploit a sudden and unexpected shock, the financial market crash of 1929, and compare survival rates among firms with many network ties to other firms with the survival rates of firms that have few network ties to other firms prior to the shock. Our identifying assumption is that we can treat firms' preexisting network ties as exogenous with respect to the shock. Thus, we essentially compare differences in responses across firms that happened to have more and fewer network ties at the time of the shock. Because the market crash in 1929 is an unanticipated event, the assumption that firms did not endogenously form network links prior to the shock anticipating that they would mitigate its negative impacts is plausible (i.e., reverse causality is not a major concern).

As a starting point, we present visual evidence of the relation between network connections and failure. In Figure 1, we graph the network of industrial firms in 1928. Each vertex on the graph represents a firm; firms that failed by 1937 are colored red and firms that survived are green. We exclude firms with no connections from the figure. Toward the center of the graph, we observe a dense cluster of green dots. Red dots (or failing firms) become more common as we move toward the perimeter of the figure. Moreover, failure rates among isolated firms (excluded from the picture) are more than 10 percentage points higher than they are among firms with at least one connection. This basic pattern between network connections and firm survival is statistically significant if we estimate it within a simple univariate regression.

The main threat to identification is that network ties are correlated with an omitted factor that also predicts survival rates in response to the shock. Our first approach to address this concern is to saturate a regression model with fixed effects and controls. In the remainder of the section, we provide additional analysis to bolster the causal interpretation.

To begin, we estimate the following linear probability model:

 $$ Y_{i1938}=\beta_{0}+\beta_{1}CONNECTIONS_{i1928}+X^{\prime}_{i1928}\beta_{2}+\varepsilon_{i1928}, $$ 

where i indexes the firm, Y is an indicator variable that takes the value 1 if a firm in our 1928 sample fails before 1937, CONNECTIONS is the measure of network ties

## FIGURE 1 Director Network

Figure 1 presents a graphical representation of the network of directors and executives in the sample of industrial companies from the 1928 Moody's Industrial manual. Subsidiaries and foreign companies are excluded from the network. The diagram does not include 746 firms that do not have any connections to other firms, though they are included in the analysis. The representation is an energy diagram created using the 2D Fruchterman–Reingold algorithm. Colors indicate firms that survived until 1937 (green) and firms that did not (red).

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//e56af164-2d96-421f-9f4e-ef8ee6bdcbe3/markdown_2/imgs/img_in_image_box_123_269_764_594.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-09T02%3A51%3A28Z%2F-1%2F%2Fec496710d73aa24007de0a52bccf6c9b6c24db27840e69983eae3447cbead07e" alt="Image" width="72%" /></div>


to other firms, and X is a vector of control variables. In all of our regressions, we include the natural logarithm of the number of directors on the board. This control captures both the mechanical tendency for larger boards to have more connections and any link between board size and effectiveness (Yermack (1996)). We also control for other factors that could affect survival probability and correlate with the network links of firms' executives and directors: firm size (measured by the natural logarithm of total assets), firm leverage (measured as total debt scaled by total assets), firm cash holdings (measured as cash plus marketable securities scaled by total assets), and an indicator that takes the value 1 if the firm is private. In some specifications, we also include industry fixed effects and fixed effects for all of the states in which firms have offices. We correct standard errors for heteroscedasticity across firms. $ ^{13} $ In the Supplementary Material, we demonstrate the robustness of our results to estimating the effects within a Cox proportional hazard model that explicitly accounts for variation in the timing of failure across firms within the 1928 to 1937 window.

We report the results of estimating equation (1) in Table 3. In column 1, we use a continuous measure of CONNECTIONS, the natural logarithm of one plus  $ TOTAL\_CONNECTIONS $. $ ^{14} $ We confirm a negative and significant correlation

##### TABLE 3

##### Network Connections and Firm Failure

Coefficient estimates in Table 3 are from OLS regressions on the sample of firms from the 1928 Moody's Industrial manual, excluding foreign firms and subsidiaries. The dependent variable is DISAPPEARED_BY_1937, an indicator variable that takes the value 1 if the firm exits by 1937. TOTAL_CONNECTIONS is the sum of connections to other firms in the sample via shared directors or managers. TOTAL_CONNECTIONS > MEDIAN is an indicator variable equal to 1 for firms that have a value of TOTAL_CONNECTIONS greater than the sample median. TOTAL_CONNECTIONS_QUARTILE_2 (3,4) is an indicator variable equal to 1 for firms that have a value of TOTAL_CONNECTIONS in the sample 2nd (3rd/4th) quartile. PRIVATE is an indicator variable equal to 1 for firms without publicly traded equity. TOTAL_ASSETS, DEBT/ASSETS, and CASH/ASSETS are winsorized at the 1% level. Standard errors that are robust to heteroscedasticity are reported in parentheses. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>6</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(\text{TOTAL\_ASSETS}) $</td><td style='text-align: center; word-wrap: break-word;'>-0.062*** (0.006)</td><td style='text-align: center; word-wrap: break-word;'>-0.062*** (0.006)</td><td style='text-align: center; word-wrap: break-word;'>-0.065*** (0.006)</td><td style='text-align: center; word-wrap: break-word;'>-0.062*** (0.007)</td><td style='text-align: center; word-wrap: break-word;'>-0.063*** (0.007)</td><td style='text-align: center; word-wrap: break-word;'>-0.065*** (0.007)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>0.071*** (0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.071*** (0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.070*** (0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.074*** (0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.073*** (0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.074*** (0.016)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>0.063 (0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.062 (0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.064 (0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.085 (0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.084 (0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.083 (0.056)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>-0.307*** (0.071)</td><td style='text-align: center; word-wrap: break-word;'>-0.308*** (0.071)</td><td style='text-align: center; word-wrap: break-word;'>-0.314*** (0.071)</td><td style='text-align: center; word-wrap: break-word;'>-0.269*** (0.077)</td><td style='text-align: center; word-wrap: break-word;'>-0.270*** (0.077)</td><td style='text-align: center; word-wrap: break-word;'>-0.276*** (0.077)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{NUMBER\_OF\_DIRECTORS}) $</td><td style='text-align: center; word-wrap: break-word;'>-0.043* (0.025)</td><td style='text-align: center; word-wrap: break-word;'>-0.043* (0.024)</td><td style='text-align: center; word-wrap: break-word;'>-0.054** (0.025)</td><td style='text-align: center; word-wrap: break-word;'>-0.048* (0.026)</td><td style='text-align: center; word-wrap: break-word;'>-0.050* (0.026)</td><td style='text-align: center; word-wrap: break-word;'>-0.061** (0.025)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{TOTAL\_CONNECTIONS}) $</td><td style='text-align: center; word-wrap: break-word;'>-0.013* (0.007)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.014* (0.008)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS &gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.034** (0.015)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.035** (0.016)</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS\_QUARTILE\_2</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.029 (0.021)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.034 (0.022)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS\_QUARTILE\_3</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.069*** (0.020)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.068*** (0.021)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS\_QUARTILE\_4</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.023 (0.021)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.027 (0.023)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Industry fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>State fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R $ ^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.088</td><td style='text-align: center; word-wrap: break-word;'>0.088</td><td style='text-align: center; word-wrap: break-word;'>0.090</td><td style='text-align: center; word-wrap: break-word;'>0.098</td><td style='text-align: center; word-wrap: break-word;'>0.099</td><td style='text-align: center; word-wrap: break-word;'>0.100</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>No. of obs.</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td></tr></table>

between network ties and the likelihood of firm failure (p-value = 0.078). Economically, a 1-standard-deviation increase in network ties predicts a decrease in the likelihood of failure by roughly 1.5 percentage points, a 7.5% decrease from the sample average of 20%. Among the control variables, we find that smaller firms, private firms, and firms with smaller cash stocks are significantly more likely to fail. Though we do not find a statistically significant relation between debt levels and failure, the relation is positive. Moreover, we recover a positive and strongly statistically significant relation if we exclude the cash control. Interestingly, we find that firms with larger boards weather the shock better than firms with smaller boards. In more recent data, Yermack (1996) finds evidence that firms with smaller boards perform better than firms with larger boards. The apparent reversal of the result in our sample is consistent with constraints in the director market that prevent firms from choosing boards of optimal size.

In column 2 of Table 3, we measure CONNECTIONS using a binary indicator that equals 1 for firms with a value of  $ TOTAL\_CONNECTIONS $ greater than the sample median. This approach is less parametric and also more robust to the presence of measurement error in  $ TOTAL\_CONNECTIONS $. Using this

alternative measure, we find a larger effect of network ties on the odds of firm survival. Here, a firm with more network ties than the median firm has a 3.4 percentage point smaller likelihood of failure (p-value = 0.022), a 17% decrease from the baseline failure probability. In column 3, we further saturate the model with indicators for firms in the second, third, and fourth quartiles of the distribution of TOTAL_CONNECTIONS. We find a negative, but insignificant 2.9 percentage point decrease in the likelihood of failure moving from the first quartile (baseline group) to the second. There is an additional 4 percentage point decrease moving to the third quartile, resulting in an overall 6.9 percentage point lower rate of failure in this quartile compared to the baseline, which is significant at the 1% level. The effect of network ties declines moving to the fourth quartile, though the effect in this quartile relative to the baseline is similar in magnitude to the effect in the second quartile. In Section III.D, we will find that there is strong heterogeneity in the effect of networks in the cross section. The lack of power in the fourth quartile here appears to be due to low representation of the types of firms in which connections matter the most: small, private, rural, and cash-poor.

Finally, in columns 4–6 of Table 3, we report the results of re-estimating the specifications from the first three columns of the table, but adding industry and state fixed effects as additional controls. The fixed effects capture omitted variation at the industry or state level that might correlate with network ties and also predict better performance following the shock. For example, firms located in states with larger populations might both have more network ties and weather the financial shock better. Because our data set is one cross section measured at a single point in time, the fixed effects capture industry and state-level factors that are time invariant and that would vary over time outside our sample. We find that these controls have little effect on our estimates and, if anything, strengthen their significance in some specifications.

A potential confounding factor is the quality of the firm at the time of the shock. Connections could correlate positively with firm quality and this underlying quality, rather than connections themselves, could predict higher survival during the Depression. Alternatively, weaker firms could seek out connections with other firms more aggressively, to the extent that connections increase value, causing us to understate the effect of connections on survival if we do not account for differences in firm quality. We do not include a direct control for performance in our baseline specification because we do not observe the required income statement information for roughly 30% of our sample firms. However, as a robustness check, we replicate Table 3, but include the ratio of net income to assets as an additional control. Despite the noise in the measure, we find that higher profitability strongly increases survival odds, both economically and statistically. But, importantly, the estimated effect of connections is largely unaffected (and, if anything, slightly stronger). We also perform several additional robustness checks. We include controls for firm age and for director expertise. We also control for county-level variation in government policy responses to the crisis, and we use major city fixed effects to control for local agglomeration effects. None of these additional factors can explain the effect of connections we estimate in Table 3. Full results are provided in the Supplementary Material.

#### B. Local Severity of the Great Depression and the Value of Network Connections

Our baseline strategy in Section III.A identifies the effect of network connections on firm survival using a single cross section of 10-year failure rates following the 1929 financial shock. Despite our control for performance, it is possible that more connected firms are less likely to fail because they differ from less connected firms on some other dimension of firm quality. Moreover, given our focus on a single cross section, the estimated network effect could reflect those differences in quality rather than differential responses to a common shock. If so, our evidence could allow a reverse causality interpretation: Directors may prefer to accept positions at companies that they believe are more likely to survive than at companies that are likely to fail. To confirm the importance of the shock itself and thereby address the concern, we test whether the effect of network connections is stronger in localities in which the impact of the disruptions caused by the Great Depression was more severe. The severity of the shock must not be positively correlated with the unobserved quality of local firms for our approach to be valid.

To implement this identification strategy, we consider variation in the severity of the financial crisis that is due to variation in the county-level rate of bank suspensions during the heart of the Depression. Following Calomiris and Mason (2003b) and Nanda and Nicholas (2014), we use data from the Federal Deposit Insurance Corporation (FDIC), which provides county-level annual reports on active and suspended banks and their deposits from 1920 to 1936. $ ^{15} $ Because the peak of bank runs and failures occurred between the summer of 1929 and winter of 1933 (Bernanke (1983), Calomiris and Mason (2003b), Richardson (2007), (2008), and Mitchener and Richardson (2019)), we focus on suspensions that occurred during the 1930 to 1933 window in our analysis. Prior to the Depression, bank loans were a primary source of working capital for the industrial sector (Currie (1931), Reifer, Friday, Lichtenstein, and Riddle (1937)). Thus, greater local failure rates are a reasonable proxy for differences in the intensity of the financial shock across firms. Consistent with this view, Nanda and Nicholas ((2014), p. 276) note that “Ford Motor Company provided approximately 12 million in loans to local banks to avert the crisis.” On the other hand, it is unlikely that local bank failure rates positively correlate with the locations of ex ante higher quality firms (i.e., firms that are more likely to survive independently from network ties). If anything, banks located in areas surrounded by stronger firms might be less likely to fail.

We measure the county-level bank failure rate using total bank deposits in the county that were held in banks that were suspended between 1930 and 1933 as a fraction of county-level bank deposits in 1929. For each firm, we match county bank failure rates to the locations in which the firm has offices, taking the minimum for firms with offices in multiple counties. We then estimate equation (1) including the local bank failure rate and its interaction with our network measures as additional independent variables. We estimate versions of all of the specifications from

<div style="text-align: center;"><div style="text-align: center;">TABLE 4</div> </div>


##### Network Connections and Firm Failure by Local Bank Distress

Coefficient estimates in Table 4 are from OLS regressions on the sample of firms from the 1928 Moody's Industrial manual, excluding foreign firms and subsidiaries. The dependent variable is DISAPPEARED_BY_1937, an indicator variable that takes the value 1 if the firm exits by 1937. TOTAL_CONNECTIONS is the sum of connections to other firms in the sample via shared directors or managers. TOTAL_CONNECTIONS > MEDIAN is an indicator variable equal to 1 for firms that have a value of TOTAL_CONNECTIONS greater than the sample median. TOTAL_CONNECTIONS_QUARTILE_2 (3,4) is an indicator variable equal to 1 for firms that have a value of TOTAL_CONNECTIONS in the sample 2nd (3rd/4th) quartile. DEP_SUSP is the minimum fraction of county bank deposits as of 1929 in banks that were suspended from 1930 through 1933 among the counties in which the firm has offices. PRIVATE is an indicator variable equal to 1 for firms without publicly traded equity. TOTAL_ASSETS, DEBT/ASSETS, and CASH/ASSETS are winsorized at the 1% level. Standard errors that are robust to heteroscedasticity are reported in parentheses. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>6</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(\text{TOTAL\_ASSETS}) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.065^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.065^{***}(0.006) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.067^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.065^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.065^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.067^{***}(0.007) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>$ 0.071^{***}(0.015) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.071^{***}(0.015) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.068^{***}(0.015) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.074^{***}(0.017) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.074^{***}(0.017) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.073^{***}(0.017) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>0.052 (0.053)</td><td style='text-align: center; word-wrap: break-word;'>0.052 (0.053)</td><td style='text-align: center; word-wrap: break-word;'>0.051 (0.053)</td><td style='text-align: center; word-wrap: break-word;'>0.075 (0.057)</td><td style='text-align: center; word-wrap: break-word;'>0.075 (0.057)</td><td style='text-align: center; word-wrap: break-word;'>0.074 (0.057)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>$ -0.324^{***}(0.073) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.324^{***}(0.073) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.332^{***}(0.072) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.285^{***}(0.078) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.286^{***}(0.078) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.293^{***}(0.078) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{NUMBER\_OF\_DIRECTORS}) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.053^{**}(0.026) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.051^{**}(0.025) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.055^{**}(0.026) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.057^{**}(0.027) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.058^{**}(0.027) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.060^{**}(0.027) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{TOTAL\_CONNECTIONS}) $</td><td style='text-align: center; word-wrap: break-word;'>0.001 (0.009)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.001 (0.009)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS &gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.016 (0.019)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.014 (0.020)</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS\_QUARTILE\_2</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.010 (0.028)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.017 (0.030)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS\_QUARTILE\_3</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.058^{**}(0.025) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.052^{*}(0.027) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS\_QUARTILE\_4</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.018 (0.026)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.012 (0.028)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEP\_SUSP</td><td style='text-align: center; word-wrap: break-word;'>0.103 (0.087)</td><td style='text-align: center; word-wrap: break-word;'>0.005 (0.064)</td><td style='text-align: center; word-wrap: break-word;'>0.071 (0.094)</td><td style='text-align: center; word-wrap: break-word;'>$ 0.247^{**}(0.106) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.166^{**}(0.083) $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.220^{**}(0.112) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEP\_SUSP  $ \times $  $ \ln(1 + \text{TOTAL\_CONNECTIONS}) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.105^{**}(0.042) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.095^{**}(0.047) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEP\_SUSP  $ \times $  $ \text{TOTAL\_CONNECTIONS} &gt; \text{MEDIAN} $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.141^{*}(0.082) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.136 (0.089)</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEP\_SUSP  $ \times $  $ \text{TOTAL\_CONNECTIONS\_QUARTILE\_2} $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.128 (0.128)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.118 (0.137)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEP\_SUSP  $ \times $  $ \text{TOTAL\_CONNECTIONS\_QUARTILE\_3} $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.111 (0.115)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.118 (0.124)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEP\_SUSP  $ \times $  $ \text{TOTAL\_CONNECTIONS\_QUARTILE\_4} $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.290^{**}(0.122) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.268^{**}(0.136) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Industry fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>State fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R $ ^2 $</td><td style='text-align: center; word-wrap: break-word;'>0.092</td><td style='text-align: center; word-wrap: break-word;'>0.092</td><td style='text-align: center; word-wrap: break-word;'>0.095</td><td style='text-align: center; word-wrap: break-word;'>0.100</td><td style='text-align: center; word-wrap: break-word;'>0.100</td><td style='text-align: center; word-wrap: break-word;'>0.102</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>No. of obs.</td><td style='text-align: center; word-wrap: break-word;'>2,872</td><td style='text-align: center; word-wrap: break-word;'>2,872</td><td style='text-align: center; word-wrap: break-word;'>2,872</td><td style='text-align: center; word-wrap: break-word;'>2,627</td><td style='text-align: center; word-wrap: break-word;'>2,627</td><td style='text-align: center; word-wrap: break-word;'>2,627</td></tr></table>

Table 3 and report the results in Table 4. Consistent with the preceding discussion, we find that greater local bank distress is associated with a higher likelihood of firm failure when we include state and industry fixed effects (columns 4–6). We also confirm that the effect of network connections on failure probability is larger in magnitude where a larger fraction of local deposits is held in banks that are in distress. The estimates of the interactive effect of our network connection measures with the bank distress variable are negative in all cases and appear to increase with the number of connections. For example, in columns 3 and 6, we estimate interactions of -0.29 and -0.27, respectively, with the indicator for connections in the top quartile of the distribution (both statistically significant at the 5% level), compared

to interactions of -0.13 and -0.12 for firms with numbers of connections in the second quartile. At the mean of the distress variable (0.13), these estimates imply a decline in the likelihood of failure of roughly 4 percentage points among firms with network ties in the top quartile. However, they also suggest large heterogeneity in the effect of connections. For example, the most distressed counties have bank suspension rates greater than 90%. In such counties, the column 6 estimates would imply a roughly 26 percentage point lower failure rate among the most connected firms. Overall, the results provide additional evidence in support of a causal interpretation of the relation between network ties and firm failure and, in particular, confirm the relevance of the financial shock itself for the estimated differences.

#### C. Instrumental Variables Regressions

One way to address directly the concern that network ties correlate with an omitted factor that positively predicts firm survival is to instrument for network connections. Our IV strategy relies on two empirical observations. First, director markets were relatively segmented in 1928 (e.g., our sample predates the widespread introduction of commercial air travel in the United States). In the Supplementary Material, we demonstrate this segmentation at the regional level within our sample. This pattern implies that most of the demand for directors' services in other firms will be local and that there can be substantial differences in this demand across localities at any given point in time. Second, firms are more likely to choose directors from firms within their own industries. $ ^{16} $ This preference implies that firms located in states in which the number of local directors in the industry is small are likely to have fewer network connections because of a lower local demand for their directors' services. Geographic segmentation in turn implies that the lower local demand is not substituted one-for-one by heightened out-of-state demand.

One reason why there could be low local demand for a director's services within her industry is because the local market is small. However, this source of variation is likely to correlate directly with the chances of survival in a crisis. We instead construct our instrument to exploit variation in local demand that is due to variation in the sizes of the boards of local firms in the industry. We define our instrument LOW as an indicator variable that takes the value 1 if the fraction of the directors in the state(s) in which the firm operate(s) that are in the firm's industry is in the bottom third of the distribution. $ ^{17} $ We isolate variation that comes from differences in average board sizes by directly controlling for the number of firms in the state–industry pair (both continuously and as an indicator that, like LOW, takes the value of 1 if the number of firms in the state–industry pair is in the bottom

third of the distribution). $ ^{18} $ Moreover, we control for the overall number of directors in the state (again continuously and as an indicator for firms located in states in the upper third of the distribution). $ ^{19} $ These controls ensure that it is only the ratio of the number of directors to firms in a state–industry pair that identifies our results. Variation in the total number of directors, which is captured by the additional controls, could correlate with local market vibrancy. Finally, we add an indicator for firms with board sizes in the lower third of the distribution. The firm’s own board size could correlate with the local average board size and has a weak negative correlation with firm failure (Table 3). The added control prevents the instrument from absorbing nonlinearities in this effect. Ultimately, our identification rests on the assumption that LOW is excludable from equation (1). Failure would require differences between the average board sizes of firms within the same industry across different states, conditional on the full set of covariates in our regressions, to correlate with an omitted factor that predicts survival.

We present the results of implementing our IV strategy in Table 5. Because the instrument varies both within-state and within-industry, we can use it to identify the effect of connections while continuing to absorb (separately) all industry- and state-level variation with fixed effects. In column 1, we report the results from the reduced form regression of the indicator for firm failure on the instrument LOW and our set of controls. We find that the instrument LOW has a positive and significant effect on the likelihood of failure. Firms located in areas in which their directors have less outside demand for their services are more likely to fail, even controlling for the size of their local product markets. As discussed previously, the most obvious threat to the exclusion restriction centers around correlation between LOW and some notion of local market vibrancy. Importantly, none of the direct controls that we add to capture local market conditions (such as the numbers of firms or directors in the state-industry pair) have any significant explanatory power for the likelihood of failure (even if we exclude LOW as an explanatory variable), casting significant doubt on the ability of this alternative story to explain our findings. Our results are also robust to the inclusion of major city fixed effects, as defined in Section III.A, as additional controls. Moreover, we do not find that market conditions in neighboring states (e.g., number of firms or directors in the industry) have any significant explanatory power for firm failure, consistent with the presence of the type of market segmentation that we use to motivate our strategy. $ ^{20} $

# TABLE 5

# Network Connections and Firm Failure: IV Regressions

Coefficient estimates in column 1 of Table 5 are from OLS regressions on the sample of firms from the 1928 Moody's Industrial manual, excluding foreign firms and subsidiaries. Coefficient estimates in columns 2 and 3 and, separately, 4 and 5 are from two-stage least-squares systems of regressions. The dependent variable in columns 1, 3, and 5 is DISAPPEARED. BY_1937, an indicator variable that takes the value 1 if the firm exits by 1937. The dependent variable in column 2 is the natural logarithm of one plus TOTAL_CONNECTIONS. TOTAL_CONNECTIONS is the sum of connections to other firms in the sample via shared directors or managers. The dependent variable in column 4 is an indicator variable equal to 1 if the firm has a value of TOTAL_CONNECTIONS greater than the sample median. PRIVATE is an indicator variable equal to 1 for firms without publicly traded equity. TOTAL_ASSETS, DEBT/ASSETS, and CASH/ASSETS are winsorized at the 1% level. SMALL_BOARD is an indicator variable equal to 1 if the firm's number of directors is less than the sample 33rd percentile. FEW_LOCAL_FIRMS is an indicator variable equal to 1 if the firm's number of firms in the firm's state-industry pair is less than the sample 33rd percentile. LOCAL_FIRMS is the number of firms in the firm's state-industry pair. MANY_LOCAL_DIRECTORS is an indicator equal to 1 if the number of directors in the firm's state-industry pair is above the sample 66th percentile. LOCAL_DIRECTORS is the number of directors in the firm's state-industry pair. The instrument LOW is an indicator variable equal to 1 if the number of directors in the firm's industry-state pair as a fraction of the number of directors in the state is less than the sample 33rd percentile. Standard errors that are robust to heteroscedasticity are reported in parentheses. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2"></td><td rowspan="2">Reduced Form 1</td><td rowspan="2">First Stage 2</td><td rowspan="2">Second Stage 3</td><td rowspan="2">First Stage 4</td><td rowspan="2">Second Stage 5</td></tr><tr></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(\text{TOTAL\_ASSETS}) $</td><td style='text-align: center; word-wrap: break-word;'>-0.064*** (0.007)</td><td style='text-align: center; word-wrap: break-word;'>0.151*** (0.018)</td><td style='text-align: center; word-wrap: break-word;'>-0.007 (0.031)</td><td style='text-align: center; word-wrap: break-word;'>0.050*** (0.008)</td><td style='text-align: center; word-wrap: break-word;'>-0.040*** (0.013)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>0.079*** (0.017)</td><td style='text-align: center; word-wrap: break-word;'>-0.202*** (0.042)</td><td style='text-align: center; word-wrap: break-word;'>0.002 (0.046)</td><td style='text-align: center; word-wrap: break-word;'>-0.085*** (0.021)</td><td style='text-align: center; word-wrap: break-word;'>0.037 (0.027)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>0.070 (0.057)</td><td style='text-align: center; word-wrap: break-word;'>0.271** (0.129)</td><td style='text-align: center; word-wrap: break-word;'>0.172* (0.092)</td><td style='text-align: center; word-wrap: break-word;'>0.090 (0.064)</td><td style='text-align: center; word-wrap: break-word;'>0.114* (0.066)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>-0.276*** (0.078)</td><td style='text-align: center; word-wrap: break-word;'>0.192 (0.181)</td><td style='text-align: center; word-wrap: break-word;'>-0.204* (0.110)</td><td style='text-align: center; word-wrap: break-word;'>0.043 (0.087)</td><td style='text-align: center; word-wrap: break-word;'>-0.256*** (0.087)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{NUMBER\_OF\_DIRECTORS}) $</td><td style='text-align: center; word-wrap: break-word;'>-0.044 (0.036)</td><td style='text-align: center; word-wrap: break-word;'>1.035*** (0.082)</td><td style='text-align: center; word-wrap: break-word;'>0.348* (0.210)</td><td style='text-align: center; word-wrap: break-word;'>0.340*** (0.039)</td><td style='text-align: center; word-wrap: break-word;'>0.121 (0.082)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>SMALL_BOARD</td><td style='text-align: center; word-wrap: break-word;'>0.023 (0.024)</td><td style='text-align: center; word-wrap: break-word;'>-0.078 (0.057)</td><td style='text-align: center; word-wrap: break-word;'>-0.006 (0.035)</td><td style='text-align: center; word-wrap: break-word;'>-0.075*** (0.029)</td><td style='text-align: center; word-wrap: break-word;'>-0.013 (0.032)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{LOCAL\_FIRMS}) $</td><td style='text-align: center; word-wrap: break-word;'>0.003 (0.018)</td><td style='text-align: center; word-wrap: break-word;'>0.012 (0.042)</td><td style='text-align: center; word-wrap: break-word;'>0.007 (0.024)</td><td style='text-align: center; word-wrap: break-word;'>-0.008 (0.020)</td><td style='text-align: center; word-wrap: break-word;'>-0.001 (0.019)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>FEW_LOCAL_FIRMS</td><td style='text-align: center; word-wrap: break-word;'>0.004 (0.030)</td><td style='text-align: center; word-wrap: break-word;'>-0.071 (0.068)</td><td style='text-align: center; word-wrap: break-word;'>-0.023 (0.040)</td><td style='text-align: center; word-wrap: break-word;'>-0.008 (0.033)</td><td style='text-align: center; word-wrap: break-word;'>0.000 (0.033)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{LOCAL\_DIRECTORS}) $</td><td style='text-align: center; word-wrap: break-word;'>0.01 (0.022)</td><td style='text-align: center; word-wrap: break-word;'>0.107* (0.058)</td><td style='text-align: center; word-wrap: break-word;'>0.050 (0.032)</td><td style='text-align: center; word-wrap: break-word;'>0.073*** (0.028)</td><td style='text-align: center; word-wrap: break-word;'>0.046* (0.026)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>MANY_LOCAL_DIRECTORS</td><td style='text-align: center; word-wrap: break-word;'>0.040 (0.066)</td><td style='text-align: center; word-wrap: break-word;'>-0.013 (0.131)</td><td style='text-align: center; word-wrap: break-word;'>0.035 (0.083)</td><td style='text-align: center; word-wrap: break-word;'>0.070 (0.071)</td><td style='text-align: center; word-wrap: break-word;'>0.074 (0.076)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>LOW</td><td style='text-align: center; word-wrap: break-word;'>0.060** (0.024)</td><td style='text-align: center; word-wrap: break-word;'>-0.158*** (0.055)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.123*** (0.027)</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{TOTAL\_CONNECTIONS}) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.379* (0.198)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL_CONNECTIONS &gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.486** (0.217)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Industry fixed effects</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>State fixed effects</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R²</td><td style='text-align: center; word-wrap: break-word;'>0.100</td><td style='text-align: center; word-wrap: break-word;'>0.359</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.251</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>No. of obs.</td><td style='text-align: center; word-wrap: break-word;'>2,681</td><td style='text-align: center; word-wrap: break-word;'>2,681</td><td style='text-align: center; word-wrap: break-word;'>2,681</td><td style='text-align: center; word-wrap: break-word;'>2,681</td><td style='text-align: center; word-wrap: break-word;'>2,681</td></tr></table>

In column 2 of Table 5, we report the first-stage regression for our instrumental variables strategy using the natural logarithm of  $ TOTAL\_CONNECTIONS $ as the endogenous variable in equation (1). As predicted, we find a strong negative partial correlation of LOW with network ties after including the controls. The instrument is strongly statistically significant (p-value < 0.01); however, the first-stage F-statistic of 8.049 lies between the Stock and Yogo (2005) critical values for a test of 15% and 20% size, suggesting some caution in assessing the strength of the instrument. In column 3, we report estimates from the second-stage regression. We find that

the instrumented effect of TOTAL_CONNECTIONS is negative and statistically significant (p-value = 0.056). In columns 4 and 5, we report the results from a similar two-stage least-squares system in which the endogenous measure of network ties is an indicator variable that equals 1 for firms with a value of TOTAL_CONNECTIONS greater than the sample median. We again find that the instrument significantly predicts TOTAL_CONNECTIONS in the first stage (p-value < 0.001) and that the instrumented effect of network ties on the likelihood of firm failure is negative and significant (p-value = 0.025). Here, the first-stage F-statistic of 20.278 exceeds the Stock and Yogo (2005) threshold for a test of 10% size, suggesting that the instrument is strong.

It is noteworthy that the estimated effect of network ties is substantially larger in magnitude in these regressions than in the baseline regressions in Table 3. One possibility, consistent with the negative correlation between net income and network ties in our sample, is that weaker firms are more likely to seek network ties so that endogeneity attenuates estimates of the network effect in OLS specifications. Hermalin and Weisbach (2003) make a similar argument in the context of board independence. We also observed in Section III.B that there is heterogeneity in the effect of networks in the sample and provide additional evidence of this heterogeneity in Section III.D. Another possibility, then, is that the local treatment effect measured by LOW applies to a subset of firms in which the effect of network ties is larger than the population effect. We provide additional tests to distinguish these possible explanations from weakness of the instrument in the Supplementary Material. Ultimately, given the results from Section III.B and the remainder of the article, the causal interpretation of our results does not rest solely on the validity of the IV approach.

#### D. The Value of Network Connections for Firms of Different Types

Our results in Section III.B suggest that network ties contribute the most to firm survival where financial constraints are most likely to bind, suggesting a role for connections in easing the flow of financing to constrained firms. Moreover, network ties could facilitate the flow of information about firm or market conditions, leading to more effective adjustment to changing fundamentals. If so, network connections should have a stronger effect among firms that are otherwise more isolated from information flow. Given this discussion, we test whether network connections are more valuable to information-sensitive and financially constrained firms. By confirming the specific theoretical patterns predicted by a network effect, these tests can further bolster the causal interpretation of our baseline results. In particular, a potential omitted variable must be able to explain not only the simple positive relation between network links and survival, but also the interacted effects with measures of constraints.

In the 1920s, not only was travel between different geographic markets more difficult, modern forms of communication (such as the Internet) had not yet been introduced. Thus, we construct a measure of geographic isolation to capture variation in access to information. We define an indicator variable for rural firms that takes the value of 1 if the rural population in the counties in which the firm has

offices is greater than 60% $ ^{21} $. We also consider three measures of financial constraints. Most directly, we compare firms that have cash holdings scaled by assets that are above the median in 1928 to firms that have cash holdings below the sample median. Building on the literature on financing constraints, we also compare small to large firms, defining an indicator variable that splits the sample at the median value of total assets. Finally, we compare private to public firms. The final proxy is likely to capture financing constraints, but also opaqueness and inferior access to information.

In Table 6, we report the results from augmenting the linear probability model in equation (1) individually with each proxy for information sensitivity or financing constraints and its interaction with network ties. To measure network ties, we use the indicator variable that takes the value 1 if the firm has TOTAL_CONNECTIONS greater than the sample median. Focusing on columns 1–4, we find that each of the three measures of financial constraints (SMALL_FIRM, PRIVATE, and LOW_CASH) is a significant positive predictor of firm failure following the 1929 financial shock. Firms that we identify as financially constrained have a likelihood of failure that is larger by 7.6 to 10.8 percentage points. Turning to the interactions, in all cases we find a significant negative interaction with network ties. Economically, membership in the high connections subsample erases the effect of financial constraints on firm failure using all three measures (i.e., we cannot reject the hypothesis that the coefficient estimates on financial constraints and their interaction with connections sum to 0). We do not find that rural firms have a different likelihood of failure from firms located in urban counties (column 2). However, we find a significant negative interaction effect with network ties. Firms in rural areas in the high connections subsample have failure rates roughly 12 percentage points lower than other firms.

In columns 5–8 of Table 6, we repeat the regressions, but include state and industry fixed effects with little effect on the results. We also find similar patterns if we instrument for network ties, running separate estimations on subsamples defined by each proxy for constraints. In all cases, we find estimates that are larger in magnitude among firms we classify as constrained. In two cases (PRIVATE and LOW_CASH), we find significant instrumented effects of network ties only in the constrained subsample. Finally, we use firm age less than 5 years as an alternative measure of constraints. Though the estimates are economically and statistically weaker, we observe that younger firms tend to be more likely to fail and that network ties reduce the effect.

<div style="text-align: center;"><div style="text-align: center;">TABLE 6</div> </div>


##### Network Connections and Firm Failure by Firm Characteristics

Coefficient estimates in Table 6 are from OLS regressions on the sample of firms from the 1928 Moody's Industrial manual, excluding foreign firms and subsidiaries. The dependent variable is DISAPPEARED_BY_1937, an indicator variable that takes the value 1 if the firm exits by 1937. TOTAL_CONNECTIONS > MEDIAN is an indicator variable equal to 1 for firms that have a value of TOTAL_CONNECTIONS greater than the sample median, where TOTAL_CONNECTIONS is the sum of connections to other firms in the sample via shared directors or managers. PRIVATE is an indicator variable equal to 1 for firms without publicly traded equity. RURAL is an indicator variable equal to 1 for firms that have offices only in counties in which the rural population in 1930 is greater than 60%. LOW_CASH (SMALL_FIRM) is an indicator variable equal to 1 for firms that have CASH/ASSETS (TOTAL_ASSETS) less than the sample median. TOTAL_ASSETS, DEBT/ASSETS, and CASH/ASSETS are winsorized at the 1% level. Standard errors that are robust to heteroscedasticity are reported in parentheses. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>8</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(\text{TOTAL\_ASSETS}) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.064^{***}(0.006) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.064^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.061^{***}(0.006) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.050^{***}(0.008) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.063^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.067^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.062^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.051^{***}(0.009) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>0.108^{***}(0.021)</td><td style='text-align: center; word-wrap: break-word;'>0.067^{***}(0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.068^{***}(0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.071^{***}(0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.111^{***}(0.022)</td><td style='text-align: center; word-wrap: break-word;'>0.071^{***}(0.017)</td><td style='text-align: center; word-wrap: break-word;'>0.072^{***}(0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.074^{***}(0.016)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>0.055(0.051)</td><td style='text-align: center; word-wrap: break-word;'>0.054(0.054)</td><td style='text-align: center; word-wrap: break-word;'>0.055(0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.061(0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.077(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.077(0.058)</td><td style='text-align: center; word-wrap: break-word;'>0.080(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.083(0.056)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>$ -0.312^{***}(0.071) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.325^{***}(0.074) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.124(0.087) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.304^{***}(0.072) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.275^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.292^{***}(0.080) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.111(0.094) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.264^{***}(0.078) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{NUMBER\_OF\_DIRECTORS}) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.044^{*}(0.024) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.053^{**}(0.025) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.041^{*}(0.024) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.043^{*}(0.024) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.051^{**}(0.026) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.057^{**}(0.027) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.047^{*}(0.026) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.051^{**}(0.026) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS &gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'>0.011(0.018)</td><td style='text-align: center; word-wrap: break-word;'>$ -0.027^{*}(0.016) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.003(0.019) $</td><td style='text-align: center; word-wrap: break-word;'>0.002(0.017)</td><td style='text-align: center; word-wrap: break-word;'>0.010(0.020)</td><td style='text-align: center; word-wrap: break-word;'>$ -0.027(0.018) $</td><td style='text-align: center; word-wrap: break-word;'>0.000(0.020)</td><td style='text-align: center; word-wrap: break-word;'>0.005(0.019)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS &gt; MEDIAN \times PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>$ -0.079^{***}(0.027) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.079^{***}(0.029) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS &gt; MEDIAN \times RURAL</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.119^{**}(0.060) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.104^{*}(0.060) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>RURAL</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.036(0.044)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.030(0.047)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS &gt; MEDIAN \times LOW\_CASH</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.064^{**}(0.027) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.069^{**}(0.029) $</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>LOW\_CASH</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.087^{***}(0.023)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.083^{***}(0.025)</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS &gt; MEDIAN \times SMALL\_FIRM</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.073^{**}(0.028) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.082^{***}(0.031) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>SMALL\_FIRM</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.076^{***}(0.025)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.075^{***}(0.026)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Industry fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>State fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R^{2}</td><td style='text-align: center; word-wrap: break-word;'>0.090</td><td style='text-align: center; word-wrap: break-word;'>0.092</td><td style='text-align: center; word-wrap: break-word;'>0.092</td><td style='text-align: center; word-wrap: break-word;'>0.091</td><td style='text-align: center; word-wrap: break-word;'>0.101</td><td style='text-align: center; word-wrap: break-word;'>0.096</td><td style='text-align: center; word-wrap: break-word;'>0.102</td><td style='text-align: center; word-wrap: break-word;'>0.101</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>No. of obs.</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,792</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,554</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td></tr></table>

### IV. Economic Mechanisms

Director and executive network connections to other firms predict increased odds of survival through the Great Depression, particularly among firms that are likely to experience financial constraints at the time of the shock. Next, we provide additional analysis to identify the economic mechanisms through which connections aid industrial firms. By identifying additional patterns that an omitted variable must explain, but that follow from a causal link between networks and survival, we further address potential endogeneity of the network measures.

#### A. Trade Credit

One channel through which network ties could improve firms’ resilience during a financial crisis is by facilitating the extension of favorable trade credit

<div style="text-align: center;"><div style="text-align: center;">TABLE 7</div> </div>


##### Network Connections to Cash-Rich Firms and Firm Failure

Table 7 shows the relation between a firm's connections to cash-rich versus cash-poor firms and firm failure. Coefficient estimates are from OLS regressions on the sample of firms from the 1928 Moody's Industrial manual, excluding foreign firms and subsidiaries. The dependent variable is DISAPPEARED_BY_1937, an indicator variable that takes the value 1 if the firm exits by 1937. CASH_RICH_CONNECTIONS (CASH_POOR_CONNECTIONS) are TOTAL_CONNECTIONS to firms that are cash-rich (cash-poor). Cash-rich (cash-poor) firms are firms with CASH/ASSETS greater than (less than or equal to) the sample median. We do not count connections toward either total for cases in which shared directorship or management is observed but CASH/ASSETS in the connected firm is unobserved. PRIVATE is an indicator variable equal to 1 for firms without publicly traded equity. TOTAL_ASSETS, DEBT/ASSETS, and CASH/ASSETS are winsorized at the 1% level. Standard errors that are robust to heteroscedasticity are reported in parentheses. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>6</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(\text{TOTAL\_ASSETS}) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.062^{***}(0.006) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.064^{***}(0.006) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.063^{***}(0.006) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.063^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.064^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.063^{***}(0.007) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>0.067^{***}(0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.072^{***}(0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.067^{***}(0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.070^{***}(0.017)</td><td style='text-align: center; word-wrap: break-word;'>0.075^{***}(0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.071^{***}(0.016)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>0.062(0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.063(0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.062(0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.086(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.084(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.086(0.056)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>$ -0.304^{***}(0.071) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.311^{***}(0.071) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.303^{***}(0.071) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.271^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.273^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.270^{***}(0.077) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{NUMBER\_OF\_DIRECTORS}) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.041^{*}(0.024) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.052^{**}(0.024) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.042^{*}(0.024) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.048^{*}(0.025) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.059^{**}(0.025) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.049^{*}(0.026) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH\_RICH\_CONNECTIONS &gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'>$ -0.046^{***}(0.015) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.049^{***}(0.016) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.045^{***}(0.016) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.047^{***}(0.017) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH\_POOR\_CONNECTIONS &gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.015(0.015) $</td><td style='text-align: center; word-wrap: break-word;'>0.007(0.016)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.015(0.016) $</td><td style='text-align: center; word-wrap: break-word;'>0.005(0.017)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Industry fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>State fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R^{2}</td><td style='text-align: center; word-wrap: break-word;'>0.090</td><td style='text-align: center; word-wrap: break-word;'>0.087</td><td style='text-align: center; word-wrap: break-word;'>0.089</td><td style='text-align: center; word-wrap: break-word;'>0.100</td><td style='text-align: center; word-wrap: break-word;'>0.097</td><td style='text-align: center; word-wrap: break-word;'>0.099</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>No. of obs.</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td></tr></table>

terms between firms with customer–supplier relationships. Preexisting network connections can be a way to lower the information asymmetries that could otherwise make such lending excessively costly. In addition, a preexisting trading relationship between the borrowing and lending firms can increase the marginal benefit to the lender of providing financial assistance to avoid a costly search for new trading partners. Nanda and Nicholas (2014) document the dependence of the auto industry in Detroit on local banking during the 1930s. More generally, their evidence suggests that working capital from trading partners could be particularly important to small, financially constrained firms when local bank financing is scarce, consistent with our results in Section III.

To test for evidence of the trade credit channel in our data, we exploit variation in the financial conditions of the firm(s) to which sample firms are connected. To begin, we distinguish between connections to firms that are cash-rich (i.e., have cash holdings as a fraction of total assets that are higher than the sample median) and connections to firms that are cash-poor. In Table 7, we report the results from estimating equation (1) using separate variables to capture connections to cash-rich and cash-poor firms. Mirroring the specifications in Table 6, we compare the survival rates of firms with levels of each type of connection that are above and below the sample median. In column 1, we include connections to cash-rich firms as the independent variable of interest. We find that such connections have a strong negative effect on the likelihood of firm failure that is statistically significant at the 1% level. Economically, the effect is roughly 50% bigger than the effect of having

an above-median level of total connections on failure, as reported in column 2 of Table 3. In column 2, we report the results using connections to cash-poor firms to define the independent variable of interest. Here, instead we do not find any significant effect of connections on the likelihood of firm failure, though the effects of all other included independent variables are similar to the estimates in column 1. In column 3, we report estimates from a regression including both the measure of high connections to cash-rich and cash-poor firms. We again find a strong negative effect of connections to cash-rich firms on failure. The small negative effect of cash-poor connections we report in column 2 does not survive when we also include the measure of cash-rich connections, suggesting that it is an artifact of positive correlation between the two measures. In columns 4–6, we report the results from replicating the columns 1–3 regressions with the addition of state and industry fixed effects. As in prior tables, our results are largely unchanged.

Building on this evidence, we test whether the effect of connections to cash-rich firms on survival is particularly prominent among firms that we classify as financially constrained. We consider all three measures of financial constraints from Table 6: firms with low cash holdings, private firms, and small firms. We report the results of separately estimating the regression specification from column 6 of Table 7 (i.e., including both connections to cash-rich and cash-poor firms in equation (1) along with state and industry fixed effects) in the subsamples of financially constrained and unconstrained firms for each measure of constraints.

In columns 1 and 2 of Table 8, we report the results using firm cash holdings as the measure of financial constraints. In column 1, we find that connections to cash-rich firms indeed have a strong negative effect on the likelihood of firm failure among cash-poor (constrained) firms, but connections to cash-poor firms again do not have a significant effect. By contrast, we see in column 2 that neither type of connection has a significant effect on the likelihood of firm failure among cash-rich (unconstrained) firms. In columns 3 and 4, we report the results for private (constrained) and public (unconstrained) firms. And, in columns 5 and 6, we do the same for small (constrained) and large (unconstrained) firms. In both cases, we find the same pattern: Connections to cash-rich firms are a significant predictor of firm survival following the financial panic, but only among constrained firms. Connections to cash-poor firms never have a significant effect on the likelihood of firm failure. We do not observe a similar pattern if we split the sample into urban and rural firms, a split less obviously related to financial constraints.

Given the relation between enhanced survival among low-cash firms and the cash holdings of connected firms, we dig deeper into the role of working capital financing as a potential channel for the effect. Specifically, we test for direct evidence that it is connections to firms that report increased accounts receivable during the crisis years that correlate with reduced failure rates. To perform this test, we collect information on accounts receivable for each sample firm from the 1928 and 1934 Moody's manuals and compute log changes for each firm. $ ^{22} $

##### TABLE 8

##### Network Connections to Cash-Rich Firms and Firm Failure by Firm Type

Table 8 shows the relation between a firm's connections to cash-rich versus cash-poor firms and firm failure for different sub-samples of firms. The full sample is the sample of firms from the 1928 Moody's Industrial manual, excluding foreign firms and subsidiaries. In column 1 (2), we limit the sample to firms with LOW_CASH (HIGH_CASH) holdings, where HIGH_CASH (LOW_CASH) are firms with CASH/ASSETS ratios above (below) the sample median. In column 3 (4), we limit the sample to PRIVATE (PUBLIC) firms, where PRIVATE firms are firms without publicly traded equity. In column 5 (6), we limit the sample to SMALL (LARGE) firms, where SMALL (LARGE) firms are firms with TOTAL_ASSETS below (above) the sample median. Coefficient estimates are from OLS regressions. The dependent variable is DISAPPEARED_BY_1937, an indicator variable that takes the value 1 if the firm exits by 1937. CASH_RICH_CONNECTIONS (CASH_POOR_ CONNECTIONS) are TOTAL_CONNECTIONS to firms that are cash-rich (cash-poor). Cash-rich (cash-poor) firms are firms with CASH/ASSETS greater than (less than or equal to) the sample median. We do not count connections toward either total for cases in which shared directorship or management is observed but CASH/ASSETS in the connected firm is unobserved. PRIVATE is an indicator variable equal to 1 for firms without publicly traded equity. TOTAL_ASSETS, DEBT/ASSETS, and CASH/ASSETS are winsorized at the 1% level. Standard errors that are robust to heteroscedasticity are reported in parentheses. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>LOW_CASH</td><td style='text-align: center; word-wrap: break-word;'>HIGH_CASH</td><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>PUBLIC</td><td style='text-align: center; word-wrap: break-word;'>SMALL</td><td style='text-align: center; word-wrap: break-word;'>LARGE</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>6</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>In(TOTAL_ASSETS)</td><td style='text-align: center; word-wrap: break-word;'>-0.073*** $ (0.012) $</td><td style='text-align: center; word-wrap: break-word;'>-0.050*** $ (0.009) $</td><td style='text-align: center; word-wrap: break-word;'>-0.091*** $ (0.012) $</td><td style='text-align: center; word-wrap: break-word;'>-0.051*** $ (0.008) $</td><td style='text-align: center; word-wrap: break-word;'>-0.120*** $ (0.025) $</td><td style='text-align: center; word-wrap: break-word;'>-0.034*** $ (0.008) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>0.068*** $ (0.026) $</td><td style='text-align: center; word-wrap: break-word;'>0.057*** $ (0.021) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.092*** $ (0.029) $</td><td style='text-align: center; word-wrap: break-word;'>0.067*** $ (0.019) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>0.047 $ (0.081) $</td><td style='text-align: center; word-wrap: break-word;'>0.138* $ (0.080) $</td><td style='text-align: center; word-wrap: break-word;'>0.047 $ (0.081) $</td><td style='text-align: center; word-wrap: break-word;'>0.102 $ (0.074) $</td><td style='text-align: center; word-wrap: break-word;'>-0.085 $ (0.092) $</td><td style='text-align: center; word-wrap: break-word;'>0.176** $ (0.070) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>-2.889*** $ (0.879) $</td><td style='text-align: center; word-wrap: break-word;'>-0.039 $ (0.099) $</td><td style='text-align: center; word-wrap: break-word;'>-0.328*** $ (0.118) $</td><td style='text-align: center; word-wrap: break-word;'>-0.175 $ (0.101) $</td><td style='text-align: center; word-wrap: break-word;'>-0.473*** $ (0.124) $</td><td style='text-align: center; word-wrap: break-word;'>-0.134 $ (0.097) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>In(1 + NUMBER_OF_DIRECTORS)</td><td style='text-align: center; word-wrap: break-word;'>-0.042 $ (0.037) $</td><td style='text-align: center; word-wrap: break-word;'>-0.039 $ (0.035) $</td><td style='text-align: center; word-wrap: break-word;'>-0.078** $ (0.039) $</td><td style='text-align: center; word-wrap: break-word;'>0.000 $ (0.031) $</td><td style='text-align: center; word-wrap: break-word;'>-0.081* $ (0.047) $</td><td style='text-align: center; word-wrap: break-word;'>-0.040 $ (0.028) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH_RICH_CONNECTIONS &gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'>-0.059** $ (0.026) $</td><td style='text-align: center; word-wrap: break-word;'>-0.035 $ (0.024) $</td><td style='text-align: center; word-wrap: break-word;'>-0.061** $ (0.027) $</td><td style='text-align: center; word-wrap: break-word;'>-0.029 $ (0.022) $</td><td style='text-align: center; word-wrap: break-word;'>-0.097*** $ (0.030) $</td><td style='text-align: center; word-wrap: break-word;'>0.002 $ (0.019) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH_POOR_CONNECTIONS &gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'>-0.025 $ (0.026) $</td><td style='text-align: center; word-wrap: break-word;'>0.033 $ (0.023) $</td><td style='text-align: center; word-wrap: break-word;'>0.001 $ (0.027) $</td><td style='text-align: center; word-wrap: break-word;'>0.007 $ (0.022) $</td><td style='text-align: center; word-wrap: break-word;'>0.022 $ (0.030) $</td><td style='text-align: center; word-wrap: break-word;'>-0.008 $ (0.020) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Industry fixed effects</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>State fixed effects</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R²</td><td style='text-align: center; word-wrap: break-word;'>0.099</td><td style='text-align: center; word-wrap: break-word;'>0.091</td><td style='text-align: center; word-wrap: break-word;'>0.072</td><td style='text-align: center; word-wrap: break-word;'>0.063</td><td style='text-align: center; word-wrap: break-word;'>0.070</td><td style='text-align: center; word-wrap: break-word;'>0.062</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>No. of obs.</td><td style='text-align: center; word-wrap: break-word;'>1,386</td><td style='text-align: center; word-wrap: break-word;'>1,343</td><td style='text-align: center; word-wrap: break-word;'>1,528</td><td style='text-align: center; word-wrap: break-word;'>1,201</td><td style='text-align: center; word-wrap: break-word;'>1,302</td><td style='text-align: center; word-wrap: break-word;'>1,427</td></tr></table>

Because 1933 was near the nadir of the Great Depression, we unsurprisingly observe an average decrease in both accounts receivable and accounts payable between the two observations. We observe positive changes in roughly the top quartiles of the distributions of both variables. Thus, we define firms with high changes in receivables to be firms in the top quartile of the distribution (and, later, likewise for payables). We then construct two indicator variables to identify firms with above-median connections to firms with high changes in receivables and above-median connections to firms with low changes in receivables. It is important to note that we only observe the necessary data to compute changes in receivables for roughly 56% of the firms in our sample. We do not include connections to firms with missing trade credit data in either category.

In Table 9, we report estimates of equation (1) using the measures of connections to firms with high and low changes in receivables as the key independent variables. The specifications mirror those we reported in Table 7 to measure the effects of connections to cash-rich and cash-poor firms. We find that it is indeed connections to firms that increased accounts receivable that significantly predict a lower likelihood of failure, whether we consider them independently or together with connections to firms that reduced receivables. There is no appreciable effect of connections to firms that did not increase receivables on the likelihood of firm failure.

<div style="text-align: center;"><div style="text-align: center;">TABLE 9</div> </div>


##### Network Connections and Firm Failure: By Changes in Connected Firm Accounts Receivable

Coefficient estimates in Table 9 are from OLS regressions on the sample of firms from the 1928 Moody's Industrial manual, excluding foreign firms and subsidiaries. The dependent variable is DISAPPEARED_BY_1937, an indicator variable that takes the value 1 if the firm exits by 1937. HIGH_CHG_REC_CONNECTIONS (LOW_CHG_REC_CONNECTIONS) is an indicator variable equal to 1 for firms that have a value of TOTAL_CONNECTIONS to firms with high changes in ACCOUNTS_RECEIVABLE between 1928 and 1933 above (below) the sample median, where TOTAL_CONNECTIONS is the sum of connections to other firms in the sample via shared directors or managers and high changes in ACCOUNTS_RECEIVABLE are changes in the top quartile of the sample distribution. PRIVATE is an indicator variable equal to 1 for firms without publicly traded equity. TOTAL_ASSETS, DSBT/ASSETS, and CASH/ASSETS are winsorized at the 1% level. Standard errors that are robust to heteroscedasticity are reported in parentheses. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>6</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(\text{TOTAL\_ASSETS}) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.063^{***}(0.006) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.064^{***}(0.006) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.063^{***}(0.006) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.063^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.064^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.063^{***}(0.007) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>0.071***(0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.072***(0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.071***(0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.074***(0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.076***(0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.074***(0.016)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>0.065(0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.063(0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.065(0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.088(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.083(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.088(0.056)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>$ -0.303^{***}(0.071) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.309^{***}(0.071) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.303^{***}(0.071) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.263^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.272^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.263^{***}(0.077) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{NUMBER\_OF\_DIRECTORS}) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.048^{**}(0.023) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.056^{**}(0.024) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.049^{**}(0.024) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.053^{**}(0.025) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.062^{**}(0.025) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.054^{**}(0.025) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>HIGH\_CHG\_REC\_CONNECTIONS</td><td style='text-align: center; word-wrap: break-word;'>$ -0.030^{**}(0.014) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.031^{**}(0.015) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.035^{**}(0.015) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.036^{**}(0.016) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>LOW\_CHG\_REC\_CONNECTIONS</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.007(0.015) $</td><td style='text-align: center; word-wrap: break-word;'>0.004(0.016)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.008(0.016) $</td><td style='text-align: center; word-wrap: break-word;'>0.003(0.017)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Industry fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>State fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R $ ^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.088</td><td style='text-align: center; word-wrap: break-word;'>0.087</td><td style='text-align: center; word-wrap: break-word;'>0.088</td><td style='text-align: center; word-wrap: break-word;'>0.099</td><td style='text-align: center; word-wrap: break-word;'>0.097</td><td style='text-align: center; word-wrap: break-word;'>0.098</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>No. of obs.</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td></tr></table>

We conduct several additional tests to explore the nature of the trade credit channel. First, we replicate the Table 9 specifications using changes in accounts payable rather than accounts receivable to partition connections. As with receivables, it appears to be connections to firms that increase payables during the Depression that are associated with lower failure rates, but the magnitude of the estimates is smaller than the effect of receivables and none are statistically significant. Though short-term funding through increased receivables appears to be the most important to reduce the odds of failure, the results together are consistent with cash-rich firms stepping into the void left by failing banks more generally to intermediate the flow of working capital among industrial firms. As a second step, we test whether trade credit flows are indeed responsible for the effect of cash-rich connections on failure that we measured in Table 7. To do so, we further partition connections to firms with high changes in accounts receivable into those that are cash-rich and cash-poor (following the definitions from Table 7) and likewise for connections to firms with low changes in receivables. We then define four indicator variables for firms with above-median numbers of connections in each of the implied categories (cash-rich high change in receivables; cash-poor high change in receivables; cash-rich low change in receivables, cash-poor low change in receivables). In Table 10, we report the results of estimating equation (1) including combinations of these measures of connections. When all four types are included together, we confirm that it is connections to cash-rich firms that also increase accounts receivable during the crisis that significantly predict a reduced likelihood.

<div style="text-align: center;"><div style="text-align: center;">TABLE 10</div> </div>


## Network Connections to High Versus Low Change in Receivable Firms and Firm Failure by Cash Holdings

Coefficient estimates in Table 10 are from OLS regressions on the sample of firms from the 1928 Moody's Industrial manual, excluding foreign firms and subsidiaries. The dependent variable is DISAPPEARED_BY_1937, an indicator variable that takes the value 1 if the firm exits by 1937. CASH_RICH_CONNECTIONS (CASH_POOR_CONNECTIONS) are TOTAL_CONNECTIONS to firms that are cash-rich (cash-poor). Cash-rich (cash-poor) firms are firms with CASH/ASSETS greater than (less than or equal to) the sample median. TOTAL_CONNECTIONS are links between firms via shared executives or directors. CHG_RECEIVABLES is the change in accounts receivable reported in the connected firm between the 1928 and 1934 manuals. Q1 indicates the top quartile of the sample distribution. PRIVATE is an indicator variable equal to 1 for firms without publicly traded equity. TOTAL_ASSETS, DEBT/ASSETS, and CASH/ASSETS are winsorized at the 1% level. Standard errors that are robust to heteroscedasticity are reported in parentheses. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>6</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(\text{TOTAL\_ASSETS}) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.063^{***}(0.006) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.064^{***}(0.006) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.063^{***}(0.006) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.062^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.064^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.062^{***}(0.007) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>0.071^{***}(0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.072^{***}(0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.071^{***}(0.015)</td><td style='text-align: center; word-wrap: break-word;'>0.074^{***}(0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.076^{***}(0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.074^{***}(0.016)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>0.065(0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.063(0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.065(0.052)</td><td style='text-align: center; word-wrap: break-word;'>0.088(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.083(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.088(0.056)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>$ -0.305^{***}(0.071) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.309^{***}(0.071) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.304^{***}(0.071) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.263^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.272^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.263^{***}(0.077) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{NUMBER\_OF\_DIRECTORS}) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.049^{**}(0.024) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.056^{**}(0.024) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.051^{**}(0.024) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.052^{**}(0.025) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.06^{**}(0.026) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.053^{**}(0.026) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH\_RICH\_CONNECTIONS and CHG\_RECEIVABLES = Q1</td><td style='text-align: center; word-wrap: break-word;'>$ -0.030^{**}(0.015) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.032^{**}(0.016) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.033^{**}(0.016) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.033^{**}(0.017) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH\_POOR\_CONNECTIONS and CHG\_RECEIVABLES = Q1</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.002(0.017) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.004(0.017) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.015(0.017) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.015(0.018) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH\_RICH\_CONNECTIONS and CHG\_RECEIVABLES &lt; Q1</td><td style='text-align: center; word-wrap: break-word;'>$ -0.002(0.016) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.004(0.016)</td><td style='text-align: center; word-wrap: break-word;'>$ -0.009(0.017) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.002(0.017) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH\_POOR\_CONNECTIONS and CHG\_RECEIVABLES &lt; Q1</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.003(0.016) $</td><td style='text-align: center; word-wrap: break-word;'>0.003(0.016)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.004(0.016) $</td><td style='text-align: center; word-wrap: break-word;'>0.003(0.017)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Industry fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>State fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R^{2}</td><td style='text-align: center; word-wrap: break-word;'>0.087</td><td style='text-align: center; word-wrap: break-word;'>0.086</td><td style='text-align: center; word-wrap: break-word;'>0.087</td><td style='text-align: center; word-wrap: break-word;'>0.098</td><td style='text-align: center; word-wrap: break-word;'>0.097</td><td style='text-align: center; word-wrap: break-word;'>0.098</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>No. of obs.</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td></tr></table>

of failure. None of the other types of connections predict failure, economically or statistically. As in prior tables, the results are robust to the inclusion of our typical controls and fixed effects.

We also directly analyze changes in (the natural logarithm of) the ratio of accounts receivable to accounts payable between 1928 and 1933. This measure allows us to capture changes in the relative intensity with which firms are net providers or recipients of trade credit during the crisis. To begin, we regress the measure on our standard set of control variables (including industry and state fixed effects) as well as the natural logarithm of the ratio in 1928, prior to the shock. $ ^{23} $ The independent variables of interest are an indicator for above-median numbers of network connections and its interaction with an indicator for firms with below-median 1928 cash holdings. We report the results in column 1 of Table 11. We find a pattern consistent with the interfirm lending channel. We find that high-cash firms increase their provision of working capital (the estimate of the level effect of high connections is positive and statistically significant at the 10% level). However,

<div style="text-align: center;"><div style="text-align: center;">TABLE 11</div> </div>


##### Change in Accounts Receivable/Accounts Payable by Connections and Cash Status

Coefficient estimates in Table 11 are from OLS regressions on the sample of firms from the 1928 Moody's Industrial manual, excluding foreign firms and subsidiaries. The dependent variable is the change in the natural logarithm of the ratio of accounts receivable to accounts payable from 1928 to 1933. TOTAL_CONNECTIONS > MEDIAN is an indicator variable equal to 1 for firms that have a value of TOTAL_CONNECTIONS greater than the sample median, where TOTAL_CONNECTIONS is the sum of connections to other firms in the sample via shared directors or managers. CASH_RICH_CONNECTIONS (CASH_POOR_CONNECTIONS) are TOTAL_CONNECTIONS to firms that are cash-rich (cash-poor). Cash-rich (cash-poor) firms are firms with CASH/ASSETS greater than (less than or equal to) the sample median. CHG_RECEIVABLES is the change in accounts receivable reported in the connected firm between the 1928 and 1934 manuals. Q1 indicates the top quartile of the sample distribution. PRIVATE is an indicator variable equal to 1 for firms without publicly traded equity. LOW_CASH (HIGH_CASH) is an indicator variable equal to 1 for firms that have CASH/ASSETS less than (greater than) the sample median. TOTAL_ASSETS, DEBT/ASSETS, and CASH/ASSETS are winsorized at the 1% level. Standard errors that are robust to heteroscedasticity are reported in parentheses. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Full Sample</td><td style='text-align: center; word-wrap: break-word;'>HIGH_CASH</td><td style='text-align: center; word-wrap: break-word;'>LOW_CASH</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>3</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL_CONNECTIONS &gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'>0.153 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.091)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL_CONNECTIONS &gt; MEDIAN  $ \times $ LOW_CASH</td><td style='text-align: center; word-wrap: break-word;'>$ -0.304 $ $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.120)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>LOW_CASH</td><td style='text-align: center; word-wrap: break-word;'>0.097</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.100)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH_POOR_CONNECTIONS &gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.238 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.105)</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH_RICH_CONNECTIONS &gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.023 $</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.110)</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH_RICH_CONNECTIONS and CHG_RECEIVABLES = Q1</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.278 $ $ ^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.103)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH_POOR_CONNECTIONS and CHG_RECEIVABLES = Q1</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.162</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.106)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>0.150 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>0.211 $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>0.102</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.068)</td><td style='text-align: center; word-wrap: break-word;'>(0.102)</td><td style='text-align: center; word-wrap: break-word;'>(0.105)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>In(TOTAL_ASSETS)</td><td style='text-align: center; word-wrap: break-word;'>$ -0.021 $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.035 $</td><td style='text-align: center; word-wrap: break-word;'>0.019</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.030)</td><td style='text-align: center; word-wrap: break-word;'>(0.040)</td><td style='text-align: center; word-wrap: break-word;'>(0.052)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>$ -0.537 $ $ ^{**} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.317 $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.81 $ $ ^{**} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.265)</td><td style='text-align: center; word-wrap: break-word;'>(0.408)</td><td style='text-align: center; word-wrap: break-word;'>(0.366)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>$ -0.236 $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.261 $</td><td style='text-align: center; word-wrap: break-word;'>0.663</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.426)</td><td style='text-align: center; word-wrap: break-word;'>(0.453)</td><td style='text-align: center; word-wrap: break-word;'>(3.764)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>ACCOUNTS_RECEIVABLE/ACCOUNTS_PAYABLE</td><td style='text-align: center; word-wrap: break-word;'>$ -0.523 $ $ ^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.531 $ $ ^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.544 $ $ ^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.033)</td><td style='text-align: center; word-wrap: break-word;'>(0.046)</td><td style='text-align: center; word-wrap: break-word;'>(0.049)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>In(1 + NUMBER_OF_DIRECTORS)</td><td style='text-align: center; word-wrap: break-word;'>0.065</td><td style='text-align: center; word-wrap: break-word;'>$ -0.071 $</td><td style='text-align: center; word-wrap: break-word;'>0.118</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(0.106)</td><td style='text-align: center; word-wrap: break-word;'>(0.159)</td><td style='text-align: center; word-wrap: break-word;'>(0.164)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Industry fixed effects</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>State fixed effects</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R $ ^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.261</td><td style='text-align: center; word-wrap: break-word;'>0.277</td><td style='text-align: center; word-wrap: break-word;'>0.243</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>No. of obs.</td><td style='text-align: center; word-wrap: break-word;'>1,421</td><td style='text-align: center; word-wrap: break-word;'>770</td><td style='text-align: center; word-wrap: break-word;'>651</td></tr></table>

low-cash firms decrease their provision of working capital by roughly the same magnitude. The difference-in-differences between the two groups is roughly 25% of a standard deviation of the dependent variable and is statistically significant at the 5% level. In column 2, we isolate further the role of cash-rich firms in providing working capital to cash-poor trading partners, the lynchpin of the trade credit mechanism. To do so, we focus on the subsample of firms with 1928 cash holdings above the sample median. Within this subsample, we regress the change in the trade credit balance on indicators for above-median connections to cash-rich and cash-poor firms (along with the full set of controls from column 1). We do not observe a difference in the change in the trade credit balance for firms connected to cash-rich firms relative to their peers; however, we observe a significant increase in the

provision of trade credit among cash-rich firms that disproportionately have connections to cash-poor firms. To close the loop, we examine the subsample of cash-poor firms. In this subsample, we regress the change in trade credit balance on indicators for above-median connections to cash-rich (-poor) firms that increased their receivables between 1928 and 1934 (building on Table 10). We find that above-median connections to the cash-rich firms are indeed significantly associated with declines in the ratio of receivables to payables (i.e., increases in payables relative to receivables). Connections to cash-poor firms are not. The results are similar if we also include indicators for cash-rich (-poor) firms with low changes in receivables.

As a final step, we examine the relation between trade credit usage and network connections prior to the 1929 crisis. Outside of the context of director and executive network connections, existing studies find evidence of increased trade credit usage around financial crises (Love, Preve, and Sarria-Allende (2007), García-Appendini and Montoriol-Garriga (2013)). A natural question, then, is whether the network ties we study correlate with greater (ex ante) financial strength among a firm's customers and suppliers. It is difficult to measure this correlation directly. However, if the trading partners of more connected firms were on average stronger, we might expect to see greater reliance on trade credit as a source of financing among these firms even outside of crisis episodes. We find no evidence for this hypothesis: The correlations between network connections and the 1928 ratios of accounts receivable and accounts payable to sales are essentially 0 and are statistically insignificant. $ ^{24} $ Thus, consistent with the IV results from Table 5, this evidence suggests the importance of network links as such for survival, not only because they correlate with other metrics of financial strength. Overall, our tests suggest that one mechanism through which director and executive network links reduce the probability of firm failure is by increasing the willingness of connected firms to extend financial assistance through trade credit, for example, by providing access to private information on credit risk.

#### B. Product Market Collusion

Another mechanism through which connections could increase survival odds is by facilitating product market collusion. For example, competing firms that sell in the same markets could collude to keep prices high. We do not observe product prices, so we cannot test this channel directly. However, collusion should be most beneficial among firms in the same product markets. Thus, to assess whether our evidence is broadly consistent with this channel, we test for differences in the effects of connections within and outside of the firm's industry or state.

In columns 1–3 of Table 12, we report the results of estimating equation (1), using indicator variables that measure above-median connections within and outside the industry as independent variables. For brevity, we report only specifications with state and industry fixed effects. We find a positive and significant

<div style="text-align: center;"><div style="text-align: center;">TABLE 12</div> </div>


##### Network Connections to Within Versus Outside Industry Firms and Firm Failure

Coefficient estimates in Table 12 are from OLS regressions on the sample of firms from the 1928 Moody's Industrial manual, excluding foreign firms and subsidiaries. The dependent variable is DISAPPEARED_BY_1937, an indicator variable that takes the value 1 if the firm exits by 1937. WITHIN_IND_CONN (OUTSIDE_IND_CONN) > MEDIAN is an indicator variable equal to 1 for firms that have a value of connections greater than the sample median, where connections is the sum of connections to firms within (outside) the firm's industry via shared directors or managers. We do not count connections toward either total for cases in which shared directorship or management is observed but industry of the connected firm is unobserved. WITHIN_IND_CONN AND_X" (WITHIN_IND_CONN AND_NOT"X") > MEDIAN captures connections that are both within-industry and also satisfy (do not satisfy) an additional "X" condition. In columns 4–6, the "X" (notX") condition is that the firm's connection has to be also through executives and directors who are at firms operating in the states where the firm operates (where the firm does not operate). In columns 7–8, the "X" (notX") condition is that the firm's connection has to be also through executives and directors who are at cash-rich (cash-poor firms. Cash-rich) firms are firms with CASH/ASSETS greater than (less than or equal to) the sample median. Similar to WITHIN_IND_CONN > MEDIAN, WITHIN_IND_CONN AND_X" (WITHIN_IND_CONN AND_NOT"X") > MEDIAN is an indicator variable for firms with connections greater than the sample median. OUTSIDE_IND_CONN AND_X" > MEDIAN is defined similarly to WITHIN_IND_CONN AND_X" > MEDIAN. PRIVATE is an indicator variable equal to 1 for firms without publicly traded equity. TOTAL_ASSETS, DEBT/ASSETS, and CASH/ASSETS are winsorized at the 1% level. Standard errors that are robust to heteroscedasticity are reported in parentheses. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td rowspan="2"></td><td rowspan="2">1</td><td rowspan="2">2</td><td rowspan="2">3</td><td colspan="3">$ \chi^{2} = IN\_STATE $</td><td colspan="3">$ \chi^{2} = CASH\_RICH $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>9</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(\text{TOTAL\_ASSETS}) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.061^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.064^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.061^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.063^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.062^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.062^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.062^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.063^{***}(0.007) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.062^{***}(0.007) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>0.072^{***}(0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.076^{***}(0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.073^{***}(0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.074^{***}(0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.072^{***}(0.017)</td><td style='text-align: center; word-wrap: break-word;'>0.071^{***}(0.017)</td><td style='text-align: center; word-wrap: break-word;'>0.071^{***}(0.017)</td><td style='text-align: center; word-wrap: break-word;'>0.075^{***}(0.016)</td><td style='text-align: center; word-wrap: break-word;'>0.071^{***}(0.017)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>0.091(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.083(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.092(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.085(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.091(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.092(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.085(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.086(0.056)</td><td style='text-align: center; word-wrap: break-word;'>0.087(0.056)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>$ -0.270^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.271^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.270^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.269^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.273^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.271^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.266^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.273^{***}(0.077) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.267^{***}(0.077) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{NUMBER\_OF\_DIRECTORS}) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.0470^{*}(0.025) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.060^{**}(0.026) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.050^{*}(0.026) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.054^{**}(0.025) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.049^{*}(0.026) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.043^{*}(0.026) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.053^{**}(0.025) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.053^{**}(0.025) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.049^{*}(0.026) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>WITHIN\_IND\_CONN &amp;gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'>$ -0.054^{***}(0.016) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.057^{***}(0.017) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>WITHIN\_IND\_CONN\_AND\_ $ \chi^{2} $ &amp;gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.028^{*}(0.017) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.021(0.017) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.046^{***}(0.016) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.041^{**}(0.017) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>WITHIN\_IND\_CONN\_AND\_NOT $ \chi^{2} $ &amp;gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.049^{***}(0.016) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.045^{***}(0.016) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.022(0.016) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.011(0.017) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>OUTSIDE\_IND\_CONN &amp;gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.009(0.016) $</td><td style='text-align: center; word-wrap: break-word;'>0.009(0.017)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>OUTSIDE\_IND\_CONN\_AND\_ $ \chi^{2} $ &amp;gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.012(0.017) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.009(0.017) $</td><td style='text-align: center; word-wrap: break-word;'>0.002(0.017)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.005(0.017)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>OUTSIDE\_IND\_CONN\_AND\_NOT $ \chi^{2} $ &amp;gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.003(0.017)</td><td style='text-align: center; word-wrap: break-word;'>0.006(0.017)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$ -0.012(0.016) $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.006(0.017) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Industry fixed effects</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>State fixed effects</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R $ ^{2} $</td><td style='text-align: center; word-wrap: break-word;'>0.101</td><td style='text-align: center; word-wrap: break-word;'>0.097</td><td style='text-align: center; word-wrap: break-word;'>0.101</td><td style='text-align: center; word-wrap: break-word;'>0.098</td><td style='text-align: center; word-wrap: break-word;'>0.100</td><td style='text-align: center; word-wrap: break-word;'>0.100</td><td style='text-align: center; word-wrap: break-word;'>0.099</td><td style='text-align: center; word-wrap: break-word;'>0.098</td><td style='text-align: center; word-wrap: break-word;'>0.099</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>No. of obs.</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td></tr></table>

association between survival and connections inside the industry, but not outside the industry. Firms with above-median within-industry connections have a 5.7 percentage point lower failure rate. We perform a similar test in which we measure separately the effects of connections to in-state and out-of-state firms. Here, we do not find strong evidence that the relation between network ties and survival differs by connection type.

Given our definitions of industry groups, the evidence on within-industry connections is also consistent with the trade credit channel. For example, we define the oil industry group using search strings that include “gasoline,” “crude,” and “refin.” In this case, firms from the entire supply chain, stretching from extraction to retail sales, are part of the group. To try to further distinguish the collusion channel, we differentiate within-industry connections to firms located in-state and out-of-state. We report the results in columns 4–6 of Table 12. We find that above-median connections to within-industry firms located out-of-state significantly associate

with lower failure odds, but above-median connections to within-industry firms located in-state do not. This pattern is not obviously predicted by the collusion channel (i.e., it is likely to be more beneficial to collude within-state). The result could be reconciled with the trade credit channel if customers and suppliers do not necessarily collocate in the same markets or if the effect of the financial shock is not identical across states. In columns 7–9 of Table 12, we report the results of interacting industry links with the cash holdings of the connected firm. We confirm that above-median connections to high-cash firms within-industry predict heightened survival. Above-median links to high-cash firms out-of-industry do not (nor do above-median connections to low-cash firms of either type). We also find some evidence that above-median connections to high-cash firms out-of-state are more related to survival, though the cross-group differences are not significant. This evidence is again consistent with the trade credit channel.

#### C. Links to Financial Institutions

Another possibility is that the shared directors we observe in our sample are actually banker-directors who aid the firm directly by facilitating access to financial markets. For example, Frydman and Hilt (2017) find evidence that firms with underwriters on their boards had cheaper access to finance and higher investment rates in the early twentieth century. Though they argue such directorships were most common among railroads, it is possible that a similar mechanism could have aided industrial firms during the Depression. Our results are strongest among private firms. Thus, the most plausible concern is that the connections driving our results come from shared commercial bankers who serve on the boards to facilitate bank lending.

We take two approaches to assess this mechanism. First, we recalculate our measure of connections excluding cases in which the connection comes via an individual whom we only observe as a director in the 1928 Moody's Industrial manual. Moody's published separate volumes that provided management information for banks and railroads. Thus, we can be sure that individuals we identify as managers are not bankers. Second, we restrict our sample only to firms that did not have any outstanding bank debt or mortgages in 1928. We find that neither restriction has a material effect on our results. In Table 6 in the Supplementary Material, we present the estimates of regressions that impose both additional conditions. We continue to find that connections significantly decrease failure rates among private, rural, cash-poor, and small firms.

#### D. Links to Financial Markets

It is also possible that connections to industrial firms correlate with connections to financial centers, so that our estimates pick up the effects of greater financial access through public markets. One way to test for this mechanism is to measure directly the frequency with which director network connections are to firms located in major financial centers. For each firm, we count connections to firms in each city with an active stock market in the 1920s: New York, Chicago, Boston, Philadelphia, Baltimore, Cincinnati, Detroit, Cleveland, Hartford, Honolulu, Los Angeles, Louisville, Pittsburgh, San Francisco, and St. Louis. We then measure the effect of connections to firms in these cities within our baseline regression specifications.

from Table 3. We do not find any evidence that connections to firms in these specific cities are particularly important for firm survival. We also consider the effects of more prominent markets individually and as a subgroup: New York, Chicago, Boston, and Philadelphia. We do not uncover any evidence that connections to firms in these markets drive the effect of connections on survival.

#### E. Equity Stakes

Another way that firms could provide financial assistance to troubled peers in addition to providing firm-to-firm credit is by taking equity stakes. Executive and director network ties could lower the costs of such investments by reducing the information asymmetries between firms. $ ^{25} $ In particular, information flow through such links could aid firms in distinguishing between potential targets that are in financial and economic distress during the crisis.

To explore this channel, we test whether network connections affect the probability that a firm becomes a takeover target or merges with another firm during the Depression. Takeovers are the limiting case of cross-firm equity investments, but have the advantage of being readily observable. Though they are also a mechanism through which firms “disappear” from the marketplace, we analyze acquisitions separately from closures because our prediction for the direction of the effect of network ties is opposite in the two contexts.

We use a variant of the linear probability model in equation (1) to test whether network ties increase the likelihood that a firm is acquired during the Great Depression. In this case, the dependent variable is an indicator variable that takes the value of 1 if the firm is acquired or merged with another firm before 1938. Otherwise, we mirror the regression specifications from our analysis of firm failure in Table 3, including the same controls and network measures. We report the results in Table 13. Generally, we find that more network ties indeed increase the likelihood that a firm is acquired by another firm following the shock. The economic magnitudes are somewhat larger than the effect of network connections on the likelihood of failure, though opposite in sign. A modest difference is that the effect on acquisitions comes primarily from the comparison of firms in the top three quartiles of the distribution of connections to firms in the bottom quartile. We do not observe significant differences across the top three quartiles. $ ^{26} $

As in Table 6, we test whether the effect on the likelihood of being acquired is magnified within small, cash-poor, rural, or private firms. We present the results in the Supplementary Material. In general, we do not uncover any consistent relation

<div style="text-align: center;"><div style="text-align: center;">TABLE 13</div> </div>


##### Network Connections and the Likelihood of Firm Being Acquired

Coefficient estimates in Table 13 are from OLS regressions on the sample of firms from the 1928 Moody's Industrial manual, excluding foreign firms and subsidiaries. The dependent variable is ACQUIRED_BY_1937, an indicator variable that takes the value 1 if the firm is acquired by another firm by 1937. TOTAL_CONNECTIONS is the sum of connections to other firms in the sample via shared directors or managers. TOTAL_CONNECTIONS > MEDIAN is an indicator variable equal to 1 for firms that have a value of TOTAL_CONNECTIONS greater than the sample median. TOTAL_CONNECTIONS_QUARTILE_2 (3,4) is an indicator variable equal to 1 for firms that have a value of TOTAL_CONNECTIONS in the sample 2nd (3rd/4th) quartile. PRIVATE is an indicator variable equal to 1 for firms without publicly traded equity. TOTAL_ASSETS, DEBT/ASSETS, and CASH/ASSETS are winsorized at the 1% level. Standard errors that are robust to heteroscedasticity are reported in parentheses. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>6</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(\text{TOTAL\_ASSETS}) $</td><td style='text-align: center; word-wrap: break-word;'>-0.016*** $ (0.005) $</td><td style='text-align: center; word-wrap: break-word;'>-0.015*** $ (0.005) $</td><td style='text-align: center; word-wrap: break-word;'>-0.014*** $ (0.005) $</td><td style='text-align: center; word-wrap: break-word;'>-0.02*** $ (0.006) $</td><td style='text-align: center; word-wrap: break-word;'>-0.019*** $ (0.006) $</td><td style='text-align: center; word-wrap: break-word;'>-0.018*** $ (0.006) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'>0.003 $ (0.013) $</td><td style='text-align: center; word-wrap: break-word;'>0.002 $ (0.013) $</td><td style='text-align: center; word-wrap: break-word;'>0.004 $ (0.013) $</td><td style='text-align: center; word-wrap: break-word;'>0.003 $ (0.014) $</td><td style='text-align: center; word-wrap: break-word;'>0.002 $ (0.014) $</td><td style='text-align: center; word-wrap: break-word;'>0.004 $ (0.014) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>DEBT/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>0.034 $ (0.039) $</td><td style='text-align: center; word-wrap: break-word;'>0.034 $ (0.039) $</td><td style='text-align: center; word-wrap: break-word;'>0.032 $ (0.039) $</td><td style='text-align: center; word-wrap: break-word;'>0.020 $ (0.043) $</td><td style='text-align: center; word-wrap: break-word;'>0.022 $ (0.043) $</td><td style='text-align: center; word-wrap: break-word;'>0.020 $ (0.043) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'>-0.045 $ (0.057) $</td><td style='text-align: center; word-wrap: break-word;'>-0.043 $ (0.057) $</td><td style='text-align: center; word-wrap: break-word;'>-0.041 $ (0.057) $</td><td style='text-align: center; word-wrap: break-word;'>-0.031 $ (0.061) $</td><td style='text-align: center; word-wrap: break-word;'>-0.029 $ (0.061) $</td><td style='text-align: center; word-wrap: break-word;'>-0.025 $ (0.061) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{NUMBER\_OF\_DIRECTORS}) $</td><td style='text-align: center; word-wrap: break-word;'>-0.036* $ (0.020) $</td><td style='text-align: center; word-wrap: break-word;'>-0.030 $ (0.019) $</td><td style='text-align: center; word-wrap: break-word;'>-0.033* $ (0.020) $</td><td style='text-align: center; word-wrap: break-word;'>-0.041* $ (0.022) $</td><td style='text-align: center; word-wrap: break-word;'>-0.032 $ (0.021) $</td><td style='text-align: center; word-wrap: break-word;'>-0.036 $ (0.022) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{TOTAL\_CONNECTIONS}) $</td><td style='text-align: center; word-wrap: break-word;'>0.015** $ (0.006) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.019*** $ (0.007) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS &gt; MEDIAN</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.024* $ (0.013) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.029** $ (0.014) $</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS\_QUARTILE\_2</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.038** $ (0.016) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.048*** $ (0.017) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS\_QUARTILE\_3</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.049*** $ (0.016) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.062*** $ (0.018) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>TOTAL\_CONNECTIONS\_QUARTILE\_4</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.033* $ (0.017) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.038** $ (0.019) $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Industry fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>State fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R²</td><td style='text-align: center; word-wrap: break-word;'>0.005</td><td style='text-align: center; word-wrap: break-word;'>0.005</td><td style='text-align: center; word-wrap: break-word;'>0.006</td><td style='text-align: center; word-wrap: break-word;'>0.019</td><td style='text-align: center; word-wrap: break-word;'>0.018</td><td style='text-align: center; word-wrap: break-word;'>0.021</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>No. of obs.</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,992</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td><td style='text-align: center; word-wrap: break-word;'>2,729</td></tr></table>

between financial constraints and the effect of network ties on the likelihood of being acquired. However, we find that the association with network connections is concentrated among private firms. These results suggest that connections facilitate information flow about opaque firms to potential acquirers, but, surprisingly, do not suggest that the mechanism is more or less active among firms that are financially constrained.

Overall, our evidence points to the increased flow of trade credit as a key economic channel through which executive and director connections help financially constrained firms to survive through the Depression. We also observe some evidence that network connections facilitate equity investments, but the effects are not concentrated among financially constrained firms. Nevertheless, we note that these and other potential economic mechanisms are not mutually exclusive: There could be other ways that connected industrial firms can aid troubled peers, such as partial equity stakes or direct long-term loans, that we do not observe in our data.

### V. Conclusion

We study how network connections to other firms through executives and directors affect firm outcomes during a major financial shock. We find that firms

with more network ties in 1928, on the eve of the Great Depression, are more likely to survive over the following 10 years.

Among the advantages of our historical setting is that both financial and director markets were more segmented than they are today. We exploit plausibly exogenous variation across these local markets to mitigate the identification challenge posed by the endogeneity of director network links. Following the banking literature (e.g., Nanda and Nicholas (2014)), we show that connections have a stronger positive relation with survival probability in local markets in which a greater fraction of banks entered distress during the peak crisis years of 1930 to 1933. We also show that the portion of the variation in network ties that is predicted by differences in the local demand for directors' services outside the firm (conditioning on the vibrancy of the local market) is sufficient to identify our results. As a third way to address the concern that network ties could be correlated with an omitted factor that predicts firm survival, we test whether connections indeed matter the most among firms that are likely to be the most vulnerable to a financial shock. We find that the effect is indeed particularly pronounced among financially constrained firms (small firms, private firms, and firms with low cash holdings) as well as among firms located in rural areas.

We also investigate a variety of mechanisms that could explain our baseline finding. Our evidence suggests that network ties are particularly important to facilitate the flow of trade credit from financially healthy firms to constrained trading partners. We find not only that it is connections to cash-rich firms that mainly drive our results, but that, in particular, it is connections to cash-rich firms that also increase their accounts receivable during the peak crisis years. The evidence suggests that network links allow firms to distinguish between unviable firms and firms that are constrained by the shock, but economically sound. This information allows them to profitably perform an intermediation function that is normally done by banks. Thus, our results provide a link between the literature on director networks and the literatures on trade credit and cash holdings. In the latter case, our findings could help to resolve the puzzle of large corporate cash holdings despite their tax disadvantages. In addition to providing precautionary savings, cash enables firms to extend working capital to trading partners in times of crisis. The effects on failure rates are significant; our analysis suggests that high connections reduce the likelihood of failure by roughly 20%. In turn, cash-rich firms can avoid the disruption costs from losing trading partners.

More generally, our evidence suggests that network ties can provide some stabilization of the economy in times when credit markets freeze, preventing the failure of firms that are viable except for the bad fortune of lacking financial resources at the time of the shock. Such a backstop could be particularly important to the degree that firm failures result in layoffs that further depress local demand, producing the potential for additional feedback effects. Thus, policies regarding board composition and corporate governance can affect not only individual firms, but also can have a multiplier effect through networks. In this sense, our results suggest a partial counterargument to the conventional wisdom in the governance literature that “busy” CEOs and directors who serve as directors on multiple

boards are bad for firm value. Moreover, our analysis questions the policy prescriptions of the literature on “interlocked directorship.” That literature suggests benefits from restricting firms’ ability to choose board members. Our results instead suggest that limiting firms’ abilities to construct optimal networks could also limit the effectiveness of networks as a stabilizing mechanism in response to common shocks.

## Appendix

In this appendix, we provide details on the construction of the director network database, as well as the definitions of the industry, geographical, and other cross-sectional variables used in our analysis. In Section A, we discuss how we obtain information on firms' executives and directors from the 1928 Moody's Industrial manual using OCR and natural language processing techniques. In Section B, we discuss variables we obtain manually from the 1928 and 1938 Moody's Industrial manuals. In Section C, we discuss other data that we automatically retrieve from the same manual, such as geographical location and industry information.

#### A. Data on Executives and Directors from the 1928 Moody’s Industrial Manual

The main source for our analysis is the 1928 Moody’s Industrial Manual. The manual was the major source of information for industrial firms existing at the time. We run Optical Character Recognition (OCR) on the images of the manual, using “ABBYY FineReader” as the software package of choice. Our main data source is the text output from this OCR stage. Table A1 provides an example of the raw output from the OCR process.

The Moody’s firm-level information is roughly organized as follows:

(a) Firm title (in capitals), followed by an entry in parentheses specifying if the firm is a subsidiary of another firm (in parentheses, using “Controlled by” or “Affiliated with”)

(b) Details on firm history, from the time it was founded until the year the manual is published

(c) Management and board of directors information, including the names of officers and directors as well as their geographic location

(d) Firm offices location, auditors, day of annual meeting

(e) Financial and operating data such as income statement and balance sheet

(f) Securities ratings (in particular, fixed income security ratings in all years and also equity ratings)

(g) Business and products (detailed information on the business lines and different products marketed by the companies)

(h) Exchange where the stocks are listed

The focal point of our research is item (c) above, for which we detail our data gathering efforts below. We also use items (d), (e), and (h) in our analysis and describe the data gathering process for those items in the next sections. While the quality of the images of the 1928 Moody's Industrial manual is quite high, the OCR has some

# TABLE A1 OCR Sample Output from the 1928 Moody's Industrial Manual

Table A1 reports the raw OCR output from ABBYY for two pages (from the top, cut for space purposes) from the 1928 Moody's Industrial Manual. See Figures A1 and A2 for the original image files.

##### OCR output for page 1 of the 1928 Moody's Industrial Manual

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fda60930-d638-42a2-8f5e-1cdd8e050fdf/markdown_1/imgs/img_in_image_box_116_269_655_622.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-09T02%3A51%3A26Z%2F-1%2F%2F03e32a1dd267d04f635e79d63f6652c31f4be88f8abb5c4f87f0506d6208a5ad" alt="Image" width="61%" /></div>


##### OCR output for page 2892 of the 1928 Moody's Industrial Manual

##### MOODY'S MANUAL OF INVESTMENTS

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//fda60930-d638-42a2-8f5e-1cdd8e050fdf/markdown_1/imgs/img_in_image_box_115_657_754_1040.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-04-09T02%3A51%3A26Z%2F-1%2F%2Fa4190d5e20b6bf7feff87fb7f57a64ba4aa5af2673ac9b0c03e4588bceebdf4c" alt="Image" width="72%" /></div>


nontrivial typographical errors in its output. As a first step in our analysis, we perform an “OCR typo correction” focused on strings of interest, in particular, strings that define sections in the document in which we are particularly interested (i.e., the management and directors section). The code generates flags for pages where the OCR may be

corrupted due to image errors, and in those cases we enter/fix the data manually (about 2% of the pages required some manual intervention).

Figure A1 presents the image of the first page of the manual that provides firm-level data. Firm-level data follow a long introduction that includes different indexes and other aggregate data. Figure A1 is a typical entry for a large firm, for which the Moody's

<div style="text-align: center;"><div style="text-align: center;">FIGURE A1</div> </div>


# First Section

# INDUSTRIAL COMPANIES

# Including security ratings where complete facts and figures are available

##### ACME STEEL COMPANY

History: Organized in 1880 and incorporated April, 1884, in Illinois, as Acme Flexible Clasp Co.; in 1899 consolidated with Quincy Hardware Manufacturing Co. as Acme Steel Goods Co.; changed to present title in 1825. Manufactures hot rolled hoop steel, barrel hoops, bale ties, bucket hoops, metal box straps, corrugated fasteners and hot and cold rolled strip steel. Plants located in Chicago and Riverdale, Illinois, have a capacity of 700 tons per day. Chicago plant covers 2% acres with total floor space of about 5 acres. Riverdale plant located on site of 185 acres. Branches, offices and warehouses in New York, San Francisco, Los Angeles, New Orleans, Atlanta, Seattle, Vancouver, Winnipeg, Montreal and Detroit.

Management: OFFICERS: J. E. MacMurray, Chairman; S. H. Norton, Pres.; F. C. Gifford, Vice-Pres.; Donald MacMurray, Vice-Pres.; C. M. MacChesney, Sec.; C. S. Traer, Treas.; T. W. Lux, Asst. Sec. and Asst. Treas., Chicago. DIRECTORS: J. E. MacMurray, F. C. Gifford, Donald MacMurray, R. H. Norton, L. H. Whiting, C. S. Traer, C. MacChesney, Chicago. ANNUAL MEETING: Third Tuesday in January. OFFICE: Chicago, Ill.

<div style="text-align: center;"><div style="text-align: center;">Comparative Income Account, Years Ended Dec. 31</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Net operating profit</td><td style='text-align: center; word-wrap: break-word;'>1927</td><td style='text-align: center; word-wrap: break-word;'>1926</td><td style='text-align: center; word-wrap: break-word;'>1925</td><td style='text-align: center; word-wrap: break-word;'>1924</td><td style='text-align: center; word-wrap: break-word;'>1923</td><td style='text-align: center; word-wrap: break-word;'>1922</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Bond interest</td><td style='text-align: center; word-wrap: break-word;'>$1,718,981</td><td style='text-align: center; word-wrap: break-word;'>$1,447,840</td><td style='text-align: center; word-wrap: break-word;'>$1,806,627</td><td style='text-align: center; word-wrap: break-word;'>$1,148,496</td><td style='text-align: center; word-wrap: break-word;'>$1,004,863</td><td style='text-align: center; word-wrap: break-word;'>$531,352</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>84,623</td><td style='text-align: center; word-wrap: break-word;'>84,599</td><td style='text-align: center; word-wrap: break-word;'>100,147</td><td style='text-align: center; word-wrap: break-word;'>92,487</td><td style='text-align: center; word-wrap: break-word;'>71,900</td><td style='text-align: center; word-wrap: break-word;'>-</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Net income</td><td style='text-align: center; word-wrap: break-word;'>$1,634,358</td><td style='text-align: center; word-wrap: break-word;'>$1,363,241</td><td style='text-align: center; word-wrap: break-word;'>$1,706,480</td><td style='text-align: center; word-wrap: break-word;'>$1,051,009</td><td style='text-align: center; word-wrap: break-word;'>$982,953</td><td style='text-align: center; word-wrap: break-word;'>$531,352</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Margin of safety</td><td style='text-align: center; word-wrap: break-word;'>95%</td><td style='text-align: center; word-wrap: break-word;'>94%</td><td style='text-align: center; word-wrap: break-word;'>94%</td><td style='text-align: center; word-wrap: break-word;'>92%</td><td style='text-align: center; word-wrap: break-word;'>93%</td><td style='text-align: center; word-wrap: break-word;'>-</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Federal taxes</td><td style='text-align: center; word-wrap: break-word;'>219,539</td><td style='text-align: center; word-wrap: break-word;'>184,038</td><td style='text-align: center; word-wrap: break-word;'>217,723</td><td style='text-align: center; word-wrap: break-word;'>127,799</td><td style='text-align: center; word-wrap: break-word;'>114,491</td><td style='text-align: center; word-wrap: break-word;'>64,455</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Surplus for year</td><td style='text-align: center; word-wrap: break-word;'>$1,414,819</td><td style='text-align: center; word-wrap: break-word;'>$1,179,203</td><td style='text-align: center; word-wrap: break-word;'>$1,488,757</td><td style='text-align: center; word-wrap: break-word;'>$932,210</td><td style='text-align: center; word-wrap: break-word;'>$818,462</td><td style='text-align: center; word-wrap: break-word;'>$466,867</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Earned per share</td><td style='text-align: center; word-wrap: break-word;'>$7.74</td><td style='text-align: center; word-wrap: break-word;'>$6.45</td><td style='text-align: center; word-wrap: break-word;'>$8.59</td><td style='text-align: center; word-wrap: break-word;'>$16.26</td><td style='text-align: center; word-wrap: break-word;'>$16.00</td><td style='text-align: center; word-wrap: break-word;'>+8.45</td></tr></table>

 $ ^{*} $ Based on no par-shares, prior to 1925. † After deducting preferred dividend requirement.

<div style="text-align: center;"><div style="text-align: center;">Comparative Balance Sheet, as of Dec. 31</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>ASSETS:</td><td style='text-align: center; word-wrap: break-word;'>1927</td><td style='text-align: center; word-wrap: break-word;'>1926</td><td style='text-align: center; word-wrap: break-word;'>LIABILITIES:</td><td style='text-align: center; word-wrap: break-word;'>1927</td><td style='text-align: center; word-wrap: break-word;'>1926</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \dagger $Plant and equipment</td><td style='text-align: center; word-wrap: break-word;'>6,256,172</td><td style='text-align: center; word-wrap: break-word;'>6,079,891</td><td style='text-align: center; word-wrap: break-word;'>Capital stock</td><td style='text-align: center; word-wrap: break-word;'>4,579,950</td><td style='text-align: center; word-wrap: break-word;'>4,573,950</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \dagger $Patents</td><td style='text-align: center; word-wrap: break-word;'>92,377</td><td style='text-align: center; word-wrap: break-word;'>52,156</td><td style='text-align: center; word-wrap: break-word;'>Bonded debt</td><td style='text-align: center; word-wrap: break-word;'>1,281,000</td><td style='text-align: center; word-wrap: break-word;'>1,410,000</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Stocks and bonds</td><td style='text-align: center; word-wrap: break-word;'>53,522</td><td style='text-align: center; word-wrap: break-word;'>25,500</td><td style='text-align: center; word-wrap: break-word;'>Accounts payable</td><td style='text-align: center; word-wrap: break-word;'>225,402</td><td style='text-align: center; word-wrap: break-word;'>185,238</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Bills and accounts rec.</td><td style='text-align: center; word-wrap: break-word;'>885,074</td><td style='text-align: center; word-wrap: break-word;'>809,107</td><td style='text-align: center; word-wrap: break-word;'>Bills payable</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>300,000</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Inventory</td><td style='text-align: center; word-wrap: break-word;'>1,543,895</td><td style='text-align: center; word-wrap: break-word;'>1,913,171</td><td style='text-align: center; word-wrap: break-word;'>Accrued interest</td><td style='text-align: center; word-wrap: break-word;'>37,311</td><td style='text-align: center; word-wrap: break-word;'>28,800</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Cash</td><td style='text-align: center; word-wrap: break-word;'>878,587</td><td style='text-align: center; word-wrap: break-word;'>126,374</td><td style='text-align: center; word-wrap: break-word;'>Reserves for taxes</td><td style='text-align: center; word-wrap: break-word;'>322,052</td><td style='text-align: center; word-wrap: break-word;'>285,628</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Deferred charges</td><td style='text-align: center; word-wrap: break-word;'>1,646</td><td style='text-align: center; word-wrap: break-word;'>4,139</td><td style='text-align: center; word-wrap: break-word;'>Surplus</td><td style='text-align: center; word-wrap: break-word;'>3,175,598</td><td style='text-align: center; word-wrap: break-word;'>2,226,822</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Total</td><td style='text-align: center; word-wrap: break-word;'>9,705,313</td><td style='text-align: center; word-wrap: break-word;'>9,009,838</td><td style='text-align: center; word-wrap: break-word;'>Total</td><td style='text-align: center; word-wrap: break-word;'>9,705,313</td><td style='text-align: center; word-wrap: break-word;'>9,009,838</td></tr></table>

* After depreciation accrued to Dec. 31: 1927, $526,288; 1926, $515,295. * After depreciation and amortization to Dec. 31: 1927, $1,768,186; 1926, $1,530,695.

Working Capital: 1927, current assets, $8,801,596; current liabilities, $574,765; net current assets, $2,726,831, 1926, current assets, $2,848,652; current liabilities, $799,066; net current assets, $2,049,586.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Table A—Bond Records</td><td style='text-align: center; word-wrap: break-word;'>Interact Psy-able</td><td style='text-align: center; word-wrap: break-word;'>Maturity</td><td style='text-align: center; word-wrap: break-word;'>Authorized</td><td style='text-align: center; word-wrap: break-word;'>Outstanding</td><td style='text-align: center; word-wrap: break-word;'>Five Year Average Income</td><td style='text-align: center; word-wrap: break-word;'>Interest Required Per Annual</td><td style='text-align: center; word-wrap: break-word;'>Times Interest Earned</td><td style='text-align: center; word-wrap: break-word;'>Security</td><td style='text-align: center; word-wrap: break-word;'>Scalability</td><td style='text-align: center; word-wrap: break-word;'>Rating</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>I. Acme Steel Goods Co. 1st 6s.</td><td style='text-align: center; word-wrap: break-word;'>M&amp;S</td><td style='text-align: center; word-wrap: break-word;'>Mr. 1943</td><td style='text-align: center; word-wrap: break-word;'>$3,500,000</td><td style='text-align: center; word-wrap: break-word;'>$1,381,000</td><td style='text-align: center; word-wrap: break-word;'>$1,424,359</td><td style='text-align: center; word-wrap: break-word;'>$82,860</td><td style='text-align: center; word-wrap: break-word;'>17.2</td><td style='text-align: center; word-wrap: break-word;'>High</td><td style='text-align: center; word-wrap: break-word;'>Fair</td><td style='text-align: center; word-wrap: break-word;'>A</td></tr></table>

1. Acme Steel Goods Co. first sinking fund gold 6s, series A: Authorized—$3,500,000; outstanding, $1,381,000; re-Securitized to Dec 31 1927 $119,000

Dated—March 1, 1923; due Ms

Dated—March 1, 1923; due March 1, 1948.

Trustee—Harris Trust & Savings Bank, Chicago.

Denomination—Coupon, $500 and $1,000; interchangeable; registerable as to principal.

Callable—At any time on 60 days' notice at 103 prior to March 1, 1988; at 102 prior to Mar. 1, 1938; at 101 until Sept. 1, 1942; thereafter at par. Bonds may also be purchased or called for the sinking fund (which see).

Sinking Fund—Semi-annually beginning Jan. 1, 1924, sufficient to retire 68% of the issue by maturity by purchase at not exceeding redemption price or if not so obtainable by call at that price. During the years 1928 to 1932 inclusive sinking fund payments shall amount to 3% of the total bonds of this issue; 1933 to 1937 4% annually; 1938 to 1942 incl., 5% annually.

Security—First mortgage on all fixed assets of the company now owned or hereafter acquired. Indenture provides that no cash dividends shall be paid on common except out of earnings, subsequent to January 1, 1923, and in no event when such action will reduce current assets below twice current liabilities, and that no additions to fixed assets shall be made which will reduce current assets below two and one-half times current liabilities.

Additional Bonds—May be issued for 60% of cost or value of additional property and permanent improvements provided net earnings for two years preceding date of proposed issue average at least three times total annual interest charges on all bonds outstanding and “be “

Tax Provisions—Company pays normal income tax up to 2%.

Offered—($1,500,000) at 99 in March, 1923, by Marshall Field, Glore, Ward & Co., New York.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Table B—Stock Records</td><td style='text-align: center; word-wrap: break-word;'>Rate of Dividend</td><td style='text-align: center; word-wrap: break-word;'>Authorized</td><td style='text-align: center; word-wrap: break-word;'>Outstanding</td><td style='text-align: center; word-wrap: break-word;'>Five Year Average Income</td><td style='text-align: center; word-wrap: break-word;'>Dividend Requirement</td><td style='text-align: center; word-wrap: break-word;'>Sability</td><td style='text-align: center; word-wrap: break-word;'>Rating</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1. Active Stock Co. stock</td><td style='text-align: center; word-wrap: break-word;'>See text</td><td style='text-align: center; word-wrap: break-word;'>200,000 sh.</td><td style='text-align: center; word-wrap: break-word;'>182,958 sh.</td><td style='text-align: center; word-wrap: break-word;'>1,164,890</td><td style='text-align: center; word-wrap: break-word;'>914,790 $ ^{*} $</td><td style='text-align: center; word-wrap: break-word;'>Fair</td><td style='text-align: center; word-wrap: break-word;'>Ba</td></tr></table>

egher stock description, see following page.

* To pay $5 per share.

# MOODY'S MANUAL OF INVESTMENTS

annual interest requirements in semi-annual installments, and in addition thereto an amount in cash and/or securities of this issue at their face value sufficient to bring the amount, including interest, up to $850,000 annually during the first five years, as a sinking fund, and annually thereafter an amount in cash and/or securities of this issue at their face value equal to $100,000 as a sinking fund, all such sinking fund payments to be made in equal semi-annual installments. Sinking fund to be applied to purchase or call bonds at not exceeding the call price. Bonds so retired to be cancelled. Secured by a first mortgage on the Munson Building, New York. Legal for trust funds in New York. Free of New York State tax. Pennsylvania and Connecticut 4 mills tax, Maryland 4½ mills tax, District of Columbia 5 mills tax and Massachusetts 6% income tax refunded. Company pays normal income tax up to 2%.

Offered ($4,000,000) at par June, 1924, by Hoagland, Allum & Co., Inc., and A. B. Leach & Co., New York.

CAPITAL STOCK: 1. Munson Steamship Line 6% cum. pref.: Authorized $3,000,000 (increased from $1,000,000 in Dec., 1923); outstanding, $1,104,500; par $100. Has preference as to assets and dividends. Dividends payable quarterly, Jan. 1, etc.

2. Munson Steamship Line common: Authorized, $3,000,000 (increased from $600,000 in Feb., 1917); outstanding, $2,400,000; par $100. Dividends paid, but rate not reported. Stock closely held.

Stock transferred at company's office.

MURPHY VARNISH CO.: Incorporated under the laws of New Jersey, Jan. 9, 1891. Manufactures varnishes, etc.; plants located at Newark, N.J., and Chicago, Ill. Number of employees, Dec. 31, 1927, 225.

MANAGEMENT: OFFICERS: Franklin Murphy, Chirm. of Board, Newark, N. J.; C. J. Roh, Pres., Montclair, N. J.; P. S. Kennedy, Vice-Pres.; Z. Belcher, Jr.; Sec., Newark, N. J.; H. C. Ware, Treas., Orange, N. J.; W. H. DeCamp, Supl., East Orange, N. J. DIRECTORS: Franklin Murphy, P. S. Kennedy, Newark, N. J.; C. J. Roh, Montclair, N. J.; A. J. Beecher, New Haven, Conn.; Charles Bradley, Convent, N. J.; C. M. Baker, Chicago, Ill.; E. F. Hopper, Maplewood, N. J. ANNUAL MEETING: Second Tuesday in January, OFFICE: 224 McWhorter St., Newark, N. J.

CAPITAL STOCK: 1. Murphy Varnish Co. 6% cum. preferred: Authorized and outstanding: $1,500,000; par: $100.

2. Murphy Varnish Co. common: Authorized and outstanding: $1,500,000; par: $100. Stock closely held.

Stock transferred and registered at company's office. Number of stockholders Dec. 31, 1927: Preferred, 235; common, 173.

MUTUAL CHEMICAL CO. OF AMERICA: Incorporated in New Jersey, Oct. 9, 1908. Acquired properties of Baltimore Chrome Works, American Chrome Co., and Mutual Chemical Co. of Jersey City. Plants are located at Baltimore, Md., and Jersey City, N. J. Company is said to be largest producer of bichromate of soda and potash in the United States.

MANAGEMENT: OFFICERS: F. W. White, Pres.; H. M. Kaufmann, Vice-Pres. and Gen. Mgr.; W. H. Bower, 2nd Vice-Pres.; G. G. Henry, Sec. and Treas., New York. DIRECTORS: F. W. White, W. R. Peters, Dr. H. M. Kaufmann, New York; W. H. Bower, F. B. Bower, Philadelphia; J. Beebe, Boston, Mass.; S. W. White, Nutley, N. J. ANNUAL MEETING: Jan. 31, at Jersey City, N. J. OFFICES: 270 Madison Ave., New York; West Side Ave., Jersey City, N. J. and Baltimore, Md.

CAPITAL STOCK: 1. Mutual Chemical Co. of America 6% cum. preferred: Authorized and outstanding, $1,500,000; par $100. Regular dividends paid quarterly, March 31, etc.

2. Mutual Chemical Co. of America common: Authorized, $5,000,000 (increased from $2,000,000 during 1922); outstanding, $4,005,000; par $100. Dividends paid but rate not reported.

Registrar: American Exchange Irving Trust Co., New York.

MUTUAL STORES, INC.: Incorporated in California

Feb. 28, 1927, to succeed Mutual Crommery Co., Inc., incorporated under California laws in 1919. Engaged in the retail food business in Oakland, San Francisco, Berkeley, Alamada, and other California towns, selling groceries, farm products and dairy products. Manufactures ice-cream, butter, baking products, etc. Properties include 58,000 sq. ft. of ground at Fourth Ave. and East Eleventh St., Oakland, on which is a plant with floor space of 36,000 sq. ft.; 5½ acres at Fifty-seventh Ave. and East Fourteenth St., Oakland, on which is another plant; trucks, store fixtures, etc. In Nov., 1927, purchased plant of California Baking Co.

MANAGEMENT: OFFICERS: E. A. Hagstrom, Pres.; Andrew Stockholm, Vice-Pres.; W. B. Rosemond, Sec. and Treas. DIRECTORS: Agnes Hagstrom, E. A. Hagstrom, John Muhelsen, W. B. Rosemond, Andrew Stockholm, GENERAL AUDITORS: Price, Waterhouse & Co. ANNUAL MEETING: First Tuesday in Feb. OFFICE: 425 East 11th St., Oakland, Cal.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>*1927</td><td style='text-align: center; word-wrap: break-word;'>1926</td><td style='text-align: center; word-wrap: break-word;'>1925</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Number of stores</td><td style='text-align: center; word-wrap: break-word;'>185</td><td style='text-align: center; word-wrap: break-word;'>127</td><td style='text-align: center; word-wrap: break-word;'>84</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Capital in business</td><td style='text-align: center; word-wrap: break-word;'>$530,200</td><td style='text-align: center; word-wrap: break-word;'>$369,569</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Store sales</td><td style='text-align: center; word-wrap: break-word;'>$2,735,976</td><td style='text-align: center; word-wrap: break-word;'>6,761,200</td><td style='text-align: center; word-wrap: break-word;'>4,609,674</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Net profits</td><td style='text-align: center; word-wrap: break-word;'>99,257</td><td style='text-align: center; word-wrap: break-word;'>252,701</td><td style='text-align: center; word-wrap: break-word;'>186,497</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Av. sales per store</td><td style='text-align: center; word-wrap: break-word;'>14,789</td><td style='text-align: center; word-wrap: break-word;'>53,238</td><td style='text-align: center; word-wrap: break-word;'>54,877</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Av. profits per store</td><td style='text-align: center; word-wrap: break-word;'>537</td><td style='text-align: center; word-wrap: break-word;'>1,990</td><td style='text-align: center; word-wrap: break-word;'>2,220</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Capital per store</td><td style='text-align: center; word-wrap: break-word;'>4,176</td><td style='text-align: center; word-wrap: break-word;'>4,400</td><td style='text-align: center; word-wrap: break-word;'></td></tr></table>

BALANCE SHEET, as of Feb. 28, 1927 (giving effect to new financing): Capital stock, $710,094; bonded debt, $700,000; accounts payable, $318,910; other current liabilities, $53,003; deferred credits, $245; total, $1,782,252. Contra: Land, buildings and equipment (less depreciation), $529,181; construction account, $350,000; investment, $5,000; cash, $256,300; accounts receivable, $36,166; inventories, $537,245; deferred charges, $68,410; total, $1,782,252.

BONDED DEBT: 1. Mutual Stores, Inc., convertible debenture gold 7s, series of 1937: Authorized, all series, $2,000,000; outstanding, series of 1937, $700,000. Dated Mar. 1, 1927; due Mar. 1, 1937.

Interest paid M&S 1 at Bank of Italy National Trust & Savings Association, San Francisco, Trustee. Coupon, $500 and $1,000. Callable on any interest date on 30 days notice at 105 to Mar. 1, 1928 incl., and at ½% less each year or part thereof thereafter. Convertible into capital stock at any time prior to maturity, or if redeemed before maturity prior to ten days before the redemption date on basis of par for debentures and $50 per share for capital stock, accrued interest on debentures to conversion date to be paid in cash. Sinking fund payable annually and cumulative beginning Mar. 1, 1929 of $35,000. In event debentures are called for redemption and shall, subsequent to such call and prior to ten days before the redemption, be converted into capital stock, sinking fund shall be credited to that extent. Bonds at par may be tendered in lieu of cash.

A direct obligation of the company but not secured by mortgage. Company agrees that it will not mortgage any of its properties, nor create any other indebtedness except (a) purchase money obligations for property other than merchandise, including renewals and substitutions thereof, (b) indebtedness incurred in the usual course of business of no longer than six months' maturity and (c) additional authorized debentures. Additional debentures up to $1,300,000 may be issued in one or more series provided net earnings for twelve months next preceding have been at least twice interest charges on debentures outstanding and to be issued, and further shall be issued only to reimburse company for not exceeding 50% of cost of capital improvements made since issuance of last debentures and shall be issued only when aggregate debentures outstanding and to be issued, shall not exceed 50% of net worth of company, including proceeds from such issue of debenture bonds and excluding bonded indebtedness. Issued for additions to plant, for expansion and for other corporate purposes. California not exceeding 5 mills taxes refunded. Company pays normal income tax up to 2%.

Offered ($700,000) at par in Apr., 1927 by Blyth, Witter & Co., and Mitchum, Tully & Co., San Francisco.

CAPITAL STOCK: 1. Mutual Stores, Inc. stock: Authorized, 150,000 shares; outstanding, 110,000 shares; reserved for conversion, 40,000 shares; no par.

MYERS (F. E.) & BRO. CO.: Incorporated under Ohio laws in 1927 to succeed company of some name incorporated in 1920. Business established in 1878. Manufactures pumps of various types and sizes, water systems for domestic and industrial use, automobile washers, spraying units, hay tools, door hangers, etc.

MANAGEMENT: OFFICERS: P. A. Myers, Pres.; J. C. Myers, G. C. Myers, A. N. Myers, G. D. Myers, Vice-Pres.; F. B. Kellogg, Sec. and Treas., Ashland, O. DIRECTORS: P. A. Myers, J. C. Myers, G. C. Myers, A. N. Myers, G. D. Myers, F. B. Kellogg, Ashland, O.; J. R. Nutt, L. B. Williams, Cleveland, O. GENERAL AUDITORS: Ernst & Ernst. OFFICE: Ashland, O.

NET EARNINGS (after eliminating income from investments in excess of those now owned, increasing depreciation charges to basis of appraised values, allowing for Federal

manual devotes multiple pages. Figure A2 presents page 2892 of the manual, which is a typical page for small firms. Note how in this page we have data on five firms: Munson Steamship Line (entry that starts on page 2891), Murphy Varnish Co., Mutual Chemical Co. of America, Mutual Stores Inc., and Myers (F.E.) & Bro. Co. There is significant

<div style="text-align: center;"><div style="text-align: center;">TABLE A2</div> </div>


<div style="text-align: center;"><div style="text-align: center;">List of Directors with Location from the Moody's 1928 Industrial Manual</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Table A2 reports the list of directors at the first 3 companies listed in the Moody's 1928 Industrial manual. The first column lists the firm, the second column lists the name of the board member, the third and fourth columns list the city and state where the board members are located.</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Company Name</td><td style='text-align: center; word-wrap: break-word;'>Director</td><td style='text-align: center; word-wrap: break-word;'>City</td><td style='text-align: center; word-wrap: break-word;'>State</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Acme Steel Company</td><td style='text-align: center; word-wrap: break-word;'>J. E. MacMurray</td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Acme Steel Company</td><td style='text-align: center; word-wrap: break-word;'>F. C. Gifford</td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Acme Steel Company</td><td style='text-align: center; word-wrap: break-word;'>Donald MacMurray</td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Acme Steel Company</td><td style='text-align: center; word-wrap: break-word;'>E. H. Norton</td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Acme Steel Company</td><td style='text-align: center; word-wrap: break-word;'>L. H. Whiting</td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Acme Steel Company</td><td style='text-align: center; word-wrap: break-word;'>C. S. Traer</td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Acme Steel Company</td><td style='text-align: center; word-wrap: break-word;'>C. MacChesney</td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The American Agricultural Chemical Company</td><td style='text-align: center; word-wrap: break-word;'>Horace Bowker</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The American Agricultural Chemical Company</td><td style='text-align: center; word-wrap: break-word;'>R. S. Bradley</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The American Agricultural Chemical Company</td><td style='text-align: center; word-wrap: break-word;'>Samuel F. Pryor</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The American Agricultural Chemical Company</td><td style='text-align: center; word-wrap: break-word;'>G. C. Clark Jr</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The American Agricultural Chemical Company</td><td style='text-align: center; word-wrap: break-word;'>Geo B. Burton</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The American Agricultural Chemical Company</td><td style='text-align: center; word-wrap: break-word;'>J. F. Dulles</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The American Agricultural Chemical Company</td><td style='text-align: center; word-wrap: break-word;'>J. S. Alexander</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The American Agricultural Chemical Company</td><td style='text-align: center; word-wrap: break-word;'>Charles Hayden</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The American Agricultural Chemical Company</td><td style='text-align: center; word-wrap: break-word;'>George C. Lee</td><td style='text-align: center; word-wrap: break-word;'>Boston</td><td style='text-align: center; word-wrap: break-word;'>Massachusetts</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The American Agricultural Chemical Company</td><td style='text-align: center; word-wrap: break-word;'>Philip Stockton</td><td style='text-align: center; word-wrap: break-word;'>Boston</td><td style='text-align: center; word-wrap: break-word;'>Massachusetts</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The American Agricultural Chemical Company</td><td style='text-align: center; word-wrap: break-word;'>C. B. Whittlesey</td><td style='text-align: center; word-wrap: break-word;'>New London</td><td style='text-align: center; word-wrap: break-word;'>Connecticut</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Chicle Company</td><td style='text-align: center; word-wrap: break-word;'>L. R. Adams</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Chicle Company</td><td style='text-align: center; word-wrap: break-word;'>H. C. Leighton</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Chicle Company</td><td style='text-align: center; word-wrap: break-word;'>H. L. McVickar</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Chicle Company</td><td style='text-align: center; word-wrap: break-word;'>S. T. Britten</td><td style='text-align: center; word-wrap: break-word;'>San Francisco</td><td style='text-align: center; word-wrap: break-word;'>California</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Chicle Company</td><td style='text-align: center; word-wrap: break-word;'>S. B. Adams</td><td style='text-align: center; word-wrap: break-word;'>Portland</td><td style='text-align: center; word-wrap: break-word;'>Maine</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Chicle Company</td><td style='text-align: center; word-wrap: break-word;'>W. S. Pringley</td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Chicle Company</td><td style='text-align: center; word-wrap: break-word;'>T. H. Blodgett</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Chicle Company</td><td style='text-align: center; word-wrap: break-word;'>W. C. Langley</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Chicle Company</td><td style='text-align: center; word-wrap: break-word;'>F. W. Shibley</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Chicle Company</td><td style='text-align: center; word-wrap: break-word;'>H. B. Clark</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr></table>

variation in the scope of coverage, but note how all companies list their management team, board of directors, as well as office location. For a given firm, we obtain information on the management and board of directors by selecting the entries in the Moody's manual that follow the string "MANAGEMENT," or strings that in the OCR output are close to "MANAGEMENT" (e.g., "MGNAGEMENT"). We use natural language processing techniques to parse the text into a database, which involves both typo correction techniques, as well as Named Entity Recognition algorithms. In this step, we obtain the names of each manager and director associated with a given firm as well as their geographic location. Table A2 presents a list of the first few firms appearing in the manual and of their directors, together with location information, from the 1928 Industrial manual. We obtain similar information on the firms' management and combine the management and director information for each firm, eliminating duplicate observations for people who appear as both executives and directors. We use this list to construct the network.

#### B. Firm Accounting, Survival, and M&A Information

We obtain data on balance sheet and income statement variables from the 1928 Moody's Industrial manual by hiring research assistants who manually inputted each firm's information. To identify private firms, we collect information on exchanges where firms list their equity shares. Firms with no listed equity are defined as private firms.

To define our main dependent variables on future survival and M&A status of firms in the 1928 Moody's Industrial manual, we obtain information on reasons for firm

#### ADDITIONAL U. S. AND CANADIAN COMPANIES FORMERLY INCLUDED

The following companies which appeared in previous editions (1928-37) of the Industrial Manual have been dropped. The date in parentheses indicates last edition in which statement appeared.

NOTE: For statements of banks, insurance companies, investment trusts, finance, mortgage and real estate companies, formerly included in the Industrial Manual, see Moody's Bank, Insurance and Financial Manual.

A. No. 1.

B. No. 2.

C. No. 3.

D. No. 4.

E. No. 5.

F. No. 6.

G. No. 7.

H. No. 8.

I. No. 9.

J. No. 10.

K. No. 11.

L. No. 12.

M. No. 13.

N. No. 14.

O. No. 15.

P. No. 16.

Q. No. 17.

R. No. 18.

S. No. 19.

T. No. 20.

U. No. 21.

V. No. 22.

W. No. 23.

X. No. 24.

Y. No. 25.

Z. No. 26.

A. No. 27.

B. No. 28.

C. No. 29.

D. No. 30.

E. No. 31.

F. No. 32.

G. No. 33.

H. No. 34.

I. No. 35.

J. No. 36.

K. No. 37.

L. No. 38.

M. No. 39.

N. No. 40.

O. No. 41.

P. No. 42.

Q. No. 43.

R. No. 44.

S. No. 45.

T. No. 46.

U. No. 47.

V. No. 48.

W. No. 49.

X. No. 50.

Y. No. 51.

Z. No. 52.

A. No. 53.

B. No. 54.

C. No. 55.

D. No. 56.

E. No. 57.

F. No. 58.

G. No. 59.

H. No. 60.

I. No. 61.

J. No. 62.

K. No. 63.

L. No. 64.

M. No. 65.

N. No. 66.

O. No. 67.

P. No. 68.

Q. No. 69.

R. No. 70.

S. No. 71.

T. No. 72.

U. No. 73.

V. No. 74.

W. No. 75.

X. No. 76.

Y. No. 77.

Z. No. 78.

A. No. 79.

B. No. 80.

C. No. 81.

D. No. 82.

E. No. 83.

F. No. 84.

G. No. 85.

H. No. 86.

I. No. 87.

J. No. 88.

K. No. 89.

L. No. 90.

M. No. 91.

N. No. 92.

O. No. 93.

P. No. 94.

Q. No. 95.

R. No. 96.

S. No. 97.

T. No. 98.

U. No. 99.

V. No. 100.

W. No. 101.

X. No. 102.

Y. No. 103.

Z. No. 104.

A. No. 105.

B. No. 106.

C. No. 107.

D. No. 108.

E. No. 109.

F. No. 110.

G. No. 111.

H. No. 112.

I. No. 113.

J. No. 114.

K. No. 115.

L. No. 116.

M. No. 117.

N. No. 118.

O. No. 119.

P. No. 120.

Q. No. 121.

R. No. 122.

S. No. 123.

T. No. 124.

U. No. 125.

V. No. 126.

W. No. 127.

X. No. 128.

Y. No. 129.

Z. No. 130.

A. No. 131.

B. No. 132.

C. No. 133.

D. No. 134.

E. No. 135.

F. No. 136.

G. No. 137.

H. No. 138.

I. No. 139.

J. No. 140.

K. No. 141.

L. No. 142.

M. No. 143.

N. No. 144.

O. No. 145.

P. No. 146.

Q. No. 147.

R. No. 148.

S. No. 149.

T. No. 150.

U. No. 151.

V. No. 152.

W. No. 153.

X. No. 154.

Y. No. 155.

Z. No. 156.

A. No. 157.

B. No. 158.

C. No. 159.

D. No. 160.

E. No. 161.

F. No. 162.

G. No. 163.

H. No. 164.

I. No. 165.

J. No. 166.

K. No. 167.

L. No. 168.

M. No. 169.

N. No. 170.

O. No. 171.

P. No. 172.

Q. No. 173.

R. No. 174.

S. No. 175.

T. No. 176.

U. No. 177.

V. No. 178.

W. No. 179.

X. No. 180.

Y. No. 181.

Z. No. 182.

A. No. 183.

B. No. 184.

C. No. 185.

D. No. 186.

E. No. 187.

F. No. 188.

G. No. 189.

H. No. 190.

I. No. 191.

J. No. 192.

K. No. 193.

L. No. 194.

M. No. 195.

N. No. 196.

O. No. 197.

P. No. 198.

Q. No. 199.

R. No. 200.

S. No. 201.

T. No. 202.

U. No. 203.

V. No. 204.

W. No. 205.

X. No. 206.

Y. No. 207.

Z. No. 208.

A. No. 209.

B. No. 210.

C. No. 211.

D. No. 212.

E. No. 213.

F. No. 214.

G. No. 215.

H. No. 216.

I. No. 217.

J. No. 218.

K. No. 219.

L. No. 220.

M. No. 221.

N. No. 222.

O. No. 223.

P. No. 224.

Q. No. 225.

R. No. 226.

S. No. 227.

T. No. 228.

U. No. 229.

V. No. 230.

W. No. 231.

X. No. 232.

Y. No. 233.

Z. No. 234.

A. No. 235.

B. No. 236.

C. No. 237.

D. No. 238.

E. No. 239.

F. No. 240.

G. No. 241.

H. No. 242.

I. No. 243.

J. No. 244.

K. No. 245.

L. No. 246.

M. No. 247.

N. No. 248.

O. No. 249.

P. No. 250.

Q. No. 251.

R. No. 252.

S. No. 253.

T. No. 254.

U. No. 255.

V. No. 256.

W. No. 257.

X. No. 258.

Y. No. 259.

Z. No. 260.

A. No. 261.

B. No. 262.

C. No. 263.

D. No. 264.

E. No. 265.

F. No. 266.

G. No. 267.

H. No. 268.

I. No. 269.

J. No. 270.

K. No. 271.

L. No. 272.

M. No. 273.

N. No. 274.

O. No. 275.

P. No. 276.

Q. No. 277.

R. No. 278.

S. No. 279.

T. No. 280.

U. No. 281.

V. No. 282.

W. No. 283.

X. No. 284.

Y. No. 285.

Z. No. 286.

A. No. 287.

B. No. 288.

C. No. 289.

D. No. 290.

E. No. 291.

F. No. 292.

G. No. 293.

H. No. 294.

I. No. 295.

J. No. 296.

K. No. 297.

L. No. 298.

M. No. 299.

N. No. 300.

O. No. 301.

P. No. 302.

Q. No. 303.

R. No. 304.

S. No. 305.

T. No. 306.

U. No. 307.

V. No. 308.

W. No. 309.

X. No. 310.

Y. No. 311.

Z. No. 312.

A. No. 313.

B. No. 314.

C. No. 315.

D. No. 316.

E. No. 317.

F. No. 318.

G. No. 319.

H. No. 320.

I. No. 321.

J. No. 322.

K. No. 323.

L. No. 324.

M. No. 325.

N. No. 326.

O. No. 327.

P. No. 328.

Q. No. 329.

R. No. 330.

S. No. 331.

T. No. 332.

U. No. 333.

V. No. 334.

W. No. 335.

X. No. 336.

Y. No. 337.

Z. No. 338.

A. No. 339.

B. No. 340.

C. No. 341.

D. No. 342.

E. No. 343.

F. No. 344.

G. No. 345.

H. No. 346.

I. No. 347.

J. No. 348.

K. No. 349.

L. No. 350.

M. No. 351.

N. No. 352.

O. No. 353.

P. No. 354.

Q. No. 355.

R. No. 356.

S. No. 357.

T. No. 358.

U. No. 359.

V. No. 360.

W. No. 361.

X. No. 362.

Y. No. 363.

Z. No. 364.

A. No. 365.

B. No. 366.

C. No. 367.

D. No. 368.

E. No. 369.

F. No. 370.

G. No. 371.

H. No. 372.

I. No. 373.

J. No. 374.

K. No. 375.

L. No. 376.

M. No. 377.

N. No. 378.

O. No. 379.

P. No. 380.

Q. No. 381.

R. No. 382.

S.

ALADIN INDUSTRIES INC. (1952)

No public interest

ALAMIDA BUGAR CO. (1984)

Allianz Group, Inc. (1923)

Allianz Group, Inc. (1924)

Allianz Group, Inc. (1925)

Allianz Group, Inc. (1926)

Allianz Group, Inc. (1927)

Allianz Group, Inc. (1928)

Allianz Group, Inc. (1929)

Allianz Group, Inc. (1930)

Allianz Group, Inc. (1931)

Allianz Group, Inc. (1932)

Allianz Group, Inc. (1933)

Allianz Group, Inc. (1934)

Allianz Group, Inc. (1935)

Allianz Group, Inc. (1936)

Allianz Group, Inc. (1937)

Allianz Group, Inc. (1938)

Allianz Group, Inc. (1939)

Allianz Group, Inc. (1940)

Allianz Group, Inc. (1941)

Allianz Group, Inc. (1942)

Allianz Group, Inc. (1943)

Allianz Group, Inc. (1944)

Allianz Group, Inc. (1945)

Allianz Group, Inc. (1946)

Allianz Group, Inc. (1947)

Allianz Group, Inc. (1948)

Allianz Group, Inc. (1949)

Allianz Group, Inc. (1950)

Allianz Group, Inc. (1951)

Allianz Group, Inc. (1952)

Allianz Group, Inc. (1953)

Allianz Group, Inc. (1954)

Allianz Group, Inc. (1955)

Allianz Group, Inc. (1956)

Allianz Group, Inc. (1957)

Allianz Group, Inc. (1958)

Allianz Group, Inc. (1959)

Allianz Group, Inc. (1960)

Allianz Group, Inc. (1961)

Allianz Group, Inc. (1962)

Allianz Group, Inc. (1963)

Allianz Group, Inc. (1964)

Allianz Group, Inc. (1965)

Allianz Group, Inc. (1966)

Allianz Group, Inc. (1967)

Allianz Group, Inc. (1968)

Allianz Group, Inc. (1969)

Allianz Group, Inc. (1970)

Allianz Group, Inc. (1971)

Allianz Group, Inc. (1972)

Allianz Group, Inc. (1973)

Allianz Group, Inc. (1974)

Allianz Group, Inc. (1975)

Allianz Group, Inc. (1976)

Allianz Group, Inc. (1977)

Allianz Group, Inc. (1978)

Allianz Group, Inc. (1979)

Allianz Group, Inc. (1980)

Allianz Group, Inc. (1981)

Allianz Group, Inc. (1982)

Allianz Group, Inc. (1983)

Allianz Group, Inc. (1984)

Allianz Group, Inc. (1985)

Allianz Group, Inc. (1986)

Allianz Group, Inc. (1987)

Allianz Group, Inc. (1988)

Allianz Group, Inc. (1989)

Allianz Group, Inc. (1990)

Allianz Group, Inc. (1991)

Allianz Group, Inc. (1992)

Allianz Group, Inc. (1993)

Allianz Group, Inc. (1994)

Allianz Group, Inc. (1995)

Allianz Group, Inc. (1996)

Allianz Group, Inc. (1997)

Allianz Group, Inc. (1998)

Allianz Group, Inc. (1999)

Allianz Group, Inc. (2000)

Allianz Group, Inc. (2001)

Allianz Group, Inc. (2002)

Allianz Group, Inc. (2003)

Allianz Group, Inc. (2004)

Allianz Group, Inc. (2005)

Allianz Group, Inc. (2006)

Allianz Group, Inc. (2007)

Allianz Group, Inc. (2008)

Allianz Group, Inc. (2009)

Allianz Group, Inc. (2010)

Allianz Group, Inc. (2011)

Allianz Group, Inc. (2012)

Allianz Group, Inc. (2013)

Allianz Group, Inc. (2014)

Allianz Group, Inc. (2015)

Allianz Group, Inc. (2016)

Allianz Group, Inc. (2017)

Allianz Group, Inc. (2018)

Allianz Group, Inc. (2019)

Allianz Group, Inc. (2020)

Allianz Group, Inc. (2021)

Allianz Group, Inc. (2022)

Allianz Group, Inc. (2023)

Allianz Group, Inc. (2024)

Allianz Group, Inc. (2025)

Allianz Group, Inc. (2026)

Allianz Group, Inc. (2027)

Allianz Group, Inc. (2028)

Allianz Group, Inc. (2029)

Allianz Group, Inc. (2030)

Allianz Group, Inc. (2031)

Allianz Group, Inc. (2032)

Allianz Group, Inc. (2033)

Allianz Group, Inc. (2034)

Allianz Group, Inc. (2035)

Allianz Group, Inc. (2036)

Allianz Group, Inc. (2037)

Allianz Group, Inc. (2038)

Allianz Group, Inc. (2039)

Allianz Group, Inc. (2040)

Allianz Group, Inc. (2041)

Allianz Group, Inc. (2042)

Allianz Group, Inc. (2043)

Allianz Group, Inc. (2044)

Allianz Group, Inc. (2045)

Allianz Group, Inc. (2046)

Allianz Group, Inc. (2047)

Allianz Group, Inc. (2048)

Allianz Group, Inc. (2049)

Allianz Group, Inc. (2050)

Allianz Group, Inc. (2051)

Allianz Group, Inc. (2052)

Allianz Group, Inc. (2053)

Allianz Group, Inc. (2054)

Allianz Group, Inc. (2055)

Allianz Group, Inc. (2056)

Allianz Group, Inc. (2057)

Allianz Group, Inc. (2058)

Allianz Group, Inc. (2059)

Allianz Group, Inc. (2060)

Allianz Group, Inc. (2061)

Allianz Group, Inc. (2062)

Allianz Group, Inc. (2063)

Allianz Group, Inc. (2064)

Allianz Group, Inc. (2065)

Allianz Group, Inc. (2066)

Allianz Group, Inc. (2067)

Allianz Group, Inc. (2068)

Allianz Group, Inc. (2069)

Allianz Group, Inc. (2070)

Allianz Group, Inc. (2071)

Allianz Group, Inc. (2072)

Allianz Group, Inc. (2073)

Allianz Group, Inc. (2074)

Allianz Group, Inc. (2075)

Allianz Group, Inc. (2076)

Allianz Group, Inc. (2077)

Allianz Group, Inc. (2078)

Allianz Group, Inc. (2079)

Allianz Group, Inc. (2080)

Allianz Group, Inc. (2081)

Allianz Group, Inc. (2082)

Allianz Group, Inc. (2083)

Allianz Group, Inc. (2084)

Allianz Group, Inc. (2085)

Allianz Group, Inc. (2086)

Allianz Group, Inc. (2087)

Allianz Group, Inc. (2088)

Allianz Group, Inc. (2089)

Allianz Group, Inc. (2090)

Allianz Group, Inc. (2091)

Allianz Group, Inc. (2092)

Allianz Group, Inc. (2093)

Allianz Group, Inc. (2094)

Allianz Group, Inc. (2095)

Allianz Group, Inc. (2096)

Allianz Group, Inc. (2097)

Allianz Group, Inc. (2098)

Allianz Group, Inc. (2099)

Allianz Group, Inc. (2000)

Allianz Group, Inc. (2001)

Allianz Group, Inc. (2002)

Allianz Group, Inc. (2003)

Allianz Group, Inc. (2004)

Allianz Group, Inc. (2005)

Allianz Group, Inc. (2006)

Allianz Group, Inc. (2007)

Allianz Group, Inc. (2008)

Allianz Group, Inc. (2009)

Allianz Group, Inc. (2010)

Allianz Group, Inc. (2011)

Allianz Group, Inc. (2012)

Allianz Group, Inc. (2013)

Allianz Group, Inc. (2014)

Allianz Group, Inc. (2015)

Allianz Group, Inc. (2016)

Allianz Group, Inc. (2017)

Allianz Group, Inc. (2018)

Allianz Group, Inc. (2019)

Allianz Group, Inc. (2020)

Allianz Group, Inc. (2021)

Allianz Group, Inc. (2022)

Allianz Group, Inc. (2023)

Allianz Group, Inc. (2024)

Allianz Group, Inc. (2025)

Allianz Group, Inc. (2026)

Allianz Group, Inc. (2027)

Allianz Group, Inc. (2028)

Allianz Group, Inc. (2029)

Allianz Group, Inc. (2030)

Allianz Group, Inc. (2031)

Allianz Group, Inc. (2032)

Allianz Group, Inc. (2033)

Allianz Group, Inc. (2034)

Allianz Group, Inc. (2035)

Allianz Group, Inc. (2036)

Allianz Group, Inc. (2037)

Allianz Group, Inc. (2038)

Allianz Group, Inc. (2039)

Allianz Group, Inc. (2040)

Allianz Group, Inc. (2041)

Allianz Group, Inc. (2042)

Allianz Group, Inc. (2043)

Allianz Group, Inc. (2044)

Allianz Group, Inc. (2045)

Allianz Group, Inc. (2046)

Allianz Group, Inc. (2047)

Allianz Group, Inc. (2048)

Allianz Group, Inc. (2049)

Allianz Group, Inc. (2050)

Allianz Group, Inc. (2051)

Allianz Group, Inc. (2052)

Allianz Group, Inc. (2053)

Allianz Group, Inc. (2054)

Allianz Group, Inc. (2055)

Allianz Group, Inc. (2056)

Allianz Group, Inc. (2057)

Allianz Group, Inc. (2058)

Allianz Group, Inc. (2059)

Allianz Group, Inc. (2060)

Allianz Group, Inc. (2061)

Allianz Group, Inc. (2062)

Allianz Group, Inc. (2063)

Allianz Group, Inc. (2064)

Allianz Group, Inc. (2065)

Allianz Group, Inc. (2066)

Allianz Group, Inc. (2067)

Allianz Group, Inc. (2068)

Allianz Group, Inc. (2069)

Allianz Group, Inc. (2070)

Allianz Group, Inc. (2071)

Allianz Group, Inc. (2072)

Allianz Group, Inc. (2073)

Allianz Group, Inc. (2074)

Allianz Group, Inc. (2075)

Allianz Group, Inc. (2076)

Allianz Group, Inc. (2077)

Allianz Group, Inc. (2078)

Allianz Group, Inc. (2079)

Allianz Group, Inc. (2080)

Allianz Group, Inc. (2081)

Allianz Group, Inc. (2082)

Allianz Group, Inc. (2083)

Allianz Group, Inc. (2084)

Allianz Group, Inc. (2085)

Allianz Group, Inc. (2086)

Allianz Group, Inc. (2087)

Allianz Group, Inc. (2088)

Allianz Group, Inc. (2089)

Allianz Group, Inc. (2090)

Allianz Group, Inc. (2091)

Allianz Group, Inc. (2092)

Allianz Group, Inc. (2093)

Allianz Group, Inc. (2094)

Allianz Group, Inc. (2095)

Al

AMERICAN BOSCH MAGNISO CORP. (1980)

Name changed to United American Bosch

Corp.

AMERICAN CHASTATION CORP. (1982)

AMERICAN RAIRO & TILMATION STORES CORP.

(1932). No recent information

exit from the Moody’s manual coverage. Specifically, the 1938 Moody’s Industrial manual contains the list of “ADDITIONAL U. S. AND CANADIAN COMPANIES FORMERLY INCLUDED,” which provides the list of companies which appeared in previous editions (1928–1937) of the Industrial manual but have been dropped as well as the reason for dropping coverage. Figure B1 shows an example of the list (its first page).

We use this list to determine firms from the 1928 Moody's Industrial manual that were dropped from coverage and to identify the reason for the exit. We define our key dependent variables as follows: The indicator variable DISAPPEARED_BY_1937 equals 1 for firms in the 1928 Moody's Industrial manual that over the subsequent 10-year period were dropped from coverage for one of the following reasons: going bankrupt, liquidated, reorganized, foreclosed, dissolved, sold at foreclosure, no public interest, or due to Moody's inability to find information on that firm. The indicator variable ACQUIRED_BY_1937 equals 1 for firms in the 1928 Moody's Industrial manual that over the subsequent 10-year period were dropped from coverage because they were acquired or merged with another firm. Cases in which the firm is the target of an acquisition vastly outnumber cases in which the firm merges with another firm: Out of 326 firms that exit due to M&A activity, 17.8% of firms are merged into another firm and 82.2% are acquired.

#### C. Other Cross-Sectional Information

##### C1. Office Location

We also obtain the data on the office location(s) of the firm, which always follows the information on the auditors and the annual meeting date for shareholders of the firm. Table C1 presents the office information that we parse out using natural language processing techniques, again for the first set of firms in the 1928 Industrial manual. We use this information to define state fixed effects (dummy variables equal to 1 for a given state if a firm has an office in that state; since a firm can have offices in several states, it can have several state dummies equal to 1). We also use the state information to define firms as either rural (indicator variable RURAL = 1) or urban (RURAL = 0). The indicator variable RURAL takes the value of 1 if the rural population in the state(s) in which the firm operates (defined using publicly available data from the 1930 U.S. Census) is in the top three quartiles of the distribution.

##### C2. Industry Information

Pages xvii–xliv of the 1928 Moody’s Industrial manual contain details on “The Nation’s Basic Industries.” This section of the manual gives both tables with sales, production, wages, prices, as well as qualitative information on each of the industries. We augment this list of qualitative information for each industry with the information in pages xlv–lv, which includes an alphabetical index of “The principal commodities, industries, articles, etc., carried in this volume.”

The following list gives the 25 different industries we consider, together with the strings that we associate with each of the industries.

1. Steel and Iron: steel, iron, rolled, forge, slab, billet, tonnage

2. Coal: coal, anthrac, bitumi, coke

3. Textile, Silk and Wool: textile, shirt, apparel, cloth, cotton, silk, wool, fall river, woolen, knit, yarn, cloth, worsted, towels, hosiery, fabric, laundr, wear, underwear, corset

4. Motor: motor, automo, airplane, aircraft, truck, road, tire

5. Rubber: rubber, tires, tire fabric, belting

6. Petroleum: petroleum, benzol, gasoline, crude, refin, oil, gas, tar, pipe

7. Copper: copper, metal

<div style="text-align: center;"><div style="text-align: center;">TABLE C1</div> </div>


<div style="text-align: center;"><div style="text-align: center;">List of Main Offices from the Moody's 1928 Industrial Manual</div> </div>


Table C1 reports the main offices of companies, as listed in the Moody's 1928 Industrial manual. The first column lists the firm name, the second column lists the street, then the city and the state. Note how the Moody's manual often includes more than one office per firm.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Company Name</td><td style='text-align: center; word-wrap: break-word;'>Street</td><td style='text-align: center; word-wrap: break-word;'>City</td><td style='text-align: center; word-wrap: break-word;'>State</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Acme Steel</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Agric. Chemical</td><td style='text-align: center; word-wrap: break-word;'>420 Lexington Ave.</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Chicle</td><td style='text-align: center; word-wrap: break-word;'>Manly St.</td><td style='text-align: center; word-wrap: break-word;'>Long Island City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Cyanamid</td><td style='text-align: center; word-wrap: break-word;'>535 Fifth Avenue</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Amalgamated Phosphate</td><td style='text-align: center; word-wrap: break-word;'>535 Fifth Ave.</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The American Hardware</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>New Britain</td><td style='text-align: center; word-wrap: break-word;'>Connecticut</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The American Ship Building</td><td style='text-align: center; word-wrap: break-word;'>West 54th St.</td><td style='text-align: center; word-wrap: break-word;'>Cleveland</td><td style='text-align: center; word-wrap: break-word;'>Ohio</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Snuff</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Memphis</td><td style='text-align: center; word-wrap: break-word;'>Tennessee</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Sumatra Tobacco</td><td style='text-align: center; word-wrap: break-word;'>131 Water St.</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Type Founders</td><td style='text-align: center; word-wrap: break-word;'>300 Communipaw Ave.</td><td style='text-align: center; word-wrap: break-word;'>Jersey City</td><td style='text-align: center; word-wrap: break-word;'>New Jersey</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Type Founders</td><td style='text-align: center; word-wrap: break-word;'>96 Beekman St.</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Barnhart Brothers &amp; Spindler</td><td style='text-align: center; word-wrap: break-word;'>Throop Sts.</td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Barnhart Brothers &amp; Spindler</td><td style='text-align: center; word-wrap: break-word;'>300 Communipaw Ave</td><td style='text-align: center; word-wrap: break-word;'>Jersey City</td><td style='text-align: center; word-wrap: break-word;'>New Jersey</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>National Paper &amp; Type</td><td style='text-align: center; word-wrap: break-word;'>38 Burling blip</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Vitrified Products</td><td style='text-align: center; word-wrap: break-word;'>15 Broad St.</td><td style='text-align: center; word-wrap: break-word;'>Akron</td><td style='text-align: center; word-wrap: break-word;'>Ohio</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Vitrified Products</td><td style='text-align: center; word-wrap: break-word;'>Oliver Building.</td><td style='text-align: center; word-wrap: break-word;'>Pittsburgh</td><td style='text-align: center; word-wrap: break-word;'>Pennsylvania</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Wholesale</td><td style='text-align: center; word-wrap: break-word;'>354 Fourth Ave</td><td style='text-align: center; word-wrap: break-word;'>Baltimore</td><td style='text-align: center; word-wrap: break-word;'>Maryland</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Window Glass Machine</td><td style='text-align: center; word-wrap: break-word;'>Farmers Bank Building</td><td style='text-align: center; word-wrap: break-word;'>Pittsburgh</td><td style='text-align: center; word-wrap: break-word;'>Pennsylvania</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>American Window Glass</td><td style='text-align: center; word-wrap: break-word;'>1 Madison Ave.</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Amoskeag Manufacturing</td><td style='text-align: center; word-wrap: break-word;'>10 State St.</td><td style='text-align: center; word-wrap: break-word;'>Boston</td><td style='text-align: center; word-wrap: break-word;'>Massachusetts</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Amoskeag Manufacturing</td><td style='text-align: center; word-wrap: break-word;'>34 Thomas St.</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Archer-Daniels-Midland</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Minneapolis</td><td style='text-align: center; word-wrap: break-word;'>Minnesota</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Arlington Mills</td><td style='text-align: center; word-wrap: break-word;'>78 Chauncey Street</td><td style='text-align: center; word-wrap: break-word;'>Boston</td><td style='text-align: center; word-wrap: break-word;'>Massachusetts</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The Arundel Co.</td><td style='text-align: center; word-wrap: break-word;'>Pier 2 Pratt St.</td><td style='text-align: center; word-wrap: break-word;'>Baltimore</td><td style='text-align: center; word-wrap: break-word;'>Maryland</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Atlas Powder Co.</td><td style='text-align: center; word-wrap: break-word;'>Market Sts.</td><td style='text-align: center; word-wrap: break-word;'>Wilmington</td><td style='text-align: center; word-wrap: break-word;'>Delaware</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Belding Heminway</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Rockville</td><td style='text-align: center; word-wrap: break-word;'>Connecticut</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Belding Heminway</td><td style='text-align: center; word-wrap: break-word;'>Madison Ave. &amp; 34th St.</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Brown Co.</td><td style='text-align: center; word-wrap: break-word;'>110 So. Dearborn St.</td><td style='text-align: center; word-wrap: break-word;'>Portland</td><td style='text-align: center; word-wrap: break-word;'>Maine</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Brown Co.</td><td style='text-align: center; word-wrap: break-word;'>233 Broadway.</td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Brown Co.</td><td style='text-align: center; word-wrap: break-word;'>233 Broadway.</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Brown Shoe Inc.</td><td style='text-align: center; word-wrap: break-word;'>Seventeenth St.</td><td style='text-align: center; word-wrap: break-word;'>Quebec</td><td style='text-align: center; word-wrap: break-word;'>Canada</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Butler Brothers</td><td style='text-align: center; word-wrap: break-word;'>Canal Sts.</td><td style='text-align: center; word-wrap: break-word;'>St. Louis</td><td style='text-align: center; word-wrap: break-word;'>Missouri</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>A M Byers</td><td style='text-align: center; word-wrap: break-word;'>235 Water St.</td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Central Aguirre Sugar</td><td style='text-align: center; word-wrap: break-word;'>45 Milk St.</td><td style='text-align: center; word-wrap: break-word;'>Pittsburgh</td><td style='text-align: center; word-wrap: break-word;'>Pennsylvania</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Central Aguirre Sugar</td><td style='text-align: center; word-wrap: break-word;'>129 Front St.</td><td style='text-align: center; word-wrap: break-word;'>Aguirre</td><td style='text-align: center; word-wrap: break-word;'>Porto Rico</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Central Aguirre Sugar</td><td style='text-align: center; word-wrap: break-word;'>129 Front St.</td><td style='text-align: center; word-wrap: break-word;'>Boston</td><td style='text-align: center; word-wrap: break-word;'>Massachusetts</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Clinchfield Coal</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Cluett Peabody &amp; Co. Inc.</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Dante</td><td style='text-align: center; word-wrap: break-word;'>Virginia</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Continental Motors</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Troy</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Crucible Steel of America</td><td style='text-align: center; word-wrap: break-word;'>17 East 42nd Street</td><td style='text-align: center; word-wrap: break-word;'>Detroit</td><td style='text-align: center; word-wrap: break-word;'>Michigan</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Crucible Steel of America</td><td style='text-align: center; word-wrap: break-word;'>15 Exchange Place</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Cuba Cane Sugar</td><td style='text-align: center; word-wrap: break-word;'>Moron</td><td style='text-align: center; word-wrap: break-word;'>Jersey City</td><td style='text-align: center; word-wrap: break-word;'>New Jersey</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Cuba Cane Sugar</td><td style='text-align: center; word-wrap: break-word;'>123 Front St.</td><td style='text-align: center; word-wrap: break-word;'>Camaguey</td><td style='text-align: center; word-wrap: break-word;'>Cuba</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Eastern Cuba Sugar</td><td style='text-align: center; word-wrap: break-word;'>Moron</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The Cuban-American Sugar</td><td style='text-align: center; word-wrap: break-word;'>136 Front St.</td><td style='text-align: center; word-wrap: break-word;'>Camaguey</td><td style='text-align: center; word-wrap: break-word;'>Cuba</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>The Cudahy Packing</td><td style='text-align: center; word-wrap: break-word;'>111 West Monroe St.</td><td style='text-align: center; word-wrap: break-word;'>New York City</td><td style='text-align: center; word-wrap: break-word;'>New York</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Alfred Decker &amp; Cohn Inc.</td><td style='text-align: center; word-wrap: break-word;'>Market Sts.</td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Alfred Decker &amp; Cohn Inc.</td><td style='text-align: center; word-wrap: break-word;'>200 Fifth Ave.</td><td style='text-align: center; word-wrap: break-word;'>Chicago</td><td style='text-align: center; word-wrap: break-word;'>Illinois</td></tr></table>

8. Equipment: equipment, car, bolts, freight, locomotive, railroad, valve, stove, passenger, foundry, machine, typewri, refrigerator, boiler, tubes, turbin, heater

9. Sugar: sugar confect sweet

10. Tobacco: tobacco, cigar, leaf, snuff, chew

11. Packing: packing, cattle, hog, meat, sheep, animal, pork, beef, slaughter, canned

12. Shoe and leather: shoe, leather

13. Retail trading: retail, store, grocer, music, piano, organ, grocery, candy, drug, mail.order, cigar.store, dry good, light, neon, lamp

14. Fertilizer: fertilizer, farm, crop, potash, phosph, nitrat, ammonium, sulphate, sulphur

15. Shipping: ship, dredg, yards, dock, marine, ocean, idle tonnage, freight, charter, liner, boat, sea, steam, wharf

16. Building: building, hardware, construct, lock, cement, lumber, asphalt, built, roof, asbesto, portland cem, glass, brick, plumb, realty, tile, tiling, paint, furniture

17. Paper: paper, fiber, newsprint, print, pulp, wood, book, board, wrapping, bag, tissue, felt, timber, publish, press

18. Food: food, grain, juice, molas, salt, soda, fruit, ice, butter, spice, soup, cream, milk, dairy, dairi, chocolat, coffee, cocoa, water, rice, bake, bakin, butcher, bottl, cereal, flour, beer, agricul, alcohol, beverage, biscuit, brew, wine, ale

19. Manufacturing: manufacturing, mfg

20. Entertainment: theat, fil, hotel, radio

21. Mining: mine, mines, minin., gold, silver, zinc, bronze, lead, tin, nickel

22. Electrical/Chemical: wire, cable, brass, power, electric, chemical, enginee, furnace

23. Mills: mill, milling

24. Storage: warehouse, storage

25. Miscellanea: pharma, magnet, batteries, battery, signal

We use regexes to decide whether a firm is in a given industry, checking the list of words for each industry against the whole entry for a given firm in the manual. We use the whole corpus of text we assign to a given company when defining industries. We note that in the above list the expressions between commas should be read as a regex (i.e., l.ght refers to strings that start with the letter “l,” followed by any other symbol, and then the string “ght”).

We use firm industry information to define industry fixed effects in the following way: We count the total number of words associated with an industry B appearing in the text for a given firm A. To define industry dummies, we set an indicator variable for an industry B of a given firm A equal to 1 if the count of words associated with the industry B in firm's A text comprises at least 25% of the total industry words we identify in A's text. Thus, similar to state fixed effects, a firm might have several industry dummies equal to 1.

We validate our industry classification in the following two ways. First, we estimate the variation that our industry fixed effects explain in a corporate finance variable that is known to have large cross-industry differences (firm financial leverage). In particular, we estimate an OLS regression in which we explain firm leverage with our industry fixed effects. We find that our industry fixed effects explain 8.3% of variation in firm leverage. These regressions are presented in Table C2. We then repeat this exercise with the Compustat/CRSP data. In particular, we use three cross sections (to match the cross-sectional nature of our data) in 1980, 1990, and 2000. Using CRSP industry codes (which, unlike Compustat codes, are dynamic through time), we assign firms to Fama–French 30 industries, which are the closest in count to our 25 industry groups. We exclude financial firms and utilities, since these are not included in the industrial manuals and hence are not in our sample. This step leaves us with 28 Fama–French industries. We find that CRSP-derived industry fixed effects explain 4.5%, 5.4%, and 14.6% of variation in leverage for the 1980, 1990, and 2000 cross sections, respectively. Comparing the  $ R^{2} $ in our and the Compustat samples, our industry fixed effects appear to explain a similar amount of variation in leverage to standard industry measures used in modern samples.

<div style="text-align: center;"><div style="text-align: center;">TABLE C2</div> </div>


##### Industry Classification Validation

Coefficient estimates in Table C2 are from OLS regressions on the sample of firms from the 1928 Moody's Industrial manual, excluding foreign firms and subsidiaries. The dependent variable is firm financial leverage (debt scaled by assets). All variables are measured as of 1928. FIRM_AGE is measured as 1928 minus the year of establishment. PRIVATE is an indicator variable equal to 1 for firms without publicly traded equity. TOTAL_ASSETS, DEBT/ASSETS, and CASH/ASSETS are winsorized at the 1% level. Standard errors that are robust to heteroscedasticity are reported in parentheses. *, **, and *** indicate significance at the 10%, 5%, and 1% levels, respectively.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>5</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(\text{TOTAL\_ASSETS}) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.018*** (0.002)</td><td style='text-align: center; word-wrap: break-word;'>0.017*** (0.003)</td><td style='text-align: center; word-wrap: break-word;'>0.017*** (0.003)</td><td style='text-align: center; word-wrap: break-word;'>0.016*** (0.003)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>PRIVATE</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.043*** (0.005)</td><td style='text-align: center; word-wrap: break-word;'>0.028*** (0.006)</td><td style='text-align: center; word-wrap: break-word;'>0.044*** (0.006)</td><td style='text-align: center; word-wrap: break-word;'>0.031*** (0.006)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CASH/ASSETS</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.317*** (0.023)</td><td style='text-align: center; word-wrap: break-word;'>-0.298*** (0.024)</td><td style='text-align: center; word-wrap: break-word;'>-0.309*** (0.023)</td><td style='text-align: center; word-wrap: break-word;'>-0.292*** (0.024)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(1 + \text{NUMBER\_OF\_DIRECTORS}) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.009 (0.009)</td><td style='text-align: center; word-wrap: break-word;'>-0.018** (0.009)</td><td style='text-align: center; word-wrap: break-word;'>-0.006 (0.009)</td><td style='text-align: center; word-wrap: break-word;'>-0.015* (0.009)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>$ \ln(\text{FIRM\_AGE}) $</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>-0.036*** (0.003)</td><td style='text-align: center; word-wrap: break-word;'>-0.036*** (0.003)</td><td style='text-align: center; word-wrap: break-word;'>-0.033*** (0.003)</td><td style='text-align: center; word-wrap: break-word;'>-0.034*** (0.003)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>State fixed effects</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Industry fixed effects</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R²</td><td style='text-align: center; word-wrap: break-word;'>0.083</td><td style='text-align: center; word-wrap: break-word;'>0.129</td><td style='text-align: center; word-wrap: break-word;'>0.189</td><td style='text-align: center; word-wrap: break-word;'>0.154</td><td style='text-align: center; word-wrap: break-word;'>0.213</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Adj. R²</td><td style='text-align: center; word-wrap: break-word;'>0.074</td><td style='text-align: center; word-wrap: break-word;'>0.127</td><td style='text-align: center; word-wrap: break-word;'>0.180</td><td style='text-align: center; word-wrap: break-word;'>0.137</td><td style='text-align: center; word-wrap: break-word;'>0.188</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>No. of obs.</td><td style='text-align: center; word-wrap: break-word;'>2,774</td><td style='text-align: center; word-wrap: break-word;'>2,924</td><td style='text-align: center; word-wrap: break-word;'>2,687</td><td style='text-align: center; word-wrap: break-word;'>2,909</td><td style='text-align: center; word-wrap: break-word;'>2,672</td></tr></table>

Second, we match the sample of NYSE-traded firms from the 1927 CRSP data with our sample of firms. Note that our Moody's sample does not include railroads or finance companies (which are not in the industrial manual). Thus, CRSP firms in those industries will not match our data, by construction. To match the rest, we first do some standardization of the company names from Moody's to match CRSP abbreviations (e.g., Corporation to Corp, Company to Co, Chemical to Chm, Mining to Mng, etc.). We then use a fuzzy matching algorithm on company names, requiring the Levenstein distance between the two strings to be less than 3. This leaves us with a matched sample of 361 firms. We use SIC codes from CRSP to assign the firms to Fama–French 30-industry groups. Among these firms, we observe a reasonable level of agreement between the Fama–French classification and ours. In Table C3, we report all Fama–French industries with more than five firms, listing next to each the most common industry in our classification, as well as the second most common industry and the corresponding firm counts. For example, we have 33 firms in the overlapped sample that match to the Fama–French "Autos" industry. In our industry classification, 25 are classified as "Motor" and the other 8 as "Rubber." More generally, the agreement is high among unambiguous industries, such as "Petroleum and Natural Gas," "Mines," or "Autos." The primary industry in our classification is the exact match. The secondary industry is typically closely related, or even a refinement of the primary classification (e.g., "Rubber" in "Autos," "Copper" in "Mines"). The same is true for other broader Fama–French categories, which our algorithm parses out into finer categories (e.g., "Clothes" into "Shoes and Leather" and "Textiles, Silk and Wool" or "Steel" into "Steel and Iron" and "Copper"). This exercise provides additional external validation of our industry groupings in the Moody's data, despite the very different approaches to defining industries.

<div style="text-align: center;"><div style="text-align: center;">TABLE C3</div> </div>


##### Industry Classification Comparison for NYSE-Traded Firms

Table C3 considers the sample of nonrailroad, nonfinancial NYSE-listed firms from the CRSP database merged to our Moody's sample. SIC codes from CRSP are used to classify firms into Fama–French 30-industry groups.



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Fama-French 30 Industry</td><td style='text-align: center; word-wrap: break-word;'>No. of Firms</td><td style='text-align: center; word-wrap: break-word;'>Moody&#x27;s Industry 1</td><td style='text-align: center; word-wrap: break-word;'>No. of Firms</td><td style='text-align: center; word-wrap: break-word;'>Moody&#x27;s Industry 2</td><td style='text-align: center; word-wrap: break-word;'>No. of Firms</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Food</td><td style='text-align: center; word-wrap: break-word;'>40</td><td style='text-align: center; word-wrap: break-word;'>Food</td><td style='text-align: center; word-wrap: break-word;'>16</td><td style='text-align: center; word-wrap: break-word;'>Sugar</td><td style='text-align: center; word-wrap: break-word;'>12</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Steel</td><td style='text-align: center; word-wrap: break-word;'>39</td><td style='text-align: center; word-wrap: break-word;'>Steel and iron</td><td style='text-align: center; word-wrap: break-word;'>16</td><td style='text-align: center; word-wrap: break-word;'>Copper</td><td style='text-align: center; word-wrap: break-word;'>12</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Auto</td><td style='text-align: center; word-wrap: break-word;'>33</td><td style='text-align: center; word-wrap: break-word;'>Motor</td><td style='text-align: center; word-wrap: break-word;'>25</td><td style='text-align: center; word-wrap: break-word;'>Rubber</td><td style='text-align: center; word-wrap: break-word;'>8</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Retail</td><td style='text-align: center; word-wrap: break-word;'>31</td><td style='text-align: center; word-wrap: break-word;'>Retail trading</td><td style='text-align: center; word-wrap: break-word;'>19</td><td style='text-align: center; word-wrap: break-word;'>Building</td><td style='text-align: center; word-wrap: break-word;'>9</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Petroleum and natural gas</td><td style='text-align: center; word-wrap: break-word;'>29</td><td style='text-align: center; word-wrap: break-word;'>Petroleum</td><td style='text-align: center; word-wrap: break-word;'>26</td><td style='text-align: center; word-wrap: break-word;'>Coal</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Construction</td><td style='text-align: center; word-wrap: break-word;'>17</td><td style='text-align: center; word-wrap: break-word;'>Building</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>Manufacturing</td><td style='text-align: center; word-wrap: break-word;'>3</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Machinery</td><td style='text-align: center; word-wrap: break-word;'>17</td><td style='text-align: center; word-wrap: break-word;'>Equipment</td><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>Manufacturing</td><td style='text-align: center; word-wrap: break-word;'>4</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Chemicals</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>Manufacturing</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>Mining</td><td style='text-align: center; word-wrap: break-word;'>3</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Clothes</td><td style='text-align: center; word-wrap: break-word;'>14</td><td style='text-align: center; word-wrap: break-word;'>Shoes and leather</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>Textile, silk and wool</td><td style='text-align: center; word-wrap: break-word;'>6</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Carry equipment</td><td style='text-align: center; word-wrap: break-word;'>12</td><td style='text-align: center; word-wrap: break-word;'>Equipment</td><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>Motor</td><td style='text-align: center; word-wrap: break-word;'>2</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Textiles</td><td style='text-align: center; word-wrap: break-word;'>12</td><td style='text-align: center; word-wrap: break-word;'>Textile, silk and wool</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>Mills</td><td style='text-align: center; word-wrap: break-word;'>4</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Mines</td><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>Mining</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>Copper</td><td style='text-align: center; word-wrap: break-word;'>3</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Tobacco</td><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>Tobacco</td><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>Retail trading</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Electrical</td><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>Electrical/chemical</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>Miscellaneous</td><td style='text-align: center; word-wrap: break-word;'>4</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Household</td><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>Mining</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>Textile, silk and wool</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Coal</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>Coal</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>Steel and iron</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Transportation</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>Equipment</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>Shipping</td><td style='text-align: center; word-wrap: break-word;'>4</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Recreation</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>Entertainment</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>Retail trading</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Paper</td><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>Paper</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>Equipment</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr></table>

### Supplementary Material

To view supplementary material for this article, please visit http://doi.org/10.1017/S0022109023000765.

## References

Adelino, M.; M. A. Ferreira; M. Giannetti; and P. Pires. "Trade Credit and the Transmission of Unconventional Monetary Policy." Review of Financial Studies, 36 (2023), 775–813.

Ahern, K. R. "Network Centrality and the Cross Section of Stock Returns." Working Paper, University of Southern California (2013).

Almeida, H.; C. Kim; and H. B. Kim. "Internal Capital Markets in Business Groups." Journal of Finance, 70 (2015), 2539–2586.

Amore, M. D.; S. Caselli; P. Colla; and G. Corbetta. "Board Connections and Debt Structure in Private Firms." Working Paper, Bocconi University (2019).

Asker, J.; J. Farre-Mensa; and A. Ljungqvist. "Corporate Investment and Stock Market Listing: A Puzzle?" Review of Financial Studies, 28 (2015), 342–390.

Banerjee, A. V. "A Simple Model of Herd Behavior." Quarterly Journal of Economics, 107 (1992), 797–817.

Benmelech, E.; C. Frydman; and D. Papanikolaou. "Financial Frictions and Employment During the Great Depression." Journal of Financial Economics, 133 (2019), 541–563.

Bernanke, B. S. “Nonmonetary Effects of the Financial Crisis in the Propagation of the Great Depression.” American Economic Review, 73 (1983), 257–276.

Bikhchandani, S.; D. Hirshleifer; and I. Welch. "A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades." Journal of Political Economy, 100 (1992), 992–1026.

Buchuk, D.; B. Larrain; M. Prem; and F. Urzua. "How Do Internal Capital Markets Work? Evidence from the Great Recession." Review of Finance, 24 (2020), 847–889.

Cai, Y., and M. Sevilir. "Board Connections and M&A Transactions." Journal of Financial Economics, 103 (2012), 327–349.

Calomiris, C. W. “Financial Factors in the Great Depression.” Journal of Economic Perspectives, 7 (1993), 61–85.

Calomiris, C. W.; M. S. Jaremski; and D. C. Wheelock. "Interbank Connections, Contagion and Bank Distress in the Great Depression." Working Paper, Columbia University (2019).

Calomiris, C. W., and J. R. Mason. "Fundamentals, Panics, and Bank Distress During the Depression." American Economic Review, 93 (2003a), 1615–1647.

Calomiris, C. W., and J. R. Mason. “Consequences of Bank Distress During the Great Depression.” American Economic Review, 93 (2003b), 937–947.

Currie, L. "The Decline of the Commercial Loan." Quarterly Journal of Economics, 45 (1931), 698–709.

Das, S. R.; K. J. Mitchener; and A. Vossmeyer. "Systemic Risk and the Great Depression." NBER Working Paper No. 25405 (2018).

Ellison, G., and D. Fudenberg. "Rules of Thumb for Social Learning." Journal of Political Economy, 101(1993), 612–643.

Ellison, G., and D. Fudenberg. "Word-of-Mouth Communication and Social Learning." Quarterly Journal of Economics, 110 (1995), 93–125.

Engelberg, J.; P. Gao; and C. A. Parsons. "Friends with Money." Journal of Financial Economics, 103 (2012), 169–188.

Fishback, P.; S. Kantor; and J. Wallis. "Can the New Deal's Three Rs be Rehabilitated?" Explorations in Economic History, 40 (2003), 278–307.

Fracassi, C. "Corporate Finance Policies and Social Networks." Management Science, 63 (2017), 2420–2438.

Fracassi, C., and G. Tate. “External Networking and Internal Firm Governance.” Journal of Finance, 67 (2012), 153–194.

Frydman, C., and E. Hilt. “Investment Banks as Corporate Monitors in the Early 20 $ ^{th} $ Century United States.” American Economic Review, 107 (2017), 1938–1970.

Gao, J. "Managing Liquidity in Production Networks: The Role of Central Firms." Review of Finance (2021), 819–861.

García-Appendini, E., and J. Montoriol-Garriga. "Firms as Liquidity Providers: Evidence from the 2007–2008 Financial Crisis." Journal of Financial Economics, 109 (2013), 272–291.

Giroud, X., and H. M. Mueller. “Firms’ Internal Networks and Local Economic Shocks.” American Economic Review, 109 (2019), 3617–3649.

Goel, A. M., and A. V. Thakor. "Do Envious CEOs Cause Merger Waves?" Review of Financial Studies, 23 (2010), 487–517.

Gofman, M., and Y. Wu. "Trade Credit and Profitability in Production Networks." Journal of Financial Economics, 143 (2022), 593–618.

Graham, J. R.; S. Hazarika; and K. Narasimhan. "Financial Distress in the Great Depression." Financial Management, 40 (2011), 821–844.

Graham, J. R.; H. Kim; and M. Leary. "CEO-Board Dynamics." Journal of Financial Economics (2020), 612–636.

Graham, J. R.; M. T. Leary; and M. R. Roberts. "A Century of Capital Structure: The Leveraging of Corporate America." Journal of Financial Economics, 118 (2015), 658–683.

Guner, B.; U. Malmendier; and G. Tate. "Financial Expertise of Directors." Journal of Financial Economics, 88 (2008), 323–354.

Hermalin, B., and M. S. Weisbach. "Boards of Directors as an Endogenously Determined Institution: A Survey of the Economic Literature." FRB New York – Economic Policy Review, 9 (2003), 7–26.

Hoberg, G., and G. Phillips. "Text-Based Network Industries and Endogenous Product Differentiation." Journal of Political Economy, 124 (2016), 1423–1465.

Huang, Q.; F. Jiang; and E. Lie. "The Value of Social Networks During Periods of Distress." Working Paper, City University of Hong Kong and University of Iowa (2012).

Hwang, B. H., and S. Kim. "It Pays to Have Friends." Journal of Financial Economics, 93 (2009), 138–158.

Lee, J., and F. Mezzanotti. "Bank Distress and Manufacturing: Evidence from the Great Depression." Working Paper, Northwestern University (2017).

Loualiche, E.; Vickers, C.; and N. L. Ziebarth. "Firm Networks in the Great Depression." Working Paper, University of Minnesota (2019).

Love, I.; L. A. Preve; and V. Sarria-Allende. "Trade Credit and Bank Credit: Evidence from Recent Financial Crises." Journal of Financial Economics, 83 (2007), 453–469.

Mitchener, K., and G. Richardson. "Network Contagion and Interbank Amplification During the Great Depression." Journal of Political Economy, 127 (2019), 465–507.

Mizruchi, M. S. The American Corporate Network 1904–1974. Beverly Hills, CA: Sage Publications (1982).

Mizruchi, M. S. "Relations Among Large American Corporations, 1904–1974." Social Science History, 7 (1983), 165–182.

Nanda, R., and T. Nicholas. "Did Bank Distress Stifle Innovation During the Great Depression?" Journal of Financial Economics, 114 (2014), 273–292.

Nguyen, B. D. “Does the Rolodex Matter? Corporate Elite’s Small World and the Effectiveness of Boards of Directors.” Management Science, 58 (2012), 236–252.

Opler, T. C., and S. Titman. "Financial Distress and Corporate Performance." Journal of Finance, 49 (1994), 1015–1040.

Reifer, W. W.; D. Friday; W. Lichtenstein; and J. H. Riddle. "Changes in the Capital Requirements of Business Enterprise and the Decline of the Commercial Loan." In A Program of Financial Research Vol 1: Report of the Exploratory Committee on Financial Research (UMI). Cambridge, MA: NBER (1937), 43–46.

Richardson, G. "Categories and Causes of Bank Distress During the Great Depression, 1929–1933: The Illiquidity Versus Insolvency Debate Revisited." Explorations in Economic History, 44 (2007), 588–607.

Richardson, G. "Categories and Causes of Bank Distress During the Great Depression." Research in Economic History, 1 (2008), 37–115.

Santioni, R.; F. Schiantarelli; and P. E. Strahan. "Internal Capital Markets in Times of Crisis: The Benefit of Group Affiliation in Italy." Review of Finance, 24 (2020), 773–811.

Schmidt, B. "Costs and Benefits of Friendly Boards During Mergers and Acquisitions." Journal of Financial Economics, 117 (2015), 424–447.

Shue, K. "Executive Networks and Firm Policies: Evidence from the Random Assignment of MBA Peers." Review of Financial Studies, 26 (2013), 1401–1442.

Stock, J. H., and M. Yogo. "Testing for Weak Instruments in Linear IV Regression." In Identification and Inference for Econometric Models: Essays in Honor of Thomas Rothenberg, D. W. K. Andrews and J. H. Stock, eds. Cambridge, UK: Cambridge University Press (2005), 80–108.

Xia, C.; X. Zhang; C. Cao; and N. Xu. "Independent Director Connectedness in China: An Examination of the Trade Credit Financing Hypothesis." International Review of Economics & Finance, 63 (2019), 209–225.

Yermack, D. "Higher Market Valuation of Companies with a Small Board of Directors." Journal of Financial Economics, 40 (1996), 185–211.

Ziebarth, N. L. "Identifying the Effects of Bank Failures from a Natural Experiment in Mississippi During the Great Depression." American Economic Journal: Macroeconomics, 5 (2013), 81–101.

