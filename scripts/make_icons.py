#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate Sundown Range II launcher icons: sunset sun + crosshair motif."""
from PIL import Image, ImageDraw
import math, os

RES = '/home/z/my-project/apk/android/app/src/main/res'

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def make_background(size):
    """Vertical sunset gradient: deep dusk top -> warm gold bottom."""
    img = Image.new('RGB', (size, size))
    dr = ImageDraw.Draw(img)
    top = (43, 45, 66)        # dusk blue-gray
    mid = (232, 128, 26)      # sunset orange
    bot = (242, 226, 196)     # cream horizon
    for y in range(size):
        t = y / size
        if t < 0.55:
            c = lerp(top, mid, t / 0.55)
        else:
            c = lerp(mid, bot, (t - 0.55) / 0.45)
        dr.line([(0, y), (size, y)], fill=c)
    # stars in upper part
    dr2 = ImageDraw.Draw(img)
    for i in range(int(size / 26)):
        x = (i * 37 % size); y = (i * 53 % int(size * 0.3))
        r = max(1, size // 220)
        dr2.ellipse([x - r, y - r, x + r, y + r], fill=(255, 236, 200))
    return img

def make_foreground(size):
    """Transparent layer: glowing sun disc + horizon + crosshair ring."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    cx = cy = size / 2
    R = size * 0.30          # sun radius (safe-zone friendly)
    sun_top = cy - size * 0.02
    # sun glow
    glow_r = R * 1.45
    for i in range(28, 0, -1):
        gr = glow_r * (1 + i / 40)
        alpha = int(26 - i * 0.85)
        if alpha <= 0: continue
        dr.ellipse([cx - gr, sun_top - gr, cx + gr, sun_top + gr], fill=(255, 170, 60, alpha))
    # sun disc with horizontal slice lines (retro sunset)
    slices = 6
    for i in range(slices):
        y0 = sun_top - R + (2 * R) * i / slices
        y1 = sun_top - R + (2 * R) * (i + 1) / slices
        gap = (size * 0.012) * i
        dr.ellipse([cx - R, y0, cx + R, min(y1, sun_top + R)], fill=(255, 122, 26, 255))
        if i < slices - 1:
            dr.rectangle([cx - R - 2, y1 - gap, cx + R + 2, y1 + gap], fill=(0, 0, 0, 0))
    # dark ground strip
    ground_y = sun_top + R * 0.55
    dr.rectangle([0, ground_y, size, size], fill=(38, 42, 54, 235))
    # silhouette ground line highlight
    dr.rectangle([0, ground_y, size, ground_y + size * 0.012], fill=(255, 196, 106, 255))
    # crosshair ring + ticks (shooting range motif)
    cr = R * 1.62
    w = max(2, int(size * 0.018))
    col = (255, 244, 214, 235)
    dr.arc([cx - cr, sun_top - cr, cx + cr, sun_top + cr], 0, 360, fill=col, width=w)
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        x1 = cx + math.cos(a) * (cr - w * 2.2)
        y1 = sun_top + math.sin(a) * (cr - w * 2.2)
        x2 = cx + math.cos(a) * (cr + w * 2.6)
        y2 = sun_top + math.sin(a) * (cr + w * 2.6)
        dr.line([(x1, y1), (x2, y2)], fill=col, width=w)
    # center dot
    d = size * 0.02
    dr.ellipse([cx - d, sun_top - d, cx + d, sun_top + d], fill=col)
    return img

def compose_legacy(size):
    """Legacy square icon: background + centered foreground scaled in."""
    bg = make_background(size).convert('RGBA')
    fg = make_foreground(size)
    out = Image.alpha_composite(bg, fg)
    # round corners for round variant handled by system; keep square + round mask
    return out

def make_round(size):
    img = compose_legacy(size)
    mask = Image.new('L', (size, size), 0)
    dr = ImageDraw.Draw(mask)
    dr.ellipse([0, 0, size, size], fill=255)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out

DENS = {'mdpi': 48, 'hdpi': 72, 'xhdpi': 96, 'xxhdpi': 144, 'xxxhdpi': 192}
FG = {'mdpi': 108, 'hdpi': 162, 'xhdpi': 216, 'xxhdpi': 324, 'xxxhdpi': 432}

for d, s in DENS.items():
    p = f'{RES}/mipmap-{d}'
    os.makedirs(p, exist_ok=True)
    compose_legacy(s).save(f'{p}/ic_launcher.png')
    make_round(s).save(f'{p}/ic_launcher_round.png')
    print(f'ic_launcher {d}: {s}px')

for d, s in FG.items():
    p = f'{RES}/mipmap-{d}'
    make_foreground(s).save(f'{p}/ic_launcher_foreground.png')
    print(f'foreground {d}: {s}px')

print('ICONS DONE')
