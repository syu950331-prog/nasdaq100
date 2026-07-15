import argparse
import json
import sys
from src.pipeline import PoCPipeline
from src.config import DATA_QUALITY_REPORT_JSON

def main():
    parser = argparse.ArgumentParser(description="Nasdaq-100 Inclusion/Exclusion Observation Candidate PoC")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-fetch all data from external sources and update raw cache."
    )
    args = parser.parse_args()

    try:
        pipeline = PoCPipeline()
        result = pipeline.run(refresh=args.refresh)
        
        # Load quality metrics from report
        with open(DATA_QUALITY_REPORT_JSON, "r", encoding="utf-8") as f:
            dq_report = json.load(f)

        repro_status = "PASS" if result.get("reproducibility_passed") else "FAIL"
        
        print("\n=== Nasdaq-100 Official Data PoC ===")
        print(f"Universe: {dq_report.get('total_universe_count')}")
        print(f"Current constituents: {dq_report.get('constituent_count')}")
        print(f"SEC matched: {dq_report.get('sec_matched_count')}")
        print(f"Market data matched: {dq_report.get('market_data_matched_count')}")
        print(f"Inclusion watch candidates: {result.get('inclusion_candidate_count')}")
        print(f"Exclusion watch candidates: {result.get('exclusion_candidate_count')}")
        print(f"Data completeness: {result.get('data_completeness_rate')}%")
        print(f"Reproducibility: {repro_status}")
        print(f"Overall result: {result.get('overall_result')}")
        
    except Exception as e:
        print(f"\nError running PoC Pipeline: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
