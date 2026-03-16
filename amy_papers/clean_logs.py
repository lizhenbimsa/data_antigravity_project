import os

def clean_logs(folder):
    for root, _, files in os.walk(folder):
        for f in files:
            if f.endswith('.do'):
                p = os.path.join(root, f)
                with open(p, 'r', encoding='utf-8') as fr:
                    lines = fr.readlines()
                with open(p, 'w', encoding='utf-8') as fw:
                    fw.writelines([l for l in lines if 'log using' not in l and 'log close' not in l])

clean_logs('f:/WiseSearch/data_antigravity_project/amy_papers/04_stata_templates')
clean_logs('f:/WiseSearch/data_antigravity_project/amy_papers/paper_50334/v1/code')
