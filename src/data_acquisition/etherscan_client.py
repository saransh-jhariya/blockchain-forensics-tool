"""
Phase 1: Multi-Source Data Acquisition
Etherscan API client for fetching on-chain transaction data.
"""

import time
from typing import Dict, List, Optional

import requests
from tqdm import tqdm

from config.settings import (
    DEFAULT_TIMEOUT,
    ETHERSCAN_API_KEY,
    ETHERSCAN_BASE_URL,
    ETHERSCAN_RATE_LIMIT,
    SUPPORTED_CHAINS,
)
from src.utils.helpers import create_evidence_record, normalize_address, save_json
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class EtherscanClient:
    """Client for interacting with Etherscan and compatible block explorers."""
    
    def __init__(self, chain: str = "ethereum", api_key: Optional[str] = None):
        """
        Initialize the Etherscan client.
        
        Args:
            chain: Chain name (ethereum, arbitrum, polygon, bsc, optimism)
            api_key: API key (defaults to ETHERSCAN_API_KEY from settings)
        """
        if chain not in SUPPORTED_CHAINS:
            raise ValueError(f"Unsupported chain: {chain}. Supported: {list(SUPPORTED_CHAINS.keys())}")
        
        self.chain = chain
        self.chain_config = SUPPORTED_CHAINS[chain]
        self.api_key = api_key or ETHERSCAN_API_KEY
        self.base_url = self.chain_config["api_url"]
        self.last_request_time = 0
        
        if not self.api_key:
            logger.warning("No API key provided. Some endpoints may be rate-limited.")
    
    def _rate_limit(self):
        """Apply rate limiting to API requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < 1.0 / ETHERSCAN_RATE_LIMIT:
            time.sleep(1.0 / ETHERSCAN_RATE_LIMIT - elapsed)
        self.last_request_time = time.time()
    
    def _make_request(self, params: Dict) -> Dict:
        """
        Make an API request with error handling and rate limiting.
        
        Args:
            params: Query parameters
            
        Returns:
            JSON response as dictionary
        """
        self._rate_limit()
        
        params["apikey"] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "0" and data.get("message") == "NOTOK":
                logger.warning(f"API returned error: {data.get('result', 'Unknown error')}")
                return {"result": []}
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {"result": []}
    
    def get_normal_transactions(
        self,
        address: str,
        start_block: int = 0,
        end_block: int = 99999999,
        page: int = 1,
        offset: int = 10000
    ) -> List[Dict]:
        """
        Fetch normal ETH transactions for an address.
        
        Args:
            address: Ethereum address
            start_block: Starting block number
            end_block: Ending block number
            page: Page number for pagination
            offset: Number of records per page (max 10000)
            
        Returns:
            List of transaction dictionaries
        """
        address = normalize_address(address)
        logger.info(f"Fetching normal transactions for {address} on {self.chain}")
        
        params = {
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "page": page,
            "offset": offset,
            "sort": "asc",
        }
        
        data = self._make_request(params)
        return data.get("result", [])
    
    def get_internal_transactions(
        self,
        address: str,
        start_block: int = 0,
        end_block: int = 99999999,
    ) -> List[Dict]:
        """
        Fetch internal transactions for an address.
        
        Args:
            address: Ethereum address
            start_block: Starting block number
            end_block: Ending block number
            
        Returns:
            List of internal transaction dictionaries
        """
        address = normalize_address(address)
        logger.info(f"Fetching internal transactions for {address} on {self.chain}")
        
        params = {
            "module": "account",
            "action": "txlistinternal",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "page": 1,
            "offset": 10000,
            "sort": "asc",
        }
        
        data = self._make_request(params)
        return data.get("result", [])
    
    def get_erc20_transfers(
        self,
        address: str,
        start_block: int = 0,
        end_block: int = 99999999,
    ) -> List[Dict]:
        """
        Fetch ERC-20 token transfers for an address.
        
        Args:
            address: Ethereum address
            start_block: Starting block number
            end_block: Ending block number
            
        Returns:
            List of ERC-20 transfer dictionaries
        """
        address = normalize_address(address)
        logger.info(f"Fetching ERC-20 transfers for {address} on {self.chain}")
        
        params = {
            "module": "account",
            "action": "tokentx",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "page": 1,
            "offset": 10000,
            "sort": "asc",
        }
        
        data = self._make_request(params)
        return data.get("result", [])
    
    def get_erc721_transfers(
        self,
        address: str,
        start_block: int = 0,
        end_block: int = 99999999,
    ) -> List[Dict]:
        """
        Fetch ERC-721 NFT transfers for an address.
        
        Args:
            address: Ethereum address
            start_block: Starting block number
            end_block: Ending block number
            
        Returns:
            List of ERC-721 transfer dictionaries
        """
        address = normalize_address(address)
        logger.info(f"Fetching ERC-721 transfers for {address} on {self.chain}")
        
        params = {
            "module": "account",
            "action": "tokennfttx",
            "address": address,
            "startblock": start_block,
            "endblock": end_block,
            "page": 1,
            "offset": 10000,
            "sort": "asc",
        }
        
        data = self._make_request(params)
        return data.get("result", [])
    
    def get_balance(self, address: str) -> Dict:
        """
        Get ETH balance for an address.
        
        Args:
            address: Ethereum address
            
        Returns:
            Dictionary with balance information
        """
        address = normalize_address(address)
        
        params = {
            "module": "account",
            "action": "balance",
            "address": address,
            "tag": "latest",
        }
        
        data = self._make_request(params)
        return {
            "address": address,
            "balance_wei": data.get("result", "0"),
            "balance_eth": int(data.get("result", "0")) / 1e18,
        }
    
    def get_contract_abi(self, contract_address: str) -> List[Dict]:
        """
        Get ABI for a smart contract.
        
        Args:
            contract_address: Contract address
            
        Returns:
            List of ABI entries
        """
        contract_address = normalize_address(contract_address)
        
        params = {
            "module": "contract",
            "action": "getabi",
            "address": contract_address,
        }
        
        data = self._make_request(params)
        import json
        try:
            return json.loads(data.get("result", "[]"))
        except json.JSONDecodeError:
            return []


class DataAcquisitionLayer1:
    """
    Layer 1: On-Chain Transaction Pull
    Fetches all transaction data from Etherscan APIs.
    """
    
    def __init__(self, chain: str = "ethereum", output_dir: Optional[str] = None):
        """
        Initialize the data acquisition layer.
        
        Args:
            chain: Chain name
            output_dir: Directory for storing raw data
        """
        self.chain = chain
        self.client = EtherscanClient(chain=chain)
        self.output_dir = output_dir
        self.evidence_records = []
    
    def fetch_all_transactions(self, seed_address: str) -> Dict:
        """
        Fetch all transaction types for a seed address.
        
        Args:
            seed_address: Seed Ethereum address
            
        Returns:
            Dictionary containing all transaction data
        """
        seed_address = normalize_address(seed_address)
        logger.info(f"Starting Layer 1 data acquisition for {seed_address} on {self.chain}")
        
        # Fetch all transaction types
        normal_txs = self.client.get_normal_transactions(seed_address)
        internal_txs = self.client.get_internal_transactions(seed_address)
        erc20_txs = self.client.get_erc20_transfers(seed_address)
        
        # Collect all unique addresses involved
        all_addresses = set()
        all_addresses.add(seed_address)
        
        for tx in normal_txs:
            all_addresses.add(normalize_address(tx.get("from", "")))
            all_addresses.add(normalize_address(tx.get("to", "")))
        
        for tx in internal_txs:
            all_addresses.add(normalize_address(tx.get("from", "")))
            all_addresses.add(normalize_address(tx.get("to", "")))
        
        for tx in erc20_txs:
            all_addresses.add(normalize_address(tx.get("from", "")))
            all_addresses.add(normalize_address(tx.get("to", "")))
        
        # Create evidence record
        evidence = create_evidence_record(
            data_type="on_chain_transactions",
            source="etherscan_api",
            seed_address=seed_address,
            chain=self.chain,
            additional_metadata={
                "normal_tx_count": len(normal_txs),
                "internal_tx_count": len(internal_txs),
                "erc20_tx_count": len(erc20_txs),
                "unique_addresses": len(all_addresses),
            }
        )
        self.evidence_records.append(evidence)
        
        result = {
            "seed_address": seed_address,
            "chain": self.chain,
            "normal_transactions": normal_txs,
            "internal_transactions": internal_txs,
            "erc20_transfers": erc20_txs,
            "all_addresses": list(all_addresses),
            "evidence_record": evidence,
        }
        
        # Save raw data
        if self.output_dir:
            filepath = f"{self.output_dir}/layer1_{self.chain}_{seed_address}.json"
            save_json(result, filepath)
            logger.info(f"Raw data saved to {filepath}")
        
        return result
    
    def fetch_counterparty_transactions(self, addresses: List[str], max_addresses: int = 100) -> Dict:
        """
        Fetch transactions for counterparties (addresses that interacted with seed).
        
        Args:
            addresses: List of addresses to fetch
            max_addresses: Maximum number of addresses to process
            
        Returns:
            Dictionary of address -> transaction data
        """
        addresses = [normalize_address(a) for a in addresses[:max_addresses]]
        result = {}
        
        logger.info(f"Fetching transactions for {len(addresses)} counterparties")
        
        for addr in tqdm(addresses, desc="Fetching counterparty data"):
            try:
                normal_txs = self.client.get_normal_transactions(addr)
                if normal_txs:  # Only store if we got data
                    result[addr] = {
                        "normal_transactions": normal_txs,
                    }
                time.sleep(0.2)  # Rate limiting
            except Exception as e:
                logger.warning(f"Failed to fetch data for {addr}: {e}")
        
        return result
