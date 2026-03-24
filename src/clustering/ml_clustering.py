"""
Phase 3: Dual Clustering Engine
Layer B: ML-Based Clustering using DBSCAN
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors

from src.utils.helpers import normalize_address
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DBSCANClustering:
    """
    Layer B: ML-Based Clustering using DBSCAN.
    
    DBSCAN (Density-Based Spatial Clustering of Applications with Noise)
    is robust to noise and doesn't require specifying cluster count in advance.
    """
    
    def __init__(self, eps: float = 0.5, min_samples: int = 3, metric: str = "euclidean"):
        """
        Initialize DBSCAN clustering.
        
        Args:
            eps: Maximum distance between two samples to be considered neighbors
            min_samples: Minimum number of samples in a neighborhood to form a dense region
            metric: Distance metric for DBSCAN
        """
        self.eps = eps
        self.min_samples = min_samples
        self.metric = metric
        self.model = DBSCAN(eps=eps, min_samples=min_samples, metric=metric)
        self.labels = None
        self.feature_matrix = None

    def optimize_eps(self, feature_matrix: pd.DataFrame, k: int = 4) -> float:
        """
        Optimize epsilon parameter using k-distance plot.

        Args:
            feature_matrix: Normalized feature matrix
            k: Number of nearest neighbors

        Returns:
            Optimal epsilon value
        """
        logger.info(f"Optimizing epsilon parameter using k-distance plot (k={k})")

        # Handle edge case: not enough samples
        n_samples = len(feature_matrix)
        if n_samples < k:
            logger.warning(f"Not enough samples ({n_samples}) for k-distance optimization (k={k}). Using default eps=0.5")
            return 0.5
        
        # Fit nearest neighbors
        nbrs = NearestNeighbors(n_neighbors=min(k, n_samples - 1), metric=self.metric)
        nbrs.fit(feature_matrix)

        # Get k-distances
        distances, _ = nbrs.kneighbors(feature_matrix)
        k_distances = distances[:, -1]  # Distance to k-th nearest neighbor

        # Sort distances
        k_distances_sorted = np.sort(k_distances)

        # Find elbow point using maximum curvature
        # Simple approach: find point with maximum second derivative
        if len(k_distances_sorted) > 10:
            x = np.arange(len(k_distances_sorted))
            y = k_distances_sorted

            # Calculate first and second derivatives
            first_deriv = np.gradient(y)
            second_deriv = np.gradient(first_deriv)

            # Find point of maximum curvature
            elbow_idx = np.argmax(second_deriv)
            optimal_eps = y[elbow_idx]
        else:
            # Fallback: use median distance
            optimal_eps = np.median(k_distances)

        logger.info(f"Optimal epsilon: {optimal_eps:.4f}")
        return optimal_eps

    def fit(self, feature_matrix: pd.DataFrame, auto_optimize_eps: bool = True) -> np.ndarray:
        """
        Fit DBSCAN model to feature matrix.

        Args:
            feature_matrix: Normalized feature matrix (n_addresses × n_features)
            auto_optimize_eps: Whether to automatically optimize epsilon

        Returns:
            Cluster labels for each address
        """
        logger.info("Starting Layer B: ML-Based Clustering (DBSCAN)")

        self.feature_matrix = feature_matrix
        
        # Handle edge case: not enough samples for DBSCAN
        n_samples = len(feature_matrix)
        if n_samples < 2:
            logger.warning(f"Not enough samples ({n_samples}) for DBSCAN. Marking all as noise.")
            self.labels = np.array([-1] * n_samples)  # All noise
            return self.labels
        
        # Optimize epsilon if requested
        if auto_optimize_eps:
            self.eps = self.optimize_eps(feature_matrix)
        
        # Fit DBSCAN
        self.labels = self.model.fit_predict(feature_matrix)
        
        # Calculate statistics
        unique_labels = set(self.labels)
        n_clusters = len([l for l in unique_labels if l != -1])
        n_noise = list(self.labels).count(-1)
        
        logger.info(f"DBSCAN complete: {n_clusters} clusters, {n_noise} noise points")
        
        # Calculate silhouette score if more than 1 cluster and not all noise
        if n_clusters > 1 and n_noise < len(self.labels):
            non_noise_mask = self.labels != -1
            if len(set(self.labels[non_noise_mask])) > 1:
                try:
                    silhouette = silhouette_score(
                        feature_matrix[non_noise_mask],
                        self.labels[non_noise_mask],
                        metric=self.metric
                    )
                    logger.info(f"Silhouette score: {silhouette:.4f}")
                except Exception as e:
                    logger.debug(f"Could not calculate silhouette score: {e}")
        
        return self.labels
    
    def get_clusters(self, addresses: List[str]) -> Dict[int, List[str]]:
        """
        Get clusters as dictionary.
        
        Args:
            addresses: List of addresses corresponding to feature matrix rows
            
        Returns:
            Dictionary of cluster_label -> list of addresses
        """
        if self.labels is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        clusters = {}
        for addr, label in zip(addresses, self.labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(normalize_address(addr))
        
        return clusters
    
    def get_noise_addresses(self, addresses: List[str]) -> List[str]:
        """
        Get addresses classified as noise/outliers.
        
        Args:
            addresses: List of addresses
            
        Returns:
            List of noise addresses
        """
        if self.labels is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        return [
            normalize_address(addr)
            for addr, label in zip(addresses, self.labels)
            if label == -1
        ]


class ConfidenceScorer:
    """
    Confidence Scoring: Reconciling Layer A and Layer B outputs.
    
    Three-tier confidence model:
    - High Confidence: Both layers assign to same cluster
    - Candidate: Only one layer fires
    - Unlinked: Neither layer finds connection
    """
    
    def __init__(self):
        """Initialize confidence scorer."""
        self.confidence_assignments = {}
    
    def compute_confidence(
        self,
        rule_based_clusters: Dict[str, List[str]],
        ml_clusters: Dict[int, List[str]],
        addresses: List[str],
    ) -> Dict[str, Dict]:
        """
        Compute confidence scores for all addresses.
        
        Args:
            rule_based_clusters: Clusters from rule-based layer (root -> addresses)
            ml_clusters: Clusters from ML layer (label -> addresses)
            addresses: All addresses to score
            
        Returns:
            Dictionary of address -> confidence info
        """
        logger.info("Computing confidence scores (reconciling Layer A and Layer B)")
        
        # Create reverse mappings: address -> cluster_id
        addr_to_rb_cluster = {}
        for cluster_id, addrs in rule_based_clusters.items():
            for addr in addrs:
                addr_to_rb_cluster[addr] = cluster_id
        
        addr_to_ml_cluster = {}
        for cluster_id, addrs in ml_clusters.items():
            for addr in addrs:
                addr_to_ml_cluster[addr] = cluster_id
        
        # Compute confidence for each address
        results = {}
        for address in addresses:
            addr = normalize_address(address)
            
            rb_cluster = addr_to_rb_cluster.get(addr)
            ml_cluster = addr_to_ml_cluster.get(addr)
            
            # Determine confidence tier
            if rb_cluster is not None and ml_cluster is not None:
                # Both layers fired
                if ml_cluster == -1:
                    # ML classified as noise, but RB found connection
                    confidence_tier = "candidate"
                    confidence_reason = "Rule-based clustering found connection; ML classified as noise"
                else:
                    # Both found connections
                    # Check if they agree on cluster membership
                    rb_members = set(rule_based_clusters.get(rb_cluster, []))
                    ml_members = set(ml_clusters.get(ml_cluster, []))
                    
                    if addr in rb_members and addr in ml_members:
                        # Check overlap
                        overlap = len(rb_members & ml_members)
                        union = len(rb_members | ml_members)
                        iou = overlap / union if union > 0 else 0
                        
                        if iou > 0.5:
                            confidence_tier = "high"
                            confidence_reason = f"Both layers agree (IoU={iou:.2f})"
                        else:
                            confidence_tier = "candidate"
                            confidence_reason = f"Both layers fired but low agreement (IoU={iou:.2f})"
                    else:
                        confidence_tier = "candidate"
                        confidence_reason = "Both layers fired with different cluster memberships"
            elif rb_cluster is not None:
                confidence_tier = "candidate"
                confidence_reason = "Only rule-based clustering found connection"
            elif ml_cluster is not None and ml_cluster != -1:
                confidence_tier = "candidate"
                confidence_reason = "Only ML clustering found connection"
            else:
                confidence_tier = "unlinked"
                confidence_reason = "Neither layer found connection"
            
            results[addr] = {
                "address": addr,
                "confidence_tier": confidence_tier,
                "confidence_reason": confidence_reason,
                "rule_based_cluster_id": rb_cluster,
                "ml_cluster_id": ml_cluster if ml_cluster != -1 else None,
                "is_ml_noise": ml_cluster == -1,
            }
        
        # Summary statistics
        tier_counts = {}
        for info in results.values():
            tier = info["confidence_tier"]
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        logger.info(f"Confidence scoring complete: {tier_counts}")
        
        return results
    
    def get_high_confidence_clusters(
        self,
        confidence_results: Dict[str, Dict],
        rule_based_clusters: Dict[str, List[str]],
    ) -> Dict[str, List[str]]:
        """
        Extract only high-confidence clusters.
        
        Args:
            confidence_results: Output from compute_confidence()
            rule_based_clusters: Original rule-based clusters
            
        Returns:
            Filtered clusters with high confidence only
        """
        high_confidence_addresses = set(
            addr for addr, info in confidence_results.items()
            if info["confidence_tier"] == "high"
        )
        
        filtered_clusters = {}
        for cluster_id, addresses in rule_based_clusters.items():
            high_conf_addrs = [a for a in addresses if a in high_confidence_addresses]
            if high_conf_addrs:
                filtered_clusters[cluster_id] = high_conf_addrs
        
        return filtered_clusters


class DualClusteringEngine:
    """
    Phase 3: Dual Clustering Engine
    Combines Layer A (Rule-Based) and Layer B (ML-Based) clustering.
    """
    
    def __init__(
        self,
        gas_funding_threshold: float = 0.01,
        temporal_window_seconds: int = 60,
        dbscan_eps: float = 0.5,
        dbscan_min_samples: int = 3,
    ):
        """
        Initialize dual clustering engine.
        
        Args:
            gas_funding_threshold: ETH threshold for gas funding heuristic
            temporal_window_seconds: Time window for temporal co-activity
            dbscan_eps: DBSCAN epsilon parameter
            dbscan_min_samples: DBSCAN minimum samples parameter
        """
        from src.clustering.rule_based_clustering import RuleBasedClustering
        
        self.rule_based = RuleBasedClustering(
            gas_funding_threshold=gas_funding_threshold,
            temporal_window_seconds=temporal_window_seconds,
        )
        self.ml_clustering = DBSCANClustering(eps=dbscan_eps, min_samples=dbscan_min_samples)
        self.confidence_scorer = ConfidenceScorer()
        
        self.final_clusters = None
        self.confidence_results = None
    
    def cluster(
        self,
        addresses: List[str],
        normal_txs: List[Dict],
        internal_txs: List[Dict],
        erc20_txs: List[Dict],
        feature_matrix: pd.DataFrame,
        vasp_addresses: Optional[set] = None,
    ) -> Tuple[Dict[str, List[str]], Dict[str, Dict]]:
        """
        Run dual clustering pipeline.
        
        Args:
            addresses: All addresses to cluster
            normal_txs: Normal transactions
            internal_txs: Internal transactions
            erc20_txs: ERC-20 token transfers
            feature_matrix: Normalized feature matrix from Phase 2
            vasp_addresses: Set of known VASP addresses
            
        Returns:
            Tuple of (final clusters, confidence results)
        """
        logger.info("=" * 60)
        logger.info("Phase 3: Dual Clustering Engine")
        logger.info("=" * 60)
        
        # Layer A: Rule-Based Clustering
        rb_clusters = self.rule_based.cluster(
            addresses=addresses,
            normal_txs=normal_txs,
            internal_txs=internal_txs,
            erc20_txs=erc20_txs,
            vasp_addresses=vasp_addresses,
        )
        
        # Layer B: ML-Based Clustering
        ml_labels = self.ml_clustering.fit(feature_matrix, auto_optimize_eps=True)
        ml_clusters = self.ml_clustering.get_clusters(addresses)
        
        # Confidence Scoring: Reconcile both layers
        self.confidence_results = self.confidence_scorer.compute_confidence(
            rule_based_clusters=rb_clusters,
            ml_clusters=ml_clusters,
            addresses=addresses,
        )
        
        # Use rule-based clusters with confidence annotations
        self.final_clusters = rb_clusters
        
        logger.info("=" * 60)
        logger.info(f"Phase 3 Complete: {len(self.final_clusters)} entity clusters identified")
        logger.info("=" * 60)
        
        return self.final_clusters, self.confidence_results
    
    def get_evidence(self) -> Dict:
        """Get all clustering evidence."""
        return {
            "rule_based_evidence": self.rule_based.get_evidence(),
            "ml_cluster_count": len(set(self.ml_clustering.labels)) if self.ml_clustering.labels is not None else 0,
            "confidence_results": self.confidence_results,
        }
