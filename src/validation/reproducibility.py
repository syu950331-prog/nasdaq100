import hashlib
import os
import pandas as pd
from typing import List

def calculate_snapshot_hash(file_paths: List[str]) -> str:
    """
    Calculate a SHA-256 hash of the contents of a list of files.
    This serves as the unique fingerprint (snapshot_hash) for the raw input data.
    """
    hasher = hashlib.sha256()
    for path in sorted(file_paths):
        if os.path.exists(path):
            with open(path, "rb") as f:
                # Read in chunks to be memory efficient
                while chunk := f.read(8192):
                    hasher.update(chunk)
        else:
            hasher.update(b"missing")
    return hasher.hexdigest()

def verify_reproducibility(run1_df: pd.DataFrame, run2_df: pd.DataFrame) -> bool:
    """
    Verify if the two DataFrames are identical in terms of tickers and their ranks.
    """
    if len(run1_df) != len(run2_df):
        return False
        
    if "ticker" not in run1_df.columns or "ticker" not in run2_df.columns:
        return False
        
    tickers1 = run1_df["ticker"].tolist()
    tickers2 = run2_df["ticker"].tolist()
    
    return tickers1 == tickers2
