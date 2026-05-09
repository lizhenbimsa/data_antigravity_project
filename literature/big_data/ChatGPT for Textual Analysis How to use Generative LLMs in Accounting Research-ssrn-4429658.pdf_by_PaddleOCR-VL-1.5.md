# ChatGPT for Textual Analysis? How to use Generative LLMs in Accounting Research

Ties de Kok

tdekok@uw.edu

University of Washington

June 2024

## Abstract

Generative Large Language Models (GLLMs), such as ChatGPT and GPT-4 by OpenAI, are emerging as powerful tools for textual analysis tasks in accounting research. GLLMs can solve any textual analysis task solvable using non-generative methods, as well as tasks previously only solvable using human coding. While new and powerful, GLLMs also come with limitations and present new challenges that require care and due diligence. This paper highlights the applications of GLLMs for accounting research and compares them to existing methods. It also provides a framework on how to effectively use GLLMs by addressing key considerations such as model selection, prompt engineering, and ensuring construct validity. In a case study, I demonstrate the capabilities of GLLMs by detecting non-answers in earnings conference calls, a traditionally challenging task to automate. The new GPT method achieves an accuracy of 96% and reduces the non-answer error rate by 70% relative to the existing Gow et al. (2021) method. Finally, I discuss the importance of addressing bias, replicability, and data sharing concerns when using GLLMs. Taken together, this paper provides researchers, reviewers, and editors with the knowledge and tools to effectively use and evaluate GLLMs for academic research.

LLM assistance statement: GPT-4 and ChatGPT were used to help with copy-editing and coding assistance.

Acknowledgements: I thank Eric So (editor), Beth Blankespoor, Ed deHaan, Andy Leone, Dawn Matsumoto, Brian Miller, Tim Martens, Xue Li, an anonymous associate editor, and two anonymous reviewers for helpful comments. I thank Finnhub.io for providing the conference call dataset and Gow et al. (2021) for publicly sharing their code and data. A prior version of this paper was titled Generative LLMs and Textual Analysis in Accounting: (Chat)GPT as Research Assistant?.

