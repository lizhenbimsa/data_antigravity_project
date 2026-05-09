# The Use of LLMs to Annotate Data in Management Research: Foundational Guidelines and Warnings

Natalie A. Carlson $ ^{*1} $ and Vanessa Burbano $ ^{2} $

 $ ^{1} $The Wharton School, University of Pennsylvania

 $ ^{2} $Columbia Business School, Columbia University

## Abstract

The emergence of large language models (LLMs) has opened new avenues for integrating artificial intelligence into research, particularly for data annotation and text classification. However, the benefits and risks of using LLMs in research remain poorly understood, such that researchers lack guidance on how best to implement this tool. We address this gap by developing a foundational framework for implementing LLMs for annotation in management research, providing structured guidance on key implementation decisions and best practices. We illustrate the implementation of this framework through an empirical application: classifying sustainability claims in crowdfunding projects to assess the performance relationships of these claims. We demonstrate that while LLMs can match or exceed traditional methods' performance at lower cost, variations in prompt design can significantly affect results and downstream analyses. We thus develop procedures for sensitivity analysis and provide documentation to help researchers implement these robustness checks while maintaining methodological integrity.

Keywords: Artificial Intelligence, LLMs, Research Methods, NLP, Classification, Crowdfunding, Sustainability

## 1 Introduction

The advent of large language models (LLMs) presents numerous research applications, representing a paradigm shift across various fields (Eloundou et al., 2023). As articulated by Tu et al. (2023), LLMs “cultivate an extensive understanding of language, common sense, and reasoning, showcasing a semblance of intelligence.” As this technology advances, applied researchers are grappling with the profound implications for their research processes.

A particularly promising use case for LLMs in social science research is data annotation: the creation of structured variables from unstructured text, for the purposes of use in downstream analysis. The prior methodological standard in this area has typically involved either human coding – often through a complex process of training research assistants – or automated methods ranging from dictionary- or keyword-based methods to custom-built supervised machine learning classifiers (see Miric et al., 2022, Choudhury et al., 2021). Early experiments have demonstrated LLMs' potential in labeling or annotating unstructured texts, consistently matching or exceeding the performance of both crowd workers and expert coders (Gilardi et al., 2023; Tornberg, 2023; Rathje et al., 2023), and doing so with significant cost and time savings. However, while the technical capabilities of these models are increasingly well documented, the implications for research validity and reproducibility remain unclear.

This gap is particularly urgent in the social sciences, because social science applications of LLMs differ fundamentally from typical computer science or commercial use cases. Rather than optimizing for accuracy alone, researchers often use LLM-generated labels as an intermediate step to study downstream relationships, frequently while explicitly testing hypotheses. This introduces unique methodological challenges.

Emerging evidence suggests that subtle implementation choices can significantly affect LLM performance (Battle and Gollapudi, 2024; Sclar et al., 2023; Meincke et al., 2025a). More concerning for social scientists, small variations in these choices can alter the interpretation

of downstream findings. However, what initially appears as a methodological weakness potentially offers a novel opportunity. While traditional approaches to data annotation, like human coding, were constrained by cost and feasibility, LLMs provide an affordable means to systematically explore how research design choices affect downstream conclusions.

In this paper, we draw from both computer science and social science – as well as insights from our own applied empirical tests – to develop a foundational framework for using LLMs in management research, focusing particularly on data annotation tasks. Our framework breaks down the implementation process into five key stages: method selection, model configuration, prompt engineering, cost and scale considerations, and validation and robustness. For each stage, we identify core decisions researchers must make, analyze their tradeoffs, and provide evidence-based best practices.

We demonstrate the utility of this framework through an empirical application: using LLMs to classify Kickstarter campaigns along the dimension of product sustainability, a task for which we had previously developed a supervised machine learning model. Through systematic testing of different prompting strategies across multiple models, we show that LLMs can match traditional methods at significantly reduced cost and time.

However, our analysis also underscores the concern that variations in model choice and prompt design can lead to markedly different labels, which in turn affect downstream analyses and conclusions. Moreover, we demonstrate that more accurate LLM prediction in the first stage does not automatically translate to better inference in the second stage. A key theoretical insight from our analysis is that higher first-stage classification accuracy does not guarantee unbiased downstream inference when classification errors are systematically correlated with outcome variables. This finding has important implications for any research design using intermediate classification steps, whether employing LLMs or other automated annotation methods.

Based on these findings, we propose a systematic approach to sensitivity analysis, aiming to provide researchers with tools to evaluate how variations in prompting and other methodological choices affect their results. In this approach, we leverage variation to help bound the range of possible research conclusions. We accompany this with detailed documentation and reusable code to help researchers implement these sensitivity checks in their own work. $ ^{1} $ We argue that these types of robustness checks will remain important even as models continue to advance – as with any empirical method in which the researcher has significant degrees of freedom.

