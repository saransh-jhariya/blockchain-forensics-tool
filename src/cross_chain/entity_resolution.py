"""
Phase 4: Cross-Chain Entity Resolution
Bridge Event Correlation, DEX Swap Tracing, and Multi-Chain Entity Stitching.
"""

import hashlib
from typing import Dict, List, Optional, Set, Tuple

from src.data_acquisition.bridge_events import BRIDGE_CONTRACTS
from src.utils.helpers import format_eth, generate_fingerprint, normalize_address
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BridgeEventCorrelator:
    """
    Correlates bridge events across chains to trace cross-chain fund movements.
    
    Matching rules:
    - Token amount: ±0.5% tolerance for bridge fees
    - Timestamp window: Lock and mint events within 5-15 minutes
    - Value fingerprint: Hash of (source address, amount, token type)
    """
    
    def __init__(
        self,
        amount_tolerance: float = 0.005,
        timestamp_window_minutes: int = 15,
    ):
        """
        Initialize bridge event correlator.
        
        Args:
            amount_tolerance: Tolerance for amount matching (0.5% = 0.005)
            timestamp_window_minutes: Maximum time window for matching events
        """
        self.amount_tolerance = amount_tolerance
        self.timestamp_window_seconds = timestamp_window_minutes * 60
        self.correlated_events = []
    
    def _amounts_match(self, amount1: int, amount2: int, tolerance: float = None) -> bool:
        """
        Check if two amounts match within tolerance.
        
        Args:
            amount1: First amount (in token smallest unit)
            amount2: Second amount
            tolerance: Tolerance fraction (default: self.amount_tolerance)
            
        Returns:
            True if amounts match within tolerance
        """
        if amount1 == 0 or amount2 == 0:
            return amount1 == amount2
        
        tolerance = tolerance or self.amount_tolerance
        diff_ratio = abs(amount1 - amount2) / max(amount1, amount2)
        return diff_ratio <= tolerance
    
    def _timestamps_match(self, ts1: int, ts2: int) -> bool:
        """
        Check if two timestamps are within the matching window.
        
        Args:
            ts1: First timestamp (Unix seconds)
            ts2: Second timestamp
            
        Returns:
            True if within window
        """
        return abs(ts1 - ts2) <= self.timestamp_window_seconds
    
    def correlate_bridge_events(
        self,
        bridge_events: Dict[str, List[Dict]],
    ) -> List[Dict]:
        """
        Correlate bridge events across chains.
        
        Args:
            bridge_events: Dictionary of chain -> list of bridge events
            
        Returns:
            List of correlated bridge event pairs
        """
        logger.info("Starting bridge event correlation across chains")
        
        # Separate events by type
        lock_events = []
        mint_events = []
        
        for chain, events in bridge_events.items():
            for event in events:
                event["chain"] = chain
                if event.get("event_type") == "lock":
                    lock_events.append(event)
                elif event.get("event_type") == "mint":
                    mint_events.append(event)
                elif event.get("event_type") == "bridge_transfer":
                    # Handle API-fetched events
                    lock_events.append(event)
                    mint_events.append(event)
        
        # Correlate lock and mint events
        correlations = []
        used_mint_indices = set()
        
        for lock_idx, lock_event in enumerate(lock_events):
            lock_amount = int(lock_event.get("amount", 0))
            lock_timestamp = int(lock_event.get("timestamp", 0))
            lock_chain = lock_event.get("chain", "")
            
            for mint_idx, mint_event in enumerate(mint_events):
                if mint_idx in used_mint_indices:
                    continue
                
                mint_amount = int(mint_event.get("amount", 0))
                mint_timestamp = int(mint_event.get("timestamp", 0))
                mint_chain = mint_event.get("chain", "")
                
                # Skip if same chain
                if lock_chain == mint_chain:
                    continue
                
                # Check amount match
                if not self._amounts_match(lock_amount, mint_amount):
                    continue
                
                # Check timestamp match
                if not self._timestamps_match(lock_timestamp, mint_timestamp):
                    continue
                
                # Create correlation record
                correlation = {
                    "correlation_id": generate_fingerprint(
                        lock_event.get("transaction_hash", ""),
                        mint_event.get("transaction_hash", "")
                    ),
                    "lock_event": lock_event,
                    "mint_event": mint_event,
                    "source_chain": lock_chain,
                    "destination_chain": mint_chain,
                    "amount": str(lock_amount),
                    "timestamp_lock": lock_timestamp,
                    "timestamp_mint": mint_timestamp,
                    "confidence": "high" if lock_amount == mint_amount else "medium",
                }
                
                correlations.append(correlation)
                used_mint_indices.add(mint_idx)
        
        self.correlated_events = correlations
        logger.info(f"Bridge event correlation complete: {len(correlations)} cross-chain transfers identified")
        
        return correlations
    
    def get_cross_chain_edges(self) -> List[Tuple[str, str, Dict]]:
        """
        Get cross-chain edges for graph construction.
        
        Returns:
            List of (source_address, destination_address, edge_attributes)
        """
        edges = []
        
        for correlation in self.correlated_events:
            lock_event = correlation.get("lock_event", {})
            mint_event = correlation.get("mint_event", {})
            
            source_addr = normalize_address(lock_event.get("address", ""))
            dest_addr = normalize_address(mint_event.get("address", ""))
            
            if source_addr and dest_addr:
                edges.append((
                    source_addr,
                    dest_addr,
                    {
                        "edge_type": "cross_chain_bridge",
                        "source_chain": correlation.get("source_chain"),
                        "destination_chain": correlation.get("destination_chain"),
                        "amount": correlation.get("amount"),
                        "bridge": lock_event.get("bridge", "unknown"),
                        "confidence": correlation.get("confidence"),
                    }
                ))
        
        return edges


