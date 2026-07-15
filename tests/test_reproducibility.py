import pandas as pd
from src.processing.normalize import normalize_universe
from src.processing.eligibility import apply_eligibility
from src.processing.rank_candidates import generate_inclusion_watch_top10, generate_exclusion_watch_top10
from src.validation.reproducibility import verify_reproducibility

def test_pipeline_reproducibility():
    # Setup simple mock raw data
    constituents = [
        {"ticker": "AAPL", "company_name": "Apple Inc.", "is_constituent": True, "sector": "Technology", "source_url": "official", "collected_at": "2026-07-15T00:00:00Z"},
        {"ticker": "MSFT", "company_name": "Microsoft Corp.", "is_constituent": True, "sector": "Technology", "source_url": "official", "collected_at": "2026-07-15T00:00:00Z"},
        {"ticker": "AMZN", "company_name": "Amazon.com Inc.", "is_constituent": True, "sector": "Consumer Cyclical", "source_url": "official", "collected_at": "2026-07-15T00:00:00Z"}
    ]
    
    universe = [
        {"ticker": "AAPL", "company_name": "Apple Inc.", "exchange": "NASDAQ", "sector": "Technology", "industry": "Consumer Electronics", "market_cap": 3000000000000.0, "last_price": 180.0, "source_url": "official", "as_of_date": "2026-07-15"},
        {"ticker": "MSFT", "company_name": "Microsoft Corp.", "exchange": "NASDAQ", "sector": "Technology", "industry": "Software", "market_cap": 3100000000000.0, "last_price": 420.0, "source_url": "official", "as_of_date": "2026-07-15"},
        {"ticker": "AMZN", "company_name": "Amazon.com Inc.", "exchange": "NASDAQ", "sector": "Consumer Cyclical", "industry": "E-Commerce", "market_cap": 1800000000000.0, "last_price": 175.0, "source_url": "official", "as_of_date": "2026-07-15"},
        {"ticker": "NFLX", "company_name": "Netflix Inc.", "exchange": "NASDAQ", "sector": "Communication Services", "industry": "Entertainment", "market_cap": 250000000000.0, "last_price": 580.0, "source_url": "official", "as_of_date": "2026-07-15"},
        {"ticker": "JPM", "company_name": "JPMorgan Chase & Co.", "exchange": "NASDAQ", "sector": "Financial Services", "industry": "Banks", "market_cap": 500000000000.0, "last_price": 170.0, "source_url": "official", "as_of_date": "2026-07-15"}
    ]
    
    market_data = {
        "AAPL": {"ticker": "AAPL", "last_price": 180.0, "market_cap": 3000000000000.0, "shares_outstanding": 16600000000, "price_date": "2026-07-15", "source_type": "secondary", "market_cap_source": "provided"},
        "MSFT": {"ticker": "MSFT", "last_price": 420.0, "market_cap": 3100000000000.0, "shares_outstanding": 7430000000, "price_date": "2026-07-15", "source_type": "secondary", "market_cap_source": "provided"},
        "AMZN": {"ticker": "AMZN", "last_price": 175.0, "market_cap": 1800000000000.0, "shares_outstanding": 10400000000, "price_date": "2026-07-15", "source_type": "secondary", "market_cap_source": "provided"},
        "NFLX": {"ticker": "NFLX", "last_price": 580.0, "market_cap": 250000000000.0, "shares_outstanding": 431000000, "price_date": "2026-07-15", "source_type": "secondary", "market_cap_source": "provided"},
        "JPM": {"ticker": "JPM", "last_price": 170.0, "market_cap": 500000000000.0, "shares_outstanding": 2900000000, "price_date": "2026-07-15", "source_type": "secondary", "market_cap_source": "provided"}
    }
    
    sec_data = {
        "AAPL": {"ticker": "AAPL", "cik": "320193", "entity_name": "Apple Inc.", "latest_sec_filing_type": "10-Q", "latest_sec_filing_date": "2026-05-01", "shares_outstanding": 16600000000, "sec_data_date": "2026-05-01", "source_url": "sec_url"},
        "MSFT": {"ticker": "MSFT", "cik": "789019", "entity_name": "Microsoft Corp.", "latest_sec_filing_type": "10-Q", "latest_sec_filing_date": "2026-04-25", "shares_outstanding": 7430000000, "sec_data_date": "2026-04-25", "source_url": "sec_url"},
        "AMZN": {"ticker": "AMZN", "cik": "1018724", "entity_name": "Amazon.com Inc.", "latest_sec_filing_type": "10-Q", "latest_sec_filing_date": "2026-04-30", "shares_outstanding": 10400000000, "sec_data_date": "2026-04-30", "source_url": "sec_url"},
        "NFLX": {"ticker": "NFLX", "cik": "1065280", "entity_name": "Netflix Inc.", "latest_sec_filing_type": "10-Q", "latest_sec_filing_date": "2026-04-18", "shares_outstanding": 431000000, "sec_data_date": "2026-04-18", "source_url": "sec_url"},
        "JPM": {"ticker": "JPM", "cik": "19617", "entity_name": "JPMorgan Chase & Co.", "latest_sec_filing_type": "10-Q", "latest_sec_filing_date": "2026-04-15", "shares_outstanding": 2900000000, "sec_data_date": "2026-04-15", "source_url": "sec_url"}
    }
    
    collected_at = "2026-07-15T00:00:00Z"
    
    # Run 1
    df1 = normalize_universe(constituents, universe, market_data, sec_data, "official_nasdaq_api", collected_at)
    df1 = apply_eligibility(df1)
    inc_top10_1 = generate_inclusion_watch_top10(df1)
    exc_top10_1 = generate_exclusion_watch_top10(df1)
    
    # Run 2
    df2 = normalize_universe(constituents, universe, market_data, sec_data, "official_nasdaq_api", collected_at)
    df2 = apply_eligibility(df2)
    inc_top10_2 = generate_inclusion_watch_top10(df2)
    exc_top10_2 = generate_exclusion_watch_top10(df2)
    
    # Verify both are identical
    assert verify_reproducibility(inc_top10_1, inc_top10_2)
    assert verify_reproducibility(exc_top10_1, exc_top10_2)
