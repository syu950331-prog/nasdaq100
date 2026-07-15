import json
import uuid
import datetime
import os
import pandas as pd
from typing import Dict, Any, List, Tuple

from src.config import (
    ensure_directories,
    NASDAQ100_CONSTITUENTS_PATH,
    NASDAQ_UNIVERSE_PATH,
    MARKET_DATA_PATH,
    SEC_COMPANY_DATA_PATH,
    CANDIDATE_UNIVERSE_CSV,
    INCLUSION_WATCH_TOP10_CSV,
    EXCLUSION_WATCH_TOP10_CSV,
    DATA_QUALITY_REPORT_JSON,
    POC_RESULT_JSON,
    WIKIPEDIA_NASDAQ100_URL
)
from src.collectors.nasdaq_collector import NasdaqCollector
from src.collectors.sec_collector import SECCollector
from src.collectors.market_collector import MarketCollector
from src.processing.normalize import normalize_universe
from src.processing.eligibility import apply_eligibility
from src.processing.rank_candidates import generate_inclusion_watch_top10, generate_exclusion_watch_top10
from src.validation.data_quality import calculate_data_quality, save_data_quality_report
from src.validation.reproducibility import calculate_snapshot_hash, verify_reproducibility

class PoCPipeline:
    def __init__(self):
        ensure_directories()
        self.nasdaq_collector = NasdaqCollector()
        self.sec_collector = SECCollector()
        self.market_collector = MarketCollector()

    def run(self, refresh: bool = False) -> Dict[str, Any]:
        """
        Run the full PoC Pipeline.
        Args:
            refresh: If True, re-fetch all data from external sources and update cache.
                     If False, load from cached raw files in data/raw/.
        """
        run_id = str(uuid.uuid4())
        collected_at = datetime.datetime.utcnow().isoformat() + "Z"
        
        # Track sources and warnings
        official_sources = ["sec_api"]
        secondary_sources = ["yfinance"]
        source_warnings = []
        failed_tickers = []
        constituents_source = "official_nasdaq_api"

        raw_files = [
            str(NASDAQ100_CONSTITUENTS_PATH),
            str(NASDAQ_UNIVERSE_PATH),
            str(MARKET_DATA_PATH),
            str(SEC_COMPANY_DATA_PATH)
        ]

        if refresh:
            print("Refreshing data from external sources...")
            # 1. Fetch constituents
            try:
                constituents, const_src, warnings = self.nasdaq_collector.fetch_constituents()
                constituents_source = const_src
                source_warnings.extend(warnings)
                if const_src == "official_nasdaq_api":
                    official_sources.append("official_nasdaq_api")
                else:
                    secondary_sources.append("wikipedia_scrape")
            except Exception as e:
                # If everything fails, raise error since constituents list is critical
                raise RuntimeError(f"Failed to fetch constituents: {e}")

            # Save constituents raw
            with open(NASDAQ100_CONSTITUENTS_PATH, "w", encoding="utf-8") as f:
                json.dump(constituents, f, indent=4, ensure_ascii=False)

            # 2. Fetch stock universe
            try:
                # Top 250 stocks by market cap
                print("Fetching Nasdaq universe stock screener...")
                universe = self.nasdaq_collector.fetch_universe(limit=250)
                official_sources.append("nasdaq_stock_screener_api")
            except Exception as e:
                # Fallback: if Stock Screener fails, we create a universe of constituents plus fallback yfinance
                source_warnings.append(f"Nasdaq Stock Screener failed: {e}. Falling back to constituents list as base universe.")
                universe = []
                for c in constituents:
                    universe.append({
                        "ticker": c["ticker"],
                        "company_name": c["company_name"],
                        "exchange": "NASDAQ",
                        "sector": c["sector"],
                        "industry": "",
                        "market_cap": None,
                        "last_price": None,
                        "source_url": c["source_url"],
                        "as_of_date": datetime.date.today().isoformat()
                    })

            # Save universe raw
            with open(NASDAQ_UNIVERSE_PATH, "w", encoding="utf-8") as f:
                json.dump(universe, f, indent=4, ensure_ascii=False)

            # Extract list of all tickers to enrich
            all_tickers = list(set(u["ticker"].upper().strip() for u in universe) | set(c["ticker"].upper().strip() for c in constituents))

            # 3. Fetch market data (yfinance)
            try:
                market_data, sector_dict, matched_mkt = self.market_collector.fetch_market_data_batch(all_tickers)
            except Exception as e:
                source_warnings.append(f"Market data collector failed: {e}")
                market_data = {}
                sector_dict = {}

            with open(MARKET_DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(market_data, f, indent=4, ensure_ascii=False)

            # 4. Fetch SEC data
            try:
                print("Fetching SEC filings and shares (this will take a moment)...")
                sec_data, matched_sec, sec_fails = self.sec_collector.fetch_sec_data_batch(all_tickers)
                failed_tickers.extend(sec_fails)
            except Exception as e:
                source_warnings.append(f"SEC collector failed: {e}")
                sec_data = {}

            with open(SEC_COMPANY_DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(sec_data, f, indent=4, ensure_ascii=False)
            
            print("Data refresh completed and saved to raw cache.")

        else:
            print("Loading data from raw cached files...")
            # Check if cache files exist
            for filepath in raw_files:
                if not os.path.exists(filepath):
                    raise FileNotFoundError(
                        f"Cache file {filepath} not found. Please run with --refresh first."
                    )
            
            # Load from files
            with open(NASDAQ100_CONSTITUENTS_PATH, "r", encoding="utf-8") as f:
                constituents = json.load(f)
            with open(NASDAQ_UNIVERSE_PATH, "r", encoding="utf-8") as f:
                universe = json.load(f)
            with open(MARKET_DATA_PATH, "r", encoding="utf-8") as f:
                market_data = json.load(f)
            with open(SEC_COMPANY_DATA_PATH, "r", encoding="utf-8") as f:
                sec_data = json.load(f)

            # Infer constituents source
            if constituents and constituents[0].get("source_url") == WIKIPEDIA_NASDAQ100_URL:
                constituents_source = "wikipedia_scrape"
                secondary_sources.append("wikipedia_scrape")
            else:
                constituents_source = "official_nasdaq_api"
                official_sources.append("official_nasdaq_api")

            official_sources.append("nasdaq_stock_screener_api")

        # Compute snapshot hash
        snapshot_hash = calculate_snapshot_hash(raw_files)

        # First run of processing pipeline
        normalized_df = normalize_universe(
            constituents, universe, market_data, sec_data, constituents_source, collected_at
        )
        processed_df = apply_eligibility(normalized_df)
        
        # Save master universe
        processed_df.to_csv(CANDIDATE_UNIVERSE_CSV, index=False)

        # Generate watch lists
        inclusion_top10 = generate_inclusion_watch_top10(processed_df)
        exclusion_top10 = generate_exclusion_watch_top10(processed_df)

        inclusion_top10.to_csv(INCLUSION_WATCH_TOP10_CSV, index=False)
        exclusion_top10.to_csv(EXCLUSION_WATCH_TOP10_CSV, index=False)

        # Data Quality check
        dq_report = calculate_data_quality(
            processed_df, official_sources, secondary_sources, failed_tickers, source_warnings
        )
        save_data_quality_report(dq_report, str(DATA_QUALITY_REPORT_JSON))

        # Perform second execution run to verify reproducibility
        normalized_df_run2 = normalize_universe(
            constituents, universe, market_data, sec_data, constituents_source, collected_at
        )
        processed_df_run2 = apply_eligibility(normalized_df_run2)
        inclusion_top10_run2 = generate_inclusion_watch_top10(processed_df_run2)
        exclusion_top10_run2 = generate_exclusion_watch_top10(processed_df_run2)

        repro_inc = verify_reproducibility(inclusion_top10, inclusion_top10_run2)
        repro_exc = verify_reproducibility(exclusion_top10, exclusion_top10_run2)
        reproducibility_passed = repro_inc and repro_exc

        # Completeness rate
        total_items = dq_report["total_universe_count"]
        data_completeness_rate = 0.0
        if total_items > 0:
            data_completeness_rate = (
                (dq_report["sec_matched_count"] + dq_report["market_data_matched_count"]) 
                / (2.0 * total_items) 
                * 100.0
            )

        # Official source ratio
        # What fraction of collectors succeeded with official sources?
        official_sources_count = sum(1 for s in [constituents_source] if s == "official_nasdaq_api")
        official_source_ratio = 1.0 if official_sources_count == 1 else 0.0

        # Assess PASS criteria
        # PoC PASS 조건:
        # - 실제 외부 데이터 수집 성공
        # - 현재 구성 종목 90개 이상 확보
        # - 전체 후보 기업 150개 이상 확보
        # - market_cap 확보율 90% 이상
        # - SEC CIK 매핑 성공률 90% 이상
        # - 편입 관찰 후보 5개 이상 생성
        # - 편출 관찰 후보 5개 이상 생성
        # - 동일 raw 스냅숏 재처리 결과 100% 동일
        # - 출력 파일 4개 생성
        # - pytest 전체 통과 (handled outside)
        
        mcap_pct = 0.0
        cik_pct = 0.0
        if total_items > 0:
            mcap_pct = (total_items - dq_report["missing_market_cap_count"]) / total_items * 100
            cik_pct = dq_report["sec_matched_count"] / total_items * 100

        has_outputs = (
            os.path.exists(INCLUSION_WATCH_TOP10_CSV) and
            os.path.exists(EXCLUSION_WATCH_TOP10_CSV) and
            os.path.exists(DATA_QUALITY_REPORT_JSON) and
            os.path.exists(CANDIDATE_UNIVERSE_CSV)
        )

        pass_conditions = {
            "constituents_ok": dq_report["constituent_count"] >= 90,
            "universe_ok": total_items >= 150,
            "market_cap_ok": mcap_pct >= 90.0,
            "sec_cik_ok": cik_pct >= 90.0,
            "inclusion_count_ok": len(inclusion_top10) >= 5,
            "exclusion_count_ok": len(exclusion_top10) >= 5,
            "reproducible": reproducibility_passed,
            "outputs_created": has_outputs
        }

        # Check if we should pass or conditional pass
        # "다만 공식 Nasdaq 데이터 접근이 제한되어 공식 구성 종목 수집에 실패한 경우에는 overall_result를 PASS로 만들지 말고 CONDITIONAL_PASS로 처리한다.
        # CONDITIONAL_PASS 조건:
        # - 실제 데이터는 수집했지만 일부 구성 또는 시장 데이터에 대체 데이터 소스를 사용한 경우
        # - source_warnings와 limitations에 이를 명확히 기록한 경우"
        
        overall_result = "PASS"
        limitations = [
            "PoC does not replicate final Nasdaq index committee discretion or all technical eligibility criteria.",
            "Market capitalization relies on publicly available dates and is not real-time."
        ]

        if constituents_source != "official_nasdaq_api" or "wikipedia_scrape" in secondary_sources:
            overall_result = "CONDITIONAL_PASS"
            limitations.append("Wikipedia fallback was used for Nasdaq-100 constituents due to official API limits/blocks.")
        
        # Check for hard failures
        all_passed = all(pass_conditions.values())
        if not all_passed:
            overall_result = "FAIL"

        result = {
            "run_id": run_id,
            "snapshot_hash": snapshot_hash,
            "inclusion_candidate_count": len(inclusion_top10),
            "exclusion_candidate_count": len(exclusion_top10),
            "reproducibility_passed": reproducibility_passed,
            "data_completeness_rate": round(data_completeness_rate, 2),
            "official_source_ratio": round(official_source_ratio, 2),
            "overall_result": overall_result,
            "limitations": limitations
        }

        with open(POC_RESULT_JSON, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

        return result
