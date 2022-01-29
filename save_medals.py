import requests
from pathlib import Path
from get_medal_stats import get_spartan_medal_stats
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)
MEDAL_CACHE_FOLDER = Path("./.medal_cache")


class PathStr(str):
    pass


def _print_medals_received(medal_stats: dict):
    for medal_descriptor in medal_stats:
        medal_count = medal_descriptor["count"]
        medal_name = medal_descriptor["name"]
        print(
            f"Earned {medal_count} {medal_name} medal{'s' if medal_count > 1 else ''}"
        )


def _create_medal_folder(medals_folder: PathStr):
    Path(medals_folder).mkdir(exist_ok=True)


@lru_cache()
def get_medal_image_data(medal_image_url):
    medal_filename = Path(medal_image_url).name
    medal_cache_file: Path = MEDAL_CACHE_FOLDER / medal_filename
    if medal_cache_file.exists():
        medal_image_data = open(medal_cache_file, "rb").read()
    else:
        res = requests.get(medal_image_url)
        if 200 <= res.status_code < 300:
            medal_image_data = res.content
        else:
            logger.warning(f"Failed to get medal for {medal_image_url}")
            return
        with open(medal_cache_file, "wb") as fp:
            fp.write(medal_image_data)
    return medal_image_data


def _download_medals(medal_stats: dict, medals_folder: PathStr):
    print("")
    for medal_descriptor in medal_stats:
        medal_image_url = medal_descriptor["image_urls"]["large"]
        medal_count = medal_descriptor["count"]
        medal_name = str(Path(medal_image_url).stem)
        medal_image_data = get_medal_image_data(medal_image_url)

        if medal_image_data:
            medal_count = medal_descriptor["count"]
            new_medal_count = _create_medal_images(
                medals_folder,
                medal_count,
                medal_image_url,
                medal_image_data,
            )
            if new_medal_count:
                print(
                    f"Awarding {new_medal_count} new {medal_name} medal{'s' if medal_count > 1 else ''}"
                )
        else:
            logger.warning("Failed to award medal_name")


def _create_medal_images(
    medals_folder: str,
    medal_count: int,
    medal_image_url: str,
    medal_image_data: bytes,
):
    medal_path_stem = Path(medal_image_url).stem
    medal_path_suffix = Path(medal_image_url).suffix
    new_medal_count = 0
    for idx in range(medal_count):
        medal_file_name = (
            f"{medals_folder}/{medal_path_stem}_{idx+1}{medal_path_suffix}"
        )
        if not Path(medal_file_name).exists():
            new_medal_count += 1
            with open(
                medal_file_name,
                "wb",
            ) as fp:
                fp.write(medal_image_data)
    return new_medal_count


def save_medals(spartan_id: str, medal_stats: dict):
    medals_folder = PathStr(f"./{spartan_id}")
    MEDAL_CACHE_FOLDER.mkdir(exist_ok=True)
    _create_medal_folder(medals_folder)
    _download_medals(medal_stats, medals_folder)


def show_me_ma_medals(spartan_id: str):
    spartan_id, medal_stats = get_spartan_medal_stats(spartan_id)
    if not (spartan_id and medal_stats):
        logger.warning(f"Spartan {spartan_id} not found!")
        return
    _print_medals_received(medal_stats)
    save_medals(spartan_id, medal_stats)


if __name__ == "__main__":
    while True:
        spartan_id = input("What is your id, Spartan?: ")
        show_me_ma_medals(spartan_id)
