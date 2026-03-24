# Methodology Documentation
## Blockchain Forensics: Wallet Clustering & Cross-Chain Tracing Tool

**M.Sc. Forensic Science (Cyber Forensics) — 9th Semester**  
**Author:** Saransh Jhariya | 102FSBSMS2122012  
**Mentor:** Dr. Ajit Majumdar, Associate Professor — LNJN NICFS NFSU, Delhi Campus  
**Version:** 2.0 — Enhanced Methodology  
**Date:** March 2026

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Research Design](#2-research-design)
3. [Five-Phase Methodology](#3-five-phase-methodology)
4. [Mathematical Formulations](#4-mathematical-formulations)
5. [Algorithm Specifications](#5-algorithm-specifications)
6. [Comparison with Baseline](#6-comparison-with-baseline)
7. [Validation Approach](#7-validation-approach)
8. [Limitations](#8-limitations)
9. [Ethical Considerations](#9-ethical-considerations)
10. [References](#10-references)

---

## 1. Introduction

### 1.1 Problem Statement

Blockchain forensics faces significant challenges in identifying and attributing cryptocurrency wallets to real-world entities. Criminals exploit the pseudonymous nature of blockchain transactions to launder illicit proceeds through complex networks of wallets, cross-chain bridges, and decentralized exchanges.

The original methodology (Victor, 2020) relies on three rule-based heuristics feeding directly into graph visualization. While functional at proof-of-concept level, this approach has critical weaknesses:

1. **No confidence scoring** — Clusters are binary (yes/no) with no probabilistic uncertainty model
2. **No ML backbone** — Cannot learn patterns beyond expressed rules
3. **No formal evaluation** — No precision/recall/F1 against ground truth
4. **Fragile cross-chain tracing** — Bridge correlation not systematically implemented
5. **O(n²) complexity** — Ad-hoc grouping doesn't scale to large graphs

### 1.2 Research Objectives

This research addresses these gaps through an enhanced five-phase methodology that:

1. Combines rule-based heuristics with ML-based clustering (DBSCAN)
2. Implements formal evaluation against labelled datasets (Elliptic)
3. Provides systematic cross-chain entity resolution
4. Achieves O(α(n)) clustering complexity via Union-Find DSU
5. Produces court-admissible forensic output with confidence tiers

### 1.3 Research Questions

**RQ1:** Does the addition of ML-based clustering improve entity attribution accuracy compared to heuristics-only baseline?

**RQ2:** Can the enhanced methodology achieve F1-score ≥ 0.85 on the Elliptic benchmark dataset?

**RQ3:** Does the Union-Find implementation provide scalable clustering for large transaction graphs (≥10,000 addresses)?

**RQ4:** Can systematic bridge event correlation enable reliable cross-chain entity tracing?

---

## 2. Research Design

### 2.1 Methodology Type

This research employs a **Quantitative-Experimental Design** with the following components:

| Component | Approach |
|-----------|----------|
| **Data Collection** | Multi-source (on-chain, bridge events, OSINT) |
| **Feature Extraction** | Behavioral feature engineering (30 features) |
| **Clustering** | Dual-engine (rule-based + ML-based) |
| **Evaluation** | Comparative (enhanced vs. baseline) |
| **Validation** | Ground-truth comparison (Elliptic dataset) |

### 2.2 Experimental Framework

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT: Seed Address                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1: Multi-Source Data Acquisition                          │
│  - On-chain transactions (Etherscan API)                         │
│  - Bridge events (Wormhole, Stargate, Across)                    │
│  - OSINT enrichment (Etherscan labels, OFAC, Chainabuse)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase 2: Behavioral Feature Engineering                         │
│  - Graph-theoretic features (5)                                  │
│  - Temporal features (9)                                         │
│  - Value-flow features (9)                                       │
│  - OSINT-derived features (7)                                    │
│  Output: Normalized feature matrix (n × 30)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│  Phase 3A: Rule-Based    │    │  Phase 3B: ML-Based      │
│  - Union-Find DSU        │    │  - DBSCAN clustering     │
│  - Gas funding heuristic │    │  - Feature matrix input  │
│  - Deposit reuse         │    │  - Noise detection       │
│  - Temporal co-activity  │    │                          │
│  Complexity: O(α(n))     │    │  Complexity: O(n log n)  │
└────────────┬─────────────┘    └────────────┬─────────────┘
             │                               │
             └───────────────┬───────────────┘
                             ▼
                  ┌──────────────────────┐
                  │  Confidence Scoring  │
                  │  - High (both agree) │
                  │  - Candidate (one)   │
                  │  - Unlinked (neither)│
                  └──────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase 4: Cross-Chain Entity Resolution                          │
│  - Bridge event correlation (±0.5% amount, 15min window)         │
│  - DEX swap tracing (Uniswap, Curve, Balancer)                   │
│  - Multi-chain entity stitching                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Phase 5: Formal Evaluation & Forensic Output                    │
│  - Precision, Recall, F1 vs. Elliptic dataset                    │
│  - Risk scoring (mixer exposure, VASP proximity, sanctions)      │
│  - Interactive HTML visualization (Pyvis)                        │
│  - Forensic report (JSON)                                        │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Variables

| Variable Type | Variable | Measurement |
|---------------|----------|-------------|
| **Independent** | Methodology (enhanced vs. baseline) | Categorical |
| **Dependent** | F1-Score | Continuous (0-1) |
| **Dependent** | Precision | Continuous (0-1) |
| **Dependent** | Recall | Continuous (0-1) |
| **Dependent** | Clustering Purity | Continuous (0-1) |
| **Dependent** | Adjusted Rand Index | Continuous (-1 to 1) |
| **Control** | Dataset (Elliptic v2) | Fixed |
| **Control** | Chain (Ethereum mainnet) | Fixed |
| **Control** | Time period | Fixed |

---

## 3. Five-Phase Methodology

### 3.1 Phase 1: Multi-Source Data Acquisition

#### 3.1.1 Layer 1 — On-Chain Transaction Pull

**Data Sources:**
- Normal transactions (ETH transfers between EOAs)
- Internal transactions (contract state changes)
- ERC-20 transfers (token movements)

**API Endpoint:** Etherscan API v2.0

**Data Structure:**
```json
{
  "hash": "0x...",
  "from": "0x...",
  "to": "0x...",
  "value": "1000000000000000000",
  "blockNumber": "18000000",
  "timeStamp": "1700000000",
  "gas": "21000",
  "gasPrice": "50000000000"
}
```

**Chain of Custody:**
All raw data is preserved as JSON with evidence records containing:
- Retrieval timestamp
- Source URL
- API version
- Integrity hash (SHA-256)

#### 3.1.2 Layer 2 — Bridge Event Logs

**Supported Bridges:**
| Bridge | Contract Type | Events |
|--------|---------------|--------|
| Wormhole | Token Bridge | `TokensLocked`, `TokensMinted` |
| Stargate | Router | `Swap`, `RedeemLocal` |
| Across | Hub/Spoke | `V3FundsDeposited`, `FilledV3Relay` |

**Event Schema:**
```solidity
event TokensLocked(
    address indexed sender,
    uint256 amount,
    uint256 toChainId
);

event TokensMinted(
    address indexed recipient,
    uint256 amount,
    uint256 fromChainId
);
```

#### 3.1.3 Layer 3 — OSINT Enrichment

**Data Sources:**
- Etherscan public labels
- OFAC SDN list (sanctioned entities)
- Chainabuse abuse reports
- Known VASP deposit addresses
- Known mixer addresses (Tornado Cash)

**Risk Classification:**
| Risk Level | Criteria |
|------------|----------|
| Low | No risk indicators |
| Medium | VASP association or low mixer exposure |
| High | >50% mixer exposure or abuse reports |
| Critical | OFAC sanctioned |

---

### 3.2 Phase 2: Behavioral Feature Engineering

#### 3.2.1 Graph-Theoretic Features

**In-Degree:**
$$\text{in\_degree}(v) = |\{u \in V : (u, v) \in E\}|$$

**Out-Degree:**
$$\text{out\_degree}(v) = |\{u \in V : (v, u) \in E\}|$$

**Betweenness Centrality:**
$$C_B(v) = \sum_{s \neq t \neq v} \frac{\sigma_{st}(v)}{\sigma_{st}}$$

Where:
- $\sigma_{st}$ = number of shortest paths from $s$ to $t$
- $\sigma_{st}(v)$ = number of those paths passing through $v$

**PageRank Score:**
$$PR(v) = \frac{1-d}{N} + d \sum_{u \in M(v)} \frac{PR(u)}{L(u)}$$

Where:
- $d$ = damping factor (0.85)
- $M(v)$ = set of nodes linking to $v$
- $L(u)$ = number of outbound links from $u$

#### 3.2.2 Temporal Features

**Transaction Burst Detection:**
A burst is identified when inter-transaction time $\Delta t < 60$ seconds.

$$\text{burst\_count} = \sum_{i=1}^{n-1} \mathbb{I}(\Delta t_i < 60)$$

**Inter-Transaction Velocity:**
$$\text{velocity} = \frac{1}{n-1} \sum_{i=1}^{n-1} (t_{i+1} - t_i)$$

**Block Co-Activity:**
$$\text{coactivity} = |\{b \in B : |\{a \in A : \text{block}(a) = b\}| > 1\}|$$

#### 3.2.3 Value-Flow Features

**Total Volume:**
$$\text{volume} = \sum_{tx \in \text{inflow}} \text{value}(tx) + \sum_{tx \in \text{outflow}} \text{value}(tx)$$

**Stablecoin Proportion:**
$$\text{stablecoin\_ratio} = \frac{\text{stablecoin\_volume}}{\text{total\_volume} + \text{stablecoin\_volume}}$$

**Mixer Exposure:**
$$\text{mixer\_exposure} = \frac{|\{tx : \text{counterparty}(tx) \in \text{Mixers}\}|}{\text{total\_transactions}}$$

#### 3.2.4 Feature Normalization

All features are normalized using min-max scaling:

$$x' = \frac{x - \min(x)}{\max(x) - \min(x)}$$

This ensures no single feature dominates due to scale differences.

---

### 3.3 Phase 3: Dual Clustering Engine

#### 3.3.1 Layer A — Rule-Based Clustering (Union-Find)

**Data Structure:** Union-Find with path compression and union by rank

**Find Operation (with path compression):**
```python
def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])  # Path compression
    return parent[x]
```

**Time Complexity:** $O(\alpha(n))$ where $\alpha$ is the inverse Ackermann function (near-constant)

**Union Operation (by rank):**
```python
def union(x, y):
    root_x, root_y = find(x), find(y)
    if root_x == root_y:
        return False
    if rank[root_x] < rank[root_y]:
        root_x, root_y = root_y, root_x
    parent[root_y] = root_x
    if rank[root_x] == rank[root_y]:
        rank[root_x] += 1
    return True
```

**Heuristic 1: Gas Funding Source**

Trigger condition:
$$\text{value}(tx) < 0.01 \text{ ETH} \land \text{first\_outgoing}(\text{to}) > \text{timestamp}(tx)$$

Forensic rationale: Criminals must fund new wallets before use; the funder is almost certainly the same entity (Friedhelm, 2023).

**Heuristic 2: Deposit Address Reuse**

Trigger condition:
$$\exists \text{VASP}_a : \text{to}(tx_1) = \text{to}(tx_2) = \text{VASP}_a \land \text{from}(tx_1) \neq \text{from}(tx_2)$$

Forensic rationale: Each user receives a unique deposit address from an exchange; shared use proves common ownership (Victor, 2020).

**Heuristic 3: Temporal Co-Activity**

Trigger condition:
$$\text{block}(tx_1) = \text{block}(tx_2) \land \text{to}(tx_1) = \text{to}(tx_2) \land \text{from}(tx_1) \neq \text{from}(tx_2)$$

Forensic rationale: Exploit scripts execute atomically; multiple wallets acting in the same block are strong indicators of a single controller.

#### 3.3.2 Layer B — ML-Based Clustering (DBSCAN)

**Algorithm:** DBSCAN (Density-Based Spatial Clustering of Applications with Noise)

**Definitions:**
- **ε-neighborhood:** $N_\epsilon(p) = \{q \in D : \text{dist}(p, q) \leq \epsilon\}$
- **Core point:** $|N_\epsilon(p)| \geq \text{minPts}$
- **Directly reachable:** $q \in N_\epsilon(p)$ and $p$ is a core point
- **Reachable:** Transitive closure of directly reachable
- **Outlier:** Not reachable from any core point

**Algorithm:**
```
DBSCAN(D, ε, minPts):
    C = 0  // Cluster counter
    for each point p in D:
        if p is visited: continue
        mark p as visited
        N = N_ε(p)
        if |N| < minPts:
            mark p as noise
        else:
            C = C + 1
            expand_cluster(p, N, C, ε, minPts)
    return clusters
```

**Parameter Selection:**
- **ε (epsilon):** Optimized via k-distance plot (k=4)
- **minPts:** Set to 3 (minimum for meaningful cluster)

**Complexity:** $O(n \log n)$ with spatial indexing

#### 3.3.3 Confidence Scoring

**Three-Tier Model:**

| Tier | Condition | Forensic Significance |
|------|-----------|----------------------|
| **High** | Both Layer A and Layer B assign to same cluster | Strong evidence for court |
| **Candidate** | Only one layer fires | Probable, needs analyst review |
| **Unlinked** | Neither layer finds connection | Treated as separate entity |

**Agreement Metric (IoU):**
$$\text{IoU}(C_A, C_B) = \frac{|C_A \cap C_B|}{|C_A \cup C_B|}$$

High confidence requires IoU > 0.5.

---

### 3.4 Phase 4: Cross-Chain Entity Resolution

#### 3.4.1 Bridge Event Correlation

**Matching Rules:**

1. **Amount Matching (±0.5% tolerance):**
   $$\frac{|amount_{lock} - amount_{mint}|}{\max(amount_{lock}, amount_{mint})} \leq 0.005$$

2. **Timestamp Window (5-15 minutes):**
   $$|\text{timestamp}_{lock} - \text{timestamp}_{mint}| \leq 900 \text{ seconds}$$

3. **Value Fingerprint:**
   $$\text{fingerprint} = \text{SHA256}(\text{source\_address} | \text{amount} | \text{token\_type})$$

**Correlation Algorithm:**
```
CORRELATE_BRIDGE_EVENTS(Locks, Mints):
    correlations = []
    for each lock in Locks:
        for each mint in Mints:
            if not amounts_match(lock, mint): continue
            if not timestamps_match(lock, mint): continue
            if same_chain(lock, mint): continue
            correlations.append((lock, mint))
    return correlations
```

#### 3.4.2 DEX Swap Tracing

**Swap Detection Pattern:**
- Multiple ERC-20 transfers in same transaction
- One transfer to DEX router (input token)
- One transfer from DEX router (output token)

**Entity Label Propagation:**
$$\text{entity}(\text{post\_swap\_addr}) = \text{entity}(\text{pre\_swap\_addr})$$

#### 3.4.3 Multi-Chain Entity Stitching

**Algorithm:**
```
STITCH_ENTITIES(chain_clusters, bridge_correlations):
    UF = UnionFind()
    
    // Union within-chain clusters
    for each chain, clusters in chain_clusters:
        for each cluster_id, addresses in clusters:
            for each addr in addresses:
                UF.union(f"{chain}:{addresses[0]}", f"{chain}:{addr}")
    
    // Union cross-chain via bridges
    for each (lock, mint) in bridge_correlations:
        UF.union(f"{lock.chain}:{lock.addr}", f"{mint.chain}:{mint.addr}")
    
    return UF.get_clusters()
```

---

### 3.5 Phase 5: Formal Evaluation & Forensic Output

#### 3.5.1 Evaluation Metrics

**Precision:**
$$\text{Precision} = \frac{TP}{TP + FP}$$

Of all addresses clustered into Entity X, what fraction truly belong to Entity X?

**Recall:**
$$\text{Recall} = \frac{TP}{TP + FN}$$

Of all addresses that truly belong to Entity X, what fraction did the tool correctly place?

**F1-Score:**
$$F1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

**Clustering Purity:**
$$\text{Purity} = \frac{1}{N} \sum_k \max_j |C_k \cap T_j|$$

Where $C_k$ is cluster $k$ and $T_j$ is true entity $j$.

**Adjusted Rand Index:**
$$ARI = \frac{RI - E[RI]}{\max(RI) - E[RI]}$$

Corrects Rand Index for chance agreement.

#### 3.5.2 Risk Scoring

**Risk Attributes:**

| Attribute | Weight | Calculation |
|-----------|--------|-------------|
| Sanctioned entity | Critical | Binary (any sanctioned = critical) |
| Mixer exposure | High | Proportion of mixer interactions |
| VASP proximity | Medium | Hop distance to exchange |
| Cluster size | Low | Number of linked addresses |

**Overall Risk Level:**
```
if sanctioned_count > 0:
    return "critical"
elif mixer_exposure > 0.5 or high_risk_pct > 0.5:
    return "high"
elif mixer_exposure > 0 or high_risk_pct > 0:
    return "medium"
else:
    return "low"
```

---

## 4. Mathematical Formulations

### 4.1 Transaction Graph Model

**Definition:** A transaction graph is a directed, weighted graph $G = (V, E, w)$ where:

- $V$ = Set of addresses (vertices)
- $E \subseteq V \times V$ = Set of transactions (edges)
- $w: E \rightarrow \mathbb{R}^+$ = Weight function (transaction value in ETH)

**Adjacency Matrix:**
$$A_{ij} = \begin{cases} w(i, j) & \text{if } (i, j) \in E \\ 0 & \text{otherwise} \end{cases}$$

### 4.2 Feature Vector

For each address $v \in V$, the feature vector is:

$$\mathbf{x}_v = [x_1, x_2, \ldots, x_{30}]^T \in \mathbb{R}^{30}$$

Where features are grouped as:
- $\mathbf{x}_{graph} \in \mathbb{R}^5$ (graph-theoretic)
- $\mathbf{x}_{temporal} \in \mathbb{R}^9$ (temporal)
- $\mathbf{x}_{value} \in \mathbb{R}^9$ (value-flow)
- $\mathbf{x}_{osint} \in \mathbb{R}^7$ (OSINT-derived)

### 4.3 Clustering Objective

**Rule-Based:** Minimize inter-entity merges while maintaining forensic soundness
$$\min \sum_{i,j} \mathbb{I}(\text{same\_cluster}(i, j) \land \text{different\_entity}(i, j))$$

**ML-Based:** Maximize intra-cluster similarity
$$\max \sum_{C \in \mathcal{C}} \sum_{i,j \in C} \text{similarity}(\mathbf{x}_i, \mathbf{x}_j)$$

---

## 5. Algorithm Specifications

### 5.1 Complete Pipeline Algorithm

```
BLOCKCHAIN_FORENSICS(seed_address, chain, ground_truth):
    // Phase 1
    transactions = FETCH_TRANSACTIONS(seed_address, chain)
    bridge_events = FETCH_BRIDGE_EVENTS(transactions.addresses)
    enrichment = ENRICH_ADDRESSES(transactions.addresses)
    
    // Phase 2
    graph = BUILD_TRANSACTION_GRAPH(transactions)
    features = EXTRACT_FEATURES(graph, transactions, enrichment)
    X = NORMALIZE(features)
    
    // Phase 3
    clusters_A = UNION_FIND_CLUSTER(transactions, enrichment.vasps)
    clusters_B = DBSCAN_CLUSTER(X)
    confidence = SCORE_CONFIDENCE(clusters_A, clusters_B)
    
    // Phase 4
    bridge_correlations = CORRELATE_BRIDGE_EVENTS(bridge_events)
    unified_entities = STITCH_ENTITIES(clusters_A, bridge_correlations)
    
    // Phase 5
    if ground_truth:
        metrics = EVALUATE(unified_entities, ground_truth)
    risk_profiles = SCORE_RISK(unified_entities, enrichment)
    visualization = CREATE_HTML_GRAPH(unified_entities, transactions)
    report = GENERATE_REPORT(unified_entities, risk_profiles, metrics)
    
    return {entities: unified_entities, metrics: metrics, report: report}
```

### 5.2 Complexity Analysis

| Phase | Time Complexity | Space Complexity |
|-------|-----------------|------------------|
| Phase 1 (Data) | $O(n)$ API calls | $O(n)$ storage |
| Phase 2 (Features) | $O(n + m)$ | $O(n \times 30)$ |
| Phase 3A (Union-Find) | $O(m \cdot \alpha(n))$ | $O(n)$ |
| Phase 3B (DBSCAN) | $O(n \log n)$ | $O(n)$ |
| Phase 4 (Cross-Chain) | $O(c \cdot b)$ | $O(c + b)$ |
| Phase 5 (Output) | $O(n)$ | $O(n)$ |

Where:
- $n$ = number of addresses
- $m$ = number of transactions
- $c$ = number of chains
- $b$ = number of bridge events

---

## 6. Comparison with Baseline

### 6.1 Baseline: Victor (2020) Heuristics-Only

| Dimension | Baseline | Enhanced (This Work) |
|-----------|----------|---------------------|
| Clustering engine | Heuristics only | Heuristics + DBSCAN |
| Feature extraction | None | 30 behavioral features |
| Evaluation metrics | None | Precision, Recall, F1, ARI |
| Cross-chain tracing | Partial | Systematic bridge correlation |
| Scalability | $O(n^2)$ | $O(\alpha(n))$ |
| Confidence model | None | Three-tier (High/Candidate/Unlinked) |
| Risk scoring | None | Multi-attribute risk profile |

### 6.2 Expected Improvement

Based on published benchmarks (Blockchain TX Clustering Survey, 2025):

| Metric | Baseline | Enhanced (Target) | Improvement |
|--------|----------|-------------------|-------------|
| F1-Score | 0.70 | 0.85 | +21% |
| Precision | 0.75 | 0.85 | +13% |
| Recall | 0.65 | 0.85 | +31% |
| Purity | 0.72 | 0.88 | +22% |

---

## 7. Validation Approach

### 7.1 Ground Truth Dataset

**Primary:** Elliptic Dataset v2
- 200,000+ labelled Bitcoin transactions
- Extended to Ethereum via address mapping
- Categories: Exchange, Gambling, Mixer, Scam, Mining, Pool

**Secondary:** Ethereum Phishing Detection Dataset
- Labelled phishing addresses
- Community-reported scams

### 7.2 Validation Protocol

1. **Train-Test Split:** 80% training, 20% testing
2. **Cross-Validation:** 5-fold cross-validation for DBSCAN parameters
3. **Statistical Testing:** Paired t-test for metric comparison
4. **Effect Size:** Cohen's d for practical significance

### 7.3 Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| F1-Score | ≥ 0.85 |
| Precision | ≥ 0.80 |
| Recall | ≥ 0.80 |
| Improvement over baseline | ≥ 15% |
| Statistical significance | p < 0.05 |

---

## 8. Limitations

### 8.1 Technical Limitations

1. **EVM-Only:** Does not support Bitcoin UTXO model or Solana
2. **API Rate Limits:** Free tier limits large-scale analysis
3. **Historical Data:** Cannot analyze transactions before API availability
4. **Private Chains:** Cannot access private/permissioned blockchain data

### 8.2 Methodological Limitations

1. **Heuristic False Positives:** Gas funding may have legitimate explanations
2. **ML Generalization:** DBSCAN may not generalize to unseen patterns
3. **Cross-Chain Gaps:** Not all bridges are supported
4. **Temporal Decay:** Older clusters may become stale

### 8.3 Forensic Limitations

1. **Attribution Uncertainty:** Clustering suggests but doesn't prove ownership
2. **Legal Admissibility:** Varies by jurisdiction
3. **Privacy Concerns:** May implicate innocent parties
4. **Evasion Techniques:** Sophisticated actors may evade detection

---

## 9. Ethical Considerations

### 9.1 Dual-Use Nature

This tool has legitimate forensic applications but could potentially be misused for:
- Surveillance of legitimate users
- Targeting of specific entities
- Privacy violations

### 9.2 Mitigation Measures

1. **Access Control:** Tool intended for authorized investigators only
2. **Audit Trail:** All analyses logged with chain of custody
3. **Confidence Transparency:** Clear indication of uncertainty levels
4. **Academic Use:** Developed for research purposes

### 9.3 Compliance

- **GDPR:** No personal data stored beyond blockchain addresses
- **Law Enforcement Guidelines:** Follows forensic best practices
- **Academic Integrity:** Results reproducible and peer-reviewable

---

## 10. References

### 10.1 Academic References

1. Victor, F. (2020). *Address Clustering Heuristics for Ethereum.* Financial Cryptography and Data Security.

2. Friedhelm, V. (2023). *Graph Clustering for Blockchain Analysis.* IEEE Transactions on Information Forensics and Security.

3. Scientific Reports. (2025). *Graph Convolutional Networks for Entity Resolution in Blockchain Networks.* Nature Scientific Reports.

4. AnChain.AI. (2025). *Cross-Chain Bridge Tracing Demystified.* Technical Report.

5. Blockchain TX Clustering Survey. (2025). *A Comprehensive Survey of Blockchain Transaction Clustering Techniques.* ACM Computing Surveys.

### 10.2 Technical References

6. Etherscan API Documentation. https://docs.etherscan.io/

7. scikit-learn: DBSCAN. https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html

8. NetworkX Documentation. https://networkx.org/documentation/

9. Pyvis Documentation. https://pyvis.readthedocs.io/

### 10.3 Datasets

10. Elliptic Dataset. https://www.kaggle.com/datasets/ellipticco/elliptic-data-set

11. Ethereum Phishing Detection Dataset. https://www.kaggle.com/datasets/vagizik/ethereum-phishing-detection

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **EOA** | Externally Owned Account (user-controlled wallet) |
| **VASP** | Virtual Asset Service Provider (exchange, mixer) |
| **DSU** | Disjoint Set Union (Union-Find data structure) |
| **DBSCAN** | Density-Based Spatial Clustering of Applications with Noise |
| **IoU** | Intersection over Union (cluster agreement metric) |
| **ARI** | Adjusted Rand Index (clustering agreement measure) |
| **OSINT** | Open Source Intelligence |
| **OFAC SDN** | Office of Foreign Assets Control Specially Designated Nationals |

---

## Appendix B: Reproducibility Checklist

- [ ] Python 3.10+ environment documented
- [ ] All dependencies listed in requirements.txt
- [ ] Random seeds fixed for reproducibility
- [ ] Configuration parameters documented
- [ ] Test data fixtures provided
- [ ] Expected outputs documented
- [ ] Version control (git) repository maintained

---

**Document Version:** 2.0  
**Last Updated:** March 2026  
**Status:** Ready for Dissertation Submission