Our paper contributes to the growing body of knowledge on the integration of AI and machine learning in management (e.g., Dell'Acqua et al., 2023; Doshi et al., 2024; Brynjolfsson et al., 2023). While a rich emergent literature focuses on the integration of such technologies within organizations (e.g., Csaszar et al., 2024; Otis et al., 2024; Boussioux et al., 2023; Jia et al., 2025), researchers increasingly recognize the methodological potential of LLMs in social science research (Weber and Reichardt, 2023; Chopra and Haaland, 2023). We build on this work by providing a foundational methodological framework that introduces core principles for LLM implementation, emphasizing sensitivity analysis and the propagation of methodological choices through the research pipeline. Rather than offering definitive guidance, we establish baseline methodology and structural principles that future researchers can build upon and adapt to their specific contexts and evolving technological capabilities. We hope that this work provides a structured foundation for the responsible and rigorous use of these technologies in research methodology, facilitating continued methodological innovation as the field develops.

## 2 A Baseline Framework for Implementing LLMs in Management Research

Large language models (LLMs) employ transformer architectures that can process and generate human-like text across a wide range of applications (Vaswani et al., 2017; Brown et al., 2020; Chowdhery et al., 2023; Bommasani et al., 2021). As these models become increasingly integrated into the research process (Chattopadhyay et al., 2024; Tranchero et al., 2024), researchers across disciplines have begun developing guidelines for their use. Drawing from emerging work in computer science, the social sciences, and management – as well as our own empirical experimentation – we synthesize and expand upon these insights to establish foundational principles that future researchers can build upon to ensure both rigor and reproducibility. These principles translate the broader goals of research transparency and reproducibility into specific protocols for LLM implementation (Bender et al., 2021; Weidinger et al., 2021).

Our framework breaks down the LLM implementation process into five key stages: (1) method selection and integration, (2) model selection and stability, (3) prompt engineering, (4) cost and scale considerations, and (5) validation and robustness assessment. Below, we discuss each stage, identifying tradeoffs and developing specific recommendations for management scholars.

## [INSERT TABLE 1 ABOUT HERE]

1: Method Selection. The first fundamental consideration concerns whether LLMs are necessary at all for a particular research application. We argue that it is useful to position LLMs within the researcher's methodological toolkit. While LLMs can process unstructured text without task-specific training data, they should be evaluated against established alternatives, each with documented strengths and limitations. Human coding allows for nuanced interpretation of context and ambiguity but faces constraints of scale and cost (Grimmer and Stewart, 2013). Dictionary or keyword methods offer computational efficiency and per-

fect reproducibility but struggle with semantic complexity and context-dependence, often performing best for narrow technical applications (Quinn et al., 2010; Miric et al., 2023). Supervised machine learning approaches enable scalable, consistent classification but require substantial labeled training data for good performance (Miric et al., 2023; Choudhury et al., 2021). LLMs occupy a distinctive position in this spectrum – they can handle complex semantic tasks without custom training data but introduce new challenges in reproducibility and output stability. For instance, specialized dictionary methods may outperform LLMs in tasks requiring precise technical or field-specific terminology. This underscores a general point: newer methods are not always better; legacy methods may work just as well or better for certain applications.

As we will demonstrate in our empirical application, one key advantage of LLMs, vis-à-vis prior methods, is the low cost and ease of sensitivity testing. This advantage signals that LLMs may provide utility – in tandem with other methods like human coding, which might be used for a primary analysis – in showing robustness to a variety of methodological choices. We emphasize a first principle for this decision point: to consider LLMs as part of a broader methodological toolkit, carefully matching the use of tool to the research setting.

2: Model Selection and Stability. Once researchers have decided to integrate LLMs into their research pipeline, the next decision point involves which models to use. The rapid evolution of LLMs presents researchers with a constant tradeoff between accessing the latest capabilities and ensuring long-term reproducibility of their findings (Raff, 2019). This requires careful consideration of model selection, version control, and access method (Mitchell et al., 2019). Researchers must document not only which model they use but also how they access it and what steps they take to ensure their analysis can be replicated in the future. While weights can be archived for open-source models, proprietary models present additional challenges for replication as they may become deprecated or inaccessible $ ^{2} $.

Open-source models, by contrast, may have less reliable APIs that can cause implementation difficulties.

Beginning in 2024, developers have begun to release so-called “reasoning” models, such as OpenAI’s o3 and Deepseek’s R1, that use test-time inference and reinforcement learning to improve output quality on complex, multi-step reasoning tasks (e.g., coding or solving math problems). While these models excel at tasks requiring extended reasoning, their suitability for basic data annotation remains unclear. These models are optimized for complex problem-solving rather than straightforward classification, and we do not yet know whether reasoning models offer advantages over traditional models for annotation tasks $ ^{3} $.

If annotating sensitive or proprietary data, particular care should be used in selecting a model that will not store or use user prompts or outputs. Researchers should check data retention policies or consider local deployment (i.e., running the model on a private cloud or institutional cluster) if the data are particularly sensitive.

While newer models may offer improved capabilities, their advantages are not universal – a finding we will explore in detail through our empirical application in Section 3. Moreover, sensitivity testing may reduce the relevance of minor performance differences between models. This leads us to our second core principle: the prioritization of reproducibility and documentation over cutting-edge performance (Dodge et al., 2019; Kapoor and Narayanan, 2022).

3: Prompt Engineering. The next stage of LLM implementation concerns prompt engineering. Unlike traditional computational tools where inputs map precisely to outputs in a deterministic manner, LLMs require carefully specified natural language instructions (“prompts”) that fundamentally shape their behavior. This introduces prompt engineering

as a critical methodological component (Wei et al., 2022) that incurs unique challenges, because unlike traditional method parameters, prompts are more difficult to systematically optimize.

While this framework focuses primarily on prompt-based approaches – which represent the most accessible starting point for basic annotation tasks – recent methodological work demonstrates impressive performance through specialized training on domain-specific data, particularly for nuanced classification tasks in strategy research (Chattopadhyay et al., 2024; Jia et al., 2025). We focus on prompt-based methods as they provide an immediately accessible baseline approach, while noting that fine-tuning represents a valuable extension for researchers with appropriate resources and complex annotation needs (see Appendix C for additional technical implementation details, including fine-tuning considerations).

The relationship between prompt construction and model outputs is complex and often unpredictable – subtle variations in phrasing, example selection, or formatting can significantly affect results (Battle and Gollapudi, 2024; Sclar et al., 2023; Meincke et al., 2024, 2025a). However, rather than viewing this sensitivity as purely problematic, we argue it presents an opportunity for methodological robustness when properly managed. Each prompting approach presents fundamental tradeoffs between simplicity, reliability, and depth of analysis – from basic classification instructions to complex reasoning frameworks – which we explore in detail in the following section.

Rather than seeking a single “optimal” prompt, researchers may benefit from developing families of related prompts based on established prompting strategies (e.g., Meincke et al., 2025a). A focus on systematic variation serves two purposes: first, it helps identify which aspects of prompt construction are most consequential for the specific research application; second, it provides bounds on how methodological choices affect research conclusions. This leads us to propose a core principle for prompt engineering: structure prompts systematically and transparently, with thorough documentation of development choices.

4: Cost and Scale Considerations. As researchers then look to scale their approach across their research application, they must explicitly plan for computational resource allocation and statistical power. The importance of this stage will vary with the size of the data annotation task and the speed with which costs fall with advancing technology. While LLMs can process individual texts quickly, costs scale with both sample size and prompt complexity. Each API call incurs charges based on input and output tokens $ ^{4} $, making experimental design choices like prompt length, number of examples, and iteration count directly tied to research budgets. For instance, chain-of-thought prompting can improve accuracy but multiplies token usage, while running multiple prompt variations for robustness checks multiplies total API calls (Kaplan et al., 2020).

In our subsequent empirical example, we provide cost calculations under different configurations, providing some benchmarks for how researchers might budget for both initial analysis and robustness checks. We also demonstrate sensitivity analysis techniques using shortened texts (for lower token costs) and bootstrapping (for large datasets), which can substantially lower the costs of robustness testing. We believe API costs will continue to drop over the coming years, making these sensitivity techniques feasible for researchers even with very limited budgets. For now, we propose the following principle: researchers should balance resource usage with the demands of statistical power and robustness needs.

5: Validation and Robustness. The final stage of LLM integration concerns validation and robustness testing. As discussed above, variations in prompt construction can materially affect research conclusions, necessitating systematic validation protocols (Ribeiro et al., 2020; Dror et al., 2018). For example, prompts that produce nearly identical accuracy metrics on validation data may still produce different downstream regression estimates. Researchers should maintain gold-standard validation sets, systematically test prompt variations, and

examine how these methodological choices feed through their analysis pipeline (Egami et al., 2024). Beyond reporting point estimates, we suggest that researchers should document the sensitivity of their findings to reasonable variations in LLM implementation.

This stage underscores our final principle: researchers should conduct systematic evaluation of result validity and stability. This article suggests a procedure for this sensitivity analysis – generating families of related prompts, testing their impact on downstream analyses, and producing bounded estimates that capture underlying methodological uncertainty. We provide code to facilitate implementation of these procedures, documented further in Appendix A.

### 2.1 Prompt Engineering Strategies

The core principles outlined in the previous section each require careful implementation decisions. Among these, prompt engineering – the systematic design of instructions given to language models – stands out as particularly critical for three reasons. First, unlike other implementation choices that can often be standardized across projects (such as model selection or validation protocols), prompts must be carefully crafted for each specific research application. Second, small variations in prompt design can significantly affect model outputs (Battle and Gollapudi, 2024), making this perhaps the most consequential implementation decision faced by researchers. Third, while other aspects of LLM implementation often parallel established practices in machine learning, prompt engineering represents a fundamentally new methodological challenge, thus requiring distinct guidance.

Importantly, different models respond differently to the same prompting strategies, and effectiveness can vary significantly based on the specific context and task. For instance, while Chain of Thought (CoT) prompting has proven valuable across many applications, recent research suggests that its benefits may be diminishing with more advanced models that have internalized reasoning patterns (Meincke et al., 2025b). This underscores the

importance of systematic testing across model-prompt combinations rather than assuming universal effectiveness of any single approach.

In Table 2, we provide a review of some commonly used prompting strategies from the extant literature (see Sahoo et al., 2024, for an excellent review). For detailed descriptions of how these strategies have evolved and their theoretical foundations, see Appendix B. In our empirical application described in Section 3, we provide specific representative examples illustrating the specific prompting strategies described below.

### [INSERT TABLE 2 ABOUT HERE]

A Note on System Prompting. When accessing LLMs through a commercial API, certain systems allow for a dedicated system prompt that persists across multiple calls, like a broad meta-prompt (e.g., “You are a helpful and truthful assistant”). Most LLMs have default system prompts when none are specified, though these defaults may vary across models and versions. While potentially useful for maintaining methodological consistency, system prompts should be documented with the same rigor as other prompting choices, as they have the potential to impact model outputs.

For details on additional technical implementation considerations, including model augmentation approaches like fine-tuning and RAG, please see Appendix C.

To demonstrate how these elements come together in practice, we now turn to an empirical application: using LLMs to classify Kickstarter campaigns along the dimension of product sustainability, in order to study the relationship between sustainability claims and success rates.

## 3 Empirical Application: Identifying Sustainability Claims in Kickstarter Projects

In this application, we apply the five-stage framework to a real research application. We first explain our method selection process (Stage 1) by comparing LLMs to our prior supervised machine learning approach. We then detail our model selection decisions (Stage 2) and prompt engineering process (Stage 3), before analyzing cost and scale considerations (Stage 4) across different implementation strategies. We report the results of testing different configurations across Stages 2-4 on a gold-standard test set before identifying an implementation decision for the full dataset. Finally, we demonstrate validation and robustness procedures (Stage 5) through systematic sensitivity analysis.

### 3.1 Stage 1: Method Selection

Sample and Objective. We use as our setting the rewards-based crowdfunding platform Kickstarter. Crowdfunding has emerged as an increasingly prevalent method for raising capital for entrepreneurial organizations (Agrawal et al., 2014; Mollick, 2014; Sorenson et al., 2016; Yu et al., 2017), and rewards-based crowdfunding is an important type of crowdfunding platform. It includes such platforms as Kickstarter, Indiegogo, Rockethub, and GoFundMe. On rewards-based crowdfunding platforms, entrepreneurial organizations solicit funding in exchange for “rewards” (the reward is what, if anything, the funder receives in the exchange).

We use a database of all Kickstarter campaigns between the years 2009 and 2016, obtained from the CrowdBerkeley Database (managed by the Fung Institute at UC Berkeley). This database includes information about the campaign (for example, project category and whether it has a video) and its current status (success, number of backers, amount pledged), but does not contain the full description of the project from its campaign page. To augment this, we scraped the full campaign text from each project page URL and matched this text to the project metadata from the database. The full sample comprises 295,985 projects.

The objective of the methods described below is to classify each Kickstarter campaign text

along the dimension of perceived social benefit. Examples of campaigns classified as offering socially beneficial products or services in the sample include a food supply company with a mission of serving food deserts, a retail store that prioritizes hiring homeless youth, or a drone imaging company used in search and rescue missions.

Given the size of the complete dataset, hand-labeling the projects was not computationally feasible. In the next two sections, we describe first the approach we took in 2017 – a custom-built supervised machine learning model – and then describe the approach to using LLMs to accomplish the same end.

Prior Method: Supervised GBM Model. Our prior approach followed a traditional supervised machine learning pipeline. First, we created a training dataset of 2,068 projects labeled by a combination of Amazon Mechanical Turk workers and university research assistants. Each project was evaluated by multiple raters who determined whether the main product or service benefited the broader society (coded as 1) or provided primarily consumer-only benefits (coded as 0), with substantial inter-rater agreement (Fleiss's kappa between 0.6-0.7) $ ^{5} $.

Using this labeled dataset, we trained a Gradient Boosting Machine (GBM) model (Friedman, 2001) to classify the remaining projects. $ ^{6} $ The model processed project descriptions through standard text preprocessing techniques and cross-validation procedures $ ^{7} $ to ensure reliability. When tested against a hand-labeled validation set of 250 examples, the model reached an accuracy of 92 percent, with balanced false positives and false negatives. While achieving satisfactory performance, this approach required significant upfront investment in training data creation and model development.

Proposed Decision. LLMs appear to be a good fit for this research application for several reasons. First, while the GBM model achieved high accuracy, it required substantial upfront investment in creating a labeled training dataset and fine-tuning the model – resources that might not be available to all researchers, and regardless incur significant cost and time to execute. LLMs offer the potential to match this performance without the need for extensive training data. Second, the text classification task at hand – evaluating societal benefit – requires nuanced understanding of context and implicit meanings that keyword-based or simpler automated methods might miss. LLMs’ demonstrated capability in processing semantic complexity makes them well-suited for this type of evaluation. Third, while human coding would offer similar nuanced understanding, the scale of our dataset (295,985 projects) makes manual coding prohibitively expensive and time-consuming. Given these tradeoffs, we proceed with LLMs as our primary method while maintaining our human-labeled validation set as a gold standard for evaluating performance.

### 3.2 Stage 2: Model Selection

Drawing on our framework’s principles for model selection, we identified five LLMs for systematic evaluation, chosen to represent different points in the tradeoff space between performance, cost, and accessibility. GPT-4 and Claude 3 Opus represent more mature models optimized for complex reasoning tasks, offering potentially higher accuracy but at greater computational cost. GPT-4o and Claude 3.5 Haiku represent newer architectures optimized for efficiency, potentially offering better cost-performance balance. We included GPT-4o-mini as an extremely lightweight option to test the viability of low-cost implementations. This selection allows us to evaluate how model scale and optimization targets affect classification performance while maintaining consistent access through stable commercial APIs.

Proposed Decision. Based on these considerations, we proceed with testing five models that span the key tradeoffs in our framework: two models optimized for complex reasoning (GPT-4, Claude 3 Opus), two models optimized for efficiency (GPT-4o, Claude 3.5 Haiku), and

one lightweight model (GPT-4o-mini). $ ^{8} $ We systematically evaluate these models across all prompting strategies, maintaining consistent parameters (temperature = 0) to maximize reliability in classification decisions (Törnberg, 2024).

### 3.3 Stage 3: Prompt Engineering

Table 3 presents a systematic application of different prompting strategies to our sustainability classification task. For each strategy discussed in Section 2.2, we developed a canonical example prompt specifically designed for identifying societal benefits in Kickstarter projects.

## [INSERT TABLE 3 ABOUT HERE]

To test each prompting strategy, we developed an automated pipeline $ ^{9} $ that:

1. Loads the project description

2. Constructs the appropriate prompt by combining the preamble prompt text with the Kickstarter project description

3. Makes an API call to retrieve the classification

## 4. Appends the binary  $ (0/1) $ label to our dataset

We maintained consistent output formatting across all strategies by explicitly requesting binary responses, allowing direct comparison of classification performance. While more complex prompting strategies (like Chain of Thought or Tree of Thoughts) often generate additional explanatory text, we constructed the prompts to extract only a single final binary classification $ ^{10} $.

Proposed Decision. We proceed with testing all seven prompting strategies outlined in Table 3, from basic zero-shot instructions to complex reasoning frameworks like ToT. This comprehensive approach serves two purposes. First, it allows us to evaluate whether more sophisticated prompting techniques justify their increased token usage for our binary classification task. Second, and more importantly, testing multiple valid prompting approaches enables us to assess the sensitivity of our research conclusions to reasonable variations in prompt design. This aligns with our framework's emphasis on systematic prompt evaluation, rather than seeking a single "optimal" prompt.

### 3.4 Stage 4: Cost and Scale Considerations

Because our full dataset comprises 295,985 Kickstarter projects, several cost and scale considerations inform our testing strategy. First, API costs scale with both input length (Kickstarter project descriptions) and prompt complexity. Second, testing all model-prompt combinations (five models multiplied by seven prompting strategies) across the full dataset would be prohibitively expensive – even using our most cost-efficient model (GPT-4o-mini), processing the full dataset would cost several thousand dollars. Third, and most importantly, testing on the complete dataset would not provide additional insights, because the full dataset does not have any ground-truth labels. Our labeled test set of 250 projects, which was previously used to validate the GBM and other supervised ML models, provides a consistent benchmark for comparing performance across methods.

Proposed Decision. Given these considerations, we proceed with systematic testing of all model-prompt combinations on our test set of 250 projects. This focused approach enables thorough comparison while maintaining reasonable computational costs (ranging from 0.03 to 5.71 USD per test run across different model-prompt combinations, as detailed in Table 4). Following the principle of balancing resource usage with robustness needs, this strategy allows us to evaluate the results of all methodological choices before potential deployment at scale.

#### Results of Tests (Stages 2-4)

First-Stage Results Comparison. Table 4 displays how each of the models performed on the test set of 250 Kickstarter campaigns, for which the “ground truth” were hand labels agreed upon by the authors. For each of the methods, we report overall accuracy, the proportion of false positives (i.e., projects labeled as one when the ground-truth label was zero), and the proportion of false negatives (i.e., projects labeled as zero when the ground-truth label was one). Finally, we report the overall cost in USD of using each method to label the test set.

## [INSERT TABLE 4 ABOUT HERE]

We observe high variance in accuracy across models and prompting strategies. In general, GPT-4o achieved the best performance – exceeding the GBM’s performance in several instances – followed by Claude 3 Opus. While there was a general trend towards improved accuracy with more advanced prompting techniques, this was not universally true. Notably, Haiku had its weakest performance with the Reflection on Search Trees (RoT) prompting strategy, with an astonishing 56 percent false positive rate. By contrast, GPT-4o achieved 87.6 percent accuracy with the zero-shot prompt, improving to 94 percent accuracy with the Tree-of-Thought (ToT) method. This was done at the cost of approximately 0.0019 USD per instance. GPT-4o-mini was even more cost-effective – at approximately 0.00012 USD per instance – but with significantly weaker performance $ ^{11} $. Notably, the mini model did not improve with more sophisticated reasoning prompts, instead achieving its best accuracy (79.6 percent) with the few-shot prompt.

These results illustrate the importance of model-specific testing. For example, while GPT-4o consistently benefited from more sophisticated prompting strategies, GPT-4o-mini achieved

its best performance with simpler few-shot prompting, and Claude-3.5-Haiku showed variable and sometimes counterintuitive responses to advanced prompting techniques. This pattern aligns with recent research suggesting that prompting effectiveness is highly context-dependent and model-specific (Meincke et al., 2025b).

The results also provide insight into the reliability of LLM annotations relative to human coding processes. While our training data showed typical inter-rater variability (Fleiss's kappa in the range of 0.6-0.7), our best-performing LLM configurations achieved 94 percent agreement with expert consensus. This benchmark highlights the continued critical role of human expertise in LLM-based research pipelines. While LLMs can scale annotation processes dramatically, our framework still relies fundamentally on human-generated ground truth for validation and performance assessment. The fact that we measure LLM "accuracy" against human consensus underscores that rather than replacing human judgment entirely, LLMs may be most valuable when they extend and scale human expertise while maintaining human oversight for quality control and validation.

However, our end goal in this analysis is not to optimize performance in the first stage, but to understand something about the construct being labeled and some secondary outcome – in this case, how do sustainability claims in crowdfunding projects relate to success rates? Therefore, we next consider the implications for the prompt and model choices above for the downstream analysis.

Second-Stage Results Comparison. Here, we consider the downstream consequences of the prompt and model choices studied in the first stage, if the labels generated by the LLM were to be used as independent variables in the second-stage analysis. We compare these results to the labels generated by the original GBM model, as well as the agreed-upon human labels, the latter being the closest thing we have as "ground truth."

We ask: what is the relationship between offering a socially beneficial product and the like-

lihood of project success? In this context, the most relevant measure of project success is a binary measure capturing whether or not the project met its funding goal. Repeating the analysis with each set of labels generated by the different models, we conduct a logistic regression with fixed effects for project category and year, controlling for the logged magnitude of the funding goal. The coefficients on the relevant variable, Socially Beneficial Product, can be seen plotted in Figure 1.

## [INSERT FIGURE 1 ABOUT HERE]

Past work has found there to be a positive association between sustainability claims in crowdfunding settings and the likelihood of project success (Calic and Mosakowski, 2016; Taeuscher et al., 2021). We will consider this to be the “true” relationship, one that is validated by the positive coefficients on the human-labeled ( $ \beta = 1.645 $) and GBM-labeled ( $ \beta = 1.438 $) variables.

Of the 35 prompt-model combinations tested, five recover this positive relationship at the 95 percent confidence level, and a further seven at the 90 percent confidence level. Most strikingly, accuracy in the first stage does not necessarily correspond to a better recovery of the “true” second-stage effect: for a notable counter-example, Claude-3-Opus + CoT has a negative point estimate in the second stage despite achieving 87.6 percent accuracy in the first stage. By contrast, GPT-4o-mini + role-based prompt reconstructs the positive association in the second stage while achieving only 55.6 percent accuracy in the first stage.

Why is this the case? If the direction of the error in the first stage is systematically correlated with the outcome in the second stage, second stage estimates may be biased. Consider a model that, for whatever reason, tends to misclassify a certain type of project as a false negative $ ^{12} $. If these types of false negatives are also disproportionately projects that tend to meet their funding goal, the particular direction of the first-stage error will bias the second-

stage coefficients downwards. This can be meaningful in the case of imbalanced classes, and, if a systematic tendency, not necessarily a problem that will be overcome by larger samples.

Moreover, the variability in second-stage results also raises concerns about the potential for manipulation in the pursuit of desired outcomes. Each of the prompts we tested is, arguably, reasonable and justifiable on its own. Scanning the variability in coefficients in Figure 1, is easy to imagine that – even if the “true” relationship were indistinguishable from zero – researchers might be tempted to choose the model-prompt combination that produces a significantly positive relationship. In theory, one could potentially iterate on plausible-sounding prompts until one is found that generates the preferred downstream results, given the increasingly low cost of iteration. Put another way, the use of LLMs for this type of application lowers the cost of p-hacking, making comprehensive sensitivity analysis more urgent. This connects to broader concerns about researcher degrees of freedom in empirical research, where the ease of testing multiple specifications, control variables, or model variations can lead researchers to focus on achieving statistical significance rather than understanding the magnitude and robustness of their findings (Shaver, 2007). The low cost and speed of LLM iteration creates analogous opportunities for such methodological cherry-picking.

Proposed Decision. Given both the first-stage accuracy results and downstream analysis implications, we would propose implementing GPT-4o with Tree of Thoughts prompting as our baseline classification method for the full dataset. This configuration achieved the highest accuracy, with good balance between false positives and negatives, at reasonable cost, and successfully recovered the expected relationship between sustainability claims and funding success. Noe that we do not expect this model-prompt combination to be optimal for all annotation tasks or to remain the best approach as models and prompting strategies continue to evolve; researchers should ideally conduct their own systematic testing for their specific tasks and contexts. Moreover, our analysis reveals that strong first-stage performance does not guarantee reliable downstream results, and even reasonable methodological choices can

produce different research conclusions. Therefore, we would propose a multi-pronged validation strategy: (1) use our best-performing configuration for primary analysis, (2) implement systematic sensitivity testing for all key findings using multiple model-prompt combinations, and (3) report bounded estimates that reflect underlying methodological uncertainty. This approach aligns with our framework's emphasis on rigorous validation while acknowledging the unique challenges that LLMs present for research reproducibility.

### 3.5 Stage 5: Validation and Robustness

Generating Prompt Variations. To extend our sensitivity analysis, we created a set of 100 unique prompts, similar to those shown in Table 3 and exhibiting a range of prompting strategies. We used the Claude-3.5-Sonnet chat interface for this task, providing it with the prompt instructions shown in Figure 2. In the instructions, we ask the LLM to generate unique and systematically varied prompts, evenly divided among the seven prompting strategies tested above. The prompt instructs the LLM to format the output as a csv (comma-separated values) file with the type of strategy (e.g. chain-of-thought, few-shot) as a separate column, so that we might systematically test how downstream outputs vary with each type of prompting design.

## [INSERT FIGURE 2 ABOUT HERE]

The resulting set of prompt variations produces approximately 14-15 variations of each type of prompting strategy, each directing the same fundamental task (the full set of prompts can be viewed in Appendix E).

Baseline Sensitivity. Figure 3 shows the distribution of downstream regression coefficients across prompt variations, using either GPT-4o (the highest performing model of those tested) or GPT-4o-mini (the lowest-cost model). As demonstrated by the earlier tests, there is considerable variation even within model across prompt specifications. The overall variance shrinks slightly with quality control restrictions, such as limited to advanced prompting

strategies only (Panel C) or dropping prompts below a threshold for first-stage accuracy (Panel E). In all cases, however, the “true” positive relationship between sustainability claims and funding success can be recovered in a confidence interval constructed within one standard deviation of the mean coefficient value across estimates.

## [INSERT FIGURE 3 ABOUT HERE]

We test several cost-reduction strategies to check the limitations of such sensitivity analysis to increasingly lightweight solutions. First, we examine a low-cost mini model, GPT-4o-mini (Panel B), finding that it produces a similar distribution of coefficients to its more expensive counterpart, albeit with slightly higher dispersion. Second, we test replacing the full Kickstarter description with only the short project taglines (typically one to three sentences). This latter intervention reduces the estimated mean coefficient by nearly 30 percent, but still preserves the overall positive relationship, suggesting that even with massively reduced information, the fundamental pattern remains detectable.

Proposed Decision. As discussed above, we proposed to use GPT-4o with Tree of Thought (ToT) prompting as the baseline model-prompt combination for the main analysis, based on its based on its strong performance in our tests and favorable cost profile. We would additionally propose reporting, at a minimum, sensitivity analysis similar to Figure 3, Panels (A) and (E) as standard robustness checks. This approach demonstrates that the findings are not merely artifacts of the specific prompt selected, but represent a robust relationship that persists across methodological variations.

The specific sensitivity analyses reported may vary according to the needs of a given project and the particular empirical concerns therein. We discuss several of these alternatives below.

#### Additional Use Cases for Sensitivity Analysis

Bootstrapping for Large Samples. For analyses involving particularly large datasets, comprehensive sensitivity testing may become prohibitively expensive and time-consuming even with low-cost models. In such cases, researchers can implement an adapted version of the sensitivity analysis described above using bootstrapping techniques, by repeatedly sampling smaller subsets (e.g., 1,000 observations) from the full dataset. In this way, researchers can test sensitivity across multiple prompt variations at significantly reduced computational cost.

Ablation Testing. Sensitivity analysis can be combined with formal ablation testing to address specific methodological concerns or disagreements, for example, in a formal peer review process. For instance, if questions arise regarding particular language elements in the prompt (e.g., the phrase “beyond its consumers” in defining societal benefit), researchers can modify the prompt generation template (Figure 2) to create a controlled comparison—generating a balanced set of prompts with and without the language in question, alongside indicator variables tracking these variations. This controlled sensitivity analysis can reveal whether downstream coefficients systematically vary with specific prompt elements – therefore providing some empirical grounds for resolving methodological disagreements.

Supplementary Analysis for Other Methods of Annotation. When primary analyses rely on more resource-intensive annotation procedures – e.g., human coding – LLM-based sensitivity analysis offers an efficient method for testing theoretical extensions or variations. If, for example, reviewers suggest shifting theoretical emphasis (e.g., from general societal benefit to specific environmental benefit), researchers can rapidly test the implications by creating parallel sets of prompt variations measuring different theoretical constructs. This approach can provide preliminary evidence regarding the consistency of findings across various framings at a fraction of the cost of repeated human annotation, serving as valuable supplementary analysis to the primary research. $ ^{13} $

## 4 Discussion

In this article, we provide a foundational framework for implementing LLMs in management research, with a particular focus on data annotation tasks. Our empirical application demonstrates both the potential and pitfalls of using these technologies for classification tasks commonly encountered in social science applications. Several key insights emerge from our findings that have important implications for researchers.

A central finding from our empirical application is that variations in prompt design and model selection can lead to substantially different downstream research conclusions, even when first-stage accuracy metrics appear similar. While this sensitivity might initially seem problematic, we argue that it actually represents a methodological opportunity when properly managed. Traditional approaches to data annotation – whether human coding or conventional machine learning – have always contained subjective elements and researcher degrees of freedom, but the associated costs often prevented comprehensive sensitivity testing. The relative affordability and speed of LLM implementation enables systematic exploration of how key methodological choices affect research conclusions.

This emphasis on sensitivity testing aligns with longstanding principles in social science methodology. Just as researchers routinely employ robustness checks for regression specifications, variable construction, or sample definitions, we propose that LLM implementation should similarly incorporate systematic sensitivity analysis. However, the democratization of annotation through LLMs also creates new challenges for research integrity analogous to traditional concerns about researcher degrees of freedom (Shaver, 2007). The low cost and speed of LLM iteration means researchers can easily test numerous model-prompt combinations, creating opportunities for specification searching that must be guarded against through transparent reporting of all tested configurations. We emphasize the importance of

bounding estimates rather than seeking a single "optimal" implementation.

Our finding that higher first-stage accuracy doesn't necessarily translate to better downstream results deserves particular attention. When a model misclassifies data in ways that correlate with outcome variables, second-stage estimates may be systematically biased. This challenge is not unique to LLMs, but the potential for large-scale implementation makes it particularly consequential. This finding underscores the importance of validating LLM implementations at multiple stages of the research pipeline, not just at the initial classification stage. This principle of multi-stage validation is a fundamental methodological consideration that should remain relevant, regardless of how LLM technology evolves.

The rapid evolution of LLMs necessitates new standards for research transparency and reproducibility. Our framework emphasizes thorough documentation of model selection, prompt design, and any other decision parameters. This documentation serves two purposes: enabling direct replication of findings and allowing for systematic exploration of how methodological choices affect results. The dramatic cost difference between human coding and LLM implementation suggests significant potential for scaling research designs. However, this scale advantage will ideally be balanced against the need for thorough validation and sensitivity testing: that is, the efficiency gains from LLMs can be partially reinvested in more comprehensive methodological validation.

Our approach also underscores the continued centrality of human expertise in the LLM era. While these technologies can dramatically reduce the cost and time required for large-scale annotation, they do not eliminate the need for careful human judgment in establishing ground truth, designing validation procedures, and interpreting results.

Several practical implications emerge from our framework and empirical application. First, researchers should explicitly plan for sensitivity analysis from the outset, rather than treating it as an afterthought. Systematic variation in prompt design, model selection, and parameter

settings should be incorporated into research design and budgeting. Second, researchers should consider hybrid approaches that leverage the strengths of different methodologies. For example, human coding might be used for creating high-quality validation sets, while LLMs aid in facilitating large-scale implementation. Similarly, multiple LLM implementations with varying approaches might be used to bound estimates and establish robustness. Third, researchers should prioritize reproducibility over cutting-edge performance. Documenting exact model versions, prompts, and parameters remains essential for building on scientific progress.

Our study has several limitations that suggest opportunities for future research. First, while our empirical application focuses on binary classification in a specific context, future work should extend these approaches to more complex annotation tasks. Second, as LLM technology continues to evolve, future research should systematically compare how newer architectures affect sensitivity to methodological choices. More fundamentally, as researchers increasingly adopt LLMs in their methodological toolkit, the field needs continued development of best practices and standards. Just as statistical methods have evolved established norms for appropriate implementation and reporting, LLM methods will require similar disciplinary consensus. Ongoing refinement through methodological dialogue will be essential.

## 5 Conclusion

LLMs have become a powerful addition to the management researcher's methodological toolkit, reducing costs while maintaining or improving accuracy compared to traditional approaches. However, their implementation requires careful attention to methodological choices and systematic validation procedures. The fundamental principles of research design – transparency, validity, reliability, and robustness – remain as relevant for LLM implementation as they are for established methods.

As with any methodological innovation, the scientific value of LLMs ultimately depends less

on their technological sophistication than on their thoughtful implementation within rigorous research designs. By providing a foundational framework for implementation decisions and validation procedures, we hope to establish baseline methodology that facilitates responsible integration of these tools into management research. As LLM technology continues to evolve rapidly, this framework should be viewed as a starting point for methodological development rather than a definitive guide. We encourage future researchers to build upon these foundations, testing our principles across different domains, tasks, and technological advances, and extending our approach as new models and capabilities emerge. The rapid pace of development in this field necessitates ongoing methodological innovation, and we hope this work provides a structured foundation for such future contributions to advance the responsible use of AI in management research.

## References

Agrawal, A., C. Catalini, and A. Goldfarb (2014). Some Simple Economics of Crowdfunding. Innovation Policy and the Economy 14(June), 63–97.

An, S., Z. Ma, Z. Lin, N. Zheng, and J.-G. Lou (2024). Make Your LLM Fully Utilize the Context. arXiv preprint arXiv:2404.16811.

Armstrong, L., A. Liu, S. MacNeil, and D. Metaxa (2024, October). The Silicon Ceiling: Auditing GPT’s Race and Gender Biases in Hiring. In Proceedings of the 4th ACM Conference on Equity and Access in Algorithms, Mechanisms, and Optimization, pp. 1–18.

Battle, R. and T. Gollapudi (2024). The Unreasonable Effectiveness of Eccentric Automatic Prompts.

Bender, E. M., T. Gebru, A. McMillan-Major, and S. Shmitchell (2021). On the dangers of stochastic parrots: Can language models be too big? FAccT 2021 - Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency, 610–623.

Bommasani, R., D. A. Hudson, E. Adeli, R. Altman, S. Arora, S. von Arx, M. S. Bernstein, et al. (2021). On the Opportunities and Risks of Foundation Models. arXiv preprint arXiv:2108.07258.

Boussioux, L., J. N. Lane, M. Zhang, V. Jacimovic, and K. R. Lakhani (2023). The Crowdless Future? How Generative AI Is Shaping the Future of Human Crowdsourcing. SSRN Electronic Journal.

Brown, T. B., G. Krueger, B. Mann, A. Askell, A. Herbert-voss, C. Winter, D. M. Ziegler, A. Radford, and S. Mccandlish (2020). Language Models are Few-Shot Learners. Advances in Neural Information Processing Systems 33.

Brynjolfsson, E., D. Li, and L. R. Raymond (2023). Generative AI at Work. NBER Working Paper.

Calic, G. and E. Mosakowski (2016). Kicking Off Social Entrepreneurship: How A Sustainability Orientation Influences Crowdfunding Success. Journal of Management Studies 53(5), 738–767.

Chattopadhyay, S., Y. Han, F. Honore, and S. Won (2024). Getting a 25th Hour: Fine-Tuning Pre-Trained LLMs to Classify Text Data for Strategy Research. Working Paper.

Chen, J. and J. Mueller (2023). Quantifying Uncertainty in Answers from Any Language Model via Intrinsic and Extrinsic Confidence Assessment. arXiv preprint arXiv:2308.16175.

Chopra, F. and I. Haaland (2023). Conducting Qualitative Interviews with AI. Working Paper.

Choudhury, P., R. T. Allen, and M. G. Endres (2021). Machine Learning for Pattern Discovery in Management Research. Strategic Management Journal 42(1), 30–57.

Chowdhery, A., S. Narang, J. Devlin, M. Bosma, G. Mishra, A. Roberts, P. Barham, et al. (2023). Palm: Scaling Language Modeling with Pathways. Journal of Machine Learning Research 24(240), 1–113.

Csaszar, F. A., H. Ketkar, and H. Kim (2024). Artificial Intelligence and Strategic Decision-Making: Evidence from Entrepreneurs and Investors. Strategy Science 9(4), 322–345.

Dell'Acqua, F., E. McFowland, E. Mollick, H. Lifshitz-Assaf, and K. C. Kellogg (2023). Navigating the Jagged Technological Frontier: Field Experimental Evidence of the Effects of AI on Knowledge Worker Productivity and Quality. Working Paper.

Ding, N., Y. Qin, G. Yang, F. Wei, Z. Yang, Y. Su, S. Hu, et al. (2023). Parameter-Efficient Fine-Tuning of Large-Scale Pre-Trained Language Models. Nature Machine Intelligence 5(3), 220–235.

Dodge, J., S. Gururangan, D. Card, R. Schwartz, and N. A. Smith (2019). Show Your Work: Improved Reporting of Experimental Results. arXiv preprint arXiv:1909.03004.

Doshi, A., J. J. Bell, E. Mirzayev, and B. Vanneste (2024). Generative Artificial Intelligence and Evaluating Strategic Decisions. Strategic Management Journal. Forthcoming.

Dror, R., G. Baumer, S. Shlomov, and R. Reichart (2018). The Hitchhiker's Guide to Testing Statistical Significance in Natural Language Processing. In Proceedings of the 56th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 1383–1392.

Egami, N., M. Hinck, B. M. Stewart, and H. Wei (2024). Using Large Language Model Annotations for the Social Sciences: A General Framework of Using Predicted Variables in Statistical Analyses.

Eloundou, T., S. Manning, P. Mishkin, and D. Rock (2023). GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models. Working Paper.

Friedman, J. H. (2001). Greedy Function Approximation a Gradient Boosting Machine. Annals of Statistics, 1189–1232.

Gao, Y., Y. Xiong, X. Gao, K. Jia, J. Pan, Y. Bi, Y. Dai, J. Sun, and H. Wang (2023). Retrieval-Augmented Generation for Large Language Models: A Survey. arXiv preprint arXiv:2312.10997.

Gilardi, F., M. Alizadeh, and M. Kubli (2023). ChatGPT Outperforms Crowd-Workers for Text-Annotation Tasks. arXiv Working Paper.

Grimmer, J. and B. M. Stewart (2013). Text as Data: The Promise and Pitfalls of Automatic Content Analysis Methods for Political Texts. Political Analysis 21(3), 267–297.

Hui, W., Y. Wang, K. Tu, and C. Jiang (2024). RoT: Enhancing Large Language Models with Reflection on Search Trees. arXiv preprint arXiv:2404.05449.

Jia, N., X. Luo, Z. Fang, and C. Liao (2025). When and How Artificial Intelligence Augments Employee Creativity. Forthcoming, Academy of Management Journal.

Jia, N., A. Roh, J. Song, and Y. Wei (2025). From Cognitive to Social Tasks: How AI Transforms Organizational Demand for Human Capital in Professional Service Firms. Working Paper.

Jin, H., X. Han, J. Yang, Z. Jiang, Z. Liu, C.-Y. Chang, H. Chen, and X. Hu (2024). LLM Maybe LongLM: Self-Extend LLM Context Window Without Tuning. arXiv preprint arXiv:2401.01325.

Kaplan, J., S. McCandlish, T. Henighan, T. B. Brown, B. Chess, R. Child, S. Gray, A. Radford, J. Wu, and D. Amodei (2020). Scaling Laws for Neural Language Models. arXiv preprint arXiv:2001.08361.

Kapoor, S. and A. Narayanan (2022). Leakage and the Reproducibility Crisis in ML-Based Science. arXiv preprint arXiv:2207.07048.

Lewis, P., E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. Küttler, et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. In Advances in Neural Information Processing Systems, Volume 33, pp. 9459–9474.

Meincke, L., E. Mollick, and C. Terwiesch (2024). Prompting Diverse Ideas: Increasing AI Idea Variance. Working Paper.

Meincke, L., E. R. Mollick, L. Mollick, and D. Shapiro (2025a, March). Prompting Science Report 1: Prompt Engineering is Complicated and Contingent. SSRN Working Paper.

Meincke, L., E. R. Mollick, L. Mollick, and D. Shapiro (2025b, June). Prompting Science Report 2: The Decreasing Value of Chain of Thought in Prompting. SSRN Working Paper.

Miric, M., N. Jia, and K. G. Huang (2023). Using supervised machine learning for large-scale classification in management research: The case for identifying artificial intelligence patents. Strategic Management Journal 44(2), 491–519.

Mitchell, M., S. Wu, A. Zaldivar, P. Barnes, L. Vasserman, B. Hutchinson, E. Spitzer, I. D. Raji, and T. Gebru (2019). Model Cards for Model Reporting. In Proceedings of the Conference on Fairness, Accountability, and Transparency, pp. 220–229.

Mollick, E. (2014). The dynamics of crowdfunding: An exploratory study. Journal of Business Venturing 29, 1.

Otis, N., R. P. Clarke, S. Delecourt, D. Holtz, and R. Koning (2024). The Uneven Impact of Generative AI on Entrepreneurial Performance. SSRN Electronic Journal.

Peeperkorn, M., T. Kouwenhoven, D. Brown, and A. Jordanous (2024). Is Temperature the Creativity Parameter of Large Language Models? arXiv preprint arXiv:2405.00492.

Quinn, K. M., B. L. Monroe, M. Colaresi, M. H. Crespin, and D. R. Radev (2010). How to Analyze Political Attention with Minimal Assumptions and Costs. American Journal of Political Science 54(1), 209–228.

Raff, E. (2019). A Step Toward Quantifying Independently Reproducible Machine Learning Research. In Advances in Neural Information Processing Systems, Volume 32.

Rathje, S., D.-M. Mirea, I. Sucholutsky, R. Marjieh, C. Robertson, and J. Van Bavel (2023). GPT is an Effective Tool for Multilingual Psychological Text Analysis. PsyArXiv Preprints.

Reynolds, L. and K. McDonell (2021). Prompt Programming for Large Language Models: Beyond the Few-Shot Paradigm. In Extended Abstracts of the 2021 CHI Conference on Human Factors in Computing Systems, pp. 1–7.

Ribeiro, M. T., T. Wu, C. Guestrin, and S. Singh (2020). Beyond Accuracy: Behavioral Testing of NLP Models with CheckList. arXiv preprint arXiv:2005.04118.

Sahoo, P., A. K. Singh, S. Saha, V. Jain, S. Mondal, and A. Chadha (2024). A Systematic Survey of Prompt Engineering in Large Language Models: Techniques and Applications. arXiv preprint arXiv:2402.07927.

Sclar, M., Y. Choi, Y. Tsvetkov, and A. Suhr (2023). Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design or: How I learned to start worrying about prompt formatting.

Shaver, J. M. (2007). Interpreting Empirical Results in Strategy and Management Research. In Research Methodology in Strategy and Management, pp. 273–293. Emerald Group Publishing Limited.

Shorten, C., C. Pierse, T. B. Smith, E. Cardenas, A. Sharma, J. Trengrove, and B. van Luijt (2024). StructuredRAG: JSON Response Formatting with Large Language Models. arXiv preprint arXiv:2408.11061.

Sorenson, O., V. Assenova, G.-C. Li, J. Boada, and L. Fleming (2016). Expand innovation finance via crowdfunding. Science 354(6319), 1526–1528.

Taeuscher, K., R. Bouncken, and R. Pesch (2021). Gaining Legitimacy by Being Different: Optimal Distinctiveness in Crowdfunding Platforms. Academy of Management Journal 64(1), 149–179.

Tam, Z. R., C.-K. Wu, Y.-L. Tsai, C.-Y. Lin, H.-y. Lee, and Y.-N. Chen (2024). Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models. arXiv preprint arXiv:2408.02442.

Tornberg, P. (2023). ChatGPT-4 Outperforms Experts and Crowd Workers in Annotating Political Twitter Messages with Zero-Shot Learning. arXiv Working Paper.

Tranchero, M., C.-F. Brenninkmeijer, A. Murugan, and A. Nagaraj (2024). Theorizing with Large Language Models. Working Paper.

Tu, X., J. Zou, W. J. Su, and L. Zhang (2023). What Should Data Science Education Do with Large Language Models. arXiv Working Paper.

Törnberg, P. (2024). Best Practices for Text Annotation with Large Language Models. arXiv preprint arXiv:2402.05129.

Vaswani, A., N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser, and I. Polosukhin (2017). Attention is all you need. Advances in Neural Information Processing Systems, 5999–6009.

Wang, X., J. Wei, D. Schuurmans, Q. Le, E. Chi, S. Narang, and D. Zhou (2022). Self-Consistency Improves Chain of Thought Reasoning in Language Models. arXiv preprint arXiv:2203.11171.

Weber, M. and M. Reichardt (2023). Evaluation is All You Need: Prompting Generative Large Language Models for Annotation Tasks in the Social Sciences. A Primer Using Open Models. arXiv preprint arXiv:2401.00284.

Wei, J., M. Bosma, V. Y. Zhao, K. Guu, A. W. Yu, B. Lester, N. Du, A. M. Dai, and Q. V. Le (2021). Finetuned Language Models Are Zero-Shot Learners. arXiv preprint arXiv:2109.01652.

Wei, J., X. Wang, D. Schuurmans, M. Bosma, F. Xia, E. Chi, Q. V. Le, and D. Zhou (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. In Advances in Neural Information Processing Systems, Volume 35, pp. 24824–24837.

Weidinger, L., J. Mellor, M. Rauh, C. Griffin, J. Uesato, P.-S. Huang, M. Cheng, et al. (2021). Ethical and Social Risks of Harm from Language Models. arXiv preprint arXiv:2112.04359.

Xiong, M., Z. Hu, X. Lu, Y. Li, J. Fu, J. He, and B. Hooi (2023). Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs. arXiv preprint arXiv:2306.13063.

Yao, S., D. Yu, J. Zhao, I. Shafran, T. Griffiths, Y. Cao, and K. Narasimhan (2024). Tree of Thoughts: Deliberate Problem Solving with Large Language Models. In Advances in Neural Information Processing Systems, Volume 36.

Yu, S., S. Johnson, C. Lai, A. Cricelli, and L. Fleming (2017). Crowdfunding and regional entrepreneurial investment: an application of the CrowdBerkeley database. Research Policy 46(10), 1723–1737.

Zhao, Z., E. Wallace, S. Feng, D. Klein, and S. Singh (2021). Calibrate Before Use: Improving Few-Shot Performance of Language Models. In International Conference on Machine Learning, pp. 12697–12706. PMLR.

<div style="text-align: center;"><div style="text-align: center;">Table 1: Core Principles and Guidelines for Integrating LLMs Into Research</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Research Stage</td><td style='text-align: center; word-wrap: break-word;'>Principle(s)</td><td style='text-align: center; word-wrap: break-word;'>Tradeoffs</td><td style='text-align: center; word-wrap: break-word;'>Best Practices</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1. Method selection and integration (Do we use LLMs or another method?)</td><td style='text-align: center; word-wrap: break-word;'>Consider LLMs as part of a broader methodological toolkit; match method to research context and data characteristics</td><td style='text-align: center; word-wrap: break-word;'>· Human Coding: High accuracy and nuance but expensive/slow/limited scale· Keywords/Dictionary: Transparent and simple but rigid/context-blind· Supervised ML: Scalable and consistent but requires training data/domain expertise· LLMs: Flexible and fast but potentially unstable/opaque</td><td style='text-align: center; word-wrap: break-word;'>· Begin with clear task specification and success criteria· Use human coding for validation and complex edge cases· Consider hybrid approaches· Document relative performance across methods</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2. Model selection and stability (Which LLM should we be using?)</td><td style='text-align: center; word-wrap: break-word;'>Prioritize reproducibility and documentation over cutting-edge performance</td><td style='text-align: center; word-wrap: break-word;'>· Newer models: Better performance but less tested/stable· Older models: More stable but potentially lower performance· Open vs. closed models: Access/cost vs. performance· Reasoning models: Optimized for complex reasoning vs. uncertain effectiveness for basic annotation tasks</td><td style='text-align: center; word-wrap: break-word;'>· Document model version and access method· Test multiple models as part of sensitivity analysis· Archive model weights (if open-source) or maintain access to older versions if possible· Plan for replication needs· Consider data security if annotating sensitive data (check policies around usage and storage)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3. Prompt engineering (How do we design and validate our prompts?)</td><td style='text-align: center; word-wrap: break-word;'>Structure prompts systematically and transparently; document thoroughly</td><td style='text-align: center; word-wrap: break-word;'>· Simple prompts: More stable but potentially lower accuracy· Complex prompts: Better performance but harder to replicate· Generic vs. task-specific prompting: Generalizability vs. accuracy</td><td style='text-align: center; word-wrap: break-word;'>· Use established frameworks (Chain of Thought, few-shot learning)· Generate systematic prompt variations for sensitivity testing· Document all prompt components· Test prompts on diverse examples</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4. Cost and scale considerations (How do we optimize resources while maintaining rigor?)</td><td style='text-align: center; word-wrap: break-word;'>Balance resource usage with statistical power and robustness needs</td><td style='text-align: center; word-wrap: break-word;'>· Sample size vs. token usage· Prompt complexity vs. processing cost· Depth vs. breadth of sensitivity testing· Model size vs. performance gains</td><td style='text-align: center; word-wrap: break-word;'>· Plan sensitivity analysis within resource constraints· Document cost structure and optimization decisions· Consider computational constraints for replication</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5. Validation and robustness assessment (How reliable and stable are our findings?)</td><td style='text-align: center; word-wrap: break-word;'>Conduct systematic evaluation of result validity and stability</td><td style='text-align: center; word-wrap: break-word;'>· Depth vs. breadth of validation testing· Cost of comprehensive testing vs. confidence in results· Simple vs. complex sensitivity metrics</td><td style='text-align: center; word-wrap: break-word;'>· If feasible, maintain gold-standard expert-coded subset· Generate systematic prompt variations· Test impact on downstream analyses· Provide bounded estimates for key findings· Document null results and validation protocols</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">Table 2: Prompt Engineering Strategies</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Approach</td><td style='text-align: center; word-wrap: break-word;'>Description</td><td style='text-align: center; word-wrap: break-word;'>Tradeoffs</td><td style='text-align: center; word-wrap: break-word;'>Implementation Guidelines</td><td style='text-align: center; word-wrap: break-word;'>Common Pitfalls</td></tr><tr><td colspan="3">Basic Prompting Strategies</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Zero-Shot Prompting</td><td style='text-align: center; word-wrap: break-word;'>Direct task instruction without examples</td><td style='text-align: center; word-wrap: break-word;'>Simplicity vs. accuracy; speed vs. reliability</td><td style='text-align: center; word-wrap: break-word;'>Clear coding criteria; explicit classification rules; unambiguous metrics; document exact prompt for reproducibility</td><td style='text-align: center; word-wrap: break-word;'>Assumption of task understanding; lack of theoretical grounding; ambiguous or underspecified instructions can lead to inconsistent or irrelevant results</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Few-Shot Prompting</td><td style='text-align: center; word-wrap: break-word;'>Including examples in prompt</td><td style='text-align: center; word-wrap: break-word;'>Higher accuracy but more token usage; risk that a non-representative few-shot set skews outputs</td><td style='text-align: center; word-wrap: break-word;'>Use 3-5 carefully validated examples that cover edge cases to avoid partial coverage; consistent formatting</td><td style='text-align: center; word-wrap: break-word;'>Non-representative example selection; overfitting to examples</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Role-Based Prompting</td><td style='text-align: center; word-wrap: break-word;'>Assigning an identity to focus responses on relevant domain knowledge</td><td style='text-align: center; word-wrap: break-word;'>Improved focus vs. potential role-induced bias</td><td style='text-align: center; word-wrap: break-word;'>Clear role definition; consistent persona; relevant expertise</td><td style='text-align: center; word-wrap: break-word;'>Inconsistent role adherence; superficial or performative ‘expertise’ without real domain rigor; potential bias introduction (stereotypes)</td></tr><tr><td colspan="3">Advanced Reasoning Prompts</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Chain of Thought (CoT)</td><td style='text-align: center; word-wrap: break-word;'>Explicit step-by-step reasoning process</td><td style='text-align: center; word-wrap: break-word;'>Transparency vs. token usage; clarity vs. length</td><td style='text-align: center; word-wrap: break-word;'>Clear reasoning steps; logical flow; explicit connections</td><td style='text-align: center; word-wrap: break-word;'>Unnecessary complexity; faulty logic chains; diminishing returns with more recent models</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Self-Consistency</td><td style='text-align: center; word-wrap: break-word;'>Multiple independent attempts at same task</td><td style='text-align: center; word-wrap: break-word;'>Reliability vs. computational cost</td><td style='text-align: center; word-wrap: break-word;'>Multiple runs with varied parameters; consistency metrics; define clear aggregation rules (majority vote, weighted average)</td><td style='text-align: center; word-wrap: break-word;'>Inefficient resource use; unclear aggregation methods</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Tree of Thought (ToT)</td><td style='text-align: center; word-wrap: break-word;'>Systematic exploration of multiple solution paths with branching decision points</td><td style='text-align: center; word-wrap: break-word;'>Comprehensive analysis vs. computational efficiency; depth vs. breadth of exploration</td><td style='text-align: center; word-wrap: break-word;'>Define clear branching criteria; establish explicit stopping conditions; maintain structured path tracking</td><td style='text-align: center; word-wrap: break-word;'>Exponential complexity growth; incomplete path exploration; resource exhaustion</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Reflection on Search Trees (RoT)</td><td style='text-align: center; word-wrap: break-word;'>Structured analysis with recursive evaluation of solution paths</td><td style='text-align: center; word-wrap: break-word;'>Enhanced decision quality vs. increased complexity; depth of analysis vs. computational cost</td><td style='text-align: center; word-wrap: break-word;'>Implement clear reflection criteria; balance depth of recursion; maintain systematic evaluation metrics</td><td style='text-align: center; word-wrap: break-word;'>Over-complex reflection loops; loss of focus on primary objective; excessive computational overhead</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">Table 3: Examples of Different Prompting Strategies in Practice</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Zero-Shot</td><td style='text-align: center; word-wrap: break-word;'>Please read the text of the following Kickstarter campaign and consider the following question. Does the main product or service offered benefit the broader society (beyond its consumers)? Answer only with a number: 1 for yes, 0 for no. Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Few-Shot</td><td style='text-align: center; word-wrap: break-word;'>Please read the text of the following Kickstarter campaign and consider whether the main product or service benefits the broader society (beyond its consumers). Examples: 1) “Solar-powered water purifier for communities” = 1 (benefits environment and public health), 2) “Premium leather accessories” = 0 (consumer-only benefit), 3) “Educational coding app for children” = 1 (benefits education and skill development). Using these examples as guidance, classify the following text with 1 for yes or 0 for no. Answer only with a number. Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Role-Based</td><td style='text-align: center; word-wrap: break-word;'>As an expert researcher in corporate social responsibility, evaluate whether the following Kickstarter campaign’s main product or service benefits the broader society (beyond its consumers). Based on your expertise, classify the text with 1 for yes or 0 for no. Answer only with a number. Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Chain of Thought (CoT)</td><td style='text-align: center; word-wrap: break-word;'>Please read the following Kickstarter campaign and determine if the main product or service benefits the broader society (beyond its consumers). First identify the core offering, then list consumer benefits, examine societal impacts, and assess their significance. After this analysis, provide your classification: 1 for yes (clear broader societal benefits) or 0 for no (primarily consumer benefits). Answer only with a number. Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Self-Consistency</td><td style='text-align: center; word-wrap: break-word;'>Please evaluate this Kickstarter campaign three times to determine if the main product or service benefits the broader society (beyond its consumers). First consider immediate impacts, then long-term effects, and finally the scale of benefits. Provide a 1 or 0 classification for each evaluation, then give a final classification based on the majority outcome. Answer only with a number. Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Tree of Thought (ToT)</td><td style='text-align: center; word-wrap: break-word;'>Please evaluate whether this Kickstarter campaign’s main product or service benefits the broader society (beyond its consumers) through three paths: 1) Impact scope (direct/indirect beneficiaries), 2) Sustainability framework (environmental/social/economic), 3) Public good criteria. Follow each path to its conclusion, then synthesize into a final 1 or 0 classification. Answer only with a number. Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Reflection on Search Trees (RoT)</td><td style='text-align: center; word-wrap: break-word;'>Please evaluate whether this Kickstarter campaign’s main product or service benefits the broader society (beyond its consumers) through branching analysis paths. For each potential classification (1 or 0), generate two supporting arguments. Reflect on the strength of each argument, considering uncertainty and evidence quality. Rate confidence in each path (high/medium/low), then provide final 0 or 1 classification based on the strongest reasoning chain. Answer only with a number. Here is the text:</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">Table 4: First Stage Results Comparison</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Model</td><td style='text-align: center; word-wrap: break-word;'>Overall Accuracy</td><td style='text-align: center; word-wrap: break-word;'>False Positives</td><td style='text-align: center; word-wrap: break-word;'>False Negatives</td><td style='text-align: center; word-wrap: break-word;'>Cost (USD)</td><td style='text-align: center; word-wrap: break-word;'>Tokens</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GBM (Prior Classifier)</td><td style='text-align: center; word-wrap: break-word;'>0.920</td><td style='text-align: center; word-wrap: break-word;'>0.033</td><td style='text-align: center; word-wrap: break-word;'>0.044</td><td style='text-align: center; word-wrap: break-word;'>approx. $3000</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Zero-Shot</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>170,348</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.652</td><td style='text-align: center; word-wrap: break-word;'>0.348</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$5.25</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.876</td><td style='text-align: center; word-wrap: break-word;'>0.112</td><td style='text-align: center; word-wrap: break-word;'>0.012</td><td style='text-align: center; word-wrap: break-word;'>$0.45</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.416</td><td style='text-align: center; word-wrap: break-word;'>0.584</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.784</td><td style='text-align: center; word-wrap: break-word;'>0.204</td><td style='text-align: center; word-wrap: break-word;'>0.012</td><td style='text-align: center; word-wrap: break-word;'>$2.74</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.580</td><td style='text-align: center; word-wrap: break-word;'>0.416</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.15</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Few-Shot</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>188,848</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.752</td><td style='text-align: center; word-wrap: break-word;'>0.240</td><td style='text-align: center; word-wrap: break-word;'>0.004</td><td style='text-align: center; word-wrap: break-word;'>$5.81</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.896</td><td style='text-align: center; word-wrap: break-word;'>0.080</td><td style='text-align: center; word-wrap: break-word;'>0.024</td><td style='text-align: center; word-wrap: break-word;'>$0.50</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.796</td><td style='text-align: center; word-wrap: break-word;'>0.200</td><td style='text-align: center; word-wrap: break-word;'>0.004</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.764</td><td style='text-align: center; word-wrap: break-word;'>0.216</td><td style='text-align: center; word-wrap: break-word;'>0.020</td><td style='text-align: center; word-wrap: break-word;'>$3.02</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.664</td><td style='text-align: center; word-wrap: break-word;'>0.332</td><td style='text-align: center; word-wrap: break-word;'>0.004</td><td style='text-align: center; word-wrap: break-word;'>$0.16</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Role-Based</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>173,598</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.668</td><td style='text-align: center; word-wrap: break-word;'>0.332</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$5.35</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.888</td><td style='text-align: center; word-wrap: break-word;'>0.100</td><td style='text-align: center; word-wrap: break-word;'>0.012</td><td style='text-align: center; word-wrap: break-word;'>$0.46</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.556</td><td style='text-align: center; word-wrap: break-word;'>0.444</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.804</td><td style='text-align: center; word-wrap: break-word;'>0.180</td><td style='text-align: center; word-wrap: break-word;'>0.016</td><td style='text-align: center; word-wrap: break-word;'>$2.79</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.672</td><td style='text-align: center; word-wrap: break-word;'>0.328</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.15</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Chain-of-Thought (CoT)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>182,348</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.736</td><td style='text-align: center; word-wrap: break-word;'>0.260</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$5.61</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.900</td><td style='text-align: center; word-wrap: break-word;'>0.092</td><td style='text-align: center; word-wrap: break-word;'>0.008</td><td style='text-align: center; word-wrap: break-word;'>$0.48</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.712</td><td style='text-align: center; word-wrap: break-word;'>0.288</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.876</td><td style='text-align: center; word-wrap: break-word;'>0.096</td><td style='text-align: center; word-wrap: break-word;'>0.028</td><td style='text-align: center; word-wrap: break-word;'>$2.92</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.696</td><td style='text-align: center; word-wrap: break-word;'>0.304</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.16</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Self-Consistency</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>179,848</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.576</td><td style='text-align: center; word-wrap: break-word;'>0.424</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$5.53</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.904</td><td style='text-align: center; word-wrap: break-word;'>0.088</td><td style='text-align: center; word-wrap: break-word;'>0.008</td><td style='text-align: center; word-wrap: break-word;'>$0.47</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.548</td><td style='text-align: center; word-wrap: break-word;'>0.452</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.872</td><td style='text-align: center; word-wrap: break-word;'>0.100</td><td style='text-align: center; word-wrap: break-word;'>0.028</td><td style='text-align: center; word-wrap: break-word;'>$2.88</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.624</td><td style='text-align: center; word-wrap: break-word;'>0.376</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.15</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Tree-of-Thought (ToT)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>180,348</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.796</td><td style='text-align: center; word-wrap: break-word;'>0.204</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$5.55</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.940</td><td style='text-align: center; word-wrap: break-word;'>0.036</td><td style='text-align: center; word-wrap: break-word;'>0.024</td><td style='text-align: center; word-wrap: break-word;'>$0.48</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.668</td><td style='text-align: center; word-wrap: break-word;'>0.328</td><td style='text-align: center; word-wrap: break-word;'>0.004</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.880</td><td style='text-align: center; word-wrap: break-word;'>0.080</td><td style='text-align: center; word-wrap: break-word;'>0.036</td><td style='text-align: center; word-wrap: break-word;'>$2.89</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.548</td><td style='text-align: center; word-wrap: break-word;'>0.452</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.15</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Reflection on Search Trees (RoT)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>185,848</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.604</td><td style='text-align: center; word-wrap: break-word;'>0.392</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$5.71</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.928</td><td style='text-align: center; word-wrap: break-word;'>0.052</td><td style='text-align: center; word-wrap: break-word;'>0.020</td><td style='text-align: center; word-wrap: break-word;'>$0.49</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.436</td><td style='text-align: center; word-wrap: break-word;'>0.564</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.856</td><td style='text-align: center; word-wrap: break-word;'>0.124</td><td style='text-align: center; word-wrap: break-word;'>0.020</td><td style='text-align: center; word-wrap: break-word;'>$2.97</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.432</td><td style='text-align: center; word-wrap: break-word;'>0.564</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.16</td><td style='text-align: center; word-wrap: break-word;'></td></tr></table>

