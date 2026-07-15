import pytest
import pandas as pd
import streamlit as st
from unittest.mock import patch
from pathlib import Path
from src.prototype.data_loader import (
    load_inclusion_candidates,
    load_exclusion_candidates,
    load_poc_result,
    load_data_quality_report,
    format_market_cap
)

def test_load_inclusion_candidates_success():
    """Verify that inclusion watch candidates CSV can be loaded and parsed properly."""
    df = load_inclusion_candidates()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "ticker" in df.columns
    assert "market_cap" in df.columns
    # Check that market cap is numeric (float)
    assert pd.api.types.is_numeric_dtype(df["market_cap"])

def test_load_exclusion_candidates_success():
    """Verify that exclusion watch candidates CSV can be loaded properly."""
    df = load_exclusion_candidates()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "ticker" in df.columns
    assert "market_cap" in df.columns
    assert pd.api.types.is_numeric_dtype(df["market_cap"])

def test_load_poc_result_success():
    """Verify that poc_result.json is loaded as a dictionary."""
    res = load_poc_result()
    assert isinstance(res, dict)
    assert "overall_result" in res
    assert "reproducibility_passed" in res

def test_missing_files_raise_error():
    """Verify that FileNotFoundError is raised when files are missing, rather than generating fake data."""
    # Clear Streamlit cache to ensure the function body is executed
    st.cache_data.clear()
    
    with patch("src.prototype.data_loader.INCLUSION_CSV_PATH", Path("non_existent_file.csv")):
        with pytest.raises(FileNotFoundError) as exc_info:
            load_inclusion_candidates()
        assert "존재하지 않습니다" in str(exc_info.value)

    st.cache_data.clear()
    with patch("src.prototype.data_loader.EXCLUSION_CSV_PATH", Path("non_existent_file.csv")):
        with pytest.raises(FileNotFoundError) as exc_info:
            load_exclusion_candidates()
        assert "존재하지 않습니다" in str(exc_info.value)

    st.cache_data.clear()
    with patch("src.prototype.data_loader.RESULT_JSON_PATH", Path("non_existent_file.json")):
        with pytest.raises(FileNotFoundError) as exc_info:
            load_poc_result()
        assert "존재하지 않습니다" in str(exc_info.value)

def test_numeric_conversion_safety():
    """Verify that format_market_cap resolves string and null values safely without crashing."""
    assert format_market_cap(None) == "N/A"
    assert format_market_cap(float("nan")) == "N/A"
    assert format_market_cap(1.25e12) == "$1.25T"
    assert format_market_cap(125.4e9) == "$125.4B"
    assert format_market_cap(850.0e6) == "$850.0M"
    assert format_market_cap(1500) == "$1,500"
    assert format_market_cap("invalid_number") == "invalid_number"
