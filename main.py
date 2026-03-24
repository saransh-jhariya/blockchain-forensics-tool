#!/usr/bin/env python3
"""
Blockchain Forensics Tool - CLI Entry Point
Wallet Clustering & Cross-Chain Tracing Tool

M.Sc. Forensic Science (Cyber Forensics) - 9th Semester
Author: Saransh Jhariya | 102FSBSMS2122012
Mentor: Dr. Ajit Majumdar, Associate Professor — LNJN NICFS NFSU, Delhi Campus
"""

import argparse
import sys
from pathlib import Path

from src.pipeline import BlockchainForensicsPipeline, run_forensics
from src.utils.helpers import normalize_address
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Blockchain Forensics Tool - Wallet Clustering & Cross-Chain Tracing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with seed address
  python main.py --seed 0x1234567890abcdef1234567890abcdef12345678
  
  # Specify chain and output directory
  python main.py --seed 0x... --chain ethereum --output ./results
  
  # Run with ground truth for evaluation
  python main.py --seed 0x... --ground-truth labels.json
  
  # Multi-chain analysis
  python main.py --seed 0x... --chain ethereum --multi-chain

This tool implements a five-phase methodology:
  Phase 1: Multi-Source Data Acquisition
  Phase 2: Behavioral Feature Engineering  
  Phase 3: Dual Clustering Engine (Union-Find + DBSCAN)
  Phase 4: Cross-Chain Entity Resolution
  Phase 5: Formal Evaluation & Forensic Output
        """,
    )
    
    parser.add_argument(
        "--seed", "-s",
        type=str,
        required=True,
        help="Seed Ethereum address or transaction hash for investigation",
    )
    
    parser.add_argument(
        "--chain", "-c",
        type=str,
        default="ethereum",
        choices=["ethereum", "arbitrum", "polygon", "bsc", "optimism"],
        help="Blockchain to analyze (default: ethereum)",
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output directory for results (default: data/output)",
    )
    
    parser.add_argument(
        "--ground-truth", "-g",
        type=str,
        default=None,
        help="Path to ground truth JSON for evaluation",
    )
    
    parser.add_argument(
        "--eth-price",
        type=float,
        default=2000.0,
        help="ETH price in USD for value calculations (default: 2000)",
    )
    
    parser.add_argument(
        "--multi-chain",
        action="store_true",
        help="Enable multi-chain analysis (experimental)",
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Blockchain Forensics Tool v2.0",
    )
    
    args = parser.parse_args()
    
    # Validate seed address
    seed = normalize_address(args.seed)
    if not seed or len(seed) != 42:
        logger.error(f"Invalid Ethereum address: {args.seed}")
        sys.exit(1)
    
    # Set up logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logger(__name__, level=getattr(__import__("logging"), log_level))
    
    logger.info("=" * 60)
    logger.info("BLOCKCHAIN FORENSICS TOOL v2.0")
    logger.info("M.Sc. Forensic Science (Cyber Forensics) - 9th Semester")
    logger.info("Author: Saransh Jhariya | 102FSBSMS2122012")
    logger.info("Mentor: Dr. Ajit Majumdar, LNJN NICFS NFSU, Delhi Campus")
    logger.info("=" * 60)
    
    try:
        # Run the forensics pipeline
        results = run_forensics(
            seed_address=seed,
            chain=args.chain,
            output_dir=args.output,
            ground_truth_path=args.ground_truth,
        )
        
        # Print summary
        logger.info("")
        logger.info("INVESTIGATION SUMMARY")
        logger.info("-" * 40)
        logger.info(f"Seed Address: {seed}")
        logger.info(f"Chain: {args.chain}")
        logger.info(f"Total Addresses Analyzed: {results['phase1_summary']['total_addresses']}")
        logger.info(f"Entity Clusters Identified: {results['phase3_summary']['total_clusters']}")
        
        # Risk summary
        risk_dist = results["phase5_summary"]["risk_distribution"]
        logger.info("")
        logger.info("Risk Distribution:")
        for level, count in risk_dist.items():
            if count > 0:
                logger.info(f"  {level.upper()}: {count} entities")
        
        # Output files
        logger.info("")
        logger.info("Output Files:")
        for name, path in results["phase5_summary"]["output_files"].items():
            logger.info(f"  {name}: {path}")
        
        logger.info("")
        logger.info("Investigation complete.")
        
    except KeyboardInterrupt:
        logger.error("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
