"""
Blockchain Forensics Tool - Main Orchestration Module
Implements the complete five-phase methodology pipeline.
"""

import json
import os
from typing import Dict, List, Optional

import pandas as pd

from config.settings import (
    DATA_DIR,
    KNOWN_MIXERS,
    KNOWN_VASPS,
    OUTPUT_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
)
from src.data_acquisition.etherscan_client import DataAcquisitionLayer1
from src.data_acquisition.osint_enrichment import DataAcquisitionLayer3
from src.feature_engineering.feature_extraction import FeatureEngineeringPipeline
from src.clustering.ml_clustering import DualClusteringEngine
from src.cross_chain.entity_resolution import CrossChainEntityResolution
from src.evaluation.forensic_output import Phase5ForensicOutput
from src.utils.helpers import load_json, normalize_address, save_json
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BlockchainForensicsPipeline:
    """
    Complete Five-Phase Blockchain Forensics Pipeline.
    
    Orchestrates all phases:
    1. Multi-Source Data Acquisition
    2. Behavioral Feature Engineering
    3. Dual Clustering Engine (Union-Find + DBSCAN)
    4. Cross-Chain Entity Resolution
    5. Formal Evaluation & Forensic Output
    """
    
    def __init__(
        self,
        seed_address: str,
        chain: str = "ethereum",
        output_dir: Optional[str] = None,
        eth_price_usd: float = 2000.0,
    ):
        """
        Initialize the forensics pipeline.
        
        Args:
            seed_address: Seed Ethereum address for investigation
            chain: Chain name (ethereum, arbitrum, polygon, bsc, optimism)
            output_dir: Directory for output files
            eth_price_usd: ETH price in USD for value calculations
        """
        self.seed_address = normalize_address(seed_address)
        self.chain = chain
        self.output_dir = output_dir or OUTPUT_DIR
        self.eth_price_usd = eth_price_usd
        
        # Create output directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(RAW_DATA_DIR, exist_ok=True)
        os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
        
        # Pipeline state
        self.chain_data = {}
        self.all_addresses = set()
        self.enrichment_data = {}
        self.feature_matrix = None
        self.clusters = {}
        self.confidence_results = {}
        self.cross_chain_results = {}
        self.final_output = {}
        
        logger.info(f"Pipeline initialized for seed address: {self.seed_address}")
    
    def run_phase1_data_acquisition(self) -> Dict:
        """
        Run Phase 1: Multi-Source Data Acquisition.
        
        Returns:
            Phase 1 results
        """
        logger.info("=" * 60)
        logger.info("Phase 1: Multi-Source Data Acquisition")
        logger.info("=" * 60)
        
        # Layer 1: On-Chain Transaction Pull
        layer1 = DataAcquisitionLayer1(chain=self.chain, output_dir=RAW_DATA_DIR)
        layer1_result = layer1.fetch_all_transactions(self.seed_address)
        
        # Store data
        self.chain_data[self.chain] = {
            "normal_transactions": layer1_result["normal_transactions"],
            "internal_transactions": layer1_result["internal_transactions"],
            "erc20_transfers": layer1_result["erc20_transfers"],
            "all_addresses": layer1_result["all_addresses"],
        }
        
        # Collect all addresses
        self.all_addresses.update(layer1_result["all_addresses"])
        
        # Layer 3: OSINT Enrichment (before Phase 2)
        layer3 = DataAcquisitionLayer3(chain=self.chain, output_dir=RAW_DATA_DIR)
        layer3_result = layer3.enrich_addresses(list(self.all_addresses))
        
        self.enrichment_data = layer3_result.get("enrichment_data", {})
        
        # Get VASP addresses for clustering
        vasp_addresses = set()
        for addr, data in self.enrichment_data.items():
            if data.get("is_vasp"):
                vasp_addresses.add(addr)
        
        phase1_result = {
            "layer1": layer1_result,
            "layer3": layer3_result,
            "total_addresses": len(self.all_addresses),
            "vasp_addresses": list(vasp_addresses),
        }
        
        logger.info(f"Phase 1 complete: {len(self.all_addresses)} addresses collected")
        
        return phase1_result
    
    def run_phase2_feature_engineering(self, vasp_addresses: set) -> Dict:
        """
        Run Phase 2: Behavioral Feature Engineering.
        
        Args:
            vasp_addresses: Set of VASP addresses
            
        Returns:
            Phase 2 results
        """
        logger.info("=" * 60)
        logger.info("Phase 2: Behavioral Feature Engineering")
        logger.info("=" * 60)
        
        chain_data = self.chain_data[self.chain]
        
        # Initialize pipeline
        pipeline = FeatureEngineeringPipeline(eth_price_usd=self.eth_price_usd)
        
        # Extract all features
        self.feature_matrix, feature_metadata = pipeline.extract_all_features(
            addresses=list(self.all_addresses),
            normal_txs=chain_data["normal_transactions"],
            internal_txs=chain_data["internal_transactions"],
            erc20_txs=chain_data["erc20_transfers"],
            enrichment_data=self.enrichment_data,
            known_mixers=KNOWN_MIXERS,
        )
        
        # Save feature matrix
        feature_path = os.path.join(PROCESSED_DATA_DIR, "feature_matrix.csv")
        self.feature_matrix.to_csv(feature_path)
        
        phase2_result = {
            "feature_matrix_path": feature_path,
            "feature_metadata": feature_metadata,
        }
        
        logger.info(f"Phase 2 complete: {self.feature_matrix.shape[0]} addresses × {self.feature_matrix.shape[1]} features")
        
        return phase2_result
    
    def run_phase3_clustering(self, vasp_addresses: set) -> Dict:
        """
        Run Phase 3: Dual Clustering Engine.
        
        Args:
            vasp_addresses: Set of VASP addresses
            
        Returns:
            Phase 3 results
        """
        logger.info("=" * 60)
        logger.info("Phase 3: Dual Clustering Engine")
        logger.info("=" * 60)
        
        chain_data = self.chain_data[self.chain]
        
        # Initialize dual clustering engine
        engine = DualClusteringEngine()
        
        # Run clustering
        self.clusters, self.confidence_results = engine.cluster(
            addresses=list(self.all_addresses),
            normal_txs=chain_data["normal_transactions"],
            internal_txs=chain_data["internal_transactions"],
            erc20_txs=chain_data["erc20_transfers"],
            feature_matrix=self.feature_matrix,
            vasp_addresses=vasp_addresses,
        )
        
        # Save clustering results
        clustering_path = os.path.join(PROCESSED_DATA_DIR, "clustering_results.json")
        save_json({
            "clusters": {k: list(v) for k, v in self.clusters.items()},
            "confidence_results": self.confidence_results,
        }, clustering_path)
        
        phase3_result = {
            "clustering_path": clustering_path,
            "total_clusters": len(self.clusters),
            "evidence": engine.get_evidence(),
        }
        
        logger.info(f"Phase 3 complete: {len(self.clusters)} entity clusters identified")
        
        return phase3_result
    
    def run_phase4_cross_chain(self) -> Dict:
        """
        Run Phase 4: Cross-Chain Entity Resolution.
        
        Returns:
            Phase 4 results
        """
        logger.info("=" * 60)
        logger.info("Phase 4: Cross-Chain Entity Resolution")
        logger.info("=" * 60)
        
        # For now, use single-chain data
        # In full implementation, fetch data from multiple chains
        chain_clusters = {
            self.chain: self.clusters,
        }
        
        # Initialize cross-chain resolution
        resolver = CrossChainEntityResolution()
        
        # Run resolution (will be minimal for single-chain)
        self.cross_chain_results = resolver.resolve(
            chain_data=self.chain_data,
            chain_clusters=chain_clusters,
        )
        
        # Update clusters with unified entities if available
        if "unified_entities" in self.cross_chain_results:
            # Convert unified entities to standard cluster format
            unified = self.cross_chain_results["unified_entities"]
            self.clusters = {
                entity_id: entity_data["addresses"].get(self.chain, [])
                for entity_id, entity_data in unified.items()
            }
        
        # Save cross-chain results
        crosschain_path = os.path.join(PROCESSED_DATA_DIR, "cross_chain_results.json")
        save_json(self.cross_chain_results, crosschain_path)
        
        phase4_result = {
            "crosschain_path": crosschain_path,
            "summary": self.cross_chain_results.get("summary", {}),
        }
        
        logger.info(f"Phase 4 complete: {phase4_result['summary'].get('total_entities', 0)} unified entities")
        
        return phase4_result
    
    def run_phase5_evaluation(self, ground_truth: Optional[Dict[str, str]] = None) -> Dict:
        """
        Run Phase 5: Formal Evaluation & Forensic Output.
        
        Args:
            ground_truth: Optional ground truth labels for evaluation
            
        Returns:
            Phase 5 results
        """
        logger.info("=" * 60)
        logger.info("Phase 5: Formal Evaluation & Forensic Output")
        logger.info("=" * 60)
        
        chain_data = self.chain_data[self.chain]
        
        # Get cross-chain edges
        cross_chain_edges = self.cross_chain_results.get("cross_chain_edges", [])
        
        # Initialize Phase 5
        phase5 = Phase5ForensicOutput(output_dir=self.output_dir)
        
        # Generate all outputs
        self.final_output = phase5.generate_output(
            clusters=self.clusters,
            confidence_results=self.confidence_results,
            enrichment_data=self.enrichment_data,
            normal_txs=chain_data["normal_transactions"],
            erc20_txs=chain_data["erc20_transfers"],
            cross_chain_edges=cross_chain_edges,
            ground_truth=ground_truth,
        )
        
        return self.final_output
    
    def run_full_pipeline(self, ground_truth: Optional[Dict[str, str]] = None) -> Dict:
        """
        Run the complete five-phase pipeline.
        
        Args:
            ground_truth: Optional ground truth for evaluation
            
        Returns:
            Complete pipeline results
        """
        logger.info("=" * 60)
        logger.info("BLOCKCHAIN FORENSICS TOOL v2.0")
        logger.info(f"Seed Address: {self.seed_address}")
        logger.info(f"Chain: {self.chain}")
        logger.info("=" * 60)
        
        # Phase 1
        phase1_result = self.run_phase1_data_acquisition()
        
        # Phase 2
        phase2_result = self.run_phase2_feature_engineering(
            vasp_addresses=phase1_result.get("vasp_addresses", set())
        )
        
        # Phase 3
        phase3_result = self.run_phase3_clustering(
            vasp_addresses=phase1_result.get("vasp_addresses", set())
        )
        
        # Phase 4
        phase4_result = self.run_phase4_cross_chain()
        
        # Phase 5
        phase5_result = self.run_phase5_evaluation(ground_truth=ground_truth)
        
        # Compile final report
        final_report = {
            "pipeline_metadata": {
                "seed_address": self.seed_address,
                "chain": self.chain,
                "timestamp": pd.Timestamp.now().isoformat(),
            },
            "phase1_summary": {
                "total_addresses": phase1_result.get("total_addresses"),
            },
            "phase2_summary": phase2_result.get("feature_metadata", {}),
            "phase3_summary": {
                "total_clusters": phase3_result.get("total_clusters"),
            },
            "phase4_summary": phase4_result.get("summary", {}),
            "phase5_summary": {
                "evaluation_metrics": phase5_result.get("evaluation_metrics", {}),
                "risk_distribution": self._get_risk_distribution(),
                "output_files": {
                    "interactive_graph": phase5_result.get("interactive_graph_path"),
                    "forensic_report": phase5_result.get("static_report_path"),
                },
            },
        }
        
        # Save final report
        report_path = os.path.join(self.output_dir, "final_report.json")
        save_json(final_report, report_path)
        
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETE")
        logger.info(f"Final Report: {report_path}")
        logger.info(f"Interactive Graph: {phase5_result.get('interactive_graph_path')}")
        logger.info("=" * 60)
        
        return final_report
    
    def _get_risk_distribution(self) -> Dict:
        """Get risk distribution from final output."""
        risk_profiles = self.final_output.get("risk_profiles", {})
        distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for profile in risk_profiles.values():
            risk_level = profile.get("overall_risk_level", "low")
            distribution[risk_level] = distribution.get(risk_level, 0) + 1
        
        return distribution


def run_forensics(
    seed_address: str,
    chain: str = "ethereum",
    output_dir: Optional[str] = None,
    ground_truth_path: Optional[str] = None,
) -> Dict:
    """
    Convenience function to run the complete forensics pipeline.
    
    Args:
        seed_address: Seed address for investigation
        chain: Chain name
        output_dir: Output directory
        ground_truth_path: Optional path to ground truth JSON
        
    Returns:
        Pipeline results
    """
    # Load ground truth if provided
    ground_truth = None
    if ground_truth_path and os.path.exists(ground_truth_path):
        ground_truth = load_json(ground_truth_path)
    
    # Initialize and run pipeline
    pipeline = BlockchainForensicsPipeline(
        seed_address=seed_address,
        chain=chain,
        output_dir=output_dir,
    )
    
    return pipeline.run_full_pipeline(ground_truth=ground_truth)
