# API Reference
## Blockchain Forensics Tool - Complete Module Documentation

**M.Sc. Forensic Science (Cyber Forensics) — 9th Semester**  
**Author:** Saransh Jhariya | 102FSBSMS2122012  
**Mentor:** Dr. Ajit Majumdar, Associate Professor — LNJN NICFS NFSU, Delhi Campus  
**Version:** 2.0 — Enhanced Methodology  
**Date:** March 2026

---

## Table of Contents

1. [Core Pipeline](#1-core-pipeline)
2. [Data Acquisition Modules](#2-data-acquisition-modules)
3. [Feature Engineering Module](#3-feature-engineering-module)
4. [Clustering Modules](#4-clustering-modules)
5. [Cross-Chain Module](#5-cross-chain-module)
6. [Evaluation Module](#6-evaluation-module)
7. [Utility Modules](#7-utility-modules)
8. [Configuration](#8-configuration)
9. [Data Structures](#9-data-structures)

---

## 1. Core Pipeline

### 1.1 `src/pipeline.py`

Main orchestration module that coordinates all five phases.

---

#### `BlockchainForensicsPipeline`

Main pipeline class for executing the complete forensics workflow.

**Constructor:**
```python
def __init__(
    self,
    seed_address: str,
    chain: str = "ethereum",
    output_dir: Optional[str] = None,
    eth_price_usd: float = 2000.0,
)
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `seed_address` | str | Required | Seed Ethereum address for investigation |
| `chain` | str | "ethereum" | Chain name (ethereum, arbitrum, polygon, bsc, optimism) |
| `output_dir` | str | None | Directory for output files |
| `eth_price_usd` | float | 2000.0 | ETH price in USD |

**Methods:**

---

##### `run_phase1_data_acquisition() -> Dict`

Executes Phase 1: Multi-Source Data Acquisition.

**Returns:**
```python
{
    "layer1": {...},  # Layer 1 results
    "layer3": {...},  # Layer 3 OSINT results
    "total_addresses": int,
    "vasp_addresses": List[str]
}
```

**Example:**
```python
pipeline = BlockchainForensicsPipeline(seed_address="0x123...")
phase1_results = pipeline.run_phase1_data_acquisition()
print(f"Addresses collected: {phase1_results['total_addresses']}")
```

---

##### `run_phase2_feature_engineering(vasp_addresses: set) -> Dict`

Executes Phase 2: Behavioral Feature Engineering.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `vasp_addresses` | set | Set of VASP addresses for feature extraction |

**Returns:**
```python
{
    "feature_matrix_path": str,
    "feature_metadata": {
        "total_addresses": int,
        "total_features": int,
        "feature_columns": List[str],
        "graph_stats": Dict
    }
}
```

---

##### `run_phase3_clustering(vasp_addresses: set) -> Dict`

Executes Phase 3: Dual Clustering Engine.

**Returns:**
```python
{
    "clustering_path": str,
    "total_clusters": int,
    "evidence": Dict
}
```

---

##### `run_phase4_cross_chain() -> Dict`

Executes Phase 4: Cross-Chain Entity Resolution.

**Returns:**
```python
{
    "crosschain_path": str,
    "summary": {
        "total_entities": int,
        "multi_chain_entities": int
    }
}
```

---

##### `run_phase5_evaluation(ground_truth: Optional[Dict] = None) -> Dict`

Executes Phase 5: Formal Evaluation & Forensic Output.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `ground_truth` | Dict | Optional ground truth labels |

**Returns:**
```python
{
    "risk_profiles": Dict,
    "evaluation_metrics": Dict,
    "interactive_graph_path": str,
    "static_report_path": str,
    "graph_stats": {"nodes": int, "edges": int}
}
```

---

##### `run_full_pipeline(ground_truth: Optional[Dict] = None) -> Dict`

Executes the complete five-phase pipeline.

**Returns:**
```python
{
    "pipeline_metadata": Dict,
    "phase1_summary": Dict,
    "phase2_summary": Dict,
    "phase3_summary": Dict,
    "phase4_summary": Dict,
    "phase5_summary": Dict
}
```

**Example:**
```python
results = pipeline.run_full_pipeline()
print(f"Total clusters: {results['phase3_summary']['total_clusters']}")
print(f"F1 Score: {results['phase5_summary']['evaluation_metrics']['f1_score']}")
```

---

#### `run_forensics()`

Convenience function for running the complete pipeline.

**Signature:**
```python
def run_forensics(
    seed_address: str,
    chain: str = "ethereum",
    output_dir: Optional[str] = None,
    ground_truth_path: Optional[str] = None,
) -> Dict
```

**Example:**
```python
from src.pipeline import run_forensics

results = run_forensics(
    seed_address="0x1234567890abcdef1234567890abcdef12345678",
    chain="ethereum",
    ground_truth_path="labels.json"
)
```

---

## 2. Data Acquisition Modules

### 2.1 `src/data_acquisition/etherscan_client.py`

Etherscan API client for fetching on-chain transaction data.

---

#### `EtherscanClient`

Client for interacting with Etherscan and compatible block explorers.

**Constructor:**
```python
def __init__(self, chain: str = "ethereum", api_key: Optional[str] = None)
```

**Methods:**

---

##### `get_normal_transactions(address, start_block=0, end_block=99999999, page=1, offset=10000) -> List[Dict]`

Fetch normal ETH transactions for an address.

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `address` | str | Required | Ethereum address |
| `start_block` | int | 0 | Starting block number |
| `end_block` | int | 99999999 | Ending block number |
| `page` | int | 1 | Page number |
| `offset` | int | 10000 | Records per page (max 10000) |

**Returns:**
```python
[
    {
        "hash": str,
        "from": str,
        "to": str,
        "value": str,  # Wei
        "blockNumber": str,
        "timeStamp": str,
        "gas": str,
        "gasPrice": str,
        ...
    }
]
```

---

##### `get_internal_transactions(address, start_block=0, end_block=99999999) -> List[Dict]`

Fetch internal transactions for an address.

**Returns:** List of internal transaction dictionaries.

---

##### `get_erc20_transfers(address, start_block=0, end_block=99999999) -> List[Dict]`

Fetch ERC-20 token transfers for an address.

**Returns:**
```python
[
    {
        "hash": str,
        "from": str,
        "to": str,
        "value": str,
        "tokenSymbol": str,
        "tokenName": str,
        "tokenDecimal": str,
        "blockNumber": str,
        "timeStamp": str,
        ...
    }
]
```

---

##### `get_balance(address: str) -> Dict`

Get ETH balance for an address.

**Returns:**
```python
{
    "address": str,
    "balance_wei": str,
    "balance_eth": float
}
```

---

##### `get_contract_abi(contract_address: str) -> List[Dict]`

Get ABI for a smart contract.

**Returns:** List of ABI entries.

---

#### `DataAcquisitionLayer1`

Layer 1: On-Chain Transaction Pull.

**Constructor:**
```python
def __init__(self, chain: str = "ethereum", output_dir: Optional[str] = None)
```

**Methods:**

---

##### `fetch_all_transactions(seed_address: str) -> Dict`

Fetch all transaction types for a seed address.

**Returns:**
```python
{
    "seed_address": str,
    "chain": str,
    "normal_transactions": List[Dict],
    "internal_transactions": List[Dict],
    "erc20_transfers": List[Dict],
    "all_addresses": List[str],
    "evidence_record": Dict
}
```

---

##### `fetch_counterparty_transactions(addresses: List[str], max_addresses: int = 100) -> Dict`

Fetch transactions for counterparties.

**Returns:** Dictionary of address → transaction data.

---

### 2.2 `src/data_acquisition/bridge_events.py`

Bridge event logs and cross-chain data.

---

#### `BridgeEventFetcher`

Fetches bridge event logs from multiple chains.

**Constructor:**
```python
def __init__(self, chain: str = "ethereum", rpc_url: Optional[str] = None)
```

**Methods:**

---

##### `fetch_bridge_events_for_address(address: str) -> List[Dict]`

Fetch bridge events involving an address.

**Returns:**
```python
[
    {
        "event_type": str,  # "lock", "mint", "burn"
        "bridge": str,  # "wormhole", "stargate", "across"
        "chain": str,
        "address": str,
        "amount": str,
        "to_chain_id": int,
        "block_number": int,
        "transaction_hash": str,
        "timestamp": int
    }
]
```

---

#### `DataAcquisitionLayer2`

Layer 2: Bridge Event Logs.

**Constructor:**
```python
def __init__(self, chain: str = "ethereum", output_dir: Optional[str] = None)
```

**Methods:**

---

##### `fetch_bridge_events(addresses: List[str]) -> Dict`

Fetch bridge events for multiple addresses.

**Returns:**
```python
{
    "chain": str,
    "bridge_events": Dict[str, List[Dict]],  # address -> events
    "evidence_record": Dict
}
```

---

### 2.3 `src/data_acquisition/osint_enrichment.py`

OSINT enrichment - tags, VASP labels, mixer flags, sanctions lists.

---

#### `OSINTEnrichmentClient`

Client for fetching OSINT data from multiple sources.

**Constructor:**
```python
def __init__(self, chain: str = "ethereum")
```

**Methods:**

---

##### `get_etherscan_labels(addresses: List[str]) -> Dict[str, Dict]`

Fetch Etherscan labels for addresses.

**Returns:**
```python
{
    "0x123...": {
        "label": str,
        "category": str,  # "exchange", "defi", "mixer", "scam"
        "source": str,
        "risk_level": str  # "low", "medium", "high"
    }
}
```

---

##### `check_ofac_sdn(addresses: List[str]) -> Dict[str, bool]`

Check addresses against OFAC SDN list.

**Returns:** Dictionary of address → is_sanctioned.

---

##### `check_chainabuse(address: str) -> Optional[Dict]`

Check address against Chainabuse database.

**Returns:** Abuse report if found, None otherwise.

---

##### `enrich_addresses(addresses: List[str]) -> Dict[str, Dict]`

Perform full OSINT enrichment on addresses.

**Returns:**
```python
{
    "0x123...": {
        "address": str,
        "label": str,
        "label_category": str,
        "is_sanctioned": bool,
        "is_mixer": bool,
        "is_vasp": bool,
        "vasp_name": str,
        "risk_level": str
    }
}
```

---

#### `DataAcquisitionLayer3`

Layer 3: OSINT Enrichment.

**Constructor:**
```python
def __init__(self, chain: str = "ethereum", output_dir: Optional[str] = None)
```

**Methods:**

---

##### `enrich_addresses(addresses: List[str]) -> Dict`

Enrich addresses with OSINT data.

**Returns:**
```python
{
    "chain": str,
    "enrichment_data": Dict,
    "summary": {
        "total_addresses": int,
        "labeled_addresses": int,
        "sanctioned_addresses": int,
        "mixer_addresses": int,
        "vasp_addresses": int,
        "high_risk_addresses": int
    },
    "evidence_record": Dict
}
```

---

## 3. Feature Engineering Module

### 3.1 `src/feature_engineering/feature_extraction.py`

Graph-theoretic, temporal, value-flow, and OSINT-derived features.

---

#### `GraphFeatureExtractor`

Extract graph-theoretic features from transaction network.

**Methods:**

---

##### `build_transaction_graph(normal_txs, internal_txs, erc20_txs) -> nx.DiGraph`

Build directed transaction graph.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `normal_txs` | List[Dict] | Normal ETH transactions |
| `internal_txs` | List[Dict] | Internal transactions |
| `erc20_txs` | List[Dict] | ERC-20 token transfers |

**Returns:** NetworkX directed graph with weighted edges.

---

##### `extract_graph_features(addresses: List[str]) -> Dict[str, Dict]`

Extract graph-theoretic features.

**Features:**
- `in_degree`: Number of unique addresses sending funds
- `out_degree`: Number of unique addresses funded
- `total_degree`: Sum of in and out degree
- `betweenness_centrality`: Shortest path frequency
- `pagerank_score`: Influence score

**Returns:**
```python
{
    "0x123...": {
        "in_degree": int,
        "out_degree": int,
        "total_degree": int,
        "betweenness_centrality": float,
        "pagerank_score": float
    }
}
```

---

#### `TemporalFeatureExtractor`

Extract temporal features from transaction patterns.

**Methods:**

---

##### `extract_temporal_features(addresses: List[str], normal_txs: List[Dict]) -> Dict[str, Dict]`

**Features:**
- `transaction_count`: Total transactions
- `avg_inter_transaction_time`: Average time between transactions
- `min_inter_transaction_time`: Minimum time between transactions
- `max_inter_transaction_time`: Maximum time between transactions
- `transaction_burst_count`: Transactions within 60-second windows
- `block_coactivity_count`: Addresses transacting in same block
- `first_tx_timestamp`: First transaction timestamp
- `last_tx_timestamp`: Last transaction timestamp
- `active_duration_seconds`: Total active time

---

#### `ValueFlowFeatureExtractor`

Extract value-flow features from transactions.

**Constructor:**
```python
def __init__(self, eth_price_usd: float = 2000.0)
```

**Methods:**

---

##### `extract_value_features(addresses, normal_txs, erc20_txs, known_mixers) -> Dict[str, Dict]`

**Features:**
- `total_inflow_eth`: Total ETH received
- `total_outflow_eth`: Total ETH sent
- `total_inflow_usd`: Total USD received
- `total_outflow_usd`: Total USD sent
- `total_volume_eth`: Total volume
- `stablecoin_proportion`: Fraction in stablecoins
- `round_number_transfer_count`: Round-number transfers
- `mixer_exposure_ratio`: Proportion touching mixers
- `mixer_interaction_count`: Direct mixer interactions

---

#### `OSINTFeatureExtractor`

Extract OSINT-derived features.

**Methods:**

---

##### `extract_osint_features(addresses, enrichment_data, graph_features) -> Dict[str, Dict]`

**Features:**
- `is_sanctioned`: Binary flag
- `is_mixer`: Binary flag
- `is_vasp`: Binary flag
- `has_label`: Binary flag
- `risk_level_numeric`: 0-3 scale
- `exchange_proximity_score`: Hop distance to VASP
- `bridge_interaction_flag`: Binary flag

---

#### `FeatureEngineeringPipeline`

Complete feature engineering pipeline.

**Constructor:**
```python
def __init__(self, eth_price_usd: float = 2000.0)
```

**Methods:**

---

##### `extract_all_features(addresses, normal_txs, internal_txs, erc20_txs, enrichment_data, known_mixers) -> Tuple[pd.DataFrame, Dict]`

Extract all features and create normalized feature matrix.

**Returns:**
```python
(
    # Feature matrix (n_addresses × 30_features)
    pd.DataFrame,
    # Metadata
    {
        "total_addresses": int,
        "total_features": int,
        "feature_columns": List[str],
        "graph_stats": {"nodes": int, "edges": int}
    }
)
```

**Feature Columns (30 total):**
```python
[
    # Graph features (5)
    "in_degree", "out_degree", "total_degree",
    "betweenness_centrality", "pagerank_score",
    
    # Temporal features (9)
    "transaction_count", "avg_inter_transaction_time",
    "min_inter_transaction_time", "max_inter_transaction_time",
    "transaction_burst_count", "block_coactivity_count",
    "first_tx_timestamp", "last_tx_timestamp", "active_duration_seconds",
    
    # Value-flow features (9)
    "total_inflow_eth", "total_outflow_eth", "total_inflow_usd",
    "total_outflow_usd", "total_volume_eth", "stablecoin_proportion",
    "round_number_transfer_count", "mixer_exposure_ratio",
    "mixer_interaction_count",
    
    # OSINT features (7)
    "is_sanctioned", "is_mixer", "is_vasp", "has_label",
    "risk_level_numeric", "exchange_proximity_score",
    "bridge_interaction_flag"
]
```

---

##### `get_feature_matrix() -> pd.DataFrame`

Get the normalized feature matrix.

---

##### `save_features(filepath: str)`

Save feature matrix to CSV.

---

## 4. Clustering Modules

### 4.1 `src/clustering/rule_based_clustering.py`

Rule-based clustering using Union-Find (Disjoint Set Union).

---

#### `UnionFind`

Union-Find (Disjoint Set Union) data structure.

**Complexity:** O(α(n)) per operation (near-constant time)

**Constructor:**
```python
def __init__(self)
```

**Methods:**

---

##### `find(x: str) -> str`

Find the representative (root) of the set containing x with path compression.

**Time Complexity:** O(α(n))

---

##### `union(x: str, y: str) -> bool`

Union the sets containing x and y using union by rank.

**Returns:** True if union was performed, False if already in same set.

**Time Complexity:** O(α(n))

---

##### `get_clusters() -> Dict[str, List[str]]`

Get all clusters as a dictionary.

**Returns:**
```python
{
    "root_address_1": ["addr1", "addr2", "addr3"],
    "root_address_2": ["addr4", "addr5"]
}
```

---

##### `get_cluster_id(address: str) -> str`

Get the cluster ID (root) for an address.

---

##### `are_connected(x: str, y: str) -> bool`

Check if two addresses are in the same cluster.

---

##### `get_cluster_size(address: str) -> int`

Get the size of the cluster containing the address.

---

#### `RuleBasedClustering`

Layer A: Rule-Based Clustering using Union-Find.

**Constructor:**
```python
def __init__(
    self,
    gas_funding_threshold: float = 0.01,
    temporal_window_seconds: int = 60,
)
```

**Heuristics:**

| Heuristic | Trigger Condition | Forensic Rationale |
|-----------|-------------------|-------------------|
| Gas Funding | A sends < 0.01 ETH to B before B's first outgoing tx | Criminals fund new wallets before use |
| Deposit Reuse | Two addresses send to same VASP deposit address | Unique deposit addresses per user |
| Temporal Co-Activity | Two addresses interact with same contract in same block | Exploit scripts execute atomically |

**Methods:**

---

##### `apply_gas_funding_heuristic(normal_txs, internal_txs) -> int`

Apply gas funding source heuristic.

**Returns:** Number of unions performed.

---

##### `apply_deposit_address_reuse_heuristic(normal_txs, erc20_txs, vasp_addresses) -> int`

Apply deposit address reuse heuristic.

---

##### `apply_temporal_coactivity_heuristic(normal_txs, internal_txs) -> int`

Apply temporal co-activity heuristic.

---

##### `cluster(addresses, normal_txs, internal_txs, erc20_txs, vasp_addresses) -> Dict[str, List[str]]`

Run all heuristics and return clusters.

**Returns:** Dictionary of cluster_id → addresses.

---

##### `get_evidence() -> Dict[str, List[Dict]]`

Get evidence for all heuristic decisions.

**Returns:**
```python
{
    "gas_funding": [
        {
            "funder": str,
            "funded": str,
            "amount_eth": float,
            "timestamp": int,
            "block_number": int
        }
    ],
    "deposit_reuse": [...],
    "temporal_coactivity": [...]
}
```

---

### 4.2 `src/clustering/ml_clustering.py`

ML-based clustering using DBSCAN and confidence scoring.

---

#### `DBSCANClustering`

Layer B: ML-Based Clustering using DBSCAN.

**Constructor:**
```python
def __init__(self, eps: float = 0.5, min_samples: int = 3, metric: str = "euclidean")
```

**Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `eps` | float | 0.5 | Maximum distance between neighbors |
| `min_samples` | int | 3 | Minimum samples for dense region |
| `metric` | str | "euclidean" | Distance metric |

**Methods:**

---

##### `optimize_eps(feature_matrix: pd.DataFrame, k: int = 4) -> float`

Optimize epsilon parameter using k-distance plot.

**Returns:** Optimal epsilon value.

---

##### `fit(feature_matrix: pd.DataFrame, auto_optimize_eps: bool = True) -> np.ndarray`

Fit DBSCAN model to feature matrix.

**Returns:** Cluster labels for each address (-1 for noise).

---

##### `get_clusters(addresses: List[str]) -> Dict[int, List[str]]`

Get clusters as dictionary.

**Returns:**
```python
{
    0: ["addr1", "addr2"],
    1: ["addr3", "addr4", "addr5"],
    -1: ["noise_addr1", "noise_addr2"]  # Outliers
}
```

---

##### `get_noise_addresses(addresses: List[str]) -> List[str]`

Get addresses classified as noise/outliers.

---

#### `ConfidenceScorer`

Confidence scoring: Reconciling Layer A and Layer B outputs.

**Confidence Tiers:**

| Tier | Condition | Forensic Significance |
|------|-----------|----------------------|
| High | Both layers assign to same cluster | Strong evidence for court |
| Candidate | Only one layer fires | Probable, needs review |
| Unlinked | Neither layer finds connection | Separate entity |

**Methods:**

---

##### `compute_confidence(rule_based_clusters, ml_clusters, addresses) -> Dict[str, Dict]`

Compute confidence scores for all addresses.

**Returns:**
```python
{
    "0x123...": {
        "address": str,
        "confidence_tier": str,  # "high", "candidate", "unlinked"
        "confidence_reason": str,
        "rule_based_cluster_id": str,
        "ml_cluster_id": int,
        "is_ml_noise": bool
    }
}
```

---

##### `get_high_confidence_clusters(confidence_results, rule_based_clusters) -> Dict[str, List[str]]`

Extract only high-confidence clusters.

---

#### `DualClusteringEngine`

Phase 3: Dual Clustering Engine - combines both layers.

**Constructor:**
```python
def __init__(
    self,
    gas_funding_threshold: float = 0.01,
    temporal_window_seconds: int = 60,
    dbscan_eps: float = 0.5,
    dbscan_min_samples: int = 3,
)
```

**Methods:**

---

##### `cluster(addresses, normal_txs, internal_txs, erc20_txs, feature_matrix, vasp_addresses) -> Tuple[Dict, Dict]`

Run dual clustering pipeline.

**Returns:**
```python
(
    # Final clusters
    Dict[str, List[str]],
    # Confidence results
    Dict[str, Dict]
)
```

---

##### `get_evidence() -> Dict`

Get all clustering evidence.

---

## 5. Cross-Chain Module

### 5.1 `src/cross_chain/entity_resolution.py`

Bridge event correlation, DEX swap tracing, and multi-chain entity stitching.

---

#### `BridgeEventCorrelator`

Correlates bridge events across chains.

**Matching Rules:**

| Field | Rule |
|-------|------|
| Token amount | ±0.5% tolerance for bridge fees |
| Timestamp window | Lock and mint within 5-15 minutes |
| Value fingerprint | Hash of (source, amount, token type) |

**Constructor:**
```python
def __init__(
    self,
    amount_tolerance: float = 0.005,
    timestamp_window_minutes: int = 15,
)
```

**Methods:**

---

##### `correlate_bridge_events(bridge_events: Dict[str, List[Dict]]) -> List[Dict]`

Correlate bridge events across chains.

**Returns:**
```python
[
    {
        "correlation_id": str,
        "lock_event": Dict,
        "mint_event": Dict,
        "source_chain": str,
        "destination_chain": str,
        "amount": str,
        "confidence": str  # "high" or "medium"
    }
]
```

---

##### `get_cross_chain_edges() -> List[Tuple[str, str, Dict]]`

Get cross-chain edges for graph construction.

**Returns:**
```python
[
    (
        "source_address",
        "destination_address",
        {
            "edge_type": "cross_chain_bridge",
            "source_chain": str,
            "destination_chain": str,
            "amount": str,
            "bridge": str,
            "confidence": str
        }
    )
]
```

---

#### `DEXSwapTracer`

Traces DEX swaps to maintain entity labels through token exchanges.

**Supported DEXs:**
- Uniswap V2/V3
- Curve
- Balancer

**Methods:**

---

##### `extract_swaps_from_transactions(normal_txs, internal_txs, erc20_txs) -> List[Dict]`

Extract potential DEX swap events.

**Returns:**
```python
[
    {
        "transaction_hash": str,
        "tokens_in": List[Dict],
        "tokens_out": List[Dict],
        "addresses_involved": List[str],
        "dex": str,
        "block_number": str,
        "timestamp": str
    }
]
```

---

##### `get_swap_edges() -> List[Tuple[str, str, Dict]]`

Get edges representing DEX swaps.

---

#### `MultiChainEntityStitcher`

Stitches entity clusters across multiple EVM-compatible chains.

**Methods:**

---

##### `stitch_clusters(chain_clusters, bridge_correlations) -> Dict`

Stitch clusters from multiple chains into unified entities.

**Returns:**
```python
{
    "entity_abc123": {
        "addresses": {
            "ethereum": ["0x123...", "0x456..."],
            "arbitrum": ["0x789..."]
        },
        "total_addresses": int,
        "chains_involved": ["ethereum", "arbitrum"]
    }
}
```

---

##### `get_unified_graph_data() -> Dict`

Get data for unified forensic graph.

**Returns:**
```python
{
    "entities": Dict,
    "total_entities": int,
    "multi_chain_entities": int
}
```

---

#### `CrossChainEntityResolution`

Phase 4: Cross-Chain Entity Resolution - complete pipeline.

**Constructor:**
```python
def __init__(
    self,
    amount_tolerance: float = 0.005,
    timestamp_window_minutes: int = 15,
)
```

**Methods:**

---

##### `resolve(chain_data: Dict[str, Dict], chain_clusters: Dict[str, Dict]) -> Dict`

Run complete cross-chain entity resolution pipeline.

**Returns:**
```python
{
    "unified_entities": Dict,
    "bridge_correlations": List[Dict],
    "dex_swaps": List[Dict],
    "cross_chain_edges": List[Tuple],
    "dex_edges": List[Tuple],
    "summary": Dict
}
```

---

## 6. Evaluation Module

### 6.1 `src/evaluation/forensic_output.py`

Evaluation metrics, risk scoring, and interactive HTML visualization.

---

#### `ClusteringEvaluator`

Evaluates clustering performance against ground truth labels.

**Metrics:**
- Precision, Recall, F1-Score
- Clustering Purity
- Adjusted Rand Index (ARI)

**Methods:**

---

##### `compute_pairwise_metrics(predicted_clusters, ground_truth) -> Dict[str, float]`

Compute pairwise precision, recall, F1.

**Returns:**
```python
{
    "precision": float,
    "recall": float,
    "f1_score": float,
    "total_pairs": int,
    "positive_pairs_gt": int,
    "positive_pairs_pred": int
}
```

---

##### `compute_ari(predicted_labels: List[int], ground_truth_labels: List[int]) -> float`

Compute Adjusted Rand Index.

**Returns:** ARI score (-1 to 1, higher is better).

---

##### `compute_purity(predicted_clusters, ground_truth) -> float`

Compute clustering purity.

**Returns:** Purity score (0-1, higher is better).

---

##### `evaluate_baseline_comparison(enhanced_metrics, baseline_metrics) -> Dict[str, float]`

Compare enhanced methodology against baseline.

**Returns:** Comparison metrics showing improvement percentage.

---

#### `RiskScorer`

Assigns risk scores to entity clusters.

**Risk Attributes:**
- Mixer exposure %
- VASP proximity
- Cluster size
- Sanctioned entity flag
- Confidence tier

**Constructor:**
```python
def __init__(self, enrichment_data: Dict[str, Dict], confidence_results: Dict[str, Dict])
```

**Methods:**

---

##### `compute_risk_scores(clusters: Dict[str, List[str]]) -> Dict[str, Dict]`

Compute risk scores for all clusters.

**Returns:**
```python
{
    "cluster_id": {
        "cluster_id": str,
        "total_addresses": int,
        "mixer_exposure_pct": float,
        "sanctioned_count": int,
        "vasp_proximity": Union[int, str],
        "high_risk_address_count": int,
        "high_risk_address_pct": float,
        "overall_risk_level": str,  # "low", "medium", "high", "critical"
        "avg_confidence_score": float,
        "dominant_confidence_tier": str
    }
}
```

---

#### `ForensicVisualizer`

Creates interactive HTML forensic graph visualizations.

**Constructor:**
```python
def __init__(self, output_dir: str = "data/output")
```

**Methods:**

---

##### `build_forensic_graph(normal_txs, erc20_txs, clusters, confidence_results, cross_chain_edges) -> nx.DiGraph`

Build NetworkX graph for visualization.

**Returns:** NetworkX directed graph with node and edge attributes.

---

##### `create_interactive_html(G: nx.DiGraph, filename: str = "forensic_graph.html", title: str = "Blockchain Forensic Graph") -> str`

Create interactive HTML visualization using Pyvis.

**Features:**
- Color-coded nodes by entity cluster
- Confidence tier borders (green=high, orange=candidate, gray=unlinked)
- Clickable nodes linking to Etherscan
- Edge weights proportional to transaction volume
- Cross-chain edges as dashed lines

**Returns:** Path to generated HTML file.

---

##### `create_static_report(clusters, risk_profiles, evaluation_metrics, filename: str = "forensic_report.json") -> str`

Create static forensic report.

**Returns:** Path to generated JSON report.

---

#### `Phase5ForensicOutput`

Phase 5: Formal Evaluation & Forensic Output - complete pipeline.

**Constructor:**
```python
def __init__(self, output_dir: str = "data/output")
```

**Methods:**

---

##### `generate_output(clusters, confidence_results, enrichment_data, normal_txs, erc20_txs, cross_chain_edges, ground_truth) -> Dict`

Generate all Phase 5 outputs.

**Returns:**
```python
{
    "risk_profiles": Dict,
    "evaluation_metrics": Dict,
    "interactive_graph_path": str,
    "static_report_path": str,
    "graph_stats": {"nodes": int, "edges": int}
}
```

---

## 7. Utility Modules

### 7.1 `src/utils/helpers.py`

Utility functions for the Blockchain Forensics Tool.

---

#### `normalize_address(address: str) -> str`

Normalize Ethereum address to lowercase with 0x prefix.

**Example:**
```python
normalize_address("0xABC123")  # Returns: "0xabc123"
normalize_address("abc123...")  # Returns: "0xabc123..."
```

---

#### `generate_fingerprint(*args) -> str`

Generate a unique fingerprint hash from input values.

**Example:**
```python
generate_fingerprint("data", "source", "address")  # Returns: SHA256 hash
```

---

#### `save_json(data: Any, filepath: str) -> None`

Save data to JSON file with proper formatting.

---

#### `load_json(filepath: str) -> Any`

Load data from JSON file.

---

#### `save_csv(df: pd.DataFrame, filepath: str) -> None`

Save DataFrame to CSV file.

---

#### `load_csv(filepath: str) -> pd.DataFrame`

Load DataFrame from CSV file.

---

#### `get_timestamp() -> str`

Get current timestamp in ISO format.

---

#### `format_eth(value_wei: int) -> float`

Convert Wei to ETH.

**Example:**
```python
format_eth(1000000000000000000)  # Returns: 1.0
```

---

#### `format_token(value: int, decimals: int = 18) -> float`

Convert token value with decimals to float.

---

#### `wei_to_usd(value_wei: int, price_usd: float) -> float`

Convert Wei value to USD given ETH price.

---

#### `is_valid_address(address: str) -> bool`

Check if address is a valid Ethereum address format.

---

#### `create_evidence_record(data_type, source, seed_address, chain, additional_metadata) -> Dict`

Create a chain-of-custody evidence record.

**Returns:**
```python
{
    "evidence_id": str,
    "data_type": str,
    "source": str,
    "seed_address": str,
    "chain": str,
    "retrieval_timestamp": str,
    "retrieved_by": str,
    "integrity_hash": str
}
```

---

#### `min_max_scale(value: float, min_val: float, max_val: float) -> float`

Apply min-max scaling to a value.

---

#### `safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float`

Safe division with default value for zero denominator.

---

### 7.2 `src/utils/logger.py`

Logging configuration.

---

#### `setup_logger(name: str, log_dir: str = "logs", level: int = logging.INFO) -> logging.Logger`

Set up a logger with both console and file handlers.

**Example:**
```python
logger = setup_logger(__name__)
logger.info("Processing started")
logger.error("An error occurred")
```

---

## 8. Configuration

### 8.1 `config/settings.py`

Configuration settings for the Blockchain Forensics Tool.

---

#### API Keys (from environment)

```python
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
CHAINABUSE_API_KEY = os.getenv("CHAINABUSE_API_KEY", "")
```

---

#### API Endpoints

```python
ETHERSCAN_BASE_URL = "https://api.etherscan.io/api"
ARBISCAN_BASE_URL = "https://api.arbiscan.io/api"
POLYGONSCAN_BASE_URL = "https://api.polygonscan.com/api"
BSCSCAN_BASE_URL = "https://api.bscscan.com/api"
OPTIMISTIC_ETHERSCAN_BASE_URL = "https://api-optimistic.etherscan.io/api"
```

---

#### Clustering Parameters

```python
class ClusteringConfig:
    GAS_FUNDING_THRESHOLD = 0.01  # ETH
    TEMPORAL_WINDOW_SECONDS = 60
    DBSCAN_EPS = 0.5
    DBSCAN_MIN_SAMPLES = 3
```

---

#### Bridge Event Matching

```python
class BridgeConfig:
    AMOUNT_TOLERANCE = 0.005  # 0.5%
    TIMESTAMP_WINDOW_MINUTES = 15
```

---

#### Supported Chains

```python
SUPPORTED_CHAINS = {
    "ethereum": {"name": "Ethereum", "chain_id": 1, "api_url": ETHERSCAN_BASE_URL},
    "arbitrum": {"name": "Arbitrum", "chain_id": 42161, "api_url": ARBISCAN_BASE_URL},
    "polygon": {"name": "Polygon", "chain_id": 137, "api_url": POLYGONSCAN_BASE_URL},
    "bsc": {"name": "BSC", "chain_id": 56, "api_url": BSCSCAN_BASE_URL},
    "optimism": {"name": "Optimism", "chain_id": 10, "api_url": OPTIMISTIC_ETHERSCAN_BASE_URL},
}
```

---

#### Known Mixers

```python
KNOWN_MIXERS = [
    "0x12D66f87A04A989229Ee8cE45E76349E89908769",  # Tornado Cash: ETH
    "0x47CE0C6eD5B0Ce3d3A51fdb1C52DC66a7c3c2936",  # Tornado Cash: USDC
    ...
]
```

---

#### Known VASPs

```python
KNOWN_VASPS = {
    "binance": ["0x28C6c06298d514Db089934071355E5743bf21d60", ...],
    "coinbase": ["0x503828976D22510aad0201ac7EC88297663E8fe6", ...],
    "kraken": ["0x267be1C1D684F78cb4F6a176C4911b741E4Ffdc0", ...],
}
```

---

## 9. Data Structures

### 9.1 Transaction Data Structure

```python
{
    "hash": str,           # Transaction hash
    "from": str,           # Sender address
    "to": str,             # Receiver address
    "value": str,          # Value in Wei
    "blockNumber": str,    # Block number
    "timeStamp": str,      # Unix timestamp
    "gas": str,            # Gas used
    "gasPrice": str,       # Gas price in Wei
    "input": str,          # Input data
    "isError": str         # "0" for success, "1" for error
}
```

---

### 9.2 ERC-20 Transfer Data Structure

```python
{
    "hash": str,           # Transaction hash
    "from": str,           # Sender address
    "to": str,             # Receiver address
    "value": str,          # Token amount (raw)
    "tokenSymbol": str,    # Token symbol (e.g., "USDT")
    "tokenName": str,      # Token name
    "tokenDecimal": str,   # Token decimals
    "blockNumber": str,
    "timeStamp": str,
    "contractAddress": str # Token contract address
}
```

---

### 9.3 Enrichment Data Structure

```python
{
    "address": str,           # Normalized address
    "label": str,             # Etherscan label
    "label_category": str,    # Category (exchange, mixer, etc.)
    "is_sanctioned": bool,    # OFAC SDN flag
    "is_mixer": bool,         # Mixer flag
    "is_vasp": bool,          # VASP flag
    "vasp_name": str,         # VASP name if applicable
    "risk_level": str         # "low", "medium", "high", "critical"
}
```

---

### 9.4 Cluster Data Structure

```python
{
    "cluster_id": str,        # Unique cluster identifier
    "addresses": List[str],   # Addresses in cluster
    "confidence_tier": str,   # "high", "candidate", "unlinked"
    "risk_level": str,        # "low", "medium", "high", "critical"
    "chains_involved": List[str]  # For cross-chain clusters
}
```

---

### 9.5 Risk Profile Data Structure

```python
{
    "cluster_id": str,
    "total_addresses": int,
    "mixer_exposure_pct": float,
    "sanctioned_count": int,
    "vasp_proximity": Union[int, str],
    "high_risk_address_count": int,
    "high_risk_address_pct": float,
    "overall_risk_level": str,
    "avg_confidence_score": float,
    "dominant_confidence_tier": str
}
```

---

**Document Version:** 2.0  
**Last Updated:** March 2026
