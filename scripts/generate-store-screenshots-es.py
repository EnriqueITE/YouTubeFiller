from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "store-screenshots"
ICON = Image.open(ROOT / "icons" / "icon128.png").convert("RGBA")

RED = (255, 0, 51)
RED_DARK = (213, 0, 0)
INK = (248, 250, 252)
MUTED = (184, 192, 204)

FONT_DIR = Path("C:/Windows/Fonts")

def font(name, size):
    for candidate in [FONT_DIR / name, FONT_DIR / "segoeui.ttf", FONT_DIR / "arial.ttf"]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()

REG = lambda s: font("segoeui.ttf", s)
BOLD = lambda s: font("segoeuib.ttf", s)
BLACK = lambda s: font("seguisb.ttf", s)


def background(w=1280, h=800):
    img = Image.new("RGB", (w, h), (5, 5, 7))
    px = img.load()
    c0 = (6, 6, 7)
    c1 = (17, 17, 22)
    c2 = (34, 0, 9)
    for y in range(h):
        for x in range(w):
            t = min(1, max(0, (x / w * 0.72 + y / h * 0.45)))
            if t < 0.55:
                k = t / 0.55
                c = tuple(int(c0[i] * (1 - k) + c1[i] * k) for i in range(3))
            else:
                k = (t - 0.55) / 0.45
                c = tuple(int(c1[i] * (1 - k) + c2[i] * k) for i in range(3))
            px[x, y] = c
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gp = glow.load()
    cx, cy = int(w * 0.18), int(h * 0.20)
    r = max(w, h) * 0.42
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy) / r
            if d < 1:
                gp[x, y] = (255, 0, 51, int(72 * (1 - d) ** 1.7))
    return Image.alpha_composite(img.convert("RGBA"), glow)


def paste_round(img, source, box, radius):
    x, y, w, h = box
    src = source.resize((w, h), Image.Resampling.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    img.paste(src, (x, y), mask)


def shadow_rect(img, box, radius, fill, shadow=(0,0,0,120), blur=30, offset=(0,26), outline=None):
    x1, y1, x2, y2 = box
    layer = Image.new("RGBA", img.size, (0,0,0,0))
    d = ImageDraw.Draw(layer)
    ox, oy = offset
    d.rounded_rectangle((x1+ox, y1+oy, x2+ox, y2+oy), radius=radius, fill=shadow)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    Image.alpha_composite(img, layer)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline)


def draw_brand(img, d):
    paste_round(img, ICON, (58, 46, 52, 52), 13)
    d.text((132, 47), "YouTube Filler", font=BOLD(26), fill=INK)
    d.text((132, 83), "Modo cover centrado para YouTube", font=REG(15), fill=(230, 234, 243, 255))


def draw_multiline(d, xy, lines, font_obj, fill, line_gap):
    x, y = xy
    for line in lines:
        d.text((x, y), line, font=font_obj, fill=fill)
        y += line_gap


def video_gradient(w, h):
    frame = Image.new("RGB", (w, h), (13, 24, 56))
    px = frame.load()
    stops = [(0.0, (13,24,56)), (.42, (24,62,147)), (.70, (91,11,143)), (1.0, (255,0,51))]
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
    od = ImageDraw.Draw(overlay)
    od.ellipse((w*.12, h*.25, w*.29, h*.47), fill=(255,255,255,34))
    od.ellipse((w*.58, h*.08, w*.78, h*.31), fill=(255,255,255,27))
    od.rectangle((w*.155, 0, w*.18, h), fill=(255,255,255,18))
    od.rectangle((w*.37, 0, w*.40, h), fill=(255,255,255,14))
    for yy in range(int(h*.70), h):
        a = int(190 * ((yy - h*.70) / (h*.30)))
        od.line((0, yy, w, yy), fill=(0,0,0,a))
    return Image.alpha_composite(frame.convert("RGBA"), overlay)


def draw_arrows(d, cx, cy, s, fill=(255,255,255,255)):
    width = max(3, int(s * .07))
    q = s * .32
    a = s * .13
    for dx, dy, sx, sy in [(-q,-q,-1,-1), (q,-q,1,-1), (-q,q,-1,1), (q,q,1,1)]:
        ex, ey = cx + dx, cy + dy
        mx, my = cx + dx*.35, cy + dy*.35
        d.line((mx,my,ex,ey), fill=fill, width=width)
        d.line((ex,ey,ex-sx*a,ey), fill=fill, width=width)
        d.line((ex,ey,ex,ey-sy*a), fill=fill, width=width)


