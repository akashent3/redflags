"""Verify backend setup and database connection."""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import os
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env_variables():
    """Check if all required environment variables are set."""
    print("=" * 60)
    print("STEP 1: Checking Environment Variables")
    print("=" * 60)

    required_vars = [
        'DATABASE_URL',
        'CELERY_BROKER_URL',
        'CELERY_RESULT_BACKEND',
        'GEMINI_API_KEY',
        'JWT_SECRET_KEY',
    ]

    optional_vars = [
        'BREVO_API_KEY',
        'VAPID_PRIVATE_KEY',
        'VAPID_PUBLIC_KEY',
        'R2_ACCESS_KEY_ID',
        'R2_SECRET_ACCESS_KEY',
    ]

    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:20]}..." if len(value) > 20 else f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            missing.append(var)

    print("\nOptional Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:20]}...")
        else:
            print(f"⚠️  {var}: NOT SET (optional)")

    if missing:
        print(f"\n❌ Missing required variables: {', '.join(missing)}")
        return False

    print("\n✅ All required environment variables are set!")
    return True


def check_database_connection():
    """Check database connection."""
    print("\n" + "=" * 60)
    print("STEP 2: Checking Database Connection")
    print("=" * 60)

    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not set")
            return False

        engine = create_engine(database_url)

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")

        # Check tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"\n📊 Found {len(tables)} tables in database:")
        for table in sorted(tables):
            print(f"   • {table}")

        # Check for new tables
        expected_new_tables = [
            'watchlist_items',
            'watchlist_alerts',
            'notification_preferences',
            'portfolios',
            'holdings'
        ]

        missing_tables = [t for t in expected_new_tables if t not in tables]

        if missing_tables:
            print(f"\n⚠️  Missing tables (need migration): {', '.join(missing_tables)}")
            print("\nRun migration with:")
            print("   cd backend")
            print("   alembic upgrade head")
            return False
        else:
            print("\n✅ All required tables exist!")

        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def check_redis_connection():
    """Check Redis connection."""
    print("\n" + "=" * 60)
    print("STEP 3: Checking Redis Connection")
    print("=" * 60)

    try:
        import redis
        redis_url = os.getenv('CELERY_BROKER_URL') or os.getenv('REDIS_URL')

        if not redis_url:
            print("❌ REDIS_URL not set")
            return False

        r = redis.from_url(redis_url)
        r.ping()
        print("✅ Redis connection successful!")
        return True

    except ImportError:
        print("⚠️  Redis package not installed (pip install redis)")
        return False
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("\nMake sure Redis is running:")
        print("   • Ubuntu/Debian: sudo systemctl start redis")
        print("   • macOS: brew services start redis")
        print("   • Windows: Download from https://redis.io/download")
        return False


def check_dependencies():
    """Check if all required packages are installed."""
    print("\n" + "=" * 60)
    print("STEP 4: Checking Python Dependencies")
    print("=" * 60)

    required_packages = [
        'fastapi',
        'sqlalchemy',
        'alembic',
        'celery',
        'pandas',
        'sib_api_v3_sdk',
        'pywebpush',
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)

    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("\nRun: pip install -r requirements.txt")
        return False

    print("\n✅ All required packages installed!")
    return True


def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("🔍 RedFlag AI Backend Verification")
    print("=" * 60)

    checks = [
        ("Environment Variables", check_env_variables),
        ("Python Dependencies", check_dependencies),
        ("Database Connection", check_database_connection),
        ("Redis Connection", check_redis_connection),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ {name} check failed with error: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 60)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 60)

    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 All checks passed! Backend is ready.")
        print("\nNext steps:")
        print("   1. Start FastAPI: uvicorn app.main:app --reload")
        print("   2. Start Celery Worker: celery -A app.celery_app worker --loglevel=info")
        print("   3. Start Celery Beat: celery -A app.celery_app beat --loglevel=info")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
