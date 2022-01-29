from pprint import pprint
import requests
from pathlib import Path
from get_stats import get_stats


class PathStr(str):
    pass


def _sort_medal_stats(medal_stats):
    return sorted(
        medal_stats,
        key=lambda medal_descriptor: medal_descriptor["count"],
    )


def get_spartan_medal_stats(spartan_id: str):
    stats = get_stats(spartan_id)
    medal_stats = stats["data"]["core"]["breakdowns"]["medals"]
    sorted_medal_stats = _sort_medal_stats(medal_stats)
    return spartan_id, sorted_medal_stats


def _print_medals_received(medal_stats: dict):
    for medal_descriptor in medal_stats:
        medal_count = medal_descriptor["count"]
        medal_name = medal_descriptor["name"]
        print(
            f"Earned {medal_count} {medal_name} medal{'s' if medal_count > 1 else ''}"
        )


def _create_medal_folder(medals_folder: PathStr):
    Path(medals_folder).mkdir(exist_ok=True)


def _download_medals(medal_stats: dict, medals_folder: PathStr):
    print("")
    for medal_descriptor in medal_stats:
        medal_image_url = medal_descriptor["image_urls"]["large"]
        medal_count = medal_descriptor["count"]
        res = requests.get(medal_image_url)
        if 200 <= res.status_code < 300:
            medal_name = str(Path(medal_image_url).stem)
            print(
                f"Awarding {medal_count} {medal_name} medal{'s' if medal_count > 1 else ''}"
            )
            _create_medal_images(medals_folder, medal_descriptor, medal_image_url, res)
        else:
            print("Failed to get", medal_image_url)


def _create_medal_images(
    medals_folder: str,
    medal_descriptor: dict,
    medal_image_url: str,
    res: requests.Response,
):
    for idx in range(medal_descriptor["count"]):
        medal_file_name = f"./{medals_folder}/{Path(medal_image_url).stem}_{idx+1}{Path(medal_image_url).suffix}"
        if not Path(medal_file_name).exists():
            with open(
                medal_file_name,
                "wb",
            ) as fp:
                fp.write(res.content)


def save_medals(spartan_id: str, medal_stats: dict):
    medals_folder = PathStr(f"./{spartan_id}")
    _create_medal_folder(medals_folder)
    _download_medals(medal_stats, medals_folder)


def show_me_ma_medals(spartan_id: str):
    spartan_id, medal_stats = get_spartan_medal_stats(spartan_id)
    _print_medals_received(medal_stats)
    save_medals(spartan_id, medal_stats)


if __name__ == "__main__":
    spartan_id = input("What is your id, Spartan?: ")
    show_me_ma_medals(spartan_id)
