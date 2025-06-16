#!/usr/bin/env python3
"""
NEAR Service for NearGravity
Service wrapper for NEAR contracts interactions following the crypto_service.py pattern
"""
import json
import hashlib
import base64
import os
from typing import Dict, Any, Optional, List
import requests
import time

import sys
from pathlib import Path

# Add src to path for imports
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)


def make_storage_key(prefix: str, identifier: str) -> str:
    """
    Create a storage key for NEAR contracts.
    
    Args:
        prefix: Prefix for the key (e.g., 'semantic', 'analysis')
        identifier: Unique identifier
        
    Returns:
        str: Storage key (hex encoded)
    """
    key_str = f"{prefix}:{identifier}"
    return hashlib.sha256(key_str.encode()).hexdigest()


def encode_json_to_base64(data: Dict[str, Any]) -> str:
    """
    Encode JSON data to base64 format for NEAR storage.
    
    Args:
        data: JSON data to encode
        
    Returns:
        str: Base64 encoded data
    """
    json_str = json.dumps(data, sort_keys=True)
    return base64.b64encode(json_str.encode()).decode()


def decode_base64_to_json(encoded_data: str) -> Dict[str, Any]:
    """
    Decode base64 data to JSON format.
    
    Args:
        encoded_data: Base64 encoded data
        
    Returns:
        dict: Decoded JSON data
    """
    json_str = base64.b64decode(encoded_data.encode()).decode()
    return json.loads(json_str)


