"""
Bitcoin Transaction Tracer - Educational Tool
Traces the lineage of Bitcoin transactions to understand blockchain transparency.

This is an EDUCATIONAL tool to demonstrate how Bitcoin's public ledger works.
Not for compliance, financial advice, or determining transaction legitimacy.
"""

import json
import requests
from typing import Dict, List, Set, Tuple
from collections import deque
from http.server import BaseHTTPRequestHandler
import time


class TransactionTracer:
    """
    Traces Bitcoin transactions backward through the blockchain.
    Uses Blockstream.info API (free, no authentication required).
    """
    
    def __init__(self, max_depth: int = 5, max_addresses: int = 50):
        """
        Initialize the tracer with limits to prevent excessive API calls.
        
        Args:
            max_depth: How many transaction hops to trace back (default 5)
            max_addresses: Maximum addresses to analyze (prevents runaway queries)
        """
        self.base_url = "https://blockstream.info/api"
        self.max_depth = max_depth
        self.max_addresses = max_addresses
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Bitcoin-Transaction-Explorer-Educational'})
        
        # Cache to avoid re-fetching same data
        self.tx_cache: Dict[str, dict] = {}
        self.address_cache: Dict[str, list] = {}
    
    def get_address_transactions(self, address: str) -> List[dict]:
        """
        Fetch all transactions for a given Bitcoin address.
        
        Args:
            address: Bitcoin address (legacy, segwit, or bech32)
            
        Returns:
            List of transaction objects
        """
        if address in self.address_cache:
            return self.address_cache[address]
        
        try:
            url = f"{self.base_url}/address/{address}/txs"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            txs = response.json()
            self.address_cache[address] = txs
            return txs
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching address {address}: {e}")
            return []
    
    def get_transaction(self, txid: str) -> dict:
        """
        Fetch detailed transaction information.
        
        Args:
            txid: Transaction ID (hash)
            
        Returns:
            Transaction object with inputs and outputs
        """
        if txid in self.tx_cache:
            return self.tx_cache[txid]
        
        try:
            url = f"{self.base_url}/tx/{txid}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            tx = response.json()
            self.tx_cache[txid] = tx
            
            # Rate limiting - be nice to free API
            time.sleep(0.2)
            
            return tx
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching transaction {txid}: {e}")
            return {}
    
    def is_coinbase(self, tx: dict) -> bool:
        """
        Check if transaction is a coinbase (mining reward) transaction.
        
        Coinbase transactions have no inputs (they create new bitcoins).
        These are the "purest" coins - directly from mining.
        """
        if not tx or 'vin' not in tx:
            return False
        
        # Coinbase tx has a single input with no previous output
        if len(tx['vin']) == 1 and 'txid' not in tx['vin'][0]:
            return True
        
        return False
    
    def trace_lineage(self, address: str) -> Dict:
        """
        Trace the lineage of coins received by an address.
        
        Uses breadth-first search to explore transaction history,
        going backwards from the address through its inputs.
        
        Args:
            address: Starting Bitcoin address
            
        Returns:
            Dictionary containing:
            - nodes: List of addresses/transactions in the graph
            - edges: Connections between them
            - metadata: Statistics and findings
        """
        # Data structures for the graph
        nodes = []  # List of {id, type, label, depth, ...}
        edges = []  # List of {source, target, amount, ...}
        visited_txs: Set[str] = set()
        visited_addresses: Set[str] = set()
        
        # BFS queue: (address/txid, depth, node_type)
        queue = deque([(address, 0, 'address')])
        visited_addresses.add(address)
        
        # Statistics tracking
        stats = {
            'total_addresses': 0,
            'total_transactions': 0,
            'max_depth_reached': 0,
            'coinbase_found': False,
            'coinbase_distance': None
        }
        
        # Add starting node
        nodes.append({
            'id': address,
            'type': 'address',
            'label': f"{address[:8]}...{address[-8:]}",
            'depth': 0,
            'is_target': True
        })
        
        while queue and len(visited_addresses) < self.max_addresses:
            current_id, depth, node_type = queue.popleft()
            
            if depth > self.max_depth:
                continue
            
            stats['max_depth_reached'] = max(stats['max_depth_reached'], depth)
            
            # Process based on node type
            if node_type == 'address':
                # Get transactions for this address
                txs = self.get_address_transactions(current_id)
                
                # Look at incoming transactions (where this address received coins)
                for tx in txs:
                    txid = tx['txid']
                    
                    if txid in visited_txs:
                        continue
                    
                    visited_txs.add(txid)
                    stats['total_transactions'] += 1
                    
                    # Get full transaction details
                    tx_details = self.get_transaction(txid)
                    
                    if not tx_details:
                        continue
                    
                    # Check if coinbase
                    is_coinbase = self.is_coinbase(tx_details)
                    if is_coinbase:
                        stats['coinbase_found'] = True
                        if stats['coinbase_distance'] is None:
                            stats['coinbase_distance'] = depth
                    
                    # Add transaction node
                    nodes.append({
                        'id': txid,
                        'type': 'transaction',
                        'label': f"TX: {txid[:8]}...",
                        'depth': depth,
                        'is_coinbase': is_coinbase,
                        'timestamp': tx_details.get('status', {}).get('block_time'),
                        'size': tx_details.get('size'),
                        'fee': tx_details.get('fee')
                    })
                    
                    # Add edge from transaction to address
                    edges.append({
                        'source': txid,
                        'target': current_id,
                        'type': 'output'
                    })
                    
                    # If not coinbase, trace inputs (where coins came FROM)
                    if not is_coinbase and depth < self.max_depth:
                        for inp in tx_details.get('vin', []):
                            if 'prevout' in inp and 'scriptpubkey_address' in inp['prevout']:
                                prev_address = inp['prevout']['scriptpubkey_address']
                                
                                if prev_address not in visited_addresses:
                                    visited_addresses.add(prev_address)
                                    stats['total_addresses'] += 1
                                    
                                    # Add previous address node
                                    nodes.append({
                                        'id': prev_address,
                                        'type': 'address',
                                        'label': f"{prev_address[:8]}...{prev_address[-8:]}",
                                        'depth': depth + 1
                                    })
                                    
                                    # Add edge from address to transaction
                                    edges.append({
                                        'source': prev_address,
                                        'target': txid,
                                        'type': 'input',
                                        'amount': inp['prevout'].get('value')
                                    })
                                    
                                    # Add to queue for further exploration
                                    queue.append((prev_address, depth + 1, 'address'))
        
        return {
            'nodes': nodes,
            'edges': edges,
            'stats': stats,
            'target_address': address
        }


