#!/usr/bin/env python3
"""makefun-news-20261121: one page that sums up the world news of
Saturday 21 November 2026, drawn at run time with pure Python stdlib.

The program takes no input, opens no socket, reads no clock and rolls no
dice: every invocation paints the same 1024x1024 PNG byte for byte.
It writes $MAKEFUN_OUTPUT_DIR/entry.png (or --out DIR/entry.png).

Stories on the page, each reported on 21 November 2026 (any timezone):
  * Two Russian missiles and a suspected drone come down in Poland;
    Warsaw calls it a deliberate provocation and NATO calls it a grave
    violation of allied airspace.
  * US stocks plunge into correction: the S and P 500 and the Dow close in
    correction territory, the Nasdaq sheds 5.28 percent and Nvidia falls
    about 14 percent as the AI sell-off deepens.
  * Cyclone Akvan crosses the Odisha coast near Gopalpur and weakens,
    after 80,000 people were evacuated ahead of it.
  * After the ICJ ruling that Myanmar committed genocide against the
    Rohingya, Malaysia plans to resettle 10,000 Rohingya refugees to
    Turkiye; rights groups press for action against Myanmar.
  * Britain and the EU sign three deals in Brussels: food trade, carbon
    markets and youth mobility.
  * Trump returns from China and calls the talks successful, after the
    first Trump-Xi-Putin trilateral summit in Shenzhen.
Ticker: Bolsonaro taken to hospital; Palisades fire arson verdict;
Indonesia fire losses near $30bn; NSE becomes the world's 5th-largest
listed exchange.
"""

import argparse
import math
import os
import struct
import sys
import zlib

SIDE = 1024

# Palette: newsprint cream, deep navy, crimson, teal and ochre.
CREAM = (244, 238, 224)
SHEET = (255, 251, 240)
NAVY = (13, 32, 61)
CRIMSON = (178, 24, 24)
TEAL = (13, 110, 102)
OCHRE = (196, 128, 12)
SLATE = (98, 102, 108)
PAPERWHITE = (255, 255, 255)
SOOT = (22, 22, 22)
SKYBLUE = (168, 205, 235)
LEAF = (34, 139, 68)

# ---------------------------------------------------------------------------
# 5x7 bitmap type. One glyph is seven integers; each integer holds five
# bits, bit 4 the leftmost column, bit 0 the rightmost. Uppercase only:
# every string is upper-cased before it is drawn.
# ---------------------------------------------------------------------------
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x15, 0x0A),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x06, 0x04, 0x00, 0x04),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "\u2022": (0x00, 0x00, 0x00, 0x0C, 0x0C, 0x00, 0x00),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
}

CELL_W = 6   # advance per glyph cell, in font units
CELL_H = 7   # rows per glyph


def text_width(text, scale):
    """Pixel width of a string at the given scale."""
    return max(0, len(text) * CELL_W * scale - scale)


