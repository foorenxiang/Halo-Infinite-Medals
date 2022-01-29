import sys, os
import requests
from pathlib import Path
import logging
from functools import lru_cache

sys.path.append(os.getcwd())
from src.get_medal_stats import get_spartan_medal_stats


def change_to_right_working_directory():
    relative_reference_to_current_module = (
        Path(os.getcwd()) / Path(__file__).parent / Path(__file__).name
    )
    assert (
        relative_reference_to_current_module.exists()
    ), "Please run this script from project root folder"


change_to_right_working_directory()


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


def _read_medal_image_from_cache(medal_cache_filename):
    return open(medal_cache_filename, "rb").read()


def _is_successful_download(res):
    return 200 <= res.status_code < 300


def _extract_image_data(res):
    medal_image_data = res.content
    return medal_image_data


def _write_medal_image_to_disk(medal_cache_file, medal_image_data):
    with open(medal_cache_file, "wb") as fp:
        fp.write(medal_image_data)


def _warn_failed_download(medal_image_url):
    logger.warning(f"Failed to get medal for {medal_image_url}")


@lru_cache()
def get_medal_image_data(medal_image_url):
    medal_filename = Path(medal_image_url).name
    medal_cache_filepath: Path = MEDAL_CACHE_FOLDER / medal_filename
    if medal_cache_filepath.exists():
        medal_image_data = _read_medal_image_from_cache(medal_cache_filepath)
        assert medal_image_data, "Failed to read medal image from cache"
        return medal_image_data
    else:
        res: requests.Response = requests.get(medal_image_url)
        if _is_successful_download(res):
            medal_image_data = _extract_image_data(res)
            assert medal_image_data, "Failed to extract medal image data"
            _write_medal_image_to_disk(medal_cache_filepath, medal_image_data)
            return medal_image_data
        _warn_failed_download(medal_image_url)


def _process_medal_image_url(medal_descriptor):
    medal_image_url = medal_descriptor["image_urls"]["large"]
    medal_name = str(Path(medal_image_url).stem)
    medal_count = medal_descriptor["count"]
    return medal_name, medal_count, medal_image_url


def _print_new_medals_awarded(medal_name, medal_count, new_medals_awarded_count):
    print(
        f"Awarding {new_medals_awarded_count} new {medal_name} medal{'s' if medal_count > 1 else ''}"
    )


def _warn_failed_medal_awarding(medal_name):
    logger.warning(f"Failed to award {medal_name}")


def _download_medals(medal_stats: dict, medals_folder: PathStr):
    print("")
    for medal_descriptor in medal_stats:
        medal_name, medal_count, medal_image_url = _process_medal_image_url(
            medal_descriptor
        )
        medal_image_data = get_medal_image_data(medal_image_url)

        if medal_image_data:
            new_medals_awarded_count = _create_medal_images(
                medals_folder,
                medal_count,
                medal_image_url,
                medal_image_data,
            )
            if new_medals_awarded_count:
                _print_new_medals_awarded(
                    medal_name, medal_count, new_medals_awarded_count
                )
        else:
            _warn_failed_medal_awarding(medal_name)


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