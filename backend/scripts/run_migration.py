"""Run Alembic migration and verify tables created."""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import os
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

load_dotenv()


def run_migration():
    """Run Alembic upgrade to head."""
    print("=" * 60)
    print("🔄 Running Database Migration")
    print("=" * 60)

    try:
        # Get alembic.ini path
        alembic_ini = backend_path / "alembic.ini"

        if not alembic_ini.exists():
            print(f"❌ alembic.ini not found at: {alembic_ini}")
            return False

        print(f"📁 Using alembic.ini: {alembic_ini}")

        # Create Alembic config
        alembic_cfg = Config(str(alembic_ini))

        # Run upgrade
        print("\n⏳ Running: alembic upgrade head\n")
        command.upgrade(alembic_cfg, "head")

        print("\n✅ Migration completed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_tables():
    """Verify that all required tables exist."""
    print("\n" + "=" * 60)
    print("🔍 Verifying Database Tables")
    print("=" * 60)

    try:
        database_url = os.getenv('DATABASE_URL')
        engine = create_engine(database_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        # Expected tables from all migrations
        expected_tables = [
            # Core tables (from initial migration)
            'users',
            'companies',
            'annual_reports',
            'analysis_results',
            'red_flags',
            # New tables (from watchlist/portfolio migration)
            'watchlist_items',
            'watchlist_alerts',
            'notification_preferences',
            'portfolios',
            'holdings',
            # Alembic metadata
            'alembic_version',
        ]

        print(f"\n📊 Database has {len(tables)} tables:\n")

        missing = []
        for table in expected_tables:
            if table in tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} (MISSING)")
                missing.append(table)

        if missing:
            print(f"\n⚠️  Missing tables: {', '.join(missing)}")
            return False

        # Show table details for new tables
        print("\n" + "=" * 60)
        print("📋 New Table Details")
        print("=" * 60)

        new_tables = [
            'watchlist_items',
            'watchlist_alerts',
            'notification_preferences',
            'portfolios',
            'holdings'
        ]

        for table_name in new_tables:
            if table_name in tables:
                columns = inspector.get_columns(table_name)
                print(f"\n{table_name}:")
                for col in columns:
                    nullable = "NULL" if col['nullable'] else "NOT NULL"
                    print(f"   • {col['name']:<30} {str(col['type']):<20} {nullable}")

        print("\n✅ All tables verified successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        return False


def main():
    """Run migration and verification."""
    print("\n" + "=" * 60)
    print("🗄️  Database Migration Script")
    print("=" * 60)

    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        print("\n❌ DATABASE_URL environment variable not set!")
        print("\nPlease set it in your .env file:")
        print("   DATABASE_URL=postgresql://user:password@localhost:5432/redflags")
        return 1

    # Run migration
    if not run_migration():
        return 1

    # Verify tables
    if not verify_tables():
        return 1

    print("\n" + "=" * 60)
    print("🎉 Migration Complete!")
    print("=" * 60)
    print("\nDatabase is ready with all tables:")
    print("   • Core tables (users, companies, reports, analysis)")
    print("   • Watchlist tables (items, alerts, preferences)")
    print("   • Portfolio tables (portfolios, holdings)")
    print("\nNext: Run seed scripts to populate company data")

    return 0


if __name__ == "__main__":
    sys.exit(main())
