from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "store-assets"
OUT.mkdir(parents=True, exist_ok=True)
ICON = Image.open(ROOT / "icons" / "icon128.png").convert("RGBA")

RED = (255, 0, 51)
RED_DARK = (202, 0, 41)
INK = (248, 250, 252)
MUTED = (206, 214, 224)

FONT_DIR = Path("C:/Windows/Fonts")

def font(name, size):
    for candidate in [FONT_DIR / name, FONT_DIR / "segoeui.ttf", FONT_DIR / "arial.ttf"]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()

REG = lambda s: font("segoeui.ttf", s)
BOLD = lambda s: font("segoeuib.ttf", s)
BLACK = lambda s: font("seguisb.ttf", s)


def background(w, h):
    img = Image.new("RGB", (w, h), (6, 6, 8))
    px = img.load()
    c0 = (6, 6, 8)
    c1 = (17, 17, 23)
    c2 = (42, 0, 12)
    for y in range(h):
        for x in range(w):
            t = min(1, (x / w) * 0.7 + (y / h) * 0.35)
            if t < 0.58:
                k = t / 0.58
                c = tuple(int(c0[i] * (1 - k) + c1[i] * k) for i in range(3))
            else:
                k = (t - 0.58) / 0.42
                c = tuple(int(c1[i] * (1 - k) + c2[i] * k) for i in range(3))
            px[x, y] = c

    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gp = glow.load()
    for cx, cy, radius, alpha in [(w * 0.12, h * 0.15, max(w, h) * 0.42, 84), (w * 0.88, h * 0.75, max(w, h) * 0.36, 54)]:
        for y in range(h):
            for x in range(w):
                d = math.hypot(x - cx, y - cy) / radius
                if d < 1:
                    existing = gp[x, y][3]
                    a = min(255, existing + int(alpha * (1 - d) ** 1.8))
                    gp[x, y] = (255, 0, 51, a)
    return Image.alpha_composite(img.convert("RGBA"), glow)


