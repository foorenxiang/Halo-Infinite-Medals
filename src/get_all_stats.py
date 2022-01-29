import sys, os
from functools import partial
import ssl
import logging
from lib import lib as Lib

sys.path.append(os.getcwd())
from src.environment import env

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    pass


def _get_stats(gamer_tag, match_type="pvp", token=""):
    if not gamer_tag:
        raise ValueError("Please provide your Spartan Service number:")
    if not token:
        raise AuthenticationError(
            "Please provide your autocode.com token in the .env file"
        )

    ssl._create_default_https_context = ssl._create_unverified_context
    lib = Lib({"token": token})

    try:
        result = (
            lib.halo.infinite["@0.3.7"]
            .stats["service-record"]
            .multiplayer({"gamertag": gamer_tag, "filter": f"matchmade:{match_type}"})
        )
        return result
    except RuntimeError:
        logger.warning(f"Could not find gamertag {gamer_tag}")


get_all_stats = partial(_get_stats, token=env["LIB_TOKEN"])