Notes: Accuracy metrics are in reference to human-labeled gold standard on held-out test sample of 250. Cost per labeling 250 instances, as of February 2025. Bolded model-prompt combinations matched or exceeded performance of GBM classifier.

<div style="text-align: center;"><div style="text-align: center;">Figure 1: Second-Stage Results Comparison</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//142d7695-3d3d-4ca9-b664-9c71c8c951e2/markdown_1/imgs/img_in_chart_box_220_316_987_1234.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-22T03%3A37%3A37Z%2F-1%2F%2F0c4c59044e1b01b0f8f014d8dbdef6026136568cd7391b25fccb888ec7ae1233" alt="Image" width="62%" /></div>


Notes: Coefficients from logistic regression with binary indicator for Kickstarter success (1=met funding goal, 0=did not meet funding goal) as dependent variable, controlling for year, logged funding goal, and category. Note that greater accuracy in the first stage does not necessarily translate to better recovery of the “true” effect if the direction of error is correlated with the second-stage dependent variable.

<div style="text-align: center;"><div style="text-align: center;">Figure 2: Template for Producing Family of Prompt Variations</div> </div>


Task: Generate 100 unique prompts for evaluating whether products/services benefit broader society beyond direct consumers.

Use these prompting strategies evenly:
- zero_shot: Direct evaluation with no additional context
- few_shot: Include 2-3 clear examples with classifications and reasons
- cot: Chain-of-thought with explicit analytical steps
- role_based: Evaluation from specific expert perspective
- self_consistency: Multiple passes with majority voting
- tot: Tree of thought with multiple analysis paths
- rot: Reasoning with competing arguments

