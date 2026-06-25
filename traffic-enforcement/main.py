"""CLI entrypoint for the traffic speed enforcement system.

Examples:
  python main.py --source traffic.mp4 --output annotated.mp4
  python main.py --source 0 --show              # live camera
"""

from __future__ import annotations

import argparse
import json

import config
from enforcement import EnforcementSystem


def _parse_source(value: str):
    return int(value) if value.isdigit() else value


def main():
    parser = argparse.ArgumentParser(description="AI traffic speed enforcement")
    parser.add_argument("--source", required=True,
                        help="video file path or camera index (e.g. 0)")
    parser.add_argument("--output", default=None,
                        help="path to write the annotated video")
    parser.add_argument("--show", action="store_true",
                        help="display annotated frames in a window")
    parser.add_argument("--limit", type=int, default=None,
                        help=f"override speed limit (default {config.SPEED_LIMIT_KMH} km/h)")
    args = parser.parse_args()

    if args.limit is not None:
        config.SPEED_LIMIT_KMH = args.limit

    system = EnforcementSystem()
    violations = system.process_video(
        _parse_source(args.source), output_path=args.output, show=args.show)

    print(f"\nProcessing complete. {len(violations)} violation(s) recorded "
          f"in '{config.VIOLATION_DIR}/'.")
    for v in violations:
        print(json.dumps(v, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
