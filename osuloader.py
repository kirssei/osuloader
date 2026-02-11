import requests
import argparse
import re
from pathlib import Path


import requests
import argparse
import re
from pathlib import Path


class OsuBeatMapsDownloader:

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0"
        }
        self.base_url = "https://catboy.best/d/{beatmap_id}"

    def _extract_id(self, value: str) -> int:
        value = value.strip()

        if value.isdigit():
            return int(value)

        match = re.search(r"(\d+)", value)
        if match:
            return int(match.group(1))

        raise ValueError(f"Cannot extract beatmap ID from: {value}")

    def _load_beatmap(self, beatmap_id: int):
        response = requests.get(
            url=self.base_url.format(beatmap_id=beatmap_id),
            headers=self.headers,
        )

        if response.status_code == 200:
            with open(f"{beatmap_id}.osz", "wb") as f:
                f.write(response.content)
            print(f"[OK] {beatmap_id} downloaded")
        else:
            print(f"[ERROR] {beatmap_id} not downloaded (status_code {response.status_code})")

    def download_from_single(self, value: str):
        beatmap_id = self._extract_id(value)
        self._load_beatmap(beatmap_id)

    def download_from_multiple(self, values: list[str]):
        for value in values:
            beatmap_id = self._extract_id(value)
            self._load_beatmap(beatmap_id)

    def download_from_file(self, filepath: str):
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    beatmap_id = self._extract_id(line)
                    self._load_beatmap(beatmap_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="osuloader",
        description="Download osu! beatmaps by ID, link, or from a .txt file",
        epilog=(
            "Examples:\n"
            "  osuloader.py -b 114220\n"
            "  osuloader.py -b https://osu.ppy.sh/beatmapsets/114220\n"
            "  osuloader.py -bs 114220 122416\n"
            "  osuloader.py -f beatmaps.txt"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-b", "--beatmap",
        metavar="ID_OR_LINK",
        help="Download one beatmap (ID or URL)"
    )

    group.add_argument(
        "-bs", "--beatmaps",
        nargs="+",
        metavar="ID_OR_LINK",
        help="Download multiple beatmaps (IDs or URLs)"
    )

    group.add_argument(
        "-f", "--file",
        metavar="FILE.txt",
        help="Download beatmaps from a .txt file (one ID or URL per line)"
    )

    args = parser.parse_args()

    downloader = OsuBeatMapsDownloader()

    try:
        if args.beatmap:
            downloader.download_from_single(args.beatmap)

        elif args.beatmaps:
            downloader.download_from_multiple(args.beatmaps)

        elif args.file:
            downloader.download_from_file(args.file)

    except Exception as e:
        print(f"[ERROR] {e}")
        exit(1)