Companion website:  $ \underline{\text{https://github.com/TiesdeKok/chatgpt paper}} $

# ChatGPT for Textual Analysis? How to use Generative LLMs in Accounting Research

June 2024

## Abstract

Generative Large Language Models (GLLMs), such as ChatGPT and GPT-4 by OpenAI, are emerging as powerful tools for textual analysis tasks in accounting research. GLLMs can solve any textual analysis task solvable using non-generative methods, as well as tasks previously only solvable using human coding. While new and powerful, GLLMs also come with limitations and present new challenges that require care and due diligence. This paper highlights the applications of GLLMs for accounting research and compares them to existing methods. It also provides a framework on how to effectively use GLLMs by addressing key considerations such as model selection, prompt engineering, and ensuring construct validity. In a case study, I demonstrate the capabilities of GLLMs by detecting non-answers in earnings conference calls, a traditionally challenging task to automate. The new GPT method achieves an accuracy of 96% and reduces the non-answer error rate by 70% relative to the existing Gow et al. (2021) method. Finally, I discuss the importance of addressing bias, replicability, and data sharing concerns when using GLLMs. Taken together, this paper provides researchers, reviewers, and editors with the knowledge and tools to effectively use and evaluate GLLMs for academic research.

LLM assistance statement: GPT-4 and ChatGPT were used to help with copy-editing and coding assistance.

Companion website:  $ \underline{\text{https://github.com/TiesdeKok/chatgpt paper}} $

## 1 Introduction

Rapid advancements in natural language processing and machine learning have given rise to Generative Large Language Models (GLLMs), such as the ChatGPT and GPT-4 models by OpenAI. This new family of models holds significant potential for accounting research studying textual data. GLLMs can solve textual analysis tasks with the power, versatility, and ease of use of human coding while enjoying the scalability, speed, and cost benefits of machine learning methods. For example, a well-instructed GLLM can extract emission targets in ESG reports, find CEOs trying to be funny in conference calls, compare risk factor consistency across firms, cluster topics in employee reviews, extract corporate culture references in job postings, and much more. While new and powerful, GLLMs also come with limitations and present new challenges that require care and due diligence. This paper provides researchers, reviewers, and editors with the knowledge and tools on how to effectively use and evaluate GLLMs in academic research.

GLLMs are a class of models that consume and generate text, like a powerful auto-complete. Generative Pre-trained Transformer (GPT) models are the most common type of GLLM. Because GLLMs work through natural language they are easier to use for a wide range of textual analysis tasks. The general-purpose capabilities of GLLMs also enable them to complete many tasks with no or little training data, which can save significant time and resources. For example, Hassan et al. (2019) identify political risk discussions in earnings calls by training an algorithm on a large training dataset of political texts. Achieving this is a challenging and time-consuming task without GLLMs. In contrast, a state-of-the-art GLLM like GPT-4 can solve this problem out-of-the-box (i.e., “zero-shot”) by simply showing it a call excerpt and asking whether it discusses political risk or not, as shown in Appendix B. Smaller models, such as GPT-3 or Llama2, can yield similar performance with appropriate instructions or training. Furthermore, the scale of GLLMs enables a basic degree of reasoning ability and world understanding that helps them solve problems that

would otherwise be infeasible to automate. For example, Gow et al. (2021) find that existing machine learning methods struggle with detecting non-answers in earnings conference calls due to the nuance and heterogeneity of that task. GLLM approaches can solve such complex tasks, as I demonstrate in a case study. Taken together, GLLMs can make it easier for researchers to analyze textual data and study new research questions.

While GLLMs are powerful they come with limitations and present new challenges. The natural language aspect of GLLMs can make it feel like working with a capable human. However, even the best GPT models make mistakes and are not guaranteed to give meaningful responses, especially when using them out-of-the-box. Care and due diligence by researchers can help mitigate this risk, but it requires carefully evaluating construct validity like with other machine learning (ML) methods. Furthermore, the large size of GLLMs can make them slow, expensive, and hard to control. Overcoming those limitations to unlock the potential of GLLMs requires working and thinking in new ways. However, the rapid rise in availability of GLLMs is accompanied by a lack of guidance on how to use these models in academic research. To illustrate, the recent overview of textual analysis methods in accounting by Bochkay et al. (2022) does not cover GLLMs. My paper provides an introduction, practical framework, case study, and discussion to help researchers effectively adopt and evaluate GLLMs for their research projects.

I start by introducing the GLLM approach to cover its basic workings and how it relates to existing LLMs such as BERT. I then compare the pros and cons of GLLMs relative to existing textual analysis techniques and human coding. The conclusion is that GLLMs can solve any textual analysis task solvable using non-generative methods. However, non-generative techniques can be substantially cheaper and faster for less complex problems that do not require the power of GLLMs. Where GLLMs start to become viable is for problems that would otherwise require complex ML machinery or human coding. GLLMs are substantially cheaper and faster relative to human coding.

and can complete equivalent work for many textual analysis tasks. However, human coders are usually easier to instruct and preferable for complex tasks with smaller samples.

Next, I provide a four-step framework to help researchers use GLLMs for their research projects. The framework complements the guidance by Anand et al. (2020) and Bochkay et al. (2022) and focuses on the implementation details and challenges specific to GLLMs. The framework first covers defining the research task and identifying the types of information necessary to perform the task. GLLMs that lack the necessary information or context are prone to "hallucinate" by guessing or making up information. To help with that, the framework next provides guidance on selecting the appropriate GLLM approach and prompt design, including a flowchart in Figure 1. The last step provides guidance on how to ensure construct validity by designing an evaluation approach to assess model performance and identify problems. Finally, the Online Appendix and companion website provide additional practical tips and code examples. $ ^{1} $

To demonstrate the capabilities of GLLMs, I do a case study of identifying non-answers in earnings conference calls. Detecting non-answers is traditionally challenging because it involves a large degree of nuance and context dependence. The results indicate that GLLMs can solve this task in multiple different ways, all improving on the accuracy of the Gow et al. (2021) approach. By combining GLLMs with existing methods, I achieve an accuracy of 96% and a non-answer F1 score of 87% at a reasonable cost. $ ^{2} $ This represents a 70% reduction in the non-answer error rate from the Gow et al. (2021) method. To further demonstrate the flexibility and capabilities of GLLMs, I also fine-tune a ChatGPT 3.5 model to extract additional non-answer dimensions, such

as its justification, question type, and sentiment, using a training dataset created with GPT-4.

Finally, I discuss several key considerations when using GLLMs in academic research. The training data of GLLMs raises concerns about biases, source material, and a lack of knowledge about recent events. Furthermore, working with GLLMs raises several new replicability challenges that researchers need to be careful with as models are not interchangeable, and third-party providers can remove or alter models at any time. Researchers should always store their raw prompts and completions under the assumption they might lose access to the source model. Researchers should also be careful with sending their research data to third-party services as such data sharing might be prohibited or undesirable. Lastly, GLLMs are increasingly popular as writing and programming assistants. While these tools can be useful productivity boosters, researchers should never blindly rely on the outputs of a GLLM when producing research and always scrutinize and check the outputs before using them.

This paper makes four contributions. First, it extends Bochkay et al. (2022) by showing how to use GLLMs as a powerful new textual analysis method. Second, it raises attention to and provides guidance on the challenges and limitations regarding GLLMs, such as ensuring construct validity, dealing with biases and knowledge limitations, and mitigating replicability and data sharing concerns. Third, it offers practical resources and guidance to help researchers get started with GLLMs for their own projects, including a framework, technical guidance, code examples, and more through the Online Appendix and companion website. Finally, the case study of non-answers in earnings conference calls adds to the disclosure literature on communication dynamics by studying the prevalence of non-answers and its various dimensions. I provide the non-answer dataset and its dimensions through the companion website for future research to use. Taken together, this paper equips researchers, reviewers, and editors with the knowledge and tools on how to effectively use and evaluate GLLMs in academic research.

## 2 Generative Large Language Models

### 2.1 What are GLLMs and how do they work?

Generative Large Language Models (GLLMs) are a class of machine learning models that consume and generate natural language. The most well-known example is ChatGPT by OpenAI; you ask ChatGPT a question and it provides you with an answer. Generative Pre-trained Transformer (GPT) models are the most common type of GLLM, but other generative architectures exist. The generative aspect is the key innovation of GLLMs that separates them from previous approaches. Specifically, GLLMs perform the task of predicting (i.e., generating) the next token based on the tokens that precede it, like auto-complete predictions when typing. A token represents a word, part of a word, or a character. For example, ChatGPT will tokenize the text “Baseball is fun!” into the tokens “Base”, “ball”, “is”, “fun”, “!”. Some words are a single token and some words are multiple tokens. $ ^{3} $ The original input we provide to the GLLM is the prompt and the resulting generation is the completion. Both the prompt and the completion are a collection of tokens, and the model predicts each token in the completion one at a time. For example, if we prompt ChatGPT with “What is the Tesla truck called?” and it provides us with the completion “Cybertruck.” the model will have made three predictions, one for each output token (in bold):

1. What- is- the- Tesla- truck- called-? → "Cyber"

2. What—is—the—Tesla—truck—called—?—Cyber→“truck”

3. What- is- the- Tesla- truck- called-?- Cyber-truck→“.”

GLLMs can try to “auto-complete” any type of text and by extension try to solve any task expressible into words. The general applicability of GLLMs as well as the abundance of possible training data (i.e., any text) make it possible to train foundational models at parameter scales not

previously feasible. $ ^{4} $ These large parameter scales and the diversity of its training data enable GLLMs to achieve a degree of language and world understanding that is significantly higher than previous models and textual analysis techniques.

Focusing on GPT models, many different model implementations exist, such as ChatGPT, GPT-3, GPT-4, Gemini (Bard), Claude, (Code)Llama2, CodeLlama, and Phi-2 to name a few. All these models work by predicting the next token based on the preceding tokens. Where the models differ is primarily in their parameter size, tuning, and availability. The model size will determine the out-of-the-box capabilities at the expense of cost and speed. The model tuning determines how the model will respond and the types of tasks the model is particularly good at. For example, the ChatGPT model is tuned to respond to your instructions like a human assistant, GPT-3 is tuned to continue your text, and CodeLlama is tuned to generate code. The availability determines whether the model is available to run locally or whether it is only accessible through a third-party service. Section 3.2 discusses how to choose the right model, and Online Appendix 1 provides a more detailed overview of model differences, popular models, and my recommendations to get started.

### 2.2 How do GLLMs relate to other LLMs like BERT?

The two most well-known types of LLMs are GPT and BERT (Bidirectional Encoder Representations from Transformers) models. Both are part of the transformer architecture family, which originates from the development of the attention mechanism (Bahdanau, Cho, and Bengio 2016; Vaswani et al. 2017). Practically, the transformer architecture is a breakthrough because it allows for better parallelization as well as better modeling of long-range dependencies in text, making it possible to train larger models that “understand” text better. BERT models, introduced by Devlin et al. (2019), use a transformer architecture to convert text into a better input for machine

learning models. In contrast, GPT models are generative and solve the task of predicting the next token like an auto-complete (Radford et al. 2018; 2019; T. Brown et al. 2020; OpenAI 2023).

Both GPT and BERT models are powerful textual analysis methods that utilize the benefits of the transformer architecture and its transfer learning abilities (e.g., Siano and Wysocki 2021). The fundamental difference is how one adapts them to solve a textual analysis problem. A BERT model is a powerful building block as part of a broader machine learning pipeline. For example, Huang et al. (2023) use a BERT model to represent financial documents which they then feed into a standard machine learning classifier to classify the sentiment. In contrast, GLLMs are standalone in that we feed them a natural language prompt, the model generates a completion, and we retrieve the result by parsing that completion. For example, Lopez-Lira and Tang (2023) classify news sentiment by showing ChatGPT news headlines and asking “Is this headline good or bad for the stock price of <company>? Answer YES if good news, NO if bad news, or UNKNOWN if uncertain”. They then parse the responses by ChatGPT to formulate their sentiment score.

I discuss the specific pros and cons of GLLMs versus existing methods in the next section. But at a higher level, textual analysis tasks are often solvable using both a GPT as well as a BERT approach. The benefit of GPT models is that they are easier to use as they generally require less (or no) training data and they are more flexible and easier to adapt to a wide range of tasks. The benefit of BERT approaches on the other hand is that once you manage to train them, they are many magnitudes faster and cheaper to use and scale. The primary issue with GPT models is that they are expensive to scale, and the primary issue with BERT approaches is that they require costly training datasets. As a result, more complex textual analysis problems at small to medium scales align well with GPT approaches whereas simpler and larger scale problems align well with BERT approaches. Finally, it is worth pointing out that the GPT method and BERT approaches are not mutually exclusive and combining them can sometimes yield the best of both worlds. For example,

a powerful GLLM like GPT-4 can be a cost-effective way to create a high-quality training dataset that can be used to train a BERT pipeline to make it cheaper and faster to scale the classifications to a large volume of documents. $ ^{5} $

### 2.3 Pros and cons relative to current methods

#### 2.3.1 Comparison to existing textual analysis methods

GLLMs have several benefits over existing textual analysis methods. The first is that large GPT models (such as ChatGPT and GPT-4) can often solve basic and objective textual analysis tasks without needing additional training. For example, Hassan et al. (2019) identify political risk conversation in conference calls by constructing a training dataset and training a classifier on it. Creating large quantities of training data manually is costly and time-consuming. Instead, a model like GPT-4 can solve this out-of-the-box by showing parts of the earnings call and asking whether the section discusses political risks, yes or no. The second benefit is that natural language prompts are more flexible in expressing tasks relative to more rigid statistical approaches. For example, Brown et al. (2018) try to identify how firms adjust their risk factor disclosures when a peer firm receives an SEC comment letter. They limit their measure to changes in the number of words as it is challenging to identify specific types of changes. The GLLM approach makes it possible to identify and classify specific types of year-over-year changes. Moreover, one could include details about the SEC comment letter to identify only changes that relate to the letter. This is done by formulating a prompt that shows the risk factors, a summary of the comment letter (which could also be GLLM generated), followed by a question in the spirit of “Did the risk factor change in response to the comment letter, yes or no?”.

The third benefit is that the basic reasoning and world understanding of large GPT models can make it possible to solve tasks that would be hard or impossible using existing natural language processing (NLP) techniques. For example, Call et al. (2023) use a sophisticated machine learning algorithm to identify cases of laughter in response to humor during conference calls. They limit their focus to only successful cases of humor, as unsuccessful attempts to be funny do not elicit laughter. Current state-of-the-art GPT models can also identify unsuccessful cases of humor, for example by showing an earnings call excerpt and asking the question “did the CEO try to be funny, yes or no?”. The final benefit is that GLLMs can handle longer inputs and documents relative to existing models. For example, BERT models can typically handle inputs of up to 512 tokens. In contrast, the most recent ChatGPT model can handle up to 16,385 tokens (about 26 pages of text) and the GPT-4-Turbo model can handle up to 128,000 tokens (a few hundred pages of text).

The GLLM approach also has important drawbacks and limitations. The primary disadvantage is that GLLMs are large and require more processing resources, making them more expensive and slower to use. Non-generative textual analysis techniques will be substantially cheaper and faster for simpler tasks that do not require the power of GLLMs. A good rule of thumb is to keep things as simple as possible and to only resort to more powerful techniques when necessary. Furthermore, GLLMs like ChatGPT and GPT-4 do make mistakes and are not guaranteed to give meaningful responses, especially when using them out of the box without any additional fine-tuning. The responses by GPT models can look good at first glance but not hold up to deeper inspection, so it is best to be skeptical of the performance until proven otherwise through evaluation. Achieving a high construct validity when using a GPT model requires researcher care and due diligence. I provide additional guidance on how to appropriately use and evaluate GLLMs in Section 3. Finally, large GPT models require expensive hardware and are most accessible through third-party providers. Sending research data to external parties is a risk and can be prohibited due to copyright

and data restrictions. Using GLLMs locally can be hard or impossible which can make them less suitable for tasks that require strict data controls.

#### 2.3.2 Comparison to human coding

The power and out-of-the-box capabilities of GLLMs make them a possible alternative to human coding. For example, Chuk et al. (2013) hand-collect management forecasts in earnings releases to compare them with a data aggregator. A powerful GLLM can plausibly complete the same task. Using a GLLM would save significant time and resources as they are cheaper, faster, and yield more consistent results relative to human coding. GLLMs can also exhibit super-human capabilities in terms of recalling and memorizing large quantities of information. However, even the most powerful GLLMs have important limitations and there is no guarantee they yield responses equivalent to human coding. The primary benefits of research assistants (RAs) are their flexibility, stronger reasoning ability, and incentives to try hard and produce good work. A human can be held accountable for their work while a machine cannot. A well incentivized RA will usually provide high-quality outputs with only minimal instructions while a GLLM might require prompt engineering or fine-tuning before it starts generating equivalent outputs. This makes human coding a better choice for complex tasks with smaller samples. Domain knowledge can be another limitation. GLLMs might need to learn domain knowledge through explicit examples, which can be hard to obtain or formulate. For example, Hail et al. (2018) use human coding to identify accounting scandals that are morally wrong versus legally wrong. It would be challenging to communicate to a GLLM what it means for something to be morally wrong.

### 2.4 Current research using GLLMs

While a relatively new technology, GLLMs are already being used in working papers for a wide range of textual analysis tasks. Bernard et al. (2024) fine-tune a Llama 3 model on a large sample of 10-K footnotes to measure the underlying business complexity. Kim et al. (2024) use

ChatGPT to generate automatic summaries of financial disclosures to measure the level of disclosure float. Rouen et al. (2023) use ChatGPT to extract seed words for every material topic in the SASB standard by sector and industry. Jha et al. (2024) use ChatGPT and conference calls to measure managers' anticipated changes in capital expenditures. Bai et al. (2023) use a variety of GLLMs such as ChatGPT, Google Bard, and an open-source model to develop a measure of information content by comparing answers in the Q&A section of conference calls with those automatically generated by the GLLMs. Finally, Hansen and Kazinnik (2023) apply GPT models to study technical language by the Federal Reserve and show that GPT-4 provides explanations that are on par with human reasoning. Several papers are also applying GLLMs to model the sentiment of financial disclosures. For example, Lopez-Lira and Tang (2023) use ChatGPT and GPT-4 to define sentiment scores for news articles covering company news. Their results suggest that the GLLM sentiment scores outperform traditional sentiment methods including BERT in terms of return predictability and trading strategies. Alternatively, Hu et al. (2023) find that FinBERT by Huang et al. (2023) outperforms a zero-shot GPT-3 model for sentiment analysis.

## 3 A framework for using GLLMs to solve research tasks

The generative natural language aspects of GLLMs pose distinct challenges that are not covered by existing NLP overview papers such as Anand et al. (2020) and Bochkay et al. (2022). Working with GLLMs requires a way of thinking that falls between interacting with a human (due to the natural language aspect) and employing a non-generative machine learning model (due to the machine aspect). Specifically, while it is possible to instruct a GLLM like instructing a human, that will often yield unsatisfactory results. Achieving high quality, consistent, and efficient results using the GLLM approach requires researcher care, effort, and due diligence. In this section, I provide a four-step framework that helps researchers implement GLLMs for their research tasks.

### 3.1 Define and understand your problem – Step 1

The first step is to define and understand the problem you are looking to automate. Doing so requires the evaluation of what information is necessary to complete the task. This may include specific domain knowledge, contextual information, or other relevant details that are necessary to generate the desired output. Any model, irrespective of how powerful it is, will not perform well if it lacks the necessary information to make a prediction or classification. When GLLMs lack sufficient context or background information they are prone to “hallucinate”, which is the generation of incorrect or made-up information, especially when using them out-of-the-box. Any information, such as specific institutional knowledge, that is likely not known to the GLLM will need to be provided, either through examples, instructions, or by fine-tuning.

To help with that, I recommend developing a deeper understanding of the task you are looking to automate by performing the task manually yourself on a set of examples and asking yourself why you made the decisions you made. What information did you use, and is it plausible that the GLLM you plan to use will "know" that information, or will you need to provide it? For example, assume you want to identify whether a footnote text relates to FASB ASU 2014-09. You might be able to complete that task easily because you know what FASB ASU 2014-09 relates to, but the GLLM might have no idea, or worse, a wrong understanding of it. Including an explicit description or definition of FASB ASU 2014-09 in the instruction will help with that.

### 3.2 Decide on the approach and model – Step 2

Each GLLM will have different strengths and limitations, and the right model depends on the task and the approach. There are three approaches to instruct a GLLM: zero-shot, few-shot, and fine-tuning. The zero-shot approach works by providing the GLLM only your instructions and the data for the task, without giving any examples. The few-shot approach works like the zero-shot approach, except that you provide a few examples, usually one to five, as part of every prompt to

complement your instructions. Finally, the fine-tuning approach works by training an existing GLLM on a larger set of examples to update all, or a part of, the model weights (“coefficients”).

The primary trade-off between the zero/few-shot and fine-tuning approaches is convenience versus control. Using GLLMs out of the box in a zero/few-shot way is relatively easy as it avoids having to create a training dataset and fine-tuning the model with it. This is especially true when using a model already set up through an external API. However, even the most powerful GLLMs like GPT-4 do make mistakes, and there is no guarantee they give meaningful responses. The primary way to control a zero-shot GLLM is through the prompt you provide, which can make it hard, and sometimes impossible, to get consistent and satisfactory results. Like a more traditional machine learning pipeline, fine-tuning a GLLM works by instructing the model through examples in a training dataset instead of through prompt instruction. A high-quality training dataset yields more control over the behavior of the model, but creating training data is costly, and fine-tuning a GLLM is significantly more complex. $ ^{6} $ I provide details and guidance on fine-tuning a GLLM in Online Appendix 5 and the companion website.

You also need to consider the number of tokens required to complete all your predictions. The time and costs of using a GLLM increase linearly with the tokens in your prompt and completion. Bigger models are generally slower and more expensive and thus lead to lower token budgets for a given amount of money and time. This has implications for your model choice, your decision between zero-shot, few-shot, and fine-tuning, as well as your prompt design. For example, a few-shot prompt can work better relative to a zero-shot prompt but including examples as part of your prompt will significantly increase the number of tokens required to process an observation.

There are many providers and models to choose from. Online Appendix I provides an overview of the popular GPT models currently available and the differences between models. The flowchart in Figure 1 can help you decide what GLLM approach to consider for a given research project. I generally recommend using the convenience of third-party party APIs (versus a local model) when sharing your data is possible. I also recommend first evaluating whether a zero-shot approach would work and only switching to model fine-tuning if a zero-shot approach does not yield satisfactory construct validity. Once you have selected the approach, try different model sizes using a smaller sample and pick the smallest model that yields satisfactory performance, which is not necessarily the model with the highest performance. For example, if a ChatGPT (or Llama 13b) model yields reasonable error rates for your task then it is unnecessary to spend a lot more time and money using a GPT-4 (or Llama 70b) model to only marginally increase performance.

### 3.3 Develop your prompt (i.e., “prompt engineering”) – Step 3

A prompt is the input you provide to the model and a completion is the output the model will generate. Both are expressed in natural language and take the form of a string of text. The input prompt is the primary way to control the output generated by the GLLM as the prompt contains your instructions, any contextual information, and the focal data. The focal data represents the information that will change for each observation in your data. For example, a simple prompt would be “Does the following tweet relate to politics, yes or no? Tweet: {the focal tweet}”. Engineering a good prompt is the key to getting reliable and high-quality outputs, especially when using a zero/few-shot approach. Prompt engineering is less influential when using fine-tuning because the model learns the task primarily through the training data examples in that approach.

When designing a prompt, the two primary objectives are to communicate to the GLLM what you expect the completion to be and to provide the GLLM with the necessary information to generate the desired completion. A model that misunderstands the instructions or that does not have

access to the necessary information will generate completions of low quality. Technically, any information representable as text can be part of a prompt or completion. This includes not only narrative data but also tabular data, JSON, XML, HTML, programming code, and others. However, zero-shot models generally perform best with regular text; alternative formats might require fine-tuning. It is hard to anticipate how GLLMs will respond to instructions, so it requires experimentation against an evaluation sample to determine the right prompt that achieves high construct validity. Appendix B, Appendix C, and Appendix D provide prompt examples as well as practical prompt engineering tips to help develop effective prompts.

When designing the completion portion of your instruction, the primary objective is to make the output machine-readable and easy to parse. Completions are natural text that can be hard, or impossible, to parse with your code if you do not design your completion with parsing in mind. For example, we might want to extract cashtag mentions out of Twitter messages and classify them as bullish or bearish. If we ask a GLLM to perform that task without being mindful of the output it might yield something like “The first cashtag is $AAPL and it is bullish and the second cashtag is bearish (MMM)”. This would be tedious and difficult to parse into a dataset. Instead, we could include an instruction to return a JSON list of the format “[cashtag, sentiment), ...]”. This would yield “[($AAPL, ‘bullish'), ($MMM, ‘bearish’)]” which we can easily parse into a dataset.

### 3.4 Evaluate the construct validity – Step 4

Evaluating the construct validity of any textual analysis approach is an important responsibility of the researcher (Bochkay et al. 2022). Evaluating generative completions comes with two primary challenges. The first challenge is that evaluating zero-shot and few-shot approaches still requires an evaluation dataset even when they do not require a training sample. The second challenge is that GLLMs can yield completions that are not compatible with standard performance metrics. For example, it is easy to develop a prompt that asks many questions at once. However, how do we

evaluate the quality of the completion if it consists of multiple individual elements? I recommend the following best practices to evaluate the construct validity of a GLLM:

(1) Always create an evaluation set of outcomes generated by human raters, such as yourself, co-authors, research assistants, domain experts, or third-party sources. This sample needs to be large enough, generally between a hundred to a couple thousand. The evaluation sample needs to be large enough to represent the diversity of the dataset and task. All approaches require an evaluation sample, including zero and few-shot approaches.

(2) When possible, engineer your instructions such that you can evaluate the GLLM approach like a standard supervised machine learning approach. For example, classifying sentiment as “positive = 0/1” will be easier to evaluate relative to a narrative description such as “sentiment = the text is mostly positive, but some parts are negative”. When returning multiple outcomes at once, I recommend evaluating and reporting each outcome independently.

(3) When it is not possible to evaluate your completion as a classification task, I recommend following the evaluation best practices for the closest non-GLLM approach that one would use for that specific task. For example, when using a GLLM for a clustering task one can follow the best practices for unsupervised machine learning (e.g., section 4 in Bochkay et al. (2022)).

(4) Be skeptical of the completion quality. GLLMs are trained to mimic human responses as closely as possible. However, GLLM responses are not human responses. Outputs generated by GLLMs tend to look great at first inspection but can be less accurate upon closer inspection. Due to human confirmation bias, it is easy to overestimate the quality of a GLLM completion.

Once a satisfactory construct validity is reached, the approach can be scaled up to generate completions for all the data observations. This step is commonly referred to as model inference.

## 4 Case study – using GLLMs to identify non-answers in earnings conference calls

One of the promises of GLLMs is to help automate tasks that would otherwise be challenging. To demonstrate and evaluate their capabilities, I deploy GLLMs for the challenging task of identifying non-answers in earnings calls. Identifying non-answers is a hard NLP problem because questions and answers in earnings calls are diverse in their content and style, often involve a large degree of nuance and context, and frequently suffer from lower data quality due to transcript errors.

Two prior papers have studied earnings call non-answers. Hollander et al. (2010), use manual hand-coding to study a small sample of earnings calls. This coding process took multiple months to complete. More recently, Gow et al. (2021) develop a rule-based technique using regular expressions to identify non-answers automatically for a large sample of earnings calls. That approach is functional, but their classifications leave significant room for improvement. They try but are unable to improve performance through traditional machine learning. They highlight that identifying non-answers using machine learning is “not as straightforward as it seems” and “we leave this challenge for future research”. As such, identifying non-answers in earnings calls is a good case study to evaluate the ability of GLLMs to solve challenging textual analysis problems.

### 4.1 Non-answer classification

I retrieve earnings call transcripts through the Finnhub.io API and limit the sample to CIKs that exist in the Gow et al. (2021) sample. To maximize Finnhub.io coverage and to enable an analysis of the COVID-19 period, I focus on a 10-year sample period from 2013 and to 2022. This yields a sample of 63,959 earnings calls after requiring that the call includes a presentation section and includes at least three question and answer (Q&A) pairs. Processing each transcript and extracting the valid Q&A pairs results in a sample of 1,152,505 Q&A pairs. $ ^{7} $

To develop my GLLM approach (i.e., the GPT method), I first examine several random samples of Q&A pairs to identify non-answers and help select and refine the best approach and prompt structure. After selecting my final approach and prompts, I draw and manually classify a final sample of 500 Q&A pairs to serve as the evaluation sample. $ ^{8} $ The manual classifications make two observations clear. First, defining the exact boundary between an answer and a non-answer is challenging and arguably somewhat subjective. Second, it is generally hard to evaluate whether a response is a non-answer without the context of the underlying question. As a result, identifying non-answers requires a tolerance for ambiguity, a degree of reasoning ability, and the ability to evaluate the answer in the context of the question. Traditional ML approaches struggle with these aspects, which explains their low performance for the task of identifying non-answers.

I replicate the baseline Gow et al. (2021) measure using their available code. Table 1 Column 2 shows the performance results for this baseline. $ ^{9} $ The baseline measure shows an accuracy of  $ \sim86\% $ and a precision of  $ \sim58\% $, which is in line with Gow et al. (2021). My replication of the baseline measure yields a higher Type II error of 57% resulting in a lower non-answer F1 score of 49%. These results indicate that the baseline measure often misses non-answers as well as incorrectly label answers as non-answers, which Gow et al. (2021) acknowledge in their paper. $ ^{10} $

I explore various approaches using ChatGPT and GPT-4 before settling on the prompts shown in Appendix D and Online Appendix 2. Starting with the zero-shot approaches, the ChatGPT

method (Table 1, column 3) substantially improves over the baseline with an accuracy of 91%, a non-answer F1 score of 72%, and a substantially lower Type II error of 26%. The GPT-4 method (column 4) outperforms the previous approaches with an accuracy of 93%, a non-answer F1 score of 79%, and a Type II error of only 8%. It is worth highlighting that ChatGPT and GPT-4 provide this level of performance only through prompt-engineering without receiving any examples or task-specific training. But the prompt engineering is important, even minor changes, like removing the distributional statement (i.e., “… these sentences are rare, in 65% …”), already significantly drop performance. Taken together, the primary downside of these approaches is that scaling zero-shot GPT-4 to the full sample would be expensive, and the ChatGPT results could be improved.

In columns 5 and 6 of Table 1, I explore an alternative approach of combining traditional methods with GPT models to outperform zero-shot GPT-4 at a more reasonable cost. At a high level, I develop a funnel approach where I use cheaper methods to filter down the sample and resolve only the remaining harder classifications using GLLMs. The full approach is available in Online Appendix 3. In summary, I first use a keyword list to identify responses that have any possibility of being a non-answer. 42% of the Q&A pairs do not match any keywords and thus do not require further processing. Next, I train a machine learning model (a fine-tuned GPT-3 Babbage model in this case) to further filter out sentences that are highly likely not reflecting a non-answer. This reduces the possible non-answer Q&A pairs to only  $ \sim1/3^{rd} $ of the original sample. The remaining sample contains the most difficult problem of separating out the true non-answers from those appearing like non-answers. To solve this task, I frame a zero-shot ChatGPT prompt (see Appendix D.2) as an evaluation task and highlight the sentences possibly reflecting a non-answer. Column 5 of Table 1 shows that this approach matches the performance of GPT-4 with an accuracy of 94% and a non-answer F1-score of 82%, while being only  $ 1/35^{th} $ the price of GPT-4.

For most research tasks this would suffice. But to fully demonstrate the potential of GLLMs, I add a final step by fine-tuning a ChatGPT (GPT-3.5) model to further improve performance while simultaneously classifying multiple other non-answer dimensions. Doing so marginally increases the costs but it brings the performance up to an accuracy of 96%, with a non-answer precision and recall of 87%. $ ^{11} $ This reflects a 70% reduction in non-answer error rates over the Gow et al. (2021) method. $ ^{12} $ Taken together, the results in Table 1 show that GLLMs can solve hard NLP problems when set up correctly. The approaches in columns 5 and 6 also highlight that combining GLLMs with existing methods can help achieve state-of-the-art performance at a reasonable cost. $ ^{13} $

Table 2 shows the results of applying the GPT method (i.e., Table 1 column 6) and the Gow et al. (2021) method on the complete sample of 1,152,505 earnings call Q&A pairs. At the Q&A pair (filing) level, the GPT method identifies 13.9% (14.2%) of Q&A pairs as containing a non-answer. The Gow et al. method identifies 12.3% (12.7%) of the pairs as containing a non-answer. These results are close in aggregate, but the Venn diagram in Figure 2 shows that there is considerable disagreement between the two methods. Only 50% of the non-answers by the GPT method are also identified by the Gow et al. method. Furthermore, only 57% of the Gow et al. non-answers are considered non-answers by the GPT method. Consistent with Table 1 and shown in Online Appendix 4, the predictions by the GPT method are considerably better with fewer errors.

### 4.2 Classification of non-answer dimensions

The flexibility of GLLMs makes it possible to construct prompts that yield multiple classifications at once with little additional costs. To demonstrate this, I fine-tune a ChatGPT model in the last step of the GPT method to also categorize non-answers across multiple additional dimensions: the justification for not providing an answer, the type of non-answer, the type of question preceding the non-answer, and whether the manager tries to give a positive sentiment spin to their non-answer. Appendix A lists the possible outcomes for each dimension, and Online Appendix 2 and 3 provide the full prompt as well as a full description of the fine-tuning approach. In summary, I use zero-shot GPT-4 to create an initial training dataset, I manually go through these responses to correct mistakes, and then I fine-tune the ChatGPT model on the resulting dataset. $ ^{14} $

Table 3 shows the out-of-sample performance of both GPT-4 and the fine-tuned ChatGPT model, split out by each of the dimensions. The GPT-4 approach (Columns 1 to 3) yields a high level of performance across all classification categories with F1 scores ranging from 85% to 98%, but at a steep cost. The fine-tuned ChatGPT approach (Columns 4 to 6) yields a better non-answer classification performance of 93% but slightly lower F1 scores for the four additional dimensions with F1 scores ranging from 81% to 94%. Importantly, the fine-tuning approach is many magnitudes cheaper than the GPT-4 approach while yielding comparable performance. Table 3 also highlights that fine-tuned models tend to underperform for classifications with diverse outcomes like “Other” due to insufficient examples. Conversely, zero-shot GLLMs can excel in these scenarios by leveraging their ability to generalize from seen to unseen outcomes.

Figure 3 portrays the 160,049 non-answers by each dimension for the full sample. Only  $ \sim $17% of the non-answers reflect a complete refusal to answer the question; instead, managers often

provide an alternative qualitative answer (~71%). Most commonly non-answers are a response to requests for a breakdown (~21%) or forward-looking information (~42%). In 55% of the non-answers the managers try to paint a positive picture. Table 4 shows the correlation between question types and the non-answer dimensions. Managers generally justify not answering a question about breakdowns or related parties by declining to answer for policy or proprietary reasons (21.225*** & 21.220***). On the contrary, they are more likely to state they do not know the answer to forward-looking questions or those about R&D and regulation (-17.545*** & -9.988***). Managers mostly give a positive spin to their non-answers when analysts ask about forward-looking statements (10.048***). Lastly, managers are most likely to directly refuse to answer questions about related parties, or R&D and regulations (9.815*** & 8.606***). Online Appendix 6 provides an additional analysis where I regress question features, such as sentiment and readability, on the likelihood of non-answers and the various dimensions.

Lastly, I perform a time-series analysis to study non-answers over time and evaluate the impact of the COVID-19 pandemic. The results in Figure 4a show a relatively stable trend with an increase in non-answers during COVID-19. The breakdown in Figure 4b reveals that this increase in non-answers during COVID-19 is driven by an increase in managers providing qualitative non-answers to forward-looking questions and justifying them by not knowing the answer.

## 5 Discussion

### 5.1 GLLM training data: biases, source material, and recent events

Researchers using GLLMs should be aware of the potential biases, source concerns, and limitations regarding recent events in the GLLM training data. GLLMs are trained on extensive textual corpora, and they can reproduce biases present in that data. For example, Kaplan et al. (2024) find that ChatGPT tends to reproduce gender-based language biases that are commonly present in human-written reference letters, although these differences do vary across prompts and

language categories. These biases could also surface, for example, when using ChatGPT to classify job postings for a research project. Researchers need to evaluate the outputs for potential biases and, when necessary, mitigate them through prompt engineering or fine-tuning procedures.

Source concerns arise because GLLMs are trained on a large diverse set of sources making it difficult to know exactly what information the model is relying on to make its generations. The lack of a clear source can make attribution challenging as well as make the model behavior harder to predict. Explicitly providing the important information to your model through prompt or fine-tuning can reduce those concerns. For example, generations by a GLLM might suggest that it understands the FASB taxonomy. However, the source material used to develop that understanding is unclear and might be incorrect or out-of-date. Passing it the explicit portion of the FASB taxonomy that you would like it to use as part of your prompt resolves that concern and gives greater control. Lastly, GLLMs are trained on historical data up to a certain point. Any events or changes outside of the training sample will not be reflected in the output of the model. Researchers must account for these limitations when interpreting the results and, if necessary, incorporate up-to-date information through their prompts or by fine-tuning the model using more recent data.

### 5.2 Replicability

Ensuring replicability is a challenging but important task, especially when working with complex data and procedures. The GLLM approach faces two specific replicability challenges. First, GLLMs are powered by large neural networks with billions of parameters that work in ways we do not fully understand. Outputs for a given prompt can vary significantly between different models, versions of the same model, and sometimes even from generation to generation. For example, Chen et al. (2023) document significant differences in the outputs from GPT-4 when comparing the variant from March 2023 with that of June 2023. Second, accessing GLLMs is most

convenient through third-party providers. However, these providers can change the models or make them unavailable at any time, which can make it difficult to ensure full replicability.

The first option to improve replicability is to not rely on third-party APIs and use only GLLMs that you can store and run locally. Online Appendix 5 and the companion website provide a discussion and code examples of how to locally use and fine-tune GLLMs. Running the model yourself yields more control and replicability. However, it does not resolve all replicability concerns. For example, access to the required specialized hardware can be expensive, not available, or require a prohibitive degree of technical know-how and expertise for others to replicate. Furthermore, running neural networks on different sets of hardware can still create minor differences in the outputs, making exact replication not a guarantee. For many projects the benefits of using a third-party API will outweigh the challenges that come with running a GLLM locally.

A more broadly applicable recommendation is to always assume that one can lose access to the exact source of the generations. The exact source could be a local GLLM, a GLLM behind an API, or even human coders. With that assumption in mind, it becomes critical to always store and backup the raw prompts and completions exactly as they enter in and exit out of the source. Having access to the raw prompts and completions enables replicating all later analyses and is second-best to a deterministic source. Making your generations as deterministic as possible also helps. Setting the “temperature” hyper-parameter to zero will make the GLLM always pick the highest probability tokens, which makes the generations as close to deterministic as possible. Finally, being transparent in your empirical choices, such as your data, your task, your prompt design, your approach, and your model(s) is always a good practice. Sharing your code, when possible, is also a straightforward way to reduce ambiguity and improve replicability.

### 5.3 Data privacy and copyright

Researchers using GLLMs need to be careful about sharing their research data with third-party providers of APIs or other computing resources. Sharing research data with external parties as part of your prompts or fine-tuning can result in data privacy, copyright, or other contractual violations. Besides the legal ramifications, API providers might use your prompts and generations to improve and re-train their models. This retraining can result in GLLMs unintentionally disclosing sensitive information in their future outputs to others. To mitigate this risk researchers should avoid using third-party APIs when data sharing is not allowed or desirable, especially when the API providers state in their terms of service that prompts can serve as additional training data.

### 5.4 Current GLLM developments

GLLMs are developing quickly in a few notable areas. Speed optimization and lower processing requirements are a primary area of progress. These optimizations will continue to make GLLMs more usable as well as more affordable and scalable. Furthermore, there are many ongoing developments to improve open-source models to make them more competitive with closed-source models, such as the Llama2 models and others (e.g., Touvron, Lavril, et al. 2023; Touvron, Martin, et al. 2023; Wang and Komatsuzaki 2021; Black et al. 2022). Better open-source models will make it easier to run GLLMs locally, which helps reduce concerns around replicability and data privacy, on top of further reducing costs.

The primary focus of this paper is on using GLLMs to process text. However, recently multimodal GLLMs have become increasingly capable and available. Multimodal models can accept other types of inputs in addition to text, such as audio and images. For example, GPT-4Vision by OpenAI and Gemini Pro Vision by Google can handle both text and images as input. Multimodal models enable an even greater range of tasks and problems that are automatable using GLLMs, such as analyzing data visualizations, challenging PDF files, corporate presentations,

video interviews, and audio transcripts. In addition to multimodal models, there are also multiple platforms that specialize in making it easier to incorporate specific types of alternative data into text prompts, such as the PDF.ai API to incorporate PDF data more easily as part of your prompt.

Another area of work is to connect GLLMs to information sources beyond their original training data such as retrieval-augmented-generations (RAG). These implementations demonstrate the potential to improve the knowledge and information lookup capabilities of GLLMs. For example, one could enable a GLLM to search the FASB taxonomy and perform a domain-specific textual analysis task. Connecting GLLMs to new sources has many applications but also raises questions about reliability and replicability, which future researchers will need to be mindful of.

Finally, most current GLLMs focus on the English language. These models commonly have basic capabilities in other languages but the state-of-the-art performance is generally limited to English texts. Multiple developments are in progress to provide GLLMs with other language focuses, such as the Ernie model for Chinese NLP tasks (Sun et al. 2021). These non-English GLLMs will make it easier to conduct textual analysis research on non-English documents.

### 5.5 Using GLLMs for writing & programming

GLLMs are also increasingly popular as writing and programming assistants, which raises specific concerns and challenges. In the context of writing, the primary concern with GLLMs is attributable and the factuality of the writing. For example, Bhattacharyya et al. (2023) find in the context of medical research that only 7% of the academic references generated by ChatGPT are authentic and accurate. GLLMs can help proofread or copy-edit academic writing, but do not blindly rely on the writing of a GLLM. Instead, carefully check the generations for inaccuracies, misattributions, or other mistakes.

In the context of programming, GLLMs can serve as useful productivity tools to write and debug code. However, the research and coding problems encountered in academia are often rare

and unusual, unlike commonly used coding problems found on the internet. Current GLLMs excel at solving coding problems that are prevalent in the training data but can struggle with more complex, rare, or domain-specific coding tasks. Minor mistakes in the code base for a research project can have major impacts on the validity of results and inferences. Code written or modified by a GLLM should always be validated for its accuracy. Researchers should not use GLLM coding assistants to write code they do not understand and cannot appropriately evaluate and scrutinize. In that regard, I echo the call by Bochkay et al. (2022) for researchers to still invest time in developing textual analysis and coding skills and for institutions to dedicate resources to provide training and guidance. The return on investment of these skills is even higher now that GLLMs exist as they enable you to leverage your skills more effectively.

## 6 Conclusion

Generative Large Language Models (GLLMs) offer significant potential for academic research analyzing textual data. GLLMs provide a powerful and versatile alternative to traditional machine learning methods and human coding. This paper provides an introduction and framework on how to effectively utilize GLLMs for a research project, while also highlighting their limitations and challenges in terms of controllability, construct validity, replicability, and data sharing. In a case study, I demonstrate the capabilities of GLLMs by detecting non-answers in earnings conference calls, a traditionally challenging task to automate. The new GPT method achieves an accuracy of 96%, which reflects a 70% reduction in non-answer error rates over the Gow et al. (2021) method. The Online Appendix and companion website provide additional practical resources such as a detailed comparison of models and code examples to get started with GLLMs. Taken together, this paper equips researchers, reviewers, and editors with the knowledge and tools to effectively use and evaluate GLLMs in academic research.

## References

Anand, Vic, Khrystyna Bochkay, Roman Chychyla, and Andrew Leone. 2020. “Using Python for Text Analysis in Accounting Research.” Foundations and Trends® in Accounting 14 (3–4): 128–359.

Bahdanau, Dzmitry, Kyunghyun Cho, and Yoshua Bengio. 2016. "Neural Machine Translation by Jointly Learning to Align and Translate." arXiv.

Bai, John (Jianqiu), Nicole M. Boyson, Yi Cao, Miao Liu, and Chi Wan. 2023. “Executives vs. Chatbots: Unmasking Insights through Human-AI Differences in Earnings Conference Q&A.” SSRN Scholarly Paper. Rochester, NY.

Bernard, Darren, Elizabeth Blankespoor, Ties de Kok, and Sara Toynbee. 2024. "A Modular Measure of Business Complexity." SSRN Scholarly Paper. Rochester, NY.

Bhattacharyya, Mehul, Valerie M Miller, Debjani Bhattacharyya, and Larry E Miller. 2023. "High Rates of Fabricated and Inaccurate References in ChatGPT-Generated Medical Content." Cureus 15 (5): e39238.

Black, Sid, Stella Biderman, Eric Hallahan, Quentin Anthony, Leo Gao, Laurence Golding, Horace He, et al. 2022. “GPT-NeoX-20B: An Open-Source Autoregressive Language Model.” arXiv.

Bochkay, Khrystyna, Stephen V. Brown, Andrew J. Leone, and Jennifer Wu Tucker. 2022. "Textual Analysis in Accounting: What's Next?" Contemporary Accounting Research.

Brown, Stephen V., Xiaoli (Shaolee) Tian, and Jennifer Wu Tucker. 2018. “The Spillover Effect of SEC Comment Letters on Qualitative Corporate Disclosure: Evidence from the Risk Factor Disclosure.” Contemporary Accounting Research 35 (2): 622–56.

Brown, Tom, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind Neelakantan, et al. 2020. "Language Models Are Few-Shot Learners." In Advances in Neural Information Processing Systems, 33:1877–1901. Curran Associates, Inc.

Call, Andrew C., Rachel W. Flam, Joshua A. Lee, and Nathan Y. Sharp. 2023. "Managers' Use of Humor on Public Earnings Conference Calls." Review of Accounting Studies.

Chen, Lingjiao, Matei Zaharia, and James Zou. 2023. "How Is ChatGPT's Behavior Changing over Time?" arXiv.

Chuk, Elizabeth, Dawn Matsumoto, and Gregory S. Miller. 2013. “Assessing Methods of Identifying Management Forecasts: CIG vs. Researcher Collected.” Journal of Accounting and Economics 55 (1): 23–42.

Devlin, Jacob, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. 2019. "BERT: Pre-Training of Deep Bidirectional Transformers for Language Understanding." arXiv.

Gow, Ian D., David F. Larcker, and Anastasia A. Zakolyukina. 2021. "Non-Answers During Conference Calls." Journal of Accounting Research 59 (4): 1349–84.

Hail, Luzi, Ahmed Tahoun, and Clare Wang. 2018. “Corporate Scandals and Regulation.” Journal of Accounting Research 56 (2): 617–71.

Hansen, Anne Lundgaard, and Sophia Kazinnik. 2023. "Can ChatGPT Decipher Fedspeak?" SSRN Scholarly Paper. Rochester, NY.

Hassan, Tarek A, Stephan Hollander, Laurence van Lent, and Ahmed Tahoun. 2019. “Firm-Level Political Risk: Measurement and Effects.” The Quarterly Journal of Economics 134 (4): 2135–2202.

Hollander, Stephan, Maarten Pronk, and Erik Roelofsen. 2010. "Does Silence Speak? An Empirical Analysis of Disclosure Choices During Conference Calls." Journal of Accounting Research 48 (3): 531–63.

Hu, Nan, Peng Liang, and Xu Yang. 2023. “Whetting All Your Appetites for Financial Tasks with One Meal from GPT? A Comparison of GPT, FinBERT, and Dictionaries in Evaluating Sentiment Analysis.” SSRN Scholarly Paper. Rochester, NY.

Huang, Allen H., Hui Wang, and Yi Yang. 2023. "FinBERT: A Large Language Model for Extracting Information from Financial Text." Contemporary Accounting Research 40 (2): 806–41.

Jha, Manish, Jialin Qian, Michael Weber, and Baozhong Yang. 2024. "ChatGPT and Corporate Policies." SSRN Scholarly Paper. Rochester, NY.

Kaplan, Deanna M, Roman Palitsky, Santiago J Arconada Alvarez, Nicole S Pozzo, Morgan N Greenleaf, Ciara A Atkinson, and Wilbur A Lam. 2024. "What's in a Name? Experimental Evidence of Gender Bias in Recommendation Letters Generated by ChatGPT." Journal of Medical Internet Research 26 (March).

Kim, Alex G., Maximilian Muhn, and Valeri V. Nikolaev. 2024. "Bloated Disclosures: Can ChatGPT Help Investors Process Information?" SSRN Scholarly Paper. Rochester, NY.

Lopez-Lira, Alejandro, and Yuehua Tang. 2023. "Can ChatGPT Forecast Stock Price Movements? Return Predictability and Large Language Models." SSRN Scholarly Paper. Rochester, NY.

OpenAI. 2023. “GPT-4 Technical Report.” arXiv.

Radford, Alec, Karthik Narasimhan, Tim Salimans, and Ilya Sutskever. 2018. "Improving Language Understanding by Generative Pre-Training."

Radford, Alec, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, and Ilya Sutskever. 2019. "Language Models Are Unsupervised Multitask Learners."

Rouen, Ethan, Kunal Sachdeva, and Aaron Yoon. 2023. "The Evolution of ESG Reports and the Role of Voluntary Standards." SSRN Scholarly Paper. Rochester, NY.

Siano, Federico, and Peter Wysocki. 2021. "Transfer Learning and Textual Analysis of Accounting Disclosures: Applying Big Data Methods to Small(Er) Datasets." Accounting Horizons 35 (3): 217–44.

Sun, Yu, Shuohuan Wang, Shikun Feng, Siyu Ding, Chao Pang, Junyuan Shang, Jiaxiang Liu, et al. 2021. "ERNIE 3.0: Large-Scale Knowledge Enhanced Pre-Training for Language Understanding and Generation." arXiv.

Touvron, Hugo, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothée Lacroix, Baptiste Rozière, et al. 2023. “LLaMA: Open and Efficient Foundation Language Models.” arXiv.

Louvron, Hugo, Louis Martin, Kevin Stone, Peter Albert, Amjad Almahairi, Yasmine Babaei, Nikolay Bashlykov, et al. 2023. "Llama 2: Open Foundation and Fine-Tuned Chat Models." arXiv.

Vaswani, Ashish, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N Gomez, Łukasz Kaiser, and Illia Polosukhin. 2017. "Attention Is All You Need." In Advances in Neural Information Processing Systems. Vol. 30. Curran Associates, Inc.

Wang, Ben, and Aran Komatsuzaki. 2021. “GPT-J-6B: A 6 Billion Parameter Autoregressive Language Model.” Software.

##### Appendix A: Definitions

<div style="text-align: center;"><div style="text-align: center;">A.1 – Common GLLM terminology</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Terminology</td><td style='text-align: center; word-wrap: break-word;'>Definition</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>API</td><td style='text-align: center; word-wrap: break-word;'>A communication protocol to interact with an internet service.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Completion</td><td style='text-align: center; word-wrap: break-word;'>The text output generated by the GLLM.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Few-shot</td><td style='text-align: center; word-wrap: break-word;'>Providing a prompt with a few examples as part of the instructions.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Fine-tuning</td><td style='text-align: center; word-wrap: break-word;'>Retraining (part of) the model weights for a specific task.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GLLM</td><td style='text-align: center; word-wrap: break-word;'>Generative Large Language Model.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT</td><td style='text-align: center; word-wrap: break-word;'>Generative Pre-trained Transformer.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Inference</td><td style='text-align: center; word-wrap: break-word;'>Using a GLLM to make a generation.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>LLM</td><td style='text-align: center; word-wrap: break-word;'>Large Language Model.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Model weights</td><td style='text-align: center; word-wrap: break-word;'>The parameter values (“coefficients”) of the neural network.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Prompt</td><td style='text-align: center; word-wrap: break-word;'>The text input provided to the GLLM.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Prompt engineering</td><td style='text-align: center; word-wrap: break-word;'>The task of developing a prompt for your task.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Token</td><td style='text-align: center; word-wrap: break-word;'>The unit of input for a GLLM. Can be a word, part of a word, or a character.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Zero-shot</td><td style='text-align: center; word-wrap: break-word;'>Providing a prompt without any examples, just the instruction.</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">A.2 - Non-answer dimensions</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Dimension</td><td style='text-align: center; word-wrap: break-word;'>Outcome</td><td style='text-align: center; word-wrap: break-word;'>Definition</td></tr><tr><td rowspan="2">Justification</td><td style='text-align: center; word-wrap: break-word;'>Cannot give</td><td style='text-align: center; word-wrap: break-word;'>The manager justifies they cannot answer because of reasons such as proprietary concerns, company policy, or legal reasons.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Do not know</td><td style='text-align: center; word-wrap: break-word;'>The manager justifies they cannot answer because it is too early, they do not know the answer or not have the information.</td></tr><tr><td rowspan="3">Non-answer type</td><td style='text-align: center; word-wrap: break-word;'>Complete refusal</td><td style='text-align: center; word-wrap: break-word;'>The manager completely refuses to provide any answer or information.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Qualitative</td><td style='text-align: center; word-wrap: break-word;'>The manager does not directly answer but instead provides a qualitative alternative answer.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Range or percentage</td><td style='text-align: center; word-wrap: break-word;'>The manager does not directly answer but instead provides a quantitative range or percentage.</td></tr><tr><td rowspan="5">Question type</td><td style='text-align: center; word-wrap: break-word;'>Breakdown</td><td style='text-align: center; word-wrap: break-word;'>The participant requests more detail on something. In most cases they request a number breakdown, such as by segment.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Forward-looking</td><td style='text-align: center; word-wrap: break-word;'>The participant requests guidance or a forward-looking statement.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Related party</td><td style='text-align: center; word-wrap: break-word;'>The participant asks about things like acquisitions, partnerships, major customers, or suppliers.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R&amp;D or regulation</td><td style='text-align: center; word-wrap: break-word;'>The participant asks about R&amp;D projects, clinical trials, or regulatory/certification matters.</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Other</td><td style='text-align: center; word-wrap: break-word;'>A question that falls outside the above four question types.</td></tr><tr><td rowspan="2">Sentiment spin</td><td style='text-align: center; word-wrap: break-word;'>Optimistic</td><td style='text-align: center; word-wrap: break-word;'>A non-answer accompanied by an optimistic statement (e.g., “I can’t give you the numbers, but things are looking good!”)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Neutral or pessimistic</td><td style='text-align: center; word-wrap: break-word;'>The manager does not provide an optimistic statement.</td></tr></table>

## Appendix B: Simple examples

This appendix provides simple examples of how one would use GLLMs and prompt-engineering to solve various types of textual analysis tasks. To save space, the prompts are shown as their zero-shot version, but they would be easily adapted to the few-shot or fine-tuning approaches. $ ^{15} $

Identifying statements about political risk:

Identify whether the earnings call transcripts below discuss political risks or not.

1. gaming industry is currently supporting a ballot initiative to amend the constitution to authorize an increase in the  $ - $BET $ - $ limits
2. Now on to the third quarter results. Cano Health continued to achieve steady organic growth in Q3. Total membership grew 4.6% from the second quarter to approximately 295,000 members, an increase of 40% year-over-year.
3. governments both President Obama's budget proposal and separate legislation  $ - $PENDING $ - $ in Congress would provide funding to continue the Medicaid stimulus for another

Return the result in the following JSON format:

[{"discusses_political_risk": Yes/No}]

JSON =

Which yields the following output when passed to GPT-4:

[{"discusses_political_risk" : "Yes"},
{"discusses_political_risk" : "No"}]
{"discusses_political_risk" : "Yes"}]

Extracting EBITDA-like numbers from the MD&A section:

Extract all EBITDA-related references and quantitative amounts from the paragraph below. Do not convert values and report them as reported.
> In the third quarter of 2021, our EBITDA increased to $1.2 billion, primarily driven by higher sales volumes and improved operational efficiency. Our Debt-to-EBIDAR increased by 20%. This growth was partially offset by increased raw material costs and unfavorable foreign exchange impacts.

Return the result in the following JSON format:
[ { "name" : ..., "value" : ... } ]
JSON =

Which yields the following output when passed to GPT-4:

[{"name":"EBITDA","value":"$1.2 billion"}]
{"name":"Debt-to-EBIDAR increase","value":"20%"}]

Topic classification for press release headlines:

Cluster the following company press releases into common categories:
1. Company A announces a new partnership with Company B to develop innovative solutions for the healthcare industry.
2. Company B reports its financial results for the second quarter of 2021, highlighting a 15% increase in revenue compared to the same period last year.
3. Company C unveils its latest initiative to reduce their carbon emissions, a $2 Billion investment in an all-electric fleet of company vehicles.
Return the result in the following JSON format:
[{"index": ..., "category": ...}]
JSON =

Which yields the following output when passed to GPT-4:

[{"index": 1, "category": "Partnerships"}]
{"index": 2, "category": "Financial Results"}
{"index": 3, "category": "Sustainability Initiatives"}]

Extract sentences from broken text:

Extract valid sentence from the following text that got split up:
In 2018, we ente
red the third
year of an ambitious 10-year goal
cycle. Our 2025 goals refl
ect
a heightened commitment

Return the result in the following JSON format:

[ { "i" : ..., "sentence" : ... } ]

JSON =

Which yields the following output when passed to GPT-4:

[{"i": 0, "sentence": "In 2018, we entered the third year of an ambitious 10-year goal cycle."}, {"i": 1, "sentence": "Our 2025 goals reflect a heightened commitment."}]

## Appendix C: Prompt engineering tips

## GLLMs generate text left to right, so their own generations become part of the prompt.

A helpful technique to improve completion quality is “chain of thought” prompting, which involves asking the model to first explain itself before making the classification. Due to the left-to-right nature of GLLMs, the explanation will become part of the context which can help create better and more consistent classifications relative to only asking the model to do the final classification.

## Optimize the number of tokens used by your prompt and completion.

Optimizing the number of tokens can save substantial time and money. Reducing the number of tokens by 10% will generally yield a 10% speed up and 10% cost saving. Classifying multiple observations through a single prompt can also help save on the number of overall tokens.

#### Be specific and to the point, less is often more.

GLLMs sometimes ignore part of the instructions, which can make them harder to control. Sticking with instructions that are short and explicit can help with this. It can also help to order your instructions in order of importance and include a note in your prompt to explain the order.

#### Chaining prompts together.

For more complex tasks it might not be possible to do everything through a single prompt. Chaining prompts together can help in this scenario. For example, feeding the first model completions back into the model with another prompt asking it to check or improve the previous completions for specific types of errors can help improve the final classification quality.

## Small differences in the prompt can make big differences in the completion.

Small changes in the prompt can make a big difference when instructing a GLLM. For example, including uncertain words such as “might”, “possibly”, or “could” can have a big impact. The influence of a single word or sentence is hard to predict, but trial and error and experimentation are effective ways to tweak the prompt to improve the completion quality and improve consistency.

### It can help to provide distributional statements as part of your prompt.

A challenge with zero/few-shot approaches is achieving the desired outcome distribution. Every generation is independent and the model does not keep track of the distribution of the outcomes. It can help to mention in your prompt that an outcome is rare or that it is encouraged to favor one outcome over another. I demonstrate this technique in my prompt in OA 2.1, for example.

#### It can help to track the prediction confidence of the model.

GLLMs can vary in their confidence from prediction to prediction. Instructing the model to also return its confidence level can provide insight into what type of documents the model is struggling with. While a helpful indicator, model-provided confidence scores are token generations like any other, and they can be wrong. A model stating it has high confidence does not guarantee a correct prediction and it remains important to evaluate construct validity using the guidance in Section 3.4.

### Appendix C: Prompt engineering tips (cont.)

#### Consider switching models if you cannot get your prompt to work.

As I highlight in Online Appendix 1, models can differ in nuanced ways. As a result, it is worth trying different models to see which ones yield the best out-of-the-box understanding of your task. You might find that it is hard to communicate your task to one model but significantly easier to communicate it to another, even if the models are of a similar size and tuning.

### Appendix D: Examples of earnings call non-answer prompts

This appendix provides two examples of the types of prompts I use for the non-answer results. The full prompts for all the specifications in Table 1 and Table 3 are shown in Online Appendix 2.

E.1 - ChatGPT zero-shot prompt (Table 1 column 3):

In the provided text, the analyst posed the question:
> {question}
The manager responded with:
> {answer}
**Task 1 - sentences:**
From the manager's response, extract only those sentences where the manager explicitly indicates either:
- They currently lack specific details or information to provide.
- They are deliberately choosing not to share specific information at the moment.
Please exclude sentences that discuss general uncertainties, company plans, or any actions the company might take in the future.
Also exclude disclaimers that are immediately followed by an answer.
Important: these sentences are rare, in 65% of the cases this will be an empty list. It is ok to return an empty list.
Provide your response using the following JSON format: JSON = {
    "sentences": []
}
JSON =

E.2 - ChatGPT zero-shot prompt after keyword/GPT-3 filter (Table 1 column 5):

Analyst question: {question}

yst question:
stion}
Manager response:
{answer}
A research assistant has marked the above response as including a statement that reflects unwillingness or inability to answer (part) of the analysts' question, because of the following comment(s):
> {comments}
Based on the question and full response above, provide a detailed assessment whether the manager's response includes a statement, explanation, or justification indicating an inability or unwillingness to answer the question. If you classify the response as reflecting inability or unwillingness to answer, justify your classification with specific phrases or sentences from the manager's response. If there's no such indication, explain why not.
Your response should be in the following JSON format:
JSON = {{
    "assessment": a detailed assessment unique to this evaluation following the instructions above,
    "your_classification": 1 or 0
}}
JSON =

<div style="text-align: center;"><div style="text-align: center;">Figure 1: GLLM approach flowchart</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//7a7d4044-eca1-495e-9d2e-5ff8b29d0ff9/markdown_2/imgs/img_in_image_box_145_189_1058_978.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-22T03%3A07%3A19Z%2F-1%2F%2F5b442467a79c73f0dc449fd0323832878d1af99c160dcd6ca14b922a0ddf4827" alt="Image" width="74%" /></div>


* Visual inspection of a few generations is not sufficient to know whether a zero-shot approach works or not. Section 3.4 discusses how to appropriately evaluate construct validity. Also, zero-shot approaches are generally more expensive as they require more tokens, so they might not work due to cost constraints.

† The scale economies of third-party APIs can make them relatively economical compared to running an equivalent model yourself. However, academic institutions commonly have existing computing infrastructure that one could utilize with a local model at low to no costs. Furthermore, local models make it possible to explore smaller GPT models, which can be significantly cheaper to use and fine-tune.

§ The costs of using a third-party API scale linearly with the number of tokens you input and output. I recommend observing or calculating the number of tokens for a small sample of prompts+completions and extrapolating those costs to the size of your entire sample to estimate how much it would cost in total.

There are many models to choose from. I recommend trying different models and model sizes using a small test sample and picking the smallest model that yields satisfactory performance, which is not necessarily the model with the highest performance due to time and cost considerations. See Section 3.2 and Online Appendix 1 for more guidance.

 $ ^{\ddagger} $ Fine-tuning a local GLLM is the most technically advanced option and I recommend only pursuing it if fine-tuning or training an existing ML pipeline such as using BERT is not working or feasible for your task.

<div style="text-align: center;"><div style="text-align: center;">Figure 2: Non-answers - Venn diagram</div> </div>


The below Venn diagram shows the overlap in non-answer classifications between the GPT and Gow et al. (2021) method. The classification report in Table 1 highlights that the GPT method significantly outperforms the Gow et al. (2021) method. To further illustrate the improvement, I show fifteen random examples of non-answers from each of the three areas of the Venn diagram in Online Appendix 4. As the random samples show, both approaches make mistakes. However, the rate of mistakes is much lower for the GPT method. The right outer (blue) slice primarily consists of non-answers missed by the Gow et al. (2021) method and the left outer (dark orange) slice primarily consists of answers falsely classified as non-answers by the Gow et al. method.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//7a7d4044-eca1-495e-9d2e-5ff8b29d0ff9/markdown_3/imgs/img_in_chart_box_361_474_921_920.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-22T03%3A07%3A20Z%2F-1%2F%2F2584ba613a96c17f16a8cd815048bdb4aeac1b24f68076bbefb186fce7b4c3e1" alt="Image" width="45%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 3: Non-answer breakdown by dimension</div> </div>


The chart below shows the non-answers split out by each of the non-answer dimensions. Within each dimension group, the bars add up to 100% to account for all the non-answers.

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//7a7d4044-eca1-495e-9d2e-5ff8b29d0ff9/markdown_4/imgs/img_in_chart_box_199_278_1038_697.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-22T03%3A07%3A21Z%2F-1%2F%2F9cf7dd9d54519b339d8891e60911019236d45975bce5691b6a189f1c44e5c026" alt="Image" width="68%" /></div>


### Figure 4: Non-answers – time-trends and COVID-19 impact

The two time-series plots below show the trend of non-answers over time. Figure 4a shows the percentage of non-answer Q&A pairs for each quarter, including both the Gow et al. (2021) and GPT methods. Each quarterly percentage is normalized by the 4-quarter moving average. Figure 4b shows the same results split out by each of the non-answer dimensions. To make the panels comparable, I center the quarterly percentage by the average of the corresponding dimension in the period prior to COVID-19, which are the years 2014-2020.

<div style="text-align: center;"><div style="text-align: center;">Figure 4a: Non-answer % over time (4-quarter moving average)</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//4463e82a-7967-4b6a-952b-10482bb7e318/markdown_0/imgs/img_in_chart_box_137_450_885_825.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-22T03%3A07%3A20Z%2F-1%2F%2F6542a8c12771795276961a260445c485e77b2b0ef28431aaf5f59e16140b9c9c" alt="Image" width="61%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Figure 4b: Change in 4-quarter moving average relative to the pre COVID-19 period</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-15//4463e82a-7967-4b6a-952b-10482bb7e318/markdown_0/imgs/img_in_chart_box_114_964_1123_1326.jpg?authorization=bce-auth-v1%2FALTAKzReLNvew3ySINYJ0fuAMN%2F2026-03-22T03%3A07%3A20Z%2F-1%2F%2Fef0d6c55411a4bf2ca1f153edfdf97e2af2db47a174ec587d520d4743156a054" alt="Image" width="82%" /></div>


<div style="text-align: center;"><div style="text-align: center;">Table 1: Non-answers - classification report</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td><td style='text-align: center; word-wrap: break-word;'>(4)</td><td style='text-align: center; word-wrap: break-word;'>(5)</td><td style='text-align: center; word-wrap: break-word;'>(6)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Manual</td><td style='text-align: center; word-wrap: break-word;'>Gow et al. (2021)</td><td style='text-align: center; word-wrap: break-word;'>ChatGPT Zero-shot</td><td style='text-align: center; word-wrap: break-word;'>GPT-4 Zero-shot</td><td style='text-align: center; word-wrap: break-word;'>Keyword + GPT-3 Filter + ChatGPT</td><td style='text-align: center; word-wrap: break-word;'>(5) + ChatGPT FT Filter</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Answer</td><td style='text-align: center; word-wrap: break-word;'>423</td><td style='text-align: center; word-wrap: break-word;'>443</td><td style='text-align: center; word-wrap: break-word;'>418</td><td style='text-align: center; word-wrap: break-word;'>398</td><td style='text-align: center; word-wrap: break-word;'>408</td><td style='text-align: center; word-wrap: break-word;'>423</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Non-answer</td><td style='text-align: center; word-wrap: break-word;'>77</td><td style='text-align: center; word-wrap: break-word;'>57</td><td style='text-align: center; word-wrap: break-word;'>82</td><td style='text-align: center; word-wrap: break-word;'>102</td><td style='text-align: center; word-wrap: break-word;'>92</td><td style='text-align: center; word-wrap: break-word;'>77</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Accuracy</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.86</td><td style='text-align: center; word-wrap: break-word;'>0.91</td><td style='text-align: center; word-wrap: break-word;'>0.93</td><td style='text-align: center; word-wrap: break-word;'>0.94</td><td style='text-align: center; word-wrap: break-word;'>0.96</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Type I error</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.06</td><td style='text-align: center; word-wrap: break-word;'>0.06</td><td style='text-align: center; word-wrap: break-word;'>0.07</td><td style='text-align: center; word-wrap: break-word;'>0.05</td><td style='text-align: center; word-wrap: break-word;'>0.02</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Type II error</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.57</td><td style='text-align: center; word-wrap: break-word;'>0.26</td><td style='text-align: center; word-wrap: break-word;'>0.08</td><td style='text-align: center; word-wrap: break-word;'>0.10</td><td style='text-align: center; word-wrap: break-word;'>0.13</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Non-answers:</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Precision</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.58</td><td style='text-align: center; word-wrap: break-word;'>0.70</td><td style='text-align: center; word-wrap: break-word;'>0.70</td><td style='text-align: center; word-wrap: break-word;'>0.75</td><td style='text-align: center; word-wrap: break-word;'>0.87</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Recall</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.43</td><td style='text-align: center; word-wrap: break-word;'>0.74</td><td style='text-align: center; word-wrap: break-word;'>0.92</td><td style='text-align: center; word-wrap: break-word;'>0.90</td><td style='text-align: center; word-wrap: break-word;'>0.87</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>F1 score</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.49</td><td style='text-align: center; word-wrap: break-word;'>0.72</td><td style='text-align: center; word-wrap: break-word;'>0.79</td><td style='text-align: center; word-wrap: break-word;'>0.82</td><td style='text-align: center; word-wrap: break-word;'>0.87</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Total:</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Precision</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.85</td><td style='text-align: center; word-wrap: break-word;'>0.91</td><td style='text-align: center; word-wrap: break-word;'>0.94</td><td style='text-align: center; word-wrap: break-word;'>0.94</td><td style='text-align: center; word-wrap: break-word;'>0.96</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Recall</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.86</td><td style='text-align: center; word-wrap: break-word;'>0.91</td><td style='text-align: center; word-wrap: break-word;'>0.93</td><td style='text-align: center; word-wrap: break-word;'>0.94</td><td style='text-align: center; word-wrap: break-word;'>0.96</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>F1 score</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.86</td><td style='text-align: center; word-wrap: break-word;'>0.91</td><td style='text-align: center; word-wrap: break-word;'>0.93</td><td style='text-align: center; word-wrap: break-word;'>0.94</td><td style='text-align: center; word-wrap: break-word;'>0.96</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>N</td><td style='text-align: center; word-wrap: break-word;'>500</td><td style='text-align: center; word-wrap: break-word;'>500</td><td style='text-align: center; word-wrap: break-word;'>500</td><td style='text-align: center; word-wrap: break-word;'>500</td><td style='text-align: center; word-wrap: break-word;'>500</td><td style='text-align: center; word-wrap: break-word;'>500</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Mean tokens per Q&amp;A pair</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>435 tokens</td><td style='text-align: center; word-wrap: break-word;'>550 tokens</td><td style='text-align: center; word-wrap: break-word;'>300 tokens</td><td style='text-align: center; word-wrap: break-word;'>335 tokens</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Costs per 1,000</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$0</td><td style='text-align: center; word-wrap: break-word;'>$0.66</td><td style='text-align: center; word-wrap: break-word;'>$16.98</td><td style='text-align: center; word-wrap: break-word;'>$0.48</td><td style='text-align: center; word-wrap: break-word;'>$1.06</td></tr></table>

This table reports the performance statistics of the various non-answer classification approaches. ChatGPT refers to the gpt-3.5-turbo model. A full description of the methods is available in Section 4.1 and Online Appendix 3. See footnote 2 for a conceptual introduction to the precision, recall, and F1 scores. The scores are based on the number of True Positives (TP), False Positives (FP), True Negatives (TN), and False Negatives (FN). Accuracy =  $ (TP + TN) / (TP + TN + FP + FN) $, Type I error =  $ FP / (FP + TN) $, Type II error =  $ FN / (FN + TP) $, Precision =  $ TP / (TP + FP) $, Recall =  $ TP / (TP + FN) $, and F1 score =  $ TP / (TP + 0.5 * (FP + FN)) $.

<div style="text-align: center;"><div style="text-align: center;">Table 2: Non-answers – large sample analysis</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td><td style='text-align: center; word-wrap: break-word;'>(4)</td><td style='text-align: center; word-wrap: break-word;'>(5)</td><td style='text-align: center; word-wrap: break-word;'>(6)</td><td style='text-align: center; word-wrap: break-word;'>(7)</td><td style='text-align: center; word-wrap: break-word;'>(8)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Obs.</td><td style='text-align: center; word-wrap: break-word;'>Mean</td><td style='text-align: center; word-wrap: break-word;'>Std. Dev</td><td style='text-align: center; word-wrap: break-word;'>P5</td><td style='text-align: center; word-wrap: break-word;'>P25</td><td style='text-align: center; word-wrap: break-word;'>P50</td><td style='text-align: center; word-wrap: break-word;'>P75</td><td style='text-align: center; word-wrap: break-word;'>P95</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Question-answer pair level</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT method - % non-answer</td><td style='text-align: center; word-wrap: break-word;'>1,152,505</td><td style='text-align: center; word-wrap: break-word;'>0.139</td><td style='text-align: center; word-wrap: break-word;'>0.35</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Gow method - % non-answer</td><td style='text-align: center; word-wrap: break-word;'>1,152,505</td><td style='text-align: center; word-wrap: break-word;'>0.123</td><td style='text-align: center; word-wrap: break-word;'>0.33</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Earnings call level</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Number of Q&amp;A pairs</td><td style='text-align: center; word-wrap: break-word;'>63,959</td><td style='text-align: center; word-wrap: break-word;'>18.019</td><td style='text-align: center; word-wrap: break-word;'>8.93</td><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>12</td><td style='text-align: center; word-wrap: break-word;'>17</td><td style='text-align: center; word-wrap: break-word;'>23</td><td style='text-align: center; word-wrap: break-word;'>34</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT method - # of non-answers</td><td style='text-align: center; word-wrap: break-word;'>63,959</td><td style='text-align: center; word-wrap: break-word;'>2.502</td><td style='text-align: center; word-wrap: break-word;'>2.20</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>1.00</td><td style='text-align: center; word-wrap: break-word;'>2.00</td><td style='text-align: center; word-wrap: break-word;'>4.00</td><td style='text-align: center; word-wrap: break-word;'>7.00</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>GPT method - % of non-answers</td><td style='text-align: center; word-wrap: break-word;'>63,959</td><td style='text-align: center; word-wrap: break-word;'>0.142</td><td style='text-align: center; word-wrap: break-word;'>0.12</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.06</td><td style='text-align: center; word-wrap: break-word;'>0.13</td><td style='text-align: center; word-wrap: break-word;'>0.20</td><td style='text-align: center; word-wrap: break-word;'>0.36</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Gow method - # of non-answers</td><td style='text-align: center; word-wrap: break-word;'>63,959</td><td style='text-align: center; word-wrap: break-word;'>2.210</td><td style='text-align: center; word-wrap: break-word;'>2.10</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>1.00</td><td style='text-align: center; word-wrap: break-word;'>2.00</td><td style='text-align: center; word-wrap: break-word;'>3.00</td><td style='text-align: center; word-wrap: break-word;'>6.00</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Gow method - % of non-answers</td><td style='text-align: center; word-wrap: break-word;'>63,959</td><td style='text-align: center; word-wrap: break-word;'>0.127</td><td style='text-align: center; word-wrap: break-word;'>0.12</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.04</td><td style='text-align: center; word-wrap: break-word;'>0.11</td><td style='text-align: center; word-wrap: break-word;'>0.19</td><td style='text-align: center; word-wrap: break-word;'>0.33</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">Table 3: Non-answer dimensions – model performance</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td><td style='text-align: center; word-wrap: break-word;'>(4)</td><td style='text-align: center; word-wrap: break-word;'>(5)</td><td style='text-align: center; word-wrap: break-word;'>(6)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td colspan="3">GPT-4 - Zero shot</td><td colspan="3">Fine-tuned ChatGPT</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Precision</td><td style='text-align: center; word-wrap: break-word;'>Recall</td><td style='text-align: center; word-wrap: break-word;'>F1 score</td><td style='text-align: center; word-wrap: break-word;'>Precision</td><td style='text-align: center; word-wrap: break-word;'>Recall</td><td style='text-align: center; word-wrap: break-word;'>F1 score</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Answer</td><td style='text-align: center; word-wrap: break-word;'>1.00</td><td style='text-align: center; word-wrap: break-word;'>0.41</td><td style='text-align: center; word-wrap: break-word;'>0.58</td><td style='text-align: center; word-wrap: break-word;'>0.93</td><td style='text-align: center; word-wrap: break-word;'>0.73</td><td style='text-align: center; word-wrap: break-word;'>0.82</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Non-answer</td><td style='text-align: center; word-wrap: break-word;'>0.86</td><td style='text-align: center; word-wrap: break-word;'>1.00</td><td style='text-align: center; word-wrap: break-word;'>0.93</td><td style='text-align: center; word-wrap: break-word;'>0.93</td><td style='text-align: center; word-wrap: break-word;'>0.98</td><td style='text-align: center; word-wrap: break-word;'>0.96</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.89</td><td style='text-align: center; word-wrap: break-word;'>0.88</td><td style='text-align: center; word-wrap: break-word;'>0.85</td><td style='text-align: center; word-wrap: break-word;'>0.93</td><td style='text-align: center; word-wrap: break-word;'>0.93</td><td style='text-align: center; word-wrap: break-word;'>0.93</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Cannot give</td><td style='text-align: center; word-wrap: break-word;'>0.98</td><td style='text-align: center; word-wrap: break-word;'>0.96</td><td style='text-align: center; word-wrap: break-word;'>0.97</td><td style='text-align: center; word-wrap: break-word;'>0.93</td><td style='text-align: center; word-wrap: break-word;'>0.91</td><td style='text-align: center; word-wrap: break-word;'>0.92</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Do not know</td><td style='text-align: center; word-wrap: break-word;'>0.98</td><td style='text-align: center; word-wrap: break-word;'>0.99</td><td style='text-align: center; word-wrap: break-word;'>0.98</td><td style='text-align: center; word-wrap: break-word;'>0.95</td><td style='text-align: center; word-wrap: break-word;'>0.96</td><td style='text-align: center; word-wrap: break-word;'>0.95</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.98</td><td style='text-align: center; word-wrap: break-word;'>0.98</td><td style='text-align: center; word-wrap: break-word;'>0.98</td><td style='text-align: center; word-wrap: break-word;'>0.94</td><td style='text-align: center; word-wrap: break-word;'>0.94</td><td style='text-align: center; word-wrap: break-word;'>0.94</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Range or percentage</td><td style='text-align: center; word-wrap: break-word;'>0.88</td><td style='text-align: center; word-wrap: break-word;'>0.86</td><td style='text-align: center; word-wrap: break-word;'>0.87</td><td style='text-align: center; word-wrap: break-word;'>0.73</td><td style='text-align: center; word-wrap: break-word;'>0.73</td><td style='text-align: center; word-wrap: break-word;'>0.73</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Qualitative</td><td style='text-align: center; word-wrap: break-word;'>0.95</td><td style='text-align: center; word-wrap: break-word;'>0.92</td><td style='text-align: center; word-wrap: break-word;'>0.93</td><td style='text-align: center; word-wrap: break-word;'>0.90</td><td style='text-align: center; word-wrap: break-word;'>0.92</td><td style='text-align: center; word-wrap: break-word;'>0.91</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Complete refusal</td><td style='text-align: center; word-wrap: break-word;'>0.84</td><td style='text-align: center; word-wrap: break-word;'>0.93</td><td style='text-align: center; word-wrap: break-word;'>0.88</td><td style='text-align: center; word-wrap: break-word;'>0.90</td><td style='text-align: center; word-wrap: break-word;'>0.85</td><td style='text-align: center; word-wrap: break-word;'>0.87</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.92</td><td style='text-align: center; word-wrap: break-word;'>0.92</td><td style='text-align: center; word-wrap: break-word;'>0.92</td><td style='text-align: center; word-wrap: break-word;'>0.88</td><td style='text-align: center; word-wrap: break-word;'>0.88</td><td style='text-align: center; word-wrap: break-word;'>0.88</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Breakdown</td><td style='text-align: center; word-wrap: break-word;'>0.96</td><td style='text-align: center; word-wrap: break-word;'>0.86</td><td style='text-align: center; word-wrap: break-word;'>0.90</td><td style='text-align: center; word-wrap: break-word;'>0.83</td><td style='text-align: center; word-wrap: break-word;'>0.79</td><td style='text-align: center; word-wrap: break-word;'>0.81</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Forward-looking</td><td style='text-align: center; word-wrap: break-word;'>0.96</td><td style='text-align: center; word-wrap: break-word;'>0.94</td><td style='text-align: center; word-wrap: break-word;'>0.95</td><td style='text-align: center; word-wrap: break-word;'>0.89</td><td style='text-align: center; word-wrap: break-word;'>0.87</td><td style='text-align: center; word-wrap: break-word;'>0.88</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Related party</td><td style='text-align: center; word-wrap: break-word;'>0.89</td><td style='text-align: center; word-wrap: break-word;'>0.93</td><td style='text-align: center; word-wrap: break-word;'>0.91</td><td style='text-align: center; word-wrap: break-word;'>0.70</td><td style='text-align: center; word-wrap: break-word;'>0.84</td><td style='text-align: center; word-wrap: break-word;'>0.76</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>R&amp;D or regulation</td><td style='text-align: center; word-wrap: break-word;'>0.85</td><td style='text-align: center; word-wrap: break-word;'>0.92</td><td style='text-align: center; word-wrap: break-word;'>0.88</td><td style='text-align: center; word-wrap: break-word;'>0.86</td><td style='text-align: center; word-wrap: break-word;'>0.90</td><td style='text-align: center; word-wrap: break-word;'>0.88</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Other</td><td style='text-align: center; word-wrap: break-word;'>0.78</td><td style='text-align: center; word-wrap: break-word;'>0.87</td><td style='text-align: center; word-wrap: break-word;'>0.82</td><td style='text-align: center; word-wrap: break-word;'>0.65</td><td style='text-align: center; word-wrap: break-word;'>0.63</td><td style='text-align: center; word-wrap: break-word;'>0.64</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.91</td><td style='text-align: center; word-wrap: break-word;'>0.91</td><td style='text-align: center; word-wrap: break-word;'>0.91</td><td style='text-align: center; word-wrap: break-word;'>0.82</td><td style='text-align: center; word-wrap: break-word;'>0.81</td><td style='text-align: center; word-wrap: break-word;'>0.81</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Optimistic</td><td style='text-align: center; word-wrap: break-word;'>0.92</td><td style='text-align: center; word-wrap: break-word;'>0.93</td><td style='text-align: center; word-wrap: break-word;'>0.92</td><td style='text-align: center; word-wrap: break-word;'>0.87</td><td style='text-align: center; word-wrap: break-word;'>0.88</td><td style='text-align: center; word-wrap: break-word;'>0.87</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Neutral or pessimistic</td><td style='text-align: center; word-wrap: break-word;'>0.92</td><td style='text-align: center; word-wrap: break-word;'>0.91</td><td style='text-align: center; word-wrap: break-word;'>0.91</td><td style='text-align: center; word-wrap: break-word;'>0.86</td><td style='text-align: center; word-wrap: break-word;'>0.85</td><td style='text-align: center; word-wrap: break-word;'>0.86</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>0.92</td><td style='text-align: center; word-wrap: break-word;'>0.92</td><td style='text-align: center; word-wrap: break-word;'>0.92</td><td style='text-align: center; word-wrap: break-word;'>0.87</td><td style='text-align: center; word-wrap: break-word;'>0.87</td><td style='text-align: center; word-wrap: break-word;'>0.87</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>N</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>400</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>400</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Mean tokens per Q&amp;A pair</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>1,267 tokens</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>324 tokens</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Costs per 1,000</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$45.53</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>$4.18</td><td style='text-align: center; word-wrap: break-word;'></td></tr></table>

This table reports the performance statistics for the last step of the GPT method. The statistics are based on an evaluation sample of 400 random Q&A pairs that remain after the first three steps of the GPT method. OA.2 and OA.3 include the GPT-4 prompt and a full description of the ChatGPT fine-tuning procedure.

<div style="text-align: center;"><div style="text-align: center;">Table 4: Non-answer dimensions – single variable regressions</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td><td style='text-align: center; word-wrap: break-word;'>(4)</td><td style='text-align: center; word-wrap: break-word;'>(5)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Non-answer Cannot give</td><td style='text-align: center; word-wrap: break-word;'>Non-answer Positive</td><td style='text-align: center; word-wrap: break-word;'>Non-answer Full reject</td><td style='text-align: center; word-wrap: break-word;'>Non-answer Qualitative</td><td style='text-align: center; word-wrap: break-word;'>Non-answer Range or Perc.</td></tr><tr><td rowspan="2">Q - Breakdown</td><td style='text-align: center; word-wrap: break-word;'>$ 21.225^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -5.175^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -3.368^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -5.751^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 9.119^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.750)</td><td style='text-align: center; word-wrap: break-word;'>(0.561)</td><td style='text-align: center; word-wrap: break-word;'>(0.309)</td><td style='text-align: center; word-wrap: break-word;'>(0.447)</td><td style='text-align: center; word-wrap: break-word;'>(0.249)</td></tr><tr><td rowspan="2">Q - Forward-looking</td><td style='text-align: center; word-wrap: break-word;'>$ -17.545^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 10.048^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -5.836^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 5.130^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.706^{**} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.878)</td><td style='text-align: center; word-wrap: break-word;'>(0.563)</td><td style='text-align: center; word-wrap: break-word;'>(0.399)</td><td style='text-align: center; word-wrap: break-word;'>(0.574)</td><td style='text-align: center; word-wrap: break-word;'>(0.305)</td></tr><tr><td rowspan="2">Q - Related party</td><td style='text-align: center; word-wrap: break-word;'>$ 21.220^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -2.111^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 9.815^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -3.580^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -6.235^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(1.135)</td><td style='text-align: center; word-wrap: break-word;'>(0.426)</td><td style='text-align: center; word-wrap: break-word;'>(0.380)</td><td style='text-align: center; word-wrap: break-word;'>(0.426)</td><td style='text-align: center; word-wrap: break-word;'>(0.320)</td></tr><tr><td rowspan="2">Q - R&amp;D or regulation</td><td style='text-align: center; word-wrap: break-word;'>$ -9.988^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -8.191^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 8.606^{***} $</td><td style='text-align: center; word-wrap: break-word;'>-1.400</td><td style='text-align: center; word-wrap: break-word;'>$ -7.206^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(1.088)</td><td style='text-align: center; word-wrap: break-word;'>(0.973)</td><td style='text-align: center; word-wrap: break-word;'>(0.732)</td><td style='text-align: center; word-wrap: break-word;'>(0.812)</td><td style='text-align: center; word-wrap: break-word;'>(0.371)</td></tr><tr><td rowspan="2">Q - Other</td><td style='text-align: center; word-wrap: break-word;'>$ -6.222^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -5.331^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 1.682^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 1.530^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -3.211^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.910)</td><td style='text-align: center; word-wrap: break-word;'>(0.471)</td><td style='text-align: center; word-wrap: break-word;'>(0.321)</td><td style='text-align: center; word-wrap: break-word;'>(0.392)</td><td style='text-align: center; word-wrap: break-word;'>(0.165)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Multivariate</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>No</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>N</td><td style='text-align: center; word-wrap: break-word;'>160,049</td><td style='text-align: center; word-wrap: break-word;'>160,049</td><td style='text-align: center; word-wrap: break-word;'>160,049</td><td style='text-align: center; word-wrap: break-word;'>160,049</td><td style='text-align: center; word-wrap: break-word;'>160,049</td></tr></table>

