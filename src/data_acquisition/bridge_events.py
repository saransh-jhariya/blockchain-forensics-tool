"""
Phase 1: Multi-Source Data Acquisition
Bridge Event Logs and Cross-Chain Data.
"""

import hashlib
from typing import Dict, List, Optional

from web3 import Web3

from config.settings import (
    SUPPORTED_CHAINS,
)
from src.data_acquisition.etherscan_client import EtherscanClient
from src.utils.helpers import create_evidence_record, format_token, normalize_address, save_json
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Bridge Contract Addresses (mainnet)
BRIDGE_CONTRACTS = {
    "wormhole": {
        "ethereum": {
            "bridge": "0x3ee18B2214AFF97000D974cf647E7C347E8fa585",  # Wormhole Token Bridge
            "core": "0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B",  # Wormhole Core
        },
        "arbitrum": {
            "bridge": "0x0b2402144Bb366A632D14B83F244D2e0e21bD39c",
        },
        "polygon": {
            "bridge": "0x5a58505a96D1dbf8dF91cB21B54419FC36e93fdE",
        },
    },
    "stargate": {
        "ethereum": {
            "router": "0x8731d54E9D02c286767d56ac0328037C37801557",  # Stargate Router
            "usdt_pool": "0x38EA452219524Bb87e18dE1C24D3bB59510BD783",
            "usdc_pool": "0x3221022e37029923aCe4235D812273C5A42C322d",
        },
        "arbitrum": {
            "router": "0x53Bf833A5d6c4ddA888F69c22C88C9f356a41614",
        },
        "polygon": {
            "router": "0x45A01E4e04F14f7A4a6702c74187c5F6222033cd",
        },
        "optimism": {
            "router": "0xB0D502E938ed5f4df2E681fE6E419ff29631d62b",
        },
    },
    "across": {
        "ethereum": {
            "hub_pool": "0xc186fA914353c44b2E33eBE05f21846F1048bEda",
            "spoke_pool": "0x5c7BCd6E7De5423a257D81B442095A1a6ced35C5",
        },
        "arbitrum": {
            "spoke_pool": "0xe35e9842fceaca96570b734083f4a58e8f7c5f2a",
        },
        "polygon": {
            "spoke_pool": "0x929526c8c8b3f504b03a597e0e362259a3704f7e",
        },
    },
}

# Bridge Event ABIs (simplified)
BRIDGE_EVENT_ABIS = {
    "lock": {
        "name": "TokensLocked",
        "inputs": [
            {"name": "sender", "type": "address", "indexed": True},
            {"name": "amount", "type": "uint256", "indexed": False},
            {"name": "toChainId", "type": "uint256", "indexed": False},
        ],
    },
    "mint": {
        "name": "TokensMinted",
        "inputs": [
            {"name": "recipient", "type": "address", "indexed": True},
            {"name": "amount", "type": "uint256", "indexed": False},
            {"name": "fromChainId", "type": "uint256", "indexed": False},
        ],
    },
    "burn": {
        "name": "TokensBurned",
        "inputs": [
            {"name": "sender", "type": "address", "indexed": True},
            {"name": "amount", "type": "uint256", "indexed": False},
            {"name": "toChainId", "type": "uint256", "indexed": False},
        ],
    },
    "transfer": {
        "name": "Transfer",
        "inputs": [
            {"name": "from", "type": "address", "indexed": True},
            {"name": "to", "type": "address", "indexed": True},
            {"name": "value", "type": "uint256", "indexed": False},
        ],
    },
}


