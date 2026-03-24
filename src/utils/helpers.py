"""
Utility functions for the Blockchain Forensics Tool.
"""

import hashlib
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd


def normalize_address(address: str) -> str:
    """Normalize Ethereum address to lowercase with 0x prefix."""
    if not address:
        return ""
    addr = address.lower().strip()
    if not addr.startswith("0x"):
        addr = "0x" + addr
    return addr


def generate_fingerprint(*args) -> str:
    """Generate a unique fingerprint hash from input values."""
    data = "|".join(str(arg) for arg in args)
    return hashlib.sha256(data.encode()).hexdigest()


def save_json(data: Any, filepath: str) -> None:
    """Save data to JSON file with proper formatting."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def load_json(filepath: str) -> Any:
    """Load data from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def save_csv(df: pd.DataFrame, filepath: str) -> None:
    """Save DataFrame to CSV file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)


def load_csv(filepath: str) -> pd.DataFrame:
    """Load DataFrame from CSV file."""
    return pd.read_csv(filepath)


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def format_eth(value_wei: int) -> float:
    """Convert Wei to ETH."""
    return float(value_wei) / 1e18


def format_token(value: int, decimals: int = 18) -> float:
    """Convert token value with decimals to float."""
    return float(value) / (10 ** decimals)


def wei_to_usd(value_wei: int, price_usd: float) -> float:
    """Convert Wei value to USD given ETH price."""
    eth_value = format_eth(value_wei)
    return eth_value * price_usd


def is_valid_address(address: str) -> bool:
    """Check if address is a valid Ethereum address format."""
    if not address:
        return False
    addr = normalize_address(address)
    return len(addr) == 42 and addr.startswith("0x") and all(c in "0123456789abcdef" for c in addr[2:])


def create_evidence_record(
    data_type: str,
    source: str,
    seed_address: str,
    chain: str = "ethereum",
    additional_metadata: Optional[Dict] = None
) -> Dict:
    """Create a chain-of-custody evidence record."""
    record = {
        "evidence_id": generate_fingerprint(data_type, source, seed_address, get_timestamp()),
        "data_type": data_type,
        "source": source,
        "seed_address": normalize_address(seed_address),
        "chain": chain,
        "retrieval_timestamp": get_timestamp(),
        "retrieved_by": "blockchain_forensics_tool_v2.0",
        "integrity_hash": None,  # Will be set after data processing
    }
    if additional_metadata:
        record.update(additional_metadata)
    return record


def min_max_scale(value: float, min_val: float, max_val: float) -> float:
    """Apply min-max scaling to a value."""
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safe division with default value for zero denominator."""
    if denominator == 0:
        return default
    return numerator / denominator
