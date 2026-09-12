# boo-lab

Local lab: play Born of Osiris FLACs, mark Riff / Hook / Breakdown / Pulse, pull notes from GP5 you already own. Feeds God Tier Metal. Nothing leaves this PC.

Read `STATUS.md` before changing behaviour. Read `LAW.md` before adding features.

## Windows

```
set BOO_FLAC_ROOT=C:\Users\RIGGUSPIG\Desktop\god-tier-metal\reference\audio-corpus\born_of_osiris
set BOO_GP_ROOT=C:\Users\RIGGUSPIG\Desktop\god-tier-metal\reference\gp-tabs
Desktop\god-tier-metal\tools\boo-lab\.venv\Scripts\activate
boo-lab studio --port 8765
```

Or `SETUP-STUDIO.bat` / `START.bat`. Ctrl+F5 after every HTML change. Kill the old server first.

## Keys

Space play. Pin buttons add an 8s box at the playhead. S save. N next green. Slider seeks.

Green = GP5. Gold = partial tab. Grey = no tab.

## After an album

```
boo-lab extract --album "The Discovery"
boo-lab export-bank --out ..\god-tier-metal\engine\data\riff_bank.json
```

Do not add FLACs or GP files to git.
