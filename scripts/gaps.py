#!/usr/bin/env python3
"""
Generate silent gap tracks in FLAC format.
"""
import subprocess
import sys
from pathlib import Path


def generate_gap(output_path, duration_seconds):
    """
    Generate a silent FLAC file.

    Args:
        output_path: Path where the FLAC file will be written
        duration_seconds: Duration of silence in seconds
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        'ffmpeg',
        '-f', 'lavfi',
        '-i', 'anullsrc=r=44100:cl=stereo',
        '-t', str(duration_seconds),
        '-c:a', 'flac',
        '-y',  # Overwrite output file without asking
        str(output_path)
    ]

    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Generated gap: {output_path} ({duration_seconds}s)")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <duration_seconds> <output_path>")
        sys.exit(1)

    duration = float(sys.argv[1])
    output = sys.argv[2]
    generate_gap(output, duration)
