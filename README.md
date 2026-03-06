# Classical Mixtapes Pipeline

A system for building curated classical music mixtapes from YouTube Music, with proper FLAC tagging, gap insertion, and artwork embedding.

## Quick Start

```bash
cd /home/peter/mixtapes
source activate.sh

# Full pipeline (requires yt-dlp cookies)
python scripts/build.py mixtapes/shostakovich-7-noseda.yaml --cookies ~/.config/yt-dlp/cookies.txt
```

## Components

### Directory Structure
- **mixtapes/** - YAML mixtape definitions
- **scripts/** - Python pipeline scripts
- **output/** (git-ignored) - Built FLAC files and playlists
- **venv/** - Python virtual environment

### YAML Schema (mixtapes/*.yaml)

```yaml
title: "Descriptive title"
context: "serious|commute|both"
artwork: "https://example.com/image.jpg" or local path

tracks:
  - search_query: "Search term for YouTube Music"
    # OR
    # ytm_id: "dQw4w9WgXcQ"

    composer: "Composer Name"
    work: "Symphony No. X in Y"
    opus: "Op. XX"
    movement_number: 1
    movement_name: "Movement Name"
    conductor: "Conductor Name"
    ensemble: "Orchestra Name"
    year_recorded: 2020
    gap_after: 0          # Silence to insert after (seconds)
    interruptible: false  # Marks safe stopping points
```

### Scripts

#### gaps.py
Generate silent FLAC gap tracks.
```bash
python scripts/gaps.py 2.5 output/gap.flac
```

#### download.py
Download tracks from YouTube Music.
```bash
python scripts/download.py mixtapes/shostakovich-7-noseda.yaml
# Optional: with cookies
python scripts/download.py mixtapes/shostakovich-7-noseda.yaml --cookies ~/.config/yt-dlp/cookies.txt
```

#### tag.py
Tag individual FLAC files with classical metadata.
```bash
python scripts/tag.py <flac_path> mixtapes/shostakovich-7-noseda.yaml <track_index>
```

#### artwork.py
Embed artwork into FLAC files.
```bash
python scripts/artwork.py file.flac https://example.com/image.jpg
# Or local file
python scripts/artwork.py file.flac /path/to/image.png
```

#### build.py
Orchestrate the complete pipeline: download → tag → embed artwork → create playlist.
```bash
python scripts/build.py mixtapes/shostakovich-7-noseda.yaml --cookies ~/.config/yt-dlp/cookies.txt
```

Options:
- `--cookies <path>` - Path to yt-dlp cookies file
- `--output <dir>` - Base output directory (default: ./output)

## Workflow

1. **Create YAML file** in `mixtapes/` with tracks and metadata
2. **Get yt-dlp cookies** - Log into YouTube Music, export cookies via browser extension
3. **Run build pipeline**:
   ```bash
   python scripts/build.py mixtapes/your-mixtape.yaml --cookies ~/cookies.txt
   ```
4. **Output** - Creates `output/your-mixtape/` with:
   - `tracks/` - Individual tagged FLAC files with embedded artwork
   - `playlist.m3u` - M3U playlist for all tracks
5. **Sync to phone** - Automatically via Syncthing (see below)

## Phone Sync via Syncthing

The Pi runs Syncthing for automatic syncing to your phone. New mixtapes appear on your device within seconds of building them.

**Syncthing Web UI:**
- **Tailscale**: `http://100.127.158.37:8384`
- **Local Network**: `http://192.168.4.71:8384`

**Pi Device ID:**
```
L4MV7PP-QBBOHWD-QEAV5EC-NLW3KY5-JXE3LMY-PD6UIZX-SEZHRU7-GNQAOAQ
```

**Setup on Phone:**
1. Install Syncthing (iPhone App Store / Android Play Store)
2. Add device using Pi's Device ID (scan QR code in web UI or paste manually)
3. Accept pairing request in Syncthing web UI on Pi
4. Select "Classical Mixtapes" folder to sync
5. Set phone's sync path to a music-app-accessible location

**After pairing:**
- ✅ All FLACs sync automatically
- ✅ Playlist (`m3u`) available on phone
- ✅ Works over Tailscale VPN (anywhere)
- ✅ Works on local LAN (at home)

## Verification

### Check FLAC metadata
```bash
# View all tags
metaflac --list output/shostakovich-7-noseda/tracks/01-track.flac

# Or in Python
from mutagen.flac import FLAC
f = FLAC('output/shostakovich-7-noseda/tracks/01-track.flac')
print(f.tags)
```

### Verify playlist
```bash
# Open in VLC or similar
vlc output/shostakovich-7-noseda/playlist.m3u
```

## yt-dlp Cookies Setup

YouTube Music requires authentication. Get cookies:

1. Install browser extension (e.g., "Get cookies.txt" for Chrome/Firefox)
2. Log into music.youtube.com
3. Export cookies to file
4. Pass to build.py: `--cookies ~/Downloads/cookies.txt`

Without cookies, searches may fail or return age-restricted content.

## Requirements

Installed in venv:
- yt-dlp - YouTube downloader
- mutagen - FLAC tagging
- Pillow - Image processing
- PyYAML - YAML parsing

System dependencies:
- ffmpeg - Audio processing (for gap generation)
- metaflac (optional) - Verify FLAC tags

Install system ffmpeg:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg
```

## Examples

See `mixtapes/shostakovich-7-noseda.yaml` for a complete example with 4 movements.

## Troubleshooting

**Error: "yt-dlp: command not found"**
- Ensure venv is activated: `source activate.sh`

**Error: "ffmpeg: command not found"**
- Install ffmpeg system-wide (see Requirements)

**Error: "Private video" or "Age restricted"**
- yt-dlp needs authentication via cookies

**No duration info in playlist**
- mutagen.flac.FLAC() couldn't read duration; check FLAC file validity

**Poor artwork quality**
- Artwork is resized to 500x500 for embedding; source should be high-res

## Next Mixtapes

After Shostakovich, create new YAMLs for other works in `mixtapes/` directory, then run:
```bash
python scripts/build.py mixtapes/your-mixtape.yaml --cookies ~/cookies.txt
```
