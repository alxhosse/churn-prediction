"""Download actions2load.csv from Google Drive for local Postgres load (gitignored).

The Fight Churn sample file is used by local-db/sql_load/02_load_actions.sql via
/workspace/actions2load.csv when the repo root is mounted in Docker.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import gdown

# https://drive.google.com/file/d/1Xulv2JS46JZKQBfh1ehu5N9wTFArL9QG/view
DEFAULT_FILE_ID = "1Xulv2JS46JZKQBfh1ehu5N9wTFArL9QG"
DEFAULT_FILENAME = "actions2load.csv"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download actions2load.csv from Google Drive (default: repo root).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=_repo_root() / DEFAULT_FILENAME,
        help=f"Destination file path (default: repo root / {DEFAULT_FILENAME})",
    )
    parser.add_argument(
        "--file-id",
        default=DEFAULT_FILE_ID,
        help="Google Drive file id (from the share link)",
    )
    args = parser.parse_args()
    out = args.output.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    gdown.download(id=args.file_id, output=str(out), quiet=False)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
