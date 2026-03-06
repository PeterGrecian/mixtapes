#!/usr/bin/env python3
"""
Tag FLAC files with classical music metadata.
"""
import sys
import yaml
from pathlib import Path
from mutagen.flac import FLAC


def tag_track(flac_path, track_data, track_number, total_tracks):
    """
    Tag a FLAC file with classical music metadata.

    Args:
        flac_path: Path to the FLAC file to tag
        track_data: Dictionary with track metadata (composer, work, conductor, etc.)
        track_number: Track number in the album
        total_tracks: Total number of tracks in the album
    """
    flac_path = Path(flac_path)

    audio = FLAC(str(flac_path))

    # Build title from movement info if available
    if 'movement_number' in track_data and 'movement_name' in track_data:
        title = f"{track_data['movement_number']}. {track_data['movement_name']}"
    elif 'movement_name' in track_data:
        title = track_data['movement_name']
    else:
        title = track_data.get('work', 'Unknown')

    # Artist = composer
    artist = track_data.get('composer', 'Unknown')

    # Album = work
    album = track_data.get('work', 'Unknown')

    # Track number
    track_str = f"{track_number}/{total_tracks}"

    # Comment = conductor and ensemble
    comment_parts = []
    if 'conductor' in track_data:
        comment_parts.append(f"Cond: {track_data['conductor']}")
    if 'ensemble' in track_data:
        comment_parts.append(f"Ens: {track_data['ensemble']}")
    comment = "; ".join(comment_parts) if comment_parts else ""

    # Date = year recorded
    date = track_data.get('year_recorded')

    # Clear existing tags and set new ones
    audio.clear()
    audio['TITLE'] = title
    audio['ARTIST'] = artist
    audio['ALBUM'] = album
    audio['TRACKNUMBER'] = track_str

    if comment:
        audio['COMMENT'] = comment

    if date:
        audio['DATE'] = str(date)

    # Optional: add opus if available
    if 'opus' in track_data:
        audio['OPUS'] = track_data['opus']

    audio.save()
    print(f"Tagged: {flac_path} - {title}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <flac_path> <yaml_path> <track_index>")
        sys.exit(1)

    flac_path = sys.argv[1]
    yaml_path = sys.argv[2]
    track_index = int(sys.argv[3])

    # Load YAML to get track data
    with open(yaml_path, 'r') as f:
        mixtape = yaml.safe_load(f)

    track_data = mixtape['tracks'][track_index]
    total_tracks = len(mixtape['tracks'])

    tag_track(flac_path, track_data, track_index + 1, total_tracks)
