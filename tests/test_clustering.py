"""
Tests for Blockchain Forensics Tool
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.clustering.rule_based_clustering import UnionFind, RuleBasedClustering
from src.clustering.ml_clustering import DBSCANClustering, ConfidenceScorer
from src.utils.helpers import normalize_address, format_eth, min_max_scale


class TestUnionFind(unittest.TestCase):
    """Test Union-Find data structure."""
    
    def setUp(self):
        self.uf = UnionFind()
    
    def test_find_initializes_new_element(self):
        """Test that find initializes a new element."""
        result = self.uf.find("0x123")
        self.assertEqual(result, "0x123")
    
    def test_union_connects_components(self):
        """Test that union connects two components."""
        self.uf.find("0x123")
        self.uf.find("0x456")
        self.uf.union("0x123", "0x456")
        self.assertTrue(self.uf.are_connected("0x123", "0x456"))
    
    def test_get_clusters(self):
        """Test cluster extraction."""
        self.uf.union("0x1", "0x2")
        self.uf.union("0x2", "0x3")
        self.uf.union("0x4", "0x5")
        
        clusters = self.uf.get_clusters()
        self.assertEqual(len(clusters), 2)
    
    def test_cluster_size(self):
        """Test cluster size tracking."""
        self.uf.union("0x1", "0x2")
        self.uf.union("0x2", "0x3")
        
        size = self.uf.get_cluster_size("0x1")
        self.assertEqual(size, 3)


class TestRuleBasedClustering(unittest.TestCase):
    """Test rule-based clustering heuristics."""
    
    def setUp(self):
        self.rbc = RuleBasedClustering(gas_funding_threshold=0.01)
    
    def test_gas_funding_heuristic(self):
        """Test gas funding source heuristic."""
        # Create mock transactions
        normal_txs = [
            {
                "from": "0xfunder",
                "to": "0xnew_wallet",
                "value": str(int(0.005 * 1e18)),  # 0.005 ETH
                "timeStamp": "1000",
                "blockNumber": "100",
            }
        ]
        
        unions = self.rbc.apply_gas_funding_heuristic(normal_txs, [])
        self.assertGreater(unions, 0)
        self.assertTrue(self.rbc.uf.are_connected("0xfunder", "0xnew_wallet"))


class TestHelpers(unittest.TestCase):
    """Test utility functions."""
    
    def test_normalize_address_lowercase(self):
        """Test address normalization to lowercase."""
        addr = "0xABC123DEF456"
        result = normalize_address(addr)
        self.assertEqual(result, "0xabc123def456")
    
    def test_normalize_address_adds_prefix(self):
        """Test address normalization adds 0x prefix."""
        addr = "abc123def456789012345678901234567890"
        result = normalize_address(addr)
        self.assertTrue(result.startswith("0x"))
    
    def test_format_eth(self):
        """Test Wei to ETH conversion."""
        wei = int(1.5 * 1e18)
        result = format_eth(wei)
        self.assertEqual(result, 1.5)
    
    def test_min_max_scale(self):
        """Test min-max scaling."""
        result = min_max_scale(5, 0, 10)
        self.assertEqual(result, 0.5)


class TestDBSCANClustering(unittest.TestCase):
    """Test DBSCAN clustering."""
    
    def setUp(self):
        import pandas as pd
        import numpy as np
        
        # Create simple feature matrix
        np.random.seed(42)
        self.feature_matrix = pd.DataFrame(
            np.random.rand(20, 5),
            columns=[f"feature_{i}" for i in range(5)]
        )
        self.addresses = [f"0x{i:040x}" for i in range(20)]
    
    def test_fit_and_cluster(self):
        """Test DBSCAN fit and cluster extraction."""
        dbscan = DBSCANClustering(eps=0.8, min_samples=2)
        labels = dbscan.fit(self.feature_matrix, auto_optimize_eps=False)
        
        self.assertEqual(len(labels), len(self.addresses))
        
        clusters = dbscan.get_clusters(self.addresses)
        self.assertIsInstance(clusters, dict)


class TestConfidenceScorer(unittest.TestCase):
    """Test confidence scoring."""
    
    def setUp(self):
        self.scorer = ConfidenceScorer()
    
    def test_high_confidence_when_both_agree(self):
        """Test high confidence when both layers agree."""
        rb_clusters = {
            "0xroot1": ["0x1", "0x2", "0x3"],
        }
        ml_clusters = {
            0: ["0x1", "0x2", "0x3"],
        }
        addresses = ["0x1", "0x2", "0x3"]
        
        results = self.scorer.compute_confidence(rb_clusters, ml_clusters, addresses)
        
        # All should be at least candidate confidence
        for addr in addresses:
            self.assertIn(results[addr]["confidence_tier"], ["high", "candidate"])
    
    def test_unlinked_when_neither_fires(self):
        """Test unlinked when neither layer finds connection."""
        rb_clusters = {}
        ml_clusters = {-1: ["0x1", "0x2"]}  # All noise
        addresses = ["0x1", "0x2"]
        
        results = self.scorer.compute_confidence(rb_clusters, ml_clusters, addresses)
        
        for addr in addresses:
            self.assertEqual(results[addr]["confidence_tier"], "unlinked")


if __name__ == "__main__":
    unittest.main()
