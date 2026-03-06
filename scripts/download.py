#!/usr/bin/env python3
"""
Download tracks from YouTube Music using yt-dlp.
"""
import subprocess
import sys
import yaml
from pathlib import Path


def download_mixtape(yaml_path, output_dir, cookies_path=None):
    """
    Download all tracks from a mixtape YAML file.

    Args:
        yaml_path: Path to the mixtape YAML file
        output_dir: Base output directory for raw downloads
        cookies_path: Optional path to yt-dlp cookies file
    """
    yaml_path = Path(yaml_path)
    output_dir = Path(output_dir)

    # Load YAML
    with open(yaml_path, 'r') as f:
        mixtape = yaml.safe_load(f)

    # Derive slug from filename
    slug = yaml_path.stem
    raw_dir = output_dir / slug / 'raw'
    raw_dir.mkdir(parents=True, exist_ok=True)

    tracks = mixtape.get('tracks', [])

    for idx, track in enumerate(tracks, 1):
        track_num = f"{idx:02d}"

        # Generate output filename
        work_slug = track.get('work', 'track').lower().replace(' ', '-')[:30]
        output_path = raw_dir / f"{track_num}-{work_slug}.flac"

        # Skip if already downloaded
        if output_path.exists():
            print(f"Skipping {track_num}: already exists at {output_path}")
            continue

        # Determine search query or URL
        if 'ytm_id' in track:
            query = f"https://music.youtube.com/watch?v={track['ytm_id']}"
        elif 'search_query' in track:
            query = f"ytsearch1:{track['search_query']}"
        else:
            print(f"Warning: track {track_num} has no ytm_id or search_query, skipping")
            continue

        # Build yt-dlp command
        cmd = [
            'yt-dlp',
            '--format', 'bestaudio',
            '--extract-audio',
            '--audio-format', 'flac',
            '--audio-quality', '0',
            '-o', str(output_path),
        ]

        if cookies_path:
            cmd.extend(['--cookies', str(cookies_path)])

        cmd.append(query)

        print(f"Downloading {track_num}: {query}")
        subprocess.run(cmd, check=True)

    print(f"Downloads complete. Raw FLACs in: {raw_dir}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <yaml_path> [--cookies <cookies_path>]")
        sys.exit(1)

    yaml_path = sys.argv[1]
    cookies_path = None

    if len(sys.argv) >= 4 and sys.argv[2] == '--cookies':
        cookies_path = sys.argv[3]

    download_mixtape(yaml_path, Path(yaml_path).parent.parent / 'output', cookies_path)