# Online Appendix to:

# ChatGPT for Textual Analysis? How to use Generative LLMs in Accounting Research

Ties de Kok

### June 2024

The following pages provide further details on the items mentioned in the main paper.

OA 1 – GPT model overview and discussion ii

OA 2 – Full prompts v

OA 3 – Full description of the GPT method

OA 4 – Examples of classification differences between the GPT and Gow et al. methods xii

OA 5 - Using and fine-tuning a local GLLM xiv

OA 6 – Additional analysis - question features and non-answers xvi

Table OA.1 – Question features and non-answers xvii

Table OA.1 (cont.) – Question features and non-answers xviii

Additional references xix

##### OA 1 – GPT model overview and discussion

There are many different GPT models available and new models come out frequently. This section covers model differences as well as an overview of popular models as of June 2024.

OA 1.1 – Conceptual differences between GPT models

From a practical point of view, there are five primary differences between GPT models:

1. Size – The model size is commonly expressed by the number of parameters (i.e., the number of “coefficients” in the neural network) and roughly reflects the capabilities of a model. For example, a 70b (70 billion parameter) model is generally expected to perform better out-of-the-box relative to a 7b (7 billion parameter) model. The downsides of model size are the memory requirements and compute time which scale with the number of parameters. Larger models require more expensive hardware and are generally slower.

