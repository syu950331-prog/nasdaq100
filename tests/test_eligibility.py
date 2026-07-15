import pandas as pd
from src.processing.eligibility import evaluate_stock_eligibility

def test_eligibility_scenarios():
    # 1. Eligible stock
    row_eligible = pd.Series({
        "ticker": "AAPL",
        "exchange": "NASDAQ",
        "is_constituent": False,
        "is_financial": "False",
        "market_cap": 2500000000000.0,
        "last_price": 180.0
    })
    status, reason = evaluate_stock_eligibility(row_eligible)
    assert status == "eligible"
    assert reason == ""

    # 2. Already a constituent
    row_const = pd.Series({
        "ticker": "MSFT",
        "exchange": "NASDAQ",
        "is_constituent": True,
        "is_financial": "False",
        "market_cap": 3000000000000.0,
        "last_price": 400.0
    })
    status, reason = evaluate_stock_eligibility(row_const)
    assert status == "ineligible"
    assert "constituent" in reason

    # 3. Financial stock
    row_fin = pd.Series({
        "ticker": "JPM",
        "exchange": "NASDAQ",
        "is_constituent": False,
        "is_financial": "True",
        "market_cap": 50000000000.0,
        "last_price": 100.0
    })
    status, reason = evaluate_stock_eligibility(row_fin)
    assert status == "ineligible"
    assert "Financial" in reason

    # 4. Unknown financial status
    row_unk_fin = pd.Series({
        "ticker": "XYZ",
        "exchange": "NASDAQ",
        "is_constituent": False,
        "is_financial": "unknown",
        "market_cap": 100000000.0,
        "last_price": 5.0
    })
    status, reason = evaluate_stock_eligibility(row_unk_fin)
    assert status == "unknown"
    assert "Sector classification unknown" in reason

    # 5. Missing market cap
    row_no_cap = pd.Series({
        "ticker": "ABC",
        "exchange": "NASDAQ",
        "is_constituent": False,
        "is_financial": "False",
        "market_cap": None,
        "last_price": 50.0
    })
    status, reason = evaluate_stock_eligibility(row_no_cap)
    assert status == "unknown"
    assert "Market capitalization data missing" in reason