Requirements for ALL prompts:
1. Must explicitly state the task: "...whether the main product or service described in the following Kickstarter campaign benefits the broader society (beyond its consumers)"
2. Must end with: "Answer only with a number (0 or 1). Here is the text:"
3. Must output strictly binary classification (0/1)
4. Must maintain consistent structure within each strategy
5. Must be unique and not a repeat of a previously generated prompt

Strategy-specific requirements:

ZERO_SHOT:
- Direct question
- No additional context or frameworks
- Example: "Please read the text of the following Kickstarter campaign and consider the following question. Does the main product or service offered benefit the broader society (beyond its consumers)? Answer only with a number (0 or 1). Here is the text:"

FEW_SHOT:
- Include exactly 3 examples
- Each example needs: product/service, classification (0/1), and reason
- Must follow format: '’’[EXAMPLE]’’ = [0/1] ([REASON])”
- Examples should be diverse and clearly justified
- Example: "Please read the text and consider whether the main product or service benefits the broader society (beyond its consumers). Examples: 1) ’”
  Solar-powered water purifier for communities’’ = 1 (benefits environment and public health), 2) ’’Premium leather accessories’’ = 0 (consumer-only benefit), 3) ’’Educational coding app for children’’ = 1 (benefits education and skill development). Using these examples as guidance, classify the following text with 1 for yes or 0 for no. Answer only with a number (0 or 1). Here is the text:"

