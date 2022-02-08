import sys, os
import requests
from pathlib import Path
import logging
from functools import lru_cache
from typing import Optional, Tuple

sys.path.append(os.getcwd())
from src.get_medal_stats import get_spartan_medal_stats

logger = logging.getLogger(__name__)
MEDAL_CACHE_FOLDER = Path("./.medal_cache")


def _check_working_directory():
    relative_reference_to_current_module = (
        Path(os.getcwd()) / Path(__file__).parent / Path(__file__).name
    )
    assert (
        relative_reference_to_current_module.exists()
    ), "Please run this script from project root folder"


_check_working_directory()


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


def _read_medal_image_data_from_cache(medal_cache_filename) -> bytes:
    medal_image_data = open(medal_cache_filename, "rb").read()
    assert medal_image_data, "Failed to read medal image from cache"
    return medal_image_data


def _is_successful_download(res) -> bool:
    return 200 <= res.status_code < 300


def _extract_image_data(res: requests.Response) -> bytes:
    medal_image_data = res.content
    assert medal_image_data, "Failed to extract medal image data"
    return medal_image_data


def _cache_medal_image_to_disk(medal_cache_file, medal_image_data):
    with open(medal_cache_file, "wb") as fp:
        fp.write(medal_image_data)


def _warn_failed_download(medal_image_url):
    logger.warning(f"Failed to get medal for {medal_image_url}")


def _download_medal_image_data(medal_image_url) -> Optional[bytes]:
    download_response = requests.get(medal_image_url)
    if _is_successful_download(download_response):
        medal_image_data = _extract_image_data(download_response)
        return medal_image_data
    _warn_failed_download(medal_image_url)


def _download_and_cache_medal_image_data(
    medal_image_url, medal_cache_filepath
) -> bytes:
    medal_image_data = _download_medal_image_data(medal_image_url)
    assert medal_image_data, f"Failed to download image data from {medal_image_url}"
    _cache_medal_image_to_disk(medal_cache_filepath, medal_image_data)
    return medal_image_data


@lru_cache()
def get_medal_image_data(medal_image_url) -> Optional[bytes]:
    medal_cache_filepath = _resolve_medal_cache_filepath(medal_image_url)
    if medal_cache_filepath.exists():
        medal_image_data = _read_medal_image_data_from_cache(medal_cache_filepath)
        return medal_image_data
    return _download_and_cache_medal_image_data(medal_image_url, medal_cache_filepath)


def _resolve_medal_cache_filepath(medal_image_url) -> Path:
    medal_filename = Path(medal_image_url).name
    medal_cache_filepath: Path = MEDAL_CACHE_FOLDER / medal_filename
    return medal_cache_filepath


def _process_medal_image_descriptor(medal_descriptor) -> Tuple[str, str, int]:
    medal_image_url: str = medal_descriptor["image_urls"]["large"]
    medal_name = str(Path(medal_image_url).stem)
    medal_count: int = medal_descriptor["count"]
    return medal_name, medal_count, medal_image_url


def _print_new_medals_awarded(
    medal_name: str, medal_count: int, new_medals_awarded_count: int
):
    print(
        f"Awarding {new_medals_awarded_count} new {medal_name} medal{'s' if medal_count > 1 else ''}"
    )


def _download_medals(medal_stats: dict, medals_folder: PathStr):
    for medal_descriptor in medal_stats:
        medal_name, medal_count, medal_image_url = _process_medal_image_descriptor(
            medal_descriptor
        )
        medal_image_data = get_medal_image_data(medal_image_url)
        new_medals_awarded_count = _create_medal_images(
            medals_folder,
            medal_count,
            medal_image_url,
            medal_image_data,
        )
        if new_medals_awarded_count:
            _print_new_medals_awarded(medal_name, medal_count, new_medals_awarded_count)


def _resolve_medal_filename(
    medals_folder: str, medal_image_url: str, medal_index
) -> str:
    medal_path_stem = Path(medal_image_url).stem
    medal_path_suffix = Path(medal_image_url).suffix
    medal_filename = (
        f"{medals_folder}/{medal_path_stem}_{medal_index+1}{medal_path_suffix}"
    )
    return medal_filename


def _create_medal_images(
    medals_folder: str,
    medal_count: int,
    medal_image_url: str,
    medal_image_data: bytes,
):

    new_medal_count = 0
    for idx in range(medal_count):
        medal_file_name = _resolve_medal_filename(medals_folder, medal_image_url, idx)
        if not Path(medal_file_name).exists():
            new_medal_count += 1
            with open(
                medal_file_name,
                "wb",
            ) as fp:
                fp.write(medal_image_data)
    return new_medal_count


def save_medals(spartan_id: str, medal_stats: dict):
    MEDAL_CACHE_FOLDER.mkdir(exist_ok=True)
    medals_folder = PathStr(f"./{spartan_id}")
    _create_medal_folder(medals_folder)
    _download_medals(medal_stats, medals_folder)


def show_me_ma_medals(spartan_id: str):
    medal_stats_results = get_spartan_medal_stats(spartan_id)
    if medal_stats_results:
        spartan_id, medal_stats = medal_stats_results
        _print_medals_received(medal_stats)
        save_medals(spartan_id, medal_stats)
        return
    logger.warning(f"Spartan {spartan_id} not found!")


if __name__ == "__main__":
    while True:
        spartan_id = input("What is your id, Spartan?: ")
        show_me_ma_medals(spartan_id)
