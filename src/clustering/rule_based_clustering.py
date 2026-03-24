"""
Phase 3: Dual Clustering Engine
Layer A: Rule-Based Clustering using Union-Find (Disjoint Set Union)
"""

from typing import Dict, List, Optional, Set, Tuple

from src.utils.helpers import format_eth, normalize_address
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class UnionFind:
    """
    Union-Find (Disjoint Set Union) data structure.
    Provides near-constant time complexity O(α(n)) for union and find operations.
    """
    
    def __init__(self):
        """Initialize Union-Find structure."""
        self.parent = {}
        self.rank = {}
        self.size = {}  # Track cluster sizes
    
    def find(self, x: str) -> str:
        """
        Find the representative (root) of the set containing x with path compression.
        
        Args:
            x: Element to find
            
        Returns:
            Representative element of the set
        """
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            self.size[x] = 1
        
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        
        return self.parent[x]
    
    def union(self, x: str, y: str) -> bool:
        """
        Union the sets containing x and y using union by rank.
        
        Args:
            x: First element
            y: Second element
            
        Returns:
            True if union was performed, False if already in same set
        """
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return False  # Already in same set
        
        # Union by rank
        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x
        
        self.parent[root_y] = root_x
        self.size[root_x] = self.size.get(root_x, 1) + self.size.get(root_y, 1)
        
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1
        
        return True
    
    def get_clusters(self) -> Dict[str, List[str]]:
        """
        Get all clusters as a dictionary.
        
        Returns:
            Dictionary of root -> list of addresses in cluster
        """
        clusters = {}
        for node in self.parent:
            root = self.find(node)
            if root not in clusters:
                clusters[root] = []
            clusters[root].append(node)
        return clusters
    
    def get_cluster_id(self, address: str) -> str:
        """
        Get the cluster ID (root) for an address.
        
        Args:
            address: Address to look up
            
        Returns:
            Cluster ID (root address)
        """
        return self.find(address)
    
    def are_connected(self, x: str, y: str) -> bool:
        """
        Check if two addresses are in the same cluster.
        
        Args:
            x: First address
            y: Second address
            
        Returns:
            True if in same cluster
        """
        return self.find(x) == self.find(y)
    
    def get_cluster_size(self, address: str) -> int:
        """
        Get the size of the cluster containing the address.
        
        Args:
            address: Address to check
            
        Returns:
            Number of addresses in the cluster
        """
        root = self.find(address)
        return self.size.get(root, 1)


