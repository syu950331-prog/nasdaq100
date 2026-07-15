import json
import pandas as pd
from typing import Dict, Any, List

def calculate_data_quality(
    df: pd.DataFrame,
    official_sources: List[str],
    secondary_sources: List[str],
    failed_tickers: List[str],
    source_warnings: List[str]
) -> Dict[str, Any]:
    """
    Calculate data quality metrics from the master DataFrame.
    """
    total_count = len(df)
    
    # Constituent counts
    constituent_count = int(df["is_constituent"].sum())
    non_constituent_count = total_count - constituent_count
    
    # Matches
    # SEC is matched if CIK is not null/empty and latest_sec_filing_type is not "unknown"
    sec_matched = int((df["latest_sec_filing_type"] != "unknown").sum())
    
    # Market data matched if market cap is present and last price is present
    market_matched = int((df["market_cap"].notna() & df["last_price"].notna()).sum())
    
    # Missings
    missing_sector = int((df["sector"].isna() | (df["sector"] == "")).sum())
    missing_mcap = int(df["market_cap"].isna().sum())
    
    # Unknown eligibility
    unknown_eligibility = int((df["eligibility_status"] == "unknown").sum())
    
    # Collect timestamp from the first row or current time
    collected_at = ""
    if len(df) > 0:
        collected_at = df.iloc[0].get("collected_at", "")
        
    report = {
        "collected_at": collected_at,
        "official_sources_used": official_sources,
        "secondary_sources_used": secondary_sources,
        "total_universe_count": total_count,
        "constituent_count": constituent_count,
        "non_constituent_count": non_constituent_count,
        "sec_matched_count": sec_matched,
        "market_data_matched_count": market_matched,
        "missing_sector_count": missing_sector,
        "missing_market_cap_count": missing_mcap,
        "unknown_eligibility_count": unknown_eligibility,
        "failed_tickers": failed_tickers,
        "source_warnings": source_warnings
    }
    
    return report

def save_data_quality_report(report: Dict[str, Any], filepath: str) -> None:
    """Save the data quality report to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
