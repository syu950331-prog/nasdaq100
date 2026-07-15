import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Base directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Raw file paths
NASDAQ100_CONSTITUENTS_PATH = RAW_DATA_DIR / "nasdaq100_constituents.json"
NASDAQ_UNIVERSE_PATH = RAW_DATA_DIR / "nasdaq_universe.json"
MARKET_DATA_PATH = RAW_DATA_DIR / "market_data.json"
SEC_COMPANY_DATA_PATH = RAW_DATA_DIR / "sec_company_data.json"

# Processed and output paths
CANDIDATE_UNIVERSE_CSV = PROCESSED_DATA_DIR / "candidate_universe.csv"
INCLUSION_WATCH_TOP10_CSV = OUTPUTS_DIR / "inclusion_watch_top10.csv"
EXCLUSION_WATCH_TOP10_CSV = OUTPUTS_DIR / "exclusion_watch_top10.csv"
DATA_QUALITY_REPORT_JSON = OUTPUTS_DIR / "data_quality_report.json"
POC_RESULT_JSON = OUTPUTS_DIR / "poc_result.json"

# SEC Configuration
SEC_USER_AGENT = os.environ.get("SEC_USER_AGENT", "Nasdaq100PoC default_poc_user@example.com")
SEC_TICKER_CIK_URL = "https://www.sec.gov/files/company_tickers.json"

# Nasdaq official endpoints
NASDAQ_CONSTITUENTS_URL = "https://api.nasdaq.com/api/quote/list-type/nasdaq100"
NASDAQ_SCREENER_URL = "https://api.nasdaq.com/api/screener/stocks"

# Wikipedia fallback for constituents
WIKIPEDIA_NASDAQ100_URL = "https://en.wikipedia.org/wiki/Nasdaq-100"

# Request Headers for Nasdaq website APIs
NASDAQ_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.nasdaq.com",
    "Referer": "https://www.nasdaq.com/"
}

# API Call settings
SEC_REQUEST_DELAY = 0.15  # Minimum wait of 0.15s between requests to SEC
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 15.0  # seconds

def ensure_directories():
    """Ensure all required directories exist."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
