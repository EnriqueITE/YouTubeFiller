from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "store-assets"
OUT.mkdir(parents=True, exist_ok=True)
ICON = Image.open(ROOT / "icons" / "icon128.png").convert("RGBA")

RED = (255, 0, 51)
RED_DARK = (213, 0, 0)
INK = (248, 250, 252)
MUTED = (200, 208, 220)
PANEL = (16, 18, 23)

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
    img = Image.new("RGB", (w, h), (5, 5, 7))
    px = img.load()
    c0 = (6, 6, 7)
    c1 = (18, 18, 24)
    c2 = (38, 0, 10)
    for y in range(h):
        for x in range(w):
            t = min(1, max(0, (x / w * 0.72 + y / h * 0.45)))
            if t < 0.58:
                k = t / 0.58
                c = tuple(int(c0[i] * (1 - k) + c1[i] * k) for i in range(3))
            else:
                k = (t - 0.58) / 0.42
                c = tuple(int(c1[i] * (1 - k) + c2[i] * k) for i in range(3))
            px[x, y] = c
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gp = glow.load()
    cx, cy = int(w * 0.16), int(h * 0.18)
    r = max(w, h) * 0.38
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy) / r
            if d < 1:
                a = int(80 * (1 - d) ** 1.8)
                gp[x, y] = (255, 0, 51, a)
    return Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")


def shadowed_round(img, box, radius, fill, shadow=(0, 0, 0, 120), blur=28, offset=(0, 22), outline=None):
    x1, y1, x2, y2 = box
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    sx, sy = offset
    d.rounded_rectangle((x1 + sx, y1 + sy, x2 + sx, y2 + sy), radius=radius, fill=shadow)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    Image.alpha_composite(img, layer)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline)


