"""
Phase 1: Multi-Source Data Acquisition
OSINT Enrichment - Tags, VASP labels, Mixer flags, Sanctions lists.
"""

import os
from typing import Dict, List, Optional, Set

import requests

from config.settings import (
    CHAINABUSE_API_KEY,
    KNOWN_MIXERS,
    KNOWN_VASPS,
)
from src.data_acquisition.etherscan_client import EtherscanClient
from src.utils.helpers import create_evidence_record, normalize_address, save_json
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# OFAC SDN List URL
OFAC_SDN_URL = "https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/XML"

# Chainabuse API
CHAINABUSE_API_BASE = "https://www.chainabuse.com/api/v1"

# Etherscan label categories
ETHERSCAN_LABEL_CATEGORIES = [
    "exchange",
    "defi",
    "mixer",
    "scam",
    "phishing",
    "sanctioned",
]


class OSINTEnrichmentClient:
    """Client for fetching OSINT data from multiple sources."""
    
    def __init__(self, chain: str = "ethereum"):
        """
        Initialize OSINT client.
        
        Args:
            chain: Chain name
        """
        self.chain = chain
        self.etherscan_client = EtherscanClient(chain=chain)
        self._ofac_list: Optional[List[Dict]] = None
        self._chainabuse_cache: Dict = {}
    
    def get_etherscan_labels(self, addresses: List[str]) -> Dict[str, Dict]:
        """
        Fetch Etherscan labels for addresses.
        
        Args:
            addresses: List of addresses to lookup
            
        Returns:
            Dictionary of address -> label info
        """
        labels = {}
        
        for address in addresses:
            address = normalize_address(address)
            # Use Etherscan's address tag endpoint
            try:
                # Note: Etherscan doesn't have a public bulk label API
                # We'll check against known labels from their database
                label_info = self._check_known_labels(address)
                if label_info:
                    labels[address] = label_info
            except Exception as e:
                logger.debug(f"Error checking label for {address}: {e}")
        
        return labels
    
    def _check_known_labels(self, address: str) -> Optional[Dict]:
        """Check address against known label databases."""
        addr_lower = address.lower()
        
        # Check mixers
        if addr_lower in [m.lower() for m in KNOWN_MIXERS]:
            return {
                "label": "Mixer",
                "category": "mixer",
                "source": "known_mixers",
                "risk_level": "high",
            }
        
        # Check VASPs
        for vasp_name, vasp_addresses in KNOWN_VASPS.items():
            if addr_lower in [a.lower() for a in vasp_addresses]:
                return {
                    "label": f"{vasp_name.capitalize()} Exchange",
                    "category": "exchange",
                    "source": "known_vasps",
                    "risk_level": "medium",
                    "vasp_name": vasp_name,
                }
        
        return None
    
    def check_ofac_sdn(self, addresses: List[str]) -> Dict[str, bool]:
        """
        Check addresses against OFAC SDN list.
        
        Args:
            addresses: List of addresses to check
            
        Returns:
            Dictionary of address -> is_sanctioned
        """
        results = {}
        
        # Load OFAC list if not already loaded
        if self._ofac_list is None:
            self._load_ofac_list()
        
        if self._ofac_list is None:
            # Fallback: check against known sanctioned addresses
            sanctioned_addresses = self._get_known_sanctioned_addresses()
            for address in addresses:
                addr_lower = normalize_address(address).lower()
                results[address] = addr_lower in [s.lower() for s in sanctioned_addresses]
            return results
        
        # Check against OFAC list
        for address in addresses:
            addr_lower = normalize_address(address).lower()
            is_sanctioned = any(
                addr_lower == entry.get("address", "").lower()
                for entry in self._ofac_list
            )
            results[address] = is_sanctioned
        
        return results
    
    def _load_ofac_list(self):
        """Load OFAC SDN list."""
        try:
            # Note: In production, you'd parse the actual OFAC XML/CSV
            # For now, we use a cached list of crypto-related sanctioned addresses
            self._ofac_list = self._get_known_sanctioned_addresses()
        except Exception as e:
            logger.error(f"Failed to load OFAC list: {e}")
            self._ofac_list = []
    
    def _get_known_sanctioned_addresses(self) -> List[str]:
        """Get known sanctioned crypto addresses (sample)."""
        return [
            # Tornado Cash addresses (sanctioned Aug 2022)
            "0x12D66f87A04A989229Ee8cE45E76349E89908769",
            "0x47CE0C6eD5B0Ce3d3A51fdb1C52DC66a7c3c2936",
            "0x169AD27A470D064DEDE56a2D3FF72A98CeC41175",
            "0xd90e2f925DA726b50C4Ed8D0Fb90Ad053316F5e2",
            # Other sanctioned addresses
            "0x8589427373D6D84E98730D7795D8f6f8731FDA11",  # Tornado Cash deployer
            "0x7229E3E958375C8610D1b0F17C81c8bF2A43186E",  # Tornado Cash relayer
        ]
    
    def check_chainabuse(self, address: str) -> Optional[Dict]:
        """
        Check address against Chainabuse database.
        
        Args:
            address: Address to check
            
        Returns:
            Abuse report info if found, None otherwise
        """
        address = normalize_address(address)
        
        # Check cache
        if address in self._chainabuse_cache:
            return self._chainabuse_cache[address]
        
        if not CHAINABUSE_API_KEY:
            return None
        
        try:
            # Note: This is a simulated API call structure
            # Actual Chainabuse API requires authentication
            headers = {
                "X-API-KEY": CHAINABUSE_API_KEY,
                "Content-Type": "application/json",
            }
            
            # In production, make actual API call:
            # response = requests.get(
            #     f"{CHAINABUSE_API_BASE}/address/{address}",
            #     headers=headers,
            #     timeout=10
            # )
            # if response.status_code == 200:
            #     report = response.json()
            #     self._chainabuse_cache[address] = report
            #     return report
            
            return None
            
        except Exception as e:
            logger.debug(f"Chainabuse check failed for {address}: {e}")
            return None
    
    def get_vasp_deposit_addresses(self) -> Dict[str, List[str]]:
        """
        Get known VASP deposit addresses.
        
        Returns:
            Dictionary of VASP name -> list of addresses
        """
        return KNOWN_VASPS
    
    def get_mixer_addresses(self) -> List[str]:
        """
        Get known mixer addresses.
        
        Returns:
            List of mixer addresses
        """
        return KNOWN_MIXERS
    
    def enrich_addresses(self, addresses: List[str]) -> Dict[str, Dict]:
        """
        Perform full OSINT enrichment on addresses.
        
        Args:
            addresses: List of addresses to enrich
            
        Returns:
            Dictionary of address -> enrichment data
        """
        logger.info(f"Enriching {len(addresses)} addresses with OSINT data")
        
        enrichment = {}
        
        # Get Etherscan labels
        labels = self.get_etherscan_labels(addresses)
        
        # Check OFAC SDN
        ofac_results = self.check_ofac_sdn(addresses)
        
        for address in addresses:
            addr = normalize_address(address)
            enrichment[addr] = {
                "address": addr,
                "label": labels.get(addr, {}).get("label"),
                "label_category": labels.get(addr, {}).get("category"),
                "is_sanctioned": ofac_results.get(address, False),
                "is_mixer": addr.lower() in [m.lower() for m in KNOWN_MIXERS],
                "is_vasp": any(
                    addr.lower() in [a.lower() for a in addrs]
                    for addrs in KNOWN_VASPS.values()
                ),
                "vasp_name": None,
                "risk_level": "low",
            }
            
            # Add VASP name if applicable
            for vasp_name, vasp_addrs in KNOWN_VASPS.items():
                if addr.lower() in [a.lower() for a in vasp_addrs]:
                    enrichment[addr]["vasp_name"] = vasp_name
                    enrichment[addr]["risk_level"] = "medium"
                    break
            
            # Upgrade risk level for mixers and sanctioned
            if enrichment[addr]["is_mixer"]:
                enrichment[addr]["risk_level"] = "high"
            if enrichment[addr]["is_sanctioned"]:
                enrichment[addr]["risk_level"] = "critical"
            
            # Check Chainabuse
            abuse_report = self.check_chainabuse(addr)
            if abuse_report:
                enrichment[addr]["abuse_reports"] = abuse_report
                enrichment[addr]["risk_level"] = "high"
        
        return enrichment


