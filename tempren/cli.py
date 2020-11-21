#!/usr/bin/env python
import argparse
from typing import List


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="tempren", description="Template-based renaming utility"
    )
    operation_mode = parser.add_mutually_exclusive_group()
    operation_mode.add_argument(
        "-n",
        "--name-template",
        type=str,
        help="Template used to generate new filename string",
    )
    operation_mode.add_argument(
        "-p",
        "--path-template",
        type=str,
        help="Template used to generate new filepath string",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Do not perform any renaming - just show expected operation results",
    )
    parser.add_argument(
        "input_directory",
        type=str,
        help="Input directory where files to rename are stored",
    )

    args = parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv))
