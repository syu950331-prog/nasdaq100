import pandas as pd
from src.processing.rank_candidates import generate_inclusion_watch_top10, generate_exclusion_watch_top10

def test_inclusion_watch_ranking():
    # Setup test data with 12 eligible stocks and 2 ineligible stocks
    data = []
    # 12 eligible stocks
    for i in range(1, 13):
        data.append({
            "ticker": f"ELG{i}",
            "company_name": f"Eligible Company {i}",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "is_financial": "False",
            "is_constituent": False,
            "market_cap": float(i * 1000000000),  # market caps from 1B to 12B
            "market_cap_source": "provided",
            "last_price": 10.0,
            "shares_outstanding": i * 100000000,
            "eligibility_status": "eligible",
            "market_data_date": "2026-07-15"
        })
    # 2 ineligible/unknown stocks
    data.append({
        "ticker": "INELG1",
        "company_name": "Ineligible Company 1",
        "exchange": "NASDAQ",
        "sector": "Financials",
        "is_financial": "True",
        "is_constituent": False,
        "market_cap": 50000000000.0,
        "market_cap_source": "provided",
        "last_price": 50.0,
        "shares_outstanding": 1000000000,
        "eligibility_status": "ineligible",
        "market_data_date": "2026-07-15"
    })
    
    df = pd.DataFrame(data)
    inclusion_top10 = generate_inclusion_watch_top10(df)
    
    # Assert top 10 rows are returned
    assert len(inclusion_top10) == 10
    
    # Assert rank is 1 to 10
    assert list(inclusion_top10["watch_rank"]) == list(range(1, 11))
    
    # Assert descending order of market cap (highest is ELG12 with 12B, down to ELG3 with 3B)
    assert inclusion_top10.iloc[0]["ticker"] == "ELG12"
    assert inclusion_top10.iloc[9]["ticker"] == "ELG3"
    
    # Assert INELG1 is not in the list
    assert "INELG1" not in inclusion_top10["ticker"].values

def test_exclusion_watch_ranking():
    # Setup test data with 12 constituent stocks
    data = []
    for i in range(1, 13):
        data.append({
            "ticker": f"CONST{i}",
            "company_name": f"Constituent Company {i}",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "is_financial": "False",
            "is_constituent": True,
            "market_cap": float(i * 1000000000),  # market caps from 1B to 12B
            "last_price": 10.0,
            "shares_outstanding": i * 100000000,
            "eligibility_status": "ineligible",  # Already constituent
            "market_data_date": "2026-07-15"
        })
        
    df = pd.DataFrame(data)
    exclusion_top10 = generate_exclusion_watch_top10(df)
    
    # Assert top 10 rows are returned
    assert len(exclusion_top10) == 10
    
    # Assert rank is 1 to 10
    assert list(exclusion_top10["watch_rank"]) == list(range(1, 11))
    
    # Assert ascending order of market cap (smallest is CONST1 with 1B, up to CONST10 with 10B)
    assert exclusion_top10.iloc[0]["ticker"] == "CONST1"
    assert exclusion_top10.iloc[9]["ticker"] == "CONST10"
