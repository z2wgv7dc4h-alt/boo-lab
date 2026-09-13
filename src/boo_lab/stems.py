from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def find_drums(flac: Path, cache: Path) -> Path | None:
    name = flac.stem
    for model in ("htdemucs", "htdemucs_ft", "mdx_extra", "mdx_extra_q"):
        p = cache / model / name / "drums.wav"
        if p.exists():
            return p
    near = [
        flac.parent / "stems" / (name + ".drums.wav"),
        flac.parent / "stems" / "drums.wav",
        flac.parent / (name + ".drums.wav"),
    ]
    for p in near:
        if p.exists():
            return p
    return None


def run_demucs(
    flac: Path,
    out_dir: Path,
    model: str = "htdemucs",
    two_stems: str = "drums",
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, "-m", "demucs", "-n", model, "-o", str(out_dir)]
    if two_stems:
        cmd += ["--two-stems", two_stems]
    cmd.append(str(flac))
    subprocess.run(cmd, check=True, timeout=900)
    return out_dir / model / flac.stem


def ensure_drums(flac: Path, cache: Path) -> tuple[Path | None, str]:
    hit = find_drums(flac, cache)
    if hit:
        return hit, "cached drums"
    try:
        import demucs  # noqa: F401
    except ImportError:
        return None, "pip install demucs"
    try:
        run_demucs(flac, cache)
    except Exception as e:
        return None, "demucs: %s" % e
    hit = find_drums(flac, cache)
    return hit, "demucs drums" if hit else "demucs wrote nothing"