def paste_round(img, source, box, radius):
    x, y, w, h = box
    src = source.resize((w, h), Image.Resampling.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    img.paste(src, (x, y), mask)


def draw_brand(draw, img, x, y, icon_size=56, title_size=25, tagline=True):
    paste_round(img, ICON, (x, y, icon_size, icon_size), max(8, icon_size // 4))
    draw.text((x + icon_size + 14, y + 2), "YouTube Filler", font=BOLD(title_size), fill=INK)
    if tagline:
        draw.text((x + icon_size + 14, y + 35), "Centered cover mode for YouTube", font=REG(14), fill=MUTED)


def red_gradient_circle(img, center, radius):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = center
    for r in range(radius, 0, -1):
        k = r / radius
        col = tuple(int(RED[i] * (1 - k) + RED_DARK[i] * k) for i in range(3)) + (255,)
        d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=col)
    Image.alpha_composite(img, layer)


def draw_arrows(draw, cx, cy, s, fill=(255, 255, 255)):
    def line(points):
        draw.line(points, fill=fill, width=max(2, int(s * 0.07)), joint="curve")
    q = s * 0.32
    a = s * 0.13
    for dx, dy, sx, sy in [(-q, -q, -1, -1), (q, -q, 1, -1), (-q, q, -1, 1), (q, q, 1, 1)]:
        ex, ey = cx + dx, cy + dy
        mx, my = cx + dx * 0.35, cy + dy * 0.35
        line((mx, my, ex, ey))
        line((ex, ey, ex - sx * a, ey))
        line((ex, ey, ex, ey - sy * a))


def video_frame(w, h):
    frame = Image.new("RGB", (w, h), (13, 24, 56))
    px = frame.load()
    stops = [(0.0, (13,24,56)), (.46, (36,83,194)), (.75, (132,16,166)), (1.0, (255,0,51))]
    for y in range(h):
        for x in range(w):
            t = min(1, (x / w * .78 + y / h * .35))
            for i in range(len(stops)-1):
                if stops[i][0] <= t <= stops[i+1][0]:
                    t0, c0 = stops[i]; t1, c1 = stops[i+1]
                    k = (t - t0) / (t1 - t0)
                    px[x, y] = tuple(int(c0[j] * (1-k) + c1[j] * k) for j in range(3))
                    break
    overlay = Image.new("RGBA", (w, h), (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    d.ellipse((w*.18, h*.25, w*.34, h*.43), fill=(255,255,255,36))
    d.ellipse((w*.58, h*.09, w*.76, h*.30), fill=(255,255,255,28))
    d.rectangle((w*.18, 0, w*.21, h), fill=(255,255,255,18))
    d.rectangle((w*.39, 0, w*.425, h), fill=(255,255,255,13))
    for yy in range(int(h*.72), h):
        a = int(190 * ((yy - h*.72) / (h*.28)))
        d.line((0, yy, w, yy), fill=(0,0,0,a))
    return Image.alpha_composite(frame.convert("RGBA"), overlay)


def draw_video(img, x, y, w, h, radius=20):
    shadowed_round(img, (x, y, x+w, y+h), radius, (7, 8, 11, 255), outline=(45, 48, 58, 255))
    clip = Image.new("L", (w, h), 0)
    ImageDraw.Draw(clip).rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    comp = Image.new("RGBA", (w, h), (7, 8, 11, 255))
    d = ImageDraw.Draw(comp)
    top = max(28, round(h * .105))
    d.rectangle((0, 0, w, top), fill=(18, 21, 27, 255))
    for i in range(3):
        d.ellipse((18+i*16-5, top/2-5, 18+i*16+5, top/2+5), fill=(58,64,75,255))
    d.rounded_rectangle((68, top/2-11, w-22, top/2+11), radius=11, fill=(11,13,18,255))
    d.text((82, top/2-7), "youtube.com/watch", font=REG(11), fill=(154,163,178,255))
    comp.alpha_composite(video_frame(w, h-top), (0, top))
    controls_h = max(26, round(h * .105))
    cy = h - controls_h - 18
    d.rounded_rectangle((24, cy, w-24, cy+controls_h), radius=controls_h//2, fill=(0,0,0,174))
    d.text((42, cy + controls_h//2 - 8), "12:42 / 28:10", font=REG(12), fill=(215,220,230,255))
    yf = round(controls_h * 1.08)
    yfx = w - 116
    red_gradient_circle(comp, (yfx + yf//2, cy + controls_h//2), yf//2)
    draw_arrows(ImageDraw.Draw(comp), yfx + yf//2, cy + controls_h//2, yf*.72)
    d.rounded_rectangle((w-62, cy+controls_h//2-10, w-42, cy+controls_h//2+10), radius=2, outline=(255,255,255,230), width=2)
    img.paste(comp, (x, y), clip)


def popup_screenshot():
    img = background(640, 400).convert("RGBA")
    d = ImageDraw.Draw(img)
    shadowed_round(img, (130, 24, 510, 376), 14, (17,17,17,255), blur=24, offset=(0, 18))
    paste_round(img, ICON, (148,44,42,42), 8)
    d.text((202,49), "YouTube Filler", font=BOLD(17), fill=(248,248,248,255))
    d.text((202,72), "Centered cover mode for YouTube videos.", font=REG(12), fill=(184,184,184,255))
    d.line((148,106,492,106), fill=(255,255,255,32))
    d.text((148,119), "SHORTCUT INSIDE YOUTUBE", font=BOLD(12), fill=(248,248,248,255))
    d.rounded_rectangle((148,140,326,177), radius=7, fill=(255,255,255,20), outline=(255,255,255,36))
    d.text((163,149), "º", font=BOLD(15), fill=(248,248,248,255))
    d.rounded_rectangle((334,140,404,177), radius=7, fill=(255,0,51,255))
    d.text((352,150), "Record", font=BOLD(13), fill=(255,255,255,255))
    d.rounded_rectangle((412,140,476,177), radius=7, fill=(255,255,255,28))
    d.text((430,150), "Reset", font=BOLD(13), fill=(248,248,248,255))
    lines = [
        "Default: º, the key left of 1 on Spanish keyboards.",
        "On other layouts, record a shortcut here.",
        "Works only while the YouTube tab has focus.",
        "For a system-wide shortcut, set the browser command",
        "to Global in chrome://extensions/shortcuts."
    ]
    y = 195
    for i, line in enumerate(lines):
        d.text((148, y), line, font=REG(12), fill=(184,184,184,255))
        y += 18 if i in (0,2,3) else 23
    d.line((148,296,492,296), fill=(255,255,255,32))
    d.ellipse((148,312,172,336), fill=(255,221,0,255))
    d.text((154,315), "B", font=BLACK(13), fill=(106,59,0,255))
    d.text((182,309), "100% free and no signup.", font=REG(12), fill=(210,210,210,255))
    d.text((182,326), "Support my extensions.", font=REG(12), fill=(210,210,210,255))
    d.rounded_rectangle((348,314,476,343), radius=7, fill=(232,0,47,255))
    d.text((369,323), "Buy me a coffee", font=BOLD(11), fill=(255,255,255,255))
    return img.convert("RGB")


def small_tile():
    img = background(440, 280).convert("RGBA")
    d = ImageDraw.Draw(img)
    draw_brand(d, img, 28, 24, 38, 18, False)
    d.text((30,88), "Fill YouTube,", font=BLACK(31), fill=INK)
    d.text((30,121), "not your screen", font=BLACK(31), fill=INK)
    d.text((30,158), "Centered cover mode with", font=REG(13), fill=(216,220,229,255))
    d.text((30,176), "browser controls still visible.", font=REG(13), fill=(216,220,229,255))
    draw_video(img, 222, 60, 194, 150, 13)
    d.rounded_rectangle((30,231,156,259), radius=14, fill=(255,255,255,20), outline=(255,255,255,40))
    d.ellipse((39,240,49,250), fill=RED)
    d.text((56,237), "No real fullscreen", font=BOLD(10), fill=(232,236,243,255))
    return img.convert("RGB")


def marquee_tile():
    img = background(1400, 560).convert("RGBA")
    d = ImageDraw.Draw(img)
    draw_brand(d, img, 72, 48, 56, 25, True)
    d.text((82,146), "Fill the YouTube tab", font=BLACK(64), fill=INK)
    d.text((82,228), "Watch videos in a clean, centered cover crop while", font=REG(24), fill=(216,220,229,255))
    d.text((82,261), "keeping tabs, the address bar, and window controls visible.", font=REG(24), fill=(216,220,229,255))
    draw_video(img, 640, 70, 690, 420, 22)
    shadowed_round(img, (670, 382, 950, 498), 18, (16,18,23,255), blur=18, offset=(0,14), outline=(55,58,70,255))
    d.text((690,402), "Configurable shortcut", font=BLACK(18), fill=INK)
    d.rounded_rectangle((690,438,762,482), radius=10, fill=(238,242,247,255), outline=(203,211,223,255), width=2)
    d.line((692,480,760,480), fill=(174,184,199,255), width=3)
    d.text((722,438), "º", font=BLACK(22), fill=(23,27,34,255), anchor="mt")
    d.text((780,443), "Record a different key", font=REG(13), fill=(207,213,223,255))
    d.text((780,461), "for your layout.", font=REG(13), fill=(207,213,223,255))
    pills = [(82, "YouTube watch pages", 175), (272, "Playback controls stay available", 250), (537, "Privacy friendly", 128)]
    for x, text, w in pills:
        d.rounded_rectangle((x,458,x+w,498), radius=20, fill=(255,255,255,20), outline=(255,255,255,40))
        d.ellipse((x+14,473,x+24,483), fill=RED)
        d.text((x+34,468), text, font=BOLD(15), fill=(232,236,243,255))
    return img.convert("RGB")


def save(img, name):
    path = OUT / name
    img.save(path, format="PNG", optimize=True)
    check = Image.open(path)
    print(f"{path.relative_to(ROOT)} {check.size[0]}x{check.size[1]} mode={check.mode}")

save(popup_screenshot(), "youtube-filler-popup-en-640x400.png")
save(small_tile(), "youtube-filler-promo-small-440x280.png")
save(marquee_tile(), "youtube-filler-promo-marquee-1400x560.png")