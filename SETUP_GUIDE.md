# Quick Setup Guide

## Files Created

1. **api/trace.py** - Main transaction tracing serverless function
2. **api/requirements.txt** - Python dependencies
3. **vercel.json** - Vercel configuration
4. **API_README.md** - Documentation (rename to README.md or keep separate)

## Adding to Your Repo

```bash
# In your project directory
git add api/trace.py api/requirements.txt vercel.json
git commit -m "Add transaction tracing API endpoint"
git push
```

Vercel will automatically detect the push and deploy!

## Testing After Deployment

Once deployed, your API will be available at:
```
https://your-project.vercel.app/api/trace?address=1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa&depth=3
```

Replace `your-project` with your actual Vercel project name.

## Expected Response Time

- First request: ~2-5 seconds (fetching from blockchain API)
- Deeper traces (depth=5+): ~5-10 seconds
- Vercel timeout: 10 seconds max (hobby tier)

## What You Can Do Now

✅ Test the API endpoint directly in your browser
✅ See the transaction graph data structure
✅ Verify it traces back through transactions
✅ Check if it finds coinbase (mining) transactions

## Next Steps

1. **Build frontend** - Create React/Vue components to visualize this data
2. **Add risk database** - Create the "traffic light" scoring system
3. **Add graph visualization** - Use D3.js or similar to show the network
4. **Educational content** - Explain what the patterns mean

## Quick Test (After Deployment)

Try these famous addresses:
- Satoshi's address: `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa`
- Pizza transaction: `1XPTgDRhN8RFnzniWCddobD9iKZatrvH4`

## Debugging

If you get errors:
1. Check Vercel function logs in dashboard
2. Verify Python runtime is set to 3.9
3. Make sure CORS headers are working
4. Check Blockstream API isn't rate limiting

## Rate Limiting

The code includes a 0.2 second delay between API calls to be respectful to Blockstream's free API. If you get 429 errors, the delay may need to increase.

Want help with the frontend next? 🎨
