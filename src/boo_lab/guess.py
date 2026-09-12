from __future__ import annotations

import re
from pathlib import Path

GP5_ROOTS = [
    Path(r"C:\Users\RIGGUSPIG\Desktop\god-tier-metal\reference\gp-tabs\gp5"),
    Path(r"C:\Users\RIGGUSPIG\Desktop\god-tier-metal\reference\gp-tabs"),
    Path(r"C:\Users\RIGGUSPIG\Desktop\god-tier-metal\reference"),
]


def _norm(s: str) -> str:
    s = (s or "").lower().replace("∆", "a").replace("Δ", "a")
    s = re.sub(r"^\d+\s*[-_.]\s*", "", s)
    return re.sub(r"[^a-z0-9]+", "", s)


def _prefer_gp5(gp: Path | None, track: str) -> Path | None:
    cands: list[Path] = []
    if gp:
        p = Path(gp)
        if p.suffix.lower() == ".gp5" and p.exists():
            return p
        sib = p.with_suffix(".gp5")
        if sib.exists():
            cands.append(sib)
        if p.exists() and p.suffix.lower() == ".gp5":
            cands.append(p)
    key = _norm(track)
    if not key and gp:
        # "Born_Of_Osiris-Recreate-s77727" -> recreate
        raw = _norm(Path(gp).stem)
        raw = re.sub(r"^bornofosiris", "", raw)
        raw = re.sub(r"s\d+$", "", raw)
        key = raw
    if key:
        for root in GP5_ROOTS:
            if not root.exists():
                continue
            try:
                hits = list(root.rglob("*.gp5"))
            except Exception:
                continue
            for hit in hits:
                n = _norm(hit.stem)
                if n == key or key in n or n in key:
                    cands.append(hit)
    for c in cands:
        if c.exists() and c.suffix.lower() == ".gp5":
            return c
    return None


def estimate_hybrid(flac: Path | None, gp: Path | None, track: str = "") -> dict:
    notes: list[str] = []
    sections: list[dict] = []
    bpm = None
    beats: list[float] = []

    gp_use = _prefer_gp5(gp, track)
    key = _norm(track) or _norm(gp.stem if gp else "")
    seen = 0
    root0 = GP5_ROOTS[0]
    if root0.exists():
        seen = sum(1 for _ in root0.rglob("*.gp5"))
    notes.append("key=%s gp5=%s files=%s" % (key or "?", root0, seen))
    if gp_use:
        notes.append("tab " + str(gp_use))
        try:
            from .extract import estimate_from_gp

            g = estimate_from_gp(gp_use)
            bpm = g.get("bpm") or bpm
            if g.get("sections"):
                sections.extend(g["sections"])
                notes.append("gp markers")
            else:
                notes.append(g.get("reason") or "tab has no markers")
        except Exception as e:
            notes.append("gp parse: %s" % e)
    else:
        notes.append("no tab")

    if flac and Path(flac).exists():
        try:
            m = _madmom_beats(Path(flac))
            beats = m.get("beats") or []
            if m.get("bpm"):
                bpm = m["bpm"]
            ht = _half_time_spans(beats)
            sections.extend(ht)
            if ht:
                notes.append("madmom half-time x%s" % len(ht))
            else:
                notes.append("madmom beats, no half-time stretch")
        except ImportError:
            notes.append("pip install madmom")
        except Exception as e:
            notes.append("madmom: %s" % e)

        if not sections:
            try:
                from .structure import run_allin1, segments_from_allin1

                raw = run_allin1(Path(flac))
                bpm = raw.get("bpm") or bpm
                for s in segments_from_allin1(raw):
                    sections.append(
                        {
                            "role": s.get("role") or "verse",
                            "start": float(s["start"]),
                            "end": float(s["end"]),
                            "source": "allin1",
                        }
                    )
                notes.append("allin1 changes")
            except ImportError:
                notes.append("allin1 not installed")
            except Exception as e:
                notes.append("allin1: %s" % e)

    sections = _clean(sections)
    return {"bpm": bpm, "beats": beats[:400], "sections": sections, "notes": notes}


def _madmom_beats(flac: Path) -> dict:
    from madmom.features.beats import DBNBeatTrackingProcessor, RNNBeatProcessor

    act = RNNBeatProcessor()(str(flac))
    beats = list(map(float, DBNBeatTrackingProcessor(fps=100)(act)))
    bpm = None
    if len(beats) > 8:
        gaps = [b - a for a, b in zip(beats, beats[1:]) if b > a]
        if gaps:
            mid = sorted(gaps)[len(gaps) // 2]
            if mid > 0:
                bpm = 60.0 / mid
    return {"beats": beats, "bpm": bpm}


def _half_time_spans(beats: list[float], min_len: float = 6.0) -> list[dict]:
    if len(beats) < 24:
        return []
    ioi = [b - a for a, b in zip(beats, beats[1:])]
    med = sorted(ioi)[len(ioi) // 2]
    if med <= 0:
        return []
    win = 8
    flags = []
    for i in range(len(ioi)):
        sl = ioi[max(0, i - win) : i + win]
        local = sorted(sl)[len(sl) // 2]
        flags.append(local > med * 1.65)
    out = []
    i = 0
    while i < len(flags):
        if not flags[i]:
            i += 1
            continue
        j = i
        while j < len(flags) and flags[j]:
            j += 1
        start = beats[i]
        end = beats[min(j, len(beats) - 1)]
        if end - start >= min_len:
            out.append(
                {
                    "role": "breakdown",
                    "start": round(start, 3),
                    "end": round(end, 3),
                    "source": "madmom-halftime",
                }
            )
        i = j
    return out


def _clean(sections: list[dict]) -> list[dict]:
    keep = []
    for s in sections:
        try:
            start = float(s["start"])
            end = float(s["end"])
        except Exception:
            continue
        if end <= start:
            continue
        keep.append({**s, "start": start, "end": end})
    keep.sort(key=lambda x: (x["start"], x["end"]))
    return keep
