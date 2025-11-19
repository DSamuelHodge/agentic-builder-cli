#!/usr/bin/env python3
"""Check that CHANGELOG.md contains the provided version.

Usage: python tools/check_changelog.py 0.3.0

This is used by CI before publishing: it ensures changelog has an entry for the tag.
"""

import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Usage: check_changelog.py <version>")
        return 2

    version = sys.argv[1]
    changelog = Path("CHANGELOG.md")
    if not changelog.exists():
        print("CHANGELOG.md is missing. Please add one before release.")
        return 2
    text = changelog.read_text(encoding="utf-8")
    if version in text:
        print(f"CHANGELOG.md contains entry for {version}")
        return 0
    else:
        print(
            f"Missing changelog entry for {version}. Add a section for {version} in CHANGELOG.md"
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
