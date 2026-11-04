"""Render the share images from their sources with headless Chrome.

Writes assets/og-image.png (en), assets/og-image-ko.png (ko), both 1200x630, and
assets/apple-touch-icon.png (180x180). The sources are tools/og/og.html (read the
language from ?lang=) and the fish mark below, which is the editor's favicon.svg.
The pages need the web fonts, so this needs network access. GitHub Pages serves
the committed PNGs as they are; run this only when the sources change.

    python3 -I tools/og.py
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

# Full-bleed square of the favicon mark: iOS rounds the corners itself.
TOUCH = """<!doctype html><meta charset="utf-8"><style>html,body{margin:0;width:180px;height:180px;background:#18181b}svg{display:block;width:180px;height:180px}</style>
<svg viewBox="0 0 64 64" fill="none"><path d="M23 25C33 16 46 21 53 32C46 43 33 48 23 39L12 46V18L23 25Z" fill="#fafafa" transform="translate(32 32) scale(1.12) translate(-32 -32)"/><path d="M31 21L26 43" stroke="#18181b" stroke-width="4.5" stroke-linecap="round" transform="translate(32 32) scale(1.12) translate(-32 -32)"/><circle cx="43" cy="30" r="2.8" fill="#18181b" transform="translate(32 32) scale(1.12) translate(-32 -32)"/></svg>"""


def shot(url: str, out: Path, w: int, h: int) -> None:
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
           f"--window-size={w},{h}", "--virtual-time-budget=8000", f"--screenshot={out}", url]
    subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)


def main() -> None:
    if not Path(CHROME).exists():
        sys.exit(f"Chrome not found at {CHROME}. Set CHROME to a Chrome or Chromium binary.")
    page = (ROOT / "tools/og/og.html").as_uri()
    shot(f"{page}?lang=en", ROOT / "assets/og-image.png", 1200, 630)
    shot(f"{page}?lang=ko", ROOT / "assets/og-image-ko.png", 1200, 630)
    with tempfile.TemporaryDirectory() as d:
        touch = Path(d) / "touch.html"
        touch.write_text(TOUCH, encoding="utf-8")
        shot(touch.as_uri(), ROOT / "assets/apple-touch-icon.png", 180, 180)


if __name__ == "__main__":
    main()
