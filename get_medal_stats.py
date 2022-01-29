from get_all_stats import get_all_stats


def _sort_medal_stats(medal_stats):
    return sorted(
        medal_stats,
        key=lambda medal_descriptor: medal_descriptor["count"],
    )


def get_spartan_medal_stats(spartan_id: str):
    stats = get_all_stats(spartan_id)
    if not stats:
        return None, None
    medal_stats = stats["data"]["core"]["breakdowns"]["medals"]
    sorted_medal_stats = _sort_medal_stats(medal_stats)
    return spartan_id, sorted_medal_stats
