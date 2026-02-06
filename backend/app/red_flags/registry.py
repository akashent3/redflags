"""Central registry for all 54 red flag detectors."""

import logging
from typing import Dict, List, Optional

from app.models.red_flag import FlagCategory
from app.red_flags.base import RedFlagBase

logger = logging.getLogger(__name__)


class FlagRegistry:
    """Registry to manage all red flag detectors."""

    def __init__(self):
        """Initialize empty registry."""
        self._flags: Dict[int, RedFlagBase] = {}
        logger.info("FlagRegistry initialized")

    def register(self, flag: RedFlagBase) -> None:
        """
        Register a red flag detector.

        Args:
            flag: RedFlagBase instance to register

        Raises:
            ValueError: If flag number already registered
        """
        if flag.flag_number in self._flags:
            logger.warning(
                f"Flag #{flag.flag_number} already registered, overwriting"
            )

        self._flags[flag.flag_number] = flag
        logger.debug(
            f"Registered flag #{flag.flag_number}: {flag.flag_name} ({flag.category.value})"
        )

    def get_flag(self, flag_number: int) -> Optional[RedFlagBase]:
        """
        Get a specific flag by number.

        Args:
            flag_number: Flag number (1-54)

        Returns:
            RedFlagBase instance or None if not found
        """
        return self._flags.get(flag_number)

    def get_all_flags(self) -> List[RedFlagBase]:
        """
        Get all registered flags.

        Returns:
            List of all RedFlagBase instances, sorted by flag number
        """
        return sorted(self._flags.values(), key=lambda f: f.flag_number)

    def get_flags_by_category(self, category: FlagCategory) -> List[RedFlagBase]:
        """
        Get all flags in a specific category.

        Args:
            category: FlagCategory enum value

        Returns:
            List of RedFlagBase instances in category, sorted by flag number
        """
        flags = [f for f in self._flags.values() if f.category == category]
        return sorted(flags, key=lambda f: f.flag_number)

    def get_flag_count(self) -> int:
        """
        Get total number of registered flags.

        Returns:
            Count of registered flags
        """
        return len(self._flags)

    def get_category_counts(self) -> Dict[FlagCategory, int]:
        """
        Get count of flags per category.

        Returns:
            Dictionary mapping categories to flag counts
        """
        counts: Dict[FlagCategory, int] = {}

        for flag in self._flags.values():
            if flag.category not in counts:
                counts[flag.category] = 0
            counts[flag.category] += 1

        return counts

    def is_complete(self) -> bool:
        """
        Check if all 54 flags are registered.

        Returns:
            True if 54 flags registered, False otherwise
        """
        return len(self._flags) == 54

    def get_missing_flag_numbers(self) -> List[int]:
        """
        Get list of flag numbers that are not yet registered.

        Returns:
            List of missing flag numbers (1-54)
        """
        all_numbers = set(range(1, 55))
        registered_numbers = set(self._flags.keys())
        missing = all_numbers - registered_numbers
        return sorted(list(missing))

    def validate_registry(self) -> Dict[str, any]:
        """
        Validate registry completeness and correctness.

        Returns:
            Dictionary with validation results:
            - is_complete: bool
            - total_flags: int
            - missing_flags: List[int]
            - category_counts: Dict[FlagCategory, int]
        """
        return {
            "is_complete": self.is_complete(),
            "total_flags": self.get_flag_count(),
            "missing_flags": self.get_missing_flag_numbers(),
            "category_counts": self.get_category_counts(),
        }


# Global singleton registry
flag_registry = FlagRegistry()