2. Tuning – The model tuning reflects how the model responds and the types of tasks it is good at. For example, the ChatGPT model is “instruct tuned” which means that it is designed to provide responses like a human assistant. Similarly, a model like CodeLlama-70b-Python is designed such that it is good at generating Python code. The tuning of a model is the product of two primary elements: the content of the original training data and the (optional) process with which it was fine-tuned at a second (or later) stage. For example, the Qwen1.5-7B-Chat model by Alibaba is bilingual in English and Mandarin due to the original training data and will respond conversationally like a human assistant (indicated by the "chat" part of the name) due to a second stage fine-tune that steers the model to respond like an assistant.

3. Context length – The context length of a model reflects the maximum number of tokens that the model can handle at a time. The context length is measured as the total number of tokens in the prompt as well as the completion and is sometimes indicated in the model name. For example, the “16k” part of “gpt-3.5-turbo-16k” by OpenAI indicates that the model has a context length of 16,385 tokens. Practically, the context length determines how long of a document the model can handle before it throws an error. Models with longer context lengths can handle longer input documents, although they might not pay equal attention to all parts of long documents. For example, Liu et al. (2023) find that GLLMs tend to focus primarily on information at the start and end of the context window.

4. Availability – GPT models can be made available in multiple ways. The biggest distinction is whether the model weights are made available or whether the model is only available from behind a third-party API. For example, the model weights for popular models by OpenAI, Google, and Cohere (e.g., ChatGPT, GPT-4, Bard, Claude2) are not public, and you can only interact with each model through its respective API. Other models like Llama2 by Meta and Phi-2 by Microsoft have publicly available model weights, often through the Huggingface platform. These “open source” models can be downloaded and run locally or in the cloud with access to the appropriate hardware. Some open-source models do have restrictive licenses that, for example, prevent them from being used for commercial purposes.

