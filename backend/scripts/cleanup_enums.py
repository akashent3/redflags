"""Cleanup script to drop existing ENUM types before migration."""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def cleanup_enums():
    """Drop existing ENUM types that are blocking migration."""
    print("=" * 60)
    print("Cleaning up existing ENUM types")
    print("=" * 60)

    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("[ERROR] DATABASE_URL not set")
        return False

    try:
        engine = create_engine(database_url)

        with engine.connect() as conn:
            # Drop existing ENUM types (CASCADE will drop dependent objects)
            enums_to_drop = [
                'alert_type_enum',
                'alert_severity_enum',
                'alert_frequency_enum'
            ]

            for enum_name in enums_to_drop:
                try:
                    print(f"\nDropping {enum_name}...")
                    conn.execute(text(f"DROP TYPE IF EXISTS {enum_name} CASCADE"))
                    print(f"[OK] Dropped {enum_name}")
                except Exception as e:
                    print(f"[WARNING] Could not drop {enum_name}: {e}")

            conn.commit()
            print("\n" + "=" * 60)
            print("Cleanup completed successfully!")
            print("=" * 60)
            print("\nYou can now run the migration:")
            print("   python scripts/run_migration.py")
            return True

    except Exception as e:
        print(f"\n[ERROR] Cleanup failed: {e}")
        return False

if __name__ == "__main__":
    success = cleanup_enums()
    sys.exit(0 if success else 1)
