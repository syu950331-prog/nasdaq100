import requests
import datetime
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Tuple
from src.config import (
    NASDAQ_HEADERS,
    NASDAQ_CONSTITUENTS_URL,
    NASDAQ_SCREENER_URL,
    WIKIPEDIA_NASDAQ100_URL,
    DEFAULT_TIMEOUT,
    MAX_RETRIES
)
from src.models import ConstituentData, ScreenerStockData

class NasdaqCollector:
    def __init__(self):
        self.headers = NASDAQ_HEADERS
        self.timeout = DEFAULT_TIMEOUT

    def _request_with_retry(self, url: str, params: Dict[str, Any] = None) -> requests.Response:
        last_err = None
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response
            except Exception as e:
                last_err = e
        raise last_err if last_err else Exception(f"Failed to fetch {url}")

    def fetch_constituents_official(self) -> List[ConstituentData]:
        """Fetch current constituents from official Nasdaq endpoint."""
        try:
            response = self._request_with_retry(NASDAQ_CONSTITUENTS_URL)
            json_data = response.json()
            rows = json_data.get("data", {}).get("data", {}).get("rows", [])
            
            constituents = []
            collected_at = datetime.datetime.utcnow().isoformat() + "Z"
            for row in rows:
                ticker = row.get("symbol", "").strip()
                if not ticker:
                    continue
                
                # Market cap is a string like "4,624,460,910,160", we might normalize later but keep it simple
                constituents.append({
                    "ticker": ticker,
                    "company_name": row.get("companyName", "").strip(),
                    "is_constituent": True,
                    "sector": row.get("sector", "").strip(),
                    "source_url": NASDAQ_CONSTITUENTS_URL,
                    "collected_at": collected_at
                })
            return constituents
        except Exception as e:
            # Let the caller handle and log to data_quality_report
            raise RuntimeError(f"Official Nasdaq constituents endpoint failed: {str(e)}")

    def fetch_constituents_wikipedia(self) -> List[ConstituentData]:
        """Fallback method to fetch constituents from Wikipedia."""
        try:
            response = requests.get(WIKIPEDIA_NASDAQ100_URL, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # The constituents list is usually in a table with id "constituents"
            table = soup.find("table", {"id": "constituents"})
            if not table:
                # Try finding any wikitable
                table = soup.find("table", {"class": "wikitable"})
            
            if not table:
                raise ValueError("Could not find constituents table on Wikipedia.")
                
            rows = table.find_all("tr")[1:]  # skip header
            constituents = []
            collected_at = datetime.datetime.utcnow().isoformat() + "Z"
            
            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 2:
                    continue
                # For Nasdaq-100 Wikipedia table: Col 0: Company, Col 1: Ticker, Col 2: GICS Sector
                company_name = cols[0].text.strip()
                ticker = cols[1].text.strip()
                sector = cols[2].text.strip() if len(cols) > 2 else ""
                
                # Cleanup ticket (e.g. dots to dashes or clean whitespace)
                ticker = ticker.replace(".", "-").strip()
                
                constituents.append({
                    "ticker": ticker,
                    "company_name": company_name,
                    "is_constituent": True,
                    "sector": sector,
                    "source_url": WIKIPEDIA_NASDAQ100_URL,
                    "collected_at": collected_at
                })
            return constituents
        except Exception as e:
            raise RuntimeError(f"Wikipedia constituents scrape failed: {str(e)}")

    def fetch_constituents(self) -> Tuple[List[ConstituentData], str, List[str]]:
        """
        Fetches the Nasdaq-100 constituents, attempting official first, falling back to Wikipedia.
        Returns (constituents_list, source_used, warnings_list)
        """
        warnings = []
        try:
            constituents = self.fetch_constituents_official()
            if len(constituents) >= 90:
                return constituents, "official_nasdaq_api", warnings
            else:
                warnings.append(f"Official constituents API returned only {len(constituents)} items, which is below expected 90+. Falling back to Wikipedia.")
        except Exception as e:
            warnings.append(f"Official constituents API failed: {str(e)}. Falling back to Wikipedia.")
        
        try:
            constituents = self.fetch_constituents_wikipedia()
            return constituents, "wikipedia_scrape", warnings
        except Exception as e:
            warnings.append(f"Wikipedia constituents fallback failed: {str(e)}.")
            raise RuntimeError("Both official Nasdaq API and Wikipedia fallback failed to fetch constituents.")

    def fetch_universe(self, limit: int = 250) -> List[ScreenerStockData]:
        """Fetch general Nasdaq stock universe (ordered by market cap)."""
        params = {
            "tableonly": "true",
            "limit": str(limit),
            "exchange": "nasdaq"
        }
        try:
            response = self._request_with_retry(NASDAQ_SCREENER_URL, params=params)
            json_data = response.json()
            rows = json_data.get("data", {}).get("table", {}).get("rows", [])
            
            universe = []
            as_of_date = datetime.date.today().isoformat()
            
            for row in rows:
                ticker = row.get("symbol", "").strip()
                if not ticker:
                    continue
                
                # Parse numeric values
                mcap_str = row.get("marketCap", "")
                market_cap = None
                if mcap_str:
                    try:
                        market_cap = float(mcap_str.replace(",", "").strip())
                    except ValueError:
                        pass
                
                price_str = row.get("lastsale", "")
                last_price = None
                if price_str:
                    try:
                        last_price = float(price_str.replace("$", "").replace(",", "").strip())
                    except ValueError:
                        pass
                
                universe.append({
                    "ticker": ticker,
                    "company_name": row.get("name", "").strip(),
                    "exchange": "NASDAQ",
                    "sector": row.get("sector", "").strip() if "sector" in row else "",
                    "industry": row.get("industry", "").strip() if "industry" in row else "",
                    "market_cap": market_cap,
                    "last_price": last_price,
                    "source_url": NASDAQ_SCREENER_URL,
                    "as_of_date": as_of_date
                })
            return universe
        except Exception as e:
            raise RuntimeError(f"Failed to fetch stock universe from Nasdaq screener: {str(e)}")
