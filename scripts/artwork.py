#!/usr/bin/env python3
"""
Embed artwork into FLAC files.
"""
import sys
import requests
from pathlib import Path
from io import BytesIO
from mutagen.flac import FLAC, Picture
from PIL import Image


def embed_artwork(flac_path, artwork_source):
    """
    Embed artwork into a FLAC file.

    Args:
        flac_path: Path to the FLAC file
        artwork_source: URL or local path to the artwork image
    """
    flac_path = Path(flac_path)
    artwork_source = str(artwork_source)

    # Load image data
    if artwork_source.startswith(('http://', 'https://')):
        print(f"Downloading artwork from {artwork_source}")
        response = requests.get(artwork_source, timeout=10)
        response.raise_for_status()
        image_data = response.content
    else:
        with open(artwork_source, 'rb') as f:
            image_data = f.read()

    # Load and resize image to 500x500
    image = Image.open(BytesIO(image_data))
    image = image.resize((500, 500), Image.Resampling.LANCZOS)

    # Convert to PNG for embedding
    png_buffer = BytesIO()
    image.save(png_buffer, format='PNG')
    png_buffer.seek(0)
    png_data = png_buffer.read()

    # Load FLAC and embed picture
    audio = FLAC(str(flac_path))

    picture = Picture()
    picture.data = png_data
    picture.type = 3  # FRONT_COVER
    picture.mime = 'image/png'
    picture.width = 500
    picture.height = 500
    picture.depth = 24
    picture.colors = 0

    audio.add_picture(picture)
    audio.save()

    print(f"Embedded artwork in: {flac_path}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <flac_path> <artwork_url_or_path>")
        sys.exit(1)

    flac_path = sys.argv[1]
    artwork_source = sys.argv[2]

    embed_artwork(flac_path, artwork_source)
