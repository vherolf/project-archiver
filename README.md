# project-archiver

Archives a project folder to a new location. Non-video files are copied as-is. Video files are re-encoded to H.265 before copying, preserving the original directory structure.

## What it does

```
source/my_project/
├── notes.txt          →  copied as-is
├── edit.prproj        →  copied as-is
└── footage/
    ├── clip_01.mts    →  compressed to H.265  →  clip_01.mp4
    └── clip_02.mp4    →  compressed to H.265  →  clip_02.mp4
```

Result lands at `destination/my_project/` — the source folder name is always preserved.

---

## Install (pre-built binary)

```bash
curl -L https://github.com/vherolf/project-archiver/releases/latest/download/project-archiver \
  -o ~/.local/bin/project-archiver && chmod +x ~/.local/bin/project-archiver
```

Then run it directly:

```bash
project-archiver -s ./projects/tet -d ~/Desktop/archive
```

> The binary still requires **ffmpeg** and **libmagic** to be installed on the system — see [System dependencies](#system-dependencies).

---

## System dependencies

| Tool | Purpose | Install |
|---|---|---|
| `ffmpeg` | Video compression | `sudo apt install ffmpeg` |
| `libmagic1` | MIME type detection | `sudo apt install libmagic1` |

macOS:

```bash
brew install ffmpeg libmagic
```

---

## Usage

```bash
project-archiver -s <source> -d <destination> [--crf <value>]
```

| Flag | Description |
|---|---|
| `-s`, `--source_directory` | Project folder to archive (required) |
| `-d`, `--destination_directory` | Parent folder for the archive (required) |
| `--crf` | H.265 quality, 0–51, lower = better (default: `28`) |

### Example

```bash
project-archiver -s ./projects/tet -d ~/Desktop/archive
```

Creates `~/Desktop/archive/tet/` with the full internal structure preserved.

### CRF guide

| CRF | Quality |
|---|---|
| 18–22 | High quality, larger files |
| 28 | Default — good balance |
| 32–38 | Smaller files, visible loss |

---

## Run from source

```bash
git clone https://github.com/vherolf/project-archiver.git
cd project-archiver
pip install -r requirements.txt
python project-archiver.py -s <source> -d <destination>
```

---

## Build a binary

```bash
pip install -r requirements-dev.txt
./build.sh
```

Output binary: `dist/project-archiver`

The script locates `libmagic.so` on the current system and bundles it into the binary. Requires `libmagic1` to be installed before building.

Upload `dist/project-archiver` to a GitHub release to make the curl install oneliner work.

---

## Output

```
Source:      /home/user/projects/tet
Destination: /home/user/Desktop/archive/tet
Video CRF:   28 (H.265)

  [COPY]  notes.txt
  [COPY]  edit.prproj
  [VIDEO] clip_01.mts
  [VIDEO] clip_02.mp4

Done: 2 videos compressed, 2 files copied, 0 errors

--- Statistics ---
Source:      4 files  4.2 GB
Destination: 4 files  1.1 GB
Size saved:  73.8%
```

A log of every operation is written to `project-archiver.log` next to the script.

---

## Video detection

Detection uses two layers so formats like AVCHD are handled correctly:

1. **MIME type** via `libmagic` — fast, covers standard containers
2. **ffprobe stream inspection** — fallback for formats libmagic misidentifies (AVCHD `.mts`/`.m2ts`, MPEG-TS, VOB, etc.)
