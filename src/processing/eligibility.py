import pandas as pd
import numpy as np
from typing import Tuple

def evaluate_stock_eligibility(row: pd.Series) -> Tuple[str, str]:
    """
    Evaluate eligibility of a single stock for Nasdaq-100 inclusion watch.
    Returns (eligibility_status, exclusion_reason).
    """
    ticker = row.get("ticker", "")
    
    # 1. Nasdaq 상장 기업 확인
    exchange = str(row.get("exchange", "")).strip().upper()
    if exchange != "NASDAQ":
        return "ineligible", "Not listed on NASDAQ"
        
    # 2. 현재 Nasdaq-100 구성 종목 여부
    is_constituent = row.get("is_constituent")
    if is_constituent:
        return "ineligible", "Already a constituent of Nasdaq-100"
        
    # 3. 금융업종 판정
    is_financial = str(row.get("is_financial", "")).strip()
    if is_financial == "True":
        return "ineligible", "Belongs to Financial sector"
    elif is_financial == "unknown":
        return "unknown", "Sector classification unknown"
        
    # 4. market_cap 및 가격 데이터 존재 여부
    market_cap = row.get("market_cap")
    last_price = row.get("last_price")
    
    if pd.isna(market_cap) or market_cap is None or market_cap <= 0:
        return "unknown", "Market capitalization data missing"
        
    if pd.isna(last_price) or last_price is None or last_price <= 0:
        return "unknown", "Transaction price data missing"
        
    return "eligible", ""

def apply_eligibility(df: pd.DataFrame) -> pd.DataFrame:
    """
    Iterate over the DataFrame and apply the eligibility evaluations.
    Updates 'eligibility_status' and 'exclusion_reason' columns.
    """
    df = df.copy()
    
    statuses = []
    reasons = []
    
    for idx, row in df.iterrows():
        status, reason = evaluate_stock_eligibility(row)
        statuses.append(status)
        reasons.append(reason)
        
    df["eligibility_status"] = statuses
    df["exclusion_reason"] = reasons
    
    return df
