from typing import TypedDict, Optional, List, Dict

class ConstituentData(TypedDict):
    ticker: str
    company_name: str
    is_constituent: bool
    sector: str
    source_url: str
    collected_at: str

class ScreenerStockData(TypedDict):
    ticker: str
    company_name: str
    exchange: str
    sector: str
    industry: str
    market_cap: Optional[float]
    last_price: Optional[float]
    source_url: str
    as_of_date: str

class MarketData(TypedDict):
    ticker: str
    last_price: Optional[float]
    market_cap: Optional[float]
    shares_outstanding: Optional[int]
    price_date: str
    source_type: str  # e.g., "primary_market_data" or "secondary_market_data"
    market_cap_source: str  # "provided" or "calculated" or "unknown"
    sector: Optional[str]
    industry: Optional[str]

class SECEntityData(TypedDict):
    ticker: str
    cik: str
    entity_name: str
    latest_sec_filing_type: str  # 10-K, 10-Q, etc.
    latest_sec_filing_date: str  # YYYY-MM-DD
    shares_outstanding: Optional[int]
    sec_data_date: str
    source_url: str