class DEXSwapTracer:
    """
    Traces DEX swaps to maintain entity labels through token exchanges.
    
    Captures Swap events from major AMMs:
    - Uniswap V2/V3
    - Curve
    - Balancer
    """
    
    def __init__(self):
        """Initialize DEX swap tracer."""
        # Known DEX router addresses
        self.dex_routers = {
            "uniswap_v2": {
                "router": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
            },
            "uniswap_v3": {
                "router": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
            },
            "curve": {
                "registry": "0x90E00ACe148ca3b23Ac1bC8C240C2a7Dd9c2d7f5",
            },
            "balancer": {
                "vault": "0xBA12222222228d8Ba445958a75a0704d566BF2C8",
            },
        }
        self.swap_events = []
    
    def extract_swaps_from_transactions(
        self,
        normal_txs: List[Dict],
        internal_txs: List[Dict],
        erc20_txs: List[Dict],
    ) -> List[Dict]:
        """
        Extract potential DEX swap events from transaction data.
        
        Args:
            normal_txs: Normal transactions
            internal_txs: Internal transactions
            erc20_txs: ERC-20 token transfers
            
        Returns:
            List of identified swap events
        """
        logger.info("Extracting DEX swap events from transaction data")
        
        swaps = []
        
        # Group ERC-20 transfers by transaction hash
        tx_transfers = {}
        for tx in erc20_txs:
            tx_hash = tx.get("hash", "")
            if tx_hash not in tx_transfers:
                tx_transfers[tx_hash] = []
            tx_transfers[tx_hash].append(tx)
        
        # Look for swap patterns: multiple token transfers in same transaction
        for tx_hash, transfers in tx_transfers.items():
            if len(transfers) >= 2:
                # Potential swap - check for token-to-token pattern
                tokens_in = []
                tokens_out = []
                addresses_involved = set()
                
                for transfer in transfers:
                    from_addr = normalize_address(transfer.get("from", ""))
                    to_addr = normalize_address(transfer.get("to", ""))
                    token_symbol = transfer.get("tokenSymbol", "")
                    value = transfer.get("value", "0")
                    
                    addresses_involved.add(from_addr)
                    addresses_involved.add(to_addr)
                    
                    # Simple heuristic: transfers from user are input, to user are output
                    if from_addr in self.dex_routers.values():
                        tokens_out.append({"token": token_symbol, "value": value})
                    elif to_addr in self.dex_routers.values():
                        tokens_in.append({"token": token_symbol, "value": value})
                
                if tokens_in and tokens_out:
                    swap = {
                        "transaction_hash": tx_hash,
                        "tokens_in": tokens_in,
                        "tokens_out": tokens_out,
                        "addresses_involved": list(addresses_involved),
                        "dex": self._identify_dex(transfers),
                        "block_number": transfers[0].get("blockNumber"),
                        "timestamp": transfers[0].get("timeStamp"),
                    }
                    swaps.append(swap)
        
        self.swap_events = swaps
        logger.info(f"Identified {len(swaps)} potential DEX swaps")
        
        return swaps
    
    def _identify_dex(self, transfers: List[Dict]) -> str:
        """Identify which DEX was used based on transfer patterns."""
        for transfer in transfers:
            to_addr = normalize_address(transfer.get("to", ""))
            from_addr = normalize_address(transfer.get("from", ""))
            
            for dex_name, contracts in self.dex_routers.items():
                if to_addr in [normalize_address(v) for v in contracts.values()] or \
                   from_addr in [normalize_address(v) for v in contracts.values()]:
                    return dex_name
        
        return "unknown"
    
    def get_swap_edges(self) -> List[Tuple[str, str, Dict]]:
        """
        Get edges representing DEX swaps for graph construction.
        
        Returns:
            List of (address1, address2, edge_attributes)
        """
        edges = []
        
        for swap in self.swap_events:
            addresses = swap.get("addresses_involved", [])
            for i, addr1 in enumerate(addresses):
                for addr2 in addresses[i+1:]:
                    edges.append((
                        addr1,
                        addr2,
                        {
                            "edge_type": "dex_swap",
                            "dex": swap.get("dex"),
                            "tokens_in": swap.get("tokens_in"),
                            "tokens_out": swap.get("tokens_out"),
                            "transaction_hash": swap.get("transaction_hash"),
                        }
                    ))
        
        return edges


