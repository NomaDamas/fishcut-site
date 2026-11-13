"""Render the share images from their sources with headless Chrome.

Writes assets/og-image.png (en) and assets/og-image-ko.png (ko), both 1200x630. The
source is tools/og/og.html (read the language from ?lang=). The favicons and
assets/apple-touch-icon.png are not made here: they are resized from the app icon tools/og/app-icon-1024.png (copy of fishcut apps/desktop/build/icon.png, the same image as the TikTok app icon).
The pages need the web fonts, so this needs network access. GitHub Pages serves
the committed PNGs as they are; run this only when the sources change.

    python3 -I tools/og.py
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

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


if __name__ == "__main__":
    main()
