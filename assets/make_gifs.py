"""Draws the two pixel-art GIFs in this folder. Run: pip install pillow ; python assets/make_gifs.py assets"""
import math, random, sys, os
from PIL import Image, ImageDraw, ImageFilter

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

FONT = {
 'A':"010101111101101",'L':"100100100100111",'T':"111010010010010",'H':"101101111101101",'F':"111100110100100",
 'R':"110101110101101",'Y':"101101010010010",'U':"101101101101111",'M':"101111111101101",'3':"111001011001111",
 'I':"111010010010111",'O':"111101101101111",'B':"110101110101110",'P':"110101110100100",'E':"111100110100111",
 'C':"111100100100111",'S':"111100111001111",'N':"110101101101101",'G':"111100101101111",'D':"110101101101110",
 'K':"101101110101101",'V':"101101101101010",'W':"101101111111101",'X':"101101010101101",' ':"000000000000000",
}
def text(d, x, y, s, col, scale=1, vertical=False):
    for ch in s:
        g = FONT[ch]
        for i, b in enumerate(g):
            if b == '1':
                px, py = x + (i % 3) * scale, y + (i // 3) * scale
                d.rectangle([px, py, px + scale - 1, py + scale - 1], fill=col)
        if vertical: y += 6 * scale
        else: x += 4 * scale

def hexc(h, a=255): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (a,)

# ------------------------------------------------------------------ banner
W, H, N, S = 320, 120, 24, 3
R = random.Random(7)
stars = [(R.randrange(W), R.randrange(45), R.randrange(N)) for _ in range(45)]
far = []; x = 0
while x < W:
    w = R.randrange(10, 26); far.append((x, w, R.randrange(28, 62))); x += w + R.randrange(0, 3)
mids = [(-4, 46, 64), (46, 40, 52), (92, 58, 74), (156, 34, 46), (196, 50, 66), (252, 30, 40), (286, 38, 58)]
wins = {}
for bi, (bx, bw, bh) in enumerate(mids):
    for wy in range(H - 22 - bh + 6, H - 24, 5):
        for wx in range(bx + 3, bx + bw - 3, 5):
            if R.random() < .42:
                wins[(wx, wy)] = (R.choice(['#ffd36b', '#7af7ff', '#ff8fd8', '#ffd36b']), R.random() < .12, R.randrange(N))
drops = [(R.randrange(W), R.randrange(H), R.choice([3, 4])) for _ in range(85)]

frames = []
for f in range(N):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):  # sky gradient
        t = y / H; d.line([(0, y), (W, y)], fill=(int(10 + 40 * t), int(5 + 12 * t), int(26 + 50 * t), 255))
    for sx, sy, ph in stars:
        if (f + ph) % 8 < 6: d.point((sx, sy), fill=hexc('#e9d8ff') if (f + ph) % 8 < 3 else hexc('#8a6bb8'))
    d.ellipse([266, 10, 284, 28], fill=hexc('#ffd9f2')); d.ellipse([272, 8, 290, 26], fill=(14, 7, 32, 255))  # crescent moon
    for bx, bw, bh in far:
        d.rectangle([bx, H - 24 - bh, bx + bw, H - 24], fill=hexc('#1c1236'))
        if bh > 50: d.line([(bx + bw // 2, H - 24 - bh - 6), (bx + bw // 2, H - 24 - bh)], fill=hexc('#1c1236'))
        if bh > 50 and f % 12 < 6: d.point((bx + bw // 2, H - 24 - bh - 7), fill=hexc('#ff3b6b'))
    # drone bobbing in the sky
    dx, dy = 40 + int(6 * math.sin(f / N * 2 * math.pi)), 22 + int(2 * math.sin(f / N * 4 * math.pi))
    d.rectangle([dx, dy, dx + 8, dy + 2], fill=hexc('#3b2a5e')); d.line([(dx - 2, dy - 1), (dx + 10, dy - 1)], fill=hexc('#6b5a8e'))
    d.point((dx + 4, dy + 3), fill=hexc('#7af7ff') if f % 4 < 2 else hexc('#3b2a5e'))
    for bi, (bx, bw, bh) in enumerate(mids):
        top = H - 22 - bh
        d.rectangle([bx, top, bx + bw, H - 22], fill=hexc('#2a1a48' if bi % 2 else '#24163e'))
        d.line([(bx, top), (bx + bw, top)], fill=hexc('#4a3478'))
    for (wx, wy), (col, flick, ph) in wins.items():
        on = not (flick and (f + ph) % 9 < 3)
        d.rectangle([wx, wy, wx + 2, wy + 2], fill=hexc(col) if on else hexc('#3a2a5a'))
    for box in [(93, 29, 148, 49), (2, 46, 31, 58), (154, 60, 175, 72), (200, 29, 213, 58)]:
        d.rectangle(box, fill=hexc('#0e0820'))
    # neon signs (glow layer)
    glow = Image.new('RGBA', (W, H)); g = ImageDraw.Draw(glow)
    althaf_on = f not in (9, 10, 17)
    sign = [(g, 1), (d, 0)]
    for layer, isglow in sign:
        if althaf_on: text(layer, 98, 34, 'ALTHAF', hexc('#ff2bd6'), scale=2)
        text(layer, 205, 34, 'AI', hexc('#7af7ff') if f % 6 < 5 else hexc('#2a6a7a'), scale=2, vertical=True)
        text(layer, 158, 64, 'ROBO', hexc('#ffd36b'))
        text(layer, 6, 50, 'CYPHER', hexc('#8cff7a') if f % 12 < 9 else hexc('#2f5a2a'))
    d.rectangle([94, 30, 147, 48], outline=hexc('#ff2bd6') if althaf_on else hexc('#5a2a5a'))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(2.2)))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(0.6)))
    d = ImageDraw.Draw(im)
    # street + wet reflections
    d.rectangle([0, H - 22, W, H], fill=hexc('#120a22'))
    d.line([(0, H - 22), (W, H - 22)], fill=hexc('#3b2a5e'))
    for rx, col, w in [(98, '#ff2bd6', 50), (205, '#7af7ff', 6), (158, '#ffd36b', 14), (6, '#8cff7a', 22)]:
        if col == '#ff2bd6' and not althaf_on: continue
        for k in range(0, 18, 2):
            wob = int(2 * math.sin((f + k) / 3))
            c = hexc(col, 120 - k * 6)
            d.line([(rx + wob + 2, H - 20 + k), (rx + w + wob - 2, H - 20 + k)], fill=c)
    # street lamp + light cone
    d.line([(250, H - 22), (250, H - 60)], fill=hexc('#4a3a6a'), width=2); d.line([(250, H - 60), (258, H - 60)], fill=hexc('#4a3a6a'), width=2)
    cone = Image.new('RGBA', (W, H)); ImageDraw.Draw(cone).polygon([(256, H - 58), (240, H - 22), (276, H - 22)], fill=(122, 247, 255, 34)); im.alpha_composite(cone)
    d = ImageDraw.Draw(im); d.rectangle([255, H - 59, 259, H - 57], fill=hexc('#bffbff'))
    # little robot with blinking eye + antenna
    rx, ry = 182, H - 34
    d.rectangle([rx, ry, rx + 9, ry + 7], fill=hexc('#5b4a85')); d.rectangle([rx + 1, ry + 8, rx + 8, ry + 11], fill=hexc('#45376a'))
    d.line([(rx + 4, ry - 3), (rx + 4, ry)], fill=hexc('#8a7ab8')); d.point((rx + 4, ry - 4), fill=hexc('#ff3b6b') if f % 6 < 3 else hexc('#5a2a3a'))
    eye = hexc('#7af7ff') if f % 12 not in (5, 6) else hexc('#5b4a85')
    d.rectangle([rx + 2, ry + 2, rx + 3, ry + 3], fill=eye); d.rectangle([rx + 6, ry + 2, rx + 7, ry + 3], fill=eye)
    # rain (loops seamlessly: 5px per frame * 24 frames = 120px = screen height)
    for x0, y0, ln in drops:
        y = (y0 + f * 5) % H; x = (x0 + y // 8) % W
        d.line([(x, y), (x + 1, y + ln)], fill=(170, 160, 255, 140))
    text(d, 4, H - 8, 'RYUMA33', hexc('#4a3a6a'))
    frames.append(im.resize((W * S, H * S), Image.NEAREST).convert('RGB'))

def save(frames, path, ms):
    pal = frames[0].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    q = [fr.quantize(palette=pal, dither=Image.Dither.NONE) for fr in frames]
    q[0].save(path, save_all=True, append_images=q[1:], duration=ms, loop=0, optimize=True, disposal=1)
    print(path, os.path.getsize(path) // 1024, 'KB')

save(frames, os.path.join(OUT, 'banner.gif'), 110)

# ------------------------------------------------------------------ robot typing at a laptop
W2, H2, N2, S2 = 64, 48, 12, 4
code = [(random.Random(i).randrange(3, 12), random.Random(i * 7).choice(['#7af7ff', '#ff8fd8', '#ffd36b', '#8cff7a'])) for i in range(40)]
fr2 = []
for f in range(N2):
    im = Image.new('RGBA', (W2, H2), hexc('#0d1117')); d = ImageDraw.Draw(im)
    d.rectangle([0, 38, W2, H2], fill=hexc('#1b1430'))  # desk
    # robot
    bob = 1 if f % 2 else 0
    d.rectangle([8, 14 + bob, 26, 28 + bob], fill=hexc('#5b4a85'))                 # head
    d.rectangle([10, 17 + bob, 24, 24 + bob], fill=hexc('#120a22'))                # visor
    eye = hexc('#7af7ff') if f not in (7,) else hexc('#2a6a7a')
    d.rectangle([12, 19 + bob, 14, 21 + bob], fill=eye); d.rectangle([20, 19 + bob, 22, 21 + bob], fill=eye)
    d.line([(17, 9 + bob), (17, 14 + bob)], fill=hexc('#8a7ab8')); d.rectangle([16, 7 + bob, 18, 9 + bob], fill=hexc('#ff2bd6') if f % 4 < 2 else hexc('#6a2a5a'))
    d.rectangle([11, 29, 23, 38], fill=hexc('#45376a'))                             # body
    d.point((17, 33), fill=hexc('#8cff7a') if f % 3 else hexc('#2f5a2a'))
    # arms typing (alternate)
    la, ra = (35, 36) if f % 2 else (36, 35)
    d.line([(23, 31), (32, la)], fill=hexc('#8a7ab8'), width=2); d.line([(23, 33), (38, ra)], fill=hexc('#8a7ab8'), width=2)
    # laptop
    d.polygon([(30, 37), (58, 37), (60, 39), (28, 39)], fill=hexc('#3b3355'))
    d.rectangle([34, 16, 58, 36], fill=hexc('#2b2445')); d.rectangle([36, 18, 56, 34], fill=hexc('#0a0716'))
    for row in range(5):  # scrolling code
        ln, col = code[(row + f) % len(code)]
        d.line([(38 + (row % 2) * 2, 20 + row * 3), (38 + ln + (row % 2) * 2, 20 + row * 3)], fill=hexc(col))
    if f % 2: d.rectangle([38 + code[(4 + f) % 40][0] + 3, 32, 39 + code[(4 + f) % 40][0] + 3, 33], fill=hexc('#ffffff'))  # cursor
    # floating code symbols
    for i, sym in enumerate(['01', '10']):
        y = 12 - ((f * 1 + i * 6) % 12)
        text(d, 44 + i * 9, y if y > 0 else 0, sym.replace('0', 'O').replace('1', 'I'), hexc('#ff2bd6', 160))
    fr2.append(im.resize((W2 * S2, H2 * S2), Image.NEAREST).convert('RGB'))
save(fr2, os.path.join(OUT, 'robot.gif'), 140)