class RuleBasedClustering:
    """
    Layer A: Rule-Based Clustering using Union-Find.
    
    Implements three heuristics:
    1. Gas Funding Source: Address A funds B (< 0.01 ETH) before B's first outgoing tx
    2. Deposit Address Reuse: Two addresses send to same VASP deposit address
    3. Temporal Co-Activity: Two addresses interact with same contract in same block
    """
    
    def __init__(
        self,
        gas_funding_threshold: float = 0.01,
        temporal_window_seconds: int = 60,
    ):
        """
        Initialize rule-based clustering.
        
        Args:
            gas_funding_threshold: ETH threshold for gas funding heuristic
            temporal_window_seconds: Time window for temporal co-activity
        """
        self.gas_funding_threshold = gas_funding_threshold
        self.temporal_window_seconds = temporal_window_seconds
        self.uf = UnionFind()
        self.heuristic_evidence = {
            "gas_funding": [],
            "deposit_reuse": [],
            "temporal_coactivity": [],
        }
    
    def apply_gas_funding_heuristic(
        self,
        normal_txs: List[Dict],
        internal_txs: List[Dict],
    ) -> int:
        """
        Apply gas funding source heuristic.
        
        Trigger: Address A sends small ETH (< 0.01 ETH) to Address B
                 before B's first outgoing transaction.
        
        Args:
            normal_txs: Normal transactions
            internal_txs: Internal transactions
            
        Returns:
            Number of unions performed
        """
        unions_count = 0
        
        # Combine all transactions
        all_txs = []
        for tx in normal_txs + internal_txs:
            from_addr = normalize_address(tx.get("from", ""))
            to_addr = normalize_address(tx.get("to", ""))
            value = int(tx.get("value", 0))
            value_eth = format_eth(value)
            timestamp = int(tx.get("timeStamp", 0))
            block_number = int(tx.get("blockNumber", 0))
            
            if from_addr and to_addr:
                all_txs.append({
                    "from": from_addr,
                    "to": to_addr,
                    "value_eth": value_eth,
                    "timestamp": timestamp,
                    "block_number": block_number,
                })
        
        # Sort by timestamp
        all_txs_sorted = sorted(all_txs, key=lambda x: x["timestamp"])
        
        # Track first outgoing transaction for each address
        first_outgoing_tx = {}
        
        for tx in all_txs_sorted:
            from_addr = tx["from"]
            to_addr = tx["to"]
            value_eth = tx["value_eth"]
            
            # Record first outgoing transaction
            if from_addr not in first_outgoing_tx:
                first_outgoing_tx[from_addr] = tx["timestamp"]
            
            # Check gas funding heuristic
            if (
                value_eth < self.gas_funding_threshold and
                to_addr not in first_outgoing_tx
            ):
                # This is a potential gas funding transaction
                self.uf.union(from_addr, to_addr)
                self.heuristic_evidence["gas_funding"].append({
                    "funder": from_addr,
                    "funded": to_addr,
                    "amount_eth": value_eth,
                    "timestamp": tx["timestamp"],
                    "block_number": tx["block_number"],
                })
                unions_count += 1
        
        logger.info(f"Gas funding heuristic: {unions_count} unions performed")
        return unions_count
    
    def apply_deposit_address_reuse_heuristic(
        self,
        normal_txs: List[Dict],
        erc20_txs: List[Dict],
        vasp_addresses: Set[str],
    ) -> int:
        """
        Apply deposit address reuse heuristic.
        
        Trigger: Two addresses both send funds to the same unique VASP deposit address.
        
        Args:
            normal_txs: Normal transactions
            erc20_txs: ERC-20 token transfers
            vasp_addresses: Set of known VASP addresses
            
        Returns:
            Number of unions performed
        """
        unions_count = 0
        
        # Map: VASP address -> set of addresses that sent to it
        vasp_senders = {}
        
        # Check normal transactions
        for tx in normal_txs:
            from_addr = normalize_address(tx.get("from", ""))
            to_addr = normalize_address(tx.get("to", ""))
            
            if to_addr in vasp_addresses:
                if to_addr not in vasp_senders:
                    vasp_senders[to_addr] = set()
                vasp_senders[to_addr].add(from_addr)
        
        # Check ERC-20 transfers
        for tx in erc20_txs:
            from_addr = normalize_address(tx.get("from", ""))
            to_addr = normalize_address(tx.get("to", ""))
            
            if to_addr in vasp_addresses:
                if to_addr not in vasp_senders:
                    vasp_senders[to_addr] = set()
                vasp_senders[to_addr].add(from_addr)
        
        # Union all addresses that sent to the same VASP address
        for vasp_addr, senders in vasp_senders.items():
            senders_list = list(senders)
            for i in range(1, len(senders_list)):
                self.uf.union(senders_list[0], senders_list[i])
                self.heuristic_evidence["deposit_reuse"].append({
                    "vasp_address": vasp_addr,
                    "address_1": senders_list[0],
                    "address_2": senders_list[i],
                })
                unions_count += 1
        
        logger.info(f"Deposit address reuse heuristic: {unions_count} unions performed")
        return unions_count
    
    def apply_temporal_coactivity_heuristic(
        self,
        normal_txs: List[Dict],
        internal_txs: List[Dict],
    ) -> int:
        """
        Apply temporal co-activity heuristic.
        
        Trigger: Two addresses interact with the same contract within the same block
                 or within a temporal window.
        
        Args:
            normal_txs: Normal transactions
            internal_txs: Internal transactions
            
        Returns:
            Number of unions performed
        """
        unions_count = 0
        
        # Group transactions by block number
        block_transactions = {}
        
        for tx in normal_txs + internal_txs:
            from_addr = normalize_address(tx.get("from", ""))
            to_addr = normalize_address(tx.get("to", ""))
            block_number = int(tx.get("blockNumber", 0))
            timestamp = int(tx.get("timeStamp", 0))
            
            if block_number not in block_transactions:
                block_transactions[block_number] = []
            
            block_transactions[block_number].append({
                "from": from_addr,
                "to": to_addr,
                "timestamp": timestamp,
            })
        
        # For each block, find addresses interacting with same contract
        for block_num, txs in block_transactions.items():
            # Group by "to" address (potential contract)
            contract_interactions = {}
            
            for tx in txs:
                to_addr = tx["to"]
                from_addr = tx["from"]
                
                if to_addr not in contract_interactions:
                    contract_interactions[to_addr] = []
                contract_interactions[to_addr].append(from_addr)
            
            # Union addresses interacting with same contract in same block
            for contract_addr, interactors in contract_interactions.items():
                if len(interactors) > 1:
                    interactors_unique = list(set(interactors))
                    for i in range(1, len(interactors_unique)):
                        self.uf.union(interactors_unique[0], interactors_unique[i])
                        self.heuristic_evidence["temporal_coactivity"].append({
                            "contract": contract_addr,
                            "address_1": interactors_unique[0],
                            "address_2": interactors_unique[i],
                            "block_number": block_num,
                        })
                        unions_count += 1
        
        logger.info(f"Temporal co-activity heuristic: {unions_count} unions performed")
        return unions_count
    
    def cluster(
        self,
        addresses: List[str],
        normal_txs: List[Dict],
        internal_txs: List[Dict],
        erc20_txs: List[Dict],
        vasp_addresses: Optional[Set[str]] = None,
    ) -> Dict[str, List[str]]:
        """
        Run all heuristics and return clusters.
        
        Args:
            addresses: All addresses to cluster
            normal_txs: Normal transactions
            internal_txs: Internal transactions
            erc20_txs: ERC-20 token transfers
            vasp_addresses: Set of known VASP addresses
            
        Returns:
            Dictionary of cluster_id -> list of addresses
        """
        logger.info("Starting Layer A: Rule-Based Clustering (Union-Find)")
        
        # Initialize Union-Find with all addresses
        for addr in addresses:
            self.uf.find(normalize_address(addr))
        
        # Apply heuristics
        self.apply_gas_funding_heuristic(normal_txs, internal_txs)
        
        if vasp_addresses:
            self.apply_deposit_address_reuse_heuristic(normal_txs, erc20_txs, vasp_addresses)
        
        self.apply_temporal_coactivity_heuristic(normal_txs, internal_txs)
        
        # Get final clusters
        clusters = self.uf.get_clusters()
        
        logger.info(f"Layer A complete: {len(clusters)} clusters identified")
        
        return clusters
    
    def get_evidence(self) -> Dict[str, List[Dict]]:
        """Get evidence for all heuristic decisions."""
        return self.heuristic_evidence