COT:
- List 4-5 explicit analytical steps
- Steps should progress logically
- Include step numbering
- Example: "Please read the following text and determine if the main product or service benefits the broader society (beyond its consumers). First identify the core offering, then list consumer benefits, examine societal impacts, and assess their significance. After this analysis, provide your classification: 1 for yes

- Start with "As a [EXPERT ROLE]..."

- Specify relevant expertise area

- Link expertise to evaluation task

- Example: "As an expert researcher in corporate social responsibility, evaluate whether the following Kickstarter campaign’s main product or service benefits the broader society (beyond its consumers). Based on your expertise, classify the text with 1 for yes or 0 for no. Answer only with a number (0 or 1). Here is the text:"

##### SELF_CONSISTENCY:

- Specify exactly 3 evaluation passes

- Each pass should have distinct focus

- Explicitly mention majority-based final decision

- Example: "Please evaluate this text three times to determine if the main product or service benefits the broader society (beyond its consumers). First consider immediate impacts, then long-term effects, and finally the scale of benefits. Provide a 1 or 0 classification for each evaluation, then give a final classification based on the majority outcome. Answer only with a number (0 or 1). Here is the text:"

- Must start with task statement

- Specify exactly 3 analysis paths

- Each path should have clear focus

- Mention synthesis requirement

- Example: "Please evaluate whether this Kickstarter campaign's main product or service benefits the broader society (beyond its consumers) through three paths: 1) Impact scope (direct/indirect beneficiaries), 2) Sustainability framework (environmental/social/economic), 3) Public good criteria. Follow each path to its conclusion, then synthesize into a final 1 or 0 classification. Answer only with a number (0 or 1). Here is the text:

- Must start with task statement

- Include bidirectional analysis (pro/con)

- Require evidence/argument evaluation

- Specify confidence rating requirement

- Example: "Please evaluate whether this Kickstarter campaign's main product or service benefits the broader society (beyond its consumers) through branching analysis paths. For each potential classification (1 or 0), generate two supporting arguments. Reflect on the strength of each argument, considering uncertainty and evidence quality. Rate confidence in each path (high/medium/low), then provide final 0 or 1 classification based on the strongest reasoning chain. Answer only with a number (0 or 1). Here is the text:"

Output 100 total prompts with even distribution across strategies.

<div style="text-align: center;"><div style="text-align: center;">Figure 3: Distribution of Regression Coefficients Across Prompt Variations</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//142d7695-3d3d-4ca9-b664-9c71c8c951e2/markdown_4/imgs/img_in_chart_box_141_216_602_591.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-22T03%3A37%3A40Z%2F-1%2F%2F34bd43b41307488f858b7b3a506b508551e1249573c71ae1038da658179cc420" alt="Image" width="37%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(a) All Prompts, GPT-4o</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//142d7695-3d3d-4ca9-b664-9c71c8c951e2/markdown_4/imgs/img_in_chart_box_678_219_1081_586.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-22T03%3A37%3A40Z%2F-1%2F%2F825cc67a743ba0d85d26ce22159b72768129954cbd2c3abda2868e1dfcea9795" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(b) All Prompts, GPT-4o-mini</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//142d7695-3d3d-4ca9-b664-9c71c8c951e2/markdown_4/imgs/img_in_chart_box_143_660_599_1053.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-22T03%3A37%3A40Z%2F-1%2F%2Fbad468571911e2eac820f183e9742e343070e9ef6979afde1948bd772655a48f" alt="Image" width="37%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(c) Advanced Prompts Only, GPT-4o</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//142d7695-3d3d-4ca9-b664-9c71c8c951e2/markdown_4/imgs/img_in_chart_box_627_677_1081_1048.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-22T03%3A37%3A40Z%2F-1%2F%2Fb3c053c93a71884056b6f416cdd5390ffc3024720150fdc74e24c472bb62c2ee" alt="Image" width="37%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(d) All Prompts, Short Descriptions Only, GPT-4o</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//142d7695-3d3d-4ca9-b664-9c71c8c951e2/markdown_4/imgs/img_in_chart_box_384_1128_839_1497.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-22T03%3A37%3A40Z%2F-1%2F%2Fb3674acaab3e9e24979f8d99e351540f9f97caebd14d09aa7896f528aac8a652" alt="Image" width="37%" /></div>


<div style="text-align: center;"><div style="text-align: center;">(e) Dropping Prompts Below First-Stage Accuracy Threshold, GPT-4o</div> </div>


# Online Appendix for “The Use of LLMs to Annotate Data in Management Research: Warnings and Guidelines”

### A Documentation for Accompanying Code Implementation

#### LLM Annotation Framework for Social Science Research

All code and detailed documentation is available at: https://github.com/LLMAnnotationResearch/llm-annotation-framework.

##### Overview

The LLM Annotation Framework provides tools for:

1. Text Annotation: Using LLMs to classify text data with binary labels

2. Evaluation: Assessing model performance against human annotations

3. Downstream Analysis: Incorporating LLM classifications into regression models

4. Sensitivity Analysis: Testing how different prompt formulations affect results

#### Components

The framework consists of several components:

## 1. API Handlers

Functions for making API calls to various LLM providers:

• Python: python/src/api_handlers_python.py

• R: R/src/api_handlers_r.R

• Documentation: See docs/api_handlers.md for detailed usage

Supported models:

• OpenAI: GPT-4o, GPT-4o-mini

• Anthropic: Claude Opus, Claude Sonnet, Claude Haiku

## 2. Evaluation Functions

Tools for evaluating model performance and running sensitivity analyses:

• Python: python/src/evaluation_functions_python.py

• R: R/src/evaluation_functions_r.R

## 3. Prompt Creation Tools

Templates for generating effective prompt variations:

• Template: data/prompt_creation_template.txt

• Examples: data/prompt_creation_example.txt

## 4. Test Scripts

Scripts to test API and evaluation functions:

• API Tests:

– Python: python/tests/test_api_handlers.py

– R: R/tests/test_api_handlers.R

#### • Evaluation Tests:

– Python: python/tests/test_evaluation_functions.py

– R: R/tests/test_evaluation_functions.R

#### Basic Usage

#### Python Example

import pandas as pd
from src.evaluation_functions_python import evaluate_model

# Load your dataset
data = pd.read_csv("data/test_sample.csv")

# Set your API keys
api_keys = {
    "openai": "your-openai-api-key-here",
    "anthropic": "your-anthropic-api-key-here"
}

# Define your prompt template
prompt_template = ""

Please classify if this product benefits society beyond its consumers.
Answer only with O or 1. Here is the text:
""

# Run the model on your data

results = evaluate_model(
    data=data,
    model_name="gpt4o_mini",  # Options: gpt4o, gpt4o_mini, claude_opus,
    claude_sonnet, claude_haiku
    api_key=api_keys["openai"],  # Use appropriate key based on the model
    prompt_template=prompt_template,
    text_column="text",  # Column containing text to classify
    human_label_column="HUMAN",  # Optional ground truth column
    regression_formula="success ~ LLM_LABEL + lgoal + year",  # Optional regression
    regression_family="gaussian"  # "gaussian" for OLS, "binomial" for logistic
)

# Access the annotated data
annotated_data = results['results']
print(f"Annotated {len(annotated_data)} items")

# View model performance metrics
metrics = results['metrics']
print(f"Accuracy: {metrics['accuracy']:.2f}")

# Check regression results
regression = results['regression']
print(f"LLM label coefficient: {regression['coefficient']:.4f}")
print(f"p-value: {regression['p_value']:.4f}")

### R Example

library(dplyr)
source("R/src/evaluation_functions_r.R")

# Load your dataset
data <- read.csv("data/test_sample.csv")

# Set your API keys
api_keys <- list(
    openai = "your-openai-api-key-here",
    anthropic = "your-anthropic-api-key-here"
)

# Define your prompt template
prompt_template <- "
Please classify if this product benefits society beyond its consumers.
Answer only with 0 or 1. Here is the text:
"

# Run the model on your data
results <- evaluate_model(
    data = data,
    model_name = "claude_haiku",
    api_key = api_keys$anthropic,  # Use appropriate key based on the model
    prompt_template = prompt_template,
    text_column = "text",
    human_label_column = "HUMAN",

regression_formula = "success ~ LLM_LABEL + lgoal + year",
regression_family = "gaussian"
)

