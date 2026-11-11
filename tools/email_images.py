"""Piyasa Masası e-posta görselleri.
Kullanım: python3 email_images.py public/data/latest.json <çıktı klasörü>
Üretilen PNG'ler (2x çözünürlük, e-postada 552-600 px genişlikte gösterilir):
  logo.png, canli.png, piyasalar.png, haber-1.png ... haber-6.png
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

F = "/usr/share/fonts/opentype/inter/"
def font(w, size):
    name = {"black": "InterDisplay-Black.otf", "xbold": "InterDisplay-ExtraBold.otf", "bold": "Inter-Bold.otf",
            "med": "Inter-Medium.otf", "reg": "Inter-Regular.otf"}[w]
    path = F + name
    if not os.path.exists(path):
        path = F + "Inter-Bold.otf"
    return ImageFont.truetype(path, size)

ORANGE, ORANGE2, BLACK, WHITE = (194, 65, 12), (249, 115, 22), (0, 0, 0), (255, 255, 255)
GREEN, RED, GREY, INK = (21, 128, 61), (185, 28, 28), (110, 110, 110), (20, 20, 20)
SECTOR = {"Makro": (30, 64, 175), "Yapay zekâ": (109, 40, 217), "Çip": (8, 145, 178), "Kuantum": (190, 24, 93),
          "Kripto": (217, 119, 6), "Enerji": (21, 128, 61), "Savunma": (71, 85, 105), "Nadir toprak": (120, 53, 15), "ETF": (15, 118, 110)}

def text_w(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]

def logo(out):
    W, H = 1200, 200
    im = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(im)
    f = font("black", 76); x = 48
    d.text((x, 34), "Piyasa", font=f, fill=WHITE); x += text_w(d, "Piyasa", f)
    d.text((x, 34), "Masası", font=f, fill=ORANGE2)
    d.text((50, 136), "ABD borsası, sade Türkçe ile", font=font("med", 28), fill=(190, 190, 190))
    # live badge
    bf = font("bold", 26); label = "CANLI PORTAL"
    bw = text_w(d, label, bf) + 70; bx = W - 48 - bw
    d.rounded_rectangle((bx, 62, bx + bw, 122), radius=30, outline=(70, 70, 70), width=3)
    d.ellipse((bx + 24, 82, bx + 44, 102), fill=(34, 197, 94))
    d.text((bx + 56, 76), label, font=bf, fill=WHITE)
    im.save(out, optimize=True)

def canli(out):
    W, H = 1104, 360
    im = Image.new("RGB", (W, H), (17, 17, 17)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius=28, fill=(17, 17, 17))
    d.ellipse((48, 52, 76, 80), fill=(239, 68, 68))
    d.text((92, 44), "CANLI", font=font("black", 34), fill=(239, 68, 68))
    d.text((48, 100), "Fiyatları portaldan anlık izle", font=font("xbold", 52), fill=WHITE)
    tiles = [("Dolar / TL", "₺"), ("Euro / TL", "₺"), ("Gram altın", "₺"), ("ABD hisseleri", "$ · ₺")]
    tw, gap, y = (W - 96 - 3 * 18) // 4, 18, 196
    for i, (t, c) in enumerate(tiles):
        x = 48 + i * (tw + gap)
        d.rounded_rectangle((x, y, x + tw, y + 110), radius=18, fill=(38, 38, 38))
        d.text((x + 22, y + 18), t, font=font("bold", 28), fill=WHITE)
        d.text((x + 22, y + 60), c, font=font("xbold", 30), fill=ORANGE2)
    im.save(out, optimize=True)

def piyasalar(data, out):
    rows = []
    for i in data.get("indices", []):
        if i.get("chg") is not None: rows.append((i["name"], float(i["chg"])))
    for m in data.get("macro", []):
        if m.get("chg") is not None and "VIX" not in m["name"]: rows.append((m["name"], float(m["chg"])))
    for c in data.get("crypto", []):
        if c.get("chg") is not None: rows.append((c["name"], float(c["chg"])))
    rows = rows[:10]
    W, top, rh = 1104, 140, 88
    H = top + rh * len(rows) + 60
    im = Image.new("RGB", (W, H), WHITE); d = ImageDraw.Draw(im)
    d.text((0, 16), "Günlük değişim (%)", font=font("xbold", 50), fill=INK)
    d.text((0, 80), "Önceki işlem günü kapanışı", font=font("med", 32), fill=GREY)
    m = max([abs(v) for _, v in rows] + [1.0])
    lab_w, cx_w = 380, W - 380 - 190
    zero = lab_w + cx_w // 2
    d.line((zero, top - 6, zero, top + rh * len(rows)), fill=(210, 210, 210), width=3)
    for k, (name, v) in enumerate(rows):
        y = top + k * rh
        d.text((0, y + 20), name, font=font("bold", 38), fill=INK)
        L = int((cx_w // 2 - 10) * abs(v) / m)
        col = GREEN if v > 0 else (RED if v < 0 else GREY)
        if v >= 0: d.rounded_rectangle((zero, y + 18, zero + max(L, 4), y + 68), radius=8, fill=col)
        else: d.rounded_rectangle((zero - max(L, 4), y + 18, zero, y + 68), radius=8, fill=col)
        s = ("+" if v > 0 else "−" if v < 0 else "") + "%" + f"{abs(v):.2f}".replace(".", ",")
        d.text((W - 178, y + 20), s, font=font("xbold", 38), fill=col)
    im.save(out, optimize=True)

def haber(n, i, out):
    W, H = 1104, 230
    col = SECTOR.get(n.get("sector", ""), (55, 65, 81))
    im = Image.new("RGB", (W, H), col); d = ImageDraw.Draw(im)
    # soft diagonal stripes for texture
    for x in range(-H, W, 46):
        d.line((x, H, x + H, 0), fill=tuple(min(255, c + 14) for c in col), width=14)
    d.rounded_rectangle((36, 36, 36 + 92, 36 + 92), radius=22, fill=WHITE)
    num = str(i); nf = font("black", 54)
    d.text((36 + (92 - text_w(d, num, nf)) // 2, 44), num, font=nf, fill=col)
    d.text((152, 40), (n.get("sector") or "Gündem").upper(), font=font("black", 44), fill=WHITE)
    imp = n.get("impact", "neutral")
    lab = {"up": "▲ OLUMLU", "down": "▼ OLUMSUZ"}.get(imp, "● NÖTR")
    lf = font("bold", 28); lw = text_w(d, lab, lf) + 40
    d.rounded_rectangle((152, 102, 152 + lw, 146), radius=22, fill=WHITE)
    d.text((172, 107), lab, font=lf, fill=GREEN if imp == "up" else RED if imp == "down" else GREY)
    x = 36
    for t in (n.get("tickers") or [])[:5]:
        tf = font("bold", 30); tw = text_w(d, t, tf) + 36
        d.rounded_rectangle((x, 164, x + tw, 208), radius=10, fill=(0, 0, 0))
        d.text((x + 18, 169), t, font=tf, fill=WHITE)
        x += tw + 12
    im.save(out, optimize=True)

if __name__ == "__main__":
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    o = sys.argv[2]; os.makedirs(o, exist_ok=True)
    logo(os.path.join(o, "logo.png")); canli(os.path.join(o, "canli.png")); piyasalar(data, os.path.join(o, "piyasalar.png"))
    for i, n in enumerate(data.get("news", [])[:6], 1):
        haber(n, i, os.path.join(o, f"haber-{i}.png"))
    print("ok")
