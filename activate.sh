#!/bin/bash
# Activate the mixtapes pipeline

cd "$(dirname "$0")" || exit
source venv/bin/activate
export PYTHONPATH="${PWD}/scripts:${PYTHONPATH}"
echo "✓ Mixtapes environment activated"
echo ""
echo "Usage:"
echo "  python scripts/gaps.py <duration> <output_path>       - Generate silent FLAC"
echo "  python scripts/download.py <yaml_path> [--cookies]    - Download tracks"
echo "  python scripts/tag.py <flac_path> <yaml_path> <idx>   - Tag FLAC file"
echo "  python scripts/artwork.py <flac_path> <artwork_src>   - Embed artwork"
echo "  python scripts/build.py <yaml_path> [--cookies <path>] - Full pipeline"
echo ""