5. Quantization – Some models are quantized. Model quantization means that the model weights are rounded to have a lower precision (i.e., “have fewer decimal places”). Reducing the precision to half-precision (16-bit),  $ 1/4^{th} $ precision (8-bit), or  $ 1/8^{th} $ precision (4-bit) helps to reduce the memory requirements necessary to run the model. For example, an 8-bit quantized model requires only  $ 1/4^{th} $ the memory relative to its full precision equivalent. Quantized models are quicker and cheaper to use although the quantization process can result in a drop in performance relative to the full precision model.

### OA 1.2 – Which models to try first for your task?

When considering GLLMs for a research project, I recommend starting with the flowchart in Figure 1 of the paper. If a third-party API is possible and feasible then I recommend starting with the OpenAI API and the ChatGPT or GPT-4 models. These models are competitively priced for the performance they deliver out of the box. The OpenAI models are also available through Microsoft Azure, which can make for easier reimbursement. The Google models are what I recommend trying second among the API providers, especially once the new Gemini 1.5 becomes more generally available. When considering local models, I recommend starting with a Llama model or a derivative, such as Llama3 70b or Mistral 8x7b for zero-shot classifications. For local model fine-tuning, I recommend trying Phi-3 mini, Mistral 7b, or one of the Qwen models as they have good fine-tuning support (e.g., by Llama-Factory). The companion website provides code examples on how to get started with the OpenAI API as well as with local models.

