# Status (2026-09-12)

Lab for Born of Osiris-shaped section labels. Not the generator. Not a songwriter.

## Truth sources (in order)

1. Human boxes on the FLAC (sections.jsonl)
2. GP5 rehearsal markers when they exist
3. Ear. Do not wait on madmom/allin1.

GP7 `.gp` (Songsterr `s77727` etc.) is not a tab for Guess. Keys-only tracks (Rebirth, A Solution, The Omniscient) have no guitar tab — Pulse/Chill by ear.

## Roles

Intro, Build, Riff, Hook, Breakdown, Solo, Chill, Pulse, Outro.

- Same guitar looping = one Riff box
- Guitar stays, drums half-time = Riff + Breakdown on the same seconds
- Different roles may overlap. Two of the same role on the same span = merge or split
- Pulse = synth/techno clock, not a chug
- Chill = clean / pads

## UI

- Whole left column scrolls
- Green = GP5, gold = partial GP5, grey = no tab
- Blue slider = seek/play
- Boxes = drag / retag. Role dropdown must not rebuild the row
- Save writes `data/sections.jsonl`. Download JSON is the backup
- Human rows beat Guess when both exist

## Paths on Wyatt's PC

```
FLAC  C:\Users\RIGGUSPIG\Desktop\god-tier-metal\reference\audio-corpus\born_of_osiris
GP5   C:\Users\RIGGUSPIG\Desktop\god-tier-metal\reference\gp-tabs\gp5
LAB   C:\Users\RIGGUSPIG\Desktop\god-tier-metal\tools\boo-lab
```

Start (after venv exists):

```
...\tools\boo-lab\.venv\Scripts\activate
set BOO_FLAC_ROOT=C:\Users\RIGGUSPIG\Desktop\god-tier-metal\reference\audio-corpus\born_of_osiris
set BOO_GP_ROOT=C:\Users\RIGGUSPIG\Desktop\god-tier-metal\reference\gp-tabs
boo-lab studio --port 8765
```

Then Ctrl+F5. Kill the old server before starting another.

SETUP-STUDIO.bat can fight pip (setuptools 84 vs madmom). Prefer the commands above once the venv works.

## Guess

1. GP5 markers under `gp-tabs\gp5`
2. Demucs drums stem on first Guess (`work/stems/`, cached)
3. librosa half-time on that stem → Breakdown drafts

`INSTALL-STEMS.bat` once. Waveform is wavesurfer.js 7. No madmom.

## ML later

10k deathcore FLACs = tone. Labels + GP5 windows = form. Do not train a song model on raw mixed FLACs. Keep audio/tabs off git.

## Sister repos

- `z2wgv7dc4h-alt/boo-lab` — this repo
- `z2wgv7dc4h-alt/1222` — generator (god-tier-metal). Do not edit Ww from here.
- Ww / 123 — archived

## Do not

- Commit `.venv`, `.env`, FLACs, GP files, zips, tokens
- Scrape Songsterr
- Treat Guess as ground truth
- Chop every riff repeat