def flow(text, scale, max_px):
    """Greedy word wrap; returns a list of upper-cased lines."""
    words = text.upper().split(" ")
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_px or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Canvas:
    """An RGB picture held as one bytearray per scanline.

    Keeping a row per bytearray makes a horizontal run a single slice
    assignment, and lets the PNG writer stream rows out unchanged.
    """

    def __init__(self, size, bg):
        self.size = size
        self.rows = [bytearray(bg * size) for _ in range(size)]

    def _clip_x(self, x, w):
        lo = max(0, x)
        hi = min(self.size, x + w)
        return (lo, hi - lo) if hi > lo else None

    def run(self, x, y, w, colour):
        """Paint w pixels of one colour on row y, clipped."""
        if 0 <= y < self.size and w > 0:
            span = self._clip_x(x, w)
            if span:
                start, length = span
                self.rows[y][start * 3:start * 3 + length * 3] = (
                    bytes(colour) * length)

    def rect(self, x, y, w, h, colour):
        for yy in range(max(0, y), min(self.size, y + h)):
            self.run(x, yy, w, colour)

    def outline(self, x, y, w, h, colour, thick=2):
        self.rect(x, y, w, thick, colour)
        self.rect(x, y + h - thick, w, thick, colour)
        self.rect(x, y, thick, h, colour)
        self.rect(x + w - thick, y, thick, h, colour)

    def hline(self, x, y, w, colour, thick=1):
        self.rect(x, y, w, thick, colour)

    def vline(self, x, y, h, colour, thick=1):
        self.rect(x, y, thick, h, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        """Bresenham segment, each step a thick square."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0, y0, thick, thick, colour)
            if x0 == x1 and y0 == y1:
                return
            step = 2 * err
            if step >= dy:
                err += dy
                x0 += sx
            if step <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, colour):
        """Filled circle, drawn as one horizontal run per row."""
        for dy in range(-r, r + 1):
            half = int(math.sqrt(r * r - dy * dy))
            self.run(cx - half, cy + dy, 2 * half + 1, colour)

    def ring(self, cx, cy, r, colour, thick=3):
        for deg in range(360):
            rad = math.radians(deg)
            self.rect(int(cx + r * math.cos(rad)),
                      int(cy + r * math.sin(rad)), thick, thick, colour)

    def _edge_x(self, ax, ay, bx, by, y):
        """X where the edge a-b crosses row y, or None."""
        if ay == by or not (min(ay, by) <= y <= max(ay, by)):
            return None
        return ax + (y - ay) * (bx - ax) / (by - ay)

    def triangle(self, p, q, s, colour):
        """Filled triangle, split at its middle vertex into two fans.

        The upper fan runs from the top vertex down to the middle one,
        the lower fan from the middle vertex to the bottom one; each row
        spans between the two edges that cross it.
        """
        pts = sorted((p, q, s), key=lambda t: t[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            xs = []
            for edge in ((ax, ay, bx, by), (bx, by, cx, cy),
                         (cx, cy, ax, ay)):
                hit = self._edge_x(*edge, y)
                if hit is not None:
                    xs.append(hit)
            if len(xs) >= 2:
                left, right = int(min(xs)), int(max(xs))
                self.run(left, y, right - left + 1, colour)

    def starburst(self, cx, cy, outer, inner, colour, points=12):
        """A spiked burst: triangles fanning out from the centre."""
        for i in range(points):
            a0 = 2 * math.pi * i / points
            a1 = 2 * math.pi * (i + 0.5) / points
            a2 = 2 * math.pi * (i + 1) / points
            tip = (int(cx + outer * math.cos(a0)),
                   int(cy + outer * math.sin(a0)))
            valley = (int(cx + inner * math.cos(a1)),
                      int(cy + inner * math.sin(a1)))
            base = (int(cx + outer * math.cos(a2)),
                    int(cy + outer * math.sin(a2)))
            self.triangle(tip, valley, base, colour)
        self.disc(cx, cy, inner // 2, colour)

    def glyph(self, x, y, ch, scale, colour):
        rows = FONT.get(ch)
        if rows is None:
            return
        for row_i, bits in enumerate(rows):
            for col in range(5):
                if bits & (1 << (4 - col)):
                    self.rect(x + col * scale, y + row_i * scale,
                              scale, scale, colour)

    def text(self, x, y, string, scale, colour):
        pen = x
        for ch in string.upper():
            self.glyph(pen, y, ch, scale, colour)
            pen += CELL_W * scale
        return pen

    def text_mid(self, y, string, scale, colour, x0=0, x1=SIDE):
        w = text_width(string, scale)
        self.text(x0 + (x1 - x0 - w) // 2, y, string, scale, colour)

    def para(self, x, y, string, scale, colour, max_px, leading=4):
        """Wrapped paragraph; returns the y just below its last line."""
        step = CELL_H * scale + leading
        for i, line in enumerate(flow(string, scale, max_px)):
            self.text(x, y + i * step, line, scale, colour)
        return y + len(flow(string, scale, max_px)) * step

    def coverage(self):
        """Share of pixels that differ from the cream background."""
        bg = bytes(CREAM)
        hit = 0
        for row in self.rows:
            for i in range(0, len(row), 3):
                if row[i:i + 3] != bg:
                    hit += 1
        return hit / (self.size * self.size)


# ---------------------------------------------------------------------------
# Pictograms, each drawn inside an 84x84 panel at (x, y).
# ---------------------------------------------------------------------------
def pic_falling_bars(cv, x, y):
    cv.rect(x, y, 84, 84, PAPERWHITE)
    cv.outline(x, y, 84, 84, SOOT, 2)
    cv.vline(x + 12, y + 10, 62, SOOT, 3)
    cv.hline(x + 12, y + 70, 62, SOOT, 3)
    heights = (52, 44, 34, 24, 14)
    for i, hgt in enumerate(heights):
        bx = x + 18 + i * 11
        cv.rect(bx, y + 68 - hgt, 8, hgt, CRIMSON if i < 3 else TEAL)
    cv.line(x + 16, y + 14, x + 74, y + 56, SOOT, 2)


def pic_spiral(cv, x, y):
    cv.rect(x, y, 84, 84, PAPERWHITE)
    cv.outline(x, y, 84, 84, SOOT, 2)
    cx, cy = x + 42, y + 42
    for r in (34, 26, 18, 10):
        cv.ring(cx, cy, r, TEAL if r % 16 == 2 else NAVY, 3)
    cv.disc(cx, cy, 5, CRIMSON)
    cv.line(cx - 34, cy, cx - 18, cy - 12, TEAL, 2)


def pic_scales(cv, x, y):
    cv.rect(x, y, 84, 84, PAPERWHITE)
    cv.outline(x, y, 84, 84, SOOT, 2)
    cx = x + 42
    cv.vline(cx, y + 10, 52, SOOT, 3)
    cv.hline(x + 14, y + 14, 56, SOOT, 3)
    cv.disc(cx, y + 10, 4, OCHRE)
    for side in (-1, 1):
        px = cx + side * 26
        cv.line(px, y + 14, px - 9, y + 34, SOOT, 2)
        cv.line(px, y + 14, px + 9, y + 34, SOOT, 2)
        cv.triangle((px - 11, y + 34), (px + 11, y + 34),
                    (px, y + 52), NAVY)
    cv.hline(x + 16, y + 62, 52, SOOT, 3)


def pic_rings(cv, x, y):
    cv.rect(x, y, 84, 84, PAPERWHITE)
    cv.outline(x, y, 84, 84, SOOT, 2)
    cv.ring(x + 32, y + 42, 20, NAVY, 3)
    cv.ring(x + 52, y + 42, 20, OCHRE, 3)
    cv.disc(x + 42, y + 42, 4, CRIMSON)


def pic_globe(cv, x, y):
    cv.rect(x, y, 84, 84, PAPERWHITE)
    cv.outline(x, y, 84, 84, SOOT, 2)
    cx, cy = x + 42, y + 42
    cv.ring(cx, cy, 30, TEAL, 3)
    cv.vline(cx, cy - 30, 60, TEAL, 2)
    cv.hline(cx - 30, cy, 60, TEAL, 2)
    cv.disc(cx - 10, cy - 10, 6, LEAF)
    cv.disc(cx + 12, cy + 10, 7, LEAF)
    cv.disc(cx + 8, cy - 14, 4, LEAF)


# ---------------------------------------------------------------------------
# Page furniture: one column story and one horizontal band story.
# ---------------------------------------------------------------------------
def column_story(cv, x, y, w, h, tint, kicker, headline, body, pic):
    cv.rect(x, y, w, h, SHEET)
    cv.outline(x, y, w, h, SOOT, 2)
    cv.rect(x, y, w, 8, tint)
    cv.text(x + 14, y + 20, kicker, 2, tint)
    pic(cv, x + 14, y + 44)
    end = cv.para(x + 14, y + 138, headline, 3, SOOT, w - 28, leading=4)
    cv.para(x + 14, end + 6, body, 2, SOOT, w - 28, leading=3)


def band_story(cv, x, y, w, h, tint, kicker, headline, body, pic):
    cv.rect(x, y, w, h, SHEET)
    cv.outline(x, y, w, h, SOOT, 2)
    cv.rect(x, y, 8, h, tint)
    cv.text(x + 20, y + 12, kicker, 2, tint)
    pic(cv, x + 20, y + 32)
    cv.para(x + 118, y + 34, headline, 3, SOOT, w - 138, leading=4)
    cv.para(x + 118, y + 86, body, 2, SOOT, w - 138, leading=3)


def build_page():
    cv = Canvas(SIDE, CREAM)

    # Date strip.
    cv.rect(0, 0, SIDE, 30, NAVY)
    cv.text_mid(8, "SATURDAY 21 NOVEMBER 2026", 2, PAPERWHITE)
    cv.text(24, 8, "NO. 325", 2, SKYBLUE)
    cv.text(SIDE - 24 - text_width("PRICE: ONE PAGE", 2), 8,
            "PRICE: ONE PAGE", 2, SKYBLUE)

    # Masthead.
    cv.text_mid(48, "THE DAILY WORLD", 9, SOOT)
    cv.text_mid(122, "ONE DAY  -  ONE IMAGE  -  THE WORLD'S NEWS", 2,
               CRIMSON)
    cv.hline(24, 146, 976, CRIMSON, 5)
    cv.hline(24, 154, 976, SOOT, 2)

    # Lead story: Russian missiles land in Poland.
    cv.rect(24, 166, 976, 296, SHEET)
    cv.outline(24, 166, 976, 296, SOOT, 3)
    cv.text(44, 182, "LEAD STORY  -  WARSAW / BRUSSELS", 2, CRIMSON)
    cv.text(44, 208, "RUSSIAN MISSILES", 5, SOOT)
    cv.text(44, 250, "HIT POLAND", 5, SOOT)
    cv.text(44, 292, "NATO CALLS IT A GRAVE VIOLATION", 3, CRIMSON)
    cv.para(44, 326,
            "TWO MISSILES AND A SUSPECTED DRONE CAME DOWN IN POLAND. "
            "WARSAW CALLS IT A DELIBERATE PROVOCATION; ALLIES MEET AS "
            "EUROPE HELD MILITARY DRILLS NEARBY.",
            2, SOOT, 560, leading=4)
    cv.para(44, 404,
            "RUSSIA ALSO HIT UKRAINE WITH 400 DRONES AND 110 MISSILES "
            "IN ONE OF THE WAR'S LARGEST ATTACKS.",
            2, SOOT, 560, leading=4)
    # Blast graphic on the right of the lead box.
    gx, gy = 700, 196
    cv.rect(gx, gy, 280, 236, PAPERWHITE)
    cv.outline(gx, gy, 280, 236, SOOT, 2)
    cv.ring(gx + 140, gy + 96, 62, CRIMSON, 3)
    cv.ring(gx + 140, gy + 96, 44, OCHRE, 3)
    cv.starburst(gx + 140, gy + 96, 52, 22, CRIMSON)
    cv.disc(gx + 140, gy + 96, 10, OCHRE)
    cv.text_mid(gy + 176, "POLAND", 3, SOOT, gx, gx + 280)
    cv.text_mid(gy + 202, "2 MISSILES + 1 DRONE", 2, CRIMSON, gx, gx + 280)

    # Three columns: markets, cyclone, ICJ aftermath.
    top = 478
    col_h = 272
    column_story(cv, 24, top, 304, col_h, CRIMSON, "MARKETS - NEW YORK",
                 "WALL STREET SLIDES INTO CORRECTION",
                 "S AND P 500 AND DOW IN CORRECTION. NASDAQ -5.28%. "
                 "NVIDIA -14%.",
                 pic_falling_bars)
    column_story(cv, 344, top, 304, col_h, TEAL, "WEATHER - INDIA",
                 "CYCLONE AKVAN CROSSES ODISHA COAST",
                 "LANDFALL NEAR GOPALPUR; WEAKENS AFTER 80,000 "
                 "EVACUATED.",
                 pic_spiral)
    column_story(cv, 664, top, 312, col_h, NAVY, "JUSTICE - THE HAGUE",
                 "MALAYSIA TO RESETTLE 10,000 ROHINGYA",
                 "RIGHTS GROUPS SEEK ACTION AFTER THE ICJ RULING.",
                 pic_scales)

    # Two bands: UK-EU deals, Trump back from China.
    band_y = 766
    band_h = 124
    band_story(cv, 24, band_y, 480, band_h, NAVY, "DIPLOMACY - BRUSSELS",
               "UK AND EU SIGN THREE DEALS",
               "FOOD, CARBON AND YOUTH MOBILITY DEALS.",
               pic_rings)
    band_story(cv, 520, band_y, 480, band_h, TEAL, "DIPLOMACY - BEIJING",
               "TRUMP RETURNS FROM CHINA",
               "CALLS TALKS SUCCESSFUL AFTER THE SHENZHEN SUMMIT.",
               pic_globe)

    # Ticker.
    cv.rect(24, 906, 976, 66, NAVY)
    cv.para(40, 916,
            "BOLSONARO TAKEN TO HOSPITAL WITH SEVERE ABDOMINAL PAIN "
            "\u2022 PALISADES FIRE ARSON VERDICT: MAN FOUND GUILTY "
            "\u2022 INDONESIA FIRE LOSSES COULD REACH $30BN "
            "\u2022 NSE BECOMES WORLD'S 5TH-LARGEST EXCHANGE",
            2, PAPERWHITE, 944, leading=4)

    # Footer.
    cv.hline(24, 982, 976, SOOT, 2)
    cv.text_mid(992, "SOURCES: BBC, REUTERS, AP, CNBC, TIMES OF INDIA - "
                "21 NOV 2026", 2, SLATE)
    return cv


# ---------------------------------------------------------------------------
# PNG writer: RGB, 8-bit, zlib level 9, filter byte 0 on every row.
# No time or text chunks, so the bytes are fully determined by the page.
# ---------------------------------------------------------------------------
def _chunk(tag, payload):
    framed = tag + payload
    return (struct.pack(">I", len(payload)) + framed +
            struct.pack(">I", zlib.crc32(framed) & 0xFFFFFFFF))


def encode_png(cv):
    header = struct.pack(">IIBBBBB", SIDE, SIDE, 8, 2, 0, 0, 0)
    body = b"".join(b"\x00" + bytes(row) for row in cv.rows)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header) +
            _chunk(b"IDAT", zlib.compress(body, 9)) + _chunk(b"IEND", b""))


def write_entry(cv, path):
    with open(path, "wb") as handle:
        handle.write(encode_png(cv))


def inspect_png(path):
    """Check a finished entry.png and report each check on its own line."""
    with open(path, "rb") as handle:
        data = handle.read()
    checks = []
    checks.append(("signature",
                   data[:8] == b"\x89PNG\r\n\x1a\n"))
    width, height = struct.unpack(">II", data[16:24])
    checks.append(("dimensions", (width, height) == (SIDE, SIDE)))
    checks.append(("size_under_1mib", 1000 < len(data) < 1048576))
    checks.append(("iend_present", data.endswith(
        _chunk(b"IEND", b""))))
    for name, passed in checks:
        print("%s: %s" % (name, "OK" if passed else "BAD"))
    return all(passed for _, passed in checks)


def summarise(cv, path):
    """Facts about the finished page, for the build log."""
    print("glyphs in font: %d" % len(FONT))
    print("ink coverage: %.3f" % cv.coverage())
    print("entry.png: %d bytes" % os.path.getsize(path))
    print("canvas rows: %d" % len(cv.rows))


def build_cli(argv=None):
    parser = argparse.ArgumentParser(
        description="Draw the 21 Nov 2026 front page as entry.png.")
    parser.add_argument("--out", metavar="DIR",
                        help="directory to write entry.png into")
    parser.add_argument("--selftest", action="store_true",
                        help="only inspect an existing entry.png")
    return parser.parse_args(argv)


def run():
    args = build_cli()
    out_dir = args.out or os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    if args.selftest:
        if not os.path.exists(path):
            print("missing: %s" % path)
            sys.exit(1)
        sys.exit(0 if inspect_png(path) else 1)
    page = build_page()
    write_entry(page, path)
    if not inspect_png(path):
        sys.exit(1)
    summarise(page, path)


if __name__ == "__main__":
    run()
