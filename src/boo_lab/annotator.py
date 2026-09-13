from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .catalogue import load_map, resolve

ROLES = [
    "intro",
    "build",
    "verse",
    "chorus",
    "breakdown",
    "solo",
    "interlude",
    "chill",
    "outro",
]


def create_app(lab_root: Path, flac_root: Path | None, gp_root: Path | None) -> FastAPI:
    app = FastAPI(title="boo-lab annotator")
    static = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static), name="static")
    map_path = lab_root / "data" / "map.csv"
    sec_path = lab_root / "data" / "sections.jsonl"

    def _norm_name(s: str) -> str:
        import re
        s = (s or "").lower().replace("∆", "a").replace("Δ", "a")
        s = re.sub(r"^\d+\s*[-_.]\s*", "", s)
        return re.sub(r"[^a-z0-9]+", "", s)

    def _gp5_index() -> dict[str, Path]:
        idx: dict[str, Path] = {}
        root = Path(r"C:\Users\RIGGUSPIG\Desktop\god-tier-metal\reference\gp-tabs\gp5")
        if not root.exists():
            return idx
        try:
            for p in root.rglob("*.gp5"):
                idx[_norm_name(p.stem)] = p
        except Exception:
            return idx
        return idx

    def tracks():
        if not map_path.exists():
            return []
        try:
            rows = [resolve(r, flac_root, gp_root) for r in load_map(map_path)]
        except Exception:
            return []
        idx = _gp5_index()
        out = []
        for i, r in enumerate(rows):
            key = _norm_name(r.get("track") or "")
            gp5 = idx.get(key)
            if not gp5 and key:
                for k, p in idx.items():
                    if key in k or k in key:
                        gp5 = p
                        break
            notes = (r.get("notes") or "").lower()
            partial = False
            if gp5:
                name = gp5.name.lower()
                try:
                    sz = gp5.stat().st_size
                except Exception:
                    sz = 0
                partial = (
                    sz < 22000
                    or "stub" in notes
                    or "fragment" in notes
                    or "partial" in notes
                    or ("bass" in name and "guitar" not in name)
                )
            flac_ok = False
            fp = r.get("flac_path") or r.get("flac")
            if fp:
                try:
                    flac_ok = Path(fp).exists()
                except Exception:
                    flac_ok = False
            if not flac_ok and flac_root and flac_root.exists() and key:
                try:
                    for p in flac_root.rglob("*"):
                        if p.suffix.lower() in {".flac", ".wav"} and _norm_name(p.stem) == key:
                            r["flac_path"] = str(p)
                            fp = str(p)
                            flac_ok = True
                            break
                except Exception:
                    pass
            out.append(
                {
                    "id": i,
                    "album": r.get("album"),
                    "track": r.get("track"),
                    "tuning": r.get("tuning"),
                    "has_flac": flac_ok,
                    "has_gp": bool(gp5),
                    "gp_partial": partial,
                    "gp_name": gp5.name if gp5 else "",
                    "gp_kind": (gp5.suffix.lower().lstrip(".") if gp5 else ""),
                }
            )
        out.sort(key=lambda t: ((t.get("album") or ""), t.get("track") or ""))
        return out

    @app.get("/", response_class=HTMLResponse)
    def index():
        return (static / "annotator.html").read_text(encoding="utf-8")

    @app.get("/api/tracks")
    def api_tracks():
        return {"roles": ROLES, "tracks": tracks()}

    @app.get("/api/audio/{track_id}")
    def api_audio(track_id: int):
        rows = [resolve(r, flac_root, gp_root) for r in load_map(map_path)]
        if track_id < 0 or track_id >= len(rows):
            raise HTTPException(404)
        path = rows[track_id].get("flac_path")
        if not path or not Path(path).exists():
            raise HTTPException(404, "flac missing — set BOO_FLAC_ROOT and map.csv")
        return FileResponse(path, media_type="audio/flac")

    @app.get("/api/tab/{track_id}")
    def api_tab(track_id: int):
        rows = [resolve(r, flac_root, gp_root) for r in load_map(map_path)]
        if track_id < 0 or track_id >= len(rows):
            raise HTTPException(404)
        from .guess import _prefer_gp5

        raw = rows[track_id].get("gp_path") or rows[track_id].get("gp") or ""
        gp5 = _prefer_gp5(Path(raw) if raw else None, rows[track_id].get("track") or "")
        path = gp5
        if not path and raw and Path(raw).exists():
            path = Path(raw)
        if not path:
            raise HTTPException(404, "no tab file")
        return FileResponse(path)

    @app.get("/api/drums/{track_id}")
    def api_drums(track_id: int):
        rows = [resolve(r, flac_root, gp_root) for r in load_map(map_path)]
        if track_id < 0 or track_id >= len(rows):
            raise HTTPException(404)
        flac = rows[track_id].get("flac_path")
        if not flac:
            raise HTTPException(404)
        from .stems import find_drums

        p = find_drums(Path(flac), lab_root / "work" / "stems")
        if not p:
            raise HTTPException(404, "no drums stem yet — press Guess")
        return FileResponse(p, media_type="audio/wav")

    @app.get("/api/estimate/{track_id}")
    def api_estimate(track_id: int):
        rows = [resolve(r, flac_root, gp_root) for r in load_map(map_path)]
        if track_id < 0 or track_id >= len(rows):
            raise HTTPException(404)
        flac = rows[track_id].get("flac_path")
        gp = rows[track_id].get("gp_path")
        from .guess import estimate_hybrid
        payload = estimate_hybrid(
            Path(flac) if flac else None,
            Path(gp) if gp else None,
            track=rows[track_id].get("track") or "",
            cache=lab_root / "work" / "stems",
        )
        return payload

    @app.get("/api/sections/{track_id}")
    def api_get_sections(track_id: int):
        meta = tracks()[track_id]
        found = []
        if sec_path.exists():
            for line in sec_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                rec = json.loads(line)
                if rec.get("album") == meta["album"] and rec.get("track") == meta["track"]:
                    found.append(rec)
        return found

    @app.post("/api/sections/{track_id}")
    async def api_save(track_id: int, request: Request):
        rows = tracks()
        if track_id < 0 or track_id >= len(rows):
            return JSONResponse({"detail": "bad track id", "saved": 0}, status_code=400)
        meta = rows[track_id]
        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"detail": "body not json", "saved": 0}, status_code=400)
        sections = body.get("sections") if isinstance(body, dict) else body
        if not isinstance(sections, list):
            return JSONResponse({"detail": "need sections list", "saved": 0}, status_code=400)
        old = []
        if sec_path.exists():
            for line in sec_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                rec = json.loads(line)
                if rec.get("album") == meta["album"] and rec.get("track") == meta["track"]:
                    continue
                old.append(rec)
        new = []
        for s in sections:
            try:
                start = float(s.get("start"))
                end = float(s.get("end"))
            except Exception:
                continue
            if end <= start:
                end = start + 0.25
            new.append(
                {
                    "album": meta["album"],
                    "track": meta["track"],
                    "start": start,
                    "end": end,
                    "role": s.get("role") or "verse",
                    "source": "human",
                }
            )
        sec_path.parent.mkdir(parents=True, exist_ok=True)
        with sec_path.open("w", encoding="utf-8") as f:
            for rec in old + new:
                f.write(json.dumps(rec) + "\n")
        try:
            from .learn import record

            record(lab_root, meta["album"], meta["track"], new)
        except Exception:
            pass
        return {"saved": len(new), "path": str(sec_path)}

    return app
