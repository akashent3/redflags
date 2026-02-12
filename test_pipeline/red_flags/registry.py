"""Central registry for all red flag detectors."""

import logging
from typing import Dict, List, Optional

from red_flags.models import FlagCategory
from red_flags.base import RedFlagBase

logger = logging.getLogger(__name__)


class FlagRegistry:
    def __init__(self):
        self._flags: Dict[int, RedFlagBase] = {}

    def register(self, flag: RedFlagBase) -> None:
        self._flags[flag.flag_number] = flag

    def get_all_flags(self) -> List[RedFlagBase]:
        return sorted(self._flags.values(), key=lambda f: f.flag_number)

    def get_flag_count(self) -> int:
        return len(self._flags)


flag_registry = FlagRegistry()
