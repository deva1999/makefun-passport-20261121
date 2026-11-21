#!/usr/bin/env python3
"""Invented passport spread for a country that does not exist.

Pure standard library: renders a two-page passport spread (data page +
visa/stamp page) as a PNG and writes it to /output/entry.png.

The country is Veskara, a small highland wool-trading republic on a cold
northern coast. Its capital is Port Varra. The holder is Mara Selvig, a
registered wool trader. Every date on the spread agrees: the passport is
issued 14 FEB 2024 and every stamp falls after that date.
"""

import math
import os
import random
import struct
import zlib

OUT_PATH = "/output/entry.png"
W, H = 1024, 720

# ---------------------------------------------------------------- palette
PAPER = (242, 234, 216)
PAPER_DARK = (228, 218, 196)
INK = (28, 42, 52)
INK_SOFT = (58, 70, 78)
TEAL = (18, 84, 82)
TEAL_DARK = (10, 58, 60)
GOLD = (176, 138, 54)
GOLD_SOFT = (203, 168, 92)
RULE = (120, 110, 88)
STAMP_BLUE = (38, 74, 138)
STAMP_RED = (158, 44, 38)
STAMP_PURPLE = (96, 58, 128)
STAMP_GREEN = (34, 96, 58)
SKIN = (216, 178, 140)
SKIN_DARK = (196, 152, 114)
HAIR = (52, 36, 26)
JACKET = (24, 96, 92)
AMBER_BG = (214, 178, 118)

# ------------------------------------------------------------------- font
# A 5x7 bitmap font, authored here. Each glyph is 7 rows of 5 cells.
# Only capitals, digits and document punctuation are needed: a passport
# is set in capitals throughout, which keeps the type consistent.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}

CHAR_W = 6  # 5 pixels + 1 pixel tracking, before scaling


def text_width(s, scale, tight=False):
    adv = 5 if tight else CHAR_W
    return len(s) * adv * scale - scale