class BridgeEventFetcher:
    """Fetches bridge event logs from multiple chains."""
    
    def __init__(self, chain: str = "ethereum", rpc_url: Optional[str] = None):
        """
        Initialize bridge event fetcher.
        
        Args:
            chain: Chain name
            rpc_url: RPC endpoint URL (optional, uses public if not provided)
        """
        self.chain = chain
        self.rpc_url = rpc_url or self._get_public_rpc(chain)
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url)) if self.rpc_url else None
        
        if self.w3 and not self.w3.is_connected():
            logger.warning(f"Could not connect to RPC endpoint for {chain}")
            self.w3 = None
    
    def _get_public_rpc(self, chain: str) -> Optional[str]:
        """Get public RPC URL for a chain."""
        public_rpcs = {
            "ethereum": "https://eth.llamarpc.com",
            "arbitrum": "https://arb1.arbitrum.io/rpc",
            "polygon": "https://polygon-rpc.com",
            "bsc": "https://bsc-dataseed.binance.org",
            "optimism": "https://mainnet.optimism.io",
        }
        return public_rpcs.get(chain)
    
    def fetch_bridge_events_for_address(self, address: str) -> List[Dict]:
        """
        Fetch bridge events involving an address.
        
        Args:
            address: Ethereum address
            
        Returns:
            List of bridge event dictionaries
        """
        address = normalize_address(address)
        events = []
        
        if not self.w3:
            logger.warning("Web3 not initialized, using API-based fetching")
            return self._fetch_bridge_events_via_api(address)
        
        # Fetch events from known bridge contracts
        for bridge_name, contracts in BRIDGE_CONTRACTS.items():
            if self.chain not in contracts:
                continue
            
            contract_address = contracts[self.chain].get("bridge") or contracts[self.chain].get("router")
            if not contract_address:
                continue
            
            try:
                contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(contract_address),
                    abi=[BRIDGE_EVENT_ABIS["lock"], BRIDGE_EVENT_ABIS["mint"], BRIDGE_EVENT_ABIS["burn"]]
                )
                
                # Fetch events (last 10000 blocks for demo - adjust as needed)
                latest_block = self.w3.eth.block_number
                from_block = max(0, latest_block - 10000)
                
                # Lock events
                lock_events = contract.events.TokensLocked.get_logs(
                    fromBlock=from_block,
                    toBlock=latest_block,
                    argument_filters={"sender": address}
                )
                for event in lock_events:
                    events.append({
                        "event_type": "lock",
                        "bridge": bridge_name,
                        "chain": self.chain,
                        "address": address,
                        "amount": str(event["args"]["amount"]),
                        "to_chain_id": event["args"]["toChainId"],
                        "block_number": event["blockNumber"],
                        "transaction_hash": event["transactionHash"].hex(),
                        "timestamp": self.w3.eth.get_block(event["blockNumber"])["timestamp"],
                    })
                
                # Mint events
                mint_events = contract.events.TokensMinted.get_logs(
                    fromBlock=from_block,
                    toBlock=latest_block,
                    argument_filters={"recipient": address}
                )
                for event in mint_events:
                    events.append({
                        "event_type": "mint",
                        "bridge": bridge_name,
                        "chain": self.chain,
                        "address": address,
                        "amount": str(event["args"]["amount"]),
                        "from_chain_id": event["args"]["fromChainId"],
                        "block_number": event["blockNumber"],
                        "transaction_hash": event["transactionHash"].hex(),
                        "timestamp": self.w3.eth.get_block(event["blockNumber"])["timestamp"],
                    })
                
            except Exception as e:
                logger.debug(f"Error fetching {bridge_name} events: {e}")
        
        return events
    
    def _fetch_bridge_events_via_api(self, address: str) -> List[Dict]:
        """Fetch bridge events via Etherscan API (fallback method)."""
        client = EtherscanClient(chain=self.chain)
        events = []
        
        # Get ERC-20 transfers involving bridge contracts
        transfers = client.get_erc20_transfers(address)
        
        for bridge_name, contracts in BRIDGE_CONTRACTS.items():
            if self.chain not in contracts:
                continue
            
            bridge_addresses = [
                contracts[self.chain].get("bridge"),
                contracts[self.chain].get("router"),
                contracts[self.chain].get("hub_pool"),
                contracts[self.chain].get("spoke_pool"),
            ]
            bridge_addresses = [normalize_address(a) for a in bridge_addresses if a]
            
            for tx in transfers:
                if normalize_address(tx.get("from", "")) in bridge_addresses or \
                   normalize_address(tx.get("to", "")) in bridge_addresses:
                    events.append({
                        "event_type": "bridge_transfer",
                        "bridge": bridge_name,
                        "chain": self.chain,
                        "address": address,
                        "amount": tx.get("value", "0"),
                        "token": tx.get("tokenSymbol", "UNKNOWN"),
                        "counterparty": tx.get("from" if tx.get("to", "").lower() == address.lower() else "to"),
                        "block_number": tx.get("blockNumber"),
                        "transaction_hash": tx.get("hash"),
                        "timestamp": tx.get("timeStamp"),
                    })
        
        return events


class DataAcquisitionLayer2:
    """
    Layer 2: Bridge Event Logs
    Fetches cross-chain bridge events for tracing funds across chains.
    """
    
    def __init__(self, chain: str = "ethereum", output_dir: Optional[str] = None):
        """
        Initialize Layer 2 data acquisition.
        
        Args:
            chain: Chain name
            output_dir: Directory for storing raw data
        """
        self.chain = chain
        self.fetcher = BridgeEventFetcher(chain=chain)
        self.output_dir = output_dir
        self.evidence_records = []
    
    def fetch_bridge_events(self, addresses: List[str]) -> Dict:
        """
        Fetch bridge events for multiple addresses.
        
        Args:
            addresses: List of addresses to fetch bridge events for
            
        Returns:
            Dictionary of address -> bridge events
        """
        logger.info(f"Fetching bridge events for {len(addresses)} addresses on {self.chain}")
        
        all_events = {}
        for address in addresses:
            address = normalize_address(address)
            events = self.fetcher.fetch_bridge_events_for_address(address)
            if events:
                all_events[address] = events
        
        # Create evidence record
        evidence = create_evidence_record(
            data_type="bridge_events",
            source="bridge_contracts",
            seed_address=",".join(addresses[:5]),  # First 5 addresses
            chain=self.chain,
            additional_metadata={
                "total_addresses": len(addresses),
                "addresses_with_events": len(all_events),
                "total_events": sum(len(evts) for evts in all_events.values()),
            }
        )
        self.evidence_records.append(evidence)
        
        result = {
            "chain": self.chain,
            "bridge_events": all_events,
            "evidence_record": evidence,
        }
        
        # Save raw data
        if self.output_dir:
            filepath = f"{self.output_dir}/layer2_bridge_{self.chain}.json"
            save_json(result, filepath)
            logger.info(f"Bridge events saved to {filepath}")
        
        return result