# Access the annotated data
annotated_data <- results$results
print(paste("Annotated", now(annotated_data), "items"))

# View model performance metrics
metrics <- results$metrics
print(paste("Accuracy:", round(metrics$accuracy, 2)))

# Check regression results
regression <- results$regression
print(paste("LLM label coefficient:(", round(regression$coefficient, 4)))
print(paste("p-value:(", round(regression$p_value, 4)))

#### Conducting Sensitivity Analysis

Sensitivity analysis tests how your results vary across different prompt formulations.

### Creating Prompt Variations

The framework includes templates for generating prompt variations:

1. Using the Prompt Creation Template: The file data/prompt_creation_template.txt provides a structured approach for generating diverse prompt variations.

2. Example Adapted Template: See data/prompt_creation_example.txt for an example of this template adapted to a particular use case.

3. Example Prompt Variations: See data/prompt_variations.csv for an example of 50 prompts generated by Claude for the use case above.

These templates help create prompt variations using different strategies like zero-shot, few-shot, chain-of-thought, and role-based approaches. We’ve had good success generating these prompt variations using Claude 3.5 Sonnet in a chat window.

#### Running Sensitivity Analysis

from src.evaluation_functions_python import run_sensitivity_analysis
import pandas as pd

# Load your dataset
data = pd.read_csv("data/test_sample.csv")

# Load prompt variations
prompts_df = pd.read_csv("data/prompt_variations.csv")

# Set your API keys

api_keys = {
    "openai": "your-openai-api-key-here",
    "anthropic": "your-anthropic-api-key-here"
}

# Run sensitivity analysis
sensitivity_results = run_sensitivity_analysis(
    prompts_df=prompts_df,
    data=data,
    api_key=api_keys["openai"],  # Use appropriate key based on the model
    model_name="gpt4o_mini",
    text_column="text",
    human_label_column="HUMAN",
    regression_formula="success ~ LLM_LABEL + lgoal + year",
    regression_family="gaussian",
    save_path="results/sensitivity_analysis/"
)

