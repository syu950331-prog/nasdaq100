import pandas as pd
import datetime
from typing import List, Dict, Any
from src.models import ConstituentData, ScreenerStockData, MarketData, SECEntityData

def determine_is_financial(sector: str) -> str:
    """
    Classify whether a sector is financial.
    Returns "True", "False", or "unknown".
    """
    if not sector:
        return "unknown"
    
    sector_clean = sector.strip().lower()
    
    # Financial indicators
    financial_terms = ["financials", "financial services", "financial", "banks", "diversified financials", "insurance"]
    if any(term in sector_clean for term in financial_terms):
        return "True"
        
    return "False"

def normalize_universe(
    constituents: List[ConstituentData],
    universe: List[ScreenerStockData],
    market_data: Dict[str, MarketData],
    sec_data: Dict[str, SECEntityData],
    constituents_source: str,
    collected_at: str
) -> pd.DataFrame:
    """
    Merge and normalize all raw data sources into a single master DataFrame.
    """
    # Create maps for constituents
    constituent_map = {c["ticker"].upper().strip(): c for c in constituents}
    
    # We want a unified set of tickers. We combine the screener universe and any constituents.
    # Typically, the universe has ~250 large caps. Some constituents might not be in the top 250 screener.
    # So we union the tickers from screener and constituents to be comprehensive.
    all_tickers = set(u["ticker"].upper().strip() for u in universe) | set(constituent_map.keys())
    
    # Build maps for screener universe
    universe_map = {u["ticker"].upper().strip(): u for u in universe}
    
    rows = []
    for ticker in all_tickers:
        ticker_upper = ticker.upper().strip()
        
        # Get base info from screener or constituent list
        u_info = universe_map.get(ticker_upper)
        c_info = constituent_map.get(ticker_upper)
        
        # Company name resolution
        company_name = ""
        if u_info:
            company_name = u_info["company_name"]
        elif c_info:
            company_name = c_info["company_name"]
            
        exchange = "NASDAQ"  # All tickers in Nasdaq-100 and Nasdaq screener are Nasdaq listed
        
        is_constituent = ticker_upper in constituent_map
        
        # Get market data (yfinance)
        m_info = market_data.get(ticker_upper)
        
        # Get SEC data
        s_info = sec_data.get(ticker_upper)
        
        # Sector resolution (prefer constituent sector, then screener, then yfinance)
        sector = ""
        if c_info and c_info.get("sector"):
            sector = c_info["sector"]
        elif u_info and u_info.get("sector"):
            sector = u_info["sector"]
        elif m_info and m_info.get("sector"):
            sector = m_info.get("sector", "")
            
        # Is financial classification
        is_financial = determine_is_financial(sector)
        
        # Market Cap and price resolution
        # Prefer screener data (primary source) but fallback to yfinance
        last_price = None
        market_cap = None
        market_cap_source = "unknown"
        shares_outstanding = None
        
        # Try primary (Nasdaq screener)
        if u_info:
            last_price = u_info["last_price"]
            market_cap = u_info["market_cap"]
            if market_cap:
                market_cap_source = "provided"
                
        # Try secondary yfinance if missing
        if market_cap is None and m_info:
            market_cap = m_info.get("market_cap")
            if market_cap:
                market_cap_source = m_info.get("market_cap_source", "provided")
            if last_price is None:
                last_price = m_info.get("last_price")
                
        # Try to resolve shares outstanding from yfinance, SEC, or calculate
        if m_info and m_info.get("shares_outstanding"):
            shares_outstanding = m_info["shares_outstanding"]
        elif s_info and s_info.get("shares_outstanding"):
            shares_outstanding = s_info["shares_outstanding"]
            
        # If shares outstanding is available but market cap is not, calculate it
        if market_cap is None and last_price is not None and shares_outstanding is not None:
            market_cap = last_price * shares_outstanding
            market_cap_source = "calculated"
            
        # Or calculate shares if market cap and price are available
        if shares_outstanding is None and market_cap is not None and last_price:
            shares_outstanding = int(market_cap / last_price)
            
        # Filing data
        latest_sec_filing_type = "unknown"
        latest_sec_filing_date = "unknown"
        sec_data_date = "unknown"
        if s_info:
            latest_sec_filing_type = s_info.get("latest_sec_filing_type", "unknown")
            latest_sec_filing_date = s_info.get("latest_sec_filing_date", "unknown")
            sec_data_date = s_info.get("sec_data_date", "unknown")
            
        market_data_date = "unknown"
        if u_info:
            market_data_date = u_info.get("as_of_date", "unknown")
        elif m_info:
            market_data_date = m_info.get("price_date", "unknown")
            
        rows.append({
            "ticker": ticker_upper,
            "company_name": company_name,
            "exchange": exchange,
            "sector": sector,
            "is_financial": is_financial,
            "is_constituent": is_constituent,
            "market_cap": market_cap,
            "market_cap_source": market_cap_source,
            "last_price": last_price,
            "shares_outstanding": shares_outstanding,
            "latest_sec_filing_type": latest_sec_filing_type,
            "latest_sec_filing_date": latest_sec_filing_date,
            "market_data_date": market_data_date,
            "sec_data_date": sec_data_date,
            "eligibility_status": "unknown",  # To be filled by eligibility module
            "exclusion_reason": "",           # To be filled by eligibility module
            "data_source": f"Nasdaq({constituents_source})/SEC/yfinance",
            "collected_at": collected_at
        })
        
    df = pd.DataFrame(rows)
    return df