# Vercel serverless function handler
class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless function handler.
    
    Accepts GET requests with 'address' parameter.
    Example: /api/trace?address=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa&depth=5
    """
    
    def do_GET(self):
        # Parse query parameters
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        
        # Get address from query params
        address = params.get('address', [None])[0]
        depth = int(params.get('depth', [5])[0])
        
        if not address:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': 'Missing required parameter: address',
                'usage': '/api/trace?address=<bitcoin_address>&depth=<optional_depth>'
            }).encode())
            return
        
        # Validate depth
        if depth < 1 or depth > 10:
            depth = 5
        
        try:
            # Trace the transaction lineage
            tracer = TransactionTracer(max_depth=depth)
            result = tracer.trace_lineage(address)
            
            # Add educational metadata
            result['educational_note'] = (
                "This shows the transaction history of the address. "
                "Each connection represents where coins came from. "
                "Bitcoin's public ledger makes all of this traceable."
            )
            
            # Success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')  # Allow frontend to call
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode())
            
        except Exception as e:
            # Error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': str(e),
                'message': 'Failed to trace transaction lineage'
            }).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


# For local testing
if __name__ == '__main__':
    # Test with Satoshi's first known address
    tracer = TransactionTracer(max_depth=3)
    result = tracer.trace_lineage('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa')
    print(json.dumps(result, indent=2))