# ------------------------------------------------------------------ canvas
class Canvas:
    """A plain RGB canvas with small vector helpers and a bitmap font."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            return (self.px[i], self.px[i + 1], self.px[i + 2])
        return PAPER

    def blend(self, x, y, c, a):
        """Blend colour c over the pixel with alpha a (0..1)."""
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.px[i] = int(self.px[i] * (1 - a) + c[0] * a)
            self.px[i + 1] = int(self.px[i + 1] * (1 - a) + c[1] * a)
            self.px[i + 2] = int(self.px[i + 2] * (1 - a) + c[2] * a)

    def fill_rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = (yy * self.w + max(0, x)) * 3
            for xx in range(max(0, x), min(self.w, x + w)):
                i = base + (xx - max(0, x)) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.fill_rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill_rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.fill_rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c, t=1, fill=False):
        for yy in range(cy - r - 1, cy + r + 2):
            for xx in range(cx - r - 1, cx + r + 2):
                d = math.hypot(xx - cx, yy - cy)
                if fill:
                    if d <= r:
                        self.set(xx, yy, c)
                elif abs(d - r) <= t / 2 + 0.4:
                    self.set(xx, yy, c)

    def ellipse(self, cx, cy, rx, ry, c, fill=False, t=1):
        for yy in range(cy - ry - 1, cy + ry + 2):
            for xx in range(cx - rx - 1, cx + rx + 2):
                v = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
                if fill:
                    if v <= 1.0:
                        self.set(xx, yy, c)
                elif abs(v - 1.0) <= 0.09:
                    self.set(xx, yy, c)

    def poly(self, pts, c, fill=True):
        if not pts:
            return
        if fill:
            ys = [p[1] for p in pts]
            for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
                xs = []
                n = len(pts)
                for i in range(n):
                    x0, y0 = pts[i]
                    x1, y1 = pts[(i + 1) % n]
                    if (y0 <= y < y1) or (y1 <= y < y0):
                        xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
                xs.sort()
                for k in range(0, len(xs) - 1, 2):
                    for x in range(int(math.ceil(xs[k])), int(xs[k + 1]) + 1):
                        self.set(x, y, c)
        else:
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                self.line(x0, y0, x1, y1, c)

    def speckle(self, rng, n, colours, alpha=0.10):
        for _ in range(n):
            x = rng.randrange(self.w)
            y = rng.randrange(self.h)
            self.blend(x, y, rng.choice(colours), alpha)

    # ------------------------------------------------------------- text
    def draw_char(self, x, y, ch, scale, c):
        g = FONT.get(ch)
        if g is None:
            return
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits[col] == "1":
                    self.fill_rect(x + col * scale, y + row * scale,
                                   scale, scale, c)

    def text(self, x, y, s, scale, c, align="left", tight=False):
        s = s.upper()
        w = text_width(s, scale, tight)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        adv = 5 if tight else CHAR_W
        for i, ch in enumerate(s):
            self.draw_char(x + i * adv * scale, y, ch, scale, c)
        return w

    def blit_rotated(self, src, cx, cy, angle_deg, alpha=0.85):
        """Composite a small canvas rotated about (cx, cy)."""
        a = math.radians(angle_deg)
        ca, sa = math.cos(a), math.sin(a)
        hw, hh = src.w / 2.0, src.h / 2.0
        for yy in range(int(cy - hh - 4), int(cy + hh + 5)):
            for xx in range(int(cx - hw - 4), int(cx + hw + 5)):
                dx, dy = xx - cx, yy - cy
                sx = ca * dx + sa * dy + hw
                sy = -sa * dx + ca * dy + hh
                ix, iy = int(sx), int(sy)
                if 0 <= ix < src.w and 0 <= iy < src.h:
                    i = (iy * src.w + ix) * 3
                    r, g, b = src.px[i], src.px[i + 1], src.px[i + 2]
                    # The stamp canvas is painted on pure white; treat
                    # near-white as transparent.
                    if r > 245 and g > 245 and b > 245:
                        continue
                    self.blend(xx, yy, (r, g, b), alpha)


# --------------------------------------------------------------------- png
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------- MRZ check digits
_MRZ_VAL = {chr(ord("A") + i): 10 + i for i in range(26)}
_MRZ_VAL.update({str(i): i for i in range(10)})
_MRZ_VAL["<"] = 0


def mrz_check(s):
    total = 0
    for i, ch in enumerate(s):
        total += _MRZ_VAL[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def build_mrz():
    """ICAO 9303 two-line MRZ for Mara Selvig, computed, not typed."""
    doc = "VK482917<"
    personal = "<" * 14
    body = (
        doc + mrz_check(doc)
        + "VES"
        + "940312" + mrz_check("940312")
        + "F"
        + "340214" + mrz_check("340214")
        + personal + mrz_check(personal)
    )
    line1_name = "SELVIG<<MARA"
    line1 = ("P<VESK" + line1_name).ljust(44, "<")
    line2 = body + mrz_check(body)
    assert len(line1) == 44, len(line1)
    assert len(line2) == 44, len(line2)
    return line1, line2


# ------------------------------------------------------------- the portrait
def draw_portrait(cv, x, y, w, h):
    """A stylised geometric portrait of Mara Selvig, drawn by code.

    High-collared teal jacket, dark braided hair, amber studio backdrop:
    the dress of a highland wool trader of Veskara, not a generic face.
    """
    # Backdrop: warm amber bands, like a studio portrait card.
    cv.fill_rect(x, y, w, h, AMBER_BG)
    cv.fill_rect(x, y, w, h // 3, (226, 196, 140))
    cv.fill_rect(x, y + 2 * h // 3, w, h // 3, (196, 158, 100))
    cx = x + w // 2
    # Shoulders and high collar jacket.
    cv.poly([(x + 8, y + h), (cx - 52, y + h - 62), (cx - 30, y + h - 96),
             (cx + 30, y + h - 96), (cx + 52, y + h - 62),
             (x + w - 8, y + h)], JACKET)
    # Woven zigzag band across the chest.
    for i in range(6):
        bx = x + 14 + i * 20
        cv.poly([(bx, y + h - 34), (bx + 10, y + h - 46),
                 (bx + 20, y + h - 34), (bx + 10, y + h - 22)],
                GOLD_SOFT)
    # Collar: two upright flaps framing the neck.
    cv.poly([(cx - 30, y + h - 96), (cx - 14, y + h - 118),
             (cx - 6, y + h - 96)], TEAL_DARK)
    cv.poly([(cx + 30, y + h - 96), (cx + 14, y + h - 118),
             (cx + 6, y + h - 96)], TEAL_DARK)
    # Small round brooch: a mountain star of Veskara.
    cv.circle(cx, y + h - 52, 7, GOLD, fill=True)
    cv.poly([(cx, y + h - 59), (cx + 3, y + h - 52),
             (cx, y + h - 45), (cx - 3, y + h - 52)], PAPER)
    # Neck.
    cv.fill_rect(cx - 11, y + h - 122, 22, 30, SKIN_DARK)
    # Head.
    cv.ellipse(cx, y + 62, 34, 42, SKIN, fill=True)
    # Hair: cap over the crown, side falls and two braids.
    cv.poly([(cx - 36, y + 66), (cx - 34, y + 18), (cx - 12, y + 4),
             (cx + 12, y + 4), (cx + 34, y + 18), (cx + 36, y + 66),
             (cx + 26, y + 58), (cx + 20, y + 22), (cx - 20, y + 22),
             (cx - 26, y + 58)], HAIR)
    cv.poly([(cx - 36, y + 60), (cx - 30, y + 96), (cx - 22, y + 96),
             (cx - 26, y + 58)], HAIR)
    cv.poly([(cx + 36, y + 60), (cx + 30, y + 96), (cx + 22, y + 96),
             (cx + 26, y + 58)], HAIR)
    # Braid bands.
    for by in (y + 74, y + 86):
        cv.fill_rect(cx - 31, by, 10, 3, GOLD_SOFT)
        cv.fill_rect(cx + 21, by, 10, 3, GOLD_SOFT)
    # Brows, eyes, nose, mouth: calm, straight at the camera.
    cv.line(cx - 24, y + 52, cx - 8, y + 50, HAIR, 2)
    cv.line(cx + 8, y + 50, cx + 24, y + 52, HAIR, 2)
    cv.ellipse(cx - 16, y + 60, 7, 4, (250, 246, 238), fill=True)
    cv.ellipse(cx + 16, y + 60, 7, 4, (250, 246, 238), fill=True)
    cv.ellipse(cx - 16, y + 60, 3, 3, (30, 26, 22), fill=True)
    cv.ellipse(cx + 16, y + 60, 3, 3, (30, 26, 22), fill=True)
    cv.line(cx, y + 62, cx - 2, y + 76, SKIN_DARK, 2)
    cv.line(cx - 9, y + 88, cx + 9, y + 88, (146, 84, 66), 2)
    # Cheek shading.
    cv.ellipse(cx - 24, y + 76, 6, 4, (222, 168, 128), fill=True)
    cv.ellipse(cx + 24, y + 76, 6, 4, (222, 168, 128), fill=True)


# ------------------------------------------------------------------ stamps
def make_stamp(lines, colour, shape="circle", w=150, h=110):
    """Render one ink stamp onto its own small canvas (white = clear)."""
    st = Canvas(w, h, (255, 255, 255))
    cx, cy = w // 2, h // 2
    if shape == "circle":
        st.circle(cx, cy, min(w, h) // 2 - 4, colour, t=3)
        st.circle(cx, cy, min(w, h) // 2 - 10, colour, t=1)
    else:
        st.ellipse(cx, cy, w // 2 - 4, h // 2 - 4, colour, t=3)
        st.ellipse(cx, cy, w // 2 - 10, h // 2 - 10, colour, t=1)
    n = len(lines)
    total = sum(7 * s for _, s in lines) + 4 * (n - 1)
    yy = cy - total // 2
    for txt, scale in lines:
        st.text(cx, yy, txt, scale, colour, align="center", tight=True)
        yy += 7 * scale + 4
    return st


def stamp_pair(cv, x, y, foreign, home, angle_f=-7, angle_h=6):
    """One journey row: foreign entry stamp + home return stamp."""
    cv.blit_rotated(foreign, x + 78, y + 52, angle_f)
    cv.blit_rotated(home, x + 78 + 168, y + 52, angle_h)


# -------------------------------------------------------------- guilloche
def guilloche(cv, x0, y0, x1, y1, colour, amp=3, waves=3, alpha=0.16):
    for row in range(4):
        yy0 = y0 + row * 7
        for x in range(x0, x1):
            yy = yy0 + int(amp * math.sin((x - x0) / 26.0 * waves))
            if y0 <= yy < y1:
                cv.blend(x, yy, colour, alpha)


# --------------------------------------------------------------- left page
def draw_left_page(cv):
    # Page frame.
    cv.rect(20, 20, 472, 680, TEAL, t=2)
    cv.rect(26, 26, 460, 668, RULE, t=1)
    # Coat of arms: roundel with three peaks and a star.
    ax, ay = 62, 58
    cv.circle(ax, ay, 26, TEAL, t=2)
    cv.circle(ax, ay, 21, GOLD, t=1)
    cv.poly([(ax - 14, ay + 10), (ax - 6, ay - 6), (ax, ay + 4),
             (ax + 6, ay - 10), (ax + 14, ay + 10)], TEAL)
    cv.poly([(ax, ay - 15), (ax + 2, ay - 10), (ax - 2, ay - 10)], GOLD)
    # Header.
    cv.text(100, 34, "REPUBLIC OF VESKARA", 3, TEAL)
    cv.text(100, 58, "REPUBLIKA VESKARA  -  PASPOR", 2, INK_SOFT)
    cv.text(100, 76, "PASSPORT", 2, INK_SOFT)
    cv.hline(48, 100, 416, TEAL, 2)
    # Type / code / number row.
    cv.text(48, 112, "TYPE", 2, INK_SOFT)
    cv.text(48, 128, "P", 2, INK)
    cv.text(120, 112, "CODE", 2, INK_SOFT)
    cv.text(120, 128, "VES", 2, INK)
    cv.text(210, 112, "PASSPORT NO.", 2, INK_SOFT)
    cv.text(210, 128, "VK 482 917", 2, INK)
    cv.text(360, 112, "PAGES", 2, INK_SOFT)
    cv.text(360, 128, "32", 2, INK)
    cv.hline(48, 150, 416, RULE, 1)

    # Portrait.
    draw_portrait(cv, 48, 164, 132, 172)
    cv.rect(48, 164, 132, 172, INK, t=2)
    cv.text(114, 342, "PHOTO", 2, INK_SOFT, align="center")

    # Data fields, two columns to the right of the portrait.
    fields = [
        ("SURNAME", "SELVIG", 200, 164),
        ("GIVEN NAMES", "MARA", 200, 204),
        ("NATIONALITY", "VESKARAN", 200, 244),
        ("DATE OF BIRTH", "12 MAR 1994", 200, 284),
        ("PLACE OF BIRTH", "KESTREL BAY", 340, 164),
        ("SEX", "F", 340, 204),
        ("DATE OF ISSUE", "14 FEB 2024", 340, 244),
        ("DATE OF EXPIRY", "14 FEB 2034", 340, 284),
        ("AUTHORITY", "PORT VARRA", 200, 324),
    ]
    for label, value, fx, fy in fields:
        cv.text(fx, fy, label, 1, INK_SOFT)
        cv.text(fx, fy + 13, value, 2, INK)
        cv.hline(fx, fy + 30, 118 if fx == 200 else 124, RULE, 1)
    # Signature: a hand-drawn squiggle above the line.
    sig = [(210, 396), (222, 384), (234, 396), (246, 382), (258, 394),
           (270, 386), (282, 396), (296, 384), (308, 394)]
    for i in range(len(sig) - 1):
        cv.line(sig[i][0], sig[i][1], sig[i + 1][0], sig[i + 1][1], INK, 2)
    cv.text(210, 402, "HOLDER'S SIGNATURE", 1, INK_SOFT)
    cv.hline(210, 398, 150, RULE, 1)
    # Highland route endorsement, the document's working note.
    cv.text(48, 428, "ENDORSEMENT: HIGHLAND ROUTE PERMIT NO. 118", 1, INK)
    cv.text(48, 444, "REGISTERED WOOL TRADER - PORT VARRA GUILD", 1, INK)
    cv.hline(48, 464, 416, RULE, 1)
    guilloche(cv, 40, 480, 472, 560, TEAL)

    # Machine-readable zone, computed check digits. The 44-character
    # lines are set tight so they fit the page width, as on a real card.
    line1, line2 = build_mrz()
    cv.fill_rect(36, 566, 452, 62, (255, 255, 255))
    cv.rect(36, 566, 452, 62, RULE, t=1)
    cv.text(48, 576, line1, 2, INK, tight=True)
    cv.text(48, 596, line2, 2, INK, tight=True)
    cv.text(48, 640, "THIS PASSPORT REMAINS THE PROPERTY OF THE", 1, INK_SOFT)
    cv.text(48, 654, "REPUBLIC OF VESKARA AND MUST BE RETURNED", 1, INK_SOFT)
    cv.text(48, 668, "ON DEMAND.  ISSUED AT PORT VARRA.", 1, INK_SOFT)


# -------------------------------------------------------------- right page
def draw_right_page(cv):
    cv.rect(532, 20, 472, 680, TEAL, t=2)
    cv.rect(538, 26, 460, 668, RULE, t=1)
    cv.text(560, 34, "VISAS", 3, TEAL)
    cv.text(560, 58, "VIZAT  -  STAMPS / PECATI", 2, INK_SOFT)
    cv.hline(560, 100, 416, TEAL, 2)

    # The telling paperwork: an Aldoria trade visa with its conditions.
    cv.rect(560, 112, 416, 100, INK_SOFT, t=1)
    cv.fill_rect(561, 113, 414, 22, TEAL)
    cv.text(572, 118, "ALDORIA - TRADE VISA  NO. A-2214", 2, (255, 255, 255))
    cv.text(572, 142, "VALID 30 DAYS FROM FIRST ENTRY", 2, INK)
    cv.text(572, 160, "WOOL TRADE ONLY - NO PAID WORK", 2, INK)
    cv.text(572, 178, "REGISTER IN LIR WITHIN 3 DAYS", 2, INK)
    cv.text(572, 196, "ISSUED 28 FEB 2024 - PORT VARRA", 1, INK_SOFT)
    # Fee stamp, tilted across the visa box's lower corner.
    fee = make_stamp([("FEE PAID", 2), ("40 DRAN", 2)], STAMP_RED,
                     shape="oval", w=150, h=76)
    cv.blit_rotated(fee, 912, 224, -12)

    # Three journeys, each a foreign entry stamp and a home return stamp.
    journeys = [
        ("02 MAR 2024  PORT VARRA - LIR, ALDORIA - 7 DAYS",
         [("ALDORIA", 2), ("ENTRY", 2), ("03 MAR 2024", 1)], STAMP_PURPLE,
         [("VESKARA", 2), ("ENTRY", 2), ("09 MAR 2024", 1)], STAMP_BLUE),
        ("21 JUN 2024  PORT VARRA - HALDEN, NORDMARK - 9 DAYS",
         [("NORDMARK", 2), ("ENTRY", 2), ("22 JUN 2024", 1)], STAMP_GREEN,
         [("VESKARA", 2), ("ENTRY", 2), ("30 JUN 2024", 1)], STAMP_BLUE),
        ("05 OCT 2024  PORT VARRA - SYLVARA - 14 DAYS",
         [("SYLVARA", 2), ("ENTRY", 2), ("06 OCT 2024", 1)], STAMP_RED,
         [("VESKARA", 2), ("ENTRY", 2), ("19 OCT 2024", 1)], STAMP_BLUE),
    ]
    y = 228
    for caption, flines, fcol, hlines, hcol in journeys:
        cv.text(560, y, caption, 1, INK_SOFT)
        fst = make_stamp(flines, fcol, shape="circle", w=170, h=108)
        hst = make_stamp(hlines, hcol, shape="oval", w=180, h=108)
        cv.blit_rotated(fst, 640, y + 66, -7)
        cv.blit_rotated(hst, 838, y + 66, 6)
        y += 124

    # Observations: what the country is, in its own paperwork.
    oy = y + 12
    cv.hline(560, oy, 416, RULE, 1)
    cv.text(560, oy + 10, "OBSERVATIONS / CATATAN", 2, TEAL)
    cv.text(560, oy + 34, "HOLDER IS A REGISTERED WOOL TRADER.", 2, INK)
    cv.text(560, oy + 54, "HIGHLAND ROUTE PERMIT NO. 118.", 2, INK)
    cv.text(560, oy + 74, "EXIT STAMPS ONLY AT PORT VARRA, KESTREL BAY, NORTH GATE", 1, INK_SOFT)


# -------------------------------------------------------------------- main
def main():
    rng = random.Random(20261121)
    cv = Canvas(W, H, PAPER)
    # Paper fibre and a soft centre gutter for the open spread.
    cv.speckle(rng, 2600, [(210, 196, 168), (250, 244, 230)], alpha=0.12)
    cv.fill_rect(510, 20, 4, 680, (206, 194, 170))
    cv.fill_rect(508, 20, 2, 680, (190, 178, 152))
    draw_left_page(cv)
    draw_right_page(cv)
    # Outer double rule around the whole spread.
    cv.rect(8, 8, W - 16, H - 16, TEAL_DARK, t=3)
    size = write_png(cv, OUT_PATH)
    print(f"wrote {OUT_PATH}: {size} bytes, {W}x{H}")


if __name__ == "__main__":
    main()
