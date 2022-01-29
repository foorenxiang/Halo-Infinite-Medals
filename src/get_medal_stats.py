import sys, os
import logging
from typing import Tuple, Optional

sys.path.append(os.getcwd())

from src.get_all_stats import get_all_stats

logger = logging.getLogger(__name__)


def _sort_medal_stats(medal_stats) -> dict:
    return sorted(
        medal_stats,
        key=lambda medal_descriptor: medal_descriptor["count"],
    )


def get_spartan_medal_stats(spartan_id: str) -> Tuple[Optional[str], dict]:
    stats = get_all_stats(spartan_id)
    if stats:
        try:
            medal_stats = stats["data"]["core"]["breakdowns"]["medals"]
            sorted_medal_stats = _sort_medal_stats(medal_stats)
            return spartan_id, sorted_medal_stats
        except:
            logger.warning("Failed to extract medal data from Waypoint network.")
