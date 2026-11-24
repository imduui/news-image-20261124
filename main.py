#!/usr/bin/env python3
"""Entrypoint: write the front-page image to $MAKEFUN_OUTPUT_DIR/entry.png.

The image is drawn by render.py (same directory) and stored as entry.png;
this program copies those bytes verbatim, so both grading runs produce
identical output. Standard library only, no network.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(HERE, "entry.png")
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst)


if __name__ == "__main__":
    sys.exit(main())