class MultiChainEntityStitcher:
    """
    Stitches entity clusters across multiple EVM-compatible chains.
    
    Combines clusters from Ethereum, Arbitrum, Polygon, BSC, and Optimism
    into a unified forensic graph.
    """
    
    def __init__(self):
        """Initialize multi-chain entity stitcher."""
        self.unified_clusters = {}
        self.chain_to_unified_mapping = {}
    
    def stitch_clusters(
        self,
        chain_clusters: Dict[str, Dict[str, List[str]]],
        bridge_correlations: List[Dict],
    ) -> Dict[str, List[str]]:
        """
        Stitch clusters from multiple chains into unified entities.
        
        Args:
            chain_clusters: Dictionary of chain -> cluster_id -> addresses
            bridge_correlations: List of correlated bridge events
            
        Returns:
            Unified clusters spanning multiple chains
        """
        logger.info("Starting multi-chain entity stitching")
        
        # Use Union-Find to merge clusters across chains
        from src.clustering.rule_based_clustering import UnionFind
        uf = UnionFind()
        
        # First, add all addresses and union within-chain clusters
        for chain, clusters in chain_clusters.items():
            for cluster_id, addresses in clusters.items():
                chain_cluster_key = f"{chain}:{cluster_id}"
                for addr in addresses:
                    addr_key = f"{chain}:{normalize_address(addr)}"
                    uf.find(addr_key)
                    # Union all addresses in same chain cluster
                    for other_addr in addresses:
                        other_key = f"{chain}:{normalize_address(other_addr)}"
                        uf.union(addr_key, other_key)
        
        # Then, union addresses connected by bridge correlations
        for correlation in bridge_correlations:
            source_chain = correlation.get("source_chain")
            dest_chain = correlation.get("destination_chain")
            
            lock_event = correlation.get("lock_event", {})
            mint_event = correlation.get("mint_event", {})
            
            source_addr = normalize_address(lock_event.get("address", ""))
            dest_addr = normalize_address(mint_event.get("address", ""))
            
            if source_addr and dest_addr:
                source_key = f"{source_chain}:{source_addr}"
                dest_key = f"{dest_chain}:{dest_addr}"
                uf.union(source_key, dest_key)
        
        # Extract unified clusters
        unified = uf.get_clusters()
        
        # Convert back to address lists
        result = {}
        for root, members in unified.items():
            # Parse chain:address format
            chain_addresses = {}
            for member in members:
                if ":" in member:
                    chain, addr = member.split(":", 1)
                    if chain not in chain_addresses:
                        chain_addresses[chain] = []
                    chain_addresses[chain].append(addr)
            
            # Create unified cluster ID
            cluster_id = f"entity_{hashlib.sha256(','.join(sorted(members)).encode()).hexdigest()[:12]}"
            result[cluster_id] = {
                "addresses": chain_addresses,
                "total_addresses": len(members),
                "chains_involved": list(chain_addresses.keys()),
            }
        
        self.unified_clusters = result
        logger.info(f"Multi-chain stitching complete: {len(result)} unified entities")
        
        return result
    
    def get_unified_graph_data(self) -> Dict:
        """
        Get data for unified forensic graph.
        
        Returns:
            Dictionary containing unified graph data
        """
        return {
            "entities": self.unified_clusters,
            "total_entities": len(self.unified_clusters),
            "multi_chain_entities": sum(
                1 for e in self.unified_clusters.values()
                if len(e.get("chains_involved", [])) > 1
            ),
        }


