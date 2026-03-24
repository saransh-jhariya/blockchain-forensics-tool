"""
Phase 5: Formal Evaluation & Forensic Output
Evaluation metrics, risk scoring, and interactive HTML visualization.
"""

import json
import os
from typing import Dict, List, Optional, Tuple

import networkx as nx
import pandas as pd
from pyvis.network import Network
from sklearn.metrics import (
    adjusted_rand_score,
    f1_score,
    precision_score,
    recall_score,
)

from src.utils.helpers import normalize_address, save_json
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ClusteringEvaluator:
    """
    Evaluates clustering performance against ground truth labels.
    
    Metrics:
    - Precision, Recall, F1-Score
    - Clustering Purity
    - Adjusted Rand Index (ARI)
    """
    
    def __init__(self):
        """Initialize clustering evaluator."""
        self.metrics = {}
    
    def compute_pairwise_metrics(
        self,
        predicted_clusters: Dict[str, List[str]],
        ground_truth: Dict[str, str],
    ) -> Dict[str, float]:
        """
        Compute pairwise precision, recall, F1.
        
        Args:
            predicted_clusters: Predicted cluster assignments (cluster_id -> addresses)
            ground_truth: Ground truth labels (address -> entity_id)
            
        Returns:
            Dictionary of evaluation metrics
        """
        logger.info("Computing pairwise evaluation metrics")
        
        # Convert to pairwise same-cluster judgments
        addresses = list(ground_truth.keys())
        n = len(addresses)
        
        y_true = []
        y_pred = []
        
        # Create predicted cluster mapping
        pred_mapping = {}
        for cluster_id, addrs in predicted_clusters.items():
            for addr in addrs:
                pred_mapping[normalize_address(addr)] = cluster_id
        
        # Generate pairwise comparisons
        for i in range(n):
            for j in range(i + 1, n):
                addr_i = normalize_address(addresses[i])
                addr_j = normalize_address(addresses[j])
                
                # Ground truth: same entity?
                same_entity_gt = ground_truth[addr_i] == ground_truth[addr_j]
                
                # Prediction: same cluster?
                cluster_i = pred_mapping.get(addr_i)
                cluster_j = pred_mapping.get(addr_j)
                same_cluster_pred = cluster_i is not None and cluster_j is not None and cluster_i == cluster_j
                
                y_true.append(1 if same_entity_gt else 0)
                y_pred.append(1 if same_cluster_pred else 0)
        
        # Compute metrics
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        self.metrics = {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "total_pairs": len(y_true),
            "positive_pairs_gt": sum(y_true),
            "positive_pairs_pred": sum(y_pred),
        }
        
        logger.info(f"Pairwise metrics: Precision={precision:.4f}, Recall={recall:.4f}, F1={f1:.4f}")
        
        return self.metrics
    
    def compute_ari(
        self,
        predicted_labels: List[int],
        ground_truth_labels: List[int],
    ) -> float:
        """
        Compute Adjusted Rand Index.
        
        Args:
            predicted_labels: Predicted cluster labels
            ground_truth_labels: True entity labels
            
        Returns:
            ARI score
        """
        ari = adjusted_rand_score(ground_truth_labels, predicted_labels)
        self.metrics["adjusted_rand_index"] = ari
        logger.info(f"Adjusted Rand Index: {ari:.4f}")
        return ari
    
    def compute_purity(
        self,
        predicted_clusters: Dict[str, List[str]],
        ground_truth: Dict[str, str],
    ) -> float:
        """
        Compute clustering purity.
        
        Args:
            predicted_clusters: Predicted clusters
            ground_truth: Ground truth labels
            
        Returns:
            Purity score (0-1)
        """
        total_correct = 0
        total_addresses = 0
        
        for cluster_id, addresses in predicted_clusters.items():
            # Find dominant entity in cluster
            entity_counts = {}
            for addr in addresses:
                addr = normalize_address(addr)
                entity = ground_truth.get(addr, "unknown")
                entity_counts[entity] = entity_counts.get(entity, 0) + 1
            
            if entity_counts:
                dominant_count = max(entity_counts.values())
                total_correct += dominant_count
                total_addresses += len(addresses)
        
        purity = total_correct / total_addresses if total_addresses > 0 else 0
        self.metrics["purity"] = purity
        logger.info(f"Clustering purity: {purity:.4f}")
        
        return purity
    
    def evaluate_baseline_comparison(
        self,
        enhanced_metrics: Dict[str, float],
        baseline_metrics: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Compare enhanced methodology against baseline.
        
        Args:
            enhanced_metrics: Metrics from enhanced (ML-augmented) pipeline
            baseline_metrics: Metrics from baseline (heuristics-only) pipeline
            
        Returns:
            Comparison metrics showing improvement
        """
        comparison = {}
        
        for metric in ["precision", "recall", "f1_score", "purity"]:
            baseline_val = baseline_metrics.get(metric, 0)
            enhanced_val = enhanced_metrics.get(metric, 0)
            
            if baseline_val > 0:
                improvement = ((enhanced_val - baseline_val) / baseline_val) * 100
            else:
                improvement = 100 if enhanced_val > 0 else 0
            
            comparison[f"{metric}_baseline"] = baseline_val
            comparison[f"{metric}_enhanced"] = enhanced_val
            comparison[f"{metric}_improvement_pct"] = improvement
        
        logger.info("Baseline vs Enhanced Comparison:")
        logger.info(f"  F1 Score: {baseline_metrics.get('f1_score', 0):.4f} -> {enhanced_metrics.get('f1_score', 0):.4f} "
                   f"({comparison.get('f1_score_improvement_pct', 0):.1f}% improvement)")
        
        return comparison


class RiskScorer:
    """
    Assigns risk scores to entity clusters.
    
    Risk attributes:
    - Mixer exposure %
    - VASP proximity
    - Cluster size
    - Sanctioned entity flag
    - Confidence tier
    """
    
    def __init__(
        self,
        enrichment_data: Dict[str, Dict],
        confidence_results: Dict[str, Dict],
    ):
        """
        Initialize risk scorer.
        
        Args:
            enrichment_data: OSINT enrichment data from Phase 1
            confidence_results: Confidence scoring from Phase 3
        """
        self.enrichment_data = enrichment_data
        self.confidence_results = confidence_results
    
    def compute_risk_scores(
        self,
        clusters: Dict[str, List[str]],
    ) -> Dict[str, Dict]:
        """
        Compute risk scores for all clusters.
        
        Args:
            clusters: Entity clusters
            
        Returns:
            Dictionary of cluster_id -> risk profile
        """
        logger.info("Computing risk scores for entity clusters")
        
        risk_profiles = {}
        
        for cluster_id, addresses in clusters.items():
            profile = self._compute_cluster_risk(cluster_id, addresses)
            risk_profiles[cluster_id] = profile
        
        # Summary statistics
        risk_distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for profile in risk_profiles.values():
            risk_distribution[profile["overall_risk_level"]] += 1
        
        logger.info(f"Risk distribution: {risk_distribution}")
        
        return risk_profiles
    
    def _compute_cluster_risk(
        self,
        cluster_id: str,
        addresses: List[str],
    ) -> Dict:
        """
        Compute risk profile for a single cluster.
        
        Args:
            cluster_id: Cluster identifier
            addresses: Addresses in cluster
            
        Returns:
            Risk profile dictionary
        """
        mixer_exposure = 0
        sanctioned_count = 0
        vasp_proximity = float('inf')
        high_risk_count = 0
        confidence_tiers = []
        
        for addr in addresses:
            addr = normalize_address(addr)
            enrichment = self.enrichment_data.get(addr, {})
            confidence = self.confidence_results.get(addr, {})
            
            # Mixer exposure
            if enrichment.get("is_mixer"):
                mixer_exposure += 1
            
            # Sanctioned check
            if enrichment.get("is_sanctioned"):
                sanctioned_count += 1
            
            # VASP check
            if enrichment.get("is_vasp"):
                vasp_proximity = 0
            
            # High risk check
            if enrichment.get("risk_level") in ["high", "critical"]:
                high_risk_count += 1
            
            # Confidence tier
            tier = confidence.get("confidence_tier", "unlinked")
            confidence_tiers.append(tier)
        
        total = len(addresses)
        
        # Calculate mixer exposure percentage
        mixer_exposure_pct = (mixer_exposure / total * 100) if total > 0 else 0
        
        # Determine overall risk level
        if sanctioned_count > 0:
            overall_risk = "critical"
        elif mixer_exposure_pct > 50 or high_risk_count > total / 2:
            overall_risk = "high"
        elif mixer_exposure_pct > 0 or high_risk_count > 0:
            overall_risk = "medium"
        else:
            overall_risk = "low"
        
        # Calculate confidence score
        tier_scores = {"high": 3, "candidate": 2, "unlinked": 1}
        avg_confidence = sum(tier_scores.get(t, 1) for t in confidence_tiers) / len(confidence_tiers) if confidence_tiers else 1
        
        return {
            "cluster_id": cluster_id,
            "total_addresses": total,
            "mixer_exposure_pct": mixer_exposure_pct,
            "sanctioned_count": sanctioned_count,
            "vasp_proximity": 0 if vasp_proximity == 0 else "unknown",
            "high_risk_address_count": high_risk_count,
            "high_risk_address_pct": (high_risk_count / total * 100) if total > 0 else 0,
            "overall_risk_level": overall_risk,
            "avg_confidence_score": avg_confidence,
            "dominant_confidence_tier": max(set(confidence_tiers), key=confidence_tiers.count) if confidence_tiers else "unlinked",
        }


class ForensicVisualizer:
    """
    Creates interactive HTML forensic graph visualizations.
    
    Features:
    - Color-coded nodes by entity cluster and confidence tier
    - Edge weights proportional to transaction volume
    - Cross-chain edges as dashed lines
    - Clickable nodes linking to Etherscan
    """
    
    def __init__(self, output_dir: str = "data/output"):
        """
        Initialize forensic visualizer.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def build_forensic_graph(
        self,
        normal_txs: List[Dict],
        erc20_txs: List[Dict],
        clusters: Dict[str, List[str]],
        confidence_results: Dict[str, Dict],
        cross_chain_edges: List[Tuple],
    ) -> nx.DiGraph:
        """
        Build NetworkX graph for visualization.
        
        Args:
            normal_txs: Normal transactions
            erc20_txs: ERC-20 token transfers
            clusters: Entity clusters
            confidence_results: Confidence scoring results
            cross_chain_edges: Cross-chain bridge edges
            
        Returns:
            NetworkX directed graph
        """
        logger.info("Building forensic graph for visualization")
        
        G = nx.DiGraph()
        
        # Create address to cluster mapping
        addr_to_cluster = {}
        for cluster_id, addresses in clusters.items():
            for addr in addresses:
                addr_to_cluster[normalize_address(addr)] = cluster_id
        
        # Add nodes with attributes
        for addr, cluster_id in addr_to_cluster.items():
            confidence = confidence_results.get(addr, {})
            G.add_node(
                addr,
                cluster_id=cluster_id,
                confidence_tier=confidence.get("confidence_tier", "unlinked"),
                label=f"{addr[:8]}...{addr[-6:]}",
            )
        
        # Add edges from transactions
        for tx in normal_txs:
            from_addr = normalize_address(tx.get("from", ""))
            to_addr = normalize_address(tx.get("to", ""))
            value_eth = float(tx.get("value", 0)) / 1e18
            
            if from_addr in G and to_addr in G:
                if G.has_edge(from_addr, to_addr):
                    G[from_addr][to_addr]["weight"] += value_eth
                    G[from_addr][to_addr]["tx_count"] += 1
                else:
                    G.add_edge(
                        from_addr, to_addr,
                        weight=value_eth,
                        tx_count=1,
                        edge_type="transaction",
                    )
        
        # Add cross-chain edges
        for source, dest, attrs in cross_chain_edges:
            if source in G and dest in G:
                G.add_edge(
                    source, dest,
                    weight=10,  # High weight for cross-chain
                    tx_count=1,
                    edge_type="cross_chain",
                    **attrs,
                )
        
        logger.info(f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        return G
    
    def create_interactive_html(
        self,
        G: nx.DiGraph,
        filename: str = "forensic_graph.html",
        title: str = "Blockchain Forensic Graph",
    ) -> str:
        """
        Create interactive HTML visualization using Pyvis.
        
        Args:
            G: NetworkX graph
            filename: Output filename
            title: Graph title
            
        Returns:
            Path to generated HTML file
        """
        logger.info(f"Creating interactive HTML visualization: {filename}")
        
        # Create Pyvis network
        net = Network(
            height="800px",
            width="100%",
            bgcolor="#222222",
            font_color="white",
            directed=True,
        )
        
        # Color schemes
        cluster_colors = {}
        confidence_colors = {
            "high": "#00ff00",  # Green
            "candidate": "#ffa500",  # Orange
            "unlinked": "#888888",  # Gray
        }
        
        # Add nodes
        for node in G.nodes(data=True):
            addr = node[0]
            attrs = node[1]
            
            cluster_id = attrs.get("cluster_id", "unknown")
            confidence = attrs.get("confidence_tier", "unlinked")
            
            # Assign cluster color
            if cluster_id not in cluster_colors:
                # Generate consistent color for cluster
                color_hash = hash(cluster_id) % 360
                cluster_colors[cluster_id] = f"hsl({color_hash}, 70%, 50%)"
            
            # Node color based on confidence
            border_color = confidence_colors.get(confidence, "#888888")
            
            net.add_node(
                addr,
                label=attrs.get("label", addr[:10]),
                title=f"Address: {addr}<br>Cluster: {cluster_id}<br>Confidence: {confidence}<br><a href='https://etherscan.io/address/{addr}' target='_blank'>View on Etherscan</a>",
                color=cluster_colors[cluster_id],
                border_width=3,
                border_color=border_color,
                size=15,
            )
        
        # Add edges
        for edge in G.edges(data=True):
            source, dest, attrs = edge
            
            edge_type = attrs.get("edge_type", "transaction")
            weight = attrs.get("weight", 1)
            
            if edge_type == "cross_chain":
                net.add_edge(
                    source, dest,
                    value=weight,
                    dashes=True,
                    color="#ff00ff",
                    title="Cross-chain bridge transfer",
                )
            else:
                net.add_edge(
                    source, dest,
                    value=weight,
                    color="#00ffff",
                    title=f"Transaction<br>Volume: {weight:.4f} ETH",
                )
        
        # Enable physics
        net.set_options("""
        {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 100,
                    "springConstant": 0.18
                },
                "maxVelocity": 146,
                "solver": "forceAtlas2Based",
                "timestep": 0.35,
                "stabilization": {
                    "iterations": 150
                }
            }
        }
        """)
        
        # Save HTML
        filepath = os.path.join(self.output_dir, filename)
        net.save_graph(filepath)
        
        logger.info(f"Interactive HTML saved to {filepath}")
        
        return filepath
    
    def create_static_report(
        self,
        clusters: Dict[str, List[str]],
        risk_profiles: Dict[str, Dict],
        evaluation_metrics: Dict[str, float],
        filename: str = "forensic_report.json",
    ) -> str:
        """
        Create static forensic report.
        
        Args:
            clusters: Entity clusters
            risk_profiles: Risk scores per cluster
            evaluation_metrics: Evaluation metrics
            filename: Output filename
            
        Returns:
            Path to generated report
        """
        logger.info(f"Creating forensic report: {filename}")
        
        report = {
            "report_metadata": {
                "generated_by": "blockchain_forensics_tool_v2.0",
                "methodology": "Enhanced Five-Phase Methodology",
                "author": "Saransh Jhariya | 102FSBSMS2122012",
                "mentor": "Dr. Ajit Majumdar, Associate Professor — LNJN NICFS NFSU, Delhi Campus",
            },
            "summary": {
                "total_entities": len(clusters),
                "total_addresses": sum(len(addrs) for addrs in clusters.values()),
                "high_risk_entities": sum(1 for p in risk_profiles.values() if p.get("overall_risk_level") == "high"),
                "critical_risk_entities": sum(1 for p in risk_profiles.values() if p.get("overall_risk_level") == "critical"),
            },
            "evaluation_metrics": evaluation_metrics,
            "entity_clusters": clusters,
            "risk_profiles": risk_profiles,
        }
        
        filepath = os.path.join(self.output_dir, filename)
        save_json(report, filepath)
        
        logger.info(f"Forensic report saved to {filepath}")
        
        return filepath


class Phase5ForensicOutput:
    """
    Phase 5: Formal Evaluation & Forensic Output
    Complete pipeline for evaluation and report generation.
    """
    
    def __init__(self, output_dir: str = "data/output"):
        """
        Initialize Phase 5 pipeline.
        
        Args:
            output_dir: Directory for output files
        """
        self.evaluator = ClusteringEvaluator()
        self.visualizer = ForensicVisualizer(output_dir=output_dir)
        self.output_dir = output_dir
    
    def generate_output(
        self,
        clusters: Dict[str, List[str]],
        confidence_results: Dict[str, Dict],
        enrichment_data: Dict[str, Dict],
        normal_txs: List[Dict],
        erc20_txs: List[Dict],
        cross_chain_edges: List[Tuple],
        ground_truth: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """
        Generate all Phase 5 outputs.
        
        Args:
            clusters: Entity clusters from Phase 3/4
            confidence_results: Confidence scoring from Phase 3
            enrichment_data: OSINT enrichment from Phase 1
            normal_txs: Normal transactions
            erc20_txs: ERC-20 token transfers
            cross_chain_edges: Cross-chain edges from Phase 4
            ground_truth: Optional ground truth labels for evaluation
            
        Returns:
            Dictionary containing all outputs
        """
        logger.info("=" * 60)
        logger.info("Phase 5: Formal Evaluation & Forensic Output")
        logger.info("=" * 60)
        
        # Step 1: Risk Scoring
        risk_scorer = RiskScorer(enrichment_data, confidence_results)
        risk_profiles = risk_scorer.compute_risk_scores(clusters)
        
        # Step 2: Evaluation (if ground truth provided)
        evaluation_metrics = {}
        if ground_truth:
            pairwise_metrics = self.evaluator.compute_pairwise_metrics(clusters, ground_truth)
            purity = self.evaluator.compute_purity(clusters, ground_truth)
            evaluation_metrics = {**pairwise_metrics, "purity": purity}
        else:
            # Basic statistics without ground truth
            evaluation_metrics = {
                "total_clusters": len(clusters),
                "avg_cluster_size": sum(len(a) for a in clusters.values()) / len(clusters) if clusters else 0,
                "note": "No ground truth provided for formal evaluation",
            }
        
        # Step 3: Build forensic graph
        G = self.visualizer.build_forensic_graph(
            normal_txs=normal_txs,
            erc20_txs=erc20_txs,
            clusters=clusters,
            confidence_results=confidence_results,
            cross_chain_edges=cross_chain_edges,
        )
        
        # Step 4: Create interactive HTML
        html_path = self.visualizer.create_interactive_html(
            G=G,
            filename="forensic_graph.html",
            title="Blockchain Forensic Analysis",
        )
        
        # Step 5: Create static report
        report_path = self.visualizer.create_static_report(
            clusters=clusters,
            risk_profiles=risk_profiles,
            evaluation_metrics=evaluation_metrics,
            filename="forensic_report.json",
        )
        
        # Compile results
        results = {
            "risk_profiles": risk_profiles,
            "evaluation_metrics": evaluation_metrics,
            "interactive_graph_path": html_path,
            "static_report_path": report_path,
            "graph_stats": {
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges(),
            },
        }
        
        logger.info("=" * 60)
        logger.info(f"Phase 5 Complete:")
        logger.info(f"  - Interactive Graph: {html_path}")
        logger.info(f"  - Forensic Report: {report_path}")
        logger.info("=" * 60)
        
        return results
