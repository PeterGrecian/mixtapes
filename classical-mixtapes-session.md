# Classical Mixtapes Project — Session Notes
## Friday 6 March 2026

---

## The Problem with YouTube Music

- Gapless playback unsuitable for classical (no configurable gap)
- Poor metadata (no composer/opus/conductor fields)
- No offline playlist creation
- No official API — unofficial Python library: `ytmusicapi` (sigma67, PyPI, MIT)

---

## Requirements

- Configurable silence between tracks (not crossfade — positive gap)
- Proper classical metadata: composer, opus, conductor, work, movement
- Offline playlists
- "Mixtapes" with gap tracks where necessary
- Artwork embedded
- Reflects two listening contexts: **commuting** and **serious listening**

---

## Pipeline

```
YAML files (curation: tracks, gaps, artwork, context)
  → yt-dlp  — download audio as FLAC from YTM
  → mutagen — tag with classical metadata
  → ffmpeg  — generate silent gap tracks to exact duration
  → Pillow  — embed artwork
  → export as folder + M3U playlist
  → Syncthing (or USB) — sync to phone over WiFi
  → Poweramp — play locally on Android
```

All driven by Python scripts. YAML is the curation layer.

---

## Key Decisions

### Why not stream?
- OuterTune (the best YTM Android client) is dropping YTM support (issue #1116 — dev lost interest)
- YTM Innertube API fragile, periodically broken by Google
- Downloaded YTM tracks are DRM-locked, useless outside YTM app
- Owning FLAC files = no dependency on Google's goodwill

### Why not a webapp?
- YAML files + Python scripts are sufficient
- Simpler, version-controlled, scriptable

### Gap tracks
- Insert actual short silent FLAC files between movements/works
- Duration specified in YAML per track/work
- Works in any player forever — no player-specific features needed
- ffmpeg generates them trivially

---

## Tools

| Tool | Purpose |
|------|---------|
| `yt-dlp` | Download FLAC from YTM |
| `ytmusicapi` | Search YTM catalogue, get metadata |
| `mutagen` | Tag FLAC files (classical schema) |
| `ffmpeg` | Generate silent gap tracks |
| `Pillow` | Artwork embedding |
| Syncthing | Wireless sync to Android (F-Droid) |
| Poweramp | Android playback (~£4, Play Store) |

---

## Android Player: Poweramp

- Best-in-class FLAC handling
- Configurable gap in milliseconds (makes silent gap tracks optional)
- Excellent M3U playlist support
- Closed source, Play Store only (not F-Droid)
- Free trial available

Alternatives considered: Musicolet (free, no internet permission, multiple queues),
Vanilla Music (FOSS, F-Droid, lightweight but feature-light)

---

## Android App Landscape (for reference)

- **ViMusic** → original FOSS YTM Android client
- **InnerTune** (z-huang) → forked from ViMusic, Material 3, still maintained with YTM
- **OuterTune** → forked from InnerTune, added local files + YTM sync
  - v0.10.x: last YTM-supporting branch, no further updates
  - v0.11.x: active, local-only
  - Issue #1116: dev dropped YTM, pivoting to local/Navidrome
- **Syncthing**: peer-to-peer folder sync, no cloud, E2E encrypted, F-Droid

---

## GitHub Repo Structure

```
classical-mixtapes/
├── mixtapes/
│   └── shostakovich-7-noseda.yaml   ← first example to build
├── scripts/
│   ├── download.py     # yt-dlp wrapper
│   ├── tag.py          # mutagen tagging
│   ├── gaps.py         # ffmpeg silent track generator
│   ├── artwork.py      # embed artwork
│   └── build.py        # orchestrates full pipeline
├── output/             # .gitignore this — FLAC files land here
└── README.md
```

YAMLs are the curation record — human readable, diffable, committed.
FLAC output is gitignored (large, reproducible from YAML via yt-dlp).

---

## Next Steps

1. `git init classical-mixtapes` on WSL
2. Draft YAML schema using Shostakovich Symphony No. 7
   conducted by Gianandrea Noseda as the first example
3. Build `download.py` around yt-dlp
4. Build `gaps.py` around ffmpeg
5. Build `tag.py` around mutagen
6. Wire together in `build.py`
7. Install Syncthing on server + Android
8. Install Poweramp, point at synced folder

---

## YAML Schema (to design)

Fields needed:
- `title` — mixtape name
- `context` — commute | serious | both
- `artwork` — path or URL
- `tracks[]`:
  - `ytm_id` or `search_query`
  - `composer`
  - `work`
  - `opus`
  - `movement` (number + name)
  - `conductor`
  - `performer` / `ensemble`
  - `year_recorded`
  - `gap_after` (seconds — 0 for gapless, n for silence)
  - `interruptible` (bool — for commute context)

First example: **Shostakovich Symphony No. 7 "Leningrad", Noseda**
