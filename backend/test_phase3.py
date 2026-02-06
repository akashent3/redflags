"""Test script to verify Phase 3 implementation."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Import all flag modules to trigger registration
from app.red_flags import auditor_flags
from app.red_flags import cashflow_flags
from app.red_flags import related_party_flags
from app.red_flags import promoter_flags
from app.red_flags import governance_flags
from app.red_flags import balance_sheet_flags
from app.red_flags import revenue_flags
from app.red_flags import textual_flags

# Import registry
from app.red_flags.registry import flag_registry
from app.models.red_flag import FlagCategory


def test_flag_registry():
    """Test that all 54 flags are registered."""
    print("=" * 80)
    print("PHASE 3: RED FLAG DETECTION ENGINE - REGISTRY TEST")
    print("=" * 80)
    print()

    # Get all flags
    all_flags = flag_registry.get_all_flags()
    print(f"Total flags registered: {len(all_flags)}")
    print()

    # Validate registry
    validation = flag_registry.validate_registry()

    print("Registry Validation:")
    print(f"  [OK] Complete: {validation['is_complete']}")
    print(f"  [OK] Total flags: {validation['total_flags']}")
    print(f"  [OK] Missing flags: {validation['missing_flags']}")
    print()

    # Category breakdown
    print("Category Breakdown:")
    category_counts = validation['category_counts']

    expected_counts = {
        FlagCategory.AUDITOR: 8,
        FlagCategory.CASH_FLOW: 8,
        FlagCategory.RELATED_PARTY: 7,
        FlagCategory.PROMOTER: 6,
        FlagCategory.GOVERNANCE: 7,
        FlagCategory.BALANCE_SHEET: 7,
        FlagCategory.REVENUE: 5,
        FlagCategory.TEXTUAL: 6,
    }

    for category, expected_count in expected_counts.items():
        actual_count = category_counts.get(category, 0)
        status = "[OK]" if actual_count == expected_count else "[FAIL]"
        print(f"  {status} {category.value:20s}: {actual_count}/{expected_count}")

    print()

    # List all flags
    print("All Registered Flags:")
    print("-" * 80)

    for category in FlagCategory:
        flags = flag_registry.get_flags_by_category(category)
        print(f"\n{category.value.upper()} ({len(flags)} flags):")

        for flag in flags:
            status_icon = "[FLAG]"
            print(
                f"  {status_icon} Flag #{flag.flag_number:2d}: {flag.flag_name:40s} "
                f"[{flag.severity.value}]"
            )

    print()
    print("=" * 80)
    print(f"RESULT: {'[PASS] ALL TESTS PASSED' if validation['is_complete'] else '[FAIL] TESTS FAILED'}")
    print("=" * 80)

    return validation['is_complete']


if __name__ == "__main__":
    try:
        success = test_flag_registry()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR]: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