def paste_round(img, source, box, radius):
    x, y, w, h = box
    src = source.resize((w, h), Image.Resampling.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    img.paste(src, (x, y), mask)


def shadow_round(img, box, radius, fill, outline=None, blur=28, offset=(0, 22)):
    x1, y1, x2, y2 = box
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    ox, oy = offset
    sd.rounded_rectangle((x1 + ox, y1 + oy, x2 + ox, y2 + oy), radius=radius, fill=(0, 0, 0, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    Image.alpha_composite(img, shadow)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline)


def draw_brand(img, x, y, icon_size, title_size, tagline=None):
    d = ImageDraw.Draw(img)
    paste_round(img, ICON, (x, y, icon_size, icon_size), max(7, icon_size // 4))
    tx = x + icon_size + max(10, icon_size // 3)
    d.text((tx, y - 1), "YouTube Filler", font=BOLD(title_size), fill=INK)
    if tagline:
        d.text((tx, y + title_size + 8), tagline, font=REG(max(12, title_size // 2)), fill=MUTED)


def video_gradient(w, h):
    frame = Image.new("RGB", (w, h), (12, 25, 60))
    px = frame.load()
    stops = [(0.0, (12, 25, 60)), (0.45, (35, 82, 194)), (0.72, (126, 16, 165)), (1.0, (255, 0, 51))]
    for y in range(h):
        for x in range(w):
            t = min(1, (x / w) * 0.78 + (y / h) * 0.34)
            for i in range(len(stops) - 1):
                if stops[i][0] <= t <= stops[i + 1][0]:
                    t0, c0 = stops[i]
                    t1, c1 = stops[i + 1]
                    k = (t - t0) / (t1 - t0)
                    px[x, y] = tuple(int(c0[j] * (1 - k) + c1[j] * k) for j in range(3))
                    break
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.ellipse((w * 0.18, h * 0.24, w * 0.34, h * 0.43), fill=(255, 255, 255, 34))
    d.ellipse((w * 0.60, h * 0.10, w * 0.78, h * 0.30), fill=(255, 255, 255, 26))
    d.rectangle((w * 0.18, 0, w * 0.205, h), fill=(255, 255, 255, 18))
    d.rectangle((w * 0.39, 0, w * 0.42, h), fill=(255, 255, 255, 13))
    for yy in range(int(h * 0.68), h):
        a = int(190 * ((yy - h * 0.68) / (h * 0.32)))
        d.line((0, yy, w, yy), fill=(0, 0, 0, a))
    return Image.alpha_composite(frame.convert("RGBA"), overlay)


def draw_fill_icon(d, cx, cy, size, fill=(255, 255, 255, 255)):
    width = max(2, round(size * 0.08))
    q = size * 0.31
    a = size * 0.14
    for dx, dy, sx, sy in [(-q, -q, -1, -1), (q, -q, 1, -1), (-q, q, -1, 1), (q, q, 1, 1)]:
        ex, ey = cx + dx, cy + dy
        mx, my = cx + dx * 0.36, cy + dy * 0.36
        d.line((mx, my, ex, ey), fill=fill, width=width)
        d.line((ex, ey, ex - sx * a, ey), fill=fill, width=width)
        d.line((ex, ey, ex, ey - sy * a), fill=fill, width=width)


def draw_red_circle(img, cx, cy, radius):
    d = ImageDraw.Draw(img)
    for r in range(radius, 0, -1):
        k = r / radius
        color = tuple(int(RED[i] * (1 - k) + RED_DARK[i] * k) for i in range(3)) + (255,)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)


def draw_browser_mock(img, x, y, w, h, radius):
    shadow_round(img, (x, y, x + w, y + h), radius, (7, 8, 11, 255), outline=(45, 48, 58, 255), blur=max(12, w // 24), offset=(0, max(10, h // 18)))
    clip = Image.new("L", (w, h), 0)
    ImageDraw.Draw(clip).rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    comp = Image.new("RGBA", (w, h), (7, 8, 11, 255))
    d = ImageDraw.Draw(comp)
    top = max(24, round(h * 0.115))
    d.rectangle((0, 0, w, top), fill=(18, 21, 27, 255))
    dot_r = max(3, round(w * 0.008))
    for i in range(3):
        cx = round(22 + i * dot_r * 4)
        d.ellipse((cx - dot_r, top / 2 - dot_r, cx + dot_r, top / 2 + dot_r), fill=(58, 64, 75, 255))
    d.rounded_rectangle((round(w * 0.13), round(top * 0.27), w - round(w * 0.04), round(top * 0.76)), radius=round(top * 0.25), fill=(11, 13, 18, 255))
    if w > 260:
        d.text((round(w * 0.16), round(top * 0.30)), "youtube.com/watch", font=REG(max(10, round(w * 0.018))), fill=(136, 174, 220, 255))

    comp.alpha_composite(video_gradient(w, h - top), (0, top))
    controls_h = max(18, round(h * 0.105))
    controls_y = h - controls_h - max(12, round(h * 0.045))
    pad = max(12, round(w * 0.045))
    d.rounded_rectangle((pad, controls_y, w - pad, controls_y + controls_h), radius=controls_h // 2, fill=(0, 0, 0, 180))
    if w > 260:
        d.text((pad + 18, controls_y + controls_h / 2 - 7), "12:42 / 28:10", font=REG(max(10, round(w * 0.018))), fill=(215, 220, 230, 255))
    button_r = max(12, round(controls_h * 0.48))
    button_cx = w - pad - max(35, round(w * 0.17))
    button_cy = controls_y + controls_h // 2
    draw_red_circle(comp, button_cx, button_cy, button_r)
    draw_fill_icon(ImageDraw.Draw(comp), button_cx, button_cy, button_r * 1.25)
    img.paste(comp, (x, y), clip)


def draw_lines(d, x, y, lines, font_obj, fill, gap):
    for line in lines:
        d.text((x, y), line, font=font_obj, fill=fill)
        y += gap


def small_tile(lang):
    is_es = lang == "es"
    img = background(440, 280)
    d = ImageDraw.Draw(img)
    draw_brand(img, 24, 22, 34, 17)
    if is_es:
        title = ["Rellena", "la pestaña"]
        subtitle = ["YouTube en grande,", "sin pantalla completa."]
    else:
        title = ["Fill", "the tab"]
        subtitle = ["Watch bigger,", "without fullscreen."]
    draw_lines(d, 28, 92, title, BLACK(34), INK, 38)
    draw_lines(d, 28, 180, subtitle, REG(14), MUTED, 19)
    draw_browser_mock(img, 232, 72, 176, 132, 14)
    return img.convert("RGB")


def marquee_tile(lang):
    is_es = lang == "es"
    img = background(1400, 560)
    d = ImageDraw.Draw(img)
    draw_brand(img, 74, 54, 58, 26, "Modo cover centrado para YouTube" if is_es else "Centered cover mode for YouTube")
    if is_es:
        title = ["YouTube grande", "sin pantalla", "completa"]
        subtitle = ["El video rellena la pestaña", "y el navegador sigue visible."]
    else:
        title = ["Fill YouTube", "without", "fullscreen"]
        subtitle = ["The video fills the tab", "while the browser stays visible."]
    draw_lines(d, 82, 154, title, BLACK(58), INK, 62)
    draw_lines(d, 82, 366, subtitle, REG(25), MUTED, 34)
    draw_browser_mock(img, 640, 78, 690, 404, 22)
    return img.convert("RGB")


def save(img, name):
    path = OUT / name
    img.save(path, "PNG", optimize=True)
    check = Image.open(path)
    print(f"{path.relative_to(ROOT)} {check.size[0]}x{check.size[1]} mode={check.mode}")

save(small_tile("en"), "youtube-filler-promo-small-en-440x280.png")
save(small_tile("es"), "youtube-filler-promo-small-es-440x280.png")
save(marquee_tile("en"), "youtube-filler-promo-marquee-en-1400x560.png")
save(marquee_tile("es"), "youtube-filler-promo-marquee-es-1400x560.png")