class NEARService:
    """
    Service for NEAR contracts interactions with semantic guard contract.
    Follows the NearGravityCryptoService pattern for consistency.
    """
    
    def __init__(
        self, 
        network: str = "testnet",
        account_id: Optional[str] = None,
        private_key: Optional[str] = None,
        contract_id: str = "semantic-guard.testnet"
    ):
        """
        Initialize the NEAR service.
        
        Args:
            network: NEAR network ("testnet" or "mainnet")
            account_id: NEAR account ID
            private_key: Private key for signing transactions
            contract_id: Deployed contract account ID
        """
        self.network = network
        self.account_id = account_id
        self.private_key = private_key
        self.contract_id = contract_id
        
        # NEAR RPC URLs
        self.rpc_urls = {
            "testnet": "https://rpc.testnet.near.org",
            "mainnet": "https://rpc.mainnet.near.org"
        }
        
        self.rpc_url = self.rpc_urls[network]
        
        # Transaction tracking
        self.last_tx_hash = None
        
    def submit_semantic_analysis(
        self, 
        prefix: str, 
        identifier: str, 
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Submit semantic analysis data to NEAR contracts.
        
        Args:
            prefix: Prefix for the storage key
            identifier: Unique identifier (e.g., query hash)
            analysis_data: Semantic analysis results
            
        Returns:
            dict: Transaction result
        """
        if not self.account_id or not self.private_key:
            raise ValueError("Account ID and private key required for transactions")
        
        # Create storage key
        storage_key = make_storage_key(prefix, identifier)
        
        # Encode analysis data
        encoded_data = encode_json_to_base64(analysis_data)
        
        # Prepare function call arguments
        function_call_args = {
            "analysis_id": storage_key,
            "analysis_data": encoded_data,
            "timestamp": int(time.time()),
            "metadata": {
                "prefix": prefix,
                "identifier": identifier,
                "version": "1.0"
            }
        }
        
        try:
            # Submit transaction via NEAR RPC
            tx_result = self._call_contract_method(
                method_name="store_semantic_analysis",
                args=function_call_args,
                deposit="0"  # No NEAR tokens attached
            )
            
            return {
                "tx_hash": tx_result.get("transaction", {}).get("hash"),
                "success": tx_result.get("status", {}).get("SuccessValue") is not None,
                "storage_key": storage_key,
                "gas_used": tx_result.get("transaction_outcome", {}).get("outcome", {}).get("gas_burnt", 0)
            }
            
        except Exception as e:
            print(f"Error submitting semantic analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "storage_key": storage_key
            }
    
    def get_semantic_analysis(
        self, 
        prefix: str, 
        identifier: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve semantic analysis data from NEAR contracts.
        
        Args:
            prefix: Prefix for the storage key
            identifier: Unique identifier
            
        Returns:
            dict: Retrieved analysis data or None if not found
        """
        # Create storage key
        storage_key = make_storage_key(prefix, identifier)
        
        try:
            # Call view method on contract
            result = self._view_contract_method(
                method_name="get_semantic_analysis",
                args={"analysis_id": storage_key}
            )
            
            if result and "analysis_data" in result:
                # Decode the base64 data
                return decode_base64_to_json(result["analysis_data"])
            
            return None
            
        except Exception as e:
            print(f"Error retrieving semantic analysis: {e}")
            return None
    
    def search_by_semantic_hash(self, semantic_hash: str) -> List[str]:
        """
        Search for analysis IDs by semantic hash.
        
        Args:
            semantic_hash: Hash to search for
            
        Returns:
            list: List of analysis IDs with matching semantic hash
        """
        try:
            result = self._view_contract_method(
                method_name="search_by_semantic_hash",
                args={"semantic_hash": semantic_hash}
            )
            
            return result if result else []
            
        except Exception as e:
            print(f"Error searching by semantic hash: {e}")
            return []
    
    def _call_contract_method(
        self, 
        method_name: str, 
        args: Dict[str, Any], 
        deposit: str = "0"
    ) -> Dict[str, Any]:
        """
        Call a contract method (transaction).
        
        Args:
            method_name: Name of the contract method
            args: Method arguments
            deposit: NEAR tokens to attach (in yoctoNEAR)
            
        Returns:
            dict: Transaction result
        """
        # For now, simulate transaction success for development
        # TODO: Implement actual NEAR transaction submission
        return {
            "status": {"SuccessValue": ""},
            "transaction": {"hash": f"mock_tx_{int(time.time())}"},
            "transaction_outcome": {
                "outcome": {"gas_burnt": 2500000000000}
            }
        }
    
    def _view_contract_method(
        self, 
        method_name: str, 
        args: Dict[str, Any]
    ) -> Any:
        """
        Call a contract view method (read-only).
        
        Args:
            method_name: Name of the view method
            args: Method arguments
            
        Returns:
            Any: Method result
        """
        # Prepare RPC request
        rpc_request = {
            "jsonrpc": "2.0",
            "id": "dontcare",
            "method": "query",
            "params": {
                "request_type": "call_function",
                "finality": "final",
                "account_id": self.contract_id,
                "method_name": method_name,
                "args_base64": base64.b64encode(
                    json.dumps(args).encode()
                ).decode()
            }
        }
        
        try:
            response = requests.post(self.rpc_url, json=rpc_request, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                raise Exception(f"RPC Error: {result['error']}")
            
            # Decode result
            if "result" in result and "result" in result["result"]:
                result_bytes = bytes(result["result"]["result"])
                if result_bytes:
                    return json.loads(result_bytes.decode())
            
            return None
            
        except Exception as e:
            print(f"Error calling view method {method_name}: {e}")
            return None
    
    def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """
        Get account balance information.
        
        Returns:
            dict: Account balance details or None if error
        """
        if not self.account_id:
            return None
        
        rpc_request = {
            "jsonrpc": "2.0",
            "id": "dontcare",
            "method": "query",
            "params": {
                "request_type": "view_account",
                "finality": "final",
                "account_id": self.account_id
            }
        }
        
        try:
            response = requests.post(self.rpc_url, json=rpc_request, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if "error" in result:
                return None
            
            return result.get("result")
            
        except Exception as e:
            print(f"Error getting account balance: {e}")
            return None
    
    def health_check(self) -> bool:
        """
        Check if NEAR service is healthy and can connect to network.
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            # Simple status check
            rpc_request = {
                "jsonrpc": "2.0",
                "id": "dontcare",
                "method": "status",
                "params": []
            }
            
            response = requests.post(self.rpc_url, json=rpc_request, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            return "result" in result and "chain_id" in result["result"]
            
        except Exception:
            return False


# Factory function for creating NEAR service instances
def create_near_service(
    network: str = "testnet",
    account_id: Optional[str] = None,
    private_key: Optional[str] = None,
    contract_id: str = "semantic-guard.testnet"
) -> NEARService:
    """
    Factory function to create NEAR service instance.
    
    Args:
        network: NEAR network
        account_id: NEAR account ID
        private_key: Private key
        contract_id: Contract account ID
        
    Returns:
        NEARService: Configured service instance
    """
    # Try to get credentials from environment if not provided
    if not account_id:
        account_id = os.getenv("NEAR_ACCOUNT_ID")
    
    if not private_key:
        private_key = os.getenv("NEAR_PRIVATE_KEY")
    
    return NEARService(
        network=network,
        account_id=account_id,
        private_key=private_key,
        contract_id=contract_id
    )