import datetime
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple
from src.models import MarketData
from src.config import MAX_RETRIES

class MarketCollector:
    def __init__(self, max_workers: int = 15):
        self.max_workers = max_workers

    def _fetch_single_ticker_info(self, ticker: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Fetch info dict from yfinance for a single ticker with simple retry."""
        ticker_clean = ticker.replace(".", "-").strip().upper()
        for attempt in range(MAX_RETRIES):
            try:
                t = yf.Ticker(ticker_clean)
                info = t.info
                if info and isinstance(info, dict):
                    return ticker, info
            except Exception:
                pass
        return ticker, None

    def fetch_market_data_batch(self, tickers: List[str]) -> Tuple[Dict[str, MarketData], Dict[str, str], int]:
        """
        Fetch market data and sectors for a list of tickers in parallel.
        Returns:
            - market_data_dict: Dict mapping ticker to MarketData Dict.
            - sector_dict: Dict mapping ticker to sector.
            - matched_count: Count of successfully resolved tickers.
        """
        market_data_dict = {}
        sector_dict = {}
        matched_count = 0
        
        print(f"Enriching {len(tickers)} tickers via yfinance...")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._fetch_single_ticker_info, ticker): ticker for ticker in tickers}
            
            for future in as_completed(futures):
                ticker = futures[future]
                try:
                    ticker, info = future.result()
                    if info:
                        # Extract sector/industry
                        sector = info.get("sector", "")
                        industry = info.get("industry", "")
                        if sector:
                            sector_dict[ticker] = sector
                        
                        # Get price and market cap
                        price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("lastPrice")
                        shares = info.get("sharesOutstanding")
                        mcap = info.get("marketCap")
                        
                        # Handle market cap calculation if not provided directly
                        mcap_source = "unknown"
                        if mcap is not None:
                            mcap_source = "provided"
                        elif price is not None and shares is not None:
                            mcap = price * shares
                            mcap_source = "calculated"
                            
                        # Format date
                        price_date = datetime.date.today().isoformat()
                        
                        market_data_dict[ticker] = {
                            "ticker": ticker,
                            "last_price": price,
                            "market_cap": mcap,
                            "shares_outstanding": shares,
                            "price_date": price_date,
                            "source_type": "secondary_market_data",
                            "market_cap_source": mcap_source,
                            "sector": sector,
                            "industry": industry
                        }
                        matched_count += 1
                    else:
                        market_data_dict[ticker] = {
                            "ticker": ticker,
                            "last_price": None,
                            "market_cap": None,
                            "shares_outstanding": None,
                            "price_date": datetime.date.today().isoformat(),
                            "source_type": "secondary_market_data",
                            "market_cap_source": "unknown",
                            "sector": "",
                            "industry": ""
                        }
                except Exception:
                    market_data_dict[ticker] = {
                        "ticker": ticker,
                        "last_price": None,
                        "market_cap": None,
                        "shares_outstanding": None,
                        "price_date": datetime.date.today().isoformat(),
                        "source_type": "secondary_market_data",
                        "market_cap_source": "unknown",
                        "sector": "",
                        "industry": ""
                    }
                    
        return market_data_dict, sector_dict, matched_count
