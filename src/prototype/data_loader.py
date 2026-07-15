import os
import json
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Any, Optional

# Base directory setup
# Assuming this file is in nasdaq100-candidate-poc/src/prototype/data_loader.py
# PROJECT_ROOT is nasdaq100-candidate-poc
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

INCLUSION_CSV_PATH = OUTPUTS_DIR / "inclusion_watch_top10.csv"
EXCLUSION_CSV_PATH = OUTPUTS_DIR / "exclusion_watch_top10.csv"
QUALITY_JSON_PATH = OUTPUTS_DIR / "data_quality_report.json"
RESULT_JSON_PATH = OUTPUTS_DIR / "poc_result.json"

def format_market_cap(mcap: Optional[float]) -> str:
    """Format market capitalization values as $1.23T, $125.4B, $850.0M, or N/A."""
    if mcap is None or pd.isna(mcap):
        return "N/A"
    
    try:
        val = float(mcap)
        if val >= 1e12:
            return f"${val / 1e12:.2f}T"
        elif val >= 1e9:
            return f"${val / 1e9:.1f}B"
        elif val >= 1e6:
            return f"${val / 1e6:.1f}M"
        else:
            return f"${val:,.0f}"
    except (ValueError, TypeError):
        return str(mcap)

@st.cache_data
def load_inclusion_candidates() -> pd.DataFrame:
    """Load inclusion candidate top 10 from CSV."""
    if not INCLUSION_CSV_PATH.exists():
        raise FileNotFoundError(
            f"편입 관찰 후보 데이터 파일이 존재하지 않습니다. 경로: {INCLUSION_CSV_PATH}\n"
            "먼저 'python run_poc.py --refresh' 명령을 실행해 데이터를 수집해 주세요."
        )
    try:
        df = pd.read_csv(INCLUSION_CSV_PATH)
        # Safe conversions
        if "market_cap" in df.columns:
            df["market_cap"] = pd.to_numeric(df["market_cap"], errors="coerce")
        if "watch_rank" in df.columns:
            df["watch_rank"] = pd.to_numeric(df["watch_rank"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        raise RuntimeError(f"편입 후보 CSV 파일을 읽는 중 오류가 발생했습니다: {e}")

@st.cache_data
def load_exclusion_candidates() -> pd.DataFrame:
    """Load exclusion candidate top 10 from CSV."""
    if not EXCLUSION_CSV_PATH.exists():
        raise FileNotFoundError(
            f"편출 관찰 후보 데이터 파일이 존재하지 않습니다. 경로: {EXCLUSION_CSV_PATH}\n"
            "먼저 'python run_poc.py --refresh' 명령을 실행해 데이터를 수집해 주세요."
        )
    try:
        df = pd.read_csv(EXCLUSION_CSV_PATH)
        # Safe conversions
        if "market_cap" in df.columns:
            df["market_cap"] = pd.to_numeric(df["market_cap"], errors="coerce")
        if "watch_rank" in df.columns:
            df["watch_rank"] = pd.to_numeric(df["watch_rank"], errors="coerce").fillna(0).astype(int)
        return df
    except Exception as e:
        raise RuntimeError(f"편출 후보 CSV 파일을 읽는 중 오류가 발생했습니다: {e}")

@st.cache_data
def load_data_quality_report() -> Dict[str, Any]:
    """Load data quality report from JSON."""
    if not QUALITY_JSON_PATH.exists():
        raise FileNotFoundError(
            f"데이터 품질 보고서 파일이 존재하지 않습니다. 경로: {QUALITY_JSON_PATH}\n"
            "먼저 'python run_poc.py --refresh' 명령을 실행해 데이터를 수집해 주세요."
        )
    try:
        with open(QUALITY_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"데이터 품질 보고서 JSON 형식이 올바르지 않습니다: {e}")
    except Exception as e:
        raise RuntimeError(f"데이터 품질 보고서 파일을 읽는 중 오류가 발생했습니다: {e}")

@st.cache_data
def load_poc_result() -> Dict[str, Any]:
    """Load PoC result statistics from JSON."""
    if not RESULT_JSON_PATH.exists():
        raise FileNotFoundError(
            f"PoC 결과 요약 파일이 존재하지 않습니다. 경로: {RESULT_JSON_PATH}\n"
            "먼저 'python run_poc.py --refresh' 명령을 실행해 데이터를 수집해 주세요."
        )
    try:
        with open(RESULT_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"PoC 결과 요약 JSON 형식이 올바르지 않습니다: {e}")
    except Exception as e:
        raise RuntimeError(f"PoC 결과 요약 파일을 읽는 중 오류가 발생했습니다: {e}")