Finally, I also recommend doing some initial experiments with the  $ \underline{\text{Tiktoken}} $ package to get a sense of the context window requirements for your task. This will help navigate the table below. For example, a task with long inputs that are up to 20k tokens long will rule out many models.

<div style="text-align: center;"><div style="text-align: center;">OA 1.3 – Overview of popular GPT models</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>Provider</td><td style='text-align: center; word-wrap: break-word;'>Model</td><td style='text-align: center; word-wrap: break-word;'>Size / Cost</td><td style='text-align: center; word-wrap: break-word;'>Context length</td><td style='text-align: center; word-wrap: break-word;'>Availability</td><td style='text-align: center; word-wrap: break-word;'>Fine-tunable?</td><td style='text-align: center; word-wrap: break-word;'>Tuning</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>OpenAI</td><td style='text-align: center; word-wrap: break-word;'>gpt-3.5-turbo</td><td style='text-align: center; word-wrap: break-word;'>$ \ref{psun_model_1} $</td><td style='text-align: center; word-wrap: break-word;'>4k</td><td style='text-align: center; word-wrap: break-word;'>$ API^{2} $</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>OpenAI</td><td style='text-align: center; word-wrap: break-word;'>gpt-3.5-turbo-16k</td><td style='text-align: center; word-wrap: break-word;'>$ \ref{psun_model_16} $</td><td style='text-align: center; word-wrap: break-word;'>16k</td><td style='text-align: center; word-wrap: break-word;'>API</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>OpenAI</td><td style='text-align: center; word-wrap: break-word;'>gpt-4-turbo &amp; gpt-4o</td><td style='text-align: center; word-wrap: break-word;'>$ \ref{psun_model_16} $</td><td style='text-align: center; word-wrap: break-word;'>128k</td><td style='text-align: center; word-wrap: break-word;'>API</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>OpenAI</td><td style='text-align: center; word-wrap: break-word;'>gpt-4</td><td style='text-align: center; word-wrap: break-word;'>$ \ref{psun_model_16} $</td><td style='text-align: center; word-wrap: break-word;'>8k</td><td style='text-align: center; word-wrap: break-word;'>API</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>OpenAI</td><td style='text-align: center; word-wrap: break-word;'>gpt-4-32k</td><td style='text-align: center; word-wrap: break-word;'>$ \ref{psun_model_16} $</td><td style='text-align: center; word-wrap: break-word;'>32k</td><td style='text-align: center; word-wrap: break-word;'>API</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>OpenAI</td><td style='text-align: center; word-wrap: break-word;'>GPT base babbage $ ^{3} $</td><td style='text-align: center; word-wrap: break-word;'>$ \ref{psun_model_16} $</td><td style='text-align: center; word-wrap: break-word;'>16k</td><td style='text-align: center; word-wrap: break-word;'>API</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Text completion</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>OpenAI</td><td style='text-align: center; word-wrap: break-word;'>GPT base davinci</td><td style='text-align: center; word-wrap: break-word;'>?? /</td><td style='text-align: center; word-wrap: break-word;'>16k</td><td style='text-align: center; word-wrap: break-word;'>API</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Text completion</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Anthropic</td><td style='text-align: center; word-wrap: break-word;'>Claude 2.0</td><td style='text-align: center; word-wrap: break-word;'>?? /</td><td style='text-align: center; word-wrap: break-word;'>100k</td><td style='text-align: center; word-wrap: break-word;'>API</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Anthropic</td><td style='text-align: center; word-wrap: break-word;'>Claude 2.1</td><td style='text-align: center; word-wrap: break-word;'>?? /</td><td style='text-align: center; word-wrap: break-word;'>200k</td><td style='text-align: center; word-wrap: break-word;'>API</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Anthropic</td><td style='text-align: center; word-wrap: break-word;'>Claude Instant</td><td style='text-align: center; word-wrap: break-word;'>?? /</td><td style='text-align: center; word-wrap: break-word;'>100k</td><td style='text-align: center; word-wrap: break-word;'>API</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Google</td><td style='text-align: center; word-wrap: break-word;'>Gemini 1.5</td><td style='text-align: center; word-wrap: break-word;'>?? /</td><td style='text-align: center; word-wrap: break-word;'>128k/1m $ ^{4} $</td><td style='text-align: center; word-wrap: break-word;'>API</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Google</td><td style='text-align: center; word-wrap: break-word;'>Gemini 1.0 Ultra</td><td style='text-align: center; word-wrap: break-word;'>?? /</td><td style='text-align: center; word-wrap: break-word;'>32k</td><td style='text-align: center; word-wrap: break-word;'>API</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Google</td><td style='text-align: center; word-wrap: break-word;'>Gemini 1.0 Pro</td><td style='text-align: center; word-wrap: break-word;'>?? /</td><td style='text-align: center; word-wrap: break-word;'>32k</td><td style='text-align: center; word-wrap: break-word;'>API</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Google</td><td style='text-align: center; word-wrap: break-word;'>Gemma 2b</td><td style='text-align: center; word-wrap: break-word;'>2b /</td><td style='text-align: center; word-wrap: break-word;'>8k</td><td style='text-align: center; word-wrap: break-word;'>Local</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Text completion or chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Google</td><td style='text-align: center; word-wrap: break-word;'>Gemma 7b</td><td style='text-align: center; word-wrap: break-word;'>7b /</td><td style='text-align: center; word-wrap: break-word;'>8k</td><td style='text-align: center; word-wrap: break-word;'>Local</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Text completion or chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Meta</td><td style='text-align: center; word-wrap: break-word;'>Llama2/3 7b</td><td style='text-align: center; word-wrap: break-word;'>7b /</td><td style='text-align: center; word-wrap: break-word;'>4k /8k</td><td style='text-align: center; word-wrap: break-word;'>Local</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Text completion or chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Meta</td><td style='text-align: center; word-wrap: break-word;'>Llama2 13b</td><td style='text-align: center; word-wrap: break-word;'>13b /</td><td style='text-align: center; word-wrap: break-word;'>4k</td><td style='text-align: center; word-wrap: break-word;'>Local</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Text completion or chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Meta</td><td style='text-align: center; word-wrap: break-word;'>Llama2/3 70b</td><td style='text-align: center; word-wrap: break-word;'>70b /</td><td style='text-align: center; word-wrap: break-word;'>4k /8k</td><td style='text-align: center; word-wrap: break-word;'>Local</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Text completion or chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Microsoft</td><td style='text-align: center; word-wrap: break-word;'>Phi-2</td><td style='text-align: center; word-wrap: break-word;'>2.7b /</td><td style='text-align: center; word-wrap: break-word;'>2k</td><td style='text-align: center; word-wrap: break-word;'>Local</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Microsoft</td><td style='text-align: center; word-wrap: break-word;'>Phi-3 mini</td><td style='text-align: center; word-wrap: break-word;'>3.8b /</td><td style='text-align: center; word-wrap: break-word;'>128k</td><td style='text-align: center; word-wrap: break-word;'>Local</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Mistral</td><td style='text-align: center; word-wrap: break-word;'>Mistral 7b</td><td style='text-align: center; word-wrap: break-word;'>7b /</td><td style='text-align: center; word-wrap: break-word;'>8k</td><td style='text-align: center; word-wrap: break-word;'>Local</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Text completion or chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Mistral</td><td style='text-align: center; word-wrap: break-word;'>Mistral 8x7b $ ^{5} $</td><td style='text-align: center; word-wrap: break-word;'>45B /</td><td style='text-align: center; word-wrap: break-word;'>32k</td><td style='text-align: center; word-wrap: break-word;'>Local</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Text completion or chat assistant</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Alibaba</td><td style='text-align: center; word-wrap: break-word;'>Qwen 1.8b</td><td style='text-align: center; word-wrap: break-word;'>1.8b /</td><td style='text-align: center; word-wrap: break-word;'>32k</td><td style='text-align: center; word-wrap: break-word;'>Local</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant, English+Chinese</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Alibaba</td><td style='text-align: center; word-wrap: break-word;'>Qwen 7b</td><td style='text-align: center; word-wrap: break-word;'>7b /</td><td style='text-align: center; word-wrap: break-word;'>32k</td><td style='text-align: center; word-wrap: break-word;'>Local</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant, English+Chinese</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Alibaba</td><td style='text-align: center; word-wrap: break-word;'>Qwen 14b</td><td style='text-align: center; word-wrap: break-word;'>14b /</td><td style='text-align: center; word-wrap: break-word;'>32k</td><td style='text-align: center; word-wrap: break-word;'>Local</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant, English+Chinese</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Alibaba</td><td style='text-align: center; word-wrap: break-word;'>Qwen 72b</td><td style='text-align: center; word-wrap: break-word;'>72b /</td><td style='text-align: center; word-wrap: break-word;'>32k</td><td style='text-align: center; word-wrap: break-word;'>Local</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Chat assistant, English+Chinese</td></tr></table>





