import re

with open('f:\\WiseSearch\\data_antigravity_project\\news_process\\run_pipeline_function.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Remove stages 00, 11, 12, 14, 15
code = re.sub(r'stages\.append\(\(\"00_preprocessing\.py.*?\"\)\)', '', code, flags=re.DOTALL)
code = re.sub(r'stages\.extend\(\[.*?15_article_policy_alignment\.py.*?\]\)', '', code, flags=re.DOTALL)

with open('f:\\WiseSearch\\data_antigravity_project\\news_process\\run_pipeline_function_from_21.py', 'w', encoding='utf-8') as f:
    f.write(code)
