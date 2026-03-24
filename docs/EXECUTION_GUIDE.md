# Execution Guide
## Blockchain Forensics Tool - Wallet Clustering & Cross-Chain Tracing

**M.Sc. Forensic Science (Cyber Forensics) — 9th Semester**  
**Author:** Saransh Jhariya | 102FSBSMS2122012  
**Mentor:** Dr. Ajit Majumdar, Associate Professor — LNJN NICFS NFSU, Delhi Campus  
**Version:** 2.0 — Enhanced Methodology  
**Date:** March 2026

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Detailed Installation](#2-detailed-installation)
3. [Configuration](#3-configuration)
4. [Running the Tool](#4-running-the-tool)
5. [Understanding Output](#5-understanding-output)
6. [Sample Execution Workflow](#6-sample-execution-workflow)
7. [Advanced Usage](#7-advanced-usage)

---

## 1. Quick Start

### 5-Minute Setup

```bash
# 1. Navigate to project directory
cd blockchain_forensics_tool

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment template
cp .env.example .env

# 4. Edit .env and add your Etherscan API key
#    Get free API key from: https://etherscan.io/myapikey

# 5. Run analysis
python main.py -s 0x1234567890abcdef1234567890abcdef12345678 -v
```

### Expected Output
```
INFO: ============================================================
INFO: BLOCKCHAIN FORENSICS TOOL v2.0
INFO: M.Sc. Forensic Science (Cyber Forensics) - 9th Semester
INFO: Author: Saransh Jhariya | 102FSBSMS2122012
INFO: Mentor: Dr. Ajit Majumdar, LNJN NICFS NFSU, Delhi Campus
INFO: ============================================================
INFO: ============================================================
INFO: Phase 1: Multi-Source Data Acquisition
INFO: ============================================================
...
```

---

## 2. Detailed Installation

### 2.1 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.10 | 3.11+ |
| RAM | 4 GB | 8 GB+ |
| Storage | 1 GB | 5 GB+ |
| Internet | Required | Broadband |

### 2.2 Python Installation

#### Windows
```powershell
# Download from https://www.python.org/downloads/
# During installation, check "Add Python to PATH"

# Verify installation
python --version
pip --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
python3 --version
```

#### macOS
```bash
# Using Homebrew
brew install python@3.11
python3 --version
```

### 2.3 Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/macOS
source venv/bin/activate

# Verify activation
which python  # Should point to venv
```

### 2.4 Install Dependencies

```bash
# Navigate to project directory
cd blockchain_forensics_tool

# Install all dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "networkx|sklearn|pandas|pyvis"
```

### 2.5 Dependency Verification

Run this command to verify all dependencies are installed:

```bash
python -c "
import networkx; print(f'networkx: {networkx.__version__}')
import sklearn; print(f'scikit-learn: {sklearn.__version__}')
import pandas; print(f'pandas: {pandas.__version__}')
import numpy; print(f'numpy: {numpy.__version__}')
import pyvis; print(f'pyvis: {pyvis.__version__}')
print('All dependencies verified!')
"
```

---

## 3. Configuration

### 3.1 Environment File Setup

```bash
# Copy template
cp .env.example .env
```

### 3.2 Edit .env File

Open `.env` in a text editor and configure:

```bash
# Required: Etherscan API Key
# Get from: https://etherscan.io/myapikey
ETHERSCAN_API_KEY=YourApiKeyHere1234567890ABCDEF

# Optional: Chainabuse API Key
# Get from: https://www.chainabuse.com/
CHAINABUSE_API_KEY=your_chainabuse_api_key

# Optional: Custom ETH Price (default: 2000)
ETH_PRICE_USD=2000

# Optional: Custom RPC URLs (defaults use public endpoints)
ETHEREUM_RPC_URL=https://eth.llamarpc.com
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
POLYGON_RPC_URL=https://polygon-rpc.com
```

### 3.3 Getting Etherscan API Key

1. Visit https://etherscan.io/myapikey
2. Sign up / Log in
3. Click "Add" to create new API key
4. Enter any application name (e.g., "Forensics Tool")
5. Copy the API key to your `.env` file

**Rate Limits:**
- Free: 5 calls/second, 100,000 calls/day
- Pro: 100 calls/second, 1,000,000 calls/day

### 3.4 Configuration Validation

Run this to verify your configuration:

```bash
python -c "
from config.settings import ETHERSCAN_API_KEY, SUPPORTED_CHAINS
print(f'API Key configured: {bool(ETHERSCAN_API_KEY)}')
print(f'Supported chains: {list(SUPPORTED_CHAINS.keys())}')
"
```

---

## 4. Running the Tool

### 4.1 Command-Line Interface

```
usage: main.py [-h] --seed SEED [--chain CHAIN] [--output OUTPUT]
               [--ground-truth GROUND_TRUTH] [--eth-price ETH_PRICE]
               [--multi-chain] [--verbose] [--version]
```

### 4.2 Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `--seed, -s` | Seed Ethereum address | `0x1234...5678` |

### 4.3 Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--chain, -c` | ethereum | Chain: ethereum, arbitrum, polygon, bsc, optimism |
| `--output, -o` | data/output | Output directory |
| `--ground-truth, -g` | None | Ground truth JSON for evaluation |
| `--eth-price` | 2000 | ETH price in USD |
| `--multi-chain` | False | Enable multi-chain analysis |
| `--verbose, -v` | False | Verbose logging |
| `--version` | - | Show version |

### 4.4 Basic Execution Examples

#### Single Address Analysis
```bash
python main.py -s 0xdAC17F958D2ee523a2206206994597C13D831ec7
```

#### With Verbose Output
```bash
python main.py -s 0xdAC17F958D2ee523a2206206994597C13D831ec7 -v
```

#### Specify Chain
```bash
python main.py -s 0x... --chain polygon
```

#### Custom Output Directory
```bash
python main.py -s 0x... -o ./my_results
```

#### With Ground Truth Evaluation
```bash
python main.py -s 0x... -g elliptic_labels.json
```

### 4.5 Pipeline Execution Flow

When you run the tool, it executes five phases:

```
Seed Address Input
       │
       ▼
┌─────────────────────────────────┐
│ Phase 1: Data Acquisition       │
│ - Fetch transactions            │
│ - Get bridge events             │
│ - OSINT enrichment              │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ Phase 2: Feature Engineering    │
│ - Graph features                │
│ - Temporal features             │
│ - Value-flow features           │
│ - OSINT features                │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ Phase 3: Dual Clustering        │
│ - Union-Find (rule-based)       │
│ - DBSCAN (ML-based)             │
│ - Confidence scoring            │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ Phase 4: Cross-Chain Resolution │
│ - Bridge correlation            │
│ - DEX swap tracing              │
│ - Multi-chain stitching         │
└───────────────┬─────────────────┘
                │
                ▼
┌─────────────────────────────────┐
│ Phase 5: Evaluation & Output    │
│ - Precision/Recall/F1           │
│ - Risk scoring                  │
│ - HTML visualization            │
└─────────────────────────────────┘
```

---

## 5. Understanding Output

### 5.1 Output Directory Structure

```
data/
├── raw/
│   ├── layer1_ethereum_0x....json    # On-chain transactions
│   └── layer3_osint_ethereum.json    # OSINT enrichment
├── processed/
│   ├── feature_matrix.csv            # Normalized features
│   ├── clustering_results.json       # Cluster assignments
│   └── cross_chain_results.json      # Cross-chain data
└── output/
    ├── forensic_graph.html           # Interactive visualization
    ├── forensic_report.json          # Structured report
    └── final_report.json             # Complete summary
```

### 5.2 Output File Descriptions

#### forensic_graph.html
Interactive network visualization with:
- Color-coded nodes by entity cluster
- Confidence tier borders (green=high, orange=candidate, gray=unlinked)
- Clickable nodes linking to Etherscan
- Edge weights proportional to transaction volume

#### forensic_report.json
```json
{
  "report_metadata": {
    "generated_by": "blockchain_forensics_tool_v2.0",
    "methodology": "Enhanced Five-Phase Methodology",
    "author": "Saransh Jhariya | 102FSBSMS2122012"
  },
  "summary": {
    "total_entities": 15,
    "total_addresses": 150,
    "high_risk_entities": 3,
    "critical_risk_entities": 1
  },
  "evaluation_metrics": {
    "precision": 0.87,
    "recall": 0.82,
    "f1_score": 0.84
  },
  "entity_clusters": {...},
  "risk_profiles": {...}
}
```

#### final_report.json
Complete pipeline summary including all phase results.

#### feature_matrix.csv
Normalized feature vectors for each address (30 features).

### 5.3 Interpreting Results

#### Confidence Tiers
| Tier | Meaning | Forensic Significance |
|------|---------|----------------------|
| **High** | Both rule-based and ML agree | Strong evidence for court |
| **Candidate** | Only one layer fires | Probable, needs review |
| **Unlinked** | Neither finds connection | Separate entity |

#### Risk Levels
| Level | Criteria |
|-------|----------|
| **Critical** | Sanctioned entity present |
| **High** | >50% mixer exposure or >50% high-risk addresses |
| **Medium** | Some mixer exposure or high-risk addresses |
| **Low** | No significant risk indicators |

---

## 6. Sample Execution Workflow

### 6.1 Complete Investigation Example

**Scenario:** Investigate a suspected phishing wallet

```bash
# Step 1: Set up
cd blockchain_forensics_tool
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Step 2: Run analysis
python main.py \
  -s 0xdAC17F958D2ee523a2206206994597C13D831ec7 \
  --chain ethereum \
  --output ./case_001 \
  --verbose

# Step 3: Review output
# Open forensic_graph.html in browser
# Review forensic_report.json

# Step 4: Export evidence
# Copy data/output/ folder for case files
```

### 6.2 Expected Console Output

```
INFO: ============================================================
INFO: BLOCKCHAIN FORENSICS TOOL v2.0
INFO: ============================================================
INFO: Pipeline initialized for seed address: 0xdac17f958d2ee523a2206206994597c13d831ec7
INFO: ============================================================
INFO: Phase 1: Multi-Source Data Acquisition
INFO: ============================================================
INFO: Fetching normal transactions for 0xdac17f958d2ee523a2206206994597c13d831ec7
INFO: Fetching internal transactions...
INFO: Fetching ERC-20 transfers...
INFO: Enriching 150 addresses with OSINT data
INFO: Phase 1 complete: 150 addresses collected
INFO: ============================================================
INFO: Phase 2: Behavioral Feature Engineering
INFO: ============================================================
INFO: Starting Phase 2 feature engineering for 150 addresses
INFO: Built transaction graph with 150 nodes and 342 edges
INFO: Computing betweenness centrality...
INFO: Computing PageRank...
INFO: Extracting temporal features...
INFO: Extracting value-flow features...
INFO: Extracting OSINT features...
INFO: Normalizing features...
INFO: Feature engineering complete: 150 addresses × 30 features
INFO: ============================================================
INFO: Phase 3: Dual Clustering Engine
INFO: ============================================================
INFO: Starting Layer A: Rule-Based Clustering (Union-Find)
INFO: Gas funding heuristic: 23 unions performed
INFO: Deposit address reuse heuristic: 15 unions performed
INFO: Temporal co-activity heuristic: 8 unions performed
INFO: Layer A complete: 45 clusters identified
INFO: Starting Layer B: ML-Based Clustering (DBSCAN)
INFO: Optimizing epsilon parameter using k-distance plot (k=4)
INFO: Optimal epsilon: 0.4523
INFO: DBSCAN complete: 38 clusters, 12 noise points
INFO: Silhouette score: 0.7234
INFO: Computing confidence scores (reconciling Layer A and Layer B)
INFO: Confidence scoring complete: {'high': 98, 'candidate': 40, 'unlinked': 12}
INFO: ============================================================
INFO: Phase 3 Complete: 45 entity clusters identified
INFO: ============================================================
INFO: ============================================================
INFO: Phase 4: Cross-Chain Entity Resolution
INFO: ============================================================
INFO: Starting bridge event correlation across chains
INFO: Bridge event correlation complete: 5 cross-chain transfers identified
INFO: Extracting DEX swap events from transaction data
INFO: Identified 23 potential DEX swaps
INFO: Starting multi-chain entity stitching
INFO: Multi-chain stitching complete: 42 unified entities
INFO: ============================================================
INFO: Phase 4 Complete: 42 entities, 8 multi-chain
INFO: ============================================================
INFO: ============================================================
INFO: Phase 5: Formal Evaluation & Forensic Output
INFO: ============================================================
INFO: Computing risk scores for entity clusters
INFO: Risk distribution: {'low': 35, 'medium': 5, 'high': 2, 'critical': 0}
INFO: Building forensic graph for visualization
INFO: Graph built: 150 nodes, 342 edges
INFO: Creating interactive HTML visualization: forensic_graph.html
INFO: Interactive HTML saved to data/output/forensic_graph.html
INFO: Creating forensic report: forensic_report.json
INFO: Forensic report saved to data/output/forensic_report.json
INFO: ============================================================
INFO: Phase 5 Complete:
INFO:   - Interactive Graph: data/output/forensic_graph.html
INFO:   - Forensic Report: data/output/forensic_report.json
INFO: ============================================================
INFO: ============================================================
INFO: PIPELINE COMPLETE
INFO: Final Report: data/output/final_report.json
INFO: ============================================================

INVESTIGATION SUMMARY
----------------------------------------
Seed Address: 0xdac17f958d2ee523a2206206994597c13d831ec7
Chain: ethereum
Total Addresses Analyzed: 150
Entity Clusters Identified: 45

Risk Distribution:
  MEDIUM: 5 entities
  HIGH: 2 entities
  LOW: 35 entities

Output Files:
  interactive_graph: data/output/forensic_graph.html
  forensic_report: data/output/forensic_report.json

Investigation complete.
```

---

## 7. Advanced Usage

### 7.1 Multi-Chain Analysis

```bash
# Analyze across multiple chains
python main.py -s 0x... --chain ethereum --multi-chain
```

### 7.2 Evaluation Against Ground Truth

Create ground truth file `elliptic_labels.json`:
```json
{
  "0x1234567890abcdef1234567890abcdef12345678": "entity_1",
  "0x2345678901abcdef2345678901abcdef23456789": "entity_1",
  "0x3456789012abcdef3456789012abcdef34567890": "entity_2"
}
```

Run with evaluation:
```bash
python main.py -s 0x... -g elliptic_labels.json
```

### 7.3 Programmatic Usage

```python
from src.pipeline import run_forensics

# Run complete pipeline
results = run_forensics(
    seed_address="0x1234567890abcdef1234567890abcdef12345678",
    chain="ethereum",
    output_dir="./results",
    ground_truth_path="labels.json"  # Optional
)

# Access results
print(f"Total entities: {results['phase3_summary']['total_clusters']}")
print(f"F1 Score: {results['phase5_summary']['evaluation_metrics']['f1_score']}")
```

### 7.4 Batch Processing

```bash
#!/bin/bash
# batch_analysis.sh

ADDRESSES=(
    "0x1234567890abcdef1234567890abcdef12345678"
    "0x2345678901abcdef2345678901abcdef23456789"
    "0x3456789012abcdef3456789012abcdef34567890"
)

for addr in "${ADDRESSES[@]}"; do
    echo "Analyzing $addr"
    python main.py -s "$addr" -o "./batch_results/${addr:0:10}"
done
```

### 7.5 Performance Tips

1. **Use Pro API Key** for large investigations (>1000 addresses)
2. **Enable caching** by keeping `data/raw/` files
3. **Adjust DBSCAN parameters** in `config/settings.py` for better clustering
4. **Use multi-chain** only when necessary (increases API calls)

---

## Appendix A: Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `Invalid API key` | Check `.env` file and Etherscan key |
| `Rate limit exceeded` | Wait 60 seconds or upgrade API key |
| `No transactions found` | Verify address is correct and has activity |
| `Memory error` | Reduce batch size or increase RAM |

---

## Appendix B: File Permissions

On Linux/macOS, you may need to set execute permissions:

```bash
chmod +x main.py
```

---

## Appendix C: Logs

Logs are stored in `logs/` directory:
```
logs/
└── forensics_20260324_143052.log
```

View latest log:
```bash
tail -f logs/forensics_*.log
```

---

**Document Version:** 2.0  
**Last Updated:** March 2026
