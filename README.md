# Blockchain Forensics Tool

**Wallet Clustering & Cross-Chain Tracing Tool**

M.Sc. Forensic Science (Cyber Forensics) — 9th Semester

**Author:** Saransh Jhariya | 102FSBSMS2122012  
**Mentor:** Dr. Ajit Majumdar, Associate Professor — LNJN NICFS NFSU, Delhi Campus  
**Version:** 2.0 — Enhanced Methodology  
**Date:** March 2026

---

## Overview

This tool implements an enhanced five-phase methodology for blockchain forensics, designed to identify, cluster, and trace criminal wallets across Ethereum and EVM-compatible chains. The tool moves beyond proof-of-concept heuristics to a production-grade, ML-augmented forensic pipeline.

### Key Features

- **Five-Phase Methodology**: Systematic approach from data acquisition to forensic output
- **Dual Clustering Engine**: Combines rule-based (Union-Find) and ML-based (DBSCAN) clustering
- **Cross-Chain Tracing**: Bridge event correlation and DEX swap tracing
- **Formal Evaluation**: Precision, recall, F1-score against ground truth datasets
- **Interactive Output**: HTML forensic graphs suitable for court submission

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Etherscan API key (free from https://etherscan.io/myapikey)

### Setup

1. **Clone or download the project:**

```bash
cd blockchain_forensics_tool
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure API keys:**

```bash
cp .env.example .env
# Edit .env and add your Etherscan API key
```

---

## Usage

### Basic Usage

```bash
python main.py --seed 0x1234567890abcdef1234567890abcdef12345678
```

### Command-Line Options

| Option | Description |
|--------|-------------|
| `--seed, -s` | Seed Ethereum address (required) |
| `--chain, -c` | Chain to analyze: ethereum, arbitrum, polygon, bsc, optimism (default: ethereum) |
| `--output, -o` | Output directory for results |
| `--ground-truth, -g` | Path to ground truth JSON for evaluation |
| `--eth-price` | ETH price in USD (default: 2000) |
| `--multi-chain` | Enable multi-chain analysis |
| `--verbose, -v` | Enable verbose logging |
| `--version` | Show version information |

### Examples

**Single address analysis:**
```bash
python main.py -s 0x1234567890abcdef1234567890abcdef12345678 -v
```

**Multi-chain analysis:**
```bash
python main.py -s 0x... --chain ethereum --multi-chain
```

**With evaluation against ground truth:**
```bash
python main.py -s 0x... -g elliptic_labels.json
```

---

## Five-Phase Methodology

### Phase 1: Multi-Source Data Acquisition

Fetches data from three layers:
- **Layer 1**: On-chain transactions (normal, internal, ERC-20)
- **Layer 2**: Bridge event logs (Wormhole, Stargate, Across)
- **Layer 3**: OSINT enrichment (Etherscan labels, OFAC SDN, Chainabuse)

### Phase 2: Behavioral Feature Engineering

Extracts multi-dimensional feature vectors:
- **Graph-theoretic**: In-degree, out-degree, betweenness centrality, PageRank
- **Temporal**: Transaction burst timing, inter-transaction velocity
- **Value-flow**: Total inflow/outflow, stablecoin proportion, mixer exposure
- **OSINT-derived**: Exchange proximity, sanctioned entity flags

### Phase 3: Dual Clustering Engine

Two parallel clustering mechanisms:
- **Layer A**: Rule-based Union-Find (gas funding, deposit reuse, temporal co-activity)
- **Layer B**: ML-based DBSCAN clustering on feature vectors
- **Confidence Scoring**: Reconciles both layers (High/Candidate/Unlinked tiers)

### Phase 4: Cross-Chain Entity Resolution

Traces funds across chains:
- **Bridge Event Correlation**: Lock/mint event matching with tolerance rules
- **DEX Swap Tracing**: Maintains entity labels through token swaps
- **Multi-Chain Stitching**: Unified forensic graph across EVM chains

### Phase 5: Formal Evaluation & Forensic Output

Produces court-admissible output:
- **Evaluation Metrics**: Precision, Recall, F1-Score, Purity, ARI
- **Risk Scoring**: Mixer exposure, VASP proximity, sanctioned entities
- **Interactive HTML**: Pyvis visualization with clickable nodes

---

## Project Structure

```
blockchain_forensics_tool/
├── main.py                     # CLI entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── config/
│   └── settings.py            # Configuration settings
├── src/
│   ├── pipeline.py            # Main orchestration
│   ├── data_acquisition/
│   │   ├── etherscan_client.py
│   │   ├── bridge_events.py
│   │   └── osint_enrichment.py
│   ├── feature_engineering/
│   │   └── feature_extraction.py
│   ├── clustering/
│   │   ├── rule_based_clustering.py
│   │   └── ml_clustering.py
│   ├── cross_chain/
│   │   └── entity_resolution.py
│   ├── evaluation/
│   │   └── forensic_output.py
│   └── utils/
│       ├── helpers.py
│       └── logger.py
├── data/
│   ├── raw/                   # Raw API responses
│   ├── processed/             # Processed data
│   └── output/                # Final outputs
└── logs/                      # Log files
```

---

## Output Files

After running the pipeline, the following files are generated:

| File | Description |
|------|-------------|
| `forensic_graph.html` | Interactive network visualization |
| `forensic_report.json` | Structured forensic report |
| `final_report.json` | Complete pipeline summary |
| `feature_matrix.csv` | Normalized feature vectors |
| `clustering_results.json` | Cluster assignments and evidence |
| `cross_chain_results.json` | Cross-chain correlation data |

---

## Evaluation

### Benchmarking Against Ground Truth

To evaluate against the Elliptic Dataset or other labelled data:

```bash
python main.py -s 0x... -g ground_truth.json
```

**Ground truth format:**
```json
{
  "0x123...": "entity_1",
  "0x456...": "entity_1",
  "0x789...": "entity_2"
}
```

### Expected Metrics

| Metric | Target |
|--------|--------|
| F1-Score | ≥ 0.85 |
| Precision | ≥ 0.80 |
| Recall | ≥ 0.80 |
| Clustering Purity | ≥ 0.85 |

---

## API Integration

### Etherscan API

Required for on-chain data. Get a free API key at https://etherscan.io/myapikey

Rate limits:
- Free tier: 5 calls/second, 100,000 calls/day
- Recommended: Pro tier for large-scale analysis

### Optional APIs

- **Chainabuse**: Address abuse reports
- **OFAC SDN**: Sanctioned entities list

---

## Technical Specifications

| Specification | Value |
|---------------|-------|
| Supported Chains | Ethereum, Arbitrum, Polygon, BSC, Optimism |
| Clustering Complexity | O(α(n)) with Union-Find |
| Scalability | ≥ 10,000 addresses |
| Python Version | 3.10+ |
| Key Libraries | networkx, scikit-learn, pandas, pyvis |

---

## Academic References

1. Victor, F. (2020). *Address Clustering Heuristics for Ethereum*
2. Friedhelm, V. (2023). *Graph Clustering for Blockchain Analysis*
3. Scientific Reports (2025). *Graph Convolutional Networks for Entity Resolution*
4. AnChain.AI (2025). *Cross-Chain Bridge Tracing Demystified*

---

## License

This tool is developed for academic research purposes as part of an M.Sc. dissertation project.

---

## Support

For issues or questions related to this tool, please contact:
- **Author**: Saransh Jhariya
- **Institution**: LNJN NICFS, NFSU Delhi Campus

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | March 2026 | Enhanced methodology with ML augmentation |
| 1.0 | Previous | Baseline heuristic-only approach |