def draw_red_circle(img, cx, cy, radius):
    d = ImageDraw.Draw(img)
    for r in range(radius, 0, -1):
        k = r / radius
        col = tuple(int(RED[i] * (1-k) + RED_DARK[i] * k) for i in range(3)) + (255,)
        d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=col)


def draw_browser(img, x=466, y=82, w=760, h=590):
    shadow_rect(img, (x, y, x+w, y+h), 22, (7,8,11,255), outline=(45,48,58,255))
    clip = Image.new("L", (w, h), 0)
    ImageDraw.Draw(clip).rounded_rectangle((0,0,w,h), radius=22, fill=255)
    comp = Image.new("RGBA", (w, h), (7,8,11,255))
    d = ImageDraw.Draw(comp)
    top = 54
    d.rectangle((0,0,w,top), fill=(18,21,27,255))
    for i in range(3):
        d.ellipse((19+i*23, 22, 31+i*23, 34), fill=(52,58,70,255))
    d.rounded_rectangle((96, 14, w-18, 42), radius=14, fill=(11,13,18,255))
    d.text((119, 20), "youtube.com/watch", font=REG(13), fill=(130, 172, 217,255))
    comp.alpha_composite(video_gradient(w, h-top), (0, top))
    d.rounded_rectangle((28, h-75, w-28, h-23), radius=26, fill=(0,0,0,174))
    d.text((47, h-58), "12:42 / 28:10", font=REG(13), fill=(215,220,230,255))
    cy = h - 49
    for ix, label_x in enumerate([w-265, w-219, w-174, w-107, w-62]):
        if ix == 2:
            draw_red_circle(comp, label_x+24, cy, 24)
            draw_arrows(ImageDraw.Draw(comp), label_x+24, cy, 34)
        else:
            ImageDraw.Draw(comp).rounded_rectangle((label_x+16, cy-8, label_x+32, cy+8), radius=2, outline=(255,255,255,230), width=2)
    img.paste(comp, (x,y), clip)


def slide_01():
    img = background()
    d = ImageDraw.Draw(img)
    draw_brand(img, d)
    draw_multiline(d, (70, 154), ["Rellena la", "ventana del", "navegador"], BLACK(52), INK, 58)
    draw_multiline(d, (70, 346), ["El modo cover centrado", "expande los videos de YouTube", "a toda la pestaña, manteniendo", "visibles los controles del navegador."], REG(23), (248,248,255,255), 31)
    draw_browser(img)
    d.text((70, 737), "Sin pantalla completa real. Sin barras negras. Solo el video, centrado.", font=REG(15), fill=(210,225,255,255))
    return img.convert("RGB")


def make_source_video():
    return video_gradient(1280, 720)