# View results summary
summary_df = sensitivity_results['results']
print(summary_df[['strategy」，'accuracy'，'reg_coef'，'p_value']])

# The function automatically saves:
# 1. A CSV with all results
# 2. A plot showing the distribution of regression coefficients

### Bootstrapping Option for Large Datasets

For large datasets, you can use bootstrapping to improve efficiency by using a different random sample for each prompt variation. This is useful for:

• Reducing computation time and API costs

• Testing how prompt variations perform on diverse subsets of data

Run sensitivity analysis with bootstrapping for large datasets
sensitivity_results = run_sensitivity_analysis(
    prompts_df=prompts_df,
    data=large_data, # A large dataset
    api_key=api_keys["openai"],
    model_name="gpt4o_mini",
    text_column="text",
    human_label_column="HUMAN",
    regression_formula="success ~ LLM_LABEL + lgoal + year",
    regression_family="gaussian",
    save_path="results/sensitivity_analysis/,
    bootstrap_size=500, # Use 500 random samples for each prompt variation
    random_seed=42 # For reproducibility
)

Example: Analyzing Crowdfunding Success

import pandas as pd
import matplotlib.pyplot as plt
from src.evaluation_functions_python import run_sensitivity_analysis

# Set your API keys
api_keys = {
    "openai": "your-openai-api-key-here",
    "anthropic": "your-anthropic-api-key-here"
}

# Step 1: Load crowdfunding data
data = pd.read_csv("data/test_sample.csv")
print(f"Loaded {len(data)} crowdfunding campaigns")

# Step 2: Load prompt variations to test different formulations
prompts = pd.read_csv("data/prompt_variations.csv")
print(f"Loaded {len(prompts)} prompt variations")

# Step 3: Run sensitivity analysis
results = run_sensitivity_analysis(
    prompts_df=prompts,
    data=data,
    api_key=api_keys["openai"],  # Use appropriate key based on the model
    model_name="gpt4o_mini",
    text_column="text",
    human_label_column="HUMAN",
    regression_formula="success ~ LLM_LABEL + lgoal + subcategory + year",
    regression_family="gaussian",
    save_path="results/crowdfunding_analysis/"
)

# Step 4: Analyze the results
summary = results['results']
print("\nSensitivity Analysis Results.")
print(summary[['strategy」，''accuracy'」, ''reg_coef'」, ''p_value']].head())

# Calculate the mean and standard deviation of the coefficient
mean_coef = summary['reg_coef'] .mean()
sd_coef = summary['reg_coef'] .std()
print(f"\nMean coefficient: {mean_coef:.4f} (SD: {sd_coef:.4f})")

#### Flexible Regression Analysis

The framework supports flexible regression analysis, allowing you to specify:

1. A custom regression formula (e.g., y ~ x1 + x2 + x3)

2. The specific coefficient of interest to extract from the results

3. The type of regression (Gaussian/OLS or Binomial/Logistic)

This enables various research designs where LLM annotations might be:

• Independent variables in your model

• Dependent variables being predicted

• Control variables in a larger model

#### Python Example:

When LLM annotation is the independent variable of interest
results = evaluate_model(
    data=data,
    model_name="gpt4o",
    api_key=api_keys["openai"],
    prompt_template=prompt_template,
    regression_formula="outcome ~ LLM_LABEL + control1 + control2",
    coefficient_of_interest="LLM_LABEL"  # Default
)

# When LLM annotation is the dependent variable
results = evaluate_model(
    data=data,
    model_name="gpt4o",
    api_key=api_keys["openai"],
    prompt_template=prompt_template,
    regression_formula="LLM_LABEL ~ predictor1 + predictor2",
    coefficient_of_interest="predictor1"  # We're interested in this predictor
)

# When interested in interaction effects
results = evaluate_model(
    data=data,
    model_name="gpt4o",
    api_key=api_keys["openai"],
    prompt_template=prompt_template,
    regression_formula="outcome ~ LLM_LABEL * treatment + control",
    coefficient_of_interest="LLM_LABEL:treatment"  # Interaction term
)

### R Example:

When LLM annotation is the independent variable of interest
results <- evaluate_model(
    data = data,
    model_name = "claude_opus",
    api_key = api_keys$anthropic,
    prompt_template = prompt_template,
    regression_formula = "outcome ~ LLM_LABEL + control1 + control2",
    coefficient_of_interest = "LLM_LABEL"  # Default
)

When LLM annotation is the dependent variable
results <- evaluate_model(
    data = data,
    model_name = "claude_opus",
    api_key = api_keys$anthropic,
    prompt_template = prompt_template,
    regression_formula = "LLM_LABEL ~ predictor1 + predictor2",
    coefficient_of_interest = "predictor1"  # We're interested in this predictor
)

The framework will automatically extract and report the coefficient, standard error, and p-value for your specified coefficient of interest.

All code and detailed documentation is available at: https://github.com/LLMAnnotationResearch/llm-annotation-framework.

### B Additional Details on Prompting Strategies

Basic Prompting Strategies. Zero-shot prompting is the simplest form of LLM interaction, where the model is given direct instructions without examples. This approach proves particularly effective for well-defined classification tasks and initial exploratory analysis, though its success depends heavily on the clarity and specificity of prompt construction. Early work by Reynolds and McDonell (2021) established the fundamental utility of zero-shot prompting with the first generation of LLMs, with subsequent work showcasing that zero-shot prompting with GPT-4 could outperform human coders at basic annotation tasks (Gilardi et al., 2023; Tornberg, 2023).

Few-shot prompting enhances performance by including carefully selected examples alongside instructions, allowing models to implicitly learn patterns from these examples. Zhao et al. (2021) demonstrated that strategic example selection (covering diverse cases and decision boundaries) can significantly improve performance, particularly for nuanced classification tasks. Recent work by Weber and Reichardt (2023) extends these principles to social science applications, providing protocols for systematic validation in research contexts. Few-shot prompts are particularly vulnerable to overfitting from examples, and so researchers may want to take care that the examples chosen are representative of the full spectrum of cases that the model should seek to classify. $ ^{14} $

Role-based prompting frames instructions as coming from or directed to a specific expert perspective (e.g., “As a sustainability researcher, evaluate...”). While this approach can enhance domain-specific reasoning, it requires careful validation to prevent introducing systematic biases into the analysis. In their comparative testing across modern LLMs, Battle and Gollapudi (2024) found that results could vary with different role-based preambles, often in unpredictable ways. $ ^{15} $

Advanced Reasoning Approaches. Chain of Thought (CoT) prompting is perhaps the most well-known and significant advancement in how researchers can extract detailed reasoning from LLMs. As first demonstrated by Wei et al. (2022), $ ^{16} $ CoT prompting explicitly decomposes complex tasks into step-by-step reasoning processes, leading to more transparent and verifiable outputs. This approach proves particularly valuable for research tasks requiring detailed classification decisions or nuanced analytical judgments. However, researchers must balance the increased transparency against heightened token usage (i.e., excessive wordiness) in model outputs.

Self-consistency methods build upon these foundations by implementing multiple independent attempts at the same analytical task. As developed by Wang et al. (2022), this approach

generates multiple iterative responses that can be evaluated for consistency, proving particularly valuable for high-stakes research decisions. However, the computational cost of multiple runs must be weighed against the benefits of increased confidence in results, particularly in large-scale applications.

Tree- and graph-based methods, such as Tree of Thoughts (ToT) and Reflection on Trees (RoT), represent the most structured approach to complex reasoning tasks. These approaches work by introducing systematic exploration of multiple solution paths (Yao et al., 2024; Hui et al., 2024), breaking down complex problems into intermediate steps and exploring multiple possible paths at each decision point. However, tree- and graph-based methods can quickly become computationally intensive if branching criteria are not carefully controlled. Successful implementation requires explicit stopping conditions – such that the model does not continue to branch onward in an uncontrolled manner – to maintain computational feasibility.

### C Other Technical Implementation Details

Model Augmentation Approaches. In certain cases, it might be desirable to enhance LLM capabilities through additional training or external knowledge integration. Fine-tuning fundamentally modifies the model itself through additional training, similar to teaching a general expert to become a domain specialist (Wei et al., 2021). As documented by Chattopadhyay et al. (2024), researchers can achieve significant improvements in model performance through this specialized training, particularly for classification tasks. Recent advances in unified fine-tuning frameworks (Ding et al., 2023) have made these techniques more accessible to researchers, though implementation still requires careful consideration of computational resources, training data quality, and potential overfitting risks. The decision to fine-tune must be weighed against the infrastructure requirements.

Retrieval-Augmented Generation (RAG), first introduced by Lewis et al. (2020) $ ^{17} $, takes a different approach by giving the model access to external reference materials rather than modifying the model itself – analogous to providing a researcher with a specialized reference library. As synthesized in a recent comprehensive survey (Gao et al., 2023), this approach proves particularly valuable for research requiring access to specific domain knowledge or current information beyond the model's training data, and is the foundational architecture of many commercial applications of LLMs. However, successful implementation requires careful attention to knowledge base construction and retrieval mechanisms.

The choice between these augmentation approaches often depends on specific research requirements and resource constraints. While fine-tuning provides deeper integration of domain knowledge by modifying the model's parameters, RAG offers greater flexibility and easier updating of knowledge sources without requiring model retraining.

Critical Parameters. There exist several other key technical decisions that can signifi-

cantly impact LLM performance in research applications. Temperature control, a fundamental parameter governing output randomness, requires careful calibration based on research objectives. For classification and annotation tasks, research supports using zero temperature to maximize consistency and reproducibility (Törnberg, 2024). While higher temperatures can be useful for exploring alternative interpretations or generating diverse outputs, recent work challenges the oversimplified notion of temperature as a “creativity parameter” (Peeperkorn et al., 2024). The relationship between temperature and output quality is complex and task-dependent, suggesting researchers should empirically validate any deviation from zero temperature rather than assuming higher values will automatically yield more insightful results.

Context window management is another critical consideration as researchers work with increasingly complex texts and datasets. Recent advances have dramatically expanded the effective context windows of LLMs (Jin et al., 2024), though recent work shows that models may still struggle to fully utilize information from very long contexts (An et al., 2024). In practice, this means researchers might consider strategies such as arranging the most relevant information early in the prompt, chunking longer texts into meaningful segments when possible, and verifying that the model actually uses information from different parts of the context in its responses. When working with long documents, researchers might consider systematic validation checks to ensure the model maintains accuracy throughout the full context window rather than just focusing on information near the beginning or end.

Output Engineering. The final stage of LLM implementation in research workflows encompasses both technical and methodological considerations for result interpretation and validation. Response parsing capabilities have evolved significantly across model generations: while earlier research showed that structured format restrictions could impact model performance (Tam et al., 2024) and demonstrated high variance in format compliance (Shorten et al., 2024), newer models have substantially improved JSON handling and often produce better results when using structured formats. In practice, researchers should consider: (1) testing whether structured formats improve or degrade performance for their specific model and task, (2) implementing robust error handling for cases where outputs deviate from expected structures, and (3) validating that format choices align with overall analysis quality goals. For newer models, structured outputs may actually enhance consistency and downstream processing efficiency.

Confidence assessment is another possible utilization strategy, particularly for high-stakes research applications. Recent work has shown that LLMs tend toward overconfidence when directly asked to assess their certainty (Xiong et al., 2023), but researchers can implement multiple validation methods to assess output reliability. Chen and Mueller (2023) demonstrate how combining both intrinsic and extrinsic confidence measures can more accurately identify unreliable responses.

<div style="text-align: center;"><div style="text-align: center;">Table C1: Additional Technical Considerations for Using LLMs</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Approach / Parameter</td><td style='text-align: center; word-wrap: break-word;'>Description</td><td style='text-align: center; word-wrap: break-word;'>Tradeoffs</td><td style='text-align: center; word-wrap: break-word;'>Implementation Guidelines</td><td style='text-align: center; word-wrap: break-word;'>Common Pitfalls</td></tr><tr><td colspan="3">Model Augmentation Approaches</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Fine-Tuning</td><td style='text-align: center; word-wrap: break-word;'>Additional training on domain-specific data</td><td style='text-align: center; word-wrap: break-word;'>Requires specialized infrastructure or credits on some platforms; time vs. performance</td><td style='text-align: center; word-wrap: break-word;'>High-quality training data; validation sets; careful hyperparameter selection</td><td style='text-align: center; word-wrap: break-word;'>Model may lose previously learned general skills when trained heavily on a narrow dataset; overfitting</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Retrieval-Augmented Generation (RAG)</td><td style='text-align: center; word-wrap: break-word;'>Augmenting LLM with external knowledge retrieval</td><td style='text-align: center; word-wrap: break-word;'>Accuracy vs. computational complexity; freshness vs. speed</td><td style='text-align: center; word-wrap: break-word;'>Maintain a well-structured, updated index; carefully design how retrieved info is merged</td><td style='text-align: center; word-wrap: break-word;'>Poor retrieval relevance; context window management; hallucination risk</td></tr><tr><td colspan="3">Input Parameters</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Temperature</td><td style='text-align: center; word-wrap: break-word;'>Controls randomness/creativity in model outputs</td><td style='text-align: center; word-wrap: break-word;'>Consistency vs. diversity of outputs; reproducibility vs. exploration</td><td style='text-align: center; word-wrap: break-word;'>Start at 0 for classification tasks; systematically test impact</td><td style='text-align: center; word-wrap: break-word;'>Inappropriate setting for task type; inconsistent validation</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Context Window Management</td><td style='text-align: center; word-wrap: break-word;'>Organizing input within token limits</td><td style='text-align: center; word-wrap: break-word;'>Completeness vs. token efficiency</td><td style='text-align: center; word-wrap: break-word;'>Prioritize relevant information; structured formatting</td><td style='text-align: center; word-wrap: break-word;'>Critical context omission; inefficient token use</td></tr><tr><td colspan="3">Output Engineering</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Response Parsing</td><td style='text-align: center; word-wrap: break-word;'>Extracting structured information from responses</td><td style='text-align: center; word-wrap: break-word;'>Flexibility vs. reliability; simplicity vs. robustness</td><td style='text-align: center; word-wrap: break-word;'>Request JSON or CSV formats explicitly; ensure robust error handling if format is not followed</td><td style='text-align: center; word-wrap: break-word;'>Brittle parsing rules; handling edge cases</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Confidence Assessment</td><td style='text-align: center; word-wrap: break-word;'>Evaluating response reliability</td><td style='text-align: center; word-wrap: break-word;'>Potentially adds more overhead or post-processing; can be worth it for high-stakes tasks</td><td style='text-align: center; word-wrap: break-word;'>Multiple validation methods; clear thresholds</td><td style='text-align: center; word-wrap: break-word;'>Many LLMs are not natively calibrated, so confidence scores may not reflect true accuracy; overreliance on single measure</td></tr></table>

### D Performance Comparison to Other Supervised ML Approaches

Below, we report training details and results comparing other commonly used supervised ML approaches (in addition to the previously selected GBM model).

#### Naive Bayes

• Method: naive_bayes

• Tuning parameters:

- Laplace: 0

– Use Kernel: FALSE

- Adjust: 1

• Cross-validation settings:

— Method: repeatedcv

– Number of folds: 10

– Number of repeats: 3

– Summary function: twoClassSummary (ROC optimization)

### Gradient Boosting Machine (GBM)

• Method: gbm

• Tuning parameters:

– Number of trees: 250

– Interaction depth: 9

- Shrinkage: 0.1

– Minimum observations in node: 5

#### • Cross-validation settings:

- Method: repeatedcv

– Number of folds: 10

- Number of repeats: 3

– Summary function: twoClassSummary (ROC optimization)

#### XGBoost

• Method: xgbTree

• Tuning parameters:    
– Number of rounds: 50    
– Max depth: 6    
– Eta: 0.3    
– Gamma: 0    
– Colsample by tree: 0.8    
– Min child weight: 1    
– Subsample: 0.8    
• Cross-validation settings

- Method: repeatedcv

– Number of folds: 10

– Number of repeats: 3

– Summary function: twoClassSummary (ROC optimization)

#### Random Forest

• Method: rf

### • Tuning parameters:

– Number of variables at each split (mtry): 59

- Number of trees: 100

### • Cross-validation settings:

— Method: repeatedcv

– Number of folds: 10

– Number of repeats: 3

– Summary function: twoClassSummary (ROC optimization)

#### Class Distribution

• Original Training Data:

- Class 'No': 2615 (94.68%)

- Class 'Yes': 147 (5.32%)

• Balanced Training Data:

- Class 'No': 2615 (78.06%)

- Class 'Yes': 735 (21.94%)

[Results of best performing iteration of each model reported on following page in Table D2]

<div style="text-align: center;"><div style="text-align: center;">Table D2: First Stage Results Comparison</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Model</td><td style='text-align: center; word-wrap: break-word;'>Overall Accuracy</td><td style='text-align: center; word-wrap: break-word;'>False Positives</td><td style='text-align: center; word-wrap: break-word;'>False Negatives</td><td style='text-align: center; word-wrap: break-word;'>Cost (USD)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GBM (Selected Model)</td><td style='text-align: center; word-wrap: break-word;'>0.920</td><td style='text-align: center; word-wrap: break-word;'>0.033</td><td style='text-align: center; word-wrap: break-word;'>0.044</td><td style='text-align: center; word-wrap: break-word;'>approx. $3000</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Random Forest</td><td style='text-align: center; word-wrap: break-word;'>0.896</td><td style='text-align: center; word-wrap: break-word;'>0.032</td><td style='text-align: center; word-wrap: break-word;'>0.072</td><td style='text-align: center; word-wrap: break-word;'>approx. $3000</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>XGBoost</td><td style='text-align: center; word-wrap: break-word;'>0.864</td><td style='text-align: center; word-wrap: break-word;'>0.072</td><td style='text-align: center; word-wrap: break-word;'>0.064</td><td style='text-align: center; word-wrap: break-word;'>approx. $3000</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>NaiveBayes</td><td style='text-align: center; word-wrap: break-word;'>0.128</td><td style='text-align: center; word-wrap: break-word;'>0.872</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>approx. $3000</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Zero-Shot</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.652</td><td style='text-align: center; word-wrap: break-word;'>0.348</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$5.25</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.876</td><td style='text-align: center; word-wrap: break-word;'>0.112</td><td style='text-align: center; word-wrap: break-word;'>0.012</td><td style='text-align: center; word-wrap: break-word;'>$0.45</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.416</td><td style='text-align: center; word-wrap: break-word;'>0.584</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.784</td><td style='text-align: center; word-wrap: break-word;'>0.204</td><td style='text-align: center; word-wrap: break-word;'>0.012</td><td style='text-align: center; word-wrap: break-word;'>$2.74</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.580</td><td style='text-align: center; word-wrap: break-word;'>0.416</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.15</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Few-Shot</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.752</td><td style='text-align: center; word-wrap: break-word;'>0.240</td><td style='text-align: center; word-wrap: break-word;'>0.004</td><td style='text-align: center; word-wrap: break-word;'>$5.81</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.896</td><td style='text-align: center; word-wrap: break-word;'>0.080</td><td style='text-align: center; word-wrap: break-word;'>0.024</td><td style='text-align: center; word-wrap: break-word;'>$0.50</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.796</td><td style='text-align: center; word-wrap: break-word;'>0.200</td><td style='text-align: center; word-wrap: break-word;'>0.004</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.764</td><td style='text-align: center; word-wrap: break-word;'>0.216</td><td style='text-align: center; word-wrap: break-word;'>0.020</td><td style='text-align: center; word-wrap: break-word;'>$3.02</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.664</td><td style='text-align: center; word-wrap: break-word;'>0.332</td><td style='text-align: center; word-wrap: break-word;'>0.004</td><td style='text-align: center; word-wrap: break-word;'>$0.16</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Role-Based</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.668</td><td style='text-align: center; word-wrap: break-word;'>0.332</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$5.35</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.888</td><td style='text-align: center; word-wrap: break-word;'>0.100</td><td style='text-align: center; word-wrap: break-word;'>0.012</td><td style='text-align: center; word-wrap: break-word;'>$0.46</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.556</td><td style='text-align: center; word-wrap: break-word;'>0.444</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.804</td><td style='text-align: center; word-wrap: break-word;'>0.180</td><td style='text-align: center; word-wrap: break-word;'>0.016</td><td style='text-align: center; word-wrap: break-word;'>$2.79</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.672</td><td style='text-align: center; word-wrap: break-word;'>0.328</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.15</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Chain-of-Thought (CoT)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.736</td><td style='text-align: center; word-wrap: break-word;'>0.260</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$5.61</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.900</td><td style='text-align: center; word-wrap: break-word;'>0.092</td><td style='text-align: center; word-wrap: break-word;'>0.008</td><td style='text-align: center; word-wrap: break-word;'>$0.48</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.712</td><td style='text-align: center; word-wrap: break-word;'>0.288</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.876</td><td style='text-align: center; word-wrap: break-word;'>0.096</td><td style='text-align: center; word-wrap: break-word;'>0.028</td><td style='text-align: center; word-wrap: break-word;'>$2.92</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.696</td><td style='text-align: center; word-wrap: break-word;'>0.304</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.16</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Self-Consistency</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.576</td><td style='text-align: center; word-wrap: break-word;'>0.424</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$5.53</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.904</td><td style='text-align: center; word-wrap: break-word;'>0.088</td><td style='text-align: center; word-wrap: break-word;'>0.008</td><td style='text-align: center; word-wrap: break-word;'>$0.47</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.548</td><td style='text-align: center; word-wrap: break-word;'>0.452</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.872</td><td style='text-align: center; word-wrap: break-word;'>0.100</td><td style='text-align: center; word-wrap: break-word;'>0.028</td><td style='text-align: center; word-wrap: break-word;'>$2.88</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.624</td><td style='text-align: center; word-wrap: break-word;'>0.376</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.15</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Tree-of-Thought (ToT)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.796</td><td style='text-align: center; word-wrap: break-word;'>0.204</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$5.55</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.940</td><td style='text-align: center; word-wrap: break-word;'>0.036</td><td style='text-align: center; word-wrap: break-word;'>0.024</td><td style='text-align: center; word-wrap: break-word;'>$0.48</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.668</td><td style='text-align: center; word-wrap: break-word;'>0.328</td><td style='text-align: center; word-wrap: break-word;'>0.004</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.880</td><td style='text-align: center; word-wrap: break-word;'>0.080</td><td style='text-align: center; word-wrap: break-word;'>0.036</td><td style='text-align: center; word-wrap: break-word;'>$2.89</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.548</td><td style='text-align: center; word-wrap: break-word;'>0.452</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.15</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Reflection on Search Trees (RoT)</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4</td><td style='text-align: center; word-wrap: break-word;'>0.604</td><td style='text-align: center; word-wrap: break-word;'>0.392</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$5.71</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o</td><td style='text-align: center; word-wrap: break-word;'>0.928</td><td style='text-align: center; word-wrap: break-word;'>0.052</td><td style='text-align: center; word-wrap: break-word;'>0.020</td><td style='text-align: center; word-wrap: break-word;'>$0.49</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT-4o-mini</td><td style='text-align: center; word-wrap: break-word;'>0.436</td><td style='text-align: center; word-wrap: break-word;'>0.564</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.03</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3-Opus</td><td style='text-align: center; word-wrap: break-word;'>0.856</td><td style='text-align: center; word-wrap: break-word;'>0.124</td><td style='text-align: center; word-wrap: break-word;'>0.020</td><td style='text-align: center; word-wrap: break-word;'>$2.97</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Claude-3.5-Haiku</td><td style='text-align: center; word-wrap: break-word;'>0.432</td><td style='text-align: center; word-wrap: break-word;'>0.564</td><td style='text-align: center; word-wrap: break-word;'>0.000</td><td style='text-align: center; word-wrap: break-word;'>$0.16</td></tr></table>

Notes: Accuracy metrics are in reference to human-labeled gold standard on held-out test sample of 250. Cost per labeling 250 instances.

### E Full Set of Prompt Variations



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Strategy</td><td style='text-align: center; word-wrap: break-word;'>Prompt</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Please read the text of the following Kickstarter campaign and consider the following question. Does the main product or service offered benefit the broader society (beyond its consumers)? Answer only with a number (0 or 1). Here is the text: Examine the text of the following Kickstarter campaign. Does the main product or service described benefit the broader society (beyond its consumers)? Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Review the text of the following Kickstarter campaign. Does the main product or service presented create value for society beyond its direct consumers? Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Based on the text of the following Kickstarter campaign, determine if the main product or service described contributes to broader societal wellbeing beyond consumer benefit. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign provides meaningful benefit to society at large, not just its users. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Assess whether the main product or service presented in the following Kickstarter campaign generates positive value for the broader society beyond individual consumers. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Consider whether the main product or service outlined in the following Kickstarter campaign advances collective societal good beyond personal utility. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign positively impacts society as a whole, rather than just its direct users. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Determine if the main product or service described in the following Kickstarter campaign serves a broader social purpose beyond individual consumer satisfaction. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Assess whether the main product or service described in the following Kickstarter campaign makes a meaningful contribution to collective societal wellbeing. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Consider whether the main product or service described in the following Kickstarter campaign delivers substantial benefits to society beyond individual user value. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate if the main product or service described in the following Kickstarter campaign has significant positive externalities that benefit non-users. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Determine whether the main product or service described in the following Kickstarter campaign provides measurable societal benefits beyond personal utility. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Assess if the main product or service described in the following Kickstarter campaign contributes to collective social progress beyond individual consumption. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>zero_shot</td><td style='text-align: center; word-wrap: break-word;'>Analyze whether the main product or service described in the following Kickstarter campaign generates meaningful value for society beyond the direct benefits to its users. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Please read the text of the following Kickstarter campaign and evaluate whether the main product or service benefits the broader society (beyond its consumers). Examples: 1) 'Solarpowered water purifier for communities' = 1 (benefits environment and public health), 2) 'Premium leather accessories' = 0 (consumer-only benefit), 3) 'Educational coding app for children' = 1 (benefits education and skill development). Using these examples as guidance, classify the following text with 1 for yes or 0 for no. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign benefits the broader society (beyond its consumers). Consider these examples: 1) 'Community composting system' = 1 (reduces waste, improves soil health), 2) 'Luxury watch collection' = 0 (individual consumer benefit only), 3) 'Open-source medical device' = 1 (advances healthcare accessibility). Based on these examples, classify the text. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Determine if the main product or service presented in the following Kickstarter campaign benefits broader society. Reference cases: 1) 'Public air quality monitoring network' = 1 (benefits community health monitoring), 2) 'Designer sunglasses' = 0 (personal fashion only), 3) 'Low-cost water filtration system' = 1 (improves public health access). Use these examples to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Assess whether the main product or service described in the following Kickstarter campaign benefits the broader society. Examples: 1) 'Renewable energy storage system' = 1 (benefits grid stability), 2) 'Collectible card game' = 0 (entertainment only), 3) 'Accessible transit app' = 1 (improves mobility for all). Apply these examples to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate if the main product or service in the following Kickstarter campaign benefits society beyond consumers. Consider: 1) 'Urban wildlife corridor project' = 1 (preserves biodiversity), 2) 'Custom phone cases' = 0 (decorative only), 3) 'Low-cost diagnostic tool' = 1 (expands healthcare access). Use these to guide classification. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Determine whether the main product or service described in the following Kickstarter campaign benefits broader society. Examples: 1) 'Community emergency response system' = 1 (improves public safety), 2) 'Personalized jewelry line' = 0 (aesthetic value only), 3) 'Open educational resources' = 1 (broadens learning access). Use these as reference. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Assess if the main product or service presented in the following Kickstarter campaign benefits society beyond its users. Reference cases: 1) 'Sustainable packaging solution' = 1 (reduces waste), 2) 'Premium headphones' = 0 (individual benefit), 3) 'Citizen science platform' = 1 (advances research). Apply these examples. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign benefits the broader society (beyond its consumers). Examples: 1) 'Public health data visualization platform' = 1 (improves healthcare decision-making), 2) 'Luxury camping gear' = 0 (personal leisure only), 3) 'Urban food waste reduction system' = 1 (reduces environmental impact). Use these examples to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Determine if the main product or service described in the following Kickstarter campaign benefits broader society. Consider these examples: 1) 'Affordable 3D-printed prosthetics' = 1 (increases medical accessibility), 2) 'Boutique coffee roaster' = 0 (personal consumption only), 3) 'Open-source pollution monitor' = 1 (enables community environmental action). Apply these cases. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Assess whether the main product or service described in the following Kickstarter campaign benefits society beyond consumers. Reference cases: 1) 'Multilingual learning platform' = 1 (bridges cultural divides), 2) 'Custom skateboard designs' = 0 (individual recreation only), 3) 'Community disaster response toolkit' = 1 (enhances public safety). Use these examples. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate if the main product or service described in the following Kickstarter campaign benefits broader society. Examples: 1) 'Wildlife tracking device network' = 1 (advances conservation efforts), 2) 'Artisanal soap collection' = 0 (personal care only), 3) 'Low-cost scientific equipment' = 1 (democratizes research). Apply this framework. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Determine whether the main product or service described in the following Kickstarter campaign benefits society beyond its users. Consider: 1) 'Mental health resource database' = 1 (improves healthcare access), 2) 'Collectible toy series' = 0 (entertainment only), 3) 'Renewable energy toolkit' = 1 (promotes sustainable practices). Use these cases. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Assess if the main product or service described in the following Kickstarter campaign benefits society beyond consumers. Reference: 1) 'Smart city sensor network' = 1 (improves urban planning), 2) 'Personalized fitness tracker' = 0 (individual health only), 3) 'Open-source farming tools' = 1 (advances food security). Apply these examples. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign benefits society beyond consumers. Reference: 1) 'Digital literacy platform' = 1 (reduces technological divide), 2) 'Premium pet accessories' = 0 (personal use only), 3) 'Community energy monitor' = 1 (enables collective action). Use these cases. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>few_shot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign benefits the broader society (beyond its consumers). Reference cases: 1) 'Accessible voting technology' = 1 (strengthens democratic participation), 2) 'Luxury smart home devices' = 0 (personal convenience only), 3) 'Open research data platform' = 1 (accelerates scientific progress). Apply these examples to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign payns benefits the broader society (beyond its consumers). Steps: 1) Identify target audience and primary function, 2) Map potential beneficiary groups, 3) Analyze social and environmental impact pathways, 4) Consider unintended consequences, 5) Determine net societal contribution. Use this analysis to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Determine if the main product or service described in the following Kickstarter campaign benefits broader society. Process: 1) Define innovation characteristics, 2) Evaluate direct application scope, 3) Identify spillover benefits, 4) Assess public good elements, 5) Measure collective advantage. Based on this analysis, classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Assess whether the main product or service described in the following Kickstarter campaign benefits society beyond consumers. Steps: 1) Characterize the offering, 2) Outline intended outcomes, 3) Map societal touchpoints, 4) Evaluate broader implications, 5) Calculate social return. Use this framework to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate if the main product or service described in the following Kickstarter campaign benefits broader society. Analysis: 1) Document key attributes, 2) Identify stakeholder groups, 3) Map impact channels, 4) Assess sustainability factors, 5) Determine collective value. Based on this process, classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Determine whether the main product or service described in the following Kickstarter cam-paign provides societal benefit. Steps: 1) Outline core mechanisms, 2) Map benefit flows, 3) Identify public good aspects, 4) Assess scalability, 5) Evaluate lasting impact. Use this analysis to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Assess if the main product or service described in the following Kickstarter campaign benefits society beyond users. Process: 1) Define solution scope, 2) Map impact pathways, 3) Identify externalities, 4) Evaluate social outcomes, 5) Determine net benefit. Based on this analysis, classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign creates broader social value. Steps: 1) Identify innovation type, 2) Map benefit distribution, 3) Assess social impact mechanisms, 4) Consider long-term effects, 5) Calculate collective gain. Use this framework to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Please evaluate whether the main product or service described in the following Kickstarter campaign benefits the broader society (beyond its consumers). First identify the core offering, then list consumer benefits, examine societal impacts, and assess their significance. After this analysis, provide your classification: 1 for yes (clear broader societal benefits) or 0 for no (primarily consumer benefits). Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Determine whether the main product or service presented in the following Kickstarter cam-paign benefits broader society. Follow these steps: 1) Define the core innovation, 2) Map direct user benefits, 3) Identify indirect beneficiaries, 4) Assess community-level impacts, 5) Evaluate long-term societal effects. Based on this analysis, classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign benefits society beyond its consumers. Process: 1) Outline key product capabilities, 2) Identify primary user groups, 3) Map secondary beneficiaries, 4) Assess societal spillover effects, 5) Evaluate net social impact. Use this analysis to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Assess whether the main product or service presented in the following Kickstarter campaign benefits broader society. Steps: 1) Extract core value proposition, 2) List direct beneficiaries, 3) Map indirect benefits, 4) Analyze societal implications, 5) Determine net public value. Based on this analysis, classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Determine if the main product or service described in the following Kickstarter campaign benefits society beyond consumers. Analysis steps: 1) Clarify primary purpose, 2) Identify immediate benefits, 3) Map broader impacts, 4) Assess societal effects, 5) Evaluate collective value. Use this framework to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service presented in the following Kickstarter campaign creates broader societal benefit. Process through: 1) Define core offering, 2) List user benefits, 3) Identify societal impacts, 4) Assess externalities, 5) Calculate net social value. Use this analysis to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>cot</td><td style='text-align: center; word-wrap: break-word;'>Analyze whether the main product or service described in the following Kickstarter campaign benefits broader society. Steps: 1) Understand key features, 2) Map beneficiary groups, 3) Examine societal effects, 4) Consider long-term impacts, 5) Assess overall social value. Based on this analysis, classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As an expert researcher in corporate social responsibility, evaluate whether the main product or service described in the following Kickstarter campaign benefits the broader society (beyond its consumers). Based on your expertise, classify the text with 1 for yes or 0 for no. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As a social impact assessor specializing in technology and innovation, determine whether the main product or service presented in the following Kickstarter campaign benefits society beyond its consumers. Drawing from your expertise in measuring social returns on investment, classify the offering. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As a public policy analyst focused on social welfare, evaluate whether the main product or service described in the following Kickstarter campaign contributes positively to societal well-being beyond individual consumer benefit. Use your policy evaluation expertise to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As an environmental sustainability consultant, assess whether the main product or service presented in the following Kickstarter campaign advances broader ecological and social goals beyond personal consumption. Apply your sustainability framework to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As a social innovation researcher, determine whether the main product or service described in the following Kickstarter campaign creates meaningful positive change for society beyond individual users. Use your understanding of social impact to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As a community development specialist, evaluate whether the main product or service presented in the following Kickstarter campaign strengthens social fabric beyond individual benefit. Use your expertise in community building to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As an urban planning expert, assess whether the main product or service described in the following Kickstarter campaign contributes to better functioning communities beyond personal utility. Apply your urban development knowledge to classify. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As a sustainable development expert, evaluate whether the main product or service described in the following Kickstarter campaign benefits the broader society (beyond its consumers). Using sustainability metrics and social impact assessment tools, classify its collective benefit. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As a public health researcher, determine if the main product or service described in the following Kickstarter campaign benefits broader society. Drawing on your expertise in population health outcomes, assess its societal impact. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As a social equity analyst, evaluate whether the main product or service described in the following Kickstarter campaign benefits society beyond consumers. Apply your understanding of inclusivity and accessibility to classify its broader impact. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As a technology ethics consultant, assess if the main product or service described in the following Kickstarter campaign benefits broader society. Use your expertise in responsible innovation to evaluate its collective benefit. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As an economic development specialist, determine whether the main product or service described in the following Kickstarter campaign creates societal value. Apply your knowledge of community prosperity metrics to classify its impact. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As a civic innovation researcher, evaluate if the main product or service described in the following Kickstarter campaign benefits broader society. Use your understanding of public benefit creation to assess its impact. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As a human rights advocate, assess whether the main product or service described in the following Kickstarter campaign advances societal wellbeing. Apply your expertise in social justice to classify its broader benefit. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>role_based</td><td style='text-align: center; word-wrap: break-word;'>As a digital inclusion expert, assess whether the main product or service described in the following Kickstarter campaign benefits broader society. Apply your expertise in technological equity and accessibility to evaluate its collective societal impact. Answer only with a number (0 or 1). Here is the text:</td></tr></table>













