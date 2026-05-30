/*==============================================================================
  文件: 02_label_dict_bert.do
  目的: 为词典法和BERT情感分析指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 3. 词典法情感分析指标 (阶段22: 词典法情感分析)
* ============================================================================

* 3.1 五本中文金融情感词典 - 全文轨道
label variable jiang_2021_tone_full "江2021词典情感得分(全文)"
label variable jiang_2021_tone_sum_full "江2021词典情感总和(全文)"
label variable jiang_2021_tone_std_full "江2021词典情感标准差(全文)"

label variable yao_2021_tone_full "姚2021词典情感得分(全文)"
label variable yao_2021_tone_sum_full "姚2021词典情感总和(全文)"
label variable yao_2021_tone_std_full "姚2021词典情感标准差(全文)"

label variable bian_2021_tone_full "卞2021词典情感得分(全文)"
label variable bian_2021_tone_sum_full "卞2021词典情感总和(全文)"
label variable bian_2021_tone_std_full "卞2021词典情感标准差(全文)"

label variable du_2022_tone_full "杜2022词典情感得分(全文)"
label variable du_2022_tone_sum_full "杜2022词典情感总和(全文)"
label variable du_2022_tone_std_full "杜2022词典情感标准差(全文)"

label variable you_2018_tone_full "尤2018词典情感得分(全文)"
label variable you_2018_tone_sum_full "尤2018词典情感总和(全文)"
label variable you_2018_tone_std_full "尤2018词典情感标准差(全文)"

* 3.2 IDF加权词典情感 (Gentzkow, Kelly & Taddy 2019, JEL)
label variable jiang_2021_idf_tone_full "江2021词典IDF情感(全文)"
label variable jiang_2021_idf_tone_sum_full "江2021词典IDF情感总和(全文)"
label variable jiang_2021_idf_tone_std_full "江2021词典IDF情感标准差(全文)"

label variable yao_2021_idf_tone_full "姚2021词典IDF情感(全文)"
label variable bian_2021_idf_tone_full "卞2021词典IDF情感(全文)"
label variable du_2022_idf_tone_full "杜2022词典IDF情感(全文)"
label variable you_2018_idf_tone_full "尤2018词典IDF情感(全文)"

* ============================================================================
* 4. BERT模型情感分析指标 (阶段23: BERT模型情感分析)
* ============================================================================

* 4.1 FinBERT-CN (三分类)
label variable finbert_cn_pos_full "FinBERT-CN正面概率(全文)"
label variable finbert_cn_pos_sum_full "FinBERT-CN正面概率总和(全文)"
label variable finbert_cn_neg_full "FinBERT-CN负面概率(全文)"
label variable finbert_cn_neg_sum_full "FinBERT-CN负面概率总和(全文)"
label variable finbert_cn_neu_full "FinBERT-CN中性概率(全文)"
label variable finbert_cn_neu_sum_full "FinBERT-CN中性概率总和(全文)"
label variable finbert_cn_pos_std_full "FinBERT-CN正面概率标准差(全文)"

* 4.2 FinSent-ZH (三分类)
label variable fin_sent_zh_pos_full "FinSent-ZH正面概率(全文)"
label variable fin_sent_zh_pos_sum_full "FinSent-ZH正面概率总和(全文)"
label variable fin_sent_zh_neg_full "FinSent-ZH负面概率(全文)"
label variable fin_sent_zh_neg_sum_full "FinSent-ZH负面概率总和(全文)"
label variable fin_sent_zh_neu_full "FinSent-ZH中性概率(全文)"
label variable fin_sent_zh_neu_sum_full "FinSent-ZH中性概率总和(全文)"

