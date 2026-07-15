import requests
import time
import datetime
from typing import Dict, Any, Optional, Tuple, List
from src.config import SEC_USER_AGENT, SEC_TICKER_CIK_URL, SEC_REQUEST_DELAY, MAX_RETRIES, DEFAULT_TIMEOUT
from src.models import SECEntityData

class SECCollector:
    def __init__(self):
        self.headers = {
            "User-Agent": SEC_USER_AGENT
        }
        self.timeout = DEFAULT_TIMEOUT
        self.cik_map: Dict[str, str] = {}

    def fetch_ticker_cik_mapping(self) -> Dict[str, str]:
        """Fetch ticker to CIK mapping from SEC."""
        try:
            response = requests.get(SEC_TICKER_CIK_URL, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            mapping = {}
            for item in data.values():
                ticker = item.get("ticker", "").strip().upper()
                cik = str(item.get("cik_str", "")).strip()
                if ticker and cik:
                    mapping[ticker] = cik
            
            self.cik_map = mapping
            return mapping
        except Exception as e:
            raise RuntimeError(f"Failed to fetch SEC ticker-CIK mapping: {str(e)}")

    def _request_with_delay(self, url: str) -> requests.Response:
        """Helper to make a request, enforce 0.15s delay, and handle retries."""
        last_err = None
        for attempt in range(MAX_RETRIES):
            try:
                # SEC compliance delay
                time.sleep(SEC_REQUEST_DELAY)
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
                response.raise_for_status()
                return response
            except Exception as e:
                last_err = e
        raise last_err if last_err else Exception(f"Failed to fetch SEC API: {url}")

    def fetch_company_filings(self, ticker: str, cik: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Fetch company submissions JSON and parse the latest 10-K or 10-Q filing.
        Returns (latest_sec_filing_type, latest_sec_filing_date)
        """
        cik_padded = cik.zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
        try:
            response = self._request_with_delay(url)
            data = response.json()
            
            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            dates = recent.get("filingDate", [])
            
            # Find the most recent 10-K or 10-Q
            for i, form in enumerate(forms):
                if form in ["10-K", "10-Q"]:
                    return form, dates[i]
            
            # If not found in the initial forms, return first form if list exists
            if forms and dates:
                return forms[0], dates[0]
            
            return None, None
        except Exception:
            return None, None

    def fetch_shares_outstanding(self, ticker: str, cik: str) -> Tuple[Optional[int], Optional[str]]:
        """
        Fetch company facts JSON and parse the latest EntityCommonStockSharesOutstanding.
        Returns (shares_outstanding, sec_data_date)
        """
        cik_padded = cik.zfill(10)
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_padded}.json"
        try:
            response = self._request_with_delay(url)
            data = response.json()
            
            # Look for EntityCommonStockSharesOutstanding in dei or us-gaap
            facts = data.get("facts", {})
            shares_data = facts.get("dei", {}).get("EntityCommonStockSharesOutstanding", {}) or \
                          facts.get("us-gaap", {}).get("EntityCommonStockSharesOutstanding", {})
            
            if not shares_data:
                return None, None
                
            units = shares_data.get("units", {})
            for unit_key, unit_vals in units.items():
                if unit_vals:
                    # Sort by filing date or end date to get the latest
                    sorted_vals = sorted(unit_vals, key=lambda x: x.get("filed", ""))
                    latest = sorted_vals[-1]
                    val = latest.get("val")
                    filed_date = latest.get("filed")
                    if val is not None:
                        return int(val), filed_date
            
            return None, None
        except Exception:
            return None, None

    def fetch_sec_data(self, ticker: str) -> Optional[SECEntityData]:
        """Fetch all SEC details for a single ticker."""
        if not self.cik_map:
            self.fetch_ticker_cik_mapping()
            
        ticker_upper = ticker.upper().strip()
        cik = self.cik_map.get(ticker_upper)
        if not cik:
            return None
            
        latest_filing, latest_date = self.fetch_company_filings(ticker_upper, cik)
        shares, shares_date = self.fetch_shares_outstanding(ticker_upper, cik)
        
        # Determine the source URL used for the company
        cik_padded = cik.zfill(10)
        source_url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
        
        return {
            "ticker": ticker_upper,
            "cik": cik,
            "entity_name": f"SEC Entity {ticker_upper}",  # We can also get this from company facts or mapping if needed
            "latest_sec_filing_type": latest_filing if latest_filing else "unknown",
            "latest_sec_filing_date": latest_date if latest_date else "unknown",
            "shares_outstanding": shares,
            "sec_data_date": shares_date if shares_date else (latest_date if latest_date else "unknown"),
            "source_url": source_url
        }

    def fetch_sec_data_batch(self, tickers: List[str]) -> Tuple[Dict[str, SECEntityData], int, List[str]]:
        """
        Batch fetch SEC data for a list of tickers.
        Returns (sec_data_dict, matched_count, failed_tickers)
        """
        sec_dict = {}
        matched_count = 0
        failed_tickers = []
        
        # Load CIK mapping first
        try:
            self.fetch_ticker_cik_mapping()
        except Exception as e:
            # If CIK mapping fails, we cannot match any ticker
            return {}, 0, list(tickers)

        for ticker in tickers:
            try:
                data = self.fetch_sec_data(ticker)
                if data:
                    sec_dict[ticker] = data
                    matched_count += 1
                else:
                    failed_tickers.append(ticker)
            except Exception:
                failed_tickers.append(ticker)
                
        return sec_dict, matched_count, failed_tickers
