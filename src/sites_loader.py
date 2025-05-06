import pandas as pd

def load_approved_sites(filepath='input/approved_sites.xlsx'):
    df = pd.read_excel(filepath)
    # Filter to enabled sites only
    df_enabled = df[df['Enabled'] == True]

    # Return a list of domains (like "grainger.com")
    return df_enabled['Domain'].dropna().tolist()
