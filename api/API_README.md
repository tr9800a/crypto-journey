# Bitcoin Transaction Tracer API

Educational tool to trace Bitcoin transaction lineage and understand blockchain transparency.

## What This Does

This API traces the history of Bitcoin transactions backward through the blockchain, showing where coins came from. It's designed to teach how Bitcoin's public ledger works.

## API Endpoint

### `GET /api/trace`

Traces the transaction lineage for a Bitcoin address.

**Parameters:**
- `address` (required): Bitcoin address to trace (legacy, segwit, or bech32)
- `depth` (optional): How many hops backward to trace (1-10, default: 5)

**Example Request:**
```
/api/trace?address=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa&depth=5
```

**Response Format:**
```json
{
  "nodes": [
    {
      "id": "address_or_txid",
      "type": "address|transaction",
      "label": "Short display name",
      "depth": 0,
      "is_coinbase": false,
      "timestamp": 1234567890
    }
  ],
  "edges": [
    {
      "source": "node_id",
      "target": "node_id",
      "type": "input|output",
      "amount": 50000000
    }
  ],
  "stats": {
    "total_addresses": 15,
    "total_transactions": 8,
    "max_depth_reached": 5,
    "coinbase_found": true,
    "coinbase_distance": 3
  },
  "target_address": "original_address",
  "educational_note": "Explanation of what this shows"
}
```

## How It Works

1. **Starts at your address**: Takes the Bitcoin address you provide
2. **Finds incoming transactions**: Looks for transactions that sent coins TO that address
3. **Traces inputs backward**: For each transaction, finds where THOSE coins came from
4. **Builds a graph**: Creates nodes (addresses & transactions) and edges (flow of coins)
5. **Stops at limits**: 
   - Maximum depth (default 5 hops)
   - Maximum addresses (50) to prevent runaway queries
   - Coinbase transactions (mining rewards - the "source")

## Educational Purpose

This demonstrates:
- ✅ Bitcoin's transparency - all transactions are public
- ✅ Pseudonymity vs. anonymity - addresses are public, identities are not (unless linked)
- ✅ Transaction graphs - how coins flow through the network
- ✅ Coinbase transactions - where new bitcoin originates
- ✅ The "fungibility debate" - not all coins are treated equally despite being identical

## Testing Locally

```bash
# Install dependencies
pip install -r api/requirements.txt

# Run test
python api/trace.py
```

## Interesting Addresses to Try

- `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa` - Satoshi's first known address
- `1JArS6jzE3AJ9sZ3aFij1BmTcpFGgN86hA` - Known exchange address
- Your own address!

## Limitations

- Uses free Blockstream.info API (rate limited, polite delays)
- Large wallets with many transactions may time out
- 10 second Vercel function timeout
- Caches results within single request (doesn't persist)

## Next Steps

This is the foundation. Next we'll add:
1. Risk scoring (checking against known problematic addresses)
2. Frontend visualization (graph display)
3. Educational context (explaining what patterns mean)

## Educational Disclaimer

This is for learning about blockchain technology. NOT for:
- ❌ Compliance or AML screening
- ❌ Financial advice
- ❌ Determining transaction legitimacy
- ❌ Privacy invasion

Bitcoin addresses are public information, but linking addresses to real identities requires additional data.
