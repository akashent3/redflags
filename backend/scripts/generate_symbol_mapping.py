"""
Generate symbol_mapping.json from FinEdge API.
This script fetches all stock symbols from FinEdge and creates a mapping file.

Usage:
    python scripts/generate_symbol_mapping.py
"""

import json
import requests
import os
from pathlib import Path

# FinEdge API configuration
FINEDGE_API_URL = "https://data.finedgeapi.com/api/v1/stock-symbols"
FINEDGE_API_TOKEN = os.getenv("FINEDGE_API_TOKEN", "hicmeh4o6heyducv4usdzfz6ar2dsrassmerqrc4jnparnj5ylgps77rxgdfmleuddifs3xxcycpijddc5eq")

# Output file path
OUTPUT_DIR = Path(__file__).parent.parent / "data"
OUTPUT_FILE = OUTPUT_DIR / "symbol_mapping.json"


def fetch_symbols():
    """Fetch all symbols from FinEdge API."""
    print(f"Fetching symbols from FinEdge API...")
    
    try:
        response = requests.get(
            FINEDGE_API_URL,
            params={"token": FINEDGE_API_TOKEN},
            timeout=30
        )
        response.raise_for_status()
        
        symbols = response.json()
        print(f"✅ Fetched {len(symbols)} symbols")
        return symbols
        
    except requests.RequestException as e:
        print(f"❌ Failed to fetch symbols: {e}")
        return []


def create_symbol_mapping(symbols):
    """
    Create symbol mapping dictionary.
    Maps broker symbols to FinEdge API symbols.
    
    Example:
        "RELIANCE" -> "RELIANCE"
        "TCS" -> "TCS"
        "HDFCBANK" -> "HDFCBANK"
    """
    mapping = {}
    
    for symbol_data in symbols:
        # Primary symbol (usually NSE symbol)
        symbol = symbol_data.get("symbol", "")
        
        if symbol:
            # Map to itself (broker symbols usually match NSE symbols)
            mapping[symbol] = symbol
            
            # Also map NSE code if different
            nse_code = symbol_data.get("nse_code", "")
            if nse_code and nse_code != symbol:
                mapping[nse_code] = symbol
            
            # Also map BSE code if available
            bse_code = symbol_data.get("bse_code", "")
            if bse_code:
                mapping[bse_code] = symbol
    
    return mapping


def save_mapping(mapping):
    """Save mapping to JSON file."""
    # Create data directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(mapping)} symbol mappings to {OUTPUT_FILE}")


def main():
    print("=" * 60)
    print("Symbol Mapping Generator")
    print("=" * 60)
    
    # Fetch symbols from API
    symbols = fetch_symbols()
    
    if not symbols:
        print("❌ No symbols fetched. Exiting.")
        return 1
    
    # Create mapping
    print(f"\nCreating symbol mapping...")
    mapping = create_symbol_mapping(symbols)
    
    # Save to file
    save_mapping(mapping)
    
    print("\n" + "=" * 60)
    print("✅ Symbol mapping generation complete!")
    print("=" * 60)
    
    # Show some examples
    print("\nSample mappings:")
    for i, (key, value) in enumerate(list(mapping.items())[:10]):
        print(f"  {key} → {value}")
    
    return 0


if __name__ == "__main__":
    exit(main())