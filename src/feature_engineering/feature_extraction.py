"""
Phase 2: Behavioral Feature Engineering
Graph-theoretic, temporal, value-flow, and OSINT-derived features.
"""

from typing import Dict, List, Optional, Tuple

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm

from src.utils.helpers import format_eth, min_max_scale, normalize_address, safe_divide
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class GraphFeatureExtractor:
    """Extract graph-theoretic features from transaction network."""
    
    def __init__(self):
        """Initialize graph feature extractor."""
        self.graph = None
        self.features = {}
    
    def build_transaction_graph(
        self,
        normal_txs: List[Dict],
        internal_txs: List[Dict],
        erc20_txs: List[Dict],
    ) -> nx.DiGraph:
        """
        Build directed transaction graph from transaction data.
        
        Args:
            normal_txs: Normal ETH transactions
            internal_txs: Internal transactions
            erc20_txs: ERC-20 token transfers
            
        Returns:
            NetworkX directed graph
        """
        G = nx.DiGraph()
        
        # Add normal transactions
        for tx in normal_txs:
            from_addr = normalize_address(tx.get("from", ""))
            to_addr = normalize_address(tx.get("to", ""))
            value = int(tx.get("value", 0))
            block_number = int(tx.get("blockNumber", 0))
            timestamp = int(tx.get("timeStamp", 0))
            
            if from_addr and to_addr:
                G.add_edge(
                    from_addr, to_addr,
                    value=value,
                    value_eth=format_eth(value),
                    block_number=block_number,
                    timestamp=timestamp,
                    tx_type="normal",
                    tx_hash=tx.get("hash", ""),
                )
        
        # Add internal transactions
        for tx in internal_txs:
            from_addr = normalize_address(tx.get("from", ""))
            to_addr = normalize_address(tx.get("to", ""))
            value = int(tx.get("value", 0))
            block_number = int(tx.get("blockNumber", 0))
            
            if from_addr and to_addr:
                # If edge exists, add to value; otherwise create new edge
                if G.has_edge(from_addr, to_addr):
                    G[from_addr][to_addr]["value"] = G[from_addr][to_addr].get("value", 0) + value
                    G[from_addr][to_addr]["value_eth"] = G[from_addr][to_addr].get("value_eth", 0) + format_eth(value)
                else:
                    G.add_edge(
                        from_addr, to_addr,
                        value=value,
                        value_eth=format_eth(value),
                        block_number=block_number,
                        timestamp=int(tx.get("timeStamp", 0)),
                        tx_type="internal",
                        tx_hash=tx.get("hash", ""),
                    )
        
        # Add ERC-20 transfers
        for tx in erc20_txs:
            from_addr = normalize_address(tx.get("from", ""))
            to_addr = normalize_address(tx.get("to", ""))
            value = int(tx.get("value", 0))
            token_symbol = tx.get("tokenSymbol", "UNKNOWN")
            token_decimal = int(tx.get("tokenDecimal", 18))
            
            if from_addr and to_addr:
                edge_key = (from_addr, to_addr, token_symbol)
                if not G.has_edge(from_addr, to_addr):
                    G.add_edge(
                        from_addr, to_addr,
                        value=0,
                        value_eth=0,
                        block_number=int(tx.get("blockNumber", 0)),
                        timestamp=int(tx.get("timeStamp", 0)),
                        tx_type="erc20",
                        tx_hash=tx.get("hash", ""),
                        erc20_transfers={},
                    )
                
                # Track ERC-20 transfers separately
                if "erc20_transfers" not in G[from_addr][to_addr]:
                    G[from_addr][to_addr]["erc20_transfers"] = {}
                
                if token_symbol not in G[from_addr][to_addr]["erc20_transfers"]:
                    G[from_addr][to_addr]["erc20_transfers"][token_symbol] = 0
                G[from_addr][to_addr]["erc20_transfers"][token_symbol] += value
        
        self.graph = G
        logger.info(f"Built transaction graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
        
        return G
    
    def extract_graph_features(self, addresses: List[str]) -> Dict[str, Dict]:
        """
        Extract graph-theoretic features for each address.
        
        Features:
        - In-degree: Number of unique addresses sending funds
        - Out-degree: Number of unique addresses funded
        - Betweenness centrality: How often on shortest path
        - PageRank score: Influence score
        
        Args:
            addresses: List of addresses to extract features for
            
        Returns:
            Dictionary of address -> graph features
        """
        if self.graph is None:
            logger.error("Graph not built. Call build_transaction_graph first.")
            return {}
        
        G = self.graph
        features = {}
        
        # Pre-compute centralities (expensive operations)
        logger.info("Computing betweenness centrality...")
        betweenness = nx.betweenness_centrality(G)
        
        logger.info("Computing PageRank...")
        try:
            pagerank = nx.pagerank(G, max_iter=100)
        except nx.PowerIterationFailedConvergence:
            logger.warning("PageRank did not converge, using uniform scores")
            pagerank = {node: 1.0 / len(G) for node in G}
        
        for address in addresses:
            addr = normalize_address(address)
            
            if addr not in G:
                features[addr] = {
                    "in_degree": 0,
                    "out_degree": 0,
                    "total_degree": 0,
                    "betweenness_centrality": 0.0,
                    "pagerank_score": 0.0,
                }
                continue
            
            in_degree = G.in_degree(addr)
            out_degree = G.out_degree(addr)
            
            features[addr] = {
                "in_degree": in_degree,
                "out_degree": out_degree,
                "total_degree": in_degree + out_degree,
                "betweenness_centrality": betweenness.get(addr, 0.0),
                "pagerank_score": pagerank.get(addr, 0.0),
            }
        
        return features


class TemporalFeatureExtractor:
    """Extract temporal features from transaction patterns."""
    
    def extract_temporal_features(
        self,
        addresses: List[str],
        normal_txs: List[Dict],
    ) -> Dict[str, Dict]:
        """
        Extract temporal features for each address.
        
        Features:
        - Transaction burst timing: Tight time windows
        - Inter-transaction velocity: Average time between transactions
        - Block-level co-activity: Addresses transacting in same block
        
        Args:
            addresses: List of addresses
            normal_txs: Normal transactions
            
        Returns:
            Dictionary of address -> temporal features
        """
        features = {}
        
        # Group transactions by address
        address_txs = {}
        for tx in normal_txs:
            from_addr = normalize_address(tx.get("from", ""))
            to_addr = normalize_address(tx.get("to", ""))
            timestamp = int(tx.get("timeStamp", 0))
            block_number = int(tx.get("blockNumber", 0))
            
            for addr in [from_addr, to_addr]:
                if addr not in address_txs:
                    address_txs[addr] = []
                address_txs[addr].append({
                    "timestamp": timestamp,
                    "block_number": block_number,
                    "is_sender": addr == from_addr,
                })
        
        for address in addresses:
            addr = normalize_address(address)
            txs = address_txs.get(addr, [])
            
            if not txs:
                features[addr] = {
                    "transaction_count": 0,
                    "avg_inter_transaction_time": 0.0,
                    "min_inter_transaction_time": 0.0,
                    "max_inter_transaction_time": 0.0,
                    "transaction_burst_count": 0,
                    "block_coactivity_count": 0,
                    "first_tx_timestamp": 0,
                    "last_tx_timestamp": 0,
                    "active_duration_seconds": 0,
                }
                continue
            
            # Sort by timestamp
            txs_sorted = sorted(txs, key=lambda x: x["timestamp"])
            timestamps = [tx["timestamp"] for tx in txs_sorted]
            blocks = [tx["block_number"] for tx in txs_sorted]
            
            # Calculate inter-transaction times
            inter_times = []
            for i in range(1, len(timestamps)):
                inter_times.append(timestamps[i] - timestamps[i-1])
            
            # Count bursts (transactions within 60 seconds)
            burst_count = 0
            for i in range(1, len(inter_times)):
                if inter_times[i] < 60:  # 60 seconds
                    burst_count += 1
            
            # Count block co-activity
            block_counts = {}
            for block in blocks:
                block_counts[block] = block_counts.get(block, 0) + 1
            coactivity_count = sum(1 for count in block_counts.values() if count > 1)
            
            features[addr] = {
                "transaction_count": len(txs),
                "avg_inter_transaction_time": np.mean(inter_times) if inter_times else 0.0,
                "min_inter_transaction_time": min(inter_times) if inter_times else 0.0,
                "max_inter_transaction_time": max(inter_times) if inter_times else 0.0,
                "transaction_burst_count": burst_count,
                "block_coactivity_count": coactivity_count,
                "first_tx_timestamp": timestamps[0],
                "last_tx_timestamp": timestamps[-1],
                "active_duration_seconds": timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0,
            }
        
        return features


class ValueFlowFeatureExtractor:
    """Extract value-flow features from transactions."""
    
    def __init__(self, eth_price_usd: float = 2000.0):
        """
        Initialize value flow extractor.
        
        Args:
            eth_price_usd: ETH price in USD for conversions
        """
        self.eth_price_usd = eth_price_usd
    
    def extract_value_features(
        self,
        addresses: List[str],
        normal_txs: List[Dict],
        erc20_txs: List[Dict],
        known_mixers: List[str],
    ) -> Dict[str, Dict]:
        """
        Extract value-flow features for each address.
        
        Features:
        - Total inflow/outflow (ETH and USD)
        - Stablecoin proportion
        - Round-number transfer flag
        - Mixer exposure ratio
        
        Args:
            addresses: List of addresses
            normal_txs: Normal transactions
            erc20_txs: ERC-20 token transfers
            known_mixers: List of known mixer addresses
            
        Returns:
            Dictionary of address -> value features
        """
        features = {}
        mixer_addresses = [m.lower() for m in known_mixers]
        
        # Initialize address balances
        address_flows = {addr: {"inflow_eth": 0, "outflow_eth": 0, "inflow_usd": 0, "outflow_usd": 0}
                         for addr in addresses}
        address_stablecoins = {addr: {"inflow": 0, "outflow": 0} for addr in addresses}
        address_mixer_interactions = {addr: {"total": 0, "mixer": 0} for addr in addresses}
        address_round_transfers = {addr: 0 for addr in addresses}
        
        # Process normal transactions
        for tx in normal_txs:
            from_addr = normalize_address(tx.get("from", ""))
            to_addr = normalize_address(tx.get("to", ""))
            value_wei = int(tx.get("value", 0))
            value_eth = format_eth(value_wei)
            value_usd = value_eth * self.eth_price_usd
            
            # Update flows
            if from_addr in address_flows:
                address_flows[from_addr]["outflow_eth"] += value_eth
                address_flows[from_addr]["outflow_usd"] += value_usd
                address_mixer_interactions[from_addr]["total"] += 1
                if to_addr.lower() in mixer_addresses:
                    address_mixer_interactions[from_addr]["mixer"] += 1
            
            if to_addr in address_flows:
                address_flows[to_addr]["inflow_eth"] += value_eth
                address_flows[to_addr]["inflow_usd"] += value_usd
                address_mixer_interactions[to_addr]["total"] += 1
                if from_addr.lower() in mixer_addresses:
                    address_mixer_interactions[to_addr]["mixer"] += 1
            
            # Check for round-number transfers (e.g., 1, 10, 100 ETH)
            if value_eth >= 1 and value_eth == int(value_eth):
                if from_addr in address_round_transfers:
                    address_round_transfers[from_addr] += 1
                if to_addr in address_round_transfers:
                    address_round_transfers[to_addr] += 1
        
        # Process ERC-20 transfers (focus on stablecoins)
        stablecoin_symbols = {"USDT", "USDC", "DAI", "BUSD", "USDP"}
        for tx in erc20_txs:
            from_addr = normalize_address(tx.get("from", ""))
            to_addr = normalize_address(tx.get("to", ""))
            value = int(tx.get("value", 0))
            decimals = int(tx.get("tokenDecimal", 18))
            symbol = tx.get("tokenSymbol", "")
            
            value_normalized = value / (10 ** decimals)
            
            if symbol in stablecoin_symbols:
                if from_addr in address_stablecoins:
                    address_stablecoins[from_addr]["outflow"] += value_normalized
                if to_addr in address_stablecoins:
                    address_stablecoins[to_addr]["inflow"] += value_normalized
        
        # Compile features
        for address in addresses:
            addr = normalize_address(address)
            flows = address_flows.get(addr, {"inflow_eth": 0, "outflow_eth": 0, "inflow_usd": 0, "outflow_usd": 0})
            stablecoins = address_stablecoins.get(addr, {"inflow": 0, "outflow": 0})
            mixer_data = address_mixer_interactions.get(addr, {"total": 0, "mixer": 0})
            round_transfers = address_round_transfers.get(addr, 0)
            
            total_volume = flows["inflow_eth"] + flows["outflow_eth"]
            total_stablecoin = stablecoins["inflow"] + stablecoins["outflow"]
            
            features[addr] = {
                "total_inflow_eth": flows["inflow_eth"],
                "total_outflow_eth": flows["outflow_eth"],
                "total_inflow_usd": flows["inflow_usd"],
                "total_outflow_usd": flows["outflow_usd"],
                "total_volume_eth": total_volume,
                "stablecoin_proportion": safe_divide(total_stablecoin, total_volume + total_stablecoin),
                "round_number_transfer_count": round_transfers,
                "mixer_exposure_ratio": safe_divide(mixer_data["mixer"], mixer_data["total"]),
                "mixer_interaction_count": mixer_data["mixer"],
            }
        
        return features


class OSINTFeatureExtractor:
    """Extract OSINT-derived features."""
    
    def extract_osint_features(
        self,
        addresses: List[str],
        enrichment_data: Dict[str, Dict],
        graph_features: Optional[Dict[str, Dict]] = None,
    ) -> Dict[str, Dict]:
        """
        Extract OSINT-derived features for each address.
        
        Features:
        - Exchange proximity score (hop distance to VASP)
        - Sanctioned entity flag
        - Bridge interaction flag
        
        Args:
            addresses: List of addresses
            enrichment_data: OSINT enrichment data from Phase 1
            graph_features: Graph features for proximity calculation
            
        Returns:
            Dictionary of address -> OSINT features
        """
        features = {}
        
        # Get VASP addresses
        vasp_addresses = set()
        for addr, data in enrichment_data.items():
            if data.get("is_vasp"):
                vasp_addresses.add(addr.lower())
        
        for address in addresses:
            addr = normalize_address(address)
            enrichment = enrichment_data.get(addr, {})
            
            features[addr] = {
                "is_sanctioned": 1 if enrichment.get("is_sanctioned", False) else 0,
                "is_mixer": 1 if enrichment.get("is_mixer", False) else 0,
                "is_vasp": 1 if enrichment.get("is_vasp", False) else 0,
                "has_label": 1 if enrichment.get("label") else 0,
                "risk_level_numeric": {
                    "low": 0,
                    "medium": 1,
                    "high": 2,
                    "critical": 3,
                }.get(enrichment.get("risk_level", "low"), 0),
                "exchange_proximity_score": 0,  # Would require BFS calculation
                "bridge_interaction_flag": 0,  # Set from bridge events
            }
        
        return features


class FeatureEngineeringPipeline:
    """
    Phase 2: Behavioral Feature Engineering
    Combines all feature extractors into a unified pipeline.
    """
    
    def __init__(self, eth_price_usd: float = 2000.0):
        """
        Initialize feature engineering pipeline.
        
        Args:
            eth_price_usd: ETH price in USD
        """
        self.graph_extractor = GraphFeatureExtractor()
        self.temporal_extractor = TemporalFeatureExtractor()
        self.value_extractor = ValueFlowFeatureExtractor(eth_price_usd=eth_price_usd)
        self.osint_extractor = OSINTFeatureExtractor()
        self.feature_matrix = None
        self.feature_columns = None
        self.scaler = MinMaxScaler()
    
    def extract_all_features(
        self,
        addresses: List[str],
        normal_txs: List[Dict],
        internal_txs: List[Dict],
        erc20_txs: List[Dict],
        enrichment_data: Dict[str, Dict],
        known_mixers: List[str],
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Extract all features and create normalized feature matrix.
        
        Args:
            addresses: List of all addresses
            normal_txs: Normal transactions
            internal_txs: Internal transactions
            erc20_txs: ERC-20 token transfers
            enrichment_data: OSINT enrichment data
            known_mixers: List of known mixer addresses
            
        Returns:
            Tuple of (feature DataFrame, metadata dict)
        """
        logger.info(f"Starting Phase 2 feature engineering for {len(addresses)} addresses")
        
        # Build transaction graph
        self.graph_extractor.build_transaction_graph(normal_txs, internal_txs, erc20_txs)
        
        # Extract all feature types
        logger.info("Extracting graph-theoretic features...")
        graph_features = self.graph_extractor.extract_graph_features(addresses)
        
        logger.info("Extracting temporal features...")
        temporal_features = self.temporal_extractor.extract_temporal_features(addresses, normal_txs)
        
        logger.info("Extracting value-flow features...")
        value_features = self.value_extractor.extract_value_features(
            addresses, normal_txs, erc20_txs, known_mixers
        )
        
        logger.info("Extracting OSINT features...")
        osint_features = self.osint_extractor.extract_osint_features(
            addresses, enrichment_data, graph_features
        )
        
        # Combine all features
        combined_features = {}
        for address in addresses:
            addr = normalize_address(address)
            combined_features[addr] = {
                **graph_features.get(addr, {}),
                **temporal_features.get(addr, {}),
                **value_features.get(addr, {}),
                **osint_features.get(addr, {}),
            }
        
        # Create DataFrame
        df = pd.DataFrame.from_dict(combined_features, orient="index")
        df.index.name = "address"
        df = df.fillna(0)
        
        # Store feature columns for later use
        self.feature_columns = df.columns.tolist()
        
        # Normalize features (min-max scaling)
        logger.info("Normalizing features...")
        df_scaled = pd.DataFrame(
            self.scaler.fit_transform(df),
            columns=df.columns,
            index=df.index,
        )
        
        self.feature_matrix = df_scaled
        
        metadata = {
            "total_addresses": len(addresses),
            "total_features": len(self.feature_columns),
            "feature_columns": self.feature_columns,
            "graph_stats": {
                "nodes": self.graph_extractor.graph.number_of_nodes() if self.graph_extractor.graph else 0,
                "edges": self.graph_extractor.graph.number_of_edges() if self.graph_extractor.graph else 0,
            },
        }
        
        logger.info(f"Feature engineering complete: {df_scaled.shape[0]} addresses × {df_scaled.shape[1]} features")
        
        return df_scaled, metadata
    
    def get_feature_matrix(self) -> pd.DataFrame:
        """Get the normalized feature matrix."""
        if self.feature_matrix is None:
            raise ValueError("Feature matrix not created. Call extract_all_features first.")
        return self.feature_matrix
    
    def save_features(self, filepath: str):
        """Save feature matrix to CSV."""
        if self.feature_matrix is None:
            raise ValueError("Feature matrix not created.")
        self.feature_matrix.to_csv(filepath)
        logger.info(f"Features saved to {filepath}")