def fit_contain(source, size):
    sw, sh = source.size
    tw, th = size
    scale = min(tw / sw, th / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    resized = source.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (tw, th), (5, 5, 5, 255))
    canvas.alpha_composite(resized, ((tw - nw) // 2, (th - nh) // 2))
    return canvas


def fit_cover_center(source, size):
    sw, sh = source.size
    tw, th = size
    scale = max(tw / sw, th / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    resized = source.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - tw) // 2)
    top = max(0, (nh - th) // 2)
    return resized.crop((left, top, left + tw, top + th))


def draw_split_panels(img):
    d = ImageDraw.Draw(img)
    source = make_source_video()
    x1, y1, w, h = 470, 136, 366, 498

    shadow_rect(img, (x1,y1,x1+w,y1+h), 18, (5,5,5,255), outline=(45,48,58,255))
    clip = Image.new("L", (w,h), 0)
    ImageDraw.Draw(clip).rounded_rectangle((0,0,w,h), radius=18, fill=255)
    pane = fit_contain(source, (w, h))
    pd = ImageDraw.Draw(pane)
    pd.rounded_rectangle((18,18,150,52), radius=17, fill=(0,0,0,185))
    pd.text((31,27), "Reproductor normal", font=BOLD(12), fill=(255,255,255,255))
    img.paste(pane, (x1,y1), clip)

    x2 = 854
    shadow_rect(img, (x2,y1,x2+w,y1+h), 18, (9,13,24,255), outline=(45,48,58,255))
    clip2 = Image.new("L", (w,h), 0)
    ImageDraw.Draw(clip2).rounded_rectangle((0,0,w,h), radius=18, fill=255)
    pane2 = fit_cover_center(source, (w, h))
    pd2 = ImageDraw.Draw(pane2)
    pd2.rounded_rectangle((18,18,137,52), radius=17, fill=(0,0,0,185))
    pd2.text((31,27), "YouTube Filler", font=BOLD(12), fill=(255,255,255,255))
    img.paste(pane2, (x2,y1), clip2)

def slide_03():
    img = background()
    d = ImageDraw.Draw(img)
    draw_brand(img, d)
    draw_multiline(d, (70,154), ["Recorte centrado,", "sin barras negras"], BLACK(52), INK, 58)
    draw_multiline(d, (70,290), ["El modo cover rellena la pestaña y", "recorta de forma uniforme desde el", "centro cuando cambia la relación de", "aspecto."], REG(23), (248,248,255,255), 31)
    draw_split_panels(img)
    return img.convert("RGB")


def draw_options_panel(img):
    d = ImageDraw.Draw(img)
    x, y, w, h = 750, 132, 430, 451
    shadow_rect(img, (x,y,x+w,y+h), 24, (255,255,255,255), blur=34, offset=(0,26))
    d.rounded_rectangle((x,y,x+w,y+h), radius=24, fill=(255,255,255,255))
    d.rounded_rectangle((x,y,x+w,y+104), radius=24, fill=RED)
    d.rectangle((x,y+72,x+w,y+104), fill=RED)
    paste_round(img, ICON, (x+28, y+28, 52, 52), 13)
    d.text((x+96, y+28), "YouTube Filler", font=BOLD(24), fill=(255,255,255,255))
    d.text((x+96, y+64), "Configuración", font=REG(14), fill=(255,219,226,255))
    body_y = y + 130
    d.rounded_rectangle((x+28, body_y, x+w-28, body_y+120), radius=16, fill=(248,250,252,255), outline=(221,225,232,255))
    d.text((x+46, body_y+20), "ATAJO ACTUAL", font=BOLD(13), fill=(100,112,132,255))
    d.rounded_rectangle((x+48, body_y+47, x+148, body_y+99), radius=12, fill=(238,242,247,255), outline=(203,211,223,255), width=2)
    d.line((x+51, body_y+96, x+145, body_y+96), fill=(174,184,199,255), width=5)
    d.text((x+98, body_y+54), "Izq. del 1", font=BLACK(14), fill=(23,27,34,255), anchor="ma")
    d.text((x+98, body_y+78), "teclado español", font=BOLD(10), fill=(102,112,133,255), anchor="ma")
    d.text((x+272, body_y+68), "Cámbialo", font=BOLD(14), fill=(104,115,134,255))
    d.text((x+272, body_y+86), "cuando quieras", font=BOLD(14), fill=(104,115,134,255))
    body_y2 = body_y + 137
    d.rounded_rectangle((x+28, body_y2, x+w-28, body_y2+94), radius=16, fill=(248,250,252,255), outline=(221,225,232,255))
    d.text((x+46, body_y2+21), "COMANDO DEL NAVEGADOR", font=BOLD(13), fill=(100,112,132,255))
    d.text((x+46, body_y2+52), "Alt+Shift+V", font=BLACK(22), fill=(20,24,32,255))
    by = y + 381
    d.rounded_rectangle((x+28, by, x+188, by+44), radius=22, fill=RED)
    d.text((x+48, by+13), "Grabar atajo", font=BOLD(14), fill=(255,255,255,255))
    d.rounded_rectangle((x+198, by, x+278, by+44), radius=22, fill=(238,241,246,255))
    d.text((x+222, by+13), "Reset", font=BOLD(14), fill=(48,54,66,255))


def slide_04():
    img = background()
    d = ImageDraw.Draw(img)
    draw_brand(img, d)
    draw_multiline(d, (70,154), ["Usa tu", "atajo", "preferido"], BLACK(52), INK, 58)
    draw_multiline(d, (70,346), ["Por defecto usa la tecla a la izquierda", "del 1 en teclados españoles. En otros", "teclados puedes grabar otro atajo."], REG(23), (248,248,255,255), 31)
    draw_options_panel(img)
    d.text((70, 738), "Captura de la ficha en español. La extensión se localiza automáticamente.", font=REG(15), fill=(210,225,255,255))
    return img.convert("RGB")


def save(img, name):
    path = OUT / name
    img.save(path, "PNG", optimize=True)
    check = Image.open(path)
    print(f"{path.relative_to(ROOT)} {check.size[0]}x{check.size[1]} mode={check.mode}")

save(slide_01(), "youtube-filler-store-01-es.png")
save(slide_03(), "youtube-filler-store-03-es.png")
save(slide_04(), "youtube-filler-store-04-es.png")