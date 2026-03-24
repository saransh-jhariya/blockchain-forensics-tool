"""
Configuration settings for the Blockchain Forensics Tool.
All API keys should be set via environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys (set via environment variables)
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
CHAINABUSE_API_KEY = os.getenv("CHAINABUSE_API_KEY", "")

# API Endpoints
ETHERSCAN_BASE_URL = "https://api.etherscan.io/api"
ARBISCAN_BASE_URL = "https://api.arbiscan.io/api"
POLYGONSCAN_BASE_URL = "https://api.polygonscan.com/api"
BSCSCAN_BASE_URL = "https://api.bscscan.com/api"
OPTIMISTIC_ETHERSCAN_BASE_URL = "https://api-optimistic.etherscan.io/api"

# Rate limiting
ETHERSCAN_RATE_LIMIT = 5  # requests per second
DEFAULT_TIMEOUT = 30  # seconds

# Clustering Parameters
class ClusteringConfig:
    # Union-Find heuristics
    GAS_FUNDING_THRESHOLD = 0.01  # ETH
    TEMPORAL_WINDOW_SECONDS = 60
    
    # DBSCAN parameters
    DBSCAN_EPS = 0.5
    DBSCAN_MIN_SAMPLES = 3
    
# Bridge Event Matching
class BridgeConfig:
    AMOUNT_TOLERANCE = 0.005  # 0.5%
    TIMESTAMP_WINDOW_MINUTES = 15
    
# Supported Chains
SUPPORTED_CHAINS = {
    "ethereum": {"name": "Ethereum", "chain_id": 1, "api_url": ETHERSCAN_BASE_URL},
    "arbitrum": {"name": "Arbitrum", "chain_id": 42161, "api_url": ARBISCAN_BASE_URL},
    "polygon": {"name": "Polygon", "chain_id": 137, "api_url": POLYGONSCAN_BASE_URL},
    "bsc": {"name": "BSC", "chain_id": 56, "api_url": BSCSCAN_BASE_URL},
    "optimism": {"name": "Optimism", "chain_id": 10, "api_url": OPTIMISTIC_ETHERSCAN_BASE_URL},
}

# Known Mixer Addresses (Tornado Cash)
KNOWN_MIXERS = [
    "0x12D66f87A04A989229Ee8cE45E76349E89908769",  # Tornado Cash: ETH
    "0x47CE0C6eD5B0Ce3d3A51fdb1C52DC66a7c3c2936",  # Tornado Cash: USDC
    "0x169AD27A470D064DEDE56a2D3FF72A98CeC41175",  # Tornado Cash: USDT
    "0xd90e2f925DA726b50C4Ed8D0Fb90Ad053316F5e2",  # Tornado Cash: DAI
    "0x5a7d6b2f92c77fad6ccabd7ee0624e64907eaf3e",  # Tornado Cash: WBTC
]

# Known VASP Addresses (sample - extend as needed)
KNOWN_VASPS = {
    "binance": [
        "0x28C6c06298d514Db089934071355E5743bf21d60",
        "0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549",
        "0xDFd5293D8e347dFe59E90eFd55b2956a1343963d",
    ],
    "coinbase": [
        "0x503828976D22510aad0201ac7EC88297663E8fe6",
        "0xA691f9e7E320a1A166aC4e6aB0bbCe502f7aB9D5",
    ],
    "kraken": [
        "0x267be1C1D684F78cb4F6a176C4911b741E4Ffdc0",
        "0x62628494e7478c8Bb12006Cf1272F8887eE760Cb",
    ],
}

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")
