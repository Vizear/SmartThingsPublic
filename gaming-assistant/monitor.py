"""Screen capture and change-detection background thread."""
import hashlib
import time
import io
import mss
from PIL import Image
from PyQt6.QtCore import QThread, pyqtSignal


def _capture_screen() -> Image.Image:
    with mss.mss() as sct:
        monitor = sct.monitors[0]  # all monitors combined
        raw = sct.grab(monitor)
        return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")


def _image_hash(img: Image.Image) -> str:
    small = img.resize((64, 36), Image.LANCZOS)
    buf = io.BytesIO()
    small.save(buf, "PNG")
    return hashlib.md5(buf.getvalue()).hexdigest()


class ScreenMonitor(QThread):
    info_detected = pyqtSignal(dict)  # emits parsed info dict from Claude

    def __init__(self, api_key: str, interval: int = 6, change_threshold: float = 0.12):
        super().__init__()
        self.api_key = api_key
        self.interval = interval          # seconds between captures
        self.change_threshold = change_threshold  # fraction of pixels changed
        self._running = False
        self._last_hash: str | None = None
        self._cooldown = 0  # don't re-trigger while popup is shown

    def set_cooldown(self, seconds: int):
        self._cooldown = seconds

    def stop(self):
        self._running = False

    def run(self):
        # Lazy import here so PyInstaller picks it up correctly
        from analyzer import analyze_screenshot

        self._running = True
        while self._running:
            time.sleep(self.interval)
            if self._cooldown > 0:
                self._cooldown -= self.interval
                continue
            try:
                img = _capture_screen()
                h = _image_hash(img)
                if self._last_hash is None:
                    self._last_hash = h
                    continue
                if h == self._last_hash:
                    continue
                # Simple change detection via pixel sampling
                changed = self._pixel_change_ratio(img)
                self._last_hash = h
                if changed < self.change_threshold:
                    continue
                # Significant change — ask Claude
                result = analyze_screenshot(img, self.api_key)
                if result:
                    self.info_detected.emit(result)
                    self._cooldown = 20  # suppress for 20s after firing
            except Exception:
                pass

    _prev_pixels: list | None = None

    def _pixel_change_ratio(self, img: Image.Image) -> float:
        import numpy as np
        small = img.resize((128, 72), Image.LANCZOS)
        arr = np.array(small, dtype=np.int16)
        if self._prev_pixels is None:
            self._prev_pixels = arr
            return 1.0
        diff = np.abs(arr.astype(np.int16) - self._prev_pixels).mean(axis=2)
        ratio = float((diff > 20).sum()) / diff.size
        self._prev_pixels = arr
        return ratio
