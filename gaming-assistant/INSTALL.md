# Altantis HUD — Gaming Assistant

Sci-fi HUD overlay that watches your screen while you game and pops up a
notification when it detects important information (codes, passwords, quest
objectives, coordinates, item stats, etc.).

---

## Quick Start

### Option A — Run from source (Python 3.11+)

```bat
pip install -r requirements.txt
python main.py
```

### Option B — Build a standalone .exe

```bat
build.bat
```

The compiled `AltantisHUD.exe` will be in the `dist\` folder.  
Double-click it — no Python required on the gaming machine.

---

## First Run

On first launch a setup dialog asks for your **Anthropic API key**.  
Get one at https://console.anthropic.com — paste it in and click Confirm.  
The key is saved locally (`~/.altantis_hud/config.json`) and never sent anywhere
except directly to the Anthropic API.

---

## How It Works

| Step | What happens |
|------|-------------|
| 1 | App sits silently in the **system tray** (bottom-right clock area) |
| 2 | Every **6 seconds** it takes a screenshot |
| 3 | If the screen changed significantly it sends it to **Claude vision AI** |
| 4 | Claude extracts codes, passwords, objectives, stats, etc. |
| 5 | A **HUD popup** appears bottom-right for **10 seconds** |
| 6 | Click **[ CONFIRM ]** or let the countdown expire to dismiss it |

---

## Tray Menu

Right-click the tray icon for:
- **Test Popup** — shows a demo popup to verify the UI is working
- **Exit** — closes the app

---

## Cost

Each screen analysis call uses approximately **~800–1200 tokens** with Claude.  
At current pricing that is roughly **$0.001–0.003 per popup**.  
The app only calls the API when it detects a significant screen change,
and enforces a 20-second cooldown after each popup fires.

---

## Sensitivity Tuning

In `monitor.py` you can adjust:

| Variable | Default | Effect |
|----------|---------|--------|
| `interval` | `6` seconds | How often to check the screen |
| `change_threshold` | `0.12` (12%) | How much the screen must change to trigger analysis |

Lower `change_threshold` = more sensitive (more API calls).  
Higher = misses subtle changes.
