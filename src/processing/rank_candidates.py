import pandas as pd

def generate_inclusion_watch_top10(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select eligible non-constituents, sort by market_cap descending, 
    and return the top 10 with inclusion watch metadata.
    """
    # Filter for eligible stocks
    eligible_df = df[df["eligibility_status"] == "eligible"].copy()
    
    # Sort by market cap descending
    eligible_df = eligible_df.sort_values(by="market_cap", ascending=False)
    
    # Take top 10
    top10 = eligible_df.head(10).copy()
    
    # Add rank
    top10["watch_rank"] = range(1, len(top10) + 1)
    
    # Add static metadata fields
    top10["rationale"] = "Nasdaq 상장 비금융 비구성 기업 중 공개 데이터 기준 시가총액 상위권"
    top10["limitation"] = "공식 Nasdaq 내부 순위 및 최종 재량은 반영되지 않음"
    
    # Select and order required columns
    columns = [
        "watch_rank", "ticker", "company_name", "market_cap", 
        "market_cap_source", "sector", "eligibility_status", 
        "market_data_date", "rationale", "limitation"
    ]
    
    # Ensure all columns exist, if not create empty
    for col in columns:
        if col not in top10.columns:
            top10[col] = None
            
    return top10[columns]

def generate_exclusion_watch_top10(df: pd.DataFrame) -> pd.DataFrame:
    """
    Select current constituents, sort by market_cap ascending,
    and return the top 10 with exclusion watch metadata.
    """
    # Filter for constituents with valid market cap
    const_df = df[df["is_constituent"] == True].copy()
    const_df = const_df.dropna(subset=["market_cap"])
    const_df = const_df[const_df["market_cap"] > 0]
    
    # Sort by market cap ascending
    const_df = const_df.sort_values(by="market_cap", ascending=True)
    
    # Take top 10
    top10 = const_df.head(10).copy()
    
    # Add rank
    top10["watch_rank"] = range(1, len(top10) + 1)
    
    # Add static metadata fields
    top10["rationale"] = "현재 구성 종목 중 공개 데이터 기준 시가총액 하위권"
    top10["limitation"] = "공식 Nasdaq 내부 순위 및 최종 재량은 반영되지 않음"
    
    # Select and order required columns
    columns = [
        "watch_rank", "ticker", "company_name", "market_cap", 
        "sector", "market_data_date", "rationale", "limitation"
    ]
    
    # Ensure all columns exist, if not create empty
    for col in columns:
        if col not in top10.columns:
            top10[col] = None
            
    return top10[columns]
