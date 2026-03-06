#!/usr/bin/env python3
"""
Orchestrate the full mixtape build pipeline.
"""
import sys
import argparse
from pathlib import Path
import yaml
import shutil

from download import download_mixtape
from tag import tag_track
from artwork import embed_artwork
from gaps import generate_gap


def get_duration_from_flac(flac_path):
    """
    Get duration of a FLAC file in seconds.
    Returns None if duration cannot be determined.
    """
    try:
        from mutagen.flac import FLAC
        audio = FLAC(str(flac_path))
        return audio.info.length
    except Exception:
        return None


def build_mixtape(yaml_path, output_base, cookies_path=None):
    """
    Build a complete mixtape: download, tag, embed artwork, and create playlist.

    Args:
        yaml_path: Path to mixtape YAML file
        output_base: Base output directory
        cookies_path: Optional path to yt-dlp cookies file
    """
    yaml_path = Path(yaml_path)
    output_base = Path(output_base)

    # Load YAML
    with open(yaml_path, 'r') as f:
        mixtape = yaml.safe_load(f)

    # Derive slug from filename
    slug = yaml_path.stem
    output_dir = output_base / slug
    # Raw files stored in /var/tmp (auto-cleaned, never synced)
    raw_dir = Path(f'/var/tmp/mixtapes-{slug}')

    print(f"\n=== Building Mixtape: {mixtape['title']} ===\n")

    # Step 1: Download raw FLACs
    print("Step 1: Downloading tracks...")
    download_mixtape(yaml_path, output_base, cookies_path)

    # Step 2: Process each track
    print("\nStep 2: Processing tracks...")
    # Put files directly in mixtape folder (no tracks/ subfolder) for Syncthing compatibility
    final_dir = output_dir
    final_dir.mkdir(parents=True, exist_ok=True)

    tracks = mixtape.get('tracks', [])
    playlist_lines = ['#EXTM3U']
    track_counter = 1
    gap_counter = 1

    for track_idx, track in enumerate(tracks):
        track_num_str = f"{track_idx + 1:02d}"

        # Find raw file
        work_slug = track.get('work', 'track').lower().replace(' ', '-')[:30]
        raw_flac = raw_dir / f"{track_num_str}-{work_slug}.flac"

        if not raw_flac.exists():
            print(f"Warning: raw file not found for track {track_num_str}, skipping")
            continue

        # Copy to final location with track number
        final_flac = final_dir / f"{track_num_str}-track.flac"
        shutil.copy(raw_flac, final_flac)
        print(f"Copied: {final_flac}")

        # Tag the file
        tag_track(final_flac, track, track_idx + 1, len(tracks))

        # Embed artwork
        if 'artwork' in mixtape:
            try:
                embed_artwork(final_flac, mixtape['artwork'])
            except Exception as e:
                print(f"Warning: Failed to embed artwork: {e}")

        # Add to playlist
        duration = get_duration_from_flac(final_flac)
        duration_str = f"{int(duration)}" if duration else "-1"
        title_parts = []
        if 'composer' in track:
            title_parts.append(track['composer'])
        if 'movement_name' in track:
            title_parts.append(track['movement_name'])
        title = " - ".join(title_parts) if title_parts else track.get('work', 'Unknown')
        playlist_lines.append(f"#EXTINF:{duration_str},{title}")
        playlist_lines.append(f"{track_num_str}-track.flac")

        # Handle gap after track
        gap_after = track.get('gap_after', 0)
        if gap_after > 0:
            gap_filename = f"{track_num_str}{chr(96 + gap_counter)}-gap.flac"
            gap_path = final_dir / gap_filename
            generate_gap(gap_path, gap_after)

            # Add gap to playlist
            playlist_lines.append(f"#EXTINF:{int(gap_after)},Gap")
            playlist_lines.append(gap_filename)

            gap_counter += 1

    # Step 3: Write playlist
    print("\nStep 3: Writing playlist...")
    playlist_path = output_dir / 'playlist.m3u'
    with open(playlist_path, 'w') as f:
        f.write('\n'.join(playlist_lines) + '\n')
    print(f"Created: {playlist_path}")

    # Summary
    print(f"\n=== Build Complete ===")
    print(f"Output directory: {output_dir}")
    print(f"Upload {output_dir}/ to Google Drive for listening on phone.")


def main():
    parser = argparse.ArgumentParser(description='Build a classical mixtape')
    parser.add_argument('yaml_path', help='Path to mixtape YAML file')
    parser.add_argument('--cookies', help='Path to yt-dlp cookies file')
    parser.add_argument('--output', default=None, help='Base output directory (default: parent of yaml_path/output)')

    args = parser.parse_args()

    yaml_path = Path(args.yaml_path)

    # Default output dir
    if args.output:
        output_base = Path(args.output)
    else:
        output_base = yaml_path.parent.parent / 'output'

    build_mixtape(yaml_path, output_base, args.cookies)


if __name__ == '__main__':
    main()