class CrossChainEntityResolution:
    """
    Phase 4: Cross-Chain Entity Resolution
    Complete pipeline for cross-chain tracing and entity stitching.
    """
    
    def __init__(
        self,
        amount_tolerance: float = 0.005,
        timestamp_window_minutes: int = 15,
    ):
        """
        Initialize Phase 4 pipeline.
        
        Args:
            amount_tolerance: Bridge amount matching tolerance
            timestamp_window_minutes: Bridge timestamp matching window
        """
        self.bridge_correlator = BridgeEventCorrelator(
            amount_tolerance=amount_tolerance,
            timestamp_window_minutes=timestamp_window_minutes,
        )
        self.dex_tracer = DEXSwapTracer()
        self.entity_stitcher = MultiChainEntityStitcher()
    
    def resolve(
        self,
        chain_data: Dict[str, Dict],
        chain_clusters: Dict[str, Dict[str, List[str]]],
    ) -> Dict:
        """
        Run complete cross-chain entity resolution pipeline.
        
        Args:
            chain_data: Dictionary of chain -> transaction and bridge data
            chain_clusters: Dictionary of chain -> clustering results
            
        Returns:
            Unified forensic graph data
        """
        logger.info("=" * 60)
        logger.info("Phase 4: Cross-Chain Entity Resolution")
        logger.info("=" * 60)
        
        # Step 1: Collect bridge events from all chains
        all_bridge_events = {}
        for chain, data in chain_data.items():
            bridge_events = data.get("bridge_events", {})
            if bridge_events:
                all_bridge_events[chain] = bridge_events
        
        # Step 2: Correlate bridge events across chains
        bridge_correlations = self.bridge_correlator.correlate_bridge_events(
            all_bridge_events
        )
        
        # Step 3: Extract DEX swaps
        all_swaps = []
        for chain, data in chain_data.items():
            normal_txs = data.get("normal_transactions", [])
            internal_txs = data.get("internal_transactions", [])
            erc20_txs = data.get("erc20_transfers", [])
            
            swaps = self.dex_tracer.extract_swaps_from_transactions(
                normal_txs, internal_txs, erc20_txs
            )
            all_swaps.extend(swaps)
        
        # Step 4: Stitch entities across chains
        unified_entities = self.entity_stitcher.stitch_clusters(
            chain_clusters=chain_clusters,
            bridge_correlations=bridge_correlations,
        )
        
        # Compile results
        results = {
            "unified_entities": unified_entities,
            "bridge_correlations": bridge_correlations,
            "dex_swaps": all_swaps,
            "cross_chain_edges": self.bridge_correlator.get_cross_chain_edges(),
            "dex_edges": self.dex_tracer.get_swap_edges(),
            "summary": self.entity_stitcher.get_unified_graph_data(),
        }
        
        logger.info("=" * 60)
        logger.info(f"Phase 4 Complete: {results['summary']['total_entities']} entities, "
                   f"{results['summary']['multi_chain_entities']} multi-chain")
        logger.info("=" * 60)
        
        return results
