import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import magic  # pip install python-magic

PWD = Path(__file__).parent.resolve()
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=Path(PWD, "project-archiver.log"),
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)


@dataclass
class Project:
    name: str = ""
    videos: int = 0
    nonvideos: int = 0
    errors: int = 0

    def total_files(self) -> int:
        return self.videos + self.nonvideos


def _check_ffmpeg():
    for tool in ("ffmpeg", "ffprobe"):
        result = subprocess.run([tool, "-version"], capture_output=True)
        if result.returncode != 0:
            raise RuntimeError(f"{tool} not found — install ffmpeg before running this tool")


def _has_video_stream(file_path: Path) -> bool:
    # ffprobe returns "video" on stdout when a video stream exists
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_type",
            "-of", "csv=p=0",
            str(file_path),
        ],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "video"


def _is_video(file_path: Path) -> bool:
    mime = magic.Magic(mime=True)
    if mime.from_file(str(file_path)).startswith("video"):
        return True
    # libmagic misidentifies some formats (AVCHD .mts/.m2ts, MPEG-TS, VOB, etc.)
    # as application/octet-stream — fall back to ffprobe stream inspection
    return _has_video_stream(file_path)


def _compress_video(src: Path, dst: Path, crf: int) -> Path:
    # H.265 output always in .mp4 container
    dst = dst.with_suffix(".mp4")
    dst.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["ffmpeg", "-i", str(src), "-vcodec", "libx265", "-crf", str(crf), "-y", str(dst)],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode(errors="replace").strip())
    return dst


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _human_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _dir_stats(path: Path) -> tuple[int, int]:
    files = [f for f in path.rglob("*") if f.is_file()]
    return len(files), sum(f.stat().st_size for f in files)


def archive_project(source: Path, destination: Path, crf: int = 28, dry_run: bool = False) -> Project:
    project = Project(name=source.name)

    for root, _, files in os.walk(source):
        root_path = Path(root)
        rel = root_path.relative_to(source)

        for file in files:
            src_file = root_path / file
            dst_file = destination / rel / file

            try:
                if _is_video(src_file):
                    out = dst_file.with_suffix(".mp4")
                    print(f"  [VIDEO] {src_file}  ->  {out}")
                    if not dry_run:
                        out = _compress_video(src_file, dst_file, crf)
                        logger.info("compressed video: %s -> %s", src_file, out)
                    project.videos += 1
                else:
                    print(f"  [COPY]  {src_file}  ->  {dst_file}")
                    if not dry_run:
                        _copy_file(src_file, dst_file)
                        logger.info("copied: %s -> %s", src_file, dst_file)
                    project.nonvideos += 1
            except Exception as exc:
                project.errors += 1
                print(f"  [ERROR] {src_file.name}: {exc}")
                logger.error("failed %s: %s", src_file, exc)

    return project


def statistics(source: Path, destination: Path) -> None:
    src_count, src_size = _dir_stats(source)
    dst_count, dst_size = _dir_stats(destination)
    reduction = (1 - dst_size / src_size) * 100 if src_size else 0

    print("\n--- Statistics ---")
    print(f"Source:      {src_count} files  {_human_size(src_size)}")
    print(f"Destination: {dst_count} files  {_human_size(dst_size)}")
    if reduction > 0:
        print(f"Size saved:  {reduction:.1f}%")


def main(source_directory: str, destination_directory: str, crf: int = 28, dry_run: bool = False) -> None:
    source = Path(source_directory).expanduser().resolve()
    destination = Path(destination_directory).expanduser().resolve() / source.name

    if not source.exists():
        print(f"Error: source '{source}' does not exist")
        return

    _check_ffmpeg()

    print(f"Source:      {source}")
    print(f"Destination: {destination}")
    print(f"Video CRF:   {crf} (H.265)")
    if dry_run:
        print("Mode:        DRY RUN — no files will be written")
    print()
    logger.info("started%s: %s -> %s", " (dry-run)" if dry_run else "", source, destination)

    if not dry_run:
        destination.mkdir(parents=True, exist_ok=True)

    project = archive_project(source, destination, crf, dry_run)

    verb = "would compress" if dry_run else "compressed"
    prefix = "(dry-run) " if dry_run else ""
    print(
        f"\n{prefix}{project.videos} videos {verb}, "
        f"{project.nonvideos} files {'would copy' if dry_run else 'copied'}, "
        f"{project.errors} errors"
    )
    logger.info("finished%s: %s", " (dry-run)" if dry_run else "", project)

    if not dry_run:
        statistics(source, destination)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Archive a project: copy non-video files as-is, compress videos with H.265"
    )
    parser.add_argument("-s", "--source_directory", required=True, help="Source project directory")
    parser.add_argument("-d", "--destination_directory", required=True, help="Destination archive directory")
    parser.add_argument("--crf", type=int, default=28, help="H.265 CRF quality (lower = better, default 28)")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Show what would be done without writing any files")
    args = parser.parse_args()

    main(args.source_directory, args.destination_directory, args.crf, args.dry_run)