The open-source (“local”) models in the table above also have hundreds of derivative variants that aim to provide improvements such as different tuning or larger context lengths. For a good overview, I recommend checking out the following website:  $ \underline{\text{https://huggingface.co/models.}} $

### OA 2 – Full prompts

OA 2.1 - ChatGPT zero shot (Table 1 column 3):

In the provided text, the analyst posed the question:

> {question}

The manager responded with:
> {answer}

**Task 1 - sentences:**

From the manager's response, extract only those sentences where the manager explicitly indicates either:
- They currently lack specific details or information to provide.
- They are deliberately choosing not to share specific information at the moment.

Please exclude sentences that discuss general uncertainties, company plans, or any actions the company might take in the future. Also exclude disclaimers that are immediately followed by an answer.

Important: these sentences are rare, in 65% of the cases this will be an empty list. It is ok to return an empty list.

Provide your response using the following JSON format: JSON = {
  "sentences": []
}

JSON =

OA 2.1 - GPT-4 zero shot (Table 1 column 4):

In the provided text, the analyst posed the question:
> {question}

The manager responded with:
> {answer}

**Task 1 - sentences:**

From the manager's response, extract only those sentences where the manager unambiguously indicates:
- A clear absence of specific details or information that prevents them from providing an answer.
- A conscious decision not to divulge particular information at the moment.

Important criteria for valid sentences:
- Must state a lack of knowledge about a specific detail.
- Must clearly indicate a choice not to share a particular detail.

Exclude:

- Statements expressing general uncertainty or vagueness.
- Sentences about company plans or potential future actions.
- Disclaimers, deferrals to others, or any remarks that still convey a type of answer or opinion.

**In essence, the qualifying sentence should firmly suggest: "I don't have that specific detail" or "I choose not to share that specific detail now."**

Provide your response using the following JSON format: JSON = {{
    "sentences": []
}}

Examples of sentences to exclude / ignore:
- "I'll let another person handle the specifics."
- "But time will tell."
- "We will decide that in the future."
- "The exact details are yet to be decided."

Be extremely selective. Only include sentences you are 100% sure about.

JSON =

OA 2.3 - ChatGPT zero shot filter (Table 1 – column 5)

Analyst question:
{question}
Manager response:
{answer}

A research assistant has marked the above response as including a statement that reflects unwillingness or inability to answer (part) of the analysts' question, because of the following comment(s):
> {comments}

Based on the question and full response above, provide a detailed assessment whether the manager's response includes a statement, explanation, or justification indicating an inability or unwillingness to answer the question. If you classify the response as reflecting inability or unwillingness to answer, justify your classification with specific phrases or sentences from the manager's response. If there's no such indication, explain why not.

Your response should be in the following JSON format:
JSON = {{
    "assessment": a detailed assessment unique to this evaluation following the instructions above,
    "your_classification": 1 or 0
}}

JSON =
OA 2.4 - GPT-4 zero shot filter with dimensions (Table 3, columns 1 to 3)

In the provided text, the analyst posed the question:
> {question}
The manager responded with:
> {answer}
**Task 1 - sentences:**
From the manager's response, extract only those sentences where the manager explicitly indicates either:
- They currently lack specific details or information to provide.
- They are deliberately choosing not to share specific information at the moment.
Please exclude sentences that discuss general uncertainties, company plans, or any actions the company might take in the future.
**Task 2 - reasons:**
Why is the manager reluctant, unable, or unwilling to share the specific information?
Your choices:
- don't know -> the manager does not know or have the numbers and/or it is too early to tell
- can't give -> the manager states that they don't provide that information as per policy, norm, or principle
- proprietary -> the manager states that the information is proprietary or sensitive for competitors
- invalid match -> the answer is incorrectly flagged as containing a refusal or hesitation to answer, select if no sentences.
**Task 3 - alternative:**
Does the manager still provide an alternative answer, if so what do they provide? Your choices:
- range or perc -> the manager instead provides a range estimate or another type of quantitative estimate such as a percentage
- comparison -> the manager instead makes a quantitative or qualitative comparison to some other point of reference
- qualitative -> the manager instead provides a qualitative statement without sharing exact details or numbers
- no alternative -> the manager provides no further information or only explains their reasoning for not answering
- invalid match -> the answer is incorrectly flagged as containing a refusal or hesitation to answer, select if no sentences.
**Task 4 - topic:**
What is the part of the question about that the manager is not, or only partially, answering? Your choices:

- forward_looking - the manager refuses to provide guidance or other forward-looking information
- breakdown - the manager refuses to provide a breakdown or more granularity or detail on something
- rd_clinical_trails - the manager refuses to provide more information on a research & development projects or clinical trails
- regulation_certification - the manager refuses to speak about a regulatory matter, a compliance issue, or an ongoing certification by a third-party
- customer_or_supplier - the manager refuses to provide details on major customers or suppliers
- major_investment - the manager refuses to speak about a merger and/or acquisition or an other type of major investment, collaboration, or partnership
- other
**Task 5 - sentiment:**
In the manager response, are they trying to paint a positive, negative, or neutral picture?
- optimistic -> the manager is trying to paint a (somewhat) positive picture with their alternate answer
- pessimistic -> the manager is trying to paint a (somewhat) cautionary or pessimistic picture with their alternative answer
- neutral -> the manager is painting is trying to paint a neutral picture
Provide your response using the following JSON format: JSON = {
  "sentences": [],
  "reasons-discussion": a brief discussion of your choice for "reasons",
  "reasons": don't know / can_give / proprietary / invalid_match,
  "alternative-discussion": a brief discussion of your choice for "alternative",
  "alternative": range_or_perc / comparison / qualitative / no_alternative / invalid_match,
  "topic-discussion": a brief discussion of your choice for "topic",
  "topic": forward_looking / breakdown / rd_clinical_trails / regulation_certification / customer_or_supplier / major_investment,
  "sentiment-discussion": a brief discussion of your choice for "sentiment"
  "sentiment": optimistic / pessimistic / neutral
}
JSON =

##### OA 2.5 - ChatGPT fine-tuned filter with dimensions (Table 3, columns 4 to 6)

Analyst question:
> {question}

Manager response:
> {answer}

###
{json} <|end|>

#### OA 3 – Full description of the GPT method

This section provides more detail on the four steps of the GPT method. This approach demonstrates the various ways to use GLLMs, which makes it more extensive than necessary. A two-step approach (e.g., keyword filter + fine-tuned GLLM) is sufficient for most use cases.

### Step 1: Keyword filter

I first narrow down the Q&A pairs to those that possibly include a non-answer. Identifying possible non-answers is an easier task than identifying exact non-answers. Specifically, any false positives (i.e., sentences matched as a possible non-answer, but are not) will be taken care of in the later stages. So, the objective is to reduce the sample of possible non-answers while minimizing false negatives. Minimizing false negatives is the primary concern as any Q&A pairs without a keyword match will be marked as an answer and not be analyzed by the more powerful methods later.

To develop the keyword list, I use the words in the regular expressions by Gow et al. (2021) as a start. I then manually extend this list with unigrams, bigrams, or trigrams that help reduce false negatives. The full keyword list is shown below. I apply the keyword search at the sentence level and mark the Q&A pairs with one or more keyword matches for further processing.

#### Trigrams:

call  $ \underline{\text{it}} $ out, at  $ \underline{\text{this}} $ time, at  $ \underline{\text{this}} $ point, at  $ \underline{\text{this}} $ moment, break  $ \underline{\text{it}} $ out, don  $ \underline{\text{t}} $ have, don  $ \underline{\text{t}} $ know  $ \underline{\text{Big}} $rams:

not_going, will_not, won_t, by_region, get_into, that_level, are_not, don_t, do_not, give_you, break_out, splice_out, tell_you, too_early, can_t, can_not, not_ready, right_now, no_idea, not_give, not_sure, wouldn_t, haven_t

##### Unigrams:

cannot, comment, commenting, comments, unable, guidance, guide, guiding, forward, hard, talk, range, disclose, report, privately, forecast, forecasts, forecasting, specific, specifics, detail, details, public, publicly, provide, breakout, statement, statements, update, announcement, announcements, answer, answers, quantify, share, sharing, information, discuss, mention, sorry, apologies, apologize, recall, remember, without, specifically, difficult, officially

### Step 2: Basic machine learning filter

The keyword approach is simple and fast, but it is naïve in its implementation as it does not take any context into account. An alternative filtering approach is to use a basic supervised machine learning algorithm. To demonstrate that, I next train a classifier using the OpenAI API to classify sentences that possibly contain a non-answer. Like in step 1, the objective is to reduce the sample while minimizing false negatives. To train the classifier, I randomly draw a sample of 1,500 Q&A pairs and classify the resulting 2,100 response sentences that contain a keyword match. The performance statistics show a non-answer recall score of 97%, which indicates a minimal number of false negatives. I apply this classifier to the keyword-matched sentences and retain Q&A pairs with one or more sentence matches for further processing.

The prompt and completion templates for the GPT-3 Babbage model are simple and shown below:

prompt_template = "" <|input|> {sentence} -> ""

completion_template = "" {answer - 0/1} <|end|> ""

#### Step 3: Zero-shot ChatGPT

The two filtering steps reduce the sample of Q&A pairs with possible non-answers to about  $ 1/3^{rd} $ of the full sample. These remaining pairs contain the answers that are hardest to classify as they all have some element of a non-answer to them. I demonstrate two ways, zero-shot and fine-tuning, of using a ChatGPT model to solve the remaining classifications. These final classifications are done at the Q&A pair level, not the sentence level, to provide the model with the full question-and-answer context when making the non-answer classifications.

For the zero-shot ChatGPT approach (i.e., step 3) I design the prompt shown in OA 2.3. The zero-shot prompt has a few notable design considerations. First, I am only applying this prompt on the sample of Q&A pairs that remain after the filtering step, which makes it a distinct task from the full sample zero-shot prompt in OA 2.1. Second, I help ChatGPT by providing it with the matched sentences from steps 1 and 2 (i.e., the “comments” portion in the prompt). Third, I frame the task in terms of “evaluate the work of a research assistant”, to help nudge ChatGPT to make more detailed and nuanced judgments for trickier cases where the classification is not immediately obvious. Finally, I apply the chain-of-thought technique to improve classifications by asking ChatGPT to first make a detailed assessment before its final classification. I feed all the Q&A pairs that remain after Steps 1 and 2 through this zero-shot prompt and extract the non-answer classifications from the completions.

### Step 4: Fine-tuning ChatGPT

The zero-shot ChatGPT approach works well, although it sometimes overestimates the probability of a non-answer. This is a challenge with zero-shot approaches as it can be hard to convey complex concept definitions and their distributional properties using only a short prompt. Fine-tuning methods can help with that, as they convey the instructions through a sample of examples rather than prompt instructions. So, to further improve the classifications coming out of step 3, I feed all the classifications through a ChatGPT (GPT 3.5) model that is fine-tuned on a training sample that I construct using GPT-4 and manual classification. As part of this fine-tuning step, I also classify four additional dimensions of non-answers with little additional costs. Classifying the additional dimensions helps to demonstrate the flexibility of GLLMs and provides additional data to improve our understanding of earnings call non-answers. An overview of the different non-answers dimensions is shown in Appendix A of the main paper.

I start by developing a zero-shot GPT-4 prompt to create a start for the training sample. The resulting prompt is shown in OA 2.4. The zero-shot prompt has a few notable design considerations. First, I manually identify common types of false positives by step 3 (such as statements about not pursuing company actions being flagged as non-answers) and tailor the GPT-4 prompt to specifically filter these out. Bringing in plenty of task-specific context generally helps improve performance with the biggest models like GPT-4, which can handle the

additional detail. Second, instead of a 0 / 1 classification, I require the model to identify the exact non-answer phrases. This is more challenging but, in my testing, increasing the complexity of the task can sometimes reduce outcome variability and improve performance. Afterward, I transform the matched sentences into a 0 / 1 variable, where no sentences receive a 0. Third, the definitions for each of the dimensions have a degree of ambiguity to them. To help communicate to the model what I am after I spell out not only the possible options but also additional context for each of the options. Finally, I ask the model to make five classifications through a single prompt. Doing so makes performance slightly harder to evaluate, however, in my testing it improves overall performance relative to creating a separate prompt for each classification. Including all the questions at once seems to help GPT-4 understand what a non-answer is and what is not.

After developing the prompt, I draw a random sample of 400 Q&A pairs that likely contain a non-answer (i.e., those remaining after the Column 5 approach in Table 1). The performance results in Table 3 of the main paper show that the GPT-4 zero-shot approach works well but has two downsides: it is not cost-efficient for large samples and it remains hard to communicate what exactly constitutes a non-answer. To help with that, I demonstrate a hybrid approach to fine-tuning a ChatGPT model on a training dataset created using zero-shot GPT-4. Specifically, I start by drawing another random sample of  $ \sim2{,}100 $ Q&A pairs and feed them through the zero-shot GPT-4 approach. The performance statistics in Table 3 show that GPT-4 achieves near-human performance for the four sub-dimensions, so I directly use those for the training data. The non-answer classification by GPT-4 can use improvement, so I manually go through all the training observations and improve the classification of non-answers with my own. I then use the improved training dataset and the OpenAI API to fine-tune a ChatGPT (GPT 3.5) model using a reduced form of the GPT-4 prompt, which is shown in OA 2.5. It is worth pointing out that the fine-tuning prompt only includes the question, the answer, and the JSON completion. We do not have to include the instructions as we communicate to the model what we want through our training data examples and not through prompt instructions. As shown in Table 3, the mean tokens per Q&A pair drop from 1,267 tokens for the zero-shot GPT-4 prompt to 324 tokens for the ChatGPT fine-tuned prompt. The lower token counts result in a substantial cost saving in addition to the already lower price of using a fine-tuned ChatGPT model versus a GPT-4 model.

#### OA 4 – Examples of classification differences between the GPT and Gow et al. methods

Below are fifteen random examples for each area of the Venn diagram in Figure 2. The Gow et al. (2021) regular expression matches are shown in bold. Comparing the error rates in the left versus right slice highlights the considerably lower non-answer error rate by the GPT method.

##### Left slice – The Gow et al. method marks it as a non-answer but the GPT method does not:

- So, not a lot of price increases relative to just supply and demand right now, really more about driving technology innovation to keep our price points higher, and reflect the value of going into those customers.

- And I think the idea is to try to not give anyone a heart attack in terms of a big change in our structure.

• It’s hard when we talk about the back half of the year.

- We need to execute this, it’s not, for us to get material revenue growth, I don’t have to deal with Metronic I just have to execute on the relationships that the company has already put in place.

- Looking at a conversion lift in the Non-Hotel category from the additional brand awareness, next to impossible for us to tell, in part because those components on TripAdvisor are growing so strong all by themselves.

- We are – when we do our monthly financial performance reviews, we are seeing that we’re coming in under cost for the quarter and that’s not too surprising given the activity and we have a lot of remote work.

- That -- I don't know that it was those orders specifically.

• I don't have that number off the top of my head.

- We just don't know we're looking at everything look, we've looking at our capital allocation, we're applying it in different things, we've got some club units that we think we can you know depending on if we can find a buyer for them, we may sell a couple of club units.

- There is no question of profits shattered out there and I’m not going to comment on the shatter but what I will tell you is we have created a very unique business with tremendous opportunities for growth as we watch consumer demand for snacks growing at a very healthy rate around the world, and we capitalize on our strong positions, especially in these emerging markets.

- We have new products or customers have changed circumstances such as consolidations, so we're managing a dynamic set of relationships, but fundamentally our duration, I don't know, the average number is maybe about 2.7 years or 2.8 years or so, and so that has been remarkably confident.

- So I remember, and I'm not going to name -- but I remember talking so many CEOs and their number one objective was, oh, I have to start being able to people text their orders into the store.

• I don't think we have that.

- So we're more in the mode of, as we're trying to play through, as I've referred to with the whack-a-mole analogy is, you get some buildup, because you might have built up your components to build an assembly or package of sorts and then you don't get a component.

- So we're not -- have any supply issues to doing that or supply chain issues.

##### Overlap area – Both methods mark the response as a non-answer:

- Now, you should not expect us to be given a volume.

- Yes. We haven't provided that, Tom. Perhaps we'll provide it in the next quarter or later on. But right now, we have not provided the range.

• We don't have specific granular views nor would we give those as part of the guidance.

• We're not disclosing at this time what indications we are going to pursue or exclude.

- Yeah, I don't know the very exact numbers, but a few quarters ago in our slide that we gave you a price chart which shows you the break down market intelligence cost by - customers and was roughly pretty evenly split between four categories.

• And so, we don't -- we're not going to give you guidance as to how we see it into the entire year,

- With regards to what the weather impact is going to be on the season, I will tell you about that on the November call, because I've never been able to figure it out how to predict it at this point.

- We haven't provided any guidance with respect to timeframe that profitability. And we are going to do that at this time, we may do that in the future but we are not providing guidance on that at this time.

• Well, there is never an easy answer to this, but I'll let Jeremy give it his best shot here.

- And as well as we hope that the economic stagnation that we see ourselves in, probably more non-U.S. than U.S., comes back to life, but it's hard to predict, we'll see.

• Well, I'm not going to speculate on 2015 at this point.

• To what extent, we don't forecast.

- Yes, on the last part of that, I don't know that we've 100% scheduled every maintenance event for next year and want to be nimble and on our toes, don't anticipate any changes.

• I honestly don't know.

- We can't tell by transaction data if we're seeing any, but I think the closest we could come is we've run a regression around the correlation between off-premise comp sales behavior and on-premise comp sales behavior.

#### Right slice – The GPT method marks it as a non-answer but the Gow et al. method does not:

- I would hesitate to get into forecasting specific items across the company, but you see the impact in the first quarter from volume and the extra costs related to unabsorbed fixed.

• They don't share individual guests' contact information.

• I don't think we have enough there to know, Bill.

- And we've got some testing to do and I really need you to let us get that testing done and come back and report on what we know and what we plan to do about it.

- But then the other piece is we just – we are at only eight weeks into the air. So, that will need to make a change in terms of overall guidance. We'll continue to evaluate guidance as we go into 2019.

• It is really early stages here on Vega.

• So I don't have -- it's a long story, I don't have a number for you.

- But on the door activation switch, we can't speak for the customer, but we hope they carry it over other platforms of course, but it is one award and we'll have to see what will happen.

- Obviously, we have to finalize this JV agreement. So -- because that's not final, we have not included anything in the guidance.

• Yes. I wish I had the crystal ball on that.

- Yeah. I don't think we're sharing detailed stats on engagement by messaging platform.

- It's very difficult at this point with the cycle and the level of volume that we're seeing to kind of outlook exactly when and where we'd feel that.

- And as a result, we're very hesitant to call when the visibility will improve there.

- And my comment to add to that is we don't have a specific number for you in terms of how that business across search, culture shaping and leadership consultants are going to breakdown.

• It's hard to quantify what, why and where.

### OA 5 - Using and fine-tuning a local GLLM

Local GLLMs can provide a more private, replicable, and cost-effective alternative to third-party APIs. In this section, I provide an overview of local fine-tuning methods as well as anecdotal observations of replicating the non-answer GPT method using local GLLMs.

### OA 5.1 - Local GLLM fine-tuning

Fine-tuning is an umbrella term to describe a set of methods to update the model weights of an LLM by means of a training sample. The fine-tuning methods differ on two main dimensions:

(1) The parts of the model weights that are subject to updating.

a. Full tuning is the original form of fine-tuning and allows all weights to be updated. This effectively continues the original training with a more specific training sample for your task. This is the most powerful but also the most computationally intensive.

b. Parameter Efficient Fine Tuning (PEFT) are methods that allow fine-tuning while keeping all or most of the original model weights unchanged (i.e., frozen). This makes fine-tuning significantly easier but can come at the cost of performance.

i. Partial or Freeze tuning are PEFT methods where most of the model weights are kept frozen and only the final model layers are allowed to update.

ii. Low-Rank Adaptation (LoRA) tuning keeps the full model weights frozen and instead trains an adapter to change the model behavior (Hu et al. 2021). Combining the original model with your trained adapter then creates your fine-tuned model. Adapters are smaller in parameter size relative to the original model and thus easier to train. QLoRA approaches combine LoRA with quantization techniques.

(2) The evaluation function used during fine-tuning to distinguish good from bad responses.

a. Standard fine-tuning procedures have the same evaluation function as the original training procedure, which is to try to predict the same token as the original text.

b. Reinforcement Learning from Human Feedback (RLHF) approaches use a different evaluation approach than the original training procedure. RLHF approaches evaluate the quality of a generation using a more sophisticated feedback mechanism. For example, ChatGPT is RLHF tuned by having human evaluators evaluate generations during various stages of the fine-tuning process, steering the model towards generations that are evaluated as higher quality by humans. Many RLHF approaches exist, notable mentions include Reward Modeling, Proximal Policy Optimization (PPO), and Direct Preference Optimization (DPO). RLHF tuning can yield better performance but is also much harder and more costly to implement.

For textual analysis tasks, I recommend first trying a standard full fine-tune of a smaller model, such as Phi-2 2.7b or Llama2 7b. For most tasks, this will be the easiest way to get good performance. If that is not feasible or does not work, I next recommend trying to fine-tune a larger model using a LoRA adapter. These adapters make it possible to fine-tune larger models although it can be harder to get good results out of them relative to full fine-tuning. Finally, RLHF techniques are generally unnecessary when fine-tuning a model for textual analysis tasks.

##### OA 5.2 – Non-answer replication using local GLLMs

As an experiment, I replicate parts of the non-answer task using local GLLMs. I start by replicating the zero-shot results in Table 1 using an A6000 GPU, the Llama2 7b and 13b chat models, and the ChatGPT prompt shown in Online Appendix 2.3. Manual inspection of the result shows that the Llama2 models struggle to follow the instructions out of the box. The models frequently return text that is not JSON or JSON that is unparseable. Around 16% (8%) of the 500 evaluations are unparseable with the 7b (13b) model. Furthermore, the remaining classifications are not good. For example, the 13b model marks 86% of the answers as containing a non-answer. However, there are a few important caveats to these results: detecting non-answers is an unusually hard task and I did not adapt the prompts to the Llama 2 models. Further prompt engineering would likely improve the results. The primary insight here is that zero-shot approaches using local GLLMs are generally more challenging to get working relative to zero-shot approaches with third-party models such as ChatGPT and GPT-4.

Fine-tuning is where local GLLMs tend to have the most potential. To demonstrate that, I next replicate the ChatGPT fine-tuning step in Table 3 by training a LoRA adapter for the Llama2 7b chat model using an RTX 4090. Fine-tuning the adapter took about an hour on the ~2,100 training observations. The resulting fine-tuned model yields results that are significantly better than the zero-shot experiments. The model strictly follows the instructions and produces valid JSON, which was not possible in the zero-shot tests. Untabulated results show that the fine-tuned Llama2 7b model yields an F1 score of 0.77 for the non-answers, 0.90 for the non-answer justification, 0.77 for the non-answer type, 0.69 for the question type, and 0.83 for the non-answer sentiment. Fine-tuning the Llama2 7b model with full fine-tuning on more powerful hardware would likely improve these results even further. Importantly, these results are getting close to those of the fine-tuned ChatGPT model, at 1/100 $ ^{th} $ the cost. It only costs around 0.04 to generate 1,000 predictions using the fine-tuned Llama2 7b model, versus 4.18 for the same 1,000 predictions using the fine-tuned ChatGPT model with the 2023 OpenAI API prices.

##### OA 6 – Additional analysis - question features and non-answers

As an additional analysis, I also replicate Table 2 of Gow et al. (2021) to study how question characteristics relate to the propensity of a non-answer. Following Gow et al. (2021), I regress each question characteristic separately on the non-answer outcome with earnings call fixed effects. To save space, the results of the independent regressions are shown below each other in Table OA.1 Panel B, columns 1 and 2. There is one notable difference between my measure and the Gow et al. (2021) measure. Specifically, Gow et al. (2021) find a positive correlation between negative question sentiment and the likelihood of a non-answer. In contrast, the more accurate GPT measure finds a negative correlation with both positive as well as negative question sentiment. In both cases the question sentiment is calculated using the Loughran & McDonald (2011) wordlists, the only difference is the non-answer classification. These new results show that managers are also less likely to provide a non-answer when an analyst asks a question with a strong negative sentiment, although to a lesser degree than a question with a strong positive sentiment.

Next, I also expand the analysis by correlating the same question features with the different types of non-answers. The results highlight that the question feature correlations are conditional on the type of non-answer. A few notable results. First, having a question with a strong positive sentiment does not impact the likelihood of managers giving a positive spin to their non-answer (-1.666, Column 4). A question with a strong negative sentiment, on the other hand, does significantly decrease the likelihood of the manager giving a positive spin (-24.240***, Column 4). Second, question complexity (i.e., Q - Fog index) generally predicts a higher likelihood of a non-answer. However, this is driven by non-answers with a qualitative alternative (0.196***, Column 6). Complete refusal and range or percentage non-answers instead are less likely for complex questions (-0.050***, Column 5 and -0.030**, Column 7). Finally, questions that ask about specific amounts, locations, or dates are generally more likely to receive a non-answer. However, these categories are significantly less likely to receive a complete refusal and more likely to receive a qualitative non-answer (-0.191***, -0.291***, -0.146*** in Column 5).

#### Table OA.1 – Question features and non-answers

<div style="text-align: center;"><div style="text-align: center;">Panel A: Descriptive statistics</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td><td style='text-align: center; word-wrap: break-word;'>(4)</td><td style='text-align: center; word-wrap: break-word;'>(5)</td><td style='text-align: center; word-wrap: break-word;'>(6)</td><td style='text-align: center; word-wrap: break-word;'>(7)</td><td style='text-align: center; word-wrap: break-word;'>(8)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Obs.</td><td style='text-align: center; word-wrap: break-word;'>Mean</td><td style='text-align: center; word-wrap: break-word;'>Std. Dev.</td><td style='text-align: center; word-wrap: break-word;'>P5</td><td style='text-align: center; word-wrap: break-word;'>P25</td><td style='text-align: center; word-wrap: break-word;'>P50</td><td style='text-align: center; word-wrap: break-word;'>P75</td><td style='text-align: center; word-wrap: break-word;'>P95</td></tr><tr><td colspan="9">Question features</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Positive tone</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>0.011</td><td style='text-align: center; word-wrap: break-word;'>0.02</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.02</td><td style='text-align: center; word-wrap: break-word;'>0.04</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Negative tone</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>0.011</td><td style='text-align: center; word-wrap: break-word;'>0.02</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.02</td><td style='text-align: center; word-wrap: break-word;'>0.04</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Uncertainty</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>0.014</td><td style='text-align: center; word-wrap: break-word;'>0.02</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.01</td><td style='text-align: center; word-wrap: break-word;'>0.02</td><td style='text-align: center; word-wrap: break-word;'>0.05</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Fog index</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>10.23</td><td style='text-align: center; word-wrap: break-word;'>4.55</td><td style='text-align: center; word-wrap: break-word;'>4.33</td><td style='text-align: center; word-wrap: break-word;'>7.50</td><td style='text-align: center; word-wrap: break-word;'>9.61</td><td style='text-align: center; word-wrap: break-word;'>12.14</td><td style='text-align: center; word-wrap: break-word;'>18.07</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Contains numbers</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>0.394</td><td style='text-align: center; word-wrap: break-word;'>0.49</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>1.00</td><td style='text-align: center; word-wrap: break-word;'>1.00</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Contains money or percent</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>0.160</td><td style='text-align: center; word-wrap: break-word;'>0.37</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>1.00</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Contains location</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>0.136</td><td style='text-align: center; word-wrap: break-word;'>0.34</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>1.00</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Contains date or time</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>0.544</td><td style='text-align: center; word-wrap: break-word;'>0.50</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>0.00</td><td style='text-align: center; word-wrap: break-word;'>1.00</td><td style='text-align: center; word-wrap: break-word;'>1.00</td><td style='text-align: center; word-wrap: break-word;'>1.00</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">Table OA.1 (cont.) – Question features and non-answers</div> </div>


<div style="text-align: center;"><div style="text-align: center;">Panel B: Determinant results</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>(1)</td><td style='text-align: center; word-wrap: break-word;'>(2)</td><td style='text-align: center; word-wrap: break-word;'>(3)</td><td style='text-align: center; word-wrap: break-word;'>(4)</td><td style='text-align: center; word-wrap: break-word;'>(5)</td><td style='text-align: center; word-wrap: break-word;'>(6)</td><td style='text-align: center; word-wrap: break-word;'>(7)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Non-answer GPT approach</td><td style='text-align: center; word-wrap: break-word;'>Non-answer Gow et al.</td><td style='text-align: center; word-wrap: break-word;'>Non-answer Can&#x27;t give</td><td style='text-align: center; word-wrap: break-word;'>Non-answer Positive</td><td style='text-align: center; word-wrap: break-word;'>Non-answer Complete refusal</td><td style='text-align: center; word-wrap: break-word;'>Non-answer Qualitative</td><td style='text-align: center; word-wrap: break-word;'>Non-answer Range or Perc.</td></tr><tr><td rowspan="2">Q - Positive sentiment</td><td style='text-align: center; word-wrap: break-word;'>$ -48.598^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -34.180^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -14.813^{***} $</td><td style='text-align: center; word-wrap: break-word;'>-1.666</td><td style='text-align: center; word-wrap: break-word;'>$ -14.421^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -22.937^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -11.240^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(3.019)</td><td style='text-align: center; word-wrap: break-word;'>(4.062)</td><td style='text-align: center; word-wrap: break-word;'>(0.641)</td><td style='text-align: center; word-wrap: break-word;'>(3.764)</td><td style='text-align: center; word-wrap: break-word;'>(0.844)</td><td style='text-align: center; word-wrap: break-word;'>(3.700)</td><td style='text-align: center; word-wrap: break-word;'>(0.432)</td></tr><tr><td rowspan="2">Q - Negative sentiment</td><td style='text-align: center; word-wrap: break-word;'>$ -14.763^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 6.892^{**} $</td><td style='text-align: center; word-wrap: break-word;'>-3.505*</td><td style='text-align: center; word-wrap: break-word;'>$ -24.240^{***} $</td><td style='text-align: center; word-wrap: break-word;'>-1.209</td><td style='text-align: center; word-wrap: break-word;'>$ -13.947^{***} $</td><td style='text-align: center; word-wrap: break-word;'>0.394</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(3.020)</td><td style='text-align: center; word-wrap: break-word;'>(2.788)</td><td style='text-align: center; word-wrap: break-word;'>(1.761)</td><td style='text-align: center; word-wrap: break-word;'>(1.455)</td><td style='text-align: center; word-wrap: break-word;'>(1.147)</td><td style='text-align: center; word-wrap: break-word;'>(1.680)</td><td style='text-align: center; word-wrap: break-word;'>(0.628)</td></tr><tr><td rowspan="2">Q - Uncertainty</td><td style='text-align: center; word-wrap: break-word;'>$ 70.868^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 50.331^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 27.300^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 42.506^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 10.081^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 50.329^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 10.458^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(3.754)</td><td style='text-align: center; word-wrap: break-word;'>(3.376)</td><td style='text-align: center; word-wrap: break-word;'>(0.911)</td><td style='text-align: center; word-wrap: break-word;'>(3.075)</td><td style='text-align: center; word-wrap: break-word;'>(1.299)</td><td style='text-align: center; word-wrap: break-word;'>(3.391)</td><td style='text-align: center; word-wrap: break-word;'>(0.870)</td></tr><tr><td rowspan="2">Q - Fog index</td><td style='text-align: center; word-wrap: break-word;'>$ 0.116^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.226^{***} $</td><td style='text-align: center; word-wrap: break-word;'>0.010*</td><td style='text-align: center; word-wrap: break-word;'>$ 0.170^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.050^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.196^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.030^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.013)</td><td style='text-align: center; word-wrap: break-word;'>(0.020)</td><td style='text-align: center; word-wrap: break-word;'>(0.005)</td><td style='text-align: center; word-wrap: break-word;'>(0.007)</td><td style='text-align: center; word-wrap: break-word;'>(0.006)</td><td style='text-align: center; word-wrap: break-word;'>(0.010)</td><td style='text-align: center; word-wrap: break-word;'>(0.002)</td></tr><tr><td rowspan="2">Q - Contains numbers</td><td style='text-align: center; word-wrap: break-word;'>$ 3.262^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 2.302^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.770^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 2.149^{***} $</td><td style='text-align: center; word-wrap: break-word;'>0.008</td><td style='text-align: center; word-wrap: break-word;'>$ 2.302^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.952^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.269)</td><td style='text-align: center; word-wrap: break-word;'>(0.191)</td><td style='text-align: center; word-wrap: break-word;'>(0.098)</td><td style='text-align: center; word-wrap: break-word;'>(0.203)</td><td style='text-align: center; word-wrap: break-word;'>(0.036)</td><td style='text-align: center; word-wrap: break-word;'>(0.212)</td><td style='text-align: center; word-wrap: break-word;'>(0.045)</td></tr><tr><td rowspan="2">Q - Contains money</td><td style='text-align: center; word-wrap: break-word;'>$ 1.550^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 1.347^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.487^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.981^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.191^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.724^{**} $</td><td style='text-align: center; word-wrap: break-word;'>$ 1.017^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.290)</td><td style='text-align: center; word-wrap: break-word;'>(0.159)</td><td style='text-align: center; word-wrap: break-word;'>(0.102)</td><td style='text-align: center; word-wrap: break-word;'>(0.230)</td><td style='text-align: center; word-wrap: break-word;'>(0.056)</td><td style='text-align: center; word-wrap: break-word;'>(0.235)</td><td style='text-align: center; word-wrap: break-word;'>(0.052)</td></tr><tr><td rowspan="2">Q - Location</td><td style='text-align: center; word-wrap: break-word;'>$ 0.745^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 1.074^{***} $</td><td style='text-align: center; word-wrap: break-word;'>-0.034</td><td style='text-align: center; word-wrap: break-word;'>$ 0.867^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.291^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 1.127^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.091^{**} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.159)</td><td style='text-align: center; word-wrap: break-word;'>(0.096)</td><td style='text-align: center; word-wrap: break-word;'>(0.046)</td><td style='text-align: center; word-wrap: break-word;'>(0.091)</td><td style='text-align: center; word-wrap: break-word;'>(0.060)</td><td style='text-align: center; word-wrap: break-word;'>(0.111)</td><td style='text-align: center; word-wrap: break-word;'>(0.038)</td></tr><tr><td rowspan="2">Q - Date or time</td><td style='text-align: center; word-wrap: break-word;'>$ 3.299^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 2.725^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.999^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 2.455^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ -0.146^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 2.703^{***} $</td><td style='text-align: center; word-wrap: break-word;'>$ 0.742^{***} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(0.163)</td><td style='text-align: center; word-wrap: break-word;'>(0.174)</td><td style='text-align: center; word-wrap: break-word;'>(0.063)</td><td style='text-align: center; word-wrap: break-word;'>(0.148)</td><td style='text-align: center; word-wrap: break-word;'>(0.025)</td><td style='text-align: center; word-wrap: break-word;'>(0.130)</td><td style='text-align: center; word-wrap: break-word;'>(0.038)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Call FE</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td><td style='text-align: center; word-wrap: break-word;'>Yes</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Multivariate</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>No</td><td style='text-align: center; word-wrap: break-word;'>No</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>N</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td><td style='text-align: center; word-wrap: break-word;'>1,152,473</td></tr></table>

##### Additional references

Hu, Edward J., Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, and Weizhu Chen. 2021. "LoRA: Low-Rank Adaptation of Large Language Models." arXiv.

Liu, Nelson F., Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, and Percy Liang. 2023. "Lost in the Middle: How Language Models Use Long Contexts." arXiv.

Loughran, Tim, and Bill Mcdonald. 2011. “When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks.” The Journal of Finance 66 (1): 35–65.

