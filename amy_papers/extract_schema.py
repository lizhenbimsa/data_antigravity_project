import pandas as pd

try:
    df = pd.read_stata('data/data.dta', iterator=True)
    labels = df.variable_labels()
    
    # Read just a small chunk to get dtypes without loading everything into memory
    df_chunk = df.read(5)
    types = df_chunk.dtypes
    
    with open('data_schema.txt', 'w', encoding='utf-8') as f:
        for col in labels.keys():
            t = types.get(col, "Unknown")
            f.write(f"Variable: {col} | Label: {labels.get(col, '')} | Type: {t}\n")
    print("Successfully extracted DTA schema.")
except Exception as e:
    print("Error:", e)
