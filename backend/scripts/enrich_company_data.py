"""Enrich NIFTY 500 data with BSE codes and market cap.

This script:
1. Reads raw NIFTY 500 CSV from NSE
2. Enriches with BSE codes (via manual mapping or scraping)
3. Adds market cap data
4. Outputs enriched CSV ready for seeding

Usage:
    python scripts/enrich_company_data.py --input data/nifty500_raw.csv --output data/nifty500_enriched.csv
    python scripts/enrich_company_data.py --mode manual-mapping  # Uses pre-built mapping
"""

import argparse
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import pandas as pd
import requests
from time import sleep

# Manual mapping for top 100 companies (NSE Symbol -> BSE Code)
# You can expand this list as needed
NSE_TO_BSE_MAPPING = {
    'RELIANCE': '500325',
    'TCS': '532540',
    'HDFCBANK': '500180',
    'INFY': '500209',
    'ICICIBANK': '532174',
    'BHARTIARTL': '532454',
    'SBIN': '500112',
    'HINDUNILVR': '500696',
    'ITC': '500875',
    'KOTAKBANK': '500247',
    'AXISBANK': '532215',
    'LT': '500510',
    'ASIANPAINT': '500820',
    'MARUTI': '532500',
    'HCLTECH': '532281',
    'WIPRO': '507685',
    'BAJFINANCE': '500034',
    'M&M': '500520',
    'SUNPHARMA': '524715',
    'TITAN': '500114',
    'ULTRACEMCO': '532538',
    'NESTLEIND': '500790',
    'ADANIENT': '512599',
    'POWERGRID': '532898',
    'NTPC': '532555',
    # Add more as needed...
}


def load_nse_csv(file_path: str) -> pd.DataFrame:
    """Load raw NIFTY 500 CSV from NSE."""
    print(f"📁 Loading CSV: {file_path}")

    try:
        df = pd.read_csv(file_path)
        print(f"✅ Loaded {len(df)} companies")

        # Standardize column names
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        # Check required columns
        required = ['company_name', 'symbol']
        missing = [col for col in required if col not in df.columns]

        if missing:
            print(f"⚠️  Missing columns: {missing}")
            print(f"   Available: {list(df.columns)}")
            # Try common variations
            if 'company' in df.columns:
                df['company_name'] = df['company']

        return df

    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return None


def enrich_with_manual_mapping(df: pd.DataFrame) -> pd.DataFrame:
    """Enrich with pre-built NSE to BSE mapping."""
    print("\n🔍 Enriching with manual BSE code mapping...")

    df['bse_code'] = df['symbol'].map(NSE_TO_BSE_MAPPING)

    matched = df['bse_code'].notna().sum()
    print(f"✅ Matched {matched}/{len(df)} companies with BSE codes")

    return df


def enrich_with_screener_data(df: pd.DataFrame, delay: float = 1.0) -> pd.DataFrame:
    """
    Enrich with market cap and sector data from Screener.in

    WARNING: This makes HTTP requests. Use responsibly.
    Adds delay between requests to avoid rate limiting.
    """
    print("\n🌐 Enriching with Screener.in data...")
    print("⚠️  This will make HTTP requests. Press Ctrl+C to skip.")

    try:
        for idx, row in df.iterrows():
            symbol = row['symbol']

            try:
                # Try to fetch data from Screener.in
                url = f"https://www.screener.in/api/company/{symbol}/"
                headers = {'User-Agent': 'Mozilla/5.0'}

                response = requests.get(url, headers=headers, timeout=5)

                if response.status_code == 200:
                    data = response.json()

                    # Extract data
                    if 'bse_code' not in df.columns or pd.isna(df.at[idx, 'bse_code']):
                        df.at[idx, 'bse_code'] = data.get('bse_code')

                    df.at[idx, 'market_cap_cr'] = data.get('market_cap', 0) / 10000000  # Convert to crores
                    df.at[idx, 'sector'] = data.get('sector', 'Not Classified')

                    print(f"✅ {symbol}: BSE {df.at[idx, 'bse_code']}, MCap ₹{df.at[idx, 'market_cap_cr']:.0f}cr")
                else:
                    print(f"⚠️  {symbol}: No data found")

                # Rate limiting
                sleep(delay)

            except Exception as e:
                print(f"⚠️  {symbol}: Error - {e}")
                continue

    except KeyboardInterrupt:
        print("\n⏸️  Enrichment interrupted by user")

    return df


def add_default_values(df: pd.DataFrame) -> pd.DataFrame:
    """Add default values for missing fields."""
    print("\n📝 Adding default values...")

    # Ensure required columns exist
    if 'industry' not in df.columns:
        df['industry'] = 'Not Classified'

    if 'sector' not in df.columns:
        df['sector'] = 'Not Classified'

    if 'market_cap_cr' not in df.columns:
        df['market_cap_cr'] = None

    # Standardize names
    df.rename(columns={
        'company_name': 'name',
        'symbol': 'nse_symbol',
        'isin_code': 'isin',
        'isin': 'isin',
    }, inplace=True)

    # Fill missing ISIN with placeholder
    if 'isin' in df.columns:
        df['isin'] = df['isin'].fillna('')

    return df


def save_enriched_csv(df: pd.DataFrame, output_path: str):
    """Save enriched CSV."""
    print(f"\n💾 Saving enriched CSV: {output_path}")

    # Select and order columns
    output_cols = ['name', 'nse_symbol', 'bse_code', 'isin', 'industry', 'sector', 'market_cap_cr']
    available_cols = [col for col in output_cols if col in df.columns]

    df_output = df[available_cols]
    df_output.to_csv(output_path, index=False)

    print(f"✅ Saved {len(df_output)} companies")
    print(f"\n📊 Summary:")
    print(f"   • Total companies: {len(df_output)}")
    print(f"   • With BSE codes: {df_output['bse_code'].notna().sum()}")
    print(f"   • With market cap: {df_output['market_cap_cr'].notna().sum() if 'market_cap_cr' in df_output.columns else 0}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Enrich NIFTY 500 data')
    parser.add_argument('--input', type=str, default='data/nifty500_raw.csv',
                        help='Input CSV file from NSE')
    parser.add_argument('--output', type=str, default='data/nifty500_enriched.csv',
                        help='Output enriched CSV file')
    parser.add_argument('--mode', choices=['manual', 'screener', 'both'], default='manual',
                        help='Enrichment mode')

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("📊 NIFTY 500 Data Enrichment")
    print("=" * 60)

    # Load CSV
    df = load_nse_csv(args.input)
    if df is None:
        return 1

    # Enrich based on mode
    if args.mode in ['manual', 'both']:
        df = enrich_with_manual_mapping(df)

    if args.mode in ['screener', 'both']:
        df = enrich_with_screener_data(df)

    # Add defaults
    df = add_default_values(df)

    # Save
    save_enriched_csv(df, args.output)

    print("\n✅ Enrichment complete!")
    print(f"\nNext step:")
    print(f"   python scripts/seed_companies.py --source csv --file {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
