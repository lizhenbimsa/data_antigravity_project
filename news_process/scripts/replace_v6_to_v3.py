import os
import glob

replacements = {
    # model names
    "gpt-5.4-nano": "gpt-5.4-nano",
    "gemini-3.1-flash-lite-preview": "gemini-3.1-flash-lite-preview",
    "deepseek-v4-flash": "deepseek-v4-flash",
    
    # short names
    "gpt54nano": "gpt54nano",
    "gemini31111": "gemini311111",
    "deepseekv4": "deepseekv4",
    
    # documentation
    "v3 锁定": "v3 锁定",
    "v3 LLM 模型列表": "v3 LLM 模型列表",
    "v3:": "v3:",
    "OpenAI + Google + DeepSeek": "OpenAI + Google + DeepSeek",
    "OpenAI + Google + DeepSeek": "OpenAI + Google + DeepSeek",
    "GPT-5.4 Nano (OpenAI via yunwu)": "GPT-5.4 Nano (OpenAI via yunwu)",
    "Gemini 3.1 Flash Lite Preview (Google via yunwu)": "Gemini 3.1 Flash Lite Preview (Google via yunwu)",
    "DeepSeek V4 Flash (DeepSeek via yunwu)": "DeepSeek V4 Flash (DeepSeek via yunwu)",
}

files_to_check = glob.glob('f:/WiseSearch/data_antigravity_project/news_process/**/*.py', recursive=True) + \
                 glob.glob('f:/WiseSearch/data_antigravity_project/news_process/**/*.yaml', recursive=True)

for file in files_to_check:
    if "data\\processed" in file or "data/processed" in file: continue
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        new_content = content
        for k, v in replacements.items():
            new_content = new_content.replace(k, v)
            
        if new_content != content:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {file}")
    except Exception as e:
        print(f"Skipping {file}: {e}")