<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Strategy</td><td style='text-align: center; word-wrap: break-word;'>Prompt</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Please evaluate whether the main product or service described in the following Kickstarter campaign benefits the broader society (beyond its consumers). Make three evaluations: 1) Immediate impacts, 2) Long-term effects, 3) Scale of benefits. Provide a 1 or 0 classification for each evaluation, then give a final classification based on the majority outcome. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Determine whether the main product or service presented in the following Kickstarter campaign benefits broader society. Conduct three analyses: 1) Direct societal impact, 2) Five-year benefit projection, 3) Community-wide value. For each analysis, determine if broader societal benefits exist. Use the majority conclusion for final classification. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign benefits society beyond consumers. Make three independent assessments: 1) Local community impact, 2) Systemic social effects, 3) Global benefit potential. Rate each separately, then use the predominant rating for classification. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Assess whether the main product or service presented in the following Kickstarter campaign benefits broader society. Perform three reviews: 1) Immediate social value creation, 2) Broader impact assessment, 3) Long-term societal benefit. Classify each independently, then use the majority result. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Determine whether the main product or service described in the following Kickstarter campaign benefits society beyond its consumers. Complete three evaluations: 1) Direct community benefit, 2) Public good contribution, 3) Social progress potential. Make separate classifications, then use the consensus for final judgment. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service presented in the following Kickstarter campaign benefits broader society. Conduct three analyses: 1) Short-term social impact, 2) Societal ripple effects, 3) Lasting community benefit. Rate each 1 or 0, then use majority for final classification. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Analyze whether the main product or service described in the following Kickstarter campaign benefits society beyond consumers. Make three assessments: 1) Direct social contribution, 2) Indirect community effects, 3) Enduring societal impact. Classify each, then determine final rating based on majority. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign benefits the broader society (beyond its consumers). Make three assessments: 1) Social value creation, 2) Collective benefit mechanisms, 3) Impact sustainability. Rate each separately, then use the majority outcome for final classification. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Determine if the main product or service described in the following Kickstarter campaign benefits broader society. Perform three analyses: 1) Public good characteristics, 2) Social impact pathways, 3) Community advancement potential. Classify each independently, then use majority conclusion. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Assess whether the main product or service described in the following Kickstarter campaign benefits society beyond consumers. Complete three evaluations: 1) Innovation impact assessment, 2) Social value measurement, 3) Collective benefit analysis. Rate each, then use predominant finding. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Evaluate if the main product or service described in the following Kickstarter campaign benefits broader society. Conduct three reviews: 1) Social outcome mapping, 2) Public benefit validation, 3) Impact sustainability check. Classify each, then use majority rating. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Determine whether the main product or service described in the following Kickstarter campaign benefits society created societal value. Perform three assessments: 1) Community impact review, 2) Social progress contribution, 3) Collective advancement potential. Rate each, then use consensus. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Assess if the main product or service described in the following Kickstarter campaign benefits society at large. Complete three analyses: 1) Public good evaluation, 2) Social benefit measurement, 3) Impact durability assessment. Classify each, then use majority finding. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>self_consistency</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign provides broader societal benefit. Make three determinations: 1) Social value assessment, 2) Collective impact review, 3) Benefit sustainability check. Rate each, then use predominant result. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Please evaluate whether the main product or service described in the following Kickstarter campaign benefits the broader society (beyond its consumers) through three paths: 1) Impact scope (direct/indirect beneficiaries), 2) Sustainability framework (environmental/social/economic), 3) Public good criteria. Follow each path to its conclusion, then synthesize into a final 1 or 0 classification. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service presented in the following Kickstarter campaign benefits broader society through three frameworks: 1) Stakeholder impact mapping (direct/indirect effects), 2) Social value creation metrics (tangible/intangible benefits), 3) Public interest alignment. Follow each framework to conclusion and synthesize findings. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Determine whether the main product or service described in the following Kickstarter campaign benefits society beyond consumers through three approaches: 1) Social benefit diffusion (primary/secondary/tertiary effects), 2) Sustainable development goals alignment, 3) Common good contribution. Follow each path and combine insights for classification. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Assess whether the main product or service presented in the following Kickstarter campaign benefits broader society through three lenses: 1) Community impact spread (local/regional/global), 2) Social progress indicators (health/education/equality), 3) Collective benefit mechanisms. Pursue each analysis path to synthesis. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign benefits society beyond its consumers through three routes: 1) Benefit distribution mapping (individual/group/society), 2) Social value chain analysis, 3) Public welfare contribution. Follow each path to completion before final synthesis. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Determine whether the main product or service presented in the following Kickstarter campaign benefits broader society through three frameworks: 1) Social impact radius (immediate/extended/societal), 2) Public benefit metrics, 3) Collective advancement indicators. Follow each to conclusion before synthesis. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Analyze whether the main product or service described in the following Kickstarter campaign benefits society beyond consumers through three paths: 1) Societal value creation (direct/indirect/induced), 2) Community benefit indicators, 3) Public good alignment. Complete each analysis path before final synthesis. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign benefits the broader society (beyond its consumers) through three paths: 1) Innovation diffusion (accessibility/adoption/impact), 2) Social advancement indicators (equity/opportunity/wellbeing), 3) Collective progress metrics. Follow each path to conclusion, then synthesize findings. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Determine if the main product or service described in the following Kickstarter campaign benefits broader society through three frameworks: 1) Value distribution analysis (individual/community/society), 2) Impact sustainability assessment (short/medium/long-term), 3) Public benefit verification. Complete each framework before synthesis. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Assess whether the main product or service described in the following Kickstarter campaign benefits society beyond consumers through three lenses: 1) Social value creation (direct/enabled/catalyzed), 2) Benefit inclusivity spectrum, 3) Collective advancement indicators. Follow each path to completion. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate if the main product or service described in the following Kickstarter campaign benefits broader society via three routes: 1) Impact pathway mapping (immediate/intermediate/ultimate), 2) Social progress indicators, 3) Public good characteristics. Complete each analysis path before synthesis. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Determine whether the main product or service described in the following Kickstarter campaign creates societal value through three approaches: 1) Benefit flow analysis (user/community/society), 2) Social impact verification, 3) Collective advantage assessment. Follow each path to conclusion. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Assess if the main product or service described in the following Kickstarter campaign benefits society at large through three frameworks: 1) Value creation mapping (individual/collective/systemic), 2) Social benefit validation, 3) Progress contribution metrics. Complete each analysis before synthesis. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>tot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign advances broader society through three paths: 1) Impact scope analysis (direct/indirect/induced), 2) Social value verification, 3) Collective benefit indicators. Follow each framework to synthesis. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>rot</td><td style='text-align: center; word-wrap: break-word;'>Please evaluate whether the main product or service described in the following Kickstarter campaign benefits the broader society (beyond its consumers) through branching analysis paths. For each potential classification (1 or 0), generate two supporting arguments. Reflect on the strength of each argument, considering uncertainty and evidence quality. Rate confidence in each path (high/medium/low), then provide final 0 or 1 classification based on the strongest reasoning chain. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>rot</td><td style='text-align: center; word-wrap: break-word;'>Determine whether the main product or service presented in the following Kickstarter campaign benefits broader society through branching paths. Generate two arguments for societal benefit and two against, evaluate evidence strength for each argument, assess validity and reliability, then determine final classification based on strongest reasoning path. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>rot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign benefits society beyond consumers through competing perspectives. List two reasons for broad social value and two for limited consumer benefit, evaluate the robustness of each argument, rate confidence levels, then choose classification based on strongest logic chain. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>rot</td><td style='text-align: center; word-wrap: break-word;'>Assess whether the main product or service presented in the following Kickstarter campaign benefits broader society through branching analysis. Identify two paths supporting societal benefit and two suggesting consumer-only benefit, assess evidence quality for each path, rate argument strength, then select final classification using strongest reasoning.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>rot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign benefits the broader society (beyond its consumers) through competing analyses. Generate two arguments for societal impact and two for consumer-only benefit, assess evidence quality and uncertainty for each, rate confidence levels, then determine classification based on strongest reasoning chain. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>rot</td><td style='text-align: center; word-wrap: break-word;'>Determine if the main product or service described in the following Kickstarter campaign benefits broader society through dialectical analysis. Present two cases for social value creation and two for limited impact, evaluate supporting evidence, rate argument strength, then classify based on most robust reasoning path. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>rot</td><td style='text-align: center; word-wrap: break-word;'>Assess whether the main product or service described in the following Kickstarter campaign benefits society beyond consumers using parallel reasoning chains. Build two arguments for collective benefit and two for individual-only impact, evaluate evidence reliability, rate confidence, then classify using strongest logic path. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>rot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate if the main product or service described in the following Kickstarter campaign benefits broader society through structured debate. Develop two positions supporting societal benefit and two opposing, assess evidence strength, rate argument quality, then classify based on most compelling reasoning. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>rot</td><td style='text-align: center; word-wrap: break-word;'>Determine whether the main product or service described in the following Kickstarter campaign creates societal value through comparative analysis. Generate two arguments for broader impact and two for limited scope, evaluate evidence validity, rate certainty levels, then classify using strongest analysis path. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>rot</td><td style='text-align: center; word-wrap: break-word;'>Assess if the main product or service described in the following Kickstarter campaign benefits society at large through contrasting perspectives. Present two cases for collective benefit and two for consumer-only value, evaluate evidence quality, rate argument strength, then classify based on most sound reasoning. Answer only with a number (0 or 1). Here is the text:</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>rot</td><td style='text-align: center; word-wrap: break-word;'>Evaluate whether the main product or service described in the following Kickstarter campaign advances broader society through dual analysis. Build two arguments supporting societal benefit and two challenging it, assess evidence robustness, rate confidence levels, then classify using strongest reasoning chain. Answer only with a number (0 or 1). Here is the text:</td></tr></table>








