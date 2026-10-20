"""Render an animated GitHub profile terminal, inspired by github-readme-terminal.
Pure Pillow implementation for reliable GitHub Actions rendering without API keys.
Run: python scripts/terminal.py
"""
from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets' / 'terminal.gif'
W, H = 900, 510
BG = '#0b1017'
SURFACE = '#111923'
BORDER = '#31404e'
FG = '#d7e1e7'
DIM = '#73879a'
TEAL = '#8bd9c9'
ORANGE = '#f4bf81'
BLUE = '#8fbce6'
GREEN = '#9cd2a4'
FONT_CANDIDATES = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationMono-Regular.ttf',
    'C:/Windows/Fonts/consola.ttf',
]
BOLD_CANDIDATES = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationMono-Bold.ttf',
    'C:/Windows/Fonts/consolab.ttf',
]

def font_for(candidates, size):
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()
FONT = font_for(FONT_CANDIDATES, 17)
SMALL = font_for(FONT_CANDIDATES, 14)
BOLD = font_for(BOLD_CANDIDATES, 20)

# Content can be edited here. This is NOT a claim of live GitHub stats.
BIO = [
    ('name', 'Moosa Alam'),
    ('handle', 'moosacodes'),
    ('university', 'University of Guelph / Computer Science'),
    ('focus', 'AI infrastructure · HPC · distributed systems'),
    ('also into', 'networking · automation · developer tools'),
    ('languages', 'Python · C · Java · JavaScript · Bash · SQL'),
    ('toolbox', 'Linux · Docker · AWS · Git · CI/CD'),
    ('currently', 'building reliable things from the ground up'),
]

def base():
    image = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((12, 12, W-12, H-12), radius=17, fill=SURFACE, outline=BORDER, width=2)
    d.rounded_rectangle((12, 12, W-12, 57), radius=16, fill='#1b2632')
    d.rectangle((13, 40, W-13, 57), fill='#1b2632')
    for x, c in ((37, '#e58a88'), (59, '#e7c27b'), (81, '#8ec8a8')):
        d.ellipse((x-6, 29, x+6, 41), fill=c)
    d.text((W//2, 35), 'moosa@github — terminal', font=SMALL, anchor='mm', fill='#adbac8')
    d.line((13, 58, W-13, 58), fill=BORDER, width=1)
    return image, d

def put(d, text, x, y, color=FG, font=FONT):
    d.text((x,y), text, font=font, fill=color)

def draw_frame(stage, partial='', caret=True):
    im, d = base()
    x, y = 42, 82
    if stage == 0:
        put(d, 'MOOSA//SYS     startup environment', x, y, TEAL, BOLD)
        put(d, '> booting profile...', x, y+53, FG)
        put(d, '> loading identity  [OK]', x, y+87, GREEN)
        put(d, '> initializing terminal ' + partial, x, y+121, ORANGE)
        put(d, 'github.com/moosacodes', x, H-65, DIM, SMALL)
    else:
        put(d, 'moosa', x, y, TEAL, BOLD)
        put(d, '@github:~$', x+70, y+2, DIM)
        put(d, 'cat about.txt', x+191, y+2, ORANGE)
        d.line((x, y+47, W-42, y+47), fill=BORDER, width=1)
        for idx, (label, value) in enumerate(BIO):
            yy = y+67 + idx*31
            put(d, f'{label:<12}', x+7, yy, BLUE)
            put(d, value, x+177, yy, FG)
        fy = y + 350
        put(d, 'moosa@github:~$ ', x, fy, TEAL)
        command = 'ls projects/' if stage == 1 else 'echo "keep building."'
        shown = partial if stage == 1 else command
        put(d, shown + ('_' if caret else ''), x+177, fy, ORANGE)
        if stage >= 2:
            put(d, 'Open-Role-Radar   InfraPulse   Agent-Seatbelt', x+7, fy+34, GREEN, SMALL)
    return im

def generate():
    frames, times = [], []
    def add(stage, s='', n=1, duration=110, caret=True):
        im=draw_frame(stage,s,caret)
        for _ in range(n): frames.append(im.copy()); times.append(duration)
    add(0,'',3,120)
    for i in range(1,7): add(0, '.'*i,1,115)
    add(0,'......',4,120)
    for i in range(1,len('ls projects/')+1,2): add(1,'ls projects/'[:i],1,90)
    add(1,'ls projects/',6,110)
    add(2,'',25,150)
    for i in range(2): add(2,'',4,180,caret=i==0)
    OUT.parent.mkdir(exist_ok=True, parents=True)
    # Palette quantization and frame optimization keep the GIF small enough for a README.
    frames[0].save(OUT,save_all=True,append_images=frames[1:],duration=times,loop=0,optimize=True,disposal=2)
    print(f'Wrote {OUT} ({OUT.stat().st_size:,} bytes, {len(frames)} frames)')

if __name__ == '__main__':
    generate()
