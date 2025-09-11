import pandas as pd

def load_wbs_csv(path: str) -> list[dict]:
    return pd.read_csv(path).to_dict(orient="records")

def load_avance_csv(path: str) -> list[dict]:
    return pd.read_csv(path).to_dict(orient="records")

def save_results_parquet(df, path: str):
    df.to_parquet(path, index=False)