class DataAcquisitionLayer3:
    """
    Layer 3: OSINT Enrichment
    Fetches tags, VASP labels, mixer flags, and sanctions data.
    """
    
    def __init__(self, chain: str = "ethereum", output_dir: Optional[str] = None):
        """
        Initialize Layer 3 data acquisition.
        
        Args:
            chain: Chain name
            output_dir: Directory for storing raw data
        """
        self.chain = chain
        self.client = OSINTEnrichmentClient(chain=chain)
        self.output_dir = output_dir
        self.evidence_records = []
    
    def enrich_addresses(self, addresses: List[str]) -> Dict:
        """
        Enrich addresses with OSINT data.
        
        Args:
            addresses: List of addresses to enrich
            
        Returns:
            Dictionary containing enrichment data
        """
        logger.info(f"Starting Layer 3 OSINT enrichment for {len(addresses)} addresses")
        
        enrichment_data = self.client.enrich_addresses(addresses)
        
        # Calculate summary statistics
        summary = {
            "total_addresses": len(addresses),
            "labeled_addresses": sum(1 for e in enrichment_data.values() if e.get("label")),
            "sanctioned_addresses": sum(1 for e in enrichment_data.values() if e.get("is_sanctioned")),
            "mixer_addresses": sum(1 for e in enrichment_data.values() if e.get("is_mixer")),
            "vasp_addresses": sum(1 for e in enrichment_data.values() if e.get("is_vasp")),
            "high_risk_addresses": sum(1 for e in enrichment_data.values() if e.get("risk_level") in ["high", "critical"]),
        }
        
        # Create evidence record
        evidence = create_evidence_record(
            data_type="osint_enrichment",
            source="multiple_osint_sources",
            seed_address=",".join(addresses[:5]),
            chain=self.chain,
            additional_metadata=summary,
        )
        self.evidence_records.append(evidence)
        
        result = {
            "chain": self.chain,
            "enrichment_data": enrichment_data,
            "summary": summary,
            "evidence_record": evidence,
        }
        
        # Save raw data
        if self.output_dir:
            filepath = f"{self.output_dir}/layer3_osint_{self.chain}.json"
            save_json(result, filepath)
            logger.info(f"OSINT enrichment saved to {filepath}")
        
        return result
    
    def get_reference_data(self) -> Dict:
        """
        Get reference data (VASP addresses, mixer addresses, sanctioned addresses).
        
        Returns:
            Dictionary containing reference data
        """
        return {
            "vasp_addresses": self.client.get_vasp_deposit_addresses(),
            "mixer_addresses": self.client.get_mixer_addresses(),
            "sanctioned_addresses": self.client._get_known_sanctioned_addresses(),
        }
